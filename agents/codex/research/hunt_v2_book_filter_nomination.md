# New current-book filter nomination: TEST for preregistration

Question: does a fixed, completed opening15-minute price/classified-flow disagreement identify whole
Swing Target v3 days to skip, while preserving both parent orders, cap, entry, stop/target/BE and exits?
No rows, trade-list bodies, prices, financial arrays or new returns were read for this nomination.
No strategy/source module was imported or executed. New hypotheses/screens/evaluations:0/0/0;
root owns registration/counters. Checkpoint:3/60 evaluations,2/10 hypotheses,2 gross screens.
H01/H02/I01 remain closed; this is not a LDF repair or FVB capacity-mask study.

## Source and current-book check

Read AGENTS.md, BUILDER_BRIEF.md, LESSONS.md, RESEARCH_CONTROLS.md, TASK_strategy_hunt_v2.md and progress.
Source pin7f0800f, fetched by root, was inspected through git without branch changes or Claude writes.
The adopted personal/funded sources are unchanged from615485f; personal19 includes STv3/PTv2.
Full source commit:7f0800ffc04d56bd878750369a4abc2316ee01d8. Exact parent path:
`funded_strategies/NQ_Swing_Target_v3.txt`, Git blobb5be0d0c235e8cb11f464b78d1d4751fe328f6e9,
SHA25688689848107edfc2cd4f704b0b5f9030b7695a92dcade38ec112f3b2f8509377.
Latest TIER_LIST/MINED_INDEX and the following exact definitions were consulted before nomination:

| Source | Exact scope relevant to novelty |
|---|---|
| analysis/orderflow_test.py REPORTS and parts2/4 | Old roster VB,ONBML,EOS,MON,LDF,NFP,VCS,ONBADX; opening09:00/09:30 standalone flow/direction studies and side-at-entry cumulative/30minute agreement. No ST/PT leg |
| analysis/bridge_filter_scan.py and bridge_filter_scan2.py | Explicit T.strat restriction VB,ONBML,MON,EOS,LDF; cumulative delta/last30 and other MBO/GEX indicators. No ST/PT leg |
| analysis/moc_orderflow_test.py | Later14:50 auction-follow filters, not the new ST first15-minute whole-day predicate |
| analysis/fc_2b_test.py at7f0800f | FC2B uses sum(V*(C-O)/max(H-L,.25))/sum(V) over08:31-09:00, standardized against60days. This is a candle-volume proxy, not actual exported buy/sell classification fields |
| funded_strategies/NQ_Swing_Target_v3.txt | Parent activates paired stop orders at08:45 close; earliest next bar is labelled08:46. One parent fill/day, both resting entries cancel after first fill. Twenty stored RTH ranges, not ATR14/true range |
| Local codex_swing_engine.py | Existing shared paired-stop/causalBE/entrybar/worse-gap/target-through infrastructure, but its literal old-v2 carry/next-observed behavior is not an already certified v3 replay |
| Current book and saved bench maps | STv3 is adopted; new question is marginal filtration of that current leg, not rediscovering its old t-stat or repeating its confirmation |

The scoped source check found no exact ST/PT opening15-minute exported-volume/price whole-day filter.
This is not a universal novelty claim. Generic flow agreement has extensive prior selection, including
H01's closed LDF strict30 failure; retain those trials and old opening-flow studies. ST author parameters,
BE selection, old Python/MC outcomes and2023+ are already seen history. A newly registered filter does not
restore a fresh holdout or reset the archived t6 or current v2 counts.

## Why whole-day gating matters

Cancelling only the contra-flow ST stop can leave room for a later opposing fill absent from BASE.
A masked BASE short/long ledger would then be an invalid executable return stream. The proposed predicate
is known BEFORE either parent entry may activate and either keeps the ENTIRE parent day or disables ALL
parent entries for that day. Every kept day's two-sided state/cap/trades remain identical to REPLAY_BASE;
removed days have no candidate entry. No side-conditioned free capacity or later replacement signal.

