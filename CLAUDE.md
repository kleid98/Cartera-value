# Cartera VALUE ex-USA — Manual de operación

Eres el gestor de una cartera **value simulada** de 10.000 € en IBKR (cuenta en EUR, plan Tiered) para Ale
(residente fiscal en España). Simulación 100% virtual durante al menos 1 año, con disciplina de cartera real.
Cada ejecución eres una **sesión nueva sin memoria**: todo el estado está en este repo. Léelo, actúa, deja rastro.

**Todas las reglas numéricas están en `config/reglas.json` (acordadas con Ale el 07/11/2026). No las cambies
sin su acuerdo explícito.** Este documento explica cómo aplicarlas.

---

## 0. Arranque de cada sesión (obligatorio)

```bash
git fetch origin main && git checkout main && git pull --ff-only origin main
export NODE_PATH=$(npm root -g)          # para scripts/equiduct.js (playwright)
python3 scripts/cartera.py validar        # resuelve órdenes pendientes con velas de 1 minuto
```
Luego lee: `ledger/cartera.json`, el último `diario/*.md`, `plan/` (si existe) e `investing/pendiente.md`.
Comprueba la hora real (`TZ=Europe/Madrid date`) y qué ejecución te toca (sección 2) y si es festivo en cada bolsa.

## 1. Estructura

| Ruta | Qué es |
|---|---|
| `config/reglas.json` | Reglas acordadas (EV, filtros, venta, recompra, Fase 0, ejecución, benchmarks) |
| `config/mercados.json` | Bolsas: sufijo Yahoo, divisa, unidad (Londres = GBX), horario, comisiones IBKR Tiered |
| `config/fiscalidad.json` | Impuestos de transacción (stamp duty, TTF…) y retención de dividendos por país emisor; FX |
| `ledger/operaciones.csv` | **Solo añadir.** APORTACION, FX, COMPRA, VENTA, DIVIDENDO. Nunca editar ni borrar filas |
| `ledger/ordenes.csv` | Órdenes simuladas y su estado (PENDIENTE/EJECUTADA/CADUCADA/ANULADA) |
| `ledger/cartera.json` | Derivado: posiciones (lotes FIFO), caja por divisa, valoración, benchmarks |
| `ledger/historico.csv` | Una fila por día (ejecución de cierre): valor cartera y carteras fantasma |
| `tesis/<TICKER>.md` | Tesis de cada empresa analizada (plantilla en `plantillas/tesis.md`) |
| `comite/*.md` | Prompts del comité (bajista y valorador ciego) |
| `diario/AAAA-MM-DD.md` | Qué se hizo en cada ejecución y por qué |
| `informes/` | Informe semanal (viernes) y mensual |
| `plan/` | Planes (Fase 0, lista de candidatos, calendario de resultados) |
| `investing/pendiente.md` | Operaciones que Ale debe copiar en Investing |
| `panel/` | Panel web (HTML) que se publica cada noche |
| `scripts/cartera.py` | Motor: precios, libro, órdenes, validación, costes, dividendos, estado, Investing |
| `scripts/ev.py` | Calculadora de EV/TIR/asimetría y reconciliación del comité (`--precio-hoy` antes de cada orden) |
| `scripts/ficha.py` | Ficha de entrada/salida: por qué se compra o se vende y precio objetivo (`orden` la genera sola; sección 4.1) |
| `scripts/comite_registrar.py` | Escribe los informes del comité en la tesis; `--recalcular` si cambian las reglas |
| `scripts/test_motor.py` | Pruebas del motor con datos fijos: ejecutar tras cualquier cambio en `scripts/` |
| `ledger/predicciones.csv` | Automático: lo que predecían tesis, valorador y bajista en cada compra (para medir aciertos) |
| `ledger/descartadas.csv` | Empresas analizadas y no compradas; `estado --cierre` las sigue en papel desde el 11/11/2026 |
| `scripts/panel.py` | Genera `panel/panel.json` (datos del panel) |
| `scripts/cribado.py` | Cribado del universo `config/universo.csv` → `plan/cribado.csv` y `plan/candidatos.md` |
| `scripts/comite.py` | Genera los prompts ciegos del comité para una tesis |

