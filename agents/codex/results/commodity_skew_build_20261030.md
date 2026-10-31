# Monthly commodity skewness: offline code built; synthetic checks pass

Summary: Built the 22-commodity monthly skewness ranking and four-long/four-short target planner.
It checks point-in-time history, same-contract returns, native sizing/costs and future delivery-safe actions.
Twenty-nine constructed regression tests and the complete generated-example CLI pass.
No historical return or portfolio result is claimed; the complete dated commodity panel remains missing.
Use this as an offline research implementation pending data admission, source reconciliation and independent review.

Build scope: `agents/codex/plans/commodity_skew_build_20261030.md`, committed before checks; its unchanged content hash is retained in the manifest.
Source: [full review](ssrn_3507947_review_20261030.md), SSRN 3507947. Economic trials: 0.

## Deliverables

- [Planner and CLI](../../../analysis/codex_commodity_skew.py).
- [Schema, usage and explicit source differences](../research/commodity_skew/README.md).
- [Deterministic synthetic input generator](../research/commodity_skew/synthetic_example.py).
- [Regression tests](../test_commodity_skew.py).
- [Executed engineering checks](../../../analysis/outputs/codex_commodity_skew_build/engineering_checks.txt),
  [synthetic targets](../../../analysis/outputs/codex_commodity_skew_build/synthetic_plan.json),
  [run manifest](../../../analysis/outputs/codex_commodity_skew_build/manifest.json).

The output supplies scores for all 22 commodities, eight signed whole-contract targets, reference weights,
rounding shortfalls, prices/multipliers/FX, explicit cost components, action deadlines and input/code/helper hashes.
The generator's artificial weekday calendar includes real holidays; neither its contracts nor dates are live inputs.

## Implementation choices

The paper provides the one-year monthly skewness sort, four assets per tail and equal weights. Its estimator,
series/roll construction, precise formation clock and leverage interpretation are insufficiently specified.
This build explicitly uses adjusted Fisher-Pearson sample skew, simple same-contract price returns, the complete
prior 12 calendar months, and 12.5% NAV per leg (50% long plus 50% short, 100% ideal gross).
At least 200 declared observations and 15 per month are local completeness checks; near-equal cutoff scores
stop formation. These are stated research choices, not independently established author replication.

Sizing floors native quantity to each reference notional budget. Unaffordable selected legs stop the plan;
the code does not drop them, substitute micros or redistribute their weight. Actual fills can change exposure.
Fees are in account USD and slippage in native ticks converted using multiplier/FX; output separates them.
Round-trip estimates assume entry from flat and an unchanged-contract exit. They exclude actual rebalance/roll
turnover, management fees, financing, margin and interest. No portfolio P&L/NAV or performance is computed.

History must contain current and previous settlements of the same dated contract, including incoming-contract
prior prices on roll days. Receipt clocks and preceding observed values must align. The code rejects expired
contracts, missing/duplicate observations, nonpositive prices, undefined skew and late information. Nonpositive
CL episodes therefore remain unresolved, not excluded opportunistically. Authenticity of provider calendars,
contract identity, original vintages and underlying units still requires independent input review.

Entry follows the declared decision in the holding month. The next roll/exit must occur within that month and
before the supplied earliest delivery/notice/last-trade/broker deadline. This emits an action requirement;
it does not execute a roll, infer a venue calendar, manage a held book, enforce margin or guarantee maximum loss.

## Validation and next step

Tests cover analytically known sample skew, rank direction/cutoff ambiguity, scale invariance, full-universe and
12-month requirements, missing nonselected data, duplicates, contract splices, prior-session/receipt alignment,
expired/shared identities, future/naive clocks, decision month, selected quotes/specs/FX, integer budgets,
native-dollar/FX cost reconciliation, delivery/action timing, invalid costs, duplicate JSON keys and invalid CLI
output preservation. The synthetic CLI completed; its target/reference exposures are invented mechanics outputs,
not evidence of a profitable strategy. Run manifest binds source files and generated inputs to those checks.

Historical validation, Monte Carlo, independent strategy verification and personal BASE/ADD/REPLACE/EMPTY remain
unrun. All four Apex evaluation/funded homes remain ineligible for the source's monthly holding period as written.
Before any return study: obtain the identified 22-market panel and original return conventions, reconcile one
formation/roll month with a native-contract ledger, then commit an admitted bounded return preregistration.

For Claude: `agents/codex/results/commodity_skew_build_20261030.md` and the linked planner/schema/tests.
