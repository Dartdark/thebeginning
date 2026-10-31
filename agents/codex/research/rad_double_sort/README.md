# Rad monthly commodity double-sort — offline research planner

This implements the source's two-stage selection and a separate draft integer allocation. It is not a historical
backtester, an admitted strategy, a MultiCharts strategy or an order router. Existing NEEDS DATA/ACCOUNTING evidence
still applies. All example symbols, calendars, contract details and prices are synthetic.

## Run the supplied example

From the repository root:

```bash
/workspace/venvs/thebeginning/bin/python analysis/codex_rad_double_sort_test.py
/workspace/venvs/thebeginning/bin/python analysis/codex_rad_double_sort.py \
  agents/codex/research/rad_double_sort/synthetic_packet.json \
  --output /tmp/rad_synthetic_plan.json
```

The example produces four long and four short reference positions, scores for all 22 invented commodities,
information/future action clocks, reference notionals, ideal/rounded weights and input/code SHA 256 hashes.
It never downloads data, connects to an account or calculates backtest returns. Import `build_plan(packet)`
from `analysis/codex_rad_double_sort.py` for offline integration. Validation raises an exception; it does not
discard missing assets or write an apparently valid partial plan. The CLI writes only after validation succeeds.

## Implemented rule

1. Check the explicitly supplied prior-calendar-month universe, session lists and warm-up dates.
2. For every expected observation, calculate momentum `ln(front_close/previous_same_contract_close)` and carry
   `ln(front_close/second_close)`. Use 40-digit Decimal arithmetic and average each over its commodity's month.
   A front-chain change needs the incoming contract's previous close, not a splice price from the outgoing one.
3. Take eight highest-momentum winners and eight lowest-momentum losers. Within winners choose four highest
   carry for longs; within losers choose four lowest carry for shorts. Exact ties use symbol order. Overlapping
   momentum tails stop formation rather than create an ambiguous long/short instrument.
4. Each ideal leg has 25% NAV notional, giving 100% long and 100% short. Draft quantities are
   `floor(NAV/4 / (reference_price * multiplier * FX_to_account))`, signed by direction. This keeps reference
   gross exposure at or below 2x, with residual unallocated notional. Reject a zero-sized selected leg.
5. Require known reference/spec/FX clocks, a future earliest-fill time, a next roll/exit action within the holding
   month, and that action strictly before the supplied delivery/last-trade deadline. Emit a plan, not assumed fills.

## JSON schema

The runnable [packet](synthetic_packet.json) is the exact complete example; these keys are required:

| Section | Fields and meaning |
|---|---|
|Formation|`ranking_month` YYYY-MM; `formation_session` first calendar day of next month; `decision_at` offset-aware ISO timestamp; positive decimal-string `reference_nav`|
|Universe/calendar|`universe`: commodity -> ordered complete ranking-session ISO dates; `warmup_sessions`: commodity -> prior-month previous session; `universe_provenance`, `calendar_provenance`, their respective `*_available_at` timestamps|
|Observations|`symbol`, `session`, `previous_session`, distinct `front_id`/`second_id`, `front_expiry`/`second_expiry`, `previous_close_contract_id`, positive decimal-string `front_close`/`second_close`/`previous_close`|
|Observation clocks|`front_event_at`, `second_event_at` at the same declared measurement instant; each corresponding `*_available_at`; `previous_event_at`, `previous_available_at`. Prior event must match prior expected observation after warm-up. Decision follows every available_at.|
|Entry contracts|`entry_contracts`: selected commodity -> `contract_id`, `currency`, decimal-string `reference_price`, `multiplier`, `fx_to_account`; `reference_price_event_at`, `reference_price_available_at`, `fx_event_at`, `fx_available_at`, `spec_available_at`; `earliest_fill_at`, `next_roll_or_exit_at`, `delivery_or_last_trade_deadline`, `roll_calendar_provenance`|

All inputs must be point-in-time and consistent in quote units, currency and contract scale; supply original close
and settlement receipt clocks rather than today's revised data. The planner checks supplied declarations, not their
truth. The feed adapter must independently verify actual first/second maturity ordering, contract calendars,
official event/session mapping, price units, eligibility, availability and FX provenance. A header or asserted
provenance is not an admission PASS. Maturity/contract IDs cannot be reconstructed from our outright CSVs.

## Explicit draft choices and incomplete parts

- The minimum 22-commodity check guards against silently reducing the paper to CL/GC. It does not prove source
  universe parity. The caller supplies the entire frozen eligible universe; there is no return-selected exclusion.
- The draft decision date is the **first UTC calendar day** of the holding month, after all ranking data. This is
  an explicit engineering convention, not a clock established by the thesis. Earliest executable fill is separately
  supplied and may fall on the next session. Real source/venue clocks must be resolved before preregistration.
- Same-contract momentum avoids treating a roll-price gap as a daily gain. This is a declared clarification pending
  vendor/source reconciliation, not proof of exact Datastream series parity. Carry uses the unannualized ratio.
- Whole contracts replace fractional source weights. Quantities use reference prices, so actual fill notionals and
  margins may differ. This is no guarantee of exposure or buying-power compliance at execution.
- This module does not infer the entry/front contract, execute rolls, manage a month-long book, drift weights,
  calculate P&L/NAV, model commission/spread/slippage or enforce account margins. The supplied next action is a
  mandatory planning checkpoint; it is not an automatic roll implementation. No carried position beyond it is modeled.
- No stop overlays: the source's trigger/weight-reallocation/reopening ambiguities and selected thresholds need
  a separately frozen specification. Current protective orders are unchanged. Missing data always stop formation.
- No compounded NAV is computed from weighted instrument log returns. Any future ledger must use actual signed
  quantities, multipliers, FX, variation margin, fees, open marks and roll cashflows, then call existing metrics/tools.

## Next gate

This is the code-building checkpoint requested by the user. Synthetic checks consume no economic definition or
scout reservation. It is not a strategy preregistration. For actual outcomes: obtain identified paired data,
reconcile one formation/roll month and the cash/short-weight rules, finish coverage/clock/power/cost gates, then
commit the lease, bounded reservation, exact code and preregistration before any design returns. No historical
validation or personal portfolio comparison follows until earned. Monthly holds remain ineligible for Apex as-is.

See [source review](../../results/rad_double_sort_review_20261031.md),
[evidence](../../evidence/rad_double_sort_20261031.md),
[build report](../../results/rad_double_sort_build_20261031.md) and execution reference E38.
