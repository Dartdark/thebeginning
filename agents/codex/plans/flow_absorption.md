# NQ Flow Absorption: frozen standalone study

Commit before returns. Continuing t6 mandate: do not end the program after a failed candidate.
Evidence: `../evidence/flow_absorption.md`. Signal frames only5/15minutes; one-minute execution.

## Rule

Raw NQ OHLCV and The Bridge OF buy/sell volume; no old strategy trade lists.
Normal cash days only via `codex_s03_calendar`, conservatively skip all weekdayJuly3/December24.
Signal bar closes09:00--14:00CT, aligned to midnight, every5 or15minutes. Bar must contain every native
minute and OF row, all valid quantities; every OF close must match native close within0.25point.
OF labels ET -> CT minus60minutes. Never use a future row/backfill to repair input.

For a complete signal bar, use NQ's first minute open, highest high, lowest low, last minute close.
Buy candidate: close>open, close in top25% of bar range, and (buy-sell)/(buy+sell)<=-threshold.
Short candidate: close<open, close in bottom25%, and delta fraction>=threshold. Range>0,totalvolume>0.
This is price acceptance against aggressive flow; no prior existing entry can trigger a position.

Decision at close j; impose one whole extra native minute for data receipt/order delay: execute market at
open of j+2 (close stamps). If that scheduled native open is absent, skip rather than fabricate a fill.
Stop0.10*prior15-weekday calendar ATR, target0.15*same ATR, both rounded UP to0.25points, active entry minute.
Time exit at close of min(j+30,14:55); one position at a time; at most4trades/day; no same-close reentry,
no reverse-while-invested, no BE/trail/overnight. All eligible bars tested regardless of current plan exposure.

## Five models

1. A5_D20:5minutes, threshold0.20, primary.
2. A5_D35:5minutes, threshold0.35.
3. A15_D20:15minutes, threshold0.20.
4. PRICE5: same complete-data mask and bar-close-location/price direction, no delta gate.
5. PRICE15: corresponding15minute price-only control. Controls are not selectable new strategies.

No additional weight/symbol/threshold/exit grid. Five models count in the cumulative research search,
with the already rejected Cash-Open Repair5 and unknown older author/repository searches disclosed.
Primary NQ$7.25RT plus1tick($5) market/stop fill; native MNQ$1.24RT plus$0.50/fill. Target requires1point
through, no extra exit slip. Fixed execution sensitivity4ticks/fill, not a selectable economic model.
Use `grid.execute` with delayed decision index and per-signal time exit; same-bar stop/gap conventions.

## Data gate and staged test

Inspect OF field/duplicate/clock/coverage matching without forward returns. Conflicting date/time duplicates
are NEEDS DATA; exact duplicate rows can be collapsed with counts. Preserve manifests/hash bindings.
Receipt latency is a conservative reconstruction assumption, not verified historical availability.
No copied scalar POINT_VALUE other thanNQ$20; native micro fees independent.

First2018-22 design only. Candidate cheap gate: >=100tickets, positive net, trade t>=2, dailyNW5>=1.5,
PF>=1.20, >=4positive design years, nativeMNQ net>0, four-tick stress net>0. All failures preserved.
If several pass choose first in fixed order A5_D20,A5_D35,A15_D20. Commit design before validation.
No pass => stop this hypothesis's validation/accounts, update the t6 program and move to a distinct rule.
Chosen2023--2026-07-07 run once, explicitly previously-seen historical validation. A point t6 must be
standalone full net trade t>=6 and dailyNW5>=6, not a basket or multiplied trade count.

## Controls and conditional completion

Show all/long/short/year/design/validation standard repo metrics, initial-zero DD, ticket/daily iid/NW5/NW20,
signals/executed/skipped, costs, missing held minutes, cap suppression and eligible opportunity counts.
Filter: total kept/base/removed net, removed average/t,1,000 matched-size random subsets; candidate kept
trade ledger must be the causal subset of base if path-dependent caps permit. If caps make subsets differ,
use a separate signal-level independent-entry diagnostic, count/report its non-executable overlap, and do
not label a nonmatching removed ledger a valid filter test. Do not delete residuals to force matches.
Only after design pass: matched-exit random-side/time controls,5,000block bootstrap/permutations,10,000trade
MC (descriptive for overlapping days), 5,000one-year dailyMC, selection/DSR lower-bound and10,000sensitivities.
Then current personal19A-D/FULL BASE/ADD/replaceRS/EMPTY at1MNQ and paired1,000histories if justified.
50K/150Keval/funded current joint chronology missing => explicit LIMITS, no precise proxy-derived improvements.
No promotion until independent raw-signal/execution check and frozen forward evidence. No newPL on failure.

Deliver scripts `analysis/codex_flow_absorption*.py`, outputs `analysis/outputs/codex_flow_absorption/`, report
`agents/codex/results/flow_absorption.md` Summary<=5lines. Only codex/work and allowed research paths.
No ranks/shared plans/rootTODO/live/VPS/broker/API/purchases/accounts/vendor messages. Respect403.
