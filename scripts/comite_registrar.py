#!/usr/bin/env python3
"""Registra en la tesis los informes del comité y aplica la reconciliación (ev.py).

Uso:
  python3 scripts/comite_registrar.py tesis/<TICKER>.md <informe_bajista.md> <informe_valorador.md> ["error documentado"]
  python3 scripts/comite_registrar.py --recalcular tesis/<TICKER>.md [<informe_valorador.md>]

Lee PROB_DESASTRE / VETO del bajista y TIR_ANUAL / PROB_DESASTRE / PRECIO_ACTUAL / dividendos del valorador, los
escribe en el bloque ```ev``` (sección comite), copia ambos informes a la sección "## Comité" y escribe la reconciliación.

La TIR del valorador se guarda BRUTA y EXACTA: si la tabla de escenarios del informe permite recalcularla, se usa ese
valor (4 decimales) en vez del TIR_ANUAL redondeado. El 09/11/2026 un redondeo de 12,8% a 13% cambió el resultado de
Teleperformance al cruzar la frontera de los 5 pp.

--recalcular: no toca los informes copiados; solo actualiza el bloque ev (si se pasa el informe del valorador),
la subsección "### Reconciliación" y devuelve el resultado. Para cuando cambian las reglas.
"""
import json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV_RE = r"```ev\s*\n(.*?)\n```"

def num(pat, txt):
    m = re.search(pat, txt, re.I)
    if not m: return None
    v = float(m.group(1).replace(",", "."))
    return v / 100 if v > 1.5 else v  # admite "12%" o "0.12"

def _n(s):
    s = s.replace("−", "-").replace("–", "-").replace(" ", "").replace("**", "").replace("+", "").replace(" ", "")
    m = re.search(r"-?\d+(?:[.,]\d+)?", s)
    return float(m.group().replace(",", ".")) if m else None

def tabla_valorador(vc_txt):
    """(TIR exacta, dividendos esperados) a partir de la tabla de escenarios del informe; None si no se puede leer."""
    try:
        sec = vc_txt.split("## Escenarios")[1].split("## Resultado")[0]
    except IndexError:
        return None, None
    er = ps = dv = 0.0; ok_div = True
    for r in sec.splitlines():
        if not r.startswith("|") or r.startswith("|---") or "Prob" in r: continue
        c = [x.strip() for x in r.strip().strip("|").split("|")]
        if len(c) < 7: continue
        p, ret, d = _n(c[1]), _n(c[-1]), _n(c[-2])
        if p is None or ret is None: continue
        if p > 1: p /= 100
        er += p * ret / 100; ps += p
        if d is None: ok_div = False
        else: dv += p * d
    if abs(ps - 1) > 0.01 or er <= -1: return None, None
    return round((1 + er) ** (1 / 3) - 1, 4), (round(dv, 4) if ok_div else None)

def leer_valorador(vc_txt, ev):
    """Datos del valorador para el bloque ev: tir (bruta, exacta), prob_desastre, precio, dividendos_esperados_3a."""
    tir_inf = num(r"TIR_ANUAL\**\s*[:=]\s*\**\s*(-?[0-9]+[.,]?[0-9]*)", vc_txt)
    pd_v = num(r"PROB_DESASTRE\**\s*[:=]\s*\**\s*([0-9]+[.,]?[0-9]*)", vc_txt)
    m = re.search(r"PRECIO_ACTUAL\**\s*[:=]\s*\**\s*([0-9]+(?:[.,][0-9]+)?)", vc_txt)
    precio = float(m.group(1).replace(",", ".")) if m else float(ev["precio_actual"])
    m = re.search(r"DIVIDENDOS_ESPERADOS_3A\**\s*[:=]\s*\**\s*([0-9]+(?:[.,][0-9]+)?)", vc_txt)
    div_inf = float(m.group(1).replace(",", ".")) if m else None
    tir_tab, div_tab = tabla_valorador(vc_txt)
    # la tabla solo vale si es coherente con la cifra que declara el propio valorador (misma TIR salvo redondeo)
    tir = tir_tab if (tir_tab is not None and tir_inf is not None and abs(tir_tab - tir_inf) <= 0.0051) else tir_inf
    div = div_inf if div_inf is not None else div_tab
    # los dividendos de la tabla solo se aceptan si son del mismo orden que los propios (evita errores de unidad)
    propios = sum(v["prob"] * v.get("dividendos_3a", 0) for v in ev["escenarios"].values())
    if div is not None and propios > 0 and not (0.5 <= div / propios <= 2.0): div = None
    out = {"tir": tir, "prob_desastre": pd_v, "precio": precio}
    if div is not None: out["dividendos_esperados_3a"] = div
    if tir_inf is not None and tir is not None and abs(tir - tir_inf) > 1e-9: out["tir_declarada"] = tir_inf
    return out

def evaluar(tpath):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts/ev.py"), tpath], capture_output=True, text=True)
    if r.returncode != 0: sys.exit(f"ev.py falló con {tpath}: {r.stderr or r.stdout}")
    return json.loads(r.stdout)

