# FX multi-strategy code: BUILT; economic validation pending

Summary: Built the requested offline Python implementation from the uploaded FX paper and review.
Twelve causal signal sleeves feed equal-weight or maximum-diversification reference positions across eight FX futures.
Twenty-six synthetic correctness tests pass; both CLI modes run on an explicitly synthetic packet.
This is a documented interpretation, not exact source replication or a tested profitable strategy.
No real-data returns, account/portfolio comparison, MultiCharts deployment or live change occurred.

Specification: `agents/codex/plans/fx_multistrategy_build.md`, initially committed `836a492` (316-session warmup clarification added during implementation).
Engine: `analysis/codex_fx_multistrategy_engine.py`.
Checks: `analysis/codex_fx_multistrategy_engine_test.py`.
Usage/schema/assumptions: `agents/codex/research/fx_multistrategy/README.md`.
Outputs: `analysis/outputs/codex_fx_multistrategy_build/`.
Economic definitions evaluated: zero. Independent verification: pending.

## What the code does

Validates an explicit synchronized session calendar and a complete eight-currency as-of panel, constructs
yield-gap/momentum/reversal/volatility/equity/commodity features, applies prior-only percentile ranks,
estimates a shrunk risk covariance and solves signed risk-budget sleeves. It combines their **current exposures**
using equal weights or maximum diversification, scales risk subject to a gross cap, and translates net currency
weights into whole native reference contracts with visible margin and rounding checks.

The maximum-diversification solver uses an equivalent convex minimum-correlation formulation, avoiding a
direct ratio optimizer's numerical failure on redundant opposing sleeves. Inputs and code are hashed.
Contract IDs, receipt clocks, reference margins and next-action/delivery deadlines remain visible in the plan.
Invalid inputs or risk/margin constraints stop formation; no subset portfolio is silently substituted.

## What differs from the paper

The user's code request authorizes explicit interpretations of the unresolved source rules. These are detailed
in the README, not claimed to be author defaults: 63/252-session windows; signed yield differences to handle
negative yields; explicit reversal/volatility directions; one common commodity index; fixed shrinkage and leverage;
no hindsight pruning; and static-exposure covariance for sleeve combination rather than a historical return ledger
for changing sleeves. All eight markets stay mandatory. The inverse-correlation winner and ambiguous rolling-Sharpe
optimizer were not silently guessed. Equal weighting provides the simple baseline.

The output is a monthly reference-position plan, not assumed fills, a trade list, NAV or an order router.
It does not execute rolls or model native costs, collateral interest, variation margin or realized USD risk.
Maximum modeled volatility and initial margin are estimates; they do not guarantee future account safety.
No daily-flat conversion is made; it remains personal-account research, not an Apex strategy.

## Validation

`synthetic_checks.txt` records 26 passing tests covering future/unavailable information, warmup/rank ties,
negative yields, feature arithmetic, covariance positivity, signed risk contributions, diversification versus equal
at identical current sleeves, zero signals, missing/duplicate calendars/currencies, contract splices and incoming
contract returns, invalid prices, shared macro consistency, reference clocks, delivery deadlines, margin, native
integer rounding and cash outcomes. The demo's contract specifications and market series are invented.
Both CLI modes successfully produce saved synthetic plan JSON; the example packet can be generated with
`--demo --write-example /tmp/fx_input_example.json`. No reported synthetic allocation is an actual recommendation.

## Next evidence gate

The [source review](fx_multistrategy_3322717.md) and [evidence sheet](../evidence/fx_multistrategy_3322717.md)
remain NEEDS DATA for exact source replication. Only 6E is owned; no complete eight-country yield/equity/futures
panel or verified roll/cash ledger has appeared. Next is a source/clock/unit audit and reconciliation of one real
formation/roll month, then a separately committed return-test plan if the evidence and power gates pass.
This code-building checkpoint does not create a successful backtest or promote the candidate.

For Claude: `agents/codex/results/fx_multistrategy_build.md`.
