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

- [ ] (2026-10-25, user requested) **Vault Break: rerun the August 27–October 23 research backtest** with one-minute Bar Magnifier,
  the documented reference limit-through assumption, and explicit actual commission/slippage; preserve the same rule and quantity.
  Export the report/settings and matching NQ day/overnight minute data. Reconcile broker fills/fees separately.
  See `agents/codex/results/vb_aug_oct_report.md`. Research chart only; no live/VPS changes.
- [x] (2026-10-20) Account #2 bought and set up on the VPS: second chart set (VB, ONB ADX30, EOS, Bridge) on the new account, logger tags `-2`, StartBalance 50000.
- [ ] **Fri 10/23 (and every Friday): export the weekly MultiCharts reports into `live/`** and tell Claude (it runs
  `analysis/live_vs_backtest.py --all live/` and the drift alarm).
- [ ] When account #1 passes ($53,000): turn auto-trading off on that account.
- [x] (2026-10-20, user: done) **Now: Rithmic copier off (or #2 removed as follower)** while set 2 auto-trades, or #2 trades double size. Copier
  waits until several funded accounts (2026-10-20).
- [ ] **~Mon 10/27: account #3** (150K No-Activation, $249).
- [ ] Optional: rerun the ONB ADX30 MultiCharts backtest once with the new code (should be nearly identical).

## ES MOC Follow (funded candidate, 2026-10-17)

- [x] (2026-10-17, confirmed 199/199) MultiCharts backtest: [ES_MOC_Follow.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/ES_MOC_Follow.txt)
  on a 5-minute **@ES** chart (Exchange time, 24-hour session, Bar Magnifier 1 min, from Jan 2018, NumContracts 1, no costs);
  save the report as "mc_reports/Backtesting Strategy Performance Report _ @ES - 5 Minutes ES MOC Follow.xlsx" and push / send it.
- [x] (2026-10-17, PASS on the rule; its clock ran 1 min early, see agents/results/TASK_09_VERDICT.md) Antigravity: Task 09 blind check (pull `agents/tasks` and the `ES_1min_*.csv` files first).
- [ ] When funded: ES MOC Follow (IN THE PLAN since 2026-10-17) on a 5-min MES chart, NumContracts 2, Symbol Mapping `@MES -> MESZ6` (roll with MNQ). Vault Break funded: `NumContracts` 2, `FlaggedContracts` 1 (decided 2026-10-17).

## Relative Strength NQ / ES (your new strategy, 2026-10-20: B, checker PASS WITH CONCERNS)

- [x] (2026-10-20, done: 1,157 days match, P&L corr 1.000) MultiCharts backtest for the trade-by-trade check: [RelStrength_v3.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/checks/candidates/relative_strength/RelStrength_v3.txt)
  (your code, unchanged) on a **1-minute @NQ chart with 1-minute @ES as Data2** (same feed, CME 24h session, Exchange
  time = CT, first RTH bar 08:31), data loaded from **Sep 2017**, default inputs, **commission and slippage 0** (Claude adds
  costs), Intrabar Order Generation off. Save as "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Relative Strength.xlsx"
  and push / send it.
- [x] (2026-10-20, you: include it in all relevant plans) In the plans: 50K funded longs only 1 MNQ, 150K funded both sides 1 MNQ, personal account; not in evaluations.
- [ ] When an account is funded: add [NQ_Relative_Strength.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/funded_strategies/NQ_Relative_Strength.txt)
  as a NEW signal on a **1-minute MNQ chart with 1-minute @ES added as Data2** (same feed, Exchange time, first RTH bar 08:31,
  IOG off), 50K: `TradeDir` 1, `NumContracts` 1; 150K: `TradeDir` 0, `NumContracts` 1; Trade Logger tag `RS`.

## Antigravity's NQAlignedWeaknessShort (2026-10-20, C)

- [x] (2026-10-20, confirmed 216/216) MultiCharts backtest: [NQ_Aligned_Weakness_Short.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/checks/candidates/aligned_weakness_short/NQ_Aligned_Weakness_Short.txt)
  on a 1-minute @NQ chart with 1-minute @ES as Data2 (same feed, CME 24h, Exchange time, first RTH bar 08:31), data from
  Sep 2017, commission / slippage 0, IOG off; save as "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Aligned Weakness Short.xlsx".

## Journal (Obsidian)

- [x] (2026-10-17, done) One-time setup: follow [journal/README.md](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/journal/README.md) (separate clone in `C:\TradingVault`, Daily notes + Templates plugins).
- [ ] From Mon 10/19: a daily note each trading day; run `journal\sync.ps1` and tell Claude "read my journal".

## Vault Break NR7 sizing (candidate, 2026-10-18)

- [x] (2026-10-18, confirmed 135/135 sessions) MultiCharts backtest of [NQ_Vault_Break_SP.txt](https://raw.githubusercontent.com/Dartdark/thebeginning/claude/nq-trading-strategy-params-5h9d20/apex_strategies/NQ_Vault_Break_SP.txt)
  on a 30-min **@NQ** chart (same settings as before, from Jan 2018), inputs **NumContracts 1, NR7Contracts 2, FlaggedContracts -1**,
  no costs; save as "mc_reports/Backtesting Strategy Performance Report _ @NQ - 30 Minutes VB NR7.xlsx" and push / send it.
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
- [ ] Reports: each Friday export the weekly MultiCharts reports on the VPS and copy them to the PC (remote-desktop
      copy / paste) into `C:\TradingVault\live\` before 16:47 CT (or later: git on the VPS exporting straight into `live\`).
- [x] (2026-10-20, user: done) Keep the PC's MultiCharts for backtests only, logged in with data only (no live trading login), so it can't
      kick the VPS off Rithmic.

## Trade logger + auto journal (2026-10-19)

- [x] (2026-10-19) VPS: `C:\TradingLogs` created; Apex Trade Logger compiled and on every live chart (VB / ONB / EOS / MON_BR).
- [x] (2026-10-19) VPS: Git for Windows + clone to `C:\TradingRepo` + the scheduled push; test log arrived in `live/trades/`.

## Automatic health checks (2026-10-21)

- [x] (2026-10-21, user: done) **One time, outside market hours:** paste the updated [Apex_Trade_Logger.txt](https://github.com/Dartdark/thebeginning/blob/claude/nq-trading-strategy-params-5h9d20/apex_strategies/Apex_Trade_Logger.txt)
  (Raw button) into the existing "Apex Trade Logger" signal on the VPS and compile. Everything else runs by itself.

## Promising strategies awaiting verification (user, 2026-10-27)

**Standing rule:** when a reviewed strategy has documented merits but its results or implementation are not yet verified,
add it here for later review. Record the merit, what is missing, the smallest next check and the source review; merge
duplicates. Keep reported results labelled as claims. Missing information alone does not make a strategy promising.
A queue entry does not add it to a trading plan or start a backtest; review when prerequisites arrive or the user prioritizes it.

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
- [ ] **Thu 12/10 (after the close): roll Symbol Mapping on the VPS** `@MNQ (dxFeed) -> MNQH7` (was MNQZ6; before the
  December roll ~12/11), then auto-trading off / on and a 1-MNQ test order per account. Reminder set: 12/10 08:00 CT
  (scheduled-jobs session).
- [ ] **Mid-December gate:** ~40–70 live trades at ≥ 75% of backtest and no ALARM → start scaling (FUNDED_PLAN.md).
- [ ] Optional: add an `OPENAI_API_KEY` to the environment's secrets for a second, different-lab strategy checker.

## Done

- [x] 2026-10-17: Docker Jesse + Antigravity installed on the user's PC and connected (MCP working). First blind-check task: when the user asks.

## Reminders

Claude reminds you every **Sunday and Wednesday at 10:52 CT** (Central). Since 2026-10-20 the reminders run in the
separate session 'Scheduled jobs (journal, Friday review, reminders)', together with the 16:40 CT journal trades and the
Friday review. Say "stop the reminders" to turn them off, or ask for a different schedule.
