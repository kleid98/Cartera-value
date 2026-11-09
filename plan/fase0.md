# Plan de la Fase 0 — BORRADOR (09/11/2026)

> **Borrador.** Faltan el comité de AZM.MI, SCR.PA, LNR.TO y de la reserva elegida. Las fechas son una **propuesta
> pendiente de confirmar con Ale** (la Fase 0 ya no empieza el 09/11). Cuando se confirmen hay que actualizar
> `config/reglas.json` (`fecha_inicio`, `fase0.inicio`, `fase0.fin`) y las menciones de "09–13/11/2026" en `CLAUDE.md`.

**Fechas propuestas:** lunes 16/11 – viernes 20/11/2026 (requiere PR fusionado y tareas reanudadas antes del lunes).

## Situación
Ninguna candidata alcanza la TIR mínima (15% euro / 17% fuera del euro), así que las 20 entran como **🟡 provisionales**
(`--provisional`): se pueden rotar con +5 pp de mejora durante sus primeras 8 semanas. Innegociables cumplidos en todas:
filtros duros y desastre ≥ −50%. Límites: máx. 6 por país y 4 por sector.

## Las 20 (orden de prioridad = TIR del comité)

| # | Ticker | Empresa | ISIN | Mercado | País | Sector | TIR comité | Precio ref. | ~Acciones (500 €) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | NWG.L | NatWest Group | GB00BM8PJY71 | LONDRES | GB | Bancos | 9,4% | 587,4p | 71 |
| 2 | IMB.L | Imperial Brands | GB0004544929 | LONDRES | GB | Tabaco | 8,3% | 2.973p | 14 |
| 3 | AYV.PA | Ayvens | FR0013258662 | PARIS | FR | Financieras | 8,1% | 9,62 € | 52 |
| 4 | NOVO-B.CO | Novo Nordisk | DK0062498333 | COPENHAGUE | DK | Salud | 7,8% | 269,45 DKK | 13 |
| 5 | SAN.PA | Sanofi | FR0000120578 | PARIS | FR | Salud | 7,3% | 83,74 € | 5 |
| 6 | NN.AS | NN Group | NL0010773842 | AMSTERDAM | NL | Seguros | 7,1% | 79,18 € | 6 |
| 7 | CNA.L | Centrica | GB00B033F229 | LONDRES | GB | Utilities | 6,6% | 151,5p | 275 |
| 8 | BNP.PA | BNP Paribas | FR0000131104 | PARIS | FR | Bancos | 6,6% | 91,93 € | 5 |
| 9 | EN.PA | Bouygues | FR0000120503 | PARIS | FR | Construcción | 6,2% | 42,29 € | 11 |
| 10 | ISP.MI | Intesa Sanpaolo | IT0000072618 | MILAN | IT | Bancos | 6,2% | 6,18 € | 80 |
| 11 | MAP.MC | Mapfre | ES0124244E34 | MADRID | ES | Seguros | 5,6% | 4,13 € | 121 |
| 12 | TEP.PA | Teleperformance | FR0000051807 | PARIS | FR | Servicios | 4,9% | 68,44 € | 7 |
| 13 | FNTN.DE | freenet | DE000A0Z2ZZ5 | XETRA | DE | Telecomunicaciones | 4,8% | 23,34 € | 21 |
| 14 | JD.L | JD Sports Fashion | GB00BM8Q5M07 | LONDRES | GB | Distribución | 4,8% | 95,34p | 437 |
| 15 | MG.TO | Magna International | CA5592224011 | TORONTO | CA | Automóvil | 4,5% | 87,38 CAD | 8 |
| 16 | HBR.L | Harbour Energy | GB00BMBVGQ36 | LONDRES | GB | Energía | 3,9% | 263,4p | 158 |
| 17 | AZM.MI | Azimut Holding | IT0003261697 | MILAN | IT | Gestión de activos | 4,0% | 35,82 € | 13 |
| 18 | SCR.PA | SCOR | FR0010411983 | PARIS | FR | Seguros | 5,1% | 34,68 € | 14 |
| 19 | LNR.TO | Linamar | CA53278L1076 | TORONTO | CA | Automóvil | (propia 4,9%) | 86,29 CAD | 9 |
| 20 | reserva | AD.AS (Ahold, NL) o BP.L (BP, GB) | — | — | — | — | (propia 4,0%) | — | — |

- Reserva: **FGR.PA no cabe** (sería la 7.ª francesa). AD.AS o BP.L, la que salga mejor del comité.
- Conteo: FR 6 · GB 5 (6 con BP) · IT 2 · CA 2 · NL 1 (2 con AD) · DK, ES, DE 1. Sectores: bancos 3, seguros 3, resto ≤ 2.
  Fuera de Europa: 2 de 20 (10%).
- Excluidas: Mazda (veto del bajista), Valeo (desastre del comité < −50%), SU, OMV, VOE, UMI (desastre < −50%),
  ACA (CET1), VK (beneficio operativo 4/10). GALP y NHY quedan por detrás por TIR y asimetría < 2.
- Las cantidades se recalculan al lanzar la orden (`--importe 500`); los precios de referencia son del 06/11/2026.

## Calendario propuesto (5 compras/día lunes–jueves; viernes solo reintentos)

| Día | APERTURA_UE (09:30) | APERTURA_US (~16:00) |
|---|---|---|
| Lun 16/11 | NWG.L, IMB.L, AYV.PA, NOVO-B.CO | SAN.PA |
| Mar 17/11 | NN.AS, CNA.L, BNP.PA, EN.PA | ISP.MI |
| Mié 18/11 | MAP.MC, TEP.PA, FNTN.DE, HBR.L | MG.TO (Toronto) |
| Jue 19/11 | AZM.MI, SCR.PA, reserva | JD.L (tras su trading statement del 19/11), LNR.TO (Toronto) |
| Vie 20/11 | Reintentos | Reintentos; lo que quede sin ejecutar va AGRESIVA para cerrar las 20 |

Reglas de ejecución:
- Por defecto PASIVA (bid de Equiduct; si no hay libro o el spread > 1%: último −0,10%). Toronto: último −0,10%.
- Si una compra lleva **2 días** caducando, el 3.er día va **AGRESIVA** (`dias_sin_ejecutar_antes_de_ask: 2`).
- Las órdenes del jueves que caduquen el viernes en APERTURA_UE se relanzan AGRESIVAS en APERTURA_US del viernes
  (último día de la Fase 0).
- Antes de cada orden: revisar noticias. **FNTN:** resultados de 9M el 11/11 (antes de la Fase 0; revisar si tocan una
  condición de invalidación). **JD:** trading statement del Q3 el 19/11; si recorta la guía FY27 se cumple la condición 1
  y no se compra (entra la siguiente reserva). **MG:** el arancel del 50% a piezas canadienses (01/01/2027) es una condición
  de vigilancia; si se firma un acuerdo antes, mejor.
- Todas con `--provisional` y motivo "Fase 0 provisional: TIR comité X%".
