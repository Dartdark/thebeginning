# Three-strategy ingredient study: useful historical drivers, no book changes

Summary: Decomposed Dual Thrust, Relative Strength and Late-Day Flow with 13 frozen cases, design first.
DT's range threshold and RS's ES adjustment improve total profit in both periods; paired uncertainty remains wide.
LDF's 14:30 exit is especially important since2023: $47.0k net versus $16.4k holding to15:00, perNQ.
Targets and filters have mixed roles; a higher average trade is insufficient. No promotion or trading change.

Plan: [preregistered definitions](../plans/ingredients_three_20261108.md), originalcommit`a5041ec`,
engineering corrections`0ad14ae`/`8734443`; exact definitions frozen before inspected outcomes.
Script: [reproducible harness](../../../analysis/codex_ingredients_three_20261108.py).
Output: [design](../../../analysis/outputs/codex_ingredients_three_20261108/design/summary.json),
[recent replication](../../../analysis/outputs/codex_ingredients_three_20261108/recent/summary.json).
Trials:13 distinct rule cases across3families, replayed unchanged in2periods; prior source variants remain relevant.
This is historical component research, not a new alpha claim. Independent verification pending.

## Scope, ingredients and rules

These three are distinct from Claude's Twin/OvernightTick/noise-area study. Source ports and calendar code
are [retained](../inputs/ingredients_three_20261108/). All trades execute NQ; ES is a signal input only.

| Family | Proposed source of return | Timing / normalization | Exit / risk shape | Extra condition |
|---|---|---|---|---|
| Dual Thrust v4 | Continuation beyond a meaningful prior-range band | RTHopen±0.5×prior RR; 08:31–14:30 signals |50ptstop,100pttarget,14:56flatten; special entry-bar stop | Skip RR/ADR20>1.2and source holidays |
| Relative Strength NQ/ES | Persistence of NQ's move unexplained by ES |09:00 residualZ, EWMA beta/variance; absZ>=1.25 | Stop0.6/target1.0×prior20dayrange;15:00flatten | Source clean-session calendar |
| Late-Day Flow | Late continuation after a large intraday move; ETF flow is a proposed explanation |14:00 signal, absRTHmove>=0.4×15dayATR | Stop0.25ATR;14:30exit; no target | Prior movement sign sets direction |

No measured ETF demand, forced trader, causal institutional participation or hedge benefit is inferred from
these price-based comparisons. Removing a component can change entry dates, timing and opportunities.
Only the verified nested filters below support a literal removed-trade analysis.

## Results: 2018–22 and already-seen2023–2026-10-09

**All dollar figures in the next three tables are net per1NQ, fixed size**, after$7.25round-tripcommission
and1tick per market/stopfill. Source target conventions retained: DT1tickthrough, RStouch; target exit has
no slippage. Daily DD includes the initial zero-P&L peak; it is not an account blow-up or intraminute guarantee.
2017 is warm-up. No settings selected or changed between periods.

### 1. Dual Thrust: range break is the principal historical ingredient

| Component removed |2018–22net|2023+net|2023+dailyDD|
|---|---:|---:|---:|
|None: original|$111117|$115138|$19621|
|Range distance: enter across the open instead|$60979|$75660|$27231|
|Large-band skip|$100918|$95737|$21993|
|Profit target only|$161002|$165688|$27353|
|Entry-bar stop only|$111117|$114548|$19621|

**Range distance carries meaningful historical value:** removing it reduces net in both periods and increases
DD. This is an entry-timing/rule intervention, not simply dropping some bad dates. The paired annual-effect
intervals still include zero, so “historically useful”is justified, “proven isolated mechanism”is not.

**The volatility-band skip has support:** the124extra design trades average−$82(t−0.78); the63extra recent
trades average−$308(t−2.00). The filter improves total profit and DD in both periods. Its recent paired annual
effect5–95%interval is approximately+$254to+$9496perNQ; the design interval includes zero. In1000
within-year random drops,3.9%beat its designprofit and none beat recentprofit, but11.0%/20.8%have lowerDD.
Thus it is useful historical selection, not a universal proof of optimal risk filtering.

**Target is a trade-off, not the origin of profit:** removing only the100pttarget adds profit in both periods.
However, recentDD rises$19.6k→$27.4k; designDD actually falls. Do not jump from that to “remove it in the
funded plan”. The account objective, altered tail timing, execution and interactions remain untested.

**Entry-bar stop is rarely exercised:** no net difference in design; original earns$590more recently and
limits worst observed trade to−$1042versus−$1322without it. Lack of frequent effect does not make insurance
useless. Later stop and target were unchanged, unlike the coupled ablation found in Claude's noise-area work.

