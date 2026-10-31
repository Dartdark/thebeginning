# FVB independent short execution: TEST

Summary: test a frozen, independently executable short-only FVB state machine, not the old short-side ledger mask.
This is confirmation of a result-informed B-item lead explicitly named by the user; it is not a new forced-flow discovery.
The stop-liquidation explanation is an unmeasured hypothesis. The first gate is a committed gross-only screen on 2018–22.
Missing MC parity, price-source/fill limitations, selection history and current-book uncertainty prevent confirmation or promotion now.
TEST authorizes a preregistration, not an immediate return calculation or trading.

Sources: repository source pin `92b1d4cde768bcfce019cf9a95944158dd0ebba3`, especially
`checks/candidates/fvb/spec.md`, `analysis/fvb_test.py`, `analysis/fvb_bench.py`, latest `TIER_LIST.md` row FVB,
and `MINED_INDEX.md`; exact source hashes and semantic review are in
`agents/codex/research/hunt_v2_fvb_source_review.md`. AGENTS.md, BUILDER_BRIEF.md, LESSONS.md and the v2 task
were read. The subsequently adopted `agents/codex/RESEARCH_CONTROLS.md` at `7d1e6a2` was read before finalizing
this sheet. Current-book definitions follow `agents/codex/research/hunt_v2_bench_source_map.md`, not FVB's old bench rosters.

Return trials: **no new H02 data, returns, ledgers or market-data caches read or computed for this sheet**.
Known prior selection includes the author's Phase 1–7 search and the source's 27 reported evaluations; prior full-history,
side and book results were already seen, including 2023+. The exact original author search count is unknown.
At this sheet's preparation v2 remains H01 closed, **3/60 counted evaluations, 1/10 hypotheses, 1 gross screen**;
the separate archived t6 65 evaluations remain in selection history. A source-only sheet does not change counters.
Root must record H02 and its at-most-five frozen configurations when preregistered; suggested counted designs are
SHORT_EXEC primary and BOTH causal reference, with BOTH unselectable.

## 1. Who trades, and what forces or causes the trade?

The proposed participants are leveraged longs whose protective sell stops may cluster around prior-RTH and
premarket lows, and directional sellers who use a confirmed break of those lows. A breach could turn contingent
liquidation demand into marketable sell orders while liquidity providers widen or withdraw. Those are plausible
price-contingent causes, not identified investors with a verified mandate or a known scheduled dollar obligation.
Nothing inspected establishes the amount of resting stops, aggressor inventory or whether the signal actually
activates forced selling. The existing FVB source calls this the maker's view, not a measured fact.

The falsifiable prediction is continued downside after an early-RTH close below a previously known low. The
prior-body and range restrictions are inherited author choices; they are not independent evidence that stops exist.
Deep liquidity, anticipatory trading or immediate absorption could remove any continuation after costs. The user
explicitly permits FVB-short confirmation, which justifies a small bounded empirical test despite the weaker
mechanistic prior. It does not justify describing this as a demonstrated forced-flow strategy.

## 2. Direction, size and timing known before entry

- Instrument: NQ one-minute signal grid, proposed executable unit one MNQ, $2/point, tick 0.25/$0.50.
- Inputs available before the RTH scan: the completed prior normal-RTH session's high/low, range and body ratio;
  the arithmetic mean of exactly 14 preceding normal-calendar RTH ranges; and the completed current premarket high/low.
  No current RTH high, low, close, final count or later data-derived day membership may gate today's entry.
- Native CT close labels: prior RTH 08:31–15:15 inclusive; current premarket 03:01–08:30 inclusive; scan signal
  closes 08:31–10:30 inclusive. A signal at column j enters the native open of **j+1**, never the next observed minute.
  CT uses the native America/Chicago clock including DST. Mapping from the author's ET open stamps is documented
  in the source review; receipt/execution delay beyond the next-open convention is unmeasured.
- SHORT_EXEC ignores every long signal before searching or changing state. Gap case has PM-low short level;
  overlapping-range case checks prior-RTH low then PM low when distinct. First close strictly below an active
  level triggers, unless the prior RTH body ratio is at least 0.6. Skip prior range >1.5 ATR or PM range >1 ATR;
  PM high must exceed PM low. Retain exact inherited inequalities.
- Size: one whole MNQ for standalone/design and the initial personal-book question. Maximum one open candidate
  position, maximum two short tickets per day; a second ticket only after a stop, from a later signal bar, with
  the stopped price level removed. No averaging, pyramiding or size search.
