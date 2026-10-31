# Hourly R2 CHoCH: direction and timing controls; no promotion

Summary: The hourly two-candle CHoCH 1:2 foundation made $4,896.08/MNQ on 408 resolved design trades, trade t=1.218. Random-side p=0.1069; causal random-delay p=0.2118; neither clears the frozen .05 diagnostic threshold. The earlier-entry random-time counterfactual is explicitly noncausal and cannot be traded. The full-source unknown path and prior failures remain. No 2023+ validation, account benchmarks or promotion follow.

Plan [preregistration](../plans/choch_h1_r2_placebos_20261029.md), public commit `2e781a6cb5dbe44eb3782cfe77480915c36648b3`; implementation commit `51c0488d6b766260e84a4fe2de8d3a32d39fc6f1`. Scripts: [catalog/study](../../../analysis/codex_choch_placebos.py), [path replay](../../../analysis/codex_choch_placebo_paths.py), [report](../../../analysis/codex_choch_placebo_report.py). Saved [summary](../../../analysis/outputs/codex_choch_placebos_20261029/design/summary.json) contains code/input hashes and dependency versions.

## Fixed rule and costs

NQ signal, one native MNQ: strict hourly swing confirmed by two completed candles on EACH side; causal core HH/HL/LH/LL trend and opposing-swing close break. Primary fill OPEN(signal+2), stop prior confirmed opposite swing, target twice fill-to-stop distance, one position, normal 09:00–14:00 CT signal hours/flatten OPEN of close-labelled 15:58; early 09:00/10:00/flatten OPEN 11:30. $2/point, $1.24 commission plus $1.00 slippage round trip = $2.24/trade. Gross 1:2 is not the realized payout of timed exits. Shared execution protects the entry bar, takes worse stop gaps and requires 1-point target-through. Entry beyond stop is charged immediate round trip. No altered side, swing or filter.

## Coverage and baseline

The original full source baseline is reproduced. For finite matched controls, the analysis uses sessions with all expected-open minutes 09:00 through planned liquidation observed. This is a future data-completeness research restriction, **not an executable entry filter or coverage-removal alpha**. Covered daily metrics use exactly complete cash-session dates, including complete no-event dates; full source retains its earlier weekday clock. Missing prior context still resets structure. Raw inputs are the same 11 hash-bound reconciled DAY/ON sources, 2017 warm-up and 2018–22 only. Close-labelled CT timestamps are the operating source assumption; exporter timestamp identity and continuous-contract roll identity remain independently unverified.

Coverage: `{'cash_sessions': 1259, 'complete_sessions': 1251, 'incomplete_sessions': 8, 'eligible_signals': 412, 'covered_signals': 411, 'excluded_trade_states': {'unresolved_missing': 1}, 'excluded_resolved_net': 0.0, 'note': 'Future data-completeness analysis restriction, not a live entry filter or new alpha rule.'}`.

| sample | trades | net | trade_t | NW5 | Sharpe | Sortino | PF | Calmar | Ulcer | maxDD | unknown |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_source_BASE | 408 | 4,896.0800 | 1.2179 | 1.1940 | 0.5241 | 0.8354 | 1.1912 | 0.3929 | 1.9217 | 2,406.6000 | 1 |
| covered_BASE | 408 | 4,896.0800 | 1.2179 | 1.1952 | 0.5353 | 0.8533 | 1.1912 | 0.4098 | 1.9232 | 2,406.6000 | 0 |

Full versus covered yearly totals:

| sample | 2018 | 2019 | 2020 | 2021 | 2022 |
| --- | --- | --- | --- | --- | --- |
| full_source_BASE | -612.7600 | 499.8400 | 650.0200 | 1,406.3200 | 2,952.6600 |
| covered_BASE | -612.7600 | 499.8400 | 650.0200 | 1,406.3200 | 2,952.6600 |

Full versus covered, both sides:

