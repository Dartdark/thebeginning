# NQ Opening Pressure Consensus: frozen standalone preregistration

Evidence: agents/codex/evidence/opening_pressure.md. Commit before returns; only5/15min signal bars.

At09:00CT, require all native OHLC minutes08:31--09:00 for NQ,ES,YM, finite valid OHLC, nonnegative volume,
normalcash day, notJuly3/December24. Read exact firstopen08:31 and frame-minute completed closes through09:00.
For each symbol, calculate net=C09:00-O08:31, path=sum(abs(diff([O08:31, completed frame closes]))),
efficiency=abs(net)/path (zero path => no signal), move=abs(net)/prior15weekday calendar ATR viaGrid24.
NQ efficiency>=0.50, NQmove>=0.15. Candidate also requires ES andYM net same sign asNQ,
each efficiency>=0.25 andmove>=0.05. Do not use old RS scores/ONB/VB/Twin entries.

Exactly five economic models, fixed candidate order:
1. CP5:5min closes, above conditions, primary.
2. CP15:15min closes, same conditions.
3. CP5_HI:5min, NQmove>=0.30 instead of0.15; other thresholds unchanged.
4. OWN5:CP5's NQconditions/complete-three-symbol mask, omit ES/YM pressure thresholds.
5. OWN15:corresponding15min own-pressure control. Controls not selectable strategies.

Buy/sell NQ at native09:01bar open in NQdirection. One trade/day. Stop0.15priorNQATR,target0.60,
ceil distances to0.25point, active entrybar; timeexit14:55CT. No trailing/BE/overnight/size/side fitting.
Sharedgrid._walk execution via codex_flow_absorption replay adapter, signal_j540,entry_j541.
NQ$7.25RT plus1tick($5) market/stopfill, target1pointthrough. MNQ$1.24RT plus$0.50/fill independent.
4tick/fill cost stress fixed, not selectable. Five models plusprior15programmodels, unknown oldsearches.

Design2018-22 first. Gate>=100trades,net>0,trade t>=2,dailyNW5>=1.5,PF>=1.20,>=4positiveyears,
nativeMNQnet>0,fourticknet>0. Ifseveralpass choose firstfixedorder, neverbestreturn. Commitdesign.
No pass => end this hypothesis's validation/accounts and continue a different preregistered mechanism.
Chosen2023--2026-10-09 once, explicitly previouslyseen historical validation. t6goal full nettrade anddailyNW5>=6.

Report all/long/short,year,design/validation standardrepo metrics includinginitialzeroDD,NW20,costs,nativefees,
counts,missingheldminutes. Allcandidateledgers exact subsets of ownframecontrol (one/day). Report total
kept/base/removedprofit,removedaverage/t,1000matchedrandomdrops. CP5_HI baseOWN5 includes NQthresholdchange.
After designpass only: matched-exit randomside/time,5000blockbootstrap/permutation,10000tradeMC,
5000oneyeardailyMC,DSR/selection/sensitivity; independent raw-spec checker before promotion, then whole-contract
1MNQ currentpersonal19A-D/FULL BASE/ADD/replaceRS/EMPTY. Missing50K/150Kjointaccountpaths=>LIMITS,
no proxy-derived claimed improvements. Frozenforward evidence needed; noPowerLanguage onfailedgate.

Onlycodex/work, writes agents/codex/,analysis/codex_*.py,analysis/outputs/codex_*.
Deliver analysis/codex_opening_pressure.py,analysis/outputs/codex_opening_pressure/,
agents/codex/results/opening_pressure.md(Summary<=5lines). No sharedrank/plan/live/APIchanges.
