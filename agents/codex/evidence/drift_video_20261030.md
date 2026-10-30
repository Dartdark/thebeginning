# Video Drift VWAP Pullback: TEST (bounded reconstruction of an existing family)

Summary: Test the NQ rules disclosed from5:34 onward, then earned current-book comparisons.
This repeats the DriftPullback family; it is not a new discovery or verified source-code replication.
The missing code leaves VWAP basis, first-pullback and loss-counter details to explicit assumptions.
Timestamp-only inventory finds1,247/1,259 complete design cash sessions;12 stay unknown.

Source: [archived user transcript](../inputs/drift_video_20261030/transcript.txt), received2026-10-30;
rules14:24–18:37,21:32–23:20. No video URL or code accompanied this upload.
Prior results: TIER_LIST DriftPullback v2.1; analysis/drift_pullback_test.py and its saved output.
Current roster: [snapshot](../inputs/greenorb/plan_snapshot/manifest.json), Claude7a42ea76c62838109d45d168887f57a922933ef2.
New return trials before this sheet: zero. Prior family has at least15 definitions plus placebos; retain them.

## 1. Who trades, and what causes the trade?

The speaker proposes that benchmark execution algorithms create continuation and pullbacks near session VWAP.
No signed customer orders, mandated net demand or causal flow estimate is supplied. The90–95%VWAP-order claim
is unverified. We test a specified price/volume rule, not the existence of mechanically forced demand.

## 2. Direction, size and timing known before entry

Cash-open-anchored15m VWAP, its trailing slope, and trailing one-hour NQ return define15m direction.
Opposing5m candle defines pullback; all features available at completed-bar decision, fill next bar open.
Trade09:30–14:30CT, flatten14:55CT; CT/ET difference is one hour on these US-session dates, including DST.
No dollar flow size can be inferred from these price features. Market entries need native quote/fill confirmation.

## 3. Does the flow reach the traded contract?

We trade NQ/MNQ, so price inputs are direct. Cash benchmark algorithms can hedge in NQ, but their netting and
hedge demand are not observed. There is no separate evidence of a cash-to-futures imbalance here.

## 4. Information and data feasibility

| Input | Exact fields/source | Coverage/warm-up | Clock/revisions | Cost |
|---|---|---|---|---|
| NQ minute exports | data/NQ_1min_2018.csv through2026.csv; date,time,OHLC,volume | 2018–22 design; later only after pass; one-hour intraday warm-up | Close-stamped CT; historical continuous export, no native MNQ/contract IDs | Owned |
| Calendar | codex_s03_calendar.calendar_status | Known cash holidays/half-days | Date-derived before outcomes | Existing |
| Current five homes | Pinned six-plan GreenORB snapshot |19-piece personal; current funded/evals | Archive/hash pinned | Owned |

Design inventory reads timestamps only:1,247complete/1,259cash sessions(99.05%). Excluded paths remain unknown.
Use completed15m HLC3×export volume VWAP; do not substitute MultiCharts uptick `Volume` for total futures volume.
No fitted models, parameter optimization or hindsight labels. Published strategy/family outcomes were already seen.

## 5. Costs and actual gaps

Primary1MNQ: $1.04RTfee plus0.25point($0.50)each market/stop fill; limits require1full NQ point through.
Gross target$80long/$100short versus$160nominal stop; this negative payout ratio needs a high hit rate.
Stress: $1.24RT plus0.50point each market/stop, replaying loss caps; source NQ bridge$7.25 plus$5permarket/stop fill.
This trades the occupied US-session window; it does not solve the08:00–09:00CT gap. Prior daily long correlation
with Vault Break was0.46. Current occupancy/concurrency must be measured at account stage, not used to select events.

## 6. Power before outcomes

1,247complete design sessions and at most4trades/session; actual signals not yet computed. Assuming daily SD$170
per1MNQ (illustrative), daily mean about$9.63supports t2, about$12.04supports t2.5, before dependence correction.
Several thousand trades are plausible from the prior family; clustering means trades are not independent days.
This is feasible to screen cheaply; it is not evidence the effect or incremental portfolio benefit exists.

## 7. Already tested and falsifiers

TIER_LIST v2.1: prior5,733trades,$56/NQ,t4.0; one-point target-through version$t43,t3.0; old funded ADD1MNQ
raised blow-ups3%→13%. WATCHLIST shorts weak since2023. Personal snapshot also lists simplifiedv3 as capital-expansion
candidate only. These are old related definitions/books, not results of today's source test/current portfolio.
Today's differences are explicit15m frozen bias, first-color-transition trigger, immediate entry-bar protection,
09:30CTstart, exact14:55close and primary consecutive-loss count. Failure of frozen net/placebo gates ends this task's
dependent stages; no stop/target/time optimization or post-hoc long-only rescue.

## 8. Failure and diversification

| Question | Prediction before results | Needed evidence |
|---|---|---|
| What stops it working? | Balanced/crowded VWAP execution; no sustained directional flow | Net-cost and time/side controls |
| Liquidity role? | Market entry/stop demands liquidity, target supplies it | Native bid/ask and fill replay later |
| Loss clustering? | Whipsaw produces repeated80point losses; source1NQ risks$1,600/trade | Joint chronological paths and account caps |
| Shared loss? | VB and other NQ momentum likely overlap; shorts may differ | Candidate/current-book covariance and simultaneous losses |
| Offset before breach? | No guarantee; small target does not neutralize deep stop | Minute-level funded/evaluation simulator |

One position, max4entries/day, stop80points, targets40/50, mandatory time exit, conservative known half-days.
Unknown paths excluded explicitly, not booked as flat. No assumption that four copied accounts are independent.

## Decision and next gate

**TEST** — user requested an actual source reconstruction/current-portfolio test. Commit the bounded plan and code
before returns. This is an existing-family replication, not an automatic scout reservation or a new scheduled cycle.
Only a passing design and historical validation earn account comparison; exact MC/source/native-MNQ parity remains pending.
