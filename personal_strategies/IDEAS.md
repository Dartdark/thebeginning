# Ideas for the future personal account (collected 2026-10-22)

The personal account starts from Apex payouts (not savings), ~$10k at 1/10 size (MNQ), once 6-12 months of live results
match the backtest (`DEVELOPMENT_PROCESS.md` 'Strategy lifecycle'). No Apex rules there: overnight / multi-day holds, no
$2,000 trailing limit, no daily loss limit, no payout caps. Everything below still goes through the normal process
(evidence sheet → plan → test → checker → forward log) before money goes on it.

**Portfolio built from these: [`PORTFOLIO.md`](PORTFOLIO.md)** (2026-10-23).

## 1. Already tested and ready (strongest first)

| Idea | Status / evidence | Where |
|---|---|---|
| **The Apex funded plan without Apex limits**, every strategy at 1 NQ (CL fade 1 CL) | Backtest $101k a year, max DD $24k, Sharpe 2.75 (2018-26, in-sample); needs ~$80-120k per 1-NQ plan for a 20-30% max DD, so start at MNQ size | `funded_strategies/FUNDED_PLAN.md` 'Apex vs a personal account', `analysis/personal_account_test.py` |
| **Twin Continuation v2.1** (user's; swing breakout + morning momentum, NQ, can hold overnight) | A: t 5.5, DSR 0.995, MultiCharts-confirmed (1,069/1,074 entries); wrong shape for Apex (swing stops ~$6k per NQ). The profile the user wants: big edge, trades a lot | `personal_strategies/Twin_Continuation.txt`, `checks/candidates/twin_continuation/` |
| **Relative Strength NQ / ES, both sides** | B: $306 per NQ, t 4.0, 9/9 years, MC-confirmed; ~1 MNQ per $25k of account | `funded_strategies/NQ_Relative_Strength.txt` |
| **Gold Breakout 15M** (user's TradingView idea) | C: $138 per GC, t 3.1, 7/9 years; hurt the Apex plan, fine as a small diversifier | `personal_strategies/Gold_Breakout_15M.txt` |
| **FC 2B, Flow-Confirmed Opening Drive** (user's file, 2026-10-23; NQ, 09:01 entry in the opening drive's direction when its volume-weighted candle flow is unusually one-sided) | A on its numbers: MC-confirmed, $275 per NQ, PF 1.51, t 4.0, 9/9 years, checker PASS WITH CONCERNS; adds nothing to the Apex plans (cap-bound); forward log from 2026-10-26 | `checks/candidates/fc_2b/` |
| **Sunday reopen push** (trade the weekend gap's direction at the 17:00 CT first print, out 17:01) | WATCHLIST #22: $179 per NQ, t 2.5, but only fillable with a pre-open auction order; forward-log ~20 Sundays first | `analysis/sunday_reopen_test.py` |

## 2. Tested, weak (only as small diversifiers)
- Overnight long NQ 15:00 → 08:30: $83 a night (t 1.4); turn of month NQ (t 1.4); 6-market daily trend portfolio Sharpe
  0.46 but +10% in 2022, correlation with ES −0.09: all D (`analysis/overnight_round.py`).
- Daily swing "building blocks" (5 / 20-day holds, 7 markets): 0 of 32 pass, the longs are just the 2018-26 bull drift
  (`analysis/blocks_step1b_daily_test.py`).

## 3. Not tested yet: from books / podcasts (2026-10-22)
| Idea | Source | What it needs |
|---|---|---|
| **Kusho FAR / v9** (user's upload, 2026-10-23: 15-min bullish small-wick bar above EMA 50 → limit retest of its open, swing stop, 3R, early break-even; v9 adds shorts on down-trend days; holds into the evening / weekend) | Same author as FC 2B / S47 (Codex source review `agents/codex/results/kusho_source_review.md`) | Native MC reports (the intraday Apex version is C03, separate); fixes for zero-risk swings and the entry-bar stop; ~320 trades a year, so a test has real power |
| **Weekend Trend Trader** (stocks, weekly): index above its 200-day MA; buy a 20-week closing high with a 20-week gain > 30%; rank by that gain; 20 positions x 5%; 20% trailing stop on the weekly close (10% when the index turns down); exits at Monday's open; order ≤ 2-3% of average daily volume | Nick Radge (Chat With Traders; book *Unholy Grails*) | Daily stock data WITH historical index members (e.g. Norgate, paid), dividend-adjusted signals |
| **Relative momentum on stocks**: when the index trends up, hold the strongest stocks by ~12-month momentum (Russell 1000 / Nasdaq 100), rotate monthly | Nick Radge (Algorithmic Advantage) | Same data as above |
| **All-weather tactical asset allocation**: 6-12 broad ETFs (US / global equities, gold, bonds, commodities, ~5% bitcoin), hold each only while its momentum is positive, rebalance monthly to fixed weights (60/40 or 50/50 growth / defensive); single-digit drawdowns reported. Two versions: (a) static: 6 ETFs, each simply in or out (cash when out); (b) two buckets of ~6 ETFs: hold the 2 strongest growth ETFs at 30% each and the strongest defensive ETF at 60% of the defensive half. Trades only at month-end; trimming winners back to weight keeps any one position from dominating | Nick Radge (his retirement account) | Free: ETF daily closes (long histories); simplest to test of these |
| **Diversified multi-sector futures portfolio** (20-30 strategies over ~7 sectors; ≤ 3 stock-index strategies of 30, because 'uncorrelated' index strategies all went long together in Feb 2018) | Kevin Davey | More strategies in other sectors (our CL / GC / ZN / 6E tests mostly failed so far) |
| **Close-based stops** (stop judged on the bar close, exit next open: fewer spike stop-outs) | Nick Radge | Dangerous on Apex (limits hit intrabar); fine to test for multi-day holds |
| **Parameter "swarm"**: trade several settings of one system at once instead of picking one | Nick Radge (large CTAs) | Our VB 15/30/60-min ensemble was slightly worse; retest on a multi-day system |

| **ES Momentum + Keltner Stochastic** (pullback in a trend, holds overnight): KS = where the close sits in a 5-bar Keltner channel (±0.5 ATR), 0-100. Long when close > close[MomLengthL] and KS < Threshold; short when close < close[MomLengthS] and KS > Threshold; exit when KS crosses back over Threshold; stop 4 x ATR(15) long / 1 x ATR(15) short. ~70% win, both sides profitable; **live since July 2021 after development stopped** | Kevin Davey (video 2026-10-22; code at kjtradingsystems.com) | Bar size and the three optimised inputs aren't given (his email pack has them). Same family as our RSI(2) dip-buy held overnight (D: t 2.2, $37k DD per NQ without a stop). Test as pre-registered with his published settings, not a fresh optimisation; ES data 2017-26 is in `data/`. His 'supercharged' version is sizing only (contracts = 1 + 0.33 x equity / $15k, max 15): more leverage, not more edge |
| **Multi-market screening of one entry** (one rule, ~44 futures x 5 bar sizes, walk-forward, costs in; keep only cases with net > $25k AND max DD < $25k per contract, and MC return / DD high) | Kevin Davey (MACD test, 2026-10-22) | Futures data for many markets (we have NQ / ES / CL / GC / ZN / 6E); a way to build a personal multi-sector set. His MACD result: 6 of 220 pass, so plain indicator entries are not the starting point |

## 4. Rules for running it (from the same sources)
- Size for about **half the drawdown you think you can take** (Davey); the plan's max drawdown ≤ 20-30% of the account.
- **Sequence risk** (Radge): the closer the money is to being needed, the lower-volatility the mix should be. The ORDER
  of gains and losses matters once money is taken out: $100k, −$10k a year, returns −30% / +20% / +20% ends at $64.4k,
  the same returns as +20% / +20% / −30% end at $75.4k (without withdrawals both end at $100.8k). A loss before a
  withdrawal sells at the bottom, and that money misses the recovery (−30% already needs +43% to get back).
  **Two buckets:** money needed within 1-2 years (bills, the ~$20k evaluation budget, planned purchases) stays in cash or
  the low-volatility part (e.g. all-weather ETFs); only money not needed for years runs the strategies. Move money from
  the strategy bucket to the safe bucket as a goal gets closer, so a bad month never forces a sale.
- Judge in hundreds of trades / years, not months; know in advance the chance of a losing 12-month window.
- Rule of thumb (Radge): expect a max drawdown of about 1.7-2 x the annual volatility at some point (stock market 15-16% vol
  → 30%+ drawdowns; a 5% vol mix → 8-10%).
- Monte Carlo return / drawdown (Davey's favourite; median 1-year P&L / median 1-year max DD, `analysis/montecarlo.py`
  prints it): his MACD best case was below 1; our plan strategies 1.6-3.2 each, the funded plan ~7 (2023+).
- Monthly: place each month's result in the Monte Carlo range (the same check as the Apex review).
