# Handoff: NQ strategies for Apex 50K (paste into a new chat)

I'm building NQ strategies in MultiCharts (PowerLanguage) to pass Apex 50K challenges
(EOD trailing: $3,000 target, $2,000 trailing drawdown that locks at start + $100, $1,000
daily loss limit, 21 trading days, $50 per account). Apex only; ignore Topstep.

**Repo:** github.com/Dartdark/thebeginning. Branches `claude/nq-trading-strategy-params-5h9d20`
(main working branch) and `claude/quirky-noether-4dla64` are identical; keep them in sync.
**Read first:** `apex_strategies/TWO_STRATEGY_PLAN.md`, `funded_strategies/FUNDED_PLAN.md`,
`multi_strategy/README.md`, this file.
**Please always give me direct GitHub links** (raw links for code I paste into MultiCharts).

Tier list of everything tested (S–F): `TIER_LIST.md`. Development process (whole strategy first, then longs and shorts separately): `DEVELOPMENT_PROCESS.md`; project rules: `CLAUDE.md`.

## Folders (2026-10-11)
- `apex_strategies/`: **Apex strategies**, for passing the challenge only (Vault Break,
  Overnight Bias, their indicators, `TWO_STRATEGY_PLAN.md`). Not for making money.
- `funded_strategies/`: **funded strategies**, built to maximize PA payouts (roster,
  design rules, benchmark in `funded_strategies/README.md`; interim plan in
  `FUNDED_PLAN.md`). The Apex strategies are only the benchmark there.
- `multi_strategy/`: research history, other tested strategies, `RESEARCH_TOPICS.md`.

## Starting a new chat (2026-10-12)
1. Read `CLAUDE.md` (rules), this file, `funded_strategies/FUNDED_PLAN.md`, `TIER_LIST.md`,
   `DEVELOPMENT_PROCESS.md`.
2. Rebuild the cached data (not in git, ~2 GB): `pip install numba` first (without it the
   funded simulator falls back to pure Python and the score step takes 30+ minutes), then
   `python3 analysis/build_lab.py scratch_data` (about 1 minute). It writes `g24.pkl` (NQ grid), `ge.pkl` (ES grid) and `lab.pkl` (funded lab
   with VB, ONB_ML2_MC, EOS, MON_MC, LDF_MC, OND_MC from the MultiCharts reports) and prints the
   current plan's score, which should be $7,676 (1 year) / $12,012 (2 years).
3. Older test scripts load pickles from the first session's scratchpad path (`SP = ...`); point
   `SP` at `scratch_data/` to rerun them. Standard tools: `analysis/metrics.py` (Sharpe, Sortino,
   PF, Calmar, Ulcer), `analysis/resampling.py` (bootstrap, permutation, fan charts),
   `analysis/param_clusters.py` + `analysis/robustness.py` (clusters, folds, sensitivity),
   `funded_lab.Lab.score(plan, 250/500, fmin=0.5, fmax=1.0, ref=2000)` (funded bench with cushion sizing).
4. To confirm a strategy: the user uploads the MultiCharts report (.xlsx) to the repo root;
   compare with `portfolio.load_mc` as in `analysis/late_day_flow_confirm.py`.

## Funded plan (updated 2026-10-13, latest)
**Vol-Control Sell dropped (late 2026-10-13):** without it $9,313 / $12,569, blown 2% / 1%, median 255 days (adds
nothing next to the Bridge Monday Long; needs @ES data2). Combine add-ons are now Bridge Monday Long 2 MNQ + EOS $500
(pass 50.1%).
Before that: eight strategies: the seven below + **the Bridge's Monday Long NQ 1 MNQ** (Sunday 19:00 CT → Monday 15:55,
daily ADX(7) filter, 100-pt target; ships with The Bridge; MC-confirmed 217/217 trades,
`analysis/bridge_monday_confirm.py`). $9,313 (1y) / $12,436 (2y), blown 1-3%, median 255 trading days to all 6
payouts (was 278), 48% get all 6 within a year (was 36%).

