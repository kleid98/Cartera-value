# RESUMEN DE SESIÓN — Cartera VALUE ex-USA

> **Qué es este archivo:** el documento de traspaso para que una sesión nueva de Claude Code, que no ha visto nada de lo
> hablado, pueda seguir el proyecto donde se dejó. Generado el **10/11/2026 (Madrid)**. Se sobrescribe en cada limpieza;
> solo vale la última versión. Para continuar, basta con decirle a Claude: *"lee RESUMEN-SESION.md y sigue"*.

---

## 1. Qué es el proyecto y en qué punto está

Una **cartera value simulada de 10.000 €** que gestiona Claude como si operase en IBKR durante al menos un año
(compras de ~500 €, máximo 20 valores, sin empresas de EE. UU.). Cada decisión se toma por **EV con 4 escenarios a
3 años** y pasa por un **comité de dos agentes independientes** (bajista y valorador ciego). Se ejecuta sola con 4 tareas
programadas y Ale copia las operaciones en Investing.

**Estado (10/11/2026, tarde):** **la cartera empieza el miércoles 11/11/2026** (Ale adelantó el inicio el 10/11; antes era
el lunes 16). La **Fase 0 va del 11 al 20/11/2026** y en ella se compran 20 valores.
- Sistema construido, auditado y con pruebas automáticas. **Todo está en `main`** (último commit de trabajo: `4fe6169`).
- 33 tesis escritas; 23 con comité completo. Las 20 de la Fase 0 elegidas y marcadas **🟡 provisional**.
- Cartera sin operaciones todavía: solo la aportación T-0001 de 10.000 €.
- **Las cuatro tareas programadas están activas** desde el 10/11. Primera APERTURA_UE: miércoles 11/11 a las 09:34 (Madrid).
- Equiduct probado **en vivo** el 10/11 (NatWest, BNP y JD Sports dan libro).

## 2. Decisiones clave y por qué (no reabrirlas)

Las reglas numéricas están en `config/reglas.json` y el manual de operación en `CLAUDE.md`. No se cambian sin acuerdo de Ale.

**Del grill-me de 21 preguntas (07/11/2026)**
- 1 año mínimo 100% virtual. El repo es la fuente de verdad; Investing es un espejo manual de Ale.
- IBKR Tiered, cuenta en EUR (Madrid en Fixed 0,05%, mínimo 3 €). Stamp duty, TTF, ITF y FX incluidos. Sin IRPF.
  Dividendos netos de retención en origen (Ale es residente fiscal en España).
- Universo: sin empresas con sede en EE. UU., bolsa de origen, nunca ADR; Europa + Japón y Canadá (≤ 30%); sin HK/China.
- Filtros duros: capitalización ≥ 2.000 M€, volumen ≥ 2 M€/día, ≥ 10 años, beneficio operativo + en ≥ 7/10,
  DN/EBITDA ≤ 3x (financieras CET1 ≥ 12%), sin insolvencia.
- Venta: TIR residual < 5%, tesis rota, algo mejor (+10 pp), peso > 10% → recorte al 7%. Sin stop-loss.
- Recompra: ≥ −20%, tesis revisada, +5 pp de TIR, máximo 3 compras / 10%, 30 días.
- Fase 0: invertir los 10.000 € en una semana. Si no hay 20 que pasen el umbral, se completa con las mejores TIR como
  🟡 provisionales (rotables con +5 pp durante 8 semanas). Máximo 4 por sector y 6 por país.
  **Innegociables:** filtros duros y desastre ≥ −50%.
- Ejecución: límite al bid de Equiduct (fila Retail); si no hay libro, último −0,10%; velas de 1 minuto con mínimo
  estrictamente < límite; órdenes DAY; 3.er día AGRESIVA. Japón: lote de 100 ≤ 750 €, orden APERTURA decidida en CIERRE.
- Avisos push solo cuando haya operaciones. Benchmarks: CEMS.DE (principal), EXUS.DE e IWDA.AS.

**Del 08–09/11/2026**
- **Universo ampliado a empresas medianas** (2.000–10.000 M€): `config/universo.csv` tiene 575 empresas.
- **Fase 0 el 11–20/11/2026** (Ale la adelantó del 16 al 11 el 10/11/2026; el final no cambia).
- **Umbral de TIR: 10% en la zona euro y 12% fuera** (antes 15%/17%). Motivo: en 23 comités ningún valorador pasó del 13%.
- **P(desastre) del comité = media de las tres** (propia, bajista, valorador; antes la más alta). Motivo: la más alta
  sesgaba la TIR a la baja en 16 de 23 casos.