- There is **no defensible pre-entry dollar-flow estimate** from these sources. Do not infer one from prior price
  movement, stop distance or favorable historical P&L, or compare a fabricated quantity with NQ volume.

Root's announced protocol uses exactly 14 previous **normal cash-calendar slots**, each requiring all 405 RTH
minutes 08:31–15:15, with no stretching farther back to replace a missing slot. Prior levels use the preceding
normal slot, explicitly older across excluded holidays/early closes. Current PM requires all 330 minutes 03:01–08:30.
Any missing prior/PM input causes a pre-entry known-input skip for that day, retained in the calendar audit;
it does not globally veto the screen. This clarifies the root plan before any H02 data, not a changed gate.
The scan checks an observed prefix through its first
signal, or all 120 bars if no signal; its first missing minute makes that day unresolved. A first signal before
a later gap is governed by the retained holding-path audit. These are substantive changes from old FVB.

Root must bind its preknown normal/holiday/early-close calendar, source-completeness rules and tick tie rounding
in the committed plan. Its conservative existing quarterly guard is second Thursday of March/June/September/December
plus calendar offsets 0,1,4,5, excluding today or the prior reference date. This is a frozen **calendar proxy**, not
verified official vendor-switch provenance. ATR may include a guard date's complete intraday RTH range; it never
uses cross-date true range. Native-contract splice uncertainty remains a limitation; do not infer the guard proves
every splice harmless or tune it after returns. A normal day is knowable in advance; observing that today's
afternoon ultimately exists is not. Known half-days/holidays are skipped, with no last-bar exit fallback.

| Event / feature | event_time | available_at | decision_time | first executable fill assumption |
|---|---|---|---|---|
| Prior levels, body and ATR | Prior completed normal RTH close 15:15 CT | After that close is received; all 14 prior slots complete | Before today's scan | None until later signal |
| Current PM high/low | Final PM close 08:30 CT | After 08:30 bar receipt, before first 08:31 signal close | At qualifying signal close | Native j+1 open |
| Close below level | Signal bar close j,08:31–10:30 CT | Same nominal close; **zero additional historical receipt/compute delay assumed** | At j close after availability | O[j+1], same boundary under bar convention, one adverse tick |
| Stop / time exit | Every held bar / exact 15:11 close | Intrabar stop model / timeclose convention | Protection active from entry; fixed time exit | Worse gap open or stop plus tick; exact timeclose plus tick |

The next-open model idealizes event ordering at a shared timestamp; historical bars do not establish actual local
receipt/compute time or a zero-delay fill. Report that assumption. Unverified raw feature timestamp mapping is a
data blocker. These fixed rules do not require a learned-label, purged-fold or scaler-fitting pipeline.

## 3. Does the flow reach the traded contract or its direct hedge?

The proposed stops and continuation orders concern NQ itself. MNQ tracks the same Nasdaq-100 index and is linked
through common underlying exposure and arbitrage, so direction transmission is plausible. NQ trades do not prove
the availability of MNQ fills at the same price. Cash baskets, options hedges and other index futures may absorb
the pressure, and a break can reflect new information rather than stop demand. This is a direct price-signal test,
not a claim that a measured outside cash flow maps dollar-for-dollar to futures demand.

## 4. New information and data feasibility

| Input | Source / fields | Coverage / warm-up | Point-in-time timing / revisions | Availability / cost |
|---|---|---|---|---|
| Native NQ one-minute OHLC | Existing owned day and overnight exports, loaded through the shared grid into allowed Codex runtime paths; open/high/low/close and native date/time | Initial root scope 2018–22 only; no 2017 source assumed. Exact usable coverage and duplicates/holes remain unmeasured here | Raw bar labels/source overlap/DST must be audited; current-day final membership may not be used | Existing repository/workspace input; no new purchase |
| Prior RTH/PM statistics | Native bars under frozen normal-session calendar | Exactly 14 previous normal-calendar slots, each 405 complete RTH minutes; full 330 PM minutes today. No 2017 invented and no stretching over missing slots | Prior stats known after prior close; PM before first signal. Missing known inputs skip that day and remain audited; otherwise eligible scan/held holes veto the screen | No independent paid input |
| Calendar / roll guard | Preknown normal/holiday/early-close calendar and conservative quarterly second-Thursday+0/1/4/5 proxy, frozen by root | Entire intended period; **not verified vendor-switch provenance** | Available before session. Do not call `rolls_index` or choose eligibility from later prices | Existing/public calendar; native continuous-contract splice uncertainty retained |
| Current personal19 definitions | Adopted source pin `92b1d4c`, equal current plan source at `afde088`; retained baseline/replay adapters named in bench map | Design-period synchronized dates first; later 2023+ only after selection commit | ST/PT in, BB_MRM out. Preserve published booking/fee/coverage differences | Existing saved source/artifacts, not opened for this sheet |
| Independent MC list for frozen short execution | None established in reviewed source tree | **Missing** | A BOTH ledger's short mask is not this executable state machine | Required later for confirmation; no user or live-system action taken |

