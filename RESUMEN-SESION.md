# RESUMEN DE SESIÓN — Cartera VALUE ex-USA

> **Qué es este archivo:** el documento de traspaso para que una sesión nueva de Claude Code, que no ha visto nada de lo
> hablado, pueda seguir el proyecto donde se dejó. Generado el **08/11/2026 a las 14:11 (Madrid)**. Se sobrescribe en cada
> limpieza; solo vale la última versión. Para continuar, basta con decirle a Claude: *"lee RESUMEN-SESION.md y sigue"*.

---

## 1. Qué es el proyecto y en qué punto está

Una **cartera value simulada de 10.000 €** que gestiona Claude como si operase en IBKR durante al menos un año:
- compras de ~500 €, máximo 20 valores, sin empresas de EE. UU.;
- cada decisión se toma por **EV con 4 escenarios** y pasa por un **comité de dos agentes independientes**;
- se ejecuta sola con 4 tareas programadas y Ale copia las operaciones en Investing.

**Estado:**
- El sistema está **construido y probado**: reglas, motor IBKR, Equiduct, EV, comité, panel, tareas programadas y PR abierto.
- Las **24 tesis de candidatos están escritas**.
- El **comité está registrado en 7 de las 20 elegibles**; faltan 13.
- Falta escribir el **plan de la Fase 0** (`plan/fase0.md`).
- La primera compra automática es el **lunes 09/11/2026 a las 9:34**.

## 2. Decisiones clave, acordadas con Ale en un "grill-me" de 21 preguntas (no reabrirlas)

Todas las reglas numéricas están en `config/reglas.json` y el manual de operación en `CLAUDE.md`. Resumen y porqués:

**Horizonte y cálculo**
- **1 año mínimo 100% virtual**, con disciplina de cartera real, antes de plantear dinero real.
- **El repo es la fuente de verdad.** Investing es un espejo manual de Ale porque Claude no puede escribir en Investing.

**Costes e impuestos**
- **IBKR Tiered** con cuenta en EUR. Madrid no tiene Tiered, así que usa Fixed 0,05% con mínimo 3 €.
- Se incluyen **stamp duty, TTF francesa (0,4%), ITF española e italiana** y conversión de divisa en cada compra (mínimo 2 USD).
- **Sin IRPF**: las plusvalías se reinvierten íntegras.
- **Dividendos netos de la retención en origen** según el convenio con España (Ale es residente fiscal en España).

**Universo y filtros**
- Excluida cualquier empresa con **sede en EE. UU.**; siempre la bolsa de origen, nunca ADR.
- Universo: Europa más Japón y Canadá, con un máximo del 30% fuera de Europa. Sin Hong Kong ni China. **Sin exclusiones sectoriales.**
- **Filtros duros:** capitalización ≥ 2.000 M€, volumen ≥ 2 M€/día, ≥ 10 años de historia, beneficio operativo positivo en ≥ 7 de 10 años, DN/EBITDA ≤ 3x (financieras: CET1 ≥ 12%), sin insolvencia.

**Reglas de compra, venta y recompra**
- **Compra:** TIR ≥ 15% (≥ 17% fuera del euro), escenario desastre ≥ −50% y asimetría ≥ 2, con horizonte de 3 años.
- **Comité:** un agente 🔴 bajista, que ve solo la tesis cualitativa, y un 🔵 valorador ciego, que ve solo el ticker. Reconciliación:
  - diferencia < 5 pp → media de las TIR; ≥ 5 pp → la más baja;
  - probabilidad de desastre = la más alta de las tres;
  - el bajista puede vetar si se cumple una condición de invalidación.
  - El comité **puede frenar una compra, nunca forzarla**.
- **Venta:** TIR residual < 5%, tesis rota, algo mejor con +10 pp, o peso > 10% (se recorta al 7%). **Sin stop-loss.**
- **Recompra:** tras una caída ≥ 20%, revisando la tesis, con +5 pp de TIR, máximo 3 compras / 10% de la cartera, y 30 días entre compras. Se puede promediar al alza.

