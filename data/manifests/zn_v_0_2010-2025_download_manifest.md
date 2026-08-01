# ZN.v.0 2010-2025 Download Notes

Raw licensed Databento files remain local under `data/raw/` and are ignored by Git.

- Dataset: `GLBX.MDP3`
- Symbol: `ZN.v.0`
- Approved estimated cost: `$17.5244`

| Package | Schema | Period | Cost | Size | DBN files | SHA-256 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| replication definitions | `definition` | 2010-06-06 to 2020-06-01 | `$0.0018` | 1.10 MB | 120 | `e780a74d2d9dc4b11835c20bfc26575fc47d2b617079767ba74e0027a9cb25e6` |
| OOS definitions | `definition` | 2021-01-01 to 2026-01-01 | `$0.0009` | 0.55 MB | 60 | `ea1f4da1f91e0d1da14404a2777b61006f4f378cae817710320219e73339d196` |
| replication OHLCV | `ohlcv-1m` | 2010-06-06 to 2020-06-01 | `$11.4086` | 32.81 MB | 120 | `78b78ab21d8274917585d1ff6c631d0a67dd323295dd08ce0786a49b0f2516c3` |
| OOS OHLCV | `ohlcv-1m` | 2021-01-01 to 2026-01-01 | `$6.1131` | 17.94 MB | 60 | `5f4be7b08af64a9204f55aac6e711dfd3121fa477b1461ec87dd215aaea606e4` |

## Data Check Summary

### replication definitions

- Rows: `3,131`
- Instrument count: `41`
- Raw symbol count: `40`
- Min price increment values: `0.015625`

### OOS definitions

- Rows: `1,570`
- Instrument count: `21`
- Raw symbol count: `21`
- Min price increment values: `0.015625`

### replication OHLCV

- Rows: `3,124,984`
- UTC range: `2010-06-07 00:00:00+00:00` to `2020-05-31 23:59:00+00:00`
- Duplicate timestamps: `0`
- Instrument count: `41`
- Price close range: `117.421875` to `140.71875`
- Required-boundary problem days: `105` of `2566`

### OOS OHLCV

- Rows: `1,674,451`
- UTC range: `2021-01-03 23:00:00+00:00` to `2025-12-31 21:59:00+00:00`
- Duplicate timestamps: `0`
- Instrument count: `21`
- Price close range: `105.359375` to `138.15625`
- Required-boundary problem days: `50` of `1292`
