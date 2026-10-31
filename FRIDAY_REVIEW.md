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
