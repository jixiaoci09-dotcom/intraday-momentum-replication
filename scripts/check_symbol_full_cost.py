#!/usr/bin/env python3
"""Estimate replication and OOS Databento costs for one continuous futures symbol."""

from __future__ import annotations

import argparse
import os

import databento as db


REQUESTS = [
    ("replication OHLCV", "ohlcv-1m", "2010-06-06T00:00:00", "2020-06-01T00:00:00"),
    ("OOS OHLCV", "ohlcv-1m", "2021-01-01T00:00:00", "2026-01-01T00:00:00"),
    ("replication definitions", "definition", "2010-06-06T00:00:00", "2020-06-01T00:00:00"),
    ("OOS definitions", "definition", "2021-01-01T00:00:00", "2026-01-01T00:00:00"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", required=True, help="Continuous symbol, e.g. NQ.v.0")
    parser.add_argument("--dataset", default="GLBX.MDP3")
    parser.add_argument("--stype-in", default="continuous")
    parser.add_argument("--mode", default="historical-streaming")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    key = os.environ.get("DATABENTO_API_KEY")
    if not key:
        raise SystemExit(
            "DATABENTO_API_KEY is not set. Export it in your local shell; "
            "do not store it in the repository."
        )

    client = db.Historical(key)
    total = 0.0
    print(f"=== {args.symbol} cost estimate ===")
    for label, schema, start, end in REQUESTS:
        cost = client.metadata.get_cost(
            dataset=args.dataset,
            symbols=[args.symbol],
            schema=schema,
            stype_in=args.stype_in,
            start=start,
            end=end,
            mode=args.mode,
        )
        total += cost
        print(f"{args.symbol} {label:<24} {schema:<10} {start[:10]} to {end[:10]}: ${cost:.4f}")
    print(f"TOTAL: ${total:.4f}")


if __name__ == "__main__":
    main()
