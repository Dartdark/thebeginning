# Three-paper pressure strategy build: no qualified candidate from completed batches

Summary: Built and tested causal NQ adaptations of the uploaded pressure/jump papers; the screenshot rule is unknown.
First five batches /15 definitions fail their frozen design gates. The only profitable selectable, RIDGE_BOOK,
earns $6,057.25/NQ but only $245.74/MNQ proxy over2018–22, PF1.056, t0.583; four-tick stress loses $7,007.75/NQ.
No version has earned later-history validation, executable MultiCharts code, account testing or a VB-protection claim.
The two-hour pre-event memory extension is being prepared prospectively; preparation is not a result.

Author: Codex. Active user build mandate, 2026-11-10; separate from paused scout/lab programs and budgets.
Source review: [papers and screenshot reconstruction](pressure_papers_reconstruction_20261110.md).
Reproducible aggregate: `analysis/codex_pressure_study_20261110_report.py` ->
`analysis/outputs/codex_pressure_study_20261110/all_definitions.csv` and its source-hash receipt.

## Rule and measurement

Native NQ minute prices,total,buy/sell2018–22 are hashed and validated. Five-minute bars require all five constituent
minutes; no stale flow filling or legacy-price splicing. ET-close labels convert to CT-close. Training normalizations
and scalers use past data only; targets mature at their entire scheduled horizon. Signals are independent of future
execution/label completeness. Unknown held paths block advancement rather than becoming successful no-trade dates.

Common market-entry geometry: one full minute after a completed decision, next-row open; fixed stop at .10priorATR
for payoff models or adverse event/confirmation extreme plus one tick, capped at .15ATR for residual models.
Target .3R tick-rounded,30minute horizon, flat14:55CT, one position/max4actualentries daily. No averaging or break-even
stop. Resting-entry batch instead freezes limit prices and reserves a slot during delayed order life, max4submissions.

Market commissions $7.25/NQ round trip plus1tick per market/stop fill; MNQ price proxy $1.24 round trip plus .50/fill.
Every target needs one NQ point trade-through. Four-tick cost and stop-first ambiguous-bar stresses are mandatory.
Passive quotes require strict nonmarketability, one-point-through fill, delayed activation/expiry and conservative
fill-bar target chronology; passive cost stress differs and is separately labeled. These are bar-model assumptions,
not verified actual NQ/MNQ quotes, queue positions, receipt latency or broker fills. No native micro claim.

## Completed trials: design2018–22 only

All dollar figures below are net per one NQ. Controls remain unselectable. Every executed definition counts, including
failed and repeated-baseline definitions; older pressure/absorption/book searches remain in the selection history.

| Batch / variant | Role | Trades | Win% | Net/NQ | PF |
|---|---|---:|---:|---:|---:|
| Residual RESID2 | primary |1300|67.92|−35,875.00|0.688|
| PRICE2 | control |1500|69.20|−34,030.00|0.722|
| NO_CONFIRM | control |2066|63.94|−63,733.50|0.597|
| Monthly RIDGE | primary |128|73.44|−4,333.00|0.786|
| Monthly HGB | alternate |752|72.61|−18,802.00|0.832|
| HGB_PRICE | control |770|74.29|−9,922.50|0.907|
| Resting L1 | primary |326|57.67|−16,223.50|0.557|
| Resting L2 | alternate |342|49.12|−18,339.50|0.370|
| MARKET | control |925|63.03|−32,126.25|0.636|
| ES-conditioned FULL | primary |1437|67.64|−50,403.25|0.630|
| COMMON_ONLY | control |1471|68.12|−42,469.75|0.671|
| FLOW_ONLY | control |1298|67.95|−35,910.50|0.687|
| HGB_BOOK | primary |878|73.23|−10,325.50|0.921|
| RIDGE_BOOK | alternate |699|76.39|+6,057.25|1.056|
| HGB_NOBOOK | control |743|73.49|−11,906.75|0.886|

