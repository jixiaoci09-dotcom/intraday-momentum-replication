# Pre-rerun Integrity Audit

Pipeline target version: `boundary_corrected_v1`

This audit reads local Databento raw `OHLCV-1m` and `definition` zip files directly. It does not read processed daily research tables and does not run regressions or market-state extensions.

## Overall Result

Recommendation: **ready to start the full rerun**, but the first step must be regenerating corrected daily tables. Regression scripts now refuse old daily parquet files unless `pipeline_version == boundary_corrected_v1`.

## Blocking FAIL

None.

## PASS/FAIL Items

| item                                                          | symbol | status | severity | detail                                                                                                                                                                                                  |
| ------------------------------------------------------------- | ------ | ------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| raw_duplicate_symbol_instrument_ts_event                      | ES.v.0 | PASS   |          | duplicate_rows=0; raw_rows=5231196                                                                                                                                                                      |
| raw_nonpositive_nan_inf_prices                                | ES.v.0 | PASS   |          | bad_price_rows=0                                                                                                                                                                                        |
| roll_alignment_no_cross_contract_returns                      | ES.v.0 | PASS   |          | mismatch_dates=61; included_mismatches=0                                                                                                                                                                |
| previous_close_from_prior_available_trading_day               | ES.v.0 | PASS   |          | included_rows=3667; gaps_gt_1_day=761; non_prior_prev_rows=0                                                                                                                                            |
| missing_exact_boundaries_are_dropped                          | ES.v.0 | PASS   |          | missing_boundary_dates=1744; included_missing=0                                                                                                                                                         |
| early_closes_deleted_main_sample                              | ES.v.0 | PASS   |          | early_close_dates=32; included_early_closes=0                                                                                                                                                           |
| rod_identity_error_lt_1e-10                                   | ES.v.0 | PASS   |          | max_error=4.441e-16; failures=0                                                                                                                                                                         |
| oos_fixed_split_no_future_training_data                       | ES.v.0 | PASS   |          | train_end=2020-05-29; oos_rows=1224; oos_rows_not_after_train_end=0                                                                                                                                     |
| strategy_statistical_and_executable_lh_separated              | ES.v.0 | PASS   |          | has_LH=True; has_LH_executable=True                                                                                                                                                                     |
| raw_duplicate_symbol_instrument_ts_event                      | NQ.v.0 | PASS   |          | duplicate_rows=0; raw_rows=5056471                                                                                                                                                                      |
| raw_nonpositive_nan_inf_prices                                | NQ.v.0 | PASS   |          | bad_price_rows=0                                                                                                                                                                                        |
| roll_alignment_no_cross_contract_returns                      | NQ.v.0 | PASS   |          | mismatch_dates=61; included_mismatches=0                                                                                                                                                                |
| previous_close_from_prior_available_trading_day               | NQ.v.0 | PASS   |          | included_rows=3667; gaps_gt_1_day=764; non_prior_prev_rows=0                                                                                                                                            |
| missing_exact_boundaries_are_dropped                          | NQ.v.0 | PASS   |          | missing_boundary_dates=1744; included_missing=0                                                                                                                                                         |
| early_closes_deleted_main_sample                              | NQ.v.0 | PASS   |          | early_close_dates=32; included_early_closes=0                                                                                                                                                           |
| rod_identity_error_lt_1e-10                                   | NQ.v.0 | PASS   |          | max_error=4.441e-16; failures=0                                                                                                                                                                         |
| oos_fixed_split_no_future_training_data                       | NQ.v.0 | PASS   |          | train_end=2020-05-29; oos_rows=1224; oos_rows_not_after_train_end=0                                                                                                                                     |
| strategy_statistical_and_executable_lh_separated              | NQ.v.0 | PASS   |          | has_LH=True; has_LH_executable=True                                                                                                                                                                     |
| raw_duplicate_symbol_instrument_ts_event                      | GC.v.0 | PASS   |          | duplicate_rows=0; raw_rows=5187751                                                                                                                                                                      |
| raw_nonpositive_nan_inf_prices                                | GC.v.0 | PASS   |          | bad_price_rows=0                                                                                                                                                                                        |
| roll_alignment_no_cross_contract_returns                      | GC.v.0 | PASS   |          | mismatch_dates=77; included_mismatches=0                                                                                                                                                                |
| previous_close_from_prior_available_trading_day               | GC.v.0 | PASS   |          | included_rows=3637; gaps_gt_1_day=765; non_prior_prev_rows=0                                                                                                                                            |
| missing_exact_boundaries_are_dropped                          | GC.v.0 | PASS   |          | missing_boundary_dates=1756; included_missing=0                                                                                                                                                         |
| early_closes_deleted_main_sample                              | GC.v.0 | PASS   |          | early_close_dates=70; included_early_closes=0                                                                                                                                                           |
| rod_identity_error_lt_1e-10                                   | GC.v.0 | PASS   |          | max_error=4.441e-16; failures=0                                                                                                                                                                         |
| oos_fixed_split_no_future_training_data                       | GC.v.0 | PASS   |          | train_end=2020-05-28; oos_rows=1223; oos_rows_not_after_train_end=0                                                                                                                                     |
| strategy_statistical_and_executable_lh_separated              | GC.v.0 | PASS   |          | has_LH=True; has_LH_executable=True                                                                                                                                                                     |
| raw_duplicate_symbol_instrument_ts_event                      | CL.v.0 | PASS   |          | duplicate_rows=0; raw_rows=5171606                                                                                                                                                                      |
| raw_nonpositive_nan_inf_prices                                | CL.v.0 | PASS   |          | bad_price_rows=0                                                                                                                                                                                        |
| roll_alignment_no_cross_contract_returns                      | CL.v.0 | PASS   |          | mismatch_dates=190; included_mismatches=0                                                                                                                                                               |
| previous_close_from_prior_available_trading_day               | CL.v.0 | PASS   |          | included_rows=3570; gaps_gt_1_day=702; non_prior_prev_rows=0                                                                                                                                            |
| missing_exact_boundaries_are_dropped                          | CL.v.0 | PASS   |          | missing_boundary_dates=1715; included_missing=0                                                                                                                                                         |
| early_closes_deleted_main_sample                              | CL.v.0 | PASS   |          | early_close_dates=85; included_early_closes=0                                                                                                                                                           |
| rod_identity_error_lt_1e-10                                   | CL.v.0 | PASS   |          | max_error=4.441e-16; failures=0                                                                                                                                                                         |
| oos_fixed_split_no_future_training_data                       | CL.v.0 | PASS   |          | train_end=2020-05-29; oos_rows=1207; oos_rows_not_after_train_end=0                                                                                                                                     |
| strategy_statistical_and_executable_lh_separated              | CL.v.0 | PASS   |          | has_LH=True; has_LH_executable=True                                                                                                                                                                     |
| raw_duplicate_symbol_instrument_ts_event                      | ZN.v.0 | PASS   |          | duplicate_rows=0; raw_rows=4799435                                                                                                                                                                      |
| raw_nonpositive_nan_inf_prices                                | ZN.v.0 | PASS   |          | bad_price_rows=0                                                                                                                                                                                        |
| roll_alignment_no_cross_contract_returns                      | ZN.v.0 | PASS   |          | mismatch_dates=68; included_mismatches=0                                                                                                                                                                |
| previous_close_from_prior_available_trading_day               | ZN.v.0 | PASS   |          | included_rows=3618; gaps_gt_1_day=763; non_prior_prev_rows=0                                                                                                                                            |
| missing_exact_boundaries_are_dropped                          | ZN.v.0 | PASS   |          | missing_boundary_dates=1794; included_missing=0                                                                                                                                                         |
| early_closes_deleted_main_sample                              | ZN.v.0 | PASS   |          | early_close_dates=117; included_early_closes=0                                                                                                                                                          |
| rod_identity_error_lt_1e-10                                   | ZN.v.0 | PASS   |          | max_error=4.441e-16; failures=0                                                                                                                                                                         |
| oos_fixed_split_no_future_training_data                       | ZN.v.0 | PASS   |          | train_end=2020-05-28; oos_rows=1221; oos_rows_not_after_train_end=0                                                                                                                                     |
| strategy_statistical_and_executable_lh_separated              | ZN.v.0 | PASS   |          | has_LH=True; has_LH_executable=True                                                                                                                                                                     |
| raw_duplicate_symbol_instrument_ts_event                      | 6E.v.0 | PASS   |          | duplicate_rows=0; raw_rows=5142776                                                                                                                                                                      |
| raw_nonpositive_nan_inf_prices                                | 6E.v.0 | PASS   |          | bad_price_rows=0                                                                                                                                                                                        |
| roll_alignment_no_cross_contract_returns                      | 6E.v.0 | PASS   |          | mismatch_dates=60; included_mismatches=0                                                                                                                                                                |
| previous_close_from_prior_available_trading_day               | 6E.v.0 | PASS   |          | included_rows=3644; gaps_gt_1_day=718; non_prior_prev_rows=0                                                                                                                                            |
| missing_exact_boundaries_are_dropped                          | 6E.v.0 | PASS   |          | missing_boundary_dates=1768; included_missing=0                                                                                                                                                         |
| early_closes_deleted_main_sample                              | 6E.v.0 | PASS   |          | early_close_dates=93; included_early_closes=0                                                                                                                                                           |
| rod_identity_error_lt_1e-10                                   | 6E.v.0 | PASS   |          | max_error=4.441e-16; failures=0                                                                                                                                                                         |
| oos_fixed_split_no_future_training_data                       | 6E.v.0 | PASS   |          | train_end=2020-05-29; oos_rows=1227; oos_rows_not_after_train_end=0                                                                                                                                     |
| strategy_statistical_and_executable_lh_separated              | 6E.v.0 | PASS   |          | has_LH=True; has_LH_executable=True                                                                                                                                                                     |
| old_results_archived_invalid_boundary_v0                      | ALL    | PASS   |          | archive_readme=True; csv_tables=30; parquet_local_archive=6; invalid_boundary_v0 archive explicitly marks old results invalid                                                                           |
| regression_script_daily_table_path                            | ALL    | PASS   |          | run_symbol_core_replication reads data/processed/{prefix}_daily_research_table.parquet                                                                                                                  |
| no_notebook_cache_inputs                                      | ALL    | PASS   |          | No notebook checkpoint inputs found                                                                                                                                                                     |
| pipeline_version_boundary_corrected_v1_in_new_outputs         | ALL    | PASS   |          | pipeline_version string present in build/regression scripts=True; future daily tables and summaries will include boundary_corrected_v1                                                                  |
| top_level_daily_tables_require_regeneration_before_regression | ALL    | PASS   |          | Existing top-level daily parquet files are old, but run_symbol_core_replication now fails closed unless pipeline_version == boundary_corrected_v1. Full rerun must start with daily-table regeneration. |
| america_new_york_trade_date_grouping                          | ES.v.0 | PASS   |          | boundary_rows_with_ny_date_mismatch=0                                                                                                                                                                   |
| america_new_york_trade_date_grouping                          | NQ.v.0 | PASS   |          | boundary_rows_with_ny_date_mismatch=0                                                                                                                                                                   |
| america_new_york_trade_date_grouping                          | GC.v.0 | PASS   |          | boundary_rows_with_ny_date_mismatch=0                                                                                                                                                                   |
| america_new_york_trade_date_grouping                          | CL.v.0 | PASS   |          | boundary_rows_with_ny_date_mismatch=0                                                                                                                                                                   |
| america_new_york_trade_date_grouping                          | ZN.v.0 | PASS   |          | boundary_rows_with_ny_date_mismatch=0                                                                                                                                                                   |
| america_new_york_trade_date_grouping                          | 6E.v.0 | PASS   |          | boundary_rows_with_ny_date_mismatch=0                                                                                                                                                                   |

