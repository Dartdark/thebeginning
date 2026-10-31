# R2Vault: REJECT for current-plan promotion
Summary: Built the PDF rules and completed all five plan contexts; no version qualifies for promotion.
CT raw is the strongest: full t=2.92, DSR=0.505, below 3.60/0.95; recent returns and nominal placebos are positive.
Evaluation additions reduce pass rates; funded effects fail consistent base/empty-slot benefit. Personal CT gains are small at equal drawdown; source promotion and execution gates remain unmet.
Move on without changing the trading plan. This is a frozen reconstruction, not verified author-platform parity.

Plan: `agents/codex/plans/r2vault.md`, **a973f0779b6e10d9c3c29adc6748ed5eba0d5f92**, before returns.
Calendar clarification: **dab01a8**, also before returns. Implementation: `analysis/codex_r2vault_replay.py`.
Adapters/checks: `analysis/codex_r2vault_*.py`. Outputs: `analysis/outputs/codex_r2vault/`.
Trials: **five fixed rule models**, with declared fee stresses/account sizes; no threshold or source-clock selection.
Known multiple-test lower bound **311**:294 ranked+7 prior Codex+5 concurrent NQDB2+5 R2Vault; original author search unknown.
The frozen context172322e was rechecked against newer Claude1f2d1ff: all 47 baseline dependency blobs remain unchanged.
The existing prepared baseline was reused. Exact rosters/sizing and inherited limits are in `r2vault_plan_context.md`.

## Rule and what was built

Five-minute NQ, long only. Standard OLS on 576 observed closes; if R²<=0.030, the current candle's high/low replace
the vault. With positive slope, next-bar buy-stop at vault high + 20% of range, rounded upward to 0.25; maximum 3 actual
entries/CT calendar date. Fixed 75-point stop/40-point target anchored at actual fill; protection active on entry.
Break-even is off. The PDF's R² exit threshold 2.00 cannot trigger on standard[0,1] R².

Source clock 09:30–15:30 lacks a timezone. ET means 08:30–14:30CT; CT means 09:30–15:30CT. Both use full 24-hour observed
576-bar history and persistent vaults. Raw models carry positions; Apex versions flatten at 15:55 CT/11:30 CT early
(next-minute opening fill). The fifth daily-reset ET model is standalone diagnostic only. No fifth-model placement selection.

One-minute execution uses the repository causal OHLC path: high first when H−O<=O−L, otherwise low first.
Opening gaps precede segments; only prices after entry/before exit contribute adverse exposure. Targets require
one-point trade-through; stops can gap. Queued Apex market flatten takes priority at its opening minute.
These are explicit reconstruction assumptions. The PDF does not specify history template, clock, vault reset,
order lifecycle, quantity or execution settings; its exact trading ledger and continuous-contract roll treatment are unavailable.

Dollar stops are interpreted for one NQ:75/40 points becomes **$150/$80 per MNQ**, not$1500/$800 on a micro.
Tables below use Apexfee $1.04/MNQ RT, $0.50 entry slip, $0.50 stop/market exit slip, zero target exit slip.
Personal portfolios use their frozen$1.275/MNQ fee convention. Full round-trip fee is reserved at entry; no duplicate charge.

## Standalone results

All amounts here are **per 1 NQ** after the declared$1.04/MNQ fee-equivalent costs. Whole strategy=longs; **zero shorts**
(short metrics N/A; explicit empty-short rows remain in CSVs). Daily risk metrics use16:00 CT observable MTM,
not profit lumped at entry. 2026 endsOctober9; repository2023+ is seen historical replication.

