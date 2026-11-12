# RESUMEN DE SESIÓN — Cartera VALUE ex-USA

> **Qué es este archivo:** el documento de traspaso para que una sesión nueva de Claude Code, que no ha visto nada de lo
> hablado, pueda seguir el proyecto donde se dejó. Generado el **jueves 12/11/2026 a las 11:00 (Madrid)**. Se sobrescribe
> en cada limpieza; solo vale la última versión. Para continuar, basta con decirle a Claude: *"lee RESUMEN-SESION.md y sigue"*.

---

## 1. Qué es el proyecto y en qué punto está

Una **cartera value simulada de 10.000 €** que gestiona Claude como si operase en IBKR durante al menos un año (compras
de ~500 €, máximo 20 valores, sin empresas de EE. UU.). Cada compra se decide por **EV con 4 escenarios a 3 años** y pasa
por un **comité de dos agentes independientes** (bajista y valorador ciego). Cuatro tareas programadas la gestionan solas
cada día; Ale copia las operaciones en Investing. El manual de operación es `CLAUDE.md`; las reglas, `config/reglas.json`.

**Estado (12/11/2026, 11:00):** estamos en la **Fase 0 (compra de las 20 posiciones), del 11 al 20/11/2026**.
- **El 11/11 se perdió entero** (incidente de permisos, ver sección 6). El primer día real de compras es hoy, 12/11.
- **Hoy a las 09:37** la APERTURA_UE lanzó 4 compras PASIVAS, guardadas en `main` (commit `a6f92e1`), **aún PENDIENTES**:
  O-0001 NWG.L @ 598,2 p · O-0002 BNP.PA @ 96,04 € · O-0003 HBR.L @ 269,4 p · O-0004 BP.L @ 562,6 p
  (**BP entra en lugar de Ayvens**: el desastre de Ayvens queda por debajo de −50% al precio del día).
- Libro: solo la aportación T-0001 de 10.000 €; ninguna compra ejecutada todavía.
- **Las 4 tareas programadas están activas y ya tienen el repositorio adjunto** (arreglado hoy por Ale y comprobado).
  Próxima: APERTURA_US hoy a las 16:04 (Madrid), que debe comprar NOVO-B.CO y validar las 4 órdenes de la mañana.

## 2. Decisiones clave y por qué (no reabrirlas)

Las reglas numéricas están en `config/reglas.json`; no se cambian sin acuerdo de Ale.

**Base (grill-me de 21 preguntas, 07/11/2026)**
- Mínimo 1 año, 100% virtual. El repo es la fuente de verdad; Investing es un espejo manual de Ale.
- IBKR Tiered, cuenta en EUR. Stamp duty, TTF, ITF y FX incluidos. Sin IRPF. Dividendos netos de retención en origen.
- Universo: sin sede en EE. UU., bolsa de origen (nunca ADR); Europa + Japón y Canadá (≤ 30%); sin HK/China.
- Filtros duros: capitalización ≥ 2.000 M€, volumen ≥ 2 M€/día, ≥ 10 años, beneficio operativo + en ≥ 7/10,
  DN/EBITDA ≤ 3x (financieras CET1 ≥ 12%), sin insolvencia.
- Venta solo por: TIR residual < 5%, tesis rota, algo mejor (+10 pp), peso > 10% → recorte al 7%. Sin stop-loss.
- Ejecución: límite al bid de Equiduct (fila Retail); si no hay libro, último −0,10%; velas de 1 minuto con mínimo
  estrictamente < límite; órdenes DAY; en la Fase 0, al 3.er día AGRESIVA. **Nunca registrar operaciones con fecha pasada.**
- **Innegociables en la Fase 0:** filtros duros y desastre ≥ −50%. Si no hay 20 que superen el umbral, se completa con
  las mejores TIR como 🟡 provisionales (rotables con +5 pp durante 8 semanas). Máx. 4 por sector y 6 por país.