## Non-blocking Warnings

| symbol | warning                                                                                                    |
| ------ | ---------------------------------------------------------------------------------------------------------- |
| ES.v.0 | roll mismatch dates dropped=61; early-close dates dropped=32; review top absolute ONFH/ROD/LH rows in CSV  |
| NQ.v.0 | roll mismatch dates dropped=61; early-close dates dropped=32; review top absolute ONFH/ROD/LH rows in CSV  |
| GC.v.0 | roll mismatch dates dropped=77; early-close dates dropped=70; review top absolute ONFH/ROD/LH rows in CSV  |
| CL.v.0 | roll mismatch dates dropped=190; early-close dates dropped=85; review top absolute ONFH/ROD/LH rows in CSV |
| ZN.v.0 | roll mismatch dates dropped=68; early-close dates dropped=117; review top absolute ONFH/ROD/LH rows in CSV |
| 6E.v.0 | roll mismatch dates dropped=60; early-close dates dropped=93; review top absolute ONFH/ROD/LH rows in CSV  |

## Need Manual Confirmation

| symbol | dates                                                                                                                                                                                                                                                             | reason                                               |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| ES.v.0 | 2011-08-08 ; 2011-08-09 ; 2011-08-11 ; 2011-08-18 ; 2011-09-21 ; 2011-09-22 ; 2011-10-04 ; 2011-11-30 ; 2015-08-24 ; 2015-08-25 ; 2018-02-05 ; 2018-02-08 ; 2018-12-27 ; 2020-02-27 ; 2020-03-02 ; 2020-03-06 ; 2020-03-09 ; 2020-03-10 ; 2020-03-11 ; 2020-03-12 | Top absolute ONFH/ROD/LH rows; no automatic deletion |
| NQ.v.0 | 2011-08-09 ; 2011-08-11 ; 2011-08-18 ; 2011-09-21 ; 2011-09-22 ; 2011-10-04 ; 2015-08-24 ; 2015-08-25 ; 2018-02-05 ; 2018-02-08 ; 2020-03-02 ; 2020-03-06 ; 2020-03-09 ; 2020-03-10 ; 2020-03-11 ; 2020-03-12 ; 2020-03-13 ; 2020-03-16 ; 2020-03-17 ; 2020-03-19 | Top absolute ONFH/ROD/LH rows; no automatic deletion |
| GC.v.0 | 2010-11-04 ; 2010-11-09 ; 2011-05-12 ; 2011-08-08 ; 2011-08-11 ; 2011-08-24 ; 2011-09-22 ; 2011-09-23 ; 2011-09-27 ; 2011-09-28 ; 2011-12-14 ; 2012-01-25 ; 2012-02-22 ; 2012-02-29 ; 2012-03-14 ; 2012-06-20 ; 2012-09-13 ; 2013-04-12 ; 2013-04-15 ; 2013-06-20 | Top absolute ONFH/ROD/LH rows; no automatic deletion |
| CL.v.0 | 2011-08-08 ; 2014-12-01 ; 2015-01-14 ; 2015-01-30 ; 2015-03-18 ; 2016-02-12 ; 2016-11-30 ; 2018-11-28 ; 2019-09-16 ; 2020-03-09 ; 2020-03-10 ; 2020-03-16 ; 2020-03-17 ; 2020-03-18 ; 2020-03-23 ; 2020-03-24 ; 2020-03-30 ; 2020-04-02 ; 2020-04-03 ; 2020-04-07 | Top absolute ONFH/ROD/LH rows; no automatic deletion |
| ZN.v.0 | 2010-09-21 ; 2010-11-04 ; 2010-12-07 ; 2010-12-14 ; 2011-08-08 ; 2011-08-09 ; 2011-11-01 ; 2011-11-28 ; 2013-06-19 ; 2013-07-05 ; 2013-09-18 ; 2014-12-17 ; 2016-06-24 ; 2019-05-01 ; 2020-03-03 ; 2020-03-09 ; 2020-03-10 ; 2020-03-12 ; 2020-03-13 ; 2020-03-16 | Top absolute ONFH/ROD/LH rows; no automatic deletion |
| 6E.v.0 | 2010-06-10 ; 2010-09-22 ; 2010-11-29 ; 2011-01-13 ; 2011-05-05 ; 2011-06-10 ; 2011-06-15 ; 2011-09-22 ; 2011-10-10 ; 2011-10-27 ; 2011-11-01 ; 2011-11-09 ; 2011-12-05 ; 2011-12-12 ; 2011-12-13 ; 2012-03-15 ; 2012-04-04 ; 2012-06-29 ; 2012-07-27 ; 2013-01-15 | Top absolute ONFH/ROD/LH rows; no automatic deletion |