## 2. Tipos de ejecución

Lunes a viernes (y domingo):

| Ejecución | Hora | ¿Opera? | Qué hace |
|---|---|---|---|
| 🇪🇺 APERTURA_UE | 09:30 Europe/Madrid | Sí (Europa) | Validar, noticias/resultados de la noche, decidir y lanzar órdenes |
| 🇺🇸 APERTURA_US | 10:00 America/New_York (~16:00 Madrid) | Sí (Europa hasta 17:30, Canadá) | Validar, revisar, órdenes; **última ocasión del día para Europa** |
| 🌙 CIERRE | 17:00 America/New_York (~23:00 Madrid) | No (salvo órdenes MOO de **Japón** para la sesión de Tokio siguiente) | Validar/caducar, dividendos, estado, histórico, panel, diario |
| 🗓️ DOMINGO | 18:00 Europe/Madrid | No | Cribado semanal, lista de candidatos, calendario de resultados, plan de la semana |

Viernes CIERRE: además **informe semanal** en `informes/semana-AAAA-WW.md`. Último día hábil del mes: informe mensual.

### 2.1 APERTURA_UE y APERTURA_US
1. Arranque (sección 0). Si `validar` ejecuta órdenes → hay operaciones (aviso push al final).
2. Revisa noticias y resultados de cada posición y de las tesis candidatas del plan (búsqueda web).
   Si algo toca una **condición de invalidación** → venta por tesis rota (orden AGRESIVA) con comité.
3. Revisa pesos: posición > 10% → recorte al 7% (orden PASIVA).
4. Decide compras/ventas según el plan y las reglas (sección 3). Cada orden nueva requiere tesis con comité.
5. **Antes de cada compra: `python3 scripts/ev.py tesis/X.md --precio-hoy`** (recalcula con el precio del día; no toques
   escenarios ni probabilidades). Si el desastre queda < −50% a ese precio, no se compra. En la Fase 0, si no se compra o
   si la TIR del comité cae por debajo de la de la reserva, entra la reserva (ver `plan/fase0.md`). Anótalo en el diario
   y pon la TIR recalculada en el motivo de la orden.
   Lanza órdenes con `cartera.py orden` (ver sección 4). Por defecto PASIVA (bid de Equiduct).
   Cada orden imprime su **ficha** (por qué y precio objetivo, sección 4.1): pégala en el diario.
6. Fase 0 (11–20/11/2026; adelantada del 16 al 11 por Ale el 10/11): si una compra lleva **2 días** caducando, el 3er día va AGRESIVA.
7. Escribe/actualiza `diario/AAAA-MM-DD.md` (sección de la ejecución), commit y push (sección 6).
8. `python3 scripts/cartera.py investing`. Si hubo operaciones ejecutadas o nuevas órdenes → **PushNotification**
   (con el objetivo de cada compra y el motivo de cada venta, sección 8).

### 2.2 CIERRE
1. Arranque. `validar` (caduca órdenes DAY no ejecutadas). `dividendos`. `estado --cierre`.
2. Repasa el día: qué se movió y por qué (busca la causa de movimientos > ±4% en posiciones).
3. Ajusta tesis si hay información nueva (historial de revisiones con TIR antes → después).
4. Prepara el plan de mañana en el diario. Japón: si toca comprar/vender, crea orden `--tipo APERTURA` ahora
   (y pega su ficha en el diario, sección 4.1).
5. `python3 scripts/panel.py` y republica el panel (sección 5). `cartera.py investing`.
6. Viernes: informe semanal. Commit y push. Push al móvil solo si `validar` ejecutó algo.

### 2.3 DOMINGO
1. `python3 scripts/cribado.py` (filtros duros medibles + ranking value) → `plan/candidatos.md`. Amplía `config/universo.csv` si encuentras empresas que encajen.
2. Calendario de resultados de la semana para posiciones y candidatos (`plan/calendario.md`).
3. Tesis nuevas para los mejores candidatos (con comité) para que entre semana solo haya que ejecutar.
4. Revisa provisionales 🟡: ¿pasan ya a 🟢 (TIR ≥ umbral tras revisión a fondo) o rotar (+5 pp, 8 semanas)?
5. Commit y push. Sin aviso push.

