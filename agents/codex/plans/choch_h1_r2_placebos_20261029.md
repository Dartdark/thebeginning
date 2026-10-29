# Hourly R2 CHoCH: frozen timing and direction diagnostics

User approved the recommended unchanged-foundation random-time/random-side follow-up. This is a bounded diagnostic of a previously failed design, not a new alpha strategy, a filter search or a restart of t6/Hunt v2. Commit/publish before any new control returns. No 2023+ returns or account benches in this task, even if a diagnostic p-value is favorable: original economic and complete-data gates already fail.

## Evidence sheet

1. **Mechanism:** the user's hourly price-structure reversal has no identified forced participant. Hypothesis: the confirmed opposing-swing break chooses direction/time better than matched random choices under the same bracket and calendar.
2. **Prior evidence/selection:** full original 2018–22 foundation408 resolved trades, net$4,896.08/MNQ, trade t1.218/NW5 1.194, one unresolved path. Four subsequent range/alignment filters failed and remain closed. Six prior structural variants/twelve economic definitions including execution references plus four filters =16 prior inspected definitions; do not reset this history.
3. **Who pays/how big:** unknown; controls can test directional/timing specificity but cannot identify a forced flow or validate profitability on their own.
4. **Liquidity/shared losses:** NQ directional/chop exposure, overlap SwingTarget/PAPERTREND and possible VB/DT/RS losses; no demonstrated account hedge.
5. **Risk/execution:** one MNQ, prior confirmed swing stop,2R target, variable time-exit payout, wide swings and gaps. No size/stop cap/side/window tuning.
6. **Evidence decision:** TEST the user-requested diagnostics; no candidate promotion follows. Save nulls/failures and end this task after reporting.
7. **Potential homes:** personal19 and four Apex plans remain unqualified. Current personal19/ST slot and50K T_ONESIDE fade vs150K/personal RS definitions are unchanged by current source review; no measured ADD/REPLACE/EMPTY gain is claimed.

## Fixed foundation, sources and clocks

Same hourly R=2 strict pivots and HH/HL/LH/LL/CHoCH state as `codex_choch4h.signals`; all eligible raw events, not only previously resolved/admitted trades. Use the hash-bound11 reconciled DAY/ON files,2017 warm-up/2018–22 design only. Preserve/reproduce full-source corrected baseline using `codex_choch_filters_execution.ledger`. No source/cache/root book writes.

Normal eligible completed-hour decisions09:00–14:00 CT; repo early-close09:00/10:00. Entry OPEN(signal+2), flat OPEN of close-labelled15:58 normal/11:30 early. Native MNQ$2/point, round-trip commission$1.24 plus slippage$1.00, total$2.24. Same shared minute `_walk`, active entry-bar protection, worse stop gaps,1-point target-through and gap-at-entry charged immediate round trip. No forward-filled unknown execution. Same nearest-extreme primary; retain stop-first collision stress outcomes.

## Coverage analysis, not a trade filter

The full source baseline has an unknown path. For an interpretable finite null comparison, define an **audited-session diagnostic sample** before calculating controls: every expected-open minute from labelled09:00 through planned flatten and the flatten open must be observed. Scheduled pre2021 pause is not missing. Exclude entire incomplete sessions equally for candidate and every control, retain excluded session dates/missing counts and full-source baseline ledgers/P&L. This uses future *data completeness* as an analysis restriction; it is **not an executable entry feature**, new strategy or evidence that deleting these days improves alpha. Never promote this covered-sample t as the full foundation t. Prior context gaps still reset signals normally.

Take all causal raw eligible events on these audited sessions; rerun the actual baseline. Do not select events on realized profitability, exit or random result. No random draw is retried or deleted. Unexpected unknown controls stay unknown; print counts and invalidate a complete-result claim.

## Four inspected definitions, three fixed nulls /1,000 paths each

BASE is reused unchanged. For each event define original potential fill P at its usual signal+2, original swing stop S, original side b, original risk r=b*(P−S). This value is known at original fill, not earlier. Controls keep this risk distance and2R/time-exit/cost method; they do not retain an exit chosen by the original path. They rerun the actual minute path. A randomized bracket can be reflected/translated and is therefore not itself a previous-swing strategy. If r<=0, original and matched brackets pay an immediate zero-gross round trip; missing P remains unknown.