## Roll Mismatches

| symbol | mismatch_dates | included_mismatches | handling         |
| ------ | -------------- | ------------------- | ---------------- |
| ES.v.0 | 61             | 0                   | drop_main_sample |
| NQ.v.0 | 61             | 0                   | drop_main_sample |
| GC.v.0 | 77             | 0                   | drop_main_sample |
| CL.v.0 | 190            | 0                   | drop_main_sample |
| ZN.v.0 | 68             | 0                   | drop_main_sample |
| 6E.v.0 | 60             | 0                   | drop_main_sample |

Sample mismatch rows; full list is in the CSV:

| symbol | trade_date | previous_trade_date | current_raw_symbol | previous_close_raw_symbol | include | handling         | drop_reason                                     |
| ------ | ---------- | ------------------- | ------------------ | ------------------------- | ------- | ---------------- | ----------------------------------------------- |
| ES.v.0 | 2021-03-15 | 2021-03-12          | ESM1               | ESH1                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2021-06-14 | 2021-06-11          | ESU1               | ESM1                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2021-09-13 | 2021-09-10          | ESZ1               | ESU1                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2021-12-13 | 2021-12-10          | ESH2               | ESZ1                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2022-03-14 | 2022-03-11          | ESM2               | ESH2                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2022-06-15 | 2022-06-14          | ESU2               | ESM2                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2022-09-14 | 2022-09-13          | ESZ2               | ESU2                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2022-12-14 | 2022-12-13          | ESH3               | ESZ2                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2023-03-15 | 2023-03-14          | ESM3               | ESH3                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2023-06-14 | 2023-06-13          | ESU3               | ESM3                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2023-09-13 | 2023-09-12          | ESZ3               | ESU3                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2023-12-13 | 2023-12-12          | ESH4               | ESZ3                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2024-03-13 | 2024-03-12          | ESM4               | ESH4                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2024-06-19 | 2024-06-18          | ESU4               | ESM4                      | False   | drop_main_sample | calendar_closed;previous_close_cross_instrument |
| ES.v.0 | 2024-06-20 | 2024-06-18          | ESU4               | ESM4                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2024-09-18 | 2024-09-17          | ESZ4               | ESU4                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2024-12-18 | 2024-12-17          | ESH5               | ESZ4                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2025-03-19 | 2025-03-18          | ESM5               | ESH5                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2025-06-18 | 2025-06-17          | ESU5               | ESM5                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2025-09-17 | 2025-09-16          | ESZ5               | ESU5                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2025-12-17 | 2025-12-16          | ESH6               | ESZ5                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2010-06-14 | 2010-06-11          | ESU0               | ESM0                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2010-09-13 | 2010-09-10          | ESZ0               | ESU0                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2010-12-13 | 2010-12-10          | ESH1               | ESZ0                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2011-03-14 | 2011-03-11          | ESM1               | ESH1                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2011-06-13 | 2011-06-10          | ESU1               | ESM1                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2011-09-12 | 2011-09-09          | ESZ1               | ESU1                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2011-12-12 | 2011-12-09          | ESH2               | ESZ1                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2012-03-13 | 2012-03-12          | ESM2               | ESH2                      | False   | drop_main_sample | previous_close_cross_instrument                 |
| ES.v.0 | 2012-06-11 | 2012-06-08          | ESU2               | ESM2                      | False   | drop_main_sample | previous_close_cross_instrument                 |

## Previous Trading Day Gaps

These gaps confirm the intended behavior is not `calendar date - 1`; weekends and holidays map to the prior available close.

