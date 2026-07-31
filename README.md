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
