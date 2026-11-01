# Runbooks (moved out of CLAUDE.md 2026-11-01, unchanged in substance)

## Live dashboard 'Apex Live Desk' (2026-10-28)
https://claude.ai/artifact/3oqbHWqBFTrUQd95wMmuL8 (accounts, trades, live guard, VPS health, live-vs-backtest range, edge per
strategy, missed-trade alarm, strategy lab). Refresh after each close: `python3 analysis/dashboard_data.py` (also runs
`analysis/live_panels.py`, `analysis/account_tools.py` and `analysis/lab_tools.py`; account rules in `account_tools.EVALS`),
upload every JSON in `analysis/outputs/dashboard/` except `bt_cache.json` and `lab.json` as an asset and update the dataset
with the same id (url / name / updated).
- New Apex balance from the user -> `ACCOUNTS` in dashboard_data.py.
- New account -> `ACCTS` in live_panels.py and `live/expected_setup.json` (charts + account rules for the floor alarm).
- Funded account -> `FUNDED` in account_tools.py (payouts).
- After a backtest report changes, rebuild scratch_data and rerun live_panels.py to refresh `bt_cache.json`.

## Journal (Obsidian, 2026-10-17)
`journal/daily/` and `journal/ideas/` are the user's notes, pushed to the work branch by `journal/sync.ps1` (with `live/`
reports). On "read my journal": `git pull` the work branch, read the new notes, compare with the backtest trades of those
days, act on problems (fix / `MULTICHARTS_PITFALLS.md` / `TODO.md`), test ideas and set their `Status:` line. Since
2026-10-19 Claude (Cowork on the user's PC) writes the daily notes from the user's answers; keep the user's own words, never
invent fills or numbers. Trades come from the VPS trade log (`apex_strategies/Apex_Trade_Logger.txt` ->
`live/trades/YYYYMMDD.csv`); `analysis/journal_trades.py` writes them into the note (weekday task 16:40 CT).

## Morning brief (user 2026-11-01)
Scheduled task 'Morning brief' (`trig_01D4QcEmooHTMpSJQPCqSroR`) wakes the master session daily at 07:47 CT:
`python3 analysis/morning_brief.py 24 --send` (headline to ntfy) and the full brief (max 15 lines) as the reply. Pure code:
lab ledger + queue, scout log, new lab ideas, Code reviewer and Codex commits, what is waiting on the user, open 'You' to-dos.
First line "CHAIN BROKEN" when the lab ran no study (and is not stopped, with ideas queued) or the scout logged nothing in the window.

## Buy gate (2026-11-01)
`python3 analysis/buy_gate.py` before buying any evaluation: PAUSE (drift alarm, account below its backtest range, or 2
accounts failed within ~10 trading days -> 7-day cool-off), PLAN ONLY (< 40 live trades: buy per the budget plan, don't
accelerate), GO (40+ trades, live edge >= 75% of backtest). Shown in the morning brief. The user decides; the gate advises.

## VPS status (2026-11-01)
`python3 analysis/vps_status.py <scratch>/vps` -> status + trade tail (no screenshot: Defender blocks it). Setup: `live/vps/VPS_STATUS.md`.
