# CL Daily Data Notes

## What This File Records

This file records the CL daily research table built from local
Databento `CL.v.0` `ohlcv-1m` downloads. The table uses the paper's NYMEX crude
oil effective trading window rather than a generic CME calendar.

## Local Output

- Processed table: `data/processed/cl_daily_research_table.parquet`
- Git status: ignored by `.gitignore`; not committed
- GitHub summary file: `data/manifests/cl_daily_data_summary.json`

The processed table is derived from licensed Databento data and must not be
uploaded to GitHub.

## Boundary Rules

- Time zone: `America/New_York`
- Product calendar: `CMEGlobex_CL`
- Effective CL window: `09:00-14:30`
- Required current-day boundaries: `09:00`, `09:30`, `13:30`, `14:00`, `14:30`
- Boundary price: one-minute bar `close`
- Prior close: prior available `14:30` New York effective close within the same
  sample segment
- Baseline rule: prior close and current `09:30`, `13:30`, `14:00`, `14:30`
  prices must all come from the same `instrument_id`

## Row Counts

| Category | Count |
| --- | ---: |
| Candidate dates | 3,869 |
| Included dates | 3,576 |
| Excluded dates | 293 |
| Included replication dates | 2,363 |
| Included OOS dates | 1,213 |

Date range: `2010-06-07` to `2025-12-31`.

## Exclusion Reasons

| Reason | Count | Interpretation |
| --- | ---: | --- |
| `calendar_early_close_before_effective_close` | 79 | Product calendar closes before the `14:30` effective close |
| `missing_exact_boundary_source_on_calendar_day` | 32 | Calendar trading days with missing required boundary bars |
| `missing_previous_close` | 2 | First candidate date in each sample segment has no prior effective close |
| `previous_close_cross_instrument` | 180 | Prior close and current boundaries are from different `instrument_id` values |

## Included Return Summary

| Variable | Count | Mean | Std | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `r_ONFH` | 3,576 | 0.000173 | 0.018949 | -0.285379 | 0.253236 |
| `r_M` | 3,576 | -0.000309 | 0.014087 | -0.224080 | 0.110759 |
| `r_SLH` | 3,576 | -0.000094 | 0.005152 | -0.184483 | 0.033115 |
| `r_ROD` | 3,576 | -0.000192 | 0.024887 | -0.533990 | 0.251618 |
| `r_LH` | 3,576 | 0.000144 | 0.006941 | -0.066149 | 0.221987 |

The CL sample contains very large 2020 oil-stress returns, although included
prices remain positive under the current continuous-contract and same-contract
rules. CL results should therefore be interpreted together with later
robustness checks around 2020.

Regression and strategy outputs are stored separately in `reports/tables/`.
