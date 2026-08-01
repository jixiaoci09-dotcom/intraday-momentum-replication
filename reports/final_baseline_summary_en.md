# Intraday Momentum Replication Results

This project replicates the main futures-market intraday momentum result from Baltussen, Da, Lammers, and Martens, "Hedging Demand and Market Intraday Momentum." The sample covers six CME continuous futures contracts: ES, NQ, GC, CL, ZN, and 6E.

The main question is whether the return over most of the trading day helps explain the return over the final half hour. To see whether the paper result also appears after the original sample period, I split the data into two parts:

- Paper replication period: June 2010 to May 1, 2020
- Out-of-sample period: January 1, 2021 to December 31, 2025

The period from May 2020 through the end of 2020 is left out of the main comparison so that the replication period and the later out-of-sample test stay clearly separated.

## 1. Method

For each futures contract, I use the contract's main trading window to collect several key intraday prices: the open, 30 minutes after the open, one hour before the close, 30 minutes before the close, and the close. These prices are then used to calculate intraday return variables.

The main specification is Eq.(7) from the paper:

```text
r_LH = alpha + beta * r_ROD + error
```

where:

- `r_ROD` is the return from the previous trading day's close to 30 minutes before the current close;
- `r_LH` is the return over the final half hour;
- `beta` measures the relationship between the earlier intraday move and the final-half-hour move.

If `beta` is positive and statistically significant, then days with positive earlier returns tend to continue upward in the final half hour, and days with negative earlier returns tend to continue downward. This is the intraday momentum pattern studied in the paper.

## 2. Paper Replication Period

The table below reports Eq.(7) results for the six contracts during the paper replication period. `beta_x100` is the regression coefficient multiplied by 100 to make the numbers easier to read.

| symbol | start      | end        | n    | beta_x100 | t      | p       |
| ------ | ---------- | ---------- | ---- | --------- | ------ | ------- |
| ES.v.0 | 2010-06-08 | 2020-05-01 | 2424 | 6.137     | 2.649  | 0.008   |
| NQ.v.0 | 2010-06-08 | 2020-05-01 | 2424 | 4.886     | 2.235  | 0.025   |
| GC.v.0 | 2010-06-08 | 2020-05-01 | 2396 | 2.408     | 4.483  | p<0.001 |
| CL.v.0 | 2010-06-08 | 2020-05-01 | 2345 | -3.885    | -0.594 | 0.552   |
| ZN.v.0 | 2010-06-08 | 2020-05-01 | 2379 | 2.037     | 3.236  | 0.001   |
| 6E.v.0 | 2010-06-08 | 2020-05-01 | 2398 | -0.129    | -0.278 | 0.781   |

ES, NQ, GC, and ZN have positive and statistically significant coefficients in the replication period. This suggests that these contracts show a clear intraday momentum relation during the period that overlaps with the paper.

CL and 6E are not significant at the single-contract level. I treat them as comparison contracts rather than simple replication failures. Different futures markets have different trading hours, liquidity, and market structure, so insignificant results for some individual contracts are not surprising.

## 3. 2021-2025 Out-of-Sample Results

I then test whether the same relationship appears in the later 2021-2025 sample.

| symbol | start      | end        | n    | beta_x100 | t      | p       |
| ------ | ---------- | ---------- | ---- | --------- | ------ | ------- |
| ES.v.0 | 2021-01-05 | 2025-12-31 | 1224 | -0.124    | -0.119 | 0.906   |
| NQ.v.0 | 2021-01-05 | 2025-12-31 | 1224 | 0.150     | 0.168  | 0.866   |
| GC.v.0 | 2021-01-05 | 2025-12-31 | 1226 | 0.516     | 0.966  | 0.334   |
| CL.v.0 | 2021-01-05 | 2025-12-31 | 1213 | -0.158    | -0.200 | 0.841   |
| ZN.v.0 | 2021-01-05 | 2025-12-31 | 1221 | 2.688     | 5.084  | p<0.001 |
| 6E.v.0 | 2021-01-05 | 2025-12-31 | 1228 | 0.497     | 1.266  | 0.206   |

The out-of-sample results are different from the replication-period results. In 2021-2025, only ZN continues to show a significant positive relationship. ES, NQ, and GC are significant in the replication period but weaken in the later sample. CL and 6E are not significantly positive in either period.

