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

- [ ] **Commodity-index roll calendar spreads — conditional personal research / NEEDS SPECIFICATION AND DATA (SSRN2942340).**
  Till/Eagleeye2017 identifies predictable sell-front/buy-deferred index demand and anticipatory spreads, but supplies
  no net backtest or exact dated protocol. Distinct from weekly basis reversal; do not recycle failed outright CL
  timing proxies (prior t1.4 and GSCI/BCOM t0.5/0.7). Need historical/current index rules and weights, actual paired
  commodity maturities, synchronized prices, native both-leg costs and delivery/margin handling. Smallest next check
  when matching evidence arrives: reconcile one specified index roll and its two-leg cashflows, then complete the
  evidence/preregistration gate before returns. Source brings no new dataset; existing acquisition blockers remain.
  Multiday description earns no Apex placement; personal contribution is unverified. Zero new trials.
  [Review](agents/codex/results/till_2942340_20261031.md) · [Evidence](agents/codex/evidence/till_2942340_20261031.md).


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

