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
  at trading size (`analysis/montecarlo.py`). Plan decisions on the bootstrapped funded bench (`analysis/funded_bootstrap.py`). Saved outputs carry a provenance
  line (code commit + data range/fingerprint): run them as `tools/run_stamped.sh analysis/x.py ... > analysis/outputs/x.txt`.
  Promotion above C needs t >= `metrics.t_threshold(N_items)` (`analysis/trials.py`) or deflated Sharpe >= 0.95 unless
  pre-registered, and the `strategy-checker` agent on `checks/candidates/<name>/`. Longs and shorts analysed separately.
- **Screen every piece against new data (user, 2026-11-10):** when new data arrives, besides the idea it was fetched for,
  run `analysis/new_data_screen.py` over every plan piece (DEVELOPMENT_PROCESS 'New data: screen every piece'); leads get a book
  bench vs the same size spread evenly, then out-of-sample evidence before any plan change.
- **Every strategy the user sends (user, 2026-11-10):** good or bad on its own, it ALSO gets (1) an ingredient breakdown (one part
  changed at a time, DEVELOPMENT_PROCESS 'Ingredient register') and (2) the full data sweep `python3 analysis/strategy_data_sweep.py
  <trades.csv> <name>` (every data series x regime, with the fair best-of-N placebo), to look for a better version. Report both with
  the standard test; a better version is a lead until a book bench and out-of-sample evidence confirm it.
- **Add or replace (2026-10-18):** test every candidate as an addition AND as a replacement of the plan piece it overlaps
  most. **Capital-expansion bench (2026-10-24):** gains that only come from more capital go to that table in `PORTFOLIO.md`.
  Preferences: low correlation, funded payouts first; regime-dependent welcome, not preferred.
- **Papers / articles:** summarize, say whether it can be a foundation, test when it fits, rank in `TIER_LIST.md`. PDFs may
  be committed (`papers/`), books not. Execution / fill / market-behavior findings -> `agents/codex/EXECUTION_REFERENCES.md`.
- **Folders:** `apex_strategies/` = challenge-only; `funded_strategies/` = funded. Data in `data/`, results in
  `analysis/outputs/`, MC reports in `mc_reports/`, old material in `archive/`.
- **A confirmed accounting / execution defect goes to the user immediately**, not on Friday.
- **KILL / RESUME (user, 2026-11-01):** when the user writes KILL (or RESUME) about trading, run
  `python3 analysis/kill_switch.py kill "<their words>"` (or `resume`) at once, no questions, then remind them of the manual
  FLATTEN steps in `live/vps/KILL_SWITCH.md`. **Overrides:** when they say they skipped, closed early, resized or paused a
  live trade by hand, log it with `python3 analysis/override_log.py add ...` in the same reply.
- **Effort (user, 2026-11-01):** before starting any non-trivial task, say which effort level you recommend (low / medium /
  high / max) and why in one line, so the user can set it before you go.
- **Corrections (user, 2026-11-01):** whenever the user corrects you, add one line to `LESSONS.md` ('Corrections from the
  user': date, their words, the rule that prevents it) in the same reply. Read that section at session start.

## Sessions and schedules
- **Master** `session_01Wk1fPYssjbaEfe21f4v6vD` (from 2026-11-01 evening; previous master `session_01Wk1fPXwvHF5qTjW7bUhYx9` retired: context full): tracks the other sessions, collects decisions, starts sessions.
  Other sessions put user decisions in their reply.
- **Papers** `session_01Wk1fPYzv9RyXGytT4z6XbK`: user uploads papers; sends the master a verdict per paper. Paper scout
  (`.claude/skills/scout/SKILL.md`, log `papers/SCOUT_LOG.md`): **schedule STOPPED by the user 2026-11-05** (with the lab); runs only
  when the user says "scout".
- **Strategy lab** `session_01Wk1fPZPJ3brXtvmkNxsoDD`: **STOPPED by the user 2026-11-05 (no finds; `lab/STOP`, schedule disabled)**; was 5x a day, skill
  `.claude/skills/lab/SKILL.md`, rules `lab/README.md`, ledger `lab/ledger.json`, kill switch `lab/STOP`. Never changes
  plans, charts or the VPS; stage-4+ results go to the master.
- **Code reviewer** `session_01Wk1fPW6LVWayRousRwL7mU`: on "review", checks new code, fixes Claude's defects, logs
  `agents/cross_review/CODE_REVIEW_LOG.md`.
- **Scheduled jobs** (pre-market check 08:21 CT + journal/dashboard 16:40 CT RESUMED 2026-11-11 for account #5; Friday review): see `RUNBOOKS.md` and `FRIDAY_REVIEW.md`.
