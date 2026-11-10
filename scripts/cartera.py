#!/usr/bin/env python3
"""Motor de la cartera VALUE ex-USA (simulación IBKR).

Solo librería estándar. Fuente de verdad: ledger/*.csv (solo se añaden filas).

Subcomandos principales:
  precio TICKER                     último precio, divisa, máximos/mínimos del día
  libro ISIN MERCADO                mejor bid/ask de Equiduct (si cubre el valor)
  orden ...                         crea una orden limitada simulada (PENDIENTE)
  validar                           comprueba ejecuciones con velas de 1 minuto / caduca órdenes
  anular ID --motivo ...            anula una orden pendiente
  dividendos                        registra dividendos netos de retención en origen
  estado [--cierre]                 valora la cartera, escribe ledger/cartera.json (+ histórico si --cierre)
  investing                         regenera investing/pendiente.md
  investing-marcar ID [ID...]       marca operaciones como pasadas a Investing
  costes ...                        simula costes de una orden sin crearla

Todas las horas se registran en Europe/Madrid.
"""
import argparse, csv, json, math, os, subprocess, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAD = ZoneInfo("Europe/Madrid")
UA = {"User-Agent": "Mozilla/5.0"}  # el UA largo de navegador provoca 429 en Yahoo

def P(*a): return os.path.join(ROOT, *a)
def load(path): return json.load(open(P(path), encoding="utf-8"))
REGLAS = load("config/reglas.json")
MERCADOS = {k: v for k, v in load("config/mercados.json").items() if not k.startswith("_")}
FISC = load("config/fiscalidad.json")
MIC = {"XETRA": "XETR", "PARIS": "XPAR", "AMSTERDAM": "XAMS", "BRUSELAS": "XBRU", "LISBOA": "XLIS",
       "MILAN": "MTAA", "MADRID": "XMAD", "VIENA": "XWBO", "HELSINKI": "XHEL", "DUBLIN": "XDUB",
       "LONDRES": "XLON", "ZURICH": "XSWX/XVTX", "ESTOCOLMO": "XSTO", "COPENHAGUE": "XCSE", "OSLO": "XOSL"}

ORD_F = ["id", "creada", "lado", "ticker", "nombre", "isin", "mercado", "pais_emisor", "sector", "cantidad",
         "limite", "tipo", "fuente_precio", "ultimo_al_crear", "provisional", "motivo", "tesis", "estado",
         "resuelta", "precio_ejec", "nota"]
OP_F = ["id", "fecha_hora", "tipo", "orden_id", "ticker", "nombre", "isin", "mercado", "pais_emisor", "sector",
        "divisa", "cantidad", "precio", "unidad_precio", "importe_divisa", "comision_ibkr", "tasas_terceros",
        "impuesto_transaccion", "costes_total_divisa", "fx_eur_por_unidad", "importe_eur", "provisional", "nota"]

def now(): return datetime.now(MAD)
def iso(dt): return dt.astimezone(MAD).strftime("%Y-%m-%d %H:%M:%S")
def parse(s): return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=MAD)
def r2(x): return round(x + 0.0, 2)

# ---------------------------------------------------------------- CSV helpers
def read_csv(path, fields):
    p = P(path)
    if not os.path.exists(p):
        with open(p, "w", newline="", encoding="utf-8") as f: csv.writer(f).writerow(fields)
        return []
    with open(p, newline="", encoding="utf-8") as f: return list(csv.DictReader(f))

