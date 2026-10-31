# H02 FVB independently executable shorts: frozen preregistration

Evidence first: `agents/codex/evidence/hunt_v2_fvb_short_execution.md` (TEST for bounded research only).
Source review: `agents/codex/research/hunt_v2_fvb_source_review.md`.
Priority/source exclusions: `hunt_v2_flow_novelty.md`, `hunt_v2_next_priority_source.md`, and current
TIER_LIST/MINED_INDEX at Claude source92b1d4c. Execution/writes remain on codex/work.
No H02 market data or new returns have been read at registration. The nine uploaded templates are references only.

## Question and prior selection

Does the previously selected FVB short lead survive an independently executable short-only state machine,
causal source eligibility, exact native clocks, realistic MNQ costs and the CURRENT personal19 book?
This is an explicitly requested B-item confirmation, not a new forced-flow discovery. The proposed cause is
contingent sell-stop liquidation at known lows; actual stop inventory/flow size is unmeasured. No compulsory
fund mandate or dollar-flow estimate is asserted. Old full-history/short-side results and roughly27 reported
author evaluations are already known, including2023+. Original wider search multiplicity is unknown.
The old bench executes BOTH then masks shorts; that is not executable SHORT_EXEC and cannot supply its returns.

## Frozen configurations and budget

Exactly TWO stopped economic configurations, only after the one raw gross gate passes:

1. SHORT_EXEC: primary; ignores long levels/signals entirely and owns its position/cap/reentry state.
2. BOTH_CAUSAL: unselectable reference with the same corrected data/clock/fee policy and original side order.

No alternative window, body/ATR threshold, eligibility relaxation, size or stop search. The fixed four-tick
cost stress is deterministic adverse repricing of these SAME tickets, not another selectable rule.
No profitable reference may replace a failed primary. Gross failure costs zero counted economic evaluations
but retains H02, its screen and all source/selection history. Registering H02 makes2/10 hypotheses; cumulative
counted evaluations stay3/60 until designs run, then5/60 if both run. Prior t6 remains archived65, not reset.

## Inputs, calendar and causal references

Only the existing `data/NQ_1min_{2018..2022}.csv` and `NQ_1min_ON_{2018..2022}.csv` are admitted initially.
No2017 warm-up is assumed, no2023+ file may be read for candidate development. Use shared Grid24 as storage,
with a separately audited duplicate-consistent native adapter. Never use current-day `g.trading`, final bar
counts, `last_j`, the old Frame, old side ledgers, or future detected-roll membership for eligibility.
Validate actual date/time keys, OHLCV, source overlap, missing clocks, CT/DST labels and file/code hashes.

Normal cash calendar slots come from shared `codex_s03_calendar.calendar_status` plus conservative existing
`replica.is_early_close`; holidays/early closes are skipped before entry. Full daily calendar rows include
excluded/zero-trade days. Complete normal RTH reference =405 native close-labelled bars08:31..15:15CT.
ATR = arithmetic mean of ranges from the EXACT14 preceding normal calendar slots, not true range. Any missing
reference slot vetoes today rather than stretching to an older available session. Prior high/low/body use
the immediately preceding normal slot, explicitly older across excluded holidays/early sessions.
Today's ATR/reference never uses today's RTH outcomes. PM = all330 closes03:01..08:30; any missing input skips
and is retained. Unknown inputs never become favorable zeros or forward fills.

Conservative preknown roll guard: in March/June/September/December, skip second Thursday and offsets0,1,4,5
calendar days, for TODAY and the immediately prior reference date. Intraday ranges from other prior slots
may remain in ATR. This matches an existing research guard, NOT an official vendor switch date or proof that
all splice effects are absent. Never detect the switch from future prices. Contract-ID/provenance uncertainty
remains a limitation; if an actual fatal splice problem appears, block promotion rather than tune this guard.

## Rule, information clock and execution

Native signal timeframe1minute, NQ prices, proposed executable unit1MNQ ($2/point, .25tick). All clocks CT with
America/Chicago DST. Signals are completed native closes j511..630 (08:31..10:30). Prior RTH reference is known
after its15:15 close; PM is known at08:30. Signal close event_time=available_at=decision_time under an IDEALIZED
zero receipt/processing-delay assumption. First executable fill is the open of exact native bar j+1, sharing
the signal-close wall boundary. Receipt/latency is not verified. Record these fields plus bar labels; do not
claim a same-bar close fill or next-observed-minute substitution. Missing scan prefix stops the search and
vetoes gross/design admission if otherwise eligible, until first signal or all120 scan minutes if none.

Skip prior range>1.5ATR, PM range>1ATR, PMhigh<=PMlow; ATR must be finite/positive. No shorts when prior
abs(close-open)/range>=.6. Gap case priorhigh<PMlow OR priorlow>PMhigh: only PMlow short level. Otherwise
priorlow first, PMlow second when distinct. First eligible close STRICTLY below an active level triggers;
a cross from above is not required. Ignore every long signal in SHORT_EXEC. Tick rounding uses NumPy
nearest tick with ties-to-even, including entry/stop-distance conventions inherited from source.

