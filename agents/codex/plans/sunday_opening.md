# Sunday Opening — frozen source and execution screen

Summary: Test the uploaded Sunday after-down-week long without tuning its unusual clocks.
Design 2018–22 first; preserve observed-session SC[0] versus SC[5], 80-point stop, 50-point target and 19:12 threshold.
Primary is a next-open executable proxy at native MNQ costs; source close fills are diagnostic.
Failure stops the candidate before 2023+ and account simulations; report that limiting condition for every requested destination.
No live changes, source-code fixes or parameter rescue search.

Evidence: agents/codex/evidence/sunday_opening.md.
Input: agents/codex/inputs/sunday_opening/Sunday_Opening.txt, preserved byte-for-byte.
Script: analysis/codex_sunday_opening_screen.py. Output: analysis/outputs/codex_sunday_opening/.
This plan is committed before any candidate gross/net return or future excursion is computed.
User standing workflow requires 50K/150K evaluation/funded and personal placement, subject to this cheap-screen stop gate.

## Frozen semantics and coverage
Use existing g24.pkl calendar-date close-stamped NQ grid; configured Python environment.
Reconstruct source session boundaries from the actual ordered bar stream: SM=(minute-1020)%1440, NewSess only if SM decreases, then push last actual close into SC.
Require six observed completed sessions, compare SC[0]<=SC[5]. Do not substitute daily RTH prices or a calendar-Friday return.
At Sunday 17:17–17:22 close, enter at first existing eligible decision; only one attempt. Source threshold exit first existing close >=19:12.
Bracket starts strictly after a close entry; next-open entries have protection from that open. Stop gap fills at first available open.
Targets require 1.0 NQ point through. If both brackets cross in one minute, use stop first (conservative extension of grid._walk).
Missing minutes do not create fills. Mark gaps and outside-window/time exits. A missing terminal session is invalid/unresolved, never silently filled before the scheduled exit.
A roll inside the holding interval blocks promotion pending explicit roll accounting; do not infer a roll solely from a losing trade.
The pre-return inventory identified eight down-week design windows with missing minutes. Replay the observed stream without invented bars and flag actual holding gaps; report such fills as conditional estimates. Unresolved exposure gaps independently block promotion and account claims, even if numerical return gates pass. No stress-date exclusions or finite guaranteed loss bound are inferred from incomplete bars.

## Exactly five return configurations
V0: source close entry/exit, down weeks; legacy NQ $7.25 RT plus 1 tick market/stop slippage. Diagnostic only.
V1 PRIMARY: after the same decision, next existing minute-open entry; after time-exit decision, next existing open; down weeks. Native MNQ $1.04 RT plus 1 tick ($0.50) on entry and stop/time exit, target no exit slippage. Report dollar amounts per MNQ and NQ-equivalent.
V2: V1 with 2 ticks per market/stop fill (one extra tick), unchanged rules.
V3: V1 on all eligible Sundays (unfiltered control).
V4: V1 on strictly positive-week Sundays (removed/complement control). Zero-week belongs to V1.
Only V1 can proceed; no selection among configurations after viewing returns.
Source TBOC and next-open proxy are disclosed differences, not claims of platform confirmation.

## Design gate, fixed before returns
2018-01-01 through 2022-12-31, inclusive:
1. At least 80 primary trades, positive total net, per-trade t>=2 and PF>=1.20.
2. Both 2018–20 and 2021–22 primary total net positive.
3. V2 total net positive.
4. V4 removed-trade mean negative (filter requirement); filtered total net must exceed at least 95% of 1,000 matched random removals from V3.
5. Primary drawdown must beat at least 95% of those random removals. Use paired year-stratified retained counts so a regime-count change is not the placebo.
If any gate fails: REJECT this configuration; no 2023+ returns, Monte Carlo promotion claim or account bench. List failed gates and document stopped/not-run status for each destination.
Gross edge and costs are reported separately. No gross/net returns before this plan's Git commit.

## Metrics and conditional controls
Always report design whole/long; shorts N/A (source has no short signals), by-year, trade count/win/mean/t/PF, daily Sharpe/Sortino/Calmar/Ulcer/maxDD using analysis/metrics.py.
Daily record belongs to Monday's trading account day, despite Sunday calendar execution; reconcile daily totals to trades exactly.
Use all design trading days including zeros and compare same date range for variants.
1,000 random-removal draws are fixed controls, not 1,000 optimized strategies; preserve seed 261026.
Only if all design gates pass: open frozen 2023+ once (already seen in the research program; historical validation), report bootstrap intervals with repository tools, side/time controls and forward suitability.
Promotion requires current global trials bar and DSR>=0.95 plus the other builder requirements. Author's prior search count is unknown; our preregistration cannot erase it.

## Account placement after a pass only
Refresh current rosters at a pinned commit. Reuse reviewed adapters/cost fixes from codex/work; never infer 150K from 50K.
At 1 MNQ compare 50K and 150K evaluations: base, addition, replacing Bridge Monday, empty Bridge slot.
50K and 150K funded: base, addition, replacing Overnight Tick/VIX at prespecified slot size, empty slot; paired block bootstrap.
Personal: base at the current ladder/full portfolio sizes, addition 1 MNQ, replacing Overnight Tick/VIX at same size, empty slot; equal-capital/integer-size comparison and chronological daily/intraday marks.
If a bench adapter cannot faithfully represent this Sunday interval or actual sizing, document it as blocked rather than returning an invented comparison.
No deployment, plan edits or rank changes; Claude checks the report.

