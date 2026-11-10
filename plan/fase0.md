# Plan de la Fase 0 (16–20/11/2026)

> Fechas confirmadas por Ale el 09/11/2026 (la Fase 0 iba a ser el 09–13/11 y se retrasó una semana para terminar el comité).
> `config/reglas.json` y `CLAUDE.md` ya están actualizados.

## Situación
**Reglas revisadas con Ale el 09/11/2026:** umbral de TIR 10% (zona euro) / 12% (fuera del euro), antes 15%/17%; y
P(desastre) del comité = media de las tres (propia, bajista, valorador), antes la más alta.

**Revisión del 09–10/11/2026 (acordada con Ale):** la TIR del valorador se usa exacta (antes redondeada al punto entero)
y en neto (se le restan los mismos costes y retenciones que a la propia); si la diferencia con la propia es ≥ 5 pp, la
TIR del comité es la más baja + 2,5 pp (antes la más baja a secas). Recalculados los 23 comités: **las 20 son las mismas**
y cambia el orden (Teleperformance sube del puesto 9 al 2: el redondeo de 12,8% a 13% la penalizaba; freenet del 15 al 6).

Ninguna candidata cumple todas las reglas de compra (`compra_ok`), así que las 20 entran como **🟡 provisionales**
(`--provisional`): rotables con +5 pp de mejora durante sus primeras 8 semanas, y en ese plazo no se les aplica la venta
por TIR residual < 5% (Linamar y Ahold están por debajo). Innegociables cumplidos en todas: filtros duros y desastre
≥ −50%. Límites: máx. 6 por país y 4 por sector.

## Las 20 (orden de prioridad = TIR del comité). Todas con comité completo.

| # | Ticker | Empresa | ISIN | Mercado | País | Sector | TIR comité | TIR propia ajust. | Umbral | Precio ref. | ~Acciones (500 €) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | NWG.L | NatWest Group | GB00BM8PJY71 | LONDRES | GB | Bancos | 9,9% | 9,5% | 12,0% | 587,4p | 71 |
| 2 | TEP.PA | Teleperformance | FR0000051807 | PARIS | FR | Servicios | 9,9% | 7,9% | 10,0% | 68,44 € | 7 |
| 3 | BNP.PA | BNP Paribas | FR0000131104 | PARIS | FR | Bancos | 9,8% | 8,1% | 10,0% | 91,93 € | 5 |
| 4 | JD.L | JD Sports Fashion | GB00BM8Q5M07 | LONDRES | GB | Distribución | 8,8% | 7,4% | 12,0% | 95,34p | 437 |
| 5 | AYV.PA | Ayvens | FR0013258662 | PARIS | FR | Financieras | 8,7% | 8,6% | 10,0% | 9,62 € | 52 |
| 6 | FNTN.DE | freenet | DE000A0Z2ZZ5 | XETRA | DE | Telecomunicaciones | 8,5% | 6,8% | 10,0% | 23,34 € | 21 |
| 7 | IMB.L | Imperial Brands | GB0004544929 | LONDRES | GB | Tabaco | 8,4% | 8,0% | 12,0% | 2.973p | 14 |
| 8 | MG.TO | Magna International | CA5592224011 | TORONTO | CA | Automóvil | 8,0% | 6,2% | 12,0% | 87,38 CAD | 8 |
| 9 | HBR.L | Harbour Energy | GB00BMBVGQ36 | LONDRES | GB | Energía | 7,9% | 7,0% | 12,0% | 263,4p | 158 |
| 10 | NOVO-B.CO | Novo Nordisk | DK0062498333 | COPENHAGUE | DK | Salud | 7,3% | 7,4% | 12,0% | 269,45 DKK | 13 |
| 11 | NN.AS | NN Group | NL0010773842 | AMSTERDAM | NL | Seguros | 7,2% | 6,8% | 10,0% | 79,18 € | 6 |
| 12 | SAN.PA | Sanofi | FR0000120578 | PARIS | FR | Salud | 6,9% | 6,7% | 10,0% | 83,74 € | 5 |
| 13 | CNA.L | Centrica | GB00B033F229 | LONDRES | GB | Utilities | 6,7% | 7,2% | 12,0% | 151,5p | 275 |
| 14 | AZM.MI | Azimut Holding | IT0003261697 | MILAN | IT | Gestión de activos | 6,4% | 5,3% | 10,0% | 35,82 € | 13 |
| 15 | ISP.MI | Intesa Sanpaolo | IT0000072618 | MILAN | IT | Bancos | 6,2% | 6,0% | 10,0% | 6,18 € | 80 |
| 16 | EN.PA | Bouygues | FR0000120503 | PARIS | FR | Construcción | 6,2% | 7,1% | 10,0% | 42,29 € | 11 |
| 17 | MAP.MC | Mapfre | ES0124244E34 | MADRID | ES | Seguros | 5,4% | 4,7% | 10,0% | 4,13 € | 121 |
| 18 | SCR.PA | SCOR | FR0010411983 | PARIS | FR | Seguros | 5,4% | 5,3% | 10,0% | 34,68 € | 14 |
| 19 | AD.AS | Ahold Delhaize | NL0011794037 | AMSTERDAM | NL | Distribución alimentaria | 4,8% | 4,4% | 10,0% | 34,22 € | 14 |
| 20 | LNR.TO | Linamar | CA53278L1076 | TORONTO | CA | Automóvil | 4,4% | 3,9% | 12,0% | 86,29 CAD | 9 |

