# 最终基线摘要：boundary_corrected_v1

本摘要冻结六个 CME 连续期货品种 ES、NQ、GC、CL、ZN、6E 的单合约基线复现结果。所有主结果来自 `pipeline_version=boundary_corrected_v1`，使用各品种独立交易时段、纽约时区、夏令时处理、非开盘边界 `T-1` 分钟 bar close、session open 的 `T` 时刻 bar open、同合约前收盘对齐、提前收盘删除和缺失精确边界删除。

严格论文重叠期为首个有效交易日至 `2020-05-01`；发表后样本外为 `2021-01-01` 至 `2025-12-31`。本轮 expanding OOS 从严格论文期训练集出发，只追加已经过去的 2021-2025 OOS 观测；`2020-05-02` 至 `2020-12-31` 不计入严格论文期，也不作为本轮 expanding 训练数据。

## 论文期 Eq.(7)

| symbol | start      | end        | n    | beta_x100 | nw_se_x100 | t      | p       | adj_r2_x100 |
| ------ | ---------- | ---------- | ---- | --------- | ---------- | ------ | ------- | ----------- |
| ES.v.0 | 2010-06-08 | 2020-05-01 | 2424 | 6.137     | 2.317      | 2.649  | 0.008   | 4.021       |
| NQ.v.0 | 2010-06-08 | 2020-05-01 | 2424 | 4.886     | 2.186      | 2.235  | 0.025   | 2.855       |
| GC.v.0 | 2010-06-08 | 2020-05-01 | 2396 | 2.408     | 0.537      | 4.483  | p<0.001 | 2.245       |
| CL.v.0 | 2010-06-08 | 2020-05-01 | 2345 | -3.885    | 6.539      | -0.594 | 0.552   | 1.562       |
| ZN.v.0 | 2010-06-08 | 2020-05-01 | 2379 | 2.037     | 0.629      | 3.236  | 0.001   | 0.943       |
| 6E.v.0 | 2010-06-08 | 2020-05-01 | 2398 | -0.129    | 0.465      | -0.278 | 0.781   | -0.036      |

ES、NQ、GC、ZN 在论文重叠期复现出显著正向 Eq.(7) 关系。CL 和 6E 的单品种 Eq.(7) 不显著，这与论文附录中的单品种结果一致，因此不应写成复现失败。CL 和 6E 也不能直接拿来与论文的能源类、货币类 pooled regression 比较。

## 2021-2025 OOS Eq.(7)

| symbol | start      | end        | n    | beta_x100 | nw_se_x100 | t      | p       | adj_r2_x100 |
| ------ | ---------- | ---------- | ---- | --------- | ---------- | ------ | ------- | ----------- |
| ES.v.0 | 2021-01-05 | 2025-12-31 | 1224 | -0.124    | 1.050      | -0.119 | 0.906   | -0.079      |
| NQ.v.0 | 2021-01-05 | 2025-12-31 | 1224 | 0.150     | 0.894      | 0.168  | 0.866   | -0.077      |
| GC.v.0 | 2021-01-05 | 2025-12-31 | 1226 | 0.516     | 0.534      | 0.966  | 0.334   | 0.090       |
| CL.v.0 | 2021-01-05 | 2025-12-31 | 1213 | -0.158    | 0.789      | -0.200 | 0.841   | -0.076      |
| ZN.v.0 | 2021-01-05 | 2025-12-31 | 1221 | 2.688     | 0.529      | 5.084  | p<0.001 | 2.333       |
| 6E.v.0 | 2021-01-05 | 2025-12-31 | 1228 | 0.497     | 0.393      | 1.266  | 0.206   | 0.111       |

2021-2025 年只有 ZN 的 Eq.(7) 关系显著延续。ES、NQ、GC 出现样本外衰减；CL、6E 在复现期和样本外均没有显著正向关系，后续扩展中作为 null/control contracts。

## OOS R2：frozen_2020 vs expanding

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

## Eq.(7) 前后系数差异