**Fase 0 (09–13/11/2026)**
- Ale quiere los 10.000 € **invertidos esa semana** para ver cómo se gestionan los cambios.
- Si no hay 20 valores con TIR ≥ umbral, se completa con las mejores TIR como **🟡 provisionales**, que se pueden rotar con +5 pp durante 8 semanas.
- Límites: máximo 4 por sector y 6 por país.
- **Innegociables incluso en la Fase 0:** filtros duros y desastre ≥ −50%.

**Ejecución**
- Órdenes limitadas al **bid de Equiduct** (fila Retail, VBB/VBO). Si Equiduct no cubre el valor: último precio −0,10%.
- Se validan con velas de 1 minuto: el mínimo tiene que quedar estrictamente por debajo del límite. Las órdenes son DAY.
- **Japón:** se decide a las 23:00 y se ejecuta a la apertura de Tokio, en lotes de 100 acciones (lote ≤ 750 €).

**Calendario y avisos**
- **Lunes a viernes:** 9:34 Madrid, 10:04 Nueva York y 17:04 Nueva York (revisión y panel).
- **Domingos:** 18:04 Madrid.
- **Avisos push solo cuando haya operaciones.**

**Seguimiento**
- **Benchmarks:** CEMS.DE (MSCI Europe Value, el principal), EXUS.DE e IWDA.AS, comparados con carteras fantasma.
- **Investing:** el formato sigue el formulario de Ale (Buscar → Tipo → Fecha → Cantidad → Precio → Comisión).
  - Londres: precio en **GBX** y comisión en **GBP**.
  - Las ventas se hacen con "Cerrar posición" **por lote FIFO**.
  - Investing no registra dividendos ni FX.
- **Git:** opción B. Se monta en la rama `claude/sharp-ritchie-qqyy9n`, se abre un PR y se fusiona una vez; después las tareas programadas trabajan sobre `main`.

## 3. Qué se ha creado (rutas exactas)

**Repositorio y PR**
- Repo: `kleid98/Cartera-value`. Rama de trabajo: `claude/sharp-ritchie-qqyy9n`.
- `main` se creó desde el primer commit, que solo tiene README y .gitignore.
- **PR abierto, aún sin fusionar:** https://github.com/kleid98/Cartera-value/pull/1

**Configuración**
- `config/reglas.json`, `config/mercados.json`, `config/fiscalidad.json`
- `config/universo.csv`: 197 empresas.
- `config/panel.json`: URL del panel y pasos para actualizarlo.
- `config/tareas.json`: IDs de las tareas programadas.

**Scripts**
- `scripts/cartera.py`: motor de órdenes, validación, costes, FX, FIFO, dividendos, estado, benchmarks e Investing.
- `scripts/equiduct.js`: libro de Equiduct con Playwright. Uso: `node scripts/equiduct.js ISIN MIC [YYYYMMDD]`, con `NODE_PATH=$(npm root -g)`.
- `scripts/ev.py`: EV, TIR y reconciliación del comité.
- `scripts/cribado.py`: cribado con quoteSummary de Yahoo (con crumb).
- `scripts/comite.py`: genera los prompts ciegos del comité.
- `scripts/comite_registrar.py`: escribe los informes del comité en la tesis y aplica `ev.py`.
- `scripts/panel.py`: genera `panel/panel.json`.

**Documentación y plantillas**
- `CLAUDE.md`: manual de operación de las ejecuciones programadas.
- `comite/bajista.md`, `comite/valorador_ciego.md`, `plantillas/tesis.md`.

**Datos y análisis**
- `ledger/operaciones.csv`: solo tiene la aportación T-0001 de 10.000 €.
- `ledger/ordenes.csv` (vacío), `ledger/cartera.json`, `ledger/historico.csv`.
- `tesis/*.md`: 24 tesis.
- `plan/cribado.csv` y `plan/candidatos.md`: resultado del cribado.
- `plan/comite_informes/`: informes del comité ya recibidos y copia de los prompts. Los prompts tienen una ruta de guardado de la sesión anterior; regenerarlos con `comite.py`.
- `investing/pendiente.md`, `investing/estado.json`, `investing/historico.md`.

