#!/usr/bin/env python3
"""Ficha de entrada o de salida de una posición: por qué se compra o se vende y con qué precio objetivo.
(Pedido por Ale el 10/11/2026: quiere la explicación cada vez que se entra o se sale de un valor.)

Uso:
  python3 scripts/ficha.py tesis/X.md [--precio P | --precio-hoy]                         ficha de ENTRADA
  python3 scripts/ficha.py tesis/X.md --venta --motivo "..." [--precio P | --precio-hoy]  ficha de SALIDA
  python3 scripts/ficha.py --comprobar [tesis/X.md ...]      qué tesis tienen (o no) la sección "En pocas palabras"

`cartera.py orden` la genera sola al lanzar cada orden (y no deja comprar si la tesis no tiene el resumen); el gestor la
pega en el diario y usa su línea de objetivo en el aviso al móvil. `cartera.py investing` añade el porqué a cada operación.

La ficha no decide nada ni cambia ninguna regla: el texto sale de la sección "## En pocas palabras" de la tesis y los
números de `ev.py` (precios de los escenarios y probabilidades ya escritos, al precio de la orden).
  · Precio objetivo = precio a 3 años del escenario central (base).
  · Precio esperado = media de los cuatro escenarios ponderada por su probabilidad (es el que da la TIR).
"""
import glob, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import cartera as C
import ev as E

CLAVES = ["Qué es", "Por qué está barata", "Qué espero", "Qué me haría vender"]
ESC = [("desastre", "🐻 Desastre"), ("bajista", "📉 Bajista"), ("base", "⚖️ Base"), ("alcista", "🚀 Alcista")]

class FaltaResumen(Exception): pass

def resumen(txt):
    """Lee la sección '## En pocas palabras' de una tesis → {clave: texto}. None si no existe."""
    m = re.search(r"^## En pocas palabras[^\n]*\n(.*?)(?=^## |\Z)", txt, re.S | re.M)
    if not m: return None
    out = {}
    for l in m.group(1).splitlines():
        mm = re.match(r"\s*[-*]\s*\*\*(.+?)\*\*:?\s*(.+)", l)
        if mm: out[mm.group(1).strip().rstrip(":").strip()] = mm.group(2).strip()
    return out or None

def faltan(path):
    r = resumen(open(path, encoding="utf-8").read()) or {}
    return [k for k in CLAVES if not r.get(k)]

def px(x, u):
    """Precio legible: 587,4 p · 23,45 € · 1.250 JPY."""
    x = float(x); dec = 0 if u == "JPY" or abs(x) >= 1000 or (abs(x) >= 100 and x == int(x)) else 1 if u == "GBX" or abs(x) >= 100 else 2
    return C.fmt_num(x, dec) + {"GBX": " p", "EUR": " €"}.get(u, " " + u)

def pct(x, dec=1):
    s = C.fmt_num(abs(x) * 100, dec) + "%"
    return ("+" if x >= 0 else "−") + s

def _leer(path, precio):
    txt = open(path, encoding="utf-8").read()
    r = E.evaluar(E.extraer(path), precio)
    nombre = re.match(r"# (.+?) \(", txt).group(1).strip()
    return txt, r, nombre

def linea_objetivo(r):
    po = r["precio_objetivo"]
    return f"Objetivo 3 años {px(po['base_3a'], po['unidad'])} ({pct(po['potencial_base'])})"

def ficha_compra(path, precio=None):
    """Devuelve (ficha en markdown, línea corta con el objetivo). FaltaResumen si la tesis no tiene 'En pocas palabras'."""
    txt, r, nombre = _leer(path, precio)
    res = resumen(txt) or {}; f = [k for k in CLAVES if not res.get(k)]
    if f: raise FaltaResumen(f"{os.path.relpath(path, ROOT)}: falta la sección '## En pocas palabras' ({', '.join(f)}). "
                             "Escríbela (plantillas/tesis.md) antes de lanzar la orden: Ale quiere el porqué de cada entrada.")
    po = r["precio_objetivo"]; u = po["unidad"]; p0 = r["precio_usado"]
    c = r.get("comite") or r["propio"]; tir = c.get("tir_final", c.get("tir")); umbral = r["propio"]["umbral_tir"]
    L = [f"#### 🟢 Entrada · {nombre} ({r['ticker']})"] + [f"- **{k}:** {res[k]}" for k in CLAVES] + [""]
    L.append(f"**Precio objetivo a 3 años: {px(po['base_3a'], u)} ({pct(po['potencial_base'])} desde {px(p0, u)})**, el del escenario "
             f"central. Ponderando los cuatro escenarios sale {px(po['esperado_3a'], u)} ({pct(po['potencial_esperado'])}), más unos "
             f"{px(po['dividendos_esperados_3a'], u)} de dividendos brutos por acción.")
    L += ["", "| Escenario | Probabilidad | Precio a 3 años | Retorno total* |", "|---|---|---|---|"]
    esc = E.extraer(path)["escenarios"]
    for k, et in ESC:
        L.append(f"| {et} | {c['probs'][k] * 100:.0f}% | {px(esc[k]['precio_3a'], u)} | {pct(c['retornos_3a'][k])} |")
    L += ["", "*Con dividendos netos de retención y costes de compra y venta, en los 3 años.", ""]
    veredicto = (f"supera el umbral del {umbral:.0%}" if tir >= umbral else
                 f"por debajo del umbral del {umbral:.0%}: solo puede entrar como 🟡 provisional")
    L.append(f"**TIR esperada: {C.fmt_num(tir * 100, 1)}% anual** ({'con comité' if r.get('comite') else 'sin comité todavía'}; {veredicto}). "
             f"Peor escenario: {pct(c['retornos_3a']['desastre'])}.")
    return "\n".join(L), linea_objetivo(r)

