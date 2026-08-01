# ZN Daily Data Notes

## What This File Records

This file records the ZN daily research table built from local
Databento `ZN.v.0` `ohlcv-1m` downloads. The table uses the paper's CBOT
10-year U.S. Treasury note effective trading window.

## Local Output

- Processed table: `data/processed/zn_daily_research_table.parquet`
- Git status: ignored by `.gitignore`; not committed
- GitHub summary file: `data/manifests/zn_daily_data_summary.json`

The processed table is derived from licensed Databento data and must not be
uploaded to GitHub.

## Boundary Rules

- Time zone: `America/New_York`
- Product calendar: `CME_Bond`
- Effective ZN window: `08:20-15:00`
- Required current-day boundaries: `08:20`, `08:50`, `14:00`, `14:30`, `15:00`
- Boundary price: one-minute bar `close`
- Prior close: prior available `15:00` New York effective close within the same
  sample segment
- Baseline rule: prior close and current `08:50`, `14:00`, `14:30`, `15:00`
  prices must all come from the same `instrument_id`

## Row Counts

| Category | Count |
| --- | ---: |
| Candidate dates | 3,869 |
| Included dates | 3,642 |
| Excluded dates | 227 |
| Included replication dates | 2,421 |
| Included OOS dates | 1,221 |

Date range: `2010-06-07` to `2025-12-31`.

## Exclusion Reasons

| Reason | Count | Interpretation |
| --- | ---: | --- |
| `calendar_early_close_before_effective_close` | 117 | Product calendar closes before the `15:00` effective close |
| `missing_boundary_on_calendar_day` | 49 | Calendar trading days with missing required boundary bars |
| `missing_previous_close` | 2 | First candidate date in each sample segment has no prior effective close |
| `previous_close_cross_instrument` | 59 | Prior close and current boundaries are from different `instrument_id` values |

## Included Return Summary

| Variable | Count | Mean | Std | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `r_ONFH` | 3,642 | 0.000041 | 0.002514 | -0.011015 | 0.019478 |
| `r_M` | 3,642 | 0.000045 | 0.002179 | -0.012952 | 0.009736 |
| `r_SLH` | 3,642 | -0.000010 | 0.000584 | -0.003514 | 0.004857 |
| `r_ROD` | 3,642 | 0.000076 | 0.003314 | -0.013811 | 0.018692 |
| `r_LH` | 3,642 | -0.000034 | 0.000626 | -0.004921 | 0.007634 |

Regression and strategy outputs are stored separately in `reports/tables/`.
