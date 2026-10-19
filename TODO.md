# To-do list (user's open items)

Started 2026-10-17. Claude ticks items off when you say they're done and reminds you on a schedule (see 'Reminders' at the
bottom). Times are Central (CT).

## Before Sunday 10/18 (test order 17:00 CT, Bridge Monday enters 19:00 CT)

- [x] (2026-10-17, user: done) **Paste and compile the stop-guard update on the combine charts** (outside market hours; inputs and backtests unchanged):
  - [x] Vault Break: [NQ_Vault_Break.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/NQ_Vault_Break.txt)
    (or [NQ_Vault_Break_SP.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/NQ_Vault_Break_SP.txt) if you already switched)
  - [x] ONB ADX30: [NQ_Overnight_Bias_ADX30.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/NQ_Overnight_Bias_ADX30.txt)
  - [x] EOS: [NQ_Expiration_Open_Short.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Expiration_Open_Short.txt)
- [x] **Bridge Monday chart: add [Apex_Stop_Guard.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Apex_Stop_Guard.txt)**,
  `StopPoints` a few ticks wider than the Bridge's own stop (read it from its inputs or its stop order).
  **Not needed (2026-10-17):** the Bridge runs with `StopPts` 0 (no stop, as backtested), so there is no stop to guard.
- [x] **Compile [Apex_Target_Guard.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Apex_Target_Guard.txt)**
  and add it to the VB, ONB and Bridge Monday charts; `TargetBalance` 53050, `StartBalance` = the Apex balance (set it before
  every session).
- [x] (2026-10-18, user: filled) **Test order Sunday 17:00 CT** to confirm a real Rithmic fill on the Apex account (Symbol Mapping `@MNQ -> MNQZ6`).
- [x] (2026-10-18, user: set) Keep the PC and connection awake during trading hours (screen sleep off).

## This week and next

- [ ] **Tue 10/20: buy account #2** (single 50K EOD, $59): real Apex fill confirmed 2026-10-18, so go ahead (automation confirmed allowed by the user 2026-10-19).
- [ ] **Fri 10/23 (and every Friday): export the weekly MultiCharts reports into `live/`** and tell Claude (it runs
  `analysis/live_vs_backtest.py --all live/` and the drift alarm).
- [ ] When account #1 passes ($53,000): turn auto-trading off on that account.
- [ ] **~Mon 10/27: account #3** (150K No-Activation, $249).
- [ ] Optional: rerun the ONB ADX30 MultiCharts backtest once with the new code (should be nearly identical).

## ES MOC Follow (funded candidate, 2026-10-17)

- [x] (2026-10-17, confirmed 199/199) MultiCharts backtest: [ES_MOC_Follow.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/ES_MOC_Follow.txt)
  on a 5-minute **@ES** chart (Exchange time, 24-hour session, Bar Magnifier 1 min, from Jan 2018, NumContracts 1, no costs);
  save the report as "Backtesting Strategy Performance Report _ @ES - 5 Minutes ES MOC Follow.xlsx" and push / send it.
- [x] (2026-10-17, PASS on the rule; its clock ran 1 min early, see agents/results/TASK_09_VERDICT.md) Antigravity: Task 09 blind check (pull `agents/tasks` and the `ES_1min_*.csv` files first).
- [ ] When funded: ES MOC Follow (IN THE PLAN since 2026-10-17) on a 5-min MES chart, NumContracts 2, Symbol Mapping `@MES -> MESZ6` (roll with MNQ). Vault Break funded: `NumContracts` 2, `FlaggedContracts` 1 (decided 2026-10-17).

## Journal (Obsidian)

- [x] (2026-10-17, done) One-time setup: follow [journal/README.md](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/journal/README.md) (separate clone in `C:\TradingVault`, Daily notes + Templates plugins).
- [ ] From Mon 10/19: a daily note each trading day; run `journal\sync.ps1` and tell Claude "read my journal".

## Vault Break NR7 sizing (candidate, 2026-10-18)

- [x] (2026-10-18, confirmed 135/135 sessions) MultiCharts backtest of [NQ_Vault_Break_SP.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/NQ_Vault_Break_SP.txt)
  on a 30-min **@NQ** chart (same settings as before, from Jan 2018), inputs **NumContracts 1, NR7Contracts 2, FlaggedContracts -1**,
  no costs; save as "Backtesting Strategy Performance Report _ @NQ - 30 Minutes VB NR7.xlsx" and push / send it.
  (Live combine charts: nothing changes; NR7Contracts defaults to -1 = off.)
