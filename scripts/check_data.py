#!/usr/bin/env python3
"""Check local Databento downloads for one continuous futures symbol."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import databento as db
import pandas as pd


DATASET = "GLBX.MDP3"
ROOT = Path("data/raw/databento") / DATASET
MANIFEST_DIR = Path("data/manifests")


@dataclass(frozen=True)
class Package:
    label: str
    path: Path
    schema: str
    period: str
    approved_cost_usd: float
    job_id: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", required=True, help="Continuous symbol, e.g. NQ.v.0")
    parser.add_argument("--window-start", default="09:30")
    parser.add_argument("--window-end", default="16:00")
    parser.add_argument(
        "--required-boundaries",
        default="09:30,10:00,15:00,15:30,16:00",
        help="Comma-separated New York clock times required for the daily table.",
    )
    return parser.parse_args()


def state_path(symbol: str) -> Path:
    safe_symbol = symbol.replace("/", "_")
    return ROOT / "batch_jobs" / f"{safe_symbol}_2010-2025_jobs.json"


def find_zip(output_dir: Path, job_id: str) -> Path:
    candidates = sorted(output_dir.glob(f"**/{job_id}.zip"))
    if not candidates:
        candidates = sorted(output_dir.glob("**/*.zip"))
    if len(candidates) != 1:
        raise FileNotFoundError(f"Expected one zip under {output_dir}, found {len(candidates)}")
    return candidates[0]


def load_packages(symbol: str) -> list[Package]:
    state_file = state_path(symbol)
    if not state_file.exists():
        raise FileNotFoundError(state_file)
    state = json.loads(state_file.read_text(encoding="utf-8"))
    costs = {
        (item["schema"], item["label"]): float(item["cost"])
        for item in state.get("requests", [])
    }

    packages = []
    for item in state["jobs"].values():
        request = item["request"]
        output_dir = Path(item["output_dir"])
        job_id = item["job_id"]
        packages.append(
            Package(
                label=request["label"],
                path=find_zip(output_dir, job_id),
                schema=request["schema"],
                period=f"{request['start'][:10]} to {request['end'][:10]}",
                approved_cost_usd=costs.get((request["schema"], request["label"]), 0.0),
                job_id=job_id,
            )
        )
    return sorted(packages, key=lambda package: (package.schema, package.period, package.label))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_dbn_from_zip(zip_file: ZipFile, name: str) -> db.DBNStore:
    return db.DBNStore.from_bytes(zip_file.read(name))


def update_min_max(stats: dict[str, Any], minimum: float, maximum: float) -> None:
    stats["min"] = minimum if stats["min"] is None else min(stats["min"], minimum)
    stats["max"] = maximum if stats["max"] is None else max(stats["max"], maximum)


def summarize_ohlcv(
    zip_file: ZipFile,
    dbn_names: list[str],
    window_start: str,
    window_end: str,
    required_boundaries: list[str],
) -> dict[str, Any]:
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
            update_min_max(stats, float(df[column].min()), float(df[column].max()))
            stats["zeros"] += int((df[column] == 0).sum())
            stats["missing"] += int(df[column].isna().sum())

        update_min_max(volume_stats, int(df["volume"].min()), int(df["volume"].max()))
        volume_stats["zeros"] += int((df["volume"] == 0).sum())
        volume_stats["missing"] += int(df["volume"].isna().sum())

        local = df.copy()
        local["ny_time"] = local.index.tz_convert("America/New_York")
        local["ny_date"] = local["ny_time"].dt.date
        local["ny_clock"] = local["ny_time"].dt.strftime("%H:%M")
        window = local[(local["ny_clock"] >= window_start) & (local["ny_clock"] <= window_end)]

        for day, group in window.groupby("ny_date"):
            boundary_days += 1
            clocks = set(group["ny_clock"])
            boundary_missing = [clock for clock in required_boundaries if clock not in clocks]
            if boundary_missing:
                missing_any_boundary += 1

            expected = pd.date_range(
                pd.Timestamp(f"{day} {window_start}", tz="America/New_York"),
                pd.Timestamp(f"{day} {window_end}", tz="America/New_York"),
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
                        "rows_in_window": int(len(group)),
                        "missing_minutes": int(len(missing)),
                        "missing_boundaries": boundary_missing,
                        "instrument_ids": [int(x) for x in sorted(group["instrument_id"].unique())],
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
        "instrument_counts": {str(k): v for k, v in sorted(instrument_counts.items())},
        "mapping_interval_count": len(unique_mappings),
        "mapping_intervals_sample": list(unique_mappings.values())[:30],
        "price_stats": price_stats,
        "volume_stats": volume_stats,
        "paper_window": {
            "timezone": "America/New_York",
            "window": f"{window_start}-{window_end}",
            "required_boundaries": required_boundaries,
            "days_checked": boundary_days,
            "days_missing_any_boundary": missing_any_boundary,
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
        if "ts_event" in df.columns:
            start = df["ts_event"].min()
            end = df["ts_event"].max()
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


def summarize_package(
    package: Package,
    window_start: str,
    window_end: str,
    required_boundaries: list[str],
) -> dict[str, Any]:
    with ZipFile(package.path) as zip_file:
        names = zip_file.namelist()
        dbn_names = sorted(name for name in names if name.endswith(".dbn.zst"))
        json_names = sorted(name for name in names if name.endswith(".json"))
        summary = {
            "label": package.label,
            "schema": package.schema,
            "period": package.period,
            "approved_cost_usd": package.approved_cost_usd,
            "job_id": package.job_id,
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
            summary["validation"] = summarize_ohlcv(
                zip_file,
                dbn_names,
                window_start,
                window_end,
                required_boundaries,
            )
        elif package.schema == "definition":
            summary["validation"] = summarize_definitions(zip_file, dbn_names)
        else:
            raise ValueError(f"Unsupported schema: {package.schema}")
        return summary


def write_markdown_manifest(symbol: str, summary: dict[str, Any], path: Path) -> None:
    total_cost = sum(package["approved_cost_usd"] for package in summary["packages"])
    rows = [
        f"# {symbol} 2010-2025 Download Notes",
        "",
        "Raw licensed Databento files remain local under `data/raw/` and are ignored by Git.",
        "",
        f"- Dataset: `{DATASET}`",
        f"- Symbol: `{symbol}`",
        f"- Approved estimated cost: `${total_cost:.4f}`",
        "",
        "| Package | Schema | Period | Cost | Size | DBN files | SHA-256 |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for package in summary["packages"]:
        rows.append(
            "| {label} | `{schema}` | {period} | `${cost:.4f}` | {size:.2f} MB | {files} | `{sha}` |".format(
                label=package["label"],
                schema=package["schema"],
                period=package["period"],
                cost=package["approved_cost_usd"],
                size=package["size_mb"],
                files=package["dbn_zst_count"],
                sha=package["sha256"],
            )
        )

    rows.extend(
        [
            "",
            "## Data Check Summary",
            "",
        ]
    )
    for package in summary["packages"]:
        validation = package["validation"]
        rows.append(f"### {package['label']}")
        rows.append("")
        if package["schema"] == "ohlcv-1m":
            rows.extend(
                [
                    f"- Rows: `{validation['rows']:,}`",
                    f"- UTC range: `{validation['utc_start']}` to `{validation['utc_end']}`",
                    f"- Duplicate timestamps: `{validation['duplicate_timestamps']}`",
                    f"- Instrument count: `{len(validation['instrument_counts'])}`",
                    f"- Price close range: `{validation['price_stats']['close']['min']}` to `{validation['price_stats']['close']['max']}`",
                    f"- Required-boundary problem days: `{validation['paper_window']['days_missing_any_boundary']}` of `{validation['paper_window']['days_checked']}`",
                    "",
                ]
            )
        else:
            rows.extend(
                [
                    f"- Rows: `{validation['rows']:,}`",
                    f"- Instrument count: `{validation['instrument_count']}`",
                    f"- Raw symbol count: `{validation['raw_symbol_count']}`",
                    f"- Min price increment values: `{', '.join(validation['min_price_increment_values'])}`",
                    "",
                ]
            )

    path.write_text("\n".join(rows), encoding="utf-8")


def main() -> None:
    args = parse_args()
    required_boundaries = [item.strip() for item in args.required_boundaries.split(",") if item.strip()]
    packages = load_packages(args.symbol)
    summary = {
        "symbol": args.symbol,
        "dataset": DATASET,
        "source": "Databento",
        "note": "Summary checks only; raw licensed data remains in data/raw/ and is ignored by Git.",
        "packages": [
            summarize_package(package, args.window_start, args.window_end, required_boundaries)
            for package in packages
        ],
    }

    safe_symbol = args.symbol.replace(".", "_").replace("/", "_")
    md_out = MANIFEST_DIR / f"{safe_symbol.lower()}_2010-2025_download_manifest.md"
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    write_markdown_manifest(args.symbol, summary, md_out)

    print(f"{args.symbol} data check complete")
    print(f"manifest: {md_out}")
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
                "  rows={rows:,}, raw_symbols={symbols}, instruments={instruments}, tick={tick}".format(
                    rows=validation["rows"],
                    symbols=validation["raw_symbol_count"],
                    instruments=validation["instrument_count"],
                    tick=",".join(validation["min_price_increment_values"]),
                )
            )


if __name__ == "__main__":
    main()
