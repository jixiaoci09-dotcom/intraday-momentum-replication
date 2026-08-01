# CL.v.0 2010-2025 Download And Validation Manifest

Raw licensed Databento files remain local under `data/raw/` and are ignored by Git.

- Dataset: `GLBX.MDP3`
- Symbol: `CL.v.0`
- Approved estimated cost: `$18.8831`

| Package | Schema | Period | Cost | Size | DBN files | SHA-256 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| replication definitions | `definition` | 2010-06-06 to 2020-06-01 | `$0.0018` | 1.10 MB | 120 | `f8061cd9cf268a454df94cf145144a205fbe5add75b599d361258d44bdde6281` |
| OOS definitions | `definition` | 2021-01-01 to 2026-01-01 | `$0.0009` | 0.56 MB | 60 | `7d4a012f6ec983763e3952d2d31688cbadee02d0075300e91e16d7a427ba514b` |
| replication OHLCV | `ohlcv-1m` | 2010-06-06 to 2020-06-01 | `$12.5000` | 46.21 MB | 120 | `5215af85702a3c7c12e2e84a283b867d595233945e17af1c68fcb952abf3881a` |
| OOS OHLCV | `ohlcv-1m` | 2021-01-01 to 2026-01-01 | `$6.3805` | 24.61 MB | 60 | `b5407110379a4262a1b6bca0ed9a3341e9541c6e418e26665f655f1ad754bb5a` |

## Validation Summary

### replication definitions

- Rows: `3,132`
- Instrument count: `121`
- Raw symbol count: `120`
- Min price increment values: `0.01`

### OOS definitions

- Rows: `1,571`
- Instrument count: `61`
- Raw symbol count: `61`
- Min price increment values: `0.01`

### replication OHLCV

- Rows: `3,423,910`
- UTC range: `2010-06-07 00:00:00+00:00` to `2020-05-31 23:59:00+00:00`
- Duplicate timestamps: `0`
- Instrument count: `121`
- Price close range: `6.9` to `114.73`
- Required-boundary problem days: `94` of `2562`

### OOS OHLCV

- Rows: `1,747,696`
- UTC range: `2021-01-03 23:00:00+00:00` to `2025-12-31 21:59:00+00:00`
- Duplicate timestamps: `0`
- Instrument count: `61`
- Price close range: `47.18` to `130.0`
- Required-boundary problem days: `41` of `1290`
