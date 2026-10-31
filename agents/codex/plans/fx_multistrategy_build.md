# FX multi-strategy: requested code-building checkpoint

User: “build the code based off ur findings.” This authorizes a declared research interpretation of SSRN 3322717,
not an exact reproduction, a return trial or live use. Source/evidence review remains NEEDS DATA.

Build an offline Python monthly reference-position planner with eight fixed source currencies and twelve causal
signal families: 1Y/10Y domestic-minus-US yield gaps; 63/252-session FX momentum; negative deviation from 63/252
price-index moving averages; negative 63/252-session realized volatility; 63/252-session linked-equity and common
commodity-index momentum. Yield gaps use percentage-point differences, permitting negative yields. Trading-day
windows, volatility direction and common commodity-index choice are our explicit assumptions.

Expanding prior-only percentile ranks (midrank ties), at least 63 earlier valid values per signal/currency.
This requires at least 316 complete sessions for the 252-session momentum's 63 earlier ranks.
Covariance: trailing 252-session correlation times mean 21/63/252-session standard deviations, annualized;
fixed 5% diagonal shrinkage for numerical stability. Signed risk-budget sleeves target 10% annualized risk,
subject to gross-notional 3x. No performance-based pruning or inference of absent source settings.

Two fixed combination modes: equal sleeve weights, or long-only maximum diversification. For this no-return
planner, combination covariance is current sleeve weights projected onto the same as-of asset covariance,
NOT a historical dynamic-strategy return backtest. This difference must be explicit. Final rescaling targets
10% risk before the same gross cap. Integer contracts truncate reference weights toward zero; disclose residual
risk/exposure and reference margin. No dollar-neutrality, buying-power or native execution guarantee.

Require complete explicit session calendar and eight-asset panel, point-in-time event/availability clocks,
same-contract current/previous closes for returns, source provenance, native reference contracts/multipliers,
future action deadlines before delivery/expiry, and explicit margin budget. Fail incomplete/misaligned inputs.
Never infer a missing currency from 6E or price jumps across contracts. No daily flatten or NQ proxy.

Deliver CLI/API, generated synthetic example, schema/assumptions README, and meaningful checks for time leakage,
missing currencies/dates, negative yields, signed risk budgets, covariance/optimizer constraints, contract transitions,
rounding/margin, calendar/roll clocks and deterministic output. Synthetic outputs are mechanics only: no Sharpe,
P&L or strategy-account performance. No economic variant tried; no historical test or portfolio change.
