#!/usr/bin/env python3
"""Run the main regression and strategy analysis for one futures symbol."""

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
PIPELINE_VERSION = "boundary_corrected_v1"
STRICT_REPLICATION_END = "2020-05-01"
OOS_START = "2021-01-01"
OOS_END = "2025-12-31"

SAMPLES = {
    "replication": ("2010-06-07", STRICT_REPLICATION_END),
    "oos": (OOS_START, OOS_END),
}

REGRESSION_SPECS = {
    "eq5_onfh": ["r_ONFH"],
    "eq6_onfh_m_slh": ["r_ONFH", "r_M", "r_SLH"],
    "eq7_rod": ["r_ROD"],
}

TICK_SIZES = {
    "ES.v.0": 0.25,
    "NQ.v.0": 0.25,
    "GC.v.0": 0.1,
    "CL.v.0": 0.01,
    "ZN.v.0": 0.015625,
    "6E.v.0": 0.00005,
}

ROUND_TRIP_TICKS = [0, 1, 2, 3]


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
        "notes": MANIFEST_ROOT / f"{prefix}_analysis_notes.md",
    }


def newey_west_lags(nobs: int) -> int:
    return int(np.floor(4 * (nobs / 100) ** (2 / 9)))


def load_sample(daily_path: Path) -> pd.DataFrame:
    if not daily_path.exists():
        raise SystemExit(f"Daily table not found: {daily_path}")
    df = pd.read_parquet(daily_path)
    if "pipeline_version" not in df.columns or set(df["pipeline_version"].dropna().unique()) != {PIPELINE_VERSION}:
        raise SystemExit(
            f"Daily table is not {PIPELINE_VERSION}; regenerate corrected daily table first: {daily_path}"
        )
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
    model_df = df[["r_LH", *predictors]].dropna().copy()
    model, hac, maxlags = fit_hac(model_df["r_LH"], model_df[predictors])
    params, bse, tvalues, pvalues, conf = robust_parts(model, hac)
    row = {
        "pipeline_version": PIPELINE_VERSION,
        "sample": sample_name,
        "sample_scope": "equation_available",
        "spec": spec_name,
        "predictors": "+".join(predictors),
        "start": df.loc[model_df.index, "trade_date"].min().date().isoformat(),
        "end": df.loc[model_df.index, "trade_date"].max().date().isoformat(),
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


def common_valid_sample(df: pd.DataFrame) -> pd.DataFrame:
    required = ["r_LH", "r_ONFH", "r_M", "r_SLH", "r_ROD"]
    return df.dropna(subset=required).copy()


def common_regression_summary(df: pd.DataFrame, sample_name: str) -> list[dict[str, Any]]:
    common = common_valid_sample(df)
    rows = []
    for spec_name, predictors in REGRESSION_SPECS.items():
        row = regression_summary(common, sample_name, spec_name, predictors)
        row["sample_scope"] = "common_valid_all_eq5_eq6_eq7"
        row["common_valid_nobs"] = int(len(common))
        rows.append(row)
    return rows


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
                    "pipeline_version": PIPELINE_VERSION,
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


def forecast_strategy_return_basis(df: pd.DataFrame) -> str:
    return "r_LH_executable" if "r_LH_executable" in df.columns else "r_LH"


def annualized_sharpe(returns: pd.Series) -> float:
    returns = returns.astype(float).dropna()
    vol_daily = returns.std(ddof=1)
    if len(returns) < 2 or vol_daily == 0:
        return np.nan
    return float((returns.mean() * ANNUALIZATION_DAYS) / (vol_daily * np.sqrt(ANNUALIZATION_DAYS)))


def forecast_oos_rows(
    df: pd.DataFrame,
    spec_name: str,
    predictors: list[str],
    training_method: str,
) -> pd.DataFrame:
    replication = sample_for_name(df, "replication").sort_values("trade_date")
    oos = sample_for_name(df, "oos").sort_values("trade_date")
    return_basis = forecast_strategy_return_basis(df)
    rows = []

    if training_method == "frozen_2020":
        fixed_train = replication.copy()
        model = sm.OLS(
            fixed_train["r_LH"].astype(float),
            sm.add_constant(fixed_train[predictors].astype(float), has_constant="add"),
        ).fit()
        fixed_benchmark = float(fixed_train["r_LH"].mean())

    for test_row in oos.itertuples(index=False):
        if training_method == "frozen_2020":
            train = fixed_train
            model_for_day = model
            benchmark = fixed_benchmark
        elif training_method == "expanding":
            prior_oos = oos[oos["trade_date"] < test_row.trade_date]
            train = pd.concat([replication, prior_oos], ignore_index=True).sort_values("trade_date")
            model_for_day = sm.OLS(
                train["r_LH"].astype(float),
                sm.add_constant(train[predictors].astype(float), has_constant="add"),
            ).fit()
            benchmark = float(train["r_LH"].mean())
        else:
            raise ValueError(f"Unknown training_method: {training_method}")

        x_test = pd.DataFrame([{predictor: getattr(test_row, predictor) for predictor in predictors}])
        x_test = sm.add_constant(x_test.astype(float), has_constant="add")
        y_pred = float(model_for_day.predict(x_test).iloc[0])
        y_actual = float(test_row.r_LH)
        strategy_lh = float(getattr(test_row, return_basis))
        forecast_strategy_return = strategy_lh if y_pred > 0 else -strategy_lh
        train_cutoff = train["trade_date"].max()
        rows.append(
            {
                "pipeline_version": PIPELINE_VERSION,
                "spec": spec_name,
                "training_method": training_method,
                "prediction_date": test_row.trade_date.date().isoformat(),
                "training_start": train["trade_date"].min().date().isoformat(),
                "training_cutoff_date": train_cutoff.date().isoformat(),
                "n_train": int(len(train)),
                "n_test": 1,
                "actual_r_LH": y_actual,
                "model_prediction": y_pred,
                "benchmark_prediction": benchmark,
                "squared_error_model": float((y_actual - y_pred) ** 2),
                "squared_error_benchmark": float((y_actual - benchmark) ** 2),
                "forecast_strategy_return": forecast_strategy_return,
                "forecast_strategy_return_basis": return_basis,
            }
        )
    return pd.DataFrame(rows)


def oos_r2_outputs(df: pd.DataFrame) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    summary_rows = []
    prediction_frames = []
    for spec_name, predictors in REGRESSION_SPECS.items():
        for method in ["expanding", "frozen_2020"]:
            predictions = forecast_oos_rows(df, spec_name, predictors, method)
            prediction_frames.append(predictions)
            mspe_model = float(predictions["squared_error_model"].mean())
            mspe_benchmark = float(predictions["squared_error_benchmark"].mean())
            r2_oos = 1 - mspe_model / mspe_benchmark if mspe_benchmark != 0 else np.nan
            summary_rows.append(
                {
                    "pipeline_version": PIPELINE_VERSION,
                    "spec": spec_name,
                    "training_method": method,
                    "training_description": (
                        "Re-estimate each prediction day using strict replication sample plus prior OOS observations"
                        if method == "expanding"
                        else "Estimate once using strict replication sample through 2020-05-01; hold fixed through OOS"
                    ),
                    "strict_replication_end": STRICT_REPLICATION_END,
                    "test_start": predictions["prediction_date"].min(),
                    "test_end": predictions["prediction_date"].max(),
                    "n_test": int(len(predictions)),
                    "first_training_cutoff_date": predictions["training_cutoff_date"].iloc[0],
                    "last_training_cutoff_date": predictions["training_cutoff_date"].iloc[-1],
                    "mspe_model": mspe_model,
                    "mspe_benchmark": mspe_benchmark,
                    "r2_oos": float(r2_oos),
                    "r2_oos_x100": float(r2_oos * 100),
                    "forecast_strategy_sharpe": annualized_sharpe(predictions["forecast_strategy_return"]),
                    "forecast_strategy_return_basis": predictions["forecast_strategy_return_basis"].iloc[0],
                }
            )
    return summary_rows, pd.concat(prediction_frames, ignore_index=True)


def max_drawdown(simple_returns: pd.Series) -> float:
    wealth = (1 + simple_returns.fillna(0)).cumprod()
    drawdown = wealth / wealth.cummax() - 1
    return float(drawdown.min())


def strategy_returns(df: pd.DataFrame, return_basis: str) -> pd.DataFrame:
    columns = ["trade_date", "year", "r_ONFH", "r_ROD", "r_LH"]
    if return_basis not in columns:
        columns.append(return_basis)
    out = df[columns].copy()
    out["strategy_return_basis"] = return_basis
    out["strategy_price_type"] = "paper_statistical" if return_basis == "r_LH" else "executable_next_open"
    out["entry_price"] = df["p_close_minus_30"] if return_basis == "r_LH" else df["p_lh_entry_next_open"]
    out["r_LH_strategy"] = out[return_basis]
    out["timing_rONFH"] = np.where(out["r_ONFH"] > 0, out["r_LH_strategy"], -out["r_LH_strategy"])
    out["timing_rROD"] = np.where(out["r_ROD"] > 0, out["r_LH_strategy"], -out["r_LH_strategy"])
    agree_positive = (out["r_ONFH"] > 0) & (out["r_ROD"] > 0)
    agree_negative = (out["r_ONFH"] < 0) & (out["r_ROD"] < 0)
    out["timing_agree_ONFH_ROD"] = np.select(
        [agree_positive, agree_negative],
        [out["r_LH_strategy"], -out["r_LH_strategy"]],
        default=0.0,
    )
    out["timing_agree_traded"] = agree_positive | agree_negative
    out["always_long"] = out["r_LH_strategy"]
    return out


def strategy_summary(
    returns: pd.Series,
    sample_name: str,
    strategy: str,
    return_basis: str,
    strategy_price_type: str,
    round_trip_ticks: int = 0,
    traded: pd.Series | None = None,
) -> dict[str, Any]:
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
        "strategy_price_type": strategy_price_type,
        "return_basis": return_basis,
        "round_trip_ticks": int(round_trip_ticks),
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
            summary = strategy_summary(
                group[strategy],
                sample_name,
                strategy,
                str(group["strategy_return_basis"].iloc[0]),
                str(group["strategy_price_type"].iloc[0]),
                round_trip_ticks=0,
                traded=traded,
            )
            summary["year"] = int(year)
            rows.append(summary)
    return rows


def cost_adjusted_strategy_returns(strategy_df: pd.DataFrame, tick_size: float, round_trip_ticks: int) -> pd.DataFrame:
    out = strategy_df.copy()
    cost_return = round_trip_ticks * tick_size / out["entry_price"].astype(float)
    for strategy in ["timing_rONFH", "timing_rROD", "always_long"]:
        out[strategy] = out[strategy] - cost_return
    traded = out["timing_agree_traded"].astype(bool)
    out["timing_agree_ONFH_ROD"] = np.where(traded, out["timing_agree_ONFH_ROD"] - cost_return, 0.0)
    out["round_trip_ticks"] = int(round_trip_ticks)
    return out


def main() -> None:
    args = parse_args()
    prefix = symbol_prefix(args.symbol)
    if args.symbol not in TICK_SIZES:
        raise SystemExit(f"Missing tick size for {args.symbol}")
    tick_size = TICK_SIZES[args.symbol]
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
        regression_rows.extend(common_regression_summary(sample, sample_name))

        return_bases = ["r_LH"]
        if "r_LH_executable" in sample.columns:
            return_bases.append("r_LH_executable")
        for return_basis in return_bases:
            strat = strategy_returns(sample, return_basis)
            strategy_price_type = str(strat["strategy_price_type"].iloc[0])
            for round_trip_ticks in ROUND_TRIP_TICKS:
                net_strat = cost_adjusted_strategy_returns(strat, tick_size, round_trip_ticks)
                for strategy in ["timing_rONFH", "timing_agree_ONFH_ROD", "timing_rROD", "always_long"]:
                    traded = net_strat["timing_agree_traded"] if strategy == "timing_agree_ONFH_ROD" else None
                    strategy_rows.append(
                        strategy_summary(
                            net_strat[strategy],
                            sample_name,
                            strategy,
                            return_basis,
                            strategy_price_type,
                            round_trip_ticks=round_trip_ticks,
                            traded=traded,
                        )
                    )
            yearly_rows.extend(summarize_yearly(strat, sample_name))
        manifest_samples[sample_name] = {
            "start": sample["trade_date"].min().date().isoformat(),
            "end": sample["trade_date"].max().date().isoformat(),
            "nobs": int(len(sample)),
            "common_valid_nobs": int(len(common_valid_sample(sample))),
        }

    beta_diff_rows = beta_difference_tests(df)
    r2_oos_rows, _ = oos_r2_outputs(df)

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(regression_rows).to_csv(output_paths["regression"], index=False)
    pd.DataFrame(beta_diff_rows).to_csv(output_paths["beta_diff"], index=False)
    pd.DataFrame(r2_oos_rows).to_csv(output_paths["oos_r2"], index=False)
    pd.DataFrame(strategy_rows).to_csv(output_paths["strategy"], index=False)
    pd.DataFrame(yearly_rows).to_csv(output_paths["yearly"], index=False)

    manifest = {
        "symbol": args.symbol,
        "pipeline_version": PIPELINE_VERSION,
        "daily_table": str(output_paths["daily"]),
        "regression_specs": REGRESSION_SPECS,
        "strict_replication_sample_end": STRICT_REPLICATION_END,
        "extended_training_sample_note": "Any estimate using data after 2020-05-01 must be labeled extended training sample, not strict paper overlap.",
        "statistical_lh_return": "r_LH uses paper boundary prices",
        "strategy_lh_return": "r_LH_executable when present; entry is close-minus-30 boundary next bar open",
        "strategy_rule": "eta(r) = strategy_lh_return if r > 0, otherwise -strategy_lh_return; eta(r_ONFH,r_ROD) trades only when signs agree",
        "beta_difference_test": "pooled regression with OOS dummy and predictor-by-OOS interactions",
        "oos_r2": {
            "expanding": "Each OOS prediction day re-estimates using strict replication sample plus prior OOS observations; benchmark mean also updates through t-1.",
            "fixed_sample": "Estimate once using strict replication sample through 2020-05-01; benchmark mean fixed through OOS.",
        },
        "annualization_days": ANNUALIZATION_DAYS,
        "tick_size": tick_size,
        "round_trip_tick_costs": ROUND_TRIP_TICKS,
        "tick_cost_rule": "Net simple return subtracts round_trip_ticks * tick_size / entry_price for traded days.",
        "strategy_price_types": {
            "paper_statistical": "Entry uses p_close_minus_30, the paper boundary price. This is not a realistic fill.",
            "executable_next_open": "Entry uses p_lh_entry_next_open, the next bar open after signal formation.",
        },
        "newey_west_lag_rule": "floor(4 * (T / 100) ** (2 / 9))",
        "samples": manifest_samples,
        "outputs": {key: str(value) for key, value in output_paths.items() if key != "daily"},
    }
    output_paths["notes"].write_text(
        f"# {args.symbol} Analysis Notes\n\n"
        "This file records the inputs, model choices, and output files for this symbol's analysis.\n\n"
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
