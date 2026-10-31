# Subpenny trading in US equities: WATCH for execution research; DON'T TEST as an ES/NQ strategy
Summary: Delassus and Tyč study subpenny stock executions and market design, not a directional futures strategy.
NASDAQ100 sample-week subpenny volume rises from 7.38% in 2009 to 10.62% in 2010.
The economic mechanism is execution priority/spread capture, requiring access and order-flow conditions we have not established.
Useful for fill skepticism; no new strategy, verification-queue entry or account change is justified.

Source: Romain Delassus and Stéphane Tyč, *Subpenny trading in US equity markets*, 30 July 2010,
[SSRN 1651201](https://ssrn.com/abstract=1651201), user-uploaded PDF.
SHA256: `54fb93782c6c58f1790d8c55926c5c646b2ba17c65cd9bcef7abc5a1c6039f95`.
Review date: 2026-10-29. Source findings only, not independently reproduced. New return trials: **0**.
Repo context: codex/work `bda6092b3f792e9a7b1f5720ccb00828c72bc3ba`.

## 1. What is it about?

U.S. equity market structure: displayed penny quotes versus stock executions at fractions of a penny.
The authors distinguish midpoint crossings that give meaningful price improvement from extremely small
improvements that can divert execution ahead of displayed quotes, which they label queue jumping.
They examine Thomson Reuters trade data, selected March 2009/2010 weeks, broader NASDAQ stock samples,
and historical weekly statistics from 2003–2010. This is not a futures entry/exit backtest.

## 2. What does it find?

| Source result | Boundary |
|---|---|
| NASDAQ100 subpenny volume: 7.38% in the March 2009 sample week and 10.62% in the March 2010 sample week (p.8). | Shares of stock volume, not returns or a representative full-year estimate. |
| Subpenny prices cluster near midpoint and near whole-cent boundaries (pp.8–10). | Consistent with midpoint crossing and tiny improvements; trade prices alone do not establish order intent or true queue priority. |
| Author-defined queue jumping is especially prevalent in low-priced stocks; discussion cites 6–10% of total volume for stocks priced $1–$5 (p.16). | Historical, stock-specific market-design evidence; not an estimate for ES/NQ. |
| Estimated aggregate price improvement is about $5 million over 2 billion shares in the studied week; authors estimate about 20% of the effective spread returned to investors (pp.11–12). | Estimated execution savings, not audited trading profits available to us. |

Crucial methodology limitation (p.7): because quote information is limited, their main price-improvement
proxy is distance between the trade price and nearest cent. They round to $0.0001 first to reduce floating-point
artifacts. A print near a penny boundary is not by itself verified improvement over an actionable contemporaneous
NBBO, nor proof of a particular trader's queue-jumping strategy. Midpoint and trade-reporting effects require care.

## 3. Why does it make money, if it does?

The plausible economics are spread capture and access to order flow. An intermediary can offer a tiny price
improvement over a displayed quote and potentially execute flow that otherwise would have reached that quote.
A midpoint execution can reduce the client's spread cost. Neither operation predicts whether the stock rises next.

The paper discusses potential intermediary gains, but does not provide an implementable, independently validated
net-profit strategy for a retail trader. Fees/rebates, adverse selection, inventory losses, hedging, venue eligibility,
latency and flow quality determine actual profits. Aggregate client savings are not the intermediary's net profit.

It describes the then-current SEC Rule 612 setting and recommends a smaller tick for low-priced stocks.
Those are historical descriptions/proposals, not verified current rules or permissions for us.
CME ES/NQ execution has different market structure and tick rules; subpenny stock practices cannot be copied
onto an outright futures order by selecting an off-tick price.

## 4. Can we build on it?

**For execution diagnostics, yes; for a new strategy allocation, no.**

It reinforces why a bar touching a limit is insufficient evidence of a fill. That is an execution lesson, not
a direct validation of our specific one-point or parity trade-through assumptions.
Our existing execution-diagnostics work is the appropriate home for later investigation.

A scoped future diagnostic could compare a strategy's arrival bid/ask, fill, spread, side and later midquote markouts.
All records need compatible exchange/receipt timestamps, clock alignment, and fees; passive orders additionally
need queue/fill evidence. A trade print alone does not recover that information, and one-minute OHLC cannot
reproduce this study or estimate queue priority. No logger or live changes were made in this review.

To establish a tradeable microstructure edge would require current quotes/trades and venue rules, sufficient
order-book or queue data, feasible routing/latency and a net simulation. The paper does not identify an actionable
scheduled flow or show predictive stock imbalance transmitted to ES/NQ. No modern data licence/access audit was performed.

The paper advertises historical weekly statistics at
`http://fiquant.mas.ecp.fr/Exchange/Subpenny/`; availability was not checked. Even if recovered, weekly
aggregates from 2003–2010 cannot establish present-day event timing, executable fills or our net profits.

## Decision

Keep as an execution/market-design reference. **DON'T TEST as a new ES/NQ strategy** from this evidence.
TIER_LIST, WATCHLIST and the current TODO queue were checked at the pinned head; no matching paper was identified.
No promising-strategy queue entry: no specific executable candidate has established merits.
No new backtests, data acquisition, MultiCharts code, strategy grade, allocation or live/VPS modifications.
Payout contribution, blow-up risk and portfolio diversification remain unmeasured.

For Claude: `agents/codex/results/subpenny_equity_paper_review_20261029.md`.
