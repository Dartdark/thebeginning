# Opening price/classified-flow agreement on Swing Target v3: TEST for preregistration

Summary: test a whole-day gate on the CURRENT adopted STv3 using completed08:31-08:45 exported flow and price.
The new question is marginal filtration of an existing leg; no ST/PT-specific counterpart was found in prior scans.
It preserves both parent orders/cap and does not inherit a selected ST or FC2B headline.
Stop-liquidation/competing opening inventory is an unmeasured causal hypothesis, not identified forced investors.
TEST means eligible to write and commit a finite plan, not data admission, a design pass or trading permission.

Sources: source7f0800f, TIER_LIST/MINED_INDEX, current personal/funded definitions,
funded_strategies/NQ_Swing_Target_v3.txt, analysis/{orderflow_test,bridge_filter_scan,bridge_filter_scan2,
moc_orderflow_test,fc_2b_test}.py; local analysis/codex_swing_engine.py; nomination source map
agents/codex/research/hunt_v2_book_filter_nomination.md. No new rows/returns or module executions.
Current v2 checkpoint3/60 evaluations,2/10 hypotheses,2gross screens; sheet adds0/0/0. Prior t6 remains65.
Prior ST author/BE/MC selection and generic OF/FC2B/opening-flow/H01 selection remain in multiplicity.
Exact parent source:7f0800ffc04d56bd878750369a4abc2316ee01d8:funded_strategies/NQ_Swing_Target_v3.txt;
Git blobb5be0d0c235e8cb11f464b78d1d4751fe328f6e9;
SHA25688689848107edfc2cd4f704b0b5f9030b7695a92dcade38ec112f3b2f8509377.

## 1. Who trades, and what forces or causes the trade?

The parent trades breaks of known prior two-session extrema. Shorts with protective buy stops near the
upper extreme, longs with sell stops near the lower extreme, and other breakout participants can generate
price-contingent liquidation/continuation demand. This is plausible, not observed stop inventory or a
verified mandate. Opening transactions also reflect inventory transfers and new information. If price
and the classified signed opening tape oppose, competing/passive absorption could make later breakouts
less reliable, while concordance could indicate a more persistent directional repricing.

No specific fund or compulsory cash-auction order is identified. The first15-minute NQ tape is NOT a
Nasdaq opening-auction imbalance feed, and its buy/sell fields do not reveal investor identities or final
unhedged positions. The filter prediction is weaker than a measured forced-flow claim: parent ST's
whole-day expected outcome should be worse on clear opening price/flow disagreement. That falsifiable
incremental question on an adopted leg justifies a small preregistered test; it does not establish a
new standalone flow mechanism or guarantee that the original breakout cause exists.

## 2. Direction, size and timing known before entry

Proposed primary is a whole-day admission flag: P=C08:45-O08:31, D=sum(volume-downvol) over15 complete
classified-flow source minutes corresponding to native close labels08:31..08:45CT. DROP only if P*D<0;
otherwise KEEP. Observed P=0 or D=0 is KEEP_KNOWN_NEUTRAL when all15 source bars and positive aggregate
quantity pass the strict audit. Incomplete/invalid/unmatched flow or zero aggregate quantity is
KEEP_UNKNOWN. These states remain separately counted; no unknown is labelled observed agreement.
Require volume=upvol and native buy+sell total/price matching under a frozen audit; do not treat volume
as total traded volume. No future whole-day availability or partial-sum substitution.

|Clock|Research convention|
|---|---|
|Prior parent references|Past stored RTH high/low/ranges, known before today's session|
|Feature event time|Each completed08:31..08:45 native-equivalent bar; latest is08:45CT|
|Feature available_at|08:45CT under idealized zero receipt/processing delay; actual receipt not verified|
|Decision_time|08:45CT close, before first parent stop may activate|
|First executable fill|Original parent stop, no earlier than next minute labelled08:46, possibly later|
|Timezone|America/Chicago native close labels; source ET mapping/DST must be bound and audited|

