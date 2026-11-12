# New-chat brief (rewritten 2026-10-29; Now updated 2026-11-11): read this first

Opener for a new chat: *"Read `NEW_CHAT_BRIEF.md`, then `CLAUDE.md`, `TODO.md` and `LESSONS.md` in
github.com/Dartdark/thebeginning (branch `claude/nq-trading-strategy-params-5h9d20`) and continue from there."*
Read `MULTICHARTS_PITFALLS.md` before writing MultiCharts code. The full history of this brief (up to 2026-10-28) is in
`archive/brief_history_2026-10.md`; ticked to-dos are in `archive/TODO_done_2026-10.md`.

## Now (2026-11-11)

- **One live account: #5 APEX-681524-05, 150K evaluation** (bought 11/10; floor 146,000, target 159,050, DLL $2,000).
  Charts (tags `<name>150-5`): ONB, EOS, MON_BR (5), Twin (2), DT (2). **VB removed from the evaluation 11/11 (user):** it blew the DLL
  twice (11/11: −$2,257.50 on one stop). Plan docs, expected_setup.json and dashboards updated; the user still has to close the VB chart.
- **11/11 result:** −$2,455 (DT −$200, VB −$2,257.50), DLL hit, account paused. Balance $147,998.08 = **$1,998 above the floor**, less
  than one ONB stop ($2,750). Proposed: ONB `RiskPerTrade` ~1500 until it recovers (waiting on the user). Chart rows after 10:30 were
  rejected orders (735), not trades. DT guard showed broker 2 / strategy 0 all afternoon; equity flat, so stale; user to confirm flat.
- **Overrides 11/10-11/11** (`live/overrides.csv`): Twin closed early by hand +$261 (its target would have made +$536); manual re-entry +$192.
- **Fixes 11/11:** Apex_Chart_Guard sends the target limit only within `TgtNearPct` (1%) of the price (a far limit was rejected 10x and
  MC switched Twin off): **user must recompile it and turn Twin back on while flat.** `live/vps/push_trade_logs.ps1` line 72 parse
  error (my edit; logs were down all day) fixed and parse-checked with pwsh. `.claude/settings.json` allows the pwsh download/parse check.
