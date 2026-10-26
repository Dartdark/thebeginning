# NQ Flow Innovation Relaxation: frozen standalone design

Evidence: agents/codex/evidence/flow_innovation_relaxation.md (TEST, weak economic prior).
Commit this plan BEFORE any new strategy returns. One five-minute signal; one-minute native execution.
Hypothesis: unusually unexpected aggressive pressure has temporary impact that relaxes. FADE residuals.
Actual dealer inventory/forced orders are unobserved; informed permanent impact is the main falsifier.

## Exact input, calendar and clock

Native NQ Grid24 OHLCV, Bridge upvol/downvol/source close only. Rebuild total=buy+sell and q=(buy-sell)/total;
OF volume is not total. ET minute-close labels -> CT minus60minutes. Every native/OF input minute must exist,
all OHLCV finite and internally valid, native volume nonnegative, buy/sell finite nonnegative, total>0,
source close finite and within0.25point of native close, native volume exactly buy+sell. No future repair,
NaN aggregation or carrying values across gaps. Exact duplicate selected-field rows may collapse with counts;
conflicting duplicate keys block intake. Audit raw native duplicates too. Record source hashes and all failures.

Use C.normal_cash/codex_s03_calendar, excluding all weekdayJuly3/December24 and C.roll_guard dates.
Do not use future-dependent g.trading membership. Five-minute bars align to midnight and contain j-4..j.
Construct q for closes08:55..14:00CT every5minutes. Decision closes09:00..14:00; previous q is exactly j-5,
with both bars in the same session. Complete current and lag input bars are mandatory for EVERY model.
Prior15-weekday ATR is the shared shifted daily_atr(15), finite positive; preserve its continuous-roll limits.

For each date, its training slots are the exact previous20 C.normal_cash calendar dates. Do not stretch
the window for missing raw dates. Roll-guard training slots contribute zero pairs. Within other slots use
complete same-session adjacent q pairs (x=q at j-5,y=q at j), j=09:00..14:00. No overnight links/current-day
observations. Require>=600pairs and>=15distinct dates with valid pairs; variance(x)>1e-12. Fit once BEFORE
today, and record all20slots/pair counts, first/last training dates and max training timestamp.

## Frozen estimator and signal

Fit b_raw=sum((x-xmean)*(y-ymean))/sum((x-xmean)^2). Project b=clip(b_raw,-0.95,0.95), then
a=ymean-b*xmean. This is OLS followed by a fixed projection and intercept recalculation, not unconstrained OLS.
Training residuals r=y-a-b*x; scale sr=sqrt(mean(r^2)). Also my=mean(y), sy=sqrt(mean((y-my)^2));
md=mean(y-x), sd=sqrt(mean(((y-x)-md)^2)). All are population/RMS scales (ddof0); require each>1e-9 finite.
Use identical training target observations and eligibility across all five models. No price/return target fit.

At decision close, e=q_current-a-b*q_previous, z=e/sr; raw_z=(q_current-my)/sy;
change_z=((q_current-q_previous)-md)/sd. The corresponding fade side is minus sign of that quantity.
Zero quantity produces no entry. No price-body, close-location, VWAP, opening-path or old-ticket gate.

Five configurations, fixed order; only first two are selectable:

| Name | Rule |
|---|---|
| INNOV15 | Fade z when abs(z)>=1.5; primary |
| INNOV20 | Fade z when abs(z)>=2.0 |
| BASE5 | Fade every nonzero e on the identical eligibility mask; matched base, unselectable |
| RAW5 | Fade raw_z when abs(raw_z)>=1.5; unselectable |
| CHANGE5 | Fade change_z when abs(change_z)>=1.5; unselectable |

Do not follow a forecast sign, invert failed fades or nominate a successful control. Audit projected/raw b,
clipped fits, near-zero(abs(b)<=0.05) and near-difference(abs(b-1)<=0.05) fits, q/current-vs-residual sides,
and exact event/side equality against controls.
At b=0 this reduces to raw demeaned flow; at b=1 to centered changes. No novelty claim from renaming AR.
All5 evaluations count; prior program60/58unique plus unknown older searches. Deduct unique rules only
with documented algebraic equivalence, not just identical realized tickets.

