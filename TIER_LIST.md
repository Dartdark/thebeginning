# Tier list: every strategy, filter and paper tested

S–F scale, updated as each new idea is tested. Results are NQ 2018–2026 unless noted, per
NQ after $7.25 costs and 1 tick of slippage per fill. "Funded" = expected payouts per Apex
50K Performance Account within 1 year (2 years in brackets); the current set (VB 3, ONB ML $400,
Monday Long 1 MNQ, EOS $700, Late-Day Flow 2 MNQ, NFP Fade $500, Bridge Monday Long 1 MNQ, full size from a
$1,500 cushion; Vol-Control Sell dropped) scores $9,313 ($12,569); with Vol-Control Sell $9,313 ($12,436); before the Bridge Monday Long $8,770 ($12,236); the previous 5-strategy set $7,676 ($12,012).

## What the tiers mean

| Tier | Meaning |
|---|---|
| **S** | Extreme profit, scalability and a very strong edge. In numbers: about $20,000+ a year per NQ, a t-stat of 4.5+ with PF 2+ and 8/9 years positive, and enough trades in liquid hours to size up without hurting fills |
| **A** | A very good, very profitable strategy, better than most of what's been tested. In numbers: t 2.5+, PF 1.4+ (or 1.9+ when it trades rarely), positive in 7+ of 9 years, MultiCharts-confirmed |
| **B** | A good strategy (or tool): a real, profitable edge, clearly below A. Roughly t 2–3.5 or PF 1.25–1.4 with most years positive, or a strong effect that still needs data / automation / a MultiCharts check |
| **C** | Less good: positive but small, inconsistent or regime-bound. Roughly t 1.5–2.5 with weak recent years, or strong only before costs / stops / the funded rules |
| **D** | Weak: the effect exists but makes about nothing after costs, stops or Apex rules, or it's the best of many tries |
| **F** | Fails: no edge, loses money, flawed study, or can't be traded on Apex |

Tiers rank how good an item is, not whether it's in the plan; the Type column says which ones are in use.

## S

| Item | Type | Key numbers | Why |
|---|---|---|---|
| Overnight Bias ML (v2: longs need score ≥ 0.03) | Funded strategy | 41% of ONB days kept; walk-forward kept $476 vs skipped $171, 6/8 years; funded $6,928 vs $6,495, blown 34% vs 42% | Per NQ (MC): 343 trades, $636 avg, PF 2.12, t 5.0, 8/9 years, about $24,800 a year; 15-min stop-order entries in the opening hour scale easily. Biggest single payout driver; frozen ridge filter on ONB (Kelly & Xiu ML survey) |

## A

| Item | Type | Key numbers | Why |
|---|---|---|---|
| Late-Day Flow (leveraged-ETF / last-hour flow): follow a ≥ 0.4 ATR move at 14:00 to 14:30 | Funded strategy (in the plan since 2026-10-12, 2 MNQ), MultiCharts-confirmed (`NQ_Late_Day_Flow.txt`) | MC: 895 trades, 55% win, $95 avg, PF 1.44, t 3.5, 7/9 years (all 895 match Python); longs PF 1.39, shorts 1.48; 2023–26 Sharpe 1.22 (bootstrap 0.45–1.96); corr ≤ 0.13; funded + 2 MNQ: $7,676 / $12,012 vs $7,153 / $11,612, blown 4–6% vs 9–10% | Forced flow, uncorrelated; long side weaker since 2023 (Sharpe 0.59) |
| Overnight Bias (plain, challenge; ADX 30 / 0.25 ATR since 2026-10-13, MultiCharts-confirmed) | Challenge strategy (in use) | ADX30 MC: 676 trades, 51% win, $372 avg, PF 1.66, t 4.9, 9/9 years, Sharpe 1.60 (longs PF 1.67, shorts 1.64; 2023–26 bootstrap Sharpe 0.92–2.26); old ADX 20: 997 trades, PF 1.38 | Challenge pass with VB 8: 46.9% vs 42.8% (2023–26 51.1% vs 44.4%); the ML version adds nothing to the challenge |
| Expiration Open Short | Funded strategy | 105 trades (12 a year, so only ~$5,700 a year per NQ: not S), t 2.6, 59% win, $474 avg, PF 1.93, 8/9 years | Forced flow: index options settle on the expiration-day open; zero correlation; +$1,100 funded |
| Cushion sizing | Risk rule | Blown 34% → 10–12%; 2-year payouts $8,379 → $11,485 | Cuts size exactly when an account is closest to blowing up |
| Monday Long (new direction source) | Funded strategy (replaced OND 2026-10-12) | MC: 450 trades, 55% win, $425 avg, PF 1.55; 2023–26 PF 1.92; corr ≤ 0.18; funded plan $7,153 / $11,612 (1y / 2y) vs $6,876 / $11,366, blown 9–10% | Uncorrelated; weak in 2018–22, so regime-dependent |
| Vault Break | Challenge + funded strategy | 1,743 trades, 66% win, $92 avg, PF 1.26, 9/9 years (funded version: t 4.1, PF 1.41, ~$18,200 a year per NQ; strong but PF too low for S) | High win rate fits Apex rules; the challenge engine; biggest swings in the funded set, so keep at 3 MNQ |
| The Bridge's Monday Long NQ (L644NQ v2.1): Sunday 19:00 CT → Monday 15:55, regular-session daily ADX(7) 10–50 and DI+ > DI−, 100-pt target, no stop | Funded strategy (added 2026-10-13, 1 MNQ next to ours) | MC-confirmed (217/217 trades match the Python port): $541, PF 1.99, t 4.4, 9/9 years, 70% win; Sharpe 1.40, Calmar 0.78, Ulcer 3.7; 2023+ bootstrap Sharpe 0.49–2.31; other weekdays t ≤ 1.0; corr 0.30 with our Monday Long; funded $9,313 / $12,436 vs $8,770 / $12,236, median days to $13k 278 → 255 | Different Monday days and entry from ours; adds by diversifying, not size (2 MNQ blows 11%); never run alone |

