#!/usr/bin/env python3
"""Registra en la tesis los informes del comité y aplica la reconciliación (ev.py).

Uso: python3 scripts/comite_registrar.py tesis/<TICKER>.md <informe_bajista.md> <informe_valorador.md>
Lee PROB_DESASTRE / VETO del bajista y TIR_ANUAL / PROB_DESASTRE del valorador, los escribe en el bloque ```ev```
(sección comite), copia ambos informes a la sección "## Comité" y escribe la reconciliación.
"""
import json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def num(pat, txt):
    m = re.search(pat, txt, re.I)
    if not m: return None
    v = float(m.group(1).replace(",", "."))
    return v / 100 if v > 1.5 else v  # admite "12%" o "0.12"

def main():
    tpath, bpath, vpath = sys.argv[1:4]
    txt = open(tpath, encoding="utf-8").read()
    bj = open(bpath, encoding="utf-8").read(); vc = open(vpath, encoding="utf-8").read()
    pd_b = num(r"PROB_DESASTRE\**\s*[:=]\s*\**\s*([0-9]+[.,]?[0-9]*)", bj)
    veto = bool(re.search(r"VETO\**\s*[:=]\s*\**\s*S[IÍ]\b", bj, re.I))
    tir_v = num(r"TIR_ANUAL\**\s*[:=]\s*\**\s*(-?[0-9]+[.,]?[0-9]*)", vc)
    pd_v = num(r"PROB_DESASTRE\**\s*[:=]\s*\**\s*([0-9]+[.,]?[0-9]*)", vc)
    m = re.search(r"```ev\s*\n(.*?)\n```", txt, re.S)
    ev = json.loads(m.group(1))
    ev["comite"] = {"valorador_ciego": {"tir": tir_v, "prob_desastre": pd_v}, "bajista": {"prob_desastre": pd_b, "veto": veto}}
    if len(sys.argv) > 4: ev["comite"]["error_documentado_valorador"] = sys.argv[4]
    txt = txt[:m.start(1)] + json.dumps(ev, ensure_ascii=False, indent=2) + txt[m.end(1):]
    open(tpath, "w", encoding="utf-8").write(txt)
    res = json.loads(subprocess.run([sys.executable, os.path.join(ROOT, "scripts/ev.py"), tpath], capture_output=True, text=True).stdout)
    c = res.get("comite", {})
    recon = (f"- Prob. desastre: propia {ev['escenarios']['desastre']['prob']} · bajista {pd_b} · valorador {pd_v} → **usada {c.get('prob_desastre_usada')}**\n"
             f"- TIR propia ajustada {c.get('tir_ajustada_propia')} · TIR valorador ciego {tir_v} → **TIR final {c.get('tir_final')}** ({c.get('regla')})\n"
             f"- Veto del bajista: {'SÍ' if veto else 'no'}\n"
             f"- Cumple: " + ", ".join(f"{k} {'✅' if v else '❌'}" for k, v in (c.get("cumple") or {}).items()) + "\n"
             f"- **compra_ok (reglas completas): {c.get('compra_ok')}**")
    def clean(s):  # rebaja los encabezados de los informes para que no rompan la estructura
        return re.sub(r"^#{1,3} ", "#### ", s.strip(), flags=re.M)
    bloque = (f"## Comité\n### 🔴 Bajista\n{clean(bj)}\n\n### 🔵 Valorador ciego\n{clean(vc)}\n\n### Reconciliación\n{recon}\n\n")
    txt = open(tpath, encoding="utf-8").read()
    txt = re.sub(r"^## Comité\n.*?(?=^## Decisión)", lambda _: bloque, txt, flags=re.S | re.M)
    open(tpath, "w", encoding="utf-8").write(txt)
    print(json.dumps({"ticker": ev["ticker"], "pd_bajista": pd_b, "veto": veto, "tir_valorador": tir_v, "pd_valorador": pd_v,
                      "tir_final": c.get("tir_final"), "pd_usada": c.get("prob_desastre_usada"), "cumple": c.get("cumple"),
                      "retornos": c.get("retornos_3a")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
