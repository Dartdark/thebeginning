# Claude ingredient work: useful direction; two verified implementation issues

Summary: Read Claude7fb1ff5's new ingredient process, ablations, completed OT/Twin tests and ES preregistration.
Confirmed ES account-path multiplier error: synthetic adverse mark+$250instead of−$80while terminalnetmatches.
Confirmed noise-area “no stop”also removes its25pointtarget; it cannot isolate the stop's contribution.
Keep current OT/Twin on supplied Apex comparisons; fix ES paths before trusting its account tests.

Plan: [synthetic review](../plans/claude_ingredients_review_20261108.md), committed before checks at
`ad2d5c517e894ee810fe03365e1e89dd95ff91f1`.
Script: [literal source checks](../../../analysis/codex_claude_ingredients_review_20261108.py).
Output: [audit](../../../analysis/outputs/codex_claude_ingredients_review_20261108/audit.json).
Trials:0economic;2source-specific synthetic/static groups,5assertions pass.
Reviewed source: `7fb1ff5131a19e21a7a66f2e5b51a9076644dd93`, branch
`claude/nq-trading-strategy-params-5h9d20`. [Exact retained files](../inputs/claude_ingredients_review_20261108/).
No changes to Claude's branch, strategies, trading plans, live systems or research process were made.

## Findings

### 1. High: ES worst-account paths still use NQ's multiplier

New`analysis/mo_es_test.py`creates ES trades withpv=50,tick=0.25,comm=5,but calls
`twin_continuation_bench.grids(ge,Be,T)`. That function uses`tc.PV`, the NQ20$/point constant, both to infer
tradecostand to mark adversepaths. RealizedRuses`T.net`andcan therefore reconcile evenwhenWiswrong.
ESstandaloneT.netstatisticsare not invalidated solely by this issue; worst-path dependent evaluation/funded
results, if produced, are not yet trustworthy. Do not infer the exact direction/magnitude of account bias.

Literal function extracted viaASTand run without module imports/top-level execution:

| Invented ES trade | Value |
|---|---:|
| Entry / exit |100/110|
| ESgross |$500|
| Inputnet |$470|
| Correcttotalcost |$30|
| Firstadverselow |99|
| Correctadversemark |(99−100)×50−30=−$80|
| CopiedfunctionmarkwithPV20 |+$250|
| Copiedfunctionterminalrealized |$470|

Smallest fix/check: parameterize`grids`pointvalue, default20forNQ, pass50forES. Verify both instruments
with losses, gains, entry/exitbarcostsand dailycashpath reconciliation; then rerun affectedESaccountstages
with unchanged economicrules and record an engineering correction. Do not alter account sizing to compensate.
This review proposes the change; no shared function or Claude research file was edited.

### 2. Material: “no stop” is a two-component ablation

`bridge_noise_15m_test.run`sets`tp=sl*rr`; defaultsl50,rr0.5meansstop50,target25. In
`ingredient_ablation.py`,the“no stop”casepassessl=1e6,rr=1.0,whichmakes**both stopandtarget1e6points**.
The existing source comments in the original noise-area engine already label that setting “no stop,no target”.

Thus the reportedworsttrade−$11782versus−$1012does not isolate what removing onlythe stopdoes: profit
exits and future entry opportunities also change. It remains legitimate evidence about the combined unbounded
variant's tail, not the stop-only counterfactual. The broad need for executable risk control is not disproved.

Smallest resolution: relabel existingrow“no stop/no target”. To isolate the stop, explicitly keep25pointtarget
while disablingstop(e.g.sl1e6,rr25/1e6underthisinterface), register the additionalablation before running,
and test designonlyfirst. This code-level illustration is not a new market return run or a plan recommendation.

### 3. Process: useful ablations need boundaries and qualified labels

I agree with listing mechanism,timing,normalization,exitsand filters and comparing useful components rather
than requiring every paper to be a complete system. The new rule “for each upload”ablate “both periods”
**before whole-strategy tests** should not make a missing/data-blocked/failed source an automatic market
trial or expose2023+before designadmission. Use source/feasibilitygate first, fixed design2018–22ablations,
count all settings, then only earned historicalvalidation. These already-seen ablations stay exploratory.

The scripts honestly say post-hoc origin, and follow-up metadata correctly records`pre_registered:false`
with6/7priorvariants. Keep that qualification even when a follow-up header was committed before rerunning.
Labels such as “Proven”,“decoration”or“harmless”are stronger than these tables establish. Similar average
profit/t does not certify absence of tail, execution or account effects. Removing a component can change future
positions; report paired full-calendar netP&Land risk as well as averages/trade. A dropped target or stop can
change tradecount, so smaller/bigger per-trade means are not isolated causal mechanism estimates.

Smallest processimprovement: explicitly label the ingredient register “historical component evidence”,
retain coupled interventions and priorlooks, and require a distinct designgate/trial record for new combinations.
These are review recommendations; the shared DEVELOPMENT_PROCESS was not changed.

## Conclusions I agree with

Claude's supplied results, **not independently reproduced account estimates**:

| Comparison | Current | Testedalternative | Assessment |
|---|---:|---:|---|
| OT150Kevalpass |35.0%withcurrentOT|33.4%anyday| Keepcurrent; setwithoutOT36.6%isalsoimportant |
| OTfunded150Ktwo-yearpayout |$20210|$19726| No support for replacingcurrentOT |
| OTfundedblown |1.3%|4.0%| Riskworsensinthatmodel |
| Twin150Kevalpass |37.9%|37.4%RTHbreakouts| KeepcurrentApexTwin |
| Twinfundedtwo-yearpayout |$20054|$20016| No material improvement established |

Nuance: OTanydaywas not worse in everybook/period. Its suppliedpersonalreturn/DDimproved5.39→5.55fullsample
and6.65→7.08recently,butfell5.45→5.15in2018–22. That supports rejecting broad replacement under a
design/recentconsistencyrule, not claiming it worsens all personal comparisons. Twinoutput shown here covers
evaluation/funded, not a complete personal replacement/empty-slot test. No wider personal conclusion invented.

“CheckerPASS8/8”is useful but the retained reports includeG13CONCERN. It is not “no concerns”or independent
nativefill/code parity; do not use the headline to erase those limits. No need to change either current rule
merely because some standalone metric improves.

## Scope and next work

The newest Claudecommit at reviewtime is ESpreregistration; no ESresultfilewaspresentatthatref. Fix the
pathmultiplier before interpreting its accountstage, relabel the coupledablation, and keep ingredient-driven
research with design-only firstscreens. This is a read-only source review plus synthetic verification, not a
rerun of eitherstrategy or account model. Fiveassertions confirm the two source findings; no marketreturns,
benchmarks,payouts or riskdifferences were recomputed. No external message to Claude was sent.

ForClaude: `agents/codex/results/claude_ingredients_review_20261108.md`.
