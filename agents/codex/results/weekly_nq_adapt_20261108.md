# Assumed weekly NQ/VIX strategy: REJECT — design gates failed

Summary: Filled the paper's missing formulas under the user's explicit instruction and tested one frozen adaptation.
2018–22at1MNQ:16trades,+$4686net,Sharpe0.54,t0.92,maxdailyDD$3500; EMA-onlybaseline+$7029.
Failed minimumtradecount,t>=2and required0.10Sharpeimprovement; no tuning or2023+returntest followed.
No portfolio addition or MultiCharts code. Independent verification pending; source replication is not claimed.

Plan: [frozen adaptation](../plans/weekly_nq_adapt_20261108.md), initialcommit
`5b383dc`, pre-return data-only amendment `2a2d27d0431929080cf9b38b7a8206887ad83653`.
Script: [implementation](../../../analysis/codex_weekly_nq_adapt_20261108.py).
Output: [JSON](../../../analysis/outputs/codex_weekly_nq_adapt_20261108/results.json),
[daily ledger](../../../analysis/outputs/codex_weekly_nq_adapt_20261108/full_daily.csv),
[trades](../../../analysis/outputs/codex_weekly_nq_adapt_20261108/full_trades.csv).
Trials:2economicdefinitions(fullruleandbaseline),2fixedcoststresses; no parameter search.

## Rule (as tested)

This is a **new assumed personal-account strategy**, not recovery of the original custom indicator code or
verification of its performance. User authorized filling missing definitions after the source review.

- Weeklyclose from owned NQ08:00–15:15CTexports. Standard EMA5andEMA25must both rise; close>EMA5.
- Ratio=weeklyNQclose/finalcashVIX; signal1=EMA12ofratio, signal2=EMA5ofratio, alladjust=False.
- Interpret screenshot's customRSI1as WilderRSI(2), with explicit initialization in code. No guessed chained
  tripleRSI, extraBBcondition or unobserved indicator optimization.
- Enter long if EMAconditions, ratio>EMA12ratio, RSI2<75andVIX<40.
- Exit on ratio<EMA5ratio, stale/missingVIX, or completedweeklyclose<95%rawentryprice. This is a weekly
  condition followed by a later market order, not an intrabar5%loss cap. No shorts, pyramiding or compounding.
- Fridayfinishedprices/VIXdrive nextweek07:59CTdecision; execute first observedclose-labelledbar>=08:01
  at itsOPEN, ordinarily08:00CT. Mondayholidaysdelay to firstactualsession. Finaldesign liquidation at
  lastobservedsessionclose. No same-decision exit/reentry.
- OneMNQ($2/point). Commission$1.25roundtrip plus0.25pointslippageperleg($1total):$2.25roundtrip.
  Stress doubles slippage to2ticksperleg, holding ordersfixed. ReferenceNQuses$17.25roundtrip, separately.
- Quarantine anyweekintersectingday5–16ofMarch/June/September/December; flat beforethatweek and noentries
  duringit. Thisfixedcalendar prevents holding across knownrollwindows without an ex-postlargestgap rule.
  It is a conservative assumption, **not authenticated actual contract/roll metadata**;45designweeks quarantined.

Baseline uses the same EMAentry, exitsclose<EMA5orweekly5%condition, samecalendar/execution/costs. The
fullrule changes exits as well as entries, so this is not an isolated causal estimate of one filter's contribution.
No returning to differentEMA/RSI/ratio/rollsettings after outcomes.

## Results

Design2018-01-01–2022-12-30;2017warm-up. Dollar results below are **oneMNQ**, fixedsize, after stated costs.

| Design metric | Full assumed rule | EMA-onlybaseline |
|---|---:|---:|
| Closedtrades, alllong |16|27|
| Winrate |56.25%|55.56%|
| GrossP&L |$4722.00|$7090.00|
| Commission |$20.00|$33.75|
| Slippage |$16.00|$27.00|
| NetP&L |$4686.00|$7029.25|
| Average net/trade |$292.88|$260.34|
| Annualnet(252sessions) |$914.70|$1372.09|
| Trade-meant |0.92|1.05|
| DailySharpe |0.54|0.50|
| Sortino |0.73|0.66|
| Tradeprofitfactor |1.88|1.73|
| Dailymaxdrawdown |$3499.88|$5820.88|
| Calmar |0.26|0.24|
| Ulcer,50Kreferencecapital |2.62|3.70|
| Netunder2ticks/legstress |$4670.00|$7002.25|
| ReferenceNQaverage,own$17.25cost |$2934.00|$2608.68|
| Shorttrades |0|0|

AnnualP&L(oneMNQ; daily marking includes unrealized P&L, not exit-only booking):

| Year | Fullrule | Baseline |
|---|---:|---:|
|2018|$1092.75|$377.75|
|2019|−$733.75|$1780.63|
|2020|$2841.00|$4971.75|
|2021|$4535.38|$4969.25|
|2022|−$3049.38|−$5070.13|

