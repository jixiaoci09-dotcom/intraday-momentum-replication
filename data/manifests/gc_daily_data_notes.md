# GC Daily Data Notes

## What This File Records

This file records the GC daily research table built from local
Databento `GC.v.0` `ohlcv-1m` downloads. The table uses the paper's COMEX gold
effective trading window rather than the U.S. equity-index window.

## Local Output

- Processed table: `data/processed/gc_daily_research_table.parquet`
- Git status: ignored by `.gitignore`; not committed
- GitHub summary file: `data/manifests/gc_daily_data_summary.json`

The processed table is derived from licensed Databento data and must not be
uploaded to GitHub.

## Boundary Rules

- Time zone: `America/New_York`
- Product calendar: `CMEGlobex_GC`
- Effective GC window: `08:20-13:30`
- Required current-day boundaries: `08:20`, `08:50`, `12:30`, `13:00`, `13:30`
- Boundary price: one-minute bar `close`
- Prior close: prior available `13:30` New York effective close within the same
  sample segment
- Baseline rule: prior close and current `08:50`, `12:30`, `13:00`, `13:30`
  prices must all come from the same `instrument_id`

## Row Counts

| Category | Count |
| --- | ---: |
| Candidate dates | 3,869 |
| Included dates | 3,640 |
| Excluded dates | 229 |
| Included replication dates | 2,414 |
| Included OOS dates | 1,226 |

Date range: `2010-06-07` to `2025-12-31`.

## Exclusion Reasons

| Reason | Count | Interpretation |
| --- | ---: | --- |
| `calendar_early_close_before_effective_close` | 67 | Product calendar closes before the `13:30` effective close |
| `missing_exact_boundary_source_on_calendar_day` | 85 | Calendar trading days with missing required boundary bars |
| `missing_previous_close` | 2 | First candidate date in each sample segment has no prior effective close |
| `previous_close_cross_instrument` | 75 | Prior close and current boundaries are from different `instrument_id` values |

## Included Return Summary

| Variable | Count | Mean | Std | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `r_ONFH` | 3,640 | 0.000255 | 0.007839 | -0.052846 | 0.067922 |
| `r_M` | 3,640 | -0.000088 | 0.005606 | -0.038014 | 0.034211 |
| `r_SLH` | 3,640 | 0.000039 | 0.001385 | -0.011419 | 0.015857 |
| `r_ROD` | 3,640 | 0.000207 | 0.009878 | -0.086481 | 0.057644 |
| `r_LH` | 3,640 | -0.000019 | 0.001465 | -0.015048 | 0.009400 |

Regression and strategy outputs are stored separately in `reports/tables/`.