**Cambios acordados con Ale (08–10/11/2026)**
- Universo ampliado a medianas (575 empresas en `config/universo.csv`).
- **Umbral de TIR 10% zona euro / 12% fuera** (antes 15%/17%): en 23 comités ningún valorador pasó del 13%.
- **P(desastre) del comité = media de las tres** (antes la más alta, que sesgaba la TIR a la baja en 16 de 23 casos).
- Revisión del sistema aprobada entera (`informes/revision-2026-11-09.md`): TIR del valorador exacta y neta; diferencia
  ≥ 5 pp → la más baja + 2,5 pp; `ev.py --precio-hoy` antes de cada orden; las provisionales quedan exentas de la venta
  por TIR < 5% sus primeras 8 semanas (si no, Linamar y Ahold se venderían al día siguiente); **grupo financiero** = un
  solo riesgo (8 de 20 aceptado en la Fase 0; después no entra ninguna financiera nueva si pesa > 30%); analista a ciegas
  respecto a los umbrales; registro de predicciones, seguimiento de descartadas y pruebas del motor.
- **Ficha de entrada y de salida** (pedida por Ale el 10/11): en cada compra o venta, el porqué en lenguaje llano y el
  **precio objetivo** (= precio a 3 años del escenario base; el "esperado" es la media ponderada). Toda tesis lleva
  `## En pocas palabras`; `cartera.py orden` no deja comprar sin ella. Detalle en `CLAUDE.md` §4.1.
- **Inicio adelantado del 16 al 11/11** (decisión de Ale del 10/11). El final de la Fase 0 sigue en el 20/11.
- **Lundbeck: cerrado.** Era solo un ejemplo de tamaño; no se añade (no salió del cribado, en máximos, necesita 12%).

**Criterios míos en los comités (comunicados a Ale, no objetados):** Valeo excluida (ambos miembros ponen el desastre
< −50%); Mazda excluida (veto del bajista); Ayvens pasa el filtro de 10 años por historia del negocio; Aegon no se
analiza (sede a EE. UU.).

**Decisión del 12/11 sobre el día perdido:** las órdenes que lanzaron las ejecuciones del 11/11 (dos juegos distintos,
nunca guardados ni validados) **no se reconstruyen**: sería registrar con fecha pasada y eligiendo a posteriori. El 11/11
queda sin operaciones; está explicado en `diario/2026-11-11.md`.

## 3. Qué se ha creado (rutas exactas)

**Repositorio:** `kleid98/Cartera-value`. Las ejecuciones trabajan y suben a **`main`** (Ale lo autorizó). Rama de las
sesiones interactivas: `claude/sharp-ritchie-qqyy9n` (igual que `main`). Queda una rama de prueba `prueba-permisos`
que no se pudo borrar (el sistema bloquea borrados de ramas); es inofensiva.

**Configuración**
- `config/reglas.json` (todas las reglas; `fecha_inicio` y `fase0.inicio` = 2026-11-11, `fase0.fin` = 2026-11-20).
- `config/mercados.json`, `config/fiscalidad.json`, `config/universo.csv`, `config/panel.json`.
- `config/tareas.json`: IDs de las tareas e historia del incidente.
- **`config/prompts/APERTURA_UE.md`, `APERTURA_US.md`, `CIERRE.md`, `DOMINGO.md`**: lo que hace cada ejecución. Las tareas
  solo dicen "lee este fichero y síguelo", así que **para cambiar una ejecución se edita su fichero en el repo**. Incluyen
  la orden de subir siempre a `main` aunque la sesión arranque en una rama `claude/...`, y de avisar si el push da 403.

**Scripts** (`scripts/`): `cartera.py` (motor), `ev.py` (EV/TIR, `--precio-hoy`, `--ciego`, bloque `precio_objetivo`),
`ficha.py` (fichas; `--comprobar`), `comite.py`, `comite_registrar.py` (`--recalcular`), `cribado.py` (~10 min),
`panel.py`, `equiduct.js`, `test_motor.py` (10 pruebas sin red; **ejecutar tras cualquier cambio en `scripts/`**).
Arreglado el 11/11: `cartera.py` crea `data/benchmarks/` si no existe (fallaba en clones nuevos).

**Prompts y plantillas:** `comite/bajista.md`, `comite/valorador_ciego.md`, `comite/analista.md`, `plantillas/tesis.md`.

**Datos**
- `tesis/*.md`: 33 tesis, 23 con comité. Las 20 de la Fase 0 y BP.L tienen `## En pocas palabras`; las otras 12 no.
- `plan/fase0.md` (plan y calendario), `plan/calendario.md` (fechas de resultados), `plan/candidatos.md`, `plan/cribado.csv`.
- `ledger/operaciones.csv` (solo T-0001), `ledger/ordenes.csv` (O-0001 a O-0004), `ledger/descartadas.csv` (12, en papel
  desde el 11/11), `ledger/predicciones.csv` (se crea con la primera compra ejecutada), `ledger/cartera.json`, `historico.csv`.
