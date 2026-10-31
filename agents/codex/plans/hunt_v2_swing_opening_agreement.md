# H03: Swing Target v3 whole-day opening-flow agreement — preregistration

Evidence BEFORE data: `agents/codex/evidence/hunt_v2_book_filter_nomination.md` (TEST for preregistration).
Source review: `agents/codex/research/hunt_v2_book_filter_nomination.md`. No H03 price/flow/trade rows or
returns have been read. Parent source is7f0800f:funded_strategies/NQ_Swing_Target_v3.txt, byte-exact archival
copy under `agents/codex/inputs/hunt_v2_swing_opening_agreement/`; this is existing source, not a new PL draft.
Execution/writes ONLY codex/work. H01/H02/I01 remain closed, no t6 or template execution.

## New incremental question and selection history

On the CURRENT adopted Swing Target v3 leg, do opening price/classified-flow disagreements identify days
whose later two-sided breakout trades should be suppressed? Breakout stop liquidation and competing opening
inventory are unmeasured hypotheses; no investor mandate, actual forced notional or opening-auction feed is
identified. The test asks incremental information beyond an adopted price-only parent, not a new standalone
flow discovery or a composite of existing returns. Extensive old flow/FC2B/parent/BE/MC selection and already
seen2023+ history remain in multiplicity. Old flow scans excluded ST/PT; FC2B uses a candle-volume proxy.

## Frozen configurations (maximum FIVE; only one selectable)

|ID|Role|
|---|---|
|MC_PUBLISHED|Unselectable current adopted MC parent reference, native cost correction disclosed|
|REPLAY_BASE|Unselectable raw-spec parent with frozen calendar/native execution audit|
|OPEN_AGREE|Sole selectable whole-day gate on REPLAY_BASE|
|REPLAY_BASE_DELAY1|Unselectable one-minute activation-delay matched reference|
|OPEN_AGREE_DELAY1|Unselectable same-filter delay stress; cannot rescue nominal failure|

The earlier unexecuted nomination mentioned PRICE_UP/DOWN controls. They are NOT in this final preregistration;
no data or returns preceded this choice. REPLAY_BASE is the price-only baseline. Opening-price direction is
also controlled through the frozen matched-subset strata below. Delay is substantive execution robustness,
so both delayed configurations count if run. Fixed adverse-cost repricing of identical tickets is monotonic,
unselectable and separately reported, not another entry/exit configuration. No other thresholds/size/window.

Registering H03 makes3/10 hypotheses, with3/60 counted evaluations and2 gross screens initially. A failed
gross costs0economic evaluations but retains H03/screen. After gross PASS, only3 nominal configurations may
run on2018–22. The2 delayed configurations may run ONLY after nominal design+immediate book bench pass.
Count all actually examined references/failures; at most5 H03 configurations. Prior archived t6 remains65.

## Input allowlist and clocks

Native RTH source: `data/NQ_1min_2018.csv`..`2022.csv`, plus feature-only warmup
`agents/codex/inputs/ob_v2_bench/NQ_1min_2017.csv`. No2017 trades and no assumed full-year warmup. No overnight
or2023+ input is needed or allowed initially. OF allowlist: owned2018–22 source annual files used by the
H01 pure-source adapter. Bind exact paths/hashes before loading; never import old financial runners or
reuse their outputs. Use shared Grid24 with isolated allowed source links/cache, not g.trading/final-day
coverage to admit earlier entries. Validate actual dates/integer clocks/OHLCV/duplicate conflicts.

Opening feature uses native CT close labels511..525 =08:31..08:45, exactly15 completed minutes. OF ET
labels map to CT by minus60minutes (common US DST calendar); this is label conversion, not verified receipt.
Feature event/available_at/decision at08:45CT assumes idealized zero receipt/processing delay. Parent first
entry minute label526 opens at08:45wall time; actual intrabar fill time/latency is unverified. Record clock
fields and this limitation; mandatory one-minute activation stress tests a different execution allowance.

## Frozen whole-day predicate

P = native C525 - O511. D = sum(OF volume - downvol) over511..525. Known requires all15 matched complete
source/native bars, finite nonnegative classified quantities, volume==upvol, upvol+downvol==native total
volume, source/native closes within.25point, and positive aggregate classified total. No partial sums,
whole-day future availability flag or later revisions chosen from returns. Keep if P*D>=0. Drop ONLY strict
P*D<0. Observed P/D zero with valid positive-total source is KEEP_KNOWN_NEUTRAL; invalid/missing/mismatched
flow or zero aggregate classified quantity => KEEP_UNKNOWN, never a favorable deletion. Preserve raw source
availability/alias/price/total audits. The price prefix itself must be complete to determine parent geometry.