| sample | side | trades | net | trade_t | win | Sharpe | Sortino | PF | Calmar | Ulcer | maxDD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_source_BASE | -1 | 204 | 3,018.5400 | 1.0020 | 0.4657 | 0.4403 | 0.7630 | 1.2218 | 0.3201 | 1.7248 | 1,820.8200 |
| full_source_BASE | 1 | 204 | 1,877.5400 | 0.7035 | 0.5000 | 0.3095 | 0.5012 | 1.1564 | 0.2266 | 1.0526 | 1,599.9200 |
| covered_BASE | -1 | 204 | 3,018.5400 | 1.0020 | 0.4657 | 0.4497 | 0.7793 | 1.2218 | 0.3339 | 1.7285 | 1,820.8200 |
| covered_BASE | 1 | 204 | 1,877.5400 | 0.7035 | 0.5000 | 0.3161 | 0.5119 | 1.1564 | 0.2364 | 1.0558 | 1,599.9200 |

## What each control tests

**RS random side:** fair +/- side at the actual signal clock. Keep original potential-fill-to-swing risk distance and reflect the bracket at that fill; re-execute minute stop/target/time exits. This tests direction conditional on actual event dates/times/risk. The mirrored stop is a matched bracket, not a newly confirmed opposing swing.

**RT random time:** uniform legal hours on the same actual event day, retaining original side/risk distance and translating the bracket around the new fill. **Earlier draws inherit information from a later actual signal. RT is a noncausal conditional counterfactual, not a tradable alternative or promotion placebo.** It also conditions on chosen days, so it cannot establish calendar-day selection.

**RD random delay:** uniform actual hour or later legal hours, retaining side/risk and translated bracket. Original potential fill/risk is observed at the original fill clock before any later delayed fill. This is a causal post-signal delay benchmark, not unrestricted random-time trading.

All original eligible events on audited sessions are supplied, not just previously admitted or profitable trades. SeedSequence 20261029 spawns independent RS/RT/RD streams; all 1,000 paths each are saved. Requests sort by scheduled entry, original signal and event ID; entries at/before the last exit are blocked, never retried. Thus realized trade counts/holding minutes may differ. Pending delayed requests may coexist, with one-position admission at their scheduled fills. The immutable outcome catalog plus chosen IDs/admission masks reconstructs each complete trade ledger; no best seed is selected.

## Randomization results

Matched BASE net **$4,896.08**, DD **$2,406.60**, 408 trades. Primary p counts null net>=BASE in exact cents, includes ties, plus-one denominator 1001. DD p counts nullDD<=BASE; joint counts both. Quantiles describe the 1,000 finite-sample random paths; they do not represent 1,000 independent market histories.

| null | complete | null_net_p5 | null_net_p50 | null_net_p95 | profit_p | DD_p | joint_p | profit_p19 | trades_p50 | minutes_p50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RS | 1000 | -6,387.6780 | 317.3600 | 6,349.2010 | 0.1069 | 0.1009 | 0.0569 | 1.0000 | 396.0000 | 104,480.5000 |
| RT | 1000 | 16,070.6640 | 19,723.7600 | 23,398.7770 | 1.0000 | 0.9990 | 0.9990 | 1.0000 | 387.0000 | 92,697.5000 |
| RD | 1000 | 417.4770 | 3,465.4200 | 6,415.4520 | 0.2118 | 0.5365 | 0.1698 | 1.0000 | 390.0000 | 76,220.5000 |

Raw diagnostic threshold is p<=.05. Direction/causal-delay specificity requires RS AND RD each to pass; RT cannot establish a causal pass. Conservative 19p is only context for 16 prior inspected economic/control definitions plus these 3 fixed null questions. It is not the repo-wide promotion correction or a fresh holdout. There are no new promoted alpha definitions; 3,000 draws do not erase earlier selection or create independent histories.

Year/side null attribution (same path admissions; USD net quantiles):

