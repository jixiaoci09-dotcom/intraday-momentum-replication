# NQ.v.0 Core Replication Manifest

This replication uses the frozen equity-index daily table rules and the paper's Table 2 Eq. (5)-(7) and Table 6 Eq. (12) logic.

```json
{
  "symbol": "NQ.v.0",
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
  "strategy_rule": "eta(r) = r_LH if r > 0, otherwise -r_LH; eta(r_ONFH,r_ROD) trades only when signs agree",
  "beta_difference_test": "pooled regression with OOS dummy and predictor-by-OOS interactions",
  "oos_r2": "model trained on replication; benchmark is replication-sample mean r_LH",
  "annualization_days": 252,
  "newey_west_lag_rule": "floor(4 * (T / 100) ** (2 / 9))",
  "samples": {
    "replication": {
      "start": "2010-06-08",
      "end": "2020-05-29",
      "nobs": 2443
    },
    "oos": {
      "start": "2021-01-05",
      "end": "2025-12-31",
      "nobs": 1224
    }
  },
  "outputs": {
    "regression": "reports/tables/nq_core_regression_summary.csv",
    "beta_diff": "reports/tables/nq_core_beta_difference_tests.csv",
    "oos_r2": "reports/tables/nq_core_oos_r2.csv",
    "strategy": "reports/tables/nq_core_strategy_summary.csv",
    "yearly": "reports/tables/nq_core_strategy_by_year.csv",
    "manifest": "data/manifests/nq_core_replication_manifest.md"
  }
}
```
