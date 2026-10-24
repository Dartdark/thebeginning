# New-chat brief (updated 2026-10-24): read this first

Paste this into a new chat: *"Read `NEW_CHAT_BRIEF.md`, then `CLAUDE.md`, in github.com/Dartdark/thebeginning (branch
`claude/nq-trading-strategy-params-5h9d20`) and continue from there."*

## State on 2026-10-24 (read this block first; the rest of the file is background)

- **Live (Apex, combine set VB 8 / ONB ADX30 $1,100 / EOS $500 / Bridge 2):** #1 APEX-681524-01 $49,899.44 (~$398 above
  its trailing line; user keeps plan size), #2 -02 $49,424.18. #3 150K No-Activation planned ~10/27. Gate ~mid-December
  (live >= 75% of backtest, no drift alarm) before scaling +2 x 150K a week to 20. Funded plan unchanged (10 strategies,
  cushion sizing table in `funded_strategies/FUNDED_PLAN.md`).
- **Research this week:** FC 2B (A), S47 v2, OB v2, Kusho v9, S30 IBS (B), C03 (C). None improves either Apex plan
  (funded plan near the payout cap; combine limited by drawdown vs target); replacing the 'weak' diversifiers (ES MOC,
  NFP, EOS, LDF) or EOS / Bridge in the combine is worse. Personal-account ladder: `personal_strategies/PORTFOLIO.md`.
- **Process changes (user):** forward log is discretionary; a candidate that clears every test incl. a plan-bench gain
  goes straight into the plan (`DEVELOPMENT_PROCESS.md`). Forward logs (paper) from 10/26: FC 2B, S47 v2, Kusho v9
  (roll-adjusted entry), S30 (`agents/codex/FORWARD_LOG.md`, frozen bands). Weekly Claude-Codex cross-review every
  Friday (`agents/codex/TASK_weekly_cross_review.md`, `agents/cross_review/`); first round 2026-10-23 closed 6 items.
