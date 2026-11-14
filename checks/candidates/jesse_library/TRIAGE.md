# jesse.trade strategy library triage (user 2026-11-13: "go through all of the strats here and see what can help us")

Read on 2026-11-13: all 48 strategies at https://jesse.trade/strategies (descriptions + the site's own backtest snapshot, whose
window the author picks: often one month or two years). **Code needs a jesse.trade login** ("You need to login to see the code"),
so nothing below is tested yet except the rows marked done. The site's stats are in-sample, author-chosen windows, crypto perps.

## Already tested by us
| Strategy | Our result |
|---|---|
| BTCAdxEnsembleFree / Premium | B; longs on MBT in the personal plan (free, 1 MBT a book); premium only better at untradeable size |
| KAMA_TrendFollowing | F (cloud, 11/14): BTC -$31 a trade, NQ negative; only ADX > 50 mattered |
| EMBIA (V3) | F (cloud, 11/14); VIX3M-high NQ version on WATCHLIST #43 |
| Golden Cross | F (GC and Jesse port, 2026-10-17) |
| Simple Donchian, Simple Bollinger, RSI2 / IFR2, SuperTrend, Ichimoku, MACD + EMA | same families already F on NQ / ES / GC (TIER_LIST: Donchian, RSI / Bollinger screen, T5 EMA + ADX, Triple SuperTrend, Mesfin OHLCV falsification) |

## Shortlist (worth the code; test order)
| # | Strategy | Why | Market for us |
|---|---|---|---|
| 1 | **CLMeanReversion** (free; premium = same idea, trend-aligned) | Bollinger fade on 30m with a 1h EMA trend filter, only while CME crude trades, exits at the mean: a MEAN-REVERSION piece on a CME market we already trade (our book is mostly trend / momentum); short holds, so an Apex-legal version is plausible | CL / MCL (our CL 1-min data) |
| 2 | **TemaTrendFollowing** (free) | BTC 30m, ADX > 40 + CMO momentum, TEMA 10/80 with a 4h TEMA 20/70 filter; site 2024-25 +309%, 76% win, 67 trades. Same high-ADX theme that carries the BTC ADX ensemble: check whether it adds to it or duplicates it | BTC spot -> MBT |
| 3 | **ADXWilliamsStrategy** (free) | BTC 15m, ADX > 50 + DI direction + Williams %R pullback entry, stop at SMA50, target recent high / low; site 2022-23 +194%, 56 trades. A pullback entry inside strong trends: a different entry on the same edge | BTC -> MBT; also NQ (ADX > 50 is the one filter that survived in KAMA) |
| 4 | **BBSqueezeTrend** (free) | 4h Bollinger-inside-Keltner squeeze release, direction by regression slope, ADX confirm, ATR trail; author reports a rule-significance test (p 0.0, 2,000 sims) | ETH on the site (no ETH data): test on BTC and NQ |
| 5 | ETHSTPullback30m (free) | 4h SuperTrend + EMA200 regime, 30m SuperTrend pullback entries, ADX filter, chandelier exit; site 2024-25 +46%, 93 trades | ETH on the site: BTC / NQ port |
| 6 | SPYTFDipLS (free) | researched on SPY: 4h SuperTrend + ADX regime, EMA-pullback entries, chandelier exit | ES / NQ (overnight holds: personal only) |

## Not pursued
- **No data for the market:** SOL (SOLSqzDon30mYTD, MtfMomo2xA, MtfKelt2xA), ETH-only squeeze variants (ETHSqueezeV35, ETHSqzDonYTD,
  ETHTrendBB), ZEC (ZecStTrend6538-31), single stocks (NVDATrendBreakout1h, NVDASuperTrendBreakout, AAPLHourlyAnchorTrend).
- **Premium, no code and no rule in the description:** Turtle V2 / V3, TrendWaveRiderV2, AlligatorV2, TrendSwingTrader V2,
  SuperScalper, Slow Trend Following, TFAtrExitBreakout, CLMeanReversionPremium (description only; covered by #1).
- **Losing or near zero on their own site, or a handful of trades:** TTMSqueezeWithAlma (-99% in its window), AAPLHourlyAnchorTrend,
  TFTrailBreakout (+1.5% in 2 years), TrendSwingTrader V1 (DD -41%), ABQ1 ("test"), RSI Trend, TrendWaveRider, AlligatorAI,
  Trend Following / TurtleAI by o1-preview, MeanReversionRSI (7 trades), CloudScalper (DD -31%), Golden Cross.

## Pattern
The strongest BTC entries in the library (BTC ADX, KAMA, TEMA, ADX-Williams, CloudScalper) all gate on ADX >= 40-50. KAMA's
own test found ADX > 50 was the only filter that mattered, and BTC ADX's edge is the ADX level. So most of these are one edge
(strong-trend continuation on BTC) with different decorations; expect high correlation with the BTC piece already in the plan.
The one genuinely different idea for our book is #1 (CL mean reversion).