- **Reserva:** BP.L (TIR comité 3,9%; sería la 6.ª británica). FGR.PA no cabe (7.ª francesa).
- Conteo: FR 6 · GB 5 · IT 2 · NL 2 · CA 2 · DK, ES, DE 1. Sectores: bancos 3, seguros 3, automóvil 2, salud 2, distribución 2
  (JD y AD si se cuentan juntas), resto 1. Fuera de Europa: 2 de 20 (10%).
- Excluidas: Mazda (veto del bajista), Valeo (desastre del comité < −50%), SU, OMV, VOE, UMI (desastre < −50%),
  ACA (CET1), VK (beneficio operativo 4/10). GALP y NHY quedan por detrás por TIR y asimetría < 2.
- Financieras (bancos, seguros, Ayvens y Azimut): 8 de 20 (40%). Aceptado por Ale para la Fase 0; después no entra ninguna
  financiera nueva mientras el grupo pese más del 30% (`grupos_de_riesgo` en `reglas.json`). Magna y Linamar comparten el
  riesgo del arancel del 01/01/2027: se revisan juntas.
- Las cantidades se recalculan al lanzar la orden (`--importe 500`); los precios de referencia son del 06/11/2026.
- El orden de la tabla cambió con el recálculo del 10/11; el calendario de abajo se mantiene (todas se compran en la semana).

## Calendario (5 compras/día lunes–jueves; viernes solo reintentos)

| Día | APERTURA_UE (09:30) | APERTURA_US (~16:00) |
|---|---|---|
| Lun 16/11 | NWG.L, BNP.PA, AYV.PA, IMB.L | NOVO-B.CO |
| Mar 17/11 | HBR.L, TEP.PA, NN.AS, SAN.PA | MG.TO (Toronto) |
| Mié 18/11 | AZM.MI, CNA.L, ISP.MI, FNTN.DE | EN.PA |
| Jue 19/11 | MAP.MC, SCR.PA, AD.AS | JD.L (tras su trading statement del 19/11), LNR.TO (Toronto) |
| Vie 20/11 | Reintentos | Reintentos; lo que quede sin ejecutar va AGRESIVA para cerrar las 20 |

Reglas de ejecución:
- **Antes de cada orden: `python3 scripts/ev.py tesis/X.md --precio-hoy`.** Recalcula la TIR con el precio del día (escenarios
  y probabilidades no se tocan). Si a ese precio el desastre queda por debajo de −50%, **no se compra** (innegociable) y
  entra la reserva. Si la TIR del comité cae por debajo de la de la reserva (BP.L, recalculada igual), entra la reserva
  (si cabe en los límites de país y sector). En los dos casos se anota en el diario. Ojo con Ayvens (desastre −49,1%
  al precio de la tesis: con una subida de ~2% deja de cumplir). La TIR recalculada va en el motivo de la orden.
- Por defecto PASIVA (bid de Equiduct; si no hay libro o el spread > 1%: último −0,10%). Toronto: último −0,10%.
- Si una compra lleva **2 días** caducando, el 3.er día va **AGRESIVA** (`dias_sin_ejecutar_antes_de_ask: 2`).
- Las órdenes del jueves que caduquen el viernes en APERTURA_UE se relanzan AGRESIVAS en APERTURA_US del viernes
  (último día de la Fase 0).
- Antes de cada orden: revisar noticias y las condiciones de invalidación de la tesis. Fechas sensibles:
  **FNTN** resultados 9M el 11/11; **JD** trading statement Q3 el 19/11 (si recorta la guía FY27 se cumple la condición 1:
  no se compra y entra la reserva BP.L); **MG y LNR** arancel del 50% a piezas canadienses anunciado para el 01/01/2027;
  **SCR** plan estratégico 03/12; **AZM** respuesta a Banca d'Italia (fin de noviembre) y exclusividad de TNB (20/12).
- Todas con `--provisional` y motivo "Fase 0 provisional: TIR comité X%".
