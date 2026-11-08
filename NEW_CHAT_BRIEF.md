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
- **Cushion cap bench 11/08** (`analysis/outputs/cushion_cap_bench_output.txt`, after Codex's 11/04 loss audit): capping each
  stop at the room above the floor cuts fails (50K 48 -> 37%) but pass rate falls (50 -> 48%), fee per funded $498 -> $519;
  combined cap worse. Not adopted for evaluations. **Funded bench 11/08** (`cushion_cap_funded_vb2_output.txt`): blown 8.1 ->
  2.3% per strategy at the same payouts: adopt for funded (FUNDED_PLAN 'Cushion cap'); code waits on the live cushion source.
- **Open for Claude:** noise-area live fill-latency measurement (needs live fills); Target Guard v2 check (needs a live trade);
  career tailoring (needs the user's background).

## Earlier

- 2026-10-31 to 11-04 details (accounts #2 / #4, VPS feed, kill switch, lab, plans): `archive/brief_history_2026-11.md`;
  before that `archive/brief_history_2026-10.md`.

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
