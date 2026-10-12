# Tier list: every strategy, filter and paper tested

S–F scale, updated as each new idea is tested. Results are NQ 2018–2026 unless noted, per
NQ after $7.25 costs and 1 tick of slippage per fill. "Funded" = expected payouts per Apex
50K Performance Account within 1 year (2 years in brackets); the current set scores
$6,928 ($8,379), or $6,995 ($11,485) with cushion sizing.

## What the tiers mean

| Tier | Meaning |
|---|---|
| **S** | In the plan, MultiCharts-confirmed, and one of the main sources of payouts |
| **A** | In the plan and MultiCharts-confirmed; solid but not the main driver |
| **B** | In use with a narrow role (backup, challenge-only, or thin edge) |
| **C** | Real edge or useful tool, not adopted (needs data, automation or more proof) |
| **D** | The effect exists but is too weak to trade after costs, stops or Apex rules |
| **F** | No edge, loses money, flawed study, or can't be traded on Apex |

## S

| Item | Type | Key numbers | Why |
|---|---|---|---|
| Overnight Bias ML | Funded strategy | 41% of ONB days kept; walk-forward kept $476 vs skipped $171, 6/8 years; funded $6,928 vs $6,495, blown 34% vs 42% | Biggest single payout driver; frozen ridge filter on ONB (Kelly & Xiu ML survey) |
| Expiration Open Short | Funded strategy | 105 trades, 59% win, $474 avg, PF 1.93, 8/9 years | Forced flow: index options settle on the expiration-day open; zero correlation; +$1,100 funded |
| Cushion sizing | Risk rule | Blown 34% → 10–12%; 2-year payouts $8,379 → $11,485 | Cuts size exactly when an account is closest to blowing up |

## A

| Item | Type | Key numbers | Why |
|---|---|---|---|
| Vault Break | Challenge + funded strategy | 1,743 trades, 66% win, $92 avg, PF 1.26, 9/9 years | High win rate fits Apex rules; the challenge engine; biggest swings in the funded set, so keep at 3 MNQ |

## B

| Item | Type | Key numbers | Why |
|---|---|---|---|
| Overnight Bias (plain) | Challenge strategy | 997 trades, 49% win, $280 avg, PF 1.40, every year positive | Challenge pass 43.8% with VB 8; the ML version adds nothing to the challenge |
| Overnight Drift | Funded strategy | 1,039 trades, $71 avg, PF 1.22 (at funded size PF 1.10) | Helps year 1, costs year 2; first to cut. Placebo: $71 vs $36 for random-day longs in the same window, so about half is general overnight drift |

## C

| Item | Type | Key numbers | Why not adopted |
|---|---|---|---|
| ONB skips the day after negative GEX | Filter | t = 4.1, 9/9 years; funded +$342 (year 2 flat) | Needs daily GEX typed in; no price-only version matched it |
| Noise-area momentum, long only ("Beat the Market") | Strategy | PF 1.38–1.45, 9/9 years | Wins only 43%; replaces VB poorly ($4,100 vs $5,387) |
| Opening Drive | Strategy (old research set) | 1,352 trades, 41% win, PF 1.23, MC-confirmed | Superseded by the current challenge pair |
| VIX regime size tilt | Filter | VB +30% per trade in "short vol"; OND better in stress | Funded/pass changes within noise; tilt with cushion sizing untested |
| Turn of the month | Strategy | +$376, t = 2.0 (t = 3.7 with stop) | Weak 2018–22; hurts funded payouts at any size |
| Release fade (8:00–8:30 CT after 7:30 data) | Strategy | +$63, t = 2.9, 485 days | Found after ~24 variants; loses with a stop in the funded bench |
| r/algotrading post: 100+ retail strategies, ~700 versions | Article / method | Random-entry placebo and trade-through fills applied to all four funded strategies: all pass (Overnight Drift least decisively, beat 97% of random-day runs) (first trade $90 vs random-after-signal $42, beat all 30 runs; $97 → $92 with 1-tick trade-through) |

## D

| Item | Type | Result |
|---|---|---|
| Last-30-minute momentum (Baltussen et al. 2021) | Paper / strategy | Regression t 1.0 NQ vs 7.3 in the paper; ~$0 per trade since 2018 |
| Gamma last-30 trade (follow after GEX<0, fade high GEX) | Strategy | t = 1.4; funded $3,835–5,006 |
| QQQ 5-minute ORB (Zarattini & Aziz 2023) | Paper / strategy | Replicates before costs (+0.13R); $42 a trade, t = 1.1 after |
| ORB + opening-volume filter (Zarattini et al. 2024) | Paper / strategy | 15-min, 0.2 ATR: t = 2.6 but best of 18; funded worse; overlaps ONB |
| Asymmetric reversal: buy after a big no-news down day (NBER w35840) | Paper / strategy | +23 bp next session, t = 2.4; PF 1.2–1.4 with a stop; funded within noise |
| Overnight-range breakout | Strategy | t = 2.5; funded $1,558–3,097 |
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