**Panel (Artifact de tipo Dashboard)**
- URL: https://claude.ai/artifact/46h4ity964Kmw8rMaB8dxR
- 6 datasets (`resumen`, `historico`, `posiciones`, `operaciones`, `ordenes`, `investing`) que leen un único asset `panel.json`. El asset actual es `/_blob/aa12e649d3bbd59b5b05ec01fd2f0414`.
- La copia de la página está en `panel/index.html`. No tocar `files/index.html` salvo que haya cambios de diseño.

**Tareas programadas** (sesión nueva en cada disparo; clonan el repo con `add_repo` y siguen `CLAUDE.md` sobre `main`). **Ahora mismo las 4 están PAUSADAS**; ver la sección 6.

| Ejecución | ID | Horario | Push |
|---|---|---|---|
| APERTURA_UE | `trig_01CEGapUaBpMEvxHmy3HZAt8` | `CRON_TZ=Europe/Madrid 34 9 * * 1-5` | sí |
| APERTURA_US | `trig_01AikUWcNyEwnr1XY35S6jAY` | `CRON_TZ=America/New_York 4 10 * * 1-5` | sí |
| CIERRE | `trig_01Q31HxP6FUV3dPWk9v1Rt2a` | `CRON_TZ=America/New_York 4 17 * * 1-5` | sí |
| DOMINGO | `trig_01UnKHPrvh2AaPgsFJfzg9PC` | `CRON_TZ=Europe/Madrid 4 18 * * 0` | no |

## 4. Credenciales

No hay credenciales propias. Yahoo, el BCE/Frankfurter, Equiduct e IBKR son públicos. GitHub va con la integración de la sesión.

## 5. Estado de las tesis y del comité

TIR propia / TIR del comité (si ya está registrado):

| Ticker | Sector | País | TIR propia | TIR comité | Desastre | Asimetría | Estado |
|---|---|---|---|---|---|---|---|
| NWG.L | Bancos | GB | 9,9% | **9,4%** | −46% | 7,1 | ✅ comité |
| TEP.PA | Servicios | FR | 8,5% | — | −46% | 3,5 | comité pendiente |
| JD.L | Distribución | GB | 8,6% | — | −48% | 4,2 | comité pendiente |
| FR.PA (Valeo) | Automóvil | FR | 8,3% | — | **−49,8%** | 4,6 | comité pendiente |
| IMB.L | Tabaco | GB | 8,2% | **8,3%** | −38% | 7,9 | ✅ comité |
| NOVO-B.CO | Salud | DK | 7,2% | **7,8%** | −43% | 3,8 | ✅ comité |
| NN.AS | Seguros | NL | 6,7% | **7,1%** | −38% | 5,6 | ✅ comité |
| EN.PA (Bouygues) | Construcción | FR | 7,1% | — | −41% | 4,5 | comité pendiente |
| CNA.L | Utilities | GB | 7,7% | **6,6%** | −46% | 4,3 | ✅ comité |
| BNP.PA | Bancos | FR | 8,5% | **6,6%** | −45% | 6,1 | ✅ comité |
| ISP.MI | Bancos | IT | 6,7% | — | −48% | 5,2 | comité pendiente |
| MG.TO (Magna) | Automóvil | CA | 6,7% | — | −43% | 3,5 | comité pendiente |
| SAN.PA (Sanofi) | Salud | FR | 6,6% | — | −34% | 6,1 | comité pendiente |
| 7261.T (Mazda) | Automóvil | JP | 5,9% | — | −46% | 2,9 | comité pendiente; lote ≈ 640 € |
| MAP.MC | Seguros | ES | 4,6% | **5,6%** | −38% | 3,6 | ✅ comité |
| LNR.TO (Linamar) | Automóvil | CA | 4,9% | — | −46% | 2,35 | comité pendiente |
| AD.AS (Ahold) | Distribución alimentaria | NL | 4,0% | — | −43% | 2,8 | comité pendiente |
| BP.L | Energía | GB | 4,0% | — | −37% | 2,6 | comité pendiente |
| GALP.LS | Energía | PT | 2,6% | — | −47% | **1,8** | comité pendiente |
| NHY.OL | Materias primas | NO | 2,3% | — | −41% | **1,6** | comité pendiente |