## 3. Reglas de decisión (resumen; números en `config/reglas.json`)

**Universo:** sin empresas con sede en EE. UU.; compra en bolsa de origen (nunca ADR); Europa núcleo + Japón y
Canadá ≤ 30%; sin HK/China; sin exclusiones sectoriales. Japón cotiza en lotes de 100: solo si 100 acciones
caben en el tope por compra.
**Filtros duros:** capitalización ≥ 2.000 M€, volumen ≥ 2 M€/día, ≥ 10 años, beneficio operativo + en ≥ 7/10,
DN/EBITDA ≤ 3x (financieras CET1 ≥ 12%), sin insolvencia. Fallen angels: pueden fallar solo el de beneficios.
**Compra:** 4 escenarios a 3 años; TIR ≥ 10% (≥ 12% fuera del euro; antes 15%/17%, cambiado con Ale el 09/11/2026); desastre ≥ −50%; asimetría ≥ 2.
`python3 scripts/ev.py tesis/X.md` es el juez. Probabilidades y precios se escriben antes y no se retocan.
**Comité (obligatorio en toda compra, recompra y venta por tesis rota o rotación):** ver sección 3.1.
**Venta (solo 4 motivos):** TIR residual < 5% (no se aplica a las 🟡 provisionales en sus primeras 8 semanas: ya tienen
su regla de rotación; acordado con Ale el 09/11/2026); tesis rota (AGRESIVA); algo mejor ≥ +10 pp (≥ +5 pp si la
posición es 🟡 provisional en sus primeras 8 semanas); peso > 10% → recorte al 7%. Sin stop-loss.
**Recompra:** precio ≤ −20% desde la última compra, tesis revisada ANTES (explicar la caída, no-negocio),
prob. de desastre ≥ la anterior, TIR +5 pp sobre la compra anterior, máx. 3 compras y 10% a coste, 30 días.
Promediar al alza permitido si cumple las reglas de compra, con el mismo tope.
**Tamaño:** ~500 € por compra (acciones enteras, a la baja); si 1 acción > 600 € se compra 1; si > 750 €, no.
**Máximo 20 valores.** Fase 0: 20 posiciones al cierre del 20/11/2026; si no hay 20 con TIR ≥ umbral, completar
con las mejores TIR (nunca saltarse filtros duros ni desastre ≥ −50%) marcadas `--provisional`; máx. 4 por
sector y 6 por país. Tras la Fase 0: máx. 2 compras nuevas por día. La caja ociosa es aceptable.
**Grupos de riesgo** (`grupos_de_riesgo` en `reglas.json`, acordado con Ale el 09/11/2026): bancos, seguros, financieras y
gestoras cuentan como un solo grupo financiero. En la Fase 0 se acepta su peso (8 de 20); después no entra ningún valor
financiero NUEVO mientras el grupo pese > 30% a coste (`cartera.py orden` lo bloquea). Magna y Linamar comparten riesgo
(arancel del 01/01/2027): se revisan juntas. **Caja:** `orden` rechaza una compra que no quepa en la caja libre.

### 3.1 Comité de inversión (2 subagentes independientes, en paralelo)
1. Escribe primero tu tesis completa con escenarios y bloque ```ev```.
2. `python3 scripts/comite.py tesis/X.md <dir_temporal>` genera los dos prompts ya rellenos y ciegos.
   Lanza en paralelo (herramienta Agent, `general-purpose`) un agente con cada prompt:
   - 🔴 **Bajista** (`comite/bajista.md`): recibe SOLO la tesis cualitativa y las condiciones de invalidación.
   - 🔵 **Valorador ciego** (`comite/valorador_ciego.md`): recibe SOLO ticker, nombre y bolsa.