def append_csv(path, fields, row):
    read_csv(path, fields)
    with open(P(path), "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fields).writerow({k: row.get(k, "") for k in fields})

def rewrite_csv(path, fields, rows):
    with open(P(path), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in rows: w.writerow({k: r.get(k, "") for k in fields})

def ordenes(): return read_csv("ledger/ordenes.csv", ORD_F)
def operaciones(): return read_csv("ledger/operaciones.csv", OP_F)
def next_id(rows, prefix):
    n = max([int(r["id"].split("-")[-1]) for r in rows if r["id"].startswith(prefix)] + [0]) + 1
    return f"{prefix}{n:04d}"

# ---------------------------------------------------------------- datos de mercado
def http_json(url, tries=4):
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except Exception as e:  # 429 de Yahoo: reintentar con espera
            last = e; time.sleep(3 * 2 ** i)
    raise RuntimeError(f"Fallo al descargar {url}: {last}")

def yahoo_chart(ticker, rng="1d", interval="1m", events=False):
    q = f"range={rng}&interval={interval}" + ("&events=div" if events else "")
    for host in ("query2", "query1"):
        try:
            d = http_json(f"https://{host}.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}?{q}")
            return d["chart"]["result"][0]
        except Exception as e:
            err = e
    raise err

def yahoo_chart_period(ticker, t0, t1, interval="1d", events=False):
    q = f"period1={int(t0)}&period2={int(t1)}&interval={interval}" + ("&events=div" if events else "")
    d = http_json(f"https://query2.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}?{q}")
    return d["chart"]["result"][0]

def cotizacion(ticker):
    r = yahoo_chart(ticker, "1d", "1m")
    m = r["meta"]
    return {"ticker": ticker, "precio": m.get("regularMarketPrice"), "divisa_yahoo": m.get("currency"),
            "max": m.get("regularMarketDayHigh"), "min": m.get("regularMarketDayLow"),
            "cierre_anterior": m.get("chartPreviousClose") or m.get("previousClose"),
            "hora": iso(datetime.fromtimestamp(m.get("regularMarketTime", 0), MAD)), "bolsa": m.get("exchangeName")}

_FX = None
def fx_eur():
    """Unidades de divisa por 1 EUR (BCE vía Frankfurter). Cacheado por día en data/fx."""
    global _FX
    if _FX: return _FX
    path = P("data/fx", now().strftime("%Y-%m-%d") + ".json")
    if os.path.exists(path):
        _FX = json.load(open(path)); return _FX
    d = http_json("https://api.frankfurter.dev/v1/latest?base=EUR")
    rates = d["rates"]; rates["EUR"] = 1.0; rates["_fecha"] = d.get("date")
    json.dump(rates, open(path, "w"), indent=1); _FX = rates
    return rates

def eur_por(divisa):
    """EUR por 1 unidad de divisa (GBX -> por penique)."""
    if divisa == "EUR": return 1.0
    if divisa == "GBX": return 1.0 / fx_eur()["GBP"] / 100.0
    return 1.0 / fx_eur()[divisa]

def libro_equiduct(isin, mercado, fecha=None):
    mic = MIC.get(mercado)
    if not mic or not isin: return {"ok": False, "error": "mercado no cubierto por Equiduct"}
    env = dict(os.environ)
    try:
        npm_root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=30).stdout.strip()
        env["NODE_PATH"] = npm_root
    except Exception: pass
    cmd = ["node", P("scripts/equiduct.js"), isin, mic] + ([fecha] if fecha else [])
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=150, env=env).stdout.strip().splitlines()
        return json.loads(out[-1]) if out else {"ok": False, "error": "sin salida"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

# ---------------------------------------------------------------- costes
def a_divisa(precio, mercado):
    """Convierte un precio en unidad de cotización a la divisa de liquidación (GBX->GBP)."""
    return precio / 100.0 if MERCADOS[mercado]["unidad_precio"] == "GBX" else precio

def costes(lado, mercado, cantidad, precio, pais_emisor):
    m = MERCADOS[mercado]
    valor = a_divisa(precio, mercado) * cantidad  # en divisa de liquidación
    if "por_accion" in m:
        com = max(m["min"], m["por_accion"] * cantidad); com = min(com, m["max_pct"] * valor)
    else:
        com = max(m["min"], m["pct"] * valor)
        if m.get("max"): com = min(com, m["max"])
    tasas = 0.0 if "Fixed" in m["plan"] else 0.0001 * valor  # estimación bolsa+compensación (pass-through Tiered)
    imp = 0.0
    if lado == "COMPRA":
        t = FISC["impuesto_transaccion_compra"].get(pais_emisor)
        if t: imp = t["pct"] * valor
    return {"valor": valor, "comision_ibkr": r2(com), "tasas_terceros": r2(tasas), "impuesto_transaccion": r2(imp),
            "total": r2(com + tasas + imp)}

def coste_fx_eur(importe_divisa, divisa):
    """EUR necesarios para obtener importe_divisa (conversión manual IdealPro) y desglose."""
    base = importe_divisa * eur_por(divisa)
    spread = base * FISC["fx"]["diferencial_pct"]
    usd_por_eur = fx_eur()["USD"]
    comision = max(FISC["fx"]["comision_min_usd"] / usd_por_eur, base * FISC["fx"]["comision_pct"])
    return {"eur_base": base, "diferencial_eur": spread, "comision_eur": comision, "total_eur": base + spread + comision}

# ---------------------------------------------------------------- cartera derivada
def derivar(ops=None):
    """Lotes FIFO por ticker y caja por divisa a partir de operaciones."""
    ops = ops if ops is not None else operaciones()
    lotes, caja, info, realizado = {}, {}, {}, {}
    for o in ops:
        t, d = o["tipo"], o["divisa"]
        imp = float(o["importe_divisa"] or 0); cst = float(o["costes_total_divisa"] or 0)
        if t == "APORTACION":
            caja[d] = caja.get(d, 0) + imp
        elif t == "FX":  # importe_divisa = divisa recibida; importe_eur = EUR pagados (incl. costes)
            caja[d] = caja.get(d, 0) + imp; caja["EUR"] = caja.get("EUR", 0) - float(o["importe_eur"])
        elif t == "DIVIDENDO":
            caja[d] = caja.get(d, 0) + imp
            realizado.setdefault(o["ticker"], 0); realizado[o["ticker"]] += float(o["importe_eur"])
        elif t == "COMPRA":
            caja[d] = caja.get(d, 0) - imp - cst
            q = float(o["cantidad"])
            lotes.setdefault(o["ticker"], []).append({"op": o["id"], "fecha": o["fecha_hora"], "cantidad": q,
                "precio": float(o["precio"]), "coste_eur": float(o["importe_eur"]), "provisional": o["provisional"]})
            info[o["ticker"]] = {k: o[k] for k in ("nombre", "isin", "mercado", "pais_emisor", "sector", "divisa", "unidad_precio")}
        elif t == "VENTA":
            caja[d] = caja.get(d, 0) + imp - cst
            q = float(o["cantidad"]); ingreso_eur = float(o["importe_eur"]); coste_salida = 0.0
            for l in lotes.get(o["ticker"], []):
                if q <= 1e-9: break
                if l["cantidad"] <= 1e-9: continue
                take = min(q, l["cantidad"]); frac = take / l["cantidad"]
                coste_salida += l["coste_eur"] * frac; l["coste_eur"] -= l["coste_eur"] * frac
                l["cantidad"] -= take; q -= take
            realizado.setdefault(o["ticker"], 0); realizado[o["ticker"]] += ingreso_eur - coste_salida
    for t in list(lotes):
        lotes[t] = [l for l in lotes[t] if l["cantidad"] > 1e-9]
        if not lotes[t]: del lotes[t]
    return lotes, {k: v for k, v in caja.items() if abs(v) > 1e-6}, info, realizado

def lotes_fifo_a_cerrar(ticker, cantidad, ops=None):
    lotes, _, _, _ = derivar(ops)
    out, q = [], cantidad
    for l in lotes.get(ticker, []):
        if q <= 0: break
        take = min(q, l["cantidad"]); out.append((l["fecha"][:10], take, l["cantidad"])); q -= take
    return out

# ---------------------------------------------------------------- órdenes
def tick_size(precio, unidad):
    """Salto mínimo de precio. Europa: tabla MiFID II (RTS 11), banda de liquidez 5 (valores grandes),
    sobre el precio en la unidad de cotización (peniques en Londres). Antes se usaba 0,5 para todo GBX,
    que en valores de menos de 200p desplazaba el límite hasta un 0,5%."""
    if unidad == "JPY": return 1.0
    if unidad == "CAD": return 0.01 if precio >= 0.5 else 0.005
    for tope, t in ((0.5, 0.0001), (1, 0.0002), (2, 0.0005), (5, 0.001), (10, 0.002), (20, 0.005), (50, 0.01),
                    (100, 0.02), (200, 0.05), (500, 0.1), (1000, 0.2), (2000, 0.5), (5000, 1.0), (10000, 2.0)):
        if precio < tope: return t
    return 5.0

def caja_libre_eur(ords=None, ops=None):
    """Caja total en EUR menos lo comprometido en órdenes de compra pendientes (valor + costes + FX)."""
    _, caja, _, _ = derivar(ops)
    libre = sum(v * eur_por(d) for d, v in caja.items())
    for o in (ords if ords is not None else ordenes()):
        if o["estado"] == "PENDIENTE" and o["lado"] == "COMPRA":
            libre -= coste_compra_eur(o["mercado"], float(o["cantidad"]), float(o["limite"]), o["pais_emisor"])
    return libre

def grupo_saturado(ticker, sector, ops=None):
    """Tras la Fase 0 no entra un valor NUEVO de un grupo de riesgo cuyo peso a coste supere su máximo (reglas.json)."""
    if now().strftime("%Y-%m-%d") <= REGLAS["fase0"]["fin"]: return None
    lotes, caja, info, _ = derivar(ops)
    if ticker in lotes: return None
    total = sum(l["coste_eur"] for ls in lotes.values() for l in ls) + sum(v * eur_por(d) for d, v in caja.items())
    for nombre, g in REGLAS.get("grupos_de_riesgo", {}).items():
        if not isinstance(g, dict) or "max_peso_para_nuevas" not in g or sector not in g.get("sectores", []): continue
        peso = sum(l["coste_eur"] for t, ls in lotes.items() if info[t]["sector"] in g["sectores"] for l in ls) / total if total else 0
        if peso > g["max_peso_para_nuevas"]:
            return (f"No entra: el grupo '{nombre}' pesa {peso:.0%} a coste (máximo {g['max_peso_para_nuevas']:.0%} para valores nuevos). "
                    f"Regla acordada con Ale el 09/11/2026.")
    return None

def coste_compra_eur(mercado, q, limite, pais):
    m = MERCADOS[mercado]; c = costes("COMPRA", mercado, q, limite, pais)
    eur = (c["valor"] + c["total"]) * eur_por(m["divisa"])
    if m["divisa"] != "EUR":
        fx = coste_fx_eur(c["valor"] + c["total"], m["divisa"]); eur += fx["diferencial_eur"] + fx["comision_eur"]
    return eur

def cmd_orden(a):
    m = MERCADOS[a.mercado]; ops = operaciones()
    cot = cotizacion(a.ticker); ultimo = cot["precio"]
    if a.lado == "VENTA":
        lotes, _, _, _ = derivar(ops)
        tenidas = sum(l["cantidad"] for l in lotes.get(a.ticker, []))
        if tenidas <= 0: sys.exit("No hay posición en " + a.ticker)
    fuente, limite = "", None
    if a.tipo == "APERTURA":
        limite, fuente = ultimo, "orden en apertura (MOO): precio = apertura de la sesión"
    else:
        lib = libro_equiduct(a.isin, a.mercado) if not a.sin_libro else {"ok": False, "error": "omitido"}
        ok_lib = lib.get("ok") and lib.get("bid") and lib.get("ask") and (lib["ask"] - lib["bid"]) / lib["bid"] < 0.01
        if a.tipo == "PASIVA":
            if ok_lib:
                limite = lib["bid"] if a.lado == "COMPRA" else lib["ask"]; fuente = f"Equiduct {lib['symbol']} {lib['fuente']} bid {lib['bid']} / ask {lib['ask']}"
            else:
                k = REGLAS["ejecucion"]["fallback_compra_bajo_ultimo_pct"]
                limite = ultimo * (1 - k) if a.lado == "COMPRA" else ultimo * (1 + k)
                fuente = f"fallback último {ultimo} ∓0,10% (Equiduct: {lib.get('error', 'spread >1%')})"
        else:  # AGRESIVA
            k = REGLAS["ejecucion"]["agresiva_pct"]
            if a.lado == "COMPRA":
                limite = max(ultimo * (1 + k), lib["ask"] if ok_lib else 0)
            else:
                limite = min(ultimo * (1 - k), lib["bid"] if ok_lib else 1e18)
            fuente = f"agresiva último {ultimo} ±0,25%" + (f"; Equiduct bid {lib['bid']} / ask {lib['ask']}" if ok_lib else "")
    tick = tick_size(limite, m["unidad_precio"])
    limite = (math.floor if a.lado == "COMPRA" else math.ceil)(round(limite / tick, 6)) * tick
    limite = round(limite, 4)
    if a.lado == "COMPRA":
        precio_eur = limite * eur_por(m["unidad_precio"])
        if a.cantidad: q = a.cantidad
        else:
            q = math.floor(a.importe / precio_eur)
            if q == 0 and precio_eur <= REGLAS["precio_unitario"]["max_eur_compra_1_accion"]: q = 1
        lote = m.get("lote_minimo", 1)
        maxe = REGLAS["precio_unitario"]["max_eur_compra_1_accion"]
        if lote > 1:
            q = max((q // lote) * lote, lote)
        if q == 0 or q * precio_eur > max(maxe, a.importe * 1.0001) and (q == lote or q == 1):
            sys.exit(f"No se puede comprar: el mínimo ({lote} acc.) cuesta {lote * precio_eur:.2f} € (> {maxe} €)")
        aviso_grupo = grupo_saturado(a.ticker, a.sector, ops)
        if aviso_grupo and not a.forzar_grupo: sys.exit(aviso_grupo)
        # Cuenta de contado: no se compra con caja que no existe (ni con la ya comprometida en órdenes pendientes)
        necesita = coste_compra_eur(a.mercado, q, limite, a.pais); libre = caja_libre_eur(ops=ops)
        if necesita > libre + 0.005:
            sys.exit(f"No hay caja suficiente: la orden necesita {necesita:.2f} € y quedan {libre:.2f} € libres "
                     f"(caja menos órdenes de compra pendientes). Usa --cantidad con menos acciones o libera caja.")
    else:
        q = a.cantidad or tenidas
        if q > tenidas: sys.exit(f"Solo hay {tenidas} acciones")
    rows = ordenes(); oid = next_id(rows, "O-")
    row = {"id": oid, "creada": iso(now()), "lado": a.lado, "ticker": a.ticker, "nombre": a.nombre, "isin": a.isin,
           "mercado": a.mercado, "pais_emisor": a.pais, "sector": a.sector, "cantidad": q, "limite": limite, "tipo": a.tipo,
           "fuente_precio": fuente, "ultimo_al_crear": ultimo, "provisional": "S" if a.provisional else "N",
           "motivo": a.motivo, "tesis": a.tesis or f"tesis/{a.ticker}.md", "estado": "PENDIENTE"}
    append_csv("ledger/ordenes.csv", ORD_F, row)
    c = costes(a.lado, a.mercado, q, limite, a.pais)
    print(json.dumps({"orden": row, "costes_estimados_divisa": c, "valor_eur_aprox": r2(q * limite * eur_por(m["unidad_precio"]))}, ensure_ascii=False, indent=1))

def cmd_anular(a):
    rows = ordenes()
    for r in rows:
        if r["id"] == a.id and r["estado"] == "PENDIENTE":
            r["estado"], r["resuelta"], r["nota"] = "ANULADA", iso(now()), a.motivo
    rewrite_csv("ledger/ordenes.csv", ORD_F, rows); print("ok")

def registrar_ejecucion(o, precio, cuando):
    m = MERCADOS[o["mercado"]]; div = m["divisa"]; q = float(o["cantidad"])
    ops = operaciones(); c = costes(o["lado"], o["mercado"], q, precio, o["pais_emisor"])
    lotes, caja, _, _ = derivar(ops)
    nuevas = []
    if o["lado"] == "COMPRA" and div != "EUR":
        necesita = c["valor"] + c["total"] - caja.get(div, 0)
        if necesita > 0:
            necesita = math.ceil(necesita * 100) / 100 + (0.0 if div != "JPY" else 0)
            fx = coste_fx_eur(necesita, div)
            nuevas.append({"tipo": "FX", "divisa": div, "importe_divisa": r2(necesita), "importe_eur": r2(fx["total_eur"]),
                           "comision_ibkr": r2(fx["comision_eur"]), "costes_total_divisa": 0,
                           "fx_eur_por_unidad": round(eur_por(div), 6),
                           "nota": f"EUR→{div} para {o['ticker']}: base {fx['eur_base']:.2f}€ + diferencial {fx['diferencial_eur']:.2f}€ + comisión {fx['comision_eur']:.2f}€"})
    fxr = eur_por(div)
    if o["lado"] == "COMPRA":
        imp_eur = (c["valor"] + c["total"]) * fxr
    else:
        imp_eur = (c["valor"] - c["total"]) * fxr
    nuevas.append({"tipo": o["lado"], "orden_id": o["id"], "ticker": o["ticker"], "nombre": o["nombre"], "isin": o["isin"],
                   "mercado": o["mercado"], "pais_emisor": o["pais_emisor"], "sector": o["sector"], "divisa": div,
                   "cantidad": int(q) if q == int(q) else q, "precio": precio, "unidad_precio": m["unidad_precio"],
                   "importe_divisa": r2(c["valor"]), "comision_ibkr": c["comision_ibkr"], "tasas_terceros": c["tasas_terceros"],
                   "impuesto_transaccion": c["impuesto_transaccion"], "costes_total_divisa": c["total"],
                   "fx_eur_por_unidad": round(fxr, 6), "importe_eur": r2(imp_eur), "provisional": o["provisional"],
                   "nota": o["motivo"]})
    for n in nuevas:
        ops = operaciones(); n["id"] = next_id(ops, "T-"); n["fecha_hora"] = iso(cuando)
        append_csv("ledger/operaciones.csv", OP_F, n)
        if n["tipo"] == "COMPRA": registrar_prediccion(o, n)
    return nuevas

PRED_F = ["op_id", "fecha", "ticker", "precio", "unidad_precio", "provisional", "tir_propia", "tir_propia_ajustada",
          "tir_valorador_bruta", "tir_valorador_neta", "tir_comite", "pd_propia", "pd_bajista", "pd_valorador", "pd_usada",
          "ret_desastre", "ret_bajista", "ret_base", "ret_alcista", "prob_desastre", "prob_bajista", "prob_base",
          "prob_alcista", "precio_3a_desastre", "precio_3a_bajista", "precio_3a_base", "precio_3a_alcista", "asimetria"]

def registrar_prediccion(o, op):
    """Guarda lo que predecían la tesis, el valorador y el bajista en el momento de la compra (ledger/predicciones.csv),
    al precio de ejecución, para medir dentro de un año quién acertó más. Nunca bloquea una ejecución."""
    try:
        import ev as E
        path = P(o.get("tesis") or f"tesis/{o['ticker']}.md")
        ev = E.extraer(path); r = E.evaluar(ev, float(op["precio"])); c = r.get("comite") or {}; pr = r["propio"]
        com = ev.get("comite") or {}; vc = com.get("valorador_ciego") or {}; bj = com.get("bajista") or {}
        rets = c.get("retornos_3a") or pr["retornos_3a"]; probs = c.get("probs") or pr["probs"]
        row = {"op_id": op["id"], "fecha": op["fecha_hora"][:10], "ticker": o["ticker"], "precio": op["precio"],
               "unidad_precio": op["unidad_precio"], "provisional": o["provisional"], "tir_propia": pr["tir"],
               "tir_propia_ajustada": c.get("tir_ajustada_propia"), "tir_valorador_bruta": vc.get("tir"),
               "tir_valorador_neta": c.get("tir_valorador_neta"), "tir_comite": c.get("tir_final"),
               "pd_propia": ev["escenarios"]["desastre"]["prob"], "pd_bajista": bj.get("prob_desastre"),
               "pd_valorador": vc.get("prob_desastre"), "pd_usada": c.get("prob_desastre_usada"),
               "asimetria": c.get("asimetria", pr["asimetria"])}
        for k in ("desastre", "bajista", "base", "alcista"):
            row[f"ret_{k}"] = rets[k]; row[f"prob_{k}"] = probs[k]; row[f"precio_3a_{k}"] = ev["escenarios"][k]["precio_3a"]
        append_csv("ledger/predicciones.csv", PRED_F, {k: ("" if v is None else v) for k, v in row.items()})
    except BaseException as e:  # incluye SystemExit de ev.py: la compra ya está registrada y no debe fallar por esto
        print(f"⚠️ No se pudo registrar la predicción de {o['ticker']}: {e}", file=sys.stderr)

def cruce(tipo, lado, lim, velas, desde, cierre):
    """Primera vela de 1 minuto (hora, apertura, máximo, mínimo) entre desde y cierre que ejecuta la orden.
    Compra: mínimo ESTRICTAMENTE < límite. Venta: máximo ESTRICTAMENTE > límite. Precio = límite.
    APERTURA: primera vela con datos, al precio de apertura. Devuelve (precio, hora) o None."""
    for bt, op, hi, lo in velas:
        if bt < desde or bt > cierre or lo is None: continue
        if tipo == "APERTURA": return (op, bt)
        if lado == "COMPRA" and lo < lim: return (lim, bt)
        if lado == "VENTA" and hi > lim: return (lim, bt)
    return None

def cmd_validar(a):
    rows = ordenes(); cambios = []
    for o in rows:
        if o["estado"] != "PENDIENTE": continue
        m = MERCADOS[o["mercado"]]; tz = ZoneInfo(m["tz"])
        creada = parse(o["creada"]); local = creada.astimezone(tz)
        h, mi = map(int, m["cierre"].split(":")); ha, ma = map(int, m["apertura"].split(":"))
        sesion_dia = local.date()
        apertura = datetime(sesion_dia.year, sesion_dia.month, sesion_dia.day, ha, ma, tzinfo=tz)
        if local > datetime(sesion_dia.year, sesion_dia.month, sesion_dia.day, h, mi, tzinfo=tz) or local.weekday() >= 5:
            # creada fuera de sesión: vale para la siguiente sesión hábil (caso Japón / órdenes nocturnas)
            d = sesion_dia + timedelta(days=1)
            while d.weekday() >= 5: d += timedelta(days=1)
            sesion_dia = d; apertura = datetime(d.year, d.month, d.day, ha, ma, tzinfo=tz)
        cierre = datetime(sesion_dia.year, sesion_dia.month, sesion_dia.day, h, mi, tzinfo=tz)
        desde = max(creada, apertura)
        try:
            ch = yahoo_chart(o["ticker"], "5d", "1m")
        except Exception as e:
            print(f"{o['id']}: sin datos ({e})"); continue
        ts = ch.get("timestamp") or []; qd = ch["indicators"]["quote"][0]
        lim = float(o["limite"])
        velas = [(datetime.fromtimestamp(t, tz), qd["open"][i], qd["high"][i], qd["low"][i]) for i, t in enumerate(ts)]
        ejec = cruce(o["tipo"], o["lado"], lim, velas, desde, cierre)
        if ejec:
            precio, cuando = ejec
            o["estado"], o["resuelta"], o["precio_ejec"] = "EJECUTADA", iso(cuando), precio
            nuevas = registrar_ejecucion(o, precio, cuando)
            cambios.append(f"✅ {o['id']} {o['lado']} {o['cantidad']} {o['ticker']} @ {precio} ({iso(cuando)})")
        elif now() > cierre + timedelta(minutes=20):
            o["estado"], o["resuelta"], o["nota"] = "CADUCADA", iso(now()), "DAY: el precio no cruzó el límite"
            cambios.append(f"⌛ {o['id']} {o['lado']} {o['ticker']} caducada (límite {lim} no alcanzado)")
        else:
            cambios.append(f"⏳ {o['id']} {o['lado']} {o['ticker']} pendiente (límite {lim})")
    rewrite_csv("ledger/ordenes.csv", ORD_F, rows)
    print("\n".join(cambios) or "Sin órdenes pendientes")

# ---------------------------------------------------------------- dividendos
def cmd_dividendos(a):
    ops = operaciones(); hechos = {o["id"] for o in ops}
    hechos_key = {(o["ticker"], o["nota"][:10]) for o in ops if o["tipo"] == "DIVIDENDO"}
    tickers = sorted({o["ticker"] for o in ops if o["tipo"] == "COMPRA"})
    nuevos = []
    for t in tickers:
        compras = [o for o in ops if o["ticker"] == t and o["tipo"] in ("COMPRA", "VENTA")]
        t0 = parse(compras[0]["fecha_hora"]).timestamp() - 86400
        try: ch = yahoo_chart_period(t, t0, time.time(), "1d", events=True)
        except Exception as e: print(t, "sin datos", e); continue
        divs = (ch.get("events") or {}).get("dividends") or {}
        for _, dv in sorted(divs.items()):
            ex = datetime.fromtimestamp(dv["date"], MAD)
            exs = ex.strftime("%Y-%m-%d")
            if (t, exs) in hechos_key: continue
            # acciones en cartera al cierre del día anterior al ex-date
            previas = [o for o in ops if o["ticker"] == t and parse(o["fecha_hora"]).date() < ex.date() and o["tipo"] in ("COMPRA", "VENTA")]
            q = sum(float(o["cantidad"]) * (1 if o["tipo"] == "COMPRA" else -1) for o in previas)
            if q <= 0: continue
            info = previas[-1]; m = MERCADOS[info["mercado"]]
            bruto_unidad = dv["amount"]  # en unidad de cotización (GBX en Londres)
            bruto = a_divisa(bruto_unidad, info["mercado"]) * q
            ret = FISC["retencion_dividendos"].get(info["pais_emisor"], 0.0)
            neto = bruto * (1 - ret)
            row = {"tipo": "DIVIDENDO", "ticker": t, "nombre": info["nombre"], "isin": info["isin"], "mercado": info["mercado"],
                   "pais_emisor": info["pais_emisor"], "sector": info["sector"], "divisa": m["divisa"], "cantidad": q,
                   "precio": bruto_unidad, "unidad_precio": m["unidad_precio"], "importe_divisa": r2(neto),
                   "costes_total_divisa": 0, "fx_eur_por_unidad": round(eur_por(m["divisa"]), 6),
                   "importe_eur": r2(neto * eur_por(m["divisa"])),
                   "nota": f"{exs} ex-date; bruto {bruto:.2f} {m['divisa']}; retención origen {ret*100:.3f}%"}
            row["id"] = next_id(operaciones(), "T-"); row["fecha_hora"] = iso(ex.replace(hour=12))
            append_csv("ledger/operaciones.csv", OP_F, row); ops = operaciones(); nuevos.append(row)
    print(json.dumps(nuevos, ensure_ascii=False, indent=1) if nuevos else "Sin dividendos nuevos")

# ---------------------------------------------------------------- valoración y benchmarks
def precios_cierre(ticker, desde_ts):
    cache = P("data/benchmarks", ticker.replace("/", "_") + ".json")
    ch = yahoo_chart_period(ticker, desde_ts - 7 * 86400, time.time(), "1d")
    serie = {}
    for t, c in zip(ch.get("timestamp") or [], ch["indicators"]["quote"][0]["close"]):
        if c is not None: serie[datetime.fromtimestamp(t, MAD).strftime("%Y-%m-%d")] = c
    serie["_ultimo"] = ch["meta"].get("regularMarketPrice"); serie["_divisa"] = ch["meta"].get("currency")
    json.dump(serie, open(cache, "w"), indent=0)
    return serie

def precio_en(serie, dia):
    dias = sorted(k for k in serie if not k.startswith("_") and k <= dia)
    return serie[dias[-1]] if dias else serie[min(k for k in serie if not k.startswith("_"))]

def benchmarks(ops):
    """Carteras fantasma: mismos flujos EUR en las mismas fechas, comisión mínima Tiered 1,25 € por compra."""
    out = {}
    flujos = [o for o in ops if o["tipo"] in ("COMPRA", "VENTA")]
    aport = sum(float(o["importe_eur"]) for o in ops if o["tipo"] == "APORTACION")
    if not aport: return out
    desde = parse(ops[0]["fecha_hora"]).timestamp()
    for clave, b in REGLAS["benchmarks"].items():
        try: serie = precios_cierre(b["ticker"], desde)
        except Exception as e: out[clave] = {"error": str(e)}; continue
        fx = eur_por(serie["_divisa"]) if serie["_divisa"] in ("EUR", "GBP", "USD", "CHF") else 1.0
        acc, caja = 0.0, aport
        for o in flujos:
            dia = o["fecha_hora"][:10]; px = precio_en(serie, dia) * fx; e = float(o["importe_eur"])
            if o["tipo"] == "COMPRA": acc += (e - 1.25) / px; caja -= e
            else: acc -= min(acc, e / px); caja += e - 1.25
        valor = acc * serie["_ultimo"] * fx + caja
        out[clave] = {"nombre": b["nombre"], "ticker": b["ticker"], "valor_eur": r2(valor), "rent": round(valor / aport - 1, 5)}
    return out

# ---------------------------------------------------------------- descartadas (cartera fantasma del comité)
DESC_F = ["ticker", "nombre", "mercado", "motivo", "fecha_ref", "precio_ref", "eur_por_unidad_ref"]

def fx_eur_fecha(dia):
    """Unidades de divisa por 1 EUR en una fecha pasada (BCE vía Frankfurter)."""
    d = http_json(f"https://api.frankfurter.dev/v1/{dia}?base=EUR"); r = d["rates"]; r["EUR"] = 1.0
    return r

def seguir_descartadas(en_cartera=()):
    """Sigue en papel las empresas analizadas y NO compradas (veto, desastre, reserva…), como si se hubieran comprado
    el día fecha_ref, para medir si las exclusiones del comité y de las reglas aportan valor.
    Rentabilidad en EUR con dividendos brutos, sin costes. Fija precio_ref la primera vez que pasa fecha_ref."""
    if not os.path.exists(P("ledger/descartadas.csv")): return []
    rows = read_csv("ledger/descartadas.csv", DESC_F); hoy = now().strftime("%Y-%m-%d"); out = []; cambiado = False
    for r in rows:
        if hoy < r["fecha_ref"]:
            out.append({"ticker": r["ticker"], "nombre": r["nombre"], "motivo": r["motivo"], "desde": r["fecha_ref"], "rent_eur": None}); continue
        try:
            unidad = MERCADOS[r["mercado"]]["unidad_precio"]
            t0 = datetime.strptime(r["fecha_ref"], "%Y-%m-%d").replace(tzinfo=MAD).timestamp()
            ch = yahoo_chart_period(r["ticker"], t0 - 7 * 86400, time.time(), "1d", events=True)
            serie = {datetime.fromtimestamp(t, MAD).strftime("%Y-%m-%d"): c
                     for t, c in zip(ch.get("timestamp") or [], ch["indicators"]["quote"][0]["close"]) if c is not None}
            if not r["precio_ref"]:
                r["precio_ref"] = round(precio_en(serie, r["fecha_ref"]), 4)
                fx = fx_eur() if hoy == r["fecha_ref"] else fx_eur_fecha(r["fecha_ref"])
                div = MERCADOS[r["mercado"]]["divisa"]
                r["eur_por_unidad_ref"] = round((1.0 / fx[div]) / (100.0 if unidad == "GBX" else 1.0), 8); cambiado = True
            px = ch["meta"].get("regularMarketPrice") or serie[max(serie)]
            divs = sum(d["amount"] for d in ((ch.get("events") or {}).get("dividends") or {}).values()
                       if datetime.fromtimestamp(d["date"], MAD).strftime("%Y-%m-%d") > r["fecha_ref"])
            rent = (px + divs) * eur_por(unidad) / (float(r["precio_ref"]) * float(r["eur_por_unidad_ref"])) - 1
            out.append({"ticker": r["ticker"], "nombre": r["nombre"], "motivo": r["motivo"], "desde": r["fecha_ref"],
                        "precio_ref": float(r["precio_ref"]), "precio": px, "dividendos": round(divs, 4),
                        "rent_eur": round(rent, 4), "en_cartera": r["ticker"] in en_cartera})
        except Exception as e:
            out.append({"ticker": r["ticker"], "nombre": r["nombre"], "motivo": r["motivo"], "desde": r["fecha_ref"], "rent_eur": None, "error": str(e)[:80]})
    if cambiado: rewrite_csv("ledger/descartadas.csv", DESC_F, rows)
    return out

def cmd_estado(a):
    ops = operaciones()
    lotes, caja, info, realizado = derivar(ops)
    pos, total_inv = [], 0.0
    for t, ls in lotes.items():
        i = info[t]; q = sum(l["cantidad"] for l in ls); coste = sum(l["coste_eur"] for l in ls)
        try: cot = cotizacion(t); px = cot["precio"]
        except Exception: cot, px = {}, ls[-1]["precio"]
        val = q * px * eur_por(i["unidad_precio"])
        total_inv += val
        pos.append({"ticker": t, "nombre": i["nombre"], "mercado": i["mercado"], "sector": i["sector"], "pais": i["pais_emisor"],
                    "cantidad": q, "precio_medio": round(sum(l["precio"] * l["cantidad"] for l in ls) / q, 4), "precio": px,
                    "unidad_precio": i["unidad_precio"], "coste_eur": r2(coste), "valor_eur": r2(val), "pyg_eur": r2(val - coste),
                    "pyg_pct": round(val / coste - 1, 4) if coste else 0, "var_dia_pct": round(px / cot["cierre_anterior"] - 1, 4) if cot.get("cierre_anterior") else None,
                    "provisional": any(l["provisional"] == "S" for l in ls), "lotes": ls,
                    "dividendos_y_realizado_eur": r2(realizado.get(t, 0))})
    caja_eur = sum(v * eur_por(d) for d, v in caja.items())
    total = total_inv + caja_eur
    aport = sum(float(o["importe_eur"]) for o in ops if o["tipo"] == "APORTACION")
    for p in pos: p["peso"] = round(p["valor_eur"] / total, 4) if total else 0
    pos.sort(key=lambda p: -p["valor_eur"])
    est = {"actualizado": iso(now()), "valor_total_eur": r2(total), "invertido_eur": r2(total_inv), "caja_eur": r2(caja_eur),
           "caja_por_divisa": {k: r2(v) for k, v in caja.items()}, "aportado_eur": r2(aport),
           "rentabilidad": round(total / aport - 1, 5) if aport else 0, "n_posiciones": len(pos), "posiciones": pos,
           "realizado_eur": r2(sum(realizado.values())), "benchmarks": benchmarks(ops) if ops else {}}
    if a.cierre: est["descartadas"] = seguir_descartadas(set(lotes))
    else:
        try: est["descartadas"] = json.load(open(P("ledger/cartera.json"), encoding="utf-8")).get("descartadas", [])
        except Exception: est["descartadas"] = []
    json.dump(est, open(P("ledger/cartera.json"), "w"), ensure_ascii=False, indent=1)
    if a.cierre:
        H = ["fecha", "valor_total_eur", "invertido_eur", "caja_eur", "aportado_eur", "rentabilidad", "n_posiciones"] + \
            [f"bench_{k}" for k in REGLAS["benchmarks"]]
        hist = read_csv("ledger/historico.csv", H)
        hoy = now().strftime("%Y-%m-%d")
        hist = [h for h in hist if h["fecha"] != hoy]
        row = {"fecha": hoy, **{k: est[k] for k in ("valor_total_eur", "invertido_eur", "caja_eur", "aportado_eur", "rentabilidad", "n_posiciones")}}
        for k in REGLAS["benchmarks"]: row[f"bench_{k}"] = est["benchmarks"].get(k, {}).get("valor_eur", "")
        rewrite_csv("ledger/historico.csv", H, hist + [row])
    print(json.dumps({k: v for k, v in est.items() if k not in ("posiciones", "descartadas")}, ensure_ascii=False, indent=1))
    con = [d for d in est["descartadas"] if d.get("rent_eur") is not None]
    if con:
        print(f"Descartadas (en papel desde {con[0]['desde']}): media {sum(d['rent_eur'] for d in con) / len(con) * 100:+.1f}%"
              + (f" · posiciones de la cartera: media {sum(p['pyg_pct'] for p in pos) / len(pos) * 100:+.1f}%" if pos else ""))
        for d in sorted(con, key=lambda d: -d["rent_eur"]): print(f"  {d['ticker']:10} {d['rent_eur'] * 100:+6.1f}%  {d['motivo']}")
    for p in pos:
        print(f"{p['ticker']:10} {p['cantidad']:>6} {p['valor_eur']:>9.2f}€ {p['pyg_pct']*100:>6.1f}% peso {p['peso']*100:4.1f}% {'🟡' if p['provisional'] else '🟢'}")

# ---------------------------------------------------------------- Investing
def fmt_num(x, dec=2):
    s = f"{x:,.{dec}f}"; return s.replace(",", "X").replace(".", ",").replace("X", ".")

def cmd_investing(a):
    ops = operaciones(); hechos = set(json.load(open(P("investing/estado.json")))["pasadas"]) if os.path.exists(P("investing/estado.json")) else set()
    bloques, info = [], []
    for o in ops:
        if o["tipo"] not in ("COMPRA", "VENTA", "DIVIDENDO") or o["id"] in hechos: continue
        f = datetime.strptime(o["fecha_hora"], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
        m = MERCADOS[o["mercado"]]; dec = 1 if o["unidad_precio"] in ("GBX", "JPY") else 4 if float(o["precio"]) < 10 else 2
        aviso = "   ⚠️ GBX (peniques)" if o["unidad_precio"] == "GBX" else ""
        if o["tipo"] == "DIVIDENDO":
            info.append(f"- `{o['id']}` {f} · Dividendo {o['nombre']}: {fmt_num(float(o['importe_eur']))} € netos (solo ledger, Investing no lo registra)")
            continue
        if o["tipo"] == "COMPRA":
            bloques.append(f"""### `{o['id']}` ✅ COMPRA · {o['nombre']}
```
Buscar:    {o['nombre']}  → elegir la de "{m['investing']}" ({o['ticker']})
Tipo:      Compra
Fecha:     {f}
Cantidad:  {o['cantidad']}
Precio:    {fmt_num(float(o['precio']), dec)}{aviso}
Comisión:  {fmt_num(float(o['costes_total_divisa']))} {o['divisa']}
```""")
        else:
            prev = [x for x in ops if x["id"] < o["id"]]
            cierres = lotes_fifo_a_cerrar(o["ticker"], float(o["cantidad"]), prev)
            ctot = float(o["costes_total_divisa"]); qtot = float(o["cantidad"])
            partes = "\n".join(f"  · Cerrar lote abierto el {datetime.strptime(d,'%Y-%m-%d').strftime('%d/%m/%Y')}: {int(q) if q == int(q) else q} acc. (de {int(t) if t == int(t) else t})"
                               f" · comisión {fmt_num(ctot * q / qtot)} {o['divisa']}" for d, q, t in cierres)
            bloques.append(f"""### `{o['id']}` 📤 VENTA · {o['nombre']}
```
Posición:  {o['nombre']} ({m['investing']})
Acción:    Cerrar posición (FIFO)
{partes}
Fecha:     {f}
Precio:    {fmt_num(float(o['precio']), dec)}{aviso}
```""")
    txt = "# 📥 Pendiente de pasar a Investing · cartera \"VALUE ex-USA\"\n\n"
    txt += "Precio en la divisa de cotización (Londres en **peniques**), comisión en la divisa del valor (Londres en **libras**). " \
           "La comisión incluye IBKR + tasas + stamp duty/TTF. Cuando las pases, dime \"pasadas\" y las marco.\n\n"
    txt += ("\n\n".join(bloques) if bloques else "_Nada pendiente._")
    if info: txt += "\n\n## ℹ️ Solo ledger (no se meten en Investing)\n" + "\n".join(info)
    open(P("investing/pendiente.md"), "w").write(txt + "\n"); print(txt)

def cmd_investing_marcar(a):
    p = P("investing/estado.json"); st = json.load(open(p)) if os.path.exists(p) else {"pasadas": []}
    st["pasadas"] = sorted(set(st["pasadas"]) | set(a.ids)); json.dump(st, open(p, "w"), indent=1)
    ops = {o["id"]: o for o in operaciones()}
    with open(P("investing/historico.md"), "a") as f:
        for i in a.ids:
            if i in ops: f.write(f"- {iso(now())} · `{i}` {ops[i]['tipo']} {ops[i]['cantidad']} {ops[i]['nombre']} @ {ops[i]['precio']} → pasada a Investing\n")
    cmd_investing(a)

# ---------------------------------------------------------------- otros
def cmd_precio(a): print(json.dumps(cotizacion(a.ticker), ensure_ascii=False, indent=1))
def cmd_libro(a): print(json.dumps(libro_equiduct(a.isin, a.mercado, a.fecha), ensure_ascii=False, indent=1))
def cmd_costes(a):
    c = costes(a.lado, a.mercado, a.cantidad, a.precio, a.pais); m = MERCADOS[a.mercado]
    out = {"costes_divisa": c, "divisa": m["divisa"], "valor_eur": r2(c["valor"] * eur_por(m["divisa"])),
           "costes_eur": r2(c["total"] * eur_por(m["divisa"]))}
    if m["divisa"] != "EUR" and a.lado == "COMPRA": out["fx"] = {k: r2(v) for k, v in coste_fx_eur(c["valor"] + c["total"], m["divisa"]).items()}
    print(json.dumps(out, ensure_ascii=False, indent=1))

def cmd_aportacion(a):
    ops = operaciones()
    if any(o["tipo"] == "APORTACION" for o in ops) and not a.forzar: sys.exit("Ya existe la aportación inicial")
    append_csv("ledger/operaciones.csv", OP_F, {"id": next_id(ops, "T-"), "fecha_hora": a.fecha or iso(now()), "tipo": "APORTACION",
               "divisa": "EUR", "importe_divisa": a.importe, "importe_eur": a.importe, "costes_total_divisa": 0, "fx_eur_por_unidad": 1, "nota": "Capital inicial simulado"})
    print("ok")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("precio"); s.add_argument("ticker"); s.set_defaults(f=cmd_precio)
    s = sp.add_parser("libro"); s.add_argument("isin"); s.add_argument("mercado"); s.add_argument("--fecha"); s.set_defaults(f=cmd_libro)
    s = sp.add_parser("orden")
    s.add_argument("--lado", required=True, choices=["COMPRA", "VENTA"]); s.add_argument("--ticker", required=True)
    s.add_argument("--nombre", required=True); s.add_argument("--isin", default=""); s.add_argument("--mercado", required=True, choices=list(MERCADOS))
    s.add_argument("--pais", required=True, help="país del emisor ISO-2"); s.add_argument("--sector", default="")
    s.add_argument("--importe", type=float, default=REGLAS["importe_objetivo_compra_eur"]); s.add_argument("--cantidad", type=float)
    s.add_argument("--tipo", default="PASIVA", choices=["PASIVA", "AGRESIVA", "APERTURA"]); s.add_argument("--provisional", action="store_true")
    s.add_argument("--motivo", required=True); s.add_argument("--tesis"); s.add_argument("--sin-libro", action="store_true")
    s.add_argument("--forzar-grupo", action="store_true", help="solo con acuerdo explícito de Ale")
    s.set_defaults(f=cmd_orden)
    s = sp.add_parser("anular"); s.add_argument("id"); s.add_argument("--motivo", required=True); s.set_defaults(f=cmd_anular)
    s = sp.add_parser("validar"); s.set_defaults(f=cmd_validar)
    s = sp.add_parser("dividendos"); s.set_defaults(f=cmd_dividendos)
    s = sp.add_parser("estado"); s.add_argument("--cierre", action="store_true"); s.set_defaults(f=cmd_estado)
    s = sp.add_parser("investing"); s.set_defaults(f=cmd_investing)
    s = sp.add_parser("investing-marcar"); s.add_argument("ids", nargs="+"); s.set_defaults(f=cmd_investing_marcar)
    s = sp.add_parser("costes"); s.add_argument("--lado", default="COMPRA"); s.add_argument("--mercado", required=True)
    s.add_argument("--cantidad", type=float, required=True); s.add_argument("--precio", type=float, required=True); s.add_argument("--pais", required=True)
    s.set_defaults(f=cmd_costes)
    s = sp.add_parser("aportacion"); s.add_argument("--importe", type=float, default=REGLAS["capital_inicial_eur"]); s.add_argument("--fecha"); s.add_argument("--forzar", action="store_true")
    s.set_defaults(f=cmd_aportacion)
    a = ap.parse_args(); a.f(a)

if __name__ == "__main__":
    main()
