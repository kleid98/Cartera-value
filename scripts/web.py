#!/usr/bin/env python3
"""Genera panel/web.html: la web de seguimiento de la cartera (pedida por Ale el 17/11/2026).

Una sola página con los datos incrustados (no depende de nada externo salvo las fuentes):
resumen, evolución frente a los índices, posiciones con su tesis en pocas palabras y su precio
objetivo, reparto por país y sector, operaciones, órdenes, Investing pendiente, descartadas y
los últimos diarios.

Cada noche (ejecución CIERRE), después de `estado --cierre` y `panel.py`:
  python3 scripts/web.py   → panel/web.html
y republicar con Artifact (url en config/panel.json → "web").
"""
import csv, json, os, re, subprocess, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def leer(p, defecto=None):
    p = os.path.join(ROOT, p)
    if not os.path.exists(p):
        return defecto
    with open(p, encoding="utf-8") as f:
        return json.load(f) if p.endswith(".json") else f.read()


def en_pocas_palabras(ticker):
    txt = leer(f"tesis/{ticker}.md", "")
    m = re.search(r"## En pocas palabras\s*\n(.*?)(?=\n## |\Z)", txt, re.S)
    out = {}
    if m:
        for linea in m.group(1).splitlines():
            r = re.match(r"\s*-\s*\*\*(.+?):\*\*\s*(.+)", linea)
            if r:
                out[r.group(1).strip()] = r.group(2).strip()
    return out


def ev(ticker):
    p = os.path.join(ROOT, "tesis", f"{ticker}.md")
    if not os.path.exists(p):
        return {}
    try:
        out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts/ev.py"), p],
                             capture_output=True, text=True, timeout=120).stdout
        return json.loads(out)
    except Exception:
        return {}


def main():
    panel = leer("panel/panel.json", {})
    est = leer("ledger/cartera.json", {})
    reglas = leer("config/reglas.json", {})
    fin = set(reglas.get("grupos_de_riesgo", {}).get("financiero", {}).get("sectores", []))

    posiciones = []
    tir_panel = {p["ticker"]: p.get("tir_esperada") for p in panel.get("posiciones", [])}
    for p in est.get("posiciones", []):
        d = ev(p["ticker"])
        po = d.get("precio_objetivo") or {}
        precio = p.get("precio")
        base = po.get("base_3a")
        posiciones.append({
            "ticker": p["ticker"], "nombre": p["nombre"], "pais": p["pais"], "sector": p["sector"],
            "mercado": p["mercado"], "cantidad": p["cantidad"], "precio": precio,
            "precio_medio": p.get("precio_medio"), "unidad": p.get("unidad_precio"),
            "coste_eur": p["coste_eur"], "valor_eur": p["valor_eur"], "pyg_eur": p["pyg_eur"],
            "pyg_pct": p["pyg_pct"], "var_dia_pct": p.get("var_dia_pct"), "peso": p["peso"],
            "provisional": bool(p.get("provisional")), "financiero": p["sector"] in fin,
            "compra": (p.get("lotes") or [{}])[0].get("fecha", "")[:10],
            "dividendos_eur": p.get("dividendos_y_realizado_eur", 0),
            "tir": tir_panel.get(p["ticker"]),
            "objetivo": base, "esperado": po.get("esperado_3a"), "rango": po.get("rango_3a"),
            "potencial": (base / precio - 1) if base and precio else None,
            "resumen": en_pocas_palabras(p["ticker"]),
        })

    diarios = []
    for f in sorted(glob.glob(os.path.join(ROOT, "diario", "*.md")))[-7:][::-1]:
        diarios.append({"fecha": os.path.basename(f)[:-3], "texto": open(f, encoding="utf-8").read()})

    calendario = leer("plan/calendario.md", "")

    datos = {
        "resumen": (panel.get("resumen") or [{}])[0],
        "historico": panel.get("historico", []),
        "benchmarks": panel.get("benchmarks", []),
        "posiciones": posiciones,
        "operaciones": panel.get("operaciones", []),
        "ordenes": panel.get("ordenes", []),
        "investing": panel.get("investing", []),
        "descartadas": est.get("descartadas", []),
        "caja_por_divisa": est.get("caja_por_divisa", {}),
        "reglas": {
            "max_fin": reglas.get("grupos_de_riesgo", {}).get("financiero", {}).get("max_peso_para_nuevas", 0.3),
            "max_valores": reglas.get("max_valores", 20),
            "fecha_inicio": reglas.get("fecha_inicio", ""),
        },
        "diarios": diarios,
        "calendario": calendario,
    }
    plantilla = leer("panel/web_plantilla.html")
    js = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    html = plantilla.replace("/*__DATOS__*/null", js)
    with open(os.path.join(ROOT, "panel/web.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"panel/web.html: {len(posiciones)} posiciones, {len(diarios)} diarios, {len(html)//1024} KB")


if __name__ == "__main__":
    main()