Keep/drop applies to ALL parent orders and tickets that day. Kept day: both original orders/state/cap remain
unchanged; removed day: both disabled. One fill/day prevents freed-cap later replacements. It is a true BASE
ticket subset. No per-side cancellation, resizing, new entry date, averaging or roster-flat entry filter.

## Parent entry-only reconstruction BEFORE gross (no stopped P&L)

Preserve v3 input parameters: Lookback2, RangeDays20, RTHOpen831, RTHClose1500, Start845, LastEntry1429,
Exit1459, Target.35, Stop.70, BE.30. References are the source's last20 STORED RTH high/low ranges, not14ATR,
true range,20normal-calendar slots or older rows stretched around missing stored sessions. Levels are extrema
of the latest2 stored sessions. At511, first native open/high/low must be inside levels inclusively. A strict
H>HiRef or L<LoRef through525 disarms. Emit both stops at525..869; first exact next minute526..870 may fill.
Gap-through entry fills worse native open; otherwise level. If both levels touch one minute, use existing
shared nearer-extreme path, ties high first, and retain ambiguous flags. One entry/day. Do not evaluate
targets/stops/BE or call codex_swing_engine.replay/_run in the gross phase.

Preserve v3 storage: at finite native900 store observed RTH extrema; if prior InRTH remains and first new-date
bar has CT<831, its backstop stores prior partial range before current session. First new-date bar==511
overwrites the old unclosed range literally; firstbar>511 can mix stale state. Preserve/audit the actual
source behavior, never silently fix it, and mark mixed/missing-start references unresolved. Known short
calendar references remain source partial sessions. Unknown gaps do not become normal-session ranges.

Trading calendar for BOTH REPLAY_BASE and filter: union of literal v3 IsHol and shared known holiday/early
calendar, including Good Friday/national mourning. Skip before entry. Literal v3 header claims Good Friday
but its IsHol body omits Easter; record this implementation difference versus published MC, not filter alpha.
No current-day final membership or late-bar fallback. For20 stored references used on BASE entry days,
normal sessions require all390 bars511..900. Known short sessions require observed contiguous511..last valid
RTH bar<=900, with extent/short-calendar status retained; no closed-market prints demanded. Internal gaps,
normal missing ends or mixed references remain flagged on retained entries and veto gross admission.
An unexplained NORMAL-session missing900 that literal next-date511 overwrites is also retained as a
lineage fault for the next20 actual stored-session updates (the maximum parent lookback), including the
current feature. This diagnostic does not insert, delete or reorder source history or remove events.
Known short-calendar missing900 alone is not such a fault. Literal trading skips such as a NORMAL Dec31
do not prove a short session; weekend references cannot qualify as scheduled short sessions. Invalid
nonpositive average range or coincident/reversed two-day levels also remain unresolved protective geometry.

An invalid otherwise-eligible native scan prefix stops search and remains unresolved, never skipped into
a next-observed entry. A first entry before later missing bars stays in the ledger; relevant held-path
coverage then determines the gate. Report all calendar/exclusion/reference/arming/order/gap/ambiguity IDs.

## MC ENTRY audit, not net-return inspection

Reference `agents/codex/inputs/rebound/plan_update_afde088/checks/candidates/swing_target/mc_trades_v3.csv`.
Only date,side,entry,t_in may be interpreted on2018–22 rows before gross. Parse date BEFORE numeric entry/
time; no exit price,gross,net or2023+ financial fields. Strict times: HH:MM[:SS] or ISOdate+time with row-date
identity; do not guess chart timezone/current date. Calendar differences retained. On common preknown
eligible dates, both directional matching fractions must be>=90% for date+side+entry within.25 and t_in
within1minute. Publish unmatched IDs and clock assumptions. Unparseable/duplicate/ambiguous entry metadata
blocks gate; old favorable t-stats are not parity evidence. Stop before stopped returns if parity fails.

## RAW GROSS gate first

First parent entry/day to exact native OPEN900(label15:00,wall14:59), NO stop/target/BE/fees/slippage.
Held coverage requires entry minute through899 complete; exit requires finite positiveO900 only. Later
H/L/C/V of exit minute are audit metadata, not future held-path vetoes. Missing endpoints/held bars,
otherwise-eligible native prefixes and unresolved references remain retained and veto admission.

Report BASE/kept/removed raw total/mean/t/SD/SE, counts, years/sides; zero unknowns visible. Raw gate is ALL:
>=100 kept events, kept mean>=4.48/MNQ, >90%known-flow fraction on BASE entry days, complete relevant paths/
references/prefixes, finite endpoints and the two>=90% MC entry matches. Native assumed RT1.24 commission
+0.50entry+0.50exit=2.24;2xcost=4.48. This is not native MNQ quote/listing/receipt verification. Failure closes
H03 before stopped/validation/bench/MC/PL. No threshold/window/reference/calendar/coverage rescue.