- `diario/2026-11-10.md`, `2026-11-11.md` (incidente), `2026-11-12.md` (compras de hoy con sus fichas).
- `investing/pendiente.md`, `investing/estado.json`.

**Las 20 de la Fase 0** (TIR del comité al 10/11; todas 🟡 provisionales): NWG.L 9,9 · TEP.PA 9,9 · BNP.PA 9,8 ·
JD.L 8,8 · AYV.PA 8,7 · FNTN.DE 8,5 · IMB.L 8,4 · MG.TO 8,0 · HBR.L 7,9 · NOVO-B.CO 7,3 · NN.AS 7,2 · SAN.PA 6,9 ·
CNA.L 6,7 · AZM.MI 6,4 · ISP.MI 6,2 · EN.PA 6,2 · MAP.MC 5,4 · SCR.PA 5,4 · AD.AS 4,8 · LNR.TO 4,4.
**Reserva única: BP.L** (3,9%) — **ya usada hoy en lugar de Ayvens**. Ya no queda reserva con comité.

**Calendario de compras** (`plan/fase0.md`, desplazado un día por el 11/11)
- Jue 12/11: NWG, BNP, HBR, BP (lanzadas) · tarde: NOVO.
- Vie 13/11: TEP, NN, SAN, AZM · tarde: MG (Toronto, tras su Investor Day del 11/11).
- Lun 16/11: CNA, ISP, EN, FNTN (publicó 9 meses el 12/11: solo si no toca una condición) · tarde: LNR.
- Mar 17/11: MAP, SCR, AD. Mié 18/11: IMB (tras sus resultados del 17/11). Jue 19/11: JD (tras su trading statement).
- Vie 20/11: lo que quede sin ejecutar va AGRESIVA.

**Panel:** https://claude.ai/artifact/46h4ity964Kmw8rMaB8dxR (Dashboard; 6 datasets que leen un asset `panel.json`;
copia de la página en `panel/index.html`; no tocar `files/index.html` salvo que Ale pida cambios de diseño).

**Tareas programadas** (las buenas se llaman «Cartera VALUE ex-USA · …»; todas activas y con el repo adjunto)

| Ejecución | ID | Horario |
|---|---|---|
| APERTURA_UE | `trig_01CEGapUaBpMEvxHmy3HZAt8` | `CRON_TZ=Europe/Madrid 34 9 * * 1-5` |
| APERTURA_US | `trig_01AikUWcNyEwnr1XY35S6jAY` | `CRON_TZ=America/New_York 4 10 * * 1-5` |
| CIERRE | `trig_01Q31HxP6FUV3dPWk9v1Rt2a` | `CRON_TZ=America/New_York 4 17 * * 1-5` |
| DOMINGO | `trig_01UnKHPrvh2AaPgsFJfzg9PC` | `CRON_TZ=Europe/Madrid 4 18 * * 0` |

Hay restos **desactivados** que no deben reactivarse: seis tareas «Cartera VALUE · <EJECUCIÓN> del 12/11 / 13/11 (un solo
uso)» con sus sesiones vacías, dos «prueba técnica» y el aviso `trig_011kX84TnoPyCTLQZhcETF4c`. Ale puede borrarlos.

## 4. Credenciales

No hay credenciales propias: Yahoo, BCE/Frankfurter, Equiduct e IBKR son públicos. GitHub va con la integración de la
sesión (y, en las tareas, con el repositorio adjunto en su configuración).

## 5. Pendiente, en este orden

1. **Comprobar hoy que las tareas guardan bien.** Tras la APERTURA_US (16:04) y el CIERRE (23:04), mirar que hay commits
   nuevos en `main`, que las órdenes O-0001…O-0004 se han validado o caducado, que NOVO se ha comprado y que el panel se
   ha actualizado. Es la primera vez que corren las tareas recurrentes con el repo adjunto y en una rama `claude/...`:
   el riesgo es que suban a su rama y no a `main` (el prompt lo prohíbe, pero no se ha visto aún en una ejecución real).