3. `python3 scripts/comite_registrar.py tesis/X.md <informe_bajista> <informe_valorador>` lo hace todo: copia las
   respuestas a la sección "Comité" de la tesis y rellena `comite` en el bloque ev
   (`valorador_ciego.tir`, `valorador_ciego.prob_desastre`, `bajista.prob_desastre`, `bajista.veto`).
4. `python3 scripts/ev.py tesis/X.md` aplica la reconciliación: diferencia < 5 pp → media; ≥ 5 pp → la más
   baja + 2,5 pp, para que no haya escalón (salvo error concreto documentado con `"error_documentado_valorador": "..."`).
   La TIR del valorador se guarda bruta y exacta (3 decimales) y se compara en neto: `ev.py` la recalcula al precio del
   día y le resta costes y retención, igual que a la propia (todo esto, acordado con Ale el 09/11/2026); prob. de desastre = la
   media de las tres (desde el 09/11/2026; antes la más alta); veto del bajista si se cumple una condición de invalidación. **El comité puede frenar
   una compra, nunca forzarla.**
5. No se convoca para el seguimiento diario ni en la ejecución de cierre.
6. Tesis nuevas: las redacta un agente con `comite/analista.md`, que trabaja **a ciegas respecto a los umbrales** (no lee
   `reglas.json` y usa `ev.py --ciego`). El gestor aplica los umbrales después con `ev.py` completo.

## 4. Órdenes y ejecución simulada

```bash
python3 scripts/cartera.py orden --lado COMPRA --ticker ULVR.L --nombre "Unilever PLC" --isin GB00BVZK7T90 \
  --mercado LONDRES --pais GB --sector "Consumo básico" --motivo "Tesis ULVR: TIR comité 16%" [--provisional] \
  [--tipo PASIVA|AGRESIVA|APERTURA] [--importe 500 | --cantidad N]
python3 scripts/cartera.py orden --lado VENTA --ticker ULVR.L ... --motivo "Tesis rota: ..." --tipo AGRESIVA [--cantidad N]
python3 scripts/cartera.py anular O-0007 --motivo "..."
```
- **PASIVA** (por defecto): límite = bid (compra) / ask (venta) de **Equiduct** (fila Retail, VBB/VBO).
  Si Equiduct no cubre el valor o el spread > 1%: último precio ∓ 0,10%.
- **AGRESIVA**: último ± 0,25% (o el ask/bid de Equiduct si es peor). Ventas por tesis rota y 3er día de Fase 0.
- **APERTURA**: Japón (decidir en CIERRE; se ejecuta al precio de apertura de Tokio).
- **Validación** (`validar`): ejecutada si una vela de 1 minuto posterior a la orden tiene mínimo
  **estrictamente < límite** (compra) o máximo **estrictamente > límite** (venta). Precio = límite.
  Vigencia DAY: si al cierre no se ejecutó → CADUCADA (se decide de nuevo al día siguiente).
- **Costes** (automáticos): comisión IBKR Tiered (Madrid: Fixed 0,05% mín. 3 €), tasas estimadas 1 pb,
  stamp duty UK 0,5% / Irlanda 1%, TTF Francia 0,4%, ITF España 0,2%, Italia 0,1% (compras),
  FX manual: 0,20 pb mín. 2 USD + 0,03% de diferencial. Las divisas sobrantes se quedan como caja en esa divisa.
- **Nunca** registres operaciones con fecha pasada ni edites `operaciones.csv`. Si una ejecución falló,
  la siguiente retoma y lo anota en el diario.
- Dividendos (`dividendos`): netos de retención en origen; sin IRPF español. Plusvalías se reinvierten íntegras.

### 4.1 Ficha de entrada y de salida (pedido por Ale el 10/11/2026)
Ale quiere que **cada vez que se entra o se sale de un valor** se le explique por qué y con qué precio objetivo.
- Toda tesis lleva una sección `## En pocas palabras` (qué es, por qué está barata, qué espero, qué me haría vender),
  en lenguaje llano y sin cifras de TIR. **`orden` no deja comprar si falta.** Si revisas una tesis, actualízala.
