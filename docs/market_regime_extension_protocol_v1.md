# Market Regime Extension Protocol v1.0

Status: pre-analysis protocol. Do not run extension regressions until this
document is explicitly approved.

## Research Question

Why does ZN retain intraday closing momentum in 2021-2025 while ES, NQ, and GC
show post-publication attenuation?

CL and 6E are not part of the attenuation group because their single-contract
Eq. (7) coefficients are not significantly positive in the replication period.
They remain null/control contracts for detecting whether state filters can
manufacture false positives.

## Frozen Baseline

All extension work must start from the frozen baseline:

- Pipeline version: `boundary_corrected_v1`.
- Strict replication sample: first valid trading day through `2020-05-01`.
- Post-publication OOS sample: `2021-01-01` through `2025-12-31`.
- Product-specific effective sessions:
  - ES and NQ: `09:30-16:00` America/New_York.
  - GC: `08:20-13:30` America/New_York.
  - CL: `09:00-14:30` America/New_York.
  - ZN: `08:20-15:00` America/New_York.
  - 6E: `07:20-14:00` America/New_York.
- Non-open theoretical boundary price at time `T`: close of the `T-1 minute`
  OHLCV-1m bar.
- Session open price: open of the bar with `ts_event == session_open`.
- Entry for executable last-half-hour strategy: open of the bar with
  `ts_event == close_minus_30`.
- No cross-contract previous-close returns.
- Early closes and missing exact boundaries are excluded.

## State Variables

Every state variable must be known before the close-minus-30 signal is traded.
No state may use the current day's final close or any future observation.

### 1. 20-Day Historical Volatility

Definition:

```text
daily_ROD_t = P_{t, close-30} / P_{t-1, close} - 1
HV20_t = std(daily_ROD_{t-20}, ..., daily_ROD_{t-1}) * sqrt(252)
```

Fields:

- `p_prev_close`
- `p_close_minus_30`
- `r_ROD`

Availability:

- `HV20_t` is known before the close-minus-30 decision on day `t` because it
  uses only observations through day `t-1`.

Minimum history and missing values:

- Require at least 20 prior included observations for the symbol.
- If fewer than 20 prior observations exist, drop the state-regression row and
  record `drop_reason = insufficient_hv20_history`.

### 2. Close-Pre Relative Volume

Definition:

```text
VolPre_t = volume from session open through close-30 source bar
RelVol20_t = VolPre_t / mean(VolPre_{t-20}, ..., VolPre_{t-1})
```

Fields:

- Minute-level OHLCV `volume` from the effective session open through the
  close-minus-30 source bar.
- If only the existing daily table is used, `volume_effective_window` is not
  sufficient because it includes the last half hour. The extension pipeline must
  either rebuild a pre-entry volume field from raw OHLCV-1m or add a new daily
  field `volume_open_to_close_minus_30`.

Availability:

- `VolPre_t` is known at close-minus-30 because it ends at the signal boundary.
- The denominator uses only days through `t-1`.

Minimum history and missing values:

- Require at least 20 prior included observations with valid `VolPre`.
- If missing, drop the state-regression row and record
  `drop_reason = insufficient_relvol20_history` or `missing_pre_entry_volume`.

### 3. Intraday Path Efficiency

Definition:

```text
PathEff_t = abs(P_{t, close-30} / P_{t-1, close} - 1)
            / sum_{m in pre-entry path} abs(P_m / P_{m-1} - 1)
```

The pre-entry path starts at the previous effective close and ends at the
close-minus-30 source bar. The denominator uses one-minute close-to-close
absolute returns during the pre-entry interval. The previous close to current
session first usable minute transition is included when both prices are from
the same active contract.

Fields:

- `p_prev_close`
- Raw OHLCV-1m `close` for all bars from session open through close-minus-30
  source bar.
- `p_close_minus_30`

Availability:

- Known at close-minus-30. No current-day close after close-minus-30 may enter
  the numerator or denominator.

Minimum history and missing values:

- No 20-day lookback is required for the raw value, but quantile assignment
  requires historical observations through `t-1`.
- If the pre-entry path has missing bars needed for the path sum, drop the
  state-regression row and record `drop_reason = missing_path_efficiency_bar`.

## Quantile Boundaries and State Groups

Each state is assigned within symbol using expanding historical quantiles.

For day `t`:

```text
q_low_t  = 33.333rd percentile of State_s over all valid dates s < t
q_high_t = 66.667th percentile of State_s over all valid dates s < t
```

Rules:

- Use only dates strictly before `t`.
- Require at least 252 prior valid state observations before assigning
  low/mid/high.
- If fewer than 252 valid prior observations exist, drop the state-regression
  row and record `drop_reason = insufficient_quantile_history`.
- Low: `State_t <= q_low_t`.
- Mid: `q_low_t < State_t <= q_high_t`.
- High: `State_t > q_high_t`.
- Ties are assigned deterministically by these inequalities.
- Quantile thresholds are never recomputed using future data.

