# VB covariance extra lot: CLOSED before features; saved book omits a normal date

Summary: The frozen own-book variance rule was not evaluated because its input calendar failed. The current saved personal19 daily baseline omits normal cash date2020-11-30. No covariance mask, active-day count, price screen, protected strategy or book gain was computed. H10 closes unchanged and exhausts the10-hypothesis budget.

Plan: [H10 preregistration](../plans/hunt_v2_vb_covariance.md), commit `f7d70c64b5a55da9afeb216996081711102ae623`. Reviewed implementation commit `98d5fd54bb4bd38511dbbe113a26040e4e1d97dc`; script `analysis/codex_hunt_v2_vb_cov_features.py` SHA256 `6a08bd063da1251c3921c1cedf8fbae39ccf4d92338661ff94ae012c4d6b6952`.

Running final budget: **5/60 economic model evaluations,10/10 registered hypotheses,4 gross screens**, in addition to archived65t6(63unique). H10 adds1hypothesis,0gross,0economic evaluations. Pause reason is the exhausted hypothesis budget. Source rejection is not an economic loss or proof the covariance family has no edge.

## Rule and economic question as preregistered

Keep the accepted plain Vault Break1MNQ slot. Before the first30-minute C1000CT decision, take the previous252 completed joint published personal19 daily rows. X is the same book's one-MNQ `VaultBreak` column; B is all19 columns INCLUDING X. Add exactly1MNQ for that date only if `2Cov(B,X)+Var(X)<0` andVar(X)>0; otherwise keepq1. The shadowBASE remains fixed, never pastPOLICY feedback. Strict zero boundary and exact stored-decimal rational arithmetic; no parent/window/buffer/budget/roster search.

The underlying parent is long-only NQ,30-minute chart: above first-observed-chart-open+.30prior15weekday-chart-dateATR and chart VWAP; next native OPEN; active75point stop,40point target with1point trade-through, max3protected tickets/date; exact14:30flat/early11:30flat, before15:59CT. Native cost plan perMNQ:2USD/point,.25tick=.50USD,1.24RTcommission,one adverse market/stop tick per fill:2.24market/stopRT or1.74targetRT. Gross hurdle4.48. Four-tick stress5.24marketRT/3.24targetRT. **None was applied to new returns here.**

This was a distinct book-risk constraint, not a new directional alpha or outside forced-order claim. WithB already containingX, it needs covariance with the rest of the book below−1.5Var(X); low correlation alone does not suffice. The identity describes a historical proxy forecast, not guaranteed realized risk reduction. The sole candidate would have been the incremental EXTRA; its qualification could not borrow parent/POLICY statistics. Conditional published-book timing, exact-native replay differences and full old selection were disclosed before data.

## Actual execution and decisive gate

Started2026-10-27T04:41:51.924394+00:00; completed2026-10-27T04:41:52.449520+00:00. Both canonicalUNIFORM andSUNDAY2 saved personal19 baselines matched the preregistered SHA256 `d724c7d02b6db71e63ba705079dbea7fefaa42c6b4f436308a28993ca1908803` before headers. Only2018–22 P&L cells were interpreted for source validity; dates outside design were inspected as metadata and skipped BEFORE financial conversion. There was no new candidate profit/t/account path calculation.

|Source check|Measured result|
|---|---:|
|Exact roster|date +19 fixed columns|
|Design rows2018-01-02..2022-12-30|1,289|
|Finite complete design rows / unknown numeric rows|1,289 /0|
|Full2018–22 calendar dates checked|1,826|
|Required normal/early cash dates|1,259|
|Required dates missing|**1:2020-11-30**|
|Additional actual holiday book rows retained|31|
|Excluded2023+ date-metadata rows|973|
|2023+ numeric financial cells converted|0|
|Covariance masks/active counts / raw-price or strategy paths|**NOT RUN**|

The minimum calendar gate failed before `compute_features`. There is no `feature_rows.json` or `feature_counts.csv`. Active days are **unknown, not zero**. The50-day/three-year feature support gate,100/50native proposal support,1,000matched masks and all raw/economic stages were not evaluated. No missing date was deleted, inserted as zero, filled from another case or treated as a no-trade day.

