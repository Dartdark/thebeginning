# Project notes for Claude

NQ/ES futures strategies in MultiCharts PowerLanguage for Apex 50K prop accounts (challenge and
funded). Start with `NEW_CHAT_BRIEF.md` (latest state), then `funded_strategies/README.md`, `TIER_LIST.md`, `TODO.md` (user's open to-dos; tick off what they say is done), `WATCHLIST.md` (items to recheck), `MULTICHARTS_PITFALLS.md` (error log: read before writing MultiCharts code, add every solved error), `LESSONS.md` (short rules learned the hard way; add to it in the Friday review) and `S_RANK_PROGRAM.md` (current goal: one S-rank strategy per symbol). `HANDOFF.md` is the old 2026-10-14 handoff: background only.

## Working rules

- **Apex only** (ignore Topstep). Positions flat by 15:59 CT; $2,000 end-of-day trailing drawdown.
- **Notifications (user, 2026-10-23):** send one PushNotification (under 200 characters, the reply's headline) at the end of
  every reply to the user, so each new message reaches the phone. The tool is often deferred: load it first with
  ToolSearch `select:PushNotification` (2026-10-24: a session wrongly reported it missing all day). (A hook can't do this from the cloud container: ntfy.sh
  answers 429 from the shared proxy.)
- **Alerts reach the phone through ntfy (2026-10-29):** Claude's PushNotification reaches the phone only while the user is NOT
  in the Claude app (it is held back while they're active in it; confirmed 2026-10-29). Every alarm or reminder from a scheduled check goes through `python3 analysis/send_alert.py "text"` (VPS relay -> ntfy,
  ~1-2 min) as well as the PushNotification. Keep alert lines short (under 200 characters).
- **Papers session (user, 2026-10-29):** `session_01Wk1fPYzv9RyXGytT4z6XbK` ("📄 Papers", nested under the master): the user
  uploads papers there; it reviews / tests / ranks them and sends the master a short verdict per paper (send_message).
- **Master session (user, 2026-10-28):** `session_01Wk1fPXwvHF5qTjW7bUhYx9` (desktop app, pinned) is the user's master session: it
  tracks the other sessions, collects the decisions waiting on the user and starts new sessions. Other sessions: put a
  decision for the user in your reply as usual; the master session reads it from there.
- **Live dashboard (2026-10-28):** 'Apex Live Desk' https://claude.ai/artifact/3oqbHWqBFTrUQd95wMmuL8 (accounts, trades,
  live guard, VPS health, live-vs-backtest range, edge per strategy, missed-trade alarm). Refresh after each close:
  `python3 analysis/dashboard_data.py` (also runs `analysis/live_panels.py` and `analysis/account_tools.py`; account rules in `account_tools.EVALS`), upload every JSON in
  `analysis/outputs/dashboard/` except `bt_cache.json` as an asset and update the dataset with the same id (url / name /
  updated). New Apex balance from the user -> `ACCOUNTS` in dashboard_data.py; new account -> `ACCTS` in live_panels.py.
  After a backtest report changes, rebuild scratch_data and rerun live_panels.py to refresh `bt_cache.json`.
- **Branches:** work on `claude/nq-trading-strategy-params-5h9d20`; keep
  `claude/quirky-noether-4dla64` and the session's designated branch identical; push every
  commit to all of them.
- **Links:** always give direct GitHub links (and the raw link for code to paste into MultiCharts). The repo is PRIVATE since
  2026-10-19: raw links only open while logged in to GitHub, and scripted downloads (Invoke-WebRequest) fail; on the PC use
  `git pull` in the clone instead.
- **Code in chat (user, 2026-10-29):** don't paste whole files into the reply. Give each file as one line: name, what it
  is / what changed, GitHub link + raw link (copy from the raw page: Ctrl+A, Ctrl+C). Paste code only when it's a few lines
  (a snippet to add) or the user asks for the full text.
- **Journal (Obsidian, 2026-10-17):** `journal/daily/` and `journal/ideas/` are the user's notes, pushed to the work branch by
  `journal/sync.ps1` (with `live/` reports). On "read my journal": `git pull` the work branch, read the new notes, compare
  with the backtest trades of those days, act on problems (fix / `MULTICHARTS_PITFALLS.md` / `TODO.md`), test ideas and set
  their `Status:` line. Since 2026-10-19 Claude (Cowork on the user's PC) writes the daily notes from the user's answers;
  keep the user's own words, never invent fills or numbers. Trades come from the VPS trade log (`apex_strategies/Apex_Trade_Logger.txt` ->
  `live/trades/YYYYMMDD.csv`); `analysis/journal_trades.py` writes them into the note (weekday task 16:40 CT). The user also pushes now: always pull before pushing.
- **Friday review (scheduled, 2026-10-19):** each Friday after the close, follow `FRIDAY_REVIEW.md` (weekly review,
  first-Friday Monte Carlo check, Claude-Codex cross-review). A confirmed accounting / execution defect goes to the user
  immediately, not on Friday.
- **Papers in git (user, 2026-10-19):** research-paper PDFs may be committed (folder `papers/`). Books stay out.
- **Repo map:** `README.md` (reorganised 2026-10-21): MultiCharts reports in `mc_reports/`, all price data in `data/`,
  script results in `analysis/outputs/`, exporters in `tools/exporters/`, old material in `archive/`. Put new files there.
- **Folders:** `apex_strategies/` = challenge-only strategies (Vault Break, Overnight Bias);
  `funded_strategies/` = funded strategies. Comparing them is fine; the challenge ones are not
  meant for making money in funded accounts.
- **Capital-expansion bench (user, 2026-10-24):** a strategy that only gains by needing more capital (lower return per
  drawdown at the current size) goes into the 'Capital-expansion bench' table in `personal_strategies/PORTFOLIO.md`, not
  into a plan; re-test the bench when the account steps up a ladder row.
- **Add or replace (user, 2026-10-18):** a candidate doesn't have to add to the plan. Always also test it as a
  replacement (in place of, or in part of, the plan strategy it overlaps most) and adopt whichever serves the plan overall.
- **Preferences:** low-correlation strategies preferred; regime-dependent ones welcome but not
  preferred; funded payouts are the main goal, challenge improvements are a bonus.
- **Testing standard:** costs $7.25/NQ ($5/ES) + 1 tick slippage per market/stop fill; 2018–2026;
  by year and 2023 onward; placebo / walk-forward where relevant; funded bench
  (`analysis/funded_lab.py`; plan decisions on the bootstrapped bench `analysis/funded_bootstrap.py`, which gives ranges). **Always report Sharpe, Sortino, profit factor, Calmar and Ulcer
  index** (`analysis/metrics.py`), for the whole strategy and for longs and shorts separately,
  with bootstrap intervals and drawdown permutation (`analysis/resampling.py`) on the
  2023-onward holdout, plus **Monte Carlo** (`analysis/montecarlo.py`: trade reshuffle + one-year block bootstrap with
  the Apex EOD-trailing hit probability, at the size it would trade). **Multiple testing:** run `analysis/trials.py` after ranking; promotion above C needs
  t ≥ `metrics.t_threshold(N_items)` or deflated Sharpe ≥ 0.95, unless pre-registered (see `DEVELOPMENT_PROCESS.md`).
  **Independent check:** before promoting, put the candidate in `checks/candidates/<name>/` and run the
  `strategy-checker` agent (it rebuilds the rule from the spec, then `analysis/checker.py`).
- **Development process:** follow `DEVELOPMENT_PROCESS.md` (including the strategy lifecycle: backtest → MultiCharts + checker →
  Apex incubation → personal live account). Every strategy is checked as a
  whole first, then its **longs and shorts are analysed and improved separately** and
  recombined.
- **Execution references (user, 2026-10-29):** every execution idea, fill / slippage measurement or verified market-behavior
  finding (ours, papers, Codex) goes into `agents/codex/EXECUTION_REFERENCES.md` (E-numbered, Codex's template); check it
  before any fill / execution work.
- **Papers / articles:** summarize (what it's about, findings, why it should make money), say
  whether a strategy can be built on top of it as a foundation, test it when there's a fit,
  and **rank every tested item in `TIER_LIST.md`** (S–F).
