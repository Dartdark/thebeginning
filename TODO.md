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
- [ ] **Test order Sunday 17:00 CT** to confirm a real Rithmic fill on the Apex account (Symbol Mapping `@MNQ -> MNQZ6`).
- [ ] Keep the PC and connection awake during trading hours (screen sleep off).

## This week and next

- [ ] **Tue 10/20: buy account #2** (single 50K EOD, $59): only after a real Apex fill is confirmed.
- [ ] **Fri 10/23 (and every Friday): export the weekly MultiCharts reports into `live/`** and tell Claude (it runs
  `analysis/live_vs_backtest.py --all live/` and the drift alarm).
- [ ] When account #1 passes ($53,000): turn auto-trading off on that account.
- [ ] **~Mon 10/27: account #3** (150K No-Activation, $249).
- [ ] Optional: rerun the ONB ADX30 MultiCharts backtest once with the new code (should be nearly identical).

## ES MOC Follow (funded candidate, 2026-10-17)

- [x] (2026-10-17, confirmed 199/199) MultiCharts backtest: [ES_MOC_Follow.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/ES_MOC_Follow.txt)
  on a 5-minute **@ES** chart (Exchange time, 24-hour session, Bar Magnifier 1 min, from Jan 2018, NumContracts 1, no costs);
  save the report as "Backtesting Strategy Performance Report _ @ES - 5 Minutes ES MOC Follow.xlsx" and push / send it.
- [ ] Antigravity: Task 09 blind check (pull `agents/tasks` and the `ES_1min_*.csv` files first).
- [ ] When funded: ES MOC Follow (IN THE PLAN since 2026-10-17) on a 5-min MES chart, NumContracts 2, Symbol Mapping `@MES -> MESZ6` (roll with MNQ). Vault Break funded: `NumContracts` 2, `FlaggedContracts` 1 (decided 2026-10-17).

## Journal (Obsidian)

- [ ] One-time setup: follow [journal/README.md](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/journal/README.md) (separate clone in `C:\TradingVault`, Daily notes + Templates plugins).
- [ ] From Mon 10/19: a daily note each trading day; run `journal\sync.ps1` and tell Claude "read my journal".

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