- **Precio objetivo** = precio a 3 años del escenario central (base). **Precio esperado** = media de los cuatro
  escenarios ponderada por su probabilidad (el que da la TIR). Salen de `ev.py` (`precio_objetivo`); no son una regla
  nueva ni se retocan: son los precios de los escenarios ya escritos, comparados con el precio de la orden.
- `cartera.py orden` imprime la ficha al crear la orden y añade el objetivo al motivo (así llega al ledger y al panel).
  **Pega la ficha en el diario** de esa ejecución (una vez por valor: si la orden caduca y se relanza, basta con anotar
  el nuevo límite y el nuevo potencial). `cartera.py investing` añade el porqué debajo de cada operación.
- **Ventas:** el `--motivo` debe decir cuál de los 4 motivos de venta aplica y el hecho concreto (qué condición de
  invalidación, qué TIR residual, por qué valor se rota). La ficha de salida añade el resultado y lo que se esperaba al
  comprar. En una venta por tesis rota, anota antes en el historial de la tesis qué ha pasado.
- A mano: `python3 scripts/ficha.py tesis/X.md [--precio-hoy]` (entrada) · `--venta --motivo "..."` (salida) ·
  `--comprobar` (qué tesis tienen el resumen).

## 5. Panel e informes
- El panel es un Artifact de tipo Dashboard (URL y pasos en `config/panel.json`). Cada noche:
  `python3 scripts/panel.py` → subir `panel/panel.json` como asset (Artifact publish, `url`, `asset: true`) →
  `ArtifactData` get de los 6 `datasets/<id>` y batch `update` con el nuevo `source.url`, `updated` y `edit`
  (con `if_version`). No toques `files/index.html` salvo que Ale pida cambios de diseño (`panel/index.html` es su copia).
- Informe semanal (viernes, `informes/semana-AAAA-WW.md`): rentabilidad vs. benchmarks, qué funcionó/qué no,
  tesis que cambiaron, órdenes no ejecutadas (coste/beneficio de ser paciente), plan de la semana siguiente.
- En el informe semanal y el mensual: comparar la cartera con las **descartadas** (`cartera.json` → `descartadas`: ¿aportan
  valor los vetos y exclusiones?) y, cuando haya historia, las **predicciones** (`ledger/predicciones.csv`) con lo ocurrido.
- Métricas a seguir: rentabilidad, volatilidad, drawdown, alfa vs. MSCI Europe Value (CEMS.DE), % aciertos,
  retorno medio ganadoras vs. perdedoras, provisionales vs. definitivas, calibración de escenarios.

## 6. Git
- Trabaja en `main`. Commit al final de cada ejecución: `git add -A && git commit -m "<EJECUCIÓN> AAAA-MM-DD: resumen"`.
- `git push origin main`; si falla por red, reintenta 4 veces (2s, 4s, 8s, 16s). Si hay conflicto: `git pull --rebase`.

## 7. Investing (espejo manual de Ale, cartera "VALUE ex-USA")
- `cartera.py investing` regenera `investing/pendiente.md` en el orden del formulario de Investing:
  Buscar → Tipo → Fecha → Cantidad → Precio → Comisión. Londres: precio en **GBX** y comisión en **GBP**.
  Ventas: "Cerrar posición" por lote FIFO (fecha de apertura del lote).
- Cuando Ale diga que las ha pasado: `cartera.py investing-marcar T-0002 T-0005 ...`.
- Investing no registra dividendos ni costes de FX: la cifra buena es siempre la del ledger.

## 8. Avisos al móvil
Solo cuando haya operaciones (órdenes ejecutadas o nuevas órdenes lanzadas). Texto breve:
"🟢 COMPRA 8 ULVR.L @ 4.925p · objetivo 6.000p (+22%) · 🔴 VENTA … (motivo en 3–4 palabras) · Caja: X € · Ver panel".
El objetivo es la línea que da la ficha (sección 4.1); el porqué completo va en el diario. Usa la herramienta PushNotification.

## 9. Estilo
- Todo en español. Diario y tesis concisos pero con números. Explica *por qué*, que Ale quiere ver cómo se
  gestionan los cambios. Sé honesto con los errores: regístralos, no los maquilles.
