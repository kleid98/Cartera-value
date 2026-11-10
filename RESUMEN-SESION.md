# RESUMEN DE SESIÓN — Cartera VALUE ex-USA

> **Qué es este archivo:** el documento de traspaso para que una sesión nueva de Claude Code, que no ha visto nada de lo
> hablado, pueda seguir el proyecto donde se dejó. Generado el **09/11/2026 (Madrid)**. Se sobrescribe en cada limpieza;
> solo vale la última versión. Para continuar, basta con decirle a Claude: *"lee RESUMEN-SESION.md y sigue"*.

---

## 1. Qué es el proyecto y en qué punto está

Una **cartera value simulada de 10.000 €** que gestiona Claude como si operase en IBKR durante al menos un año
(compras de ~500 €, máximo 20 valores, sin empresas de EE. UU.). Cada decisión se toma por **EV con 4 escenarios a
3 años** y pasa por un **comité de dos agentes independientes**. Se ejecuta sola con 4 tareas programadas y Ale copia
las operaciones en Investing.

**Estado (09/11/2026):** la preparación está **terminada**.
- Sistema construido y probado; **PR #1 fusionado en `main`** (lo fusionó Ale el 09/11 a las 11:46 UTC).
- 33 tesis escritas; **comité completo** en las 20 de la Fase 0 y en las reservas.
- **Plan de la Fase 0 escrito** (`plan/fase0.md`): del **lunes 16/11 al viernes 20/11/2026** (fecha confirmada por Ale).
- Las 20 tesis están marcadas **🟡 provisional**.
- **Reglas revisadas con Ale hoy** (umbral y reconciliación, ver 2). **Ya en `main`** (push directo autorizado por Ale el 09/11).
- Tarea **DOMINGO activa** (primera: 15/11 18:04). Las 3 de entre semana siguen **pausadas** hasta el domingo 15/11 por la noche
  (aviso programado a esta sesión, `trig_011kX84TnoPyCTLQZhcETF4c`, 15/11 21:00 Madrid, para activarlas).
- Cartera aún sin operaciones: solo la aportación T-0001 de 10.000 €.

## 2. Decisiones clave y por qué (no reabrirlas)

Las reglas numéricas están en `config/reglas.json` y el manual de operación en `CLAUDE.md`.

**Del grill-me de 21 preguntas (07/11/2026)**
- 1 año mínimo 100% virtual. El repo es la fuente de verdad; Investing es un espejo manual de Ale.
- IBKR Tiered, cuenta en EUR (Madrid en Fixed 0,05%, mínimo 3 €). Stamp duty, TTF, ITF y FX incluidos. Sin IRPF.
  Dividendos netos de retención en origen (Ale es residente fiscal en España).
- Universo: sin empresas con sede en EE. UU., bolsa de origen, nunca ADR; Europa + Japón y Canadá (≤ 30%); sin HK/China;
  sin exclusiones sectoriales.
- Filtros duros: capitalización ≥ 2.000 M€, volumen ≥ 2 M€/día, ≥ 10 años, beneficio operativo + en ≥ 7/10,
  DN/EBITDA ≤ 3x (financieras CET1 ≥ 12%), sin insolvencia.
- Venta: TIR residual < 5%, tesis rota, algo mejor (+10 pp), peso > 10% → recorte al 7%. Sin stop-loss.
- Recompra: ≥ −20%, tesis revisada, +5 pp de TIR, máximo 3 compras / 10%, 30 días.
- Fase 0: invertir los 10.000 € en una semana. Si no hay 20 que pasen el umbral, se completa con las mejores TIR como
  🟡 provisionales (rotables con +5 pp durante 8 semanas). Máximo 4 por sector y 6 por país.
  **Innegociables:** filtros duros y desastre ≥ −50%.
- Ejecución: límite al bid de Equiduct (fila Retail); fallback último −0,10%; velas de 1 minuto con mínimo
  estrictamente < límite; órdenes DAY; 3.er día AGRESIVA. Japón: lote de 100 ≤ 750 €, orden APERTURA decidida en CIERRE.
- Avisos push solo cuando haya operaciones. Benchmarks: CEMS.DE (principal), EXUS.DE e IWDA.AS.

**De esta sesión (08–09/11/2026)**
- **Opción B (Ale):** ampliar el universo a empresas medianas (2.000–10.000 M€). Se añadieron 378 empresas:
  `config/universo.csv` pasa a 575. El filtro de capitalización ya permitía ≥ 2.000 M€, así que no hizo falta tocar reglas.
- **Fechas de la Fase 0 (Ale):** 16–20/11/2026. Ya actualizadas en `reglas.json` (`fecha_inicio`, `fase0.inicio/fin`),
  `CLAUDE.md` y `plan/fase0.md`.
