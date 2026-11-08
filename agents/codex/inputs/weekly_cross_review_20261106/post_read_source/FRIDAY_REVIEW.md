# Friday review (moved out of CLAUDE.md 2026-10-29, unchanged)

- **Friday review (scheduled, 2026-10-19):** each Friday after the close: pull, read the week's journal notes and `live/`
  reports, run `analysis/live_vs_backtest.py --all live/`, update `TIER_LIST.md` / `WATCHLIST.md` / `TODO.md` /
  `NEW_CHAT_BRIEF.md`, add new lines to `LESSONS.md`, and condense the brief on the first Friday of each month. **Also on the
  first Friday of each month (from December 2026, user 2026-10-22, after Kevin Davey):** per account, place last month's
  actual P&L (Apex dashboard, fees included) in the Monte Carlo range for one month of the live strategy set at live size
  (`analysis/montecarlo.py`, 21-day block bootstrap of the backtest daily P&L, 2023 onward) and report its percentile;
  below the 10th two months running → review with the drift alarm. Count the same signal on two accounts as one event.
  **Also every Friday (user, 2026-10-23): the Claude-Codex cross-review** (`agents/codex/TASK_weekly_cross_review.md`):
  review Codex's week independently into `agents/cross_review/YYYY-MM-DD_claude.md` (max 5 material disagreements, each with
  evidence and the smallest settling check), then read Codex's file when the user has run its side, and write the joint
  `..._summary.md` (agreed / disputed / user decisions). Remind the user to send Codex "do the weekly cross-review" One response
  each, then a deciding check; open items stay 'unresolved' and carry forward. Routine checks run at once; new backtests keep
  the pre-registration gates. A confirmed accounting / execution defect goes to the user immediately, not on Friday;
  judgement calls go to the user with both views, the uncertainty and a recommendation.

- **Stale-rule review (first Friday of each month, user 2026-11-01, 'harnesses decay'):** go through `CLAUDE.md`,
  `LESSONS.md`, `MULTICHARTS_PITFALLS.md`, `lab/README.md` and the skills. For each rule ask: which failure does it prevent,
  has that failure happened in the last 2 months, can code enforce it instead (move it into a check: `tools/prepush_check.py`,
  `analysis/lab_tools.py`, a test), is it still true (accounts, sizes, sessions)? Then: enforceable -> code; outdated ->
  fix; no longer useful -> move to `archive/retired_rules.md` with the date and reason (never delete outright). Keep
  `CLAUDE.md` a short map (under ~6,000 characters). Report what changed in the Friday summary.

- **Manual overrides (every Friday, user 2026-11-01):** `python3 analysis/override_log.py summary`. Fill the results of the
  week's rows first (what actually happened vs the strategy's own result: the other account's same trade, or the backtest
  list). Report whether overriding made or cost money; after ~20 overrides, recommend keeping or stopping the habit.