### 2. Relative Strength: ES adjustment is more useful than its target

| Component removed |2018–22net|2023+net|2023+dailyDD|
|---|---:|---:|---:|
|None: original|$164392|$192266|$28539|
|ES adjustment: use NQ-only standardized momentum|$94667|$74451|$45489|
|Z magnitude hurdle|$199298|$108224|$60487|
|Profit target only|$161211|$200261|$30210|

**The cross-market residual is the strongest tested RS ingredient:** original beats the own-momentum
comparator in both periods, with lowerDD. Recent dailySharpe is1.37versus0.60withoutES. This comparator
uses own variance when removingES; it tests the entire cross-market adjustment, not beta subtraction alone.
Paired intervals remain wide: annual contribution includes zero in both periods. These selected historical
comparisons do not establish an independently identified causal effect or new standalone ingredient discovery.

**Z>=1.25is a concentration/risk filter, with regime-dependent totalprofit:** removing it earns more in
design but more than doubles designDD($19.7k→$44.5k). Since2023it reduces net and raisesDD to$60.5k.
The634removed design trades were profitable on average(+$55,t0.66); the379removed recent trades average
−$222(t−1.49). Do not pretend those early dropped trades lost money. Randomdrop controls support unusually
good concentration: designprofit is beaten by4.9%ofsubsets and lowerDD by1.0%; recentprofit by none and
lowerDD by0.2%. This is historical conditional evidence, not a newly earned pass for changing the threshold.

**Target has no consistent profit contribution:** original wins slightly in design; no-target wins slightly
recently, with modestly greater recentDD. Stop, entry timing and range scaling remain unchanged. Its strongest
plausible role is exit/risk shaping; these differences do not support treating it as the main source of edge.

### 3. Late-Day Flow: the short late-day window matters recently

| Component removed |2018–22net|2023+net|2023+dailyDD|
|---|---:|---:|---:|
|None: original|$37366|$47000|$10461|
|Large-move hurdle|$50247|$44117|$20847|
|Stop only|$41533|$45271|$11949|
|14:30exit: hold to15:00|$49925|$16358|$21719|

**Exit timing is regime-dependent and important since2023:** extending the same entries/stops to15:00
increases early profit but cuts recent profit sharply, doubles recentDD and reduces recentSharpe1.21→0.30.
The recent paired annual benefit of14:30over15:00has5–95%interval approximately+$981to+$15194perNQ.
That is conditional on already-chosen history; it is not a newly validated universal closing-flow law.
No post-hoc explanation such as a specific dealer regime is claimed proven by this pattern.

**Large-move hurdle mostly concentrates exposure:** the756extra design trades average+$17(t0.77), so
the filter sacrificed early totalprofit. Recent533extra trades average−$5(t−0.17), essentially no measured
mean advantage before uncertainty. The original's recentDD is much lower than trading every nonzero move.
Yet randomdrops show that lowerDD is not uniquely special:86.8%ofdesign subsets and23.8%ofrecent subsets
have lowerDD. The fullrule's profit is beaten by7.6%/2.1%ofsubsets. Keep the distinction between general
exposure reduction, better selection than random and proven incremental dollar value.

**Stop effect is mixed:** no-stop improves design profit andDD, but original improves recent profit andDD.
Intervals on profit contribution cross zero in both periods. This does not certify uncapped risk. No target
exists in LDF, and no-stop retained all other settings; the sentinel stop did not fire. Risk-control choices
still require actual adverse paths/account limits, not this small return comparison alone.

## Original-rule metrics and side decomposition

| Period / strategy |Trades|Net/trade|t|Sharpe|PF|DailyDD|
|---|---:|---:|---:|---:|---:|---:|
|2018–22DT|888|$125|3.14|1.39|1.28|$13328|
|2023+DT|723|$159|3.07|1.56|1.28|$19621|
|2018–22RS|608|$270|3.06|1.35|1.40|$19696|
|2023+RS|559|$344|2.69|1.37|1.33|$28539|
|2018–22LDF|492|$76|2.70|1.19|1.44|$15036|
|2023+LDF|404|$116|2.38|1.21|1.44|$10461|

Recent side-specific net/t, perNQ: DTlongs$35326/t1.36,shorts$79813/t2.97; RSlongs$137757/t2.81,
shorts$54508/t1.05; LDFlongs$16104/t1.13,shorts$30896/t2.26. These are diagnostic splits, not newly
selected long-only/short-only strategies. All variants' whole/long/short metrics, Sortino, Calmar, Ulcer,
winrate, annualbreakdowns, gross/commission/slippage and native micro figures are saved in
[design metrics](../../../analysis/outputs/codex_ingredients_three_20261108/design/metrics.csv) and
[recent metrics](../../../analysis/outputs/codex_ingredients_three_20261108/recent/metrics.csv).

