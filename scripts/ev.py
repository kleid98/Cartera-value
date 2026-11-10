#!/usr/bin/env python3
"""Calculadora de EV y comprobación de reglas de compra.

Lee el bloque ```ev ... ``` (JSON) de una tesis (tesis/<TICKER>.md) o un JSON suelto y calcula:
  - retorno esperado a 3 años (incluye dividendos netos acumulados y costes de entrada/salida)
  - TIR anual esperada
  - asimetría (ganancia ponderada / pérdida ponderada)
  - si cumple las reglas de compra (config/reglas.json)
  - si la tesis tiene comité: reconciliación con los otros dos análisis

Uso: python3 scripts/ev.py tesis/X.md [--precio P | --precio-hoy] [--ciego]
  --precio P     recalcula con otro precio de partida (escenarios y probabilidades no se tocan)
  --precio-hoy   igual, con el último precio de Yahoo (obligatorio justo antes de lanzar una orden)
  --ciego        solo retornos y TIR, sin umbrales ni veredicto (para el agente analista)

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
     "valorador_ciego": {"tir": 0.112, "prob_desastre": 0.15, "precio": 4930, "dividendos_esperados_3a": 480},
                                       # tir BRUTA y exacta (3 decimales) al precio que vio el valorador
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
    if prob_desastre_override is not None and abs(prob_desastre_override - esc["desastre"]["prob"]) > 1e-9:
        extra = prob_desastre_override - esc["desastre"]["prob"]  # puede ser negativo (media < propia)
        esc["desastre"]["prob"] = prob_desastre_override
        # la diferencia se resta (o se suma) proporcionalmente a los escenarios favorables
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
    div_esp = sum(esc[k]["prob"] * esc[k].get("dividendos_3a", 0) for k in esc)  # bruto, en unidad de cotización
    return {"retornos_3a": {k: round(v, 4) for k, v in rets.items()}, "probs": {k: round(v["prob"], 4) for k, v in esc.items()},
            "retorno_esperado_3a": round(er, 4), "tir": round(tir, 4), "asimetria": round(asim, 2) if asim != float("inf") else "inf",
            "coste_ida_vuelta_pct": round(coste_pct, 4), "umbral_tir": umbral, "cumple": checks, "compra_ok": all(checks.values()),
            "_div_esperado_bruto": div_esp, "_retencion_div": ret_div}

def tir_neta_valorador(vc, ajust, precio, precio_tesis):
    """TIR del valorador ciego puesta en las mismas condiciones que la propia (regla del 09/11/2026):
    1) se recalcula al precio de hoy (el valorador la dio BRUTA a su precio: valor final = precio_vc × (1+TIR)^3);
    2) se restan los costes de ida y vuelta y la retención en origen de los dividendos.
    Si el informe no trae los dividendos esperados, se usan los de la tesis propia como aproximación."""
    n = C.REGLAS["ev"]["horizonte_anos"]
    p_vc = float(vc.get("precio") or precio_tesis)
    valor_final = p_vc * (1 + vc["tir"]) ** n
    div = vc.get("dividendos_esperados_3a")
    if div is None: div = ajust["_div_esperado_bruto"]
    r = valor_final / precio - 1 - ajust["coste_ida_vuelta_pct"] - ajust["_retencion_div"] * div / precio
    return (1 + r) ** (1 / n) - 1 if r > -1 else -1

def limpio(d): return {k: v for k, v in d.items() if not k.startswith("_")}

def precio_objetivo(ev, probs, p0):
    """Precio objetivo a 3 años (pedido por Ale el 10/11/2026). No es una regla nueva: son los precios de los escenarios
    de la tesis, sin tocar. base_3a = precio del escenario central (el "objetivo"); esperado_3a = media ponderada de los
    cuatro escenarios con las probabilidades que se usan para la TIR (las del comité si lo hay)."""
    esc = ev["escenarios"]; base = float(esc["base"]["precio_3a"])
    esp = sum(probs[k] * esc[k]["precio_3a"] for k in esc)
    div = sum(probs[k] * esc[k].get("dividendos_3a", 0) for k in esc)
    return {"unidad": C.MERCADOS[ev["mercado"]]["unidad_precio"], "base_3a": base, "potencial_base": round(base / p0 - 1, 4),
            "esperado_3a": round(esp, 2), "potencial_esperado": round(esp / p0 - 1, 4), "dividendos_esperados_3a": round(div, 2),
            "rango_3a": [esc["desastre"]["precio_3a"], esc["alcista"]["precio_3a"]]}

def evaluar(ev, precio=None):
    """Evaluación completa de una tesis. precio: precio de partida alternativo (p. ej. el de hoy)."""
    precio_tesis = float(ev["precio_actual"])
    if precio is not None: ev = dict(ev, precio_actual=float(precio))
    p0 = float(ev["precio_actual"])
    propio = calcular(ev)
    out = {"ticker": ev["ticker"], "precio_usado": p0, "precio_tesis": precio_tesis, "propio": limpio(propio)}
    com = ev.get("comite") or {}
    vc = com.get("valorador_ciego") or {}; bj = com.get("bajista") or {}
    if vc.get("tir") is not None or vc.get("prob_desastre") is not None or bj.get("prob_desastre") is not None:
        RC = C.REGLAS["comite"]
        pds = [ev["escenarios"]["desastre"]["prob"]] + [x for x in (vc.get("prob_desastre"), bj.get("prob_desastre")) if x is not None]
        # Regla acordada con Ale el 09/11/2026: media de las tres (antes: la más alta)
        pd = round(sum(pds) / len(pds), 4) if RC.get("prob_desastre_modo", "max") == "media" else max(pds)
        ajust = calcular(ev, pd)
        tir_vc = vc.get("tir"); tir_vc_neta = None
        if tir_vc is None: tir_final = ajust["tir"]; regla = "sin valorador ciego"
        else:
            tir_vc_neta = tir_neta_valorador(vc, ajust, p0, precio_tesis) if RC.get("tir_valorador_neta", False) else tir_vc
            baja, media = min(ajust["tir"], tir_vc_neta), (ajust["tir"] + tir_vc_neta) / 2
            tope = RC.get("tope_sobre_la_mas_baja_pp")
            if abs(ajust["tir"] - tir_vc_neta) < 0.05: tir_final = media; regla = "diferencia < 5 pp → media"
            elif tope is not None: tir_final = baja + tope / 100; regla = f"diferencia ≥ 5 pp → la más baja + {tope} pp (tope)"
            else: tir_final = baja; regla = "diferencia ≥ 5 pp → la más baja (salvo error documentado)"
            if com.get("error_documentado_valorador") and tir_vc_neta < ajust["tir"]:
                tir_final = ajust["tir"]; regla += " — se usa la propia por error documentado en el valorador"
        veto = bool(bj.get("veto"))
        umbral = ajust["umbral_tir"]
        checks = dict(ajust["cumple"]); checks[f"TIR comité ≥ {umbral:.0%}"] = tir_final >= umbral
        checks["sin veto del bajista"] = not veto
        out["comite"] = {"prob_desastre_usada": pd, "tir_ajustada_propia": ajust["tir"], "tir_valorador_ciego": tir_vc,
                         "tir_valorador_neta": round(tir_vc_neta, 4) if tir_vc_neta is not None else None,
                         "tir_final": round(tir_final, 4), "regla": regla, "cumple": checks, "compra_ok": all(checks.values()),
                         "asimetria": ajust["asimetria"], "retornos_3a": ajust["retornos_3a"], "probs": ajust["probs"]}
    out["precio_objetivo"] = precio_objetivo(ev, (out.get("comite") or out["propio"])["probs"], p0)
    return out

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if not args: sys.exit(__doc__)
    path = args[0]
    ev = extraer(path) if path.endswith(".md") else json.load(open(path))
    precio = None
    if "--precio-hoy" in flags: precio = C.cotizacion(ev["ticker"])["precio"]
    elif "--precio" in flags: precio = float(args[1])
    out = evaluar(ev, precio)
    if "--ciego" in flags:
        pr = out["propio"]
        out = {"ticker": out["ticker"], "retornos_3a": pr["retornos_3a"], "probs": pr["probs"],
               "retorno_esperado_3a": pr["retorno_esperado_3a"], "tir": pr["tir"], "asimetria": pr["asimetria"],
               "coste_ida_vuelta_pct": pr["coste_ida_vuelta_pct"]}
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