|Model|n|Win%|$/trade|PF|t|DSR311|Sharpe|Sortino|Calmar|Ulcer%|Daily DD|
|---|---|---|---|---|---|---|---|---|---|---|---|
|et_raw|3037|66.5|15.29|1.030|0.77|0.017|0.24|0.34|0.07|19.48|71,680|
|et_apex|3148|63.3|1.45|1.003|0.08|0.002|0.03|0.03|0.01|26.04|87,183|
|ct_raw|2760|68.2|60.78|1.125|2.92|0.505|0.96|1.40|0.72|15.05|25,836|
|ct_apex|2856|63.1|32.05|1.078|1.79|0.136|0.58|0.81|0.43|9.59|23,988|
|et_daily_reset_raw|987|66.7|25.41|1.050|0.71|0.014|0.24|0.33|0.12|14.20|22,695|


Design/recent cohorts (entry-date closed-trade statistics):

|Model|Period|n|$/trade|t|Net|
|---|---|---|---|---|---|
|et_raw|2018_22|1463|31.51|1.11|46,095|
|et_raw|2023_plus|1574|0.22|0.01|345|
|et_raw|2025_plus|745|-49.02|-1.19|-36,523|
|et_apex|2018_22|1571|14.95|0.61|23,482|
|et_apex|2023_plus|1577|-12.00|-0.45|-18,931|
|et_apex|2025_plus|745|-63.23|-1.58|-47,108|
|ct_raw|2018_22|1307|43.36|1.44|56,677|
|ct_raw|2023_plus|1453|76.44|2.66|111,064|
|ct_raw|2025_plus|690|93.86|2.22|64,764|
|ct_apex|2018_22|1401|21.33|0.89|29,880|
|ct_apex|2023_plus|1455|42.38|1.60|61,663|
|ct_apex|2025_plus|688|51.93|1.33|35,730|
|et_daily_reset_raw|2018_22|495|42.07|0.86|20,827|
|et_daily_reset_raw|2023_plus|492|8.64|0.17|4,253|
|et_daily_reset_raw|2025_plus|208|-33.00|-0.41|-6,863|


CT raw had one position open at the design split; its later exit belongs to the full entry cohort but was not
known in the original design run. `staged_design_closed_trade_stats.csv` preserves the1306 closed+1open stage;
the combined entry-cohort table has1307 design entries. Daily MTM splits strictly by calendar without future prices.

Annual net per NQ by trade entry year (same costs; 2026 partial):

|Year|et_raw|et_apex|ct_raw|ct_apex|et_daily_reset_raw|
|---|---|---|---|---|---|
|2018|-13,116|-6,034|-10,501|-5,519|-20,441|
|2019|19,376|11,238|2,276|4,263|12,212|
|2020|6,716|-7,143|25,713|4,404|10,095|
|2021|36,283|21,995|29,568|17,285|21,766|
|2022|-3,165|3,425|9,621|9,446|-2,804|
|2023|40,630|38,774|23,174|21,473|7,696|
|2024|-3,762|-10,597|23,126|4,460|3,420|
|2025|-42,529|-52,715|17,425|-5,784|-2,002|
|2026|6,006|5,607|47,339|41,514|-4,862|


2023+20-day-block95% intervals for total marked net,5,000 resamples:

|Model|Actual|95% interval|
|---|---|---|
|et_raw|345|[-92,259, 89,593]|
|et_apex|-18,931|[-106,031, 65,818]|
|ct_raw|112,679|[29,947, 192,425]|
|ct_apex|61,663|[-14,097, 138,254]|
|et_daily_reset_raw|4,253|[-39,679, 49,066]|


CT raw's recent edge is more credible than ET's; it still fails the required full t/DSR gate. Its Apex adaptation
has recent t<2 as well. Higher fees do not repair either failure. This is not a claim that every source interpretation loses.
Full 2018–24, exact author OOS dates, years, fee stresses, daily/trade t and all metrics are in `diagnostics/standard_stats.csv`.

## Placebos and standalone risk

