# NQ Cash-Open Repair: frozen standalone discovery test

2026-10-25. Commit before return tests. Evidence: `../evidence/cash_open_repair.md`.
User correction: existing mechanics are guides only; one new rule, no old-signal basket. Allowed bar frames
1/5/15/30 minutes; this experiment uses **5 and 15 minutes**, with one-minute execution data.

## Exact standalone rule

Instrument NQ, $20/point; MNQ repricing $2/point with native fees. No other traded leg.
For cash date d, use exact NQ and ES 08:31-labeled opens (08:30 wall time) and the exact 15:00 close of the
preceding **normal full cash session**. Do not skip a missing preceding-session anchor by reaching further back.
Use existing `codex_s03_calendar.calendar_status`, exclude holidays/early closes in advance, plus July 3 and
December 24 when weekdays (conservative predeclared no-trade dates). Weekends are not cash sessions.
Daily calendar includes all ordinary/early cash sessions; ineligible dates have zero strategy P&L.

Contract roll guard: no entries on the second Thursday of March/June/September/December or following Friday,
Monday or Tuesday (the standard quarterly roll-transfer window), known from date alone. Do not select observed
jumps using forward returns. If either endpoint touches these dates, the overnight observation is unavailable.
This is a conservative calendar convention, not proof of the actual continuous-contract roll time.

Overnight returns a=log(NQ open/prior NQ close), b=log(ES open/prior ES close).
From the previous **60 valid paired overnight observations**, before appending today:
beta=cov(a,b)/var(b); residual scale=sampleSD(a-beta*b); center=mean(a-beta*b).
Today's z=(a-beta*b-center)/scale. Current overnight prices may be known at entry, but today's outcome
never enters beta/center/scale. Do not fit coefficients to trade returns. Require finite positive prices/scale.

At the first k-minute cash bar close (08:35 for k=5; 08:45 for k=15), require every native NQ minute in that
bar to exist and be valid. Let side=sign(NQ bar close - 08:31 open); a flat bar has no signal.
For a repair candidate require |z|>=threshold and **side=-sign(z)**. Enter next minute's native open.
Stop=0.15*prior15-weekday calendar true-range SMA from `Grid24.daily_atr(15)`; target=0.30*same ATR.
Round both distances UP to the NQ tick. Bracket is frozen before entry, active on entry bar, one trade/day.
Time exit at the 11:00 CT minute close; no BE/trail/reentry/ML/weekday-side selection.
Missing scheduled entry open skips the order instead of fabricating a price. No new entries on missing input.
Keep/inventory any held-minute gap; do not remove bad trades after prices are seen.

## Five economic configurations, no more

1. **R5_Z1**: k=5, threshold1.0 (primary).
2. **R15_Z1**: k=15, threshold1.0 (coarser confirmation).
3. **R5_Z2**: k=5, threshold2.0 (large-dislocation sensitivity).
4. **BASE5**: all same-data/calendar-eligible nonzero 5-minute first-bar directions; no z gate.
5. **BASE15**: same for 15 minutes. These two are controls, never selectable as a new strategy.

Controls share the candidate's prior-beta/anchor availability mask and exits, so dropping that input alone
does not create a calendar advantage. Candidate/control shared entries must match. All five count as tested
economic models. No additional symbol, timeframe, direction, stop or target grid is authorized by this plan.
Related RS, CO-OC, opening momentum and inventory searches remain prior trials, not erased by preregistration.

## Costs, execution and staged stop rule

Use repo `grid.execute` / `_walk`, one-point target-through, nearer-extreme OHLC ordering and worse-open stops.
NQ $7.25 RT + one adverse tick per entry and per stop/time exit; MNQ $1.24 RT + $0.50 per slipped fill.
No slippage at a target exit. Fixed execution sensitivities after design: four adverse ticks/fill and opposite
minute path; not selectable models. Native MNQ fills remain unobserved.

First run **2018-22 design only**, with 2017 warm-up where available. Per candidate cheap gate:
>=100 trades; net>0; trade t>=2; daily Newey-West(5) t>=1.5; PF>=1.20; >=4 positive design years;
net positive at native MNQ fees and under four-tick NQ execution stress. Save all failed configurations.
If none passes: **stop**, no 2023+ returns, full account benches, new parameter grid or PowerLanguage.
If several pass, choose the first in the fixed order R5_Z1, R15_Z1, R5_Z2; do not choose the largest seen t.
Commit design evidence before running the chosen candidate and matching control once on 2023--October9,2026.
This is previously examined historical validation, not fresh out-of-sample evidence.

Goal t>=6 means the chosen **standalone** full net trade t and full daily NW(5) t >=6; report iid daily/NW20
too. Falling short is not permission to refit or substitute the prior six-leg composite.

## Diagnostics and conditional placement

All/long/short standard metrics, yearly/design/validation, true count of signals/trades/gaps/skips,
prior-only feature timestamps and initial-zero DD. No zero-trade side ratio invented.
Filter controls: kept/removed total net and average/t, 1,000+ matched-size random subsets of base, profit and DD
together, same eras/calendar. Compare total dollars, not just mean remaining profit.
Only after cheap-pass: random direction and random eligible morning entry time with the same known bracket/exit,
500 runs each; 5,000 ten-session block bootstrap and 5,000 permutations using repo tools; source trial count
from current TIER_LIST plus all5 models, sensitivity10,000 and disclosed unknown prior searches.

If a candidate survives, assess current19-leg personal A-D/FULL at fixed1MNQ: BASE/ADD/replace RS/empty RS,
1,000 paired histories, native fees, profits, DD95 and conditional book-loss contribution. Current plan afde088
is unchanged by latest5d1096d's code/calendar fixes. No new allocation is inferred from positive standalone t.
For 50K/150K evaluation/funded use reviewed current account engines, whole micro sizes and addition/RS replacement/
empty controls if causal joint paths exist. Existing missing overnight baselines must be LIMITS, not precise
pass/blown/payout claims from proxy daily paths. Standalone EOD-trail MC is an illustration only.
After a design failure, account contexts are REJECT/does-not-advance on the candidate design evidence, not
uncomputed claims of no marginal gain. No placement claim is needed for the unselectable controls.

## Deliverables

New rule/engine `analysis/codex_cash_open_repair.py`; outputs `analysis/outputs/codex_cash_open_repair/`;
concise result `agents/codex/results/cash_open_repair.md` with Summary<=5lines and explicit t6 outcome.
Commit/push only codex/work. No rankings, shared plans, root TODO, live files, VPS, broker/API settings,
vendor messages, purchases or account creation. A numeric pass needs independent review and a separately
frozen forward log; new PowerLanguage only after research passes and MULTICHARTS_PITFALLS.md is read.
