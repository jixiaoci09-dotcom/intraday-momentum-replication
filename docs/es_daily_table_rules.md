# ES Daily Research Table Rules

These rules freeze the first ES implementation before regression or strategy
results are inspected.

## Time Zone And Window

- Source timestamps are UTC.
- Boundary times are defined in `America/New_York`.
- Effective ES window follows the underlying U.S. equity market: `09:30-16:00`.

## Boundary Prices

For each trade date:

- `P_{t-1, close}`: prior available `16:00` New York close.
- `P_{t, open+30}`: current `10:00` New York close.
- `P_{t, close-60}`: current `15:00` New York close.
- `P_{t, close-30}`: current `15:30` New York close.
- `P_{t, close}`: current `16:00` New York close.

The minute bar `close` is used for each boundary price.

## Inclusion Rules

A day is included only when:

- NYSE is open and has a regular `16:00` New York close.
- Current `09:30`, `10:00`, `15:00`, `15:30`, and `16:00` boundaries exist.
- Current `10:00`, `15:00`, `15:30`, and `16:00` boundaries are from the same
  `instrument_id`.
- A prior available `16:00` close exists.
- The prior close and current boundaries share the same `instrument_id`.

Days failing these rules are retained in the local daily table with exclusion
reasons, but excluded from regressions and strategy tests.

NYSE trading days and early closes are identified with
`pandas-market-calendars` using the `NYSE` calendar. Early closes are excluded
from the baseline because the paper removes days on which the exchange closed
early.

## Variables

For included days:

```text
r_ONFH = P_{t, open+30} / P_{t-1, close} - 1
r_M    = P_{t, close-60} / P_{t, open+30} - 1
r_SLH  = P_{t, close-30} / P_{t, close-60} - 1
r_ROD  = P_{t, close-30} / P_{t-1, close} - 1
r_LH   = P_{t, close} / P_{t, close-30} - 1
```

The core replication estimates the paper's Table 2 specifications:

```text
Eq. (5): r_LH,t = alpha + beta_ONFH * r_ONFH,t + epsilon_t
Eq. (6): r_LH,t = alpha + beta_ONFH * r_ONFH,t
                  + beta_M * r_M,t + beta_SLH * r_SLH,t + epsilon_t
Eq. (7): r_LH,t = alpha + beta_ROD * r_ROD,t + epsilon_t
```

## Outputs

- Local processed table: `data/processed/es_daily_research_table.parquet`
- Git-tracked summary: `data/manifests/es_daily_data_summary.json`

The processed table is ignored by Git because it is derived from licensed
Databento data.
