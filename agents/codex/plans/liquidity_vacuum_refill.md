# NQ Liquidity Vacuum Refill: frozen standalone study

Evidence: agents/codex/evidence/liquidity_vacuum_refill.md. Commit before returns. Signal frames5/15minutes.
NativeCT minute close stamps; normalcash dates, skipJuly3/Dec24. Only NQraw OHLCV; no old tickets.

## Entry

LetA,B be consecutive completed frame bars. B closes01:00--06:30CT aligned to midnight. Require complete
valid native OHLCV for both and the entire preceding30minutes beforeA; all quantities finite/nonnegative.
A range>0, direction sign(close-open)!=0, body>=70%range, close in top20%(up) / bottom20%(down).
A range>=r times median A-same-clock range over exact prior20normal cash dates, at least15valid observations.
B direction oppositeA and B closes at/beyond A midpoint againstA. ForupA, Bhigh<=Ahigh+0.25 and
Bclose< Bopen and Bclose<=(Ahigh+Alow)/2; fordownA mirrored low>=Alow-0.25, close>=midpoint.
B range>0. Volume gate: Avolume<=its same-clock prior20normal-session median, at least15valid observations.
Use identical prior-range/volume eligibility on controls. No gap-based entry or static high/low level.
Buy ifdownA rejected, short ifupA rejected; nativeopen Bclose+1. One position, no stale/same-close signals,
max4/day. Stop0.08prior15weekdayATR,target0.12priorATR ceilto0.25,activeentryminute. Timeexit min(Bclose+30,07:25).

Five models, fixedcandidateorder: LV5_R2(primary5min,r2,volumegate); LV5_R3(5min,r3,volumegate);
LV15_R2(15min,r2,volumegate); PRICE5(5min,r2,no volume gate); PRICE15(15min,r2,no volume gate).
No further entry/exit/symbol/side/sizing grid. Controls unselectable. Count5+prior25evaluations=30
(29unique rules; one repeated-source nomination disclosed previously), plus olderunknown repositorytrials.
NQ$7.25RT+1tick($5)market/stopfill; nativeMNQ$1.24RT+$0.50/fill; target1pointthrough. Fixed4tickfillstress.
Execution sharedgrid._walk via F.replayadapter; entrybar/gap conventions unchanged. Max4/day supports allsignals.

Design2018-22 first:>=100tickets,net>0,trade t>=2,dailyNW5>=1.5,PF>=1.20,>=4positiveyears,
MNQnet>0,4tickstressnet>0. Firstpassingcandidate byfixedorder,notbestreturn. Commitdesign.
Additionally volume filters mustremove losing signals andbeat>=90%matchedrandomdrops onnet/DD with
p(randomnet>=kept)<=.10. Becauseactualcapledgers maynotnest, label independent-per-signaldiagnostics
nonexecutable; these cannot bythemselvesjustify anaccount filter improvement. No pass=>continue distinct
mechanism,do notvalidate/retune. Ifpass,chosen+pricecontrol2023--2026-10-09once,previouslyseenhistoricalvalidation.
Fullt6goal nettradeanddailyNW5>=6,design/validationpositive. NW20 reported, alltrials visible.

All/long/short/yearstandardrepo metrics,costs,nativefees/stress,initialzeroDD,cashdayzeros,counts/missingminutes.
Filterbase/kept/removedtotalnet,removedmean/t,1000matchedrandomsubsets. Afterpassonly matched-exitrandomside/
time,5000blockbootstrap/permutation,10000tradeMC,5000oneyeardailyMC; selection/DSR>=223lowerboundtrials,
independentrawspeccheckerbeforepromotion. Then currentpersonal19A-D/FULLBASE/ADD/replaceBML/EMPTY1MNQ,
wholecontracts; missing50K/150Kjointchronology=>LIMITS, no proxybenchclaims. Forwardlogneeded beforetrading.

Deliver analysis/codex_liquidity_vacuum_refill.py,analysis/outputs/codex_liquidity_vacuum_refill/,
agents/codex/results/liquidity_vacuum_refill.md Summary<=5lines. Onlycodex/workandallowedpaths;noPLonfailedgate.