## Funded plan (updated 2026-10-13, 7 strategies)
Seven strategies, full size from a $1,500 cushion (f = cushion/$1,500 in 0.5-1): VB 3 MNQ, ONB ML v2
RiskPerTrade 400, Monday Long 1 MNQ, EOS RiskPerTrade 700, Late-Day Flow 2 MNQ, **NFP Fade RiskPerTrade
500, Vol-Control Sell Flow 1 MNQ** (both MultiCharts-confirmed 2026-10-13; VCS needs 5-min @ES as data2).
Expected payouts $8,770 (1y) / $12,236 (2y), blown 2-3%, median 278 trading days to all 6 payouts
(was 306); portfolio Sharpe 2.61. `python3 analysis/build_lab.py scratch_data` prints both plans
(install numba first).

## Funded plan (2026-10-12, previous)
Current funded set (`funded_strategies/FUNDED_PLAN.md`): VB 3 MNQ, Overnight Bias ML v2 RiskPerTrade 400,
Monday Long 1 MNQ (replaced Overnight Drift), Expiration Open Short RiskPerTrade 700, **Late-Day Flow
2 MNQ** (added), with cushion sizing (f = cushion/$2,000 in 0.5-1). Expected payouts $7,676 (1y) /
$12,012 (2y), blown 4-6%; portfolio Sharpe 2.51.