## B

| Item | Type | Key numbers | Notes |
|---|---|---|---|
| NFP Fade: fade the 7:30→7:45 payroll reaction, 7:46→9:00, stop 0.5 ATR | Funded strategy (in the plan since 2026-10-13), MultiCharts-confirmed (`NQ_NFP_Fade.txt`) | MC: 79 trades, 52% win, $335, PF 1.79, t 1.9, 7/9 years; 2023–26 PF 2.30, bootstrap Sharpe 0.19–1.54; all 76 Python trades match (corr 1.000); corr ≤ 0.04 | ~9 trades a year; t < 2.5 keeps it below A |
| Vol-Control Sell Flow: short 14:00→15:00 when a lagged S&P vol-control model must sell > 6% of fund size | Funded strategy (in the plan since 2026-10-13), MultiCharts-confirmed (`NQ_Vol_Control_Sell.txt`) | MC: 71 trades (4 Jan-2018 warm-up), 55% win, $427, PF 2.12, t 2.1; 2023–26 PF 3.12, bootstrap Sharpe 0.32–1.56; all 67 Python trades match (corr 1.000); corr ≤ 0.05 | Forced flow, ~8 trades a year; t < 2.5 keeps it below A |
| ES versions of the plan's forced flows (EOS, Monday Long, NFP Fade, Late-Day Flow, Vol-Control Sell) | Robustness check / instrument | Same sign on ES for all five, weaker: per same notional Sharpe 0.12–0.64 vs 0.62–1.16 on NQ; EOS t 1.6, MON 1.7, LDF 1.5, VCS 1.5, NFP 0.3 (does not transfer); NQ–ES daily correlation 0.71–0.95, so half NQ / half ES lowers Sharpe (five together 1.60 vs 1.85). Keep NQ; the ES results support the mechanisms |
| Crabel Stretch Breakout (your MultiCharts file v3): open ± 1.4 × 10-day stretch stop entries to 9:30 CT, stop 0.7 × stretch, out 14:56 | Strategy (Python replica) | 1,653 trades, 22% win, $120, PF 1.25, t 2.7, 9/9 years; 2018–23 PF 1.26, 2024–26 PF 1.23 (holds out of sample); placebo $44; neighbours PF 1.12–1.25 for stops 0.7–1.0; but funded + 1 MNQ $8,591 / $11,969, blown 8% / 6% (plan $8,770 / $12,236); combine + 2 MNQ 45.7% vs 46.9% | Real breakout edge like the noise-area one, but a 22% win rate and lumpy years (2022 = 36%) don't fit Apex rules |
| ONB skips the day after negative GEX | Filter | t = 4.1, 9/9 years; funded +$342 (year 2 flat) | Needs daily GEX typed in; no price-only version matched it |
| Noise-area momentum, long only ("Beat the Market") | Strategy | PF 1.38–1.45, 9/9 years | Wins only 43%; replaces VB poorly ($4,100 vs $5,387) |
| Bootstrap + permutation (out-of-sample resampling) | Method | Funded portfolio Sharpe 90% interval 1.53–3.00 (2023–26); real drawdown smaller than 99% of shuffles (95% shuffle $8,347 vs real $3,351) | Adopted as a standard check; shows the edges aren't luck but the real drawdowns were, and that losses don't cluster |
| r/algotrading post: 100+ retail strategies, ~700 versions | Article / method | Random-entry placebo and trade-through fills applied to all four funded strategies: all pass (Overnight Drift least decisively, beat 97% of random-day runs) (first trade $90 vs random-after-signal $42, beat all 30 runs; $97 → $92 with 1-tick trade-through) |  |
| DriftPullback v2.1 (F. Agnello, Bridge Strategies Feedbacks): 15-min VWAP + 0.10% drift arms, 5-min counter-bar entry, 9:30–14:25 CT, long 80/40, short 80/50 pts, ≤ 4 trades / 2 losses a day | Strategy (Python replica) | 5,733 trades (637 a year), 63% win, $56, PF 1.12, t 4.0, 9/9 years (2018–22 $62, 2023–26 $50); longs t 3.3, shorts t 2.4 (2023–26 $20); random-side placebo −$16; neighbours t 2.3–3.9; limit trade-through 1 pt t 3.0; Sharpe 1.30, Calmar 1.02, Ulcer 5.6, max DD $35k per NQ; longs corr 0.46 with VB; funded + 1 MNQ $9,170 / $11,182, blown 13% (plan $9,313 / $12,436, 3% / 1%); shorts only $9,453 / $12,492 | Real edge, clean placebo, but daily swings too big for the $2,000 trailing drawdown; shorts weak since 2023 |
| The Bridge's Overnight Bias ORB (close beyond the 8:30–8:45 range, ADX(16) ≥ 20, up to 4 trades a day, bar-range and OR-size filters, RTH-ATR stop from the signal close, last entry 12:00) | Strategy (Python replica) | 779 trades, $313, PF 1.52, t 4.4, 9/9 years; placebo $56; Sharpe 1.47, Calmar 1.64, Ulcer 3.1 vs our ONB ADX30 $372 / PF 1.66 / Sharpe 1.60 / Calmar 2.06 and ML v2 $636 / PF 2.12; with our ADX(14) > 30 gate $364, PF 1.66 (= ours); combine pass 38.9% vs 46.9%; funded instead of ML $7,712 / $10,491 at $300 | Real edge, weaker version of ours; its OR-size band doesn't help ours |
| Combine add-ons: Bridge Monday Long 2 MNQ + EOS $500 + Vol-Control Sell 2 MNQ on top of VB 8 + ONB ADX30 | Challenge set (MC trade lists) | Pass 50.5% vs 46.9% (2023–26 55.4% vs 51.1%), blown 47.8% vs 50.0%, cost per pass ~$99 vs $107; best of ~20 combinations, each piece MC-confirmed | Small, consistent gain from uncorrelated forced flows |

