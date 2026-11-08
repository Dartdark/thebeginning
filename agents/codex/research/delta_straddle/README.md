# Delta-straddle offline research code — SSRN4677166

This is one **interpreted signal/whole-lot target planner**, built at the user's request. It is not a complete
personal-account backtester, MultiCharts strategy or broker connector. It never confirms a fill, mutates holdings,
calculates investment returns, fetches prices or sends orders. Profitability and personal placement remain unverified.
[Frozen build protocol](../../plans/delta_straddle_4677166_build.md) ·
[Build/test report](../../results/delta_straddle_4677166_build.md).

## Reproduce

From repository root, Python 3.10+; standard library only:

```bash
python3 analysis/codex_delta_straddle_build_check.py
python3 -m unittest discover -s agents/codex -p test_delta_straddle_strategy.py -v
python3 analysis/codex_delta_straddle_strategy.py --demo
python3 analysis/codex_delta_straddle_strategy.py --admission
python3 analysis/codex_delta_straddle_strategy.py --write-demo /tmp/delta_straddle_synthetic.json
python3 analysis/codex_delta_straddle_strategy.py --packet /tmp/delta_straddle_synthetic.json --output /tmp/delta_straddle_proposals.json
```

The generated demo is explicitly synthetic: 520 invented weekday observations across all 41 identifiers,
invented $100,000 NAV, $1,000 return-notional per lot, $50 margin per lot and $1.25 one-way estimated total cost.
It is a parser/engineering example, not an economically plausible common contract specification. It supplies no
evidence about actual capital, margins, trading costs, historical performance or diversification.

## Packet fields and clocks

The generated JSON is the complete schema example. Unknown missing mandatory fields raise an error; there is no
drop/forward-fill/subset mode. Caller must authenticate provenance separately; a string does not prove correctness.

| Fields | Meaning |
|---|---|
| `kind` | `synthetic` or `historical_review`; the latter still does not admit returns or personal trading |
| `decision_at`, `latency_seconds` | Offset-aware decision, positive latency; output is only earliest eligible fill, no fill price |
| `sessions`, `last_complete_session`, `next_session` | At least 504 unique ordered, complete aligned session dates; supplied real calendar, not inferred holidays |
| `calendar_provenance`, `calendar_available_at`, `history_provenance` | Source/methodology/available-at evidence references |
| `observations` | One row per session: `session`, `event_at`, `available_at`, `returns` dictionary with all exact 41 symbols |
| `nav_usd`, `gross_limit_multiple`, `margin_budget_usd` | Current reconciled NAV and independent target gross/margin budgets; margin budget cannot exceed NAV |
| `portfolio_multiplier` | `value` in (0,10], `sample_end_at`, `available_at`, `provenance`; external past-only risk calibration, not fitted by this code |
| `max_snapshot_age_seconds` | Explicit freshness limit for current holdings, contract/margin/cost mapping and multiplier availability |
| `held_asof_at`, `held_available_at`, `held_provenance` | Reconciled confirmed position snapshot, no pending proposals counted as held |
| `held[symbol]` | Explicit integer signed `lots` and dated `contract_id` for every market, including flat markets |
| `markets[symbol]` | New/current contract mapping below; optional `old_contract` with identical fields, required to roll nonzero actual old lots |

Each native mapping requires `contract_id`, `asof_at`, `available_at`, `expiry_at`, `provenance`,
`reference_price`, `usd_return_notional`, `margin_per_lot`, `fee_per_lot_usd`,
`spread_slippage_per_lot_usd`. Prices, return notionals and margins must be positive. Fees and slippage are
nonnegative per lot **per execution**, already converted into USD using a causally available audited convention.
`usd_return_notional` means the USD P&L sensitivity per unit simple return, including contract multiplier and FX;
it is not source liquidity weight, margin, tick value or one-percent-move dollar value. For a straightforward
linear future it is price * multiplier * USD conversion. Historical nonpositive prices and unusual payoff mappings
need a different separately specified risk denominator; this implementation rejects them.

Return construction is external: self-financing index returns, native dated contract returns, FX total-return,
carry/roll/collateral and simple/log conversion must first be reconciled. An index is not its executable future.
Every aligned observation is explicitly supplied; closed-market zeros require authenticated calendars/conventions.
The common row `event_at` is the conservative completion time for that whole row and `available_at` is its latest
input availability. They must be ordered, match the UTC session and precede decision. Market sessions crossing
UTC boundaries require an authenticated common-session mapping before they can use this simplified schema.
Snapshot clocks and expiry checks do not prove a market is open at the earliest eligible time. No simultaneous
global same-close fill assumption is made; executable fills require a separate market-calendar/quote ledger.

## Rule and deliberate source differences

The engine uses source horizons/weights and smooth t-stat sign. Horizon volatility is sample SD of simple returns;
EWMA position volatility initializes from the first squared return and uses .94 decay, annualized by sqrt(252).
This is an explicit source interpretation. No printed disputed AR(1) correction is used. The caller supplies the
portfolio-risk multiplier because the original expanding-window initialization and actual native portfolio series
are unresolved. Source table rounding is preserved without renormalization or a second 25% class multiplier.

Dollar target = NAV * .10 * portfolio multiplier * source weight * signal / annual vol. Convert to whole lots
toward zero. Compare unrounded desired dollars against **actual held** dollars with a .25 * NAV * .10 *
multiplier * weight / vol no-trade band. At equality rebalance; small sign crossings remain held if inside the band.
A roll bypasses the band, closes old actual lots and proposes new target lots, with costs on both legs. A partial
fill must arrive in the next confirmed snapshot; it is never inferred from yesterday's target.

After the band, scale all desired holdings down together if gross or margin budgets are breached; round toward
zero and check budgets again. This may force trades through the band. Outputs expose scale and tracking error.
These budgets apply to the **final modeled positions**, not temporary exposure/margin during legged execution,
open-order risk, broker offsets, cash settlement, overnight margin hikes or gap loss. Estimated execution costs
are reported separately and are not deducted from NAV or available cash; no account ledger is implemented.
Actual personal affordability requires costs/cash/carry/FX and a fill-path margin check before any admission.

The source is daily/multiday and does not specify a stop loss. No stop, Apex close-out, intraday reinterpretation,
NQ subset, ETF substitution, ED4-to-SOFR splice or Bloomberg FX-index-to-spot mapping is added.
The whole source program is not reproduced by this code; building the remaining native replay/cash adapter
requires the inputs in [D54](../../DATA_NEEDED.md#d54--diversified-delta-straddle-trend-ssrn4677166-november82026).
