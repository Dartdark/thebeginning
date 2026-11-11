# Frozen pressure-memory extension: identical estimators, longer causal state

Evidence: [pressure_memory_20261110.md](../evidence/pressure_memory_20261110.md).
Code: `analysis/codex_pressure_memory_20261110.py` plus its frozen original input/replay/learning dependencies.
Commit this plan, evidence and exact code BEFORE any actual profile-label join, fitting, predictions or returns.
Input-only synthetic checks remain separate. Existing prior outcomes are not a reason to retune this specification.

## Question, unchanged components and multiplicity

Does a120minute pre-event state improve the net barrier forecast beyond the original three-bar state?
This is a related-family extension; it is not a literal Hawkes/propagator replication or an independent new factor.
Source one-minute sampling (uploaded2021paper PDF p.3) and parameter .12 (p.5) motivate a prospective memory measure.
They do not specify this NQ rule, its nine features, or a profitable price direction. u below is not exact source J;
do not add the source's4.36 jump threshold or retrospective event labels.

Reuse **`analysis/outputs/codex_pressure_learning_20261110/features_and_labels.csv.gz` bound at commit
`0d61f59e30304a5a9850ef1a20b33a2d1f04cc2d`**, with verified cache bytes in the run binding.
Preserve all original21features, local normalization, normal-cash/roll rules, bracket geometry, processing
allowance and costs. Do not rebuild or relabel payoffs. Add only the frozen profile below.

There are four new definitions, increasing the active study's cumulative15 to19; retain older AR/raw-pressure,
absorption,39book-feature and other selection history. Comparable controls are counted as definitions. This fourth
matching-estimator control is accepted prospectively, before this extension's outcomes, to identify the feature increment.

## Exact profile and day-local normalization

Let d be the decision's calendar date and T its completed five-minute CT close. The profile contains120one-minute
return endpoints **T−124 through T−5 inclusive**, needing121exact closes **T−125 through T−5**. Require all120native
buy/sell/total observations at the return endpoints to be finite, nonnegative and consistent with total=buy+sell.
Do not bridge a missing minute, forward-fill, interpolate or substitute candle-color volume.

Let ATR_d be the original shared shifted prior-day ATR15, known before d. For a historical minute endpoint m on
normal-cash date s, define a_s,m=abs(C_s,m−C_s,m−1)/ATR_s using that historical date's own known ATR. For every d:

1. Use the exact preceding20normal-cash calendar slots. Roll-date history remains in the input seasonal window,
   as with the original volume normalization; candidate/label dates keep their original roll exclusions.
2. For each of the1440clock-minute slots, calculate the median of finite a_s,m values. Finite zeros count toward
   the required minimum15observations. The resulting median must be strictly positive to admit that clock slot.
3. Normalize those positive valid medians by their median across **all1440clock slots**. Thus f_d,m=m_d,m/g_d.
   Missing/nonpositive slots stay unknown. No date is admitted before20prior calendar slots exist.
4. Fit f before d. For each profile endpoint τ, set
   **u_τ=(C_τ−C_τ−1)/(ATR_d × f_d,clock(τ))**. Every required u must be finite.

All profile endpoints lie before the current event bar T−4..T. The original local three-bar inputs remain intact.
This is an incremental history measure and deliberately shares information with the preceding local bars.
No future post-jump relaxation curve, fitted jump class, future news match or full-day normalization is available at entry.

## Nine fixed added features and four interactions

Order the120profile values from oldest to newest. The last15endpoints are T−19..T−5; the preceding105endpoints
are T−124..T−20. Compute exactly:

| Feature | Frozen definition |
|---|---|
| A120 | mean of abs(u) over120endpoints |
| log activity acceleration | log(A15/A105), where each A is that segment's mean abs(u) |
| EMA_abs | initialize S=0 before the oldest endpoint; iterate S←.12×abs(u)+.88×S |
| EMA_u | same initialization/recurrence on signed u |
| EMA_sign | same initialization/recurrence on sign(u) |
| pressure120 | sum(buy−sell)/sum(total) over120endpoints |
| pressure acceleration | last15minute pressure minus preceding105minute pressure, each ratio of summed quantities |
| alignment | sum(u×sign(buy−sell))/sum(abs(u)) |
| peak fraction | max(abs(u))/sum(abs(u)) |

These are discrete one-minute exponential averages with coefficient .12; do not silently substitute exp(−.12) decay,
change initialization or reset at a jump. Large observed u values remain; they are not removed by a source J threshold.
Individual zero returns, zero signed flows and zero imbalances remain valid observations. Require A15>0, A105>0,
sum(abs(u))>0 and positive120/15/105total-volume denominators; otherwise the profile is unknown. No epsilon replacement.

Add four directional interactions: side×EMA_u, side×EMA_sign, side×pressure120 and side×pressure acceleration.
The memory models therefore use **34features = original21 + nine + four interactions**. No other feature, period,
threshold, effect slice, interaction, peak-location statistic or learned decay is searched.

## Same eligible observations, labels and execution

