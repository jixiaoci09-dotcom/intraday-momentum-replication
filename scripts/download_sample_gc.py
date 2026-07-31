#!/usr/bin/env python3
"""Download the approved one-month GC.v.0 OHLCV-1m sample."""

from __future__ import annotations

import os
from pathlib import Path

import databento as db


DATASET = "GLBX.MDP3"
SYMBOL = "GC.v.0"
SCHEMA = "ohlcv-1m"
START = "2024-01-01"
END = "2024-02-01"
OUT = Path(
    "data/raw/databento/GLBX.MDP3/ohlcv-1m/GC.v.0/"
    "GC.v.0_2024-01_ohlcv-1m.dbn.zst"
)


def main() -> None:
    key = os.environ.get("DATABENTO_API_KEY")
    if not key:
        raise SystemExit(
            "DATABENTO_API_KEY is not set. Export it in your local shell; "
            "do not store it in the repository."
        )

    if OUT.exists():
        raise SystemExit(f"Refusing to overwrite existing raw data file: {OUT}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    client = db.Historical(key)
    client.timeseries.get_range(
        dataset=DATASET,
        symbols=[SYMBOL],
        schema=SCHEMA,
        stype_in="continuous",
        stype_out="instrument_id",
        start=START,
        end=END,
        path=OUT,
    )

    print(f"Downloaded: {OUT}")
    print(f"Size MB: {OUT.stat().st_size / 1024 / 1024:.2f}")


if __name__ == "__main__":
    main()
