# Intraday Momentum Replication

This repository contains a reproducible baseline replication and post-publication
out-of-sample study of Baltussen, Da, Lammers, and Martens, "Hedging Demand and
Market Intraday Momentum," using Databento CME futures minute data.

## Contracts

- ES: E-mini S&P 500
- NQ: E-mini Nasdaq 100
- GC: Gold
- CL: WTI crude oil
- ZN: 10-year U.S. Treasury note
- 6E: Euro FX

## Frozen Baseline

The frozen baseline uses `pipeline_version=boundary_corrected_v1`.

Boundary rules:

- Product-specific effective sessions are used for every contract.
- Timestamps are handled in `America/New_York`, including daylight saving time.
- For a theoretical non-open boundary `T`, the price is the close of the
  OHLCV-1m bar with `ts_event = T - 1 minute`.
- Session open uses the open of the bar with `ts_event = session_open`.
- Executable last-half-hour entry uses the next bar open after the signal is
  formed at the close-minus-30 boundary.
- Previous close and same-day prices must be from the same `instrument_id`.
- Roll-mismatch days, early closes, missing exact boundaries, and missing
  previous closes are excluded by pre-specified rules.

Samples:

- Strict paper-overlap sample: first valid trading day through `2020-05-01`.
- Post-publication OOS: `2021-01-01` through `2025-12-31`.
- `2020-05-02` through `2020-12-31` is not included in the strict paper-overlap
  results and is not used in the frozen OOS expanding window.

## Baseline Conclusions

All six contracts, ES, NQ, GC, CL, ZN, and 6E, have complete single-contract
baseline replications.

ES, NQ, GC, and ZN replicate positive and statistically significant Eq. (7)
relations in the strict paper-overlap sample. CL and 6E are insignificant at
the single-contract level, which is consistent with the paper's appendix-level
single-contract evidence; they should not be described as replication failures.
CL and 6E are retained as null/control contracts and should not be directly
compared with the paper's energy or currency pooled regressions.

In 2021-2025, only ZN continues to show a positive and significant Eq. (7)
relation. ES, NQ, and GC show statistically significant post-publication
attenuation. Statistical significance is not the same as tradeability after
costs; the ZN executable strategy is highly sensitive to tick costs.

## Main Outputs

- Chinese frozen baseline summary:
  `reports/final_baseline_summary_zh.md`
- English frozen baseline summary:
  `reports/final_baseline_summary_en.md`
- Full boundary-corrected rerun summary:
  `reports/core_rerun_summary_boundary_corrected_v1.md`
- Regression long table:
  `reports/tables/boundary_corrected_v1_regression_long.csv`
- OOS frozen/expanding table:
  `reports/tables/boundary_corrected_v1_oos_all.csv`
- Period-difference tests:
  `reports/tables/boundary_corrected_v1_beta_difference_all.csv`
- Executable and paper-price strategy cost table:
  `reports/tables/boundary_corrected_v1_strategy_all.csv`
- ZN executable round-trip tick-cost table:
  `reports/tables/zn_executable_round_trip_tick_costs.csv`
- ZN break-even round-trip tick cost:
  `reports/tables/zn_break_even_round_trip_tick_cost.csv`
- Baseline file manifest:
  `reports/baseline_file_manifest.csv`
- Baseline validation report:
  `reports/audit/baseline_validation_report.md`

## Invalidated Boundary Version

Earlier results are preserved only as an audit trail under
`reports/archive/invalid_boundary_v0/README.md`. The invalidated tables are
ignored by Git and are not used in the README conclusions or final result
tables.

The invalidation reason is that Databento OHLCV-1m `ts_event` was initially
treated as the interval end rather than the interval start. The corrected
pipeline uses the `T - 1 minute` source bar for non-open boundary closes.

## Market Regime Extension Protocol

The next stage is pre-registered but not yet run:

- `docs/market_regime_extension_protocol_v1.md`

The extension research question is why ZN retains intraday closing momentum in
2021-2025 while ES, NQ, and GC attenuate. CL and 6E remain controls because they
are not significant in the replication period.

## Data Policy

Do not commit:

- Databento API keys or `.env` files.
- Raw Databento market data.
- Processed market-data parquet files.
- Large intermediate data.
- Invalidated old result tables.
- Account, billing, or credential files.

Git may contain source code, documentation, data manifests, aggregate result
tables, audit summaries, and final reports.

## Reproducibility

Create and activate a local virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Set the Databento key only in the local shell:

```bash
export DATABENTO_API_KEY="your_key_here"
```

Validate the frozen baseline:

```bash
python scripts/freeze_baseline.py
python -m unittest tests/test_boundary_rules.py tests/test_oos_methods.py
```
