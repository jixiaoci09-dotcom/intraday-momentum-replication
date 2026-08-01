#!/usr/bin/env python3
"""Print corrected boundary sources for manual inspection without writing files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import databento as db
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from intraday_momentum.boundaries import (
    NY_TZ,
    SYMBOL_WINDOWS,
    boundary_plan,
    source_clock_for_field,
    symbol_prefix,
)


DATASET = "GLBX.MDP3"
RAW_ROOT = Path("data/raw/databento") / DATASET / "ohlcv-1m"
SYMBOLS = ["ES.v.0", "NQ.v.0", "GC.v.0", "CL.v.0", "ZN.v.0", "6E.v.0"]
PACKAGES = [
    ("replication", "2010-06-06", "2020-06-01", "replication_2010-06-06_2020-06-01"),
    ("oos", "2021-01-01", "2026-01-01", "oos_2021-01-01_2026-01-01"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default="2019-01-15", help="New York trade date to inspect")
    parser.add_argument("--symbols", nargs="*", default=SYMBOLS)
    return parser.parse_args()


def package_for_date(symbol: str, trade_date: str) -> Path:
    day = pd.Timestamp(trade_date)
    for _segment, start, end, path_part in PACKAGES:
        if pd.Timestamp(start) <= day < pd.Timestamp(end):
            directory = RAW_ROOT / symbol / path_part
            candidates = sorted(directory.glob("**/*.zip"))
            if len(candidates) != 1:
                raise FileNotFoundError(f"Expected one zip under {directory}, found {len(candidates)}")
            return candidates[0]
    raise ValueError(f"No local package configured for {trade_date}")


def candidate_months(trade_date: str, previous_date: str) -> set[str]:
    return {
        pd.Timestamp(trade_date).strftime("%Y%m"),
        pd.Timestamp(previous_date).strftime("%Y%m"),
    }


def load_local_rows(symbol: str, trade_date: str, previous_date: str) -> pd.DataFrame:
    zip_path = package_for_date(symbol, trade_date)
    months = candidate_months(trade_date, previous_date)
    frames = []
    with ZipFile(zip_path) as zip_file:
        for name in sorted(n for n in zip_file.namelist() if n.endswith(".dbn.zst")):
            if not any(month in name for month in months):
                continue
            store = db.DBNStore.from_bytes(zip_file.read(name))
            df = store.to_df(price_type="float", pretty_ts=True, map_symbols=False)
            if df.empty:
                continue
            local = df.reset_index()
            local["ny_time"] = local["ts_event"].dt.tz_convert(NY_TZ)
            local["trade_date"] = local["ny_time"].dt.date.astype(str)
            local["clock"] = local["ny_time"].dt.strftime("%H:%M")
            frames.append(local)
    if not frames:
        raise ValueError(f"No rows loaded for {symbol} around {trade_date}")
    return pd.concat(frames, ignore_index=True)


def value_at(rows: pd.DataFrame, trade_date: str, source_clock: str, price_column: str) -> dict[str, Any]:
    hit = rows[(rows["trade_date"] == trade_date) & (rows["clock"] == source_clock)]
    if hit.empty:
        return {
            "source_ts_utc": None,
            "source_ts_ny": None,
            "price_column": price_column,
            "price": None,
            "instrument_id": None,
        }
    row = hit.iloc[-1]
    ts = pd.Timestamp(row["ts_event"])
    return {
        "source_ts_utc": ts.isoformat(),
        "source_ts_ny": ts.tz_convert(NY_TZ).isoformat(),
        "price_column": price_column,
        "price": float(row[price_column]),
        "instrument_id": int(row["instrument_id"]),
    }


def inspect_symbol(symbol: str, trade_date: str) -> None:
    window = SYMBOL_WINDOWS[symbol]
    previous_date = (pd.Timestamp(trade_date) - pd.tseries.offsets.BDay(1)).date().isoformat()
    rows = load_local_rows(symbol, trade_date, previous_date)

    print(f"\n===== {symbol} ({symbol_prefix(symbol).upper()}) {trade_date} =====")
    prev = value_at(rows, previous_date, source_clock_for_field(window, "close"), "close")
    print(
        "prev_close",
        f"prev_date={previous_date}",
        f"theoretical={window.close}",
        f"source={source_clock_for_field(window, 'close')}",
        f"source_ts={prev['source_ts_ny']}",
        f"price={prev['price']}",
    )

    values: dict[str, float] = {"p_prev_close": prev["price"]}
    for item in boundary_plan(window, include_entry=True):
        val = value_at(rows, trade_date, item["source_clock"], item["price_column"])
        print(
            item["field"],
            f"theoretical={item['theoretical_clock']}",
            f"source={item['source_clock']}",
            f"price_col={item['price_column']}",
            f"source_ts={val['source_ts_ny']}",
            f"price={val['price']}",
        )
        values[item["field"]] = val["price"]

    if all(values.get(key) is not None for key in ["p_prev_close", "open_plus_30", "close_minus_60", "close_minus_30", "close", "lh_entry_next_open"]):
        r_onfh = values["open_plus_30"] / values["p_prev_close"] - 1
        r_m = values["close_minus_60"] / values["open_plus_30"] - 1
        r_slh = values["close_minus_30"] / values["close_minus_60"] - 1
        r_rod = values["close_minus_30"] / values["p_prev_close"] - 1
        r_lh = values["close"] / values["close_minus_30"] - 1
        r_lh_exec = values["close"] / values["lh_entry_next_open"] - 1
        print(
            "returns",
            f"ONFH={r_onfh:.10f}",
            f"M={r_m:.10f}",
            f"SLH={r_slh:.10f}",
            f"ROD={r_rod:.10f}",
            f"LH_stat={r_lh:.10f}",
            f"LH_executable={r_lh_exec:.10f}",
        )


def main() -> None:
    args = parse_args()
    for symbol in args.symbols:
        inspect_symbol(symbol, args.date)


if __name__ == "__main__":
    main()
