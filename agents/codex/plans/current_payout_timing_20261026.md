# Current portfolio first-payout timing — frozen measurement plan

Summary: Answer the user's first-payout question using the adopted current 50K/150K stacks.
This measures existing allocations; no strategy selection, optimization, promotion or live change.
Commit this plan before loading account paths or computing new timing results.

## Sources and fixed allocations

Authoritative Claude revision: `7f0800ffc04d56bd878750369a4abc2316ee01d8`.
Archive: `agents/codex/inputs/current_payout_timing_20261026/`.
Use the selected rows in `analysis/swing_target_bench.py`, consistent with FUNDED_PLAN.md:
- 50K: VB_N 1 / VB_F 1; ONB ML risk $400; EOS risk $700; LDF 2 MNQ;
  NFP risk $500; Bridge Monday 1 MNQ; CLS 2 MCL; MOC 2 MES; RS longs 1 MNQ;
  OT/VIX 1 MNQ; Swing Target 1 MNQ; Monday Long removed.
- 150K: legacy base x1.5 (VB_N 3 / VB_F 1.5 before integer rounding;
  ONB $600, Monday Long 1.5, EOS $1,050, LDF 3, NFP $750,
  Bridge 1.5, CLS 3, MOC 3), RS both sides 1, OT 2, ST 2; Dual Thrust removed.
- Quantity is floor(base x f + 1e-9), f clamped to [0.5,1]. Full size from
  cushion $1,500 (50K) / $3,000 (150K). Preserve the canonical rounding convention.
- Evaluation stays VB 8 / ONB ADX30 $1,100 / Bridge 2 / EOS $500 on 50K;
  VB 20 / ONB $2,750 / Bridge 5 / EOS $1,250 on 150K. Scale dollar risk
  before flooring, never multiply already-rounded 50K quantities by 2.5.

## Data, clock, costs and unchanged account policy

Reuse existing g24/ge/lab/CL/single-print caches; do not rebuild market grids.
Reconstruct additions with archived canonical loaders and source ledgers.
Primary common coverage: 2018-01-01 through 2026-07-07, inclusive, because
the reviewed OT order-flow ledger ends there. Never treat later missing OT
signals as known zero P&L. The known date cutoff is a coverage choice made
before results, not a performance filter. Record actual input coverage.
ST uses the canonical three holiday exits; retain canonical extra slippage.
Preserve disclosed CL/OT daily-adverse and MOC close-path approximations.
This is historical planning evidence, not unseen strategy validation.

Primary cost: $1.04 per micro round trip, with existing one-tick market/stop
slippage unchanged. Sensitivity: $1.24. Also run inherited legacy fees only
as a benchmark-method diagnostic, not a selectable strategy configuration.
Full-cap payout requests at the qualifying close, as in the existing bench:
first cap $1,500 / $2,500; safety net $52,100 / $154,100; five $250 / $350+
days; best day <50% of cycle profit; existing daily loss and EOD trailing rules.
Cash settlement/approval and evaluation activation delays are not modeled.

## Estimands and fixed simulation

1. Fresh funded account: first full-cap payout eligibility. Simulate at most
   500 trading days, ending on blow-up or six payouts. Report unconditional
   probability of a payout by days 21/42/63/84/105/126/252/500, no-payout
   share and blow-up share. Report unconditional median/10th/90th event
   quantiles, assigning no payout +infinity; label recipient-only quantiles
   separately. Never hide failures by conditioning the headline on survival.
2. Fresh evaluation slot: same market history through evaluation attempts,
   then the current funded stack, until its first payout or day 500. Failed/
   expired evaluations restart next session. A funded account that blows
   before paying returns to evaluation next session. Do not add separate
   medians or sample the two phases independently. Not conditioned on the
   user's existing account balances, already elapsed days or current cushion.

Use circular 20-session blocks of whole market days, preserving every
strategy and both phases together. Exactly 1,000 histories: seeds 1,2,3,4,
250 histories each, horizon 500. Same histories across accounts/costs.
Use existing funded_bootstrap history construction and quantity-state
accelerator. Extend only the account lookup to parameterize 50K/150K
rules and return timing; demonstrate parity against the existing direct
simulators on fixed histories before using accelerated results. Evaluation
uses the existing engines; disclose their same-minute priority assumptions.
Report trading days and months (21 sessions/month), not promised bank dates.

## Decision rule and trials

No adopt/reject gate: descriptive calculation requested by the user.
No entry, exit, sizing, risk or payout policy may be tuned to accelerate dates.
If source/coverage/parity fails, resolve implementation or report a blocker;
do not substitute independent phase medians or a daily-P&L-only proxy.
New strategy variants: 0. Fixed account allocations: 2; costs are diagnostics.
Record preregistration/code/source hashes, cache/input hashes, versions,
seeds, coverage, exclusions and outputs in the run manifest.

Outputs: `analysis/codex_current_payout_timing.py`,
`analysis/outputs/codex_current_payout_timing_20261026/`,
`agents/codex/results/current_payout_timing_20261026.md`.
No live files, account settings, broker/VPS/API-key access or trading changes.
