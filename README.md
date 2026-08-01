# 日内动量论文复现项目

这个项目是对 Baltussen、Da、Lammers 和 Martens 的论文
《Hedging Demand and Market Intraday Momentum》做一个基础复现。
论文主要研究的是：期货市场在一天内前面几个时间段的价格变化，
能不能解释或预测最后半小时的价格变化。

我使用 Databento 的 CME 期货一分钟数据，对六个连续期货合约分别做了单品种复现：

- ES：E-mini S&P 500
- NQ：E-mini Nasdaq 100
- GC：黄金期货
- CL：WTI 原油期货
- ZN：10 年期美国国债期货
- 6E：欧元外汇期货

项目的目标不是构建一个真实交易系统，而是尽量按照论文思路，
把数据处理、收益率计算、回归分析和结果整理完整跑通。

## 文件结构

```text
intraday_momentum/
  trading_times.py     # 六个期货品种的交易时间和取价规则

scripts/
  download_data.py     # 下载一个品种的数据
  build_daily_data.py  # 把一分钟数据整理成每日研究表
  run_analysis.py      # 对一个品种跑回归和策略统计
  make_summary.py      # 汇总六个品种的最终结果
  check_data.py        # 检查本地下载的数据

reports/
  final_baseline_summary_zh.md      # 中文结果总结
  final_baseline_summary_en.md      # 英文结果总结
  detailed_results_zh.md            # 更完整的结果附录
  tables/                           # 回归、样本外和策略结果表

data/
  manifests/                        # 数据下载和处理记录，不包含原始行情数据

docs/
  data_notes.md                     # 数据使用和本地文件说明

tests/
  test_trading_times.py # 检查交易时间
  test_oos_methods.py   # 检查样本外方法
```

仓库中没有上传原始行情数据。因为 Databento 数据有授权限制，
`data/raw/`、`data/interim/` 和 `data/processed/` 都被 `.gitignore` 排除了。
如果要重新运行，需要自己下载数据并放在本地。

## 研究方法

每天先根据不同品种的交易时间取几个价格点，然后计算日内不同时间段的收益率。
主要变量包括：

- `r_ONFH`：隔夜到开盘后半小时的收益率
- `r_M`：中间时间段收益率
- `r_SLH`：倒数第二个半小时收益率
- `r_ROD`：从前一交易日收盘到当天最后半小时前的收益率
- `r_LH`：最后半小时收益率

核心回归是用前面已经发生的收益率解释最后半小时收益率。
其中最重要的是论文中的 Eq. (7)，也就是用 `r_ROD` 解释 `r_LH`：

```text
r_LH = alpha + beta * r_ROD + error
```

如果 `beta` 显著为正，说明当天前面大部分时间的方向和最后半小时方向之间存在正相关，
也就是论文所说的日内动量现象。

## 样本划分

项目分成两个主要时间段：

- 论文重叠期：2010 年 6 月到 2020 年 5 月 1 日
- 样本外时期：2021 年 1 月 1 日到 2025 年 12 月 31 日

2020 年 5 月之后到 2020 年底没有放进主要比较里，
这样可以让论文复现期和后面的样本外检验分开。

## 主要结果

在论文重叠期，ES、NQ、GC 和 ZN 的 Eq. (7) 回归结果为正且显著。
CL 和 6E 在单品种层面不显著，因此更适合作为对照品种。

在 2021-2025 年的样本外检验中，只有 ZN 仍然保持比较明显的正向关系。
ES、NQ 和 GC 的结果变弱，CL 和 6E 仍然没有明显的正向关系。

更完整的结果见：

- `reports/final_baseline_summary_zh.md`
- `reports/detailed_results_zh.md`
- `reports/tables/boundary_corrected_v1_regression_long.csv`
- `reports/tables/boundary_corrected_v1_oos_all.csv`
- `reports/tables/boundary_corrected_v1_strategy_all.csv`

## 如何运行

先创建 Python 环境并安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

然后在本地设置 Databento API key。不要把 key 写进代码或上传到 GitHub。

```bash
export DATABENTO_API_KEY="your_key_here"
```

下载某个品种的数据，例如 ES：

```bash
python scripts/download_data.py --symbol ES.v.0 --approved-total 0
```

把一分钟数据整理成每日研究表。不同品种需要使用不同的交易时间，
这些时间可以在 `intraday_momentum/trading_times.py` 里查看。

```bash
python scripts/build_daily_data.py \
  --symbol ES.v.0 \
  --calendar NYSE \
  --window-start 09:30 \
  --open-plus-30 10:00 \
  --close-minus-60 15:00 \
  --close-minus-30 15:30 \
  --close 16:00
```

运行一个品种的核心复现：

```bash
python scripts/run_analysis.py --symbol ES.v.0
```

如果六个品种都已经处理完成，可以生成最终汇总：

```bash
python scripts/make_summary.py
```

也可以运行测试：

```bash
python -m unittest tests/test_trading_times.py tests/test_oos_methods.py
```

## 数据说明

这个项目只上传代码、说明文档、数据清单和结果表。
不要上传以下内容：

- Databento API key
- `.env` 文件
- 原始行情数据
- 处理后的 parquet 数据
- 大型中间文件

这些文件已经在 `.gitignore` 中排除。

## 项目局限

这个项目主要是课程学习性质的论文复现，还有很多地方可以继续改进：

- 没有复现论文中所有资产类别和所有附录结果。
- 使用的是连续期货合约，和论文原始数据可能不完全一样。
- 样本外结果只能说明历史统计关系，不能直接说明可以真实交易获利。
- 交易成本、滑点和实际成交问题这里只做了比较简单的讨论。
