# v0 vs boundary_corrected_v1

旧结果位于 `reports/archive/invalid_boundary_v0/`，仅用于说明边界修复影响。旧结果无效，不用于最终研究结论。

比较口径：Eq.(7) replication beta、t、p、adjusted R2；OOS R2 使用新口径中的 `frozen_2020` 与旧固定切分结果比较；Sharpe 使用 replication `timing_rROD` 毛收益、论文统计价格口径。

| symbol | metric_basis                                                                      | v0_beta_x100 | v1_beta_x100 | v0_t   | v1_t   | v0_p  | v1_p  | v0_adj_r2_x100 | v1_adj_r2_x100 | v0_oos_r2_x100 | v1_oos_r2_x100 | v0_sharpe | v1_sharpe | v0_n | v1_n |
| ------ | --------------------------------------------------------------------------------- | ------------ | ------------ | ------ | ------ | ----- | ----- | -------------- | -------------- | -------------- | -------------- | --------- | --------- | ---- | ---- |
| ES.v.0 | Eq7 replication; OOS R2 frozen_2020; strategy timing_rROD gross paper_statistical | 4.215        | 6.137        | 2.323  | 2.649  | 0.020 | 0.008 | 2.106          | 4.021          | -3.792         | -6.161         | 0.819     | 0.989     | 2443 | 2424 |
| NQ.v.0 | Eq7 replication; OOS R2 frozen_2020; strategy timing_rROD gross paper_statistical | 3.185        | 4.886        | 1.933  | 2.235  | 0.053 | 0.025 | 1.291          | 2.855          | -2.403         | -4.737         | 0.665     | 0.886     | 2443 | 2424 |
| GC.v.0 | Eq7 replication; OOS R2 frozen_2020; strategy timing_rROD gross paper_statistical | 1.451        | 2.408        | 2.727  | 4.483  | 0.006 | 0.000 | 0.829          | 2.245          | -0.700         | -2.116         | 0.351     | 1.035     | 2421 | 2396 |
| CL.v.0 | Eq7 replication; OOS R2 frozen_2020; strategy timing_rROD gross paper_statistical | -6.755       | -3.885       | -0.867 | -0.594 | 0.386 | 0.552 | 4.411          | 1.562          | -10.695        | -3.090         | 0.217     | 0.490     | 2347 | 2345 |
| ZN.v.0 | Eq7 replication; OOS R2 frozen_2020; strategy timing_rROD gross paper_statistical | 1.669        | 2.037        | 2.682  | 3.236  | 0.007 | 0.001 | 0.663          | 0.943          | 0.806          | 2.261          | 0.646     | 0.832     | 2421 | 2379 |
| 6E.v.0 | Eq7 replication; OOS R2 frozen_2020; strategy timing_rROD gross paper_statistical | 0.183        | -0.129       | 0.492  | -0.278 | 0.623 | 0.781 | -0.030         | -0.036         | -0.031         | -0.113         | 0.034     | -0.248    | 2430 | 2398 |