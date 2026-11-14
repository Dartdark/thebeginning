PASS WITH CONCERNS. The edge replicates, there is no look-ahead, and the ADX placebo is clean. The returns get thinner once fills are realistic, 2023+ shorts are flat, and 3% per R is too much risk for this drawdown.

**Replication** (`replica.py`, written from spec.md alone, on data/BTCUSD_spot_1min_*): 774 vs 773 book trades. Match on entry time + book + side: 770, which is 99.6% of the maker's trades and 99.5% of mine. Exits identical on 99.7% of the matched trades, R corr 0.995, R per trade (ATR) identical. Mean +0.253R vs +0.252R, PF 1.68 vs 1.67. The 3 + 4 mismatched trades are a 1-hour shift around 2018-11-04 (US DST fall-back; the CSV holds only one copy of the doubled hour) and 2019-06-16, plus 2 trades in July 2018 during the EMA-200 warm-up.

**Gates** (`analysis/checker.py` on trades.csv; `checker_report.md`): 8/8 pass, plus G13.
- G1: t 5.61, DSR(N=487) 0.997.
- G2: 2018-22 t 4.90; 2023-26 +0.186R, t 2.93.
- G3: 9/9 years positive.
- G4: +86R without the top 5% of trades.
- G5: placebo with the ADX series rotated in time, 40 runs (`placebo.csv`, mine): placebo mean +0.022R; 0/40 runs reach +0.25R.
- G6: P(Sharpe<=0) 0.021.
- G7: MinTRL 59.
- G8: rho 0.81.
- G13: passes, but meaningless here, because it uses VIX regimes.
- Not run:
  - G9: there are no variant trade lists.
  - G10/G11: leak_checks.py has no tick size for BTCUSD_spot (KeyError) and expects CT bar-end clocks. I ran them by hand instead. L1: 100% of the 1,548 fills lie inside their 15m candle (`fills_replica.csv`). L2: entry one 15m candle late gives +0.221R, t 4.93, so it bends rather than breaks.
  - G12: the rule has no fitted parts.
- Caveat: checker `daily()` keeps business days only, so the 17% of rows dated Sat/Sun (28.5R) are left out of G6/G8 and the metrics table. The "$" in the report means R.

**1 Look-ahead**: none. One more candle of lag on the 4h EMA: +0.254R. On the vol ratio: +0.250R. On all three inputs together: +0.199R, t 4.60. The 1h indicators one candle older give +0.196R, t 4.5, but that change shifts the timing of most entries (only 26% still match the maker). As a planted leak, I used the NEXT 1h candle: that gives +0.316R and t 7.07, and the maker does NOT match it (26%). The maker's trades match the honest version at 99.6%. The entry price equals the decision candle's close in 100% of trades.
**2 Indicators**: ADX and ATR as written match an independent ewm(1/14) version to 1e-13 after warm-up. SuperTrend direction agrees 100% with an independent TradingView-style SuperTrend. A simple-mean (non-Wilder) ADX gives 1,869 trades, +0.076R, 2023+ t 0.70: the result depends on the ADX definition. No ADX filter at all: +0.018R, PF 1.04, which confirms the maker's claim.
**3 Fills**: the 15m-close fill flatters the result. 63% of stop closes are back inside the stop, worth +0.068R per stop.
- Stops at stop -0.05% and targets at their price: +0.187R, PF 1.48, t 4.45; 2023+ +0.130R, t 2.19.
- Entry one candle late: +0.221R.
- Both together: +0.150R, PF 1.36, t 3.56; 2023+ +0.087R, t 1.46; 8/9 years positive.
- Stops at -0.20%: +0.158R. Costs 0.12% per side: +0.201R.
- Guard: 34 exits; no exit candle opened beyond the guard.
**4 Independence**: 63 entries are shared by both books; daily-R correlation between the books is 0.57.

| Period | Book 40 t | Book 50 t | Daily-sum t |
|---|---|---|---|
| All | 3.88 | 4.28 | 4.37 |
| 2018-22 | 3.61 | 3.44 | 4.03 |
| 2023+ | 1.77 | 2.56 | 2.13 |

| Daily-sum t | All | 2018-22 | 2023+ |
|---|---|---|---|
| Longs | 3.84 | 3.10 | 2.34 |
| Shorts | 2.25 | 2.58 | **0.48** (book t 0.45 / 0.43) |

**5 Concentration**: the top 5% of trades (39) carry 56% of total R. Without them the result is +0.118R per trade. Without the best year (2019, 56.6R): +0.211R per trade, t 4.50.
**6 Neighbours** (single book): ADX 35 +0.10R (2023+ t 0.53), 40 +0.21, 45 +0.33, 50 +0.34, 55 +0.35, 60 +0.42. Pairs: 35/45 +0.18R, 45/55 +0.33R. Stop 2.0 ATR +0.255R, 3.0 ATR +0.225R. Target 6 ATR +0.175R, 10 ATR +0.267R. Every neighbour is positive. Below 40 the edge is weak.
**7 Drawdown**: closed-trade max DD is 14.5R (maker 15.4R), which is **43-46% of the account at 3% per R** (36-38% compounded). It is reached in 2018; in-year DDs are up to 11.1R (2023). Longest losing streak: 17 book trades. Longest time underwater: 197 days (218 with price fills).

**What would change my mind**: (1) Jesse's own backtest, or live fills, with stops filled at their price: if 2023+ falls below t 1.5 per trade, downgrade. (2) Perp funding: shorts are only ~+0.09R per day in 2023+ and could turn negative. (3) Risk: at 3% per R a repeat of the 15R drawdown costs about 45%. At about 1% per R it would be about 15%.
