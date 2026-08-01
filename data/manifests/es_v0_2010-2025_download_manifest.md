# ES.v.0 2010-2025 Download Notes

## Download Decision

The project first purchased ES only, instead of all six target futures, to
validate the complete replication and out-of-sample pipeline before spending
the remaining Databento credit.

Approved request total: `$19.1006`.

## Packages

| Label | Schema | Period | Approved Cost | Size | DBN Files | SHA-256 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| ES replication OHLCV | `ohlcv-1m` | 2010-06-06 to 2020-06-01 | `$12.6435` | 43.07 MB | 120 | `7503bef4bcca4347e51541190e6a7372e2bb0b8baff7b6bcd53f3e98b9b88273` |
| ES OOS OHLCV | `ohlcv-1m` | 2021-01-01 to 2026-01-01 | `$6.4545` | 25.80 MB | 60 | `5859ea6fa94caa34b3899bb09aa5a45699e79202ea132b1a495c5485e1f850ba` |
| ES replication definitions | `definition` | 2010-06-06 to 2020-06-01 | `$0.0018` | 1.13 MB | 120 | `6f71d3ca9eb1e0ed9ac0d037efdbcabdf072880b28025e701131e3dae11eedf3` |
| ES OOS definitions | `definition` | 2021-01-01 to 2026-01-01 | `$0.0009` | 0.58 MB | 60 | `3da5ca4ca4099d44c16da26406d443af1cb0e53a8448d5e9c176cfa80dec2f08` |

Raw files are stored under `data/raw/databento/GLBX.MDP3/` and are ignored by
Git. The data check notes below summarize the local checks that were run after
download.

## OHLCV Data Check

| Segment | Rows | UTC Start | UTC End | Instrument Count | Duplicate Timestamps |
| --- | ---: | --- | --- | ---: | ---: |
| Replication | 3,463,223 | 2010-06-07 00:00:00+00:00 | 2020-05-31 23:59:00+00:00 | 41 | 0 |
| OOS | 1,767,973 | 2021-01-03 23:00:00+00:00 | 2025-12-31 21:59:00+00:00 | 21 | 0 |

Price and volume checks:

| Segment | Close Min | Close Max | Price Zeros | Price Missing | Volume Min | Volume Max | Volume Missing |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Replication | 1003.75 | 3397.00 | 0 | 0 | 1 | 192,341 | 0 |
| OOS | 3503.50 | 6992.75 | 0 | 0 | 1 | 185,625 | 0 |

The price scale and tick size are consistent with ES futures. Definitions show
`min_price_increment = 0.25`.

## Definitions Data Check

| Segment | Rows | Raw Symbol Count | Instrument Count | Expiration Count |
| --- | ---: | ---: | ---: | ---: |
| Replication | 3,131 | 40 | 41 | 41 |
| OOS | 1,569 | 21 | 21 | 21 |

Definitions include quarterly ES contracts such as `ESH`, `ESM`, `ESU`, and
`ESZ`. Expiration timestamps reflect daylight-saving-time differences in UTC.

## Paper Window Checks

For ES, the paper's effective trading day follows the underlying U.S. equity
market hours. The working data-check window is:

- Time zone: `America/New_York`
- Window: `09:30-16:00`
- Key boundaries checked: `09:30`, `10:00`, `15:30`, `16:00`

| Segment | Days Checked | Days Missing Any Boundary | Days Missing 15:30 | Days Missing 16:00 | Days With Any Missing Minute | Max Missing Minutes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Replication | 2,558 | 74 | 74 | 74 | 78 | 302 |
| OOS | 1,289 | 44 | 44 | 44 | 44 | 182 |

The boundary-problem examples are primarily U.S. holidays and early-close days
such as Independence Day observations, Thanksgiving, the day after
Thanksgiving, Christmas Eve, Martin Luther King Jr. Day, Presidents' Day, and
Memorial Day. These dates must be excluded or explicitly flagged in the daily
research table.

## Research Implications

- ES data is sufficiently complete to proceed with the daily research table.
- Trading calendar logic must remove holidays and early-close days before
  estimating paper variables.
- `instrument_id` switches are present and must be tracked.
- Returns must not combine boundary prices from different instruments.
- Raw Databento files need a private backup outside this repository.
