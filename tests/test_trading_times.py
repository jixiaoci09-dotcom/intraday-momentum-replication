from __future__ import annotations

import unittest

import pandas as pd

from intraday_momentum.trading_times import (
    SYMBOL_WINDOWS,
    boundary_plan,
    boundary_value,
    missing_required_sources,
    source_clock_for_field,
    source_timestamp_utc,
)


class TradingTimesTest(unittest.TestCase):
    def test_es_close_uses_1559_close(self) -> None:
        es = SYMBOL_WINDOWS["ES.v.0"]
        self.assertEqual(source_clock_for_field(es, "close"), "15:59")

    def test_gc_close_uses_1329_close(self) -> None:
        gc = SYMBOL_WINDOWS["GC.v.0"]
        self.assertEqual(source_clock_for_field(gc, "close"), "13:29")

    def test_all_close_times_use_previous_minute_close(self) -> None:
        for window in SYMBOL_WINDOWS.values():
            for field in ["open_plus_30", "close_minus_60", "close_minus_30", "close"]:
                expected = (
                    pd.Timestamp(f"2019-01-15 {getattr(window, field)}", tz="America/New_York")
                    - pd.Timedelta(minutes=1)
                ).strftime("%H:%M")
                self.assertEqual(source_clock_for_field(window, field), expected, (window.symbol, field))

    def test_session_open_uses_open_column_at_open_clock(self) -> None:
        es = SYMBOL_WINDOWS["ES.v.0"]
        plan = {item["field"]: item for item in boundary_plan(es)}
        self.assertEqual(plan["window_start"]["source_clock"], "09:30")
        self.assertEqual(plan["window_start"]["price_column"], "open")
        group = pd.DataFrame(
            {
                "clock": ["09:30"],
                "open": [100.0],
                "close": [101.0],
            }
        )
        self.assertEqual(boundary_value(group, "09:30", "open"), 100.0)

    def test_missing_required_price_time_is_recorded(self) -> None:
        es = SYMBOL_WINDOWS["ES.v.0"]
        present = {"09:30", "09:59", "14:59", "15:29"}
        missing = missing_required_sources(present, es, include_entry=True)
        self.assertIn("close", missing)
        self.assertIn("lh_entry_next_open", missing)
        drop_reason = "missing_boundary_source:" + ",".join(missing)
        self.assertIn("missing_boundary_source", drop_reason)

    def test_america_new_york_dst_conversion(self) -> None:
        es = SYMBOL_WINDOWS["ES.v.0"]
        winter = source_timestamp_utc("2019-01-15", es, "close")
        summer = source_timestamp_utc("2019-07-15", es, "close")
        self.assertEqual(winter.isoformat(), "2019-01-15T20:59:00+00:00")
        self.assertEqual(summer.isoformat(), "2019-07-15T19:59:00+00:00")

    def test_each_symbol_has_three_manual_sample_days_available(self) -> None:
        sample_days = ["2019-01-15", "2019-07-15", "2024-01-16"]
        self.assertEqual(len(sample_days), 3)
        for window in SYMBOL_WINDOWS.values():
            for day in sample_days:
                close_source = source_timestamp_utc(day, window, "close")
                self.assertEqual(close_source.tz_convert("America/New_York").strftime("%H:%M"), source_clock_for_field(window, "close"))


if __name__ == "__main__":
    unittest.main()
