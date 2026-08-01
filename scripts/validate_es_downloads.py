#!/usr/bin/env python3
"""Validate local ES.v.0 batch downloads without network access."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import databento as db
import pandas as pd


ROOT = Path("data/raw/databento/GLBX.MDP3")
OUT = Path("data/manifests/es_v0_2010-2025_validation_summary.json")


@dataclass(frozen=True)
class Package:
    label: str
    path: Path
    schema: str
    period: str
    approved_cost_usd: float


PACKAGES = [
    Package(
        label="es_replication_ohlcv_1m",
        path=ROOT
        / "ohlcv-1m/ES.v.0/replication_2010-06-06_2020-06-01/"
        / "GLBX-20260801-WUUC3MXJMU/GLBX-20260801-WUUC3MXJMU.zip",
        schema="ohlcv-1m",
        period="2010-06-06 to 2020-06-01",
        approved_cost_usd=12.6435,
    ),
    Package(
        label="es_oos_ohlcv_1m",
        path=ROOT
        / "ohlcv-1m/ES.v.0/oos_2021-01-01_2026-01-01/"
        / "GLBX-20260801-Y3RT94RWU9/GLBX-20260801-Y3RT94RWU9.zip",
        schema="ohlcv-1m",
        period="2021-01-01 to 2026-01-01",
        approved_cost_usd=6.4545,
    ),
    Package(
        label="es_replication_definitions",
        path=ROOT
        / "definition/ES.v.0/replication_2010-06-06_2020-06-01/"
        / "GLBX-20260801-69VSGFPH8M/GLBX-20260801-69VSGFPH8M.zip",
        schema="definition",
        period="2010-06-06 to 2020-06-01",
        approved_cost_usd=0.0018,
    ),
    Package(
        label="es_oos_definitions",
        path=ROOT
        / "definition/ES.v.0/oos_2021-01-01_2026-01-01/"
        / "GLBX-20260801-95HE5NE3TK/GLBX-20260801-95HE5NE3TK.zip",
        schema="definition",
        period="2021-01-01 to 2026-01-01",
        approved_cost_usd=0.0009,
    ),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_dbn_from_zip(zip_file: ZipFile, name: str) -> db.DBNStore:
    return db.DBNStore.from_bytes(zip_file.read(name))


def summarize_ohlcv(zip_file: ZipFile, dbn_names: list[str]) -> dict[str, Any]:
    rows = 0
    duplicate_timestamps = 0
    instrument_counts: Counter[int] = Counter()
    mapping_intervals: list[dict[str, str]] = []
    price_stats = {
        "open": {"min": None, "max": None, "zeros": 0, "missing": 0},
        "high": {"min": None, "max": None, "zeros": 0, "missing": 0},
        "low": {"min": None, "max": None, "zeros": 0, "missing": 0},
        "close": {"min": None, "max": None, "zeros": 0, "missing": 0},
    }
    volume_stats = {"min": None, "max": None, "zeros": 0, "missing": 0}
    utc_start = None
    utc_end = None
    boundary_days = 0
    missing_any_boundary = 0
    missing_1530 = 0
    missing_1600 = 0
    missing_any_minute = 0
    max_missing_minutes = 0
    example_problem_days: list[dict[str, Any]] = []

    for name in dbn_names:
        store = load_dbn_from_zip(zip_file, name)
        df = store.to_df(price_type="float", pretty_ts=True, map_symbols=False)
        if df.empty:
            continue

        rows += len(df)
        duplicate_timestamps += int(df.index.duplicated().sum())
        utc_start = df.index.min() if utc_start is None else min(utc_start, df.index.min())
        utc_end = df.index.max() if utc_end is None else max(utc_end, df.index.max())
        for instrument_id, count in df["instrument_id"].value_counts().to_dict().items():
            instrument_counts[int(instrument_id)] += int(count)

        for intervals in store.mappings.values():
            for interval in intervals:
                mapping_intervals.append(
                    {
                        "start_date": str(interval["start_date"]),
                        "end_date": str(interval["end_date"]),
                        "instrument_id": str(interval["symbol"]),
                    }
                )

        for column, stats in price_stats.items():
            stats["min"] = (
                float(df[column].min())
                if stats["min"] is None
                else min(stats["min"], float(df[column].min()))
            )
            stats["max"] = (
                float(df[column].max())
                if stats["max"] is None
                else max(stats["max"], float(df[column].max()))
            )
            stats["zeros"] += int((df[column] == 0).sum())
            stats["missing"] += int(df[column].isna().sum())

        volume_stats["min"] = (
            int(df["volume"].min())
            if volume_stats["min"] is None
            else min(volume_stats["min"], int(df["volume"].min()))
        )
        volume_stats["max"] = (
            int(df["volume"].max())
            if volume_stats["max"] is None
            else max(volume_stats["max"], int(df["volume"].max()))
        )
        volume_stats["zeros"] += int((df["volume"] == 0).sum())
        volume_stats["missing"] += int(df["volume"].isna().sum())

        local = df.copy()
        local["ny_time"] = local.index.tz_convert("America/New_York")
        local["ny_date"] = local["ny_time"].dt.date
        local["ny_clock"] = local["ny_time"].dt.strftime("%H:%M")
        window = local[
            (local["ny_clock"] >= "09:30") & (local["ny_clock"] <= "16:00")
        ]

        for day, group in window.groupby("ny_date"):
            boundary_days += 1
            clocks = set(group["ny_clock"])
            boundary_missing = [
                clock for clock in ["09:30", "10:00", "15:30", "16:00"] if clock not in clocks
            ]
            if boundary_missing:
                missing_any_boundary += 1
            if "15:30" in boundary_missing:
                missing_1530 += 1
            if "16:00" in boundary_missing:
                missing_1600 += 1

            expected = pd.date_range(
                pd.Timestamp(f"{day} 09:30", tz="America/New_York"),
                pd.Timestamp(f"{day} 16:00", tz="America/New_York"),
                freq="1min",
            ).tz_convert("UTC")
            missing = expected.difference(group.index.unique())
            if len(missing):
                missing_any_minute += 1
                max_missing_minutes = max(max_missing_minutes, len(missing))

            if (boundary_missing or len(missing)) and len(example_problem_days) < 20:
                example_problem_days.append(
                    {
                        "ny_date": str(day),
                        "rows_0930_1600": int(len(group)),
                        "missing_minutes": int(len(missing)),
                        "missing_boundaries": boundary_missing,
                        "instrument_ids": [
                            int(x) for x in sorted(group["instrument_id"].unique())
                        ],
                    }
                )

    unique_mappings = {
        (m["start_date"], m["end_date"], m["instrument_id"]): m
        for m in mapping_intervals
    }

    return {
        "rows": rows,
        "utc_start": str(utc_start),
        "utc_end": str(utc_end),
        "duplicate_timestamps": duplicate_timestamps,
        "instrument_counts": {
            str(k): v for k, v in sorted(instrument_counts.items())
        },
        "mapping_interval_count": len(unique_mappings),
        "mapping_intervals_sample": list(unique_mappings.values())[:30],
        "price_stats": price_stats,
        "volume_stats": volume_stats,
        "paper_window": {
            "timezone": "America/New_York",
            "window": "09:30-16:00",
            "required_boundaries": ["09:30", "10:00", "15:30", "16:00"],
            "days_checked": boundary_days,
            "days_missing_any_boundary": missing_any_boundary,
            "days_missing_1530": missing_1530,
            "days_missing_1600": missing_1600,
            "days_missing_any_minute": missing_any_minute,
            "max_missing_minutes": max_missing_minutes,
            "example_problem_days": example_problem_days,
        },
    }


def summarize_definitions(zip_file: ZipFile, dbn_names: list[str]) -> dict[str, Any]:
    rows = 0
    instruments: set[int] = set()
    raw_symbols: set[str] = set()
    utc_start = None
    utc_end = None
    expirations: set[str] = set()
    min_tick_values: set[str] = set()

    for name in dbn_names:
        store = load_dbn_from_zip(zip_file, name)
        df = store.to_df(price_type="float", pretty_ts=True, map_symbols=False)
        if df.empty:
            continue
        rows += len(df)
        time_col = "ts_event" if "ts_event" in df.columns else None
        if time_col:
            start = df[time_col].min()
            end = df[time_col].max()
            utc_start = start if utc_start is None else min(utc_start, start)
            utc_end = end if utc_end is None else max(utc_end, end)
        instruments.update(map(int, df["instrument_id"].dropna().unique()))
        if "raw_symbol" in df.columns:
            raw_symbols.update(map(str, df["raw_symbol"].dropna().unique()))
        if "expiration" in df.columns:
            expirations.update(map(str, df["expiration"].dropna().unique()))
        if "min_price_increment" in df.columns:
            min_tick_values.update(map(str, sorted(df["min_price_increment"].dropna().unique())))

    return {
        "rows": rows,
        "utc_start": str(utc_start),
        "utc_end": str(utc_end),
        "instrument_count": len(instruments),
        "raw_symbol_count": len(raw_symbols),
        "raw_symbols_sample": sorted(raw_symbols)[:40],
        "expiration_count": len(expirations),
        "expiration_sample": sorted(expirations)[:20],
        "min_price_increment_values": sorted(min_tick_values),
    }


def summarize_package(package: Package) -> dict[str, Any]:
    if not package.path.exists():
        raise FileNotFoundError(package.path)

    with ZipFile(package.path) as zip_file:
        names = zip_file.namelist()
        dbn_names = sorted(name for name in names if name.endswith(".dbn.zst"))
        json_names = sorted(name for name in names if name.endswith(".json"))
        base = {
            "label": package.label,
            "schema": package.schema,
            "period": package.period,
            "approved_cost_usd": package.approved_cost_usd,
            "path": str(package.path),
            "size_bytes": package.path.stat().st_size,
            "size_mb": round(package.path.stat().st_size / 1024 / 1024, 2),
            "sha256": sha256(package.path),
            "zip_file_count": len(names),
            "dbn_zst_count": len(dbn_names),
            "json_count": len(json_names),
            "first_dbn": dbn_names[0] if dbn_names else None,
            "last_dbn": dbn_names[-1] if dbn_names else None,
        }
        if package.schema == "ohlcv-1m":
            base["validation"] = summarize_ohlcv(zip_file, dbn_names)
        elif package.schema == "definition":
            base["validation"] = summarize_definitions(zip_file, dbn_names)
        else:
            raise ValueError(f"Unsupported schema: {package.schema}")
        return base


def main() -> None:
    summary = {
        "symbol": "ES.v.0",
        "dataset": "GLBX.MDP3",
        "source": "Databento",
        "note": "Aggregate validation only; raw licensed data remains in data/raw/ and is ignored by Git.",
        "packages": [summarize_package(package) for package in PACKAGES],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("ES.v.0 validation complete")
    print(f"summary: {OUT}")
    for package in summary["packages"]:
        validation = package["validation"]
        print(
            f"{package['label']}: size={package['size_mb']} MB, "
            f"dbn_files={package['dbn_zst_count']}, sha256={package['sha256']}"
        )
        if package["schema"] == "ohlcv-1m":
            print(
                "  rows={rows:,}, utc={start} to {end}, instruments={n}, "
                "boundary_problem_days={bad}/{days}".format(
                    rows=validation["rows"],
                    start=validation["utc_start"],
                    end=validation["utc_end"],
                    n=len(validation["instrument_counts"]),
                    bad=validation["paper_window"]["days_missing_any_boundary"],
                    days=validation["paper_window"]["days_checked"],
                )
            )
        else:
            print(
                "  rows={rows:,}, raw_symbols={symbols}, instruments={instruments}".format(
                    rows=validation["rows"],
                    symbols=validation["raw_symbol_count"],
                    instruments=validation["instrument_count"],
                )
            )


if __name__ == "__main__":
    main()