| symbol | trade_date | previous_trade_date | gap_days | weekday |
| ------ | ---------- | ------------------- | -------- | ------- |
| ES.v.0 | 2021-01-11 | 2021-01-08          | 3.0      | Monday  |
| ES.v.0 | 2021-01-19 | 2021-01-15          | 4.0      | Tuesday |
| ES.v.0 | 2021-01-25 | 2021-01-22          | 3.0      | Monday  |
| ES.v.0 | 2021-02-01 | 2021-01-29          | 3.0      | Monday  |
| ES.v.0 | 2021-02-08 | 2021-02-05          | 3.0      | Monday  |
| ES.v.0 | 2021-02-16 | 2021-02-12          | 4.0      | Tuesday |
| ES.v.0 | 2021-02-22 | 2021-02-19          | 3.0      | Monday  |
| ES.v.0 | 2021-03-01 | 2021-02-26          | 3.0      | Monday  |
| ES.v.0 | 2021-03-08 | 2021-03-05          | 3.0      | Monday  |
| ES.v.0 | 2021-03-22 | 2021-03-19          | 3.0      | Monday  |
| ES.v.0 | 2021-03-29 | 2021-03-26          | 3.0      | Monday  |
| ES.v.0 | 2021-04-05 | 2021-04-01          | 4.0      | Monday  |
| ES.v.0 | 2021-04-12 | 2021-04-09          | 3.0      | Monday  |
| ES.v.0 | 2021-04-19 | 2021-04-16          | 3.0      | Monday  |
| ES.v.0 | 2021-04-26 | 2021-04-23          | 3.0      | Monday  |
| ES.v.0 | 2021-05-03 | 2021-04-30          | 3.0      | Monday  |
| ES.v.0 | 2021-05-10 | 2021-05-07          | 3.0      | Monday  |
| ES.v.0 | 2021-05-17 | 2021-05-14          | 3.0      | Monday  |
| ES.v.0 | 2021-05-24 | 2021-05-21          | 3.0      | Monday  |
| ES.v.0 | 2021-06-01 | 2021-05-28          | 4.0      | Tuesday |
| ES.v.0 | 2021-06-07 | 2021-06-04          | 3.0      | Monday  |
| ES.v.0 | 2021-06-21 | 2021-06-18          | 3.0      | Monday  |
| ES.v.0 | 2021-06-28 | 2021-06-25          | 3.0      | Monday  |
| ES.v.0 | 2021-07-06 | 2021-07-02          | 4.0      | Tuesday |
| ES.v.0 | 2021-07-12 | 2021-07-09          | 3.0      | Monday  |
| ES.v.0 | 2021-07-19 | 2021-07-16          | 3.0      | Monday  |
| ES.v.0 | 2021-07-26 | 2021-07-23          | 3.0      | Monday  |
| ES.v.0 | 2021-08-02 | 2021-07-30          | 3.0      | Monday  |
| ES.v.0 | 2021-08-09 | 2021-08-06          | 3.0      | Monday  |
| ES.v.0 | 2021-08-16 | 2021-08-13          | 3.0      | Monday  |
| ES.v.0 | 2021-08-23 | 2021-08-20          | 3.0      | Monday  |
| ES.v.0 | 2021-08-30 | 2021-08-27          | 3.0      | Monday  |
| ES.v.0 | 2021-09-07 | 2021-09-03          | 4.0      | Tuesday |
| ES.v.0 | 2021-09-20 | 2021-09-17          | 3.0      | Monday  |
| ES.v.0 | 2021-09-27 | 2021-09-24          | 3.0      | Monday  |
| ES.v.0 | 2021-10-04 | 2021-10-01          | 3.0      | Monday  |
| ES.v.0 | 2021-10-11 | 2021-10-08          | 3.0      | Monday  |
| ES.v.0 | 2021-10-18 | 2021-10-15          | 3.0      | Monday  |
| ES.v.0 | 2021-10-25 | 2021-10-22          | 3.0      | Monday  |
| ES.v.0 | 2021-11-01 | 2021-10-29          | 3.0      | Monday  |

## Early Closes

| symbol | early_close_dates | handling         |
| ------ | ----------------- | ---------------- |
| ES.v.0 | 32                | drop_main_sample |
| NQ.v.0 | 32                | drop_main_sample |
| GC.v.0 | 70                | drop_main_sample |
| CL.v.0 | 85                | drop_main_sample |
| ZN.v.0 | 117               | drop_main_sample |
| 6E.v.0 | 93                | drop_main_sample |

Sample early close rows; full list is in the CSV:

| symbol | trade_date | calendar_close_clock | handling         |
| ------ | ---------- | -------------------- | ---------------- |
| ES.v.0 | 2010-11-26 | 13:00                | drop_main_sample |
| ES.v.0 | 2011-11-25 | 13:00                | drop_main_sample |
| ES.v.0 | 2012-07-03 | 13:00                | drop_main_sample |
| ES.v.0 | 2012-11-23 | 13:00                | drop_main_sample |
| ES.v.0 | 2012-12-24 | 13:00                | drop_main_sample |
| ES.v.0 | 2013-07-03 | 13:00                | drop_main_sample |
| ES.v.0 | 2013-11-29 | 13:00                | drop_main_sample |
| ES.v.0 | 2013-12-24 | 13:00                | drop_main_sample |
| ES.v.0 | 2014-07-03 | 13:00                | drop_main_sample |
| ES.v.0 | 2014-11-28 | 13:00                | drop_main_sample |
| ES.v.0 | 2014-12-24 | 13:00                | drop_main_sample |
| ES.v.0 | 2015-11-27 | 13:00                | drop_main_sample |
| ES.v.0 | 2015-12-24 | 13:00                | drop_main_sample |
| ES.v.0 | 2016-11-25 | 13:00                | drop_main_sample |
| ES.v.0 | 2017-07-03 | 13:00                | drop_main_sample |
| ES.v.0 | 2017-11-24 | 13:00                | drop_main_sample |
| ES.v.0 | 2018-07-03 | 13:00                | drop_main_sample |
| ES.v.0 | 2018-11-23 | 13:00                | drop_main_sample |
| ES.v.0 | 2018-12-24 | 13:00                | drop_main_sample |
| ES.v.0 | 2019-07-03 | 13:00                | drop_main_sample |
| ES.v.0 | 2019-11-29 | 13:00                | drop_main_sample |
| ES.v.0 | 2019-12-24 | 13:00                | drop_main_sample |
| ES.v.0 | 2021-11-26 | 13:00                | drop_main_sample |
| ES.v.0 | 2022-11-25 | 13:00                | drop_main_sample |
| ES.v.0 | 2023-07-03 | 13:00                | drop_main_sample |
| ES.v.0 | 2023-11-24 | 13:00                | drop_main_sample |
| ES.v.0 | 2024-07-03 | 13:00                | drop_main_sample |
| ES.v.0 | 2024-11-29 | 13:00                | drop_main_sample |
| ES.v.0 | 2024-12-24 | 13:00                | drop_main_sample |
| ES.v.0 | 2025-07-03 | 13:00                | drop_main_sample |
| ES.v.0 | 2025-11-28 | 13:00                | drop_main_sample |
| ES.v.0 | 2025-12-24 | 13:00                | drop_main_sample |
| NQ.v.0 | 2010-11-26 | 13:00                | drop_main_sample |
| NQ.v.0 | 2011-11-25 | 13:00                | drop_main_sample |
| NQ.v.0 | 2012-07-03 | 13:00                | drop_main_sample |
| NQ.v.0 | 2012-11-23 | 13:00                | drop_main_sample |
| NQ.v.0 | 2012-12-24 | 13:00                | drop_main_sample |
| NQ.v.0 | 2013-07-03 | 13:00                | drop_main_sample |
| NQ.v.0 | 2013-11-29 | 13:00                | drop_main_sample |
| NQ.v.0 | 2013-12-24 | 13:00                | drop_main_sample |

