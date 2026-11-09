# RESUMEN DE SESIÓN — Cartera VALUE ex-USA

> **Qué es este archivo:** el documento de traspaso para que una sesión nueva de Claude Code, que no ha visto nada de lo
> hablado, pueda seguir el proyecto donde se dejó. Actualizado el **09/11/2026 (pausa por límite de uso)**. Se sobrescribe en cada
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

## 5. Estado de las tesis y del comité (actualizado)

**Opción B aprobada por Ale:** universo ampliado a mid caps (`config/universo.csv`, 575 empresas; `reglas.json` sin cambios).
Cribado nuevo en `plan/cribado.csv`/`candidatos.md`. 8 tesis nuevas de mid caps (HBR, FGR, AYV, SCR, UMI, AZM, FNTN, VK)
escritas por agentes analistas con `comite/analista.md` (prompt reutilizable). Ninguna llega al 15%.

TIR comité (o propia si falta) — la reconciliación usa la P(desastre) más alta, que casi siempre es la del bajista (13–30%):

| Ticker | País | TIR propia | TIR comité | Desastre | Estado |
|---|---|---|---|---|---|
| NWG.L | GB | 9,9% | 9,4% | −46% | ✅ comité |
| IMB.L | GB | 8,2% | 8,3% | −38% | ✅ |
| AYV.PA | FR | 9,5% | 8,1% | −49% | ✅ (CET1 12,8%; 9,4 años en bolsa como ALD, el negocio tiene >10) |
| NOVO-B.CO | DK | 7,1% | 7,8% | −43% | ✅ |
| SAN.PA | FR | 6,6% | 7,3% | −34% | ✅ |
| NN.AS | NL | 6,7% | 7,1% | −38% | ✅ |
| CNA.L | GB | 7,7% | 6,6% | −46% | ✅ |
| BNP.PA | FR | 8,5% | 6,6% | −45% | ✅ |
| EN.PA | FR | 7,1% | 6,2% | −41% | ✅ |
| ISP.MI | IT | 6,7% | 6,2% | −48% | ✅ |
| MAP.MC | ES | 4,6% | 5,6% | −38% | ✅ |
| TEP.PA | FR | 8,5% | 4,9% | −46% | ✅ |
| FNTN.DE | DE | 7,5% | 4,8% | −41% | ✅ (resultados 9M el 11/11: no lanzar orden antes) |
| JD.L | GB | 8,6% | 4,8% | −48% | ✅ (trading statement 19/11) |
| MG.TO | CA | 6,7% | 4,5% | −43% | ✅ (arancel 50% piezas CA desde 01/01/2027 anunciado) |
| HBR.L | GB | 7,8% | 3,9% | −47% | ✅ |
| 7261.T | JP | 5,9% | 2,9% | −46% | ❌ **VETO del bajista** (condición 5: CX-5 < predecesor en EE. UU. 2 trimestres) |
| AZM.MI | IT | 5,7% | — | −48% | comité pendiente |
| SCR.PA | FR | 5,6% | — | −47% | comité pendiente |
| LNR.TO | CA | 4,9% | — | −46% | comité pendiente |
| Reservas | | AD.AS 4,0 · BP.L 4,0 · FGR.PA 4,0 | — | | sin comité |

**Excluidas:** SU.TO, OMV.VI, VOE.VI, UMI.BR (desastre < −50%); ACA.PA (CET1 11,2%); VK.PA (beneficio operativo 4/10);
**FR.PA (Valeo): excluida por el comité** — los dos miembros ponen el desastre < −50% (−54%/−55%) frente al −49,8% propio.
Criterio adoptado (decisión mía, comunicada a Ale): se excluye solo si **ambos** miembros del comité sitúan el desastre
(retorno total) por debajo de −50%. GALP.LS y NHY.OL (asimetría < 2) quedan fuera por TIR. Aegon no se analizó (traslada sede a EE. UU.).

**20 de la Fase 0 (provisional):** las 16 con comité + AZM, SCR, LNR + 1 reserva (AD.AS, BP.L o FGR.PA, tras comité). Mazda vetada. Límites: FR 6 (AYV, SAN, BNP, EN, TEP, SCR),
GB 5, automóvil 2 (MG, LNR), fuera de Europa 2 (10%). Todas 🟡 provisionales.

## 6. Pendiente, en este orden

1. **Comité de AZM.MI, SCR.PA y LNR.TO y de una reserva** (AD.AS, BP.L o FGR.PA; de uno en uno). Prompts en `plan/comite_informes/`
   (el de AZM; para SCR y LNR, `python3 scripts/comite.py tesis/X.md <scratch>`). Copiar los prompts a un scratch
   nuevo si cambian las rutas: el prompt indica dónde guardar el informe. Registrar con `scripts/comite_registrar.py`.
   Si alguna cae por debajo de AD/BP/FGR (4,0% propia), hacer comité de la reserva antes de sustituirla.
2. **`plan/fase0.md`:** las 20 ordenadas por TIR comité, ~4 compras/día; FNTN después del 11/11 y JD después del 19/11 si
   cae en esa semana; Mazda como orden APERTURA desde un CIERRE.
3. Tesis → 🟡 provisional en Estado y Decisión.
4. **Mover fechas de la Fase 0** (`reglas.json` fase0.inicio/fin y fecha_inicio; menciones en CLAUDE.md): proponer fecha a Ale.
5. Commit/push, pedir a Ale que fusione https://github.com/kleid98/Cartera-value/pull/1, y solo después reanudar las 4 tareas
   (`update_trigger enabled=true`: trig_01CEGapUaBpMEvxHmy3HZAt8, trig_01AikUWcNyEwnr1XY35S6jAY, trig_01Q31HxP6FUV3dPWk9v1Rt2a,
   trig_01UnKHPrvh2AaPgsFJfzg9PC). **Siguen PAUSADAS.**
6. **Uso:** Ale pide parar al ~80% del límite de 5 horas. Cada comité ≈ 240k tokens; cada tesis ≈ 145k. No hay forma de
   leer el % de uso: estimar y quedarse corto.
7. **Observación para Ale:** con este método ninguna empresa grande o mediana llega al 15%; el bajista sube la P(desastre) a
   13–30% y la reconciliación deja TIR de 4–9%. Ale eligió la opción B (ampliar universo); el umbral no se ha tocado y la Fase 0 sería 100% provisional. Pendiente comentarlo con datos.

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
