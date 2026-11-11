# Frozen batch 1: conditional price-impact residual and repair

Evidence: `agents/codex/evidence/pressure_build_20261110.md`. Commit plan and executable code before returns.
User's objective is a coded strategy with screenshot-like or better economic performance that improves the150K book.
Success is earned validation/account utility, not a tuned82% hitrate. No promise of success and no screenshot replication.
This direct user-requested study preserves all prior families/multiplicity and does not restart a scheduled scout/lab.

## Inputs / clocks / causal calendar

Use only native2018–22 minute OHLC,total,buy,sell for design, with existing transfer-manifest hashes. Five-minute bars
require all5 constituent closes; never fill prices/flow. CT timestamps, barclose convention; one-minute inputs originallyET.
Normal cash calendar `codex_cash_open_repair.normal_cash`, excluding July3/Dec24 and its fixed quarterly roll guard.
PriorATR15 is the shared Grid24.daily_atr(15): shifted15 stored observed weekday TRs including overnight native bars;
report this actual convention. Complete signal and2 same-session lagged bars mandatory. Training slots08:45–14:00;
event closes09:00–14:00. Confirmation is exactly event+5min, complete, same date. Late/holiday rows never rescheduled.

## Daily fit, no parameter search

Before date d, select exact preceding20normal_cash calendar dates; roll-guard slots contribute no observations, not replacements.
For each clock slot compute median abs((C-O)/ATR) over these dates, >=15 valid dates. Divide slot medians by their cross-slot
median to form f_slot. All training/current y=(C-O)/(priorATR*f_slot), using today's past-only seasonal scales. No future
sessions or current-day fits. q=(sum_buy-sum_sell)/sum_total. X=[1,q_t,q_t-1,q_t-2]; exact contiguous five-minute lags only.
Require>=600 rows over>=15 dates, full rank, finite residual RMS>1e-9 and b0>0. Fit ordinary least squares once/day;
no projection, alternative fitter, return-target or kernel search. It is an impact regression, not exact propagator theory.
e=y-X*b; z=e/RMS(training residual), ddof0. Price-only z=(y-training_mean_y)/training_population_SD_y.

## Three return definitions, fixed before outcomes

1. **RESID2**, selectable primary: event abs(z)>=2, side=-sign(z). Following closed5min candle must have
   side*(Cconf-Oconf)>0 AND side*(Cconf-Cevent)>0.
2. **PRICE2**, unselectable control: abs(price_z)>=2; side=-sign(price_z); identical confirmation/exits.
3. **NO_CONFIRM**, unselectable control: same event/side as RESID2, same delayed confirmation-clock entry and same stop
   geometry, but no directional confirmation condition. Both policies are stateful under caps; don't label their executable
   difference a pure removed-trade ledger. No control promotion, threshold/side/time/exit rescue after these outcomes.

## Orders and risk

At confirmationclose j, allow one wholeminute receipt/order delay. At walltime j+1, observe native OPEN of j+2-labelled
minute as an execution-attempt quote proxy. Only this open may condition the guard; not its futureHLC.
Long stop=min(eventlow,conflow)-.25; short stop=max(eventhigh,confhigh)+.25.
If reference price is wrongside of stop or distance>.15priorATR, skip attempt; no stop relocation. Tick-ceiling target
distance=.3*positive reference risk. Brackets active in entryminute. Separate adverse fill slippage can exceed this
reference risk cap; actual quote-to-fill receipt is unverified. Shared _walk stop-gap/both-hit logic; target1pointthrough.
Close by min(entryrow+29,14:55),30wallminutes after its minuteopen; earliestnextentry must be strictlyafter priorexit;
max4trades/day; no BE/trail/averaging.
No missing scheduled open => later retry. Audit every actually heldOHLC minute; unknown path blocks advancement.

NQ$20/point, fee7.25RT+5USD permarket/stopfill; MNQproxy$2, fee1.24RT+.50/fill. No target-exitslip but1pointthrough.
4tick permarket/stopfill coststress, not newstrategy. MNQnative cost/price parity unverified. Preserve fees/quotes limits.

## Cheap gate and earned stages

Save all3 uncensored signal/executable trade ledgers, suppression and quote-guard counts, daily zeros, annual/long/short
metrics, trade t,dailyNW5/NW20, standardSharpe/Sortino/PF/Calmar/Ulcer, observedriskcost and held-minuteQA.
Primary gate:>=150trades,>=25eachside, netNQ>0, tradet>=2, dailyNW5>=1.5, PF>=1.20,>=4positive designyears,
MNQproxy net>0,4tickstressnet>0, zeroinvalidheldpaths. A partial gate is not a pass.
Count ambiguous both-hit exitbars and require positive stop-first ambiguity-stress net as well; never manufacture a high
hit rate from the shared minute OHLC path heuristic. This is an execution stress, not another economic strategy.
If basicgatepasses, assess confirmation as a filter using independent sameevent ledgers without occupancy/caps and label
these diagnostic, not executable. Removed events must lose on average/t<=-1; compare1000year×side matched random subsets
at same count, candidate joint profit/DD ranks>=90thpercentile. Compare PRICE2 wholepolicy and paired daily effects;
primary incremental total positive with10day-block90%CI low>0. The control cannot replace primary if it wins.
Only after all design gates pass: commit selected rule/results before reading2023+ returns; import separately reconciled
price/aggressor daytime data through2026-07-07. Already-seen history is historical validation, not fresh OOS. Same rule once.
Positive validation: randomtime/side matched-exitplacebos,5000blockbootstrap/permutation, fullstandard byyear/side, oneextra
minute andextratickfillstress, selection-adjusted significance with allpriorsearches; independent raw-spec checker.
PowerLanguage only after economic gates pass; nativeMC not verified by this environment.

## Book utility after candidate earns it

Freeze1MNQ before account outcomes. BASE=current six pieces(VB15,ONB2750,Bridge5,EOS1250,Twin2,DT2);
EMPTY=BASE−VB, ADD=BASE+candidate, REPLACE=EMPTY+candidate. Correct integerfinish per sleeve, explicit30calendardays,
continuing150K4kEODtrail/intradaytouch,2kDLL with overshoot/fees, commonprice chronology and UNKNOWN paths.
Track candidate contribution at/before VB/ONB stop/failure timestamps, not only full-day P&L. No positive account claim
from old21session/fractionalfinish/clippedDLL/summedindependentextrema engines. If source gaps block honest replay, say so.

Each failed batch closes its dependent validation, not the whole authorized research task. Continue only with a genuinely
specified alternative mechanism and a new committed protocol, preserving trials; never tune until the screenshot matches.
Initial batch economicdefinitions=3; maintain append-only study trial records including later batches and controls.
