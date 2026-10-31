# TODO: done items archived 2026-10-28 (moved out of TODO.md by the context trim; nothing lost)


### Before Sunday 10/18 (test order 17:00 CT, Bridge Monday enters 19:00 CT)
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

### This week and next
- [x] (2026-10-20) Account #2 bought and set up on the VPS: second chart set (VB, ONB ADX30, EOS, Bridge) on the new account, logger tags `-2`, StartBalance 50000.
- [x] (2026-10-26: account #1 BLOWN, user) When account #1 passes ($53,000): turn auto-trading off on that account.
- [x] (2026-10-20, user: done) **Now: Rithmic copier off (or #2 removed as follower)** while set 2 auto-trades, or #2 trades double size. Copier
  waits until several funded accounts (2026-10-20).

### ES MOC Follow (funded candidate, 2026-10-17)
- [x] (2026-10-17, confirmed 199/199) MultiCharts backtest: [ES_MOC_Follow.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/ES_MOC_Follow.txt)
  on a 5-minute **@ES** chart (Exchange time, 24-hour session, Bar Magnifier 1 min, from Jan 2018, NumContracts 1, no costs);
  save the report as "mc_reports/Backtesting Strategy Performance Report _ @ES - 5 Minutes ES MOC Follow.xlsx" and push / send it.
- [x] (2026-10-17, PASS on the rule; its clock ran 1 min early, see agents/results/TASK_09_VERDICT.md) Antigravity: Task 09 blind check (pull `agents/tasks` and the `ES_1min_*.csv` files first).

### Relative Strength NQ / ES (your new strategy, 2026-10-20: B, checker PASS WITH CONCERNS)
- [x] (2026-10-20, done: 1,157 days match, P&L corr 1.000) MultiCharts backtest for the trade-by-trade check: [RelStrength_v3.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/checks/candidates/relative_strength/RelStrength_v3.txt)
  (your code, unchanged) on a **1-minute @NQ chart with 1-minute @ES as Data2** (same feed, CME 24h session, Exchange
  time = CT, first RTH bar 08:31), data loaded from **Sep 2017**, default inputs, **commission and slippage 0** (Claude adds
  costs), Intrabar Order Generation off. Save as "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Relative Strength.xlsx"
  and push / send it.
- [x] (2026-10-20, you: include it in all relevant plans) In the plans: 50K funded longs only 1 MNQ, 150K funded both sides 1 MNQ, personal account; not in evaluations.

### Dual Thrust v4 (your file, 2026-10-24: A, checker PASS WITH CONCERNS; personal plan; 150K funded slot given to Swing Target 2026-10-25)
- [x] (2026-10-25, done: 1,609 / 1,611 trades identical) Optional, no deadline (outside market hours, not on the live VPS): export the MultiCharts backtest of
  [NQ_Dual_Thrust_v4_CT.txt](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/checks/candidates/dual_thrust/NQ_Dual_Thrust_v4_CT.txt)
  on a 1-minute @NQ chart (Exchange time = CT, CME 24h session, IOG off, default inputs, from Jan 2017, **commission and
  slippage 0**, Claude adds costs); save as "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Dual Thrust v4.xlsx"
  and push it. Claude then checks it trade by trade against the rebuild (1,611 trades, $140 per NQ after costs).
  **Needed before the first 150K funded account trades it.**
- [x] (2026-10-25: replaced by Swing Target v3 Qty 2 on 150K funded) When a 150K account is funded: add [NQ_Dual_Thrust.txt](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Dual_Thrust.txt)
  ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Dual_Thrust.txt))
  on a 1-minute MNQ chart (Exchange time, CME 24h, IOG off), `NumContracts` 2 (1 while the cushion is below $3,000),
  Trade Logger tag `DT`. Not on 50K accounts or evaluations.

### T_ONESIDE (your file, 2026-10-24: B, IN THE 50K FUNDED PLAN since 2026-10-28, checker PASS WITH CONCERNS; fade leg = small funded gain at 1 MNQ)
- [x] (2026-10-28, user: yes, swapped) **Your call (2026-10-28 re-bench):** 50K funded, Relative Strength longs 1 MNQ -> T_ONESIDE v2 fade 1 MNQ (UseT true, UseOS false, UseStop true)? Fewer blown accounts (5.9 -> 4.3%), same 2-year money (+$190), year 1 −$60, 6th payout ~6 days later. Adding it on top, or on 150K, does nothing.
- [x] (2026-10-25, done: 348 / 358 fades identical, net t 3.5) Optional, before any plan use (outside market hours, not on the live VPS): MultiCharts backtest of
  [T_ONESIDE_v2.txt](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/checks/candidates/t_oneside/T_ONESIDE_v2.txt)
  on a **1-minute @NQ chart** (Rithmic, CME 24h session 17:00-16:00, Exchange time = CT, IOG off, Bar Magnifier off, from
  Sep 2017), inputs **UseT true, UseOS false, UseStop true, Qty 1**, **commission and slippage 0** (Claude adds costs); save as
  "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute T_ONESIDE v2.xlsx" and push / send it.
  Claude checks it trade by trade (363 fades 2018-26, $239 per NQ after costs).

