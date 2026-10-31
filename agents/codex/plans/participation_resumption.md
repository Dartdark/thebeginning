# NQ Participation Resumption: frozen standalone study

Evidence: agents/codex/evidence/participation_resumption.md. Commit before returns. Only5/15min signals.
Use rawNQ Grid24 bars aligned to midnight; require full valid constituent minutes, nativeCT close labels.
Normal cash sessions only; noJuly3/December24. Prior15weekday ATR, shifted by sharedgrid. No old trades.

## Exact entry

LetA,B,C be consecutive completed frame-minute bars, with A's first minute>=08:31CT and C close<=14:00,
C close>=09:00. Each range>0. A direction is sign(close-open), body>=60%range; longA closes in top20%,
shortA bottom20%. A range>=1.5times median same-clock A range across prior20normal cash sessions.
Prior20sessions are chronological, do not stretch for missing data; at least15valid observations required.
B candle direction oppositeA; B range<=60%A range; B low>=A midpoint(long) / high<=A midpoint(short).
C close>B high(long) / C close<B low(short), C direction agreesA.
Volume gate: A volume>=k times same-clock prior20normal-session median; B volume<=50%A volume.
All volume quantities finite nonnegative, same complete-data mask for price-only controls.
Buy/sell at native open immediately after C's close (j+1), no same-close/stale/invested signals. Max4/day,
one position, signals while invested suppressed; stop0.10priorATR,target0.20priorATR, ceilto0.25point,
entry-bar active. Time exit Cclose+60minutes or14:55whicheverfirst. No BE/trail/overnight/size fitting.

Five economic configurations, fixed order: P5_V15(primary5min,k1.5); P5_V20(5min,k2); P15_V15(15min,k1.5);
PRICE5,PRICE15(exactprice rules/data eligibility without A-volume/B-volume gate). Controls unselectable.
Count all5 plusprior10program configurations and unknown older searches. No threshold/exit retuning.
NQ$7.25RT plus1tick($5) market/stop fill; MNQ$1.24RT plus$0.50/fill separately. Target1point through.
Fixed4tickfill stress, not a selectable model. Shared_walk execution adapter from flow_absorption retains
same source execution conventions, with entry_j=j+1 and this plan's60minute time exit.

## Staging and decisions

Input duplicate/valid OHLCV/clock audit and prior-only checks before returns. Conflictingduplicatesblock.
First2018-22 only: >=100trades,net>0,trade t>=2,dailyNW5>=1.5,PF>=1.20,>=4positiveyears,
nativeMNQ net>0 and4tickstressnet>0. Ifseveralpass choose firstfixedorder, notmaxreturn. Commitdesign.
Ifnonepass do notvalidate orbench; continue next distinct hypothesis. Validation2023--2026-10-09 once,
previouslyseenhistory, notfreshholdout. Standalonet6meansfullnettrade t>=6 AND dailyNW5>=6 aftercosts.

Reportall/long/short/year standardrepo metrics including initialzeroDD,NW5/NW20,signal/cap/missingminute
counts,cost/nativefees/stress. Filtertotalbase/kept/removednet,removedavg/t,1000matchedrandomdrops;
actualcapdependentledgers may notnest, so use separatelylabelled nonexecutable independent-per-signal
subsetdiagnostics. Countthoseadditionaldiagnosticreturnpaths, nofalseexecutablefilterclaim.
Afterpass only: matched-exit randomside/time controls,5000blockbootstrap/permutation,10000tradeMC,
5000oneyeardailyMC,DSR/selection/sensitivity withalltrials. Checker rebuildbeforepromotion, then current
personal19A-D/FULLBASE/ADD/replaceRS/EMPTY at1MNQ. Validjointpathsrequired for50K/150Kaccountclaims;
missingpathsexplicitLIMITS, neverinventproxyimprovement. NoPowerLanguage/live actiononfailedgate.

Deliver analysis/codex_participation_resumption.py, analysis/outputs/codex_participation_resumption/,
agents/codex/results/participation_resumption.md (Summary<=5lines). Onlycodex/workandallowedpaths.