def ficha_venta(path, motivo, precio=None, ops=None):
    """Ficha de salida. Usa el libro (precio medio de compra) y, si existe, lo que se predijo al comprar."""
    txt, r, nombre = _leer(path, precio)
    res = resumen(txt) or {}; po = r["precio_objetivo"]; u = po["unidad"]; p0 = r["precio_usado"]; t = r["ticker"]
    c = r.get("comite") or r["propio"]; tir = c.get("tir_final", c.get("tir"))
    L = [f"#### 🔴 Salida · {nombre} ({t})", f"- **Por qué vendo:** {motivo}"]
    compras = [o for o in (ops if ops is not None else C.operaciones()) if o["tipo"] == "COMPRA" and o["ticker"] == t]
    if compras:
        q = sum(float(o["cantidad"]) for o in compras); pm = sum(float(o["precio"]) * float(o["cantidad"]) for o in compras) / q
        f0 = compras[0]["fecha_hora"][:10]; f0 = f"{f0[8:10]}/{f0[5:7]}/{f0[:4]}"
        L.append(f"- **Resultado:** comprada a {px(pm, u)} de media (primera compra el {f0}) y vendida a {px(p0, u)}: "
                 f"{pct(p0 / pm - 1)} en precio. Sin dividendos, costes ni divisa: la cifra exacta en euros está en el ledger.")
    pred = [p for p in C.read_csv("ledger/predicciones.csv", C.PRED_F) if p["ticker"] == t] if os.path.exists(C.P("ledger/predicciones.csv")) else []
    if pred:
        p = pred[-1]; tc = p.get("tir_comite") or p.get("tir_propia")
        L.append(f"- **Qué esperaba al comprar:** objetivo de {px(p['precio_3a_base'], u)} a 3 años y una TIR del "
                 f"{C.fmt_num(float(tc) * 100, 1)}% anual." + (f" La idea era: {res['Qué espero']}" if res.get("Qué espero") else ""))
    elif res.get("Qué espero"):
        L.append(f"- **Qué esperaba al comprar:** {res['Qué espero']}")
    L.append(f"- **Qué quedaba a este precio:** el objetivo de la tesis es {px(po['base_3a'], u)} ({pct(po['potencial_base'])}) y la TIR "
             f"esperada, {C.fmt_num(tir * 100, 1)}% anual.")
    return "\n".join(L)

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Ficha de entrada o de salida de una posición")
    ap.add_argument("tesis", nargs="*"); ap.add_argument("--venta", action="store_true"); ap.add_argument("--motivo", default="(sin motivo)")
    ap.add_argument("--precio", type=float); ap.add_argument("--precio-hoy", action="store_true"); ap.add_argument("--comprobar", action="store_true")
    a = ap.parse_args()
    if a.comprobar:
        mal = 0
        for p in (a.tesis or sorted(glob.glob(os.path.join(ROOT, "tesis", "*.md")))):
            f = faltan(p); mal += bool(f)
            print(("✅ " if not f else "❌ ") + os.path.relpath(os.path.abspath(p), ROOT) + ("" if not f else "  falta: " + ", ".join(f)))
        sys.exit(1 if mal and a.tesis else 0)
    if not a.tesis: sys.exit(__doc__)
    path = a.tesis[0]; precio = a.precio
    if a.precio_hoy: precio = C.cotizacion(E.extraer(path)["ticker"])["precio"]
    try:
        print(ficha_venta(path, a.motivo, precio) if a.venta else ficha_compra(path, precio)[0])
    except FaltaResumen as e: sys.exit(str(e))

if __name__ == "__main__":
    main()
