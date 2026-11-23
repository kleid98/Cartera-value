# Pasar operaciones a Investing con Claude en Chrome

Ale pasa las operaciones a Investing con la extensión **Claude en Chrome** (desde el 14/11/2026). Desde aquí no se
puede: la sesión no controla su navegador. El gestor prepara un mensaje con las operaciones de `pendiente.md`, Ale lo
pega en una conversación con la extensión y, cuando dice «pasadas», se marcan con `cartera.py investing-marcar`.

## Símbolos de Investing que no coinciden con el ticker oficial

| Valor | Ticker (Yahoo) | Investing | Cuidado con |
|---|---|---|---|
| Sanofi | SAN.PA | **SASY** (París, EUR, pair 414) | "SAN" es el DRC de CBOE Canadá; "AVEPp" es una línea secundaria |
| Azimut | AZM.MI | **AZMT** (Milán, pair 13378) | — |
| Magna | MG.TO | **MG** (Toronto, CAD, pair 24586) | MGA es Nueva York (USD) |
| BNP Paribas | BNP.PA | **BNPP** (París, pair 396) | — |
| Novo Nordisk | NOVO-B.CO | **NOVOb** (Copenhague, DKK, pair 555) | — |
| Bouygues | EN.PA | **BOUY** (París, pair 397) | — |
| freenet | FNTN.DE | **FNTGn** (Xetra, pair 6285) | — |
| Teleperformance | TEP.PA | **TEPRF** (París, pair 7087) | — |
| SCOR | SCR.PA | **SCOR** (París) | — |
| Mapfre, Linamar, Imperial, Ahold | MAP.MC, LNR.TO, IMB.L, AD.AS | mismo ticker (Madrid, Toronto CAD, Londres GBp, Ámsterdam) | IMB: precio en peniques (2873) |
| NN Group | NN.AS | NN (Ámsterdam, pair 943213) | — |
| Ayvens | AYV.PA | AYV (París, pair 1012045) | — |
| Intesa Sanpaolo | ISP.MI | ISP (Milán, pair 6951) | — |
| NatWest, BP, Harbour, Centrica | NWG.L, BP.L, HBR.L, CNA.L | NWG (295), BP (284), HBR (6718), CNA (6574) (Londres, GBp) | precio en peniques |

Añadir aquí cada valor nuevo que la extensión encuentre con otro símbolo.

## Cómo es el formulario «Añadir posición»
- Se busca en la caja "EUR/USD o BBVA" y se elige la fila de la bolsa ("Acción - París", etc.).
- Una vez elegido solo se ve el símbolo, no la bolsa: se comprueba por la divisa de la comisión o el pair ID.
- La fecha no admite texto: hay que usar el calendario (por defecto pone hoy).
- El precio sale relleno con el actual: hay que cambiarlo.
- La comisión no aparece luego en las tablas de Posiciones ni de Transacciones.

## Mensaje tipo para la extensión
Incluir, además de las operaciones (valor, bolsa, símbolo de Investing, cantidad, precio con divisa, comisión, fecha):
comprobar cada campo antes de guardar; bolsa indicada y nunca ADR; no duplicar si ya existe la misma fecha y cantidad;
no tocar nada más; parar y preguntar si algo no cuadra; al final, tabla con lo guardado.

## Historial
- 14/11/2026: pasadas T-0003, T-0004, T-0006, T-0008, T-0010 (12/11) y T-0011 a T-0014 y T-0016 (13/11).
  Valor de mercado en Investing tras añadirlas: 4.830,39 € (ledger al cierre del 13/11: 4.825,25 € en posiciones;
  la diferencia es el tipo de cambio que usa Investing).
- 16/11/2026: pasadas T-0018 a T-0022. Comprobación completa con la extensión en modo lectura: las 15 compras de Investing
  coinciden con el ledger (fecha, cantidad, precio, bolsa); sin duplicados. Valor de mercado a las 12:40: Investing
  7.256,82 € · ledger 7.254,02 € (diferencia de tipo de cambio).
- 23/11/2026: pasadas T-0023, T-0024, T-0026, T-0028 y T-0029 → **20/20 en Investing**. La extensión no devolvió la tabla de
  transacciones, solo el resumen: 20 posiciones, sin duplicados (en Mapfre el primer clic no guardó; comprobó que solo hay una).
  Valor de mercado a las 12:24: Investing 9.283,20 € · ledger 9.279,34 € (diferencia de tipo de cambio).

## Mensaje de comprobación (modo lectura)
Tras meter operaciones, pedir a la extensión que NO cambie nada y devuelva: (1) tabla de todas las transacciones
(Fecha | Valor | Símbolo | Bolsa | Pair ID | Tipo | Cantidad | Precio | Divisa | Comisión), (2) nº de posiciones, valor de
mercado y duplicados, (3) símbolos que no coincidan con el ticker. Se cruza con `ledger/operaciones.csv` antes de marcar.
