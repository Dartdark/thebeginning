# S03 Noise Area v2: WATCH; risk benefit observed, no validated plan placement

Summary: The fixed OHLC reconstruction is profitable in every tested year; source/tick parity is unconfirmed.
2018-22: 1,366 trades, $117/NQ, PF 1.43; 2023+: 1,013, $123/NQ, PF 1.28.
The stop roughly halves recent daily drawdown with almost unchanged profit; the formal improvement criterion does not pass.
Top 10 trades supply 97.8% of recent net; DSR 0.890<0.95 and actual-fee recent t<2.
Three missing held-price minutes and calendar gaps block all account tests. Keep current allocations; placement remains unknown.

Plan: `agents/codex/plans/s03_noisearea.md`, **d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad**, published before any new signals/returns.
Scripts: `analysis/codex_s03_{calendar,replay,run,stats,diagnostics,accounts,personal,report}.py`.
Output: `analysis/outputs/codex_s03_noisearea/`. Trials: **one idea/four fixed profiles**, all failures included; 400 registered null replays.

## Rule (as tested)

At half-hour checks 10:00-15:30ET, trade beyond the 14-prior-full-session same-clock mean absolute open-to-close return band, confirmed by VWAP. Upper=max(open,prior cash close)*(1+sigma); lower=min(...)*(1-sigma). Both directions share one position; opposite signals reverse. Band/VWAP trailing exits occur only at checks. Market orders fill at the next observed minute open. V2 fixes a 0.4*raw-sigma*signal-close protective stop, rounded toward raw entry and live on the fill minute. This sigma is mean absolute displacement, not standard deviation or ATR. No profit target. Normal flat decision 16:00ET fills 16:01ET=15:01CT, within the account's15:59CT deadline.

Primary reconstruction uses actual 08:30CT cash-open price from the 08:31 close-stamped minute, one-minute typical-price/total-volume VWAP, and the immediately preceding cash-session close (including a legitimate early close). Only prior completed full sessions enter sigma; past completeness is known after their close. Today's later missing prices never retroactively exclude earlier trades. Known calendar closures/early closes are skipped.

Frozen profiles: **V2** primary; **V1** identical with protective stop disabled; **C2** one 08:30-bar-inclusive anchor sensitivity; **E2** V2 at three ticks per market/stop fill. C2/E2 are not selectable winners. No stop, weekday, clock, size or direction search followed results. Standard cost $7.25/NQ RT plus one tick per market/stop fill, ordinarily $17.25 total; source used $15. Net already includes fills and fees once. Source LucidFlex payout/size assumptions are not used as Apex results.

## Results

All amounts in the next tables are **per one NQ**, fixed size, after research costs. 2026 ends October9. 2023+ is selected/previously seen historical replication, not a fresh holdout. These are observed-bar reconstruction results, with the missing-path limitation below.

| Profile | 2018-22 n | Net | t | 2023+ n | Net | t | Full net |
|---|---|---|---|---|---|---|---|
| V2 | 1366 | $159,646 | 3.94 | 1013 | $124,671 | 2.008 | $284,317 |
| V1 | 1073 | $140,196 | 3.10 | 767 | $125,934 | 1.853 | $266,130 |
| C2 | 1357 | $145,717 | 3.64 | 1005 | $119,679 | 1.924 | $265,396 |
| E2 | 1366 | $132,326 | 3.26 | 1013 | $104,411 | 1.681 | $236,737 |

Standard whole/long/short metrics (side rows are slices of the shared replay, not newly selected single-side strategies):

