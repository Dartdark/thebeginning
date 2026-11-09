# To-do list (user's open items)

Started 2026-10-17. Claude ticks items off when you say they're done and reminds you on a schedule (see 'Reminders' at the
bottom). Times are Central (CT).

## This week and next

- [x] (2026-11-04, VB + ONB live replay 10/20-11/04: `analysis/outputs/live_replay_1020_1104_output.txt`; VB 15/15 trades identical, ONB: 10/27 missed (known compile miss), 11/04 entered one bar later (ADX 30.12 at 09:15 = knife-edge), same loss) **Claude: re-run the backtests on the extended NQ data (daily feed, data now to 10/28; 2026-10-29).** Rebuild
  scratch_data (`analysis/build_lab.py`), refresh `analysis/live_panels.py` (bt_cache.json) and the plan benches, and compare
  each live strategy's trades on 10/12-10/28 with what its backtest would have done (first real missed-trade check).

- [ ] **Target Guard v2 (2026-10-29, after one check):** reads the balance from Rithmic, so StartBalance no longer needs
  typing each evening, and it guards the whole account's target. [Apex_Target_Guard_v2](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Apex_Target_Guard_v2.txt)
  ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Apex_Target_Guard_v2.txt)).
  Claude first checks from the logs whether Rithmic's Equity moves with open P&L (next live trade), then tells you to install it.
  **2026-11-08: checked from the 10/30-11/04 ACCT logs: Equity moves with open P&L -> EquityHasOpenPL true; install with the next account.**

