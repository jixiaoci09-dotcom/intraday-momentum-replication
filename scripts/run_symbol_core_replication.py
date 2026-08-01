#!/usr/bin/env python3
"""Run paper Eq. (5)-(7) and Eq. (12) for one cleaned daily symbol table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats


PROCESSED_ROOT = Path("data/processed")
REPORT_ROOT = Path("reports/tables")
MANIFEST_ROOT = Path("data/manifests")
ANNUALIZATION_DAYS = 252

SAMPLES = {
    "replication": ("2010-06-07", "2020-05-31"),
    "oos": ("2021-01-01", "2025-12-31"),
}

REGRESSION_SPECS = {
    "eq5_onfh": ["r_ONFH"],
    "eq6_onfh_m_slh": ["r_ONFH", "r_M", "r_SLH"],
    "eq7_rod": ["r_ROD"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", required=True, help="Continuous symbol, e.g. NQ.v.0")
    return parser.parse_args()


def symbol_prefix(symbol: str) -> str:
    return symbol.split(".")[0].lower()


def paths(prefix: str) -> dict[str, Path]:
    return {
        "daily": PROCESSED_ROOT / f"{prefix}_daily_research_table.parquet",
        "regression": REPORT_ROOT / f"{prefix}_core_regression_summary.csv",
        "beta_diff": REPORT_ROOT / f"{prefix}_core_beta_difference_tests.csv",
        "oos_r2": REPORT_ROOT / f"{prefix}_core_oos_r2.csv",
        "strategy": REPORT_ROOT / f"{prefix}_core_strategy_summary.csv",
        "yearly": REPORT_ROOT / f"{prefix}_core_strategy_by_year.csv",
        "manifest": MANIFEST_ROOT / f"{prefix}_core_replication_manifest.md",
    }


def newey_west_lags(nobs: int) -> int:
    return int(np.floor(4 * (nobs / 100) ** (2 / 9)))


def load_sample(daily_path: Path) -> pd.DataFrame:
    if not daily_path.exists():
        raise SystemExit(f"Daily table not found: {daily_path}")
    df = pd.read_parquet(daily_path)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df = df[df["include"]].copy()
    df["year"] = df["trade_date"].dt.year
    return df


def sample_for_name(df: pd.DataFrame, sample_name: str) -> pd.DataFrame:
    start, end = SAMPLES[sample_name]
    sample = df[(df["trade_date"] >= start) & (df["trade_date"] <= end)].copy()
    if sample.empty:
        raise SystemExit(f"No rows for sample {sample_name}: {start} to {end}")
    return sample


def fit_hac(y: pd.Series, x: pd.DataFrame) -> tuple[Any, Any, int]:
    x_const = sm.add_constant(x.astype(float), has_constant="add")
    model = sm.OLS(y.astype(float), x_const).fit()
    maxlags = newey_west_lags(int(model.nobs))
    hac = model.get_robustcov_results(cov_type="HAC", maxlags=maxlags, use_t=True)
    return model, hac, maxlags


def robust_parts(model: Any, hac: Any) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.DataFrame]:
    index = model.params.index
    params = pd.Series(hac.params, index=index)
    bse = pd.Series(hac.bse, index=index)
    tvalues = pd.Series(hac.tvalues, index=index)
    pvalues = pd.Series(hac.pvalues, index=index)
    conf = pd.DataFrame(hac.conf_int(alpha=0.05), index=index, columns=["ci_low", "ci_high"])
    return params, bse, tvalues, pvalues, conf


def add_beta_columns(
    row: dict[str, Any],
    params: pd.Series,
    bse: pd.Series,
    tvalues: pd.Series,
    pvalues: pd.Series,
    conf: pd.DataFrame,
) -> None:
    for predictor in ["r_ONFH", "r_M", "r_SLH", "r_ROD"]:
        if predictor in params.index:
            row[f"beta_{predictor}"] = float(params[predictor])
            row[f"beta_{predictor}_x100"] = float(params[predictor] * 100)
            row[f"beta_{predictor}_se_hac"] = float(bse[predictor])
            row[f"beta_{predictor}_t_hac"] = float(tvalues[predictor])
            row[f"beta_{predictor}_p_hac"] = float(pvalues[predictor])
            row[f"beta_{predictor}_ci_low"] = float(conf.loc[predictor, "ci_low"])
            row[f"beta_{predictor}_ci_high"] = float(conf.loc[predictor, "ci_high"])
        else:
            row[f"beta_{predictor}"] = np.nan
            row[f"beta_{predictor}_x100"] = np.nan
            row[f"beta_{predictor}_se_hac"] = np.nan
            row[f"beta_{predictor}_t_hac"] = np.nan
            row[f"beta_{predictor}_p_hac"] = np.nan
            row[f"beta_{predictor}_ci_low"] = np.nan
            row[f"beta_{predictor}_ci_high"] = np.nan


def regression_summary(df: pd.DataFrame, sample_name: str, spec_name: str, predictors: list[str]) -> dict[str, Any]:
    model, hac, maxlags = fit_hac(df["r_LH"], df[predictors])
    params, bse, tvalues, pvalues, conf = robust_parts(model, hac)
    row = {
        "sample": sample_name,
        "spec": spec_name,
        "predictors": "+".join(predictors),
        "start": df["trade_date"].min().date().isoformat(),
        "end": df["trade_date"].max().date().isoformat(),
        "nobs": int(model.nobs),
        "nw_lags": maxlags,
        "alpha": float(params["const"]),
        "alpha_se_hac": float(bse["const"]),
        "alpha_t_hac": float(tvalues["const"]),
        "alpha_p_hac": float(pvalues["const"]),
        "alpha_ci_low": float(conf.loc["const", "ci_low"]),
        "alpha_ci_high": float(conf.loc["const", "ci_high"]),
        "r2": float(model.rsquared),
        "r2_x100": float(model.rsquared * 100),
        "adj_r2": float(model.rsquared_adj),
        "adj_r2_x100": float(model.rsquared_adj * 100),
    }
    add_beta_columns(row, params, bse, tvalues, pvalues, conf)
    return row


def beta_difference_tests(df: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    replication = sample_for_name(df, "replication").copy()
    replication["period_oos"] = 0
    oos = sample_for_name(df, "oos").copy()
    oos["period_oos"] = 1
    combined = pd.concat([replication, oos], ignore_index=True).sort_values("trade_date")

    for spec_name, predictors in REGRESSION_SPECS.items():
        x = combined[predictors + ["period_oos"]].copy()
        for predictor in predictors:
            x[f"{predictor}_x_oos"] = combined[predictor] * combined["period_oos"]
        model, hac, maxlags = fit_hac(combined["r_LH"], x)
        params, bse, tvalues, pvalues, conf = robust_parts(model, hac)
        for predictor in predictors:
            interaction = f"{predictor}_x_oos"
            beta_rep = float(params[predictor])
            beta_diff = float(params[interaction])
            rows.append(
                {
                    "spec": spec_name,
                    "predictor": predictor,
                    "nobs": int(model.nobs),
                    "nw_lags": maxlags,
                    "beta_replication": beta_rep,
                    "beta_replication_x100": beta_rep * 100,
                    "beta_oos_minus_replication": beta_diff,
                    "beta_oos_minus_replication_x100": beta_diff * 100,
                    "beta_oos_implied": beta_rep + beta_diff,
                    "beta_oos_implied_x100": (beta_rep + beta_diff) * 100,
                    "difference_se_hac": float(bse[interaction]),
                    "difference_t_hac": float(tvalues[interaction]),
                    "difference_p_hac": float(pvalues[interaction]),
                    "difference_ci_low": float(conf.loc[interaction, "ci_low"]),
                    "difference_ci_high": float(conf.loc[interaction, "ci_high"]),
                }
            )
    return rows


def oos_r2_rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    train = sample_for_name(df, "replication")
    test = sample_for_name(df, "oos")
    y_train = train["r_LH"].astype(float)
    y_test = test["r_LH"].astype(float)
    benchmark = float(y_train.mean())

    for spec_name, predictors in REGRESSION_SPECS.items():
        train_x = sm.add_constant(train[predictors].astype(float), has_constant="add")
        test_x = sm.add_constant(test[predictors].astype(float), has_constant="add")
        model = sm.OLS(y_train, train_x).fit()
        pred = model.predict(test_x)
        sse_model = float(((y_test - pred) ** 2).sum())
        sse_benchmark = float(((y_test - benchmark) ** 2).sum())
        r2_oos = 1 - sse_model / sse_benchmark if sse_benchmark != 0 else np.nan
        rows.append(
            {
                "spec": spec_name,
                "train_start": train["trade_date"].min().date().isoformat(),
                "train_end": train["trade_date"].max().date().isoformat(),
                "test_start": test["trade_date"].min().date().isoformat(),
                "test_end": test["trade_date"].max().date().isoformat(),
                "n_train": int(len(train)),
                "n_test": int(len(test)),
                "benchmark": "replication_mean_r_LH",
                "benchmark_mean": benchmark,
                "sse_model": sse_model,
                "sse_benchmark": sse_benchmark,
                "r2_oos": float(r2_oos),
                "r2_oos_x100": float(r2_oos * 100),
            }
        )
    return rows


def max_drawdown(simple_returns: pd.Series) -> float:
    wealth = (1 + simple_returns.fillna(0)).cumprod()
    drawdown = wealth / wealth.cummax() - 1
    return float(drawdown.min())


def strategy_returns(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["trade_date", "year", "r_ONFH", "r_ROD", "r_LH"]].copy()
    out["timing_rONFH"] = np.where(out["r_ONFH"] > 0, out["r_LH"], -out["r_LH"])
    out["timing_rROD"] = np.where(out["r_ROD"] > 0, out["r_LH"], -out["r_LH"])
    agree_positive = (out["r_ONFH"] > 0) & (out["r_ROD"] > 0)
    agree_negative = (out["r_ONFH"] < 0) & (out["r_ROD"] < 0)
    out["timing_agree_ONFH_ROD"] = np.select(
        [agree_positive, agree_negative],
        [out["r_LH"], -out["r_LH"]],
        default=0.0,
    )
    out["timing_agree_traded"] = agree_positive | agree_negative
    out["always_long"] = out["r_LH"]
    return out


def strategy_summary(returns: pd.Series, sample_name: str, strategy: str, traded: pd.Series | None = None) -> dict[str, Any]:
    returns = returns.astype(float).dropna()
    trade_count = len(returns) if traded is None else int(traded.loc[returns.index].sum())
    avg_daily = returns.mean()
    vol_daily = returns.std(ddof=1)
    avg_ann = avg_daily * ANNUALIZATION_DAYS
    vol_ann = vol_daily * np.sqrt(ANNUALIZATION_DAYS)
    sharpe = avg_ann / vol_ann if vol_ann != 0 else np.nan
    t_stat = avg_daily / (vol_daily / np.sqrt(len(returns))) if vol_daily != 0 else np.nan
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=len(returns) - 1)) if len(returns) > 1 else np.nan

    return {
        "sample": sample_name,
        "strategy": strategy,
        "nobs": int(len(returns)),
        "trade_count": int(trade_count),
        "trade_rate": float(trade_count / len(returns)) if len(returns) else np.nan,
        "avg_daily": float(avg_daily),
        "avg_ann": float(avg_ann),
        "avg_ann_pct": float(avg_ann * 100),
        "vol_ann": float(vol_ann),
        "vol_ann_pct": float(vol_ann * 100),
        "sharpe": float(sharpe),
        "success_rate": float((returns > 0).mean()),
        "max_drawdown": max_drawdown(returns),
        "avg_trade_return": float(avg_daily),
        "avg_trade_return_bp": float(avg_daily * 10000),
        "t_stat_mean": float(t_stat),
        "p_value_mean": float(p_value),
    }


def summarize_yearly(strategy_df: pd.DataFrame, sample_name: str) -> list[dict[str, Any]]:
    rows = []
    for year, group in strategy_df.groupby("year"):
        for strategy in ["timing_rONFH", "timing_agree_ONFH_ROD", "timing_rROD", "always_long"]:
            traded = group["timing_agree_traded"] if strategy == "timing_agree_ONFH_ROD" else None
            summary = strategy_summary(group[strategy], sample_name, strategy, traded=traded)
            summary["year"] = int(year)
            rows.append(summary)
    return rows


def main() -> None:
    args = parse_args()
    prefix = symbol_prefix(args.symbol)
    output_paths = paths(prefix)
    df = load_sample(output_paths["daily"])

    regression_rows = []
    strategy_rows = []
    yearly_rows = []
    manifest_samples = {}
    for sample_name in SAMPLES:
        sample = sample_for_name(df, sample_name)
        for spec_name, predictors in REGRESSION_SPECS.items():
            regression_rows.append(regression_summary(sample, sample_name, spec_name, predictors))

        strat = strategy_returns(sample)
        strategy_rows.append(strategy_summary(strat["timing_rONFH"], sample_name, "timing_rONFH"))
        strategy_rows.append(
            strategy_summary(
                strat["timing_agree_ONFH_ROD"],
                sample_name,
                "timing_agree_ONFH_ROD",
                traded=strat["timing_agree_traded"],
            )
        )
        strategy_rows.append(strategy_summary(strat["timing_rROD"], sample_name, "timing_rROD"))
        strategy_rows.append(strategy_summary(strat["always_long"], sample_name, "always_long"))
        yearly_rows.extend(summarize_yearly(strat, sample_name))
        manifest_samples[sample_name] = {
            "start": sample["trade_date"].min().date().isoformat(),
            "end": sample["trade_date"].max().date().isoformat(),
            "nobs": int(len(sample)),
        }

    beta_diff_rows = beta_difference_tests(df)
    r2_oos_rows = oos_r2_rows(df)

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(regression_rows).to_csv(output_paths["regression"], index=False)
    pd.DataFrame(beta_diff_rows).to_csv(output_paths["beta_diff"], index=False)
    pd.DataFrame(r2_oos_rows).to_csv(output_paths["oos_r2"], index=False)
    pd.DataFrame(strategy_rows).to_csv(output_paths["strategy"], index=False)
    pd.DataFrame(yearly_rows).to_csv(output_paths["yearly"], index=False)

    manifest = {
        "symbol": args.symbol,
        "daily_table": str(output_paths["daily"]),
        "regression_specs": REGRESSION_SPECS,
        "strategy_rule": "eta(r) = r_LH if r > 0, otherwise -r_LH; eta(r_ONFH,r_ROD) trades only when signs agree",
        "beta_difference_test": "pooled regression with OOS dummy and predictor-by-OOS interactions",
        "oos_r2": "model trained on replication; benchmark is replication-sample mean r_LH",
        "annualization_days": ANNUALIZATION_DAYS,
        "newey_west_lag_rule": "floor(4 * (T / 100) ** (2 / 9))",
        "samples": manifest_samples,
        "outputs": {key: str(value) for key, value in output_paths.items() if key != "daily"},
    }
    output_paths["manifest"].write_text(
        f"# {args.symbol} Core Replication Manifest\n\n"
        "This replication uses the frozen cleaned daily table rules for the symbol and "
        "the paper's Table 2 Eq. (5)-(7) and Table 6 Eq. (12) logic.\n\n"
        "```json\n"
        + json.dumps(manifest, indent=2)
        + "\n```\n",
        encoding="utf-8",
    )

    print(f"{args.symbol} core replication complete")
    print(pd.DataFrame(regression_rows).to_string(index=False))
    print()
    print(pd.DataFrame(beta_diff_rows).to_string(index=False))
    print()
    print(pd.DataFrame(r2_oos_rows).to_string(index=False))
    print()
    print(pd.DataFrame(strategy_rows).to_string(index=False))


if __name__ == "__main__":
    main()
