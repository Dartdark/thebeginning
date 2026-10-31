# PrimeSync account placement — frozen exploratory bench
Summary: User requests placement in every plan and MultiCharts code.
Previous rule/exit remain frozen; recent history is already seen.
Commit before account/portfolio returns. This is conditional Python research, not MC verification.

## Sources and variants
Use PrimeSync exit0, all four contexts NQ15/NQ30/ES15/ES30, no entry or side tuning.
Current funded baseline: current_payout_timing_20261026 archived canonical stack.
Current personal baseline: Claude 6416de2dd39782eb4a43bd665c866409da4deb70, 19 pieces; verify referenced CSV blobs before reusing staged files.
Explicit user request authorizes exploratory account comparisons despite pending native MC parity; no promotion without parity/checker.
Four variants = four fixed contexts, not a new exit/threshold search.

## Sizing and configurations
One micro per eligible position, normalizing the existing frozen ledgers by original quantity.
Preserve the original signal/cooldown and three-micro/$500 eligibility screen: no new signals from smaller size.
This is a prespecified account sizing projection, distinct from the prior variable-quantity profit table.
No rescaled entry search. $1.04 RT, same slipped entry/stop/exit and limit assumptions.
For each context: base, add1micro, replace entire Vault Break slot with1micro, and empty VB slot.
VB is selected ex ante as the overlapping directional breakout family, not from recent performance.
No candidate sizing search; funded cushion rule floors1*f to0 below full cushion.
Personal compare the published19-piece base and same add/replace/empty controls at1micro; retain baseline costing/booking, label its limitations.

## Execution and bench
Reconstruct per-one-micro minute adverse/realized paths from each saved entry/fill.
Milestones start at1.5R and2.5R, full exit4.5R; no partials.
Use existing walk convention and ensure earlier stop improvements limit later adverse marks in the same minute.
Use min(native adverse, original then raised stop fill) with actual slipped stop fill; entry and exit fee halves.
Do not use minute ranges after an exit-at-open; time exits hold through close.
Reconcile terminal daily cash to sum of trade net/quantity.
Common coverage2018-01-02 through2026-07-07, so missing OT history is not zero filled.

Funded:1000 paired500-day20-day-block histories, seeds1-4 x250, fresh accounts; same current50K/150K rules and cushion refs1500/3000.
Reuse exact quantity-state tables and generic canonical lookup; check direct-simulator parity on fixed paths.
Evaluation: unchanged four-leg size/engines; fresh complete21-day starts, real-fee paths; all/recent cohorts.
Personal:19-piece same common dates;1000 paired252-day20-day blocks seed2710; annual profit,p95 DD,Sharpe,capital at20% rule and joint correlation.
All four configurations stay visible; context choice after these results is exploratory and does not create unseen evidence.

## Decision
Funded candidate only if1y payout gain>= $250, paired90% lower bound>0, no higher blowups and no slower sixth payout.
Evaluation candidate only if pass gain>=2 percentage points in all and recent starts, with paired90% lower bound>0 overall.
Personal candidate only if p95DD-adjusted return improves>=5%, paired annual-profit lower bound>0, without increasing the existing capital requirement.
Failure is no addition; no rescue by new sizes, rules, side or parameters.
Any positive finding remains provisional until MC parity, matched controls and independent review; no plan/live files changed.
Report all five plan destinations and code links in chat.