## Raw Data Quality

| symbol | rows      | duplicate_rows | bad_price_rows |
| ------ | --------- | -------------- | -------------- |
| ES.v.0 | 5231196.0 | 0.0            | 0.0            |
| NQ.v.0 | 5056471.0 | 0.0            | 0.0            |
| GC.v.0 | 5187751.0 | 0.0            | 0.0            |
| CL.v.0 | 5171606.0 | 0.0            | 0.0            |
| ZN.v.0 | 4799435.0 | 0.0            | 0.0            |
| 6E.v.0 | 5142776.0 | 0.0            | 0.0            |

## Drop Reasons

| symbol | detail |
| ------ | ------ |

## Variable Identity

| symbol | status | detail                          |
| ------ | ------ | ------------------------------- |
| ES.v.0 | PASS   | max_error=4.441e-16; failures=0 |
| NQ.v.0 | PASS   | max_error=4.441e-16; failures=0 |
| GC.v.0 | PASS   | max_error=4.441e-16; failures=0 |
| CL.v.0 | PASS   | max_error=4.441e-16; failures=0 |
| ZN.v.0 | PASS   | max_error=4.441e-16; failures=0 |
| 6E.v.0 | PASS   | max_error=4.441e-16; failures=0 |

## OOS Leakage

| symbol | prediction_date | training_cutoff_date | status |
| ------ | --------------- | -------------------- | ------ |
| ES.v.0 | 2021-01-05      | 2020-05-29           | PASS   |
| ES.v.0 | 2021-01-06      | 2020-05-29           | PASS   |
| ES.v.0 | 2021-01-07      | 2020-05-29           | PASS   |
| ES.v.0 | 2021-01-08      | 2020-05-29           | PASS   |
| ES.v.0 | 2021-01-11      | 2020-05-29           | PASS   |
| ES.v.0 | 2025-12-23      | 2020-05-29           | PASS   |
| ES.v.0 | 2025-12-26      | 2020-05-29           | PASS   |
| ES.v.0 | 2025-12-29      | 2020-05-29           | PASS   |
| ES.v.0 | 2025-12-30      | 2020-05-29           | PASS   |
| ES.v.0 | 2025-12-31      | 2020-05-29           | PASS   |
| NQ.v.0 | 2021-01-05      | 2020-05-29           | PASS   |
| NQ.v.0 | 2021-01-06      | 2020-05-29           | PASS   |
| NQ.v.0 | 2021-01-07      | 2020-05-29           | PASS   |
| NQ.v.0 | 2021-01-08      | 2020-05-29           | PASS   |
| NQ.v.0 | 2021-01-11      | 2020-05-29           | PASS   |
| NQ.v.0 | 2025-12-23      | 2020-05-29           | PASS   |
| NQ.v.0 | 2025-12-26      | 2020-05-29           | PASS   |
| NQ.v.0 | 2025-12-29      | 2020-05-29           | PASS   |
| NQ.v.0 | 2025-12-30      | 2020-05-29           | PASS   |
| NQ.v.0 | 2025-12-31      | 2020-05-29           | PASS   |
| GC.v.0 | 2021-01-05      | 2020-05-28           | PASS   |
| GC.v.0 | 2021-01-06      | 2020-05-28           | PASS   |
| GC.v.0 | 2021-01-07      | 2020-05-28           | PASS   |
| GC.v.0 | 2021-01-08      | 2020-05-28           | PASS   |
| GC.v.0 | 2021-01-11      | 2020-05-28           | PASS   |
| GC.v.0 | 2025-12-24      | 2020-05-28           | PASS   |
| GC.v.0 | 2025-12-26      | 2020-05-28           | PASS   |
| GC.v.0 | 2025-12-29      | 2020-05-28           | PASS   |
| GC.v.0 | 2025-12-30      | 2020-05-28           | PASS   |
| GC.v.0 | 2025-12-31      | 2020-05-28           | PASS   |
| CL.v.0 | 2021-01-05      | 2020-05-29           | PASS   |
| CL.v.0 | 2021-01-06      | 2020-05-29           | PASS   |
| CL.v.0 | 2021-01-07      | 2020-05-29           | PASS   |
| CL.v.0 | 2021-01-08      | 2020-05-29           | PASS   |
| CL.v.0 | 2021-01-11      | 2020-05-29           | PASS   |
| CL.v.0 | 2025-12-23      | 2020-05-29           | PASS   |
| CL.v.0 | 2025-12-26      | 2020-05-29           | PASS   |
| CL.v.0 | 2025-12-29      | 2020-05-29           | PASS   |
| CL.v.0 | 2025-12-30      | 2020-05-29           | PASS   |
| CL.v.0 | 2025-12-31      | 2020-05-29           | PASS   |
| ZN.v.0 | 2021-01-05      | 2020-05-28           | PASS   |
| ZN.v.0 | 2021-01-06      | 2020-05-28           | PASS   |
| ZN.v.0 | 2021-01-07      | 2020-05-28           | PASS   |
| ZN.v.0 | 2021-01-08      | 2020-05-28           | PASS   |
| ZN.v.0 | 2021-01-11      | 2020-05-28           | PASS   |
| ZN.v.0 | 2025-12-23      | 2020-05-28           | PASS   |
| ZN.v.0 | 2025-12-26      | 2020-05-28           | PASS   |
| ZN.v.0 | 2025-12-29      | 2020-05-28           | PASS   |
| ZN.v.0 | 2025-12-30      | 2020-05-28           | PASS   |
| ZN.v.0 | 2025-12-31      | 2020-05-28           | PASS   |
| 6E.v.0 | 2021-01-05      | 2020-05-29           | PASS   |
| 6E.v.0 | 2021-01-06      | 2020-05-29           | PASS   |
| 6E.v.0 | 2021-01-07      | 2020-05-29           | PASS   |
| 6E.v.0 | 2021-01-08      | 2020-05-29           | PASS   |
| 6E.v.0 | 2021-01-11      | 2020-05-29           | PASS   |
| 6E.v.0 | 2025-12-23      | 2020-05-29           | PASS   |
| 6E.v.0 | 2025-12-26      | 2020-05-29           | PASS   |
| 6E.v.0 | 2025-12-29      | 2020-05-29           | PASS   |
| 6E.v.0 | 2025-12-30      | 2020-05-29           | PASS   |
| 6E.v.0 | 2025-12-31      | 2020-05-29           | PASS   |

## Regression Samples