def pct(x): return "—" if x is None else f"{x * 100:.1f}%".replace(".", ",")

def texto_recon(ev, c):
    vc = ev["comite"]["valorador_ciego"]; bj = ev["comite"]["bajista"]
    return (f"- Prob. desastre: propia {ev['escenarios']['desastre']['prob']} · bajista {bj.get('prob_desastre')} · valorador {vc.get('prob_desastre')}"
            f" → **usada {c.get('prob_desastre_usada')}** (media de las tres)\n"
            f"- TIR propia ajustada {pct(c.get('tir_ajustada_propia'))} · TIR valorador ciego {pct(vc.get('tir'))} bruta → {pct(c.get('tir_valorador_neta'))} neta"
            f" (mismos costes y retención que la propia) → **TIR final {pct(c.get('tir_final'))}** ({c.get('regla')})\n"
            f"- Veto del bajista: {'SÍ' if bj.get('veto') else 'no'}\n"
            f"- Cumple: " + ", ".join(f"{k} {'✅' if v else '❌'}" for k, v in (c.get("cumple") or {}).items()) + "\n"
            f"- **compra_ok (reglas completas): {c.get('compra_ok')}**\n"
            f"- Reglas del 09/11/2026: TIR del valorador exacta y en neto; si la diferencia es ≥ 5 pp, la más baja + 2,5 pp.")

def escribir_ev(tpath, ev):
    txt = open(tpath, encoding="utf-8").read(); m = re.search(EV_RE, txt, re.S)
    txt = txt[:m.start(1)] + json.dumps(ev, ensure_ascii=False, indent=2) + txt[m.end(1):]
    open(tpath, "w", encoding="utf-8").write(txt)

def leer_ev(tpath):
    return json.loads(re.search(EV_RE, open(tpath, encoding="utf-8").read(), re.S).group(1))

def recalcular(tpath, vpath=None):
    ev = leer_ev(tpath)
    if vpath:
        nuevo = leer_valorador(open(vpath, encoding="utf-8").read(), ev)
        ev["comite"]["valorador_ciego"] = nuevo; escribir_ev(tpath, ev)
    c = evaluar(tpath).get("comite", {})
    txt = open(tpath, encoding="utf-8").read()
    txt, n = re.subn(r"(^### Reconciliación\n).*?(?=^## )", lambda m: m.group(1) + texto_recon(ev, c) + "\n\n", txt, flags=re.S | re.M)
    if n != 1: sys.exit(f"{tpath}: no encuentro una única sección '### Reconciliación'")
    open(tpath, "w", encoding="utf-8").write(txt)
    return ev, c

def main():
    if sys.argv[1] == "--recalcular":
        ev, c = recalcular(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        tpath, bpath, vpath = sys.argv[1:4]
        bj = open(bpath, encoding="utf-8").read(); vc = open(vpath, encoding="utf-8").read()
        pd_b = num(r"PROB_DESASTRE\**\s*[:=]\s*\**\s*([0-9]+[.,]?[0-9]*)", bj)
        veto = bool(re.search(r"VETO\**\s*[:=]\s*\**\s*S[IÍ]\b", bj, re.I))
        ev = leer_ev(tpath)
        ev["comite"] = {"valorador_ciego": leer_valorador(vc, ev), "bajista": {"prob_desastre": pd_b, "veto": veto}}
        if len(sys.argv) > 4: ev["comite"]["error_documentado_valorador"] = sys.argv[4]
        escribir_ev(tpath, ev)
        c = evaluar(tpath).get("comite", {})
        def clean(s):  # rebaja los encabezados de los informes para que no rompan la estructura
            return re.sub(r"^#{1,3} ", "#### ", s.strip(), flags=re.M)
        bloque = (f"## Comité\n### 🔴 Bajista\n{clean(bj)}\n\n### 🔵 Valorador ciego\n{clean(vc)}\n\n### Reconciliación\n{texto_recon(ev, c)}\n\n")
        txt = open(tpath, encoding="utf-8").read()
        txt = re.sub(r"^## Comité\n.*?(?=^## Decisión)", lambda _: bloque, txt, flags=re.S | re.M)
        open(tpath, "w", encoding="utf-8").write(txt)
    vc = ev["comite"]["valorador_ciego"]; bj = ev["comite"]["bajista"]
    print(json.dumps({"ticker": ev["ticker"], "pd_bajista": bj.get("prob_desastre"), "veto": bj.get("veto"), "tir_valorador": vc.get("tir"),
                      "tir_valorador_neta": c.get("tir_valorador_neta"), "pd_valorador": vc.get("prob_desastre"),
                      "tir_propia_ajustada": c.get("tir_ajustada_propia"), "tir_final": c.get("tir_final"),
                      "pd_usada": c.get("prob_desastre_usada"), "asimetria": c.get("asimetria"), "cumple": c.get("cumple"),
                      "retornos": c.get("retornos_3a")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