The saved `metrics.csv` per batch contains whole/long/short/year trade counts, win rate, gross/net/costs, trade and
daily-dependence t-statistics, Sharpe, Sortino, PF, Calmar, Ulcer and closed-trade drawdown. Full ledgers, calendar-zero
daily series, predictions, fits, exclusions, code/input hashes and design decisions accompany those metrics.
Closed-trade drawdown is not intraday account drawdown. No missing recent-year rows are invented.

RIDGE_BOOK has only three positive design years, $11,330.50 closed-trade drawdown/NQ and daily NW5 t0.490.
Its one-MNQ proxy earns about35c net/trade. Positive net alone therefore fails the precommitted evidence threshold.
It is not selected, scaled up, promoted as an independent factor, or passed to account tests.

## Protocols, code and outputs

| Batch | Frozen protocol | Main source | Output below `analysis/outputs/` |
|---|---|---|---|
|1|67fbba5d; pre-outcome engineering QA258badc7|`codex_pressure_build_20261110.py`|`codex_pressure_build_20261110/batch1_design_qa2/`|
|2|c852212a|`codex_pressure_learning_20261110.py`|`codex_pressure_learning_20261110/`|
|3|0d61f59e|`codex_pressure_passive_20261110.py`|`codex_pressure_build_20261110/passive_design/`|
|4|8e405d69|`codex_pressure_market_20261110.py`|`codex_pressure_market_20261110/`|
|5|e898078b|`codex_pressure_book_learning_20261110.py`|`codex_pressure_book_learning_20261110/`|

Matching evidence and exact plans live under `agents/codex/evidence/` and `plans/`, names pressure_build,
pressure_learning,pressure_passive,pressure_market,pressure_book_learning with suffix20261110.md.
Batch1 initial binding-only run was interrupted before any outcome artifact because repeated roll-calendar calculation
consumed CPU; its interruption receipt remains. The frozen engineering amendment caches identical date flags and fixes
unknown time-exit tails/empty stress schema. It does not change economic rules after a result.

## Placebos, validation and account stage

No selectable clears basic design gates; later placebos/bootstrap/recent history and account simulations are unearned.
No selected version, adopted size, pass rate, blow-up reduction, payout estimate or actual VB/ONB offset is established.
The candidate would have to earn profit before an incumbent loss breaches the account; later same-day gains cannot
rescue it. Do not substitute annual correlation for this timestamped question or run an old account model for a table.

Any future earned account stage must refresh Claude's actual roster. The inspected current reference25ca9556 uses
VB15MNQ, ONB risk2750, Bridge5, EOS1250, Twin cap1v2.1 twoMNQ, DTv4 twoMNQ, with integer sleeve-level finish sizing.
Legacy150K research base with VB20/noDT is a different portfolio; older engines also use21sessions, fractional finish,
clipped DLL or filled missing paths. Common native event-path/30calendar expiry/actual DLL overshoot are prerequisites.

## Data and independent verification limits

Input census/reconciliation is real, but original native contract/build/roll/receipt provenance remains incomplete.
Book snapshots add an additional unresolved source-vintage gate: historical GetAt(BarKey) is not proof of original
availability, and exporter files can be deleted/rebuilt during recalculation. All515,156 same-key closes and flows match
native exactly; eleven unsupported quote rows remain unknown. That establishes alignment, not causal vintage.

Owned source search found no actual bridge DLL/history cache/builder/manual or native priced-ladder/event stream.
The OF exports supply top/depth/wall scalars; two largest walls cannot identify nearest occupied price levels, and
aggregate depletion cannot order additions/cancels/replenishment. Stored search and static QA receipts are in
`agents/codex/inputs/pressure_book_20261110/`. No paid access, live/VPS action, API-key handling or notification occurred.

Independent agents audited source clocks, model isolation, replay chronology and planted fixtures. This is code QA,
not independent raw-spec reproduction of economic returns or native MultiCharts acceptance.

## PowerLanguage differences

No deployable PowerLanguage strategy was produced because every completed strategy fails the economic gate. Python
research code is complete for the tested rules and preserves all failures. A profitable simulator claim cannot be made
true by porting a rejected rule. No live strategy, chart input, size, trailing stop, broker or monitoring setting changed.
