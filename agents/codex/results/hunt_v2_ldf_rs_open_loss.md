# H07 LDF after a losing same-side RS position: CLOSE at support gate

Summary: the frozen interaction is too rare and cannot support its required price-matched comparison. Of485 design LDF decisions, it removes only **6 versus20 required**; conditional nullA has only **4 distinct masks versus1,000 required**. Close H07 before inspecting any gross or stopped outcome. This is a support failure, not evidence that its omitted tickets lose or win.

Plan: `agents/codex/plans/hunt_v2_ldf_rs_open_loss.md`, original preregistration **4c3612104c10f5e5eeb96e53d8cde6bc2a3f2b3d**. Evidence: `agents/codex/evidence/hunt_v2_ldf_rs_open_loss.md`. SOURCE implementation7a9832725f1011ad554bd4da0efa92ca06ef70b2; feature implementation **ce88a74ca84c7fba74dd6f163df148743c5aa014**. Actual output: `analysis/outputs/codex_hunt_v2_ldf_rs_open_loss/`. **Running count:5/60 economic evaluations,7/10 registered hypotheses,4 gross screens, plus archived65t6. H07 adds0 gross and0 economic evaluations.** Retain all source-only exclusions and old selection history; do not restart t6 or pause the hunt for this failure.

## Mechanism and four frozen definitions

The participant is this finite-risk book, not an invented compulsory outside trader. Adding NQ delta while an earlier same-side RS ticket remains underwater might concentrate failing exposure. A late flow could instead rescue it. Qualification therefore required omitted LDF tickets to lose net money and the executable allocation to beat BASE, EMPTY and matched parent implementation controls, rather than merely reduce activity.

Use unchanged canonical5-minute LDF,1MNQ, one consumed decision/date. Its parent uses cash OPEN511, completed C84014:00 decision, absolute daymove>=0.40prior15stored-date ATR, next OPEN841 at wall14:00,0.25ATR stop rounded up0.25point, active entry-bar protection, worse gap fills, no target and C87014:30 time exit. Omission frees no new trade/capacity and alters no RS entry/stop/exit. Target-through is inapplicable without a target.

Four definitions: BASE; sole primary RS_OPEN_LOSS (omit iff a strictly earlier same-side owned RS position is still open and RSside*(C840−recordedRSentry)<0); unselectable SAME_SIDE_OPEN without mark condition; and independent PRICE_0901 (omit iff LDFside*(C840−O541)<0 on every parent event regardless of RS). Unknown/zero retains the primary. Exact basis is MC entry==nativeO541 within1e-8point; no offset, nearby-minute, side or loss-threshold search. On admitted same-side-open states, the primary is exactly overlap×adverse-price sign. Both components and prior cap/agreement/DD/filter ancestry remain selection history.

The gross-versus-cost gate was frozen at$4.48/MNQ, twice$1.24RT commission plus$0.50per market/stop fill. **That gross screen was not reached.** Fees are research assumptions, not verified broker quotes or native micro liquidity. The inherited C840→OPEN841 boundary assumes ordinary bar availability without an extra full-minute processing delay; no receipt latency was measured.

## Actual source and feature execution

SOURCE ran2026-10-27T00:34:58.097580Z–00:35:05.345990Z and passed:1,222 selected2018–22 event records/611 complete position pairs, zero structural issues, all485 parent decisions inside the exact declared report bounds. The current one-minute/both-side RS defaults and report identity passed the fixed protocol. Bounds2017-09-12T09:01:00.00000048 to2026-10-20T18:01:00.00000048 are Chicago civil report coverage, not independently authenticated completeness or live receipt.

FEATURES ran **2026-10-27T00:46:01.282343Z–00:46:06.732213Z**. All ten exact H01-bound2018–22 native DAY/ON input hashes were checked before selected C840close/O541open conversion. All970 required native keys were complete/consistent. No broad grid, OF mask, OPEN841/CLOSE870 endpoint or stopped financial value was interpreted, and no parent maker was executed. Bound parent artifacts were read only opaquely for hashes; selected parent metadata remained separate from outcomes. Global malformed-event faults would have stopped the whole source; admitted features consumed only the as-of prefix. Valid later entries/exits and the full-day noncanonical diagnostic cannot alter earlier masks. The single unknown was a source event exactly at840 and was kept.

