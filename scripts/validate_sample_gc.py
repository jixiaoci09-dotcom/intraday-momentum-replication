#!/usr/bin/env python3
"""Validate the local GC.v.0 OHLCV-1m sample without network access."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import databento as db
import pandas as pd


DEFAULT_PATH = Path(
    "data/raw/databento/GLBX.MDP3/ohlcv-1m/GC.v.0/"
    "GC.v.0_2024-01_ohlcv-1m.dbn.zst"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.path.exists():
        raise SystemExit(f"Sample file not found: {args.path}")

    store = db.DBNStore.from_file(args.path)
    df = store.to_df(price_type="float", pretty_ts=True, map_symbols=False)

    print("GC sample validation")
    print(f"path:       {args.path}")
    print(f"sha256:     {sha256(args.path)}")
    print(f"dataset:    {store.dataset}")
    print(f"schema:     {store.schema}")
    print(f"stype_in:   {store.stype_in}")
    print(f"stype_out:  {store.stype_out}")
    print(f"symbols:    {store.symbols}")
    print(f"rows:       {len(df):,}")
    print(f"utc_start:  {df.index.min()}")
    print(f"utc_end:    {df.index.max()}")
    print(f"columns:    {list(df.columns)}")
    print(f"duplicates: {int(df.index.duplicated().sum())}")

    print("\ninstrument_id counts")
    print(df["instrument_id"].value_counts().sort_index().to_string())

    for column in ["open", "high", "low", "close"]:
        print(
            f"{column}: min={df[column].min():.1f}, max={df[column].max():.1f}, "
            f"zeros={int((df[column] == 0).sum())}, na={int(df[column].isna().sum())}"
        )
    print(
        "volume: "
        f"min={df['volume'].min()}, max={df['volume'].max()}, "
        f"zeros={int((df['volume'] == 0).sum())}, na={int(df['volume'].isna().sum())}"
    )

    local = df.copy()
    local["ny_time"] = local.index.tz_convert("America/New_York")
    local["ny_date"] = local["ny_time"].dt.date
    local["ny_clock"] = local["ny_time"].dt.strftime("%H:%M")
    window = local[(local["ny_clock"] >= "08:20") & (local["ny_clock"] <= "13:30")]

    print("\nPaper GC window, 08:20-13:30 New York time")
    for day, group in window.groupby("ny_date"):
        expected = pd.date_range(
            pd.Timestamp(f"{day} 08:20", tz="America/New_York"),
            pd.Timestamp(f"{day} 13:30", tz="America/New_York"),
            freq="1min",
        ).tz_convert("UTC")
        missing = expected.difference(group.index.unique())
        boundary_missing = [
            clock
            for clock in ["08:20", "13:00", "13:30"]
            if clock not in set(group["ny_clock"])
        ]
        instruments = ",".join(map(str, sorted(group["instrument_id"].unique())))
        print(
            f"{day}: rows={len(group):3d}, missing={len(missing):3d}, "
            f"boundaries_missing={boundary_missing}, instruments={instruments}"
        )


if __name__ == "__main__":
    main()
