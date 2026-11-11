# Archived liquidity state and pressure: conditional TEST, source gate unresolved

Summary: Four batches / 12 definitions failed and remain rejected. Add previously unused archived displayed-depth state
to the frozen monthly net-payoff forecast, with the original pressure model as matched control. This is an aggregate
bar-state adaptation, not a price-level gap or event-replenishment replication. Historical indexed-DLL availability is
conditional: original receipt/build/revision vintages remain missing. Even positive conditional returns cannot clear that
source gate or authorize live implementation. Three definitions, cumulative15, plus older pressure/book research.

Sources: uploaded papers and `results/pressure_papers_reconstruction_20261110.md`; exporter
`tools/exporters/OFB_OrderFlow_Exporter.txt` uses closed-bar OFB_GetAt(slot,BarKey) on ofb_hist.bin;
`analysis/codex_pressure_book_20261110_inputs.py` freezes all20 2018–22 quarterly CSV hashes and exact headers.
Input-only receipt `agents/codex/inputs/pressure_book_20261110/intake.json`. No new return/model-fit outcomes yet.

## 1. Participants and cause

Order splitting can create persistent aggressor flow while limit suppliers replenish depth. The papers support
variable response to flow, not a guaranteed mean-reversion premium. Prediction: observed pressure relative to displayed
nearby liquidity and changing depth may identify a different subsequent barrier-payoff distribution. No forced trader,
mandate, direction or unfilled quantity is observed. Displayed depth can cancel or be misleading.

## 2. Direction, size and timing

Both candidate directions are forecast from completed five-minute NQ bars and same-key archived book snapshots.
Snapshot close T is the assumed event/availability time; actual original availability remains unverified. Decision T,
first market entry open at T+1 wall minute (close-labeled row j+2), exit no later than T+31 /14:55 CT.
ET-close snapshots convert to CT-close with DST, no extra shift, no centered/future book statistics. No signal may depend
on label validity or later receipt. Research one NQ and separately repriced one-MNQ proxy; account sizing unearned.

## 3. Transmission

These are NQ futures book/flow scalars directly joined to native NQ bars, not inferred cash-basket flows. MNQ outcome
repricing is a proxy and does not authenticate its queue or fill costs. There is no executed ES hedge.

## 4. New input and feasibility

| Input | Coverage and source | Clock / limit | Status |
|---|---|---|---|
| NQ native minute OHLCV/buy/sell | Five hashed 2018–22 gzip exports | ET close to CT; native contract/roll vintages incomplete | Owned design inputs |
| spread/top sizes/depth10/20/50 | 20 hashed OF quarterly CSVs, 515,156 rows | Historical GetAt(BarKey), original calculation/revision/receipt unknown | Conditional archive only |
| frozen features/labels | Exact batch2 gzip Git object at0d61f59e | Label matures after scheduled30min horizon | Reuse without regeneration |

All515,156 book source closes and buy/sell quantities exactly match native at the same CT minute; top<=depth10<=20<=50.
Eleven rows lack positive quote support and stay unknown; 96,534 endpoints have all nine features across the entire
exported daytime window. Do not infer opportunity count after parent eligibility from that larger census.
No full price ladder, gap spacing, order IDs, additions/cancellations or replenishment receipts exists in these scalars.
Source availability is a blocker for actual strategy validation; this test measures conditional archived predictive value
to decide whether further source reconstruction is worthwhile. It cannot establish a causal original-vintage return.

## 5. Costs and exposure

Same market-taking entry and fixed .10ATR stop/.3R target, one-point target trade-through, one tick per market/stop fill,
NQ7.25RT or MNQ proxy1.24RT commissions. Four-tick and stop-first stress are binding. A .3R target needs76.92% wins
before costs under exact binary payouts. Extra book inputs must improve net P&L, not just forecast accuracy/win rate.
Test all eligible observations without incumbent-flat filtering. Cash09:00–14:00 can share VB/ONB/Bridge losses; no
occupancy gap or diversification benefit is yet demonstrated.

## 6. Power

Prior frozen paired observations provide many overlapping examples, not independent trades. Same126-slot training,
>=100 represented sessions and10,000 valid paired labels, >=50 full-stop labels per side over>=30sessions.
Executed basic screen needs250 trades/100 dates/25each side. For an assumed .55R trade SD, t2 requires about.070R
mean at250 independent trades, higher after dependence/selection. This is an assumed power hurdle, not observed edge.
Mature training losses and monthly chronological forecasts prevent easy upside-only calibration.

## 7. Prior tests and falsifiers

Retain first12 study definitions and earlier flow innovation, absorption, book/pattern and39-feature searches.
New inputs do not reset family multiplicity. HGB_NOBOOK retains original21 price+flow features, same known-book mask.
HGB_BOOK must improve total daily net over that control; Ridge versus HGB control is a whole-policy comparison.
Negative net, weak significance, unstable years, no paired incremental value or cost/latency failure refutes this rule.
No feature/depth/threshold/clock/direction rescue and no control promotion after outcomes.

## 8. Failure and diversification

| Question | Prediction / required falsifier |
|---|---|
| What stops it? | Permanent information, cancelled/stale depth or no incremental information; matched net control and vintage proof required |
| Liquidity role? | Market taker, paying spread/impact; archive gives no execution priority |
| Clustering? | Persistent trend, spread widening, gaps and bad input; hard stop can slip, no averaging |
| Shared losses? | Likely NQ direction/volatility overlap with VB/ONB; measure only after standalone gates |
| Offset before breach? | Unknown; chronological current150K replay required, not end-of-day correlation |

One position, maximum4 entries/day; absent current/exact-lag/prior20-slot support means no forecast, unknown held paths
block advancement. Later earned stage: BASE / ADD / REPLACE / EMPTY at frozen integer exposure, current six sleeves,
actual30calendar expiry/DLL overshoot and common price path. No such stage is earned now.

Decision: **TEST conditional archived predictive value only** under committed protocol. Original-vintage source gate
remains **NEEDS DATA** for validation/live use. No paid acquisition, platform/live change or claimed screenshot replication.