There is no incremental non-price information. The increment is correct execution of a separately stated short-only
state machine at native micro costs, with causal eligibility and current-book comparison. BOTH is a locked causal
reference, not a fall-back winner. Do not import/run `analysis/fvb_test.py`: its imports/entry point can populate
caches, use a full-history frame and launch many variants. Original CSV/trade-list bodies were not opened here.

## 5. Costs and actual intraday gaps

Under the task's MNQ research convention: $1.24 round-trip commission/fees plus one adverse tick on entry and exit,
$1.00 total slippage, gives **$2.24 per completed MNQ round trip**. The gross screen hurdle is **$4.48 per event**.
These are cost arithmetic, not a measured candidate effect. NQ-price-based MNQ fills remain a proxy; lack of
quotes, queue/latency and fast-stop impact must be disclosed. The frozen execution stress is four adverse ticks
per market/stop fill: $1.24+$2.00+$2.00=**$5.24/MNQ round trip**. It reprices the same two executable configurations,
does not select another rule and is retained in stress/selection history. Gross-to-net must separate commission,
slippage and latency assumptions, avoid double charging and report breakeven additional cost per trade.

The gross screen proposed for preregistration uses the **first eligible short signal each day**, exact next-minute
native open to exact 15:11 CT native close, no stop, no target and no reentry. It must retain raw gross mean/t,
counts, years and the empty long side, and at least 100 observed opportunities. Any held-minute/endpoint hole remains
in the opportunity audit and vetoes a pass; do not remove bad paths because a complete subset looks attractive.
Only if all frozen cheap gates pass may stopped SHORT_EXEC and its reference be run. Do not present stopped
P&L or reentry variants as the raw screen.

Later design stop: 0.18 times prior ATR, nearest-tick distance under a predeclared tie rule, active on the entry
bar; worse opening fill on any stop gap, plus adverse slippage; no target. Fixed exact 15:11 CT time exit.
Missing minutes cannot trigger a next-observed entry or an early/late final-bar fallback. An unresolved active
path blocks economic claims instead of becoming a conveniently absent trade. All known half-day/holiday dates
are skipped, so there should be no candidate hold through their close and no exit after 15:59 CT.

The older Tue–Fri 01:00–03:00 CT empty-hours claim is stale: adopted OT/VIX can hold 17:05→03:00 on eligible down
nights. Actual event-level current-book occupancy is unmeasured here. This candidate's 08:32–15:11 window overlaps
DT, PT, VB and other RTH pieces. Whether the book is flat on a particular signal day is
not a candidate entry filter. Event-level overlap and joint losses must be measured later at book level.

## 6. Power before a return test

There are roughly 1,250 weekday sessions across five years before holidays, exclusions, warm-up and data loss;
that is a calendar-scale planning bound, not an observed opportunity count. First-signal gross events cannot
exceed eligible sessions. Frequency of qualifying short breaks has not been newly inspected. Require at least
100 gross events; fewer means stop under the frozen screen rather than broaden the window.

For transparent planning only, if the raw MNQ window SD were $100–$200, net mean for t≈2 would be roughly
$20–$40 at effective n=100, or $8–$16 at n=600, plus $2.24 costs for gross. Those SD/n figures are assumptions,
not source measurements or a promotion threshold. Effective n may be much smaller because volatile days and
losses cluster. A $4.48 gross-cost hurdle alone does not establish significance; report observed dispersion,
full daily zeros, dependence and uncertainty later. Earlier side/parameter selection raises the eventual
promotion hurdle; it does not reset when this new v2 counter starts.

## 7. Already tested and falsifiers

Latest TIER_LIST/MINED_INDEX and existing confirmation-readiness/flow-novelty reviews were consulted first.
Scheduled-flow proxies in priority 1 are already tested; true expiring-contract/WI-tail inputs remain missing.
STv3/PTv2 are already confirmed/adopted, BB_MRM demoted, S03 has a prior placement rejection, and T_ONESIDE's
fade has already undergone MC parity. FVB shorts remain an explicitly named, result-informed unfinished case.
The old full FVB source/short mask, its historical side split, 27 reported runs, old cost model and old17-piece
bench are selection evidence, not new native-cost results or current19 plan improvement.

