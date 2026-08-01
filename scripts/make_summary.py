#!/usr/bin/env python3
"""Freeze boundary-corrected baseline reports and validation manifests."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SYMBOLS = ["ES.v.0", "NQ.v.0", "GC.v.0", "CL.v.0", "ZN.v.0", "6E.v.0"]
PREFIXES = {symbol: symbol.split(".")[0].lower() for symbol in SYMBOLS}
PIPELINE_VERSION = "boundary_corrected_v1"
STRICT_REPLICATION_END = "2020-05-01"
OOS_START = "2021-01-01"
OOS_END = "2025-12-31"
ANNUALIZATION_DAYS = 252
ZN_TICK_SIZE = 0.015625
ZN_TICK_VALUE_USD = 15.625
REPORT_ROOT = Path("reports")
TABLE_ROOT = REPORT_ROOT / "tables"
AUDIT_ROOT = REPORT_ROOT / "audit"
DOC_ROOT = Path("docs")
MANIFEST_ROOT = Path("data/manifests")
PROCESSED_ROOT = Path("data/processed")


def p_fmt(value: float) -> str:
    return "p<0.001" if float(value) < 0.001 else f"{float(value):.3f}"


def n_fmt(value: Any, digits: int = 3, column: str = "") -> str:
    if pd.isna(value):
        return ""
    if column.lower() in {"p", "difference_p_hac"}:
        return p_fmt(float(value))
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)) and float(value).is_integer() and abs(float(value)) > 100:
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.{digits}f}"
    return str(value)


def md_table(df: pd.DataFrame, digits: int = 3) -> str:
    if df.empty:
        return "_None._"
    rendered = df.copy()
    for col in rendered.columns:
        rendered[col] = rendered[col].map(lambda value: n_fmt(value, digits, col))
    widths = [max(len(str(col)), *(len(str(v)) for v in rendered[col])) for col in rendered.columns]
    header = "| " + " | ".join(str(col).ljust(widths[i]) for i, col in enumerate(rendered.columns)) + " |"
    sep = "| " + " | ".join("-" * width for width in widths) + " |"
    rows = [
        "| " + " | ".join(str(row[col]).ljust(widths[i]) for i, col in enumerate(rendered.columns)) + " |"
        for row in rendered.to_dict("records")
    ]
    return "\n".join([header, sep, *rows])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def max_drawdown(returns: pd.Series) -> float:
    wealth = (1 + returns.fillna(0)).cumprod()
    drawdown = wealth / wealth.cummax() - 1
    return float(drawdown.min())


def zn_cost_outputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    daily = pd.read_parquet(PROCESSED_ROOT / "zn_daily_research_table.parquet")
    if sorted(daily["pipeline_version"].dropna().unique()) != [PIPELINE_VERSION]:
        raise SystemExit("ZN daily table is not boundary_corrected_v1")
    daily = daily[daily["include"]].copy()
    daily["trade_date"] = pd.to_datetime(daily["trade_date"])
    rows = []
    be_rows = []
    samples = {
        "replication": ("2010-06-07", STRICT_REPLICATION_END),
        "oos": (OOS_START, OOS_END),
    }
    for sample, (start, end) in samples.items():
        df = daily[(daily["trade_date"] >= start) & (daily["trade_date"] <= end)].copy()
        gross = df["r_LH_executable"].where(df["r_ROD"] > 0, -df["r_LH_executable"]).astype(float)
        inv_entry = 1 / df["p_lh_entry_next_open"].astype(float)
        break_even_ticks = float(gross.mean() / (ZN_TICK_SIZE * inv_entry.mean()))
        be_rows.append(
            {
                "sample": sample,
                "n_trades": int(len(df)),
                "avg_gross_return_bp": float(gross.mean() * 10000),
                "break_even_round_trip_ticks": break_even_ticks,
                "break_even_one_way_ticks": break_even_ticks / 2,
                "break_even_round_trip_usd_per_contract": break_even_ticks * ZN_TICK_VALUE_USD,
                "break_even_one_way_usd_per_contract": break_even_ticks * ZN_TICK_VALUE_USD / 2,
            }
        )
        for round_trip_ticks in [0, 1, 2, 3]:
            cost_return = round_trip_ticks * ZN_TICK_SIZE * inv_entry
            net = gross - cost_return
            avg_ann = net.mean() * ANNUALIZATION_DAYS
            vol_ann = net.std(ddof=1) * np.sqrt(ANNUALIZATION_DAYS)
            rows.append(
                {
                    "sample": sample,
                    "round_trip_tick_cost": round_trip_ticks,
                    "one_way_tick_cost": round_trip_ticks / 2,
                    "round_trip_cost_usd_per_contract": round_trip_ticks * ZN_TICK_VALUE_USD,
                    "one_way_cost_usd_per_contract": round_trip_ticks * ZN_TICK_VALUE_USD / 2,
                    "n_trades": int(len(net)),
                    "avg_gross_return_bp": float(gross.mean() * 10000),
                    "avg_net_return_bp": float(net.mean() * 10000),
                    "annualized_return_pct": float(avg_ann * 100),
                    "annualized_volatility_pct": float(vol_ann * 100),
                    "sharpe": float(avg_ann / vol_ann) if vol_ann != 0 else np.nan,
                    "max_drawdown_pct": float(max_drawdown(net) * 100),
                    "cumulative_net_return_pct": float(((1 + net).prod() - 1) * 100),
                }
            )
    cost = pd.DataFrame(rows)
    breakeven = pd.DataFrame(be_rows)
    cost.to_csv(TABLE_ROOT / "zn_executable_round_trip_tick_costs.csv", index=False)
    breakeven.to_csv(TABLE_ROOT / "zn_break_even_round_trip_tick_cost.csv", index=False)
    return cost, breakeven


def load_tables() -> dict[str, pd.DataFrame]:
    return {
        "regression": pd.read_csv(TABLE_ROOT / "boundary_corrected_v1_regression_long.csv"),
        "oos": pd.read_csv(TABLE_ROOT / "boundary_corrected_v1_oos_all.csv"),
        "diff": pd.read_csv(TABLE_ROOT / "boundary_corrected_v1_beta_difference_all.csv"),
        "strategy": pd.read_csv(TABLE_ROOT / "boundary_corrected_v1_strategy_all.csv"),
        "deletion": pd.read_csv(TABLE_ROOT / "boundary_corrected_v1_data_deletion_summary.csv"),
    }


def final_summaries(cost: pd.DataFrame, breakeven: pd.DataFrame) -> None:
    tables = load_tables()
    reg = tables["regression"]
    oos = tables["oos"]
    diff = tables["diff"]
    deletion = tables["deletion"]
    rep_eq7 = reg[(reg["sample"] == "replication") & (reg["spec"] == "eq7_rod") & (reg["predictor"] == "ROD")]
    oos_eq7 = reg[(reg["sample"] == "oos") & (reg["spec"] == "eq7_rod") & (reg["predictor"] == "ROD")]
    oos_r2_eq7 = oos[oos["spec"] == "eq7_rod"][
        ["symbol", "training_method", "n_test", "first_training_cutoff_date", "last_training_cutoff_date", "r2_oos_x100", "forecast_strategy_sharpe"]
    ]
    diff_eq7 = diff[(diff["spec"] == "eq7_rod") & (diff["predictor"] == "r_ROD")].copy()
    diff_eq7["difference_ci_low_x100"] = diff_eq7["difference_ci_low"] * 100
    diff_eq7["difference_ci_high_x100"] = diff_eq7["difference_ci_high"] * 100
    diff_eq7 = diff_eq7[
        ["symbol", "beta_replication_x100", "beta_oos_implied_x100", "beta_oos_minus_replication_x100", "difference_t_hac", "difference_p_hac", "difference_ci_low_x100", "difference_ci_high_x100"]
    ]

    zh = [
        "# 最终基线摘要：boundary_corrected_v1",
        "",
        "本摘要冻结六个 CME 连续期货品种 ES、NQ、GC、CL、ZN、6E 的单合约基线复现结果。所有主结果来自 `pipeline_version=boundary_corrected_v1`，使用各品种独立交易时段、纽约时区、夏令时处理、非开盘边界 `T-1` 分钟 bar close、session open 的 `T` 时刻 bar open、同合约前收盘对齐、提前收盘删除和缺失精确边界删除。",
        "",
        "严格论文重叠期为首个有效交易日至 `2020-05-01`；发表后样本外为 `2021-01-01` 至 `2025-12-31`。本轮 expanding OOS 从严格论文期训练集出发，只追加已经过去的 2021-2025 OOS 观测；`2020-05-02` 至 `2020-12-31` 不计入严格论文期，也不作为本轮 expanding 训练数据。",
        "",
        "## 论文期 Eq.(7)",
        "",
        md_table(rep_eq7[["symbol", "start", "end", "n", "beta_x100", "nw_se_x100", "t", "p", "adj_r2_x100"]]),
        "",
        "ES、NQ、GC、ZN 在论文重叠期复现出显著正向 Eq.(7) 关系。CL 和 6E 的单品种 Eq.(7) 不显著，这与论文附录中的单品种结果一致，因此不应写成复现失败。CL 和 6E 也不能直接拿来与论文的能源类、货币类 pooled regression 比较。",
        "",
        "## 2021-2025 OOS Eq.(7)",
        "",
        md_table(oos_eq7[["symbol", "start", "end", "n", "beta_x100", "nw_se_x100", "t", "p", "adj_r2_x100"]]),
        "",
        "2021-2025 年只有 ZN 的 Eq.(7) 关系显著延续。ES、NQ、GC 出现样本外衰减；CL、6E 在复现期和样本外均没有显著正向关系，后续扩展中作为 null/control contracts。",
        "",
        "## OOS R2：frozen_2020 vs expanding",
        "",
        md_table(oos_r2_eq7),
        "",
        "## Eq.(7) 前后系数差异",
        "",
        md_table(diff_eq7),
        "",
        "## ZN 可执行策略成本表",
        "",
        "成本表使用 `r_LH_executable`：信号在 close-30 边界形成，入场使用下一根 bar open。0/1/2/3 tick 是每次完整往返交易的总成本，不在入场和出场重复扣除；对应单边成本为往返成本的一半。",
        "",
        "ZN tick size = 0.015625 price points，tick value = $15.625 per contract。Tick value 依据 CME 10-Year Treasury Note futures contract specifications。成本扣除公式：`net_return_t = gross_return_t - round_trip_ticks * tick_size / entry_price_t`。",
        "",
        md_table(cost),
        "",
        "## ZN break-even round-trip tick cost",
        "",
        "Break-even 公式：`c* = mean(gross_return) / (tick_size * mean(1 / entry_price))`。`c*` 是每次完整往返交易可承受的总 tick 成本；单边 tick 成本为 `c*/2`。",
        "",
        md_table(breakeven),
        "",
        "## 数据删除统计",
        "",
        md_table(deletion),
        "",
        "## 冻结结论",
        "",
        "- 六个品种 ES、NQ、GC、CL、ZN、6E 均完成单合约复现。",
        "- ES、NQ、GC、ZN 在论文重叠期复现出显著正向 Eq.(7) 关系。",
        "- CL、6E 在单品种层面不显著，与论文附录的单品种结果一致，应作为对照品种保留。",
        "- 2021-2025 年只有 ZN 的 Eq.(7) 关系显著延续。",
        "- ES、NQ、GC 出现统计显著的样本外衰减。",
        "- 统计显著不等于扣除成本后可交易；ZN 虽有统计延续，但可执行策略对 tick 成本高度敏感。",
    ]
    (REPORT_ROOT / "final_baseline_summary_zh.md").write_text("\n".join(zh), encoding="utf-8")

    en = [
        "# Final Baseline Summary: boundary_corrected_v1",
        "",
        "This report freezes the single-contract baseline replication for ES, NQ, GC, CL, ZN, and 6E. All headline results use `pipeline_version=boundary_corrected_v1`: product-specific effective sessions, America/New_York timestamps with DST, `T-1` minute bar closes for non-open theoretical boundaries, session-open bar opens, same-contract previous-close alignment, and pre-specified deletion of early closes, missing exact boundaries, and roll-mismatch days.",
        "",
        "The strict paper-overlap sample ends on `2020-05-01`; the post-publication OOS period is `2021-01-01` to `2025-12-31`. The expanding OOS implementation starts from the strict replication sample and only appends prior OOS observations; `2020-05-02` to `2020-12-31` is not included in the strict overlap results or in this expanding training window.",
        "",
        "## Paper-Overlap Eq.(7)",
        "",
        md_table(rep_eq7[["symbol", "start", "end", "n", "beta_x100", "nw_se_x100", "t", "p", "adj_r2_x100"]]),
        "",
        "ES, NQ, GC, and ZN show positive and statistically significant Eq.(7) coefficients in the paper-overlap period. CL and 6E are insignificant at the single-contract level, consistent with the paper's appendix-level single-contract evidence; they should not be described as replication failures. Their single-contract estimates also must not be directly compared with the paper's energy or currency pooled regressions.",
        "",
        "## 2021-2025 OOS Eq.(7)",
        "",
        md_table(oos_eq7[["symbol", "start", "end", "n", "beta_x100", "nw_se_x100", "t", "p", "adj_r2_x100"]]),
        "",
        "Only ZN continues to show a positive and significant Eq.(7) relation in 2021-2025. ES, NQ, and GC exhibit OOS attenuation. CL and 6E have no significant positive relation in either the replication period or OOS and will be retained as null/control contracts.",
        "",
        "## OOS R2: frozen_2020 vs expanding",
        "",
        md_table(oos_r2_eq7),
        "",
        "## Eq.(7) Period-Difference Tests",
        "",
        md_table(diff_eq7),
        "",
        "## ZN Executable Strategy Cost Table",
        "",
        "The ZN table uses `r_LH_executable`: the signal is formed at the close-minus-30 boundary and entry uses the next bar open. The 0/1/2/3 tick scenarios are total round-trip costs per completed trade, not separately charged again at entry and exit; the one-way cost is half the round-trip cost.",
        "",
        "ZN tick size is 0.015625 price points and tick value is $15.625 per contract, following CME 10-Year Treasury Note futures contract specifications. The cost rule is `net_return_t = gross_return_t - round_trip_ticks * tick_size / entry_price_t`.",
        "",
        md_table(cost),
        "",
        "## ZN Break-Even Round-Trip Tick Cost",
        "",
        "`c* = mean(gross_return) / (tick_size * mean(1 / entry_price))`, where `c*` is the maximum total round-trip tick cost per completed trade that sets the average net return to zero.",
        "",
        md_table(breakeven),
        "",
        "## Frozen Conclusions",
        "",
        "- All six contracts, ES, NQ, GC, CL, ZN, and 6E, have complete single-contract baseline replications.",
        "- ES, NQ, GC, and ZN replicate positive and significant Eq.(7) relations in the paper-overlap sample.",
        "- CL and 6E are insignificant at the single-contract level, consistent with the paper's appendix-level single-contract evidence, and remain control contracts.",
        "- Only ZN remains significant in the 2021-2025 OOS period.",
        "- ES, NQ, and GC show statistically significant OOS attenuation.",
        "- Statistical significance is not the same as tradeability after costs; ZN remains highly sensitive to tick costs.",
    ]
    (REPORT_ROOT / "final_baseline_summary_en.md").write_text("\n".join(en), encoding="utf-8")


def file_manifest() -> pd.DataFrame:
    generated_at = datetime.now(timezone.utc).isoformat()
    paths = []
    for symbol, prefix in PREFIXES.items():
        paths.append(PROCESSED_ROOT / f"{prefix}_daily_research_table.parquet")
        for suffix in ["regression_summary", "oos_r2", "oos_predictions", "beta_difference_tests", "strategy_summary", "strategy_by_year"]:
            paths.append(TABLE_ROOT / f"{prefix}_core_{suffix}.csv")
    paths += [
        TABLE_ROOT / "boundary_corrected_v1_regression_long.csv",
        TABLE_ROOT / "boundary_corrected_v1_oos_all.csv",
        TABLE_ROOT / "boundary_corrected_v1_beta_difference_all.csv",
        TABLE_ROOT / "boundary_corrected_v1_strategy_all.csv",
        TABLE_ROOT / "boundary_corrected_v1_data_deletion_summary.csv",
        TABLE_ROOT / "zn_executable_round_trip_tick_costs.csv",
        TABLE_ROOT / "zn_break_even_round_trip_tick_cost.csv",
        REPORT_ROOT / "core_rerun_summary_boundary_corrected_v1.md",
        REPORT_ROOT / "final_baseline_summary_zh.md",
        REPORT_ROOT / "final_baseline_summary_en.md",
        AUDIT_ROOT / "v0_vs_boundary_corrected_v1.md",
        AUDIT_ROOT / "v0_vs_boundary_corrected_v1.csv",
    ]
    rows = []
    for path in paths:
        if not path.exists():
            raise SystemExit(f"Missing expected baseline file: {path}")
        rows.append(
            {
                "path": str(path),
                "pipeline_version": PIPELINE_VERSION,
                "generated_at_utc": generated_at,
                "strict_replication_end": STRICT_REPLICATION_END,
                "oos_start": OOS_START,
                "oos_end": OOS_END,
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    manifest = pd.DataFrame(rows)
    manifest.to_csv(REPORT_ROOT / "baseline_file_manifest.csv", index=False)
    (REPORT_ROOT / "baseline_file_manifest.md").write_text(
        "# Baseline File Manifest\n\n" + md_table(manifest[["path", "pipeline_version", "generated_at_utc", "strict_replication_end", "oos_start", "oos_end", "bytes"]], digits=0),
        encoding="utf-8",
    )
    return manifest


def validate_files(manifest: pd.DataFrame) -> pd.DataFrame:
    checks = []
    def add(name: str, status: str, detail: str) -> None:
        checks.append({"check": name, "status": status, "detail": detail})

    for symbol, prefix in PREFIXES.items():
        daily = pd.read_parquet(PROCESSED_ROOT / f"{prefix}_daily_research_table.parquet")
        add(f"{symbol} daily pipeline_version", "PASS" if sorted(daily["pipeline_version"].dropna().unique()) == [PIPELINE_VERSION] else "FAIL", str(sorted(daily["pipeline_version"].dropna().unique())))
        add(f"{symbol} daily executable LH", "PASS" if "r_LH_executable" in daily.columns else "FAIL", "r_LH_executable column present")
        add(f"{symbol} kept same-contract rows", "PASS" if int((~daily[daily["include"]]["same_instrument_as_prev"]).sum()) == 0 else "FAIL", "kept rows have same_instrument_as_prev=True")
        reg = pd.read_csv(TABLE_ROOT / f"{prefix}_core_regression_summary.csv")
        oos = pd.read_csv(TABLE_ROOT / f"{prefix}_core_oos_r2.csv")
        add(f"{symbol} regression pipeline_version", "PASS" if set(reg["pipeline_version"]) == {PIPELINE_VERSION} else "FAIL", str(set(reg["pipeline_version"])))
        add(f"{symbol} OOS pipeline_version", "PASS" if set(oos["pipeline_version"]) == {PIPELINE_VERSION} else "FAIL", str(set(oos["pipeline_version"])))

    text_files = [REPORT_ROOT / "final_baseline_summary_zh.md", REPORT_ROOT / "final_baseline_summary_en.md", REPORT_ROOT / "core_rerun_summary_boundary_corrected_v1.md"]
    for path in text_files:
        text = path.read_text()
        add(f"{path} p display", "PASS" if "p<0.001" in text else "FAIL", "Markdown p-values below 0.001 display as p<0.001")

    readme = Path("README.md").read_text()
    old_number_tokens = ["4.215", "3.185", "1.451", "-6.755", "1.669", "0.183"]
    add(
        "README final baseline references",
        "PASS" if "reports/final_baseline_summary_zh.md" in readme and "boundary_corrected_v1" in readme else "FAIL",
        "README points readers to frozen boundary_corrected_v1 summaries",
    )
    add(
        "README excludes invalid v0 headline numbers",
        "PASS" if not any(token in readme for token in old_number_tokens) else "FAIL",
        "README does not cite invalid_boundary_v0 numeric results in main conclusions",
    )

    ignored_patterns = Path(".gitignore").read_text()
    for pattern in ["data/raw/", "data/processed/", ".env", ".env.*", "*.dbn", "*.parquet", "reports/archive/invalid_boundary_v0/tables/"]:
        add(f".gitignore contains {pattern}", "PASS" if pattern in ignored_patterns else "FAIL", pattern)

    add("manifest pipeline_version", "PASS" if set(manifest["pipeline_version"]) == {PIPELINE_VERSION} else "FAIL", "all manifest rows boundary_corrected_v1")
    result = pd.DataFrame(checks)
    result.to_csv(AUDIT_ROOT / "baseline_validation_report.csv", index=False)
    (AUDIT_ROOT / "baseline_validation_report.md").write_text(
        "# Baseline Validation Report\n\n" + md_table(result),
        encoding="utf-8",
    )
    if (result["status"] != "PASS").any():
        raise SystemExit("Baseline validation failed; see reports/audit/baseline_validation_report.csv")
    return result


def main() -> None:
    REPORT_ROOT.mkdir(exist_ok=True)
    TABLE_ROOT.mkdir(parents=True, exist_ok=True)
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    cost, breakeven = zn_cost_outputs()
    final_summaries(cost, breakeven)
    manifest = file_manifest()
    validate_files(manifest)
    print("Baseline freeze outputs generated and validated.")


if __name__ == "__main__":
    main()