**Excluidas (innegociable):**
- SU.TO: desastre −50,9%.
- OMV.VI: desastre −50,2%.
- VOE.VI: desastre −54,9%.
- ACA.PA: CET1 de la cotizada 11,2% < 12%. El grupo tiene 17,3%, pero se aplicó el filtro literal.

**Límites de la Fase 0 con estas 20:**
- Ninguna pasa el umbral de TIR, así que **todas entrarían como 🟡 provisionales**.
- Las 20 caben justo en los límites: Francia 5, Reino Unido 5, automóvil 4, fuera de Europa 3 (15%).
- Galp y Norsk Hydro tienen asimetría < 2. La asimetría no está entre las reglas innegociables de la Fase 0, pero son las peores candidatas.
- Si el comité veta alguna o sube su desastre por debajo de −50%, quedarían < 20 y habría que analizar reservas. Posibles reservas del cribado: Shell, TotalEnergies, GSK, Saint-Gobain, Kingfisher, Tesco y Arkema.

## 6. Pendiente, en este orden

1. **Comité de las 13 que faltan:** TEP, JD, FR, EN, ISP, MG, SAN, 7261, LNR, AD, BP, GALP y NHY.
   - Lánzalo **DE UNO EN UNO o como mucho de dos en dos**: un bajista y un valorador de la misma empresa, y esperar.
   - Por cada empresa:
     - `python3 scripts/comite.py tesis/X.md <dir_scratch>`
     - lanzar 2 agentes `general-purpose` con el prompt "Lee tus instrucciones en <dir>/bajista_X.txt…" / ".../valorador_X.txt…", más "no leas tesis ni otros ficheros del comité"
     - `python3 scripts/comite_registrar.py tesis/X.md <dir>/informe_bajista_X.md <dir>/informe_valorador_X.md`
   - Los prompts ya piden al agente que guarde su informe en `<dir>/informe_{rol}_X.md`.
   - Los agentes de la sesión anterior que se cortaron por el límite **no se pueden reanudar** desde una sesión nueva: hay que relanzarlos.
2. **Escribir `plan/fase0.md`:**
   - Las 20 ordenadas por TIR del comité (o propia si no hay comité), todas `--provisional`.
   - Reparto de unas 4 compras al día, de lunes a viernes, entre APERTURA_UE y APERTURA_US.
   - ISIN, mercado, país emisor y sector de cada una (en cada tesis).
   - Mazda, como orden `--tipo APERTURA` decidida en un CIERRE.
   - Regla del 3er día: AGRESIVA.
3. **Actualizar cada tesis** a 🟡 provisional en "Estado" y "Decisión".
4. Commit y push a la rama. El PR se actualiza solo. Pedir a Ale que **fusione el PR**.
5. **⏸️ LAS 4 TAREAS PROGRAMADAS ESTÁN PAUSADAS** (Ale lo pidió el 08/11/2026 a las 14:18) hasta que el comité y el plan estén listos y el PR fusionado.
   - IDs: `trig_01CEGapUaBpMEvxHmy3HZAt8`, `trig_01AikUWcNyEwnr1XY35S6jAY`, `trig_01Q31HxP6FUV3dPWk9v1Rt2a` y `trig_01UnKHPrvh2AaPgsFJfzg9PC`.
   - **Para reanudar:** `update_trigger` con `enabled=true` en las cuatro, **solo después** de que Ale fusione el PR.
   - Como la Fase 0 ya no empieza el lunes 09/11, hay que **mover las fechas de la Fase 0** a la semana real de arranque: `config/reglas.json` → `fase0.inicio`/`fin` y `fecha_inicio`, y las menciones de "09–13/11/2026" en `CLAUDE.md`. Es un cambio de calendario, no de reglas, pero confírmalo con Ale al proponer la fecha.
