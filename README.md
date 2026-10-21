# thebeginning: map of the repo

NQ / ES futures strategies (MultiCharts PowerLanguage) for Apex 50K / 150K prop accounts, plus the research behind them.
**Start here:** `NEW_CHAT_BRIEF.md` (latest state) and `CLAUDE.md` (working rules). Settings for every live chart:
`reports/Strategy_Settings.pdf` (the single place for inputs; rebuilt by `python3 reports/build_strategy_settings.py`).

## Where things are

| You want... | Look in |
|---|---|
| **The code to paste into MultiCharts** | `apex_strategies/` (evaluation set + Target Guard, Stop Guard, Trade Logger) and `funded_strategies/` (funded plan, incl. `NQ_Relative_Strength.txt`); `personal_strategies/` (not for Apex) |
| **What runs where, with which inputs** | `reports/Strategy_Settings.pdf`; plan detail `funded_strategies/FUNDED_PLAN.md`; roster `funded_strategies/README.md` |
| **Business plan / guides** | `reports/` (`Trading_Business_Plan.pdf`, `Performance_Report_Guide.pdf`, screenshots of Apex terms in `reports/screenshots/`) |
| **Your to-do list** | `TODO.md` |
| **Milestones: how it started and the progress so far** | `MILESTONES.md` |
| **Every idea tested and its grade (S-F)** | `TIER_LIST.md`; things to recheck: `WATCHLIST.md`; multiple-testing log `TRIALS.csv` |
| **Rules learned the hard way** | `LESSONS.md` (short rules), `MULTICHARTS_PITFALLS.md` (every MultiCharts / Rithmic / Apex error and its fix) |
| **How strategies are developed and promoted** | `DEVELOPMENT_PROCESS.md`; current goal `S_RANK_PROGRAM.md`; history `HANDOFF.md` |
| **MultiCharts backtest reports (.xlsx)** | `mc_reports/` (put new exports here) |
| **Live trading records** | `live/` (weekly MultiCharts reports; `live/trades/` = the VPS trade log, pushed daily 16:10 CT) |
| **Your journal** | `journal/daily/`, `journal/ideas/` (Obsidian; synced by `journal/sync.ps1`) |
| **Research code and results** | `analysis/` (Python; one `*_test.py` per idea) and `analysis/outputs/` (each script's printed results, `<script>_output.txt`) |
| **Independent checks of candidates** | `checks/candidates/<name>/` (spec, trades, checker verdict) |
| **Antigravity's tasks and brief** | `agents/tasks/` (`ANTIGRAVITY_BRIEF.md`, `plan_daily_pnl.csv`); its results in `agents/results/`; its own work on branch `antigravity/jesse` |
| **Price data** | `data/` (1-minute CSVs: NQ day + overnight, ES, YM, GC, CL, ZN, 6E, BTC; order flow OF_*, gamma GEX*, COT, VIX / VXN daily) |
| **Data exporters for MultiCharts / The Bridge** | `tools/exporters/` |
| **Research papers** | `papers/` |
| **Local Claude (Cowork) instructions** | `cowork/INSTRUCTIONS.md` |
| **Old / superseded material** | `archive/` (v3 VWAP system, old indicators, notebooks), `multi_strategy/` (2026-10 early research notes) |

## Conventions

- Times are Central (CT, exchange time) unless a file says otherwise. Costs: $7.25 per NQ + 1 tick per market / stop fill.
- Rebuild the cached data for research: `pip install numba`, then `python3 analysis/build_lab.py scratch_data` (git-ignored).
- The repo is private: raw links only work from GitHub's **Raw** button while logged in; on the PC use `git pull`.