The calendar source classifies2020-11-30 as NORMAL. Its absence is a source gap in this retained book proxy. Independently, [H09's earlier source review](../reviews/hunt_v2_mes_source_admission.md) already found that the ES2020file on this same date contains evening keys only and no C1400/C1450 references. H10 did not reread ES/NQ prices or rerun that audit. The relationship does not prove that every underlying leg has no data, nor does it quantify the omitted day's P&L.

The [independent actual-source review](../reviews/hunt_v2_vb_covariance_source_result.md) and [machine decision](../reviews/hunt_v2_vb_covariance_source_result.json) verify the retained evidence and focused date-only check. Integrity-review PASS is separate from hypothesis/source FAIL; no raw outcome is authorized.

## Economic results, placebos and account disposition

|Period / side|New candidate metrics|
|---|---|
|2018–22 design; long/short/year|Not run: no signal/trade universe or mask computed|
|2023+ previously seen historical validation|Not run; no numeric financial values inspected|
|Full2018–26|Not run|
|Gross/net trade t,dailyNW5,DSR|Not computed|
|Winrate,Sharpe,Sortino,PF,Calmar,Ulcer,maxDD|Not computed|
|Matched allocations/random-side/random-time/dependence|Not run|
|BASE/ADD/REPLACE/EMPTY,personalMC,funded/evaluations|Not run|

No five-definition stopped study, reentry simulation, native-fee stress, selected2023+ run, fresh financial raw-spec checker, PowerLanguage draft or trading/deployment action followed. Predata synthetic review PASS concerns software/math only. Pre-MNQlisting NQ-price/MNQ-cost history would have been counterfactual; no historical micro-fill claim is made.

## What the source finding changes

The input is the same retained personal19 case used in H05's already-rejected nominal book comparison. It cannot be presented as a complete normal-date history. The missing day adds an explicit calendar limitation to earlier published-proxy comparisons; it does not establish the sign of a correction, a pass-rate/payout change, or a reversal of H05's frozen rejection. Existing metrics/artifacts remain unchanged. No shared allocation/ranking was edited.

Other limits remain: per-active-day fee corrections can undercount reentries; Twin is markedv1 rather than exactv2.1; Kusho is exit-booked; MOC/S30 retain approximations; OTcoverage ends2026-07-07. The prior-row completion convention is conditional published-shadow-book timing, not actual account receipt/native equity certification. The feature source, parent and roster have selected historical ancestry.

A useful future source repair would require original full NQ/ES sessions for2020-11-30 with exporter/timezone/close-label/contract-roll provenance and a reconciled19-leg row on the same calendar. An omitted row cannot be patched with zero or invented P&L. Repair/qualification was not performed here; any later hypothesis needs a new authorized budget and its own preregistration. The existing6J access question is optional future input, not permission for an11th test.

## Reproduction and immutable evidence

Actual command, retained for provenance (do not repeat the failed attempt):

```text
/workspace/venvs/thebeginning/bin/python -B analysis/codex_hunt_v2_vb_cov_features.py --features --prereg f7d70c64b5a55da9afeb216996081711102ae623
```

- [Execution marker](../../../analysis/outputs/codex_hunt_v2_vb_covariance/feature_verified_execution.json), SHA256 `a2dfc238c3cbac421e17df18320edb8fb2657ee78d0dbc077ccd09a6c8f75556`.
- [Gate](../../../analysis/outputs/codex_hunt_v2_vb_covariance/feature_gate.json), SHA256 `e18c0820437b2a1085b4c428be79523d6c32de2e7b5353517dc042c716c0f5a2`.
- [Input/code bindings](../../../analysis/outputs/codex_hunt_v2_vb_covariance/feature_input_binding.json), [pre-value binding](../../../analysis/outputs/codex_hunt_v2_vb_covariance/feature_pre_value_binding.json).
- [Source audit](../../../analysis/outputs/codex_hunt_v2_vb_covariance/feature_source_audit.json), [full calendar audit](../../../analysis/outputs/codex_hunt_v2_vb_covariance/feature_calendar_audit.json).
- [Mechanism](../research/hunt_v2_independent_book_constraint_gate.md), [math/prereg review](../reviews/hunt_v2_vb_covariance_predata.md), [implementation review](../reviews/hunt_v2_vb_cov_features_predata.md).

**Verdict: CLOSED at source calendar gate before covariance, raw returns or economic testing. Final program summary and budget pause are required; no rule/source/window rescue or11th hypothesis.**
