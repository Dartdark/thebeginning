# NQ Opening Path Persistence: frozen, result-informed follow-up

Evidence: agents/codex/evidence/opening_path_persistence.md. Commit before any new returns. The OPP source
rule was previously run as unselectable OWN5control (opening_pressure,31eeb11). Its2018-22 results are known.
This is a NEW counted nomination, NOT a new independent preregistration or permission to relabel the old test.
No2023+ results for this entry have been seen. Only completed5min signals with1min execution.

## Exact rule and five evaluations

Use same common cash-open data eligibility as source: NQ/ES/YM exact08:31open and every native valid OHLCV
minute08:31--09:00CT. Normalcash days, skipJuly3/December24; no ES/YMdirection/return filter. No old trades.
Six completed NQ5min closes08:35...09:00. net=C09:00-O08:31. path=sum|diff([open,sixcloses])|.
Efficiency=|net|/path; zero path or net means no trade. Move=|net|/prior15weekday calendar ATR.
Primary OPP requires efficiency>=0.50 AND move>=0.15. At09:01nativeopen buy ifnet>0,sell ifnet<0.
One/day; stop0.15ATR,target0.60ATR ceilto0.25, entrybaractive, noBE/trail, timeexit14:55CT. Shared_walk.
Warm-up exactly as source: design source files2018-22, no2017warm-up, cashdayzeros retained.

Five model evaluations (count all; primary repeated fromsource, four unique new configurations):
1. OPP:primary0.50efficiency/0.15move, prechosen before newtests; only selectable nomination.
2. E40:efficiency0.40/move0.15, fixed neighboring diagnostic, unselectable.
3. E60:efficiency0.60/move0.15, fixed neighboring diagnostic, unselectable.
4. M10:efficiency0.50/move0.10, fixed neighboring diagnostic, unselectable.
5. ALL5:same direction/entry/bracket/time and common data mask, no efficiency/move threshold. Control only.
No exit/side/symbol/size search. NQ$7.25RT plus1tick($5) market/stopfill; target1pointthrough.
NativeMNQ$1.24RT plus$0.50/fill; fixed4tickfillstress not a selectable model.
Conservative program total25counted evaluations (24unique rules); unknown older trials remain relevant.

## Design nomination and staged return access

Reproduce OPP2018-22 ledger against source OWN5exactly before evaluating newresults. Primary cheapgate:
>=100trades,net>0,trade t>=2,dailyNW5>=1.5,PF>=1.20,>=4positiveyears,nativeMNQnet>0,4ticknet>0.
Neighborhood: all3netpositive and at least2of3trade t>=2; no selecting neighbors ifprimaryfails.
Filter control: ALL5actual base, exactsubset; removedmean<0, kepttotal>=basetotal,
matched1000randomsubset p(net>=kept)<=0.10 AND kept jointlybetterprofit/DD than>=90%random subsets.
These extra checks can veto the basic gate. Commit design before any validation. Ifvetoed stopthisfamily,
continue a different mechanism. Do not flip direction/threshold/target after seeingresults.

Ifaccepted, run OPPandALL5only2023--2026-10-09once. Previouslyseenmarket history, neverfreshholdout.
Full t6pointgoal nettrade t>=6 AND dailyNW5>=6, each design/validationnetpositive. ReportNW20 as sensitivity.
Ifpointgoalnotmet do not manufacture achievement; report and continue distinct newresearch.

All/long/short/year standardrepo metrics; cash-dayzeros,initialzeroDD,costs,missing/suppressioncounts,
NQ/nativeMNQ/stress. Filter all/kept/removed totalnet,removedmean/t,1000randomdrops ondesign/validation/full.
Before a qualifying claim: randomside andrandomtime entries matchedexits,5000each; blockbootstrap/permutation
5000,tradeMC10000,oneyeardailyMC5000 at1MNQ; DSR at>=218reportedtrials as alower-boundcount,
explicit selection/unknownsearch limits. No broad plateau claim from3neighbors or their maxreturn.
Independent spec-only fresh checker before promotion; then current personal19A-D/FULL1MNQBASE/ADD/
replaceRS/EMPTY. Missingjoint50K/150Kchronology=>LIMITS,no inventedbenchmarkimprovements. Frozenforwardlog
needed beforetradingdecision. NoPowerLanguage or liveaction onfailedgate or unqualifiedt6.

Onlycodex/workandallowedresearchpaths. Deliver analysis/codex_opening_path_persistence.py,
analysis/outputs/codex_opening_path_persistence/,agents/codex/results/opening_path_persistence.md Summary<=5lines.
