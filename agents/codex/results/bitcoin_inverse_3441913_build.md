# Bitcoin inverse strategy code: BUILT FOR REVIEW, empirical validation pending

Summary: Implemented the paper's exponential/power allocation rules as a reusable offline Python strategy module.
It produces native-lot rebalance proposals with BTC collateral, reciprocal futures basis/P&L and a reconciled USD cost bridge.
All20 behavioral tests pass; a labeled synthetic input exercises the complete CLI and order-proposal path.
Quotes are hypothetical fill references and the wallet is a declared pooled research model; no real return test or execution was performed.
Ready for Claude's implementation review; original data/specification gates and current-plan ineligibility remain.

User request: “make the strategy code for claude review.” Scope: [committed build plan](../plans/bitcoin_inverse_3441913_build.md),
`8f5b191`. Implementation and tests: `5807eb9`. This explicit code request permits an offline build while source evidence
remains NEEDS DATA for a historical performance study. It does not waive the return preregistration or portfolio gates.

## Files for Claude

| File | Purpose |
|---|---|
| [Strategy module](../../../analysis/codex_bitcoin_inverse_3441913_strategy.py) | Coefficients, utility targets, typed inputs, native-lot orders, hypothetical funding/cost bridge and CLI |
| [Behavioral tests](../test_bitcoin_inverse_strategy.py) |20 synthetic arithmetic, state-transition and rejection tests |
| [README and input contract](../research/bitcoin_inverse/README.md) | Protocol, units, assumptions, omissions and reproduction commands |
| [Synthetic input](../research/bitcoin_inverse/synthetic_input.json) | Explicit fixed assumptions; fabricated contract, quotes and account |
| [Synthetic proposal](../../../analysis/outputs/codex_bitcoin_inverse_3441913_build/synthetic_proposal.json) | Full ordered proposal, expected account/cost bridge, input/script hashes |
| [Validation receipt](../../../analysis/outputs/codex_bitcoin_inverse_3441913_build/validation.json) | Observed test result, code/input hashes and exact commands |
| [Source review](bitcoin_inverse_3441913_review.md) | Source claims, formula typo, actual acquisition attempts and remaining return gates |

The main Eq4.3/Eq4.4 C2 minus sign is implemented; rendered AppendixB.2's contradictory plus sign is not.
Both utility forms are equation implementations, not selected profitable variants. The one example uses power alpha−0.5.
No economic trials or historical price/return files are read by this build. Standard-library code; no new packages.

## Rule and implementation differences from the paper

Caller supplies an explicit UTC decision time, completed calibration, matching dated inverse instrument, fresh spot/futures
bid/ask/marks and reconciled USD/BTC account snapshot. Compute the source targets, round futures toward zero to whole contracts,
and produce spot adjustments at the supplied lot size. No unobservable same-close/continuous fills are claimed.

The paper's continuous frictionless controls become **offline discrete rebalance proposals**. Their cadence is chosen by the
caller and must be separately frozen for a later study. Settings add explicit fees, lot rounding, an exposure bound,
condition-number guard, initial/maintenance checks and a conservative collateral reserve. Targets that require unsupported
borrowing/short spot are rejected rather than clipped into a different strategy. Source model covariance is not silently regularized.

The book includes USD cash, unpledged BTC, collateral BTC and marked inverse P&L. BTC collateral and unrealized P&L count toward
the model's non-futures BTC exposure. Partial closes, same-direction additions and reversals retain reciprocal-price accounting;
future fees are native BTC and spot fees USD. NAV decrease at fixed marks must equal fees plus signed execution-to-mark differences.

**Pooled wallet** is the explicit research assumption for the dry-run transfer/funding calculation. Separate venue transfers,
latency, custody fees, mark tiers and exchange liquidation are not established. Ordered actions have a strictly later eligibility
bound, but reference quotes do not guarantee actual fills or atomic execution. The hypothetical book retains input snapshot clocks;
it must not be relabeled as a confirmed newer state or reused without actual fill/transfer reconciliation.

No scheduler, broker connector, perpetual funding, roll, expiry settlement, margin-liquidation engine, cash interest or short-spot
borrow is implemented. No MultiCharts version was written: the requested review artifact is Python and this two-wallet inverse
contract is not the existing NQ/ES execution model.

## Verification completed

Command: `python3 -m unittest discover -s agents/codex -p test_bitcoin_inverse_strategy.py -v` — **20/20 PASS**.
Checks include independent covariance-equation residuals; source long/short BTC/USD example; reciprocal-weighted basis;
partial closes/reversals; realized+unrealized conservation; source-target lot rounding; both utilities; complete funding/fee
NAV bridge; account immutability; BTC collateral exposure; quote/calibration/book timing; expiry; identity/product checks;
maintenance, leverage, cash/short-spot and covariance rejection paths. One synthetic short-futures test fixture initially required
unsupported cash borrowing; its utility risk was corrected to test a cash-funded short scenario. No return data or variant selection.

The CLI was exercised after the implementation commit. In its fabricated$100,000 account, power targets are$35,039.09 total
non-futures BTC exposure and88,987 whole inverse contracts (K=$1, Z=40000/40400). Hypothetical fees$101.19 plus signed
execution-to-mark difference$15.29 reconcile to$116.48 NAV decrease. These numbers are bookkeeping examples, **not profits,
historical trades, recommended size or a verified margin requirement**.

Independent review is pending. Claude should inspect particularly:

1. Mapping of theta to total BTC exposure including collateral and marked inverse P&L, and main-source coefficient sign/units.
2. Reciprocal entry basis, partial realization and reversals; BTC fees versus USD cost bridge.
3. Sequenced collateral funding and the gap between a pooled research wallet and executable separate-venue transfers.
4. Quote/calibration availability, hypothetical pricing versus actual later fills, and rejection rather than silent target clipping.

## Placement status

| Home | Verdict |
|---|---|
| Personal | Conditional research only; no allocation earned, matching data/executable protocol and portfolio validation pending |
|50K evaluation | No eligible placement established; no intraday adaptation or account test |
|150K evaluation | No eligible placement established; no intraday adaptation or account test |
|50K funded | No eligible placement established; no intraday adaptation or account test |
|150K funded | No eligible placement established; no intraday adaptation or account test |

Original Sharpe claims remain source-only. No2018–22 strategy design test,2023+ validation, bootstrap/Monte Carlo,
BASE/ADD/REPLACE/EMPTY comparison, live/VPS/broker/policy or allocation change. This is the completed code-review build,
not a substitute for the later data-gated historical test.
