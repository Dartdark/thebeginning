# NQ Relative Turnover Switch: frozen standalone preregistration

Evidence: agents/codex/evidence/relative_turnover_switch.md. Commit before returns. Only5/15min signals,
one-minute inputs/execution. Prior45evaluations/44unique; add5=>50/49, plus unknown much larger old searches.
No old trade lists, fitted price residual, implied-variance gate or Opening Path Persistence retuning.

## Inputs, references and signal

Native CT close-stamped NQ/ES grids; exact calendar-date alignment. Design grids start2018, no2017warm-up.
Normal cash research dates only (shared calendar, skipJuly3/Dec24), skip C.roll_guard standard quarterly window
(secondThu,Friday,nextMonday,Tuesday inMar/Jun/Sep/Dec). Roll dates retain NaN places in normal-date reference
windows. No current-day full-session data/completeness mask may determine an earlier signal.

Bars aligned to midnight. Both current and previous bars must have every NQ/ES minute finite/valid OHLCV,
nonnegative volumes; aggregated Vnq,Ves and closes positive. Define R=Vnq*20*Cnq/(Ves*50*Ces), a notional
turnover ratio, not net demand. For each clock bar, references are median R, Vnq and Ves over exact prior20
normal research dates, excluding today,min15valid joint observations; missing/roll observations stayNaN,
never stretch the window. Ratio normalization Q=R/priorMedianR, N=Vnq/priorMedianVnq,E=Ves/priorMedianVes.
Require valid positive references for current AND previous bar in every model.

At current bar close j09:00--14:00CT, potential long if NQclose>NQopen, body>=50%range and close in top25%
of positive range; short mirrored bottom25%. Common own-volume gate N>=1 and E>=0.5. Candidate additionally
requires previous bar Q<=1 and current Q>=k. Previous Q uses its own same-clock prior reference, NOT today's
current-bar reference. No prior-price residual, absolute move or day trend filter.

Five models/order: CTS5_15(primary5min,k1.5),CTS5_20(5min,k2),CTS15_15(15min,k1.5),OWN5,OWN15.
Controls retain price/own-volume/current+previous-data/history conditions but omit BOTH peer-ratio switch
conditions. They are unselectable; do not nominate after seeing returns. No extra side/symbol/exit/size grid.

## Execution and costs

Signal at close j; market at native open j+2, one extra whole minute for receipt/order delay. Stop0.10prior
15weekday calendar ATR,target0.20sameATR,ceil distances to0.25point. Active entryminute, shared_grid._walk
via F.replay adapter; no shared engine edits. Max4trades/day,oneposition,no stale/same-close entry; time exit
min(j+45,14:55). NoBE/trail/overnight/resizing. NQ$7.25RT plus1tick($5)market/stopfill; target1pointthrough.
NativeMNQ$1.24RT+$0.50/fill independent. Fixed4tickfillstress. Missing scheduled open=>skipthat signal;
subsequent signals can be considered under the ordinary4/day/flatness rule, no delayed stale order.

## Intake and design gate

Audit duplicate conflicts, both clocks/date mapping, minute completeness, positive quantity/multiplier units,
prior-only medians, roll windows and actual execution counts. Conflictingkeys=>NEEDS DATA. Preserve source
hashes, features and synthetic tests before returns: turnover units, switch direction/previous-clock reference,
long/short price symmetry, current/future mutation invariance, exact rolling windows with missing records,
entry-bar/gap/through and delayed-entry/flatness conventions. No data repaired from future observations.

2018-22 cheap gate:>=100tickets,net>0,trade t>=2,dailyNW5>=1.5,PF>=1.20,>=4positiveyears,nativeMNQnet>0,
4tickstressnet>0. Actual candidate capped net must be>=its OWN control capped net. Different capped actual
ledgers are NOT nested; do not invent actual removed trades by forcing a join.

Separate independent-per-window diagnostic permits overlapping entries, using original exits/costs. Candidate
signals are true subsets of OWN signal windows. Report all/kept/removed totalnet,removedmean/t and1000matched-
size random subsets. Require removedmean<0,kepttotal>=base,p(randomnet>=kept)<=.10 and candidate jointly
betterprofit/DD than>=90%random subsets. These sums/DD are NON-EXECUTABLE diagnostic paths, not portfolios.

Additional1000matched random subsets hold the candidate's count in EACH signal-clock-hour x own-relative-
volume stratum. NQrelativevolume strata: [1,1.5),[1.5,2),[2,infinity); hours j//60. Sample without replacement
inside each cell from eligible OWN independent windows; same total count as candidate. Require same pnet<=.10
and jointprofit/DD>=90%. This controls some own-volume/time effects, not all causal confounding. Save all
random totals/DD as diagnostic paths; no selected placebo or cell/threshold retuning.

First candidate passing ALL basic/actual/uniform/stratified gates by fixed order, never maxreturn. Commit
design before chosen+matching OWN2023--2026-10-09 once, explicitly previously-seen historical validation.
Nonepasses=>stop this hypothesis's validation/accounts, preserve failure and continue a DISTINCT mechanism.
Full-history t4.5/t5/t6 threshold requires BOTH nettrade t and dailyNW5>=threshold, positive design/validation,
realistic native costs and no fatal issue. Preserve milestone history; lower crossings don't complete t6.

## Conditional completion and outputs

Report all/long/short/year standard shared metrics, cashdayzeros/initialzeroDD,NW20,costs,nativefees/stress,
signal/suppression/missingentry/missingheld counts, actual capped comparison and clearly separated diagnostics.
After pass only: matched-exit randomside/time5000 with actual chronological/cap rules, blockbootstrap/
permutation5000,tradeMC10000,oneyeardailyMC5000 at1MNQ,DSR/selection at>=243reported-trial lowerbound and
fixed sensitivities. Fresh spec-only independent checker before promotion, then currentpersonal19A-D/FULL
1MNQ BASE/ADD/replaceRS/EMPTY; valid50K/150Kjoint chronology required for precise account improvements,
otherwiseLIMITS. No proxy pass/payout claims or inferred pre-breach protection. Frozenforward needed.

Deliver analysis/codex_relative_turnover_switch.py,analysis/outputs/codex_relative_turnover_switch/,
agents/codex/results/relative_turnover_switch.md Summary<=5lines. Onlycodex/workandallowedresearchpaths;
no watcher changes, sharedrank/plan/rootTODO/live/VPS/broker/API/purchases/accounts/messages orPLonfailedgate.