- [x] (2026-10-18) Strategy-checker: **FAIL** (t 2.81 below 3.53; 2023-26 weaker). Not added to the plan (your condition). Leave `NR7Contracts` -1 everywhere; recheck on new data (WATCHLIST #21).

## Cowork (2026-10-19)

- [ ] Install the Claude desktop app, open Cowork, give it only the folders in `cowork/INSTRUCTIONS.md`, and paste that
  file into its instructions. Test it with: "copy this week's MultiCharts reports into C:\TradingVault\live and run journal\sync.ps1".

## Move live trading to the VPS (QuantVPS, 2026-10-19)

Split: VPS = live trading only (MultiCharts live charts, Rithmic, later the copier). Home PC = everything else (local
Claude chores, Obsidian / `C:\TradingVault`, Antigravity / Docker, MultiCharts backtests). Do the move on a weekend or
after 15:59 CT, never with a position open.

- [x] (2026-10-19) Memory check: MultiCharts with the 4 live charts uses ~290 MB in total (app 100 MB + background
      processes ~190 MB); ~30 charts later ≈ 1.5-3 GB + 2 GB Windows. QuantVPS tiers (user's screenshot 2026-10-19): Starter
      $29.99 (2 cores, 4 GB), Lite $59.99 (4 cores, 8 GB), Pro $99.99 (6 cores, 16 GB); annual -20%.
- [ ] Buy **VPS Lite** (Chicago, Windows; annual if sure). Starter's 4 GB / 2 cores is too tight once accounts and the
      copier are added; move to Pro only if startup / reconnects get slow.
- [ ] Ask Apex / Rithmic whether one login may be connected from two machines at once; plan for live on the VPS ONLY.
- [ ] On the home PC: export the MultiCharts workspace(s) and the compiled signals (VB, ONB ADX30, EOS, Target Guard,
      Stop Guard, Bridge Monday) and note every chart's settings: inputs (VB 8, ONB `RiskPerTrade` 1100 / ADX 30 /
      StopAtrPct 0.25, EOS $500, Bridge 2 MNQ), bar size, session template (CME 24h), Exchange time zone, Bar Magnifier,
      Symbol Mapping `@MNQ -> MNQZ6`, Target Guard `StartBalance` / `TargetBalance` 53050.
- [ ] On the VPS: install MultiCharts + the data feed + Rithmic connection, import the workspace and signals, check every
      input against the list above.
- [x] (2026-10-19) Same-result check: ONB on the VPS vs the PC report, Jan-Oct 2026: 77/77 trade days, 75 identical,
      2 differ by 1 tick (data). The others are assumed the same (user: VPS isn't for backtesting); just check their inputs
      and that the last few days' trade arrows on each chart look like the PC's.
- [ ] VPS Windows: updates paused during market hours (set active hours / pause), sleep and screen-off disabled,
      MultiCharts set to start with Windows if the VPS restarts.
- [ ] Switch over: turn auto-trading OFF on the PC charts, ON on the VPS charts (after 15:59 CT or on a weekend);
      watch the first live trade on the VPS (fill shows in Rithmic / Apex).
- [ ] Reports: each Friday export the weekly MultiCharts reports on the VPS and copy them to the PC (remote-desktop
      copy / paste) into `C:\TradingVault\live\` before 16:47 CT (or later: git on the VPS exporting straight into `live\`).
- [ ] Keep the PC's MultiCharts for backtests only, logged in with data only (no live trading login), so it can't
      kick the VPS off Rithmic.

## Trade logger + auto journal (2026-10-19)

- [ ] VPS: create `C:\TradingLogs`; compile `apex_strategies/Apex_Trade_Logger.txt` as a Signal; add it to every live chart
      (Tag = VB / ONB / EOS / MON_BR). If it doesn't compile, send Claude the error.
- [ ] VPS: Git for Windows + clone to `C:\TradingRepo` + the scheduled push (steps in `live/vps/README.md`); test it once.

## Later

- [ ] Before the CL Sunday fade goes live: confirm Apex allows MCL on the account.
- [ ] When an account goes funded: paste the funded files (all have the stop guard):
  [ONB ML](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Overnight_Bias_ML.txt),
  [Monday Long](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Monday_Long.txt),
  [Late-Day Flow](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Late_Day_Flow.txt),
  [NFP Fade](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_NFP_Fade.txt),
  [CL Sunday Fade](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/CL_Sunday_Gap_Fade.txt),
  VB SP, EOS.
- [ ] **~Thu 12/10: roll Symbol Mapping** `@MNQ -> MNQH7` (before the December roll, ~12/11).
- [ ] **Mid-December gate:** ~40–70 live trades at ≥ 75% of backtest and no ALARM → start scaling (FUNDED_PLAN.md).
- [ ] Optional: add an `OPENAI_API_KEY` to the environment's secrets for a second, different-lab strategy checker.

## Done

- [x] 2026-10-17: Docker Jesse + Antigravity installed on the user's PC and connected (MCP working). First blind-check task: when the user asks.

## Reminders

Claude reminds you in this session (scheduled tasks, Central time): every **Sunday and Wednesday at 10:52 CT**, plus a
last call **Sunday 10/18 at 15:30 CT** before the 17:00 test order. Say "stop the reminders" to turn them off, or ask for a
different schedule.