One whole MNQ in the initial personal question, one position/day, no resizing or averaging. Keep ALL
parent tickets/orders/state on kept days; suppress ALL entries on removed days. No directional order
cancellation followed by a later new entry. Actual residual notional cannot be estimated before data:
observed classified volume is not forced inventory or an executable net dollar-order estimate.

## 3. Does it reach the traded contract?

The measured classification concerns NQ itself, not a stock-level effect assumed to aggregate into an index.
MNQ shares the Nasdaq-100 exposure, but NQ bar observations do not prove MNQ spreads, stop fills, queues or
receipt timing. Counterparties may offset through QQQ, baskets/options and other futures. The gate tests
incremental information; no assumption that every classified contract is compulsory demand is made.

## 4. Inputs, independence and feasibility

|Input|Owned/source definition|Known before test|Audit still required after committed plan|
|---|---|---|---|
|Opening NQ OHLC|Native annual one-minute exports/shared Grid24|08:31open/08:45close causal before entry; no row read here|Actual dates/clocks/OHLC/source duplicates and no future eligibility|
|Classified opening volume|Owned OF volume/upvol/downvol; old source CT=ET-1h, volume is buy/up-classified amount|Existing H01 work established a strict-source adapter; this sheet does not rerun that audit|All15 bars, semantics, nonnegative finite quantities, volume=upvol, native totals/price matching, source-era/receipt limits|
|Parent STv3|Current adopted source7f0800f|Paired entries08:45close;1/day;20stored RTH ranges; target/stop/BE and flat rule|Freeze raw BASE, shared stop-entry/BE engine, actual MC-entry parity and all implementation differences before gross|
|Current personal19 and ST MC reference|Existing retained afde088/92b1d4c source/MC paths, same adopted definitions7f0800f|No roster change; no financial CSV body read|Native fee/gross bridge, book marks/coverage and uncertainty envelopes; actual whole-contract slot|

The increment is exported classified-volume disagreement beyond the original price-only parent, not a
new price indicator or an existing FC2B ticket composite. FC2B's source uses a candle-volume proxy over
a different opening window; do not describe it as the same actual flow input. Prior generic opening-flow
and plan-OF scans are still related selected research. Unknown states never get dropped for availability.

## 5. Costs, clocks and book fit

Research MNQ cost:1.24RT commission plus0.50 per market/stop fill; raw-window round trip2.24, gross hurdle4.48.
Limit targets need target-through and correct separate fill/slippage treatment; do not subtract a second
spread or borrow NQ-net/10. Prespecify a cost/latency stress before returns. Parent stop.70,target.35 and
BE.30 times20stored RTH range remain unchanged; nearer-extreme path/worse opening gaps and active entry-bar
protection need a frozen shared-engine adapter, not optimistic price touches.

The gate is15-minute, parent execution1-minute; accepted timeframe scope is preserved. It does not exploit
the stale01:00-03:00empty-hours claim. ST is already in personal19 and current funded swaps. This question
primarily REPLACES its slot with a filtered version; adding an extra same-parent copy is an explicit ADD
control, not independent diversification. Signal days must not be chosen from whether other legs were flat.
Known calendar skips including early/holiday closes apply before entry to replay+filter; exits before15:59CT.

The adopted v3 header says Good Friday but its IsHol body has no Easter/GF calculation. Do not silently
present a stricter replay as published-book alpha. Also preserve exact20stored RTH range/history semantics;
the old literal v2 engine's carry/next-observed fallback is not a certified v3 replay. Raw BASE versus MC
ENTRY-reference differences and coverage are an explicit pre-gross audit after registration. The gross
phase must use an ENTRY-ONLY parent state extractor, not replay/_run or any stopped-P&L engine. MC exit
prices/net fields remain unread until gross PASS; only entry metadata supports the earlier parity audit.
Gross fixed exit is native openj900(label15:00,wall14:59), matching literal14:59 next-bar-market timing.
The owned2017 warmup archive may build features only after preregistration, no2017 trades; do not assume
complete2017 coverage. RTH day exports suffice; no overnight-price input is required for these references.