1,000 random-side and1,000 random-time draws per main model. Side draws condition on actual source entry events and
skip overlaps after re-executed exits; they are falsifiers, not an executable alternative. Time controls plan one
long decision/day using an independent coverage calendar, skip missing decision/open quotes, and never condition on
whether the actual strategy later trades. Source max3/day versus control max1/day differs; compare both total and expectancy.
Recent results below use same-calendar actual entries for time controls, all source events for side controls.

|Model|Null|Actual $/trade|Null median $/trade|p(total)|p(expectancy)|
|---|---|---|---|---|---|
|et_raw|random_side|0.22|-51.87|0.033|0.033|
|et_raw|random_time|0.22|1.99|0.525|0.526|
|et_apex|random_side|-12.00|-46.73|0.103|0.093|
|et_apex|random_time|-12.00|-8.32|0.640|0.543|
|ct_raw|random_side|76.44|-19.09|0.001|0.001|
|ct_raw|random_time|74.97|20.14|0.006|0.044|
|ct_apex|random_side|42.38|-19.96|0.005|0.012|
|ct_apex|random_time|40.85|-5.67|0.010|0.042|


CT nominal control passes are favorable evidence, not a bypass around multiple testing/source uncertainty. ET time
controls do not support timing value. Null DD is chronological closed-trade equity; main risk/account tables use
MTM/minute paths. Terminal unclosed/unpriced/unknown-held events are counted separately, not forced into fake exits.
Fixed-long null walkers reproduce every main source event's exit exactly. Standalone daily/trade Monte Carlo at 1/2 MNQ
is saved in `diagnostics/standalone_mc.csv`; its EOD trailing approximation is not the funded-account risk model.

## Evaluation: both sizes, additions and replacements

Real 21-session windows, with the whole window inside its cohort; unknown-day windows are excluded without compressing
the calendar.50K retains pass-first and 150K breach-first same-minute tie conventions. Correct 150K risk scaling floors
after scaling dollar risk; no fractional-contract shortcut. Full-cohort primary-fee results:

|Account|Allocation|Pass%|Fail%|Median pass days|
|---|---|---|---|---|
|50K_evaluation|BASE|51.02|47.15|6.0|
|50K_evaluation|EMPTY_VB|43.32|38.82|10.0|
|50K_evaluation|et_apex__ADD1|50.24|48.77|6.0|
|50K_evaluation|et_apex__ADD2|49.14|50.39|6.0|
|50K_evaluation|et_apex__REPLACE_VB2|43.53|47.93|9.0|
|50K_evaluation|ct_apex__ADD1|50.13|48.72|6.0|
|50K_evaluation|ct_apex__ADD2|48.56|50.39|6.0|
|50K_evaluation|ct_apex__REPLACE_VB2|45.36|45.68|9.0|
|150K_evaluation|BASE|42.59|55.42|8.0|
|150K_evaluation|EMPTY_VB|31.12|50.18|12.0|
|150K_evaluation|et_apex__ADD1|41.85|56.16|8.0|
|150K_evaluation|et_apex__ADD2|40.39|57.73|7.0|
|150K_evaluation|et_apex__ADD4|37.45|61.34|7.0|
|150K_evaluation|et_apex__REPLACE_VB2|31.01|50.60|11.0|
|150K_evaluation|ct_apex__ADD1|42.27|55.53|8.0|
|150K_evaluation|ct_apex__ADD2|39.92|57.88|7.0|
|150K_evaluation|ct_apex__ADD4|38.08|60.19|7.0|
|150K_evaluation|ct_apex__REPLACE_VB2|31.90|49.66|11.0|


Every full-cohort addition lowers pass rate at both sizes/clocks. No replacement beats BASE. Empty-slot comparisons,
all five cohorts, fee1.24 and chronological-block intervals remain in `accounts/evaluation_*`.

## Funded: joint minute risk, not end-of-day standalone profit

1,000 paired circular 20-day histories, seeds1..4; 250/500-day horizons. Counts undergo the same cushion sizing and integer
floor as the plan. Both clocks/allocations share 2,242/2,262 complete days. Internal 100 synthetic + 360 production records
match the original state machines on all five outputs. Full-cohort primary-fee results:

