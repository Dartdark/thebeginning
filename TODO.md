# To-do list (user's open items)

Started 2026-10-17. Claude ticks items off when you say they're done and reminds you on a schedule (see 'Reminders' at the
bottom). Times are Central (CT).

## This week and next

- [ ] **Claude: re-run the backtests on the extended NQ data (daily feed, data now to 10/28; 2026-10-29).** Rebuild
  scratch_data (`analysis/build_lab.py`), refresh `analysis/live_panels.py` (bt_cache.json) and the plan benches, and compare
  each live strategy's trades on 10/12-10/28 with what its backtest would have done (first real missed-trade check).

- [ ] **Target Guard v2 (2026-10-29, after one check):** reads the balance from Rithmic, so StartBalance no longer needs
  typing each evening, and it guards the whole account's target. [Apex_Target_Guard_v2](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Apex_Target_Guard_v2.txt)
  ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Apex_Target_Guard_v2.txt)).
  Claude first checks from the logs whether Rithmic's Equity moves with open P&L (next live trade), then tells you to install it.

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

## Live guard additions (2026-10-30) - this weekend
- [x] VPS: follow `live/vps/VPS_MAINTENANCE.md` (updates only on Saturdays, weekly Saturday restart, Sunday pre-open routine).
- [x] Repaste the live strategies once (VB, Overnight Bias, EOS, Bridge) from the repo: their heartbeat now stamps a code
      version, and the pre-market check flags any chart running old code. Compile, look for 'compiled successfully'.
- [ ] On the VPS: `cd C:\TradingRepo; git pull` (watchdog: account-floor alarm and Apex-lock hint).
- [ ] On the VPS after `git pull` (2026-10-30 fix): PowerShell `powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\watchdog.ps1`
      once, then `Get-Content C:\TradingLogs\alerts.txt -Tail 5`: no errors = the floor alarm can read the logs.
- [x] Claude: 150K funded whole-number inputs (Codex audit): round the 1.5s down to 1, results unchanged (`FUNDED_PLAN.md`).
- [ ] Claude: update the personal ladder (`PORTFOLIO.md` still says 16-piece core; full book needs ~$35k; tested subsets for smaller starts).
- [x] Claude: replay the Swing Target account benches with the corrected exit kinds -> ties; user reverted both funded swaps 2026-10-31.
- Claude: a new funded account -> `FUNDED` in analysis/account_tools.py (payout tracker); each payout you request -> its list.
- [ ] Claude, once ~20 evaluations have finished: Brier-score the dashboard's pass odds (account_tools.pass_odds at each start)
      against actual pass / fail, to check they aren't too optimistic (idea from the 'Simulate like a quant desk' X article, 10/30).
- [ ] Claude, before the first funded account (~late Nov): heartbeat + HB_Ver stamp in every funded strategy file that lacks
      them (ONB ML, LDF, NFP, ES MOC, CL fade, Overnight Tick, Dual Thrust, T_ONESIDE, Monday Long); funded floor rules in
      expected_setup.json (150K: trail 4,000, lock 150,100); rejected-orders limit 10 on every funded chart.

## 150K buying plan, Nov-Dec 2026 (user, 2026-10-30; job Nov 10 - Dec 24, $25 x 8 h, paid weekly, all pay to evaluations)
- [ ] Sun Nov 1: buy 150K No-Activation #4 (afternoon, before ~18:00 CT), set up its 4 charts, send Claude the account number.
- [ ] Each payday (Fri Nov 13, 20, 27, Dec 4, 11, 18; last pay ~Dec 24): buy as many $249 150Ks as the pay covers, ONE a day (same-day buys pass/fail together):
      after tax ~3 (5 days/wk) / ~4 (6 days/wk); without tax 4 (5 days) / 4-5 (6 days). Dec 26 pay (3 days): ~2, January starts.
- [ ] Each new account: 4 charts, account number typed in every strategy's Auto Trading gear, rejected-orders limit 10,
      initial position Flat; send Claude the number (watchdog / dashboard / expected_setup.json).
- [ ] Stop buying if the drift alarm fires (live clearly below backtest). No more new 50Ks; #2 runs to the end.
- Expected funded 150Ks: after tax ~6 (5 d) / ~8 (6 d) by Dec 31; no tax ~8 (5 d) / ~10 (6 d); +~4-5 more by late January.
- From January: refill slots up to ~20 from payouts.
- 2027 outlook (Claude, 2026-10-30): first payouts ~late Feb-March (each 150K needs +$6,600 and 5 days of $350+; January
  at the earliest); per 150K slot ~$14k in the first 12 months (backtest), ~$10k at 75% edge. ~10 slots: ~$140k backtest /
  ~$100k at 75% / ~$60-70k bad year, nearly all March-December. Plan Jan-Feb with no trading income.
  If the job continues through 2027 (~$850/wk after tax): reach 20 slots by ~February from pay, then switch pay to the
  personal account from ~March: ~$320k backtest / ~$175k at 75% from Apex (median), + personal account ~$30k by autumn.
  Budget simulation (analysis/ramp_budget_test.py, 10/30): job to Dec 24 -> 2027 median ~$252k backtest / ~$89k at 75% (whole contracts, rerun 10/30);
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

- [ ] **Personal account (when it starts): PAPERTREND v2 at `Qty` 1** ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/checks/candidates/papertrend/PAPERTREND_v2_claude.txt)), 5-min MNQ, Exchange time, IOG off, `StopATRMult` 2, logger tag `PT`.
- [ ] **Personal account (when it starts): Swing Target v3 at `Qty` 1**, 1-min MNQ, Exchange time, IOG off, ClockShiftMin 0, logger tag `ST` (user 2026-10-25).
- [ ] **When a 50K account is funded:** Vault Break `NumContracts` 2, `FlaggedContracts` 1, no Swing Target. **150K funded:** Dual Thrust `Qty` 2, no Swing Target (reverted 2026-10-31, `FUNDED_PLAN.md`).


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
