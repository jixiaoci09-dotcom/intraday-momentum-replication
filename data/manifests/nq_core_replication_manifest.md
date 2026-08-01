# NQ.v.0 Core Replication Manifest

This replication uses the frozen cleaned daily table rules for the symbol and the paper's Table 2 Eq. (5)-(7) and Table 6 Eq. (12) logic.

```json
{
  "symbol": "NQ.v.0",
  "pipeline_version": "boundary_corrected_v1",
  "daily_table": "data/processed/nq_daily_research_table.parquet",
  "regression_specs": {
    "eq5_onfh": [
      "r_ONFH"
    ],
    "eq6_onfh_m_slh": [
      "r_ONFH",
      "r_M",
      "r_SLH"
    ],
    "eq7_rod": [
      "r_ROD"
    ]
  },
  "strict_replication_sample_end": "2020-05-01",
  "extended_training_sample_note": "Any estimate using data after 2020-05-01 must be labeled extended training sample, not strict paper overlap.",
  "statistical_lh_return": "r_LH uses paper boundary prices",
  "strategy_lh_return": "r_LH_executable when present; entry is close-minus-30 boundary next bar open",
  "strategy_rule": "eta(r) = strategy_lh_return if r > 0, otherwise -strategy_lh_return; eta(r_ONFH,r_ROD) trades only when signs agree",
  "beta_difference_test": "pooled regression with OOS dummy and predictor-by-OOS interactions",
  "oos_r2": {
    "expanding": "Each OOS prediction day re-estimates using strict replication sample plus prior OOS observations; benchmark mean also updates through t-1.",
    "frozen_2020": "Estimate once using strict replication sample through 2020-05-01; benchmark mean fixed through OOS."
  },
  "annualization_days": 252,
  "tick_size": 0.25,
  "round_trip_tick_costs": [
    0,
    1,
    2,
    3
  ],
  "tick_cost_rule": "Net simple return subtracts round_trip_ticks * tick_size / entry_price for traded days.",
  "strategy_price_types": {
    "paper_statistical": "Entry uses p_close_minus_30, the paper boundary price. This is not a realistic fill.",
    "executable_next_open": "Entry uses p_lh_entry_next_open, the next bar open after signal formation."
  },
  "newey_west_lag_rule": "floor(4 * (T / 100) ** (2 / 9))",
  "samples": {
    "replication": {
      "start": "2010-06-08",
      "end": "2020-05-01",
      "nobs": 2424,
      "common_valid_nobs": 2424
    },
    "oos": {
      "start": "2021-01-05",
      "end": "2025-12-31",
      "nobs": 1224,
      "common_valid_nobs": 1224
    }
  },
  "outputs": {
    "regression": "reports/tables/nq_core_regression_summary.csv",
    "beta_diff": "reports/tables/nq_core_beta_difference_tests.csv",
    "oos_r2": "reports/tables/nq_core_oos_r2.csv",
    "oos_predictions": "reports/tables/nq_core_oos_predictions.csv",
    "strategy": "reports/tables/nq_core_strategy_summary.csv",
    "yearly": "reports/tables/nq_core_strategy_by_year.csv",
    "manifest": "data/manifests/nq_core_replication_manifest.md"
  }
}
```
