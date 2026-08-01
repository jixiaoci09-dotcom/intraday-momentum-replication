# 6E.v.0 2010-2025 Download Notes

Raw licensed Databento files remain local under `data/raw/` and are ignored by Git.

- Dataset: `GLBX.MDP3`
- Symbol: `6E.v.0`
- Approved estimated cost: `$18.7778`

| Package | Schema | Period | Cost | Size | DBN files | SHA-256 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| replication definitions | `definition` | 2010-06-06 to 2020-06-01 | `$0.0018` | 1.10 MB | 120 | `bf482719b645e009dc2bf544c71b29c25d4cb4a02292a95ea833839948c7a7c4` |
| OOS definitions | `definition` | 2021-01-01 to 2026-01-01 | `$0.0009` | 0.56 MB | 60 | `f355d95fad1c590174cc534e678b565d900174ac601b9f437860a8a12f68d220` |
| replication OHLCV | `ohlcv-1m` | 2010-06-06 to 2020-06-01 | `$12.4303` | 41.96 MB | 120 | `fd3cb4792ffc43f68b9808c0c65a33c6b9e0d1de176a1a95a21da1c1546e5674` |
| OOS OHLCV | `ohlcv-1m` | 2021-01-01 to 2026-01-01 | `$6.3448` | 21.79 MB | 60 | `ca0717196e23943433ed999df443930dc00c2f578f260294ab13505323939744` |

## Data Check Summary

### replication definitions

- Rows: `3,131`
- Instrument count: `41`
- Raw symbol count: `40`
- Min price increment values: `0.0001, 5e-05`

### OOS definitions

- Rows: `1,575`
- Instrument count: `21`
- Raw symbol count: `21`
- Min price increment values: `5e-05`

### replication OHLCV

- Rows: `3,404,835`
- UTC range: `2010-06-07 00:00:00+00:00` to `2020-05-31 23:59:00+00:00`
- Duplicate timestamps: `0`
- Instrument count: `41`
- Price close range: `1.03685` to `1.4921`
- Required-boundary problem days: `92` of `2563`

### OOS OHLCV

- Rows: `1,737,941`
- UTC range: `2021-01-03 23:00:00+00:00` to `2025-12-31 21:59:00+00:00`
- Duplicate timestamps: `0`
- Instrument count: `21`
- Price close range: `0.95945` to `1.23675`
- Required-boundary problem days: `33` of `1292`
