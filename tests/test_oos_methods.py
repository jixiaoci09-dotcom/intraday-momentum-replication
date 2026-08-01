from __future__ import annotations

import unittest

import pandas as pd

from scripts.run_symbol_core_replication import (
    STRICT_REPLICATION_END,
    common_valid_sample,
    cost_adjusted_strategy_returns,
    oos_r2_outputs,
    sample_for_name,
    strategy_returns,
)


class OosMethodsTest(unittest.TestCase):
    def synthetic_daily(self) -> pd.DataFrame:
        dates = pd.to_datetime(
            [
                "2020-04-27",
                "2020-04-28",
                "2020-04-29",
                "2020-04-30",
                "2020-05-01",
                "2020-05-04",
                "2021-01-04",
                "2021-01-05",
                "2021-01-06",
            ]
        )
        x = pd.Series(range(1, len(dates) + 1), dtype=float)
        return pd.DataFrame(
            {
                "trade_date": dates,
                "include": True,
                "r_ONFH": x / 100,
                "r_M": x / 200,
                "r_SLH": x / 300,
                "r_ROD": x / 120,
                "r_LH": x / 500,
                "r_LH_executable": x / 600,
                "year": dates.year,
            }
        )

    def test_strict_replication_ends_on_2020_05_01(self) -> None:
        df = self.synthetic_daily()
        replication = sample_for_name(df, "replication")
        self.assertEqual(replication["trade_date"].max().date().isoformat(), STRICT_REPLICATION_END)
        self.assertNotIn(pd.Timestamp("2020-05-04"), set(replication["trade_date"]))

    def test_expanding_and_frozen_training_cutoffs_are_separate(self) -> None:
        rows, predictions = oos_r2_outputs(self.synthetic_daily())
        self.assertTrue({"expanding", "frozen_2020"}.issubset(set(predictions["training_method"])))

        eq7_expanding = predictions[
            (predictions["spec"] == "eq7_rod") & (predictions["training_method"] == "expanding")
        ]
        eq7_frozen = predictions[
            (predictions["spec"] == "eq7_rod") & (predictions["training_method"] == "frozen_2020")
        ]
        self.assertEqual(eq7_expanding["training_cutoff_date"].tolist(), ["2020-05-01", "2021-01-04", "2021-01-05"])
        self.assertEqual(eq7_frozen["training_cutoff_date"].tolist(), ["2020-05-01", "2020-05-01", "2020-05-01"])

        summary = pd.DataFrame(rows)
        self.assertEqual(
            set(summary[summary["spec"] == "eq7_rod"]["training_method"]),
            {"expanding", "frozen_2020"},
        )
        self.assertIn("mspe_model", summary.columns)
        self.assertIn("forecast_strategy_sharpe", summary.columns)

    def test_common_valid_sample_and_tick_cost(self) -> None:
        df = self.synthetic_daily()
        df["p_close_minus_30"] = 100.0
        df["p_lh_entry_next_open"] = 100.0
        df.loc[0, "r_M"] = None
        self.assertEqual(len(common_valid_sample(df)), len(df) - 1)

        strat = strategy_returns(df.dropna(), "r_LH_executable")
        zero_cost = cost_adjusted_strategy_returns(strat, tick_size=0.25, round_trip_ticks=0)
        one_tick = cost_adjusted_strategy_returns(strat, tick_size=0.25, round_trip_ticks=1)
        self.assertAlmostEqual(zero_cost["timing_rROD"].iloc[0], strat["timing_rROD"].iloc[0])
        self.assertAlmostEqual(one_tick["timing_rROD"].iloc[0], strat["timing_rROD"].iloc[0] - 0.0025)

        statistical = strategy_returns(df.dropna(), "r_LH")
        self.assertEqual(statistical["strategy_price_type"].iloc[0], "paper_statistical")
        self.assertEqual(statistical.columns.tolist().count("r_LH"), 1)


if __name__ == "__main__":
    unittest.main()
