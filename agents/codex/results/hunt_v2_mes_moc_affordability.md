# MES MOC affordability: CLOSED at source gate, no returns measured

Summary: The frozen extra-MES policy had enough observed design opportunities, but one normal cash date lacks both required decision references. The unknown event cannot be discarded as a nonsignal. Close H09 before gross, stopped designs or book tests. No profitability, candidate, failed-economic-edge or account-improvement claim follows.

Plan: [H09 preregistration](../plans/hunt_v2_mes_moc_affordability.md), commit `1a8087f7358901e08fa7e284ded7a6913b58568b`. Source implementation: `2c2391039dc774dfc4cb9511e63920c229a8e6c8`.

Running budget: **5/60 economic evaluations, 9/10 registered hypotheses, 4 gross screens**, plus archived65t6(63unique rules). H09 adds1registered hypothesis,0gross screens,0economic evaluations. This is not the budget limit; the program is not paused because H09 failed.

## Rule and mechanism as frozen

The accepted ES closing-flow parent follows the signed C1400-to-C1450 move when magnitude>=.30 of its literal prior15weekday CT5-minute chart-date ATR. Exact next native OPEN1451, active .25ATR stop rounded up to MES.25tick, no target, exact C1500 exit. Literal holiday predicate plus the preregistered conservative normal-cash-session guard; no future full-session membership, forward fill or endpoint fallback. The guard is a disclosed research port, not exact PL/MC parity.

Keep the existing1MES. Allocate one EXTRA MES only when two contracts' planned stop risk including primary costs fits the fixed250USD research slice: D=ceil(A)*.25points; EXTRA=1 iff2*(D*5+3.74)<=250, else0; POLICY=1+EXTRA. Exact rational/tick arithmetic includes equality. A250USD allowance is a research normalization, not actual user capital or a guaranteed loss cap; gaps remain uncapped. Baselineq1 stays even when planned risk exceeds250.

This continues H08's disclosed affordability family on an accepted parent; it is neither new directional alpha nor independent of prior RiskPerTrade, constant-size, volatility-target and fractional MOC ATR-dollar-pooling selection. Benchmark/index execution is the parent's proposed cause, not measured auction imbalance, authenticated participant identity or forced size. Prior source comments reporting199MC/202Python full-history trades and parameter/future-year performance remain selected history, not fresh validation. The incremental EXTRA itself, rather than POLICY borrowing parent statistics, would have needed promotion and book/placebo gates.

MES primary native cost:5USD/point, .25tick=1.25USD;1.24RT commission+one adverse tick per entry and market/stop exit=**3.74USD**. Frozen raw EXTRA hurdle **7.48USD**. Four-tick stress planning cost11.24USD. These are preregistered assumptions, not measured broker charges or executed fills. No cost was applied to returns here.

## Actual source/support execution

Execution started2026-10-27T02:10:01.015192+00:00 and completed2026-10-27T02:10:52.155366+00:00. Only explicitly bound ES2017–22 minute files were read;2017 is warmup,2018–22 design. All six input hashes were saved before header/value interpretation. Shared Grid24/bars5 was checked against the global native audit; its future `trading`/last-bar fields did not select events, and its one-minute daily ATR was not substituted for literal chart-date ATR.

|Source check|Measured result|
|---|---:|
|Native rows / unique keys|2,096,132 /2,096,132|
|Duplicate groups / invalid OHLCV-clock-tick rows|0 /0|
|Observed5-minute chart bars / partial buckets|420,890 /6,713|
|Observed weekday TR records / records with partial buckets|1,556 /1,300|
|Reconstructed provisional parent events|131 (57long,74short)|
|EXTRA events|118 (49long,69short)|
|Known affordability on reconstructed events|131/131|
|EXTRA years represented|5|
|Distinct permissible matched masks / variable cells|77,051,520 /4|
|Parent held paths891..900 complete|131/131|
|Unresolved expected normal cash dates|**1:2020-11-30**|

Counts are provisional observed-source opportunities, not executed trades, a complete event universe or evidence of profitability. The missing date may add an unknown signal. Exact allocation masks were counted combinatorially, **not sampled**; no return paths or diagnostic portfolios were priced.

|Design year|Observed parent count|EXTRA count|Long/short profitability and five metrics|
|---|---:|---:|---|
|2018|37|37|Not run|
|2019|17|17|Not run|
|2020|28|25|Not run|
|2021|19|19|Not run|
|2022|30|20|Not run|
|2018–22|131|118|Not run|
|Previously seen2023+ / full2018–26|Not read|Not read|Not run|

## Decisive source failure and independent review

