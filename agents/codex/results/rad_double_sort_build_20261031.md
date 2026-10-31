# Rad double-sort: offline signal and integer-planning code built

Summary: Built the monthly commodity momentum/carry ranking and four-long/four-short research planner.
Draft whole-contract allocation respects the supplied reference notional budget and rejects unaffordable legs.
Twenty-three constructed mechanics checks pass; the synthetic CLI example also completes.
Paired data, source clocks, contract/cash accounting and executable costs remain prerequisites for return work.
No historical return test, account comparison, MultiCharts code or trading allocation is claimed.

Request: build code based on the reviewed findings. Latest fetched remote parent 70f 708a; only codex/work changed.
Source findings and four paper questions remain in the [full review](rad_double_sort_review_20261031.md).
This report is a build/checkpoint, not a new paper review or economic result.

## Deliverables and executed checks

- [Planner and CLI](../../../analysis/codex_rad_double_sort.py).
- [Synthetic engineering checks](../../../analysis/codex_rad_double_sort_test.py).
- [Input schema, usage and explicit implementation choices](../research/rad_double_sort/README.md).
- [Complete synthetic input packet](../research/rad_double_sort/synthetic_packet.json).
- [Executed check log](../../../analysis/outputs/codex_rad_double_sort_build_20261031/engineering_checks.txt).
- [Synthetic plan with input/code hashes](../../../analysis/outputs/codex_rad_double_sort_build_20261031/synthetic_plan.json).

Configured Python ran 23 unittest cases and the CLI. Cases cover exact winner/loser membership, carry changing
selection inside momentum tails, signed whole-contract quantities,2x reference gross budget/rounding, missing
nonselected assets, duplicate rows, same-contract prior closes, invalid/zero prices, late/impossible/naive clocks,
unmatched maturity measurements, bad maturity order, warm-up/session gaps, late universe/FX, delivery deadlines,
late formation/next action and ambiguous overlapping momentum ties. Inputs are invented; these checks establish
program behavior, not profitability or full source parity. No actual market-return data were loaded.

## Source fidelity and boundaries

The central one-month mean-log momentum/carry double sort follows the paper's eight-per-tail then four-per-side
selection. Decimal arithmetic and deterministic tie handling are engineering choices. Source 37 total commodities
versus initially 22/peak 35 are not replaced by two outright markets. A supplied complete eligible universe of at
least 22 is required, but the code cannot certify that a caller's universe/calendar declarations match reality.

Draft integer floor sizing, same-contract roll-boundary momentum and first-of-month UTC decision timing are
explicit clarifications/adaptations awaiting real-data preregistration; do not report this as exact reproduction.
Reference quotes are not fills. Entry contract and next roll/exit schedule must be independently supplied and
verified. The program emits those action deadlines, without executing a roll or constructing a held-book ledger.
No fees, margins, account buying power or source short-weight drift are guessed. The unresolved stop overlays
and missing-return redistribution are not implemented. No log-return sum is represented as NAV.

## Test/account status and continuation

Economic return definitions/reservations 0; no scout lease/progress/trial history changed. The existing evidence
remains NEEDS DATA/ACCOUNTING. BASE/ADD/REPLACE/EMPTY for the 19-piece personal portfolio is unrun. All four
evaluation/funded homes remain incompatible with the source's monthly overnight holds. No gross/design gate,
2023+ validation, independent review, account payout simulation or MultiCharts compile/trade match occurred.

Exact next step when genuinely new matching data arrive: adapt identified front/second prices to the documented
packet, reconcile one formation/roll month and a self-financing ledger, perform coverage/clock/cost/power admission,
then freeze budget/code/preregistration before outcomes. Existing tools remain the later metrics/account engines.
No unchanged data-acquisition loop, broker installation or live change is needed for this code checkpoint.

For Claude: `agents/codex/results/rad_double_sort_build_20261031.md` and its linked code/schema/checks.