Every model uses the same common mask: original batch2 local eligibility AND profile-known at the decision.
Local controls must not gain or lose rows relative to memory models. Their training sets likewise share common input
eligibility, label availability and known-outcome policy. Never require label_valid to make a prediction.

Decision closes are09:00–14:00CT on original normal cash/roll dates. Long and short forecasts use the same point.
Entry is OPEN of row j+2, corresponding to wall j+1 after one whole minute of processing allowance. Stop is
ceil(.10×priorATR/.25)×.25 points; target is ceil(.3×stop/.25)×.25. Preserve rounded effective target/stop ratios.
Scheduled exit is CLOSE at min(j+31,14:55), thirty wall minutes after the scheduled entry open. One position and
maximum4actual entries/day; no same-close reentry, averaging, BE or trail. Preserve original missing-entry handling.

Use shared _walk entry-bar protection, adverse stop gaps,1point target trade-through and its declared both-hit path.
Preserve stop-first ambiguity stress. NQ fee7.25RT plus5USD per market/stop fill; separately repriced NQ-price MNQ
proxy fee1.24RT plus.50per such fill. Four-tick stress charges20USD per NQ market/stop fill. Native micro fills are
not established. Gap losses can exceed nominal1R; do not clip them. Existing labels are net_mnq/(2×stopdistance),
available only at the full scheduled horizon even when their actual target exited earlier.

## Monthly fitting and four definitions

Before each calendar month, train on the exact preceding126normal-cash calendar slots. Missing/roll slots do not
stretch the window. All training labels must have matured **strictly before** fit-month start. Use the original
full-horizon label-known policy. Require at least100represented dates and10,000valid long+short label rows, plus
at least50kind0stop labels EACHside across at least30sessions EACHside. Failure means skip the month, not relax a gate.

Fit StandardScaler mean/std on training features only; zero-variance columns receive scale1. Fit one shared regressor
over the paired side rows. No shuffled folds, tuning, early-stopping split, daily refit or current-month target use.
Current-month feature normalization may use only its already preceding observed days; model/scaler parameters stay fixed.

| Definition | Role and fixed configuration |
|---|---|
| HGB_MEMORY | Primary candidate,34features; HGB max_iter120,max_leaf_nodes7,max_depth3,min_samples_leaf250,l2=10,learning_rate=.05,early_stopping=False,seed20261110 |
| RIDGE_MEMORY | Alternate candidate,34features; Ridge alpha100, default intercept |
| HGB_LOCAL | Unselectable matched control, original21full-q features; same HGB/scaler/training protocol |
| RIDGE_LOCAL | Unselectable matched control, original21full-q features; same Ridge/scaler/training protocol |

For each decision choose the higher predicted net-R side only if its score is strictly>.02R. Retain the original
near-equality tie suppression (absolute1e−12); no fit or no adequate score means no entry. No inversion of failed signs.
Select the first candidate passing every gate: HGB_MEMORY, then RIDGE_MEMORY. Never select a local control or the
maximum observed Sharpe. Save fixed feature names, daily normalization clocks/coverage, training calendar slots,
last label-availability time, downside coverage, scaler identities and every monthly fit/skip.

## Frozen gates and earned continuation

For each selectable candidate require all basic gates: >=250executable trades across>=100dates; >=25eachside;
positive NQ and MNQ net; trade t>=2; daily Newey-West(5)t>=1.5; PF>=1.2; >=4positive design years;
positive four-tick stress and stop-first stress net; zero unknown/invalid held paths. These thresholds are a cheap
screen, not a claim of selection-adjusted significance or account readiness.

Only a basic pass earns the paired increment gate: daily net minus its **same-estimator** local control, aligned to
the same full calendar with zero no-trade days, must have10day-block90%bootstrap CI lower bound>0. HGB_MEMORY compares
with HGB_LOCAL; RIDGE_MEMORY compares with RIDGE_LOCAL. Do not credit an estimator difference to memory features.
Preserve existing fixed random-side/time same-exit placebos, cost/latency stress, dependence/multiplicity standards and
all required validation/account stages. A positive control or an unpaired net increase cannot substitute for these gates.

Save all four predictions, signals, ledgers, zero-filled daily calendars, year/side ratios, skips and input/label
coverage. Unknown training labels may be excluded under the inherited cache contract; unknown selected candidate
executions must be retained, reported and stop advancement. No actual failed execution is silently removed.

Commit a definitive design selection before any2023+ outcome access. Full-session native buyer/seller profiles after
2022 are not assumed available from daytime legacy exports; resolve input availability before an earned validation.
Never shorten the120minute window, fill missing pressure, or invent a recent zero-flow series. Historical validation
is already seen data, not a pristine holdout. Only after earned standalone validation do independent checking and
joint BASE/ADD/REPLACE/EMPTY account comparisons follow at frozen integer exposure and actual floor/expiry rules.

If both candidates fail, reject this specified extension and preserve all19newstudy definitions plus earlier history.
No threshold/window/hurdle/model-feature rescue, control promotion, effects scan, repeated holdout look or claim that
an earlier failure became positive. Quote/contract/receipt/roll/native-MultiCharts limitations persist. No live,
broker/VPS, phone, schedule, order or portfolio change is authorized by this research plan.
