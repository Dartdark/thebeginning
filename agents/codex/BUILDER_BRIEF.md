# Codex: strategy builder brief

Written by Claude, 2026-10-21. Read this whole page before any task.

## Your role

You build and test trading-strategy ideas for one trader running **MultiCharts (PowerLanguage) on Apex prop accounts**
(50K / 150K, NQ / MNQ futures, some ES / CL). **Claude** (another AI, in this repo) reviews and independently checks
everything you report before it reaches the trading plan. **The user** decides what trades.

Your output is evidence, not persuasion. A clean negative result is as useful as a positive one. Most ideas fail. A
report that makes noise look like an edge costs the user money and costs you trust.

## Read first

1. `README.md`: the repo map (data in `data/`, MultiCharts reports in `mc_reports/`, scripts in `analysis/`).
2. `NEW_CHAT_BRIEF.md`: the current plan, accounts and research state.
3. `DEVELOPMENT_PROCESS.md`: the testing process. It applies to you in full.
4. `TIER_LIST.md`: every idea already tested (S-F). Check it before starting anything; don't rediscover a ranked item.
5. `WATCHLIST.md`, `MULTICHARTS_PITFALLS.md` (before writing any PowerLanguage), `LESSONS.md`.
6. `CLAUDE.md`: written for Claude, but its testing standard is the standard for you too.

## Hard limits (Apex)

- Intraday only: **flat by 15:59 CT**, no overnight holds except the Sunday 17:00 CT reopen into Monday.
- **$2,000 end-of-day trailing drawdown** on 50K accounts. A strategy is judged by what it does to the account at the size
  it would trade, not by its profit per NQ.
- Contract maths: NQ $20 a point, **MNQ $2 a point = 1/10 NQ** (2 MNQ = 1/5 NQ), tick 0.25. ES $50, MES $5.

## Setup

```
pip install numpy pandas numba openpyxl scipy scikit-learn
python3 analysis/build_lab.py scratch_data      # builds the cached 1-minute grids (10-30 min); scratch_data/ is git-ignored
```

## Use the repo's tools; don't write your own versions

| Need | Use |
|---|---|
| 1-minute NQ grid, 24 h, Central time | `analysis/grid24.py` (`Grid24`, `bars(k)`, `vwap_rows`, `daily_atr`, `jof`) |
| Signals into trades (one position, stop / target / time exit) | `analysis/grid.execute` (costs $7.25 per NQ; a target needs a 1-point trade-through) |
| Slippage (1 tick per market / stop fill) | `analysis/param_clusters.trade_net(trades)` |
| Sharpe, Sortino, PF, Calmar, Ulcer, t bar, deflated Sharpe | `analysis/metrics.py` (`perf`, `t_threshold`, `deflated_sharpe`) |
| Bootstrap / permutation | `analysis/resampling.py` |
| Monte Carlo with the Apex trailing drawdown | `analysis/montecarlo.report` |
| Funded-account bench (the plan) | `analysis/funded_lab.py`, `analysis/funded_bootstrap.py` (plan decisions use the bootstrap) |
| Existing strategies to compare or combine with | `analysis/candidates24.py`, `analysis/portfolio.load_mc` (MultiCharts trade lists), `agents/tasks/plan_daily_pnl.csv` |
| Multiple testing | `analysis/trials.py` |

If a tool is missing something, extend it in a new file and say so. Every number in a report must come from a script
committed in the repo that reproduces it.

## How every idea is tested