2. **Sin reserva.** BP ya entró por Ayvens. Si freenet (9 meses del 12/11), Imperial (17/11) o JD (19/11) tocan una
   condición de invalidación, no hay sustituto con comité: la cartera se queda en 19 (o menos) y se anota. Opción, si
   Ale quiere: preparar el domingo una tesis con comité de reserva (≈ 30% de una ventana de uso). Azimut (−49,0%) e
   Intesa (−49,4%) estaban al límite del desastre: pueden caerse al precio del día.
3. Fechas sensibles: Magna y Linamar (arancel del 01/01/2027, se revisan juntas), SCOR (plan estratégico 03/12), Azimut
   (Banco de Italia a finales de noviembre; TNB 20/12), BP (estrategia en diciembre).
4. A vigilar sin acción: retención francesa (el sistema usa 12,8%; IBKR podría aplicar 25%; hay 6 francesas);
   dividendos de Magna y Harbour declarados en USD en Yahoo (revisar el primero a mano); lo cobrado en GBP/DKK/CAD se
   queda en esa divisa.
5. El texto del panel aún dice que la Fase 0 empieza el 9 y acaba el 13; no se ha tocado porque es la página del panel
   (solo con permiso de Ale).

## 6. Cosas a tener en cuenta

**Incidente del 11/11 (que no se repita)**
- Una tarea programada abre una sesión **nueva**; si la tarea no tiene el repositorio en su configuración, la sesión
  puede clonar y leer pero **el push da 403** y todo se pierde al cerrarse. `add_repo` no existe en esas sesiones.
- Se arregla en claude.ai/code/routines → tarea → Edit → Advanced settings → Repository → Save changes (solo Ale).
- Para comprobarlo desde una sesión: `update_trigger` con el mismo `enabled` que ya tiene devuelve
  `session_request.config.sources`, que debe incluir el repo. `get_trigger` no lo muestra.
- Fallo mío de diseño: nunca se había probado un disparo real de principio a fin. **Probar siempre un disparo real**
  (p. ej., cambiando un momento el prompt de una tarea pausada y lanzándola con `fire_trigger`) antes de fiarse.
- Ale ve las ejecuciones por las notificaciones del móvil; al salir de una, no la encuentra en la app. Las tareas de
  un solo uso con nombres parecidos le confundieron: usar nombres claramente distintos.
- Crear una sesión "lanzadora" que crea otras sesiones lo bloquea el sistema; no insistir.

**Límite de uso**
- Ale pide **parar hacia el ~80% del límite de 5 horas** (no se puede leer desde la sesión: estimar y quedarse corto).
- El límite **semanal** estaba en aviso el 10/11; se reinicia el **domingo 15/11 a las 03:00 (Madrid)**. Si se agota,
  las tareas fallan hasta entonces.
- Cada comité ≈ 220–270k tokens (11–12% de una ventana); cada tesis con el agente analista ≈ 140–155k. Agentes de uno
  en uno (como mucho el par de un comité). `comite_registrar.py --recalcular` apenas gasta.

**Datos de mercado**
- Yahoo: usar `User-Agent: Mozilla/5.0`; los fundamentales a veces dan 429 → búsqueda web. Londres cotiza en GBX.
- Equiduct funciona **en vivo** (probado el 10/11 y usado hoy). Investing.com da 403; Tweenvest 404.
- Las velas de 1 minuto llegan con retraso: una orden recién lanzada suele seguir PENDIENTE durante un rato.

**Herramientas**
- Para probar órdenes sin tocar el libro: copiar el repo a una carpeta temporal y ejecutar allí.
- Si cambian reglas del comité: recalcular los 23 con `--recalcular` y actualizar `plan/fase0.md`, las tesis y este resumen.
- Los hooks del repo exigen commit y push antes de terminar cada turno.

## 7. Preferencias de Ale para este proyecto

- Todo en español y en lenguaje llano; quiere ver **cómo y por qué** se gestionan los cambios.
- Prefiere ir despacio antes que quemar el límite de uso.
- Las decisiones de reglas son suyas: plantearlas con datos y esperar respuesta. Cuando aprueba, todo de una vez y a `main`.
- Sigue el proyecto desde el móvil: dar instrucciones de configuración paso a paso, con nombres exactos de lo que debe tocar.
- El resto, ver `CLAUDE.md`.