This suggests that intraday momentum is not stable across all contracts and all time periods. In this sample, ZN is the most persistent result, while equity-index futures and gold show weaker out-of-sample performance.

## 4. Out-of-Sample Prediction

I also compare two simple out-of-sample prediction approaches:

- Fixed training sample: estimate the model using only the paper replication period, then predict 2021-2025;
- Expanding training sample: re-estimate the model each prediction day using all data available up to that point.

Based on OOS R2 and the directional forecast strategy, most contracts have weak out-of-sample explanatory power. ZN is the main exception: it has positive OOS R2 under both training approaches and stronger forecast-strategy performance than the other contracts.

| symbol | training_method | n_test | r2_oos_x100 | forecast_strategy_sharpe |
| ------ | --------------- | ------ | ----------- | ------------------------ |
| ES.v.0 | expanding       | 1224   | -4.043      | 0.226                    |
| ES.v.0 | fixed_sample    | 1224   | -6.161      | 0.111                    |
| NQ.v.0 | expanding       | 1224   | -2.747      | -0.203                   |
| NQ.v.0 | fixed_sample    | 1224   | -4.737      | -0.111                   |
| GC.v.0 | expanding       | 1226   | -1.430      | 0.414                    |
| GC.v.0 | fixed_sample    | 1226   | -2.116      | 0.267                    |
| CL.v.0 | expanding       | 1213   | -2.421      | -0.338                   |
| CL.v.0 | fixed_sample    | 1213   | -3.090      | -0.262                   |
| ZN.v.0 | expanding       | 1221   | 2.271       | 2.028                    |
| ZN.v.0 | fixed_sample    | 1221   | 2.261       | 1.819                    |
| 6E.v.0 | expanding       | 1228   | -0.072      | -0.516                   |
| 6E.v.0 | fixed_sample    | 1228   | -0.113      | -0.073                   |

## 5. Transaction Cost Check

Statistical significance does not mean that the pattern can be traded directly. To get a rough sense of transaction costs, I focus on ZN, which has the strongest out-of-sample result.

The simple strategy is: go long during the final half hour when `r_ROD` is positive, and go short during the final half hour when `r_ROD` is negative. To make the execution assumption more realistic, the entry price uses the next one-minute bar open after the signal is formed.

| sample      | round_trip_tick_cost | n_trades | avg_gross_return_bp | avg_net_return_bp | sharpe | cumulative_net_return_pct |
| ----------- | -------------------- | -------- | ------------------- | ----------------- | ------ | ------------------------- |
| replication | 0                    | 2379     | 0.314               | 0.314             | 0.810  | 7.696                     |
| replication | 1                    | 2379     | 0.314               | -0.920            | -2.378 | -19.692                   |
| oos         | 0                    | 1221     | 0.909               | 0.909             | 2.188  | 11.703                    |
| oos         | 1                    | 1221     | 0.909               | -0.432            | -1.041 | -5.165                    |

The result shows that even though the ZN statistical relationship is strong, transaction costs matter a lot. With a 1-tick round-trip cost, the average net return falls sharply and becomes negative. Therefore, I interpret this mainly as a statistical replication result, not as evidence that the strategy is directly tradable.

## 6. Data Processing Notes

The main data-processing choices are:

- Each contract uses a trading window that fits its own market;
- Timestamps are handled in New York time;
- Holidays, early-close days, and days with missing key prices are excluded from the main sample;
- Around continuous-contract rolls, days are excluded when the previous close and current-day prices come from different underlying contracts;
- Raw Databento data is not uploaded to GitHub. The repository only keeps code, data notes, and result tables.

These choices reduce the sample size, but they help avoid obvious inconsistencies in the return calculations.

## 7. Summary

The main findings are:

- All six CME futures contracts are included in the single-contract replication.
- During the paper replication period, ES, NQ, GC, and ZN have positive and significant Eq.(7) results.
- CL and 6E are not significant at the single-contract level and are better interpreted as comparison contracts.
- In the 2021-2025 out-of-sample period, only ZN remains significantly positive.
- Most contracts have weak out-of-sample prediction performance, so the intraday momentum relationship is not very stable.
- Even when the statistical relationship is significant, transaction costs can remove the apparent trading profitability.

Overall, the intraday momentum pattern can be replicated for some futures contracts, but it is not equally stable across the later out-of-sample period.