- **Cambio de reglas (Ale, 09/11):**
  - **Umbral de TIR: 10% en la zona euro y 12% fuera del euro** (antes 15%/17%). Motivo: en 23 comités, ningún valorador
    independiente pasó del 13%; el 15% equivalía a pedir el doble que el mercado.
  - **P(desastre) del comité = media de las tres** (propia, bajista y valorador; antes la más alta). Motivo: con la más
    alta, en 16 de 23 casos la TIR final quedaba por debajo de la propia y de la del valorador, un sesgo sistemático a la baja.
  - Se mantienen: veto del bajista, diferencia < 5 pp → media de TIR, ≥ 5 pp → la más baja, desastre ≥ −50%, asimetría ≥ 2.
  - En código: `config/reglas.json` (`ev.tir_min_*` y `comite.prob_desastre_modo: "media"`) y `scripts/ev.py`. La media
    puede **bajar** la P(desastre) por debajo de la propia; el código lo aplica en los dos sentidos.
  - `compra_ok` exige que la TIR del comité **y** la TIR propia ajustada superen el umbral (el comité puede frenar, no forzar).
- **Revisión del sistema (09–10/11, Ale aprobó las 10 propuestas; detalle en `informes/revision-2026-11-09.md`):**
  - TIR del valorador **exacta** (un redondeo de 12,8% a 13% penalizaba a Teleperformance) y **neta** (mismos costes y
    retención que la propia, recalculada al precio del día). Si la diferencia con la propia es ≥ 5 pp: **la más baja + 2,5 pp**.
  - **Precio del día antes de cada orden** (`ev.py --precio-hoy`); el desastre ≥ −50% se comprueba a ese precio.
  - La venta por **TIR residual < 5% no se aplica a las provisionales** en sus primeras 8 semanas.
  - **Grupo financiero** (bancos, seguros, financieras, gestoras): aceptado el 40% en la Fase 0; después no entra ninguna
    financiera nueva mientras pese > 30% (lo bloquea `cartera.py orden`).
  - El **analista trabaja a ciegas** respecto a los umbrales (`comite/analista.md`, `ev.py --ciego`).
  - Motor: salto de precio real (MiFID II), control de caja, `ledger/predicciones.csv` (automático en cada compra),
    `ledger/descartadas.csv` (12 empresas seguidas en papel desde el 16/11) y `scripts/test_motor.py` (10 pruebas).
- **Criterios aplicados en los comités (míos, comunicados a Ale; no los ha objetado):**
  - **Valeo (FR.PA) excluida:** los dos miembros del comité ponen el desastre por debajo de −50% (−54% y −55%), frente al
    −49,8% propio. Criterio: se excluye solo si **ambos** miembros lo sitúan por debajo de −50% en retorno total.
  - **Mazda (7261.T) excluida:** veto del bajista por la condición 5 en lectura literal (el CX-5 vendió menos que el modelo
    anterior en EE. UU. dos trimestres seguidos). Ale puede pedir la lectura alternativa ("lanzamiento completo").
  - **Ayvens:** solo 9,4 años en bolsa (como ALD), pero el negocio tiene más de 10 años de cuentas: se dio por bueno el filtro.
  - **Aegon no se analizó:** traslada su sede a EE. UU.

## 3. Qué se ha creado (rutas exactas)

**Repositorio y ramas**
- Repo: `kleid98/Cartera-value`. `main` está al día (incluye `1082b3c`, el cambio de reglas, subido el 09/11).
- Rama de trabajo: `claude/sharp-ritchie-qqyy9n`, igual que `main`. Las ejecuciones programadas trabajan en `main`.
- PR #1 (fusionado): https://github.com/kleid98/Cartera-value/pull/1

**Configuración**
- `config/reglas.json` (umbral 10%/12% y P(desastre) media en la rama), `config/mercados.json`, `config/fiscalidad.json`.
- `config/universo.csv`: 575 empresas.
- `config/panel.json`: URL del panel y pasos para actualizarlo. `config/tareas.json`: IDs de las tareas programadas.

**Scripts**
- `scripts/cartera.py`: motor de órdenes, validación, costes, FX, FIFO, dividendos, estado, benchmarks e Investing.
- `scripts/equiduct.js`: libro de Equiduct (`NODE_PATH=$(npm root -g) node scripts/equiduct.js ISIN MIC [YYYYMMDD]`).
- `scripts/ev.py`: EV, TIR y reconciliación del comité (regla de la media desde el 09/11).
- `scripts/cribado.py`: cribado con Yahoo quoteSummary (cookie + crumb). Tarda ~10 minutos con 575 empresas.
- `scripts/comite.py tesis/X.md <dir>`: genera los prompts ciegos del bajista y del valorador; el prompt dice al agente
  que guarde su informe en `<dir>/informe_{bajista|valorador}_X.md`.
