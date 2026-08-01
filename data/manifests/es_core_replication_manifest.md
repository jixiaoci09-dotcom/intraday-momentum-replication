# ES Core Replication Manifest

The ES core replication uses the frozen daily table rules, the paper's Table 2 Eq. (5)-(7), Table 6 Eq. (12), period-interaction beta difference tests, and fixed-split OOS R2 diagnostics.

```json
{
  "regression_specs": {
    "eq5_onfh": "r_LH,t = alpha + beta_ONFH * r_ONFH,t + epsilon_t",
    "eq6_onfh_m_slh": "r_LH,t = alpha + beta_ONFH * r_ONFH,t + beta_M * r_M,t + beta_SLH * r_SLH,t + epsilon_t",
    "eq7_rod": "r_LH,t = alpha + beta_ROD * r_ROD,t + epsilon_t"
  },
  "beta_difference_test": "pooled regression with OOS dummy and predictor-by-OOS interactions; interaction beta tests OOS beta minus replication beta",
  "oos_r2": "1 - SSE_model / SSE_benchmark, where model is trained on replication and benchmark is replication-sample mean r_LH",
  "strategy_rule": "eta(r) = r_LH if r > 0, otherwise -r_LH; eta(r_ONFH,r_ROD) trades only when signs agree",
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
    "regression": "reports/tables/es_core_regression_summary.csv",
    "beta_difference": "reports/tables/es_core_beta_difference_tests.csv",
    "oos_r2": "reports/tables/es_core_oos_r2.csv",
    "strategy": "reports/tables/es_core_strategy_summary.csv",
    "yearly_strategy": "reports/tables/es_core_strategy_by_year.csv"
  }
}
```
