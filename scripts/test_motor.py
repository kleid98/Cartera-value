#!/usr/bin/env python3
"""Pruebas del motor con datos fijos (sin red). Ejecutar tras cualquier cambio en scripts/:

    python3 scripts/test_motor.py

Comprueban costes, saltos de precio, validación de órdenes, lotes FIFO, control de caja, la calculadora de EV,
la reconciliación del comité y el registro de una compra de principio a fin. Si algo falla, no se sube el cambio.
"""
import copy, os, shutil, sys, tempfile, unittest, warnings
warnings.simplefilter("ignore", ResourceWarning)
from datetime import datetime, timedelta
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import cartera as C, ev as E, comite_registrar as R

FX = {"EUR": 1.0, "GBP": 0.85, "USD": 1.10, "DKK": 7.46, "CAD": 1.50, "JPY": 160.0, "CHF": 0.95, "SEK": 11.0, "NOK": 11.5}

def op(i, tipo, **k):
    base = {"id": f"T-{i:04d}", "fecha_hora": f"2026-11-{15 + i:02d} 10:00:00", "tipo": tipo, "divisa": "EUR", "ticker": "",
            "importe_divisa": 0, "costes_total_divisa": 0, "importe_eur": 0, "cantidad": 0, "precio": 0, "provisional": "N",
            "nombre": "", "isin": "", "mercado": "PARIS", "pais_emisor": "FR", "sector": "Bancos", "unidad_precio": "EUR"}
    base.update(k); return base

EV = {"ticker": "PRU.PA", "mercado": "PARIS", "pais": "FR", "precio_actual": 100.0, "fecha": "2026-11-09",
      "escenarios": {"desastre": {"prob": 0.10, "precio_3a": 55, "dividendos_3a": 5},
                     "bajista": {"prob": 0.25, "precio_3a": 90, "dividendos_3a": 10},
                     "base": {"prob": 0.45, "precio_3a": 130, "dividendos_3a": 12},
                     "alcista": {"prob": 0.20, "precio_3a": 170, "dividendos_3a": 14}},
      "comite": {"valorador_ciego": {"tir": None, "prob_desastre": None}, "bajista": {"prob_desastre": None, "veto": False}}}