- `scripts/comite_registrar.py tesis/X.md <informe_bajista> <informe_valorador>`: escribe los informes en la tesis,
  rellena el bloque ev y la reconciliación.
- `scripts/panel.py`: genera `panel/panel.json`.

**Documentación, prompts y plantillas**
- `CLAUDE.md`: manual de operación de las ejecuciones programadas (ya con fechas 16–20/11 y reglas nuevas en la rama).
- `comite/bajista.md`, `comite/valorador_ciego.md`, **`comite/analista.md`** (nuevo: prompt del agente que redacta una
  tesis nueva), `plantillas/tesis.md`.

**Datos y análisis**
- `tesis/*.md`: 33 tesis. 23 con comité.
- `plan/fase0.md`: **plan definitivo de la Fase 0** (las 20, ISIN, mercado, TIR, calendario por día y ejecución).
- `plan/cribado.csv`, `plan/candidatos.md`: cribado del universo ampliado.
- `plan/comite_informes/`: todos los informes del comité y copias de los prompts.
- `ledger/operaciones.csv` (solo T-0001), `ledger/ordenes.csv` (vacío), `ledger/cartera.json`, `ledger/historico.csv`.
- `investing/pendiente.md`, `investing/estado.json`, `investing/historico.md`.

**Las 20 de la Fase 0** (TIR del comité tras el recálculo del 10/11; todas 🟡 provisionales; todas por debajo de su umbral). Ver la tabla completa en `plan/fase0.md`.

| # | Ticker | TIR comité | # | Ticker | TIR comité |
|---|---|---|---|---|---|
| 1 | NWG.L | 9,9% | 11 | NN.AS | 7,2% |
| 2 | TEP.PA | 9,9% | 12 | SAN.PA | 6,9% |
| 3 | BNP.PA | 9,8% | 13 | CNA.L | 6,7% |
| 4 | JD.L | 8,8% | 14 | AZM.MI | 6,4% |
| 5 | AYV.PA | 8,7% | 15 | ISP.MI | 6,2% |
| 6 | FNTN.DE | 8,5% | 16 | EN.PA | 6,2% |
| 7 | IMB.L | 8,4% | 17 | MAP.MC | 5,4% |
| 8 | MG.TO | 8,0% | 18 | SCR.PA | 5,4% |
| 9 | HBR.L | 7,9% | 19 | AD.AS | 4,8% |
| 10 | NOVO-B.CO | 7,3% | 20 | LNR.TO | 4,4% |

- Reserva: **BP.L** (3,9%; sería la 6.ª británica). FGR.PA no cabe (sería la 7.ª francesa).
- Excluidas: 7261.T (veto), FR.PA (desastre del comité), SU.TO, OMV.VI, VOE.VI, UMI.BR (desastre < −50%),
  ACA.PA (CET1 11,2%), VK.PA (beneficio operativo 4/10). GALP.LS y NHY.OL quedan detrás por TIR y asimetría < 2.
- Límites: FR 6, GB 5, IT 2, NL 2, CA 2; fuera de Europa 10%; ningún sector pasa de 3.

**Calendario** (en `plan/fase0.md`):
- Lunes 16/11: NWG, BNP, AYV, IMB (apertura europea) y NOVO (apertura de EE. UU.).
- Martes 17/11: HBR, TEP, NN, SAN y MG (Toronto).
- Miércoles 18/11: AZM, CNA, ISP, FNTN y EN.
- Jueves 19/11: MAP, SCR, AD; JD después de su trading statement; LNR (Toronto).
- Viernes 20/11: reintentos; lo que quede sin ejecutar va AGRESIVA.

**Panel (Artifact de tipo Dashboard)**
- URL: https://claude.ai/artifact/46h4ity964Kmw8rMaB8dxR.
- 6 datasets que leen un único asset `panel.json`. El asset actual es `/_blob/aa12e649d3bbd59b5b05ec01fd2f0414`.
- Copia de la página en `panel/index.html`. No tocar `files/index.html` salvo cambios de diseño.

**Tareas programadas** (sesión nueva en cada disparo; clonan el repo y siguen `CLAUDE.md` sobre `main`). DOMINGO activa; las otras 3 pausadas hasta el 15/11.

| Ejecución | ID | Horario |
|---|---|---|
| APERTURA_UE | `trig_01CEGapUaBpMEvxHmy3HZAt8` | `CRON_TZ=Europe/Madrid 34 9 * * 1-5` |
| APERTURA_US | `trig_01AikUWcNyEwnr1XY35S6jAY` | `CRON_TZ=America/New_York 4 10 * * 1-5` |
| CIERRE | `trig_01Q31HxP6FUV3dPWk9v1Rt2a` | `CRON_TZ=America/New_York 4 17 * * 1-5` |
| DOMINGO | `trig_01UnKHPrvh2AaPgsFJfzg9PC` | `CRON_TZ=Europe/Madrid 4 18 * * 0` |

