# Intraday Momentum Replication

This repository supports a replication and extension of Baltussen, Da,
Lammers, and Martens, "Hedging demand and market intraday momentum."

The project focuses on CME futures minute data from Databento:

- ES: E-mini S&P 500
- NQ: E-mini Nasdaq 100
- GC: Gold
- CL: WTI crude oil
- ZN: 10-year U.S. Treasury note
- 6E: Euro FX

## Research Goals

1. Reproduce the paper's core intraday closing momentum result using CME
   futures minute data.
2. Run a true post-paper out-of-sample test for 2021-2025.
3. Separate statistical predictability from net tradability after costs.
4. Study market states using only information known before the entry time,
   including volatility, volume, and signal strength.

## Current Progress

- Databento account setup was completed outside this repository.
- Python environment was created locally.
- A one-month GC continuous futures sample was downloaded locally for
  validation only.
- The sample was checked for fields, UTC timestamps, price scale, volume,
  missing minutes, and continuous contract instrument changes.
- Public minute-level chart validation was not available for the historical
  window. Public daily/spot price checks support the downloaded data's price
  scale.
- The GC sample manifest is stored in
  `data/manifests/gc_v0_2024-01_ohlcv-1m_manifest.md`. The raw Databento file
  remains local and ignored by Git.

## Sample Validation Findings

The January 2024 `GC.v.0` sample contains 29,474 one-minute rows. Prices are in
the expected COMEX gold futures range, volume is positive, timestamps are UTC,
and no duplicate event timestamps were found.

The continuous symbol maps to two Databento `instrument_id` values during the
sample:

- `41512`: most of January 2024.
- `44740`: January 31 onward.

The paper window for GC is `08:20-13:30` New York time. Most dates have complete
coverage in that window. January 30, 2024 is an important exception: it has 94
missing minutes in the paper window and is missing the `08:20` and `13:00`
boundary bars. This date should be excluded or flagged in research-table
construction.

## ES Data Acquisition

The project purchased ES before the remaining five symbols to validate the full
pipeline at lower cost. The approved Databento total was `$19.1006`, covering:

- ES `ohlcv-1m`, 2010-06-06 to 2020-06-01.
- ES `ohlcv-1m`, 2021-01-01 to 2026-01-01.
- ES `definition` data for both periods.

The raw files remain local under `data/raw/` and are ignored by Git. The
download and validation manifest is stored in
`data/manifests/es_v0_2010-2025_download_manifest.md`.

Initial ES validation found:

- 3,463,223 replication OHLCV rows and 1,767,973 OOS OHLCV rows.
- Zero duplicate timestamps and no missing/zero prices.
- `min_price_increment = 0.25` in definitions.
- 74 replication-window and 44 OOS-window dates missing key `09:30-16:00`
  boundaries, primarily holidays and early closes that must be excluded or
  flagged.

## ES Daily Research Table

The baseline ES daily table rules are frozen in
`docs/es_daily_table_rules.md`. The generated local table is stored at
`data/processed/es_daily_research_table.parquet` and is ignored by Git because
it is derived from licensed data.

The Git-tracked manifest is
`data/manifests/es_daily_research_table_manifest.md`. The initial build created
3,853 candidate dates and included 3,667 dates after excluding NYSE closed
days, early closes, missing-boundary observations, and cross-instrument
observations.

## ES Core Replication

The ES core replication now follows the paper's Table 2 Eq. (5), Eq. (6), and
Eq. (7), plus the timing strategies based on Eq. (12):

```text
Eq. (5): r_LH,t = alpha + beta_ONFH * r_ONFH,t + epsilon_t
Eq. (6): r_LH,t = alpha + beta_ONFH * r_ONFH,t
                  + beta_M * r_M,t + beta_SLH * r_SLH,t + epsilon_t
Eq. (7): r_LH,t = alpha + beta_ROD * r_ROD,t + epsilon_t
Eq. (12): eta(r) = r_LH if r > 0, otherwise -r_LH
```

Outputs are stored in `reports/tables/`.

Current ES-only gross results:

- Eq. (5), replication window: `beta_ONFH * 100 = 4.63`,
  Newey-West `t = 1.67`, `p = 0.096`. The sign is positive, but the
  statistical evidence is weak and does not meet the common 5% threshold.
- Eq. (6), replication window: `beta_ONFH * 100 = 4.31`, `beta_M * 100 = 2.69`,
  and `beta_SLH * 100 = 13.98`; their Newey-West p-values are `0.090`,
  `0.245`, and `0.093`, respectively.
- Eq. (7), replication window: `beta_ROD * 100 = 4.22`,
  Newey-West `t = 2.32`, `p = 0.020`, supporting the paper's core
  `ROD -> LH` intraday closing momentum relation for ES in the overlapping
  historical sample.
- Eq. (7), OOS window: `beta_ROD * 100 = -0.58`,
  Newey-West `t = -0.54`, `p = 0.591`. This does not establish a significant
  reversal; it fails to reject a zero OOS predictive coefficient.
- A pooled period-interaction test for Eq. (7) estimates
  `beta_OOS - beta_replication = -4.80` percentage points with Newey-West
  `t = -2.28`, `p = 0.023`. For ES alone, this supports describing the
  post-2020 result as a statistically detectable attenuation of the historical
  `ROD` coefficient.
- Fixed-split OOS `R^2` values are negative for all three ES specifications:
  Eq. (5) `-3.47%`, Eq. (6) `-2.78%`, and Eq. (7) `-3.79%`. The predictive
  models trained on 2010-2020 do not beat the replication-sample mean
  benchmark for 2021-2025.
