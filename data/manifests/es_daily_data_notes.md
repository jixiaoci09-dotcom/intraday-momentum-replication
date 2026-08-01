# ES Daily Data Notes

## What This File Records

This file records the ES daily research table built from local
Databento `ES.v.0` `ohlcv-1m` downloads. The table follows the data cleaning rules in `docs/daily_data_rules.md`.

## Local Output

- Processed table: `data/processed/es_daily_research_table.parquet`
- Git status: ignored by `.gitignore`; not committed
- GitHub summary file: `data/manifests/es_daily_data_summary.json`

The processed table is derived from licensed Databento data and must not be
uploaded to GitHub.

## Boundary Rules

- Time zone: `America/New_York`
- Effective ES window: `09:30-16:00`
- Required current-day boundaries: `09:30`, `10:00`, `15:00`, `15:30`, `16:00`
- Boundary price: one-minute bar `close`
- Prior close: prior available `16:00` New York close
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
| `missing_boundary_on_regular_day` | 7 | NYSE regular-close days with missing required boundary bars |
| `missing_previous_close` | 1 | First candidate date has no prior close |
| `nyse_closed` | 85 | CME had relevant observations but NYSE was closed |
| `nyse_early_close` | 32 | NYSE early-close days removed from the sample |
| `previous_close_cross_instrument` | 61 | Prior close and current boundaries are from different `instrument_id` values |

## Included Return Summary

| Variable | Count | Mean | Std | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `r_ONFH` | 3,667 | 0.000280 | 0.007217 | -0.090664 | 0.064348 |
| `r_M` | 3,667 | 0.000231 | 0.006352 | -0.041067 | 0.056985 |
| `r_SLH` | 3,667 | 0.000018 | 0.002097 | -0.019671 | 0.027721 |
| `r_ROD` | 3,667 | 0.000532 | 0.010066 | -0.093541 | 0.093463 |
| `r_LH` | 3,667 | -0.000017 | 0.002751 | -0.026830 | 0.043781 |

These are descriptive checks only. Regression and strategy results are stored
separately in `reports/tables/`.

## Research Implications

- The ES daily table is ready for the regression and strategy scripts.
- Early closes and holidays are excluded by the missing-boundary rule.
- Roll-sensitive days are excluded when prior and current prices cross
  `instrument_id`.
- Future robustness checks can compare this conservative sample against
  alternative roll handling.
