#!/usr/bin/env python3
"""Calculadora de EV y comprobación de reglas de compra.

Lee el bloque ```ev ... ``` (JSON) de una tesis (tesis/<TICKER>.md) o un JSON suelto y calcula:
  - retorno esperado a 3 años (incluye dividendos netos acumulados y costes de entrada/salida)
  - TIR anual esperada
  - asimetría (ganancia ponderada / pérdida ponderada)
  - si cumple las reglas de compra (config/reglas.json)
  - con --comite: reconciliación con los otros dos análisis del comité

Formato del bloque ev:
{
  "ticker": "ULVR.L", "mercado": "LONDRES", "pais": "GB",
  "precio_actual": 4930,              # en unidad de cotización (GBX en Londres)
  "fecha": "2026-11-07",
  "escenarios": {
     "desastre": {"prob": 0.10, "precio_3a": 3000, "dividendos_3a": 450, "relato": "..."},
     "bajista":  {"prob": 0.25, "precio_3a": 4300, "dividendos_3a": 480, "relato": "..."},
     "base":     {"prob": 0.45, "precio_3a": 6000, "dividendos_3a": 500, "relato": "..."},
     "alcista":  {"prob": 0.20, "precio_3a": 7200, "dividendos_3a": 520, "relato": "..."}
  },
  "comite": {                          # opcional, se rellena tras el comité
     "valorador_ciego": {"tir": 0.11, "prob_desastre": 0.15},
     "bajista": {"prob_desastre": 0.20, "veto": false}
  }
}
Los dividendos se introducen BRUTOS por acción; se aplica la retención en origen del país.
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import cartera as C

def extraer(path):
    txt = open(path, encoding="utf-8").read()
    m = re.search(r"```ev\s*\n(.*?)\n```", txt, re.S)
    if not m: sys.exit("No hay bloque ```ev``` en " + path)
    return json.loads(re.sub(r"\s#.*", "", m.group(1)))

def calcular(ev, prob_desastre_override=None):
    R = C.REGLAS["ev"]; mk = ev["mercado"]; m = C.MERCADOS[mk]
    fuera_euro = m["divisa"] != "EUR"
    p0 = float(ev["precio_actual"]); ret_div = C.FISC["retencion_dividendos"].get(ev["pais"], 0.0)
    # costes de ida y vuelta aproximados sobre una orden de ~500 €
    q = max(1, int(500 / (p0 * C.eur_por(m["unidad_precio"])))) if m.get("lote_minimo", 1) == 1 else m["lote_minimo"]
    ce = C.costes("COMPRA", mk, q, p0, ev["pais"]); cs = C.costes("VENTA", mk, q, p0, ev["pais"])
    coste_pct = (ce["total"] + cs["total"]) / ce["valor"]
    if fuera_euro:
        fx = C.coste_fx_eur(ce["valor"], m["divisa"]); coste_pct += 2 * (fx["comision_eur"] + fx["diferencial_eur"]) / fx["eur_base"]
    esc = {k: dict(v) for k, v in ev["escenarios"].items()}
    if prob_desastre_override is not None and prob_desastre_override > esc["desastre"]["prob"]:
        extra = prob_desastre_override - esc["desastre"]["prob"]
        esc["desastre"]["prob"] = prob_desastre_override
        # se resta proporcionalmente de los escenarios favorables
        fav = esc["base"]["prob"] + esc["alcista"]["prob"]
        for k in ("base", "alcista"): esc[k]["prob"] -= extra * esc[k]["prob"] / fav
    tot = sum(v["prob"] for v in esc.values())
    if abs(tot - 1) > 0.001: sys.exit(f"Las probabilidades suman {tot}, no 1")
    rets = {}
    for k, v in esc.items():
        rets[k] = (v["precio_3a"] + v.get("dividendos_3a", 0) * (1 - ret_div)) / p0 - 1 - coste_pct
    er = sum(esc[k]["prob"] * rets[k] for k in esc)
    tir = (1 + er) ** (1 / R["horizonte_anos"]) - 1 if er > -1 else -1
    gan = sum(esc[k]["prob"] * rets[k] for k in esc if rets[k] > 0)
    per = -sum(esc[k]["prob"] * rets[k] for k in esc if rets[k] < 0)
    asim = gan / per if per > 0 else float("inf")
    umbral = R["tir_min_fuera_euro"] if fuera_euro else R["tir_min_zona_euro"]
    checks = {
        f"TIR ≥ {umbral:.0%}": tir >= umbral,
        f"desastre ≥ {R['desastre_min_retorno']:.0%}": rets["desastre"] >= R["desastre_min_retorno"],
        f"asimetría ≥ {R['asimetria_min']}": asim >= R["asimetria_min"],
    }
    return {"retornos_3a": {k: round(v, 4) for k, v in rets.items()}, "probs": {k: round(v["prob"], 4) for k, v in esc.items()},
            "retorno_esperado_3a": round(er, 4), "tir": round(tir, 4), "asimetria": round(asim, 2) if asim != float("inf") else "inf",
            "coste_ida_vuelta_pct": round(coste_pct, 4), "umbral_tir": umbral, "cumple": checks, "compra_ok": all(checks.values())}

def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    path = sys.argv[1]
    ev = extraer(path) if path.endswith(".md") else json.load(open(path))
    propio = calcular(ev)
    out = {"ticker": ev["ticker"], "propio": propio}
    com = ev.get("comite")
    if com:
        vc = com.get("valorador_ciego", {}); bj = com.get("bajista", {})
        pd = max(ev["escenarios"]["desastre"]["prob"], vc.get("prob_desastre", 0), bj.get("prob_desastre", 0))
        ajust = calcular(ev, pd)
        tir_vc = vc.get("tir")
        if tir_vc is None: tir_final = ajust["tir"]; regla = "sin valorador ciego"
        elif abs(ajust["tir"] - tir_vc) < 0.05: tir_final = (ajust["tir"] + tir_vc) / 2; regla = "diferencia < 5 pp → media"
        else: tir_final = min(ajust["tir"], tir_vc); regla = "diferencia ≥ 5 pp → la más baja (salvo error documentado)"
        if com.get("error_documentado_valorador") and tir_vc is not None and tir_vc < ajust["tir"]:
            tir_final = ajust["tir"]; regla += " — se usa la propia por error documentado en el valorador"
        veto = bool(bj.get("veto"))
        umbral = ajust["umbral_tir"]
        checks = dict(ajust["cumple"]); checks[f"TIR comité ≥ {umbral:.0%}"] = tir_final >= umbral
        checks["sin veto del bajista"] = not veto
        out["comite"] = {"prob_desastre_usada": pd, "tir_ajustada_propia": ajust["tir"], "tir_valorador_ciego": tir_vc,
                         "tir_final": round(tir_final, 4), "regla": regla, "cumple": checks, "compra_ok": all(checks.values()),
                         "retornos_3a": ajust["retornos_3a"]}
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