## Regression Specifications

Primary baseline:

```text
LH_t = alpha + beta * ROD_t + epsilon_t
```

State interaction within each symbol:

```text
LH_t = alpha
       + beta * ROD_t
       + gamma_mid * I(State_t = mid)
       + gamma_high * I(State_t = high)
       + delta_mid * ROD_t * I(State_t = mid)
       + delta_high * ROD_t * I(State_t = high)
       + epsilon_t
```

Low state is the omitted category.

Post-period attenuation with state interactions:

```text
LH_t = alpha
       + beta * ROD_t
       + theta * Post_t
       + phi * ROD_t * Post_t
       + gamma_mid * I(State_t = mid)
       + gamma_high * I(State_t = high)
       + delta_mid * ROD_t * I(State_t = mid)
       + delta_high * ROD_t * I(State_t = high)
       + psi_mid * ROD_t * I(State_t = mid) * Post_t
       + psi_high * ROD_t * I(State_t = high) * Post_t
       + controls for State_t * Post_t
       + epsilon_t
```

`Post_t = 1` for 2021-2025 OOS observations and `0` for the strict replication
sample. If an extended training sample is ever used, it must be labeled
explicitly and may not be mixed into strict paper-overlap estimates.

## Newey-West and Inference

- Use the frozen baseline Newey-West lag rule:

```text
floor(4 * (T / 100) ** (2 / 9))
```

- Use HAC/Newey-West standard errors with `use_t=True`, matching the baseline.
- Report coefficient, HAC standard error, t-statistic, p-value, 95% confidence
  interval, adjusted R2, sample start, sample end, and N.
- Display p-values below 0.001 as `p<0.001` in reports while preserving numeric
  values in CSV files.

## Hypothesis Families

Primary hypothesis family:

- ZN state interactions in 2021-2025 for the three pre-specified states:
  `HV20`, `RelVol20`, `PathEff`.
- Main coefficients of interest:
  - `ROD * State`.
  - `ROD * Post`.
  - `ROD * State * Post`.

Control/false-positive family:

- The same state-interaction tests for CL and 6E.

Attenuation comparison family:

- ES, NQ, and GC state interactions designed to explain attenuation.

Multiple testing:

- Apply Benjamini-Hochberg FDR correction within each hypothesis family.
- Report unadjusted p-values and FDR-adjusted q-values.
- Do not select states, thresholds, or symbols based on unadjusted significance.

## Primary vs Exploratory Tests

Primary tests:

- ZN `ROD * State` and `ROD * State * Post` for the three pre-specified states.
- ES/NQ/GC `ROD * Post` and `ROD * State * Post` as attenuation comparisons.
- CL/6E as null/control checks.

Exploratory tests:

- Alternative state definitions.
- Alternative lookback windows.
- State combinations.
- Asset-class pooled regressions.
- Additional transaction-cost models beyond fixed tick costs.

Exploratory tests must be clearly labeled and cannot change the frozen primary
conclusions.

## Economic Significance and Transaction Costs

For every state-conditioned strategy:

- Use only `r_LH_executable` for tradability tests.
- Entry is the next bar open after signal formation.
- Report gross results and 0/1/2/3 tick total round-trip cost scenarios.
- A round-trip cost of 2 ticks equals one-way 1 tick.
- Do not double-count costs at both entry and exit.
- Report annualized return, annualized volatility, Sharpe, win rate, maximum
  drawdown, average trade return, cumulative net return, and break-even
  round-trip tick cost.

Economic significance rule:

- A state result is economically interesting only if the OOS executable
  strategy remains positive after at least 1 tick total round-trip cost and the
  associated predictive coefficient survives the pre-specified inference
  standard.

## Look-Ahead Controls

The extension must enforce:

- No same-day final close in state variables.
- No future observations in quantile thresholds.
- Day `t` quantiles use only dates `< t`.
- No threshold, window, state definition, or symbol inclusion rule may be
  changed after observing extension results.
- Missing values are dropped only under pre-declared rules.

## Required Outputs After Approval

- State daily table manifest.
- State variable audit table with timestamps and availability checks.
- State quantile threshold audit table.
- Regression tables with unadjusted p-values and FDR q-values.
- State-conditioned executable strategy and cost tables.
- Null/control report for CL and 6E.
- Final extension report, clearly separated from the frozen baseline.

## Pending Confirmation Checklist

- Confirm the three states: `HV20`, `RelVol20`, `PathEff`.
- Confirm 20-day lookback for volatility and relative volume.
- Confirm 252 prior valid observations before assigning expanding quantiles.
- Confirm low/mid/high cutoffs at 33.333% and 66.667%.
- Confirm Benjamini-Hochberg FDR by hypothesis family.
- Confirm CL and 6E remain controls, not attenuation contracts.
- Confirm no BBO data purchase before fixed tick-cost extension results are
  reviewed.