The old short mask ran BOTH then dropped longs; it inherited long-induced time, cap and level-removal effects.
SHORT_EXEC is separately executable and may produce additional/different tickets. Neither its outcomes nor its
causal corrections can inherit the old FVB checker PASS or old personal-book result. Retain an immutable BOTH
causal reference and any row-level comparison; do not select BOTH if the primary fails. Any filter diagnostic
must retain total base/kept/removed profit and 1,000 matched subsets with IDs/paths; those overlaps are not
executable portfolios and cannot stand in for independent SHORT_EXEC.

Predeclared gross falsifiers: mean below $4.48; fewer than 100 events; unresolved scan/held paths or fatal clock/calendar
errors. Stopped design requires ≥100 trades, positive net profit, net trade t≥2, daily NW5 t>0 and ≥4/5 positive years;
all unresolved scan/held issues veto. Later falsifiers: failure against identical-exit random-time or
random-side controls; or inability to improve any eligible current plan versus BASE **and EMPTY**. A failure
closes this hypothesis, not the hunt; it does not authorize retuning a side, level, stop, exit or calendar.

## 8. Failure and diversification — required supplement

| Question | Prediction before results | Evidence needed / what would refute it |
|---|---|---|
| What stops the mechanism? | A low break gets absorbed; sell stops were absent/already anticipated; information reverses | Weak/no gross continuation, failures versus random-time/side at identical exits, repeated false breaks |
| What liquidity role do orders play? | Next-open shorts and stop exits demand liquidity; the model pays adverse ticks | Native fill/quote evidence or conservative stress; bar OHLC alone cannot prove impact/latency |
| How could losses cluster? | Choppy recovery/risk-on sessions stop multiple shorts; overnight-to-open repricing invalidates old levels | Side/year/day clusters, loss streaks, entry-bar/worse-gap fills and complete native paths at one MNQ |
| Which existing legs may share losses? | DT/PT/VB may share RTH momentum risk; short selection might offset some long losses, but no hedge is assumed | Aligned current-book daily and chronological conditional losses; old reported correlations are insufficient |
| Can an offset arrive before breach? | Unknown; FVB can lose before another leg realizes profit | Valid joint intraday account replay required. Personal daily return/DD or annual correlation cannot answer this |

At design pass run current-book benches **immediately**, before extra robustness: personal19 BASE, ADD one MNQ,
REPLACE DualThrust one MNQ as the frozen overlapping morning-breakout leg, and that slot EMPTY, on identical
2018–22 dates, fees and paired one-year paths. Use whole contracts and the shared Monte Carlo implementation.
Separate publication-method versus replay/fee/mark/coverage changes from candidate alpha. If no eligible plan
improves versus both controls, stop without 2023+, placebos or additional variants. Current funded/evaluation
baseline chronology is limited; do not invent pass/payout changes from daily proxies. If used later, these
require current adopted definitions, valid joint paths and paired 50K/150K bootstrap/account engines.

## Decision and next gate

**TEST — eligible to preregister a small, disclosed confirmation experiment and its raw gross screen.**
Root must first freeze/commit exact calendar/roll/completeness policy, short state, source bounds, native costs,
gross gate, cheap stopped-design gate, current-book controls and trial accounting. No new raw prices or returns
were read for this decision. If those causal input policies cannot be verified, stop as NEEDS DATA before returns.
Retain run identity: family/config IDs, preregistration/code SHA, raw input hashes/versions/schema eras, settings,
counts/exclusions/unresolved paths, seeds/dependencies/result paths. Implementation reruns do not erase earlier
returns; a changed trading protocol/universe/availability rule is substantive. Preserve the baseline ladder
without undeclared selectable variants: this is a price-only rule and BOTH a causal state reference, not evidence
of an incremental non-price feature. After design+bench success commit selection before future candidate returns.

This revises the earlier source-readiness note's *immediate confirmation* limit only for a bounded research stage:
missing MC parity still blocks a confirmed/promoted result. After design and book gates, commit selection before
the selected rule and matched control see 2023+ once; label it **previously seen historical validation**. Full
2018–26 native-cost promotion needs current `metrics.t_threshold(N_items)` or DSR≥0.95, positive both periods,
both placebos p≤0.05, dependence/selection and fill/calendar audits, plan-size Monte Carlo, and a fresh independent
raw-spec checker. Only a survivor may receive a PowerLanguage draft for Claude's MC check. No deployment follows.