| Period | Side | n | Win | $/trade | t | Sharpe | Sortino | PF | Calmar | Ulcer% | Daily maxDD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| design | whole | 1366 | 30.5% | $117 | 3.94 | 1.81 | 3.87 | 1.43 | 2.65 | 2.13 | $11,774 |
| design | long | 669 | 34.5% | $118 | 3.18 | 1.43 | 2.96 | 1.49 | 1.94 | 2.86 | $7,943 |
| design | short | 697 | 26.5% | $116 | 2.52 | 1.16 | 2.56 | 1.38 | 1.20 | 4.55 | $13,127 |
| recent | whole | 1013 | 29.8% | $123 | 2.01 | 1.08 | 2.57 | 1.28 | 1.51 | 4.91 | $21,451 |
| recent | long | 493 | 35.1% | $221 | 2.32 | 1.26 | 4.19 | 1.58 | 1.77 | 4.78 | $15,951 |
| recent | short | 520 | 24.8% | $30 | 0.39 | 0.20 | 0.39 | 1.06 | 0.15 | 12.20 | $27,632 |
| 2018_plus | whole | 2379 | 30.2% | $120 | 3.83 | 1.35 | 3.09 | 1.35 | 1.48 | 2.21 | $21,451 |
| 2018_plus | long | 1162 | 34.8% | $162 | 3.54 | 1.25 | 3.54 | 1.54 | 1.31 | 2.85 | $15,951 |
| 2018_plus | short | 1217 | 25.8% | $79 | 1.87 | 0.64 | 1.29 | 1.21 | 0.39 | 5.44 | $27,632 |

Sharpe/Sortino use the common calendar including zero dates; daily realized totals reconcile exactly because all closed trades are intraday. Intraday adverse excursions are separately audited; daily maxDD is not the full account breach path. Ulcer uses the repository's$50,000 reference equity.

| Year | n | Total net | Long net | Short net | PF | t |
|---|---|---|---|---|---|---|
| 2018 | 255 | $44,176 | $5,444 | $38,732 | 2.09 | 3.09 |
| 2019 | 258 | $1,000 | $7,144 | -$6,144 | 1.03 | 0.14 |
| 2020 | 259 | $31,912 | $5,678 | $26,234 | 1.40 | 1.70 |
| 2021 | 281 | $23,528 | $21,955 | $1,572 | 1.30 | 1.48 |
| 2022 | 313 | $59,031 | $38,768 | $20,263 | 1.44 | 2.11 |
| 2023 | 252 | $52,628 | $45,440 | $7,188 | 1.80 | 3.17 |
| 2024 | 293 | $12,631 | $5,191 | $7,440 | 1.11 | 0.56 |
| 2025 | 259 | $40,037 | $33,658 | $6,379 | 1.30 | 0.87 |
| 2026 | 209 | $19,375 | $24,677 | -$5,302 | 1.16 | 0.62 |

Post-source extension,2026-07-08 onward: 54 trades, $13,234, t=0.84. This is a short descriptive extension, not independent validation.

**The protective-stop claim:** full-history point results improve total net and reduce drawdown, but the registered design/recent criteria do not both support an improvement. The design V2 maxDD is slightly higher; recent profit is slightly lower. The mechanism is changed re-entry opportunity as well as changed loss size.

| Period | V2 minus V1 metric | Observed | 90% low | 90% high |
|---|---|---|---|---|
| design | net_change | $19,451 | -$6,812 | $42,111 |
| design | sharpe_change | 0.418 | 0.110 | 0.671 |
| design | max_dd_reduction | -$114 | -$2,580 | $5,878 |
| recent | net_change | -$1,264 | -$43,433 | $39,156 |
| recent | sharpe_change | 0.070 | -0.277 | 0.444 |
| recent | max_dd_reduction | $25,809 | -$2,533 | $22,595 |

For the design's 1,073 common entries the stop changes net by −$26,560; 293 extra re-entries add $46,010.75. Recent: 767 common entries change −$40,490; 246 extra re-entries add $39,226.50. No original entries disappear. Therefore stop-trade losses alone cannot measure the intervention, and per-trade average alone is misleading.

**Actual micro fee arithmetic**, on identical observed V2 fills at fixed 1 MNQ. This is not a payout/account simulation:

| MNQ round-trip fee | Recent avg/MNQ | Recent t | PF |
|---|---|---|---|
| $1.04 | $11.99 | 1.956 | 1.273 |
| $1.24 | $11.79 | 1.924 | 1.267 |

Repricing credits the original $0.725/MNQ research commission and charges $1.04/$1.24 per actual trade; existing slippage stays included. At actual micro fees, recent t falls below2. The nominal one-NQ result barely clears2 and the anchor sensitivity does not.

