#!/usr/bin/env python3
"""Cribado del universo (config/universo.csv) con datos de Yahoo Finance (quoteSummary).

Aplica los filtros duros que se pueden medir automáticamente (capitalización, liquidez, deuda neta/EBITDA)
y ordena por señales value. Los filtros de historia (10 años, beneficio 7/10) se verifican en la tesis.

Uso: python3 scripts/cribado.py [--salida plan/cribado.csv] [--md plan/candidatos.md]
"""
import argparse, csv, http.cookiejar, json, math, os, sys, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import cartera as C

MODS = "price,summaryDetail,defaultKeyStatistics,financialData"

class Yahoo:
    def __init__(self):
        self.cj = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        self.op.addheaders = [("User-Agent", "Mozilla/5.0")]
        try: self.op.open("https://fc.yahoo.com", timeout=20)
        except Exception: pass
        self.crumb = self.op.open("https://query2.finance.yahoo.com/v1/test/getcrumb", timeout=20).read().decode()

    def resumen(self, t):
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{t}?modules={MODS}&crumb={self.crumb}"
        for i in range(4):
            try:
                return json.load(self.op.open(url, timeout=30))["quoteSummary"]["result"][0]
            except Exception as e:
                err = e; time.sleep(3 * 2 ** i)
        raise err

def v(d, *ks):
    for k in ks:
        d = (d or {}).get(k)
    return d.get("raw") if isinstance(d, dict) else d