## 6. Power before returns

The old published parent study had roughly340 design events; that is already-seen planning context, not a
new count for v3 or this filter. Exact kept/removed/known/unknown counts are unmeasured. If approximately
200-300 events remain and per-MNQ SD were50-100, IID net mean for t≈2 would be roughly5.8-14.1 before
adding2.24 costs for gross. These are stated assumptions; clustering/selection raises requirements.
Require root's>=100kept raw events,>90%known flow on parent entry days,mean>=4.48 gross and complete paths.
Five-year yearly/side stability,
removed-profit and matched-subset evidence are mandatory; a raised per-trade average alone is not a pass.
No expanding the window, relaxing completeness or adding2023+ to rescue failed design power.

## 7. Prior tests and falsifiers

Scoped source search found no exact ST/PT whole-day actual-flow opening predicate. Old orderflow scans cover
VB/ONB/MON/EOS/LDF/NFP/VCS; Bridge scans restrict VB/ONB/MON/EOS/LDF. Old standalone09:00/09:30 flow trades,
H01's closed LDF filter, MOC orderflow and FC2B candle-proxy selection are prior related evidence, not erased.
ST's BE/formula/MC selection and later returns are already known;2023+ remains historical validation.

Fail if raw gross/cost/complete-path gate fails; if removed stopped trades do not lose money; if total kept
net does not improve over BASE; if1000matched subsets show no joint profit/DD advantage; or if no current
plan improves over BOTH BASE and EMPTY immediately after design pass. The final root plan freezes
MC_PUBLISHED, REPLAY_BASE, OPEN_AGREE and matched BASE/primary one-minute activation-delay stresses
(at most5 total). The earlier unexecuted PRICE_UP/DOWN proposal is superseded before data. Frozen
matched-subset strata include opening-price sign to control direction confounding; delay results cannot
rescue nominal failure. No post-result tuning.

## 8. Failure and diversification

|Question|Prediction before results|Evidence/falsifier|
|---|---|---|
|What removes the effect?|Opening inventory is absorbed, fresh later information dominates, classification has no independent content|No removed-profit/subset/placebo advantage|
|Liquidity role?|Parent stop entries and stop/BE/time exits demand liquidity; targets supply conditional liquidity|Actual native fills/queues/latency, worse gaps and target-through; no passive claim from label|
|Loss clustering?|Opening reversal/chop and later macro shocks can cluster ST losses; disagreement might remove winners too|Both sides/year/conditional joint losses, not high selected averages|
|Shared book losses?|ST/PT/DT/VB share RTH momentum risk; removing an ST day is not automatically a hedge|Current aligned personal/funded paths and paired outcomes|
|Offset before breach?|Unknown; a skipped ST trade does not itself pay cash before another leg breaches|Valid joint account chronology; daily correlation is insufficient|

## Decision and next gate

**TEST for a bounded exploratory preregistration of the incremental current-leg filter.** No dataset,
financial return or source audit is authorized merely by this sheet. Root must first commit exact parent
replay/source/calendar/fill policy, whole-day predicate, unknown treatment, gross gate, at most5 designs,
trial accounting and current-book controls. Audit raw BASE/MC ENTRY parity/source integrity after that
commit and before gross; target/BE/full-stopped parity waits until gross PASS. Fatal issues stop advancement.
Never inherit a source headline or call masks executable.

After gross and stopped design PASS, immediate current19 BASE/ADD/REPLACE/EMPTY with whole contracts and
paired histories/uncertainty envelopes before extra robustness. Only a surviving selected primary/matched
control may run previously seen2023+ once after a selection commit. Full native t-or-DSR/both-era positivity,
same-exit random-time and random-side p<=.05, dependence/selection checks and fresh raw-spec checker remain
required. No funded/evaluation improvement from daily proxies, no MC/PL/live claim and no paused-program restart.
