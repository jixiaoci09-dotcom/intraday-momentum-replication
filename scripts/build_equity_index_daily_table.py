#!/usr/bin/env python3
"""Build a daily research table for ES/NQ-style U.S. equity index futures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import databento as db
import pandas as pd
import pandas_market_calendars as mcal


DATASET = "GLBX.MDP3"
RAW_ROOT = Path("data/raw/databento") / DATASET / "ohlcv-1m"
PROCESSED_ROOT = Path("data/processed")
MANIFEST_ROOT = Path("data/manifests")

PACKAGES = [
    {
        "segment": "replication",
        "calendar_start": "2010-06-07",
        "calendar_end": "2020-05-31",
        "path_part": "replication_2010-06-06_2020-06-01",
    },
    {
        "segment": "oos",
        "calendar_start": "2021-01-01",
        "calendar_end": "2025-12-31",
        "path_part": "oos_2021-01-01_2026-01-01",
    },
]

BOUNDARY_CLOCKS = ["09:30", "10:00", "15:00", "15:30", "16:00"]
RESEARCH_CLOCKS = ["10:00", "15:00", "15:30", "16:00"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", required=True, help="Continuous symbol, e.g. NQ.v.0")
    return parser.parse_args()


def symbol_prefix(symbol: str) -> str:
    return symbol.split(".")[0].lower()


def find_zip(symbol: str, path_part: str) -> Path:
    directory = RAW_ROOT / symbol / path_part
    candidates = sorted(directory.glob("**/*.zip"))
    if len(candidates) != 1:
        raise FileNotFoundError(f"Expected one zip under {directory}, found {len(candidates)}")
    return candidates[0]


def packages_for_symbol(symbol: str) -> list[dict[str, Any]]:
    packages = []
    for package in PACKAGES:
        item = dict(package)
        item["path"] = find_zip(symbol, package["path_part"])
        packages.append(item)
    return packages


def is_present(value: Any) -> bool:
    return pd.notna(value)


def one_value(group: pd.DataFrame, column: str, clock: str) -> Any:
    values = group.loc[group["ny_clock"] == clock, column]
    if values.empty:
        return None
    return values.iloc[-1]


def load_rows(package: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    boundary_rows = []
    volume_rows = []
    with ZipFile(package["path"]) as zip_file:
        dbn_names = sorted(name for name in zip_file.namelist() if name.endswith(".dbn.zst"))
        for name in dbn_names:
            store = db.DBNStore.from_bytes(zip_file.read(name))
            df = store.to_df(price_type="float", pretty_ts=True, map_symbols=False)
            if df.empty:
                continue

            local = df.reset_index()
            local["ny_time"] = local["ts_event"].dt.tz_convert("America/New_York")
            local["trade_date"] = local["ny_time"].dt.date.astype(str)
            local["ny_clock"] = local["ny_time"].dt.strftime("%H:%M")
            local["segment"] = package["segment"]

            boundaries = local[local["ny_clock"].isin(BOUNDARY_CLOCKS)].copy()
            if not boundaries.empty:
                boundaries["source_zip"] = package["path"].name
                boundaries["source_member"] = name
                boundary_rows.append(
                    boundaries[
                        [
                            "segment",
                            "trade_date",
                            "ny_clock",
                            "ts_event",
                            "ny_time",
                            "instrument_id",
                            "close",
                            "volume",
                            "source_zip",
                            "source_member",
                        ]
                    ]
                )

            window = local[(local["ny_clock"] >= "09:30") & (local["ny_clock"] <= "16:00")]
            if not window.empty:
                grouped = window.groupby(["segment", "trade_date"], as_index=False).agg(
                    volume_0930_1600=("volume", "sum"),
                    rows_0930_1600=("volume", "size"),
                    instruments_0930_1600=("instrument_id", lambda values: ",".join(map(str, sorted(set(values))))),
                )
                last_half_hour = window[(window["ny_clock"] >= "15:30") & (window["ny_clock"] <= "16:00")]
                lh_grouped = last_half_hour.groupby(["segment", "trade_date"], as_index=False).agg(
                    volume_1530_1600=("volume", "sum"),
                    rows_1530_1600=("volume", "size"),
                )
                grouped = grouped.merge(lh_grouped, on=["segment", "trade_date"], how="left")
                volume_rows.append(grouped)

    boundaries_out = pd.concat(boundary_rows, ignore_index=True) if boundary_rows else pd.DataFrame()
    volumes_out = pd.concat(volume_rows, ignore_index=True) if volume_rows else pd.DataFrame()
    if not volumes_out.empty:
        volumes_out = volumes_out.groupby(["segment", "trade_date"], as_index=False).agg(
            volume_0930_1600=("volume_0930_1600", "sum"),
            rows_0930_1600=("rows_0930_1600", "sum"),
            volume_1530_1600=("volume_1530_1600", "sum"),
            rows_1530_1600=("rows_1530_1600", "sum"),
            instruments_0930_1600=("instruments_0930_1600", lambda values: ",".join(sorted(set(",".join(values).split(","))))),
        )
    return boundaries_out, volumes_out


def load_nyse_calendar(packages: list[dict[str, Any]]) -> pd.DataFrame:
    nyse = mcal.get_calendar("NYSE")
    calendars = []
    for package in packages:
        schedule = nyse.schedule(
            start_date=package["calendar_start"],
            end_date=package["calendar_end"],
        )
        calendar = schedule.copy()
        calendar["trade_date"] = calendar.index.date.astype(str)
        calendar["segment"] = package["segment"]
        calendar["nyse_close_ny"] = calendar["market_close"].dt.tz_convert("America/New_York")
        calendar["nyse_close_clock"] = calendar["nyse_close_ny"].dt.strftime("%H:%M")
        calendar["nyse_is_regular_close"] = calendar["nyse_close_clock"] == "16:00"
        calendars.append(
            calendar[
                [
                    "segment",
                    "trade_date",
                    "market_open",
                    "market_close",
                    "nyse_close_clock",
                    "nyse_is_regular_close",
                ]
            ].reset_index(drop=True)
        )
    return pd.concat(calendars, ignore_index=True)


def build_boundary_table(boundaries: pd.DataFrame, volumes: pd.DataFrame, packages: list[dict[str, Any]]) -> pd.DataFrame:
    date_rows: list[dict[str, Any]] = []
    for (segment, trade_date), group in boundaries.groupby(["segment", "trade_date"], sort=True):
        clocks = set(group["ny_clock"])
        missing = [clock for clock in BOUNDARY_CLOCKS if clock not in clocks]
        ids_by_clock = {clock: one_value(group, "instrument_id", clock) for clock in BOUNDARY_CLOCKS}
        closes_by_clock = {clock: one_value(group, "close", clock) for clock in BOUNDARY_CLOCKS}
        ts_by_clock = {clock: one_value(group, "ts_event", clock) for clock in BOUNDARY_CLOCKS}
        current_research_ids = [
            ids_by_clock[clock] for clock in RESEARCH_CLOCKS if ids_by_clock[clock] is not None
        ]
        current_same_instrument = len(set(current_research_ids)) == 1 if current_research_ids else False

        date_rows.append(
            {
                "segment": segment,
                "trade_date": trade_date,
                "has_current_boundaries": not missing,
                "missing_boundaries": missing,
                "current_same_instrument": current_same_instrument,
                "instrument_0930": ids_by_clock["09:30"],
                "instrument_1000": ids_by_clock["10:00"],
                "instrument_1500": ids_by_clock["15:00"],
                "instrument_1530": ids_by_clock["15:30"],
                "instrument_1600": ids_by_clock["16:00"],
                "p_0930": closes_by_clock["09:30"],
                "p_1000": closes_by_clock["10:00"],
                "p_1500": closes_by_clock["15:00"],
                "p_1530": closes_by_clock["15:30"],
                "p_1600": closes_by_clock["16:00"],
                "ts_0930": ts_by_clock["09:30"],
                "ts_1000": ts_by_clock["10:00"],
                "ts_1500": ts_by_clock["15:00"],
                "ts_1530": ts_by_clock["15:30"],
                "ts_1600": ts_by_clock["16:00"],
            }
        )

    boundary_table = pd.DataFrame(date_rows)
    nyse_calendar = load_nyse_calendar(packages)
    boundary_table = boundary_table.merge(nyse_calendar, on=["segment", "trade_date"], how="outer")
    boundary_table = boundary_table.merge(volumes, on=["segment", "trade_date"], how="left")
    boundary_table = boundary_table.sort_values(["segment", "trade_date"]).reset_index(drop=True)

    for column in ["has_current_boundaries", "current_same_instrument"]:
        boundary_table[column] = boundary_table[column].map(
            lambda value: bool(value) if pd.notna(value) else False
        )
    boundary_table["nyse_is_trading_day"] = boundary_table["market_open"].notna()
    boundary_table["nyse_is_regular_close"] = boundary_table["nyse_is_regular_close"].map(
        lambda value: bool(value) if pd.notna(value) else False
    )
    boundary_table["nyse_close_clock"] = boundary_table["nyse_close_clock"].fillna("")
    return boundary_table


def build_daily(boundary_table: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for segment, segment_table in boundary_table.groupby("segment", sort=False):
        prev_close_candidates = segment_table[
            segment_table["p_1600"].notna() & segment_table["instrument_1600"].notna()
        ][["trade_date", "p_1600", "instrument_1600", "ts_1600"]].copy()

        for row in segment_table.itertuples(index=False):
            current_ok = bool(row.has_current_boundaries and row.current_same_instrument)
            current_instrument = row.instrument_1000 if current_ok else None

            prior = prev_close_candidates[prev_close_candidates["trade_date"] < row.trade_date].tail(1)
            has_prev_close = not prior.empty
            if has_prev_close:
                prev = prior.iloc[0]
                p_prev_close = float(prev["p_1600"])
                prev_instrument = int(prev["instrument_1600"])
                prev_trade_date = str(prev["trade_date"])
                ts_prev_close = prev["ts_1600"]
            else:
                p_prev_close = None
                prev_instrument = None
                prev_trade_date = None
                ts_prev_close = None

            same_instrument_as_prev = (
                current_ok and has_prev_close and int(current_instrument) == int(prev_instrument)
            )
            include = bool(current_ok and has_prev_close and same_instrument_as_prev)

            reason = []
            if not row.has_current_boundaries:
                if not row.nyse_is_trading_day:
                    reason.append("nyse_closed")
                elif not row.nyse_is_regular_close:
                    reason.append("nyse_early_close")
                else:
                    reason.append("missing_boundary_on_regular_day")
            if row.has_current_boundaries and not row.current_same_instrument:
                reason.append("current_boundaries_cross_instrument")
            if not has_prev_close:
                reason.append("missing_previous_close")
            if current_ok and has_prev_close and not same_instrument_as_prev:
                reason.append("previous_close_cross_instrument")

            record = {
                "trade_date": row.trade_date,
                "segment": segment,
                "include": include,
                "exclude_reason": ";".join(reason),
                "prev_trade_date": prev_trade_date,
                "instrument_id": int(current_instrument) if current_instrument is not None else None,
                "prev_close_instrument_id": prev_instrument,
                "p_prev_close": p_prev_close,
                "p_open_plus_30": float(row.p_1000) if is_present(row.p_1000) else None,
                "p_close_minus_60": float(row.p_1500) if is_present(row.p_1500) else None,
                "p_close_minus_30": float(row.p_1530) if is_present(row.p_1530) else None,
                "p_close": float(row.p_1600) if is_present(row.p_1600) else None,
                "ts_prev_close_utc": ts_prev_close,
                "ts_open_plus_30_utc": row.ts_1000,
                "ts_close_minus_60_utc": row.ts_1500,
                "ts_close_minus_30_utc": row.ts_1530,
                "ts_close_utc": row.ts_1600,
                "volume_0930_1600": float(row.volume_0930_1600) if is_present(row.volume_0930_1600) else None,
                "volume_1530_1600": float(row.volume_1530_1600) if is_present(row.volume_1530_1600) else None,
                "rows_0930_1600": int(row.rows_0930_1600) if is_present(row.rows_0930_1600) else 0,
                "rows_1530_1600": int(row.rows_1530_1600) if is_present(row.rows_1530_1600) else 0,
                "has_0930": is_present(row.p_0930),
                "has_1000": is_present(row.p_1000),
                "has_1500": is_present(row.p_1500),
                "has_1530": is_present(row.p_1530),
                "has_1600": is_present(row.p_1600),
                "current_same_instrument": bool(row.current_same_instrument),
                "same_instrument_as_prev": bool(same_instrument_as_prev),
                "nyse_is_trading_day": bool(row.nyse_is_trading_day),
                "nyse_is_regular_close": bool(row.nyse_is_regular_close),
                "nyse_close_clock": row.nyse_close_clock,
            }

            if include:
                record["r_ONFH"] = record["p_open_plus_30"] / record["p_prev_close"] - 1
                record["r_M"] = record["p_close_minus_60"] / record["p_open_plus_30"] - 1
                record["r_SLH"] = record["p_close_minus_30"] / record["p_close_minus_60"] - 1
                record["r_ROD"] = record["p_close_minus_30"] / record["p_prev_close"] - 1
                record["r_LH"] = record["p_close"] / record["p_close_minus_30"] - 1
            else:
                record["r_ONFH"] = None
                record["r_M"] = None
                record["r_SLH"] = None
                record["r_ROD"] = None
                record["r_LH"] = None

            records.append(record)

    daily = pd.DataFrame(records).sort_values(["segment", "trade_date"])
    summary = {
        "rows_total": int(len(daily)),
        "rows_included": int(daily["include"].sum()),
        "rows_excluded": int((~daily["include"]).sum()),
        "nyse_trading_days": int(daily["nyse_is_trading_day"].sum()),
        "nyse_regular_close_days": int(daily["nyse_is_regular_close"].sum()),
        "included_by_segment": {
            key: int(value)
            for key, value in daily[daily["include"]]["segment"].value_counts().sort_index().items()
        },
        "excluded_by_reason": {
            key: int(value)
            for key, value in daily.loc[~daily["include"], "exclude_reason"].value_counts().sort_index().items()
        },
        "excluded_by_nyse_close_clock": {
            str(key): int(value)
            for key, value in daily.loc[~daily["include"], "nyse_close_clock"].value_counts().sort_index().items()
        },
        "date_min": str(daily["trade_date"].min()),
        "date_max": str(daily["trade_date"].max()),
        "return_summary_included": {},
    }
    included = daily[daily["include"]]
    for column in ["r_ONFH", "r_M", "r_SLH", "r_ROD", "r_LH"]:
        summary["return_summary_included"][column] = {
            "count": int(included[column].count()),
            "mean": float(included[column].mean()),
            "std": float(included[column].std()),
            "min": float(included[column].min()),
            "max": float(included[column].max()),
        }
    return daily, summary


def main() -> None:
    args = parse_args()
    symbol = args.symbol
    prefix = symbol_prefix(symbol)
    packages = packages_for_symbol(symbol)
    loaded = [load_rows(package) for package in packages]
    boundaries = pd.concat([item[0] for item in loaded], ignore_index=True)
    volumes = pd.concat([item[1] for item in loaded], ignore_index=True)
    boundary_table = build_boundary_table(boundaries, volumes, packages)
    daily, summary = build_daily(boundary_table)
    summary["symbol"] = symbol
    summary["dataset"] = DATASET
    summary["effective_window"] = "09:30-16:00 America/New_York"
    summary["required_boundaries"] = BOUNDARY_CLOCKS

    out_parquet = PROCESSED_ROOT / f"{prefix}_daily_research_table.parquet"
    out_summary = MANIFEST_ROOT / f"{prefix}_daily_research_table_summary.json"
    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    daily.to_parquet(out_parquet, index=False)
    out_summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"{symbol} daily research table built")
    print(f"rows total:    {summary['rows_total']:,}")
    print(f"rows included: {summary['rows_included']:,}")
    print(f"rows excluded: {summary['rows_excluded']:,}")
    print(f"included by segment: {summary['included_by_segment']}")
    print(f"excluded by reason: {summary['excluded_by_reason']}")
    print(f"parquet: {out_parquet}")
    print(f"summary: {out_summary}")


if __name__ == "__main__":
    main()