6. ✅ **Tarea programada antigua borrada** (`trig_01UJiwFhup6i55z79wxW5PFz`, "Cartera value: revisión diaria 16:00", del proyecto anterior de 100.000 €), por orden de Ale.
7. **Pregunta abierta a Ale:**
   - **Hallazgo importante:** ninguno de los 24 candidatos (todos large caps) llega a la TIR del 15%. El rango es −3% a 10%.
     - La Fase 0 será 100% provisional.
     - Comentar a Ale si quiere mantener el umbral, ampliar el universo a mid caps de 2.000–10.000 M€ (más probable encontrar un 15%), o dejarlo así y que la rotación mejore la cartera con el tiempo.
     - **No cambiar `reglas.json` sin su acuerdo.**

## 7. Cosas a tener en cuenta

**Límite de uso (lo más importante)**
- **Lanzar 20 agentes a la vez agota el límite de 5 horas** y se cortan todos a mitad.
- Ale ha pedido expresamente **lanzarlos despacio, de uno en uno**. Cada agente consume unos 100–150k tokens.
- Aunque haya varios lanzados, lo que cuenta es el consumo total, no la concurrencia.

**Yahoo y datos de mercado**
- Con un user-agent largo de navegador devuelve 429. Funciona con `User-Agent: Mozilla/5.0`, ya puesto en `cartera.py`.
- Para los fundamentales hace falta cookie + crumb (`fc.yahoo.com` + `getcrumb`), hecho en `cribado.py`.
- **Los datos de Yahoo tienen errores frecuentes:**
  - En Londres, el P/VC sale en peniques (×100).
  - El FCF yield y el EV/EBITDA se inflan por partidas extraordinarias.
  - Los analistas lo detectaron y lo corrigieron en las tesis. No fiarse del cribado más que para ordenar.
- Londres cotiza en **GBp/GBX** (peniques): el motor lo convierte. Japón compra en lotes de 100.

**Otras fuentes**
- **Equiduct:** `api.equiduct.com/mdwebapi/instrument` da el mapa ISIN→símbolo. El viewer acepta `?symbol=X&date=YYYYMMDD` (modo replay).
  - Se lee la fila "Retail" (VBB/VBO).
  - En replay de cierre algunos libros salen raros (spread ancho); el motor descarta spreads > 1% y usa el último −0,10%.
  - El libro en vivo **aún no se ha probado en horario de mercado**: comprobarlo el lunes.
- **Investing.com** bloquea el acceso automatizado (403).
- **Tweenvest** devolvió 404 a los agentes.
- **IBKR web** responde con curl, pero no con WebFetch (403).

**Herramientas y fallos ya corregidos**
- **Fallos corregidos:**
  - `ev.py` se rompía con el comité en null.
  - `comite.py` redactaba palabras que contenían "ev" (ahora usa `\b`).
- `comite_registrar.py` toma la **TIR redondeada** que escribe el valorador (`TIR_ANUAL: 0.07`).
- Los hooks del repo exigen **commit y push** antes de terminar cada turno: hacerlo siempre en `claude/sharp-ritchie-qqyy9n`.

## 8. Preferencias de Ale para este proyecto

- Todo en español, en lenguaje llano.
- Quiere **ver cómo se gestionan los cambios**: explicar el porqué en diario y tesis.
- No le importa que el montaje tarde más si así se evita quemar el límite de uso.
- Las decisiones de reglas son suyas: plantearlas y esperar su respuesta.
- El resto, ver `CLAUDE.md`.