| symbol | sample      | equation           | N      | start_date | end_date   | newey_west_lag_rule             |
| ------ | ----------- | ------------------ | ------ | ---------- | ---------- | ------------------------------- |
| ES.v.0 | replication | Eq5                | 2443.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| ES.v.0 | replication | Eq6                | 2443.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| ES.v.0 | replication | Eq7                | 2443.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| ES.v.0 | replication | common_eq5_eq6_eq7 | 2443.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| ES.v.0 | oos         | Eq5                | 1224.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| ES.v.0 | oos         | Eq6                | 1224.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| ES.v.0 | oos         | Eq7                | 1224.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| ES.v.0 | oos         | common_eq5_eq6_eq7 | 1224.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| NQ.v.0 | replication | Eq5                | 2443.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| NQ.v.0 | replication | Eq6                | 2443.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| NQ.v.0 | replication | Eq7                | 2443.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| NQ.v.0 | replication | common_eq5_eq6_eq7 | 2443.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| NQ.v.0 | oos         | Eq5                | 1224.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| NQ.v.0 | oos         | Eq6                | 1224.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| NQ.v.0 | oos         | Eq7                | 1224.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| NQ.v.0 | oos         | common_eq5_eq6_eq7 | 1224.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| GC.v.0 | replication | Eq5                | 2414.0 | 2010-06-08 | 2020-05-28 | floor(4 * (T / 100) ** (2 / 9)) |
| GC.v.0 | replication | Eq6                | 2414.0 | 2010-06-08 | 2020-05-28 | floor(4 * (T / 100) ** (2 / 9)) |
| GC.v.0 | replication | Eq7                | 2414.0 | 2010-06-08 | 2020-05-28 | floor(4 * (T / 100) ** (2 / 9)) |
| GC.v.0 | replication | common_eq5_eq6_eq7 | 2414.0 | 2010-06-08 | 2020-05-28 | floor(4 * (T / 100) ** (2 / 9)) |
| GC.v.0 | oos         | Eq5                | 1223.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| GC.v.0 | oos         | Eq6                | 1223.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| GC.v.0 | oos         | Eq7                | 1223.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| GC.v.0 | oos         | common_eq5_eq6_eq7 | 1223.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| CL.v.0 | replication | Eq5                | 2363.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| CL.v.0 | replication | Eq6                | 2363.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| CL.v.0 | replication | Eq7                | 2363.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| CL.v.0 | replication | common_eq5_eq6_eq7 | 2363.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| CL.v.0 | oos         | Eq5                | 1207.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| CL.v.0 | oos         | Eq6                | 1207.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| CL.v.0 | oos         | Eq7                | 1207.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| CL.v.0 | oos         | common_eq5_eq6_eq7 | 1207.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| ZN.v.0 | replication | Eq5                | 2397.0 | 2010-06-08 | 2020-05-28 | floor(4 * (T / 100) ** (2 / 9)) |
| ZN.v.0 | replication | Eq6                | 2397.0 | 2010-06-08 | 2020-05-28 | floor(4 * (T / 100) ** (2 / 9)) |
| ZN.v.0 | replication | Eq7                | 2397.0 | 2010-06-08 | 2020-05-28 | floor(4 * (T / 100) ** (2 / 9)) |
| ZN.v.0 | replication | common_eq5_eq6_eq7 | 2397.0 | 2010-06-08 | 2020-05-28 | floor(4 * (T / 100) ** (2 / 9)) |
| ZN.v.0 | oos         | Eq5                | 1221.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| ZN.v.0 | oos         | Eq6                | 1221.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| ZN.v.0 | oos         | Eq7                | 1221.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| ZN.v.0 | oos         | common_eq5_eq6_eq7 | 1221.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| 6E.v.0 | replication | Eq5                | 2417.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| 6E.v.0 | replication | Eq6                | 2417.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| 6E.v.0 | replication | Eq7                | 2417.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| 6E.v.0 | replication | common_eq5_eq6_eq7 | 2417.0 | 2010-06-08 | 2020-05-29 | floor(4 * (T / 100) ** (2 / 9)) |
| 6E.v.0 | oos         | Eq5                | 1227.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| 6E.v.0 | oos         | Eq6                | 1227.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| 6E.v.0 | oos         | Eq7                | 1227.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |
| 6E.v.0 | oos         | common_eq5_eq6_eq7 | 1227.0 | 2021-01-05 | 2025-12-31 | floor(4 * (T / 100) ** (2 / 9)) |

## Strategy Executability

| symbol | status | detail                              |
| ------ | ------ | ----------------------------------- |
| ES.v.0 | PASS   | has_LH=True; has_LH_executable=True |
| NQ.v.0 | PASS   | has_LH=True; has_LH_executable=True |
| GC.v.0 | PASS   | has_LH=True; has_LH_executable=True |
| CL.v.0 | PASS   | has_LH=True; has_LH_executable=True |
| ZN.v.0 | PASS   | has_LH=True; has_LH_executable=True |
| 6E.v.0 | PASS   | has_LH=True; has_LH_executable=True |

## Largest Absolute Returns

Full top-20 rows per symbol and variable are in the CSV. First 60 rows:

