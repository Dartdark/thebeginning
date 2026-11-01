# Project notes for Claude

NQ/ES (and other CME futures) strategies in MultiCharts PowerLanguage for Apex prop accounts (evaluations and funded; new
accounts are 150K No-Activation since 2026-10-30) and a later personal account.

**Map (read in this order):** `NEW_CHAT_BRIEF.md` (latest state) · `TODO.md` (user's to-dos; tick what they say is done) ·
`TIER_LIST.md` (every tested item, S-F) · `funded_strategies/README.md`, `funded_strategies/FUNDED_PLAN.md`,
`personal_strategies/PORTFOLIO.md` (plans) · `WATCHLIST.md` · `LESSONS.md` · `MULTICHARTS_PITFALLS.md` (read before writing
MultiCharts code; add every solved error) · `DEVELOPMENT_PROCESS.md` · `RUNBOOKS.md` (dashboard refresh, journal) ·
`FRIDAY_REVIEW.md` · `lab/README.md` · `README.md` (repo layout). `HANDOFF.md` / `S_RANK_PROGRAM.md`: background only.

## Rules

- **Apex only.** Flat by 15:59 CT; end-of-day trailing drawdown ($2,000 on 50K, $4,000 on 150K; intraday touch fails).
- **Every reply ends with one PushNotification** (< 200 characters, the reply's headline; load it with ToolSearch
  `select:PushNotification` when deferred). Write the reply text once, after the notification (2026-11-01: writing it before
  and after doubled every reply). Alarms from scheduled checks also go through `python3 analysis/send_alert.py "text"` (ntfy;
  PushNotification is held back while the user is in the app).
- **Branches:** work on `claude/nq-trading-strategy-params-5h9d20`; keep `claude/quirky-noether-4dla64` and the session's
  designated branch identical; pull before pushing. **Run `python3 tools/prepush_check.py <designated>` before every push**
  (refuses: not pulled, model IDs) and `--after <designated>` after it (branch sync). No model IDs in commits.
- **Receipts:** a summary of finished work names what was verified (actually run), what was NOT verified, and the risks.
  Never state a result that wasn't run ("can only strengthen" without the replay: 2026-10-30).
- **Links and code:** direct GitHub links (repo PRIVATE: raw links need a login; on the PC `git pull`). Don't paste whole
  files: one line per file (what changed, GitHub + raw link); paste only short snippets or on request.
- **Testing standard:** costs $7.25/NQ ($5/ES) + 1 tick per market/stop fill; 2018-2026, by year and 2023 onward; placebo /
  walk-forward where relevant. Always report Sharpe, Sortino, PF, Calmar, Ulcer (`analysis/metrics.py`), whole and longs /
  shorts separately, bootstrap intervals + drawdown permutation on the 2023+ holdout (`analysis/resampling.py`), Monte Carlo
  at trading size (`analysis/montecarlo.py`). Plan decisions on the bootstrapped funded bench (`analysis/funded_bootstrap.py`).
  Promotion above C needs t >= `metrics.t_threshold(N_items)` (`analysis/trials.py`) or deflated Sharpe >= 0.95 unless
  pre-registered, and the `strategy-checker` agent on `checks/candidates/<name>/`. Longs and shorts analysed separately.
- **Add or replace (2026-10-18):** test every candidate as an addition AND as a replacement of the plan piece it overlaps
  most. **Capital-expansion bench (2026-10-24):** gains that only come from more capital go to that table in `PORTFOLIO.md`.
  Preferences: low correlation, funded payouts first; regime-dependent welcome, not preferred.
- **Papers / articles:** summarize, say whether it can be a foundation, test when it fits, rank in `TIER_LIST.md`. PDFs may
  be committed (`papers/`), books not. Execution / fill / market-behavior findings -> `agents/codex/EXECUTION_REFERENCES.md`.
- **Folders:** `apex_strategies/` = challenge-only; `funded_strategies/` = funded. Data in `data/`, results in
  `analysis/outputs/`, MC reports in `mc_reports/`, old material in `archive/`.
- **A confirmed accounting / execution defect goes to the user immediately**, not on Friday.
- **Corrections (user, 2026-11-01):** whenever the user corrects you, add one line to `LESSONS.md` ('Corrections from the
  user': date, their words, the rule that prevents it) in the same reply. Read that section at session start.

## Sessions and schedules
- **Master** `session_01Wk1fPXwvHF5qTjW7bUhYx9` (pinned): tracks the other sessions, collects decisions, starts sessions.
  Other sessions put user decisions in their reply.
- **Papers** `session_01Wk1fPYzv9RyXGytT4z6XbK`: user uploads papers; sends the master a verdict per paper. Paper scout
  (`.claude/skills/scout/SKILL.md`, log `papers/SCOUT_LOG.md`) on "scout" and 5x a day (00:43 / 06:43 / 11:43 / 16:43 /
  20:43 CT), feeding `lab/IDEAS.md` (keeps >= 3 queued).
- **Strategy lab** `session_01Wk1fPZPJ3brXtvmkNxsoDD`: 5x a day (01:13 / 07:13 / 12:13 / 17:13 / 21:13 CT), skill
  `.claude/skills/lab/SKILL.md`, rules `lab/README.md`, ledger `lab/ledger.json`, kill switch `lab/STOP`. Never changes
  plans, charts or the VPS; stage-4+ results go to the master.
- **Code reviewer** `session_01Wk1fPW6LVWayRousRwL7mU`: on "review", checks new code, fixes Claude's defects, logs
  `agents/cross_review/CODE_REVIEW_LOG.md`.
- **Scheduled jobs** (journal + dashboard 16:40 CT, Friday review): see `RUNBOOKS.md` and `FRIDAY_REVIEW.md`.