The fullrule has smaller daily drawdown but less total profit and only a small Sharpeimprovement. Its16trades
do not establish a reliable positive mean. No claim of confirmed netedge, independence, hedgeprotection or
paper's claimed5.9%drawdown follows from this cheap screen. $50Kis a metricnormalization, not a recommended
accountbalance or evidence of collateral sufficiency.

## Frozen gates and stop

| Gate | Fullrule |
|---|---|
|>=20closedtrades|**FAIL:16**|
|Positivegrossandnet|PASS|
|Trade-meant>=2|**FAIL:0.92**|
|DailySharpe>=0.5|PASS|
|>=3positiveyears|PASS|
|Positivefixedcoststressnet|PASS|
|Sharpe>=baseline+0.10|**FAIL:0.54vs0.50**|
|Annualprofit/DD>=baseline|PASS|

Allgateswererequired. **Designfailed.** No2023+NQdatafiles orreturnevaluations, bootstrap, circular-shift
placebo, personalBASE/ADD/REPLACE/EMPTYorApexsimulation followed. FullVIXCSVwas read for integrity/hash
and then truncated at2022before features; JSON'sholdout_read=falsemeans no laterNQ/outcomeevaluation,
not that bytes of the completeVIXsourcefile were never read. No laterVIXvalue enters this screen.

## Data, ledger and verification

Owned NQminuteexports2017–22andVIX_daily were read from the existing sourcecheckout, without changing it.
Gitblobidentitywas checked against currentcodex/work; SHA256/bytes/blobs are retained inresults.json. Weekly
formation296rowsbegin2017-05-01; EMA25valid2017-10-20, beforedesign. Missing/NaNprices or duplicatebars
abort; no indefiniteVIXforwardfill. The frozen task aggregates and features are retained with both ledgers.

The first run stopped during preflight on a missing08:01bar, before features/trades/returns. A date/time-only
inventory found2020-03-12first08:02,2020-03-13and2020-03-16first08:06. The data-only amendment was
committed **before** the successful economicrun: use firstobservedbar>=08:01 and record delays. A08:06
close-labelledbarOPENis08:05CT; no absent08:00fill was invented. This is still a bar-open execution proxy.

Cashmarks run daily while holding; entry/exitfees and slippagebook on their actualdays. Gross,commission,
slippage andnet daily sums reconcile to closedtrades within$0.005. Source metric functions are reused;
maxDD uses the repo helper that includes the initialzeroP&Lpeak, with Calmar matched to thatDD. These are
engineering reconciliations, not independent verification. Both candidate and baseline outcomes remain visible.

## Five review questions after filling the gaps

1. **About:** an assumed weekly longNQtrend/relative-strength system inspired bySSRN5630830.
2. **Finds:** our2018–22screen makes$4686net/1MNQwitht0.92andfails; originalauthorreturns remainunverified.
3. **Why money:** proposed equitydrift/trendpersistence, not identified forcedflow. This test does not establish
   the assumed VIX/RSIaddition as a reliable source of excessreturns over the simplerbaseline.
4. **Build on it:** no planaddition from these outcomes; failedfrozengatesstopdependentwork. Weeklyholdalso
   excludes50K/150Keval/fundedfit. No personalportfolio benefit was earned or fabricated.
5. **Code:** the committedPythonstrategy **nowexists and was actuallybacktested** with explicit assumptions.
   MultiCharts is withheld afterfailure. It is an adaptation, not the missingauthorcustomcode.

## What could make this wrong

Signalassumptions, MondayRTHexecution and rollquarantine materially differ from the paper. This rejection
applies to the testeddefinition, not every possibleweeklytrendstrategy. Unidentifiedcontractswitches outside
quarantine could affect P&L; rawcontinuouspricelevels can affect features even when rollcarrying is avoided.
RTHdailyclosemarks capture close-to-closeovernightgaps, but not full overnightintraperiod adverse excursions,
so reportedDD is **daily-markdrawdown, not a full minute-by-minute worstloss**. No funding,collateral,margin
or brokerexecutability certification. Stated costsare modelassumptions; no measured bid/ask execution.
Trade t is the frozen cheapgate diagnostic, not a serial-dependence-corrected promotion result.

No more variants were selected to rescue this failure. Existing source-rejection and multiplicity history
remain; this task adds twoeconomicdefinitions and their twofixedexecutionstresses. No TIER/tradingplan,
live/VPS/broker/APIkey, scoutstate or automation change. Retain the source's execution lessons with this
failed adaptation as follow-up; no new promising-strategy queue or data-shopping request.

## Differences between MultiCharts code and test

No MultiCharts strategy was written after the failed gate. Exact Python definitions, settings, input hashes,
features, trade ledgers and results are available for Claude's independent review.
