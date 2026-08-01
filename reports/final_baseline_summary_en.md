# Final Baseline Summary: boundary_corrected_v1

This report freezes the single-contract baseline replication for ES, NQ, GC, CL, ZN, and 6E. All headline results use `pipeline_version=boundary_corrected_v1`: product-specific effective sessions, America/New_York timestamps with DST, `T-1` minute bar closes for non-open theoretical boundaries, session-open bar opens, same-contract previous-close alignment, and pre-specified deletion of early closes, missing exact boundaries, and roll-mismatch days.

The strict paper-overlap sample ends on `2020-05-01`; the post-publication OOS period is `2021-01-01` to `2025-12-31`. The expanding OOS implementation starts from the strict replication sample and only appends prior OOS observations; `2020-05-02` to `2020-12-31` is not included in the strict overlap results or in this expanding training window.

## Paper-Overlap Eq.(7)

| symbol | start      | end        | n    | beta_x100 | nw_se_x100 | t      | p       | adj_r2_x100 |
| ------ | ---------- | ---------- | ---- | --------- | ---------- | ------ | ------- | ----------- |
| ES.v.0 | 2010-06-08 | 2020-05-01 | 2424 | 6.137     | 2.317      | 2.649  | 0.008   | 4.021       |
| NQ.v.0 | 2010-06-08 | 2020-05-01 | 2424 | 4.886     | 2.186      | 2.235  | 0.025   | 2.855       |
| GC.v.0 | 2010-06-08 | 2020-05-01 | 2396 | 2.408     | 0.537      | 4.483  | p<0.001 | 2.245       |
| CL.v.0 | 2010-06-08 | 2020-05-01 | 2345 | -3.885    | 6.539      | -0.594 | 0.552   | 1.562       |
| ZN.v.0 | 2010-06-08 | 2020-05-01 | 2379 | 2.037     | 0.629      | 3.236  | 0.001   | 0.943       |
| 6E.v.0 | 2010-06-08 | 2020-05-01 | 2398 | -0.129    | 0.465      | -0.278 | 0.781   | -0.036      |

ES, NQ, GC, and ZN show positive and statistically significant Eq.(7) coefficients in the paper-overlap period. CL and 6E are insignificant at the single-contract level, consistent with the paper's appendix-level single-contract evidence; they should not be described as replication failures. Their single-contract estimates also must not be directly compared with the paper's energy or currency pooled regressions.

## 2021-2025 OOS Eq.(7)

| symbol | start      | end        | n    | beta_x100 | nw_se_x100 | t      | p       | adj_r2_x100 |
| ------ | ---------- | ---------- | ---- | --------- | ---------- | ------ | ------- | ----------- |
| ES.v.0 | 2021-01-05 | 2025-12-31 | 1224 | -0.124    | 1.050      | -0.119 | 0.906   | -0.079      |
| NQ.v.0 | 2021-01-05 | 2025-12-31 | 1224 | 0.150     | 0.894      | 0.168  | 0.866   | -0.077      |
| GC.v.0 | 2021-01-05 | 2025-12-31 | 1226 | 0.516     | 0.534      | 0.966  | 0.334   | 0.090       |
| CL.v.0 | 2021-01-05 | 2025-12-31 | 1213 | -0.158    | 0.789      | -0.200 | 0.841   | -0.076      |
| ZN.v.0 | 2021-01-05 | 2025-12-31 | 1221 | 2.688     | 0.529      | 5.084  | p<0.001 | 2.333       |
| 6E.v.0 | 2021-01-05 | 2025-12-31 | 1228 | 0.497     | 0.393      | 1.266  | 0.206   | 0.111       |

Only ZN continues to show a positive and significant Eq.(7) relation in 2021-2025. ES, NQ, and GC exhibit OOS attenuation. CL and 6E have no significant positive relation in either the replication period or OOS and will be retained as null/control contracts.

## OOS R2: frozen_2020 vs expanding

| symbol | training_method | n_test | first_training_cutoff_date | last_training_cutoff_date | r2_oos_x100 | forecast_strategy_sharpe |
| ------ | --------------- | ------ | -------------------------- | ------------------------- | ----------- | ------------------------ |
| ES.v.0 | expanding       | 1224   | 2020-05-01                 | 2025-12-30                | -4.043      | 0.226                    |
| ES.v.0 | frozen_2020     | 1224   | 2020-05-01                 | 2020-05-01                | -6.161      | 0.111                    |
| NQ.v.0 | expanding       | 1224   | 2020-05-01                 | 2025-12-30                | -2.747      | -0.203                   |
| NQ.v.0 | frozen_2020     | 1224   | 2020-05-01                 | 2020-05-01                | -4.737      | -0.111                   |
| GC.v.0 | expanding       | 1226   | 2020-05-01                 | 2025-12-30                | -1.430      | 0.414                    |
| GC.v.0 | frozen_2020     | 1226   | 2020-05-01                 | 2020-05-01                | -2.116      | 0.267                    |
| CL.v.0 | expanding       | 1213   | 2020-05-01                 | 2025-12-30                | -2.421      | -0.338                   |
| CL.v.0 | frozen_2020     | 1213   | 2020-05-01                 | 2020-05-01                | -3.090      | -0.262                   |
| ZN.v.0 | expanding       | 1221   | 2020-05-01                 | 2025-12-30                | 2.271       | 2.028                    |
| ZN.v.0 | frozen_2020     | 1221   | 2020-05-01                 | 2020-05-01                | 2.261       | 1.819                    |
| 6E.v.0 | expanding       | 1228   | 2020-05-01                 | 2025-12-30                | -0.072      | -0.516                   |
| 6E.v.0 | frozen_2020     | 1228   | 2020-05-01                 | 2020-05-01                | -0.113      | -0.073                   |