- `compra_ok` exige que la TIR del comité **y** la TIR propia ajustada superen el umbral (el comité frena, no fuerza).
- **Criterios aplicados en los comités (míos, comunicados a Ale; no los ha objetado):**
  - **Valeo (FR.PA) excluida:** los dos miembros del comité ponen el desastre por debajo de −50%. Criterio: se excluye
    solo si **ambos** lo sitúan por debajo de −50% (por eso Harbour no se excluyó: valorador −56%, bajista −35/−45%).
  - **Mazda (7261.T) excluida:** veto del bajista por la condición 5 en lectura literal.
  - **Ayvens:** 9,4 años en bolsa, pero el negocio tiene más de 10 años de cuentas: se dio por bueno el filtro.
  - **Aegon no se analizó:** traslada su sede a EE. UU.

**De la revisión del sistema (09–10/11/2026).** Ale pidió una auditoría y aprobó las 10 propuestas ("hazlas todas").
Detalle en `informes/revision-2026-11-09.md`.
- **TIR del valorador exacta y neta.** Se guardaba redondeada al punto entero (un 12,8% guardado como 13% hizo que
  Teleperformance cruzara la frontera de los 5 pp) y bruta, mientras la propia era neta. Ahora se guarda bruta con 3–4
  decimales y `ev.py` la compara en neto: recalculada al precio del día y restando costes y retención de dividendos.
- **Diferencia ≥ 5 pp → la más baja + 2,5 pp** (antes la más baja a secas). Motivo: quitar el escalón (4,9 pp daba la
  media y 5,1 pp la más baja). Hoy ninguna de las 23 llega a 5 pp, así que aún no se ha aplicado.
- **Precio del día antes de cada orden** (`ev.py --precio-hoy`). Escenarios y probabilidades no se tocan. El desastre
  ≥ −50% se comprueba a ese precio; si no cumple, no se compra y entra la reserva.
- **La venta por TIR residual < 5% no se aplica a las provisionales** en sus primeras 8 semanas. Motivo: el plan compra
  Linamar (4,4%) y Ahold (4,8%); sin la exención, una sesión podría venderlas al día siguiente.
- **Grupo financiero** (bancos, seguros, financieras, gestoras) = un solo grupo de riesgo. Son 8 de 20 (40%): Ale lo
  acepta para la Fase 0 porque no hay reservas para sustituirlas. Después no entra ninguna financiera **nueva** mientras
  el grupo pese > 30% a coste. Magna y Linamar comparten riesgo (arancel del 01/01/2027): se revisan juntas.
- **El analista trabaja a ciegas** respecto a los umbrales. Motivo: 6 de 20 desastres estaban entre −47% y −49%, pegados
  a un límite que el analista conocía. Solo afecta a tesis nuevas; las escritas no se tocan.
- Para medir y aprender: registro de predicciones en cada compra, seguimiento en papel de las descartadas y pruebas
  automáticas del motor (ver sección 3).

**Ficha de entrada y de salida (10/11/2026, pedido por Ale).** Quiere que cada vez que se entre o se salga de un valor
se le explique la tesis del porqué y el precio objetivo. Hecho y en `main`:
- **Precio objetivo** = precio a 3 años del escenario central; **precio esperado** = media ponderada de los cuatro
  escenarios. Los da `ev.py` (`precio_objetivo`). No es una regla nueva: son los precios ya escritos en cada tesis.
- Cada tesis lleva una sección `## En pocas palabras` (qué es, por qué está barata, qué espero, qué me haría vender).
  Escrita para las 20 de la Fase 0 y BP.L. Las otras 11 tesis (descartadas) no la tienen: hay que escribirla si algún
  día se compran, porque **`cartera.py orden` no deja comprar sin ella**.
- `cartera.py orden` imprime la ficha (se pega en el diario) y añade el objetivo al motivo de la orden (llega al ledger
  y al panel); `cartera.py investing` pone el porqué bajo cada operación; el aviso al móvil lleva el objetivo.
  Detalle en `CLAUDE.md` sección 4.1. Ale vio un ejemplo (NatWest) y pidió subirlo a `main`; no ha pedido cambios de formato.

## 3. Qué se ha creado (rutas exactas)

**Repositorio y ramas**
- Repo: `kleid98/Cartera-value`. **`main` está al día.** Las tareas programadas trabajan en `main`.
- Rama de trabajo de las sesiones interactivas: `claude/sharp-ritchie-qqyy9n`, igual que `main`.
- PR #1 (fusionado el 09/11): https://github.com/kleid98/Cartera-value/pull/1. Desde entonces Ale autorizó subir
  directamente a `main` (lo ha confirmado cada vez que se le ha preguntado; no hay PR abiertos).