| symbol | variable | trade_date | value               | current_raw_symbol | previous_close_raw_symbol | p_previous_close | p_close_minus_30 | p_close |
| ------ | -------- | ---------- | ------------------- | ------------------ | ------------------------- | ---------------- | ---------------- | ------- |
| ES.v.0 | ONFH     | 2020-03-16 | -0.0941285251964864 | ESH0               | ESH0                      | 2703.75          | 2452.25          | 2387.0  |
| ES.v.0 | ONFH     | 2020-03-24 | 0.060561633021315   | ESM0               | ESM0                      | 2216.75          | 2411.25          | 2433.0  |
| ES.v.0 | ONFH     | 2020-03-09 | -0.0597542501262413 | ESH0               | ESH0                      | 2970.5           | 2772.75          | 2735.75 |
| ES.v.0 | ONFH     | 2020-03-12 | -0.0566106647187728 | ESH0               | ESH0                      | 2738.0           | 2500.5           | 2469.75 |
| ES.v.0 | ONFH     | 2020-04-06 | 0.047086106069772   | ESM0               | ESM0                      | 2479.5           | 2629.25          | 2646.75 |
| ES.v.0 | ONFH     | 2022-11-10 | 0.041871921182266   | ESZ2               | ESZ2                      | 3755.5           | 3949.75          | 3961.0  |
| ES.v.0 | ONFH     | 2015-08-24 | -0.0395071138211382 | ESU5               | ESU5                      | 1968.0           | 1878.5           | 1886.25 |
| ES.v.0 | ONFH     | 2020-03-13 | 0.0361372608563619  | ESH0               | ESH0                      | 2469.75          | 2582.75          | 2703.75 |
| ES.v.0 | ONFH     | 2025-04-08 | 0.0355479284138269  | ESM5               | ESM5                      | 5098.75          | 5025.5           | 5017.5  |
| ES.v.0 | ONFH     | 2025-04-03 | -0.0352451838879159 | ESM5               | ESM5                      | 5710.0           | 5449.5           | 5436.0  |
| ES.v.0 | ONFH     | 2024-08-05 | -0.0336665891653104 | ESU4               | ESU4                      | 5376.25          | 5207.75          | 5218.75 |
| ES.v.0 | ONFH     | 2011-11-30 | 0.0334868145667643  | ESZ1               | ESZ1                      | 1194.5           | 1237.75          | 1245.5  |
| ES.v.0 | ONFH     | 2020-04-07 | 0.0334372343440068  | ESM0               | ESM0                      | 2646.75          | 2658.5           | 2649.75 |
| ES.v.0 | ONFH     | 2011-08-18 | -0.0333683105981111 | ESU1               | ESU1                      | 1191.25          | 1135.5           | 1140.25 |
| ES.v.0 | ONFH     | 2020-04-01 | -0.033148634198503  | ESM0               | ESM0                      | 2571.75          | 2445.75          | 2455.75 |
| ES.v.0 | ONFH     | 2011-09-22 | -0.0327798145352599 | ESZ1               | ESZ1                      | 1159.25          | 1111.75          | 1122.75 |
| ES.v.0 | ONFH     | 2025-04-23 | 0.0315660723526367  | ESM5               | ESM5                      | 5314.25          | 5391.75          | 5398.25 |
| ES.v.0 | ONFH     | 2020-03-27 | -0.0312380222307397 | ESM0               | ESM0                      | 2609.0           | 2594.5           | 2532.0  |
| ES.v.0 | ONFH     | 2020-03-10 | 0.0310700904687928  | ESH0               | ESH0                      | 2735.75          | 2837.25          | 2881.25 |
| ES.v.0 | ONFH     | 2020-03-06 | -0.030365712394506  | ESH0               | ESH0                      | 3021.5           | 2918.0           | 2970.5  |
| ES.v.0 | ROD      | 2020-03-16 | -0.0930189551548774 | ESH0               | ESH0                      | 2703.75          | 2452.25          | 2387.0  |
| ES.v.0 | ROD      | 2025-04-09 | 0.0883408071748879  | ESM5               | ESM5                      | 5017.5           | 5460.75          | 5489.5  |
| ES.v.0 | ROD      | 2020-03-24 | 0.0877410623660763  | ESM0               | ESM0                      | 2216.75          | 2411.25          | 2433.0  |
| ES.v.0 | ROD      | 2020-03-12 | -0.0867421475529583 | ESH0               | ESH0                      | 2738.0           | 2500.5           | 2469.75 |
| ES.v.0 | ROD      | 2020-03-09 | -0.0665712842955731 | ESH0               | ESH0                      | 2970.5           | 2772.75          | 2735.75 |
| ES.v.0 | ROD      | 2020-04-06 | 0.0603952409760031  | ESM0               | ESM0                      | 2479.5           | 2629.25          | 2646.75 |
| ES.v.0 | ROD      | 2020-03-11 | -0.0550108459869848 | ESH0               | ESH0                      | 2881.25          | 2722.75          | 2738.0  |
| ES.v.0 | ROD      | 2011-08-11 | 0.0539511976718154  | ESU1               | ESU1                      | 1116.75          | 1177.0           | 1168.0  |
| ES.v.0 | ROD      | 2022-11-10 | 0.0517241379310344  | ESZ2               | ESZ2                      | 3755.5           | 3949.75          | 3961.0  |
| ES.v.0 | ROD      | 2025-04-04 | -0.0510025754231052 | ESM5               | ESM5                      | 5436.0           | 5158.75          | 5108.5  |
| ES.v.0 | ROD      | 2011-08-08 | -0.05               | ESU1               | ESU1                      | 1195.0           | 1135.25          | 1117.0  |
| ES.v.0 | ROD      | 2020-04-01 | -0.0489938757655292 | ESM0               | ESM0                      | 2571.75          | 2445.75          | 2455.75 |
| ES.v.0 | ROD      | 2020-03-26 | 0.0479375696767001  | ESM0               | ESM0                      | 2466.75          | 2585.0           | 2609.0  |
| ES.v.0 | ROD      | 2011-08-18 | -0.0467995802728227 | ESU1               | ESU1                      | 1191.25          | 1135.5           | 1140.25 |
| ES.v.0 | ROD      | 2020-03-13 | 0.0457536187873266  | ESH0               | ESH0                      | 2469.75          | 2582.75          | 2703.75 |
| ES.v.0 | ROD      | 2025-04-03 | -0.0456217162872154 | ESM5               | ESM5                      | 5710.0           | 5449.5           | 5436.0  |
| ES.v.0 | ROD      | 2015-08-24 | -0.0454776422764228 | ESU5               | ESU5                      | 1968.0           | 1878.5           | 1886.25 |
| ES.v.0 | ROD      | 2022-05-05 | -0.0446241563881778 | ESM2               | ESM2                      | 4297.0           | 4105.25          | 4144.5  |
| ES.v.0 | ROD      | 2022-05-18 | -0.0427653716732946 | ESM2               | ESM2                      | 4086.25          | 3911.5           | 3923.75 |
| ES.v.0 | ROD      | 2022-09-13 | -0.041045910611128  | ESU2               | ESU2                      | 4111.25          | 3942.5           | 3932.25 |
| ES.v.0 | LH       | 2020-03-13 | 0.0468492885490272  | ESH0               | ESH0                      | 2469.75          | 2582.75          | 2703.75 |
| ES.v.0 | LH       | 2020-03-17 | 0.0303152789005658  | ESH0               | ESH0                      | 2387.0           | 2474.0           | 2549.0  |
| ES.v.0 | LH       | 2011-10-04 | 0.0290122035459359  | ESZ1               | ESZ1                      | 1092.75          | 1085.75          | 1117.25 |
| ES.v.0 | LH       | 2020-03-16 | -0.0266082169436232 | ESH0               | ESH0                      | 2703.75          | 2452.25          | 2387.0  |
| ES.v.0 | LH       | 2011-08-09 | 0.0263273365511189  | ESU1               | ESU1                      | 1117.0           | 1139.5           | 1169.5  |
| ES.v.0 | LH       | 2020-03-25 | -0.0259624876604146 | ESM0               | ESM0                      | 2433.0           | 2532.5           | 2466.75 |
| ES.v.0 | LH       | 2020-03-27 | -0.0240894199267681 | ESM0               | ESM0                      | 2609.0           | 2594.5           | 2532.0  |
| ES.v.0 | LH       | 2020-03-20 | -0.0201608579088471 | ESM0               | ESM0                      | 2398.25          | 2331.25          | 2284.25 |
| ES.v.0 | LH       | 2020-03-02 | 0.0190484043869052  | ESH0               | ESH0                      | 2973.75          | 3031.75          | 3089.5  |
| ES.v.0 | LH       | 2015-08-25 | -0.0186817524009998 | ESU5               | ESU5                      | 1886.25          | 1900.25          | 1864.75 |
| ES.v.0 | LH       | 2018-02-05 | -0.0180046403712297 | ESH8               | ESH8                      | 2760.0           | 2693.75          | 2645.25 |
| ES.v.0 | LH       | 2020-03-06 | 0.0179917751884852  | ESH0               | ESH0                      | 3021.5           | 2918.0           | 2970.5  |
| ES.v.0 | LH       | 2023-03-22 | -0.0169659442724458 | ESM3               | ESM3                      | 4038.5           | 4037.5           | 3969.0  |
| ES.v.0 | LH       | 2011-09-21 | -0.0169599321602713 | ESZ1               | ESZ1                      | 1196.75          | 1179.25          | 1159.25 |
| ES.v.0 | LH       | 2011-08-08 | -0.0160757542391544 | ESU1               | ESU1                      | 1195.0           | 1135.25          | 1117.0  |
| ES.v.0 | LH       | 2018-02-08 | -0.0159351145038167 | ESH8               | ESH8                      | 2679.0           | 2620.0           | 2578.25 |
| ES.v.0 | LH       | 2020-02-27 | -0.0158848349466368 | ESH0               | ESH0                      | 3116.25          | 3021.75          | 2973.75 |
| ES.v.0 | LH       | 2022-01-24 | 0.0158556273062731  | ESH2               | ESH2                      | 4385.5           | 4336.0           | 4404.75 |
| ES.v.0 | LH       | 2020-03-10 | 0.0155079742708608  | ESH0               | ESH0                      | 2735.75          | 2837.25          | 2881.25 |
| ES.v.0 | LH       | 2018-12-27 | 0.0142508143322475  | ESH9               | ESH9                      | 2468.25          | 2456.0           | 2491.0  |

