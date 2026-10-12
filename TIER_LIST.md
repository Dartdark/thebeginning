# Tier list: every strategy, filter and paper tested

S–F scale, updated as each new idea is tested. Results are NQ 2018–2026 unless noted, per
NQ after $7.25 costs and 1 tick of slippage per fill. "Funded" = expected payouts per Apex
50K Performance Account within 1 year (2 years in brackets); the current set (VB 3, ONB ML $400,
Monday Long 1 MNQ, EOS $700, cushion sizing) scores $7,153 ($11,612).

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
| Overnight Bias (plain; recommended ADX 30 / 0.25 ATR from parameter clusters, challenge pass 46.8% vs 43.3%) | Challenge strategy (in use) | 997 trades, 49% win, $268 avg, PF 1.38, t 3.8, 8/9 years, about $30,400 a year per NQ | Challenge pass 43.8% with VB 8; the ML version adds nothing to the challenge |
| Expiration Open Short | Funded strategy | 105 trades (12 a year, so only ~$5,700 a year per NQ: not S), t 2.6, 59% win, $474 avg, PF 1.93, 8/9 years | Forced flow: index options settle on the expiration-day open; zero correlation; +$1,100 funded |
| Cushion sizing | Risk rule | Blown 34% → 10–12%; 2-year payouts $8,379 → $11,485 | Cuts size exactly when an account is closest to blowing up |
| Monday Long (new direction source) | Funded strategy (replaced OND 2026-10-12) | MC: 450 trades, 55% win, $425 avg, PF 1.55; 2023–26 PF 1.92; corr ≤ 0.18; funded plan $7,153 / $11,612 (1y / 2y) vs $6,876 / $11,366, blown 9–10% | Uncorrelated; weak in 2018–22, so regime-dependent |
| Vault Break | Challenge + funded strategy | 1,743 trades, 66% win, $92 avg, PF 1.26, 9/9 years (funded version: t 4.1, PF 1.41, ~$18,200 a year per NQ; strong but PF too low for S) | High win rate fits Apex rules; the challenge engine; biggest swings in the funded set, so keep at 3 MNQ |

## B

| Item | Type | Key numbers | Notes |
|---|---|---|---|
| Late-Day Flow (leveraged-ETF / last-hour flow): follow a ≥ 0.4 ATR move at 14:00 to 14:30 | Funded candidate (`NQ_Late_Day_Flow.txt`) | 898 trades, 55% win, $94 avg, PF 1.44, t 3.5, 7/9 years; longs and shorts both positive; neighbours t 2.9–3.9; beats all 20 random-side runs; funded + 2 MNQ: $7,648 / $12,019 vs $7,153 / $11,612, blown 4–6% vs 9–10% | Found among ~70 comparisons; ES weaker (t 1.2); needs a MultiCharts check |
| ONB skips the day after negative GEX | Filter | t = 4.1, 9/9 years; funded +$342 (year 2 flat) | Needs daily GEX typed in; no price-only version matched it |
| Noise-area momentum, long only ("Beat the Market") | Strategy | PF 1.38–1.45, 9/9 years | Wins only 43%; replaces VB poorly ($4,100 vs $5,387) |
| Bootstrap + permutation (out-of-sample resampling) | Method | Funded portfolio Sharpe 90% interval 1.53–3.00 (2023–26); real drawdown smaller than 99% of shuffles (95% shuffle $8,347 vs real $3,351) | Adopted as a standard check; shows the edges aren't luck but the real drawdowns were, and that losses don't cluster |
| r/algotrading post: 100+ retail strategies, ~700 versions | Article / method | Random-entry placebo and trade-through fills applied to all four funded strategies: all pass (Overnight Drift least decisively, beat 97% of random-day runs) (first trade $90 vs random-after-signal $42, beat all 30 runs; $97 → $92 with 1-tick trade-through) |  |

## C

| Item | Type | Key numbers | Notes |
|---|---|---|---|
| Overnight Drift (backup; replaced by Monday Long 2026-10-12) | Funded strategy (backup) | 1,039 trades, $71 avg, PF 1.22 (at funded size PF 1.10) | Helps year 1, costs year 2; first to cut. Placebo: $71 vs $36 for random-day longs in the same window, so about half is general overnight drift. Bootstrap Sharpe interval includes zero (P ≤ 0: 9%, 14% since 2023) |
| Opening Drive | Strategy (old research set) | 1,352 trades, 41% win, PF 1.23, MC-confirmed | Superseded by the current challenge pair |
| Turn of the month | Strategy | +$376, t = 2.0 (t = 3.7 with stop) | Weak 2018–22; hurts funded payouts at any size |
| Asymmetric reversal: buy after a big no-news down day (NBER w35840) | Paper / strategy | +23 bp next session, t = 2.4; PF 1.2–1.4 with a stop; funded within noise | Funded effect within noise |
| Overnight-range breakout | Strategy | t = 2.5; funded $1,558–3,097 | Overlaps ONB; funded worse than the set |
| 60-min breakout, longs only, entries 9:00–14:00, flat 15:00 (your idea) | Strategy | PF 1.31, t = 2.4, but 2025–26 negative; correlation 0.41 with VB; funded +$133 year 1, −$309 year 2 at $200 risk | Lost in 2025–26 |
| Morning direction at 10:30 CT, followed to 15:00 (direction search) | Signal | t 2.2, 7/9 years, $112 a day; not yet tested as a trade | Test as a trade next |

## D

| Item | Type | Result |
|---|---|---|
| Post-settlement reversal (15:00–15:15 fades the last hour) | Forced flow | Very consistent (t −4.0 for following, 1/9 years) but only ~$29 gross a trade: about $12 after costs |
| Wednesday overnight long (prev 15:00 → 8:30) | Calendar | t 2.5, 8/9 years, but 1 of 20 weekday-window tests and overlaps Overnight Drift |
| VIX regime size tilt | Filter | VB +30% per trade in "short vol"; OND better in stress; Funded/pass changes within noise; tilt with cushion sizing untested |
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
| Gap Fill (old research set) | Strategy | PF 1.14, but $12 a trade in 2023–26 (vs $76 before) |
| Yes/no (logistic) ML filter for ONB (after Vilkov 2026) | Filter | Kept beat skipped only 2–5/8 years; ridge version stays |

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
| Pre-holiday / post-holiday / mid-month pay days | Calendar | t ≤ 0.5 |
| Technical rules and FX intervention (LeBaron 1996, SSRN 1105) | Paper | 150-day MA rule on DM/yen 1979–92, Sharpe 0.7–1.0, but almost all of it on Fed intervention days (Sharpe 0.1–0.4 without); currencies, multi-day holds, and that intervention regime is gone. MA rules on NQ already failed here (MA 5–200 agreement, 50-day MA distance) |
| Forced-flow round 3: vol-target de-levering (realized-vol jumps), quarter-end pension fade, Friday pre-weekend de-risking | Forced flow | t ≤ 0.8 (vol target), −0.2 (quarter end), Friday windows −1.0 to 0.2 |
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
