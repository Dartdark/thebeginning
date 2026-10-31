# Evidence sheet 2: Real opening / closing auction imbalances instead of price proxies (ES first)
Verdict: **NEEDS DATA (paid): get a price quote, then decide.** Rank 2.

1. **Who trades and why.** Index funds, ETF creations, rebalancers and closing-price benchmarks send
   market-on-open / market-on-close orders. The exchange must match them in the auction; the published imbalance is
   the unmatched part that liquidity providers absorb, often hedging in index futures.
2. **Direction, size, timing known in advance?** Yes, by construction. NYSE publishes closing imbalances every
   5 seconds from 15:45 ET = **14:45 CT** (TAQ NYSE Order Imbalances spec); opening imbalances before the open. Sum the
   $ imbalance across S&P 500 members → ES direction and size before 14:50 / before 8:30.
3. **Reaches ES / NQ?** ES directly via futures hedges. **NQ needs Nasdaq's NOII** (Nasdaq-100 stocks list on Nasdaq),
   a separate product: start with ES.
4. **What separates it from momentum?** The imbalance is the order itself. Our ES MOC Follow (in the plan, 2 MES) uses
   the 14:00→14:50 price move as a proxy; the real imbalance can disagree with the move. Test: does the imbalance sign
   / size predict 14:51→15:00 better than the price proxy, on the same days?
   **Data:** NYSE TAQ Order Imbalances (history from 2008; NYSE Managed File Transfer or WRDS). Paid, price on request.
   NYSE's free tool shows only the trailing 3 months, graphically.
5. **Beats costs in a gap?** Close: same slot as ES MOC (its upgrade). Open: **08:00-09:00 CT is ~99% flat Tue-Thu**
   in the plan's occupancy map: the biggest empty daytime window. ES cost ≈ $30 a round trip ($5 + 2 ticks).
6. **Power.** One event a day, ~1,250 design days: power is fine (a $15-20 net edge per ES trade would show).
7. **Already tested?** ES MOC (price proxy, B), MOC order-flow and month-end close tests (price / The Bridge order
   flow). No test with exchange imbalance data.
Decision for the user: worth it only if the 2018-26 ES file costs a few hundred dollars, or a short sample (1 year) is
cheap enough to check first whether imbalance beats the price proxy.
