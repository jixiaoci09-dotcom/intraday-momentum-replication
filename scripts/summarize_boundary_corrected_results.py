#!/usr/bin/env python3
"""Summarize boundary-corrected core replication outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


SYMBOLS = ["ES.v.0", "NQ.v.0", "GC.v.0", "CL.v.0", "ZN.v.0", "6E.v.0"]
PREFIXES = {symbol: symbol.split(".")[0].lower() for symbol in SYMBOLS}
REPORT_ROOT = Path("reports")
TABLE_ROOT = REPORT_ROOT / "tables"
AUDIT_ROOT = REPORT_ROOT / "audit"
ARCHIVE_TABLE_ROOT = REPORT_ROOT / "archive/invalid_boundary_v0/tables"
MANIFEST_ROOT = Path("data/manifests")


def fmt(value: Any, digits: int = 3, column: str = "") -> str:
    if pd.isna(value):
        return ""
    if column.lower() in {"p", "difference_p_hac", "beta_r_rod_p_hac", "beta_r_onfh_p_hac", "beta_r_m_p_hac", "beta_r_slh_p_hac"}:
        numeric = float(value)
        return "p<0.001" if numeric < 0.001 else f"{numeric:.3f}"
    if isinstance(value, (int,)) or (isinstance(value, float) and float(value).is_integer() and abs(value) > 100):
        return str(int(value))
    return f"{float(value):.{digits}f}"


def md_table(df: pd.DataFrame, digits: int = 3) -> str:
    if df.empty:
        return "_无。_"
    rendered = df.copy()
    for col in rendered.columns:
        rendered[col] = rendered[col].map(lambda value: fmt(value, digits, col) if isinstance(value, (int, float)) else ("" if pd.isna(value) else str(value)))
    widths = [max(len(str(col)), *(len(str(v)) for v in rendered[col])) for col in rendered.columns]
    header = "| " + " | ".join(str(col).ljust(widths[i]) for i, col in enumerate(rendered.columns)) + " |"
    sep = "| " + " | ".join("-" * width for width in widths) + " |"
    rows = [
        "| " + " | ".join(str(row[col]).ljust(widths[i]) for i, col in enumerate(rendered.columns)) + " |"
        for row in rendered.to_dict("records")
    ]
    return "\n".join([header, sep, *rows])


def predictor_rows(reg: pd.DataFrame, symbol: str) -> list[dict[str, Any]]:
    out = []
    reg = reg[reg["sample_scope"].eq("common_valid_all_eq5_eq6_eq7")].copy()
    predictors = ["r_ONFH", "r_M", "r_SLH", "r_ROD"]
    for row in reg.itertuples(index=False):
        for predictor in predictors:
            beta_col = f"beta_{predictor}_x100"
            if beta_col not in reg.columns or pd.isna(getattr(row, beta_col)):
                continue
            out.append(
                {
                    "symbol": symbol,
                    "sample": row.sample,
                    "spec": row.spec,
                    "predictor": predictor.removeprefix("r_"),
                    "beta_x100": getattr(row, beta_col),
                    "nw_se_x100": getattr(row, f"beta_{predictor}_se_hac") * 100,
                    "t": getattr(row, f"beta_{predictor}_t_hac"),
                    "p": getattr(row, f"beta_{predictor}_p_hac"),
                    "adj_r2_x100": row.adj_r2_x100,
                    "n": row.nobs,
                    "start": row.start,
                    "end": row.end,
                }
            )
    return out


def load_outputs() -> dict[str, dict[str, pd.DataFrame]]:
    outputs: dict[str, dict[str, pd.DataFrame]] = {}
    for symbol, prefix in PREFIXES.items():
        outputs[symbol] = {
            "reg": pd.read_csv(TABLE_ROOT / f"{prefix}_core_regression_summary.csv"),
            "oos": pd.read_csv(TABLE_ROOT / f"{prefix}_core_oos_r2.csv"),
            "diff": pd.read_csv(TABLE_ROOT / f"{prefix}_core_beta_difference_tests.csv"),
            "strategy": pd.read_csv(TABLE_ROOT / f"{prefix}_core_strategy_summary.csv"),
        }
    return outputs


def data_deletion_summary() -> pd.DataFrame:
    rows = []
    for symbol, prefix in PREFIXES.items():
        summary = json.loads((MANIFEST_ROOT / f"{prefix}_daily_research_table_summary.json").read_text())
        rows.append(
            {
                "symbol": symbol,
                "rows_total": summary["rows_total"],
                "rows_included": summary["rows_included"],
                "rows_excluded": summary["rows_excluded"],
                "replication_included": summary["included_by_segment"].get("replication", 0),
                "oos_included": summary["included_by_segment"].get("oos", 0),
                "excluded_by_reason": "; ".join(f"{k}={v}" for k, v in summary["excluded_by_reason"].items()),
            }
        )
    return pd.DataFrame(rows)


def v0_comparison(outputs: dict[str, dict[str, pd.DataFrame]]) -> pd.DataFrame:
    rows = []
    for symbol, prefix in PREFIXES.items():
        v1_reg = outputs[symbol]["reg"]
        v1_oos = outputs[symbol]["oos"]
        v1_strat = outputs[symbol]["strategy"]
        v0_reg = pd.read_csv(ARCHIVE_TABLE_ROOT / f"{prefix}_core_regression_summary.csv")
        v0_oos = pd.read_csv(ARCHIVE_TABLE_ROOT / f"{prefix}_core_oos_r2.csv")
        v0_strat = pd.read_csv(ARCHIVE_TABLE_ROOT / f"{prefix}_core_strategy_summary.csv")

        old_reg = v0_reg[(v0_reg["sample"] == "replication") & (v0_reg["spec"] == "eq7_rod")].iloc[0]
        new_reg = v1_reg[
            (v1_reg["sample"] == "replication")
            & (v1_reg["sample_scope"] == "common_valid_all_eq5_eq6_eq7")
            & (v1_reg["spec"] == "eq7_rod")
        ].iloc[0]
        old_oos = v0_oos[v0_oos["spec"] == "eq7_rod"].iloc[0]
        new_oos = v1_oos[(v1_oos["spec"] == "eq7_rod") & (v1_oos["training_method"] == "frozen_2020")].iloc[0]
        old_sharpe = v0_strat[
            (v0_strat["sample"] == "replication") & (v0_strat["strategy"] == "timing_rROD")
        ]["sharpe"].iloc[0]
        new_sharpe = v1_strat[
            (v1_strat["sample"] == "replication")
            & (v1_strat["strategy"] == "timing_rROD")
            & (v1_strat["strategy_price_type"] == "paper_statistical")
            & (v1_strat["round_trip_ticks"] == 0)
        ]["sharpe"].iloc[0]
        rows.append(
            {
                "symbol": symbol,
                "metric_basis": "Eq7 replication; OOS R2 frozen_2020; strategy timing_rROD gross paper_statistical",
                "v0_beta_x100": old_reg["beta_r_ROD_x100"],
                "v1_beta_x100": new_reg["beta_r_ROD_x100"],
                "v0_t": old_reg["beta_r_ROD_t_hac"],
                "v1_t": new_reg["beta_r_ROD_t_hac"],
                "v0_p": old_reg["beta_r_ROD_p_hac"],
                "v1_p": new_reg["beta_r_ROD_p_hac"],
                "v0_adj_r2_x100": old_reg["adj_r2_x100"],
                "v1_adj_r2_x100": new_reg["adj_r2_x100"],
                "v0_oos_r2_x100": old_oos["r2_oos_x100"],
                "v1_oos_r2_x100": new_oos["r2_oos_x100"],
                "v0_sharpe": old_sharpe,
                "v1_sharpe": new_sharpe,
                "v0_n": old_reg["nobs"],
                "v1_n": new_reg["nobs"],
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    TABLE_ROOT.mkdir(parents=True, exist_ok=True)
    outputs = load_outputs()

    regression_long = pd.DataFrame(
        row for symbol in SYMBOLS for row in predictor_rows(outputs[symbol]["reg"], symbol)
    )
    oos_all = pd.concat(
        [df["oos"].assign(symbol=symbol) for symbol, df in outputs.items()],
        ignore_index=True,
    )
    diff_all = pd.concat(
        [df["diff"].assign(symbol=symbol) for symbol, df in outputs.items()],
        ignore_index=True,
    )
    strategy_all = pd.concat(
        [df["strategy"].assign(symbol=symbol) for symbol, df in outputs.items()],
        ignore_index=True,
    )
    deletion = data_deletion_summary()
    v0_vs_v1 = v0_comparison(outputs)

    regression_long.to_csv(TABLE_ROOT / "boundary_corrected_v1_regression_long.csv", index=False)
    oos_all.to_csv(TABLE_ROOT / "boundary_corrected_v1_oos_all.csv", index=False)
    diff_all.to_csv(TABLE_ROOT / "boundary_corrected_v1_beta_difference_all.csv", index=False)
    strategy_all.to_csv(TABLE_ROOT / "boundary_corrected_v1_strategy_all.csv", index=False)
    deletion.to_csv(TABLE_ROOT / "boundary_corrected_v1_data_deletion_summary.csv", index=False)
    v0_vs_v1.to_csv(AUDIT_ROOT / "v0_vs_boundary_corrected_v1.csv", index=False)

    rep_eq7 = regression_long[
        (regression_long["sample"] == "replication")
        & (regression_long["spec"] == "eq7_rod")
        & (regression_long["predictor"] == "ROD")
    ].copy()
    oos_eq7 = regression_long[
        (regression_long["sample"] == "oos")
        & (regression_long["spec"] == "eq7_rod")
        & (regression_long["predictor"] == "ROD")
    ].copy()
    oos_r2_eq7 = oos_all[oos_all["spec"] == "eq7_rod"][
        [
            "symbol",
            "training_method",
            "test_start",
            "test_end",
            "n_test",
            "first_training_cutoff_date",
            "last_training_cutoff_date",
            "mspe_model",
            "mspe_benchmark",
            "r2_oos_x100",
            "forecast_strategy_sharpe",
        ]
    ]
    diff_eq7 = diff_all[(diff_all["spec"] == "eq7_rod") & (diff_all["predictor"] == "r_ROD")][
        [
            "symbol",
            "beta_replication_x100",
            "beta_oos_implied_x100",
            "beta_oos_minus_replication_x100",
            "difference_t_hac",
            "difference_p_hac",
            "difference_ci_low",
            "difference_ci_high",
        ]
    ].copy()
    diff_eq7["difference_ci_low_x100"] = diff_eq7["difference_ci_low"] * 100
    diff_eq7["difference_ci_high_x100"] = diff_eq7["difference_ci_high"] * 100
    diff_eq7 = diff_eq7.drop(columns=["difference_ci_low", "difference_ci_high"])

    exec_strategy = strategy_all[
        (strategy_all["strategy_price_type"] == "executable_next_open")
        & (strategy_all["strategy"] == "timing_rROD")
    ][
        [
            "symbol",
            "sample",
            "round_trip_ticks",
            "nobs",
            "trade_count",
            "avg_ann_pct",
            "vol_ann_pct",
            "sharpe",
            "success_rate",
            "max_drawdown",
            "avg_trade_return_bp",
        ]
    ]

    replicated = rep_eq7[(rep_eq7["beta_x100"] > 0) & (rep_eq7["p"] < 0.05)]["symbol"].tolist()
    oos_failed = oos_eq7[(oos_eq7["p"] >= 0.05) | (oos_eq7["beta_x100"] <= 0)]["symbol"].tolist()
    attenuated = diff_eq7[
        (diff_eq7["beta_oos_minus_replication_x100"] < 0) & (diff_eq7["difference_p_hac"] < 0.05)
    ]["symbol"].tolist()

    summary_lines = [
        "# Boundary-Corrected v1 完整基线重跑摘要",
        "",
        "本轮结果使用 `pipeline_version=boundary_corrected_v1`。所有非开盘理论边界价格均使用 `T-1` 分钟 bar 的 close；session open 使用 `T` 时刻 bar 的 open。换月不一致、提前收盘、缺失精确边界和无前收盘的日期均按预定规则删除。",
        "",
        "严格论文重叠期截止日为 `2020-05-01`。本轮 OOS 使用 `2021-01-01` 至 `2025-12-31`，实际首个有效 OOS 交易日因前收盘和日历过滤通常为 `2021-01-05`。`2020-05-02` 至 `2020-12-31` 没有进入严格论文期结果，也没有进入本轮 expanding 训练窗口。",
        "",
        "## 六品种论文期 Eq.(7) 复现总表",
        "",
        md_table(rep_eq7[["symbol", "start", "end", "n", "beta_x100", "nw_se_x100", "t", "p", "adj_r2_x100"]]),
        "",
        "## 三个论文模型完整长表",
        "",
        md_table(regression_long[regression_long["sample"] == "replication"][["symbol", "spec", "predictor", "start", "end", "n", "beta_x100", "nw_se_x100", "t", "p", "adj_r2_x100"]]),
        "",
        "## 2021-2025 OOS Eq.(7) 系数",
        "",
        md_table(oos_eq7[["symbol", "start", "end", "n", "beta_x100", "nw_se_x100", "t", "p", "adj_r2_x100"]]),
        "",
        "## frozen 与 expanding OOS R2 对比",
        "",
        md_table(oos_r2_eq7),
        "",
        "## 前后 Eq.(7) 系数差异检验",
        "",
        md_table(diff_eq7),
        "",
        "## executable 策略结果：timing_rROD",
        "",
        md_table(exec_strategy),
        "",
        "## 数据删除统计",
        "",
        md_table(deletion),
        "",
        "## 当前结论",
        "",
        f"- 论文期 Eq.(7) 正且 5% 显著的品种：{', '.join(replicated) if replicated else '无'}。",
        f"- 2021-2025 OOS 中 Eq.(7) 未延续为正且显著的品种：{', '.join(oos_failed) if oos_failed else '无'}。",
        f"- Eq.(7) 前后系数差异检验显示显著衰减的品种：{', '.join(attenuated) if attenuated else '无'}。",
        "- 交易成本后结论以 executable 策略表为准；0/1/2/3 tick 是每次往返总成本，尚未使用 BBO。",
    ]
    (REPORT_ROOT / "core_rerun_summary_boundary_corrected_v1.md").write_text("\n".join(summary_lines), encoding="utf-8")

    audit_lines = [
        "# v0 vs boundary_corrected_v1",
        "",
        "旧结果位于 `reports/archive/invalid_boundary_v0/`，仅用于说明边界修复影响。旧结果无效，不用于最终研究结论。",
        "",
        "比较口径：Eq.(7) replication beta、t、p、adjusted R2；OOS R2 使用新口径中的 `frozen_2020` 与旧固定切分结果比较；Sharpe 使用 replication `timing_rROD` 毛收益、论文统计价格口径。",
        "",
        md_table(v0_vs_v1),
    ]
    (AUDIT_ROOT / "v0_vs_boundary_corrected_v1.md").write_text("\n".join(audit_lines), encoding="utf-8")
    print(f"Wrote {REPORT_ROOT / 'core_rerun_summary_boundary_corrected_v1.md'}")
    print(f"Wrote {AUDIT_ROOT / 'v0_vs_boundary_corrected_v1.md'}")
    print(f"Wrote aggregate CSV tables under {TABLE_ROOT}")


if __name__ == "__main__":
    main()
