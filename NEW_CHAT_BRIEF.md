# New-chat brief (rewritten 2026-10-29): read this first

Opener for a new chat: *"Read `NEW_CHAT_BRIEF.md`, then `CLAUDE.md`, `TODO.md` and `LESSONS.md` in
github.com/Dartdark/thebeginning (branch `claude/nq-trading-strategy-params-5h9d20`) and continue from there."*
Read `MULTICHARTS_PITFALLS.md` before writing MultiCharts code. The full history of this brief (up to 2026-10-28) is in
`archive/brief_history_2026-10.md`; ticked to-dos are in `archive/TODO_done_2026-10.md`.

## Now (2026-11-05)

- **No live accounts.** #1 (10/26), #3 (10/30), #2 and #4 (11/04) all failed. Live replay 10/20-11/04: VB 15/15 trades match the
  backtest, ONB matches bar the known 10/27 miss: execution OK, a losing stretch (~6.5th percentile, ~5 a year;
  `analysis/outputs/bad_stretch_freq_output.txt`). Sizing can't fix it (`eval_sizing_bench_output.txt`). Buy gate PAUSE until 11/06;
  next buy also needs the paycheck to cover the budget deficit.
- **Budget:** start $500, balance -$335 (MultiCharts $152.65 due 11/08); recurring $252.64/month (MC, Claude, ChatGPT, VPS Lite).
  `live/budget/` + dashboard https://claude.ai/artifact/9S2F8YHC2mdM8adWkzCB1v (steps: RUNBOOKS 'Budget dashboard'). User reports
  paychecks weekly (job from Nov 10). VPS downgrade under consideration.
- **Watchdog phone alerts muted 11/05 (user)** while no account in `live/expected_setup.json` is "live"; problems still go to
  C:\TradingLogs\alerts.txt as MUTED. Setting a new account to "live" turns them back on. Kill / Claude relay alerts not muted.
- **Stopped by the user 11/05:** strategy lab (`lab/STOP`), paper scout schedule, pre-market check, 16:40 journal/dashboard job (restart
  both checks when an account is bought). Still on: morning brief 07:47 CT, Friday review, to-do reminders, MNQ roll 12/10.
- **Research 11/03-11/05:** Bridge noise-area longs B (MC RTH-anchor 98.9% match, t 5.0) -> personal plan 1 MNQ (needs early-close
  flat + fill-latency check before live). Ricochet 1144 C -> capital-expansion bench, last in line. BTC weekend beta C; Monday Long
  BTC filter WATCHLIST #27 (post hoc, noise-level). Pre-screen soft guide (DEVELOPMENT_PROCESS): piece Sharpe > ~3.15 x corr with book.
- **Career:** `career/APPLICATIONS.md` (Mercor, Outlier, Alignerr, Micro1, DataAnnotation, Upwork/Fiverr, Anthropic Residency by
  Nov 22); waiting on the user's background to tailor; tick as applied.
- **Done 11/05 (repo, not compiled on the VPS):** kill-switch tri-state (GetLastError; 6 files, HB_Ver 2026-11-05: paste all at
  the next account setup), funded heartbeats (9 files) + `funded_rules` in expected_setup.json, pre-market VB 30-min stamp fix
  (replayed 11/03 08:20: no flag), noise-area early-close flat (EL + replay `bridge_noise_15m_earlyclose_output.txt`: +$3.1k, 0 held).
- **Open for Claude:** noise-area live fill-latency measurement (needs live fills); Target Guard v2 check (needs a live trade);
  career tailoring (needs the user's background).

## Earlier (2026-11-01 to 11-04)

- **Live accounts:** #1 blown 10/26, #3 blown 10/30. **#2** APEX-681524-02 50K eval ~$49,828 (~$1,064 above floor $48,764: one
  full VB loss ~$1,200 could fail it; user not yet asked to resize). **#4** APEX-681524-04 150K No-Activation, bought 11/01
  despite the buy-gate PAUSE (live/overrides.csv), first session 11/02; reuses tags VB150/ONB150/EOS150/MON_BR150 (dashboard +
  journal: #3 through 10/30, #4 from 11/02). Floor $146,000, lock $150,100, target $159,000. Buy gate PAUSE until 11/06.
- **VERIFIED 11/01 18:45 (VPS feed):** all 8 charts on 2026-11-02 strategy versions; routing (GetAccountID) #2 -> -02, #4 -> -04;
  auto-trading on; flat. Bridge Monday Long could enter 19:00 Sunday (2 MNQ #2, 5 MNQ #4).
- **VPS feed (new 11/01):** `python3 analysis/vps_status.py <scratch>/vps` -> status, routing table, trade tail, screen.jpg
  (Read it). Branch `vps-status`, every 5 min. Setup `live/vps/VPS_STATUS.md`. Defender exclusion on screen_push.ps1 only.
- **Kill switch (installed 11/01):** strategies read C:\TradingLogs\KILL via kernel32 GetFileAttributesA (EL Collections NOT
  installed); folder unreadable -> no new entries. Two latches (KILL_LOCAL / KILL_REMOTE), relay self-repair every minute,
  kill_test.ps1 16/16 PASS, remote KILL/RESUME tested end to end. User KILL -> `python3 analysis/kill_switch.py kill "..."`.
- **Strategy lab STOPPED by the user 2026-11-05** (no candidate reached the benches; `lab/STOP`). Paper scout schedule stopped too (user 2026-11-05).
- **#2 and #4 FAILED 11/04** (ONB full stop + 2 VB stops; same signals on both). Live replay 10/20-11/04 (`analysis/outputs/live_replay_1020_1104_output.txt`): VB 15/15 trades identical to the backtest, ONB matches except the known 10/27 compile miss and an ADX knife-edge one-bar-late entry (same loss): execution OK, the stretch was a losing one. Sizing bench (`analysis/outputs/eval_sizing_bench_output.txt`): smaller sizes turn fails into time-outs and slow passes (half size 50K pass 50 -> 38%, fee per funded $498 -> $661); VB loss cap no effect; only ONB $550 on 50K lowers fails (48 -> 40%) at ~the same pass rate; no sizing would have survived this stretch. No accounts open; buy gate PAUSE.
- **Bridge noise-area 15-min (11/03, user's paste):** longs-only B (t 5.6, checker PASS WITH CONCERNS, entry latency the risk); no plan gain (best: 150K funded VB -> NBL 3, noise-level). Waiting on the user's MultiCharts List of Trades (RTH chart, after market 11/03). `TIER_LIST.md` row, `analysis/bridge_noise_15m_*.py`.
- **Codex:** review 11/01 (7 findings) + follow-up 11/02 (3) all fixed/installed. Codex kill-reply review 11/02: 2 closed, 1 medium left (file-error tri-state), user: fold into next repaste (TODO). Packet `agents/codex/TASK_review_2026-11-01.md`.
- **Rule (11/01, LESSONS):** every MultiCharts claim names its source and says VERIFIED or GUESS. ACCT column 4 = typed
  monitor account, column 9 = real routing.
- **Open:** firm view panel (after #4, TODO); funded heartbeats; Brier pass odds after ~20 evals; DATA_NEEDS.md (free MC exports
  first: NG expiring contracts unblock lab Q011); local kill.ps1 phone alert untested (optional, Monday after 16:00).

## Earlier (2026-10-31)

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
- **Sessions:** master `session_01Wk1fPYssjbaEfe21f4v6vD` (previous `session_01Wk1fPXwvHF5qTjW7bUhYx9`, retired 11/01); Papers `session_01Wk1fPYzv9RyXGytT4z6XbK`; scheduled jobs
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