1. **Random side (RS):** independently draw +1/−1 with probability1/2 at each actual signal. Same scheduled decision/entry. At P use stop=P−drawnSide*r and target=P+drawnSide*2r. Original side outcome reproduces the foundation. Direction and risk are available at this fill. This tests direction conditional on original signal times/risk, not independent calendar-day selection.
2. **Random time (RT), conditional diagnostic:** for each actual event draw uniformly from all legal decision hours on its same calendar session, including earlier/equal/later. Preserve actual event side and r; at randomized fill Q translate stop=Q−b*r, target=Q+b*2r. A draw earlier than the actual signal uses information that did not yet exist. **This is an expressly noncausal, risk/date-matched counterfactual, not an executable alternative strategy or promotion placebo.** It measures clock association conditional on selected days/risk; it does not test day selection. Retain earlier/equal/later counts.
3. **Random delay (RD), causal timing diagnostic:** draw uniformly only from actual signal hour and later legal hours on that session. Preserve side/risk as above. At an equal fill P, risk is available immediately; a later fill follows P. No earlier event information is used. Label it post-signal delay, not unrestricted random-time superiority.

Draws use NumPy SeedSequence(20261029).spawn(3), listed RS/RT/RD order.1000 paths per null, all retained. Preassign draws per original event; sort scheduled requests by randomized entry time, ties earlier original signal then event ID. Admit at most one position: requests at/before previous exit are blocked and never resampled. A missing entry blocks through session flatten. Pending future requests may coexist; only scheduled admissions matter. These paths test scheduling policies, not exact equal realized trade counts; report attempted/admitted/blocked counts, minutes held and side exposures. RT chronology remains a hypothetical scheduling calculation because of its earlier-signal information.

Build an immutable outcome catalog using shared execution for every event/legal scheduled hour with original side, and opposite side at original hour. Retain each outcome's original/scheduled clocks, risk, stop/target, entry/exit, gross/fees/net, state/collision flags. Original-clock/original-side outcomes must match independently reconstructed baseline admission. A path stores all chosen outcome IDs, admission flags and daily increments, allowing exact full-ledger reconstruction without storing duplicate million-row text. These compact ledgers and all3,000 paths are saved, not just summaries/best seeds.

## Statistics and decision

Primary statistic = total native-cost net of each complete one-position path versus coverage-matched BASE. Use shared `metrics.perf`, tstat/NW5 and `resampling.max_dd`; integers cents for rank/ties. Raw one-sided p=(1+#nullTotal>=baseTotal)/1001, ties included. Report p for lower DD and joint profit/DD as diagnostics, all1000 path totals/count distributions,5/50/95 quantiles and BASE rank. Stop-first catalog/path stress shares exact choices; extra$2.24/trade cost stress reported without seed/model selection. Retain baseline sides/year, five metrics, risk/time exits and full-to-covered attribution.

If any path is unknown, keep it and show p-rank bounds [(1+knownExceed)/1001,(1+knownExceed+unknownPaths)/1001]; do not claim a fully specified null distribution. Full-source unknown BASE has no exact complete total, so any full-source resolved subtotal is reference only. Coverage nulls must not repair that issue by implication.

Both primary named controls use rawp<=.05 only as a **diagnostic** threshold; causal direction/delay evidence additionally requires RS and RD each<=.05. RT cannot establish a causal pass. Report conservative min(1,19p) context for16 prior inspected definitions plus these3 fixed null questions; this is not a repo-wide promotion adjustment or fresh holdout. The3000 draws are not3000 new market histories/alpha trials. No adoption follows regardless of ranks: full foundation t1.22, source limits and historical selection remain.

End with all five homes (personal,50K/150K funded,50K/150K evaluation), no claimed account gain when not tested. Do not run another filter, side/year rescue,2023+, account engine or PowerLanguage in this task. Save reproducible code/ledgers/reports under Codex allowed paths and selectively publish only derived artifacts to codex/work with fresh expected-head checks. Uploaded raw source CSVs stay local.
