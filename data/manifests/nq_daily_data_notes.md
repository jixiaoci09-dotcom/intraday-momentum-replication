# NQ Daily Data Notes

## What This File Records

This file records the NQ daily research table built from local
Databento `NQ.v.0` `ohlcv-1m` downloads. The table follows the same U.S. equity-index timing choices used for ES.

## Local Output

- Processed table: `data/processed/nq_daily_research_table.parquet`
- Git status: ignored by `.gitignore`; not committed
- GitHub summary file: `data/manifests/nq_daily_data_summary.json`

The processed table is derived from licensed Databento data and must not be
uploaded to GitHub.

## Boundary Rules

- Time zone: `America/New_York`
- Effective NQ window: `09:30-16:00`
- Required current-day boundaries: `09:30`, `10:00`, `15:00`, `15:30`, `16:00`
- Boundary price: one-minute bar `close`
- Prior close: prior available `16:00` New York close within the same sample
  segment
- Baseline rule: prior close and current `10:00`, `15:00`, `15:30`, `16:00`
  prices must all come from the same `instrument_id`

## Row Counts

| Category | Count |
| --- | ---: |
| Candidate dates | 3,853 |
| Included dates | 3,667 |
| Excluded dates | 186 |
| Included replication dates | 2,443 |
| Included OOS dates | 1,224 |

Date range: `2010-06-07` to `2025-12-31`.

## Exclusion Reasons

| Reason | Count | Interpretation |
| --- | ---: | --- |
| `missing_exact_boundary_source_on_regular_day` | 7 | NYSE regular-close days with missing required boundary bars |
| `missing_previous_close` | 2 | First candidate date in each sample segment has no prior close |
| `nyse_closed` | 85 | CME had relevant observations but NYSE was closed |
| `nyse_early_close` | 32 | NYSE early-close days removed from the sample |
| `previous_close_cross_instrument` | 60 | Prior close and current boundaries are from different `instrument_id` values |

## Included Return Summary

| Variable | Count | Mean | Std | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `r_ONFH` | 3,667 | 0.000476 | 0.008404 | -0.088205 | 0.057220 |
| `r_M` | 3,667 | 0.000232 | 0.007887 | -0.044293 | 0.076161 |
| `r_SLH` | 3,667 | -0.000016 | 0.002344 | -0.018407 | 0.019920 |
| `r_ROD` | 3,667 | 0.000698 | 0.012229 | -0.086757 | 0.110778 |
| `r_LH` | 3,667 | -0.000035 | 0.003179 | -0.042536 | 0.051261 |

Regression and strategy outputs are stored separately in `reports/tables/`.