## Eq.(7) Period-Difference Tests

| symbol | beta_replication_x100 | beta_oos_implied_x100 | beta_oos_minus_replication_x100 | difference_t_hac | difference_p_hac | difference_ci_low_x100 | difference_ci_high_x100 |
| ------ | --------------------- | --------------------- | ------------------------------- | ---------------- | ---------------- | ---------------------- | ----------------------- |
| ES.v.0 | 6.137                 | -0.124                | -6.262                          | -2.473           | 0.013            | -11.226                | -1.298                  |
| NQ.v.0 | 4.886                 | 0.150                 | -4.735                          | -2.010           | 0.045            | -9.355                 | -0.115                  |
| GC.v.0 | 2.408                 | 0.516                 | -1.892                          | -2.479           | 0.013            | -3.388                 | -0.396                  |
| CL.v.0 | -3.885                | -0.158                | 3.727                           | 0.566            | 0.572            | -9.189                 | 16.643                  |
| ZN.v.0 | 2.037                 | 2.688                 | 0.651                           | 0.790            | 0.429            | -0.964                 | 2.266                   |
| 6E.v.0 | -0.129                | 0.497                 | 0.626                           | 1.023            | 0.306            | -0.574                 | 1.827                   |

## ZN Executable Strategy Cost Table

The ZN table uses `r_LH_executable`: the signal is formed at the close-minus-30 boundary and entry uses the next bar open. The 0/1/2/3 tick scenarios are total round-trip costs per completed trade, not separately charged again at entry and exit; the one-way cost is half the round-trip cost.

ZN tick size is 0.015625 price points and tick value is $15.625 per contract, following CME 10-Year Treasury Note futures contract specifications. The cost rule is `net_return_t = gross_return_t - round_trip_ticks * tick_size / entry_price_t`.

| sample      | round_trip_tick_cost | one_way_tick_cost | round_trip_cost_usd_per_contract | one_way_cost_usd_per_contract | n_trades | avg_gross_return_bp | avg_net_return_bp | annualized_return_pct | annualized_volatility_pct | sharpe | max_drawdown_pct | cumulative_net_return_pct |
| ----------- | -------------------- | ----------------- | -------------------------------- | ----------------------------- | -------- | ------------------- | ----------------- | --------------------- | ------------------------- | ------ | ---------------- | ------------------------- |
| replication | 0                    | 0.000             | 0.000                            | 0.000                         | 2379     | 0.314               | 0.314             | 0.790                 | 0.975                     | 0.810  | -2.783           | 7.696                     |
| replication | 1                    | 0.500             | 15.625                           | 7.812                         | 2379     | 0.314               | -0.920            | -2.318                | 0.975                     | -2.378 | -20.983          | -19.692                   |
| replication | 2                    | 1.000             | 31.250                           | 15.625                        | 2379     | 0.314               | -2.153            | -5.426                | 0.975                     | -5.566 | -40.248          | -40.118                   |
| replication | 3                    | 1.500             | 46.875                           | 23.438                        | 2379     | 0.314               | -3.387            | -8.535                | 0.975                     | -8.754 | -55.355          | -55.350                   |
| oos         | 0                    | 0.000             | 0.000                            | 0.000                         | 1221     | 0.909               | 0.909             | 2.290                 | 1.046                     | 2.188  | -1.172           | 11.703                    |
| oos         | 1                    | 0.500             | 15.625                           | 7.812                         | 1221     | 0.909               | -0.432            | -1.089                | 1.046                     | -1.041 | -5.266           | -5.165                    |
| oos         | 2                    | 1.000             | 31.250                           | 15.625                        | 1221     | 0.909               | -1.773            | -4.468                | 1.046                     | -4.272 | -19.516          | -19.488                   |
| oos         | 3                    | 1.500             | 46.875                           | 23.438                        | 1221     | 0.909               | -3.114            | -7.847                | 1.046                     | -7.503 | -31.637          | -31.649                   |

## ZN Break-Even Round-Trip Tick Cost

`c* = mean(gross_return) / (tick_size * mean(1 / entry_price))`, where `c*` is the maximum total round-trip tick cost per completed trade that sets the average net return to zero.

| sample      | n_trades | avg_gross_return_bp | break_even_round_trip_ticks | break_even_one_way_ticks | break_even_round_trip_usd_per_contract | break_even_one_way_usd_per_contract |
| ----------- | -------- | ------------------- | --------------------------- | ------------------------ | -------------------------------------- | ----------------------------------- |
| replication | 2379     | 0.314               | 0.254                       | 0.127                    | 3.972                                  | 1.986                               |
| oos         | 1221     | 0.909               | 0.678                       | 0.339                    | 10.589                                 | 5.295                               |

## Frozen Conclusions

- All six contracts, ES, NQ, GC, CL, ZN, and 6E, have complete single-contract baseline replications.
- ES, NQ, GC, and ZN replicate positive and significant Eq.(7) relations in the paper-overlap sample.
- CL and 6E are insignificant at the single-contract level, consistent with the paper's appendix-level single-contract evidence, and remain control contracts.
- Only ZN remains significant in the 2021-2025 OOS period.
- ES, NQ, and GC show statistically significant OOS attenuation.
- Statistical significance is not the same as tradeability after costs; ZN remains highly sensitive to tick costs.