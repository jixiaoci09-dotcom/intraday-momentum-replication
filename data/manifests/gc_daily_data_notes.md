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
| Included dates | 3,651 |
| Excluded dates | 218 |
| Included replication dates | 2,421 |
| Included OOS dates | 1,230 |

Date range: `2010-06-07` to `2025-12-31`.

## Exclusion Reasons

| Reason | Count | Interpretation |
| --- | ---: | --- |
| `calendar_early_close_before_effective_close` | 67 | Product calendar closes before the `13:30` effective close |
| `missing_boundary_on_calendar_day` | 74 | Calendar trading days with missing required boundary bars |
| `missing_previous_close` | 2 | First candidate date in each sample segment has no prior effective close |
| `previous_close_cross_instrument` | 75 | Prior close and current boundaries are from different `instrument_id` values |

## Included Return Summary

| Variable | Count | Mean | Std | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `r_ONFH` | 3,651 | 0.000229 | 0.007877 | -0.053364 | 0.069047 |
| `r_M` | 3,651 | -0.000076 | 0.005619 | -0.040171 | 0.034150 |
| `r_SLH` | 3,651 | 0.000051 | 0.001402 | -0.009737 | 0.019394 |
| `r_ROD` | 3,651 | 0.000206 | 0.009880 | -0.086342 | 0.056847 |
| `r_LH` | 3,651 | -0.000018 | 0.001451 | -0.010539 | 0.007151 |

Regression and strategy outputs are stored separately in `reports/tables/`.
