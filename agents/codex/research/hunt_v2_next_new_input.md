# Next owned-input question: classified support for an RS order

Decision: **a small RS-specific filter question is eligible for a separate TEST preregistration**.
It is not a new standalone forced-flow discovery. The new information is classified NQ tape at an
already adopted Relative Strength decision, conditional on the parent's cross-market price signal.
The same broad input family has substantial prior selection; there is no measured edge here.

Source-only review,2026-10-26: read AGENTS.md, BUILDER_BRIEF.md, LESSONS.md, RESEARCH_CONTROLS.md,
TASK_strategy_hunt_v2.md and progress. Latest adopted/ranking pin inspected read-only is **7f0800f**.
Read the existing hunt flow/confirmation/source gates before this nomination; none was rerun or reopened.
No raw price, OF, COT position, CSV/trade-list body, workbook or return array was opened. No strategy
module was imported/executed, financial result calculated, network source acquired or blocked request
retried. A fresh helper independently checked the narrow source counterpart question without data reads.
This adds **0 hypotheses,0 gross screens,0 counted evaluations**. Root owns registration/counters;
checkpoint3/60 evaluations,3/10 hypotheses,2gross screens, plus archived65t6 evaluations.

## Exact adopted parent, not an optimization winner

Current `funded_strategies/FUNDED_PLAN.md:18–33` explicitly adopts the user's RelStrength_v3 defaults.
Personal19 uses both sides at1MNQ,50K funded longs1MNQ,150K funded both1MNQ; evaluations do not use RS.
The current personal source/roster and latest TIER entry retain this rule. The optimization follow-up's
alternative exits were not adopted. No local default is allowed to override the current source version.

|Pinned source at7f0800f|Git blob|SHA256|
|---|---|---|
|funded_strategies/NQ_Relative_Strength.txt|5c7f16c3c93b71877b03a38a2b5b219343169133|20882cb3486ccbd60801572fa72f984161d408b89bc1621142e131de86292ffc|
|checks/candidates/relative_strength/RelStrength_v3.txt|c8249d5135855682e5ea3a0f19ef71a3709cc8ca|d819039cd0aedb33aa730f4b3b723adcc3169d10f4e9fa57c351e4652dc79b61|

Parent source uses synchronized NQ/MNQ Data1 and ES Data2,1-minute close labels in CT, RTH time>08:30
through15:00. At new RTH it stores the previous eligible RTH high-low range and sets anchors to the
previous Data1/Data2 closes, normally08:30. Its20-day quantity is the mean of up to20 stored eligible
RTH ranges, not true-range ATR. EWMA alpha is2/(20*390+1), initialized from the first admissible pair;
it updates covariance and both variances on eligible RTH bars and requires1950updates before a signal.
At the first RTH bar Time>=09:00 it decides once, using elapsed RTH bar count NBA in the residual-scale
denominator. A missing09:00bar is not permission to silently substitute another clock in a new replay.

`Z=(10000log(C1/anchor1)-beta*10000log(C2/anchor2))/sqrt(residualVariance*NBA)`.
At|Z|>=1.25 the parent follows its sign next bar at market, one filled entry/calendar date. Normal entry
is native label09:01/open wall09:00. Stop.6 and target1.0 times the stored range; flat15:00this-bar close.
Holidays/early closes are skipped by the source lists. The source's minimum5RTHdays is not full EWMA
stabilization; preserve its documented September2017 warmup/first-state convention and audit the actual
owned prefix before admitting2018entries. Never backfill a missing reference from later outcomes.

Filename-only warmup readiness check found `data/ES_1min_2017.csv`,
`data/NQ_1min_ON_2017.csv` and the owned DAY archive
`agents/codex/inputs/ob_v2_bench/NQ_1min_2017.csv`. No rows or cached grid were opened.
Their presence does not certify September warmup completeness, synchronized08:30anchors, clock
alignment or the first eligible entry. Root reports the native DAY source covers08:00–15:15 and can
supply08:30anchors, so this nomination does not require a new ON intake. Freeze exact DAY inputs and
hashes before loading; no retrospective forward-fill may silently replace an absent source minute.

Literal source protection starts after the entry bar, unlike this task's required active entry-bar stop.
The old Python rebuild also forward-fills native arrays and defaults to target-touch. The existing
MC-confirmation source says its report used1NQpoint target-through. Therefore the later frozen REPLAY
BASE must use audited observed prices, active entry-bar protection, worse gap fills and the specified
shared target-through; apply identical changes to BASE, flow and price controls. Quantify any published
book versus replay effect separately at the bench. An implementation repair cannot be called filter alpha.
No source strategy file is changed by this review.

## Why this exact input question is new within a selected family

