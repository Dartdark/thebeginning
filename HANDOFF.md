# Handoff: NQ strategies for Apex 50K (paste into a new chat)

I'm building NQ strategies in MultiCharts (PowerLanguage) to pass Apex 50K challenges
(EOD trailing: $3,000 target, $2,000 trailing drawdown that locks at start + $100, $1,000
daily loss limit, 21 trading days, $50 per account). Apex only; ignore Topstep.

**Repo:** github.com/Dartdark/thebeginning. Branches `claude/nq-trading-strategy-params-5h9d20`
(main working branch) and `claude/quirky-noether-4dla64` are identical; keep them in sync.
**Read first:** `apex_strategies/TWO_STRATEGY_PLAN.md`, `funded_strategies/FUNDED_PLAN.md`,
`multi_strategy/README.md`, this file.
**Please always give me direct GitHub links** (raw links for code I paste into MultiCharts).

## Folders (2026-10-11)
- `apex_strategies/`: **Apex strategies**, for passing the challenge only (Vault Break,
  Overnight Bias, their indicators, `TWO_STRATEGY_PLAN.md`). Not for making money.
- `funded_strategies/`: **funded strategies**, built to maximize PA payouts (roster,
  design rules, benchmark in `funded_strategies/README.md`; interim plan in
  `FUNDED_PLAN.md`). The Apex strategies are only the benchmark there.
- `multi_strategy/`: research history, other tested strategies, `RESEARCH_TOPICS.md`.

## Funded build status (2026-10-11)
Instruments are open: NQ, ES, GC, CL, anything with an edge. Test bench:
`analysis/funded_lab.py`; candidates `analysis/funded_candidates.py`; results in
`funded_strategies/README.md`. Five rounds of NQ/ES funded candidates (new exits, ES, NQ-ES spread, event days,
overnight-positioning family, quiet-day/unused-hours brackets) are all below the $5,387
benchmark (VB 3 + ONB $300 + OND $500); details in funded_strategies/README.md.
Next step needs 1-minute 24-hour exports of GC, CL, ES (NQ_Bar_Exporter, StartTime 0,
EndTime 2359, FilePrefix e.g. GC_1min_) into data/.

## Current plan (decided)
One Apex account at a time, running two strategies together, both on **MNQ**, each in
its **own chart window**, **CME 24-hour session**, Exchange time zone (CT), Bar Magnifier
on at 1 minute for backtests:

| Strategy | File | Chart | Live inputs |
|---|---|---|---|
| Vault Break (mine) | `apex_strategies/NQ_Vault_Break.txt` | 30 min | `NumContracts` 8 |
| Overnight Bias (mine) | `apex_strategies/NQ_Overnight_Bias.txt` | 15 min | `RiskPerTrade` 1100, `NumContracts` 1, `ExitTime` 1430, `EarlyExitTime` 1130 (= 3-4 MNQ at late-2026 prices) |

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
