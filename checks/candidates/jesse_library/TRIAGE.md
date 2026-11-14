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

## Premium strategies (no code anywhere; stats and descriptions only; each is the author's tuned version of a free parent)
Site snapshot, author's window, BTC-USDT unless noted: return / win / Sharpe / max DD / trades.
| Strategy | Snapshot | Rule we can rebuild from | Verdict |
|---|---|---|---|
| **CLMeanReversionPremium** | Oct 2026: +1.3%, 3 trades | Full rule in the description: 30m close beyond the Bollinger band, fade only WITH the 1h EMA trend (buy stretched dips in uptrends, sell pops in downtrends), CME crude hours only, ATR stop, target the middle band, exit on a mean cross | **Shortlist #1 together with the free version** (rebuildable; the trend-aligned filter is the premium difference) |
| **AlligatorV2** | 2022-23: +90%, 73% win, Sharpe 1.77, DD -13.9%, 37 trades | Free parent AlligatorAI is described rule by rule (Alligator trend on 30m + 6h-style higher tf, ADX strong, EMA100 higher tf, CMO threshold, StochRSI pullback, ATR stop / target) | **Shortlist #7**: rebuild the parent from its description, then the premium snapshot is the target to compare |
| **TrendWaveRiderV2** | 2024-25 (15m): +108%, 75% win, Sharpe 2.18, DD -19.6%, 67 trades | MAs for direction + ADX / DMI strength + CCI timing, ATR stop and target (free parent TrendWaveRider: same, DMI) | **Shortlist #8** (high-win trend entries on BTC; parameters must be guessed: pre-register defaults ADX 25, CCI(20) +-100, MA 50/200, stop 2 / target 3 ATR) |
| **TrendSwingTrader V2** | 2022-23 (4h): +71%, 57% win, Sharpe 1.95, DD -10.7%, 30 trades | Free V1 rule: three EMAs for trend, ADX against ranges, ATR stop and first target, trailing stop on the second half | **Shortlist #9**, low priority: 4h, ~15 trades a year (too few to judge) |
| **Turtle V2 / V3** | 2022-23 (1h): +118% / +96%, 44% / 43% win, Sharpe 1.79 / 1.69, DD -16.6% / -19.1%, 68 / 72 trades | 'Premium version of Turtle AI': Donchian breakout family (free TurtleAI by o1-preview: 2023-24 +74%, Sharpe 1.65) | Same family as our Donchian F rows; test only as part of #7-style rebuilds if the user wants: **deferred** |
| **SuperScalper** | 2022-23 (15m): +59%, 52% win, Sharpe 1.93, DD -12.5%, 132 trades | SuperTrend in-and-out in trends; 'better in a downtrend' | SuperTrend family already F on NQ / GC; the one window shown is the 2022 bear: **deferred** |
| **MtfKelt2xA** | 2025-26 SOL (1h): +44%, 51% win, Sharpe 2.22, DD -8.9%, 72 trades | Keltner(29, 2.77) breakout on 4h with a daily anchor, entries on 1h | SOL only on the site; a BTC / NQ port is possible: **shortlist #10, low priority** (tuned to SOL) |
| Slow Trend Following | no snapshot on its page | 'a trend following indicator', no rule | not rebuildable: skip |
| TFAtrExitBreakout | 2025-26 (1h): -1.3%, Sharpe -0.07, 125 trades | Bollinger breakout + EMA filter, ATR bracket | loses on its own site: skip |
| BTCAdxEnsemblePremium | 2024-25: +78.5% | six ADX books | done (rounded and 1/3 versions benched) |

## Not pursued
- **No data for the market:** SOL (SOLSqzDon30mYTD, MtfMomo2xA, MtfKelt2xA), ETH-only squeeze variants (ETHSqueezeV35, ETHSqzDonYTD,
  ETHTrendBB), ZEC (ZecStTrend6538-31), single stocks (NVDATrendBreakout1h, NVDASuperTrendBreakout, AAPLHourlyAnchorTrend).
