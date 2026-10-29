# New-chat brief (rewritten 2026-10-29): read this first

Opener for a new chat: *"Read `NEW_CHAT_BRIEF.md`, then `CLAUDE.md`, `TODO.md` and `LESSONS.md` in
github.com/Dartdark/thebeginning (branch `claude/nq-trading-strategy-params-5h9d20`) and continue from there."*
Read `MULTICHARTS_PITFALLS.md` before writing MultiCharts code. The full history of this brief (up to 2026-10-28) is in
`archive/brief_history_2026-10.md`; ticked to-dos are in `archive/TODO_done_2026-10.md`.

## Now (2026-10-29)

- **Live accounts (Apex, VPS QuantVPS Chicago, MultiCharts + Rithmic, data dxFeed):**
  - #1 APEX-681524-01 50K evaluation: **blown 2026-10-26** (was ~$398 above its trailing line; plan size kept).
  - #2 APEX-681524-02 50K evaluation: last reported $49,424.18 (10/21), floor ~$48,000. Combine set: VB 8, ONB ADX30
    $1,100, EOS $500, Bridge Monday 2.
  - #3 APEX-681524-03 150K No-Activation from 10/26: combine set x 2.5 (VB 20, ONB $2,750, EOS $1,250, Bridge 5);
    +$9,000 target in 30 days, $4,000 EOD trailing, $2,000 daily loss pause. 10/26: #3's copied charts first sent 150K-size
    orders to #2 (account field on the strategy, see `MULTICHARTS_PITFALLS.md`).
  - Gate ~mid-December: ~40-70 live trades at >= 75% of backtest, no drift alarm -> then +2 x 150K No-Activation a week to 20.
- **Master session (user, 2026-10-28):** `session_01Wk1fPXwvHF5qTjW7bUhYx9` ('★ Master session'). Scheduled jobs run in
  'Scheduled jobs' `session_014DKffATms37kZigaa2xR2P`: journal + dashboard weekdays 16:40 CT, Friday review 16:47 CT,
  to-do reminder Sun/Wed 10:52 CT, MNQ roll reminder 12/10.
- **Dashboard 'Apex Live Desk':** https://claude.ai/artifact/3oqbHWqBFTrUQd95wMmuL8 (accounts, trades, VPS health), data from
  `analysis/dashboard_data.py`. Balances = last Apex balance the user reported + logged gross P&L since.
- **Plans** (details: `funded_strategies/FUNDED_PLAN.md`, `funded_strategies/README.md`, `personal_strategies/PORTFOLIO.md`):
  - Evaluation (combine) set: VB 8 / ONB ADX30 $1,100 / EOS $500 / Bridge 2; backtest pass 50.1% (150K x 2.5: 41.6%).
  - 50K funded: 10 strategies; 2026-10-28 Relative Strength longs -> **T_ONESIDE fade 1 MNQ** (`NQ_T_Oneside_Fade.txt`);
    Overnight Tick / VIX 1 MNQ in place of the Monday Long; Vault Break 1/1 + Swing Target v3 1 when funded.
  - 150K funded: plan x 1.5 + RS 1 + Overnight Tick 2; Swing Target 2 in the slot first given to Dual Thrust (2026-10-25).
  - Personal (from the first payouts, ~Feb 2027): 19 pieces at 1 micro incl. Dual Thrust, Swing Target, PAPERTREND, Kusho v9,
    S47 v2, S30 IBS; capital ladder in `PORTFOLIO.md`; 'Capital-expansion bench' table there.
- **Forward logs (paper, from 10/26):** FC 2B, S47 v2, Kusho v9, S30, BB_MRM (`agents/codex/FORWARD_LOG.md`, frozen bands).
- **Open for Claude:** automatic cushion sizing after the user's Apex Account Check; live-monitoring plan
  (`live/vps/LIVE_GUARD_PLAN.md`); the VPS 'rejected_today' count looks like whole-file counts (10/28: 3,228, last reject
  dated 10/26) and 10/28 had no 08:15 open check-in.
- **Open for the user:** see `TODO.md` 'This week and next' (account #3 charts check, Friday exports into `live/`, VIX file on
  the VPS, FC 2B re-export 11/06, MNQ roll 12/10).
- **Every reply ends with a PushNotification** (CLAUDE.md).

## Who / what

- Algo trader on **Apex** (ignore Topstep): flat by 15:59 CT; 50K: $2,000 EOD trailing (locks at $50,100), combine $3,000
  target, $1,000 daily loss limit. Goal: funded payouts (6 = $13,000 per 50K account), as fast as possible.
- Path: Apex = live test bench and funding source; proven strategies and payouts move to a personal account
  (`DEVELOPMENT_PROCESS.md` 'Strategy lifecycle'). Business plan v2: `reports/Trading_Business_Plan_2026-10-24.pdf`
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

## Rebuilding the data (not in git)

- `pip install numba`, then `python3 analysis/build_lab.py scratch_data` builds g24 / ge / lab; gc / cl pickles build on first
  `load("GC")` / `load("CL")`. Raw 1-minute CSVs in `data/`, MultiCharts reports in `mc_reports/`.
- Continuous contracts are not back-adjusted: roll jumps at 03:32 or 17:01 CT; drop roll bars in new tests.