0. **Evidence sheet first (adopted 2026-10-22).** Before any plan or backtest, write `agents/codex/evidence/<name>.md`
   answering, with sources:
   1. **Who trades, and what forces or causes the trade?** (a rule, a mandate, a hedge, a deadline; "investors react to
      news" is not enough)
   2. **Direction, size and timing: can we estimate them with information available BEFORE the trade?** Give an
      order-of-magnitude size in $ and compare it with NQ / ES volume in that window.
   3. **Does the order reach NQ / ES (or MNQ / MES / ES-QQQ hedges) directly?** A proxy price for an imbalance in another
      market is a weak link.
   4. **What data separates the idea from ordinary momentum / reversal?** (the flow estimate must vary independently of
      the price move, e.g. AUM, open interest, a calendar) Name the data, whether we have it, and its cost if not.
   5. **Can it beat costs in an actual gap?** Expected move vs $17.25 per NQ round trip; which hours of the plan's
      occupancy map (`analysis/outputs/codex_sge_delivery_screen/roster_*_occupancy.csv`) it uses.
   6. **Power: can the test ever pass?** Expected trade count in 2018-22, a plausible per-trade sd, and the net $ per
      trade needed for t >= 2. If that is unrealistic, stop here (or pool pre-registered related events).
   7. **Already tested?** TIER_LIST / WATCHLIST / `analysis/` hits and how this differs.
   End with a verdict: TEST / NEEDS DATA (what, cost) / DON'T TEST. Only TEST sheets go to step 1.
   Test the edge on ALL events; never select events by whether the plan holds a position (that conditions on the
   market). Handle overlap afterwards at account level.

1. **Plan first.** Commit `agents/codex/plans/<name>.md` BEFORE running anything. It must contain: the rule, the
   mechanism (who is forced to trade, and why that leaves money on the table), at most 5 variants, the decision rule
   (what result means adopt / reject), and which existing plan strategy it overlaps most.
2. **Design 2018-2022, holdout 2023 onward.** Choose on 2018-22 only. Run the chosen version(s) on 2023+ once. If you
   change anything after seeing 2023+, it is a new trial: say so. 2023+ has been looked at by ~275 ranked ideas, so it is
   no longer clean: anything that passes also goes into the **forward log** (`agents/codex/FORWARD_LOG.md`: rule frozen,
   date frozen, then paper results added at each Friday review) before it can trade.
3. **Standard report** for the whole strategy and **for longs and shorts separately**: trades, win rate, $ per NQ,
   t-stat, Sharpe, Sortino, profit factor, Calmar, Ulcer, max DD. Give the results by year and for 2018-22 vs 2023+, plus
   bootstrap intervals on 2023+.
4. **Placebos**: random entry time / random side with the same exits. For a **filter** (anything that removes trades):
   - judge on total $, not $ per trade (removing break-even trades raises the per-trade average by itself);
   - show the removed trades' average and t (they must lose money);
   - drop the same number of trades at random 1,000+ times: the filter must beat most random drops on drawdown and
     profit;
   - compare with the unfiltered base on the SAME years, the holdout above all.
5. **Account level**: Monte Carlo at the size it would trade (P of hitting the $2,000 trail in a year) and the funded
   bench. Test it **as an addition and as a replacement** for the plan strategy it overlaps most.
6. **Count trials.** List every variant you ran, failures included. The bar for promotion above C is
   t >= `metrics.t_threshold(N_items)` (about 3.6 now) or deflated Sharpe >= 0.95, unless pre-registered with <= 3
   variants and a clean placebo.
7. **MultiCharts code** only after the idea passes. It must implement exactly the rule you tested (same ATR, same
   anchors, same bar timing, exits active on the entry bar, early-close days, flat by 15:59 CT). Read
   `MULTICHARTS_PITFALLS.md` first. List every difference between the code and the Python test in the report.

## Report format (`agents/codex/results/<name>.md`)

```
# <name>: <one-line verdict: REJECT / WATCH / CANDIDATE>
Summary: <5 lines max: the question, the answer, the 2-3 numbers that decide it, what the user should do>
Plan: <path, commit>   Script: <path>   Output: <path>   Trials run: <n>
## Rule (as tested)
## Results (tables: whole / longs / shorts; 2018-22 / 2023+ / by year; vs base or plan)
## Placebos and account level
## What could make this wrong (data, fills, look-ahead, multiple testing)
## Differences between the MultiCharts code and the test (if code was written)
```

Write plainly. Don't use "breakthrough", "massive", "institutional", "law", "proves", "deployed" or "champion". Don't
explain a result with a market story unless the plan predicted it before the test. Never round a weak result into a
strong word.

## Git and boundaries

- Work on branch **`codex/work`**. Pull before every push. Never push to `claude/*` or `antigravity/*`.
- Write only under `agents/codex/`, `analysis/codex_*.py` and `analysis/outputs/codex_*`. Don't edit `TIER_LIST.md`,
  `TODO.md`, the plan or any live strategy file: Claude ranks and merges after checking.
- **Never** touch live trading, the VPS, broker / Rithmic / Apex settings, or API keys.
- When a task is done: commit, push, and say in one line what to tell Claude (the result file's path).

## What a good task looks like

Ideas that have worked here are **forced or scheduled flows**: expiration opens, leveraged-ETF / vol-control
rebalancing, payroll reactions, Monday and Sunday-reopen flows. Price-pattern ideas (breakouts, indicators,
mean reversion) have mostly failed. Aim at the plan's gaps: `agents/tasks/plan_daily_pnl.csv` shows which days and
hours the plan is already exposed. Low correlation with the plan matters more than a high Sharpe.