Proposed primary: price=C08:45-O08:31; flow=sum(volume-downvol) over all15 completed native-equivalent
08:31..08:45 rows. Keep if the product is nonnegative; drop only strict disagreement. Observed P/D zero
with strict valid source and positive aggregate volume is KEEP_KNOWN_NEUTRAL. Incomplete/invalid/mismatched
classification or zero aggregate volume is KEEP_UNKNOWN, never false agreement or a favorable deletion. Exact source clock/schema,
volume=upvol identity, native-total-volume/range/close checks and completeness must be frozen before data.
No threshold/window/side search or later availability reinterpretation. A15-minute filter with1-minute
parent execution fits the user's accepted signal timeframes.

## Required parent/source audit before gross, after economic preregistration

Do not silently use old CODE_BE results as v3. Freeze a raw-spec REPLAY_BASE using the current v3 source:
two prior stored RTH high/low levels; parent twenty stored RTH range mean; source early-break disarming;
paired stop entries; target.35/stop.70/BE.30 times parent range; one fill/day;14:59 next-bar-market exit.
Known calendar skips are applied before entry to both REPLAY_BASE and filtered strategies, including
Good Friday/early closes, with no late-bar fallback or unprotected entry. The v3 header mentions Good
Friday but its IsHol body contains no Easter/Good-Friday calculation. Report this implementation effect
against the published MC reference, never as filter alpha. Preserve source storage semantics across
short sessions or explicitly document any unavoidable replay difference before returns.

Audit raw entry geometry/source clock and2018-22 MC ENTRY parity before gross, after the economic
preregistration. Read MC entry metadata only, never its exit price/net; those are gated until gross PASS.
Use a separate ENTRY-ONLY state extractor for gross: do NOT call codex_swing_engine.replay/_run or a
stopped engine before the gross gate. The gross fixed exit is native openj900, labelled15:00 but
wall14:59, matching the parent's14:59 decision/next-bar-market convention. Only after gross PASS use
source-controlled native-cost and target/BE fill logic. Quantify ambiguous
double-level/intrabar paths, missing references/held bars, worse gaps and target-through. The retained
MC conversion/source fee semantics must be bound before a native repricing, not inferred from file names.
Any fatal input/execution issue blocks the test; no favorable old headline supplies missing evidence.

## Proposed finite experiment, not execution authority

Evidence: agents/codex/evidence/hunt_v2_book_filter_nomination.md (eight questions, TEST for preregistration).
Root's final at-most5 stopped configurations are MC_PUBLISHED reference, REPLAY_BASE, OPEN_AGREE primary,
and matched BASE/primary one-minute activation-delay stresses. The earlier unexecuted PRICE_UP/DOWN
proposal is superseded before data; frozen matched-subset strata include opening-price sign to address
direction confounding. REPLAY_BASE remains the price-only parent. Nominal strategies share identical
source/coverage/fees/parent exits. No alternative may rescue a failed OPEN_AGREE primary.

First run only frozen RAW_NO_STOP: first parent entry/day to native openj900(wall14:59), no target/BE/stop P&L. Show base/kept/
removed gross, years/sides, source availability and missing-path audit; primary mean>=4.48/MNQ,>=100 kept
events,>90%known flow on parent entry days and complete relevant paths under root's frozen rule.
The owned2017 archive may warm parent features only after registration; no2017 trades or assumed full-year
coverage. No overnight input is needed for RTH references/entries. This is not stopped strategy performance.
Only after gross passes run the frozen stopped designs. Filters require total BASE/kept/removed profit,
removed mean/t and1000matched random subsets with IDs/paths. Stop a failed hypothesis, not the hunt.

After design PASS, immediate current-book BASE/ADD/REPLACE/EMPTY at whole-contract ST slot size, paired
histories and current-source uncertainty envelopes before additional robustness. Only after committed
selection may the selected primary and matched control inspect previously seen2023+ once. Promotion
needs full-history native t-or-DSR, both-period positivity, identical-exit time/side placebos, dependence/
selection checks and a fresh raw-spec checker. This nomination is not a qualifying book improvement,
funded/evaluation claim, trading approval, PowerLanguage permission or live-system action.
