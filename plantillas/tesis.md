# {NOMBRE} ({TICKER} · {BOLSA}) — Tesis

- **Estado:** 🟡 provisional | 🟢 definitiva | 🔴 vendida | ⚪ candidata (no comprada)
- **ISIN:** · **País emisor:** · **Sector:** · **Divisa/unidad:**
- **Última revisión:** AAAA-MM-DD · **Próximos resultados:** AAAA-MM-DD

## Filtros duros (pregunta 6)
| Filtro | Valor | ¿Cumple? |
|---|---|---|
| Capitalización ≥ 2.000 M€ | | |
| Volumen medio diario ≥ 2 M€ | | |
| ≥ 10 años de historia | | |
| Beneficio operativo + en ≥ 7/10 años | | |
| Deuda neta/EBITDA ≤ 3x (financieras: CET1 ≥ 12%) | | |
| Sin insolvencia / going concern | | |
Filtros blandos: ROCE medio · FCF + en x/5 · dilución anual.

## Tesis (cualitativa)
Por qué está barata, qué espera el mercado, qué espero yo y por qué tengo razón. Catalizadores.

## Condiciones de invalidación
Hechos concretos y verificables que, si ocurren, obligan a vender sin mirar el precio.
1.
2.

## Escenarios y EV (escritos ANTES de ver si "sale bien")
| Escenario | Prob | Relato | Métrica año 3 × múltiplo | Precio 3a | Div. 3a |
|---|---|---|---|---|---|
| 🐻 Desastre | | | | | |
| 📉 Bajista | | | | | |
| ⚖️ Base | | | | | |
| 🚀 Alcista | | | | | |

```ev
{
  "ticker": "", "mercado": "", "pais": "", "precio_actual": 0, "fecha": "",
  "escenarios": {
    "desastre": {"prob": 0.0, "precio_3a": 0, "dividendos_3a": 0},
    "bajista":  {"prob": 0.0, "precio_3a": 0, "dividendos_3a": 0},
    "base":     {"prob": 0.0, "precio_3a": 0, "dividendos_3a": 0},
    "alcista":  {"prob": 0.0, "precio_3a": 0, "dividendos_3a": 0}
  },
  "comite": {
    "valorador_ciego": {"tir": null, "prob_desastre": null},
    "bajista": {"prob_desastre": null, "veto": false}
  }
}
```
Resultado `python3 scripts/ev.py tesis/{TICKER}.md`: (pegar TIR propia, TIR comité, cumple)

## Comité
### 🔴 Bajista
### 🔵 Valorador ciego
### Reconciliación
Regla aplicada, TIR final, decisión.

## Decisión
COMPRAR / NO COMPRAR / PROVISIONAL — motivo.

## Historial de revisiones
| Fecha | Evento | TIR antes → después | Cambio en probabilidades | Acción |
|---|---|---|---|---|
