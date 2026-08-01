# 6E Daily Research Table Manifest

## Purpose

This manifest documents the first 6E daily research table built from local
Databento `6E.v.0` `ohlcv-1m` downloads. The table uses the paper's CME Euro FX
effective trading window.

## Local Output

- Processed table: `data/processed/6e_daily_research_table.parquet`
- Git status: ignored by `.gitignore`; not committed
- Git-tracked summary: `data/manifests/6e_daily_research_table_summary.json`

The processed table is derived from licensed Databento data and must not be
uploaded to GitHub.

## Boundary Rules

- Time zone: `America/New_York`
- Product calendar: `CMEGlobex_FX`
- Effective 6E window: `07:20-14:00`
- Required current-day boundaries: `07:20`, `07:50`, `13:00`, `13:30`, `14:00`
- Boundary price: one-minute bar `close`
- Prior close: prior available `14:00` New York effective close within the same
  sample segment
- Baseline rule: prior close and current `07:50`, `13:00`, `13:30`, `14:00`
  prices must all come from the same `instrument_id`

## Row Counts

| Category | Count |
| --- | ---: |
| Candidate dates | 3,872 |
| Included dates | 3,668 |
| Excluded dates | 204 |
| Included replication dates | 2,430 |
| Included OOS dates | 1,238 |

Date range: `2010-06-07` to `2025-12-31`.

## Exclusion Reasons

| Reason | Count | Interpretation |
| --- | ---: | --- |
| `calendar_closed` | 2 | Candidate date appears in data but is closed in the selected product calendar |
| `calendar_early_close_before_effective_close` | 92 | Product calendar closes before the `14:00` effective close |
| `missing_boundary_on_calendar_day` | 48 | Calendar trading days with missing required boundary bars |
| `missing_previous_close` | 2 | First candidate date in each sample segment has no prior effective close |
| `previous_close_cross_instrument` | 60 | Prior close and current boundaries are from different `instrument_id` values |

## Included Return Summary

| Variable | Count | Mean | Std | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `r_ONFH` | 3,668 | -0.000114 | 0.003764 | -0.026201 | 0.021839 |
| `r_M` | 3,668 | -0.000001 | 0.003504 | -0.021492 | 0.028715 |
| `r_SLH` | 3,668 | 0.000028 | 0.000782 | -0.010440 | 0.006868 |
| `r_ROD` | 3,668 | -0.000086 | 0.005179 | -0.021262 | 0.028905 |
| `r_LH` | 3,668 | -0.000002 | 0.000864 | -0.007488 | 0.009626 |

Databento definitions show two `min_price_increment` values historically for
6E, `0.0001` and `0.00005`; the current OOS period uses `0.00005`. Tick-cost
analysis must therefore use date-aware contract definitions.

Regression and strategy outputs are stored separately in `reports/tables/`.