Stopped SHORT_EXEC: next exact minute open, stop distance nearest-tick(.18ATR), active in entry minute;
no target; exact15:11 close time exit j911. Shared grid execution/walk must enforce worse opening fills
on stop gaps, including entry-bar protection, and adverse slippage. One open position; maximum2tickets/day;
second only after a stop, start scanning AFTER the stop bar, remove stopped level by PRICE. Time exit ends
the day. No pyramiding. Require every held minute; retain unresolved tickets/holes and veto admission, never
last-bar fallback, later observed minute, favorable deletion or shortened exit. Skip half-days/holidays,
and independently verify no exit after15:59CT. BOTH reference retains original long/short level order/cap
but uses these SAME causal corrections, exact next minute/time exit and costs. It is not old-source parity.

## First gate: raw GROSS only

SHORT_EXEC first eligible SHORT per day; exact next-minute native open to15:11 native close; NO stop, target,
reentry, commission or slippage subtraction. Preserve every opportunity and missing path. Report events,
mean/t/dispersion, yearly rows, all/short/empty-long rows, calendar exclusions and source/clock audit.
Native cost assumption =1.24RT commission+0.50entry adverse slippage+0.50exit=$2.24/MNQ; minimum mean GROSS
=$4.48 (2xcost), at least100events, all held paths/endpoints and otherwise-eligible scan prefixes complete.
Any failed condition CLOSES H02 before stopped returns/validation/benches/MC/PL. A gross pass is not net
significance, promotion, a book improvement, or an independent validation. Save immutable hashed marker.

## Stopped design gate and immediate book bench

After a verified gross PASS, commit/freeze stopped implementation before running the two configurations.
Design2018-22 PRIMARY requires >=100trades, positive total native net, trade t>=2, daily NW(5)t>0,
at least4/5positive years and no unresolved execution/source/calendar issue. Give all/long/short/year rows,
Sharpe/Sortino/PF/Calmar/Ulcer/maxDD, gross/commission/slippage/net separately, break-even additional cost,
and fixed4adverse ticks per market/stopfill (RT$5.24) stress. Source timeframe1minute, not return rescaling.
No long side is silently invented for a short-only rule. BOTH is a reference only, not a rescue candidate.

Immediately after design PASS, before placebos/resampling/robustness, run CURRENT personal19 bench on
identical2018-22 dates, coverage and fee conventions: BASE; ADD=BASE+SHORT_EXEC1MNQ; EMPTY=BASE-DualThrust1MNQ;
REPLACE=EMPTY+SHORT_EXEC1MNQ. DualThrust is the preselected overlapping morning intraday breakout slot.
No occupancy filter. Use current adopted ST/PT additions, BB_MRM removed, every current leg1micro; not
future aggressive allocation or stale funded constants. Personal MC shared histories/simulator: paired
5000 draws,252day horizon,20day blocks, seed20261026. Report paired changes/intervals in annual return,
maxDD, return/DD and one-year loss/DD risk. Candidate must improve return/DD over BOTH BASE and EMPTY in
at least one executable ADD/REPLACE row, with positive paired return/DD difference5%quantile against both;
otherwise stop. Disclose inherited baseline mark/reentry/fee/coverage uncertainty and separate publication
method effects from candidate alpha. Small gains inside unresolved source uncertainty do not qualify.
Daily personal simulations do NOT establish funded pass/payout improvement; missing joint account paths
remain limits. No funded/evaluation claims without repaired current joint intraday account histories.

## Selection, historical validation and promotion (conditional, never automatic)

Only a primary surviving design+immediatebench may be selected in a SEPARATE committed selection record
before running ONLY that frozen rule and matched causal reference on2023+ ONCE. Call it previously seen
historical validation, never fresh holdout. No tuning after that look. Freeze eligible matched placebo
universes/seeds and the validation runner before returns; do not add an alternative selected rule.
Full2018-26 native net trade t must clear shared metrics.t_threshold(N_items) OR DSR>=.95, with positive
design AND validation. Retain current repository N_items and prior author/v2/t6 selection history; show
dependence/selection sensitivity, not a favorable unadjusted selected headline.

Random-time AND random-side placebos each require p<=.05, SAME stop/target/time-exit/reentry protection,
calendar/coverage/nativefees as primary. Use shared resampling/MC engines. If any actual filter-subset is
examined, total BASE/kept/removed net and removed t plus1000matched random subsets with IDs/paths are mandatory;
cap-dependent/overlapping diagnostic subsets are not executable returns. SHORT_EXEC vs BOTH has distinct
timelines, so no false subset profit identity or inherited posthoc short-mask claim.
Repeat eligible book rows for frozen validation/full common coverage, at most2026-07-07 for complete retained
current19 source; postcutoff candidate alone cannot imply complete-book evidence. Require fresh independent
raw-spec checker before promotion, actual MC-list confirmation later, and only after all passing gates save
a PowerLanguage draft under agents/codex/ for Claude. Never live deployment.

## Artifacts and immutable run identity

Code: `analysis/codex_hunt_v2_fvb_short_gross.py`, later separately committed stopped/bench code.
Output/cache ONLY `analysis/outputs/codex_hunt_v2_fvb_short/`; evidence/report under agents/codex/.
Bind candidate/family ID, this prereg commit, implementation commit/SHA, dependency/input hashes, calendar/
schema versions, exact exclusions/unresolved opportunities, cost/settings/seeds and dependency versions.
Retain all failures/controls, gross screens and counters. Use no old runnable FVB module import, no shared
ranking/plan edits, no Claude writes, no watcher/t6 restart, purchases/accounts/live settings or messages.
At cumulative60evaluations OR10hypotheses: final summary then pause continuation6adea9fee9c88191a45399d233743746.