### GC_COMBO v2 (your gold files, 2026-10-24: C pending the MultiCharts report)
- [x] (2026-10-24, done: exact parity after ETminusChart 0; ranked C) Optional, no deadline (outside market hours, not on the live VPS): run it in MultiCharts and export the report, step by
  step in [MC_SETUP.md](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/checks/candidates/gc_combo/MC_SETUP.md)
  (@GC 1-min + @CL Data2 + GCCOMBO Data3); save as "mc_reports/Backtesting Strategy Performance Report _ @GC - 1 Minute GC COMBO v2.xlsx"
  and push / send it. Expect ~1,204 trades, ~$226k for 2017-09-18 → 2026-08-07.

### Overnight TickRSV / VIX (your spec, 2026-10-24: A, MultiCharts-confirmed 97% of nights)
- [x] (2026-10-24) VIX: dxFeed has no VIX index; mapped data/VIX_daily.csv with Map ASCII (live needs a daily update or the previous-day VIX).
- [x] (2026-10-24, matched 529 nights, P&L corr 1.000) MultiCharts backtest of [NQ_Overnight_Tick_VIX.txt](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/checks/candidates/overnight_tick/NQ_Overnight_Tick_VIX.txt)
  ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/checks/candidates/overnight_tick/NQ_Overnight_Tick_VIX.txt))
  on a 5-minute @NQ chart (CME 24h, Exchange time = CT, IOG off) with VIX daily as Data2, from Sep 2017, default inputs,
  **PrintDiag true**, commission / slippage 0; save as "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Overnight Tick VIX.xlsx"
  and send the report + the PowerLanguage output (the printed lines). Claude checks trades and the UpTicks / DownTicks signs.

