# NQ.v.0 2010-2025 Download And Validation Manifest

Raw licensed Databento files remain local under `data/raw/` and are ignored by Git.

- Dataset: `GLBX.MDP3`
- Symbol: `NQ.v.0`
- Approved estimated cost: `$18.4628`

| Package | Schema | Period | Cost | Size | DBN files | SHA-256 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| replication definitions | `definition` | 2010-06-06 to 2020-06-01 | `$0.0018` | 1.14 MB | 120 | `28b3ee70862404077fde102ddfcb9116a9be9280007a35ad2c06c7409a2f73fc` |
| OOS definitions | `definition` | 2021-01-01 to 2026-01-01 | `$0.0009` | 0.58 MB | 60 | `d7444ad01e7a76053e86f26b628b08a2cf471e12ad9d2aa9b404bb780145eeca` |
| replication OHLCV | `ohlcv-1m` | 2010-06-06 to 2020-06-01 | `$12.0043` | 46.54 MB | 120 | `837666ad9973e6e0b3a9b3421de50797755af56df0a6323754ce6d2f8c08b2a3` |
| OOS OHLCV | `ohlcv-1m` | 2021-01-01 to 2026-01-01 | `$6.4558` | 32.43 MB | 60 | `a120b837f07fd4ace7f10dcda07898706fe4e12d35921cac83e9090bccfe665f` |

## Validation Summary

### replication definitions

- Rows: `3,131`
- Instrument count: `41`
- Raw symbol count: `40`
- Min price increment values: `0.25`

### OOS definitions

- Rows: `1,571`
- Instrument count: `21`
- Raw symbol count: `21`
- Min price increment values: `0.25`

### replication OHLCV

- Rows: `3,288,145`
- UTC range: `2010-06-07 00:00:00+00:00` to `2020-05-31 23:59:00+00:00`
- Duplicate timestamps: `0`
- Instrument count: `41`
- Price close range: `1699.25` to `9762.0`
- Required-boundary problem days: `74` of `2558`

### OOS OHLCV

- Rows: `1,768,326`
- UTC range: `2021-01-03 23:00:00+00:00` to `2025-12-31 21:59:00+00:00`
- Duplicate timestamps: `0`
- Instrument count: `21`
- Price close range: `10495.75` to `26396.25`
- Required-boundary problem days: `44` of `1289`