## C

| Item | Type | Key numbers | Notes |
|---|---|---|---|
| Overnight Drift (backup; replaced by Monday Long 2026-10-12) | Funded strategy (backup) | 1,039 trades, $71 avg, PF 1.22 (at funded size PF 1.10) | Helps year 1, costs year 2; first to cut. Placebo: $71 vs $36 for random-day longs in the same window, so about half is general overnight drift. Bootstrap Sharpe interval includes zero (P ≤ 0: 9%, 14% since 2023) |
| Opening Drive | Strategy (old research set) | 1,352 trades, 41% win, PF 1.23, MC-confirmed | Superseded by the current challenge pair |
| Turn of the month | Strategy | +$376, t = 2.0 (t = 3.7 with stop) | Weak 2018–22; hurts funded payouts at any size |
| Asymmetric reversal: buy after a big no-news down day (NBER w35840) | Paper / strategy | +23 bp next session, t = 2.4; PF 1.2–1.4 with a stop; funded within noise | Funded effect within noise |
| Overnight-range breakout | Strategy | t = 2.5; funded $1,558–3,097 | Overlaps ONB; funded worse than the set |
| 60-min breakout, longs only, entries 9:00–14:00, flat 15:00 (your idea) | Strategy | PF 1.31, t = 2.4, but 2025–26 negative; correlation 0.41 with VB; funded +$133 year 1, −$309 year 2 at $200 risk | Lost in 2025–26 |
| Headline Shock Follow: follow an unscheduled 5-min jump > 5.5x its normal size, 8:40–14:15, stop = jump, out 60 min | Strategy (Python only) | 835 trades, $142, PF 1.31, t 2.5, 6/9 years; longs and shorts both PF 1.31; placebo $32; corr ≤ 0.15; funded + 1 MNQ $7,922 / $12,097, + 2 MNQ $8,413 / $11,690 | Real edge, but regime-bound: 2025 (tariff headlines) is 45% of the profit, 2023–24 lost; funded within noise |
| Bundle of the three edges (HSF + NFP Fade + Vol-Control Sell Flow) | Funded add-on (NFP + VCS adopted 2026-10-13 after MC confirmation) | Per NQ: 978 trades, PF 1.39, Sharpe 1.11 (2023–26 1.34, bootstrap 0.79–1.97); corr with plan 0.06; NFP $500 + VCS 1 MNQ: funded +$456 year 1 (90% $123–826), +$10 year 2, blown 4% / 3% | Clears noise in year 1 only; candidate for MultiCharts versions, not adopted |
| Morning direction at 10:30 CT, followed to 15:00 (direction search) | Signal | t 2.2, 7/9 years, $112 a day; not yet tested as a trade | Test as a trade next |
| VaultBreak v8 (the Bridge's version): noise band from the 15-session high − low average incl. Sunday sessions, + 7-bar VWAP exit, next-bar time exit | Variant of Vault Break | 1,880 trades, $82, PF 1.23, t 3.9, 9/9 years vs v1 (MC) $92, PF 1.26, t 4.3; Sharpe 1.25 vs 1.35, Calmar 1.02 vs 1.31; only the band matters (VWAP exit never fires); funded at 3 MNQ $8,750 / $12,259 blown 5% / 4% vs $9,313 / $12,436; combine pass 43.1% vs 46.9% | Same strategy, slightly worse band; keep v1 |
| The Bridge's COT Dealer Rank, weekly hold (TFF dealer net 13-week rank > 70 / < 30 + 50-day SMA, re-decided each Friday release) | Positioning (not Apex-legal: holds overnight / weekends) | 51 trades, $3,185, PF 1.98, t 1.8, 8/9 years; all from 32 longs ($5,854; $2,428 a week held vs $864 for long-above-SMA alone); shorts lose; Legacy sister t 0.9 | Possible weekly long-side edge, too few trades; swing accounts only |
| Open-breakout pullback on 15-min bars (your idea): 0.15% break from the 8:30 open, a 15-min bar touching the open and closing back up, bar-low stop, 3R | Strategy (Python, best of 120) | Longs 625 trades, $153, PF 1.30, t 2.4, 7/9 years (2018–22 $121, 2023–26 $197); short at the same fills −$109; same trade on random days −$37; Sharpe 0.79, 2023+ 0.86; funded 1 MNQ fixed $9,492 / $12,589 (noise), risk-sized blows up; combine worse; shorts t ≤ 0.7 | Real modest long pattern, best of many, no room in the plans |

## D

| Item | Type | Result |
|---|---|---|
| Post-settlement reversal (15:00–15:15 fades the last hour) | Forced flow | Very consistent (t −4.0 for following, 1/9 years) but only ~$29 gross a trade: about $12 after costs |
| Wednesday overnight long (prev 15:00 → 8:30) | Calendar | t 2.5, 8/9 years, but 1 of 20 weekday-window tests and overlaps Overnight Drift |
| VIX regime size tilt | Filter | VB +30% per trade in "short vol"; OND better in stress; Funded/pass changes within noise; tilt with cushion sizing untested |
| RSI(2) dip-buying held overnight (from the QQQ RSI + EMA + VWAP article, RSI part only; Apex-legal re-entry at midnight) | Strategy | 94 trades, $1,828, PF 1.97, t 2.2, beats 96% of random-day placebos; Sharpe 0.51, $37k max DD per NQ without a stop, 2025 = 47% of the profit; funded + 1 MNQ $7,134 / $11,898 (worse) |
| Multi-timeframe trend filter on the plan's strategies (daily SMA 20/50/200, 60-min EMA) | Filter | 28 strategy × measure tests on the MultiCharts lists: 1 with t ≥ 2 (ONB ML with the 20-day SMA, $906 vs $388, 8/9 years), about what chance gives; filtering all strategies cuts funded payouts to $3,126–6,470 (from $8,770); ONB-only SMA20 $7,915 / $11,826 |
| Timeframe ensemble: Vault Break on 15 + 30 + 60-min bars, 1 MNQ each, vs 30-min × 3 | Sizing / diversification | Daily correlation 0.77–0.84; Sharpe 1.16 vs 1.20; funded $7,350 / $11,749 vs $8,471 / $12,203 (1-MNQ legs also round to 0 under cushion sizing) |
| MSCI quarterly review closes (last business day of Feb / May / Aug / Nov) | Forced flow | Real: last 10 minutes 2.25× the normal size (0.18 vs 0.08 ATR), last hour 1.8×; but no direction from the day's move (follow / fade t −0.1, 30 days) |
| Month-end close momentum: follow the 8:30→14:45/14:50 direction into the 15:00 close on the last business day | Forced flow | 101 days: t 1.1–2.1 depending on the window (14:46 best, 14:56 negative), 3–6/9 years; ES t 1.6; day before / first day of month nothing; below the t ≥ 3 bar for 36 comparisons |
| BTC Momentum "September Winner" (your MBT file): short when 8:00→8:30 CT is down, hold to 15:00 | Strategy (CME Bitcoin futures, Python) | As coded (window really 7:55→8:25): 993 trades, $47 per BTC ($4.70 per MBT), PF 1.14, t 1.3, 5/8 years, 2024–25 make all the profit; as documented t 0.9; random-side placebo −$42, shorting every day $4; stop 1–2% t 1.7; longs lose; no September effect |
| 0DTE NDX gamma regime from The Bridge (price above / below the cumulative gamma flip, steepness > 0.02) as a volatility gauge and as a filter on the plan | Filter (options data, 2023-03-28 → 2026-07-07) | Below the flip the next 30 min move 30% more (20.0 vs 15.3 bp, both halves), but within realized-vol quintiles 1.00–1.33×; no momentum / reversion difference (corr −0.007 vs −0.004); plan splits: 1 of ~20 with \|t\| ≥ 2 (VCS above $1,331 vs below −$262, 27 trades); previous-session regime: ONB sign flips with the reading time, VB better after below-flip closes (t −1.4 to −2.1, mostly 2025–26) |
| Late-Day Flow longs only when the last 30 minutes of order-flow delta agree (The Bridge MBO) | Filter (order flow, 2018–2026) | $138 vs −$4 a trade, same in 2018–22 and 2023–26 (t 2.1; 1 of ~40 splits); LDF Sharpe 1.17 → 1.25, PF 1.44 → 1.57, Calmar 0.62 → 0.91; funded 2 MNQ $8,801 / $11,843, blown 8% / 7% vs $8,770 / $12,236, 3% / 2% |
| Release fade (8:00–8:30 CT after 7:30 data) | Strategy | +$63, t = 2.9, 485 days; Found after ~24 variants; loses with a stop in the funded bench |
| Last-30-minute momentum (Baltussen et al. 2021) | Paper / strategy | Regression t 1.0 NQ vs 7.3 in the paper; ~$0 per trade since 2018 |
| Gamma last-30 trade (follow after GEX<0, fade high GEX) | Strategy | t = 1.4; funded $3,835–5,006 |
| QQQ 5-minute ORB (Zarattini & Aziz 2023) | Paper / strategy | Replicates before costs (+0.13R); $42 a trade, t = 1.1 after |
| ORB + opening-volume filter (Zarattini et al. 2024) | Paper / strategy | 15-min, 0.2 ATR: t = 2.6 but best of 18; funded worse; overlaps ONB |
| Month-end rebalancing fade | Strategy | NQ t ≤ 1.7, ES nothing |
| Roll-week short | Strategy | Raw ES t = −2.2; PF 1.06–1.13 as a trade; funded worse |
| Day after triple witching, long | Strategy | t = 1.6 raw, PF 1.06 as a trade |
| DIX-high long | Strategy | t = 2.1, driven by 2025 |
| Quiet-day midday fade | Strategy | t = 1.4 |
| VWAP trend, slow version (Zarattini & Aziz VWAP paper) | Paper / strategy | PF 1.08, ~$0 since 2023 |
| NQ–ES spread (follow) | Strategy | +$79 gross, too thin after costs |
| Overnight Drift GEX filter | Filter | Funded $5,433–6,150 |
| FOMC statement reaction (follow / fade 13:00→13:05–13:15, out 13:29–15:00; press conference) | News | 69 days; best of 22 PF 1.62, t 1.5; sign flips with the exit and since 2023 |
| CTA trend-signal flip, fade next day (21/63/126/252-day model) | Forced flow | 2+ flips +$2,397 (22 days, t 4.0), 1+ flips $335 (t 1.7); but random non-CTA lookback sets fade as well (real beats 56%), so not CTA flow; with a stop t 0.7–1.4 |
| Gap Fill (old research set) | Strategy | PF 1.14, but $12 a trade in 2023–26 (vs $76 before) |
| Yes/no (logistic) ML filter for ONB (after Vilkov 2026) | Filter | Kept beat skipped only 2–5/8 years; ridge version stays |
| VWAP Pullback + ADX gate (the Bridge's C.S. profile: ADX(14) 1-min ≥ 20 and falling, long only, flat 15:55) | Strategy (Python replica) | 1,052 trades, $60, PF 1.23, t 2.2, 6/9 years (2018–20 lose; 2023+ $152); no gate $59, random gate $47, inverted gate $21; random-side placebo $0 (= NQ drift); Sharpe 0.73, Calmar 0.27, Ulcer 16.8; funded + 1 MNQ $9,250 / $11,841, blown 7% (plan $9,313 / $12,436) |
| Donchian(96) breakout + Larry Williams Large Trade Index > / < 50 + volume above average, TP 100 / SL 50 points (user's paste) | Strategy (Python) | 15-min as coded $67, PF 1.10, t 1.8 (holds overnight); Apex version 1,631 trades, $61, PF 1.11, t 1.8, 6/9 years, 2018–22 $113 vs 2023–26 −$6; shorts t 0.4; placebo $6; without LWTI $21; Sharpe 0.61, 2023+ −0.05 |
| Open-breakout pullback (your idea): break X% from the 8:30 open by 10:30, buy the pullback to the open (limit or 5-min confirmation, bar-low / 0.20-ATR stop), R-multiple or breakout-extreme targets | Strategy (Python, 120 combinations) | No combination t ≥ 2; best longs 0.50% limit at the open 2R: 336 trades, $171, PF 1.23, t 1.6 (2018–22 $128, 2023–26 $233); after a 0.15% break $37; mirrored short −$16; Sharpe 0.54; funded + $200 risk $9,545 / $11,533, blown 9%; shorts mostly negative |
| Time clusters in the plans' trades (entry half-hour, weekday, month, earlier exits; ~170 cells) | Filters / exits | 12 cells with |t| ≥ 2 (≈ 8 by chance); current exits best or tied; VB without September funded $9,833 / $12,670 but 1 of 170 cells and Sept 2026 positive; LDF no-Friday, ONB no-Friday, NFP 8:45 exit within noise or worse |
| NQ–YM relative value (your idea): follow / fade the β-hedged spread from the 8:30 open at 9:00–12:00 or on the gap, hold to 14:55 | Strategy (two legs, Python) | Fading loses (0/9 years at 0.5σ, t to −3.6): divergences trend. Following, best 9:00 |z| ≥ 1: $164, t 1.3 (2023–26 $55) after two legs of costs; NQ leg alone $538, t 2.4, but it's NQ's own early momentum (same direction 95%; biggest NQ moves alone $623) |

## F

| Item | Type | Result |
|---|---|---|
| VWAP always-in, 1-minute (Zarattini & Aziz) | Paper / strategy | −$1 a trade; costs $17 vs edge $6 |
| Fading big intraday moves | Strategy | Loses in every setting (PF 0.71–0.95) |
| Round numbers (fade or break) | Strategy | PF 0.59–0.95 |
| VWAP Pullback ADX | Strategy | PF 0.87 |
| Pre-FOMC drift (Lucca & Moench) | Paper | Gone since 2018 (−$12 NQ) |
| Announcement-day premium (Savor & Wilson) | Paper | No premium |
| IBS, pivot points ("151 Trading Strategies") | Strategy | Not significant / loses |
| Bhatti gold VWAP-EMA pullback (SSRN 6650958) | Paper | Results were simulated, not backtested; PF 0.94 on NQ |
| ES versions of VB / ONB / OND | Strategy | PF 1.01–1.13; no edge worth adding |
| Window trades (fixed brackets in unused hours) | Strategy | Nothing significant |
| CFTC positioning (Traders in Financial Futures) | Data / filter | No relation to next week/month; filters slightly worse |
| Index rebalance days, buyback blackout, VIX-expiration Wednesday | Calendar | Too few days, no effect, or FOMC overlap |
| Commodity storage/momentum (Gorton et al. 2008) | Paper | Monthly commodity book; nothing for NQ |
| Implied equity term structure (NY Fed SR 1203) | Paper | Long-horizon asset pricing; no trading rule |
| The Golden Dilemma (Erb & Harvey 2013, SSRN 2078535) | Paper | Gold valuation over years to decades; no trading rule, and GC data here covers one week |
| Momentum Turning Points (Goulding, Harvey & Mazzoleni, SSRN 3489539) | Paper / filter | Monthly states; on NQ 2018–26 'Bear' months were followed by gains (+278 bp), not losses; strategy splits flip with the window |
| Fact, Fiction and Momentum Investing (Asness et al. 2014, SSRN 2435323) | Paper | Cross-sectional stock momentum (12-1 month winners vs losers); myth-busting essay, no NQ day-trading rule |
| Index MA agreement for ES (your idea; ES + NQ only so far, YM pending) | Strategy | MA 5–200, three modes: −$72 to +$23 a day, t −1.9 to +1.0; shorts lose; long side ≈ market drift |
| 60-min 40-bar breakout + 200 SMA, 2x ATR stop (your idea) | Strategy | As written: PF 1.08, t 0.7, shorts lose, −$97k max DD, holds 2–3 days (not Apex-legal); 2026 −$76k |
| Hybrid channel breakout + MA retrace + volume (Rogul 2026, SSRN 6469419) | Paper / strategy | 42 trades in 3 hand-picked months, perfect-hindsight bias, parameters withheld. Mechanical 1-min version: no bias PF 1.01–1.11 (Sharpe 0.47); hindsight bias PF 2.29 (the paper's 'edge'); ONB bias PF 1.62 but random entries in the ONB direction do better ($356 vs $284), so the engine adds nothing |
| Price-pattern direction search: 25 signals known by 8:45 (Asia/Europe session, gap, order-flow imbalance, prior day, 2–60-day momentum, NQ–ES, VIX) and a frozen ridge of the non-ONB ones | Signal search | Overnight-range signals just re-find ONB (80–95% agreement); the rest: ridge t 3–4 in 2018–22, negative 2023–26 and walk-forward ≈ $0 |
| Overnight VWAP fades (Asia 17:00–23:59, London 0:00–7:25, target VWAP) | Mean reversion | Asia PF 0.57–0.93 (t to −3.2); London PF 0.86–1.05, 2023+ negative |
| Multi-day pullback (fade 2–4 sessions in a row, next 8:30–15:00) | Mean reversion | PF 1.02–1.18, t ≤ 0.9, 2023+ negative |
| 9:00 CT releases and non-payroll 7:30 releases (CPI, PPI...), follow or fade | News | t ≤ 0.9 |
| Fading headline jumps (day or overnight); following overnight jumps | News | Fades lose (t to −3.5); overnight follow ≈ $0 |
| Following CTA flows (next day, into the close, break of the trigger level) and same-day vol-control flow | Forced flow | CTA follow next day t −1.9 (2+ flips −4.1), trigger break −$409 (t −2.4), into close t 0.4; vol-control lag 0 t ≤ 0.6; vol-control does not explain Late-Day Flow |
| Nasdaq-100 special rebalance | Forced flow | One event in 2018–26 (21 Jul 2023): not testable |
| RSI + EMA + rolling VWAP on QQQ (Rule-Based Trader, Oct 2026) | Article / strategy | Claimed PF 3.54; on NQ 2018–26 the 3-filter version PF 1.16, t 0.3, below random rising-EMA days ($517 vs $890); each filter lowers PF; Apex-legal version −$155; 48 neighbours PF 0.54–3.62 (fragile); RTH part ≈ 0 |
| Bollinger Band reversals (your idea): fade a close outside the bands or the close back inside; 5 / 15-min, K 2–3, RTH and overnight, ADX / band-width filters; daily version | Mean reversion | 72 intraday versions: none with t ≥ 2, 42% significantly negative (overnight t to −5.5); best (5-min K 3 re-entry, quiet days) t 1.1 on 205 trades, falls apart with other stops; daily lower-band buy t 0.8 |
| 20/50 EMA zone pullback, 10-min, stop 30 / target 65 points (your spec) | Strategy | As specified: 11,627 trades, 33% win, −$10, PF 0.98, t −1.2, 4/9 years; = random entries in the EMA-trend direction (−$7); shorts PF 0.93, longs 1.02; best of 12 variants (next-bar confirmation) $12, t 1.3, 5/9 years |
| Gold Breakout 15M (TradingView): Asia-range (17:00–23:00 CT) both-side stop breakout, 1% stop, out 12:00 CT, ported to NQ | Strategy | Gold-literal on NQ: 2,246 trades, −$36, PF 0.97, t −0.6, 4/9 years, below the random-side placebo (−$20); NQ-adapted best of 24 (range to 8:30, 0.5% stop) $83, t 2.0, but placebo $46, corr 0.39 with ONB ML, funded worse ($8,531 / $11,755 vs $8,770 / $12,236); = the C-tier overnight-range breakout |
| Glow Ribbon Flip (TradingView): EMA(21) + ratcheting ATR band, stop-and-reverse flips + pullback re-entries | Strategy | Defaults on 15-min NQ: 7,829 trades, $2, PF 1.00, Sharpe −0.02, $145k max DD per NQ; 20 variants (5–60 min, 2R / no target, 2–3 ATR, day session, flips only): best t 1.2 (day session 15-min, $45, 5/9 years, Sharpe 0.38); longs beat shorts in every variant (just NQ's drift) |
| Weekly (PM-settled) options expiry Fridays: afternoon pin, follow / fade into the close, strike magnet (NQ 100s), Monday after | Forced flow | Afternoon only ~5% quieter than Mon–Thu; follow / fade t ≤ 0.5; magnet $28, t 0.8 (monthly Fridays −$127); Monday after t ≤ 0.6 (after monthly expiry t 1.8, 88 days) |
| JPMorgan Hedged Equity collar reset (quarter-ends, est. call strike = previous reset × 1.04) | Forced flow | 35 resets: day ranges ~9% lower in the 5 days before (0.75 vs 0.83 ATR), but short-near-strike −$104 (t −0.2), long after the reset $373 (t 1.1) |
| Bitcoin forced flows: spot-ETF close (follow the day 14:01→15:00 since Jan 2024) and CME monthly settlement (BRR, last Friday ~10:00 CT) | Forced flow (BTC) | ETF-era last hour: following loses (t −2.6), fading ≈ $0 after costs; expiry Fridays 9:00–10:00 ~20% more volatile, no direction |
| VWAP pullback after a 30-min opening-range break (user's file VWAP_Pullback_NQ_Margin_Vol), swing stop / target | Strategy | Replica matches the author since 2021 ($74, PF 1.17, 57% win, original bracket-only) but 2018–20 lose −$48k: 2018–26 $23, PF 1.06, t 0.8; Apex version (flat 15:55) −$2, PF 0.99; random-side placebo $0; shorts lose every year but one; longs only $62, t 2.0 = NQ drift; funded + 1 MNQ $8,423 / $11,672 (worse) |
| Gamma flip cross breakout (The Bridge 0DTE NDX flip + basis on NQ): first close through the flip 9:00–13:30 CT, trade the cross, stop 0.3 ATR, out 14:55 | Strategy (options data) | 499 trades, −$79, PF 0.93, t −0.6, Sharpe −0.39; fake levels at flip ±0.5% / ±1% the same (−$406 to +$22); fading the cross $140, t 1.3 |
| Gamma regime follow / fade: follow the first hour below the flip, fade it above | Strategy (options data) | Regime rule −$105, PF 0.91, Sharpe −0.54; following beats fading in both regimes (above $160 vs −$247, below $185 vs −$319) |
| 0DTE strike pin: from 13:30 CT on above-flip days trade toward the major positive-gamma strike (0.15–1% away) | Forced flow (options data) | 229 days, price moves toward the strike 49% of the time; −$161, t −1.8, Sharpe −1.13; toward another 100-point NDX strike (placebo) −$115 |
| Order-flow prediction (The Bridge MBO, 2018–2026): delta 5–30 min, RTH delta, book / count imbalance, depth 10 / 50, pulled orders, queue depletion, icebergs, big prints, walls → next 5 / 15 / 30 min | Signal (order flow) | All 39 correlations −0.008 to +0.013 (costs need ~0.05); best design feature (50-level depth) as a 15-min trade: 2018–22 $4, 2023–26 −$24, Sharpe −0.27 (holdout −0.80) |
| Opening order flow: trade the sign of the 8:30–9:30 CT delta to 14:55 | Strategy (order flow) | 2,117 days $8, PF 1.01, Sharpe 0.05; the price move instead $111 (t 2.0); when they disagree delta's side −$214 |
| Big prints (≥ 99.5th percentile of the prior 20 sessions): follow 15 / 30 / 60 min | Strategy (order flow) | 2,006 prints: $2 / −$9 / −$2 a trade, PF 0.97–1.01, buys and sells alike |
| The Bridge's VWAP Fade: fade a 1-min close beyond Globex VWAP ± 2σ, target ± 1σ, no stop, 60-bar time exit, 8:30–14:00 CT | Strategy (Python, VWAP / σ checked vs the Bridge's) | 4,009 trades, −$25, PF 0.93, t −1.5, 3/9 years; longs and shorts both lose; random side −$13; 10 variants: 9 lose, best (3σ, VWAP target, 4σ stop) $22, t 0.4; Sharpe −0.52, max DD $108k per NQ |
| The Bridge's Large Trade Predictability (next-bar: candle colour / whale print ≥ 100–200 / both, 1- and 5-min bars) | Signal (order flow, 2018–2026) | 1-min gross +0.05 to +0.40 points a bar ($2–8 a trade) vs $17.25 costs: net −$9 to −$15 a trade (whale ≥ 100: 4,385 trades, PF 0.85); 5-min gross negative, net −$21 to −$44 |
| The Bridge's Liquidity Predictability (follow resting-book imbalance, 10 / 20 / 50 levels, ±20 / 40%, next bar) | Signal (order flow, 2018–2026) | 1-min: every row net −$10 to −$23 (best gross +0.35 pts, t 2.5, both-agree 50 levels); 5-min: 2 of 11 rows positive (±40%, 292–612 trades, $26–27), one negative 2023–26; fading −$18 / −$29 |
| The Bridge's COT Dealer Rank as an Apex day trade (8:30 → 15:00 in the weekly state) or a filter on the plan | Positioning | TFF $42 a day, t 0.3 (placebo $17); Legacy $47, t 0.4; other variants negative; filter splits all |t| ≤ 1.2 |
| Open-breakout pullback on 1-min bars (your idea, follow-up) | Strategy (Python, 120 combinations) | Longs: 3% of combinations positive 2018–22; best t 1.6 ($49, 2018–22 −$10); the 15-min winner (0.15%, 3R) −$13 a trade; 1-minute stops too tight |
| The plan's strategies on YM (Dow futures), 2018–2026 | Instrument | NQ–YM daily correlation 0.80 (ES 0.93), opposite direction 27% of days; every plan strategy is near zero or negative on YM: VB $1, ONB ADX30 $4, EOS $9, Monday $41, NFP −$43, LDF $8, Bridge Monday $80 (t ≤ 1.3); Sharpe −0.19 to 0.43 |
| 101 Formulaic Alphas (Kakushadze / WorldQuant 2015, SSRN 2701346), time-series port on NQ and ES (rank → 60-day percentile, yesterday's close → today 8:30–14:59) | Paper / signal search (97 testable alphas × 2 rules) | Design winners positive in 2023–26 25% (random signs 46%), design–holdout rank correlation +0.05 (placebo ±0.16); vote of all 101 design $184 → holdout −$151 (Sharpe −0.58); best single (#37 extreme, design t 3.8) holdout t 0.7, shorts lose, max DD $75k per NQ; ES no better |
| Pre-holiday / post-holiday / mid-month pay days | Calendar | t ≤ 0.5 |
| Technical rules and FX intervention (LeBaron 1996, SSRN 1105) | Paper | 150-day MA rule on DM/yen 1979–92, Sharpe 0.7–1.0, but almost all of it on Fed intervention days (Sharpe 0.1–0.4 without); currencies, multi-day holds, and that intervention regime is gone. MA rules on NQ already failed here (MA 5–200 agreement, 50-day MA distance) |
| Forced-flow round 3: vol-target de-levering (realized-vol jumps), quarter-end pension fade, Friday pre-weekend de-risking | Forced flow | t ≤ 0.8 (vol target), −0.2 (quarter end), Friday windows −1.0 to 0.2 |
| The Power of Price Action Reading (Zarattini & Stamatoudis 2024, SSRN 4879527) | Paper | Single stocks gapping up ≥ 6%, held up to 30–50 days: every mechanical rule loses or is ~0R (best +0.07R); profits only with a human picking charts (+0.25R) and managing trades (+0.9R), not reproducible as rules. NQ has no such gaps; NQ gap follow and opening-range rules were already tested here (gap follow t −0.1 out of sample) |
| 0DTE trading rules (Vilkov 2026) | Paper | SPX options; not tradable on Apex |
| 0DTE gamma and volatility (Dim, Eraker & Vilkov 2025) | Paper | Needs intraday 0DTE dealer positions (paid Cboe data) |
| Contrarian VRP ETF strategy (SSRN 4841308) | Paper | Rules undefined, no costs, multi-day ETFs |
| SPY/TQQQ "arbitrage" (SSRN 4944736) | Paper | Unhedged 1:1 share pair; a disguised directional bet |
| Futures short-term reversal (QuantConnect) | Article | Code contradicts its description; weekly multi-market holds |
| Mean-reversion Colab notebook | Notebook | Not noteworthy (reviewed earlier) |

## Adding a new item

Test it on the funded bench (or the challenge simulator if it's a challenge idea), then
place it by the definitions above, with its key numbers and a one-line reason. Move items
when new evidence arrives (e.g. a MultiCharts confirmation moves C → A/S, a live
breakdown moves an S down).