|Account|Allocation|1y payout mean|2y mean|2y p5–p95|Blown%|Median days to 6|
|---|---|---|---|---|---|---|
|50K_funded|BASE|9,058|11,968|0–13,000|7.9|267.0|
|50K_funded|EMPTY_VB|7,895|12,021|1,500–13,000|6.1|304.0|
|50K_funded|et_apex__ADD1|8,458|11,546|0–13,000|11.0|280.0|
|50K_funded|et_apex__ADD2|6,168|7,868|0–13,000|42.3|388.0|
|50K_funded|et_apex__REPLACE_VB2|5,555|7,752|0–13,000|42.0|434.0|
|50K_funded|ct_apex__ADD1|8,698|11,494|0–13,000|11.8|273.5|
|50K_funded|ct_apex__ADD2|6,960|8,552|0–13,000|35.8|311.0|
|50K_funded|ct_apex__REPLACE_VB2|7,044|9,410|0–13,000|29.1|319.5|
|150K_funded|BASE|16,410|19,946|20,500–20,500|2.7|233.0|
|150K_funded|EMPTY_VB|15,428|20,180|20,500–20,500|1.0|256.0|
|150K_funded|et_apex__ADD1|16,082|20,071|20,500–20,500|2.0|240.0|
|150K_funded|et_apex__ADD2|14,962|18,875|0–20,500|8.1|252.0|
|150K_funded|et_apex__ADD4|11,617|14,519|0–20,500|30.3|304.5|
|150K_funded|et_apex__REPLACE_VB2|14,464|19,404|8,350–20,500|5.0|269.5|
|150K_funded|ct_apex__ADD1|16,332|19,894|20,500–20,500|3.0|235.5|
|150K_funded|ct_apex__ADD2|16,025|19,355|2,500–20,500|5.8|232.0|
|150K_funded|ct_apex__ADD4|13,198|15,720|0–20,500|24.4|259.0|
|150K_funded|ct_apex__REPLACE_VB2|15,762|19,876|20,500–20,500|2.8|247.0|


Recent 2023+ ADD1 paired effects versus BASE,95% MC sampling intervals conditional on observed history:

|Account|Allocation|2y payout change|95% interval|
|---|---|---|---|
|50K_funded|et_apex__ADD1|-384.0|[-574.0, -195.0]|
|50K_funded|ct_apex__ADD1|-386.5|[-569.0, -213.0]|
|150K_funded|et_apex__ADD1|-94.0|[-288.5, 94.0]|
|150K_funded|ct_apex__ADD1|1.0|[-172.5, 170.0]|


The favorable-looking150K CT replacement 2025+ is mixed:1y beats BASE and EMPTY, but2y fails to beat EMPTY reliably.
Full paired results below expose that empty-slot control rather than crediting removal of VB to the candidate:

|Reference|Metric|Change|95% interval|
|---|---|---|---|
|BASE|year1|301.5|[7.0, 599.0]|
|BASE|year2|681.5|[361.0, 1,009.0]|
|BASE|blown|-0.034|[-0.051, -0.017]|
|EMPTY_VB|year1|376.0|[116.0, 630.5]|
|EMPTY_VB|year2|-126.0|[-382.0, 126.5]|
|EMPTY_VB|blown|0.008|[-0.005, 0.021]|


Fee1.24 full-cohort ADD1 effects versus BASE (same stress on both sides):

|Account|Allocation|2y payout change|95% interval|
|---|---|---|---|
|50K_funded|et_apex__ADD1|-446.5|[-655.5, -249.0]|
|50K_funded|ct_apex__ADD1|-362.5|[-555.5, -174.0]|
|150K_funded|et_apex__ADD1|38.5|[-83.0, 166.0]|
|150K_funded|ct_apex__ADD1|2.0|[-149.0, 154.0]|