- **Codex:** GPT-6.1 Sol ('Light'), builder on `codex/work`; reads / writes files only. @codex PR-mention mailbox tried
  2026-10-24 (PR #2, closed unmerged): connector can't see the environment; stopped (`agents/codex/STATUS.md`).
- **Open for the user:** Sun 10/25 after 17:00 CT the `Apex Account Check` indicator on both charts (`TODO.md`); Friday
  exports into `live/` (MC reports, order tracker CSV, 1-min data); 11/06 FC 2B re-export; optionally turn off Codex's automatic / security reviews for the repo.
- **2026-10-24 (Claude):** real micro fees ($1.04 per round trip, from the Apex fills) on the benches: combine 50.1% ->
  49.8%, funded plan −$96 over 2 years, no past decision flips (`analysis/real_fee_bench.py`). Twin marked daily in the
  personal ladder: no change. **Dual Thrust v4 (user's file): A** (rebuild $140 per NQ, t 4.4, 9/9 years; checker PASS
  WITH CONCERNS, replica identical) **in the 150K funded plan at 2 MNQ and the personal plan (user)**: 150K
  funded bootstrap 6 payouts by day 226 vs 250, 1y +$1,400, blown 1.8% -> 2.2%; not on 50K (ties) or evaluations (worse);
  personal (14 pieces) $24.4k a year, return/DD 8.2, capital $25k. MultiCharts check needed before a 150K account trades it. MultiCharts export optional (`TODO.md`). S47 / Kusho loaders
  now place trades by date (old CSV rows were on a 2016-09-29 grid).
- **Codex 2026-10-24 (codex/work 541d111):** 13 studies of uploads, none changes a plan: S03 v2 B (no placement), NQDB2 /
  R2Vault C, ORPullback / Anson D, night volume switch = T_ONESIDE (WATCH); 6 source-only reviews need code / data
  (Valeris 848, GC risk-adjusted, noise-band CODE.txt, PROP ORB, GC_COMBO v2, Overnight TickRSV). `agents/codex/STATUS.md`.
- **Open for Claude:** automatic cushion sizing after the account check; Dual Thrust MC check when the report arrives.
- **Every reply ends with a PushNotification** (CLAUDE.md). Scheduled jobs (journal 16:40 CT, Friday review, reminders)
  run in the session 'Scheduled jobs' (session_014DKffATms37kZigaa2xR2P), not in a new chat.

## Who / what

- Algo trader running MultiCharts (PowerLanguage) on **Apex 50K** accounts via **Rithmic** (data dxFeed). Apex only
  (ignore Topstep). Flat by 15:59 CT; $2,000 end-of-day trailing drawdown (locks at $50,100); combine: $3,000 target,
  $1,000 daily loss limit.
- Goal: **funded payouts** (6 payouts = $13,000 per account), reached as fast as possible.
- **Business plan (2026-10-16): `reports/Trading_Business_Plan.pdf`** (rebuild: `python3 reports/build_business_plan.py`): account
  choice (test on single 50K EOD $59 -- 5-pack evals all start at purchase, so they'd share one outcome; scale with 150K no-activation), projections, roadmap, risks, settings per account type.
- Long-term path (user, 2026-10-15): Apex = live test bench and funding source; proven strategies and Apex payouts move to a
  personal account (`DEVELOPMENT_PROCESS.md` 'Strategy lifecycle').
- **The plan, in priority order (agreed 2026-10-16; full version `reports/Trading_Business_Plan.pdf`):**
  1. **Prove the edge live:** #1 50K EOD (since 10/12), #2 50K EOD Tue 10/20 ($59 single; 5-pack evals all start at purchase),
     #3 **150K No-Activation** ~10/27 ($249, tests the 150K settings / copier master early). Gate ~mid-December: ~40–70 live
     trades at ≥ 75% of backtest, no ALARM.
  2. **Scale Apex:** ~$20k set aside for evaluation fees; +2 x 150K No-Activation a week to 20; 50K slots keep cycling until
     their first funded account pays all 6 ($13,000) or blows, then switch to 150K; pause adding if cumulative cash < −$20k.
     Sim (`analysis/ramp150_test.py`): year 1 ~$175k, 3 years ~$1.03M (75% edge: ~$96k / $743k, bad case −$33k).
  3. **Personal account from the first Apex payouts** (expected ~mid/late Feb 2027), ~$10k at 1/10 size, not from savings;
     full 1-NQ size needs ~$100k (DD $24k); add Twin there (stop cap 1 ATR).
- Preferences: forced / scheduled flows (they work here; price patterns fail), low correlation, longs and shorts
  analysed separately. Always give **direct GitHub links + raw links** for code to paste into MultiCharts.
- Working rules, testing standard and branch rules are in `CLAUDE.md` (push every commit to
  `claude/nq-trading-strategy-params-5h9d20`, `claude/quirky-noether-4dla64` and the session's own branch).

- **Setup since 2026-10-19:** repo is PRIVATE (raw links need a GitHub login; use `git pull`). A local Claude Code session
  on the user's PC (folder `C:\TradingVault`, rules in `cowork/INSTRUCTIONS.md`) does chores: daily journal note from the
  user's answers, `journal\sync.ps1`, copying weekly MultiCharts reports into `live/`, papers into `papers/`. It never
  touches MultiCharts / Rithmic / Apex / The Bridge (since 2026-10-19 it may look at MultiCharts, and click to navigate
  views on the PC's copy once live trading runs on a VPS; never orders, inputs or auto-trading). Cloud sessions do research and the Friday review (scheduled Fri
  16:47 CT). `LESSONS.md` = short rules learned the hard way. Live: test order filled 10/18; Bridge Monday first live run
  10/18 19:00 CT; account #2 Tue 10/20.
- **Scheduled jobs (2026-10-20):** run in their own small session 'Scheduled jobs (journal, Friday review, reminders)'
  (session_014DKffATms37kZigaa2xR2P, repo attached): journal trades weekdays 16:40 CT, Friday review 16:47 CT, to-do
  reminder Sun/Wed 10:52 CT. Fresh-session-per-run doesn't work (new sessions can't reach the private repo).
- **Account #2 (2026-10-20):** a second 50K evaluation on the VPS, its own chart set (no copier: Rithmic copy trading not
  enabled yet), logger tags VB-2 / ONB-2 / EOS-2 / MON_BR-2. Rejected-order stop set to 10 per chart.
- **Rithmic copier (2026-10-20):** user enabled it in R|Trader Pro, then decided (agreed): NOT for evaluations. Each
  evaluation keeps its own chart set (own Target Guard / StartBalance; a copier would let #1's Guard close #2's trades and
  stop #2 when #1 passes). Use the copier later, when several funded accounts run the same plan, grouped by cushion
  (0.5 multiplier below a $1,500 cushion). Never run the copier and a follower's own chart set at once (double size).
- **First Apex daily-loss-limit day (2026-10-19):** VB long 8 MNQ at 10:30 CT reversed; Apex's $1,000 daily limit closed it
  at -$1,017 (11:01 CT) and locked the account ('Account is done for day'); MultiCharts kept re-sending VB's exits (rejected).
  Within the plan (the combine sim models the limit). VB size vs the limit (`analysis/combine_vb_size_test.py`): 6 MNQ
  ($900 risk) 49.2% pass vs 8 MNQ 50.1% (4: 48.2%, 10: 50.4%): keep 8. After any Apex lock, reset charts before the open.
- **VPS + trade log (2026-10-19):** QuantVPS Lite (Chicago, Central clock) runs MultiCharts with Rithmic; ONB backtest on the
  VPS matched the PC (75/77 identical, 2 by 1 tick). Every live chart has `Apex Trade Logger` (writes C:\TradingLogs\YYYYMMDD.csv);
  Task Scheduler 'PushTradeLogs' pushes it to `live/trades/` at 16:10 CT (tested); Claude's 16:40 CT weekday task runs
  `analysis/journal_trades.py` into the day's journal note.
- **Apex automation (2026-10-19):** some 2026 web sources say Apex bans automation; the user confirmed automation is
  allowed for their accounts. Resolved; plan unchanged.

## Latest (2026-10-17)

- **Friday review 2026-10-23 (week of 10/19):** live = Vault Break only. #1: 10/19 −$1,025.66 (Apex daily-loss lock), 10/21
  −$575.82 → $49,899.44 (~$398 above its trailing line; user keeps plan size). #2: 10/21 −$575.82 → $49,424.18. 10/20 logged
  but not filled (@MNQ symbol mapping, fixed). 10/22-23 no trades. No weekly MultiCharts reports in live/, so no
  live-vs-backtest / drift run (3 live VB days is too few to judge anyway). Research this week: FC 2B (A), S47 v2, OB v2,
  Kusho v9, S30 IBS (B), C03 (C) — none improves either Apex plan (cap-bound funded plan; combine drawdown vs target);
  replacing the 'weak' diversifiers (ES MOC, NFP, EOS, LDF) with FC 2B / S47 / Kusho is worse or a tie, and replacing EOS or
  Bridge in the combine lowers the pass rate (50.1% → 45-49%) (`analysis/replace_weak_bench.py`): plans unchanged.
  Personal portfolio built (`personal_strategies/PORTFOLIO.md`); accounts → income table in `funded_strategies/FUNDED_PLAN.md`.
- **FC 2B (user's opening-drive strategy, 2026-10-23):** MultiCharts-confirmed (v2 with holiday flatten + entry-bar stop),
  $275 per NQ, t 4.0, checker PASS WITH CONCERNS → A; but the 50K funded plan is near the payout cap and the combine gains
  nothing, so it is NOT added; forward-logged (`agents/codex/FORWARD_LOG.md`), personal-account candidate.
- **Codex break test (2026-10-22, `agents/codex/results/REVIEW_break_vb_onb_and_rest.md`):** ONB ADX30 bends under noise /
  indicators / timing / execution (no change); VB parity 97.5% because MultiCharts fills targets with 1 tick through (Python
  needs 1 point, stricter); VB stress rerun pending. Codex's RSI/Bollinger and XAU gold screens: F.
- **Stack stress test (2026-10-22, `analysis/stack_stress_test.py`, after Kevin Davey's Feb-2018 story):** the funded plan's NQ
  lines at full 50K size, 2018-26: worst day −$1,275 (2025-11-17), no day below −$1,500; Feb 2018 −$638, Mar 2020 −$562,
  Apr 2025 −$968. Worst 5-day stretch −$3,333 (to 2026-10-02): multi-day runs, not single days, threaten the $2,000 trail
  (cushion sizing + the bench's 6.7% blow-ups already cover them). Theoretical 'every line's worst day at once': Mon −$4,088,
  Fri −$3,737, Tue/Wed −$2,528 (never happened). The worst days cluster in 2025-26 (bigger $ moves). No change (overlap
  cap tested worse); recheck if a single real day goes below −$1,500.
- **Account #01 near its trailing limit (2026-10-22): user keeps it at plan size.** Balance $49,899.44 vs failure line
  ≈ $49,500.92 (≈ $398 room after 10/16 +$1,500.92, 10/19 −$1,025.66, 10/21 −$575.82); #02 $49,424.18 (≈ $1,424 room).
  Cushion sizing on the combine was tested and doesn't help (`combine_levers_test`). 10/20 no-fill = orders sent as
  `@MNQ` (mapping not applied); 10/21 filled on both accounts (`live/orders_20261020_21.md`).
- **Antigravity's Vault Break Combined (HYP-025, 2026-10-21): D, not adopted.** Its 12:30 CT last-entry + 0.5-ATR VWAP
  stretch cap: design t 3.21 vs 2.71 but 2023+ t 2.46 vs 2.66 and −$3.4k a year; removed trades make money (+$42, t 1.1);
  DD cut = random removal (P 0.50); its MultiCharts code used a 30-min ATR and left the entry bar unprotected.
  Review `agents/results/VB_COMBINED_REVIEW.md`; its 'microstructure laws' are post-hoc stories, not adopted. Live VB unchanged.
- **Antigravity's role (user, 2026-10-20): strategy builder by default** (its brief now shows the plan's hours and
  `agents/tasks/plan_daily_pnl.csv` so it aims at gaps); blind checker only in a fresh conversation with task text only.
  Its strategies today: NQBreakoutATR F, NQIntradayMR F, NQIBBreakout C (overlaps VB). Each mistake caught is written into
  its rules (full 2018-26, costs, flat, random entries, t >= 2.5 on 2018-22 + positive 2023-26, per-contract $).
- **Antigravity's NQBreakoutATR (its first block-built strategy, 2026-10-20): F.** Our rebuild 2018-26: $55 per NQ, t 1.5,
  5/9 years, 2025-26 −$51k, random-entry p 0.11; its report used 2019-24 only; the filter adds nothing; profit = overnight holds.
- **Relative Strength NQ / ES (user's new strategy, 2026-10-20): B, checker PASS WITH CONCERNS.** Rebuild t 4.0, $306 per NQ,
  9/9 years, holdout holds, random side p 0.002, the ES adjustment is what works. Concerns: top 5% of trades carry the
  profit, 9:00 decision only (9:30 t 1.3), shorts weak since 2023. Funded bench + 1 MNQ: faster to 6 payouts (278 -> 250
  days) but blown +1.3 pt; longs only +0.5 pt. Optimisation (pre-registered, design 2018-22): nothing beats the user's
  settings; VXN regime splits strongly (high $508 vs low $94 a trade) -> WATCHLIST #24. MultiCharts check postponed (user
  can't backtest while live). **In the plans (user, 2026-10-20):** 50K funded longs 1 MNQ (bootstrapped: 6 payouts in 258 vs
  278 days, blown +0.5 pt), 150K funded both sides 1 MNQ, personal account both sides; NOT in evaluations (lowers the pass
  rate). File `funded_strategies/NQ_Relative_Strength.txt` (+ stop guard, 2027 holidays). FUNDED_PLAN.md section.
- **Building blocks program (user, 2026-10-20):** build strategies from entry / exit / filter blocks (Antigravity's
  catalog on `antigravity/jesse`: 10 entries, 10 exits, 143 filters, plus our own filters). Library `analysis/blocks.py`.
  Step 1 (entries alone, pre-registered, 64 trials, `analysis/blocks_step1_test.py`): 62 F; only E9 SMA 10/50 cross SHORT
  passes (NQ $129, t 2.4, holdout +; ES weaker) = C, about chance level. Next: Step 2 = Apex-fit exits (ATR stop / target /
  trail / time / 15:55) on E9 short, then a few pre-chosen filter families; count trials.
  Step 1b (user: not only Apex; blocks as designed, daily bars, 5 / 20-day holds, 7 markets pooled, 32 trials,
  `analysis/blocks_step1b_daily_test.py`): 0 pass; longs on NQ / ES / YM / GC make money but no more than random long
  days (= bull drift). Antigravity called the library 'battle-tested': as components yes, as edges no.
- **Antigravity Phase 2 done (2026-10-17, `agents/results/PHASE2_VERDICT.md`):** 40 pre-registered variants on the 8 plan
  strategies, none beat the originals in both periods; LDF move ≥ 0.50 ATR on the bootstrapped bench a wash; its new
  ESEuroCloseTrend rebuilt = t 1.4, F. Task 09 (ES MOC) done: PASS on the rule; its run was 1 minute early (read close stamps as open) and still made $156-161
  per ES, PF 2.19 = robust to the minute (`agents/results/TASK_09_VERDICT.md`). Journal: `journal/` (Obsidian).
- **New candidate (2026-10-18): Vault Break sized by NR7 day** (Kaufman book via Antigravity): VB $217 vs $60 a trade after an
  NR7 day (t 2.8, both periods, placebo p 0.005); bench VB 1 / NR7 3 blown 3.5% vs 7.2%, 2y +$415. MC-confirmed 135/135, but checker FAIL (t 2.81 < 3.53,
  regime 0.55): NOT in the plan (user: add only if it passes); WATCHLIST #21 forward recheck. NR7Contracts stays -1.
  Antigravity book readings so far: Chan (F), Prado (no trade), Kaufman (NR7), Pedersen + Chan ML (F, ZN releases tested), Hilpisch (coding book, nothing), Carver (framework, nothing), Grimes (price action; failure test F), Taulli / Pruitt / Covel (nothing new).
- **NR7 family test FAIL (2026-10-18):** the user's NR7 breakout on NQ / YM / CL / GC shows no NR7 effect (pooled z 0.31); VB and ES
  NR7 results likely chance. ES Core 3 (user's weekend finds): D (Sharpe 0.88 rebuilt, Monday filter backwards).
- **Overnight round for a future personal account (2026-10-18, `analysis/overnight_round.py`): all D.** Overnight long NQ $83/night
  (t 1.4), turn of month NQ $1,063 (t 1.4), 6-market trend portfolio Sharpe 0.46 (2022 +10%, corr ES −0.09). Personal account =
  the intraday plan without Apex limits first; these only as small diversifiers.
- **Limit vs market entries (2026-10-18, `analysis/limit_entry_test.py`): keep MARKET entries** — limits miss the big winners on every
  plan strategy (ES MOC −$76 to −$109 a signal).
- **Lead 1, leveraged-ETF closing push reverses overnight (2026-10-18, `analysis/letf_overnight_reversal_test.py`): F.** Fading big
  8:30→15:00 days from the 17:00 reopen to 8:30: NQ t 0.3, ES t −0.5; shorts lose; the longs are only the known overnight drift. Post-hoc
  'long after a down 14:40→15:00 push' (NQ t 2.8, ES t 2.4) failed on YM (t 0.7). Nothing to add.
- **Index rebalancing next-morning reversal (Franz 2019, SSRN 3459744; 2026-10-18): F.** Stock-level effect; the index analog
  (fade the last 30 min of rebalancing dates to 10:30 next day) loses on NQ and ES (`analysis/index_rebalance_reversal_test.py`).
- **Antigravity paper screen (TASK_PAPER_SCREEN, 2026-10-18): 3 picks, none new.** Treasury auctions already tested; FOMC
  liquidity premium and YM opening-range reversal both F (`analysis/anti_papers_1018_test.py`).
  After reading the PDFs: Antigravity misread the FOMC paper; the paper's real post-announcement sign (short after a high-liquidity
  day) holds on ES $626 / NQ $1,104 but t 1.4 on ~35 days: D, WATCHLIST #23. Antigravity committed the 3 PDFs to its branch (copyright: remove).
- **Noise-band intraday momentum (Chuk 2026, SSRN 7609644; Antigravity screen b): C.** Replicates partly (t 2.6 at our costs,
  2023-26 t 1.1); a near-twin of Vault Break; funded bench +1 MNQ −$224 / blown +1.5 pts: not added.
- **Replacement sweep (2026-10-18, FUNDED_PLAN.md 'Replacement sweep'): no swap beats the plan.** 15 candidates in each slot
  vs the empty slot, bootstrapped: all within noise (best +$114); the plan is saturated, its drawdown budget is the limit.
  Test order filled 2026-10-18 17:00 CT (real Apex fill): account #2 Tue 10/20 is a go.
- **User's to-do list: `TODO.md`** (reminders scheduled in the original session: Sun + Wed 10:52 CT, and Sun 10/18 15:30 CT).

- **Account #1 (50K EOD evaluation): about +$1,500, $1,500 left to the $3,000 target.** The user entered the ONB trade
  manually after a rejection and closed it at +$1,500 (agreed afterwards: **no early exits, no re-entries** -- the Apex
  evaluation has no consistency rule; capping days at $1,500 cuts pass rate 50.1% → 45.3%, `analysis/profit_cap_test.py`).
- **Finish line:** `apex_strategies/Apex_Target_Guard.txt` (exit-only signal added next to each strategy on its chart;
  `StartBalance` = Apex balance before the session, `TargetBalance` 53050). Not yet compiled by the user; confirm it compiles
  and is on the VB, ONB and Bridge Monday charts before Monday. After the pass: auto-trading off on that account.
- Still waiting on the user: test order confirming real Rithmic fills (Sunday 17:00 CT), EOS stop-guard paste, weekly
  live reports into `live/`.
- **Research this week:** forced flows round 5 (`analysis/forced_flows_round5_test.py`): ES stocks-vs-bonds month-end
  rebalancing D (t 1.2), gold first-notice-day short F, CL holiday-reopen fade too rare. **Monte Carlo**
  (`analysis/montecarlo.py`, `MC.report(trades, daily, size=...)`) is now part of the testing standard (CLAUDE.md,
  DEVELOPMENT_PROCESS.md); CL Sunday fade at 2 MCL: P(losing year) 14%, P(hit $2,000 trailing) 0%.
- **Other AIs (user asked):** idea = a second, different-lab model (OpenAI reasoning model; Gemini runner-up, e.g. via
  Google Antigravity) as an extra blind checker of strategy specs in `checks/candidates/`. Needs an `OPENAI_API_KEY`
  in the environment's Network secrets (never pasted in chat). Not set up yet.
- **Monte Carlo on the whole funded plan at plan size (done 2026-10-17;** `analysis/plan_montecarlo_test.py`, FUNDED_PLAN.md
  'Monte Carlo at plan size'): bench reproduces ($10,184 / $12,450, blown 3%). Full size with no cushion rule would hit the
  $2,000 trail in ~23% of years -- the cushion rule (half size below $1,500) is what keeps blown at 3%. Vault Break is the main
  drawdown source (alone 29% / yr at 3 MNQ); NFP Fade the weakest line ($375 / yr, P(losing year) 31%, no trail risk);
  ONB ML longs lost all of 2018 (clustered, DD rank 99%), fine since. No plan change.
- **Apex Target Guard reviewed statically** (can't compile here): logic and tick rounding look right; still needs the
  user's compile on the VB, ONB and Bridge Monday charts.
- **Stop-rejection guard on every strategy (2026-10-17):** all live / funded files using `SetStopLoss` now exit at market
  when a bar trades through the stop and the position is still open (MULTICHARTS_PITFALLS.md 'Live order rejections');
  EOS switched from Close to High. Bridge Monday: new add-on `apex_strategies/Apex_Stop_Guard.txt` (`StopPoints` a few
  ticks wider than its stop) -- NOT NEEDED as shipped: the Bridge runs `StopPts` 0 (no stop; target 100, out 15:55, as
  backtested and MC-confirmed), so there is no stop order to be rejected; user's chart has no Stop Guard (correct, 2026-10-17). **User: paste and compile the updated files outside market hours** (VB, ONB ADX30, EOS on
  the combine charts now; the funded files when an account passes); inputs unchanged, backtests unchanged.
- **Jesse cross-check (2026-10-17, `analysis/jesse/README.md`):** all nine current strategies ported to Jesse (independent
  engine) on our data; trade-by-trade agreement with MultiCharts 97-100% (P&L within $50). Found and fixed: ONB ML traded
  unfiltered until its score had 60 days of history (now stands aside; user pastes the funded file when funded). Monday
  report / bench include 40 holiday Mondays the code skips (negligible). Setup sheet for Docker Jesse + Antigravity on the
  user's PC: `agents/JESSE_ANTIGRAVITY_SETUP.md` (user will say when to write Antigravity's first task).
- **Antigravity's work lands on branch `antigravity/jesse`** (user's jesse-bot folder; `git fetch origin antigravity/jesse`).
  First item: Golden Cross 50/200 (never backtested by it) -> F on our data (`analysis/jesse/strategies/GoldenCross`).
- **Data that would unlock new forced flows (researched 2026-10-17):** NYSE closing-auction imbalances (NYSE TAQ Order
  Imbalances from 2008, or Databento NYSE Integrated imbalance schema from May 2018, paid) and SPY / SPX option open interest
  by strike (historicaloptiondata.com ALLSPY from 2005 ~$455; historicaldata.net from 2002, free 6-month sample incl. SPX;
  optionsDX). Free SPX sample tested 2026-10-17 (`analysis/spx_gex_sample_test.py`, data on branch `antigravity/jesse` options_sample/): GEX's range signal is already in VIX, no direction / pinning -> don't buy the option history. The closing-imbalance data (Databento): user declined (2026-10-17); no paid data for now.
- **Meta-labeling (2026-10-17):** VB and LDF both F (pre-registered walk-forward ridge; no trade-level predictability). ONB is
  the only strategy where a day filter works.
- **IMPORTANT (2026-10-17, `analysis/nfp_replacement_test.py`): the funded bench is path-fragile.** Reshuffling only NFP's
  78 results among its own days (same total) moves 2-year blown from 2% to 16% (median 10%) and 2-year payouts $10,992-12,562.
  The plan's '3% blown' is a lucky ordering of one history; plan differences of a few % blown or a few hundred $ are noise.
  Future plan decisions need a bootstrapped bench (many resampled histories), not the single history. NFP replacement: none
  passes; NFP stays.
- **Antigravity blind checks: all 8 strategies PASS (2026-10-17;** `agents/results/TASK_01_VERDICT.md`, `TASKS_02_08_VERDICT.md`):
  MultiCharts, Claude's Jesse ports and Antigravity's blind Jesse rebuilds agree within $50 on 99-100% of matched trades. Phase 2
  (improvement under the brief's rules) is open for any strategy.
- **Bootstrapped bench built (2026-10-17, `analysis/funded_bootstrap.py`; FUNDED_PLAN.md 'Bootstrapped bench'):** use it for
  every plan decision. Realistic plan: 1y ~$8.5k, 2y ~$11.2k, blown 12-16% in 2 years, ~279 days to 6 payouts (single history
  said $10.2k / $12.5k / 3% / 229). Best found: **VB 2 / 1 + ES MOC follow 2 MES**: 2y +$760-880, blown 5-9%, as fast or faster.
  MES is allowed (user, 2026-10-17). ES MOC follow MultiCharts code written (`funded_strategies/ES_MOC_Follow.txt`; its Jesse port = the Python test's 202 trades, same days); MULTICHARTS CONFIRMED 2026-10-17 (199/199 trades, $171 per ES net, t 3.7, 8/9 yrs, 2025 -$4.6k); to do: Antigravity Task 09. VB 2 / 1 ADOPTED (user, 2026-10-17;
  just an input). Business-plan projections (`reports/Trading_Business_Plan.pdf`, ramp sims) used the single history: redo
  with the bootstrap.
- **Next ideas:** more forced-flow candidates on ES / GC / CL.

## Live status (2026-10-14)

- **2026-10-16 finding: nothing had traded on the Apex account yet.** The 10/12 fills were on Paper Trader (SIM 001); every
  Rithmic order (ONB 10/14, EOS 10/16 stops, a manual test) was rejected because Symbol Mapping sent `@MNQ` to Rithmic. Fixed:
  `@MNQ (dxFeed) -> MNQZ6`. Live start = first real Apex fill; confirm with a test order Sunday 17:00 CT before Bridge Monday
  (19:00 CT). Roll the mapping to MNQH7 ~Dec 11. Add account #2 only after a real fill. EOS got a stop guard (paste new code).
- **1 combine account live since Monday 2026-10-12** (user corrected 2026-10-15: running one account first as a shakedown
  week for errors / screen sleep; 2 of 2 trades so far). Plan: add accounts one at a time, 5–10 trading days apart.
  Next: EOS trades Fri 10/16 and Bridge Monday Sun 10/18 19:00 CT on account #1 (first live runs of both); if clean,
  **add account #2 Tue 10/20** (50K EOD), #3 about a week later (150K No-Activation). First live days:
  - **Monday 10/12:** a winning trade was missed because the connection dropped.
  - **Tuesday 10/14:** the Overnight Bias short (5 MNQ) was rejected by Rithmic: *"Invalid StopMarket order
    parameters"*, a sell stop placed above the market.
    - **Fixed:** all Overnight Bias versions now enter at market when price is already at / through the
      opening-range level (`EntryBufTicks` 2). The new order names are "ON Bias LM / SM".
    - **User must paste and compile the new code before the next open.**
  - Pass odds per account unchanged (~50%).
- **Evaluation finish line (2026-10-16):** `apex_strategies/Apex_Target_Guard.txt`, an exit-only signal added next to each
  strategy on its chart; set `StartBalance` (the Apex balance) before the session, `TargetBalance` 53050; it closes the
  position by limit when the account would reach the target. No consistency rule in the Apex evaluation and no early exits
  otherwise (`analysis/profit_cap_test.py`).
- **All strategy files were audited:** every other entry is a market order; order names are unique per file.
- **Combine set** (`apex_strategies/`, MNQ, 24-hour session, Exchange time CT):

  | Strategy | File | Chart | Live inputs |
  |---|---|---|---|
  | Vault Break | `NQ_Vault_Break.txt` | 30 min | `NumContracts` 8 |
  | Overnight Bias ADX30 | `NQ_Overnight_Bias_ADX30.txt` | 15 min | `RiskPerTrade` 1100, `NumContracts` 1, `ADXMin` 30, `StopAtrPct` 0.25, `ExitTime` 1430, `EarlyExitTime` 1130 |
  | Bridge Monday Long (ships with The Bridge, not in repo) | — | as shipped | 2 MNQ; enters Sunday 19:00 CT |
  | Expiration Open Short | `funded_strategies/NQ_Expiration_Open_Short.txt` | 5 min | `RiskPerTrade` 500; next trade **Fri 2026-10-16** (3rd Friday) |

  Backtest: pass 50.1% per try, median 6 trading days; combine sizing barely matters (`analysis/pipeline_tuning_test.py`).
  2026-10-15: state sizing / daily stops don't help (`analysis/combine_levers_test.py`); optional swap ONB ADX30 → ONB ML
  $1,100 = 52.0% (`analysis/combine_swap_test.py`). **Stagger new combines 5–10 trading days apart**: same-day combines on one
  copier share one outcome (correlation +1.0; 10 days apart +0.19). See FUNDED_PLAN.md 'Combine levers and staggering'.
- **Live tracking:** the user exports weekly MultiCharts reports into `live/`.
  - Run `python3 analysis/live_vs_backtest.py --all live/` (see `live/README.md`).
  - It now also prints a CUSUM **drift alarm** per strategy (OK / WATCH / ALARM = half size and review; `live/README.md`).
  - Count technical misses separately from the edge.
  - Scale beyond 3 slots only when the live edge is ≥ ~75% of backtest (×1.25 sizing only at ≥ 90%).

## Funded plan (when an account passes; `funded_strategies/FUNDED_PLAN.md`, roster in `funded_strategies/README.md`)

| Strategy | Chart | Inputs |
|---|---|---|
| Vault Break (`NQ_Vault_Break_SP.txt`) | 30 min MNQ | **2 MNQ** (`NumContracts` 2, was 3 until 2026-10-17), `FlaggedContracts` 1 |
| Overnight Bias ML v2 (`NQ_Overnight_Bias_ML.txt`) | 15 min MNQ | `RiskPerTrade` 400 |
| Monday Long | 5 min MNQ | 1 MNQ |
| Expiration Open Short | 5 min MNQ | `RiskPerTrade` 700 |
| Late-Day Flow | 5 min MNQ | 2 MNQ |
| NFP Fade | 5 min MNQ | `RiskPerTrade` 500 |
| Bridge Monday Long | as shipped | 1 MNQ |
| **CL Sunday Gap Fade** (new, `CL_Sunday_Gap_Fade.txt`) | 5 min **MCL**, Eastern exchange time | `NumContracts` 2, `ExitTime` 1000 (= 9:00 CT) |
| **ES MOC Follow** (added 2026-10-17, `ES_MOC_Follow.txt`) | 5 min **MES**, Central | `NumContracts` 2; mapping `@MES -> MESZ6` |
| **Relative Strength** (added 2026-10-20, `NQ_Relative_Strength.txt`) | 1 min MNQ + @ES Data2, Central | 50K: longs only 1 MNQ (`TradeDir` 1); 150K: both sides 1 MNQ; not in evaluations |

- **Cushion sizing:** f = cushion / ref, kept in 0.5–1.
  - **Funded phase: full size from a $1,500 cushion (user's decision, 2026-10-14).** The $1,000 setting blows 17–18%
    of accounts in the bench vs 2–4% at $1,500; it only looked better counting blown accounts as cheap restarts.
  - The funded bench numbers below use ref $1,500.
- **Backtest per account** (bench, ref $1,500):
  - $9,818 in year 1, $12,595 in 2 years, blown 4% / 2%.
  - Median 239 trading days to all 6 payouts.
  - About $800 a month net per slot over the challenge → funded → next-challenge pipeline.
- **To do before the CL strategy goes live:** confirm Apex allows MCL on the account.

## Research state

- **Current goal (`S_RANK_PROGRAM.md`): one S-rank strategy per symbol.**

  | Symbol | Best | Tier |
  |---|---|---|
  | NQ | Overnight Bias ML v2 | S |
  | CL | Sunday up-gap fade, MultiCharts-confirmed (96/97 trades): $653 per CL, PF 3.02, t 3.2, 9/9 years | A, in the funded plan |
  | ES | MOC auction follow | B |
  | YM | MOC follow, post-settlement fade | C |
  | GC | Asian-range breakout; still hurts the funded bench | C, parked |
  | BTC | Nothing; CME bitcoin trades 24/7 since 2026-05-29, so the weekend gap is gone | D/F |

- **Done today:**
  - Covered-call ETF rolls: the only effect is EOS, which is already in the plan.
  - Forced-flow round 4: MOC auction follow C (watchlist #10); quarterly rebalance closes and Tokyo / London opens F.
  - S-rank rounds 1–2 on ES / YM / GC / CL / BTC.
  - The user's CL forced-flow chat: Platts window, EIA sweep fade and round numbers F; USO roll short D.
  - Gold / BTC FOMC: D.
- **Gold vs rates / dollar** (ZN + 6E now in `data/`, 2017-12 → 2026-10): F (`analysis/gold_rates_dollar_test.py`).
  - Treasury-auction price pressure paper (NY Fed SR 1188) on ZN / GC / 6E: D (pre-auction ZN fall real, +$15 gross t 2.3, vs $38.50 cost;
    `analysis/treasury_auction_test.py`).
  - Overnight-Intraday Reversal Everywhere (SSRN 2730304), cross-sectional on the 7 markets: F (gross negative on a
    synchronised clock; `analysis/co_oc_reversal_test.py`).
  - A Tale of One Day (SSRN 4192163), morning momentum / afternoon reversal on NQ / ES / YM: F
    (`analysis/morning_afternoon_test.py`).
  - Maroy 2025 exits (SSRN 5095349) on Vault Break: the VWAP exit looked better in Python but **MultiCharts did not
    confirm** (target on $4,947 / yr, Sharpe 1.29; off $5,849, 1.00; live VB $5,341, 1.35): D. Live VB unchanged.
  - Mesfin 2026 MNQ falsification study (SSRN 6709401): F; its London Signal B only works with a look-ahead entry
    (`analysis/london_signal_b_test.py`).
  - Mega-cap earnings on NQ (Alpha Vantage data in `data/ndx_megacap_earnings.csv`; the user's API key is NOT stored):
    pre-specified rules no edge; 'sell the news' short D (all from 2024–25); intraday shape F.
  - CL round 3 (Friday, Monday after the fade, overnight, London open): F. The Sunday up-gap fade stands alone.
  - Plan combination: Vault Break after an Overnight Bias ML long earns $214 vs $64 (t 2.55), but the funded bench says
    extra VB on those days lowers payouts and raises blow-ups at every size (+1 MNQ $9,519 vs $9,818; +2 blown 12%): D.
  - Quantpedia sentiment / overnight anomaly (SSRN 3829582): its filters backfire on OND (the overnight premium is larger
    after fear); neither version beats the funded plan: F.
  - ES mean reversion (six families + day-to-day fade): F on ES; ES reverts only slightly more than NQ and far below its
    $30 round trip; the day-to-day fade is stronger on NQ (t 2.2, 5/9 years: D).
  - The Bridge's exported indicators (order flow, gamma) scanned as filters on the plan: 1 pass in 63 (chance level), no bench
    gain: F (`analysis/bridge_filter_scan.py`; features cached in scratch `bridge_features.pkl`).
  - Gold Breakout 15M (user's TradingView strategy): real (t 3.1, beats a random side) but lowers the funded plan at 1 MGC: C.
  - Bridge indicators round 2 (user's code: depth, walls, other VWAP anchors, gamma fixed for the NDX → NQ basis): no filter
    beats the plan. GAMMA LEVELS ARE NDX POINTS: NQ level = level + basis. Earnings-day gamma rule on watchlist #15.
  - Single-print day filter (Red Ledger RL-FS-2026-01, `analysis/single_print_test.py`): replicates on our NQ 2018-26; VB earns
    $21 vs $123 a trade the session after an interior single print; funded VB 3 / 1 on flagged days $10,184 vs $9,818 (1 year),
    blown 3% vs 4%, beats all random-day placebos: B. MC-CONFIRMED (262 / 274 flagged days identical, no false skips);
    user to paste it over `NQ Vault Break` outside market hours. Combine: FlaggedContracts -1 (= old VB, no gain).
  - **USER PREFERENCE (2026-10-15): Twin Continuation is the profile the user wants -- a big edge that trades a lot. Keep it
    logged for future use (a personal / non-prop account, or a prop firm with a larger or static drawdown).** Look for more like it.
  - Twin-like search (2026-10-15): round 1 Twin is NQ-only (ES/GC/YM/CL fail); MO risk-sized doesn't fit. Round 2 MO with a
    tight 0.10-ATR stop: $374, PF 2.00, t 4.07, 9/9 yrs, but 29% win rate → losing streaks vs $2k trail: no Apex gain (B, not adopted).
    LESSON: for Apex look for HIGH win rate frequent edges (VB-like 66%), not trend-day capture.
    Round 3 high-win search: MO entry + T 0.10 / S 0.20 ATR = 75% win, t 4.13 (B) -- but adding ANY new risk to the funded plan
    raises blown (3% → 7%+): the plan's risk budget is full. Gains now need replacements, more accounts, or the combine.
  - Twin Continuation (user's MC code; `analysis/twin_continuation_*.py`, checker `checks/candidates/twin_continuation/verdict.md`):
    real edge (t 5.5, DSR 0.995, checker replica 99.8%, PASS WITH CONCERNS) but wrong shape for Apex (BO swing stops ~$6k/NQ,
    fat-tailed MO wins vs consistency): no gain in funded plan / own PA / combine. MC-CONFIRMED (v2 report: 1,069/1,074 entries identical, $296 t 5.3): A.
    Non-prop account idea; v2.1 in personal_strategies/ (holiday fix, SetExitOnClose removed).
  - Trials log + deflated Sharpe (`analysis/trials.py`, `TRIALS.csv`, `metrics.deflated_sharpe` / `t_threshold`): 193 items tested,
    bar |t| 3.47; plan DSR: ONB ML 0.99 passes, VB 0.92, Bridge Monday 0.91, LDF 0.79, Monday 0.73, EOS 0.42, NFP 0.16 (forced-flow
    items stand on the pre-registered rule; watch them live). New promotion rule in DEVELOPMENT_PROCESS.md.
  - The Bridge's 'Propfirms as a business' slides: 'bench strategies in drawdown' tested on our plan (`analysis/bench_in_dd_test.py`):
    no clustering, benching lowers the combine pass rate (50.1% → 41-48%): F. Don't bench on drawdown; the drift alarm covers a dead edge.
  - OU mean-reversion regime (user's post, `analysis/ou_regime_test.py`): theta doesn't persist day to day; VWAP fade loses, worse in
    the 'MR regime': F. Side find: Late-Day Flow $191 vs $19 in high-theta regime (t 3.1, 8/9 yrs) but funded no gain: watchlist #16.
  - NDX 0DTE open interest by strike (`data/GEXOI_*.csv`, `analysis/gex_oi_pin_test.py`): no pinning, no wall effect, put/call
    useless, 0 / 15 plan filters pass: F. Export has no Mondays; use only the 9:31 ET OI snapshot. Apex PA terms CONFIRMED from the user's dashboard 2026-10-15 ($2,000 drawdown, safety net
    $52,100, min balance to request $52,600, 5 days of $250+, 6 payouts then closed): the simulator already matches, no change.
  - YM's own events (Dow heavyweight earnings, ZN overnight / lead-lag / shocks): F (`analysis/ym_dow_events_test.py`).
  - BTC short-only euphoria fades (multi-day / overnight / intraday spike / heavy-volume / round numbers): F.
  - Funded bench rebuilt this session (numba, build_lab, s_rank_gap_round2 + gy / btc grids): reproduces the documented numbers.
- **Next research (needs data from the user):**
  - Closing-imbalance or options open-interest data for ES.
  - Without new data, the clock flows on GC / ES / YM / BTC are exhausted.
- **Watchlist (`WATCHLIST.md`), notable items:**
  - #1 Late-Day Flow sized by the gamma flip
  - #10 / #12 MOC follow
  - #13 ONB ML filter out of sample: fit on 2018–22 only, kept $469 vs skipped $212 on 2023–26, t 1.0. Live reports
    decide.
  - #14 EOS sized up in calm VIX
- **Data caveat:** continuous contracts are not back-adjusted.
  - Roll jumps happen at 03:32 or 17:01 CT (NQ +120..310 points per roll since 2023).
  - The plan's trades are clear of them; drop roll bars in new tests.

## Rebuilding the data (not in git)

- `pip install numba`, then `python3 analysis/build_lab.py scratch_data` builds g24 / ge / lab.
- The gc / cl pickles build on first `load("GC")` / `load("CL")`; btc via `cross_asset_overnight_test.btc()`.
- The CL fade's bench needs `scratch_data/s_rank_gap2.pkl`: run `analysis/s_rank_gap_round2_test.py` first.
- Raw 1-minute CSVs are all in `data/` (moved from the repo root 2026-10-21); MultiCharts reports in `mc_reports/`.

## Open items for the user

1. Compile the fixed Overnight Bias code (combine chart now; funded ML version later) and re-enable auto trading.
2. Keep the PC / connection awake during trading hours (Monday's miss).
3. Optional: rerun the ONB ADX30 MultiCharts backtest once with the new code (should be nearly identical).
4. Check Apex allows MCL; send weekly live reports; no exports pending (ZN and 6E are complete).
