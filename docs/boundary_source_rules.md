# Corrected Boundary Source Rules

Databento `OHLCV-1m` `ts_event` represents the start of the one-minute bar.
Therefore the project uses the following corrected source rules for all daily
research tables built after `INVALID_BOUNDARY_V0`.

## Statistical Boundary Prices

For any theoretical non-open boundary time `T`, the price `P_T` is the `close`
of the bar with `ts_event = T - 1 minute`.

Examples:

- ES/NQ `P_16:00` uses the `15:59` bar `close`.
- GC `P_13:30` uses the `13:29` bar `close`.
- CL `P_14:30` uses the `14:29` bar `close`.
- ZN `P_15:00` uses the `14:59` bar `close`.
- 6E `P_14:00` uses the `13:59` bar `close`.

If the exact source bar is missing, the main sample drops that symbol-date and
records `drop_reason` plus `missing_boundary_sources`. No nearest-neighbor
selection or interpolation is allowed.

## Session Open

When the session open price is recorded, it uses the `open` of the bar with
`ts_event` equal to the session open.

## Executable Last-Half-Hour Return

The paper statistical `r_LH` uses:

```text
r_LH = P_close / P_close_minus_30 - 1
```

where both prices are corrected boundary prices. The executable strategy return
is stored separately as `r_LH_executable`, with entry at the `open` of the bar
whose `ts_event` equals the theoretical `close_minus_30` boundary.
