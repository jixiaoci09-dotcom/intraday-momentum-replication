# GC.v.0 January 2024 OHLCV-1m Sample Manifest

## Request

- Vendor: Databento
- Dataset: `GLBX.MDP3`
- Schema: `ohlcv-1m`
- Symbol: `GC.v.0`
- Input symbol type: `continuous`
- Output symbol type: `instrument_id`
- Start: `2024-01-01`
- End: `2024-02-01`
- Access mode: historical streaming
- Approved estimated cost: `$0.1076`

## Local Raw File

- Path: `data/raw/databento/GLBX.MDP3/ohlcv-1m/GC.v.0/GC.v.0_2024-01_ohlcv-1m.dbn.zst`
- File size: `0.43 MB`
- SHA-256: `38716d556be1afad326bdec9004c5e5269adf8f0dbe47381929ab57302cf88fc`
- Git status: ignored by `.gitignore`; not committed

## Parsed Metadata

- Dataset: `GLBX.MDP3`
- Schema: `ohlcv-1m`
- Start UTC: `2024-01-01 23:00:00+00:00`
- End UTC: `2024-01-31 23:59:00+00:00`
- Rows: `29,474`
- Timestamp index: `ts_event`, UTC
- Columns: `rtype`, `publisher_id`, `instrument_id`, `open`, `high`, `low`, `close`, `volume`

## Instrument Mapping

Databento metadata mapped the continuous symbol to two `instrument_id` values:

| Interval | instrument_id |
| --- | ---: |
| 2024-01-01 to 2024-01-31 | 41512 |
| 2024-01-31 to 2024-02-01 | 44740 |

Observed row counts:

| instrument_id | rows |
| ---: | ---: |
| 41512 | 28,098 |
| 44740 | 1,376 |

## Price And Volume Checks

| Field | Min | Max | Zero Count | Missing Count |
| --- | ---: | ---: | ---: | ---: |
| open | 2005.0 | 2088.0 | 0 | 0 |
| high | 2005.4 | 2088.1 | 0 | 0 |
| low | 2004.0 | 2087.3 | 0 | 0 |
| close | 2005.0 | 2087.9 | 0 | 0 |
| volume | 1 | 5930 | 0 | 0 |

The price scale is consistent with COMEX gold futures quoted in USD per troy
ounce.

## Paper Window Checks

The paper's GC trading window is `08:20-13:30` New York time. For this product:

- `P_{c-30,t}` is the `13:00` New York bar.
- `P_{c,t}` is the `13:30` New York bar.

Most January 2024 dates have complete minute coverage in this window.

Important exceptions:

| New York date | Rows in 08:20-13:30 | Missing minutes | Missing key boundaries | instrument_id |
| --- | ---: | ---: | --- | --- |
| 2024-01-15 | 310 | 1 | none | 41512 |
| 2024-01-30 | 217 | 94 | `08:20`, `13:00` | 41512 |
| 2024-01-31 | 311 | 0 | none | 44740 |

The `2024-01-30` observation is not suitable for research-table construction
because a key boundary price is missing. It is also near the continuous-contract
roll and should be treated as a roll/liquidity edge case.

## Public Cross-Check

Free public charts did not provide reliable historical one-minute GC futures
bars for January 2024. A price-level sanity check was performed with public
daily/spot gold data. The check supports the downloaded data's price scale but
does not validate minute boundaries.

Selected comparisons:

| Date | Databento GC.v.0 minute-derived close | Public spot gold close | Assessment |
| --- | ---: | ---: | --- |
| 2024-01-03 | 2050.3 | 2043.06 | broadly consistent |
| 2024-01-10 | 2036.1 | 2026.94 | broadly consistent |
| 2024-01-24 | 2015.5 | 2016.53 | close |
| 2024-01-31 | 2057.2 | 2039.88 | different, likely roll/contract basis |

## Research Implications

- Continuous futures data must be checked for `instrument_id` switches.
- Roll dates must not combine prior-day close from one instrument with current
  day boundary prices from another instrument.
- Days with missing `P_{c-30,t}` or `P_{c,t}` must be excluded or explicitly
  flagged.
- Public chart validation is insufficient for historical minute-boundary
  validation; definitions, mappings, and direct data QA are required.