## Placebos, uncertainty and account level

Every original-minus-ablation daily effect has1000paired20session moving-block bootstrap draws,
seed20261108. Full effect tables:
[design](../../../analysis/outputs/codex_ingredients_three_20261108/design/paired_effects.csv),
[recent](../../../analysis/outputs/codex_ingredients_three_20261108/recent/paired_effects.csv).
Intervals are5/95%, not selection-corrected confidence that a mechanism is true. Significance thresholds
and prior-selection corrections would still apply to any future proposed modification.

Pure filters were verified by matching common-date side/entry/exit/net. Their removed-trade means/t and
1000within-year equal-count randomdrop controls are in summaryJSON. A zero empirical exceedance means
none of1000runs beat it, not a literal probability of zero. Price-only, entry-time and exit interventions
were not mislabelled pure filters. Equal-count controls cannot by themselves validate portfolio usefulness.

No current-book BASE/ADD/REPLACE/EMPTYorApexsimulations were run: the user asked for ingredient attribution,
not adoption. Nothing is promoted, removed, reweighted or written to MultiCharts based on these diagnostics.
The existing13rule cases are the complete budget; no new combination or best-case selection was run.

NativeMNQcosts are computed with$1.25roundtripcommission and actual modeled slip/10. For example, original
recent net totals areDT$11134,RS$18933,LDF$4488at1MNQ, rather than naively dividing NQnet by10.
These are standalone replay totals, not account payouts, required capital or recommended trading sizes.

## What could make this wrong

Pinned owned source snapshot`fe35af99aa90d7f31b91f8693859251bb44dd9ab`; rawfiles verified byGitbloband
SHA256. First design files were committed at`a58f13b`before recent minute data was read.2017warm-up,
common recent cutoff2026-10-09. Raw2026files contain later rows, clipped before feature computation;
no outcome beyond the cutoff was evaluated. This does not make2023+fresh: all three families/settings
have earlier research/selection on that history. These are original Python-port reruns, not a fresh
MultiCharts trade-by-trade confirmation of all counterfactuals.

Source-compatible missingdata policies were retained: DTwalks observed bars, RSforwardfills within a row,
LDFskips missing internal bars. Unknown closes in nominal held intervals are counted, not repaired from future
prices. OriginalDTcounts16design/3recent; RS2/5; LDF0/0. LDF15:00variant has1/3. Thus returns are conditional
on those source execution conventions; native adverse excursions and counterfactual stops in gaps are not
certified. Nominal DTentry index is signalminute+1, so its gap counts can include a delayed next-observed-entry
interval as well as held minutes. Do not treat these counts as precise minutes of an already-open position.

All are intraday, avoiding overnight roll-carry P&L, but continuous-series levels/ATR and incomplete native
contract metadata remain limitations. LDFATR includes fullcalendar-day source ranges; it is not a separately
verified AUM-flow score. RSsource stop/targetactivate after entrybar; target policies differ across source ports.
No same-future-price interpolation, market capacity claim, native collateral certification or independence claim.

The harness had two recorded engineering failures: missingNMIN24constant before strategy execution, then
missingregexmodule atRS calendar loading afterDTcases ran in memory. Both bindings were corrected/committed
without inspecting economic summaries or changing any strategy definition. Replays do not erase13casehistory
or become undisclosed new settings. Daily/trade gross-cost-net reconciliations pass within a cent.

## Reusable lessons and next steps

- DT: meaningful range displacement and the large-band skip are more defensible historical ingredients than
  the fixedtarget as a profit generator. Entry protection remains rare insurance.
- RS: the cross-market residual and its magnitude filter deserve separate roles: signal information versus
  exposure concentration. Target is secondary and regime-sensitive.
- LDF: preserve timing specificity. A large preceding move and a tight holding window are distinct components;
  neither alone establishes actual ETF demand, and stop value varies across periods.

This informs future source-supported, separately registered combinations. It does not authorize combining all
three into a new fitted rule or changing the current books. Useful execution lessons retained in
[EXECUTION_REFERENCES](../EXECUTION_REFERENCES.md). No live/VPS/broker/APIkey, tradingplan/TIER, scoutstate or
automation changes; no external message to Claude. Independent review remains pending.

## Differences between MultiCharts code and test

No new MultiCharts code. Exact pinned source ports, input adapters, intervention settings, complete trade/daily
ledgers and controls are retained for verification. Send Claude this result path.
