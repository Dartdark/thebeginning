# Preregistration — selected-book 0.25% adverse-offset limits

Summary: Vault Break, FC 2B and S47, selected before new returns by directional holding horizon.
Compare unchanged immediate virtual-parent entries with a fixed 0.25% adverse limit; original exits stay fixed.
Design 2018-04-02–2022-12-30 first; all original opportunities, nonfills, UNKNOWNs and prior selection retained.
15-definition project cap: per parent BASE, LIMIT025, LIMIT025_STRESS, RANDOM_TIME, RANDOM_DROP.
Stop failed gates without threshold/clock/side rescues; research only, no book or live changes.

Program `user-mae-selected-20261108`; [evidence](../evidence/mae_selected_20261108.md).
Exact code `analysis/codex_mae_selected_20261108.py`; inputs/config/lease/reservations in
`agents/codex/inputs/mae_selected_20261108/`. Underlying source review remains the historical source decision;
the user's new explicit request authorizes this narrow experiment. Separate from stopped scout/lab/eval budgets.

## Frozen policies and data

- BASE: existing parent ticket at one MNQ, source gross cash and original entry/exit cost categories.
- LIMIT025: long limit = floor(original entry × .9975 / .25) × .25; short limit = ceiling(entry × 1.0025 / .25) × .25.
  Activate in minute b+1; never use original entry bar. Search chronologically through x−1, where x is original
  virtual exit minute. Cancel if unfilled; do not fallback to market or re-estimate expiry after seeing outcomes.
  Original virtual parent keeps running to produce cancellation/exit intents; no hindsight exit is used as an
  observable pre-entry feature. Parent reconstruction remains conditional until independent native review.
- Require one native tick beyond the limit; touch does not fill. A marketable gap at the open can improve raw
  fill price; use observed open, adverse one/two-tick modeled cost capped at the limit. Intrabar fill is at limit
  on the existing common OHLC path, no passive entry slippage. No invented traded price through an empty gap.
- Targets, stops, trailing decisions and time exits remain original virtual intents/levels, not re-anchored.
  No exit delay. Preserve original target trade-through. A pending actual holding suppresses later overlapping
  parent intents. This does not claim full regenerated parent-bracket or current-account parity.
- Missing waiting or held data, invalid OHLC, unsupported changed roll interval or source fill is UNKNOWN. No
  ffill/interpolation. Exclude documented exchange closures only. Previous selected-definition and source-hole
  history stays visible. Descriptive conditional comparisons may be published; zero UNKNOWNs required to advance.
- MNQ $2/point, .25 tick, commission $1.24 RT; market/stop fills one adverse tick. Stress $2.48 RT / two ticks.
  MAIN versus STRESS changes fees/slippage only, not which orders fill. Stress definition includes its paired
  stressed BASE comparator. Gross and cost bridge are views of these registered definitions, not free variants.

Only owned NQ raw 2017–22 inputs in config are loaded. Parent CSVs include already-seen later rows and are filtered
before new price/return arithmetic. Shared price/helper APIs are reused and hashed; no old script/output overwritten.
Source roster/rules are pinned read-only to the recorded Claude commit. Full-book sizing remains a later stage.

## Design gates, selection and reporting

One candidate per parent; no winner among offsets or selected sides. Compute whole/long/short and design-year
metrics for actual fills; missed trades remain zero contributions in the original opportunity/calendar universe.
Reconcile gross−fee−slippage to net and daily sums; report fills/nonfills/UNKNOWNs, delay, source-missed average/t,
net/stress increment, paired daily t, DSR, Sharpe/Sortino/PF/Calmar/Ulcer/DD and year effects.
Daily series is closed-ticket contribution, not full MTM/account equity, especially when source paths are incomplete.

Each candidate must pass **all**: zero UNKNOWNs; at least 30 complete opportunities and 30 actual fills; positive
total main/stress net and main/stress increment; paired daily t >= metrics.t_threshold(N); DSR >= .95; at least
four positive design years and three positive incremental years. N = max(root variants, 10,000) + 120 prior
current-book reservations + 58 older fast-alpha looks + 51 small-limit looks + 9 author-table profiles + 15 here.
Conservative floor is not a complete census of undisclosed author/parent tuning. Descriptive side results cannot
be used for promotion or changing the test. Failure closes that parent's dependent work.

## Earned controls and historical/account stages

Commit design disposition and selected parent IDs before controls. Exact controls are implemented in the frozen
runner; 1,000 histories each, fixed seed 7063478 + character-code sum(parent), no favorable seed choice:

1. RANDOM_TIME: at each original event sample an independent integer delay uniformly 1–60 minutes, enter next
   designated minute OPEN with market costs if before parent exit and open; otherwise cancel. No future price
   or realized candidate delay selects a random clock. This is one unselectable null policy per parent.
2. RANDOM_DROP: on BASE randomly drop exactly the candidate's missed count within each source exit-year/side
   stratum. Keep original dollars, no risk rescaling. One unselectable null per parent.

Candidate must exceed 95% of random-time totals, 95% of random-drop totals and 95% of random-drop drawdowns
(lower DD), retain positive incremental uncertainty, and missed BASE trades must lose with t <= −2. Unresolved
control paths stop inference, not imputation. These descriptive DDs are not native-account certification.
Only then once-only unchanged 2023+ historical validation, after a committed selection and data/cost admission;
positive incremental main/stress, t >= 2, full paths and existing multiple-testing/independent reconstruction
requirements remain. Already-seen 2023+ is not fresh validation. Independent raw-spec/native checks and relevant
BASE/ADD/REPLACE/EMPTY personal/50K/150K evaluation/funded at actual integer size follow only earned gates.
Refresh those source versions then; do not infer funded/evaluation benefit from daily diagnostic curves.

If later required raw settings/native account inputs are materially missing, save the exact blocked stage and
continue the other predeclared parents. No false floor, DLL, 30-day-expiry or partial-path account model.
Use existing research engines and all required accounting/Monte Carlo checks only when earned.

## Ownership and reproducibility

Dedicated project progress has 15 unique reserved definition IDs and a checked-head owner/run two-hour lease.
The runner verifies committed exact code/spec/config and input hashes, committed progress, lease ownership,
HEAD == fetched origin/codex/work == matching FETCH_HEAD before any raw market outcome. This direct-user
project does not restart the stopped automated scout; its hard-coded scout admission CLI is not used to mutate
that program. The dedicated guard follows the existing explicit current-book experiment precedent.
Synthetic selftests use invented prices only. Publish code/evidence/reservation before design; confirm remote
claim. Preserve every executed definition including failed/stressed/null views; release unused reservations
and lease at completion. Commit/push only authorized research paths to codex/work without force.
