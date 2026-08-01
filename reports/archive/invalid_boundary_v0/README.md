# INVALID_BOUNDARY_V0 Archive

These results are invalidated because OHLCV-1m `ts_event` was treated as the
interval end rather than the interval start.

The archived result tables were copied from `reports/tables/` before applying
the corrected boundary logic. The matching local processed daily tables were
copied to `data/processed/archive/invalid_boundary_v0/`; those parquet files
remain ignored by Git because they are derived from licensed Databento data.

No archived result in this directory should be used for final inference.
