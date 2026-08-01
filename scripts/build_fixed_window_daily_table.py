#!/usr/bin/env python3
"""Build a daily research table for a symbol with a fixed paper trading window."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import databento as db
import pandas as pd
import pandas_market_calendars as mcal

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from intraday_momentum.boundaries import (
    NY_TZ,
    REQUIRED_FIELDS,
    STAT_CLOSE_FIELDS,
    SymbolWindow,
    boundary_plan,
    boundary_value,
    missing_required_sources,
    required_source_clocks,
    source_clock_for_field,
)


DATASET = "GLBX.MDP3"
PIPELINE_VERSION = "boundary_corrected_v1"
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", required=True, help="Continuous symbol, e.g. GC.v.0")
    parser.add_argument("--calendar", required=True, help="pandas-market-calendars calendar name")
    parser.add_argument("--window-start", required=True, help="Effective open clock, e.g. 08:20")
    parser.add_argument("--open-plus-30", required=True, help="Open plus 30 minutes, e.g. 08:50")
    parser.add_argument("--close-minus-60", required=True, help="Close minus 60 minutes, e.g. 12:30")
    parser.add_argument("--close-minus-30", required=True, help="Close minus 30 minutes, e.g. 13:00")
    parser.add_argument("--close", required=True, help="Effective close clock, e.g. 13:30")
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
    values = group.loc[group["clock"] == clock, column]
    if values.empty:
        return None
    return values.iloc[-1]


def load_rows(package: dict[str, Any], window: SymbolWindow) -> tuple[pd.DataFrame, pd.DataFrame]:
    source_clocks = required_source_clocks(window, include_entry=True)
    close_source_clock = source_clock_for_field(window, "close")
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
            local["ny_time"] = local["ts_event"].dt.tz_convert(NY_TZ)
            local["trade_date"] = local["ny_time"].dt.date.astype(str)
            local["clock"] = local["ny_time"].dt.strftime("%H:%M")
            local["segment"] = package["segment"]

            boundaries = local[local["clock"].isin(source_clocks)].copy()
            if not boundaries.empty:
                boundaries["source_zip"] = package["path"].name
                boundaries["source_member"] = name
                boundary_rows.append(
                    boundaries[
                        [
                            "segment",
                            "trade_date",
                            "clock",
                            "ts_event",
                            "ny_time",
                            "instrument_id",
                            "open",
                            "close",
                            "volume",
                            "source_zip",
                            "source_member",
                        ]
                    ]
                )

            window_rows = local[
                (local["clock"] >= window.window_start) & (local["clock"] <= close_source_clock)
            ]
            if not window_rows.empty:
                grouped = window_rows.groupby(["segment", "trade_date"], as_index=False).agg(
                    volume_effective_window=("volume", "sum"),
                    rows_effective_window=("volume", "size"),
                    instruments_effective_window=("instrument_id", lambda values: ",".join(map(str, sorted(set(values))))),
                )
                last_half_hour = window_rows[
                    (window_rows["clock"] >= window.close_minus_30)
                    & (window_rows["clock"] <= close_source_clock)
                ]
                lh_grouped = last_half_hour.groupby(["segment", "trade_date"], as_index=False).agg(
                    volume_last_half_hour=("volume", "sum"),
                    rows_last_half_hour=("volume", "size"),
                )
                grouped = grouped.merge(lh_grouped, on=["segment", "trade_date"], how="left")
                volume_rows.append(grouped)

    boundaries_out = pd.concat(boundary_rows, ignore_index=True) if boundary_rows else pd.DataFrame()
    volumes_out = pd.concat(volume_rows, ignore_index=True) if volume_rows else pd.DataFrame()
    if not volumes_out.empty:
        volumes_out = volumes_out.groupby(["segment", "trade_date"], as_index=False).agg(
            volume_effective_window=("volume_effective_window", "sum"),
            rows_effective_window=("rows_effective_window", "sum"),
            volume_last_half_hour=("volume_last_half_hour", "sum"),
            rows_last_half_hour=("rows_last_half_hour", "sum"),
            instruments_effective_window=(
                "instruments_effective_window",
                lambda values: ",".join(sorted(set(",".join(values).split(",")))),
            ),
        )
    return boundaries_out, volumes_out


def load_calendar(packages: list[dict[str, Any]], calendar_name: str, effective_close: str) -> pd.DataFrame:
    calendar = mcal.get_calendar(calendar_name)
    rows = []
    for package in packages:
        schedule = calendar.schedule(
            start_date=package["calendar_start"],
            end_date=package["calendar_end"],
        )
        part = schedule.copy()
        part["trade_date"] = part.index.date.astype(str)
        part["segment"] = package["segment"]
        part["calendar_close_ny"] = part["market_close"].dt.tz_convert(NY_TZ)
        part["calendar_close_clock"] = part["calendar_close_ny"].dt.strftime("%H:%M")
        part["calendar_has_effective_close"] = part["calendar_close_clock"] >= effective_close
        rows.append(
            part[
                [
                    "segment",
                    "trade_date",
                    "market_open",
                    "market_close",
                    "calendar_close_clock",
                    "calendar_has_effective_close",
                ]
            ].reset_index(drop=True)
        )
    return pd.concat(rows, ignore_index=True)


def build_boundary_table(
    boundaries: pd.DataFrame,
    volumes: pd.DataFrame,
    packages: list[dict[str, Any]],
    calendar_name: str,
    window: SymbolWindow,
) -> pd.DataFrame:
    source_clocks = required_source_clocks(window, include_entry=True)
    plan = boundary_plan(window, include_entry=True)
    date_rows: list[dict[str, Any]] = []
    for (segment, trade_date), group in boundaries.groupby(["segment", "trade_date"], sort=True):
        present_clocks = set(group["clock"])
        missing = missing_required_sources(present_clocks, window, include_entry=True)
        ids_by_clock = {clock: one_value(group, "instrument_id", clock) for clock in source_clocks}
        ts_by_clock = {clock: one_value(group, "ts_event", clock) for clock in source_clocks}
        current_research_ids = [ids_by_clock[item["source_clock"]] for item in plan if ids_by_clock[item["source_clock"]] is not None]
        current_same_instrument = len(set(current_research_ids)) == 1 if current_research_ids else False
        values = {
            item["field"]: boundary_value(group, item["source_clock"], item["price_column"])
            for item in plan
        }
        ts_values = {
            item["field"]: ts_by_clock[item["source_clock"]]
            for item in plan
        }
        id_values = {
            item["field"]: ids_by_clock[item["source_clock"]]
            for item in plan
        }

        date_rows.append(
            {
                "segment": segment,
                "trade_date": trade_date,
                "has_current_boundaries": not missing,
                "missing_boundaries": missing,
                "current_same_instrument": current_same_instrument,
                "instrument_window_start": id_values["window_start"],
                "instrument_open_plus_30": id_values["open_plus_30"],
                "instrument_close_minus_60": id_values["close_minus_60"],
                "instrument_close_minus_30": id_values["close_minus_30"],
                "instrument_close": id_values["close"],
                "instrument_lh_entry_next_open": id_values["lh_entry_next_open"],
                "p_window_start": values["window_start"],
                "p_open_plus_30": values["open_plus_30"],
                "p_close_minus_60": values["close_minus_60"],
                "p_close_minus_30": values["close_minus_30"],
                "p_close": values["close"],
                "p_lh_entry_next_open": values["lh_entry_next_open"],
                "ts_window_start": ts_values["window_start"],
                "ts_open_plus_30": ts_values["open_plus_30"],
                "ts_close_minus_60": ts_values["close_minus_60"],
                "ts_close_minus_30": ts_values["close_minus_30"],
                "ts_close": ts_values["close"],
                "ts_lh_entry_next_open": ts_values["lh_entry_next_open"],
            }
        )

    boundary_table = pd.DataFrame(date_rows)
    product_calendar = load_calendar(packages, calendar_name, window.close)
    boundary_table = boundary_table.merge(product_calendar, on=["segment", "trade_date"], how="outer")
    boundary_table = boundary_table.merge(volumes, on=["segment", "trade_date"], how="left")
    boundary_table = boundary_table.sort_values(["segment", "trade_date"]).reset_index(drop=True)
    for column in ["has_current_boundaries", "current_same_instrument"]:
        boundary_table[column] = boundary_table[column].map(
            lambda value: bool(value) if pd.notna(value) else False
        )
    boundary_table["calendar_is_trading_day"] = boundary_table["market_open"].notna()
    boundary_table["calendar_has_effective_close"] = boundary_table[
        "calendar_has_effective_close"
    ].map(lambda value: bool(value) if pd.notna(value) else False)
    boundary_table["calendar_close_clock"] = boundary_table["calendar_close_clock"].fillna("")
    return boundary_table


def build_daily(boundary_table: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for segment, segment_table in boundary_table.groupby("segment", sort=False):
        prev_close_candidates = segment_table[
            segment_table["p_close"].notna() & segment_table["instrument_close"].notna()
        ][["trade_date", "p_close", "instrument_close", "ts_close"]].copy()

        for row in segment_table.itertuples(index=False):
            current_ok = bool(row.has_current_boundaries and row.current_same_instrument)
            current_instrument = row.instrument_open_plus_30 if current_ok else None
            prior = prev_close_candidates[prev_close_candidates["trade_date"] < row.trade_date].tail(1)
            has_prev_close = not prior.empty
            if has_prev_close:
                prev = prior.iloc[0]
                p_prev_close = float(prev["p_close"])
                prev_instrument = int(prev["instrument_close"])
                prev_trade_date = str(prev["trade_date"])
                ts_prev_close = prev["ts_close"]
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
                if not row.calendar_is_trading_day:
                    reason.append("calendar_closed")
                elif not row.calendar_has_effective_close:
                    reason.append("calendar_early_close_before_effective_close")
                else:
                    reason.append("missing_exact_boundary_source_on_calendar_day")
            if row.has_current_boundaries and not row.current_same_instrument:
                reason.append("current_boundaries_cross_instrument")
            if not has_prev_close:
                reason.append("missing_previous_close")
            if current_ok and has_prev_close and not same_instrument_as_prev:
                reason.append("previous_close_cross_instrument")

            record = {
                "pipeline_version": PIPELINE_VERSION,
                "trade_date": row.trade_date,
                "segment": segment,
                "include": include,
                "exclude_reason": ";".join(reason),
                "drop_reason": ";".join(reason),
                "missing_boundary_sources": ",".join(row.missing_boundaries) if isinstance(row.missing_boundaries, list) else "",
                "prev_trade_date": prev_trade_date,
                "instrument_id": int(current_instrument) if current_instrument is not None else None,
                "prev_close_instrument_id": prev_instrument,
                "p_prev_close": p_prev_close,
                "p_window_start": float(row.p_window_start) if is_present(row.p_window_start) else None,
                "p_open_plus_30": float(row.p_open_plus_30) if is_present(row.p_open_plus_30) else None,
                "p_close_minus_60": float(row.p_close_minus_60) if is_present(row.p_close_minus_60) else None,
                "p_close_minus_30": float(row.p_close_minus_30) if is_present(row.p_close_minus_30) else None,
                "p_close": float(row.p_close) if is_present(row.p_close) else None,
                "p_lh_entry_next_open": float(row.p_lh_entry_next_open) if is_present(row.p_lh_entry_next_open) else None,
                "ts_prev_close_utc": ts_prev_close,
                "ts_window_start_utc": row.ts_window_start,
                "ts_open_plus_30_utc": row.ts_open_plus_30,
                "ts_close_minus_60_utc": row.ts_close_minus_60,
                "ts_close_minus_30_utc": row.ts_close_minus_30,
                "ts_close_utc": row.ts_close,
                "ts_lh_entry_next_open_utc": row.ts_lh_entry_next_open,
                "volume_effective_window": float(row.volume_effective_window) if is_present(row.volume_effective_window) else None,
                "volume_last_half_hour": float(row.volume_last_half_hour) if is_present(row.volume_last_half_hour) else None,
                "rows_effective_window": int(row.rows_effective_window) if is_present(row.rows_effective_window) else 0,
                "rows_last_half_hour": int(row.rows_last_half_hour) if is_present(row.rows_last_half_hour) else 0,
                "has_window_start": is_present(row.p_window_start),
                "has_open_plus_30": is_present(row.p_open_plus_30),
                "has_close_minus_60": is_present(row.p_close_minus_60),
                "has_close_minus_30": is_present(row.p_close_minus_30),
                "has_close": is_present(row.p_close),
                "has_lh_entry_next_open": is_present(row.p_lh_entry_next_open),
                "current_same_instrument": bool(row.current_same_instrument),
                "same_instrument_as_prev": bool(same_instrument_as_prev),
                "calendar_is_trading_day": bool(row.calendar_is_trading_day),
                "calendar_has_effective_close": bool(row.calendar_has_effective_close),
                "calendar_close_clock": row.calendar_close_clock,
            }
            if include:
                record["r_ONFH"] = record["p_open_plus_30"] / record["p_prev_close"] - 1
                record["r_M"] = record["p_close_minus_60"] / record["p_open_plus_30"] - 1
                record["r_SLH"] = record["p_close_minus_30"] / record["p_close_minus_60"] - 1
                record["r_ROD"] = record["p_close_minus_30"] / record["p_prev_close"] - 1
                record["r_LH"] = record["p_close"] / record["p_close_minus_30"] - 1
                record["r_LH_executable"] = (
                    record["p_close"] / record["p_lh_entry_next_open"] - 1
                    if record["p_lh_entry_next_open"] is not None
                    else None
                )
            else:
                record["r_ONFH"] = None
                record["r_M"] = None
                record["r_SLH"] = None
                record["r_ROD"] = None
                record["r_LH"] = None
                record["r_LH_executable"] = None
            records.append(record)

    daily = pd.DataFrame(records).sort_values(["segment", "trade_date"])
    summary = {
        "rows_total": int(len(daily)),
        "rows_included": int(daily["include"].sum()),
        "rows_excluded": int((~daily["include"]).sum()),
        "calendar_trading_days": int(daily["calendar_is_trading_day"].sum()),
        "calendar_effective_close_days": int(daily["calendar_has_effective_close"].sum()),
        "included_by_segment": {
            key: int(value)
            for key, value in daily[daily["include"]]["segment"].value_counts().sort_index().items()
        },
        "excluded_by_reason": {
            key: int(value)
            for key, value in daily.loc[~daily["include"], "exclude_reason"].value_counts().sort_index().items()
        },
        "excluded_by_calendar_close_clock": {
            str(key): int(value)
            for key, value in daily.loc[~daily["include"], "calendar_close_clock"].value_counts().sort_index().items()
        },
        "date_min": str(daily["trade_date"].min()),
        "date_max": str(daily["trade_date"].max()),
        "return_summary_included": {},
    }
    included = daily[daily["include"]]
    for column in ["r_ONFH", "r_M", "r_SLH", "r_ROD", "r_LH", "r_LH_executable"]:
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
    window = SymbolWindow(
        symbol=symbol,
        calendar=args.calendar,
        window_start=args.window_start,
        open_plus_30=args.open_plus_30,
        close_minus_60=args.close_minus_60,
        close_minus_30=args.close_minus_30,
        close=args.close,
    )
    packages = packages_for_symbol(symbol)
    loaded = [load_rows(package, window) for package in packages]
    boundaries = pd.concat([item[0] for item in loaded], ignore_index=True)
    volumes = pd.concat([item[1] for item in loaded], ignore_index=True)
    boundary_table = build_boundary_table(boundaries, volumes, packages, args.calendar, window)
    daily, summary = build_daily(boundary_table)
    summary["symbol"] = symbol
    summary["dataset"] = DATASET
    summary["pipeline_version"] = PIPELINE_VERSION
    summary["calendar"] = args.calendar
    summary["timezone"] = NY_TZ
    summary["effective_window"] = f"{args.window_start}-{args.close}"
    summary["theoretical_boundary_clocks"] = {
        field: getattr(window, field) for field in REQUIRED_FIELDS
    }
    summary["source_boundary_clocks"] = {
        field: source_clock_for_field(window, field) for field in REQUIRED_FIELDS
    }
    summary["source_boundary_rule"] = "OHLCV-1m ts_event is interval start; non-open boundary prices use T-1 minute bar close"
    summary["session_open_rule"] = "session open price uses ts_event == open time bar open"
    summary["executable_lh_entry_rule"] = "entry price uses ts_event == close_minus_30 theoretical boundary bar open"

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
