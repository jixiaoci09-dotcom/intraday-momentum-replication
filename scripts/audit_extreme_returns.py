#!/usr/bin/env python3
"""Create an extreme-return review table from raw OHLCV-1m files.

This audit rebuilds daily boundary prices in memory using the corrected
Databento OHLCV-1m source timestamp rule. It does not overwrite processed
research tables or regression outputs.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import databento as db
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from intraday_momentum.boundaries import (  # noqa: E402
    NY_TZ,
    SYMBOL_WINDOWS,
    SymbolWindow,
    boundary_plan,
    boundary_value,
    missing_required_sources,
    required_source_clocks,
    source_clock_for_field,
)
from scripts.build_fixed_window_daily_table import (  # noqa: E402
    PACKAGES,
    build_boundary_table,
    build_daily,
    load_rows,
    packages_for_symbol,
)


AUDIT_ROOT = Path("reports/audit")
CSV_OUT = AUDIT_ROOT / "extreme_returns_review.csv"
MD_OUT = AUDIT_ROOT / "extreme_returns_review.md"
RAW_ROOT = Path("data/raw/databento/GLBX.MDP3/ohlcv-1m")
DEFINITION_ROOT = Path("data/raw/databento/GLBX.MDP3/definition")
RETURN_COLUMNS = ["r_ONFH", "r_ROD", "r_LH"]
PRICE_COLUMNS = [
    "p_prev_close",
    "p_open_plus_30",
    "p_close_minus_60",
    "p_close_minus_30",
    "p_close",
]


def one_value(group: pd.DataFrame, column: str, clock: str) -> Any:
    values = group.loc[group["clock"] == clock, column]
    if values.empty:
        return None
    return values.iloc[-1]


def find_definition_zips(symbol: str) -> list[Path]:
    directory = DEFINITION_ROOT / symbol
    return sorted(directory.glob("**/*.zip"))


def load_raw_symbol_map(symbol: str) -> dict[int, str]:
    """Map instrument_id to the latest raw_symbol seen in definitions."""
    mapping: dict[int, str] = {}
    for zip_path in find_definition_zips(symbol):
        with ZipFile(zip_path) as zip_file:
            for name in sorted(n for n in zip_file.namelist() if n.endswith(".dbn.zst")):
                store = db.DBNStore.from_bytes(zip_file.read(name))
                df = store.to_df(price_type="float", pretty_ts=True, map_symbols=False)
                if df.empty or "raw_symbol" not in df.columns:
                    continue
                local = df.reset_index()
                for row in local[["instrument_id", "raw_symbol"]].dropna().itertuples(index=False):
                    mapping[int(row.instrument_id)] = str(row.raw_symbol)
    return mapping


def raw_data_quality(symbol: str) -> dict[str, int]:
    counts = {
        "raw_rows": 0,
        "raw_duplicate_symbol_instrument_ts_rows": 0,
        "raw_nonpositive_price_rows": 0,
        "raw_nan_or_inf_price_rows": 0,
    }
    seen: set[tuple[str, int, pd.Timestamp]] = set()
    for package in packages_for_symbol(symbol):
        with ZipFile(package["path"]) as zip_file:
            for name in sorted(n for n in zip_file.namelist() if n.endswith(".dbn.zst")):
                store = db.DBNStore.from_bytes(zip_file.read(name))
                df = store.to_df(price_type="float", pretty_ts=True, map_symbols=False)
                if df.empty:
                    continue
                local = df.reset_index()
                counts["raw_rows"] += int(len(local))
                price = local[["open", "high", "low", "close"]]
                counts["raw_nonpositive_price_rows"] += int((price <= 0).any(axis=1).sum())
                counts["raw_nan_or_inf_price_rows"] += int(
                    (~price.map(lambda value: pd.notna(value) and math.isfinite(float(value)))).any(axis=1).sum()
                )
                for row in local[["ts_event", "instrument_id"]].itertuples(index=False):
                    key = (symbol, int(row.instrument_id), row.ts_event)
                    if key in seen:
                        counts["raw_duplicate_symbol_instrument_ts_rows"] += 1
                    else:
                        seen.add(key)
    return counts


def audit_daily_for_symbol(symbol: str, raw_symbol_map: dict[int, str]) -> pd.DataFrame:
    window = SYMBOL_WINDOWS[symbol]
    packages = packages_for_symbol(symbol)
    loaded = [load_rows(package, window) for package in packages]
    boundaries = pd.concat([item[0] for item in loaded], ignore_index=True)
    volumes = pd.concat([item[1] for item in loaded], ignore_index=True)
    boundary_table = build_boundary_table(boundaries, volumes, packages, window.calendar, window)
    daily, _summary = build_daily(boundary_table)
    daily["symbol"] = symbol
    daily["raw_symbol"] = daily["instrument_id"].map(
        lambda value: raw_symbol_map.get(int(value), "") if pd.notna(value) else ""
    )
    daily["previous_close_raw_symbol"] = daily["prev_close_instrument_id"].map(
        lambda value: raw_symbol_map.get(int(value), "") if pd.notna(value) else ""
    )
    return daily


def with_flag_columns(daily: pd.DataFrame) -> pd.DataFrame:
    out = daily.copy()
    out["same_contract_flag"] = out["same_instrument_as_prev"].fillna(False).astype(bool)
    out["early_close_flag"] = ~out["calendar_has_effective_close"].fillna(False).astype(bool)
    boundary_cols = [
        "has_open_plus_30",
        "has_close_minus_60",
        "has_close_minus_30",
        "has_close",
    ]
    if "has_window_start" in out.columns:
        boundary_cols.insert(0, "has_window_start")
    out["missing_boundary_flag"] = ~out[boundary_cols].fillna(False).all(axis=1)
    out["nonpositive_price_flag"] = out[PRICE_COLUMNS].le(0).any(axis=1)
    out["drop_or_keep"] = out["include"].map(lambda value: "keep" if bool(value) else "drop")
    if "drop_reason" not in out.columns:
        out["drop_reason"] = out["exclude_reason"].fillna("")
    out["drop_reason"] = out["drop_reason"].fillna("")
    return out


def pick_extremes(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    included = daily[daily["include"]].copy()
    for return_column in RETURN_COLUMNS:
        selected = included.reindex(
            included[return_column].abs().sort_values(ascending=False).head(20).index
        ).copy()
        selected.insert(0, "review_variable", return_column.removeprefix("r_"))
        rows.append(selected)
    return pd.concat(rows, ignore_index=True)


def normalize_ts(value: Any) -> str:
    if pd.isna(value):
        return ""
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert(NY_TZ).isoformat()


def rename_and_select(extremes: pd.DataFrame) -> pd.DataFrame:
    out = extremes.rename(
        columns={
            "trade_date": "date",
            "p_prev_close": "previous_close_price",
            "p_open_plus_30": "open_plus_30_price",
            "p_close_minus_60": "close_minus_60_price",
            "p_close_minus_30": "close_minus_30_price",
            "p_close": "close_price",
            "r_ONFH": "ONFH",
            "r_M": "M",
            "r_SLH": "SLH",
            "r_ROD": "ROD",
            "r_LH": "LH",
        }
    )
    source_map = {
        "previous_close_source_ts": "ts_prev_close_utc",
        "window_start_source_ts": "ts_window_start_utc",
        "open_plus_30_source_ts": "ts_open_plus_30_utc",
        "close_minus_60_source_ts": "ts_close_minus_60_utc",
        "close_minus_30_source_ts": "ts_close_minus_30_utc",
        "close_source_ts": "ts_close_utc",
    }
    for out_col, in_col in source_map.items():
        out[out_col] = out[in_col].map(normalize_ts) if in_col in out.columns else ""
    for col in ["raw_symbol", "previous_close_raw_symbol", "drop_reason"]:
        if col not in out.columns:
            out[col] = ""
    ordered = [
        "review_variable",
        "symbol",
        "date",
        "raw_symbol",
        "instrument_id",
        "previous_close_raw_symbol",
        "prev_close_instrument_id",
        "previous_close_price",
        "open_plus_30_price",
        "close_minus_60_price",
        "close_minus_30_price",
        "close_price",
        "ONFH",
        "M",
        "SLH",
        "ROD",
        "LH",
        "previous_close_source_ts",
        "window_start_source_ts",
        "open_plus_30_source_ts",
        "close_minus_60_source_ts",
        "close_minus_30_source_ts",
        "close_source_ts",
        "same_contract_flag",
        "early_close_flag",
        "missing_boundary_flag",
        "nonpositive_price_flag",
        "drop_or_keep",
        "drop_reason",
        "segment",
    ]
    return out[ordered].sort_values(["symbol", "review_variable", "date"]).reset_index(drop=True)


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "_None._"
    rendered = df.copy()
    for column in rendered.columns:
        if pd.api.types.is_float_dtype(rendered[column]):
            rendered[column] = rendered[column].map(lambda value: "" if pd.isna(value) else f"{value:.8f}")
        else:
            rendered[column] = rendered[column].map(lambda value: "" if pd.isna(value) else str(value))
    headers = list(rendered.columns)
    rows = rendered.values.tolist()
    widths = [
        max([len(header)] + [len(str(row[index])) for row in rows])
        for index, header in enumerate(headers)
    ]

    def render_row(values: list[Any]) -> str:
        return "| " + " | ".join(str(value).ljust(widths[index]) for index, value in enumerate(values)) + " |"

    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    return "\n".join([render_row(headers), separator, *[render_row(row) for row in rows]])


def main() -> None:
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    all_extremes = []
    quality_rows = []
    final_quality_rows = []
    cl_2020_rows = []

    for symbol in SYMBOL_WINDOWS:
        print(f"Auditing {symbol}...")
        raw_symbol_map = load_raw_symbol_map(symbol)
        quality = raw_data_quality(symbol)
        quality["symbol"] = symbol
        quality_rows.append(quality)

        daily = with_flag_columns(audit_daily_for_symbol(symbol, raw_symbol_map))
        final_quality_rows.append(
            {
                "symbol": symbol,
                "candidate_rows": int(len(daily)),
                "kept_rows": int(daily["include"].sum()),
                "candidate_nonpositive_price_rows": int(daily["nonpositive_price_flag"].sum()),
                "kept_nonpositive_price_rows": int(daily.loc[daily["include"], "nonpositive_price_flag"].sum()),
                "kept_missing_boundary_rows": int(daily.loc[daily["include"], "missing_boundary_flag"].sum()),
                "kept_cross_contract_rows": int((~daily.loc[daily["include"], "same_contract_flag"]).sum()),
            }
        )

        extremes = pick_extremes(daily)
        all_extremes.append(extremes)
        if symbol == "CL.v.0":
            cl_2020_rows.append(extremes[extremes["trade_date"].astype(str).str.startswith("2020-")].copy())

    review = rename_and_select(pd.concat(all_extremes, ignore_index=True))
    review.to_csv(CSV_OUT, index=False)

    quality_df = pd.DataFrame(quality_rows)[
        [
            "symbol",
            "raw_rows",
            "raw_duplicate_symbol_instrument_ts_rows",
            "raw_nonpositive_price_rows",
            "raw_nan_or_inf_price_rows",
        ]
    ]
    final_quality_df = pd.DataFrame(final_quality_rows)
    cl_2020 = (
        rename_and_select(pd.concat(cl_2020_rows, ignore_index=True))
        if cl_2020_rows and not pd.concat(cl_2020_rows, ignore_index=True).empty
        else pd.DataFrame()
    )
    flags = review[
        [
            "symbol",
            "review_variable",
            "same_contract_flag",
            "early_close_flag",
            "missing_boundary_flag",
            "nonpositive_price_flag",
            "drop_or_keep",
            "drop_reason",
        ]
    ].copy()
    flag_summary = (
        flags.assign(
            cross_contract=lambda df: ~df["same_contract_flag"],
            any_rule_issue=lambda df: (
                (~df["same_contract_flag"])
                | df["early_close_flag"]
                | df["missing_boundary_flag"]
                | df["nonpositive_price_flag"]
                | (df["drop_or_keep"] != "keep")
            ),
        )
        .groupby(["symbol", "review_variable"], as_index=False)
        .agg(
            rows=("review_variable", "size"),
            any_rule_issue=("any_rule_issue", "sum"),
            cross_contract=("cross_contract", "sum"),
            early_close=("early_close_flag", "sum"),
            missing_boundary=("missing_boundary_flag", "sum"),
            nonpositive_price=("nonpositive_price_flag", "sum"),
            dropped=("drop_or_keep", lambda values: int((values != "keep").sum())),
        )
    )

    md = [
        "# Extreme Returns Review",
        "",
        "Generated from raw Databento OHLCV-1m packages with corrected boundary rules. "
        "Large absolute returns are not dropped by this audit; only pre-specified rule violations are flagged.",
        "",
        "## Raw Data Price Checks",
        "",
        markdown_table(quality_df),
        "",
        "## Final Audit Candidate Checks",
        "",
        markdown_table(final_quality_df),
        "",
        "## Extreme Row Rule Flags",
        "",
        markdown_table(flag_summary),
        "",
        "## CL 2020 Extreme Dates",
        "",
        markdown_table(
            cl_2020[
                [
                    "review_variable",
                    "symbol",
                    "date",
                    "raw_symbol",
                    "instrument_id",
                    "previous_close_raw_symbol",
                    "prev_close_instrument_id",
                    "previous_close_price",
                    "open_plus_30_price",
                    "close_minus_60_price",
                    "close_minus_30_price",
                    "close_price",
                    "ONFH",
                    "ROD",
                    "LH",
                    "same_contract_flag",
                    "early_close_flag",
                    "missing_boundary_flag",
                    "nonpositive_price_flag",
                    "drop_or_keep",
                    "drop_reason",
                ]
            ]
            if not cl_2020.empty
            else cl_2020
        ),
        "",
        "## Extreme Rows",
        "",
        markdown_table(review),
    ]
    MD_OUT.write_text("\n".join(md), encoding="utf-8")

    print(f"Wrote {CSV_OUT}")
    print(f"Wrote {MD_OUT}")
    print(f"Rows: {len(review)}")


if __name__ == "__main__":
    main()