## Stopped design only after verified gross PASS

Commit stopped/native execution and benchmark implementation before returns. Run nominal MC_PUBLISHED,
REPLAY_BASE, OPEN_AGREE on2018–22 only. Reuse shared paired-stop execution infrastructure extended in a new
allowed file for v3 state/calendar; entry-bar stops/causal BE/worse-open gaps active. Distances.70/.35/.30
retain source multipliers; actual stop/target prices round to nearest.25tick, NumPy ties-to-even, disclosed
as native execution convention versus floating source/MC assumptions. Target requires1point trade-through;
gap beyond target fills the target limit conservatively. Native fees per contract:1.24RT; adverse.50 per
market/stop fill, no extra spread or target-limit slippage. Fixed4tick/fill stress:2.00 per adverse fill.
Use no missing-bar fallback, no hold past15:59/known halt; unresolved execution blocks results.

Show five metrics/MaxDD/trade t/daily NW5, long/short/year, gross/commission/slippage/net and break-even extra
cost per trade. Reconcile daily/trade/book totals, published-reference versus replay effects separately.
Require primary>=100 trades, total net>0, trade t>=2,dailyNW5>0,>=4/5positiveyears, kept net>REPLAY_BASE net,
removed net<0 and removed t<0. A larger per-trade average alone fails.

Filter test:1000 matched random kept subsets, fixed seed2026102603, strata(year,side,opening P sign,
entry_label_j<=660 versus>660, known/unknown flow). Preserve actual count in each stratum and selected
IDs/daily paths. Unknown/Pzero cells remain included. Actual primary must strictly beat>=90% jointly on
total profit AND drawdown. These are nonexecutable diagnostic subsets, not account portfolios. Matching
opening price direction explicitly tests incremental flow information without extra PRICE_UP/DOWN trials.

## Immediate book bench BEFORE extra robustness

Only if nominal design passes, current personal19 at1micro each: BASE adopted published book; EMPTY remove
its ST1MNQ; ADD=BASE+OPEN_AGREE1MNQ; REPLACE=EMPTY+OPEN_AGREE1MNQ. Also show EMPTY+REPLAY_BASE1MNQ to isolate
parent implementation effects. Current ST/PT IN, BB OUT; no stale future-aggressive/funded constants. Same
2018–22 dates/coverage/fees, paired5000 MC histories,252dayhorizon,20dayblocks, seed20261026. Shared MC/metrics
engines. Candidate row must improve return/DD versus BOTH BASE and EMPTY with paired5%difference>0, surviving
prespecified baseline fee/mark/coverage uncertainty envelopes; no small unbounded publication-method gain.
Quantify fee repairs/envelopes BEFORE the first bench using current bench-source note, not after favorable
returns. If no plan improvement, STOP before extra robustness/2023. Daily MC is not funded/evaluation evidence;
missing valid joint account paths preclude pass/payout claims, never create proxy-derived account gains.

After nominal bench PASS only: run the two registered design-period DELAY1 execution stresses, first stop
activation label527 instead526, same525 feature/early-break logic, last entry/exit unchanged. No later gate
reinterpretation. Require delayed filtered-minus-delayedBASE total net>0 and no fatal execution issue;
neither delayed result can rescue nominal failure. Fixed costs do not erase latency uncertainty.

## Selection, previously seen validation and promotion

Freeze/COMMIT selected OPEN_AGREE only after design+bench+delay gates, BEFORE only selected rule and matched
REPLAY_BASE run2023+ ONCE. It is previously seen historical validation, not fresh holdout. No retuning.
Full2018–26 native trade t>=metrics.t_threshold(currentN_items) OR DSR>=.95, positive design AND validation,
identical-exit random-time AND random-side placebos eachp<=.05, dependence/selection checks and fresh
independent raw-spec checker still mandatory. Retain old author/parent/flow/t6/v2 multiplicity and sensitivity
to unranked searches; a selected unadjusted t is insufficient. Full-book common coverage stops2026-07-07
under retained OT source; later candidate-only evidence is not a complete current book. No PowerLanguage
draft until all passing gates for Claude's MC check; no trading/deployment or changes to live/shared plans.

Artifacts: analysis/codex_hunt_v2_swing_opening_gross.py, later frozen design/bench scripts; outputs/cache
ONLYanalysis/outputs/codex_hunt_v2_swing_opening/; final report agents/codex/results/hunt_v2_swing_opening_agreement.md.
Bind prereg/code/dependency/source hashes, versions/eras, clocks, seeds, all failures/controls/IDs and counters.
At cumulative60evaluations OR10hypotheses, final summary then pause continuation6adea9fee9c88191a45399d233743746.
