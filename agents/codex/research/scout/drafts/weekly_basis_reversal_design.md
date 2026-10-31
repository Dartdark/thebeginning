# Weekly basis reversal — implementation draft, not an admitted preregistration

Status: NEEDS DATA. Author primary abstract plus secondary weekly implementation only; no real-data test authorized
by this draft. User requested actual strategy creation; the signal core now exists and has synthetic engineering checks.
Source/evidence: [feasibility](../../../results/scout_spread_strategy_feasibility_20261029.md),
[evidence sheet](../../../evidence/scout_basis_reversal_20261029.md).

## One proposed rule

For two explicitly selected, same-commodity maturity contracts, measure each contract's return over the same
completed weekly interval. If front outperforms deferred, target short front and long deferred next week; if front
underperforms, reverse; exactly equal relative growth means flat. Use prices of the same identified contract at both
measurement endpoints. Re-selecting a maturity requires its own historical endpoints, not a continuous-series splice.
Wait until all settlements are available before deciding. Do not infer the week/calendar from whichever rows survived.

The Python core outputs directions only. It accepts explicit decision/exit dates and an expiry buffer, rejecting
look-ahead, mismatched legs, unsupported nonpositive prices, first-notice risk and holding through last trade.
It loads no data, places no orders, selects no universe, sizes no portfolio and calculates no forward P&L.
This adapts the inspected secondary implementation; equivalence to the primary paper remains unverified.

## Unresolved settings — no economic outcomes may be used to fill these

- Primary source/version and exact sign, weekly selection, roll and execution conventions.
- Admitted universe with complete paired2018–22 contract histories and actual availability/roll/expiry evidence.
- Named-zone exchange calendar, first executable entry and next weekly liquidation event, including holidays.
- Integer equal-contract versus equal-dollar exposure, risk limits and stops/time exits.
- Both-leg commissions, native ticks/slippage, spread execution, margin/funding and stress assumptions.
- Power, matched placebos/baselines and exact variant reservation. No variants consumed by synthetic checks.

Research home: personal only for a weekly overnight implementation; evaluation/funded homes are ineligible as-is.
No current portfolio benefit inferred. After prerequisites resolve, update the evidence to TEST if justified, freeze
the exact code/settings/control/decision rules in the real preregistration and scout reservation, publish/recheck the
lease/head, run artifact admission and only then inspect cheap2018–22 design outcomes. A failed gate stops; only a
pass earns once-only previously seen2023+ historical validation and BASE/ADD/REPLACE/EMPTY personal comparisons.

## Required input handoff

A readable permitted primary paper; raw daily contract prices for at least two eligible maturities per commodity
through2018–22 and the later validation period, with actual contract IDs/expiry/FND, adjustment/roll metadata,
timestamps/timezones and settlement availability; executable entry/exit quotes or prices; native fee/margin facts.
Keep licensed raw inputs outside Git unless redistribution is expressly allowed. No passwords/API keys needed.

For one pilot sample, include both raw paths across a weekly observation interval and the following holding week,
with an expiry/roll transition if available. A pilot validates schema/clocks, not profitability or full-period power.
