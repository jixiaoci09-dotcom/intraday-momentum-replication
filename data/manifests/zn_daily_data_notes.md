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
| Included dates | 3,618 |
| Excluded dates | 251 |
| Included replication dates | 2,397 |
| Included OOS dates | 1,221 |

Date range: `2010-06-07` to `2025-12-31`.

## Exclusion Reasons

| Reason | Count | Interpretation |
| --- | ---: | --- |
| `calendar_early_close_before_effective_close` | 117 | Product calendar closes before the `15:00` effective close |
| `missing_exact_boundary_source_on_calendar_day` | 73 | Calendar trading days with missing required boundary bars |
| `missing_previous_close` | 2 | First candidate date in each sample segment has no prior effective close |
| `previous_close_cross_instrument` | 59 | Prior close and current boundaries are from different `instrument_id` values |

## Included Return Summary

| Variable | Count | Mean | Std | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `r_ONFH` | 3,618 | 0.000024 | 0.002511 | -0.010891 | 0.019196 |
| `r_M` | 3,618 | 0.000043 | 0.002166 | -0.012567 | 0.010663 |
| `r_SLH` | 3,618 | -0.000018 | 0.000673 | -0.006016 | 0.008818 |
| `r_ROD` | 3,618 | 0.000048 | 0.003322 | -0.013938 | 0.018836 |
| `r_LH` | 3,618 | -0.000016 | 0.000634 | -0.004778 | 0.007762 |

Regression and strategy outputs are stored separately in `reports/tables/`.
