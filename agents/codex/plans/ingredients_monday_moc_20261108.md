# Frozen ingredient round: Monday Long, Bridge Monday, ES MOC

Summary: Attribute three existing rules, preserving all previous searches and known outcomes.
Fifteen fixed definitions; no best-version selection, combination or account recommendation.
Commit plan/evidence/exact harness/source copies before real returns.

## Definitions: five per family

**MON / our Monday Long, NQ:** original long at08:31labelledOPEN (08:30civilCT), stop0.50×past15weekday ATR
from slipped entry, no target,15:00CLOSE exit. Other cases:
`no_Monday_gate`: same trade on all source weekdays, not a selection among five weekdays;
`short_direction`: original Mondays, short with mirrored stop;
`no_stop`: original Mondays/long/exit, no stop;
`exit_1000`: original Monday entry/long/stop,10:00CLOSE instead of15:00.

**BR / Bridge Monday Long v2.1, NQ:** original buy Sunday19:00CLOSE,100point target from raw close, no stop,
exit Monday15:55CLOSE. Last completed RTH ADX7>=10 and<50, DI+>DI−; source holiday/no-trade rules retained.
`no_ADX_band`: keep DI+>DI− and initialized state, remove only the10–50ADXband;
`no_DI_direction`: keep10–50ADXband, remove only positive DI difference;
`no_target`: original gate/entry/exit without target;
`RTH_entry`: same original Friday state and target/exit, enter Monday08:30CLOSE per source `rth_only=True`.
Do not price an extra unrestricted no-filter rule while constructing the two separate gate removals.
The source RTH close is not silently substituted with the other Monday rule's next-minute OPEN.

**MOC / ES MOC Follow, ES:** original follow14:00→14:50CT move when magnitude>=0.30×past15weekday ATR;
enter14:51labelledOPEN (14:50civilCT), stop0.25ATR from slipped entry, exit15:00CLOSE. Source full-session check
and predecision close-forward-fill retained. Other cases:
`no_move_gate`: same signal direction/stop/window on all nonzero-move source sessions;
`fade_direction`: original selected dates, opposite direction and mirrored stop;
`no_stop`: original dates/direction/window without stop;
`hold_1515`: original signal/entry/stop,15:15CLOSE instead of15:00.
No alternative thresholds, times, weekdays or long-only/short-only rule is selected from these results.

## Input, clock and implementation admission

Same pinned raw snapshot `fe35af99aa90d7f31b91f8693859251bb44dd9ab`,2017warm-up, in-memory NQ day/overnight and
ES Grid24. Verify each raw blob/SHA256, retained source and committed shared helper before returns. First run
2018-01-01–2022-12-30; save/check implementation receipts, then all15unchanged on already-seen2023-01-01–2026-10-09.
These are historical replications, not a new holdout. No economic gate picks or promotes a diagnostic version.

Reuse the committed ingredient helpers for grids, metrics, paired ledgers, JSON and random subsets. Bind this
round's source Grid24 path and seed explicitly. Compile only selected source functions; never execute top-level
source backtests, MultiCharts or live guards. Source instrumentation only adds exact entry/exit row/minute and
exit-kind metadata, plus the preregistered gate alternatives. Original entries/exits/net must match uninstrumented
MON/BR functions. ES uses an isolated source namespace with PV50, not NQ's PV20; verify its price/cost bridge.
Also match its original entry/exit/net to the retained independent vectorized MOC price simulator; this is the
same baseline definition for implementation checking, not a sixth candidate or fresh MultiCharts verification.

Source Bridge target convention is a **touch fill**, limit improvement at favorable gaps, no target-exit slippage.
Retain it for attribution rather than silently replacing the original strategy with a new fill policy. This does
not certify modern executable limit fills or waive the standard1point rule for future new-candidate tests.
Target exits on Sunday must preserve their actual time and be attributed to Monday; don't use the old source's
Monday j1=0 as the actual fill time. Inspect the full Sunday-to-exit adverse path. No stop/target confusion.

Source selection itself uses historical calendar/data checks (Bridge requires a Monday14:55price before replay;
MOC uses source last_j/full flags). Preserve and identify that retrospective coverage policy; it is not a verified
live-knowable availability rule. Missing entry prices are excluded before pricing with reasons. Missing held bars,
target-bar path ambiguity and last-known-close exits must be flagged; no invented path or fresh native fill parity.
Abort on nonfinite execution/net, cost/daily mismatch, changed original source prices, uninitialized used state,
or failure to include any observed Sunday-before-midnight path. Never repair code/rules based on profitable outcomes.

## Costs, measurements and interpretation

NQ:$20/point,tick0.25,$7.25RTcommission. ES:$50/point,tick0.25,$5RTcommission. Market/stop fills pay one adverse
tick per leg; Bridge target exit is a limit and pays only entry slippage. Native MNQ/MES use1/10price/slippage
dollars and **assumed$1.25RTcommission**, not verified broker fees. Thus normal market roundtrips$2.25MNQ/$3.75MES;
Bridge target sensitivity$1.75MNQ. Also subtract one additional tick per market/stop fill on fixed orders; no latency
or re-anchored stop-path claim. Fixed one standard contract; no compounding or account-size optimization.

All cases/sides/eras/years: trades,wins,gross/fees/slippage/net,average,t,Sharpe,Sortino,PF,zero-initial-peak DD,
Calmar/Ulcer,worst trade/source adverse mark,native micro sensitivity,missing/fallback counts and cost stress.
Save original feature/state admission and all trade/daily ledgers; reconcile to cent. Dollar results across NQ/ES
are not equal risk. Daily DD is not intraday trailing-floor survival; native quotes/roll metadata remain absent.

Every base-minus-intervention effect:1000paired20session block resamples, seed80313, annual5/50/95%bounds.
Original-rule annual/Sharpe bounds also retained. Pure nested controls: MONweekday gate, BRADXband, BRDIdirection,
MOCmove gate. Verify retained date/side/entry/exit/net identities; report removed total/mean/t and1000within-year
random drops with matching retained counts, judged by total profit and DD. Nonnested timing/exit/direction cases
stay paired rule comparisons. No average-trade-only filter recommendation or uncounted strategy rescue.

Reporting rule: historically persistent profit contribution requires base-minus-intervention total>0 in both eras;
stronger support additionally requires paired bounds above0, retaining earlier selection caveats. Risk shaping
requires reported DD/tail consequences; mixed signs or wide intervals mean conditional/inconclusive. No adoption
decision follows. All fifteen definitions and previous source/ingredient trials remain multiplicity.

No account/portfolio simulations, new combined rule, live/MC/TIER/plan changes, scouts/schedules, external messages,
paid data, VPS/broker/API-key access or automatic reopening of a failed family. Any new rule needs a separate protocol.