## Exact execution and costs

Decision j, extra whole-minute receipt/order allowance, market entry at native OPEN j+2 (09:02-labelled row
for09:00decision, its actual minute starts09:01). Missing scheduled native open => skip, never retry later.
Stop ceil(0.10*priorATR/0.25)*0.25points; target ceil(0.15*priorATR/0.25)*0.25. Both active entry minute;
shared grid._walk, worse gap opens, shared both-hit convention, target1point through. Exit at close
min(j+30,14:55). Shared F.replay one-position/max4tickets per day; suppress signals while invested and
at the exit close, no stale queued signals, same exits/settings for every model. No BE/trail/overnight/size fit.

NQ20USD/point, tick0.25,7.25USD RT fee +5USD for each market/stop fill; target no extra exit slip.
MNQ2USD/point,1.24USD RT +0.50USD/fill separately; label NQ-price proxy, not native MNQ execution evidence.
Fixed4ticks per market/stop fill stress, not an economic configuration. These are repository cost assumptions.
Preserve prelisting/native-parity and source-receipt limitations; no invented account claims.

## Design gate, controls and strict phase separation

2018-22 FIRST, loading only2018-22 native/OF inputs (2017 may be used only for native prior-ATR warm-up).
No2023+ outcome read.
Save all5signal/trade ledgers, yearly/all/long/short and micro/stress standard metrics, daily zero-filled P&L,
both trade t and dailyNW5/NW20, calendar/clock/roll/training audit and execution suppression counts.
Audit ALL held OHLC fields, volume consistency and scheduled exits, not just missing closes; retain failures.
No profitable-path deletion or missing-minute fill. An unresolved held-price path prevents advancement.

Candidate cheap gate:>=100executable trades, NQnet>0, trade t>=2, dailyNW5>=1.5,PF>=1.20,
>=4positive design years, micro-cost proxy net>0, four-tick stress net>0, and zero invalid held OHLC bars.
Additionally require matched-base independent-signal removed net<0 and candidate kept total>base total;
candidate must beat>=90% of1000matched-size random subsets jointly on net and daily maxDD. Require the
same result for1000subsets matched within year x side x signal-hour. Both subset modes use fixed RNG seed20261026.
If a matching cell cannot support the kept count, stop rather than borrow unrelated observations.

For INNOV15/20 versus BASE5 report executable ledgers side by side. Caps make them nonnested; do not call
their difference an executable removed-trade strategy. Separately replay EVERY independent signal with
same exits (overlaps/caps ignored only in this diagnostic), show total base/kept/removed profit and
removed mean/t, and retain all1000unconditional and1000matched subset paths. Label these extra overlapping
return paths nonexecutable diagnostics, not more economic configurations or evidence of an account path.

If both pass choose INNOV15 first, never maximal t. If neither passes, stop THIS family's validation/accounts,
retain failures/counts and continue a DISTINCT hypothesis. Commit the full design decision/selection BEFORE
any2023+ returns. Only selected and BASE5 may then run once through OF coverage end2026-07-07; call it
previously seen historical validation, never fresh holdout. No later threshold/window/direction tuning.

After a promising validation only: matched-exit random-side/time placebos,5000block bootstrap/permutation,
shared metrics/DSR/selection dependence checks using total prior search, and a fresh independent raw-spec
checker before promotion. Then whole-contract BASE/ADD/replacement/EMPTY comparisons with valid joint
50K/150K/account paths; missing chronology is LIMITS, never proxy payout improvements. NoPL on failed gates.

Final goal: both full-history net trade t AND dailyNW5>=6 after realistic costs and all required reviews.
First full-history4/4.5/5crossings need both metrics, positive design/2023+ and no known fatal execution/data
issue; design-only/selected/unadjusted/side/year results never qualify. Preserve prior events/milestone history.
Only actual material milestones create a new notification_event. EIA access blocker remains pending separately.

Deliver analysis/codex_flow_innovation_relaxation*.py, analysis/outputs/codex_flow_innovation_relaxation/,
agents/codex/results/flow_innovation_relaxation.md. Onlycodex/work and user-authorized research paths;
no shared ranks/plans/rootTODO/live/VPS/broker/API/purchases/accounts/external messages/watcher edits.