### PAPERTREND v2 (your description + report, 2026-10-24: B, checker FAIL narrow on deflated Sharpe; personal-plan candidate)
- [x] (2026-10-25, done: 556 / 558 rebuild trades identical, +13 roll days the code can't see; t 4.35) (2026-10-25: Claude wrote the code from the spec, `checks/candidates/papertrend/PAPERTREND_v2_claude.txt`; backtest it on @NQ 5-min, Exchange CT, commission / slippage 0, and export the List of Trades as `...@NQ - 5 Minutes PAPERTREND v2 claude.xlsx`) Optional (outside market hours, not on the live VPS): export the PAPERTREND v2 **List of Trades** from MultiCharts (the report you sent) into
  `mc_reports/` and send the code. The Python rebuild trades 582 times to 2026-08-14 vs the report's 535; the trade list shows where they differ.
- [x] (2026-10-25, user: yes; added at 1 MNQ with Claude's code, return/DD 8.5 -> 9.0) Your call: add it to the personal plan at 1 micro (+$2.3k a year, return/DD 8.3 -> 8.7) once the trade lists agree. Not for Apex (benches worse).
  If you trade it: add a 2 x ATR disaster stop (costs nothing in the backtest) and keep the 14:55 CT flatten exact.

### BB_MRM (your file, 2026-10-25: C after the MultiCharts report; OUT of the personal plan (user 2026-10-25), paper forward log from 10/26)
- [x] (2026-10-25, done: 1,657 trades, net t 2.5 vs the rebuild's 3.4 -> C; decide whether BB_MRM stays live) **MultiCharts backtest 2018-01 -> today** (outside market hours, not on the live VPS): [BB_MRM_Pre-market_user.txt](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/checks/candidates/bb_mrm/BB_MRM_Pre-market_user.txt)
  on a 1-minute **@NQ** chart, **Time Zone = Exchange (CT)**, 24-hour session, IntrabarOrderGeneration off, no Bar Magnifier needed (1-min bars),
  your input screen (AlphaReductionPct 10, Session_Open 08:05, Offset 1h15), 1 contract, no costs. Export the report with its **List of Trades** into
  `mc_reports/` (name: `Backtesting Strategy Performance Report _ @NQ - 1 Minute BB_MRM.xlsx`) and tell Claude. The Python rebuild matches your
  2020-23 report (802 vs 801 trades); this checks 2018-19 and 2024-26 (the −$24k stretch 2024 Q4 - 2025 Q2, +$44.7k in 2026).
- [x] (2026-10-25: cancelled, out of the plan; don't put it on the personal account) Live (personal account): MNQ 1 contract, chart on the **Exchange** clock (on Italian time it trades 01:05-02:20 CT, which loses).
- [x] (2026-10-25: not needed now, it's C) Claude: run the strategy-checker on BB_MRM (`checks/candidates/bb_mrm/`).

### Antigravity's NQAlignedWeaknessShort (2026-10-20, C)
- [x] (2026-10-20, confirmed 216/216) MultiCharts backtest: [NQ_Aligned_Weakness_Short.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/checks/candidates/aligned_weakness_short/NQ_Aligned_Weakness_Short.txt)
  on a 1-minute @NQ chart with 1-minute @ES as Data2 (same feed, CME 24h, Exchange time, first RTH bar 08:31), data from
  Sep 2017, commission / slippage 0, IOG off; save as "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Aligned Weakness Short.xlsx".

### Journal (Obsidian)
- [x] (2026-10-17, done) One-time setup: follow [journal/README.md](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/journal/README.md) (separate clone in `C:\TradingVault`, Daily notes + Templates plugins).

### Vault Break NR7 sizing (candidate, 2026-10-18)
- [x] (2026-10-18, confirmed 135/135 sessions) MultiCharts backtest of [NQ_Vault_Break_SP.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/NQ_Vault_Break_SP.txt)
  on a 30-min **@NQ** chart (same settings as before, from Jan 2018), inputs **NumContracts 1, NR7Contracts 2, FlaggedContracts -1**,
  no costs; save as "mc_reports/Backtesting Strategy Performance Report _ @NQ - 30 Minutes VB NR7.xlsx" and push / send it.
  (Live combine charts: nothing changes; NR7Contracts defaults to -1 = off.)
- [x] (2026-10-18) Strategy-checker: **FAIL** (t 2.81 below 3.53; 2023-26 weaker). Not added to the plan (your condition). Leave `NR7Contracts` -1 everywhere; recheck on new data (WATCHLIST #21).

### Move live trading to the VPS (QuantVPS, 2026-10-19)
- [x] (2026-10-19) Memory check: MultiCharts with the 4 live charts uses ~290 MB in total (app 100 MB + background
      processes ~190 MB); ~30 charts later ≈ 1.5-3 GB + 2 GB Windows. QuantVPS tiers (user's screenshot 2026-10-19): Starter
      $29.99 (2 cores, 4 GB), Lite $59.99 (4 cores, 8 GB), Pro $99.99 (6 cores, 16 GB); annual -20%.
- [x] (2026-10-20, user: done) Buy **VPS Lite** (Chicago, Windows; annual if sure). Starter's 4 GB / 2 cores is too tight once accounts and the
      copier are added; move to Pro only if startup / reconnects get slow.
- [x] (2026-10-20, user: done) Ask Apex / Rithmic whether one login may be connected from two machines at once; plan for live on the VPS ONLY.
- [x] (2026-10-20, user: done) On the home PC: export the MultiCharts workspace(s) and the compiled signals (VB, ONB ADX30, EOS, Target Guard,
      Stop Guard, Bridge Monday) and note every chart's settings: inputs (VB 8, ONB `RiskPerTrade` 1100 / ADX 30 /
      StopAtrPct 0.25, EOS $500, Bridge 2 MNQ), bar size, session template (CME 24h), Exchange time zone, Bar Magnifier,
      Symbol Mapping `@MNQ -> MNQZ6`, Target Guard `StartBalance` / `TargetBalance` 53050.
- [x] (2026-10-20, user: done) On the VPS: install MultiCharts + the data feed + Rithmic connection, import the workspace and signals, check every
      input against the list above.
- [x] (2026-10-19) Same-result check: ONB on the VPS vs the PC report, Jan-Oct 2026: 77/77 trade days, 75 identical,
      2 differ by 1 tick (data). The others are assumed the same (user: VPS isn't for backtesting); just check their inputs
      and that the last few days' trade arrows on each chart look like the PC's.
- [x] (2026-10-20, user: done) VPS Windows: updates paused during market hours (set active hours / pause), sleep and screen-off disabled,
      MultiCharts set to start with Windows if the VPS restarts.
- [x] (2026-10-20, user: done) Switch over: turn auto-trading OFF on the PC charts, ON on the VPS charts (after 15:59 CT or on a weekend);
      watch the first live trade on the VPS (fill shows in Rithmic / Apex).
- [x] (2026-10-20, user: done) Keep the PC's MultiCharts for backtests only, logged in with data only (no live trading login), so it can't
      kick the VPS off Rithmic.

### Trade logger + auto journal (2026-10-19)
- [x] (2026-10-19) VPS: `C:\TradingLogs` created; Apex Trade Logger compiled and on every live chart (VB / ONB / EOS / MON_BR).
- [x] (2026-10-19) VPS: Git for Windows + clone to `C:\TradingRepo` + the scheduled push; test log arrived in `live/trades/`.

### Automatic health checks (2026-10-21)
- [x] (2026-10-21, user: done) **One time, outside market hours:** paste the updated [Apex_Trade_Logger.txt](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Apex_Trade_Logger.txt)
  (Raw button) into the existing "Apex Trade Logger" signal on the VPS and compile. Everything else runs by itself.

### New strategies (2026-10-23)
- [x] (2026-10-25, done: S47 v2 710 / 714 trades, Kusho v9 3,086 / 3,152, C03 3,439 / 3,490 match; `analysis/outputs/mc_parity_2026-10-25.txt`) Optional, only if you want them on the shelf: MultiCharts runs of `checks/candidates/s47_v2/S47_v2_fixed.txt` (new signal,
      not over FC 2B) and of Kusho v9 / C03 (reports .xlsx into `mc_reports/`).
- [x] (2026-10-26: #1 BLOWN; turn off its auto-trading / remove its charts on the VPS) **Account #1 is ~$398 above its trailing line:** one full VB stop at 8 MNQ (~$1,200) would end it. Your call (plan size kept
      2026-10-22); check the Apex dashboard each morning.

### Swing Target NQ v2 (your file + Codex's test, 2026-10-25: B, personal candidate; not Apex-legal as written)
- [x] (2026-10-25) Claude: v3 = v2 + break-even + holiday skip: [NQ_Swing_Target_v3.txt](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Swing_Target_v3.txt) ([raw](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Swing_Target_v3.txt)).
- [x] (2026-10-25, done: t 4.55, 0 overnight holds, matches Codex's ledger) You: MultiCharts backtest of v3 (1-min @NQ / OFB_BARS_NQ, Exchange CT, ClockShiftMin 0, IOG off, from Dec 2017, commission and slippage 0) with **List of Trades** into `mc_reports/` (`Backtesting Strategy Performance Report _ @NQ - 1 Minute Swing Target v3.xlsx`). Expect ~600 trades 2018-26, ~36 break-even exits, no trade on holiday sessions.
- [x] (2026-10-25, user: yes) After parity: your call on the swaps that bench better: 50K funded VB 2/1 -> 1/1 + ST 1 MNQ; 150K funded Dual Thrust 2 -> ST 2 MNQ. Not in the evaluations.
- [x] **Optional (for Codex's IFT_NQ5 test): export full-Globex up / down volume** with [NQ_UpDown_Exporter.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/tools/exporters/NQ_UpDown_Exporter.txt) on a 5-min @NQ chart (Exchange CT, 24h session, from 06/2017, home PC), files into `data/`; plus the IFT MultiCharts report with its List of Trades.
  (2026-10-28: done. Bar Magnifier rerun identical, trade volume confirmed: IFT = C, not for any plan.)

### Done
- [x] 2026-10-17: Docker Jesse + Antigravity installed on the user's PC and connected (MCP working). First blind-check task: when the user asks.

### Before Sunday 10/18 (test order 17:00 CT, Bridge Monday enters 19:00 CT)

### Dual Thrust v4 (your file, 2026-10-24: A, checker PASS WITH CONCERNS; personal plan; 150K funded slot given to Swing Target 2026-10-25)

### T_ONESIDE (your file, 2026-10-24: B, IN THE 50K FUNDED PLAN since 2026-10-28, checker PASS WITH CONCERNS; fade leg = small funded gain at 1 MNQ)

### GC_COMBO v2 (your gold files, 2026-10-24: C pending the MultiCharts report)

### PAPERTREND v2 (your description + report, 2026-10-24: B, checker FAIL narrow on deflated Sharpe; personal-plan candidate)

### BB_MRM (your file, 2026-10-25: C after the MultiCharts report; OUT of the personal plan (user 2026-10-25), paper forward log from 10/26)

### Antigravity's NQAlignedWeaknessShort (2026-10-20, C)

### Vault Break NR7 sizing (candidate, 2026-10-18)

### Trade logger + auto journal (2026-10-19)

### Automatic health checks (2026-10-21)

### Done
