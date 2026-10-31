# FX carry/trend portfolio — runnable offline Python planner

Requested implementation based on the [SSRN 3322717 review](../../results/fx_multistrategy_3322717.md).
This is our declared interpretation of incomplete source rules. It calculates monthly reference positions,
not historical profitability or live orders. It is for multi-day personal-account research; no Apex conversion.

## Run

From the repo root, with Python, numpy, pandas and scipy installed:

```bash
python3 analysis/codex_fx_multistrategy_engine_test.py
python3 analysis/codex_fx_multistrategy_engine.py --demo --output /tmp/fx_plan.json \
  --write-example /tmp/fx_input_example.json
python3 analysis/codex_fx_multistrategy_engine.py --packet /tmp/fx_input_example.json \
  --method equal --output /tmp/fx_equal_plan.json
```

`--demo` uses deterministic invented observations, identifiers, multipliers, margins and calendars.
It is a mechanics example, never a market-data result. Replace that JSON with an independently audited real
packet before using `--packet`. The input `synthetic` field is an assertion by the caller, not certification.
Import `build_plan(packet, method="max_diversification")` for offline integration.
Validation/optimizer failures raise an error before a new plan is written. A pre-existing output file remains
unchanged on failure; consumers must check successful exit and the output decision timestamp/hash.

## Implemented definitions and explicit assumptions

- Fixed eight-currency universe: 6A/6B/6C/6E/6J/6M/6N/6S. No return-selected pruning or ticker substitution.
- Twelve signal sleeves: domestic-minus-US 1Y and 10Y yield gaps; FX momentum, reversal, negative realized
  volatility, linked equity momentum and common commodity-index momentum at 63/252 sessions.
- Yield gaps use percentage-point differences, rather than undefined logarithms at negative yields.
  Reversal is negative log(index / moving average). High realized volatility gets a negative raw score.
  Equity/commodity momentum is positive-following. These signs, trading-day approximations and a single
  declared commodity index are our choices, not verified author settings.
- FX momentum/reversal uses a chained index from same-contract current/previous closes. A roll transition
  must supply the incoming contract's previous-session close. It never counts an outgoing/incoming price splice
  as a return. This does not reconstruct executable rolls or a futures total-return/NAV series.
- Each currency/signal score is the percentile of today's feature among strictly earlier finite features,
  with midpoint treatment of ties, minus 0.5. Need at least 63 earlier valid values and 316 complete sessions
  overall. Historical warm-up and dates are explicit; no missing observation is forward-filled.
- Annualized risk covariance uses the trailing 252-session correlation and the average of 21/63/252-session
  standard deviations. Fixed 5% diagonal shrinkage stabilizes covariance. Per-sleeve risk budgets are proportional
  to absolute signal scores; weights retain their signs. A convex log-barrier risk-budget problem is solved,
  checked for contribution residuals, then scaled toward 10% annualized volatility with a 3x gross cap.
- Combination modes: equal nonzero-sleeve weights (baseline), or maximum diversification using a convex
  minimum-correlation formulation with long-only sleeve weights. A tiny fixed diagonal regularizer stabilizes
  redundant sleeves. **Combination covariance is current sleeve exposures projected onto as-of asset covariance.**
  It is not the paper's historical covariance of changing sleeve returns. No return backtest is hidden in this step.
- Net final currency weights are again risk-scaled toward 10%, capped at 3x gross. Targets are translated to
  native reference contracts with `trunc(weight * NAV / (price * multiplier))`. Rounding residuals are visible.
  If rounding removes offsets and estimated portfolio risk exceeds the target, formation stops. Rounded-to-zero
  portfolios explicitly report cash. Initial margin at reference prices must fit the caller's cash margin budget.
- No USD-neutrality constraint, optimizer fit on realized returns, learned method selection, rolling-Sharpe
  optimizer or inverse-correlation “winning method” is invented. No expected return is estimated.

## Input schema

The `--write-example` file is a complete generated schema example. Required top-level fields:

| Field | Meaning |
|---|---|
| `decision_at` | Offset-aware as-of timestamp; must follow the last complete session |
| `rebalance_month` | YYYY-MM containing decision; data ends in the preceding month |
| `next_action_at` | Explicit future review/roll/exit checkpoint in next month |
| `nav_usd`, `margin_budget_usd` | Positive USD reference NAV and permitted initial-margin budget (budget <= NAV) |
| `sessions`, `warmup_session` | Complete, ordered shared calendar; prior session before its first date |
| `calendar_provenance`, `data_provenance`, `commodity_index_id` | Nonempty actual source identifiers |
| `calendar_available_at`, `universe_available_at` | Offset-aware timestamps no later than decision |
| `observations` | Exactly one row per declared session and each of the eight currencies |
| `reference_contracts` | Native reference contract metadata for exactly those eight currencies |

Each observation has `session`, `symbol`, `contract_id`, `previous_close_contract_id`, `previous_session`,
positive `close`, `previous_close`, `equity_index`, `commodity_index`, and finite `yield_1y`, `yield_10y`,
`usd_yield_1y`, `usd_yield_10y` (all yields in percentage points, including negative values).
US yields and the common commodity index must agree across currencies on each session.
Same-contract previous closes must match the preceding row's close; at a roll, previous close must be for
the incoming contract. `event_at` and `available_at` must be offset-aware, event <= available <= decision.
The declared snapshot event is on its UTC session date. `available_at` must be the latest receipt/publication
time across **all inputs in that row**, including linked markets and yields. That conservative joined snapshot
must be assembled upstream from per-field source clocks. The code checks declarations, not provider truth.

Each reference contract has `contract_id`, positive `price`, `multiplier` (USD per price unit) and
`initial_margin_usd`, `quote_currency` = USD; `price_event_at`, `price_available_at`, `spec_available_at`,
`calendar_available_at`; `spec_provenance`, `calendar_provenance`; `earliest_fill_at` and
`delivery_or_expiry_at`. Latest declared snapshot <= reference quote event <= receipt <= decision.
Decision < earliest possible fill < next action < delivery/expiry. It can be a different identified contract
from the history's latest contract, but source/roll identity and quote-unit consistency must be verified upstream.
No supplied reference is an assumed execution fill.

Complete global calendar means an explicitly audited synchronized intersection with enough history for every
source. Local-market holidays, release lags and value dates need deliberate upstream alignment; the planner
does not verify an asserted calendar or synthesize a missing country. It rejects stale latest observations
more than seven calendar days before decision, naive clocks, missing/extra/duplicate rows and invalid numbers.

## Output and remaining work

JSON contains raw-ranked signals, sleeve allocations/exposures, covariance, ideal and rounded weights, integer
reference quantities, margin, estimated risk/gross exposure, fill/action deadlines, input/code hashes and versions.
Maximum modeled volatility and margin compliance are **as-of model estimates**, not loss or buying-power guarantees.
The earliest-fill declaration does not establish venue opening, spread or feasible execution.

This planner does not maintain positions, route orders, execute rolls, enforce variation margin, charge native
commissions/spread/slippage, compute collateral return, P&L/NAV/Sharpe or compare with our personal book.
No native micro fee/fill assumption or installed MultiCharts parity is claimed. MultiCharts code waits for
source/data reconciliation and validation under the project gates.

Next: audit real source clocks and native contract units, reconcile one formation/roll month including fills,
fees and cash, then finish data/power/evidence gates and commit a bounded return preregistration. Until then,
the original replication remains NEEDS DATA; synthetic checks do not create alpha evidence or a trading grade.