| symbol | beta_replication_x100 | beta_oos_implied_x100 | beta_oos_minus_replication_x100 | difference_t_hac | difference_p_hac | difference_ci_low_x100 | difference_ci_high_x100 |
| ------ | --------------------- | --------------------- | ------------------------------- | ---------------- | ---------------- | ---------------------- | ----------------------- |
| ES.v.0 | 6.137                 | -0.124                | -6.262                          | -2.473           | 0.013            | -11.226                | -1.298                  |
| NQ.v.0 | 4.886                 | 0.150                 | -4.735                          | -2.010           | 0.045            | -9.355                 | -0.115                  |
| GC.v.0 | 2.408                 | 0.516                 | -1.892                          | -2.479           | 0.013            | -3.388                 | -0.396                  |
| CL.v.0 | -3.885                | -0.158                | 3.727                           | 0.566            | 0.572            | -9.189                 | 16.643                  |
| ZN.v.0 | 2.037                 | 2.688                 | 0.651                           | 0.790            | 0.429            | -0.964                 | 2.266                   |
| 6E.v.0 | -0.129                | 0.497                 | 0.626                           | 1.023            | 0.306            | -0.574                 | 1.827                   |

## ZN 可执行策略成本表

成本表使用 `r_LH_executable`：信号在 close-30 边界形成，入场使用下一根 bar open。0/1/2/3 tick 是每次完整往返交易的总成本，不在入场和出场重复扣除；对应单边成本为往返成本的一半。

ZN tick size = 0.015625 price points，tick value = $15.625 per contract。Tick value 依据 CME 10-Year Treasury Note futures contract specifications。成本扣除公式：`net_return_t = gross_return_t - round_trip_ticks * tick_size / entry_price_t`。

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

## ZN break-even round-trip tick cost

Break-even 公式：`c* = mean(gross_return) / (tick_size * mean(1 / entry_price))`。`c*` 是每次完整往返交易可承受的总 tick 成本；单边 tick 成本为 `c*/2`。

| sample      | n_trades | avg_gross_return_bp | break_even_round_trip_ticks | break_even_one_way_ticks | break_even_round_trip_usd_per_contract | break_even_one_way_usd_per_contract |
| ----------- | -------- | ------------------- | --------------------------- | ------------------------ | -------------------------------------- | ----------------------------------- |
| replication | 2379     | 0.314               | 0.254                       | 0.127                    | 3.972                                  | 1.986                               |
| oos         | 1221     | 0.909               | 0.678                       | 0.339                    | 10.589                                 | 5.295                               |

## 数据删除统计

| symbol | rows_total | rows_included | rows_excluded | replication_included | oos_included | excluded_by_reason                                                                                                                                                                |
| ------ | ---------- | ------------- | ------------- | -------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ES.v.0 | 3853       | 3667          | 186           | 2443                 | 1224         | missing_exact_boundary_source_on_regular_day=7; missing_previous_close=2; nyse_closed=85; nyse_early_close=32; previous_close_cross_instrument=60                                 |
| NQ.v.0 | 3853       | 3667          | 186           | 2443                 | 1224         | missing_exact_boundary_source_on_regular_day=7; missing_previous_close=2; nyse_closed=85; nyse_early_close=32; previous_close_cross_instrument=60                                 |
| GC.v.0 | 3869       | 3640          | 229           | 2414                 | 1226         | calendar_early_close_before_effective_close=67; missing_exact_boundary_source_on_calendar_day=85; missing_previous_close=2; previous_close_cross_instrument=75                    |
| CL.v.0 | 3869       | 3576          | 293           | 2363                 | 1213         | calendar_early_close_before_effective_close=79; missing_exact_boundary_source_on_calendar_day=32; missing_previous_close=2; previous_close_cross_instrument=180                   |
| ZN.v.0 | 3869       | 3618          | 251           | 2397                 | 1221         | calendar_early_close_before_effective_close=117; missing_exact_boundary_source_on_calendar_day=73; missing_previous_close=2; previous_close_cross_instrument=59                   |
| 6E.v.0 | 3872       | 3645          | 227           | 2417                 | 1228         | calendar_closed=2; calendar_early_close_before_effective_close=92; missing_exact_boundary_source_on_calendar_day=73; missing_previous_close=2; previous_close_cross_instrument=58 |

## 冻结结论

- 六个品种 ES、NQ、GC、CL、ZN、6E 均完成单合约复现。
- ES、NQ、GC、ZN 在论文重叠期复现出显著正向 Eq.(7) 关系。
- CL、6E 在单品种层面不显著，与论文附录的单品种结果一致，应作为对照品种保留。
- 2021-2025 年只有 ZN 的 Eq.(7) 关系显著延续。
- ES、NQ、GC 出现统计显著的样本外衰减。
- 统计显著不等于扣除成本后可交易；ZN 虽有统计延续，但可执行策略对 tick 成本高度敏感。