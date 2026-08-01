#!/usr/bin/env python3
"""Submit and download approved Databento batch jobs for one futures symbol."""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import databento as db


DATASET = "GLBX.MDP3"
ROOT = Path("data/raw/databento") / DATASET


@dataclass(frozen=True)
class Request:
    key: str
    label: str
    schema: str
    start: str
    end: str
    split_duration: str

    def output_dir(self, symbol: str) -> Path:
        period = f"{self.key}_{self.start[:10]}_{self.end[:10]}"
        return ROOT / self.schema / symbol / period


REQUESTS = [
    Request(
        key="replication",
        label="replication OHLCV",
        schema="ohlcv-1m",
        start="2010-06-06T00:00:00",
        end="2020-06-01T00:00:00",
        split_duration="month",
    ),
    Request(
        key="oos",
        label="OOS OHLCV",
        schema="ohlcv-1m",
        start="2021-01-01T00:00:00",
        end="2026-01-01T00:00:00",
        split_duration="month",
    ),
    Request(
        key="replication",
        label="replication definitions",
        schema="definition",
        start="2010-06-06T00:00:00",
        end="2020-06-01T00:00:00",
        split_duration="month",
    ),
    Request(
        key="oos",
        label="OOS definitions",
        schema="definition",
        start="2021-01-01T00:00:00",
        end="2026-01-01T00:00:00",
        split_duration="month",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", required=True, help="Continuous symbol, e.g. NQ.v.0")
    parser.add_argument("--approved-total", type=float)
    parser.add_argument("--estimate-only", action="store_true", help="Only print the estimated Databento cost")
    parser.add_argument("--max-cost-drift", type=float, default=0.01)
    parser.add_argument("--poll-seconds", type=int, default=120)
    return parser.parse_args()


def load_state(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"jobs": {}}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def package_key(request: Request) -> str:
    return f"{request.schema}_{request.label.replace(' ', '_').lower()}"


def has_downloaded_zip(output_dir: Path) -> bool:
    return any(output_dir.glob("*/*.zip")) or any(output_dir.glob("*.zip"))


def estimate_cost(client: db.Historical, symbol: str) -> list[dict[str, Any]]:
    rows = []
    for request in REQUESTS:
        cost = client.metadata.get_cost(
            dataset=DATASET,
            symbols=[symbol],
            schema=request.schema,
            stype_in="continuous",
            start=request.start,
            end=request.end,
            mode="historical-streaming",
        )
        rows.append({"request": request, "cost": float(cost)})
    return rows


def submit_missing_jobs(client: db.Historical, symbol: str, state: dict[str, Any]) -> None:
    for request in REQUESTS:
        key = package_key(request)
        output_dir = request.output_dir(symbol)
        if has_downloaded_zip(output_dir):
            print(f"Already downloaded, skipping submit: {request.label} -> {output_dir}")
            continue
        if key in state["jobs"]:
            print(f"Existing job in state, skipping submit: {request.label} -> {state['jobs'][key]['job_id']}")
            continue

        print(f"Submitting batch job: {request.label}")
        job = client.batch.submit_job(
            dataset=DATASET,
            symbols=[symbol],
            schema=request.schema,
            start=request.start,
            end=request.end,
            encoding="dbn",
            compression="zstd",
            pretty_px=False,
            pretty_ts=False,
            map_symbols=False,
            split_symbols=False,
            split_duration=request.split_duration,
            delivery="download",
            stype_in="continuous",
            stype_out="instrument_id",
        )
        job_id = str(job["id"])
        state["jobs"][key] = {
            "job_id": job_id,
            "request": asdict(request),
            "output_dir": str(output_dir),
            "submitted_job": job,
        }
        save_state(state_path(symbol), state)
        print(f"job_id: {job_id}")


def state_path(symbol: str) -> Path:
    safe_symbol = symbol.replace("/", "_")
    return ROOT / "batch_jobs" / f"{safe_symbol}_2010-2025_jobs.json"


def job_by_id(client: db.Historical, job_id: str) -> dict[str, Any] | None:
    for job in client.batch.list_jobs(states="queued,processing,done"):
        if job.get("id") == job_id:
            return job
    return None


def poll_and_download(client: db.Historical, state: dict[str, Any], poll_seconds: int) -> None:
    while True:
        pending = []
        for key, item in state["jobs"].items():
            output_dir = Path(item["output_dir"])
            if has_downloaded_zip(output_dir):
                print(f"{key}: already downloaded")
                continue

            job_id = item["job_id"]
            job = job_by_id(client, job_id)
            if job is None:
                print(f"{key}: job not found in recent job list: {job_id}")
                pending.append(key)
                continue

            state_text = job.get("state")
            progress = job.get("progress")
            cost = job.get("cost_usd")
            print(f"{key}: job_id={job_id}, state={state_text}, progress={progress}, cost_usd={cost}")

            if state_text == "done":
                print(f"Downloading {key} to {output_dir}")
                output_dir.mkdir(parents=True, exist_ok=True)
                client.batch.download(job_id=job_id, output_dir=output_dir, keep_zip=True)
            else:
                pending.append(key)

        if not pending:
            break
        print(f"Waiting for {len(pending)} job(s). Checking again in {poll_seconds} seconds...")
        time.sleep(poll_seconds)


def main() -> None:
    args = parse_args()
    key = os.environ.get("DATABENTO_API_KEY")
    if not key:
        raise SystemExit(
            "DATABENTO_API_KEY is not set. Export it in your local shell; "
            "do not store it in the repository."
        )

    client = db.Historical(key)
    state = load_state(state_path(args.symbol))

    costs = estimate_cost(client, args.symbol)
    total = sum(row["cost"] for row in costs)
    print(f"=== {args.symbol} approved batch download ===")
    for row in costs:
        request = row["request"]
        print(f"{request.label:<24} {request.schema:<10} {request.start[:10]} to {request.end[:10]}: ${row['cost']:.4f}")
    print(f"TOTAL: ${total:.4f}")

    if args.estimate_only:
        return

    if args.approved_total is None:
        raise SystemExit("Set --approved-total after checking the estimated cost, or use --estimate-only.")

    if total > args.approved_total + args.max_cost_drift:
        raise SystemExit(
            f"Cost ${total:.4f} exceeds approved total ${args.approved_total:.4f} "
            f"by more than ${args.max_cost_drift:.4f}. Aborting before submit."
        )

    state["symbol"] = args.symbol
    state["dataset"] = DATASET
    state["approved_total"] = args.approved_total
    state["latest_estimated_total"] = total
    state["requests"] = [
        {"label": row["request"].label, "schema": row["request"].schema, "cost": row["cost"]}
        for row in costs
    ]
    save_state(state_path(args.symbol), state)

    submit_missing_jobs(client, args.symbol, state)
    poll_and_download(client, state, args.poll_seconds)
    save_state(state_path(args.symbol), state)
    print("Batch download complete.")


if __name__ == "__main__":
    main()