## Combine: Overnight Bias ADX30 confirmed (2026-10-13)
MultiCharts report `Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx`
(ADXMin 30, StopAtrPct 0.25): 676 trades, PF 1.66, 675/676 match Python. Combine pass with VB 8 MNQ
46.9% (was 42.8%); switch the live combine chart to these inputs. `analysis/onb_adx30_confirm.py`.
Add-ons (`analysis/combine_addons_test.py`): + Bridge Monday Long 2 MNQ + EOS $500 + Vol-Control Sell 2 MNQ ->
pass 50.5% (2023-26 55.4%), blown 47.8% vs 50.0%; our Monday Long and NFP Fade don't help the combine.
Funded re-check (`analysis/funded_today_check.py`): nothing else worth adding. DriftPullback shorts 1 MNQ is within noise
(median 245 vs 255 days, +$140 / +$56, blown 4% vs 3%) and weak since 2023: watch item, not a plan candidate.
Open-breakout pullback (user's idea, `analysis/open_pullback_test.py`): longs t 1.6 at best, shorts lose; funded worse (D).
On 15-min bars (`analysis/open_pullback_15m_test.py`): longs 0.15% 3R t 2.4, controls clean, but best of 120; funded
neutral at 1 MNQ, combine worse (C, watch). On 1-min bars (`analysis/open_pullback_1m_test.py`): fails (F).
Time clusters in the plans' trades (`analysis/time_clusters_test.py`): nothing to change; current exits best; VB September
weak (7/9 years) is a watch item, not a filter.
YM (`data/YM_1min_2017..2026.csv`, `analysis/ym_test.py`): correlation with NQ 0.80, but none of the plan's strategies
work on YM (t <= 1.3, 2018-2026): don't add it. NQ-YM spread (`analysis/nq_ym_spread_test.py`): divergences trend
intraday but two legs of costs eat it; the NQ leg is NQ's own opening momentum (D). CL / GC: user's feed stops at Oct 4 (NYMEX / COMEX entitlement); export pending.
101 Formulaic Alphas (SSRN 2701346, `analysis/alpha101_test.py`): cross-sectional stock alphas ported to NQ / ES time series;
design winners fail in 2023-26 (below random), the 101-alpha vote loses in the holdout (F).
Beta from A to Z (textbook, `analysis/beta_pairs_test.py`): Kalman / cointegration pairs on NQ-ES and NQ-YM: not cointegrated,
no short-run over-reaction, spreads keep diverging from extremes (F). NQ-on-ES hedge ratio ~1.2 at every horizon.
Fast-alpha execution overlay (Concretum 2026, `analysis/fast_alpha_test.py`): waiting for a 5-min counter bar costs every plan
strategy except NFP (VB -$32, LDF -$69, EOS -$250 a trade), same as random delays: keep market entries (F).
Market Intraday Momentum (Gao et al., SSRN 2440866, `analysis/gao_intraday_momentum_test.py`): first half-hour -> last half-hour
is gone on NQ / ES 2018-26 (out-of-sample R2 < 0, timing -$28 a trade); LDF's 14:30 exit confirmed (F).
Gamma x intraday momentum (`analysis/gamma_momentum_test.py`): no momentum into the close below the 0DTE flip (F), but LDF earns
$158 below the flip vs $36 above (both halves, p 0.09): watch item for sizing LDF by the flip (C); on the funded bench (2023+ starts, `analysis/ldf_gamma_sizing_check.py`)
3 MNQ below / 1 above: $10,924 vs $10,489 a year, blown 3% vs 7% (in-sample). Tracked in `WATCHLIST.md` with the other watch items.
Volatility targeting (SSRN 3175538, `analysis/vol_target_test.py`): our edges grow with vol, every vol-scaled plan is worse (F).
Abnormal volume (Bajo, SSRN 675587, `analysis/abnormal_volume_test.py`): no next-day continuation on NQ; spikes are sell-offs (F).
Gold Asian-range breakout (user's file, `analysis/asian_breakout_test.py`): NQ $-3 a trade, ES $-42, best of 36 = the ONB-like
overnight breakout, funded worse (F). Its code re-enters after stop-outs (not one a day as described).
GC 2017-11 -> 2026-10 now in `data/GC_1min_*.csv` (converted ET -> CT). On gold itself the breakout is real but thin
(`analysis/gold_asian_breakout_gc_test.py`: Sharpe 0.66, uncorrelated, +0.045 R t 1.4); funded bench worse (C, watchlist #6).
CL 2017-11 -> 2026-10 in `data/CL_1min_*.csv` (converted ET -> CT). Forced flows (`analysis/cl_forced_flows_test.py`): EIA, settlement,
expiry, weekday all F; front-running the index roll (short BD 1-4) t 1.4 (D). CL-NQ corr 0.16, GC-NQ 0.12: diversifiers if an edge turns up.
Gold breakout filter (`analysis/gold_breakout_filter_test.py`): cancel at 02:00 CT -> +0.078 R t 2.0, holds 2023-26; funded still
below the plan (C, watchlist #6). Plan strategies on CL / GC (`analysis/commodity_plan_port_test.py`): none carries over (F).
Gold breakout exits (`analysis/gold_breakout_exit_test.py`): hold to 12:00 CT best (+0.091 R t 2.2); tighter stops / breakeven / targets worse;
funded about neutral; combine (`analysis/combine_gold_test.py`) no gain (pass 49.4-50.2% vs 50.1%).

## Account pipeline (2026-10-14): how many accounts
`analysis/account_pipeline_test.py`: N slots each cycling challenge -> funded -> 6 payouts or blown -> next challenge,
on real history. With the backtest edge, about $800 a month per slot, nearly linear (3 slots: about $30k in year one,
$13k net after about 8 months). At 75% / 50% of the edge it's still positive over 3 years, but year one can be
negative. Plan: start 3 slots, scale to 5-10 once live results are >= ~75% of the backtest per trade (`analysis/live_vs_backtest.py`).
Apex allows trade copying (user, 2026-10-14): one master per phase; reduce a follower's multiplier if its cushion falls well below the master's. User starting 3 slots together on 2026-10-14. Details: `funded_strategies/FUNDED_PLAN.md` (last section).
Pipeline tuning (`analysis/pipeline_tuning_test.py`): combine sizing barely matters (keep current); funded full size from a $1,000
cushion (instead of $1,500) adds ~7% net per slot at the edge and at 75% of it; scale 1.25 only after the live edge ratio is >= 0.9.
Live tracking: export live reports to `live/<KEY>_live.xlsx`, run `python3 analysis/live_vs_backtest.py --all live/` (see `live/README.md`).
Cross-asset overnight (gold / oil / bitcoin) filters: 0 of 25 pass (`analysis/cross_asset_overnight_test.py`); ONB-after-gold-up on the watchlist (#7).
Cross-asset map (`analysis/cross_asset_map_test.py`): correlations rise on FOMC / high-VIX days; no lead-lag; decoupling not tradeable.
Zoom-in (`analysis/release_reaction_fade_test.py`): data-reaction fade is mostly NFP; NFP held to 12:00 earns 2.4x per trade but blows
more funded accounts -> keep 9:00 (watchlist #8).
Covered-call ETF rolls (`analysis/option_income_etf_test.py`, `analysis/opex_morning_short_test.py`): no selling in the BXN 10:30-11:00 window,
no pin, no damped vol (F); the roll-morning drop (8:30-10:30 -$487) is EOS already in the plan (now with a mechanism: dealer pre-hedging).
Friday after the roll long 2023+ only (watchlist #9).

## Apex rules confirmed (2026-10-13)
The user confirmed the PA rules assumed in `analysis/funded_sim.py` (trailing drawdown and lock, daily
loss limit, contract tiers, payout rules). Each challenge account costs $50.

## Speed to $13k (2026-10-13)
New priority: reach all 6 payouts sooner. Current plan: median 306 trading days. Full size from a
$1,500 cushion (f = cushion/$1,500, 0.5-1): 289. Adding NFP Fade ($500) + Vol-Control Sell Flow (1 MNQ,
MultiCharts code written, `funded_strategies/NQ_NFP_Fade.txt`, `NQ_Vol_Control_Sell.txt`, awaiting
backtests): 278. Biggest lever: 2-3 PAs in parallel ($13k in total after ~225 / ~200 days).
Details: `funded_strategies/FUNDED_PLAN.md` (speed section).

## The Bridge 0DTE gamma data tested (2026-10-13)
User has The Bridge (MatFin MultiCharts add-on). `GEX_1min_<year>.csv` (repo root, 2022-09 to 2026-07-07,
exported by `multi_strategy/OFB_Gamma_Exporter.txt` on a 1-min chart of `C:\OFB\ofb_bars_NQ.csv`, Exchange
time zone = Eastern) tested in `analysis/gamma_regime_test.py`: below the flip NQ moves ~30% more, but
realized vol explains it; no filter on the plan clears noise (watch VCS above-flip, t 2.5 on 27 trades);
flip cross, regime follow / fade, strike pin all F. Order flow (MBO 2018-2026, `OF_1min_*.csv`, exporter
`multi_strategy/OFB_OrderFlow_Exporter.txt`, test `analysis/orderflow_test.py`): describes moves, doesn't predict
them (F); LDF-long delta filter D (no funded gain). Export quirk: MC `Volume` = buy volume on these bars.
The Bridge's Monday Long NQ (`analysis/bridge_monday_long_test.py`, its v2.1 code ported): PF 2.04, t 4.4, 9/9 years;
MC-confirmed (217/217 trades match): A, in the funded plan at 1 MNQ.
DriftPullback v2.1 (`analysis/drift_pullback_test.py`): real edge (t 4.0, 9/9 years, placebo −$16) but funded
worse (+1 MNQ blown 13%): B, not adopted. MC code for shorts only: `funded_strategies/NQ_Drift_Pullback_Shorts.txt`
(needs 15-min data2; user dropped the MC run).
VaultBreak v8 (the Bridge's, `analysis/vault_break_v8_test.py`): slightly worse than our v1 (band from H-L incl.
Sunday sessions); VWAP exit never fires; keep v1 (C).
VWAP Pullback + ADX (C.S. profile, `analysis/vwap_pullback_adx_test.py`): t 2.2, 6/9 years, only since 2021, gate ≈ random;
funded worse (D).
The Bridge's Overnight Bias ORB (`analysis/bridge_onb_orb_test.py`): $313, PF 1.52 vs our ADX30 $372 / PF 1.66;
combine 38.9% vs 46.9%; keep ours (B).
The Bridge's VWAP Fade (`analysis/bridge_vwap_fade_test.py`): −$25 a trade, PF 0.93, worse than random (F).
The Bridge's Large Trade Predictability (`analysis/bridge_large_trade_test.py`): 1-min gross edge $2-8 a trade < $17 costs (F).
Donchian + LWTI (`analysis/donchian_lwti_test.py`): t 1.8, worked 2018-22, negative since 2023 (D).
The Bridge's Liquidity Predictability (`analysis/bridge_liquidity_test.py`): book imbalance doesn't predict the next bar (F).
The Bridge's COT Dealer Rank (`analysis/bridge_cot_test.py`, `COT_NQ.csv`): weekly hold C (32 longs carry it, not
Apex-legal); Apex daily / filter versions F.
Setup notes: restart MultiCharts after any DLL / data change ("OLD DLL" error); compile every OFB function
("unverified function" error); Map ASCII with Exchange CME, time zone Exchange, start row 2, bar-close
conversion unchecked.

## Funded build status (2026-10-11)
Instruments are open: NQ, ES, GC, CL, anything with an edge. Test bench:
`analysis/funded_lab.py`; candidates `analysis/funded_candidates.py`; results in
`funded_strategies/README.md`. Five rounds of NQ/ES funded candidates (new exits, ES, NQ-ES spread, event days,
overnight-positioning family, quiet-day/unused-hours brackets) are all below the $5,387
benchmark (VB 3 + ONB $300 + OND $500); details in funded_strategies/README.md.
Calendar round found the first one that helps: **Expiration Open Short**
(`funded_strategies/NQ_Expiration_Open_Short.txt`): short NQ 8:30-10:00 CT on monthly options
expiration day, stop 0.3 ATR, RiskPerTrade 500 -> funded estimate $6,516 vs $5,387.
MultiCharts-confirmed (`Backtesting Strategy Performance Report EOS v1.xlsx`, identical 105 trades).
Overnight Drift MultiCharts-confirmed (`... OND v1.xlsx`); holiday fix (`MaxEntryDelay` 30).
Funded set: VB 3 MNQ, ONB $300, OND $500, Expiration Open Short $500 -> $6,495 within 1 year
(all MultiCharts lists, 1 tick slippage), 42% blown. Next: sim-trade all four together.
Overnight Bias ML replaced ONB in the funded set (2026-10-12): `funded_strategies/NQ_Overnight_Bias_ML.txt`,
ONB plus a frozen ridge "skip today" filter (Kelly & Xiu ML survey, `analysis/ml_filter_test.py`).
MultiCharts-confirmed (decisions match Python from April 2018). Funded set now: VB 3 MNQ, ONB ML $300,
OND $500, EOS $500 -> $6,928 within 1 year, $8,379 within 2 years, 34% blown (MC lists).
Next step needs 1-minute 24-hour exports of GC, CL, ES (NQ_Bar_Exporter, StartTime 0,
EndTime 2359, FilePrefix e.g. GC_1min_) into data/.

## Current plan (decided)
One Apex account at a time, running two strategies together, both on **MNQ**, each in
its **own chart window**, **CME 24-hour session**, Exchange time zone (CT), Bar Magnifier
on at 1 minute for backtests:

| Strategy | File | Chart | Live inputs |
|---|---|---|---|
| Vault Break (mine) | `apex_strategies/NQ_Vault_Break.txt` | 30 min | `NumContracts` 8 |
| Overnight Bias ADX30 (mine, since 2026-10-13) | `apex_strategies/NQ_Overnight_Bias_ADX30.txt` | 15 min | `RiskPerTrade` 1100, `NumContracts` 1, `ADXMin` 30, `StopAtrPct` 0.25, `ExitTime` 1430, `EarlyExitTime` 1130 (= 4-5 MNQ at late-2026 prices) |

Results (backtests 2018-2026 from my MultiCharts reports, real-day Apex simulation):
combined account passes **44%** (2018-22 43%, 2023-26 45%, worst start year 29%);
typical 12 trading days and about $117 (2.3 accounts) to the first funded account.
Vault Break alone 41%, Overnight Bias alone 37% (no-edge versions 31% / 26%).
Daily P&L correlation between them 0.25 (both trade the same day only 21% of days).

**Vault Break:** longs only; noise level = midnight open + 0.30 x 15-day ATR (weekday
calendar-date true ranges incl. overnight); VWAP from midnight; at 30-min closes
10:00-14:00 CT, close > noise and > VWAP -> buy next bar; TP 40 pts, SL 75 pts, max 3
trades/day, flat 14:30 (holiday half-days: last entry 11:00, flat 11:30). MC report:
1,743 trades, 66% win, $99/trade per NQ after $7.25 costs, PF 1.28, every year positive.

**Overnight Bias:** 8:30 open in top third of the 23:00-8:30 overnight range -> longs
only, bottom third -> shorts only, middle -> no trade; opening range = 8:30-8:45 bar;
from 8:45 to 14:00 while ADX(14) on 15-min > 20, stop order at OR high (long) / low
(short); stop = 0.30 x 15-day ATR, target 3x stop, flat 14:30; 1 trade/day. MC report:
997 trades, 49% win, $278/trade, PF 1.39, every year positive. Monte Carlo: 95% range
$147-$416/trade, PF 1.19-1.63. Must be sized by RiskPerTrade (stop is $700/NQ in 2018,
$2,850/NQ in 2026). **Backtest on @NQ with RiskPerTrade 0 and NumContracts 1**;
RiskPerTrade 1100 only on an MNQ chart (on NQ it buys 0 contracts most days).

## Other strategies (not in the plan)
- v3 VWAP Momentum (`final_v3/`): PF 1.14, 33% pass (41% if started after the 10-day
  range filter is green 3+ days), worst year 5%. Retired from the challenge plan.
  Note: `final_v3/README.md` says one stop-out at 10 MNQ is ~$800; it is $1,600.
- Opening Drive (`multi_strategy/NQ_Opening_Drive.txt`, made by Claude): at 9:00 CT follow
  the first 30 minutes' direction if the move is at least 0.2%, stop 50 pts, out 11:00. PF 1.23,
  33% pass, most independent of the others. Optional add-on (VB 6 + OD 4 + ONB $1,100 = 43%).
- Rejected: VWAP Pullback ADX (my spec, PF 0.87), Gap Fill (weak since 2023), late-day
  momentum (fragile), VWAP fade, opening-range breakout, lunchtime RSI(2), prior-day
  levels, Vault Break short side, Vault Break 1-2 trades/day cap, daily profit-lock/stop rules.
- Volatility-scaled sizing (Moreira-Muir 1/variance, Harvey et al. 1/vol): did not improve
  the plan. Overnight Bias already is inverse-vol sized; 1/vol lowers Vault Break's Sharpe.

## Findings that shape the approach
- Apex geometry caps the pass rate: even no-edge versions pass ~26-31%. Gains come
  from consistency and speed, not huge pass-rate jumps.
- Separate accounts started together pass almost independently (pass/fail correlation
  0.02-0.24); one combined account at a time was the cheapest route to funded.
- I do not want strategies that need specific market regimes; new strategies should
  be built independently (not from v3) and have low correlation with the others.
- If adding anything later: an overnight-session strategy (Asia/London hours) would be
  the most independent; all current strategies trade 8:30-15:55 CT.

## Data and code
- 1-min NQ bars: `NQ_1min_<year>.csv` (08:00-15:15 CT) + `NQ_1min_ON_<year>.csv`
  (15:16-07:59 CT), Dec 2017 - 9 Oct 2026, exported by `NQ_Bar_Exporter.txt`.
- Python (in `analysis/`): `grid24.py` (24-hour grid), `grid.py` (execution engine,
  reproduces MC fills), `portfolio.py` (real-day Apex simulator, `load_mc` reads any MC
  "List of Trades" report, bar size from Settings sheet), `multi_strategy24.py` (main
  tables, ~1 min), `monte_carlo_onb.py`, `vol_scaling.py`, `candidates24.py`,
  `candidates.py`, `start_timing.py`, `prop_sim.py`, `replica.py`.
- MC reports in repo root: `Backtesting Strategy Performance Report VB v1.xlsx`,
  `... OD v1.xlsx`, `... ONB v2.xlsx`, v3: `... v2 filtered up test.xlsx`.
- Indicators: `apex_strategies/NQ_Strategy_ATR.txt` (ATR, 30% ATR, ONB MNQ size),
  `apex_strategies/NQ_ONB_ADX.txt`. Not yet compiled by me; may need fixes.
- Colab notebook `TheInstitutionalProtocol_PropSimulations_ChartAcademy.ipynb` (course):
  assumes 1 NQ per trade, adds $2.25 + $5 costs; Cells 21b/21c fixed to run with one
  strategy. It cannot model RiskPerTrade sizing, so it understates Overnight Bias.

## MultiCharts gotchas seen so far
- Replacing code in an existing signal keeps old input values with the same name
  (an old ExitTime 1100 broke one backtest). Check the report's Settings sheet: name,
  inputs, Compression, Bar Magnifier, commission/slippage 0, fill limit +1 point.
- A signal runs on data1 only; each strategy needs its own chart window.
- Auto trading: Paper Trader (dxFeed) first. Each chart: Format Signals > Properties >
  Auto Trading tab (broker plug-in, account); mode dropdown at the chart's top-left
  (set **AA**); click the AA box to switch on; initial position Flat; no automatic
  position sync (two strategies share one account). Intra-bar order generation off
  (Format Signals > select signal > Format... > Properties).
- Order and Position Tracker: View > Show Order and Position Tracker Window (Ctrl+Shift+O).

## Funded phase (2026-10-11, `funded_strategies/FUNDED_PLAN.md`)
Goal once funded: maximize payouts (50K PA: max 6 payouts, caps 1,500/1,500/2,000/
2,500/2,500/3,000 = $13,000; 5 days of $250+, 50% consistency, safety net $52,100).
- Challenge sizes in a PA expect only ~$2,700 within a year (75% blown).
- Recommended funded sizes ("Balanced"): VB 3 MNQ, ONB RiskPerTrade 300, new
  **Overnight Drift** (`funded_strategies/NQ_Overnight_Drift.txt`, long midnight-3:00 CT
  after a down session, stop 30% ATR) RiskPerTrade 500: ~$5,900 within 1 year,
  ~$6,800 within 2. Slower plans (VB 1-2) reach $8,000-9,700 within 2 years.
- Take each payout as soon as the full cap is allowed.
- Overnight Drift is Python-only so far (PF 1.25, 8 of 9 years positive, flat 2023-24,
  correlation ~0 with the rest); needs a MultiCharts backtest (`... OND v1.xlsx`).
- Code: `analysis/funded_sim.py` (PA simulator, rules/assumptions at the top),
  `analysis/funded24.py` (all funded tables, ~1 min).

## Research direction (2026-10-11)
I prefer intraday strategies with more trades a day and published research behind them.
Reading list and test plan: `multi_strategy/RESEARCH_TOPICS.md`.
Guide to practitioner sources (market makers, bank desks, options traders, fund quants):
`multi_strategy/PRACTITIONER_SOURCES.md`.
Tested (`analysis/intraday_research.py`): VWAP trend (no edge after costs), big-move
reversal (loses), round numbers (loses), full noise-area version (PF 1.26, real edge,
but not better than VB in the funded plan; long-only 1 MNQ in place of 1 VB is about equal).

## VIX regime test (2026-10-11, `apex_strategies/VIX_REGIME.md`)
"The Volatility Edge" regimes (eVRP and backwardation; stand-ins for VIX3M/SPY):
Vault Break and Overnight Bias earn ~30% more per trade in the calm "short vol" regime
and least in "cash"/"half short"; Overnight Drift/Opening Drive lean the other way.
Sizing VB by regime changes challenge/funded results only within noise; kept as
`apex_strategies/NQ_Vault_Break_VIX.txt` (data2 = daily VIX) for later. With real S&P vol
(`data/SPY_daily.csv`, @ES export): VB weakest on "cash" days ($39/trade); skipping them
= 45.3% pass vs 43.8%. My MultiCharts feed has no VIX, so it is parked.

## Intraday research results (2026-10-11, end of `multi_strategy/RESEARCH_TOPICS.md`)
- "Beat the Market" full version (trailing exit, long+short): higher avg/trade but 43% wins;
  worse in the funded sim ($4,100 vs $5,387 Balanced, both with 1 tick slippage) and the
  challenge (35% vs 43%). Win rate and smooth days matter more than PF under Apex rules.
- Fading large intraday moves: loses in every variant (NQ intraday = momentum).
- Round numbers: price passes through 100/50 levels slightly more than other levels; too
  small to trade.
- With 1 tick slippage on everything, Balanced funded estimate is ~$5,400 (not $5,900).
- Code: `analysis/intraday_research.py` (~1 min).

## Where I am / next steps
1. Both charts are set up on MNQ; turning on auto trading on Paper Trader.
2. Run 1-2 weeks on sim; log each trade (time, side, size, price) and compare with the
   backtest; check the two charts don't interfere (account position = sum of both).
3. Then start Apex accounts one at a time; stop and review after 3 failures in a row.
4. Funded phase planned (see above). Next: MultiCharts backtest of Overnight Drift,
   check the assumed PA rules on Apex's help center, sim-trade Overnight Drift.
