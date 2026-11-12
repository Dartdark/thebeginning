# Project notes for Claude

NQ/ES (and other CME futures) strategies in MultiCharts PowerLanguage for Apex prop accounts (evaluations and funded; 150K
No-Activation since 2026-10-30) and a later personal account.

**Map (read in this order):** `NEW_CHAT_BRIEF.md` (latest state) · `TODO.md` (user's to-dos; tick what they say is done) ·
`TIER_LIST.md` (every tested item, S-F) · `funded_strategies/README.md`, `funded_strategies/FUNDED_PLAN.md`,
`personal_strategies/PORTFOLIO.md` (plans) · `WATCHLIST.md` · `LESSONS.md` · `MULTICHARTS_PITFALLS.md` (read before writing
MultiCharts code; add every solved error) · `DEVELOPMENT_PROCESS.md` · `RUNBOOKS.md` · `FRIDAY_REVIEW.md` · `README.md`.

## Rules

- **Apex only.** Flat by 15:59 CT; EOD trailing drawdown ($2,000 on 50K, $4,000 on 150K; intraday touch fails).
- **Every reply ends with one PushNotification** (< 200 chars, the headline; ToolSearch `select:PushNotification` if deferred),
  sent before the reply text, which is written once. Scheduled-check alarms: `python3 analysis/send_alert.py "text"`.
- **Branches:** work on `claude/nq-trading-strategy-params-5h9d20`; keep `claude/quirky-noether-4dla64` and the designated
  branch identical; pull first. `python3 tools/prepush_check.py <designated>` before every push (no pipe on it) and
  `--after <designated>` after. No model IDs in commits.
- **Receipts:** name what was verified (run), what was not, and the risks. Never state a result that wasn't run.
- **Links and code:** direct GitHub links (repo private). One line per changed file; paste code only on request.
- **Testing standard:** costs $7.25/NQ ($5/ES) + 1 tick per market/stop fill; 2018-2026 by year and 2023+; placebo /
  walk-forward where relevant; Sharpe, Sortino, PF, Calmar, Ulcer (`metrics.py`), longs / shorts separately, bootstrap + DD
  permutation on 2023+ (`resampling.py`), MC at trading size (`montecarlo.py`). Outputs via `tools/run_stamped.sh analysis/x.py
  > analysis/outputs/x.txt`. Above C needs t >= `metrics.t_threshold(N_items)` or DSR >= 0.95 (unless pre-registered) and the
  `strategy-checker` agent. Details: `DEVELOPMENT_PROCESS.md`.
- **New data:** run `analysis/new_data_screen.py` over every plan piece too (DEVELOPMENT_PROCESS 'New data').
- **Every strategy the user sends:** also an ingredient breakdown and `analysis/strategy_data_sweep.py <trades.csv> <name>`.
- **Bench base = the live plan:** `bench150.LIVE_EVAL` = `live/expected_setup.json` = `apex_strategies/README.md`; change them in
  the same commit. **Resize after every plan change:** then run `analysis/resize_book.py` (account state in its `NOW` line) and
  report it in the same reply; change sizes only if the holdout AND account-now bands are above 0.
- **Add or replace:** test candidates as an addition AND as a replacement of the piece they overlap most; capital-only gains
  go to `PORTFOLIO.md`'s capital-expansion table.
- **Papers:** summarize, foundation or not, test when it fits, rank in `TIER_LIST.md`; PDFs in `papers/`. Execution findings ->
  `agents/codex/EXECUTION_REFERENCES.md`.
- **Folders:** `apex_strategies/` evaluation, `funded_strategies/` funded; `data/`, `analysis/outputs/`, `mc_reports/`, `archive/`.
- **A confirmed accounting / execution defect goes to the user immediately.**
- **KILL / RESUME:** run `python3 analysis/kill_switch.py kill "<their words>"` (or `resume`) at once, then point to the FLATTEN
  steps in `live/vps/KILL_SWITCH.md`. **Overrides** (skipped / closed early / resized / paused a live trade by hand):
  `python3 analysis/override_log.py add ...` in the same reply.
- **Effort:** before any non-trivial task, recommend low / medium / high / max in one line.
- **Corrections:** add one line to `LESSONS.md` 'Corrections from the user' in the same reply; read it at session start.

## Sessions and schedules
- **Master** `session_01Wk1fPYssjbaEfe21f4v6vD`: tracks sessions, collects decisions. **Papers** `session_01Wk1fPYzv9RyXGytT4z6XbK`.
  **Code reviewer** `session_01Wk1fPW6LVWayRousRwL7mU` (on "review"; `agents/cross_review/CODE_REVIEW_LOG.md`).
- Paper scout and strategy lab STOPPED by the user 2026-11-05 (scout runs only on "scout"; lab: `lab/STOP`). History:
  `archive/retired_rules.md`.
- **Scheduled jobs:** pre-market check 08:21 CT, journal / dashboard 16:40 CT, Friday review (`RUNBOOKS.md`, `FRIDAY_REVIEW.md`).