## Placebos and account level

All400 registered controls were run through the full state engine:100 random-side and100 time-permuted streams per period. No slow approximate scheduler, future-occupancy count matching or discarded outcomes was used. These controls have important interpretation limits:

- Side controls randomize raw check-bar directions; extra reversals change holding time, number of filled trades and costs. This is a joint policy/turnover comparison, not an isolated directional-prediction test.
- Time permutations can move a later signal's direction earlier in the day. They are **future-informed retrospective comparisons**, not causal random-entry policies. Their large profits do not reject the actual entry edge. A clean causal timing test remains open; no new rescue control was chosen after returns.
- Some control paths cross missing bars. All remain visible; p-values on incomplete paths are descriptive under observed-bar execution, not validated executable outcomes.

| Period | Control | Profit p | Median null net | Actual filled | Median null filled | Complete /100 |
|---|---|---|---|---|---|---|
| design | side | 0.0099 | -$34,106 | 1366 | 3201.0 | 100 |
| design | time | 1.0000 | $422,627 | 1366 | 1709.5 | 65 |
| recent | side | 0.0099 | -$206 | 1013 | 2341.5 | 55 |
| recent | time | 1.0000 | $496,082 | 1013 | 1277.0 | 7 |

Recent20-day/3,000-draw bootstrap,90%: net $47,354 to $203,833; tradePF 1.105-1.456; Sharpe 0.48-1.55; daily maxDD $13,993-$36,774. Whole/long/short bootstrap and drawdown-permutation files are saved.

Recent tail concentration: best trade 29.1%, best 10 97.8%, best 25 163.3% of net. Fractions above 100% mean the rest lost money; no deletion was used to select a rule. Recent longs supply $108,965.75; shorts $15,705 with t 0.39 and a bootstrap interval crossing zero. No long-only re-optimization or account selection followed.

**All account stages stopped at the registered data gate.** Candidate paths contain three unknown held minutes on 2024-10-09: 14:47,14:48,14:55CT, within a long entered 13:01 and exited 15:01. Both current raw NQ exports omit those minutes; file Git blobs and cached finite masks match. The stop is 20362.75, raw entry 20399.75; the observed net $1,147.75 cannot establish what happened inside the missing minutes.

A structural audit also finds 2020-11-30's entire normal cash session absent and a missing 12:00 decision on 2020-03-18. The latter may be an exchange halt, but the inherited repository closure mask does not certify it. Thirteen other flat, nonscheduled-minute gaps are explicitly permitted by the frozen observed-only VWAP rule; they are not mislabelled additional fatal held-path gaps. All 2,290 expected weekday rows are retained. No prices, trades, returns or missing days were invented or silently dropped.

| Destination | Frozen comparison | Outcome |
|---|---|---|
| 50K evaluation | BASE / +1MNQ / EMPTY_VB / VB8 replacement | BLOCKED_DATA; no simulation |
| 150K evaluation | BASE / +2MNQ / EMPTY_VB / VB20 replacement | BLOCKED_DATA; no simulation |
| 50K funded | BASE / +1MNQ / EMPTY_VB / original VB2/1 slot | BLOCKED_DATA; no simulation |
| 150K funded | Current DT-inclusive plan; +2MNQ / EMPTY / original VB slot | BLOCKED_DATA; no simulation |
| Personal | Current17 pieces,11 fixed ladders,44 configurations | BLOCKED_DATA; no simulation |

Account and personal helpers passed synthetic fixtures and current-source provenance checks, but no historical baseline was built and no account/portfolio simulation ran. No payout, breach, evaluation-pass, marginal portfolio-value or capital-allocation conclusion is inferred from standalone statistics. The individual manifests record each limiting condition and distinguish unknown contribution from proven no gain.

## What could make this wrong

