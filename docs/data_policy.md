# Data Policy

This repository must not contain licensed market data, secrets, or account
information.

## Never Commit

- Databento API keys.
- `.env` or `.env.*` files.
- Databento raw OHLCV, trades, MBP, MBO, or BBO files.
- Large cleaned or processed market data files.
- Account, billing, invoice, or payment information.
- Any data sample whose license has not been explicitly cleared for GitHub.

## Allowed

- Python source code.
- Configuration templates without secrets.
- Tests.
- Download, cost-estimation, validation, and cleaning scripts.
- Data dictionaries.
- Data manifests with source, schema, symbol, date range, cost, download time,
  local path, and SHA-256 hash.
- Aggregated research tables.
- Figures and final reports.

## Local Data Layout

- `data/raw/`: licensed raw data, ignored by Git.
- `data/interim/`: intermediate files, ignored by Git.
- `data/processed/`: cleaned market data, ignored by Git.
- `data/manifests/`: metadata and hashes only, allowed in Git.

After every full data download, make a private backup outside the repository.
Record the source, schema, symbols, time range, download time, cost, and
SHA-256 hash in `data/manifests/`.