- [x] (2026-10-29, user: feed on the chart) **NQ Daily Bar Feed (2026-10-29; VPS, outside market hours, ~5 min):** create `C:\TradingLogs\bars\`; new 1-minute @NQ
  chart (or @MNQ), Exchange time, CME 24h, loaded from 10/05, no strategy; add the indicator
  [NQ_Daily_Bar_Feed](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/tools/exporters/NQ_Daily_Bar_Feed.txt)
  ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/tools/exporters/NQ_Daily_Bar_Feed.txt))
  with `KeepDays` **25** once (fills the gap since the 10/09 export), then set it to 4. Leave the chart open.

- [x] (2026-10-29, user: all done) **Strategy heartbeat (2026-10-29; outside market hours, ~15 min):** paste the updated code into each live strategy and
  compile; read the Output tab for 'compiled successfully' every time (the 10/27 ONB miss). Files (raw):
  [NQ_Vault_Break](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/NQ_Vault_Break.txt),
  [NQ_Overnight_Bias_ADX30](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/NQ_Overnight_Bias_ADX30.txt)
  (or [NQ_Overnight_Bias](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/NQ_Overnight_Bias.txt) if that is the one on the chart),
  [NQ_Expiration_Open_Short](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Expiration_Open_Short.txt);
  [Bridge_Monday_Long_L644NQ](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Bridge_Monday_Long_L644NQ.txt)
  (the Bridge's v2.1 with the heartbeat). The only change is a new input `HeartbeatTag` and a log-only block at the end. Then on each of the 8 charts set
  `HeartbeatTag` = the chart's tag (VB-2, ONB-2, EOS-2, MON_BR-2, VB150, ONB150, EOS150, MON_BR150), check the other inputs
  are unchanged (MULTICHARTS_PITFALLS.md: old inputs survive a paste), auto-trading off / on (Flat).

- [x] (2026-10-29, user: added to all charts) **Apex Chart Monitor (new signal, 2026-10-29; outside market hours, ~10 min):** paste
  [Apex_Chart_Monitor.txt](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Apex_Chart_Monitor.txt)
  ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Apex_Chart_Monitor.txt))
  as a new Signal "Apex Chart Monitor", compile. Add it to each of the 8 live charts: `Tag` = the logger tag (VB-2, ONB-2, EOS-2,
  MON_BR-2, VB150, ONB150, EOS150, MON_BR150), `AccountName` = APEX-681524-02 (the -2 charts) or APEX-681524-03 (the 150
  charts). Auto-trading off / on (Flat). It places no orders. Replaces the Apex Account Check step. Tell Claude about any
  compile error (unsure words: `aiStrategyAuto`, `RecalcLastBarAfter`, `DateTime`, `ComputerDateTime`).

- [x] (2026-10-29, user: charts removed) **Now (found 2026-10-29 by the new live guard): account #1's four charts (VB / ONB / EOS / MON_BR, account -01, blown
  10/26) are still running on the VPS** (VB sent orders on 10/27; thousands of rejection lines). Auto-trading off on each, or
  close them. Details: `live/vps/LIVE_GUARD_PLAN.md`.

- [ ] **Account #3 (2026-10-26):** gear account = APEX-681524-03 on all four #3 charts (ONB, VB, EOS, Bridge), 150K sizes (VB 20, Bridge 5,
  ONB $2,750, EOS $1,250), AA on starting Flat outside a trade window; confirm the first order shows -03 in the Orders tab.

- [ ] **Fri 10/23 (and every Friday): export the weekly MultiCharts reports into `live/`** and tell Claude (it runs
  `analysis/live_vs_backtest.py --all live/` and the drift alarm).
- [x] (2026-10-29: trading since 10/26) **Account #3 (150K No-Activation, $249) trades from Sun 10/25 evening (user, 2026-10-25; the 17:00 CT reopen starts Monday's Apex day).** 150K evaluation stack = the
  combine set x 2.5: Vault Break 20 MNQ, Overnight Bias ADX30 `RiskPerTrade` 2750, Bridge Monday Long 5 MNQ (enters
  **Sunday 19:00 CT**, so it must be on the account by then to trade this week), EOS `RiskPerTrade` 1250 (next 11/20).
  Backtest pass 41.6%. Rules: +$9,000 in 30 days, $4,000 EOD trailing, $2,000 daily loss pause. On pass: switch to the
  150K funded stack (FUNDED_PLAN.md). Add its account number to the logger / live reports.
- [ ] Optional: rerun the ONB ADX30 MultiCharts backtest once with the new code (should be nearly identical).

## Kill switch install (2026-11-01) - DONE 11/01 evening (remote KILL 18:07 -> phone + VPS flag ON 18:10; RESUME -> flag OFF 18:15)
- [x] File check: EL Collections not installed; switched to Windows GetFileAttributesA, compiled on the VPS (2026-11-01).
- [x] Latch test kill_test.ps1: ALL PASS (2026-11-01; 16 checks incl. Codex follow-up cases, 18:3x CT).
- [x] Repasted the 2026-11-01 versions of VB, ONB ADX30, EOS, Bridge: all 8 charts report them (VPS feed 18:05, 2026-11-01).
- [ ] You: Sunday test: `kill.ps1` -> ntfy KILL ACTIVE -> `kill.ps1 -Resume`; then a remote KILL / RESUME via Claude.
      Steps: `live/vps/KILL_SWITCH.md`.
- [x] Claude: `pending_install` removed (2026-11-01).

## Firm view panel (2026-11-01, user yes) - after #4 is set up
- [ ] Claude: once #4's account number is in and 2+ accounts are live, add a 'Firm view' panel to the Apex Live Desk:
      total open risk and combined day P&L across all accounts, worst-case if every open position hits its stop, and a
      flag when several accounts sit near their floors at once (the 'one bet' risk from `analysis/firm_risk_test.py`).
      Also test correlated funded-account blow-ups before running many funded accounts.

## Failover (2026-11-01)
- [ ] You: fill in the table in `live/vps/FAILOVER.md` (VPS dashboard + support, Apex support, a second way into Rithmic)
      and test logging in to R Trader Pro from your own PC once, on a quiet weekend.

## Career (2026-11-01)
- [ ] You: compare `career/resume_section.md` (v1) with `career/resume_section_v2_my_voice.md` (v2), pick what sounds like
      you, then retype the final version **in your own words** (both drafts are Claude-written and carry the text
      watermark; your own rewrite removes it). Then apply to Mercor's Generalist role and Finance Expert pool.
- [ ] You: optional, finish practice 4 (paused at line 4) when you want more code-reading practice.
- [ ] You (LOW PRIORITY, start when you say go): 4-week 'build it yourself' backtester (Karpathy loop, 2026-11-01).
      Wk 1 pick the concept (an honest backtest) · Wk 2 type a ~30-line backtester yourself on one simple rule, Claude
      explains each line first · Wk 3 plant the practice-round bugs (look-ahead, no costs, same-bar) and fix them ·
      Wk 4 record yourself explaining it; add it to `portfolio/` as the piece you wrote. ~1-2 h a week.

## Live guard additions (2026-10-30) - this weekend
- [x] VPS: follow `live/vps/VPS_MAINTENANCE.md` (updates only on Saturdays, weekly Saturday restart, Sunday pre-open routine).
- [x] Repaste the live strategies once (VB, Overnight Bias, EOS, Bridge) from the repo: their heartbeat now stamps a code
      version, and the pre-market check flags any chart running old code. Compile, look for 'compiled successfully'.
- [ ] On the VPS: `cd C:\TradingRepo; git pull` (watchdog: account-floor alarm and Apex-lock hint).
- [ ] On the VPS after `git pull` (2026-10-30 fix): PowerShell `powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\watchdog.ps1`
      once, then `Get-Content C:\TradingLogs\alerts.txt -Tail 5`: no errors = the floor alarm can read the logs.
- [x] Claude: 150K funded whole-number inputs (Codex audit): round the 1.5s down to 1, results unchanged (`FUNDED_PLAN.md`).
- [x] Claude: opposing-position overlap measured (Codex audit step 2): benches overstate risk slightly on 4-17% of days; conservative, no decision changes (`FUNDED_PLAN.md`).
- [x] Claude: personal ladder rebuilt on the 19-piece book (`PORTFOLIO.md`, `analysis/personal_ladder.py`): ~$10.9k = 4 pieces, ~$14.9k = 12 (best ratio), ~$24.3k = all 15 cleared, ~$36k = full 19.
- [x] Claude: replay the Swing Target account benches with the corrected exit kinds -> ties; user reverted both funded swaps 2026-10-31.
- Claude: a new funded account -> `FUNDED` in analysis/account_tools.py (payout tracker); each payout you request -> its list.
- [ ] Claude, once ~20 evaluations have finished: Brier-score the dashboard's pass odds (account_tools.pass_odds at each start)
      against actual pass / fail, to check they aren't too optimistic (idea from the 'Simulate like a quant desk' X article, 10/30).
- [x] (2026-11-05, repo only: heartbeat + HB_Ver in the 9 files, `funded_rules` in expected_setup.json; NOT compiled on the VPS yet, rejected-orders limit is set on each chart when it is made) Claude, before the first funded account (~late Nov): heartbeat + HB_Ver stamp in every funded strategy file that lacks
      them (ONB ML, LDF, NFP, ES MOC, CL fade, Overnight Tick, Dual Thrust, T_ONESIDE, Monday Long); funded floor rules in
      expected_setup.json (150K: trail 4,000, lock 150,100); rejected-orders limit 10 on every funded chart.
- [x] (2026-11-05, code in all 6 files, HB_Ver 2026-11-05; compile on the VPS = the next repaste, not yet done) Claude, with the NEXT planned repaste of the live charts (user, 2026-11-02: "fold it", not a repaste of its own):
      kill-switch file-error tri-state (Codex REVIEW_kill_reply_20261102, medium). KILL file query = -1 with a readable
      parent folder is now read as 'no KILL'; check GetLastError: 2/3 (not found) = no KILL, anything else = UNKNOWN ->
      NoEntry. All 6 kill-switch strategy files; VPS compile + check inputs survive the paste.

## When an account is FUNDED (passes its evaluation) - do before its first funded trade (added 2026-11-08)
- [ ] **You:** paste and compile the funded strategy files (VB_SP, ONB ML, Monday Long, Late-Day Flow, NFP, EOS, CL fade;
      version 2026-11-08); read the Output tab for 'compiled successfully' on each (first compile of `GetRTAccountEquity`
      inside a strategy: if it fails, send Claude the error).
- [ ] **You:** on every funded chart set the cushion guard inputs (`funded_strategies/FUNDED_PLAN.md`, 'Cushion cap'):
      UseCushion true, AccountName = the funded account exactly, StartBalance / TrailDD / LockBalance / CushionRef
      (50K: 50000 / 2000 / 50100 / 1500; 150K: 150000 / 4000 / 150100 / 3000), **PeakSeed = the start balance**.
- [ ] **You, from then on:** after ANY MultiCharts restart or recompile, retype PeakSeed = the highest end-of-day balance so
      far on every funded chart (0 = the strategy takes no trades).
- [ ] **Claude:** first funded day: check from the logs that each entry's size matches the cushion (balance - threshold)
      and the stop cap; add the account to `FUNDED` in analysis/account_tools.py and to expected_setup.json.

## 150K buying plan, Nov-Dec 2026 (user, 2026-10-30; job Nov 10 - Dec 24, $25 x 8 h, paid weekly, all pay to evaluations)
- Note (user 2026-11-08): the job starts Nov 10 and the FIRST payday is likely Mon Nov 17, not Fri Nov 13; dates below shift once the pay schedule is known.
- [ ] Sun Nov 1: buy 150K No-Activation #4 (afternoon, before ~18:00 CT), set up its 4 charts, send Claude the account number.
- [ ] Each payday (Fri Nov 13, 20, 27, Dec 4, 11, 18; last pay ~Dec 24): buy as many $249 150Ks as the pay covers, ONE a day (same-day buys pass/fail together):
      after tax ~3 (5 days/wk) / ~4 (6 days/wk); without tax 4 (5 days) / 4-5 (6 days). Dec 26 pay (3 days): ~2, January starts.
- [ ] **150K evaluations from the next purchase (user 2026-11-09): Vault Break `NumContracts` 20 -> 15 (other VB inputs unchanged) and a
      6th chart, Dual Thrust 2 MNQ** (`funded_strategies/NQ_Dual_Thrust.txt`, the same file as the 150K funded chart: 1-minute MNQ, Exchange
      time = CT, CME 24h session, IOG off, `NumContracts` 2, `HeartbeatTag` DT150 or DT150-<n>). Compile, check 'compiled successfully';
      Claude adds DT150 to expected_setup.json. Quarterly check in the Friday review: back to VB 20 / no DT if VB 20 wins the last 12 months
      (FUNDED_PLAN '150K' section, `analysis/vb_vs_dt_eval.py`).
- [ ] **150K accounts from the next purchase (user 2026-11-08): a 5th chart, Twin Continuation 150K** (`apex_strategies/Twin_Continuation_150K.txt`):
      MNQ 1-minute chart, 24h CME session, Data1 only, Intrabar Order Generation OFF; inputs Qty 2, BO_MaxStopMult 1 (defaults),
      HeartbeatTag TW150 (or TW150-<n> per account); funded accounts also UseCushion true + the cushion inputs (FUNDED_PLAN 'Cushion cap').
      Compile and read the Output tab ('compiled successfully'; first compile of this file). Claude adds TW150 to expected_setup.json.
      Then (outside market hours) run a MultiCharts backtest of this file on NQ 1-minute 2018+ with Qty 1, BO_MaxStopMult 1, and send
      Claude the List of Trades: Claude checks it trade by trade against the Python port (analysis/twin_continuation_test.py, v21=True)
      so the added kill / heartbeat / cushion blocks change no trades.
- [ ] Each new account: 4 charts, account number typed in every strategy's Auto Trading gear, rejected-orders limit 10,
      initial position Flat; send Claude the number (watchdog / dashboard / expected_setup.json) Claude sets its status to "live" in expected_setup.json: that also un-mutes the watchdog's phone alerts (muted 2026-11-05 while no account is live).
- [ ] Stop buying if the drift alarm fires (live clearly below backtest). No more new 50Ks; #2 runs to the end.
- Expected funded 150Ks: after tax ~6 (5 d) / ~8 (6 d) by Dec 31; no tax ~8 (5 d) / ~10 (6 d); +~4-5 more by late January.
- From January: refill slots up to ~20 from payouts.
- 2027 outlook (Claude, 2026-10-30): first payouts ~late Feb-March (each 150K needs +$6,600 and 5 days of $350+; January
  at the earliest); per 150K slot ~$14k in the first 12 months (backtest), ~$10k at 75% edge. ~10 slots: ~$140k backtest /
  ~$100k at 75% / ~$60-70k bad year, nearly all March-December. Plan Jan-Feb with no trading income.
  If the job continues through 2027 (~$850/wk after tax): reach 20 slots by ~February from pay, then switch pay to the
  personal account from ~March: ~$320k backtest / ~$175k at 75% from Apex (median), + personal account ~$30k by autumn.
  Budget simulation (analysis/ramp_budget_test.py; rerun 11/08 with the corrected evaluation floor, 150K pass 33% / 24% at 75% edge):
  job to Dec 24 -> 2027 median ~$237k backtest / ~$72k at 75% (was $252k / $89k);
  13-31% of histories have NO funded account by Dec 31 (then $0 in 2027 without the job). Buy ONE evaluation a day,
  not all on payday (same-day accounts pass or fail together).

## Half-day fixes for two funded strategies (2026-10-25, from Codex's Day Flow Six review; not live yet)

- [ ] **Before the funded accounts trade them:** paste and compile the updated
  [NQ_Monday_Long.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Monday_Long.txt)
  (skips Monday July 3 / Dec 24 early closes) and
  [NQ_NFP_Fade.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_NFP_Fade.txt)
  (skips Good Friday). In 2023 each held a trade through a session halt (Monday Long to 17:05, NFP Fade over the weekend).
  Backtests: one small losing trade removed from each (−$170 / −$85 per NQ). If 'this word has already been defined' appears
  on one of the new Easter variable names, tell Claude.

## ES MOC Follow (funded candidate, 2026-10-17)

- [ ] When a 50K account is funded: T_ONESIDE fade [NQ_T_Oneside_Fade.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_T_Oneside_Fade.txt) on a 1-min MNQ chart (Exchange time, CME 24h, IOG off, Bar Magnifier off), defaults (Qty 1, UseOS false), Trade Logger tag `TOS`; no Relative Strength chart on 50K funded.
- [ ] When funded: ES MOC Follow (IN THE PLAN since 2026-10-17) on a 5-min MES chart, NumContracts 2, Symbol Mapping `@MES -> MESZ6` (roll with MNQ). Vault Break funded: `NumContracts` 2, `FlaggedContracts` 1 (decided 2026-10-17).

## Relative Strength NQ / ES (your new strategy, 2026-10-20: B, checker PASS WITH CONCERNS)

- [ ] When an account is funded: add [NQ_Relative_Strength.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Relative_Strength.txt)
  as a NEW signal on a **1-minute MNQ chart with 1-minute @ES added as Data2** (same feed, Exchange time, first RTH bar 08:31,
  IOG off), 50K: `TradeDir` 1, `NumContracts` 1; 150K: `TradeDir` 0, `NumContracts` 1; Trade Logger tag `RS`.

## Claude: recheck earlier "no gain" calls on speed, bad-case year and blow-ups (user, 2026-10-24)

- [ ] FC 2B, S47 v2, Kusho v9 15:45 (and other recent Apex-plan rejections) judged on median days to the 6th payout,
  the 5th-percentile first year and blown rate, not only 2-year payouts (the cap hides speed gains; Dual Thrust and
  Overnight Tick got in on those). S03 v2 already fails on all of them (Codex: 50K +1 MNQ 1y −$348, 6th payout 274 vs 270
  days, blown +1.7 pt; 150K 235 vs 233 days).

## Overnight TickRSV / VIX (your spec, 2026-10-24: A, MultiCharts-confirmed 97% of nights)

**In the plans since 2026-10-24 (you):** 50K funded 1 MNQ in place of the Monday Long, 150K funded 2 MNQ, personal (in
place of Overnight Anomaly). Nothing to do until a funded account starts; the VIX feed (step 1) is worth setting up early.

- [ ] **1. Daily VIX file on the VPS** (once, outside market hours). 2026-10-24: script in place, first run OK (log 'OK');
  scheduled task (VIXUpdate, weekdays 15:30 / 16:30) and Map ASCII done (symbol **VIX_daily**, folder C:\TradingData\VIX).
  Still to do: Monday 10/26 after 16:30 CT, the log shows `last date 2026-10-26` and the chart's VIX has a 10/26 bar:
  - copy [tools/vix_update.ps1](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/tools/vix_update.ps1)
    ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/tools/vix_update.ps1))
    to `C:\TradingData\VIX\vix_update.ps1` on the VPS;
  - run it once: `powershell -ExecutionPolicy Bypass -File C:\TradingData\VIX\vix_update.ps1`; check
    `C:\TradingData\VIX\vix_update.log` says `OK, last date` (the last trading day);
  - register the scheduled task with the 4 lines at the top of the script (PowerShell as Administrator): weekdays 15:30
    and 16:30 CT;
  - in QuoteManager on the VPS: Map ASCII the file as `VIX_CBOE` (same settings as on your PC).
- [ ] **2. Live check (first evening it runs):** with `PrintDiag` true, the evening line's `VIXdate` must be that day. If it
  shows yesterday, MultiCharts did not reload the mapped file: tell Claude (it still trades, with the previous day's VIX).
- [ ] **3. When a 50K account is funded:** remove the Monday Long chart; add
  [NQ_Overnight_Tick_VIX.txt](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Overnight_Tick_VIX.txt)
  ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Overnight_Tick_VIX.txt))
  on a 5-min MNQ chart (CME 24h, Exchange time, IOG off) with `VIX_CBOE` daily as Data2, `NumContracts` 1 (0 below a
  $1,500 cushion), Trade Logger tag `OTV`. **150K funded:** keep the Monday Long and add it with `NumContracts` 2 (1 below $3,000).


## Journal (Obsidian)

- [ ] From Mon 10/19: a daily note each trading day; run `journal\sync.ps1` and tell Claude "read my journal".

## Cowork (2026-10-19)

- [ ] Install the Claude desktop app, open Cowork, give it only the folders in `cowork/INSTRUCTIONS.md`, and paste that
  file into its instructions. Test it with: "copy this week's MultiCharts reports into C:\TradingVault\live and run journal\sync.ps1".

## Move live trading to the VPS (QuantVPS, 2026-10-19)

Split: VPS = live trading only (MultiCharts live charts, Rithmic, later the copier). Home PC = everything else (local
Claude chores, Obsidian / `C:\TradingVault`, Antigravity / Docker, MultiCharts backtests). Do the move on a weekend or
after 15:59 CT, never with a position open.

- [ ] Reports: each Friday export the weekly MultiCharts reports on the VPS and copy them to the PC (remote-desktop
      copy / paste) into `C:\TradingVault\live\` before 16:47 CT (or later: git on the VPS exporting straight into `live\`).

## New strategies (2026-10-23)
- [ ] **First Friday of each month (next: 11/06): re-export the FC 2B v2 MultiCharts report** (same chart and inputs) into
      `mc_reports/` for the forward log (`agents/codex/FORWARD_LOG.md`). Paper only, not traded.

- [x] (2026-10-29: replaced by the Apex Chart Monitor, which logs NetWorth per chart) **Automatic cushion sizing, step 1: Sun 10/25 after 17:00 CT (market open), ~5 minutes.** The indicator
      `Apex Account Check` is already compiled (2026-10-23). (1) [#1 blown 2026-10-26: skip -01] On the account -01 chart: right-click → Insert Study →
      Indicator → Apex Account Check; Format Study → Inputs → `AccountName` = `APEX-681524-01`. (2) Same on the -02 chart
      with `APEX-681524-02`. (3) Open the PowerLanguage Editor → Output tab (bottom; View → Output Bar if hidden) and leave it
      open. (4) Within a minute: one line per chart with account and NetWorth. Send Claude a screenshot + both Apex dashboard
      balances. NetWorth 0 / no line → fallback (one morning cushion input); same balance on both → wrong account binding.
      Indicator only: places no orders; remove it once read.

## Codex and new research data (2026-10-22)

- [ ] **Export NQ 2017 daytime 1-minute data** (warm-up for the LDF flow-sizing test), on the **home PC** (not the VPS):
  new folder `C:\NQdata2017\`; 1-minute **@NQ** chart, Exchange time zone, CME 24h session, data from **05/01/2017**;
  add the indicator `NQ Bar Exporter` ([tools/exporters/NQ_Bar_Exporter.txt](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/tools/exporters/NQ_Bar_Exporter.txt))
  with Folder `C:\NQdata2017\`, FilePrefix `NQ_1min_`, StartTime 800, EndTime 1515, Decimals 2; wait until the chart finishes;
  copy ONLY `NQ_1min_2017.csv` into `C:\TradingVault\data\` (don't overwrite 2018+), then in PowerShell in `C:\TradingVault`:
  `git pull` · `git add data/NQ_1min_2017.csv` · `git commit -m "NQ 2017 daytime data"` · `git push origin HEAD:claude/nq-trading-strategy-params-5h9d20`
  (sync.ps1 only uploads journal/ and live/), then tell Claude.
- [ ] **Email NYSE** (quote + free sample only, no purchase): to **datasales@nyse.com**, text in
  [agents/claude_evidence/NYSE_QUOTE_EMAIL.md](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/agents/claude_evidence/NYSE_QUOTE_EMAIL.md)
  (copy Subject → Thank you, add your name). List price ~$52k (SPY/Arca) + ~$58k (NYSE) for 2018-26: buy only if a
  SPY-only extract costs a few hundred dollars or the free sample shows a strong signal. Forward their reply to Claude.
- [ ] **Weekly (Fridays, with the reports): export the order history and fresh 1-minute data** for the execution diagnostics:
  (1) VPS MultiCharts, Ctrl+Shift+O → Orders tab → right-click → Export (CSV) → save as `live\orders\YYYYMMDD_orders.csv`
  (or screenshots if there's no export); (2) home PC: NQ Bar Exporter on the 1-minute @NQ chart (as for 2017; Folder
  `C:\NQdata\`, StartTime 800 / EndTime 1515, and FilePrefix `NQ_1min_ON_` with 1516 / 759 for the overnight file),
  copy this year's files into `C:\TradingVault\data\`, then `git add data/NQ_1min_2026.csv data/NQ_1min_ON_2026.csv live` ·
  commit · push (sync.ps1 only adds journal/ and live/).
- [ ] **Send Codex the review message** for the LDF flow-sizing plan (in `agents/codex/STATUS.md`, 'Next message for Codex').

## Swing Target NQ v2 (your file + Codex's test, 2026-10-25: B, personal candidate; not Apex-legal as written)

- [ ] **MultiCharts backtests to run (research, home PC; send each Strategy Performance Report):**
      (a) **Ricochet 1144 target 80** (WATCHLIST #35): `checks/candidates/ricochet_1144/NQ_Ricochet_1144_T80.txt`
      ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/relaxed-bell-dr4os0/checks/candidates/ricochet_1144/NQ_Ricochet_1144_T80.txt)),
      @NQ 5 min, Exchange time, CME 24h, Bar Magnifier 1 min, IOG off, NumContracts 1, 2018 -> now; Claude matches it to python_trades_t80.csv.
      (b) **S30 IBS with `IbsEntry` 0.10** (WATCHLIST #34): `checks/candidates/s30_ibs/S30_IBS.txt` on @NQ **15 min** (the file counts 26 cash bars; 1 min gives 0 trades), back-adjusted continuous, Exchange time, 24h,
      IOG off, `IbsExit` 0.80, ContractQty 1, 2018 -> now (expect ~172 trades).
      (c) **ZT continuation EntryZ 1.25** (WATCHLIST #36): `checks/candidates/zt_continuation/NQ_ZT_Continuation.txt`
      ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/relaxed-bell-dr4os0/checks/candidates/zt_continuation/NQ_ZT_Continuation.txt)),
      @NQ 15 min, Exchange time, CME 24h, IOG off, 1 contract, 2017-06 -> now (warm-up; expect ~600 trades from 2018); Claude matches it to python_trades_z125.csv.
- [ ] **Personal account (when it starts): ZT continuation at 1 MNQ** (user 2026-11-09; watched, WATCHLIST #36): `NQ_ZT_Continuation.txt` on 15-min MNQ, Exchange time, 24h, IOG off, defaults as in the file (EntryZ 1.25, 08:35-14:45). No more than 1 MNQ (corr 0.41 with the book).
- [ ] **Personal account (when it starts): Overnight Tick / VIX at 2 MNQ** (contracts input 1 -> 2; user 2026-11-08). Same chart and code as now.
- [ ] **Personal account (when it starts): PAPERTREND v2 at `Qty` 1** ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/checks/candidates/papertrend/PAPERTREND_v2_claude.txt)), 5-min MNQ, Exchange time, IOG off, `StopATRMult` 2, logger tag `PT`.
- [ ] **Personal account (when it starts): Swing Target v3 at `Qty` 1**, 1-min MNQ, Exchange time, IOG off, ClockShiftMin 0, logger tag `ST` (user 2026-10-25).
- [ ] **When a 50K account is funded:** Vault Break `NumContracts` 2, `FlaggedContracts` 1, no Swing Target. **150K funded:** Dual Thrust `NumContracts` 2, no Swing Target (reverted 2026-10-31, `FUNDED_PLAN.md`).


## Later

- [ ] **Export order-flow + gamma from 2026-07-07 to now** (home PC; `OFB_OrderFlow_Exporter`, `OFB_Gamma_Exporter`,
  `OFB_GexOI_Exporter` in `tools/exporters/`, same charts and settings as before, a few days of overlap). All three files
  in `data/` stop on 07-07. This unblocks Overnight Tick / VIX's backtest (24 live-period MC trades averaged -$280 per NQ)
  and watchlist #1 / #5 / #15. List: `agents/claude_evidence/DATA_NEEDED_CLAUDE.md` (C01) (Claude, 2026-10-31).
- [ ] **Export 1-minute data for NG, ZC and ZS** (natural gas, corn, soybeans), Jan 2018 to now, same way as the CL / ZN files
  (Exchange time, 24-hour session), into `data/` (or `C:\TradingVault`, then sync). Claude then tests the NG storage report
  (Thursdays 9:30 CT) and the USDA WASDE report (monthly, 11:00 CT) on ZC / ZS (2026-10-20,
  `agents/results/MARKET_PROFILES_REVIEW.md`). Also check whether Apex offers NG / ZC / ZS (and the micros).

- [ ] Before the CL Sunday fade goes live: confirm Apex allows MCL on the account.
- [ ] When an account goes funded: paste the funded files (all have the stop guard):
  [ONB ML](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Overnight_Bias_ML.txt),
  [Monday Long](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Monday_Long.txt),
  [Late-Day Flow](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Late_Day_Flow.txt),
  [NFP Fade](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_NFP_Fade.txt),
  [CL Sunday Fade](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/CL_Sunday_Gap_Fade.txt),
  VB SP, EOS.
- [ ] **Thu 12/10 (after the close): roll Symbol Mapping on the VPS** (phone reminder set for 12/10 07:00 CT; all three @MNQ / MNQZ6 lines) `@MNQ (dxFeed) -> MNQH7` (was MNQZ6; before the
  December roll ~12/11), then auto-trading off / on and a 1-MNQ test order per account. Reminder set: 12/10 08:00 CT
  (scheduled-jobs session).
- [ ] **Mid-December gate:** ~40–70 live trades at ≥ 75% of backtest and no ALARM → start scaling (FUNDED_PLAN.md).
- [ ] Optional: add an `OPENAI_API_KEY` to the environment's secrets for a second, different-lab strategy checker.

## Reminders

Claude reminds you every **Sunday and Wednesday at 10:52 CT** (Central). Since 2026-10-20 the reminders run in the
separate session 'Scheduled jobs (journal, Friday review, reminders)', together with the 16:40 CT journal trades and the
Friday review. Say "stop the reminders" to turn them off, or ask for a different schedule.

## VPS status for Claude (2026-11-01)
- [ ] Install the 5-minute status snapshot: steps in [live/vps/VPS_STATUS.md](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/live/vps/VPS_STATUS.md) (git pull, test with -Diag, one schtasks line), then tell Claude "status installed".

## Routing check (2026-11-01)
- [ ] Repaste **Apex Chart Monitor** ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Apex_Chart_Monitor.txt)) in the PowerLanguage Editor, compile (F7); on each of the 8 charts auto-trading off/on (Flat). Then tell Claude: it confirms every chart's real order account from the VPS feed.
- [x] Codex follow-up #3: INSTALLED 2026-11-01 18:45 CT, all 8 charts on 2026-11-02 (VPS feed). Was:: strategies treat any read failure of the KILL file as "no kill". Proposal: also
      check C:\TradingLogs; if the folder can't be read -> no new entries. Next weekend repaste, with a distinct version tag.