**Configuración**
- `config/reglas.json`: todas las reglas, incluidas las del 09–10/11 (`comite.tope_sobre_la_mas_baja_pp`,
  `comite.tir_valorador_neta`, `venta.tir_residual_exime_provisionales_semanas`, `grupos_de_riesgo`, `precio_al_ordenar`).
- `config/mercados.json`, `config/fiscalidad.json`, `config/universo.csv` (575 empresas).
- `config/panel.json` (URL del panel y pasos) y `config/tareas.json` (IDs de las tareas programadas).

**Scripts**
- `scripts/cartera.py`: motor (órdenes, validación, costes, FX, FIFO, dividendos, estado, benchmarks, Investing).
  Novedades: `tick_size` (salto de precio real), control de caja y de grupo de riesgo en `orden`, `cruce` (validación
  como función pura), `registrar_prediccion`, `seguir_descartadas`.
- `scripts/ev.py`: EV, TIR y reconciliación. Opciones: `--precio P`, `--precio-hoy`, `--ciego`.
- `scripts/comite.py tesis/X.md <dir>`: genera los prompts ciegos del bajista y del valorador.
- `scripts/comite_registrar.py tesis/X.md <informe_bajista> <informe_valorador>`: escribe los informes en la tesis y
  rellena el bloque ev (TIR exacta leída de la tabla del informe). Con `--recalcular tesis/X.md [<informe_valorador>]`
  rehace solo la reconciliación (para cuando cambian las reglas).
- `scripts/ficha.py`: ficha de entrada/salida (`tesis/X.md [--precio-hoy]`, `--venta --motivo "..."`, `--comprobar`).
- `scripts/test_motor.py`: 10 pruebas sin red. **Ejecutar tras cualquier cambio en `scripts/`.**
- `scripts/cribado.py` (~10 minutos con 575 empresas), `scripts/equiduct.js`, `scripts/panel.py`.

**Prompts y plantillas**
- `comite/bajista.md`, `comite/valorador_ciego.md` (ahora pide TIR con 3 decimales y `DIVIDENDOS_ESPERADOS_3A`),
  `comite/analista.md` (a ciegas: no lee `reglas.json`, usa `ev.py --ciego`), `plantillas/tesis.md`.

**Datos y análisis**
- `tesis/*.md`: 33 tesis; 23 con comité, recalculadas el 10/11 (fila nueva en el historial de las 20).
- `plan/fase0.md`: **plan definitivo de la Fase 0** (las 20, ISIN, mercado, TIR, calendario y reglas de ejecución).
- `plan/cribado.csv`, `plan/candidatos.md`, `plan/comite_informes/` (informes y prompts del comité).
- `ledger/operaciones.csv` (solo T-0001), `ledger/ordenes.csv` (vacío), `ledger/cartera.json`, `ledger/historico.csv`.
- `ledger/descartadas.csv`: 12 empresas analizadas y no compradas (Mazda, Valeo, BP, Suncor, OMV, voestalpine, Umicore,
  Crédit Agricole, Vallourec, Galp, Norsk Hydro, Eiffage). `estado --cierre` fija su precio el 11/11 y las sigue en papel.
- `ledger/predicciones.csv`: se crea solo con la primera compra ejecutada.
- `informes/revision-2026-11-09.md`: la auditoría, las 10 propuestas y su resultado.
- `investing/pendiente.md`, `investing/estado.json`, `investing/historico.md`.

**Las 20 de la Fase 0** (TIR del comité tras el recálculo del 10/11; todas 🟡 provisionales y por debajo de su umbral)

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

- Reserva: **BP.L** (3,9%; sería la 6.ª británica, cabe). FGR.PA no cabe (sería la 7.ª francesa).
- Límites: FR 6, GB 5, IT 2, NL 2, CA 2; fuera de Europa 10%; ningún sector pasa de 3.
- Compra de las 20 a precios del 06/11: 9.684 € (67 € de costes); quedan ~315 € de caja.

**Calendario** (en `plan/fase0.md`, desplazado un día el 12/11 porque el 11/11 se perdió; resultados en `plan/calendario.md`)
- Jueves 12/11: NWG, BNP, AYV (o BP si su desastre no cumple), HBR y NOVO (apertura de EE. UU.).
- Viernes 13/11: TEP, NN, SAN, AZM y MG (Toronto).
- Lunes 16/11: CNA, ISP, EN, FNTN (publicó sus 9 meses el 12/11) y LNR (Toronto).
- Martes 17/11: MAP, SCR, AD. Miércoles 18/11: IMB (tras sus resultados del 17/11).
- Jueves 19/11: JD (tras su trading statement). Viernes 20/11: lo que quede sin ejecutar va AGRESIVA.

