#!/usr/bin/env python3
"""Create the final Chinese and English result summaries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


REPORT_ROOT = Path("reports")
TABLE_ROOT = REPORT_ROOT / "tables"


def n_fmt(value: Any, digits: int = 3, column: str = "") -> str:
    if pd.isna(value):
        return ""
    if column.lower() == "p":
        return "p<0.001" if float(value) < 0.001 else f"{float(value):.3f}"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer() and abs(value) > 100:
            return str(int(value))
        return f"{value:.{digits}f}"
    return str(value)


def md_table(df: pd.DataFrame, digits: int = 3) -> str:
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


def load_result_tables() -> dict[str, pd.DataFrame]:
    return {
        "regression": pd.read_csv(TABLE_ROOT / "boundary_corrected_v1_regression_long.csv"),
        "oos": pd.read_csv(TABLE_ROOT / "boundary_corrected_v1_oos_all.csv"),
        "cost": pd.read_csv(TABLE_ROOT / "zn_executable_round_trip_tick_costs.csv"),
    }


def result_views() -> dict[str, pd.DataFrame]:
    tables = load_result_tables()
    reg = tables["regression"]

    rep_eq7 = reg[(reg["sample"] == "replication") & (reg["spec"] == "eq7_rod") & (reg["predictor"] == "ROD")]
    oos_eq7 = reg[(reg["sample"] == "oos") & (reg["spec"] == "eq7_rod") & (reg["predictor"] == "ROD")]

    oos_r2 = tables["oos"][tables["oos"]["spec"] == "eq7_rod"][
        ["symbol", "training_method", "n_test", "r2_oos_x100", "forecast_strategy_sharpe"]
    ].copy()
    oos_r2["training_method"] = oos_r2["training_method"].replace({"frozen_2020": "fixed_sample"})

    cost = tables["cost"][tables["cost"]["round_trip_tick_cost"].isin([0, 1])][
        [
            "sample",
            "round_trip_tick_cost",
            "n_trades",
            "avg_gross_return_bp",
            "avg_net_return_bp",
            "sharpe",
            "cumulative_net_return_pct",
        ]
    ].copy()

    columns = ["symbol", "start", "end", "n", "beta_x100", "t", "p"]
    return {
        "rep_eq7": rep_eq7[columns],
        "oos_eq7": oos_eq7[columns],
        "oos_r2": oos_r2,
        "cost": cost,
    }


def chinese_summary(views: dict[str, pd.DataFrame]) -> str:
    return "\n".join(
        [
            "# 日内动量部分复现结果总结",
            "",
            "本项目对 Baltussen、Da、Lammers 和 Martens 的论文《Hedging Demand and Market Intraday Momentum》中期货日内动量的核心回归框架进行六品种部分复现。研究对象是六个 CME 连续期货合约：ES、NQ、GC、CL、ZN 和 6E。",
            "",
            "项目并不尝试完整复制原论文覆盖的全部市场、历史时期、机制分析和扩展结果。这里主要关注核心回归设定在本项目数据中的表现，以及 2021-2025 年样本外时期的结果。",
            "",
            "核心问题是：当天前面大部分时间的收益率，是否能够解释最后半小时的收益率。为了观察论文结果在后续时期是否仍然存在，我把样本分成两个部分：",
            "",
            "- 论文重叠期：2010 年 6 月至 2020 年 5 月 1 日",
            "- 样本外时期：2021 年 1 月 1 日至 2025 年 12 月 31 日",
            "",
            "其中 2020 年 5 月之后到 2020 年底没有放入主要比较，目的是让论文重叠期和后续样本外检验保持清楚分开。",
            "",
            "## 1. 方法说明",
            "",
            "每天根据各期货品种的主要交易时段，提取开盘、开盘后半小时、收盘前一小时、收盘前半小时和收盘等关键价格点，并计算几个日内收益率。",
            "",
            "本文最关注的是论文中的 Eq.(7)：",
            "",
            "```text",
            "r_LH = alpha + beta * r_ROD + error",
            "```",
            "",
            "其中：",
            "",
            "- `r_ROD` 表示从前一交易日收盘到当天收盘前半小时的收益率；",
            "- `r_LH` 表示当天最后半小时的收益率；",
            "- `beta` 衡量前面大部分时间的价格方向和最后半小时价格方向之间的关系。",
            "",
            "如果 `beta` 显著为正，说明前面时间段上涨时，最后半小时也更倾向于上涨；前面时间段下跌时，最后半小时也更倾向于下跌。这就是论文讨论的日内动量现象。",
            "",
            "## 2. 论文重叠期结果",
            "",
            "下表是六个品种在本项目定义的论文重叠期内的 Eq.(7) 回归结果。`beta_x100` 是回归系数乘以 100 后的数值，方便阅读。",
            "",
            md_table(views["rep_eq7"]),
            "",
            "在本项目定义的论文重叠期内，ES、NQ、GC 和 ZN 的 Eq.(7) 系数为正，且在名义显著性水平下显著；CL 和 6E 未能呈现显著的正向关系。",
            "",
            "这里的不显著结果只表示在当前数据处理和样本划分下没有得到统计上显著的正向关系，并不等同于证明这些品种不存在相关效应。",
            "",
            "## 3. 2021-2025 年样本外结果",
            "",
            "为了观察这种关系在论文发表后的时期是否仍然存在，我继续检验 2021-2025 年的数据。",
            "",
            md_table(views["oos_eq7"]),
            "",
            "样本外结果和论文重叠期相比有明显变化。2021-2025 年，只有 ZN 仍然表现出显著的正向关系。ES、NQ 和 GC 在论文重叠期显著，但在样本外时期变弱。CL 和 6E 在两个时期都没有显著的正向关系。",
            "",
            "这说明日内动量并不是在所有品种和所有时期都持续出现。在这个样本中，ZN 的样本外结果最明显，而股指期货和黄金的样本外表现明显减弱。",
            "",
            "## 4. 样本外预测结果",
            "",
            "我还比较了两种样本外预测方式：",
            "",
            "- 固定训练样本：只使用论文重叠期的数据估计模型，再预测 2021-2025 年；",
            "- 递增训练样本：预测每一天时，使用此前已经观察到的数据重新估计模型。",
            "",
            "从 OOS R2 和预测策略表现看，大部分品种的样本外解释力并不强。ZN 是主要例外，它在两种训练方式下都保持正的 OOS R2，并且预测方向的表现好于其他品种。",
            "",
            md_table(views["oos_r2"]),
            "",
            "## 5. 交易成本观察",
            "",
            "统计关系显著不等于策略可以直接交易。为了粗略观察交易成本的影响，我重点看了样本外表现最明显的 ZN。",
            "",
            "策略思路是：如果 `r_ROD` 为正，则做多最后半小时；如果 `r_ROD` 为负，则做空最后半小时。为了更接近实际执行，入场价格使用信号形成后的下一分钟开盘价。",
            "",
            md_table(views["cost"]),
            "",
            "结果显示，ZN 的统计关系虽然比较明显，但交易成本影响很大。只要加入 1 tick 的往返成本，平均净收益就会明显下降，甚至变成负值。因此，这个结果更适合作为统计现象和样本外观察，不能直接理解成可以真实交易的策略。",
            "",
            "## 6. 数据处理说明",
            "",
            "数据处理时，我主要做了以下几件事：",
            "",
            "- 不同品种使用各自更合适的主要交易时段；",
            "- 时间统一按照纽约时间处理；",
            "- 提前收盘日、假期和关键价格缺失的日期不放入主样本；",
            "- 连续合约换月时，避免把前一日收盘价和当天价格来自不同合约的日期放进回归；",
            "- 原始 Databento 数据不上传到 GitHub，只保留代码、数据记录和结果表。",
            "",
            "这些处理会减少一部分样本，但可以避免一些明显的数据不一致问题。",
            "",
            "## 7. 总结",
            "",
            "本项目的主要结论是：",
            "",
            "- 本项目完成了六个 CME 期货品种的核心回归部分复现。",
            "- 在论文重叠期，ES、NQ、GC 和 ZN 的 Eq.(7) 结果为正，且在名义显著性水平下显著。",
            "- CL 和 6E 在本项目定义的论文重叠期内未能呈现显著的正向关系。",
            "- 在 2021-2025 年样本外时期，只有 ZN 仍然保持显著正向关系。",
            "- 大部分品种的样本外预测效果较弱，说明日内动量关系没有在所有品种中持续出现。",
            "- 即使统计结果显著，加入交易成本后也不一定具有实际交易价值。",
            "",
            "总体来看，本项目在六个 CME 期货品种上完成了核心设定的部分复现；结果显示，论文重叠期内的正向关系主要出现在 ES、NQ、GC 和 ZN，而后续样本外结果并不普遍延续。",
        ]
    )


def english_summary(views: dict[str, pd.DataFrame]) -> str:
    return "\n".join(
        [
            "# Intraday Momentum in CME Futures",
            "",
            "A Partial Replication and Post-2020 Out-of-Sample Evaluation",
            "",
            'This project conducts a partial replication of the paper\'s core futures-market intraday momentum specifications from Baltussen, Da, Lammers, and Martens, "Hedging Demand and Market Intraday Momentum." The sample covers six CME continuous futures contracts: ES, NQ, GC, CL, ZN, and 6E.',
            "",
            "The project does not attempt to reproduce every market, historical period, mechanism analysis, or extension in the original paper. It focuses on the core regression specifications in this repository's data and on a 2021-2025 out-of-sample evaluation.",
            "",
            "The main question is whether the return over most of the trading day helps explain the return over the final half hour. To see whether the paper result also appears after the original sample period, I split the data into two parts:",
            "",
            "- Paper-overlap period: June 2010 to May 1, 2020",
            "- Out-of-sample period: January 1, 2021 to December 31, 2025",
            "",
            "The period from May 2020 through the end of 2020 is left out of the main comparison so that the paper-overlap period and the later out-of-sample test stay clearly separated.",
            "",
            "## 1. Method",
            "",
            "For each futures contract, I use the contract's main trading window to collect several key intraday prices: the open, 30 minutes after the open, one hour before the close, 30 minutes before the close, and the close. These prices are then used to calculate intraday return variables.",
            "",
            "The main specification is Eq.(7) from the paper:",
            "",
            "```text",
            "r_LH = alpha + beta * r_ROD + error",
            "```",
            "",
            "where:",
            "",
            "- `r_ROD` is the return from the previous trading day's close to 30 minutes before the current close;",
            "- `r_LH` is the return over the final half hour;",
            "- `beta` measures the relationship between the earlier intraday move and the final-half-hour move.",
            "",
            "If `beta` is positive and statistically significant, then days with positive earlier returns tend to continue upward in the final half hour, and days with negative earlier returns tend to continue downward. This is the intraday momentum pattern studied in the paper.",
            "",
            "## 2. Paper-Overlap Period",
            "",
            "The table below reports Eq.(7) results for the six contracts during the paper-overlap period defined in this project. `beta_x100` is the regression coefficient multiplied by 100 to make the numbers easier to read.",
            "",
            md_table(views["rep_eq7"]),
            "",
            "During the paper-overlap period defined in this project, ES, NQ, GC, and ZN have positive Eq.(7) coefficients that are statistically significant at conventional nominal levels, whereas CL and 6E do not show a statistically significant positive relationship.",
            "",
            "A non-significant result here only means that this project does not find a statistically significant positive relationship under the current data processing and sample definition. It does not prove that no related effect exists in those contracts.",
            "",
            "## 3. 2021-2025 Out-of-Sample Results",
            "",
            "I then test whether the same relationship appears in the later 2021-2025 sample.",
            "",
            md_table(views["oos_eq7"]),
            "",
            "The out-of-sample results are different from the paper-overlap results. In 2021-2025, only ZN continues to show a significant positive relationship. ES, NQ, and GC are significant in the paper-overlap period but weaken in the later sample. CL and 6E are not significantly positive in either period.",
            "",
            "This suggests that intraday momentum does not appear consistently across all contracts and all time periods. In this sample, ZN has the clearest out-of-sample result, while equity-index futures and gold show weaker out-of-sample performance.",
            "",
            "## 4. Out-of-Sample Prediction",
            "",
            "I also compare two simple out-of-sample prediction approaches:",
            "",
            "- Fixed training sample: estimate the model using only the paper-overlap period, then predict 2021-2025;",
            "- Expanding training sample: re-estimate the model each prediction day using all data available up to that point.",
            "",
            "Based on OOS R2 and the directional forecast strategy, most contracts have weak out-of-sample explanatory power. ZN is the main exception: it has positive OOS R2 under both training approaches and better forecast-strategy performance than the other contracts.",
            "",
            md_table(views["oos_r2"]),
            "",
            "## 5. Transaction Cost Check",
            "",
            "Statistical significance does not mean that the pattern can be traded directly. To get a rough sense of transaction costs, I focus on ZN, which has the strongest out-of-sample result.",
            "",
            "The simple strategy is: go long during the final half hour when `r_ROD` is positive, and go short during the final half hour when `r_ROD` is negative. To make the execution assumption more realistic, the entry price uses the next one-minute bar open after the signal is formed.",
            "",
            md_table(views["cost"]),
            "",
            "The result shows that even though the ZN statistical relationship is clear in this sample, transaction costs matter a lot. With a 1-tick round-trip cost, the average net return falls sharply and becomes negative. Therefore, I interpret this mainly as a statistical out-of-sample observation, not as evidence that the strategy is directly tradable.",
            "",
            "## 6. Data Processing Notes",
            "",
            "The main data-processing choices are:",
            "",
            "- Each contract uses a trading window that fits its own market;",
            "- Timestamps are handled in New York time;",
            "- Holidays, early-close days, and days with missing key prices are excluded from the main sample;",
            "- Around continuous-contract rolls, days are excluded when the previous close and current-day prices come from different underlying contracts;",
            "- Raw Databento data is not uploaded to GitHub. The repository only keeps code, data notes, and result tables.",
            "",
            "These choices reduce the sample size, but they help avoid obvious inconsistencies in the return calculations.",
            "",
            "## 7. Summary",
            "",
            "The main findings are:",
            "",
            "- The project completes a partial replication of the core specifications for six CME futures contracts.",
            "- During the paper-overlap period, ES, NQ, GC, and ZN have positive Eq.(7) results that are significant at conventional nominal levels.",
            "- CL and 6E do not show a statistically significant positive relationship during the paper-overlap period used in this project.",
            "- In the 2021-2025 out-of-sample period, only ZN remains significantly positive.",
            "- Most contracts have weak out-of-sample prediction performance, so the intraday momentum relationship does not appear consistently across all contracts.",
            "- Even when the statistical relationship is significant, transaction costs can remove the apparent trading profitability.",
            "",
            "Overall, this project provides a partial replication of the core specifications for six CME futures contracts. In the paper-overlap period, the positive relationship is mainly found in ES, NQ, GC, and ZN, while the later out-of-sample results do not continue across all contracts.",
        ]
    )


def main() -> None:
    REPORT_ROOT.mkdir(exist_ok=True)
    views = result_views()
    (REPORT_ROOT / "final_baseline_summary_zh.md").write_text(chinese_summary(views), encoding="utf-8")
    (REPORT_ROOT / "final_baseline_summary_en.md").write_text(english_summary(views), encoding="utf-8")
    print("Final summaries written.")


if __name__ == "__main__":
    main()
