#!/usr/bin/env python3
"""Genera panel/panel.json: el único fichero de datos del panel (Artifact Dashboard).

Cada noche (ejecución CIERRE):
  1) python3 scripts/cartera.py estado --cierre
  2) python3 scripts/panel.py
  3) subir panel/panel.json como asset del dashboard y actualizar los datasets (ver CLAUDE.md §5).
"""
import csv, json, os, re, subprocess, sys
from datetime import datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import cartera as C

def tir_tesis(ticker):
    p = os.path.join(ROOT, "tesis", f"{ticker}.md")
    if not os.path.exists(p): return None
    try:
        out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts/ev.py"), p], capture_output=True, text=True, timeout=120).stdout
        d = json.loads(out)
        return (d.get("comite") or {}).get("tir_final", d["propio"]["tir"])
    except Exception:
        return None

def main():
    est = json.load(open(os.path.join(ROOT, "ledger/cartera.json"))) if os.path.exists(os.path.join(ROOT, "ledger/cartera.json")) else {}
    ops = C.operaciones(); ords = C.ordenes()
    bm = est.get("benchmarks", {})
    principal = bm.get("principal", {}).get("rent")
    resumen = [{
        "actualizado": est.get("actualizado", ""), "valor_total_eur": est.get("valor_total_eur", C.REGLAS["capital_inicial_eur"]),
        "aportado_eur": est.get("aportado_eur", C.REGLAS["capital_inicial_eur"]), "rentabilidad": est.get("rentabilidad", 0.0),
        "caja_eur": est.get("caja_eur", C.REGLAS["capital_inicial_eur"]), "invertido_eur": est.get("invertido_eur", 0.0),
        "n_posiciones": est.get("n_posiciones", 0), "max_posiciones": C.REGLAS["max_valores"],
        "rent_bench_principal": principal, "alfa": (est.get("rentabilidad", 0.0) - principal) if principal is not None else None,
        "n_provisionales": sum(1 for p in est.get("posiciones", []) if p.get("provisional")),
        "pendientes_investing": 0,
    }]
    hist = []
    hp = os.path.join(ROOT, "ledger/historico.csv")
    if os.path.exists(hp):
        for h in csv.DictReader(open(hp)):
            a = float(h["aportado_eur"] or 1)
            row = {"fecha": h["fecha"], "cartera": round(float(h["valor_total_eur"]) / a - 1, 5)}
            for k in C.REGLAS["benchmarks"]:
                v = h.get(f"bench_{k}")
                row[k] = round(float(v) / a - 1, 5) if v else None
            hist.append(row)
    posiciones = []
    for p in est.get("posiciones", []):
        posiciones.append({"ticker": p["ticker"], "nombre": p["nombre"], "mercado": p["mercado"], "pais": p["pais"], "sector": p["sector"],
                           "estado": "Provisional" if p["provisional"] else "Definitiva", "cantidad": p["cantidad"],
                           "coste_eur": p["coste_eur"], "valor_eur": p["valor_eur"], "pyg_eur": p["pyg_eur"], "pyg_pct": p["pyg_pct"],
                           "var_dia_pct": p.get("var_dia_pct"), "peso": p["peso"], "tir_esperada": tir_tesis(p["ticker"])})
    operaciones = [{"id": o["id"], "fecha": o["fecha_hora"], "tipo": o["tipo"], "nombre": o["nombre"] or ("Divisa " + o["divisa"] if o["tipo"] == "FX" else "Capital inicial"),
                    "ticker": o["ticker"], "cantidad": float(o["cantidad"]) if o["cantidad"] else None,
                    "precio": float(o["precio"]) if o["precio"] else None, "unidad": o["unidad_precio"],
                    "importe_eur": float(o["importe_eur"] or 0), "motivo": o["nota"]} for o in ops][-40:][::-1]
    ordenes = [{"id": o["id"], "creada": o["creada"], "lado": o["lado"], "nombre": o["nombre"], "ticker": o["ticker"],
                "cantidad": float(o["cantidad"]), "limite": float(o["limite"]), "tipo": o["tipo"], "estado": o["estado"],
                "motivo": o["motivo"]} for o in ords if o["estado"] == "PENDIENTE" or o["creada"][:10] >= (datetime.now(C.MAD).strftime("%Y-%m-%d"))][::-1]
    pasadas = set(json.load(open(os.path.join(ROOT, "investing/estado.json")))["pasadas"]) if os.path.exists(os.path.join(ROOT, "investing/estado.json")) else set()
    investing = []
    for o in ops:
        if o["tipo"] not in ("COMPRA", "VENTA") or o["id"] in pasadas: continue
        m = C.MERCADOS[o["mercado"]]
        investing.append({"id": o["id"], "fecha": datetime.strptime(o["fecha_hora"][:10], "%Y-%m-%d").strftime("%d/%m/%Y"),
                          "tipo": "Compra" if o["tipo"] == "COMPRA" else "Venta (cerrar FIFO)", "nombre": o["nombre"], "bolsa": m["investing"],
                          "cantidad": float(o["cantidad"]), "precio": float(o["precio"]), "unidad": o["unidad_precio"],
                          "comision": float(o["costes_total_divisa"]), "divisa_comision": o["divisa"]})
    resumen[0]["pendientes_investing"] = len(investing)
    bench = [{"clave": k, "nombre": b["nombre"], "ticker": b["ticker"], "rent": bm.get(k, {}).get("rent")} for k, b in C.REGLAS["benchmarks"].items()]
    out = {"resumen": resumen, "historico": hist, "posiciones": posiciones, "operaciones": operaciones, "ordenes": ordenes,
           "investing": investing, "benchmarks": bench}
    os.makedirs(os.path.join(ROOT, "panel"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "panel/panel.json"), "w"), ensure_ascii=False, indent=1)
    print(f"panel/panel.json: {len(posiciones)} posiciones, {len(hist)} días, {len(investing)} pendientes Investing")

if __name__ == "__main__":
    main()
