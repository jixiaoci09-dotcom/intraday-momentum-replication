#!/usr/bin/env python3
"""Estimate Databento historical data cost without downloading data."""

from __future__ import annotations

import argparse
import os

import databento as db


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="GLBX.MDP3")
    parser.add_argument("--symbol", default="GC.v.0")
    parser.add_argument("--schema", default="ohlcv-1m")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
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
    cost = client.metadata.get_cost(
        dataset=args.dataset,
        symbols=[args.symbol],
        schema=args.schema,
        stype_in=args.stype_in,
        start=args.start,
        end=args.end,
        mode=args.mode,
    )

    print("Databento historical cost estimate")
    print(f"dataset: {args.dataset}")
    print(f"symbol:  {args.symbol}")
    print(f"schema:  {args.schema}")
    print(f"start:   {args.start}")
    print(f"end:     {args.end}")
    print(f"cost:    ${cost:.4f}")


if __name__ == "__main__":
    main()
