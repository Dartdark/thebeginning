# QuantJourney stop-limit protection — DON'T TEST returns; inspect mechanics

Summary: This uploaded daily-ETF SMA example is an order-type demonstration, not evidence of a futures edge.
Its published 25-year CAGR is1.99%, excess-return Sharpe0.02; these are author claims, not our replication.
SPY/QQQ/IWM shares held for weeks cannot directly enter any of the four intraday futures account plans.
The price bound on a sell stop-limit does not bound losses when it remains unfilled.
Retain and test the execution lessons; no new economic return trial passes this evidence gate.

Source: user-pasted code/screenshot, original [strategy](../inputs/qj_stop_limit_20261030/source.py),
[published claims](../inputs/qj_stop_limit_20261030/published_claims.json),
[access receipt](../inputs/qj_stop_limit_20261030/access_receipt.json).
Public engine pinned at QuantJourneyOrg/quantjourney-bt `4f403d853833e1daa6de01c5b6c6cb3983dc0044`.
Public packet engine is0.10.0+private; current public engine is0.12.5. Exact historical engine parity is unverified.
Original source class is archived, but its API/credential helper and main will never be executed.

## 1. Who trades, and why?

No forced participant or incremental cash flow is identified. Twenty/fifty-day SMA crossover is a generic
trend rule; the author explicitly presents this as an educational order simulation. A protective exit changes
execution and risk; it does not by itself supply positive expected returns. No new signal is extracted here.

## 2. Direction, size and information clock

Long-only SPY/QQQ/IWM shares. On a completed daily bar, a transition from SMA20<=SMA50 to SMA20>SMA50 buys
integer shares at15% of then-NAV/reference close. Orders become eligible on the next bar. Published/current
public engine timing is next-bar open for market orders; current public simulator processes old orders before
the strategy callback after the daily close. A4% entry-price stop activates a sell limit4.5% below entry.
The stop order is submitted in a separate later callback, rather than linked to the entry as a bracket.
An unfilled activated stop-limit can persist, exposing the position to more downside.

## 3. Transmission and account fit

SPY/QQQ/IWM daily trends are not identical to ES/NQ/RTY intraday futures signals. Replacing shares with
contracts, adding daily liquidation, changing stops or using different holding times is a new strategy definition.
No such adaptation is justified by this execution demo. The four evaluation/funded homes cannot directly hold
these ETF positions under their intraday futures mandate. A personal ETF sleeve is theoretically possible,
but no useful incremental contribution to the current futures portfolio is established.

## 4. Inputs and feasibility

| Input | Inspected source | Actual availability | Limitation |
|---|---|---|---|
| Strategy class | user paste + canonical GitHub source | complete logic; fixed universe/settings | source intent/order state can be tested without market returns |
| Public execution engine | pinned fill_engine, order_types, slippage, commission, simulator/core | reviewed public0.12.5 | not certified as published0.10.0+private engine |
| ETF OHLC/history | owned-file search | no verified SPY/QQQ/IWM daily OHLC set | `SPY_daily.csv` has close-only index/futures-scale values, not verified ETF OHLC |
| Free observed data | Yahoo public chart attempt | proxy tunnel403; no data obtained | respected denial; no accounts, purchases or keys |
| Alternative public repo | GetPriceData pinned tree | downloader scripts, no stored OHLC CSVs | not a usable data panel |
| Engine demo data | sample_data.py | deterministic generated prices | never substitute for historical returns |
| Published outcomes | user screenshot/public packet | author statistics/round-trip counts | source outcomes, not independent return reproduction |

No placeholder high/low/open, imputed missing returns, synthetic historical price panel or futures proxy is allowed.
Missing native ticks/order books also preclude measuring the real probability of stop-limit nonfill or queue priority.

## 5. Costs and portfolio overlap

Source costs are5bps one way and $0.005/share, minimum$1 per order; these equity fees cannot be copied to MNQ.
15% entry allocations per ETF imply up to45% initial gross exposure when all enter, subject to source risk controls;
weights can drift. The packet reports average gross exposure25.35%, so full SPY buy-and-hold is not a risk-matched
comparator. Its1.99% CAGR and Sharpe0.02 nevertheless provide no convincing economic reason for a new sleeve.
Do not infer a fair alpha comparison from unequal exposure or equate price-limited execution with a maximum loss.
Current plan documents are archived read-only at Claude `7ce07ece525fa16e95ac2221a27521d317b2b05c`.
No event-level existing-plan overlap or account effect has been measured; there is no earned placement stage.

## 6. Power before returns

Published379trade events are191buys+188sells, not379independent closed trades; there are188closed long round trips
over roughly25years, averaging77days held. Source sample selection/serial dependence and ETF co-movement matter.
No local2018–22 opportunity census, executable historical fill ledger or net-edge power claim exists.
Neither an unknown data set nor a generated demo series can establish power. A new return trial is unwarranted.

## 7. Prior evidence and falsifiers

Prior Tier SMA trend filters and indicator studies do not establish an incremental edge; the existing execution
library E03/E05/E18 covers order state, missed fills and fill conventions. This specific source has not been
economically retested. Early evidence rejects promotion: no new mechanism, weak published excess returns,
nonmatching instrument/holding rules and unresolved exact-source execution provenance. Do not rescue by
substituting NQ, changing SMA periods or converting stop-limit exits into guaranteed stop-market fills.

## 8. Failure/diversification questions

| Question | Prediction before synthetic checks | Needed evidence |
|---|---|---|
| What can fail? | gaps below the limit, signal reversal, rejected protective orders | actual order-state/clock checks |
| Liquidity role? | marketable entry; activated resting sell limit | post-trigger quotes, queue/fill and cancellation records |
| Loss clustering? | correlated ETF selloffs and overnight gaps | observed data and native costs, not an assumed4% cap |
| Shared portfolio loss? | US equity beta overlaps existing NQ/ES legs | future joint-path account test only if a distinct candidate earns it |
| Offset before breach? | no guaranteed fill or timely offset | chronological native account replay; annual Sharpe is insufficient |

## Decision

**DON'T TEST new return variants.** The evidence does not justify a strategy project or promote the posted
returns to verified results. Complete the finite, disconnected mechanics checks in the committed plan and retain
the lessons. No verified positive equity or futures return, account payout/pass rate or independent review claimed.
All five homes receive explicit nonplacement/untested-account verdicts. No TODO promising-strategy entry.