def eur_por_divisa(div):
    if div in (None, ""): return None
    if div in ("GBp", "GBX"): return C.eur_por("GBX")
    if div == "ILA": return None
    return C.eur_por(div)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--salida", default="plan/cribado.csv"); ap.add_argument("--md", default="plan/candidatos.md")
    a = ap.parse_args()
    F = C.REGLAS["filtros_duros"]
    y = Yahoo(); filas = []
    univ = list(csv.DictReader(open(os.path.join(ROOT, "config/universo.csv"), encoding="utf-8")))
    for u in univ:
        t = u["ticker"]
        try: r = y.resumen(t)
        except Exception as e:
            print(f"{t}: sin datos ({e})", file=sys.stderr); filas.append({**u, "error": str(e)[:80]}); continue
        pr, sd, ks, fd = r.get("price", {}), r.get("summaryDetail", {}), r.get("defaultKeyStatistics", {}), r.get("financialData", {})
        div_px = v(pr, "currency"); div_fin = v(fd, "financialCurrency") or div_px
        fx_px, fx_fin = eur_por_divisa(div_px), eur_por_divisa(div_fin if div_fin != "GBP" or div_px != "GBp" else "GBP")
        precio = v(pr, "regularMarketPrice"); mcap = v(pr, "marketCap") or v(sd, "marketCap")
        # Yahoo da marketCap de Londres en GBP (no peniques)
        mcap_eur = mcap * (C.eur_por("GBP") if div_px == "GBp" else fx_px) if (mcap and fx_px) else None
        vol = v(sd, "averageVolume") or v(pr, "averageDailyVolume3Month")
        vol_eur = vol * precio * fx_px if (vol and precio and fx_px) else None
        deuda, caja, ebitda = v(fd, "totalDebt"), v(fd, "totalCash"), v(fd, "ebitda")
        fcf = v(fd, "freeCashflow")
        fin_a_eur = eur_por_divisa("GBP" if div_fin == "GBp" else div_fin)
        fcf_yield = (fcf * fin_a_eur) / mcap_eur if (fcf is not None and fin_a_eur and mcap_eur) else None
        nd_ebitda = (deuda - (caja or 0)) / ebitda if (deuda is not None and ebitda and ebitda > 0) else None
        pe_t, pe_f = v(sd, "trailingPE"), v(sd, "forwardPE") or v(ks, "forwardPE")
        pb, roe = v(ks, "priceToBook"), v(fd, "returnOnEquity")
        ev_ebitda = v(ks, "enterpriseToEbitda")
        hi52, lo52 = v(sd, "fiftyTwoWeekHigh"), v(sd, "fiftyTwoWeekLow")
        caida = (precio / hi52 - 1) if (precio and hi52) else None
        financiera = u["sector"] in ("Bancos", "Seguros", "Financieras", "Gestión de activos", "Holding")
        fallos = []
        if mcap_eur is None or mcap_eur < F["capitalizacion_min_eur"]: fallos.append("cap")
        if vol_eur is None or vol_eur < F["volumen_medio_diario_min_eur"]: fallos.append("liquidez")
        if not financiera and nd_ebitda is not None and nd_ebitda > F["deuda_neta_ebitda_max"]: fallos.append("deuda")
        if not financiera and ebitda is not None and ebitda <= 0: fallos.append("ebitda<0")
        # Señales value (cuanto más alto, más barato)
        ey = 1 / pe_f if pe_f and pe_f > 0 else (1 / pe_t if pe_t and pe_t > 0 else None)
        filas.append({**u, "precio": precio, "divisa": div_px, "cap_eur_bn": round(mcap_eur / 1e9, 2) if mcap_eur else None,
                      "vol_eur_m": round(vol_eur / 1e6, 1) if vol_eur else None, "per": round(pe_t, 1) if pe_t else None,
                      "per_fwd": round(pe_f, 1) if pe_f else None, "ev_ebitda": round(ev_ebitda, 1) if ev_ebitda else None,
                      "p_vc": round(pb, 2) if pb else None, "roe": round(roe, 3) if roe is not None else None,
                      "fcf_yield": round(fcf_yield, 3) if fcf_yield is not None else None,
                      "div_yield": round(v(sd, "dividendYield") or 0, 3), "dn_ebitda": round(nd_ebitda, 2) if nd_ebitda is not None else None,
                      "caida_52s": round(caida, 3) if caida is not None else None, "ey": ey, "financiera": financiera,
                      "lote_eur": round(precio * fx_px * C.MERCADOS[u["mercado"]].get("lote_minimo", 1), 0) if (precio and fx_px) else None,
                      "filtros_ko": ",".join(fallos)})
        time.sleep(0.4)
    ok = [f for f in filas if not f.get("error") and not f["filtros_ko"]]
    # Puntuación: percentiles de ey, fcf_yield (no financieras), 1/ev_ebitda, roe/pb (financieras), caída 52s
    def pct(lista, key, f):
        vals = sorted(x[key] for x in lista if x.get(key) is not None)
        return (sum(1 for z in vals if z <= f[key]) / len(vals)) if (f.get(key) is not None and vals) else 0.5
    for f in ok:
        f["inv_ev_ebitda"] = 1 / f["ev_ebitda"] if f.get("ev_ebitda") and f["ev_ebitda"] > 0 else None
        f["roe_pb"] = f["roe"] / f["p_vc"] if (f.get("roe") and f.get("p_vc")) else None
        f["neg_caida"] = -f["caida_52s"] if f.get("caida_52s") is not None else None
    for f in ok:
        if f["financiera"]:
            s = 0.4 * pct(ok, "ey", f) + 0.4 * pct(ok, "roe_pb", f) + 0.2 * pct(ok, "div_yield", f)
        else:
            s = 0.3 * pct(ok, "ey", f) + 0.3 * pct(ok, "fcf_yield", f) + 0.25 * pct(ok, "inv_ev_ebitda", f) + 0.15 * pct(ok, "neg_caida", f)
        f["puntuacion"] = round(s, 3)
    ok.sort(key=lambda f: -f["puntuacion"])
    campos = ["ticker", "nombre", "mercado", "pais", "sector", "precio", "divisa", "cap_eur_bn", "vol_eur_m", "per", "per_fwd", "ev_ebitda",
              "p_vc", "roe", "fcf_yield", "div_yield", "dn_ebitda", "caida_52s", "lote_eur", "puntuacion", "filtros_ko", "error"]
    with open(os.path.join(ROOT, a.salida), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore"); w.writeheader()
        for f in ok + [f for f in filas if f not in ok]: w.writerow(f)
    pctf = lambda x: "—" if x is None else f"{x*100:.1f}%"
    lines = [f"# Candidatos (cribado {C.now().strftime('%Y-%m-%d %H:%M')})", "",
             f"Universo: {len(univ)} · con datos: {sum(1 for f in filas if not f.get('error'))} · pasan filtros medibles: {len(ok)}.",
             "Puntuación = percentiles de rendimiento del beneficio, FCF yield, EV/EBITDA y caída desde máximos (financieras: beneficio, ROE/P-VC y dividendo).",
             "", "| # | Empresa | Ticker | Sector | País | Cap. (bn€) | PER fwd | EV/EBITDA | FCF yield | Div. | DN/EBITDA | vs máx. 52s | Punt. |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, f in enumerate(ok, 1):
        lines.append(f"| {i} | {f['nombre']} | {f['ticker']} | {f['sector']} | {f['pais']} | {f['cap_eur_bn']} | {f.get('per_fwd') or '—'} | {f.get('ev_ebitda') or '—'} | "
                     f"{pctf(f.get('fcf_yield'))} | {pctf(f.get('div_yield'))} | {f.get('dn_ebitda') if f.get('dn_ebitda') is not None else '—'} | {pctf(f.get('caida_52s'))} | {f['puntuacion']} |")
    lines += ["", "## Descartados por filtros medibles", ""]
    for f in filas:
        if f.get("error") or f.get("filtros_ko"):
            lines.append(f"- {f['nombre']} ({f['ticker']}): {f.get('filtros_ko') or 'sin datos: ' + f.get('error', '')}")
    open(os.path.join(ROOT, a.md), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"{len(ok)} pasan filtros de {len(filas)}. Top 40:")
    for f in ok[:40]:
        print(f"{f['puntuacion']:.3f} {f['ticker']:11} {f['sector'][:18]:18} PERf {f.get('per_fwd')} EV/EBITDA {f.get('ev_ebitda')} FCFy {pctf(f.get('fcf_yield'))} DN/EBITDA {f.get('dn_ebitda')} caida {pctf(f.get('caida_52s'))} lote {f.get('lote_eur')}€")

if __name__ == "__main__":
    main()