| null | group | net_p5 | net_p50 | net_p95 | trades_p50 |
| --- | --- | --- | --- | --- | --- |
| RS | long | -3,720.6240 | -385.6400 | 2,792.2380 | 198.0000 |
| RS | short | -2,686.2990 | 660.1700 | 3,656.1050 | 198.0000 |
| RS | 2018 | -1,305.4070 | 173.2200 | 1,643.1070 | 47.0000 |
| RS | 2019 | -978.5190 | 218.0400 | 1,380.2560 | 82.0000 |
| RS | 2020 | -3,174.0870 | -32.3900 | 2,925.9530 | 100.0000 |
| RS | 2021 | -2,573.2120 | -243.7000 | 2,208.8400 | 80.0000 |
| RS | 2022 | -4,585.2460 | 74.5100 | 4,386.0330 | 88.0000 |
| RT | long | 8,081.9400 | 10,482.3000 | 12,755.5970 | 194.0000 |
| RT | short | 6,701.6570 | 9,278.8400 | 12,072.0210 | 193.0000 |
| RT | 2018 | 595.1320 | 1,443.3300 | 2,346.6220 | 45.0000 |
| RT | 2019 | 1,139.7390 | 1,921.1800 | 2,707.1900 | 80.0000 |
| RT | 2020 | 2,186.8710 | 4,056.2300 | 5,796.3020 | 98.0000 |
| RT | 2021 | 2,274.0010 | 3,937.5300 | 5,546.1580 | 78.0000 |
| RT | 2022 | 5,685.7970 | 8,369.7300 | 11,073.1000 | 85.0000 |
| RD | long | 317.5920 | 1,882.3300 | 3,609.4550 | 195.0000 |
| RD | short | -643.8000 | 1,585.8400 | 3,742.2990 | 195.0000 |
| RD | 2018 | -839.7890 | -206.1700 | 385.4570 | 46.0000 |
| RD | 2019 | -324.7300 | 222.5500 | 786.3810 | 81.0000 |
| RD | 2020 | -1,579.3070 | -288.7700 | 984.7180 | 98.0000 |
| RD | 2021 | -459.4450 | 551.2900 | 1,580.6910 | 78.0000 |
| RD | 2022 | 805.8300 | 3,100.3700 | 5,565.6100 | 87.0000 |

## Execution, stresses and saved evidence

| null | stop_first_profit_p | double_cost_net_p5 | double_cost_net_p50 | double_cost_net_p95 | unknown_paths |
| --- | --- | --- | --- | --- | --- |
| RS | 0.1069 | -7,274.6060 | -576.0300 | 5,455.7770 | 0 |
| RT | 1.0000 | 15,199.5280 | 18,853.5200 | 22,527.5290 | 0 |
| RD | 0.2118 | -462.1710 | 2,588.3100 | 5,548.8970 | 0 |

Full catalog retains gross/commission/slippage/net, risk, stop/target, entry/exit, collisions and stop-first outcome. Every per-path CSV records the five metrics, t/NW5, counts, side exposure and earlier/equal/later admissions; compressed paths retain all choice IDs/masks/daily/stress increments. Daily sums reconcile to admitted trade cents. Source/session/clock audits, excluded sessions/trades and original full baseline remain saved. Synthetic checks cover shared-engine parity, exact risk reflection/translation, original-clock reconstruction, missing-risk propagation, early closes, one-position/tie/unknown bounds and integer-cent ranks. The shared minute collision assumption is stressed stop-first with identical draws; extra $2.24/trade is a cost stress, not a tuned rule.

All derived results, including full compact control ledgers, are in the [evidence archive](../../../analysis/outputs/codex_choch_placebos_20261029/evidence.zip); uploaded raw CSVs are excluded. Independent saved-artifact review is distinct from the fresh raw-spec financial checker required before promotion.

## Five plan homes and verdict

| home | verdict | limit |
| --- | --- | --- |
| Personal19 | No earned slot | Full foundation economic/data gates fail; no ADD/REPLACE/EMPTY or one-year plan MC run. |
| 50K funded | No earned slot | No current-book paired bootstrap; no payout/blow improvement established. |
| 150K funded | No earned slot | No current-book paired bootstrap; no payout/blow improvement established. |
| 50K evaluation | No earned slot | No valid current joint account-path comparison; no pass-rate improvement established. |
| 150K evaluation | No earned slot | No valid current joint account-path comparison; no pass-rate improvement established. |

Current adopted book/ranking sources are unchanged at the recorded Claude source snapshot; existing personal/funded/evaluation path and fee limitations remain. The null experiment cannot repair full-source t1.22, the unknown path, prior structural/filter selection, missing historical validation, dependence evidence or plan contribution. No 2023+ prices/returns, additional filters, account simulation, PowerLanguage or live/settings changes were authorized by these diagnostics or performed.

Verdict: finish this diagnostic and retain the foundation as unqualified research. A favorable conditional comparison alone cannot make it a plan candidate. For Claude: review `agents/codex/results/choch_h1_r2_placebos_20261029.md` with all saved controls and limitations.