- **Scheduled jobs RESUMED 11/11:** pre-market check 08:21 CT and 16:40 journal/dashboard. Watch that tomorrow's runs see the logs.
- **Budget:** −$605 (eval #5 −$250, Claude −$20; MC already counted). Dashboard dataset 'ledger' v2.
- **Jump Fade ADDED to #5 11/12 (user decision): `apex_strategies/NQ_Jump_Fade.txt` v3 with MinVolRatio 0 (= the unfiltered version), 2 MNQ**, 1-min @MNQ 24h chart. Eval bench (VB out): fresh +1.3 pt, from #5's state +1.0 pt (band +0.1/+2.0). Worst trade ~$1,460 at 2 MNQ vs the $1,998 cushion. **v4 (11/12): kill switch + heartbeat added (tag JF150-5, in expected_setup.json); MinVolRatio default 0; no cushion guard. User confirmed 11/12: v4 compiled and set, Chart Guard recompiled on all #5 charts.** 11/12 user: VB chart closed, DT flat, ONB RiskPerTrade left as is (declined ~1500).
- **Drift-burst fade + order-flow turn 11/12 (user's combination 1):** F. Reversal 62-64% from the after-the-fact peak, a coin flip once the turn is confirmed; all four markets PF 0.5-0.6. Combinations 2-3 still to come from the user.
- **Combination 2 (calendar-spread feedback + queue imbalance) 11/12:** D, not testable (no second-month data; a 500 ms HFT edge); NQ queue imbalance predicts nothing at 1-15 min (corr -0.002).
- **Combination 3 (queue signal + quoting + adverse selection) 11/12:** D, no test (engine dead at our scale; market making needs co-location). E34: 66-89% of CME limit fills are adverse -> re-test small-target rules with targets needing 1-2 ticks through.
- **11/12 later:** IBS v6 (no stop, exit 0.7) PF 1.70, both periods better, holds on NQ; still fails the personal book rule (TIER_LIST C+). Jump fade MultiCharts code `apex_strategies/NQ_Jump_Fade.txt` (port-verified, not compiled; forward log / sim only).
- **IBS Globex ES v5 11/12 (user's forum post + file):** rebuilt to the post (306 vs 301 trades); our costs PF 1.46, 2018-22 PF 1.16 / 2023+ 1.93; personal book +1 MES fails 2018-22. TIER_LIST C (S30 is the better version). Sweep look-ahead bug found and fixed (LESSONS).
- **Jump study 11/11 (user: pino1 screenshot, 82% wins / PF 1.41, three CFM papers):** not reproduced. Rebuilt as a 5-min jump-score rule: the 0.3R shape gives 78% wins, PF 1.05 (t 0.6);
  30-min follow versions passed 2018-22 (t 3.1-3.4) and failed the one holdout look (PF 0.88-0.94). TIER_LIST D (2 rows), `analysis/outputs/jump_final_output.txt`, `checks/candidates/jump5/`.
  Post-hoc lead: morning jump fade 07:00-09:59 CT (WATCHLIST #40, t 2.7 vs bar 3.70; forward log, MNQ only). Not asked yet: pino1 for his rule / trade list.
- **Research 11/10:** satellite Cushing, 6J pivot continuation, curve papers, 5 papers, API pre-EIA: rows in TIER_LIST (nothing promoted).
  Codex has the API/EIA data task. Older-data validation BENCHED (MC data only from 11/2016).

## Earlier (2026-11-05; research update 2026-11-09)

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
  2.3% per strategy at the same payouts: adopt for funded (FUNDED_PLAN 'Cushion cap'). Code written 11/08 (UseCushion, reads Rithmic Equity; 7 funded files;
  not compiled). Rithmic Equity includes open P&L (verified from ACCT logs). funded_bootstrap.PLAN VB_N 3 -> 2.
- **Codex weekly review 11/06 (read 11/08), 4 findings on Claude's code, all handled:** (1) evaluation engines locked the floor at
  start + $100 (funded rule); Apex evaluations keep trailing: corrected engine (`cushion_cap_bench.run(evalrule=True)`,
  `analysis/outputs/eval_rule_fix_check_output.txt`): **50K plan pass 50.0 -> 49.0%, 150K 41.0 -> 35.9% (fee per funded
  $608 -> $693)**; ranking of sizes unchanged. **All engines fixed 11/08** (combine_levers_test, plan_150k_test, portfolio.challenge,
  onb_cushion, vb_cushion_sizing, profit_cap, twin_150k; funded engines keep the PA lock, correct) and 15 plan benches rerun: budget
  ramp 150K pass 38.1 -> 33.4% (75% edge 28.9 -> 24.4%), 2027 median (job ends, 1 a day) $252k -> $237k / $89k -> $72k; P(no funded
  by Dec 31) 14% / 31% unchanged; same-day batch fails together 48 -> 54% (firm_risk); every size / cap / filter ranking unchanged.
  **Rerun 11/09 (after Dot's review): evaluation parts of real_fee_bench and replace_weak_bench (rs_trades.csv regenerated) and
  eval_sizing_bench part C (g24_ext.pkl linked to g24.pkl, NQ to 11/04): 50K combine pass 50.1 -> 49.0%; every replacement / fee /
  size ranking unchanged; the live stretch fails at every size (as live). Outputs `real_fee_bench_combine_output.txt`,
  `replace_weak_bench_combine_output.txt`, `eval_sizing_bench_output.txt`.**
  Still not modelled: DLL fill at the limit, 30-calendar-day clock. (2) held-path gaps: 4% of long-after-green trades, result unchanged.
  (3) Bertola / long-after-green charged commission twice: fixed, reruns saved (verdicts unchanged). (4) green-day filters
  relabelled exploratory.
- **Twin Continuation 150K added to the 150K plan 11/08 (user):** `apex_strategies/Twin_Continuation_150K.txt`, 2 MNQ, eval + funded;
  not compiled yet (TODO 150K section). Python port gained `v21=True` (live holiday rules; 0 session-break crossings).
- **Research day 11/08 (late; full rows in TIER_LIST / WATCHLIST / DEVELOPMENT_PROCESS 'Ingredient register'):**
  - **Plan changes (user):** personal **Overnight Tick 1 -> 2 MNQ** (book median year +$2.2k, DD +$0.1k; PORTFOLIO, TODO). **FINRA
    short-volume longs PENDING at 1 MNQ** (personal; WATCHLIST #32; long NQ the day after a high Nasdaq off-exchange short ratio, 08:31 ->
    14:55, stop 0.5 ATR; $661 / t 3.51, random-day longs $138; **MultiCharts-confirmed 373/374**, report in mc_reports/; post hoc ->
    ~6 months forward log; data `data/finra/`, file `checks/candidates/finra_longs/NQ_FINRA_Short_Volume_Longs.txt` regenerated by
    `analysis/finra_mc_export.py` when FINRA days are appended). Apex: no FINRA version fits (all-day holds hurt the 150K books).
  - **Ingredient ablations of all 17 plan pieces (rounds 1-5 + Codex's ONB/FC/T):** every live version held up; ~60 variants, 1 adopted.
    Engines: open-breakout distance (VB, DT, PT, noise), morning momentum (Twin), closing flow x VIX (OT), NQ beyond ES (RS), forced-flow
    windows (LDF 14:00-14:30, EOS expiry open, NFP overshoot, CL weekend gap, Monday). Moving engines to CL / GC / ZN / ES / YM failed.
  - **New data tried:** leveraged-ETF flows (fade on NQ C, WATCHLIST #31, failed to replicate on ES / YM / CL / GC), FINRA (above),
    NY Fed RRP (F), VIX9D / VIX (C), Treasury buybacks on ZN (C/D), order-flow absorption (D; Codex REJECT too). Codex's 11/08 data copied
    to `data/codex_20261108/`; ProShares S&P / Dow funds in `data/letf/`; RRP in `data/nyfed/`.
  - **Fixed:** `twin_continuation_bench.grids` marked non-NQ paths at NQ's $20 a point (Codex): `pv=` added, MO-on-ES rerun (still C).
    Dual Thrust was already MultiCharts-confirmed (stale 'pending' notes fixed). Shared bench helper `analysis/bench150.py`.
  - **Watch:** #31 LETF fade, #32 FINRA longs, #33 ONB ML price-term decay (refit only pre-registered on 2018-22). Capital-expansion
    bench + Swing Target 2nd MNQ on shorts only. Job starts 11/10, first payday likely 11/17 (not 11/13).
- **Evaluation work 11/09:** diagnosis (`analysis/eval_failure_diag.py`): 89% of failed 150K evaluations die from one big VB / ONB stop
  (each ~ the $2,000 daily limit) after one daily-limit pause. A capped evaluation set (`analysis/eval_set_builder.py`) cuts fails 60 -> 48%
  but time-outs rise 2 -> 16%: holdout pass 43.2% vs 43.4% (D). **User 11/09: the Apex evaluation has a 30-day limit**, so a time-out is a
  lost fee like a fail and the current concentrated set stays. Screen for future evaluation add-ons: mean per unit of variance, low
  correlation with VB / ONB, flat or positive on their stop days.
- **Late 11/09 (user decisions):** **150K evaluation from the next purchase: VB 20 -> 15 MNQ + Dual Thrust 2 MNQ (DT150)**
  (`analysis/vb_vs_dt_eval.py`: all starts 38.3 -> 38.9%, 2025-26 starts +4.0%, band +0.5 / +7.5; quarterly check; FUNDED_PLAN + TODO).
  Stop-day screen / vol gap fade (D), eval-profile screen (only Twin fits), near misses (none). **Personal: ZT continuation EntryZ 1.25
  at 1 MNQ, IN while watched (WATCHLIST #36)**: user's vol-normalised-Z paste; as coded (EntryZ 2) it barely trades; ablation: engine =
  vol-scaled EMA distance, earns only on Twin-active days; plateau 1.05-1.30; book median year +$1.4k, DD p95 +$0.2k; MC check pending
  (`checks/candidates/zt_continuation/`). Rejected: Donchian + LWTI repaste (D, already tested 10/23), Overnight v2 trend + vol sizing (F).
- **11/09 evening:** MultiCharts confirmed S30 0.10 (169/169), ZT 1.25 (604/604), Ricochet T80 (99.2%). S30 0.10 strategy checker FAIL
  10/11 (G9 PBO 0.71: 0.10 is the in-sample peak; plan on the 0.20 level, 1-min-marked DD $60.9k per NQ). **FINRA longs IN the personal
  plan at 1 MNQ while watched (user, like ZT).** Progress 11/07 -> now (`analysis/outputs/progress_books_output.txt`): 150K evaluation
  pass 36.3 -> 38.9% (2025+ starts 35.4 -> 41.5%); funded 150K 2y $19,988 -> $20,031 (Twin ~neutral); personal core book median year
  $26.3k -> $32.7k, DD p95 $4.86k -> $5.30k, return/DD 5.42 -> 6.17 (full book $40.5k -> $46.8k). Budget ramp rerun (`analysis/outputs/progress_ramp_output.txt`, same schedule as 11/08): 2027 payouts median $237k -> $296k (75% edge $72k -> $92k), first payout Mar 01 -> Feb 09, P(0 funded by Dec 31) 14 -> 12%. Your ONB ML chart code was pre-v2:
  re-import before funded use.
- **11/09 night, automation (user: 'nothing manual'; NOT compiled yet):** 150K evaluation finish mode (`UseFinish`, half size from
  $156k) in the 6 evaluation files; ONE helper per chart `apex_strategies/Apex_Chart_Guard.txt` (replaces logger / monitor /
  target guard / stop guard, same rows); cushion guard on all 13 funded files; account read from each chart's Auto Trading gear
  (GetAccountID), peak from VPS files (`live/vps/cushion_peak.ps1`), so no AccountName / PeakSeed typing; FINRA signal from the VPS
  task FinraDaily (`live/vps/finra_daily.ps1` -> flag files, strategy `UseFlagFiles`); weekly VPS restart task removed.
- **Copier (user 11/09): Rithmic's built-in copier, two leaders (evaluations / funded), followers 1x.** Charts on the leaders only;
  auto account rules (no per-account inputs); group sizing via VPS files: funded = weakest cushion, evaluations = finish mode when
  the group mean is +$6k (40.0% vs 40.9% per account). Chart guard scans all accounts at 15:55 (needs testing: GetRTAccountEquity
  on accounts no chart trades).
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