- (premium strategies: assessed in their own table below, user 2026-11-13 'even the premium ones show stats and descriptions')
- **Losing or near zero on their own site, or a handful of trades:** TTMSqueezeWithAlma (-99% in its window), AAPLHourlyAnchorTrend,
  TFTrailBreakout (+1.5% in 2 years), TrendSwingTrader V1 (DD -41%), ABQ1 ("test"), RSI Trend, TrendWaveRider, AlligatorAI,
  Trend Following / TurtleAI by o1-preview, MeanReversionRSI (7 trades), CloudScalper (DD -31%), Golden Cross.

## Pattern
The strongest BTC entries in the library (BTC ADX, KAMA, TEMA, ADX-Williams, CloudScalper) all gate on ADX >= 40-50. KAMA's
own test found ADX > 50 was the only filter that mattered, and BTC ADX's edge is the ADX level. So most of these are one edge
(strong-trend continuation on BTC) with different decorations; expect high correlation with the BTC piece already in the plan.
The one genuinely different idea for our book is #1 (CL mean reversion).

## Results (2026-11-13, free code as coded on our data; tier-list rows)
| Strategy | Result | Verdict |
|---|---|---|
| CLMeanReversion (CME CL) | t -0.8; premium-as-described t 1.66 at EMA 50 only, 2023+ t 0.2 | F (premium rebuild D) |
| TemaTrendFollowing | t 1.18, placebo p 0.10 | F |
| ADXWilliamsStrategy | t 3.28 but random side earns the same (p 0.30) | F |
| TrendWaveRider (V2's parent) | t 2.19, placebo p 0.00, 2023+ t -0.1 | D |
| AlligatorAi (V2's parent) | t 1.50, placebo p 0.00 | D |
| **TrendSwingTrader V1 (V2's parent)** | **t 2.24, placebo p 0.03, both periods positive; longs t 3.38** | **C** |
| TurtleAI (Turtle V2 / V3's parent) | t -0.13 | F |
| BBSqueezeTrend (on BTC) | t 1.06, placebo p 0.23 | F |
| ETHSTPullback30m (on BTC) | t 0.60; 2023+ t -1.5 | F |
| SPYTFDipLS (ES / NQ) | t 0.76 / 1.17, placebo p 0.12 / 0.42 | F |

## Premium code worth getting (user asked which to request)
1. **TrendSwingTrader V2**: its free parent is the only library strategy that passed; V2 is the author's optimised version.
2. **TrendWaveRiderV2**: parent has a real direction edge (placebo p 0.00) but nothing since 2023; the site's V2 snapshot is
   2024-25 (+108%), so the code would show whether V2 fixed the post-2023 decay or just refit it.
3. **CLMeanReversionPremium**: my rebuild from the description lives on one EMA length; the real code settles the trend filter.
   CME crude, short holds: the only Apex-relevant idea in the library.
4. AlligatorV2 (optional): parent t 1.5 with a clean placebo; worth a look only if cheap.
Not worth it: Turtle V2 / V3 (parent F), SuperScalper (SuperTrend family F, one bear-market window), MtfKelt2xA (SOL tuned),
TFAtrExitBreakout (loses on its own site), Slow Trend Following (no stats, no rule), BTCAdxEnsemblePremium (already rebuilt
from its exact description; at tradeable size it does not beat the plan's free version).

## Premium pages sent by the user (2026-11-13, screenshots; code still locked)
| Premium | Window shown (calendar) | Stats | Free parent in the same year (our test, sum of trade %) |
|---|---|---|---|
| TrendSwingTrader V2 (BTC 4h) | 2022 | +70.8%, 30 trades (7 long / 23 short), win 57%, Sharpe 1.95, DD -10.7% | V1 2022 +21%; V1 shorts lose overall |
| | 2023 ('2023 - 2024' filter = calendar 2023; first logged as 2024 by mistake) | +72.4%, 28 trades (24 long), win 61%, Sharpe 2.22, DD -9.2% | V1 2023 +23% |
| TrendWaveRiderV2 (BTC 15m) | 2024 | +108%, 67 trades (23 long / 44 short), win 75%, Sharpe 2.18, DD -19.6% | free TWR 2024 -4% (V2 is materially different) |
| AlligatorV2 (BTC 30m) | 2022 | +90%, 37 trades (13 long / 24 short), win 73%, Sharpe 1.77, DD -13.9% | AlligatorAi 2022 +13% |
| CLMeanReversionPremium (CL perp 30m) | June 2026 | +1.3%, 3 trades | nothing to judge |
Two of the four shown windows are 2022 (the BTC bear year, carried by shorts). The pages' period filter has every month / quarter /
year 2021-2026; per-year stats for each premium would show whether the edge holds outside the window the author picked.

## Every year and quarter from the site's metrics endpoint (user 2026-11-13 'do the endpoint'; Binance BTC-USDT perp, the
## author's sizing and fees; the filter label 'YYYY - YYYY+1' = calendar YYYY). Return % / max DD % / trades.
| Strategy | 2022 | 2023 | 2024 | 2025 | 2026 Q1 / Q2 / Q3 |
|---|---|---|---|---|---|
| **TrendSwingTrader V2** | +70.8 / -10.7 / 30 | +72.4 / -9.2 / 28 | +74.6 / -36.1 / 35 (**identical to V1's 2024**) | -2.1 / -13.7 / 22 (Q1 +1.6, Q2 +5.7, Q3 +0.3) | +2.2 / +9.6 / +10.4 |
| TrendSwingTrader V1 (free) | +68.0 / -41.4 / 30 | +103.3 / -28.5 / 31 | +74.6 / -36.1 / 35 | n/a (Q1 -35.1, Q2 +22.6, Q3 +1.5) | +4.5 / +24.2 / -19.7 |
| TrendWaveRiderV2 | +19.6 / -40.1 / 92 | -3.4 / -24.9 / 103 | +108.3 / -19.6 / 67 | n/a (Q1 -1.4, Q2 +13.6, Q3 -4.1) | -7.4 / +16.7 / +7.6 |
| TrendWaveRider (free) | +42.6 / -38.8 / 52 | +141.8 / -39.9 / 61 | +26.4 / -22.9 / 35 | -24.1 / -38.1 / 32 | +10.3 / +18.0 / +22.2 |
| AlligatorV2 | +90.1 / -13.9 / 37 | +73.0 / -16.4 / 48 | +47.4 / -12.0 / 35 | n/a (Q1 +17.7, Q2 -14.0, Q3 -0.2, Q4 +0.6) | +7.8 / +11.4 / -5.1 |
| AlligatorAi (free) | +67.7 / -14.0 / 41 | +28.0 / -18.7 / 57 | +32.3 / -27.4 / 60 | +9.4 / -21.8 / 50 | +6.8 / +3.5 / -8.1 |
| CLMeanReversion / Premium | no yearly or quarterly results on the site (404): only single months | | | | |
Reading: the premium versions were published about two years ago (late 2024), so 2025-26 is after publication.
- **TrendSwingTrader V2** is the steadiest: positive every year 2022-24 with ~10% drawdowns (except 2024, whose numbers are
  byte-identical to V1's, so that year looks like V1's backtest, not V2's), then roughly flat 2025 (-2.1%) and +22% over
  2026 Q1-Q3 with small drawdowns. The free V1 swings far more (Q1 2025 -35%, Q3 2026 -20%). V2 is the one worth the code.
- TrendWaveRiderV2: 2024 was its showcase (+108%); 2023 -3% and mixed since publication; the free version did better in 2026.
- AlligatorV2: strong 2022-24 (DD 12-16%), about +16% over the 7 quarters since publication with one -14% quarter.
These are the author's own backtests (perp, their fills and leverage): direction of the evidence, not a test.