|Frozen definition|Kept|Removed|
|---|---:|---:|
|BASE|485|0|
|RS_OPEN_LOSS primary|479|6|
|SAME_SIDE_OPEN control|337|148|
|PRICE_0901 control|474|11|

Primary known state484/485=**99.7938%**, above90%. Kept257long/222short; removed4long/2short. Kept100minimum and10each-side minima pass; removed20minimum fails.

|Year|Primary kept|Primary removed|
|---|---:|---:|
|2018|96|1|
|2019|89|0|
|2020|86|3|
|2021|107|1|
|2022|101|1|

Removed observations span4years, passing the3year spread requirement, but that does not replace the20-observation count. NullA matches year/side/fixed-price sign without RS-open state; unknown rows remain fixed kept. It has **4** feasible distinct masks/1variable cell, failing1,000. NullB matches year/side/known-state/same-side-open without price sign; it has **6,800,640** masks/4variable cells and passes feasibility. Neither scheme matches both components jointly. These are exact combinatorial support counts, **not sampled return paths or placebo p-values**. Do not merge cells, relax counts, change seeds or test only the favorable comparison.

## Reproducible bindings and review

The named RS workbook SHA256 is `6cc3bedab9b44a0598339c177eaa2933bf0c0e01de29af1fe3a6b4f1ade69977`. Metadata helper SHA `1b85ccfcbccb62ece192fb8c7d04049440b1242f0e09ae7c4c23edf4c3e7815f`; SOURCE producer `ccd3e4e2e92c8a6f12138192a518178924e16e708857759722a60809803f8d77`; FEATURES producer **ba2690140079a59dd9bcf5282a3b53319cb76336645d72cb819808d8837a7fc2**. Original rules and pre-data source clarifications were committed before actual values. Date/Time fractions and declared two-row Trade# merges are retained, not guessed from returns.

SOURCE marker SHA **35034d3e71e4c183d6267c23bd3f9904f1d4c80d18019ebde3d469586fb0882a**; failed FEATURES marker SHA **62a01ed1d4075b1a8ad2c50cd105217e590bcc3e5cb5bac2dc7b0413fc696571**. Saved hashes bind features.csv/JSON, all144 count rows, native mark/source references, both null-support cell inventories, stage attempts and input bindings. Reviews: `reviews/hunt_v2_ldf_rs_preexecution.md`, `reviews/hunt_v2_ldf_rs_features_preexecution.md`, and saved-result audit `reviews/hunt_v2_ldf_rs_result_audit.md`. These source/synthetic/artifact checks are not raw-spec promotion approval.

## What was not run and why

The frozen support failure stops H07 before raw gross, four protected economic definitions, base/kept/removed profits or t, all five net metrics, Newey-West, sampled1,000-mask return tests, plan-size Monte Carlo, BASE/ADD/REPLACE/EMPTY books,2023+ historical validation, full-history promotion, random-time/random-side placebos and fresh raw-spec checker. None is inferred from input marks/counts. No funded/evaluation pass/payout claim, PowerLanguage draft or trading approval exists. A prospective financial adapter was retained as **NOT RUN/unreviewed** engineering source; its six invented fixture groups are not economic evaluations, and failed support cannot authorize it.

Only2018–22 feature values were used; future-year RS Time/Price/quantity, exit Price, realized P&L, MAE/MFE and nonallowlisted Settings were not interpreted. Existing H01 calendar/ATR/native audits were bound rather than rerun; normal parent sessions exclude known half-days/holidays and retain14:30 maximum parent exits, before15:59CT. No new protected strategy or Apex account path was executed.

The owned MC-book stream still depends on report completeness and current-path assumptions, not verified live fills or corrected raw-spec RS. Correcting RS entry-bar protection could change open-state paths and must be separated from filter alpha. Native feed/micro liquidity, receipts, fees/reentries and baseline marks remain limits; none is silently cleared. H01's rejected OF filter and H04's failed reference study remain closed. No different pair, source version, quantity, window or price-sign gate may rescue this family.

**Verdict: CLOSE H07 for insufficient interaction support and an infeasible required conditional null; no measured return conclusion. Continue only a distinct credible v2 question within the remaining budget.**
