# GC.v.0 2010-2025 Download And Validation Manifest

Raw licensed Databento files remain local under `data/raw/` and are ignored by Git.

- Dataset: `GLBX.MDP3`
- Symbol: `GC.v.0`
- Approved estimated cost: `$18.9420`

| Package | Schema | Period | Cost | Size | DBN files | SHA-256 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| replication definitions | `definition` | 2010-06-06 to 2020-06-01 | `$0.0018` | 1.11 MB | 120 | `59a3652a81a0991cb1bd059e9bf000e9de9707a9b07df7be1be4744bc83551a2` |
| OOS definitions | `definition` | 2021-01-01 to 2026-01-01 | `$0.0009` | 0.56 MB | 60 | `870a66f1dcdcbfa75c4826b34c947ace24cc530930d7cb5ef13dd073ca2ed776` |
| replication OHLCV | `ohlcv-1m` | 2010-06-06 to 2020-06-01 | `$12.5616` | 45.41 MB | 120 | `75374aa5dabd46eb480866db5bd21dfe4e988b4e89b0de544f2e5d088f337414` |
| OOS OHLCV | `ohlcv-1m` | 2021-01-01 to 2026-01-01 | `$6.3778` | 25.16 MB | 60 | `5ce51a7f12a48a583a6ff8abfd48b1714fd8a70e722b7f4beb1e8061842f7cac` |

## Validation Summary

### replication definitions

- Rows: `3,131`
- Instrument count: `51`
- Raw symbol count: `50`
- Min price increment values: `0.1`

### OOS definitions

- Rows: `1,571`
- Instrument count: `26`
- Raw symbol count: `26`
- Min price increment values: `0.1`

### replication OHLCV

- Rows: `3,440,794`
- UTC range: `2010-06-07 00:00:00+00:00` to `2020-05-31 23:59:00+00:00`
- Duplicate timestamps: `0`
- Instrument count: `51`
- Price close range: `1045.6` to `1922.8`
- Required-boundary problem days: `88` of `2560`

### OOS OHLCV

- Rows: `1,746,957`
- UTC range: `2021-01-03 23:00:00+00:00` to `2025-12-31 21:59:00+00:00`
- Duplicate timestamps: `0`
- Instrument count: `26`
- Price close range: `1618.6` to `4583.4`
- Required-boundary problem days: `34` of `1290`
