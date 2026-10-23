# Kusho FAR final / v9: NEEDS DATA — personal-account research; supplied holding rules do not fit Apex

Summary: A directional candle/EMA signal places a limit order on a retest; v9 adds shorts in a declining regime.
Reported annual totals reconcile, but the historical net and S grade are not independently verified.
Both versions allow evening/weekend holds, and calculation settings plus entry/stop chronology are unresolved.
Obtain raw MultiCharts workbooks and the already-existing intraday version before account-level testing.
No strategy return screen, parameter variation, cache or account simulation was run here.

Sources: uploaded files preserved under `agents/codex/inputs/kusho/`; source review
`agents/codex/results/kusho_source_review.md`; inventory checked at Claude `e7c394f`.
Return trials: **0 new Codex trials**. The author describes optimization and multiple redesigns; the complete
external trial count is unknown. NEEDS DATA is not a rejection of personal-account research or permission to trade.

## 1. Who trades, and what forces or causes the trade?

The proposed finished-auction interpretation says a bullish bar with a limited lower wick shows buyer control,
and a retest offers a useful entry before continuation. V9 mirrors this for shorts in a declining daily regime.
The code observes OHLC and moving averages; it does not measure executed bid/ask auctions, order-book depletion,
mandatory hedging or a named participant's obligation. This is a price-pattern hypothesis, not a documented
forced-flow mechanism. No published effect size for this exact proxy is supplied.

## 2. Direction, size and timing known before entry

On completed 15-minute bars stamped 09:00-13:59 CT, the long signal requires close above open and EMA(50), and
open minus low at most 70 ticks. Leave a buy limit at that known bar's open for the next bar; v9 mirrors it for
shorts only when the prior session's 15:00 close is below its 50-close average and that average is falling over
five sessions. Those observations are causal. No flow dollar size or unabsorbed demand is known.

At the first calculation observing a fill, choose the most recent fractal swing from bars 2-10 back; if accepted,
use it as the stop and target three times its distance, with break-even after a reported half-R excursion.
Otherwise use 200-tick stop/target. Source checks omit a positive swing-risk requirement. Ordinary orders are
issued next bar; exact activation depends on unprovided intrabar/recalculate-after-fill settings. An evening
time exit is generated from 21:00 CT; Friday positions can remain through the weekend. No repair was made.

## 3. Does the flow reach the traded contract or its direct hedge?

Signal and trade use NQ/MNQ prices directly. That avoids an indirect-hedge transmission assumption but does not
establish who causes continuation or whether the retest has positive expectancy after adverse selection.
MNQ fills, fees, contract mapping and actual rolling positions require their own accounting, beyond point scaling.

## 4. New information and data feasibility

| Input | Source / fields | Coverage and warm-up | Timing / revisions | Availability |
|---|---|---|---|---|
| Minute prices and 15-minute bars | Owned NQ OHLCV; aggregation and source/session settings must match | Exact parity not checked; EMA warm-up and 55+ sessions for v9 daily regime | Causal raw prices; continuous-contract revisions/splices affect rules | Owned CSVs, not a verified replica |
| Exact backtest ledger | Native MC report, List of Trades and Settings | FAR/v9 full-history runs plus identified earlier snapshots | Preserve exports and calculation/fill settings | PDF only in this task |
| Roll corrections | Original/corrected four-trade records, true-contract overlap and splice mapping | Historical schedule, especially post-mid-2024 | PDF flags v9's stale assumed roll time | Explanation supplied; trade-level evidence missing |
| Existing prop version | Already-tested 15:45 CT flatten source and report | Exact variant/version/window needed | Treat as an existing trial, not a new discovery | Described in PDF, code/report not supplied |

The headline assumes 15-minute signals with one-minute Bar Magnifier. Magnifier granularity is not proof of
intrabar strategy recalculation or post-fill excursion tracking. Neither uploaded source forces IOG.

## 5. Costs and actual intraday gaps

Entry and target are limits, with uncertain queue position and trade-through; stops/time exits are marketable.
Headers describe per-side/per-order costs while the PDF uses per-contract/per-trade wording. Verify native
Settings, accounting and real MNQ fees rather than divide NQ costs by ten and call them verified micro costs.

The 09:00-13:59 signal window overlaps the existing US-session NQ book. Evening/weekend occupancy also intersects
the Bridge Monday carry. These are predicted overlaps, not measured joint exposure or correlation. The saved
`analysis/outputs/codex_sge_delivery_screen/roster_minute_occupancy.csv` is an older roster snapshot; it cannot
establish current candidate-event gaps. Test all eligible signals before measuring overlap later.
These supplied rules violate the current Apex flat deadline; their account benchmark is not yet meaningful.

## 6. Power before a return test

The overview's annual rows imply 1,581 FAR trades and 1,875 v9 trades in 2018-22. These are claimed counts,
not independently counted events. IID arithmetic gives a t=2 mean hurdle of approximately 0.050 or 0.046 times
trade SD, respectively; actual SD, clustering and search history are unavailable. Tail dependence and multiple
positions on the same day reduce the usefulness of treating each trade as independent. No power pass is claimed.
Use a preregistered cheap design screen only after source/fill/roll readiness is established; no fitted rescue.

## 7. Already tested and falsifiers

No exact Kusho/finished-auction entry was found in the ranked/watchlist inventory at `e7c394f`. Existing wick,
order-flow and Twin swing-risk ideas are related but do not establish this rule's result. The PDF itself already
tested strict no-wick signals, alternative execution granularity, break-even settings, ATR exits and a prop
flattening version; preserve that trial history and do not silently repeat it as new research.

Falsifiers before a new test: the signal adds nothing to same-clock/same-order random-long controls; the edge
vanishes under executable entry/BE timing or realistic limit fills; the corrected ledger still depends on roll
artifacts; tail opportunities disappear prospectively; or v9's net improvement fails once displaced long trades
and actual costs are included. Its regime filter also needs frozen controls, not hindsight-selected down years.

## 8. Failure and diversification

| Question | Prediction before new results | Evidence needed / refutation |
|---|---|---|
| What stops it working? | Retests become informed selling/buying; trends reverse; large continuation days thin out | Frozen forward comparison against matched controls and preregistered tail diagnostics |
| Liquidity role? | Limits offer liquidity and risk adverse selection; stops take liquidity | Bid/ask, trade-through and queue/fill evidence |
| Loss growth/clustering? | Whipsaws, first-bar protection gaps, invalid stops, overnight/weekend gaps and bad rolls | Post-fill paths and executable order-state chronology |
| Shared losses? | Likely common NQ direction risk with the US book; v9 may offset some down days while displacing longs | Conditional losses and paired combined ledgers, not a short-label assumption |
| Offset before breach? | No reliable timed offset is established | Full account/netted chronological replay with actual fees and trailing floor |

At NQ tick size, nominal positive-risk stops range from a 50-point fallback to at most 125-point accepted
structural distance, before fees/slippage/gaps. The missing positive-risk guard means these are not assured
runtime limits. The closing-sequence Monte Carlo is not an annual Apex floor-breach estimate.
No external-source auto-trading instruction was followed, and no change was made to a live strategy or account.

## Decision and next gate

**NEEDS DATA / WATCH for personal-account research; do not use these supplied versions in Apex.** Obtain both
raw reports/Settings, original and corrected roll accounting, and the existing intraday version. Freeze exact
calculation/fill semantics before a separate parity test or executable amendment. Any new Codex return test
needs its own committed plan, at most five variants and the 2018-22 stop rule. Reused 2023+ data must be labeled
historical replication. Account addition/replacement/empty-slot tests follow only for an eligible verified rule.