**Panel (Artifact de tipo Dashboard)**
- URL: https://claude.ai/artifact/46h4ity964Kmw8rMaB8dxR. 6 datasets que leen un único asset `panel.json`.
- Copia de la página en `panel/index.html`. No tocar `files/index.html` salvo cambios de diseño.

**INCIDENTE DEL 11/11/2026 (leer antes de tocar las tareas).** Las tareas programadas abren sesiones nuevas **sin el
repositorio adjunto**: leen el repo pero el `git push` da 403, y `add_repo` no existe en esas sesiones. Se perdió todo lo
del CIERRE del 10/11 y de las tres ejecuciones del 11/11 (órdenes lanzadas dos veces y nunca guardadas; el 11/11 queda sin
operaciones, ver `diario/2026-11-11.md`). Comprobado el 12/11: una sesión creada con `create_session` y `source_url` del
repo **sí** puede escribir en `main`.
- **Arreglo definitivo (solo Ale, desde la web):** claude.ai/code/routines → cada una de las 4 tareas → Edit → Advanced
  settings → Repository → `kleid98/Cartera-value` → Save changes. Para comprobarlo: `update_trigger` con `enabled` igual
  al que tiene devuelve `session_request.config.sources`, que debe incluir el repo.
- **Mientras tanto:** las tres de entre semana están pausadas y cada ejecución se lanza con una sesión creada a mano con el
  repo adjunto más un aviso de un solo uso (`run_once_at`, `persistent_session_id`) que le manda el prompt a su hora. Los
  prompts están en `config/prompts/`. Hay que prepararlas cada día hasta que Ale haga el arreglo definitivo.
- No se creó un "lanzador" automático (una sesión que cree otras sesiones): el sistema lo bloqueó y necesita permiso de Ale.

**Tareas programadas** (sesión nueva en cada disparo; clonan el repo y siguen `CLAUDE.md` sobre `main`)

| Ejecución | ID | Horario | Estado |
|---|---|---|---|
| DOMINGO | `trig_01UnKHPrvh2AaPgsFJfzg9PC` | `CRON_TZ=Europe/Madrid 4 18 * * 0` | Activa (próxima: 15/11 18:04) |
| APERTURA_UE | `trig_01CEGapUaBpMEvxHmy3HZAt8` | `CRON_TZ=Europe/Madrid 34 9 * * 1-5` | Activa desde el 10/11 |
| APERTURA_US | `trig_01AikUWcNyEwnr1XY35S6jAY` | `CRON_TZ=America/New_York 4 10 * * 1-5` | Activa desde el 10/11 |
| CIERRE | `trig_01Q31HxP6FUV3dPWk9v1Rt2a` | `CRON_TZ=America/New_York 4 17 * * 1-5` | Activa desde el 10/11 |

- El aviso programado `trig_011kX84TnoPyCTLQZhcETF4c` (domingo 15/11 a las 21:00, para activar las tres pausadas) ya no
  hace falta y está **desactivado**.

## 4. Credenciales

No hay credenciales propias. Yahoo, el BCE/Frankfurter, Equiduct e IBKR son públicos. GitHub va con la integración de
la sesión.

## 5. Pendiente, en este orden

1. **Miércoles 11/11: primera ejecución real.** Ninguna tarea programada había corrido antes: revisar que APERTURA_UE
   (09:34), APERTURA_US (~16:04) y CIERRE (~23:04) han dejado commit en `main`, diario y, si hubo órdenes, aviso al móvil.
   Si alguna falla, la siguiente retoma; nunca registrar operaciones con fecha pasada.
2. **Ayvens:** con los precios del 09/11 su desastre es −50,2% (no cumple). Azimut (−49,0%) e Intesa (−49,4%) están al
   límite. Se decide con `ev.py --precio-hoy` en el momento de comprar; si Ayvens no cumple, entra BP.L.
3. **Lundbeck: cerrado (10/11/2026).** Ale aclaró que solo era un ejemplo de tamaño de empresa; añadirla o no es
   decisión del gestor. No se añade ahora: no salió del cribado, cotiza en máximos de 52 semanas y necesitaría una TIR
   del 12%. Si algún domingo aparece en el cribado, se trata como cualquier otra candidata.