- **Selection:** author's at least 12 stop values and walk-forward claims were supplied already selected; source 2023+ is not fresh. Our 4 profiles were frozen before returns. The ranked-item-plus-one t bar is 3.581; full t 3.835 clears it but DSR 0.890 fails 0.95. Actual-micro recent t also misses 2.
- **Source parity:** no original PowerLanguage signal, s03_engine.py, original OFB bars or tick stop export was supplied. The bulletin's1-minute replica and claimed trade parity are not confirmation of this reconstruction. Its 2017 start differs from our 2018 start; datasets/clocks/costs differ.
- **Price path:** one-minute OHLC and missing held prices cannot validate tick execution or exact intraday liquidation. Gap stops may fill beyond planned risk. No SetExitOnClose final-price rescue was fabricated.
- **Contract rolls:** the unadjusted data can affect prior-close band references. Known 03:32/17:01CT roll jumps lie outside normal RTH holds, so they are not automatically trade profits; a back-adjusted-source comparison was not silently added.
- **Inference:** conditional/future-informed timing controls and different-turnover side controls are not clean proof of executable predictive edge. Resampling selected returns does not remove selection bias or certify account survival.

## Differences between the MultiCharts code and the test

No new MultiCharts code was written. This is a descriptive-rule reconstruction with explicit cash-open, VWAP, prior-close/calendar, observed-bar gap, stop-price rounding and shared OHLC-path conventions. No original source code was available to claim exact equivalence. Source costs$15 become research $17.25 and actual/stress micro fees. Known calendar closures skip entries; missing current data never retroactively deletes an earlier trade. All observed trade nets reconcile to raw/slipped fills and daily totals.

## Decision and reproduction

**WATCH.** The stop's historical risk effect is useful evidence, but the fixed version has not earned a current plan placement. Resolving price/source gaps and tick confirmation is a data/validation task; no open-ended stop, clock, side or size search is justified by this report. The independent review is `agents/codex/results/s03_noisearea_independent_review.md`: implementation checks pass within scope; source/data/causal-placebo concerns remain.

Use the configured Python environment and existing cache; do not rebuild grids. Pinned Codex/Claude refs must be available locally. The prepare commands stage exact source blobs without calculating historical baseline returns. From repository root:

```bash
export PYTHONPATH=analysis
PY=/workspace/venvs/thebeginning/bin/python
$PY analysis/codex_s03_run.py --design --prereg-commit d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad
$PY analysis/codex_s03_stats.py --stage design
$PY analysis/codex_s03_diagnostics.py --stage design --prereg-commit d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad --nulls
$PY analysis/codex_s03_stats.py --certify-design
$PY analysis/codex_s03_run.py --recent --prereg-commit d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad --gate-file analysis/outputs/codex_s03_noisearea/design_gate.json
$PY analysis/codex_s03_stats.py --stage recent
$PY analysis/codex_s03_diagnostics.py --stage recent --prereg-commit d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad --gate-file analysis/outputs/codex_s03_noisearea/design_gate.json --nulls
$PY analysis/codex_s03_stats.py --account-gate
$PY analysis/codex_s03_accounts.py --prepare
$PY analysis/codex_s03_accounts.py --audit-only --prereg d9ef177df4f2a788dc4e9d108c4cdc1fbc4880ad --gate analysis/outputs/codex_s03_noisearea/candidate_gate.json --ledger analysis/outputs/codex_s03_noisearea/candidate_V2.csv --held-gaps analysis/outputs/codex_s03_noisearea/candidate_held_gaps.csv
$PY analysis/codex_s03_personal.py prepare
$PY analysis/codex_s03_personal.py --blocked-only --candidate-gate analysis/outputs/codex_s03_noisearea/candidate_gate.json
$PY analysis/codex_s03_stats.py --finalize
$PY analysis/codex_s03_report.py
```

Account/run commands remain guarded against a false data gate. Source, cache, plan, exact module pins and generated artifact hashes are preserved. No plan/ranking/live/VPS/broker/API-key changes or external messages occurred.

Publication scope approved by the user: scripts, aggregate results, reviews and audit hashes on Dartdark/thebeginning, codex/work. Detailed trade/order/daily histories and per-draw samples are omitted from the publication, retained in the workspace and reproducible locally.