class Motor(unittest.TestCase):
    def setUp(self):
        C._FX = dict(FX)

    def test_costes(self):
        c = C.costes("COMPRA", "PARIS", 5, 100.0, "FR")       # 500 €: mínimo 1,25 + 1 pb + TTF 0,4%
        self.assertEqual((c["comision_ibkr"], c["tasas_terceros"], c["impuesto_transaccion"], c["total"]), (1.25, 0.05, 2.0, 3.3))
        c = C.costes("COMPRA", "MADRID", 100, 5.0, "ES")      # Fixed: mínimo 3 €, sin tasas, ITF 0,2%
        self.assertEqual((c["comision_ibkr"], c["tasas_terceros"], c["impuesto_transaccion"]), (3.0, 0.0, 1.0))
        c = C.costes("COMPRA", "LONDRES", 100, 500.0, "GB")   # 500p = 5 £: valor 500 £, stamp duty 0,5%
        self.assertEqual((c["valor"], c["comision_ibkr"], c["impuesto_transaccion"]), (500.0, 1.0, 2.5))
        c = C.costes("VENTA", "LONDRES", 100, 500.0, "GB")    # las ventas no pagan stamp duty
        self.assertEqual(c["impuesto_transaccion"], 0.0)
        c = C.costes("COMPRA", "TORONTO", 8, 87.0, "CA")      # 0,008 CAD/acción, mínimo 1 CAD
        self.assertEqual(c["comision_ibkr"], 1.0)
        c = C.costes("COMPRA", "XETRA", 2000, 50.0, "DE")     # 100.000 €: 0,05% = 50 → tope 29 €
        self.assertEqual(c["comision_ibkr"], 29.0)

    def test_fx(self):
        f = C.coste_fx_eur(425.0, "GBP")                      # 500 € de base: mínimo 2 USD y 0,03% de diferencial
        self.assertAlmostEqual(f["eur_base"], 500.0, places=6)
        self.assertAlmostEqual(f["comision_eur"], 2 / 1.10, places=6)
        self.assertAlmostEqual(f["diferencial_eur"], 0.15, places=6)
        self.assertAlmostEqual(C.eur_por("GBX"), 1 / 0.85 / 100, places=9)

    def test_tick(self):
        for precio, unidad, esperado in ((96.18, "GBX", 0.02), (151.5, "GBX", 0.05), (263.4, "GBX", 0.1), (587.8, "GBX", 0.2),
                                         (2973, "GBX", 1.0), (4.13, "EUR", 0.001), (9.62, "EUR", 0.002), (91.93, "EUR", 0.02),
                                         (87.38, "CAD", 0.01), (2500, "JPY", 1.0)):
            self.assertEqual(C.tick_size(precio, unidad), esperado, (precio, unidad))

    def test_cruce_estricto(self):
        t0 = datetime(2026, 11, 16, 9, 30, tzinfo=C.MAD); fin = t0 + timedelta(hours=8)
        velas = [(t0 - timedelta(minutes=5), 9.9, 10.0, 9.0),   # anterior a la orden: no cuenta
                 (t0 + timedelta(minutes=1), 10.1, 10.2, 10.0),  # toca el límite sin cruzarlo: no ejecuta
                 (t0 + timedelta(minutes=2), 10.0, 10.1, 9.99)]  # mínimo < límite: ejecuta al límite
        self.assertEqual(C.cruce("PASIVA", "COMPRA", 10.0, velas, t0, fin), (10.0, velas[2][0]))
        self.assertIsNone(C.cruce("PASIVA", "COMPRA", 10.0, velas[:2], t0, fin))
        self.assertIsNone(C.cruce("PASIVA", "VENTA", 10.2, velas, t0, fin))          # máximo = límite: no ejecuta
        self.assertEqual(C.cruce("PASIVA", "VENTA", 10.15, velas, t0, fin), (10.15, velas[1][0]))
        self.assertEqual(C.cruce("APERTURA", "COMPRA", 0, velas, t0, fin), (10.1, velas[1][0]))
        self.assertIsNone(C.cruce("PASIVA", "COMPRA", 10.0, velas, t0, t0 + timedelta(seconds=90)))  # tras el cierre no

    def test_fifo_y_caja(self):
        ops = [op(1, "APORTACION", importe_divisa=10000, importe_eur=10000),
               op(2, "COMPRA", ticker="AAA.PA", cantidad=10, precio=50, importe_divisa=500, costes_total_divisa=3, importe_eur=503),
               op(3, "COMPRA", ticker="AAA.PA", cantidad=10, precio=40, importe_divisa=400, costes_total_divisa=3, importe_eur=403),
               op(4, "VENTA", ticker="AAA.PA", cantidad=15, precio=60, importe_divisa=900, costes_total_divisa=2, importe_eur=898)]
        lotes, caja, info, realizado = C.derivar(ops)
        self.assertAlmostEqual(caja["EUR"], 10000 - 503 - 403 + 898)
        self.assertEqual(len(lotes["AAA.PA"]), 1)                       # el primer lote se cierra entero (FIFO)
        self.assertAlmostEqual(lotes["AAA.PA"][0]["cantidad"], 5)
        self.assertAlmostEqual(lotes["AAA.PA"][0]["coste_eur"], 201.5)
        self.assertAlmostEqual(realizado["AAA.PA"], 898 - 503 - 201.5)
        self.assertEqual(C.lotes_fifo_a_cerrar("AAA.PA", 15, ops[:3]), [("2026-11-17", 10, 10), ("2026-11-18", 5, 10)])

    def test_caja_libre(self):
        ops = [op(1, "APORTACION", importe_divisa=1000, importe_eur=1000)]
        pend = [{"estado": "PENDIENTE", "lado": "COMPRA", "mercado": "PARIS", "cantidad": "5", "limite": "100", "pais_emisor": "FR"},
                {"estado": "CADUCADA", "lado": "COMPRA", "mercado": "PARIS", "cantidad": "5", "limite": "100", "pais_emisor": "FR"}]
        self.assertAlmostEqual(C.caja_libre_eur(pend, ops), 1000 - 503.3)
        self.assertAlmostEqual(C.coste_compra_eur("LONDRES", 100, 500.0, "GB"),
                               503.55 / 0.85 + 2 / 1.10 + 503.55 / 0.85 * 0.0003, places=6)

    def test_ev_propia(self):
        r = E.calcular(EV)
        coste = (3.3 + 1.3) / 500
        self.assertAlmostEqual(r["coste_ida_vuelta_pct"], round(coste, 4))
        self.assertAlmostEqual(r["retornos_3a"]["desastre"], round((55 + 5 * (1 - 0.128)) / 100 - 1 - coste, 4))
        er = sum(v["prob"] * ((v["precio_3a"] + v["dividendos_3a"] * 0.872) / 100 - 1 - coste) for v in EV["escenarios"].values())
        self.assertAlmostEqual(r["tir"], round((1 + er) ** (1 / 3) - 1, 4))
        self.assertTrue(r["cumple"]["desastre ≥ -50%"])
        self.assertLess(E.evaluar(EV, 110.0)["propio"]["tir"], r["tir"])            # más caro → menos TIR
        self.assertFalse(E.evaluar(EV, 125.0)["propio"]["cumple"]["desastre ≥ -50%"])  # y el desastre deja de cumplir
        po = E.evaluar(EV)["precio_objetivo"]                                       # objetivo = escenario base; esperado = media ponderada
        self.assertEqual(po["base_3a"], EV["escenarios"]["base"]["precio_3a"])
        self.assertAlmostEqual(po["esperado_3a"], sum(v["prob"] * v["precio_3a"] for v in EV["escenarios"].values()), places=2)
        self.assertAlmostEqual(E.evaluar(EV, 110.0)["precio_objetivo"]["potencial_base"], po["base_3a"] / 110 - 1, places=4)

    def test_reconciliacion(self):
        ev = copy.deepcopy(EV); propia = E.calcular(EV)
        ev["comite"] = {"valorador_ciego": {"tir": 0.10, "prob_desastre": 0.10, "precio": 100.0}, "bajista": {"prob_desastre": 0.10, "veto": False}}
        c = E.evaluar(ev)["comite"]
        self.assertAlmostEqual(c["prob_desastre_usada"], 0.10)
        self.assertLess(c["tir_valorador_neta"], 0.10)                              # se le restan costes y retención
        self.assertAlmostEqual(c["tir_final"], round((propia["tir"] + c["tir_valorador_neta"]) / 2, 4), places=3)
        ev["comite"]["valorador_ciego"]["tir"] = 0.01                               # diferencia ≥ 5 pp → la más baja + 2,5 pp
        c = E.evaluar(ev)["comite"]
        self.assertIn("tope", c["regla"])
        self.assertAlmostEqual(c["tir_final"], round(c["tir_valorador_neta"] + 0.025, 4), places=3)
        ev["comite"]["bajista"] = {"prob_desastre": 0.40, "veto": True}             # media de las tres y veto
        c = E.evaluar(ev)["comite"]
        self.assertAlmostEqual(c["prob_desastre_usada"], 0.20)
        self.assertFalse(c["compra_ok"]); self.assertFalse(c["cumple"]["sin veto del bajista"])
        self.assertAlmostEqual(sum(c["probs"].values()), 1.0, places=3)

    def test_valorador_exacto(self):
        ruta = os.path.join(ROOT, "plan/comite_informes/informe_valorador_TEP.PA.md")
        tir, div = R.tabla_valorador(open(ruta, encoding="utf-8").read())
        self.assertAlmostEqual(tir, 0.1279, places=3)                               # el informe redondeaba a 0.13
        self.assertAlmostEqual(div, 0.15 * 8 + 0.35 * 13.5 + 0.35 * 14 + 0.15 * 14.5, places=3)

    def test_compra_de_principio_a_fin(self):
        tmp = tempfile.mkdtemp(); raiz = C.ROOT
        try:
            os.makedirs(os.path.join(tmp, "ledger")); os.makedirs(os.path.join(tmp, "tesis"))
            shutil.copy(os.path.join(ROOT, "tesis/NWG.L.md"), os.path.join(tmp, "tesis/NWG.L.md"))
            C.ROOT = tmp
            C.append_csv("ledger/operaciones.csv", C.OP_F, {"id": "T-0001", "fecha_hora": "2026-11-07 12:00:00", "tipo": "APORTACION",
                         "divisa": "EUR", "importe_divisa": 10000, "importe_eur": 10000, "costes_total_divisa": 0})
            o = {"id": "O-0001", "lado": "COMPRA", "ticker": "NWG.L", "nombre": "NatWest Group", "isin": "GB00BM8PJY71", "mercado": "LONDRES",
                 "pais_emisor": "GB", "sector": "Bancos", "cantidad": "71", "provisional": "S", "motivo": "prueba", "tesis": "tesis/NWG.L.md"}
            nuevas = C.registrar_ejecucion(o, 587.4, datetime(2026, 11, 16, 10, 0, tzinfo=C.MAD))
            self.assertEqual([n["tipo"] for n in nuevas], ["FX", "COMPRA"])
            lotes, caja, _, _ = C.derivar()
            self.assertAlmostEqual(lotes["NWG.L"][0]["cantidad"], 71)
            self.assertLess(abs(caja.get("GBP", 0)), 0.02)                          # se convierte justo lo necesario
            valor = 71 * 5.874; costes = 1.0 + round(valor * 0.0001, 2) + round(valor * 0.005, 2)
            self.assertAlmostEqual(10000 - caja["EUR"], (valor + costes) / 0.85 * 1.0003 + 2 / 1.10, delta=0.05)
            pred = C.read_csv("ledger/predicciones.csv", C.PRED_F)
            self.assertEqual(len(pred), 1); self.assertEqual(pred[0]["ticker"], "NWG.L")
            self.assertTrue(pred[0]["tir_comite"] and pred[0]["pd_bajista"] and pred[0]["precio_3a_base"])
            # Ficha de entrada y de salida (por qué y precio objetivo), con el libro y la predicción recién creados
            import ficha as F
            ficha, linea = F.ficha_compra(os.path.join(tmp, "tesis/NWG.L.md"), 587.4)
            self.assertIn("Entrada · NatWest Group (NWG.L)", ficha); self.assertIn("Qué me haría vender", ficha)
            self.assertIn("748 p (+27,3% desde 587,4 p)", ficha); self.assertEqual(linea, "Objetivo 3 años 748 p (+27,3%)")
            compra = [n for n in nuevas if n["tipo"] == "COMPRA"][0]
            self.assertIn("Objetivo 3 años 748 p", C.porque_operacion(compra))
            salida = F.ficha_venta(os.path.join(tmp, "tesis/NWG.L.md"), "Peso > 10%: recorte", 646.14)
            self.assertIn("comprada a 587,4 p", salida); self.assertIn("+10,0% en precio", salida)
            self.assertIn("objetivo de 748 p a 3 años", salida); self.assertIn("Peso > 10%: recorte", salida)
            sin = os.path.join(tmp, "tesis/SIN.md")
            open(sin, "w").write(open(os.path.join(tmp, "tesis/NWG.L.md")).read().replace("## En pocas palabras", "## Otra cosa"))
            self.assertRaises(F.FaltaResumen, F.ficha_compra, sin, 587.4)            # sin resumen no hay compra
        finally:
            C.ROOT = raiz; shutil.rmtree(tmp)

if __name__ == "__main__":
    unittest.main(verbosity=1)