## 4. Credenciales

No hay credenciales propias. Yahoo, el BCE/Frankfurter, Equiduct e IBKR son públicos. GitHub va con la integración de
la sesión.

## 5. Pendiente, en este orden

1. ✅ Reglas nuevas en `main` (09/11, push directo con permiso de Ale).
2. ✅ DOMINGO reanudada. **Domingo 15/11 a las 21:00 (Madrid)**: activar APERTURA_UE, APERTURA_US y CIERRE
   (`update_trigger` con `enabled=true`). Hay un aviso programado a la sesión original; si no llega, hacerlo a mano
   y comprobar que la primera APERTURA_UE cae el 16/11 a las 08:34 UTC. Los prompts ya mandan leer `CLAUDE.md` y `plan/fase0.md`.
2b. ✅ Revisión del 09–10/11 hecha y subida a `main` (10 mejoras). **Aviso para el lunes 16:** con los precios del 09/11,
   Ayvens ya no cumple el desastre (−50,2%) y Azimut e Intesa están a menos de 1 punto. Se decide con el precio del día
   (`ev.py --precio-hoy`); si Ayvens no cumple, entra BP.L (sería la 6.ª británica, cabe).
3. **Lunes 16/11, primera ejecución:** comprobar el libro de Equiduct **en vivo** (solo se probó en modo replay).
4. Vigilar las fechas sensibles del plan:
   - FNTN: resultados de 9 meses el 11/11.
   - JD: trading statement el 19/11. Si recorta la guía, no se compra y entra BP.
   - MG y LNR: arancel del 50% a piezas canadienses anunciado para el 01/01/2027.
   - SCR: plan estratégico el 03/12.
   - AZM: respuesta a Banca d'Italia a finales de noviembre y exclusividad de TNB hasta el 20/12.
   - BP: plan estratégico el 15/12.
   - Mazda: resultados del semestre el 09/11.

## 6. Cosas a tener en cuenta

**Límite de uso (lo más importante)**
- Ale pide **parar cuando el límite de 5 horas llegue al ~80%**. No hay forma de leer el porcentaje desde la sesión: estimar
  y quedarse corto. Él avisa de su porcentaje si se le pregunta.
- Costes medidos: cada comité (bajista + valorador) ≈ 220–270k tokens, unos 11–12% de una ventana. Cada tesis nueva con
  el agente analista ≈ 140–155k. Lanzar agentes **de uno en uno** (como mucho el par de un comité).
- Si un agente se corta por el límite, en la misma sesión se reanuda con SendMessage a su ID; en una sesión nueva hay que
  relanzarlo.

**Patrón observado en los comités**
- El bajista pone una P(desastre) del 8–30% (media 18%), mucho más alta que la tesis propia (12%) y el valorador (9%).
- Ningún valorador ha pasado del 13% de TIR. Las TIR finales con las reglas nuevas están entre el 3,9% y el 10,2%.

**Yahoo y datos de mercado**
- Con un user-agent largo devuelve 429; funciona `User-Agent: Mozilla/5.0` (ya puesto). Los fundamentales necesitan
  cookie + crumb (`cribado.py`).
- Errores frecuentes: el P/VC de Londres sale ×100 (peniques); el FCF yield y el EV/EBITDA se inflan por extraordinarios
  (p. ej. Harbour con un FCF yield del 91%); en Vallourec el dividendo sale a 0 y las acciones mal contadas. El cribado
  solo sirve para ordenar.
- Londres cotiza en GBp/GBX: el motor lo convierte.

**Otras fuentes**
- Equiduct: `api.equiduct.com/mdwebapi/instrument` da el mapa ISIN → símbolo; el viewer acepta `?symbol=X&date=YYYYMMDD`.
  Se usa la fila "Retail". Spread > 1% → último −0,10%.
- Investing.com da 403 a peticiones automáticas, Tweenvest da 404 e IBKR web solo responde con curl.

**Herramientas**
- `comite_registrar.py` toma la TIR **redondeada** del valorador (`TIR_ANUAL: 0.07`).
- `ev.py` necesita `NODE_PATH` solo para Equiduct; para la EV basta con python.
- Los hooks del repo exigen **commit y push** antes de terminar cada turno.

## 7. Preferencias de Ale para este proyecto

- Todo en español, en lenguaje llano. Quiere ver **cómo y por qué** se gestionan los cambios.
- Prefiere ir despacio antes que quemar el límite de uso.
- Las decisiones de reglas son suyas: plantearlas con datos y esperar su respuesta. No cambiar `reglas.json` sin su acuerdo.
- El resto, ver `CLAUDE.md`.
