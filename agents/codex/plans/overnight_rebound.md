# Overnight Rebound: frozen source replication and plan-placement screen

Date2026-10-25. Commit before real-data returns. Evidence `../evidence/overnight_rebound.md`.
User code workflow applies: assess50K/150K evaluation/funded and current personal ladder/full portfolio, with actual backtests or concrete limits.

## Fixed economic models and clock

**UNIFORM:** uploaded down-cash-day rule, Qty=SundayQty=1.
**SUNDAY2:** uploaded defaults Qty1/SundayQty2; same entries/stops/exits.
**ALLNIGHTS:** unfiltered control Qty1 every valid cash session, including up/flat; not a selectable replacement or optimized strategy.
Three models; no new entry/exit/stop/regime/side search. Count author's336 versions and unknown filters; previously seen2023+ is historical validation.
Run all three on2018–22 before2023+; then both supplied versions and control once on2023–2026-10-09. No validation-dependent changes.
AuthorJan2018–Jul2026 comparison is descriptive; days/fees/size must match. Separate Sunday and other-night summaries without selecting a new strategy.

Data CT minute-close stamps. Source assumes ET display and ClockShift=-60: normalize that declared display to intended CT,
preserving ET Date/DayOfWeek, rather than subtracting60 from already-CT cache. RTH08:31 open through15:00 close builds today range.
If cash close<open, arm. First available close>=17:01 submits market buy for next available native bar, normally17:02-labeled open
(about17:01 wall CT/18:01ET). Preserve Friday->Sunday arm and source one-entry/ET-calendar-date guard.
Stop=.5 cash range, active entry bar, gaps at worse open. Qty separate from per-contract P&L/MAE; no double size/cost multiplication.
Atfirst available03:00<=time<08:31 submit next-bar market exit, normally03:01-labeled open (about03:00wallCT/04:00ET).
Source08:31–15:00 next-bar safety exit remains. No invented16:45ET/weekend guard or holiday repair; inventory exceptions/open positions/missing bars.
Ordinary17→03 calendar-date crossing is inside one17→16 CME/account day under the adopted current-plan convention, not automatically an Apex violation.
Check true15:59flat/16:00maintenance crossings. The older brief's overnight wording does not override the current plan's explicitly adopted OT accounting;
report this as a simulation convention, not newly verified broker permission. Never touch live settings.

Use existing Grid24 read-only and new bounded stop/market chronological adapter if shared flat-day execute cannot represent source state.
Pending orders act on next available native bar, entry-bar stop active, no pre-entry extremes in MAE. Freeze synthetic checks before real history.

## Costs, metrics, controls and cheap gate

Primary NQ$7.25 RT plus1 adverse tick each market/stop fill. Native MNQ$1.24 RT plus$.50 each entry/exit; sensitivity$1.04.
Also author's$1/MNQ zero-slippage convention, explicitly separate. Fixed execution stresses2 and4 adverse ticks per fill; no selected fill convention.
All/long plus explicit shortsN/A; full/2018–22/2023+/yearly standard metrics, total net, gross/cost, trade/EOD DD, MAE, safety/stop/time exits.
Both sizing versions report ticket counts and summed contracts separately. Cash signal known atentry; no direction labels from future returns.
Book outcomes on actual account exit day, not entry date.5,000 ten-day block bootstrap90% intervals,5,000 permutations,10,000 trade MC,
one-year native-size EOD-trail risk illustration (1MNQ/$2k and2MNQ/$4k); seed20261025. Initial zero must count in every DD path.
Significance: current ranked items+3 and conservative additional336-search sensitivity; neither is a complete count of undisclosed author work.

Fixed nulls:500 random evening entry times per model, uniform among observed17:02–20:02 native bars on the same cash-signal/entry dates,
same long direction/range/exits;500 random-side runs at actual entry times, same exits/range. Track intended versus closed paths, no dropped nulls.
Down-day filter: on UNIFORM versus ALLNIGHTS compare total net/DD in each era, removed up/flat trade average and t, and1,000 random subsets
keeping the same trade count as UNIFORM (whole trades, no fitting; seed fixed). Verify shared down entries actually match control, preserve residuals.
A higher per-trade PF alone is not a filter win; removed trades should lose and selected totals/risk should beat random dropping for that claim.
The baseline long drift may still be real even if the down filter's incremental effect is unproven.

Cheap screen for each supplied version: positive net in both eras, full trade t>=2, designPF>=1.15, validation net positive under4ticks/fill.
This replicates a weak existing family; strict promotion still requires multiple-test bar/DSR, controls, independent parity and forward evidence.
No model passing cheap screen=>stop expensive placement and document every plan's limiting condition. Control is never promoted as a post-hoc rescue.

## Conditional placement and baseline limitations

Pin currente1a94f7 metadata: personal roster remains17 (BB_MRM removed); Swing Target bench/v3 files are research, not implicitly a new allocation.
For cheap-pass models, personal currentA–D/FULL: BASE, +candidate atcommon1MNQ scale (Sunday2 applies), replaceOvernightTick where present,
otherwiseONBML, and empty replacement slot. Same1,000 paired252-day10-day paths,5,000 historical annual-mean intervals; primaryfee1.24/1.04sensitivity.
Report day/overnight beta, conditional book-loss contribution and capital/DD tradeoff. Preserve original baselines, no shared cache rebuild.
50K evaluation/funded candidate1MNQ,150K evaluation2MNQ,150K funded1MNQ; Sunday2 multiplies quantity before account rounding/cushion scaling.
Evaluation replacementONB_ADX30; fundedreplacementOvernightTick; empty-slot controls mandatory. Existing account engines are calendar-row matrices
with collapsed Bridge Sunday path/CLS constant adverse/OT whole-night constant adverse. A causal17→16 candidate alone cannot repair their joint
timeline. If causal baseline overlap cannot be reproduced from current data, mark each50K/150K context LIMITED and give the exact missing
baseline chronology; do not publish spurious pass/payout improvements or label otherwise legal midnight crossing an incompatibility.

## Deliverables and boundary

Archive original and metadata under `agents/codex/inputs/rebound/`; scripts `analysis/codex_rebound_*.py`; outputs
`analysis/outputs/codex_rebound/`; report `agents/codex/results/overnight_rebound.md` Summary<=5lines plus independent source/engine review.
All source-size and null/stress trials disclosed. Commit/push only codex/work, pull before push. No resets, force pushes, live/VPS/broker/API
access, PR#2 review/merge, other-agent pushes, paid data/account creation or purchases. No strategy/ranking/allocation edits.