|Source inspected|Existing definition|Bounded distinction/required history|
|---|---|---|
|analysis/orderflow_test.py|Generic opening-flow/price studies and entry-flow splits on its old REPORTS roster|Roster excludes RS; generic opening-flow selection remains relevant|
|analysis/bridge_filter_scan.py and bridge_filter_scan2.py|Explicit VB/ONB_ML/MON/EOS/LDF restriction; cum/30minute delta and other MBO/GEX fields|No RS-specific gate; do not reset their63+40scan history|
|analysis/relative_strength_opt_test.py and follow-up; latest TIER|Large selected exit/side search plus VXN/FOMC/macro/overnight/Z-size filters|No classified-tape predicate found; retain approximately170optimization variants and author selection|
|analysis/relative_strength_test.py|Already tests own-price and ES-explained parts, plus own-opening-price sign on RS trades|Purely relative tickets were stronger in published source. New flow must add information within price-sign controls, not borrow a momentum story|
|analysis/anti_nq_es_crossflow_test.py; anti_nq_aligned_weakness_short_test.py|Cross-market price-residual/ES-direction variants|Their names do not denote observed classified flow; failed/selected histories remain relevant|
|H01 LDF and H03 ST opening gate|Related signed-tape filtration; both CLOSED|No rerun, parent coverage rescue, window/availability change or transfer of a favorable old result|

No exact RS-specific classified-flow rule was found in this scoped source review. This is not universal
novelty, a claim all priority-one sources are exhausted, or an independent new alpha-family assertion.
Priority1/2 gates are already recorded in the saved hunt maps; this is a priority3 conditional book leg.

## Single prospective predicate and clock before any new data

Freeze **15completed native-equivalent OF close labels08:45..08:59CT**. Rebuild signed quantity
`D=sum(volume-downvol)` only when all15bars pass the previously established classification/native
matching checks. `volume` is buy/up-classified quantity, not total volume; require volume=upvol,
nonnegative finite quantities, native total matching, price matching and positive aggregate volume.
At the unchanged09:00RS decision, DROP only `RSside*D<0`; neutral validDzeroKEEP_KNOWN and incomplete/
invalid/mismatched inputKEEP_UNKNOWN. Keep the original one order/ticket on a kept day; no replacement
entry, altered side, cap, signal threshold or reentry. There is no rank, fitted threshold or window search.

The08:59last feature gets an explicitly assumed1-minute availability allowance to09:00. That is a
conservative historical research convention, **not verified receipt or latency evidence**. It is chosen
before rows/outcomes rather than selecting a favorable availability correction. A matched additional
one-minute activation-delay stress for BASE and FLOW may run only after design and the immediate book
bench pass, if preregistered within the five-model ceiling. No completed H03 audit is repeated unchanged.

The same15-minute price-only reference is explicitly `P=C[j539]-O[j525]`, i.e. `C08:59-O08:45` using
native close labels, **not** `C08:59-C08:44`. DROP only `RSside*P<0`; valid observed zeroKEEP_KNOWN,
incomplete/invalid native windowKEEP_UNKNOWN with unresolved-price states retained/flagged. It is an
unselectable control, not another nomination.
Base/kept/removed dollars and1000matched subsets must retain selected IDs/paths and condition at least
on year,side, own full-opening-price sign, parent entry clock and input-known state. Add the exact
same-window price-sign strata where feasible under a frozen policy, not after favorable outcomes.

An economic plan can fit five definitions: REPLAY_BASE, FLOW15primary, PRICE15reference and the
conditional matched DELAY_BASE/DELAY_FLOW pair. PUBLISHED is source plus ENTRY metadata only, not a
sixth new standalone financial model. The later required published-book/replay bench comparison is
explicit baseline implementation accounting. If root needs an additional financial definition, revise
the model list before data; do not disguise it as a free diagnostic or omit its selection history.

## Smallest next step

Read the eight-question sheet `agents/codex/evidence/hunt_v2_next_new_input.md`, then root may freeze a
separate <=5configuration plan, exact parent archive/dependencies, entry-only parity and source gates,
gross window/native costs and counter accounting, and COMMIT all before new rows/returns. First admit
2018–22signals/entries/source clocks; retain real limit locks, missing prefixes, reference gaps and MC
disagreements without favorable deletion. Failed admission means no raw return look, not a rescue with
new availability, feature or timestamp offsets. Any new financial experiment would be H04 only when
root registers it; this source note itself is not H04 and does not change the current I02 outcome.
H03's source gaps remain useful context, not an inherited H04 verdict: H04 must audit its own actual
EWMA/range/anchor references, entry prefixes, held windows and source calendar under its frozen plan.
