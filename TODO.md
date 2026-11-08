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
- [ ] Claude: replay the Swing Target account benches with the corrected exit kinds (expected: ST adoption only stronger).
- Claude: a new funded account -> `FUNDED` in analysis/account_tools.py (payout tracker); each payout you request -> its list.
- [ ] Claude, once ~20 evaluations have finished: Brier-score the dashboard's pass odds (account_tools.pass_odds at each start)
      against actual pass / fail, to check they aren't too optimistic (idea from the 'Simulate like a quant desk' X article, 10/30).
- [ ] Claude, before the first funded account (~late Nov): heartbeat + HB_Ver stamp in every funded strategy file that lacks
      them (ONB ML, LDF, NFP, ES MOC, CL fade, Overnight Tick, Swing Target, T_ONESIDE, Monday Long); funded floor rules in
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
- [ ] **When a 50K account is funded:** Vault Break `NumContracts` 1 (was 2), `FlaggedContracts` 1, + Swing Target v3 `Qty` 1. **150K funded:** Swing Target `Qty` 2 instead of Dual Thrust (`FUNDED_PLAN.md`).


## Later

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

## Promising strategies awaiting verification (user, 2026-10-27)

- [ ] **KSE Sentinel / PSX trend continuation — NEEDS RULES AND VALIDATION (uploaded SSRN7102818).**
  Low-priority personal-market lead only. Author claims 1,009 trades, PF 2.51, Sharpe 2.08,
  PKR CAGR 7.47% but USD CAGR −2.96%; unverified. Exact EMA/regime/exit/sizing rules withheld;
  DSR left as a placeholder, archive/forward outcomes not supplied. Public strategy shortlink
  returned HTTP 403; bounded title/link search found no reproducible specification. Next only
  with free new inputs: frozen rules/code plus a small dated trade/blocked-signal and cost/FX
  ledger before acquiring full PSX point-in-time history or admitting a return experiment.
  Do not invent settings, use an opaque API as verification, or adapt to NQ/ES automatically.
  [Review](agents/codex/results/kse_sentinel_7102818_review.md) ·
  [Data register](agents/codex/DATA_NEEDED.md#kse-sentinel--psx-source-rule-gate-uploaded-ssrn7102818).

- [ ] **International Buffett-indicator allocation — NEEDS DATA AND SPECIFICATION (SSRN4071039).**
  Conditional low-priority personal long-term lead: country-wise matured ten-year-return regressions on
  log(market-cap/GDP), equal-weight top7 of14, reset everyten years. Source composite10.5% versus9.5%,
  Sharpe0.57 versus0.49, DD−52.1%; not independently reproduced. Source waits for label maturity but
  quarter-end GDP publication/vintages are unverified. Need1973–2019 quarterly total-market cap, GDP/RI/
  rates and native base-currency/FX/composite-cost ledger. OECD/World Bank free probes proxy403; annual
  proxy is nonmatching. Next: one country/formation identity, released-GDP/mature-label/cash reconciliation,
  then coverage/power and committed protocol. No intraday/NQ/crash-timing substitute or new return trial.
  [Review](agents/codex/results/buffett_international_4071039_review.md) ·
  [Evidence](agents/codex/evidence/buffett_international_4071039.md) · [Data register](agents/codex/DATA_NEEDED.md).

- [ ] **Diversified delta-straddle trend — NEEDS DATA AND SPECIFICATION (SSRN4677166).**
  User-requested offline signal/whole-lot planner now built:34synthetic mechanical checks pass; no return backtest
  or personal allocation established. Native replay/cash adapter still requires the matching data below.
  Conditional low-priority personal lead: explicit smooth t-stat signal,32/64/126/252/504-day blend and41-market
  risk-scaled portfolio. Author reports9.27%annual/Sharpe1.03/13.60%DD, not independently reproduced; fast4/8/16-day
  version loses after modeled costs. Need full identified futures/FX total-return/carry panel,504-session warm-up,
  native rolls/cash/collateral/margins, causal liquidity weights and exact execution/no-trade-band conventions.
  Owned/free replication searches did not admit a matching panel. Printed AR(1)t adjustment and fast DD below−100%
  require reconciliation. Next only on new inputs: one rebalance/roll/cash interval, then coverage/cost/power gate
  before committed returns. No NQ subset, intraday port, failed-family rescue or allocation; multiday holds fail Apex.
  [Review](agents/codex/results/delta_straddle_4677166_review.md) · [Code/test report](agents/codex/results/delta_straddle_4677166_build.md) ·
  [Data gate](agents/codex/inputs/delta_straddle_4677166/free_data_gate.md).

- [ ] **SPY “Beat the Market” replication audit — conditional low-priority NEEDS DATA (SSRN7323419).**
  Author closely replicates the historical SPY noise-band/VWAP result, but reports−8.1%September2025–August2026;
  final overlays selected after80adaptive SPY alternatives, no clean holdout, and fail to improve QQQ Sharpe.
  Native SPY minute/dividend/calendar/cash/borrow data and authenticated replication engine/trial package missing
  after bounded free checks. No new planner built. Existing NQ/ES family failures are retained, not revived.
  Next only on genuinely new inputs: one causal formation/dividend/early-close/fill cash reconciliation, then
  coverage/cost gate before economic protocol. No personal or Apex allocation.
  [Review](agents/codex/results/delgado_7323419_review.md) · [D55 data needs](agents/codex/DATA_NEEDED.md).

- [ ] **ETF-flow stock selection — NEEDS DATA AND SPECIFICATION (SSRN7517178).**
  Conditional personal-stock lead: monthly top/bottom50 using z12−z3 of thematic/sector ETF-induced pressure.
  Authors report17.57%annualized/Sharpe0.98 design; later Jan–Aug2026 earns8.54% versus16.82% benchmark,
  Sharpe0.54 versus2.01. Source-only, not net verified. Need as-of NAV/shares/splits, historical holdings/category,
  stock market caps/membership and borrow/financing/cost clocks. Public Trackinsight/SEC checks proxy403;
  current ETF prices/holdings are not matching historical inputs. Next: one formation month and availability/
  stock-pressure/cash ledger without returns, then coverage/power and committed protocol. Zero new return trials,
  NQ/ES substitute or current allocation. [Review](agents/codex/results/etf_flows_7517178.md) ·
  [Evidence](agents/codex/evidence/etf_flows_7517178.md) · [Data register](agents/codex/DATA_NEEDED.md).

- [ ] **Lagged-volume intraday risk sizing — conditional SOURCE/EXECUTION WATCH (2026-11-06), SSRN5795584.**
  Specific merit and unreplicated author results: [record](agents/codex/research/scout/records/5795584.json).
  Owned price/volume fields overlap; this does not reopen prior generic volatility-targeting failures.
  Prerequisites: causal preprocessing, observed paths and native costs/integer exposure. Smallest next check,
  only with genuinely new matching evidence: reconcile one available-at forecast-to-position transition without
  imputing prices or assuming fractional fills. Park and continue discovery; no allocation or TEST admission.
  [D53](agents/codex/DATA_NEEDED.md#2026-11-06-volume-conditioned-risk-watch),
  [checkpoint](agents/codex/results/scout_owned_source_20261106.md).

- [ ] **Signed Treasury jump-risk premium — conditional personal WATCH / NEEDS DATA (2026-11-05), SSRN1716759.**
  Merit: a specific countercyclical jump-risk predictor; the author abstract reports OOS Sharpe0.52 and the related
  Tilburg thesis Table18 reports IR0.52 for2003–2009. Neither is our native ZN result. Monthly duration-normalized
  JP Morgan index bets/CRSP excess-return targets do not establish an Apex intraday strategy. Need authenticated
  published rules/version parity, causal jump detection/initialization and12/24-month formation, five-year
  normalization/staggered-bet warm-up, source target/roll/duration reconciliation and actual integer sizing/costs.
  Own named ZN exports start2017; no complete pre2018warm-up/native ledger is established. A bounded free check
  found a public project advertising older ZN data, but its README explicitly excludes proprietary raw inputs.
  Smallest later check only with genuinely new matching source/data: reconcile one fully past-only formation,
  target and dated-contract position before assessing complete2018–22power or preregistering returns. Do not
  shorten holds, omit overnights, impute jumps or recycle news-fade definitions. Park and continue discovery.
  [D52](agents/codex/DATA_NEEDED.md#2026-11-05-treasury-jump-risk-watch),
  [record](agents/codex/research/scout/records/1716759.json),
  [source checkpoint](agents/codex/results/scout_owned_source_20261105.md).

- [ ] **BTC asset-manager option positioning — SOURCE/DATA CHECK (Shen/Li/Luo2026).**
  Merit: published CME-specific second-week-ahead predictive association beyond futures positioning, attributed to
  non-momentum risk-transfer/inventory response; net strategy profit unverified. Need full residual/target rules,
  matching option/futures positions, actual Friday/backlog availability and native costs. OwnTFFarchives are
  futures-only. Bounded free combined-data request and manuscript reader were403; park, no unchanged retries,
  paid access or user request. Smallest next check is an authenticated full source plus one matching released row.
  [Metadata/acquisition record](agents/codex/results/scout_expanded_data_intake_20261101.md), data registerD46.

- [ ] **COT top-four concentration -> gold — SOURCE/CAUSAL-CLOCK CHECK (Liu et al.2023).**
  Merit: author Table5links CL top-four net concentration to GC(coefficient0.0457,SE0.0154); specific cross-market
  information distinct from previously rejected dealer/nonreportable ranks. Owned COTheaders contain the fields;
  net strategy profit is unverified. Smallest check: resolve`r[t+4]`target alignment and actual Friday/backlog
  availability, then certify GC/CLhistory/rolls/costs before any bounded preregistration. No Tuesday look-ahead,
  assumed four-week hold or shifted-horizon rescue. No return reservation. Move on while source specifics are absent.
  [Selected-source assessment](agents/codex/results/scout_owned_data_discovery_20261031.md).

- [ ] **Cross-calendar overlap and overnight continuation — SOURCE SETTINGS CHECK, not TEST (SSRN6818821).**
  Merit: specific interaction among scheduled flows, rather than another single-family timing rule; author reports
  −5.03bp/SD in sign-adjusted reversal,t−2.61,2016–24. Not verified net profit;2006–22source result is weak.
  Prerequisites: complete source/exact footprint intensities, accurate calendars, causal entry clock and native costs.
  Smallest next check: reconcile source calendar identities and obtain fixed constants before considering one
  registered ES/NQ adaptation. Final cash-close direction cannot earn a guaranteed same-close fill. No quarter-end
  reversal rescue, no return reservation, no repeated404or paid-data loop; continue other owned-data leads meanwhile.
  [Selected-section assessment](agents/codex/results/scout_owned_data_discovery_20261031.md).

**Data shopping/export register:** [Research leads awaiting data](agents/codex/DATA_NEEDED.md) consolidates previous
data-blocked leads, exact missing inputs, partial acquisitions, next checks and superseded requests. Maintain it for future
worthwhile NEEDS DATA leads. Acquisition preference: **free sources only**; a listing does not authorize a return test.

- [x] **NG storage announcement short — CLOSED: DON'T TEST at source gate (SSRN3575861).**
  Full paper received/read. Table8's After2011 panel reports −0.90% after bid/ask costs (Sharpe−0.16),
  −0.97% including funding (−0.17), versus the full-sample headline +12.01%/1.76. Author results, not reproduced.
  This replaces the earlier summary-only promising/data-blocked status. No calendar/side/filter rescue or new
  return trial; no portfolio place earned. The corrected2,959,522-bar NG exports remain archived for distinct
  justified research; no further export/PDF/metadata request for this rule. Generic market inventory remains D12.
  [Full-source review](agents/codex/results/ng_3575861_full_review_20261030.md) ·
  [Evidence gate](agents/codex/evidence/ng_3575861_20261030.md) ·
  [Corrected data intake](agents/codex/results/ng_corrected_intake_20261031.md).

- [ ] **Bitcoin spot/inverse-futures utility allocation — CODE BUILT / NEEDS MATCHING DATA AND SPECIFICATION (SSRN3441913).**
  Conditional personal-account research: explicit utility-allocation formulas; authors report Sharpe4.86–5.07
  versus spot4.40 on111days in2019, not independently reproduced net returns. Main formula/payoff audit passes;
  AppendixB.2 has a confirmed sign discrepancy. Both calibrated legs are long BTC, not a neutral hedge.
  Need exact source BitMEX contract IDs and spot/index clocks, executable spot, rebalancing, native lots,
  collateral/mark liquidation and costs. Four public API probes hit network proxy403; owned CME/spot bars
  are not matching inverse inputs. Next step only with new matching inputs: reconcile one native BTC/USD
  contract/spot interval and availability clock, then committed coverage/cost/power gates before returns.
  No new economic trial, Apex placement, modern perpetual substitution or allocation.
  [Offline strategy/review packet](agents/codex/results/bitcoin_inverse_3441913_build.md) built at user request;20 synthetic tests
  pass for native lots, reciprocal BTC accounting, costs and timing guards. Pooled-wallet execution assumptions remain;
  independent Claude review and empirical verification pending.
  [Review](agents/codex/results/bitcoin_inverse_3441913_review.md) ·
  [Evidence](agents/codex/evidence/bitcoin_inverse_3441913.md).

- [ ] **FOMC short nearby VX — NEEDS DATA AND SPECIFICATION (SSRN2544445).**
  Conditional personal-research lead: scheduled uncertainty-release mechanism; author claims34selected2010–14trades,
  +28.68%total/Sharpe1.085/0.7%DD, not independently reproduced. Need individual-contract intradayVXprices/quotes,
  event-clock eras, source11:00timezone and the chart-only`min-Maturity=5`units/contract-selection rule. Printed Eq3
  negative leverage reverses the sign; screenshotpositive3.5matches the short17example. Cboe/FirstRate/Portara products
  found, but public sample attempts yielded no admitted panel. Follow-up2026-10-31: direct sample download proxy-blocked;
  advertised FinzData$49/market and Portara$220 special verified on pricing pages, delivered quality unverified/no purchase.
  User chose **free sources only**; no matching free panel acquired, paid paths excluded.
  [Acquisition receipt](agents/codex/results/fomc_vx_data_acquisition.md). Smallest next check
  when matching inputs/clarification arrive: reconcile one dated event/contract/clock/stop, then committed design/cost/power
  screen. No daily/spotVIXorESproxy, parameter rescue, plan placement or return trial. This is separate from the failed
  naked Calvados component. [Review](agents/codex/results/fomc_vx_2544445_review.md) ·
  [Evidence](agents/codex/evidence/fomc_vx_2544445.md) · [Data gate](agents/codex/inputs/fomc_vx_2544445/data_gate.md).

- [ ] **Extreme positive firm-news sentiment — low-priority personal-stock lead / NEEDS DATA AND RULES (SSRN2631135).**
  Merit: nonprice company-information feature with reported2007–14long trend mean16.90%,Sharpe0.64;
  source DD49.09%, unspecified costs and test-period cutoff scanning limit that claim. No independent net edge.
  Need lawful TRNA probabilities/relevance with entity/receipt/model vintages, historical equity universe/sectors,
  corporate-action cash ledgers, exact weights and position lifecycle. Actual owned/exact-title/GitHub/official
  LSEG checks found documentation and manuscript records, not a full free admitted news panel.
  Smallest next check when matching inputs arrive: audit an entitled historical sample and clocks, freeze a
  training-only protocol, then cheap design screen. No NQ substitute, Apex placement or new return trial.
  Python research code is feasible with those inputs; code feasibility is not profitability.
  [Review](agents/codex/results/news_sentiment_2631135_20261031.md) · [Evidence](agents/codex/evidence/news_sentiment_2631135_20261031.md).


- [ ] **ANANTA interest-rate differential momentum — NEEDS DATA AND SPECIFICATION (SSRN 2419243).**
  Low-priority personal FX lead: two-year swap-rate differential changes across eleven currencies, rebalanced
  at London 18:00 and New York 17:00. Author reports net 3.5/5 bp per dollar traded in 2003–2013; unverified.
  Literal pseudocode reverses its verbal rate-momentum direction; percentile, zero-divisor and gross-sizing
  rules need clarification. A declared synthetic interpretation exceeds the stated 20% concentration bound.
  Need synchronized original-vintage swap/FX snapshots, availability/fill clocks, financing and native costs.
  Owned data and bounded BOE/ICE/CME checks did not provide the exact panel. Resume only with genuinely new
  matching inputs/source clarification: reconcile one two-clock day and cashflows before a committed data/cost
  gate. Continuous 6E, daily policy rates or OIS proxies are not an exact replication. No paid data or returns
  attempted; no Apex adaptation, allocation or tier promotion.
  [Review](agents/codex/results/ananta_2419243_review.md) · [Evidence](agents/codex/evidence/ananta_2419243.md).


- [ ] **Monthly low-frequency FX momentum — NEEDS DATA / SOURCE CONVENTIONS (SSRN 1259661; 2026-10-30).**
  Lower-priority personal lead: recursively fitted HP trend (monthly penalty 14,400), then MA(1,2) on the trend.
  Author's 1993–2008 basket Sharpe 0.76 versus raw MA 0.41; carry included, costs ignored, not independently
  reproduced. Public Fed-mirror daily FX panel and metadata acquired; euro starts 1999, source carry/pre-euro
  history and exact basket/quote/endpoint conventions missing. Kernel bandwidth units also unresolved.
  Resume only on genuinely new matching inputs or author clarification: reconcile one dated month and signal
  vintage, then coverage/power/cost gate before a committed bounded HP/raw-MA design test. Monthly holds fail
  all four Apex homes. No spot-only/subset/intraday proxy, return trial or allocation admitted.
  [Review](agents/codex/results/fx_low_frequency_1259661_review.md) · [Evidence](agents/codex/evidence/fx_low_frequency_1259661.md).

- [x] **Corrected stock + intraday MNQ RL selectors — TESTED / REJECT DESIGN (SSRN 3690996; 2026-10-30).**
  User requested both corrected adaptations after the original-source audit. Frozen quarterly PPO/A2C/DDPG selector:
  stocks2018–2019 lost$120 on$10,000 versus equal-weight+$1,790; fixed1MNQ2018–2022 made$2,090 versus
  long-control+$5,404, and lost$5,188 at doubled costs. Both fail their prespecified advancement gates; no earned
  personal,50K/150K evaluation or funded allocation. Later periods/seeds/portfolio tests were not earned.
  Integer positions, later-bar fills, causal features and reconciled ledgers are implemented in a new bounded protocol;
  the original paper's13%/Sharpe1.30 remain unreplicated. Static28-stock/no-dividend panel ends2020; futures condition
  on complete observed NQ sessions as MNQ proxies. No rescue tuning or live changes.
  [Build/results](agents/codex/results/rl3690996_build_20261030.md) · [Code guide](agents/codex/code/rl3690996/README.md) ·
  [Original-source review](agents/codex/results/rl_ensemble_3690996_20261030.md).
  Related [SSRN 7013523 upload review](agents/codex/results/ssrn_7013523_review_20261030.md):30/30 table cells
  match the original; that source review adds no independent return test. The corrected builds above are new protocols.


- [ ] **WASDE pre-release futures/options volume — NEEDS DATA AND SPECIFICATION (SSRN 4841490; 2026-10-30).**
  Lower-priority personal-account lead: author reports positive futures-volume and negative options-volume
  associations with subsequent 5–20-day agricultural futures returns (1995–2018); no net strategy independently
  reproduced. Need dated agricultural futures/options volumes, option-underlying/expiry mapping, paired basis
  inputs, vintaged forecasts, publication clocks and exact pre-event aggregation. Day-zero return inclusion,
  retrospective normalization and forecast-revision versus consensus-surprise distinctions need resolution.
  Owned filename census found no matching panel; public USDA/CME checks returned proxy tunnel 403.
  Resume only with genuinely new matching inputs/specification: reconcile one report/contract without returns,
  then a committed coverage/cost/power gate. Source multiday holdings fail all four Apex homes; no NQ proxy,
  intraday adaptation, return trial, paid acquisition or allocation is earned.
  [Review](agents/codex/results/wasde_volume_4841490_review.md) · [Evidence](agents/codex/evidence/wasde_volume_4841490.md).

- [ ] **Commodity-index roll calendar spreads — conditional personal research / NEEDS SPECIFICATION AND DATA (SSRN2942340).**
  Till/Eagleeye2017 identifies predictable sell-front/buy-deferred index demand and anticipatory spreads, but supplies
  no net backtest or exact dated protocol. Distinct from weekly basis reversal; do not recycle failed outright CL
  timing proxies (prior t1.4 and GSCI/BCOM t0.5/0.7). Need historical/current index rules and weights, actual paired
  commodity maturities, synchronized prices, native both-leg costs and delivery/margin handling. Smallest next check
  when matching evidence arrives: reconcile one specified index roll and its two-leg cashflows, then complete the
  evidence/preregistration gate before returns. Source brings no new dataset; existing acquisition blockers remain.
  Multiday description earns no Apex placement; personal contribution is unverified. Zero new trials.
  [Review](agents/codex/results/till_2942340_20261031.md) · [Evidence](agents/codex/evidence/till_2942340_20261031.md).
  [Actual acquisition follow-up](agents/codex/results/commodity_roll_data_20261031.md): downloaded pinned public
  WHEAT/WHEAT_mini multi-maturity files and read2018/current roll documentation. Standard WHEAT holds annual
  December contracts, not the required nearby pair. Mini prices have delivery-cycle identities but missingness,
  clock and native identity remain unverified. Complete free2018–22paired ZW panel is not admitted; zero returns.


- [ ] **Monthly commodity skewness — OFFLINE CODE BUILT / NEEDS FULL PANEL (SSRN 3507947; 2026-10-30).**
  Personal-account lead: monthly long four lowest-skew / short four highest-skew across 22 commodities.
  Authors report 6.67% annual return after modeled costs and -0.32 equity correlation; neither is independently
  reproduced or established for our portfolio. Offline planner, schema and synthetic checks built at the user's request.
  Need identified full-universe daily contracts/settlements, return/roll conventions and native cost/cash accounting.
  Smallest next check: map those inputs to the packet and reconcile one formation/roll month before a separately
  committed return test; do not substitute CL/GC or an NQ daily-flat rule. No economic trials or plan allocation.
  [Source review](agents/codex/results/ssrn_3507947_review_20261030.md) ·
  [Code/checkpoint](agents/codex/results/commodity_skew_build_20261030.md).

  **Free-data follow-up2026-11-01:** downloaded a pinned84-series daily reference panel plus separate OATIES/OJ
  multiple-price histories. Twenty of the22economic names occur in the reference panel; the two extra files do
  not make a homogeneous/native22-market input. Multiple timestamps, missing cells, different rolls, receipt clocks,
  costs and source settings remain unadmitted. No splicing, reduced-universe sort or return test. Reconcile one
  complete formation/roll month before returns; do not redownload unchanged sources each cycle.
  [Intake/source mapping](agents/codex/results/scout_expanded_data_intake_20261101.md).

- [ ] **FX carry/trend multi-strategy — NEEDS SOURCE CLARIFICATION / DATA (SSRN 3322717; reviewed 2026-10-30).**
  Personal-account research only, low priority. Merit: author reports Sharpe 0.88 versus 0.55 for its best single
  signal across eight FX futures; not independently reproduced or established after executable costs.
  Source prose misidentifies the winning allocator; performance-pruning dates, exact signal/solver definitions,
  execution clocks and roll/collateral accounting are unresolved. Only 6E of the source futures is owned.
  Smallest next check when matching evidence arrives: author rules/code and one dated futures/yield/rebalance/roll
  month reconciled before any design test. No invented NQ or daily-flat variant, return trial, Apex placement or allocation.
  [Review](agents/codex/results/fx_multistrategy_3322717.md) · [Evidence](agents/codex/evidence/fx_multistrategy_3322717.md).

**Standing rule:** when a reviewed strategy has documented merits but its results or implementation are not yet verified,
add it here for later review. Record the merit, what is missing, the smallest next check and the source review; merge
duplicates. Keep reported results labelled as claims. Missing information alone does not make a strategy promising.
A queue entry does not add it to a trading plan or start a backtest; review when prerequisites arrive or the user prioritizes it.

- [ ] **Calvados 2.0 preferred VX + ES hedge — conditional personal research / unverified (2026-10-30).**
  Merit: specific dated-volatility basis normalization and an equity hedge; author claims +273.7% gross with 11.3% DD
  in selected 2010–14 leveraged simulations. These are not verified current returns. The separately registered naked
  component FAILED 2018–22: one VX, 58 trades, gross −$2,980 / net −$9,360, marked DD $18,385; no later/account stages.
  Do not revive that component or claim its failure falsifies the untested hedge. Preferred-source work needs a verified
  dated ES chain/roll cashflows, additive hedge-equation correction, explicit adjustment clock and actual integer sizes;
  one VX often maps to less than one ES, and prelaunch MES/VXM histories must not be invented. Smallest next check:
  authenticate vendor/price type and clock in the newly found public quarterly ES archive, audit complete paired prices,
  then freeze the hedge protocol before a separately committed test. Three full samples were inspected; this is an
  actual data lead, not a claim that no free ES chain exists. [ES gate](agents/codex/inputs/calvados_2379985_20261030/es_hedge_gate/es_hedge_feasibility.md).
  Multiday VX is ineligible
  for all four Apex homes as written; any personal addition/replacement must earn historical validation and native
  account/margin comparison. [Review/results](agents/codex/results/calvados_2379985_20261030.md) ·
  [Evidence](agents/codex/evidence/calvados_2379985_20261030.md) ·
  [Acquisition](agents/codex/inputs/calvados_2379985_20261030/acquisition.md).

- [ ] **Nocturne — verify archived assumed replay only; NOT ADMITTED (2026-10-30).**
  Merit: user-authorized R²/target/reentry assumptions produce1085design trades,+$8.75/MNQ,PF1.38,
  all5years positive, compared with+$4.32withoutR². These are conditional2018–22screen results, not independent
  reproduction or portfolio contribution. Advancement FAILS: skipped nights t−0.95and matched random-keep joint
  win89.9%miss preregistered−2/95%requirements. No2023+or accounts opened; no stop/threshold rescue project.
  Source PDF also reports millions of configurations, weak finalOOSand fragile nearby settings; full author rules
  remain withheld. Smallest next check: Claude independently verifies the archived assumed implementation,
  cost/night accounting and failed gates. No place in personal,50K/150Kevaluation or50K/150Kfunded plans is earned.
  [Results](agents/codex/results/nocturne_20261030.md) · [Frozen assumptions](agents/codex/plans/nocturne_20261030.md).

- [ ] **Monthly commodity momentum/carry double-sort — PARKED / NEEDS PAIRED DATA AND NAV AUDIT (2026-10-31), SSRN 2614241.**
  Specific merit: prior-month momentum selects eight winners/eight losers; curve signal `ln(front/second)` narrows
  to four longs/four shorts held one month. Proposed trend plus inventory/hedging premia may diversify a personal
  futures book; that benefit is unmeasured. The December 2012 thesis claims 20.22% annual excess return/24.91%vol
  over February 1979–October 2011 at 2x gross, before costs. Its $7.63 endpoint matches additive return accumulation,
  not demonstrated compounded NAV; no author result independently reproduced. This specifies the broad commodity
  storage/momentum family already noted in TIER_LIST; it does not reopen the failed CL/GC hedging-pressure trial.
  Need a point-in-time broad commodity first/second-contract panel, executable clocks, roll/cash/short-weight rules,
  native costs and integer sizing. Owned CL/GC OHLCV and the bounded free check do not supply these inputs.
  Smallest next check **when genuinely new matching inputs arrive**: reconcile one formation/roll month with
  identified maturities and self-financing quantities/cash, then a no-return 2018–22 coverage/power census.
  Low-priority personal research only; monthly holds fail all four Apex homes as written. No proxy, stop-overlay
  rescue, recurring unchanged acquisition loop, return trial or allocation. Separate rule from weekly basis reversal
  below, sharing its paired-data prerequisite. Risk-method findings retained in execution reference E38.
  [Full-source review](agents/codex/results/rad_double_sort_review_20261031.md) ·
  [Evidence](agents/codex/evidence/rad_double_sort_20261031.md).
  [Code-building checkpoint](agents/codex/results/rad_double_sort_build_20261031.md): offline monthly selector,
  integer reference allocation and strict input checks built;23 synthetic mechanics cases pass. No real-data
  return/account result; source/data/accounting prerequisites remain unchanged.

- [ ] **Weekly commodity basis reversal — NEEDS FULL TEXT / PAIRED DATA (2026-10-29), SSRN5250499.**
  Merit: specific adjacent-maturity relative-return reversal claimed in the primary abstract, distinct from an
  outright price reversal; public secondary code defines a delayed weekly two-leg implementation. No net return
  or account benefit independently verified. Source mechanism is differential information sensitivity/limited arbitrage,
  not a verified forced order. Primary full rules and version remain unread; secondary curves are gross and depend on
  a private engine/data service. Smallest next check: obtain lawful primary text and one identified front/deferred
  contract sample, verify expiry/settlement availability and integer versus equal-dollar exposure before2018–22 census.
  Need complete paired history, native both-leg costs, rolls and executable prices; no imputed second month.
  Weekly holding is ineligible for Apex as described; personal research only pending evidence, preregistration and tests.
  [Source/strategy audit](agents/codex/results/scout_spread_strategy_feasibility_20261029.md) ·
  [Evidence](agents/codex/evidence/scout_basis_reversal_20261029.md). No return trial started.
  [Build checkpoint](agents/codex/results/weekly_basis_reversal_build_20261029.md): Python signal prototype created;
  14 synthetic engineering checks pass. Real-data rules/sizing/costs remain unresolved; no profitability or portfolio
  test. Source/data blockers stay visible; the draft is not an admitted preregistration.

- [ ] **Clock-aware Treasury index-duration demand — WATCH / NEEDS FULL TEXT (2026-10-29), SSRN7601879.**
  Specific merit: Bloomberg independently documents the U.S. index snapshot moving14:00→15:00CT effective2021-01-14;
  the earlier failed ZN month-end A/B/C protocols exit13:59CT. Authors claim snapshot-centered price pressure,
  stronger with forecast duration extensions; their1.19bp versus0.07bp abstract figures are not verified net returns.
  Preserve the old negative A result (−$31/ZN net, t−1.4;2023+−$79.7); do not repeat unconditional month-end longs or tune its exit.
  Smallest next check: obtain/pin lawful full text, extract exact source clocks and perform a no-return event/data census.
  Need dated holiday/early-close regimes, contracts/rolls, pre-entry duration-forecast vintages and reconciled native costs.
  Complete source/clock/data/power gates before TEST and any new bounded preregistration. No return trial started.
  [Review](agents/codex/results/scout_buying_duration_20261029.md) · [Evidence](agents/codex/evidence/scout_buying_duration_20261029.md).
  [Testability follow-up](agents/codex/results/scout_7601879_testability_20261029.md): source still unavailable after
  author/institution/replication searches. Three isolated forecast examples do not form a point-in-time panel.
  Timestamp-only census confirms60 observed monthly endpoints, not60 authoritative events; November2020 demonstrates
  that selecting the last available data date can select the wrong day. No returns or rescue protocol opened.
  [Acquisition](agents/codex/results/scout_duration_acquisition_20261029.md) saved4 provider rows (only3/60 design months)
  and3 separate institutional references; original availability remains unknown. Missing months were retained, not filled.

- [ ] **Treasury auctions × next-day macro-announcement FX — WATCH / NEEDS FULL TEXT (2026-10-29), SSRN5207418.**
  Merit: a specific scheduled interaction with direct FX transmission; authors claim roughly8bp foreign-currency
  appreciation on release days following auctions, versus near zero on other release days. Not independently
  verified, euro-specific or established net of costs. Different from the already weak same-day6E auction short;
  retain that negative/weak cost evidence and audit overlap with the existing personal6E package.
  Smallest next check: obtain/pin the full April2025 or March2026 version and extract exact currencies, clocks,
  auction/release definitions and costs before selecting rules. Owned6E minutes/auction records and free Fed/BEA
  calendar sources establish partial feasibility; complete as-of releases and contract/roll provenance remain missing.
  No realized price-spike event proxy, silently truncated overnight window or return trial is authorized by this entry.
  Apex15:59CT fit is unknown; personal overnight research is conditional on the verified source window.
  [Review](agents/codex/results/scout_fx_auctions_20261029.md) · [Evidence](agents/codex/evidence/scout_fx_auctions_20261029.md).
  [Testability follow-up](agents/codex/results/scout_5207418_testability_20261029.md): new author/BoC/conference and
  replication searches did not recover the source rule. Exact-window, flat-time and overnight constraints remain unresolved.
  [Calendar acquisition](agents/codex/results/scout_fx_calendar_acquisition_20261029.md) now saves943 primary BLS/BEA/Fed
  calendar facts for2018–22, with secondary inventory separate, shutdown revisions and unusual clocks explicit.
  Full paper/event universe and original schedule/receipt evidence still precede TEST; this is data progress, not validation.
  [Claims acquisition](agents/codex/results/scout_claims_calendar_acquisition_20261029.md) adds261 officially corroborated
  release dates and249 printed clocks, retaining12 unknown times. Two omitted2019dates were restored from actual
  official evidence; failed download URLs were not treated as absent releases.

- [ ] **Signed SPX dealer delta at PM expiry — WATCH / NEEDS DATA (2026-10-29), SSRN7330098.**
  Full source now read: a direct ES hedge-unwinding channel with reported extreme-group gross differences of17bp
  over30minutes and12.5bp over15minutes, July2020–June2023. These are author evidence, not our net strategy results.
  Need signed C1 SPXW dealer positions reconstructed from series inception plus matching option deltas, prior inventory,
  session coverage, corrections and actual receipt clocks. Owned NDX GEX/OI and NQ tape delta cannot supply the signal.
  Minute-start labels with end-minute quotes must be lagged correctly; retrospective T+1 records cannot become same-day signals.
  Smallest next check: retain/hash the public paper and obtain a lawful sample; reconcile one expiring series from
  inception and available-at data before any design returns. Public ZIP samples were unreadable via connector and
  a network-enabled proxy download returned403. No complete historical book obtained and no return trial started.
  Merge input acquisition with existing flow evidence-sheetD; retain the distinction between terminal book-level
  hedge removal and time-decay position-change hedging. Existing failed gamma/OI/max-pain results remain in force.
  [Full-source review and testability](agents/codex/results/scout_7330098_testability_20261029.md).
  [Acquisition/intake packet](agents/codex/results/scout_spx_positions_acquisition_20261029.md): no raw signed book obtained.
  Current Cboe terms identify a fixed2022H2 free sample for eligible first-time users; enrollment/licensing is unactivated.
  The one-minute product was introduced in2025 and arrives2–5minutes after interval end; historical timestamps alone
  do not certify a tradable2018–22 signal. Do not buy/activate access or substitute OI under this queue entry.

- [ ] **U.S. factor-beta stock baskets — PARTIAL SCREEN FAIL; exact replication unverified (2026-10-29).**
  Authorized restricted S&P500/SPY-beta screen is completed under a committed plan:2018–22 covered-day overnight +3.93bp gross/−0.66bp net, intraday +0.89/−3.52bp under4bp RT plus borrow.
  120/114 of1,259 selected days are unresolved after acquisitions; quoted returns are conditional diagnostics, not a complete native cash ledger. Rounded shares do not rescue it. No2023+ or funded bench opened.
  Stop this protocol; no timing/filter/sizing rescue search. Full CRSP/FF5 study still needs exact factor data, historical raw share basis, acquisition/settlement treatment and borrow/auction evidence before a separately justified preregistration.
  Source's gross conditional coefficients remain author evidence, not validated portfolio returns. Outside current futures allocations.
  [Screen/code/manifest](agents/codex/results/factor_beta_sessions_test_20261029.md) · [Original review](agents/codex/results/factor_beta_sessions_review_20261029.md).

- [ ] **ORB30 + M30 EMA20, long-only NQ — WATCH; proxy tested, native implementation unverified.**
  Verified proxy merit: 994 trades, PF 1.25 after NQ costs; full-session EMA outperformed cash-only EMA in the frozen
  2018–22 design comparison. Later PF weakens to 1.21; 4R/no-target improvements remain statistically unproven.
  Current personal19 additions lower profit/DD95; no allocation recommendation, and full Apex comparisons remain limited.
  Smallest next check: compile the research PowerLanguage prototype on a home-PC research chart, confirm full-session
  M30 EMA / 15:55 CT proxy settings, export exact fills/settings and reconcile with saved Python trades. Original author
  EA/flatten settings, native ticks, roll handling and 18 unclassified held minutes still need verification.
  No new parameter search or live/VPS changes. [Report](agents/codex/results/orb30_ema.md) ·
  [Research code](agents/codex/code/ORB30_EMA_Research.txt).

- [ ] **PrimeSync ES/NQ, 15m/30m — WATCH; research prototype, not MC-verified (2026-10-27).** Merit: in the frozen
  reconstruction, full exit at4.5R beat thirds in all four2018-22 contexts and the selected style stayed net positive
  in all four2023+ checks. Recent significance is weak; parameters are assumed, not the author's verified settings.
  Compile [PrimeSync_v1](agents/codex/code/PrimeSync_v1.txt) on a separate research chart using the
  [setup notes](agents/codex/code/PrimeSync_SETUP.md); export Settings, List of Trades and matching minute/total-volume data.
  Verify signals, ADX/VWAP/ATR, integer risk sizing, entry-bar protection and IOG stop/partial behavior; reconcile native
  micro versus mini-volume/cost assumptions. Matched controls, independent review and portfolio/account contribution
  remain unverified; do not add it to a plan from this screen. [Results](agents/codex/results/primesync.md).
  Account tests completed: none of the five plans clears the preregistered placement gates at1micro; closest personal
  ES30 improves mean-profit/p95-DD only1.8%. Do not add or start a sizing rescue search. Keep MC parity pending for later review.
  [Placement results](agents/codex/results/primesync_accounts.md) · [v2 code](agents/codex/code/PrimeSync_v2.txt).

- [ ] **6E cross-asset package v4 — WATCH / NEEDS DATA; personal-account research.** Merit: a different market and multi-day
  horizon, with reported cross-asset and walk-forward evidence; potential diversification from the NQ-heavy book.
  Obtain the original Python implementation, frozen settings, contract/roll map, trade/order ledger and daily marked P&L.
  First verify as-of 16:00 ET inputs, later executable fills, integer M6E vol-target quantities, native fees/spread/slippage
  and trade-to-daily/roll reconciliation. The 08:29–09:30 euro-reaction branch needs intraday data; daily bars alone cannot reproduce it.
  Review **Macro Momentum, Macro-Shock and Gold-Shock first**, retaining the complete six-leg package as the reference
  (RSI pullback, weekly breakout and Stock-Shock included); no unregistered hindsight deletion or optimization.
  Then preregister a bounded replication and, if it passes, measure addition/replacement in the current personal portfolio.
  [Review](agents/codex/results/six_e_cross_asset_review_20261027.md) · [Evidence](agents/codex/evidence/six_e_cross_asset_20261027.md).

- [ ] **IFT_NQ5_Flow_Signal — WATCH / NEEDS DATA; account placement unverified.** Merit: a fully supplied rule with disclosed
  walk-forward, sensitivity and transfer claims that justify a careful replication. Obtain native **full-Globex 5-minute
  OHLC + Volume + UpTicks + DownTicks**, 500 prior ratio observations plus their indicator warm-up, and the matching detailed MultiCharts report/settings;
  also request the author's Python/WF selection records. Existing cash-session-only directional-volume files cannot reproduce it.
  Home-PC research export only: [Claude's NQ Up/Down exporter](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/tools/exporters/NQ_UpDown_Exporter.txt).
  First reconcile volume classification, completed-bar/next-fill timing, staged scale-outs and position counting. Freeze source-parity
  versus protected-entry protocols and the live/historical position-gate assumptions before returns. Then run the preregistered
  cheap screen; account/personal comparisons follow only if it passes. Minimum two-contract scale-out and current risk limits need testing.
  [Review](agents/codex/results/ift_nq5_flow_review.md) · [Evidence](agents/codex/evidence/ift_nq5_flow.md).

- [ ] **Monthly S&P 500 VRP-conditioned equity exposure — exact-source verification pending; bounded proxy REJECT (2026-10-29).**
  Merit: Zhou's SSRN 1783624 reports positive three-month equity-return predictability, adjusted R² 9.61% and
  overlap-robust t 7.22 over 1990–2016; these are in-sample source claims, not verified net strategy returns.
  This is monthly equity allocation, not an options-selling rule or a new intraday Apex filter.
  Obtain/pin original monthly IV/RV series and construction code, historical availability, SPX five-minute/overnight
  conventions and return units. Audit against related VIX/VRP work; daily SPY/futures substitutions are proxy adaptations.
  Completed pre-return-registered adaptation: 2018–22, positive-VRP exposure one MES-equivalent,31 selected months
  net$8,322.81 versus$9,614.12 for37 same-universe constant-exposure months; t1.79, removed months+$215.22 average.
  Reject this filter; no2023+test or account placement. Rolling-median/IV-only/RV-only outcomes were not run:
  history availability failed. A missing2020-11-30 daily mark also blocks daily-risk certification; no price repair.
  Author data is advertised throughDec2024 but its Drive download is network-policy denied; older official Fed data
  endsDec2008. Exact source replication remains distinct and unverified. Smallest later check, if source data becomes
  accessible: pin/audit it before a separately registered source replication. No threshold rescue or automatic rerun.
  [Actual proxy test](agents/codex/results/vrp_monthly_proxy_20261029.md).
  [Review](agents/codex/results/variance_risk_premium_review_20261029.md) ·
  [Evidence](agents/codex/evidence/variance_risk_premium_20261029.md).


- [ ] **Actual closing-auction imbalances — shared SPY/ES and QQQ/NQ family; NEEDS DATA (2026-10-29).**
  Academic merit: source auction-state reversion and temporary stock/ETF pressure support checking real signed
  updates. No net futures edge or portfolio placement verified. Consolidates existing SPY/QQQ evidence rather
  than counting another clock/ticker as a new family. This cycle moved past blocked leads: two Arca sample
  sessions, one Nasdaq sample day and advertised2010–2018 author aggregates do not supply the design panel.
  Smallest later check: permitted original source bytes plus venue-specific signed updates, reference/indicative
  definitions, synchronized quotes and publication/receipt clocks; audit before a bounded preregistered screen.
  Keep pre-auction pressure and post-auction reversal distinct. Personal stock/ETF implementation is a separate
  possibility; do not transfer stock alpha to NQ/ES or reuse a final auction print as a hindsight fill.
  [Cycle/source reviews](agents/codex/results/scout_closing_auctions_cycle_20261029.md) ·
  [Evidence/data gates](agents/codex/evidence/scout_closing_auction_imbalances_20261029.md).


- [ ] **Cross-asset futures OFI residual reversal — METADATA WATCH, not TEST (2026-11-02), SSRN7245981.**
  Specific merit: lagged idiosyncratic flow pressure may unwind while PCA-rotation refits address changing common
  institutional flows; author claims net/low-exposure results, but these are unverified and expressly not formal OOS.
  This uses order-flow residuals, not a revival of the rejected price-spread/PCA pairs family. Needs full rules,
  matching20-market L1tick OFI, native clocks/fills/costs and admissible2018–22history; own NQminute aggregates and
  other-market OHLCV do not provide it. Smallest next check only on genuinely new source/data: authenticate the
  exact universe and one complete matching observation. Bounded owned/free check completed; parked, no repeat crawl,
  return reservation or user-action request. [Data D47](agents/codex/DATA_NEEDED.md#2026-11-02-owned-field-screen),
  [record](agents/codex/research/scout/records/7245981.json), [report](agents/codex/results/scout_owned_source_20261102.md).

- [ ] **Crude-oil distribution asymmetry OIS — METADATA WATCH / NEEDS FULL SOURCE (2026-11-02), SSRN5392801.**
  Specific merit: authors claim OOS forecasting/allocation improvement beyond historical mean and realized skewness;
  these are unverified primary-abstract claims. Owned CL prices may supply raw distribution inputs, conditional on
  exact formation/forecast/roll rules. No formula, threshold or strategy inferred from a secondary summary.
  Smallest next check only when genuinely new primary text arrives: authenticate OIS/target construction and map
  one dated formation to actual owned fields/clocks before any trial. Primary403 and no-file author listing recorded;
  parked, no repeated crawl or user-action request. [Data/source D48](agents/codex/DATA_NEEDED.md#2026-11-02-source-watches),
  [record](agents/codex/research/scout/records/5392801.json), [report](agents/codex/results/scout_owned_source_followon_20261102.md).

- [ ] **CTA subscription/redemption month-turn pressure — METADATA WATCH / NEEDS FULL SOURCE (2026-11-02), SSRN2515900.**
  Specific merit: a timed fund-flow mechanism and author claim of concentrated CTA-index returns on three month-turn
  days. This is not a verified net futures strategy or a forecast-accuracy statistic. Exact replication signal,
  universe/weights, calendars, flow sign and costs remain unknown; existing CTA flip/fade and generic month-end
  selections remain prior history. Smallest next check on new primary availability: identify a causal source rule
  and its exact owned-field map; no invented CTA positions or trend window. Primary403, bounded author/institution
  search found no authenticated full copy; parked and move on. [Data/source D49](agents/codex/DATA_NEEDED.md#2026-11-02-source-watches),
  [record](agents/codex/research/scout/records/2515900.json), [report](agents/codex/results/scout_owned_source_followon_20261102.md).

- [ ] **Post-publication commercial-position liquidity spread — conditional WATCH / NEEDS DATA (2026-11-03), SSRN2449315.**
  Merit: the2018primary manuscript's Table4 reports29bp top-minus-bottom on days5–10after Tuesday formation
  (t3.73), after its public-information boundary. This is an unreplicated26-market spread, not verified CL alpha.
  Merge the related3881922robustness paper and2023HPM source watch (DOI10.1016/j.econmod.2023.106214) here;
  do not count new titles as separate trials. Prior2311859/4534852clock cautions and failed Williams COT-index
  tests remain history. Owned legacy archives contain783CL/GC/NG position-date rows, not the native26-market
  portfolio, original released vintages or source roll legs. Smallest next check only with genuinely new matching
  evidence: reconcile one source-specific public-release/formation/dated-contract roll week, retaining holidays,
  shutdown catch-up and initial-versus-revised data; then assess the full design panel and native costs before
  any bounded preregistration. No three-market substitute, Tuesday look-ahead or Apex intraday port. Park and
  continue other discovery. [D50](agents/codex/DATA_NEEDED.md#2026-11-03-conditional-positioning-and-lei-watches),
  [record](agents/codex/research/scout/records/2449315.json), [source checkpoint](agents/codex/results/scout_owned_source_20261103.md).

- [ ] **LEI stale-information post-release reversal — conditional personal WATCH / NEEDS DATA (2026-11-03), SSRN1108050.**
  Merit: authors report a transient ES response to publicly reconstructable information and65bp gross over the
  complete three-day trade, not independently verified profit. The source's10:05ETpost-release reversal lasts
  through next-day close; no Apex-compatible adaptation is supplied. Need original LEI releases, exact Bloomberg
  consensus/receipt vintages, overlap calendar and native ES paths/rolls/costs. A bounded free check found public
  forecasts but no faithful consensus panel: February22,2018MetaTrader0.5%versus contemporary ActionEconomics0.6%.
  Smallest later check with new matching inputs: authenticate one surprise's available-at sign and source-leg
  timing, then inspect complete2018–22coverage/power before reserving a test. No hindsight pre-release sign,
  price-sign substitute, shortened hold or repeated vendor crawl. Park and move on.
  [D51](agents/codex/DATA_NEEDED.md#2026-11-03-conditional-positioning-and-lei-watches),
  [record](agents/codex/research/scout/records/1108050.json), [source checkpoint](agents/codex/results/scout_owned_source_20261103.md).