The 5–95% quantiles use all histories; outcomes below p5, including zero payout, remain possible. Median time to 6 treats incomplete histories as infinity. MC mean intervals
describe simulation precision, not certainty about future markets. Multiple account/allocation comparisons are descriptive;
they are not independent confirmations of an edge. All 180 funded and180 evaluation rows remain saved, including failures.

## Personal: complete 14-piece plan and A/B/C/D ladder

Published baseline, raw carry retained,16:00 CT daily MTM; no Apex drawdown/payout rules. 5,000 paired252day L20 histories,
seed1, full and2025+ cohorts.21 configurations per clock include1/2 MNQ adds and VB-empty/replacement where present.
Full-cohort ADD1 effects below; equal-DD figures are continuous research risk budgets, not executable contract counts.

|Model|Plan|Median profit Δ|DDp95 Δ|Equal-DD median profit Δ|Historical annual mean95%CI|
|---|---|---|---|---|---|
|et_raw|A|431|1,275|-2,654|[-1,006, 1,788]|
|et_raw|B|471|1,177|-2,679|[-1,006, 1,788]|
|et_raw|C|418|1,190|-2,897|[-1,006, 1,788]|
|et_raw|D|436|748|-1,894|[-1,006, 1,788]|
|et_raw|FULL|602|510|-1,647|[-1,006, 1,788]|
|ct_raw|A|1,738|731|-666|[570, 2,951]|
|ct_raw|B|1,774|683|-665|[570, 2,951]|
|ct_raw|C|1,735|711|-797|[570, 2,951]|
|ct_raw|D|1,796|480|71|[570, 2,951]|
|ct_raw|FULL|1,800|359|94|[570, 2,951]|


Full personal portfolio primary MC levels (per MNQ costs$1.275):

|Model|Allocation|Median profit|DDp95|Capital at20%DD|Median profit/DDp95|
|---|---|---|---|---|---|
|et_raw|FULL__BASE|23,698|5,001|25,004|4.739|
|et_raw|FULL__ADD_1|24,300|5,511|27,554|4.410|
|et_raw|FULL__ADD_2|24,733|6,665|33,324|3.711|
|et_raw|FULL__EMPTY_VB|21,943|4,522|22,608|4.853|
|et_raw|FULL__REPLACE_VB_1|22,493|5,005|25,027|4.494|
|ct_raw|FULL__BASE|23,698|5,001|25,004|4.739|
|ct_raw|FULL__ADD_1|25,498|5,359|26,796|4.758|
|ct_raw|FULL__ADD_2|27,346|6,316|31,579|4.330|
|ct_raw|FULL__EMPTY_VB|21,943|4,522|22,608|4.853|
|ct_raw|FULL__REPLACE_VB_1|23,742|4,883|24,414|4.863|


CT personal has a plausible incremental return; do not call it an unequivocal portfolio failure. Its full-plan
ADD1 equal-DD gain is small. Its historical annual mean effect is positive (95% block interval$570–$2951), while
source significance still fails the mandatory multiple-test/DSR promotion gate. Replacing VB is nearly flat versus BASE and adds little risk-adjusted value versus EMPTY.
The ET version worsens risk efficiency. All 42 allocations across both clocks,2025+ cases, paired downside and historical
intervals are saved under `personal/`; no clock/size was selected afterward for promotion.

## Overlap, data and execution limitations

- No exogenous forced flow is identified: this remains a price-based breakout hypothesis. Daily correlation is not a hedge.
- Source ET raw has 2,289/3,037 already-crossed signal-stop entries,312 cross-date trades and 326 trades with unknown held
  quote gaps. CT has 2,093/2,760,441 and 440 respectively. Neither version has a final open trade. Already-crossed buy-stop
  acceptance/conversion needs platform validation; this replay assumes an opening fill as frozen before returns.
