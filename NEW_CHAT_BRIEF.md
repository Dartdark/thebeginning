# New-chat brief (rewritten 2026-10-29): read this first

Opener for a new chat: *"Read `NEW_CHAT_BRIEF.md`, then `CLAUDE.md`, `TODO.md` and `LESSONS.md` in
github.com/Dartdark/thebeginning (branch `claude/nq-trading-strategy-params-5h9d20`) and continue from there."*
Read `MULTICHARTS_PITFALLS.md` before writing MultiCharts code. The full history of this brief (up to 2026-10-28) is in
`archive/brief_history_2026-10.md`; ticked to-dos are in `archive/TODO_done_2026-10.md`.

## Now (2026-10-31)

- **Live accounts (Apex, VPS QuantVPS Chicago, MultiCharts + Rithmic, data dxFeed):**
  - #1 APEX-681524-01 50K: **blown 10/26**. #3 APEX-681524-03 150K: **blown 10/30** (Apex liquidated the ONB short on an
    intraday touch of the $146,000 floor; MULTICHARTS_PITFALLS). Its 150 charts are retired (watchdog shows them OFF until closed).
  - #2 APEX-681524-02 50K evaluation: ~$49,828, ~$1,064 above its $48,764 floor; model pass odds ~46%. Combine set VB 8,
    ONB ADX30 $1,100, EOS $500, Bridge Monday 2. **Full size stays** (thin-cushion test, rerun with whole contracts).
  - **#4: 150K No-Activation, user buys it Sunday 11/01** -> add its id to `live/expected_setup.json`, `ACCTS` in
    `analysis/live_panels.py`, `ACCOUNTS` in `analysis/dashboard_data.py`, `account_tools.EVALS` (floor alarm). Set = combine x 2.5
    (VB 20, ONB $2,750, EOS $1,250, Bridge 5). **No new 50Ks.**
- **Buying plan (TODO):** job Nov 10 - Dec 24, $25/h x 8 h, paid weekly, all of it for evaluations: 150K No-Activation only,
  3-4 per payday, one a day, stop on the drift alarm. `analysis/ramp_budget_test.py`: nothing funded by 12/31 13-31%; first
  payouts late Feb - Mar 2027; 2027 at 75% edge ~$89-116k (job ends) / ~$176-182k (job kept*). Personal account ~Apr-May.
  Business plan v3 (rewritten 10/30): `reports/Trading_Business_Plan_2026-10-30.pdf` (source html + `render_business_plan.js`).
- **Live guard (10/30):** rejected-orders limit 10 on every strategy; watchdog Apex floor alarm (ACCTFAIL/NEARFLOOR, ran clean
  on the VPS 10/30); `HB_Ver` code-version stamps in SIG rows (user repasted); `analysis/live_guard.py`; pre-market check 08:22 CT
  (`premarket_check.py`: Chicago clock/DST, each ACCT/POS/SIG row aged vs its own interval + 15 min); payout tracker
  (`account_tools.FUNDED`, fill as accounts pass); `live/vps/VPS_MAINTENANCE.md` (Saturday updates/restart, Sunday pre-open
  routine by 16:30 CT, done by user).
- **Weekly cross-review 10/30:** Codex found 5 defects in Claude's week code, all fixed; follow-ups fixed through a01be1b
  (`agents/cross_review/2026-10-30_summary.md`, Codex `agents/codex/results/weekly_fix_reply_20261030.md`). Lesson: Claude's
  weekly side reviews its OWN code too.
- **Open for Claude:** heartbeat + HB_Ver in all 9 funded strategies + funded floor rules before the first funded account (~late Nov); Brier-score
  pass odds after ~20 finished evaluations; rerun backtests on extended data; futures-trend upload waits in
  `checks/candidates/futures_trend/` (test at ~$150k).