## DST Checks

| symbol | trade_date | source_close_ts_utc       | source_close_ts_new_york  | ny_date    | utc_date   | expected_source_clock |
| ------ | ---------- | ------------------------- | ------------------------- | ---------- | ---------- | --------------------- |
| ES.v.0 | 2019-03-08 | 2019-03-08T20:59:00+00:00 | 2019-03-08T15:59:00-05:00 | 2019-03-08 | 2019-03-08 | 15:59                 |
| ES.v.0 | 2019-03-11 | 2019-03-11T19:59:00+00:00 | 2019-03-11T15:59:00-04:00 | 2019-03-11 | 2019-03-11 | 15:59                 |
| ES.v.0 | 2019-11-01 | 2019-11-01T19:59:00+00:00 | 2019-11-01T15:59:00-04:00 | 2019-11-01 | 2019-11-01 | 15:59                 |
| ES.v.0 | 2019-11-04 | 2019-11-04T20:59:00+00:00 | 2019-11-04T15:59:00-05:00 | 2019-11-04 | 2019-11-04 | 15:59                 |
| NQ.v.0 | 2019-03-08 | 2019-03-08T20:59:00+00:00 | 2019-03-08T15:59:00-05:00 | 2019-03-08 | 2019-03-08 | 15:59                 |
| NQ.v.0 | 2019-03-11 | 2019-03-11T19:59:00+00:00 | 2019-03-11T15:59:00-04:00 | 2019-03-11 | 2019-03-11 | 15:59                 |
| NQ.v.0 | 2019-11-01 | 2019-11-01T19:59:00+00:00 | 2019-11-01T15:59:00-04:00 | 2019-11-01 | 2019-11-01 | 15:59                 |
| NQ.v.0 | 2019-11-04 | 2019-11-04T20:59:00+00:00 | 2019-11-04T15:59:00-05:00 | 2019-11-04 | 2019-11-04 | 15:59                 |
| GC.v.0 | 2019-03-08 | 2019-03-08T18:29:00+00:00 | 2019-03-08T13:29:00-05:00 | 2019-03-08 | 2019-03-08 | 13:29                 |
| GC.v.0 | 2019-03-11 | 2019-03-11T17:29:00+00:00 | 2019-03-11T13:29:00-04:00 | 2019-03-11 | 2019-03-11 | 13:29                 |
| GC.v.0 | 2019-11-01 | 2019-11-01T17:29:00+00:00 | 2019-11-01T13:29:00-04:00 | 2019-11-01 | 2019-11-01 | 13:29                 |
| GC.v.0 | 2019-11-04 | 2019-11-04T18:29:00+00:00 | 2019-11-04T13:29:00-05:00 | 2019-11-04 | 2019-11-04 | 13:29                 |
| CL.v.0 | 2019-03-08 | 2019-03-08T19:29:00+00:00 | 2019-03-08T14:29:00-05:00 | 2019-03-08 | 2019-03-08 | 14:29                 |
| CL.v.0 | 2019-03-11 | 2019-03-11T18:29:00+00:00 | 2019-03-11T14:29:00-04:00 | 2019-03-11 | 2019-03-11 | 14:29                 |
| CL.v.0 | 2019-11-01 | 2019-11-01T18:29:00+00:00 | 2019-11-01T14:29:00-04:00 | 2019-11-01 | 2019-11-01 | 14:29                 |
| CL.v.0 | 2019-11-04 | 2019-11-04T19:29:00+00:00 | 2019-11-04T14:29:00-05:00 | 2019-11-04 | 2019-11-04 | 14:29                 |
| ZN.v.0 | 2019-03-08 | 2019-03-08T19:59:00+00:00 | 2019-03-08T14:59:00-05:00 | 2019-03-08 | 2019-03-08 | 14:59                 |
| ZN.v.0 | 2019-03-11 | 2019-03-11T18:59:00+00:00 | 2019-03-11T14:59:00-04:00 | 2019-03-11 | 2019-03-11 | 14:59                 |
| ZN.v.0 | 2019-11-01 | 2019-11-01T18:59:00+00:00 | 2019-11-01T14:59:00-04:00 | 2019-11-01 | 2019-11-01 | 14:59                 |
| ZN.v.0 | 2019-11-04 | 2019-11-04T19:59:00+00:00 | 2019-11-04T14:59:00-05:00 | 2019-11-04 | 2019-11-04 | 14:59                 |
| 6E.v.0 | 2019-03-08 | 2019-03-08T18:59:00+00:00 | 2019-03-08T13:59:00-05:00 | 2019-03-08 | 2019-03-08 | 13:59                 |
| 6E.v.0 | 2019-03-11 | 2019-03-11T17:59:00+00:00 | 2019-03-11T13:59:00-04:00 | 2019-03-11 | 2019-03-11 | 13:59                 |
| 6E.v.0 | 2019-11-01 | 2019-11-01T17:59:00+00:00 | 2019-11-01T13:59:00-04:00 | 2019-11-01 | 2019-11-01 | 13:59                 |
| 6E.v.0 | 2019-11-04 | 2019-11-04T18:59:00+00:00 | 2019-11-04T13:59:00-05:00 | 2019-11-04 | 2019-11-04 | 13:59                 |

## File Isolation Notes

- Old CSV results are copied under `reports/archive/invalid_boundary_v0/tables/`.
- Old processed parquet files are copied under `data/processed/archive/invalid_boundary_v0/` and remain ignored by Git.
- Current top-level `data/processed/*_daily_research_table.parquet` files are still old until regenerated. The regression script now refuses them because they lack `pipeline_version=boundary_corrected_v1`.
- Future regenerated daily tables and summaries will include `pipeline_version=boundary_corrected_v1`.