- The replication-window `r_ROD` timing strategy has annualized gross return
  `3.71%` and Sharpe `0.82`; OOS gross return is `0.23%` with Sharpe `0.06`.
- The `r_ONFH` timing strategy is weak for ES alone: replication Sharpe `0.10`
  and OOS Sharpe `-0.87`.

These are gross, single-symbol ES results before transaction costs and before
buying the remaining target futures.

ES-stage conclusion: We replicate a positive and statistically significant
relation between rest-of-day and last-half-hour returns in ES futures during
2010-2020. However, the coefficient declines significantly in 2021-2025, while
the model produces a negative out-of-sample R^2, indicating no improvement over
the historical-mean forecast.

## NQ Data Acquisition

NQ was downloaded after ES to test whether the ES result extends to the other
U.S. equity index future before buying the remaining non-equity contracts. The
approved Databento total was `$18.4628`, covering:

- NQ `ohlcv-1m`, 2010-06-06 to 2020-06-01.
- NQ `ohlcv-1m`, 2021-01-01 to 2026-01-01.
- NQ `definition` data for both periods.

The raw files remain local under `data/raw/` and are ignored by Git. The
download and validation manifest is stored in
`data/manifests/nq_v_0_2010-2025_download_manifest.md`.

Initial NQ validation found:

- 3,288,145 replication OHLCV rows and 1,768,326 OOS OHLCV rows.
- `min_price_increment = 0.25` in definitions.
- 74 replication-window and 44 OOS-window dates missing key `09:30-16:00`
  boundaries, matching the expected holiday and early-close pattern seen in ES.

## NQ Core Replication

The NQ daily research table uses the same U.S. equity-index effective window as
ES: `09:30-16:00` New York time. The baseline table includes 3,667 dates:
2,443 in the 2010-2020 replication window and 1,224 in the 2021-2025 OOS
window.

Current NQ-only gross results:

- Eq. (5), replication window: `beta_ONFH * 100 = 3.94`,
  Newey-West `t = 1.42`, `p = 0.155`.
- Eq. (6), replication window: `beta_ONFH * 100 = 3.74`, `beta_M * 100 = 1.36`,
  and `beta_SLH * 100 = 13.11`; only `beta_SLH` is close to conventional
  significance with `p = 0.075`.
- Eq. (7), replication window: `beta_ROD * 100 = 3.19`,
  Newey-West `t = 1.93`, `p = 0.053`. The sign is consistent with the paper,
  but the evidence is slightly weaker than the common 5% threshold.
- Eq. (7), OOS window: `beta_ROD * 100 = -0.11`,
  Newey-West `t = -0.12`, `p = 0.901`. There is no stable positive OOS
  predictive relation.
- A pooled period-interaction test for Eq. (7) estimates
  `beta_OOS - beta_replication = -3.30` percentage points with Newey-West
  `t = -1.76`, `p = 0.078`. This is not significant at the common 5% level;
  it is only suggestive at roughly the 10% level. Therefore, NQ should be
  described as showing no stable OOS predictive relation and only weak
  evidence of coefficient attenuation, unlike the stronger ES period-difference
  evidence.
- Fixed-split OOS `R^2` values are negative for all three NQ specifications:
  Eq. (5) `-2.92%`, Eq. (6) `-1.88%`, and Eq. (7) `-2.40%`.
- The replication-window `r_ROD` timing strategy has annualized gross return
  `3.25%` and Sharpe `0.66`; OOS gross return is `-1.62%` with Sharpe `-0.34`.

## Data Policy

Do not commit licensed Databento market data, API keys, billing information,
or local environment files. Raw and processed market data belong only in
ignored local directories such as `data/raw/`, `data/interim/`, and
`data/processed/`.

GitHub may contain source code, documentation, data manifests, file hashes,
aggregate result tables, figures, and final reports.

## Reproducibility

Install dependencies in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Set the Databento API key locally, never in the repository:

```bash
export DATABENTO_API_KEY="your_key_here"
```

Check the cost of a historical request before downloading:

```bash
python scripts/check_databento_cost.py \
  --dataset GLBX.MDP3 \
  --symbol GC.v.0 \
  --schema ohlcv-1m \
  --start 2024-01-01 \
  --end 2024-02-01
```

Check the full replication plus OOS cost for one continuous futures symbol:

```bash
python scripts/check_symbol_full_cost.py --symbol NQ.v.0
```

Download an approved full symbol batch:

```bash
python scripts/download_symbol_batch.py --symbol NQ.v.0 --approved-total 18.4628
```

Validate a downloaded full symbol batch:

```bash
python scripts/validate_symbol_downloads.py --symbol NQ.v.0
```

Download the approved GC sample:

```bash
python scripts/download_sample_gc.py
```

Validate the local GC sample:

```bash
python scripts/validate_sample_gc.py
```

## Planned Version Tags

- `v0.1-scaffold`: project scaffold, README, environment, and Git rules.
- `v0.2-sample-validated`: GC one-month sample download and validation code.
- `v0.3-data-pipeline`: full data download, cleaning, calendars, and roll logic.
- `v0.4-core-replication`: 2010-May 2020 core replication.
- `v0.5-out-of-sample`: 2021-2025 out-of-sample test.
- `v0.6-execution-costs`: fixed-cost and necessary BBO cost analysis.
- `v1.0`: market-state extension, final report, figures, and README.