- The Apex shared universe omits 20 dates, including several March2020 stress sessions. Saved date lists make that
  selection visible; account estimates are conditional on the covered universe and cannot certify omitted-day risk.
- Before 2021-06-28,15:16–15:30 close-stamped minutes correspond to a documented exchange pause. They are stale-marked,
  not filled; post-change missing minutes are not presumed closed. The dated [CME notice](https://www.cmegroup.com/notices/electronic-trading/2021/06/20210621.html)
  governs this boundary, rather than a generic stale FAQ. No synthetic regression bars were added.
- Inherited baseline pause handling can substitute entry price in Monday 19 pauses/Bridge 63 pauses; preserved cache
  convention is disclosed. It affects early history, not2023+/2025+. The small prior50K published-baseline mismatch
  also remains; candidate effects use a matched frozen baseline, not a claim of exact published payout parity.
- Personal baseline day-based fee adjustments undercount some VB reentries, MOC has a lower inherited fee, and Twin
  uses the published v1 ledger. Personal daily DD omits intraday margin/liquidation exposure.
- Ulcer% uses the repository metrics' $50,000 reporting-capital convention; it is not an account-sizing recommendation.
- `minute_occupancy.csv`, `VB_low_timing.csv`, `overlap_daily.csv` and personal joint-loss files expose simultaneous
  NQ exposure and loss timing. Full-size occupancy is an upper-bound description before cushion reductions; winning
  closes after a VB low are not assumed to rescue a previously breached account. Joint minute account paths govern risk.
- All five models share unverified full-session history and roll conventions; an RTH-only or original-code implementation
  might differ. Such a change would require a new preregistration/trial, not a retroactive explanation that validates these results.

## PDF reconciliation and independent review

The author reports 2,518trades/$265780, including2017 unavailable here; exact platform/settings/cost parity is unverified.
For2025-01-15 through2026-08-31, the PDF reports 564trades/$88675; costed ET raw has685/−$32889 and CT raw 635/$67711
at fee1.04. Different counts/timezone/fills prevent claiming an exact replication. The PDF's$190300.45 adjusted profit
matches a win/loss-count statistical adjustment, not a verified commission/slippage deduction. Its seven residual trades
reflect nonmatching displayed date partitions, not automatically an arithmetic error. See `r2vault_source_audit.md`.

Independent adapter reviews are `r2vault_personal_review.md`, `r2vault_personal_checker.md`, `r2vault_accounts_review.md`
and `r2vault_diagnostics_review.md`. Review independence is scoped: different agents checked source, adapters and saved arithmetic; the replay
author checked others' adapters. This is not a fresh blind Claude/strategy-checker PASS or MultiCharts confirmation.

The Python build is the research deliverable. No PowerLanguage/live strategy was added because the validation gates
failed. No parameter rescue, forward-log entry, live-plan change, VPS/broker/API action or PR2 action was taken.

## Reproduce and hand off

Use the configured scientific Python environment, existing ignored caches and pinned baseline snapshots. In this
Windows checkout the bundled Python plus `agents/codex/runtime/or_pullback_python` supplies the dependencies.
From the repository root with `analysis` and that dependency directory on PYTHONPATH:

```text
python -c "from codex_r2vault_replay import run_cached; run_cached()"
python analysis/codex_r2vault_personal.py
python analysis/codex_r2vault_accounts.py --prereg a973f0779b6e10d9c3c29adc6748ed5eba0d5f92
python analysis/codex_r2vault_diagnostics.py --phase all
python analysis/codex_r2vault_personal_check.py
python analysis/codex_r2vault_accounts_check.py
python analysis/codex_r2vault_diagnostics_check.py
python analysis/codex_r2vault_report.py
```

Input/ledger/script hashes, sample definitions, gap calendars, fixed histories and all trial models are in the component
manifests. Do not rebuild market caches just to rerun this report assembler. Claude handoff: review/rank
`agents/codex/results/r2vault.md`; no current-plan promotion is supported.