4. Fechas sensibles del plan (detalle en `plan/calendario.md`):
   - MG: Investor Day el 11/11 (se compra el 12). FNTN: resultados de 9 meses el 11/11 o 12/11 (se compra después).
   - IMB: resultados anuales el 17/11 (se compra el 18). JD: trading statement el 19/11 (se compra después).
     En los tres casos, si se toca una condición de invalidación no se compra y entra BP. Solo hay una reserva: si
     fallan dos, la cartera se queda en 19.
   - MG y LNR: arancel del 50% a piezas canadienses anunciado para el 01/01/2027.
   - SCR: plan estratégico el 03/12. AZM: respuesta a Banca d'Italia a finales de noviembre; exclusividad de TNB hasta el 20/12.
   - BP: actualización estratégica en diciembre.
5. A vigilar sin acción ahora (lista completa en `informes/revision-2026-11-09.md`):
   - **Retención francesa:** el sistema usa 12,8%; no se pudo confirmar que IBKR no aplique el 25%. Hay 6 francesas.
   - **Dividendos de Yahoo:** Magna y Harbour declaran en USD; revisar a mano el primer dividendo de cada valor.
   - **Ventas en divisa:** lo cobrado en GBP/DKK/CAD se queda en esa divisa; no hay conversión de vuelta a EUR.

## 6. Cosas a tener en cuenta

**Límite de uso (lo más importante)**
- Ale pide **parar cuando el límite de 5 horas llegue al ~80%**. No se puede leer el porcentaje desde la sesión: estimar
  y quedarse corto. Él avisa de su porcentaje si se le pregunta. El 09/11 se quedó sin créditos a mitad de un trabajo.
- **Límite semanal:** el 10/11 estaba en aviso (cerca del tope) y se reinicia el domingo 15/11 a las 03:00 (Madrid). Si se
  agota, las tareas programadas fallan hasta entonces (ya pasó el 08/11 con otra tarea de Ale). Se le avisó el 10/11.
- Costes medidos: cada comité (bajista + valorador) ≈ 220–270k tokens, un 11–12% de una ventana. Cada tesis nueva con el
  agente analista ≈ 140–155k. Lanzar agentes **de uno en uno** (como mucho el par de un comité).
- Recalcular comités con `comite_registrar.py --recalcular` no usa agentes y gasta muy poco.

**Si se vuelven a cambiar reglas del comité**
- Recalcular los 23 con `--recalcular`, actualizar la tabla y la "Situación" de `plan/fase0.md`, la línea de Decisión y
  el historial de cada tesis, y este resumen. El 10/11 se hizo con un script puntual que no se guardó.
- Los dividendos del valorador se leen de la tabla de su informe; si no son del mismo orden que los de la tesis propia,
  se usan los de la tesis (evita errores de unidad). Los informes nuevos los dan en una línea aparte.

**Patrón observado en los comités**
- El bajista pone una P(desastre) del 8–30% (media 18%), bastante por encima de la tesis propia (12%) y del valorador (9%).
- Ningún valorador ha pasado del 13% de TIR bruta. Las TIR finales están entre el 3,9% y el 9,9%.

**Yahoo y datos de mercado**
- Con un user-agent largo devuelve 429; funciona `User-Agent: Mozilla/5.0` (ya puesto). Los fundamentales necesitan
  cookie + crumb (`cribado.py`) y a veces dan 429 aunque los precios funcionen: en ese caso, usar búsqueda web.
- Errores frecuentes del cribado: el P/VC de Londres sale ×100 (peniques); el FCF yield y el EV/EBITDA se inflan por
  extraordinarios. El cribado solo sirve para ordenar.
- Londres cotiza en GBX: el motor lo convierte. Equiduct también da Londres en peniques (comprobado).

**Otras fuentes**
- Equiduct: `api.equiduct.com/mdwebapi/instrument` da el mapa ISIN → símbolo; el viewer acepta `?symbol=X&date=YYYYMMDD`.
  Se usa la fila "Retail". JD Sports no tenía libro en la prueba: va por último −0,10%.
- Investing.com da 403 a peticiones automáticas, Tweenvest da 404 e IBKR web solo responde con curl.

**Herramientas**
- `ev.py` y las pruebas no necesitan red, salvo `--precio-hoy`. `NODE_PATH` solo hace falta para Equiduct.
- Para probar órdenes sin tocar el libro real: copiar el repo a una carpeta temporal y ejecutar allí.
- Los hooks del repo exigen **commit y push** antes de terminar cada turno.

## 7. Preferencias de Ale para este proyecto

- Todo en español, en lenguaje llano. Quiere ver **cómo y por qué** se gestionan los cambios.
- Prefiere ir despacio antes que quemar el límite de uso.
- Las decisiones de reglas son suyas: plantearlas con datos y esperar su respuesta. Cuando aprueba, quiere que se haga
  todo de una vez y se suba a `main`.
- El resto, ver `CLAUDE.md`.
