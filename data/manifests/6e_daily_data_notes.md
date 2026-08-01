# 6E Daily Data Notes

## What This File Records

This file records the 6E daily research table built from local
Databento `6E.v.0` `ohlcv-1m` downloads. The table uses the paper's CME Euro FX
effective trading window.

## Local Output

- Processed table: `data/processed/6e_daily_research_table.parquet`
- Git status: ignored by `.gitignore`; not committed
- GitHub summary file: `data/manifests/6e_daily_data_summary.json`

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
| Included dates | 3,645 |
| Excluded dates | 227 |
| Included replication dates | 2,417 |
| Included OOS dates | 1,228 |

Date range: `2010-06-07` to `2025-12-31`.

## Exclusion Reasons

| Reason | Count | Interpretation |
| --- | ---: | --- |
| `calendar_closed` | 2 | Candidate date appears in data but is closed in the selected product calendar |
| `calendar_early_close_before_effective_close` | 92 | Product calendar closes before the `14:00` effective close |
| `missing_exact_boundary_source_on_calendar_day` | 73 | Calendar trading days with missing required boundary bars |
| `missing_previous_close` | 2 | First candidate date in each sample segment has no prior effective close |
| `previous_close_cross_instrument` | 58 | Prior close and current boundaries are from different `instrument_id` values |

## Included Return Summary

| Variable | Count | Mean | Std | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `r_ONFH` | 3,645 | -0.000117 | 0.003809 | -0.026242 | 0.021931 |
| `r_M` | 3,645 | -0.000012 | 0.003500 | -0.021145 | 0.029712 |
| `r_SLH` | 3,645 | 0.000035 | 0.000830 | -0.014302 | 0.009392 |
| `r_ROD` | 3,645 | -0.000094 | 0.005231 | -0.022254 | 0.029672 |
| `r_LH` | 3,645 | 0.000002 | 0.000817 | -0.012130 | 0.013492 |

Databento definitions show two `min_price_increment` values historically for
6E, `0.0001` and `0.00005`; the current OOS period uses `0.00005`. Tick-cost
analysis must therefore use date-aware contract definitions.

Regression and strategy outputs are stored separately in `reports/tables/`.