- **Recent research verdicts:** CHoCH D, Nocturne C (WATCHLIST #26), Setup Generator F, Prior VWAP Trap bench-only; GreenORB and
  video Drift rejected (Codex). Execution references E01-E31 (`agents/codex/EXECUTION_REFERENCES.md`, next E32). Paper scout:
  `/scout`, also Mon/Wed/Fri in the Papers session.
- **Sessions:** master `session_01Wk1fPXwvHF5qTjW7bUhYx9`; Papers `session_01Wk1fPYzv9RyXGytT4z6XbK`; scheduled jobs
  `session_014DKffATms37kZigaa2xR2P` (16:40 journal + dashboard, Friday review 16:47, reminders Sun/Wed, MNQ roll 12/10).
  Dashboard 'Apex Live Desk' https://claude.ai/artifact/3oqbHWqBFTrUQd95wMmuL8.
- **Plans:** `funded_strategies/FUNDED_PLAN.md`, `funded_strategies/README.md`, `personal_strategies/PORTFOLIO.md` (50K funded:
  RS longs -> T_ONESIDE 1, VB 2/1; 150K funded: Dual Thrust 2. Swing Target funded swaps reverted 10/31: ties after the fix).
- **Every reply ends with a PushNotification** (CLAUDE.md); alerts also via `python3 analysis/send_alert.py`.

## Who / what

- Algo trader on **Apex** (ignore Topstep): flat by 15:59 CT; 50K: $2,000 EOD trailing (locks at $50,100), combine $3,000
  target, $1,000 daily loss limit. Goal: funded payouts (6 = $13,000 per 50K account), as fast as possible.
- Path: Apex = live test bench and funding source; proven strategies and payouts move to a personal account
  (`DEVELOPMENT_PROCESS.md` 'Strategy lifecycle'). Business plan v3: `reports/Trading_Business_Plan_2026-10-30.pdf` (rewritten: source `reports/business_plan_2026-10-30.html`, render `node reports/render_business_plan.js`; v2 2026-10-24)
  (new dated file per update).
- Preferences: forced / scheduled flows (price patterns fail here), low correlation, longs and shorts analysed separately.
  Always give direct GitHub links + raw links for code to paste into MultiCharts (repo PRIVATE: links need a login).
- Helpers: Cowork / local Claude Code on the user's PC (`cowork/INSTRUCTIONS.md`: daily journal note, sync, copying
  reports; never orders or inputs). Codex (GPT-6.1 Sol) builds on `codex/work`; weekly cross-review every Friday
  (`agents/codex/TASK_weekly_cross_review.md`, `agents/cross_review/`).
- VPS pipeline: every live chart has `Apex Trade Logger` (C:\TradingLogs\YYYYMMDD.csv, OPEN / CLOSE / POS rows);
  `push_trade_logs.ps1` pushes to `live/trades/` + `live/health/` at 16:10 CT (open check-in 08:15); `watchdog.ps1` alerts the
  phone via ntfy every 5 min in RTH (`live/vps/README.md`).
- Account #2 and #3 each keep their own chart set (no copier for evaluations; copier later for funded accounts, grouped by
  cushion). Logger tags: VB / ONB / EOS / MON_BR + `-2` (account #2) or `150` (account #3).

## Research state (short; the tier list is the record)

- `TIER_LIST.md` ranks every tested item S-F; `WATCHLIST.md` items to recheck; `S_RANK_PROGRAM.md` current goal.
- Recent: Dual Thrust v4 A (MC-confirmed), Overnight Tick / VIX A (MC-confirmed), FC 2B A (forward log), T_ONESIDE B
  (MC-confirmed, in the 50K funded plan), PAPERTREND v2 B, FVB B (capital-expansion bench), IFT_NQ5 C, YZ ORB D, Brooks F.
- Lessons that keep repeating: a plan near Apex's payout cap can't use a better strategy; judge on the bootstrapped bench
  (`analysis/funded_bootstrap.py`), always against the empty slot and as a replacement too (`LESSONS.md`).

- Origins (user, 2026-10-29): the user's own designs are Vault Break and Overnight Bias only; every other 'user's' upload
  (Relative Strength, Dual Thrust, Overnight Tick / VIX, Swing Target, T_ONESIDE, Kusho, S47, FC 2B, ...) was found
  outside. Our own research found EOS, Monday Long, Late-Day Flow, NFP Fade, ES MOC, CL gap fade, Overnight Drift.

## Rebuilding the data (not in git)

- `pip install numba`, then `python3 analysis/build_lab.py scratch_data` builds g24 / ge / lab; gc / cl pickles build on first
  `load("GC")` / `load("CL")`. Raw 1-minute CSVs in `data/`, MultiCharts reports in `mc_reports/`.
- Continuous contracts are not back-adjusted: roll jumps at 03:32 or 17:01 CT; drop roll bars in new tests.
