from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


NY_TZ = "America/New_York"


@dataclass(frozen=True)
class SymbolWindow:
    symbol: str
    calendar: str
    window_start: str
    open_plus_30: str
    close_minus_60: str
    close_minus_30: str
    close: str


SYMBOL_WINDOWS: dict[str, SymbolWindow] = {
    "ES.v.0": SymbolWindow("ES.v.0", "NYSE", "09:30", "10:00", "15:00", "15:30", "16:00"),
    "NQ.v.0": SymbolWindow("NQ.v.0", "NYSE", "09:30", "10:00", "15:00", "15:30", "16:00"),
    "GC.v.0": SymbolWindow("GC.v.0", "CMEGlobex_GC", "08:20", "08:50", "12:30", "13:00", "13:30"),
    "CL.v.0": SymbolWindow("CL.v.0", "CMEGlobex_CL", "09:00", "09:30", "13:30", "14:00", "14:30"),
    "ZN.v.0": SymbolWindow("ZN.v.0", "CME_Bond", "08:20", "08:50", "14:00", "14:30", "15:00"),
    "6E.v.0": SymbolWindow("6E.v.0", "CMEGlobex_FX", "07:20", "07:50", "13:00", "13:30", "14:00"),
}

STAT_CLOSE_FIELDS = ("open_plus_30", "close_minus_60", "close_minus_30", "close")
REQUIRED_FIELDS = ("window_start", "open_plus_30", "close_minus_60", "close_minus_30", "close")


def symbol_prefix(symbol: str) -> str:
    return symbol.split(".")[0].lower()


def timestamp_ny(trade_date: str, clock: str) -> pd.Timestamp:
    return pd.Timestamp(f"{trade_date} {clock}", tz=NY_TZ)


def clock_minus_one(clock: str) -> str:
    dummy = timestamp_ny("2000-01-03", clock) - pd.Timedelta(minutes=1)
    return dummy.strftime("%H:%M")


def source_clock_for_field(window: SymbolWindow, field: str) -> str:
    if field == "window_start":
        return window.window_start
    if field == "lh_entry_next_open":
        return window.close_minus_30
    theoretical = getattr(window, field)
    return clock_minus_one(theoretical)


def theoretical_clock_for_field(window: SymbolWindow, field: str) -> str:
    if field == "lh_entry_next_open":
        return window.close_minus_30
    return getattr(window, field)


def price_column_for_field(field: str) -> str:
    if field in {"window_start", "lh_entry_next_open"}:
        return "open"
    return "close"


def source_timestamp_utc(trade_date: str, window: SymbolWindow, field: str) -> pd.Timestamp:
    if field in {"window_start", "lh_entry_next_open"}:
        source = timestamp_ny(trade_date, theoretical_clock_for_field(window, field))
    else:
        source = timestamp_ny(trade_date, theoretical_clock_for_field(window, field)) - pd.Timedelta(minutes=1)
    return source.tz_convert("UTC")


def boundary_plan(window: SymbolWindow, include_entry: bool = True) -> list[dict[str, str]]:
    fields = list(REQUIRED_FIELDS)
    if include_entry:
        fields.append("lh_entry_next_open")
    return [
        {
            "field": field,
            "theoretical_clock": theoretical_clock_for_field(window, field),
            "source_clock": source_clock_for_field(window, field),
            "price_column": price_column_for_field(field),
        }
        for field in fields
    ]


def required_source_clocks(window: SymbolWindow, include_entry: bool = True) -> list[str]:
    return sorted({item["source_clock"] for item in boundary_plan(window, include_entry=include_entry)})


def missing_required_sources(present_clocks: set[str], window: SymbolWindow, include_entry: bool = True) -> list[str]:
    return [
        item["field"]
        for item in boundary_plan(window, include_entry=include_entry)
        if item["source_clock"] not in present_clocks
    ]


def boundary_value(group: pd.DataFrame, source_clock: str, price_column: str):
    values = group.loc[group["clock"] == source_clock, price_column]
    if values.empty:
        return None
    return values.iloc[-1]