The bound calendar and literal predicate both treat **2020-11-30 as an ordinary eligible cash date**. Its native2020ES file contains only359date/time keys,18:01–23:59CT. Every native component of C1400(j836..840) and C1450(j886..890) is absent. A parent decision is unavailable. It is impermissible to assume no signal, substitute later data, delete the date or change the calendar.

The saved reason `EXPECTED_NORMAL_PRIOR_15_CHART_TR_ATR_NOT_READY_POSITIVE` occurs because there is **no decision record**; it does not independently prove that the preceding ATR history was unready. Reference absence alone is decisive.

The [independent actual source review](../reviews/hunt_v2_mes_source_admission.md) verifies15artifact hashes,7code/dependency hashes, every event/mask count, all131held-path records and a focused date/time-only check of the missing date. Its [machine-readable decision](../reviews/hunt_v2_mes_source_admission.json) is `passed:false, raw_screen_authorized:false`. This is a source-rejection review, not an independent financial raw-spec PASS. No full input audit was rerun and no OHLCV/outcome was selected in the focused check.

Ten observed calendar late-bar contradictions are retained under the frozen conservative exclusions. Past observed-chart partial buckets, upstream timestamp/contract-roll identity, historical receipt, ES-to-MES liquidity and pre-MESlisting counterfactual history remain limits. They are not certified complete feed or MultiCharts parity. The active stop execution helper passed invented-path checks, including entry-through/worse raw OPEN, but actual financial execution was never authorized.

## Gross, economic metrics, placebos and account benches

**All NOT RUN by gate:** raw gross effect/t; net trade t; dailyNW5; winrate; Sharpe/Sortino/PF/Calmar/Ulcer/maxDD; protected primary/control/stress ledgers; kept/omitted profit;1,000matched allocation return paths; random-time/random-side placebos; dependence/selection performance; BASE/ADD/REPLACE/EMPTY book/MC; funded50K/150K/evaluation paths;2023+historical validation. No daily proxy implies pass/payout improvement. No PowerLanguage draft or live action.

The prospective `analysis/codex_hunt_v2_mes_moc_gross.py` was authored with invented fixtures only and stopped on this source failure. Its actual path is **NOT RUN, not authorized and not independently certified for outcome execution**. Retaining it does not reopen H09. Do not reinterpret software fixtures as gross tests or economic trials.

## Reproduction and immutable artifacts

Actual command, for historical provenance (do **not** rerun the retained failed attempt):

```text
/workspace/venvs/thebeginning/bin/python -B analysis/codex_hunt_v2_mes_moc_admit.py --source --prereg 1a8087f7358901e08fa7e284ded7a6913b58568b
```

- [Immutable source marker](../../../analysis/outputs/codex_hunt_v2_mes_affordability/source_verified_execution.json), SHA256 `65664717db0542fbad4bc19abdf226507293e814ae88cd0a87dd23ccdf9d307c`.
- [Source gate](../../../analysis/outputs/codex_hunt_v2_mes_affordability/source_gate.json), SHA256 `42d02d746d72f202dc8e96e1966ffe992d815e155600dca7a10ce893d085c9f7`.
- [Source/input bindings](../../../analysis/outputs/codex_hunt_v2_mes_affordability/source_input_binding.json), [global native audit](../../../analysis/outputs/codex_hunt_v2_mes_affordability/source_native_audit.json), [expected dates](../../../analysis/outputs/codex_hunt_v2_mes_affordability/source_expected_dates.json).
- [Event features](../../../analysis/outputs/codex_hunt_v2_mes_affordability/source_features.csv), [both-side/year counts](../../../analysis/outputs/codex_hunt_v2_mes_affordability/source_counts.csv), [all ATR source references](../../../analysis/outputs/codex_hunt_v2_mes_affordability/source_TR_audit.json), [held paths](../../../analysis/outputs/codex_hunt_v2_mes_affordability/source_held_path_audit.json), [exact null support](../../../analysis/outputs/codex_hunt_v2_mes_affordability/source_null_support.json), [calendar contradictions](../../../analysis/outputs/codex_hunt_v2_mes_affordability/source_calendar_contradictions.json).
- [Predata helper/prereg review](../reviews/hunt_v2_mes_helpers_predata.md), [predata admission review](../reviews/hunt_v2_mes_admission_predata.md). Their invented fixtures are not financial measurements.

**Verdict: CLOSED SOURCE FAILURE before gross; preserve all counts/gates/history, no unknown-date deletion or family rescue. One bounded hypothesis slot remains; this rejection neither completes nor pauses the hunt.**
