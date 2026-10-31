# Hourly two-candle CHoCH filters: no filter earns advancement

Summary: Five frozen configurations were evaluated on 2018–22, including the same-coverage baseline. None passed all registered economic, removal, matched-subset and complete-data gates. These are one-MNQ research results, not book/trading approval. No 2023+ returns were inspected in this phase.

Plan: [preregistration](../plans/choch_h1_r2_filters_20261028.md), public commit `1898b1f597a3ef526ced52778e9a48d12b900fbf`. Implementation commit `898070dc845f282efd86bb102e379220ab4ef96a`; code hashes and source hashes in [summary](../../../analysis/outputs/codex_choch_filters_20261028/design/summary.json). Scripts: [study](../../../analysis/codex_choch_filters.py), [execution](../../../analysis/codex_choch_filters_execution.py), [matched subsets](../../../analysis/codex_choch_filters_subsets.py), [report](../../../analysis/codex_choch_filters_report.py).

## Rule and clocks

The frozen hourly R=2 CHoCH foundation trades both directions: two completed candles on each side confirm a strict swing; a completed-hour close breaking the opposing swing after a structural trend triggers entry. Executable entry is OPEN(signal+2), stop at the prior confirmed opposite swing, gross target twice entry-to-stop risk. Normal decisions 09:00–14:00 CT, flatten at OPEN of close-labelled 15:58; early 09:00/10:00, flatten OPEN 11:30. One position at a time. No overnight holds or later 15:59 exits. 1:2 applies only when the target is reached; timed exits have variable payoffs.

F1/F1_5 require decision-close target distance <=1.0/1.5 times median remaining high–low range in the immediately prior 20 normal cash-calendar sessions. Same-clock history ends at the planned liquidation open; no later liquidation-minute extremes. Every prior window must be complete; missing windows are not replaced by older ones. A4 requires the same direction as the latest fully completed, R=2 confirmed four-hour structure state, including causal CHoCH flips and missing-bar resets. F1_A4 combines strict feasibility and alignment. Full 4h windows are anchored 17:00 CT; incomplete 13–16 stub unused. Both features are known at the signal close; the future fill does not determine acceptance.

## Coverage and reproducibility

Raw hourly signals 1104; intraday-eligible 412; common feature-known eligible 235. Range unavailable 35; 4h context unavailable 162; these can overlap. All five primary runs use the common feature-known universe. Feature availability uses only past information, never future path completeness. Warm-up/coverage exclusions are disclosed separately, not called filter alpha. Original full baseline reproduced to numerical tolerance; corrected full baseline also retained.

| model | trades | net | trade_t | NW5 | maxDD | unresolved |
| --- | --- | --- | --- | --- | --- | --- |
| original_full_baseline | 408 | 4,896.080 | 1.218 | 1.194 | 2,406.600 | 1 |
| corrected_full_baseline | 408 | 4,896.080 | 1.218 | 1.194 | 2,406.600 | 1 |

Unknown-feature full-baseline attribution: `{'full_baseline_states': {'resolved': 175, 'unresolved_missing': 1}, 'resolved_net': -828.5000000000011, 'note': 'Coverage/warmup exclusion, not predictive filter alpha; rerun opportunity sets may differ.'}`. Different opportunity sets can alter later entries; attribution is not an executable return series. Dates 2018-01-01 through 2022-12-30, full weekday daily clock including zero days. 2017 warm-up has no RTH source and can make initial historical ranges unavailable. The reconciled DAY/ON inputs and clock/calendar/source audits are hash-bound to the prior RR2 design; raw user CSVs stay local. Missing expected minutes retain unknown execution states, never zero P&L.

## Executable primary results / USD per MNQ

| model | trades | win_pct | net | trade_t | NW5 | Sharpe | Sortino | PF | Calmar | Ulcer | maxDD | unresolved | pass_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BASE | 233 | 51.502 | 5,724.580 | 1.785 | 1.865 | 0.758 | 1.194 | 1.388 | 0.590 | 0.926 | 1,873.360 | 0 | False |
| F1 | 41 | 36.585 | -521.840 | -0.529 | -0.565 | -0.242 | -0.344 | 0.809 | -0.081 | 1.084 | 1,237.580 | 0 | False |
| F1_5 | 79 | 37.975 | -634.960 | -0.383 | -0.374 | -0.168 | -0.250 | 0.895 | -0.073 | 1.123 | 1,670.600 | 0 | False |
| A4 | 118 | 47.458 | 1,048.180 | 0.492 | 0.467 | 0.217 | 0.357 | 1.139 | 0.134 | 1.241 | 1,512.300 | 0 | False |
| F1_A4 | 21 | 38.095 | -82.540 | -0.118 | -0.116 | -0.053 | -0.085 | 0.932 | -0.023 | 0.657 | 707.920 | 0 | False |

By year, net:

| model | 2018 | 2019 | 2020 | 2021 | 2022 |
| --- | --- | --- | --- | --- | --- |
| BASE | 549.120 | 608.840 | 1,680.120 | 1,362.620 | 1,523.880 |
| F1 | -150.480 | 39.840 | 99.120 | -618.900 | 108.580 |
| F1_5 | 162.540 | 136.620 | -17.280 | -120.800 | -796.040 |
| A4 | 307.820 | 546.440 | 230.320 | -240.220 | 203.820 |
| F1_A4 | -42.740 | 63.060 | -256.940 | -147.200 | 301.280 |

Both sides, same daily calendar:

| model | side | trades | win_pct | net | trade_t | Sharpe | Sortino | PF | Calmar | Ulcer | maxDD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BASE | -1 | 116 | 49.138 | 3,988.660 | 1.547 | 0.676 | 1.247 | 1.498 | 0.705 | 0.836 | 1,092.680 |
| BASE | 1 | 117 | 53.846 | 1,735.920 | 0.907 | 0.399 | 0.589 | 1.258 | 0.178 | 1.171 | 1,884.820 |
| F1 | -1 | 22 | 31.818 | -362.280 | -0.450 | -0.201 | -0.302 | 0.772 | -0.051 | 1.095 | 1,383.380 |
| F1 | 1 | 19 | 42.105 | -159.560 | -0.271 | -0.122 | -0.163 | 0.859 | -0.057 | 0.384 | 542.440 |
| F1_5 | -1 | 40 | 25.000 | -1,625.100 | -1.341 | -0.584 | -0.816 | 0.571 | -0.143 | 1.927 | 2,198.520 |
| F1_5 | 1 | 39 | 51.282 | 990.140 | 0.893 | 0.393 | 0.676 | 1.441 | 0.216 | 0.495 | 883.680 |
| A4 | -1 | 58 | 46.552 | 510.580 | 0.279 | 0.123 | 0.204 | 1.108 | 0.061 | 1.203 | 1,627.020 |
| A4 | 1 | 60 | 48.333 | 537.600 | 0.488 | 0.216 | 0.348 | 1.192 | 0.146 | 0.362 | 709.600 |
| F1_A4 | -1 | 8 | 25.000 | -136.920 | -0.247 | -0.116 | -0.215 | 0.767 | -0.045 | 0.538 | 587.440 |
| F1_A4 | 1 | 13 | 46.154 | 54.380 | 0.119 | 0.054 | 0.075 | 1.086 | 0.037 | 0.192 | 281.460 |

## Fixed-BASE attribution and 1,000 matched random subsets per filter

Filters were first applied to eligible signals and execution rerun; removed signals can free later entries. Separately, filter masks were applied to resolved common BASE trade IDs. Those fixed-trade kept/removed sets and random subsets retain original exits and costs; they are diagnostic overlaps, not executable portfolios. Match exactly year × direction × signal hour and kept counts in every stratum; seed 20261028, 1,000 draws each. Profit p counts random profit >=observed; DD p counts randomDD<=observed; joint counts both; plus-one denominator1001, ties retained. Full summaries, retained memberships and daily paths are in the matched_subsets directory/archive.

| model | base | kept | removed | removed_mean | removed_t | profit_p | DD_p | joint_p | unique_paths | random_strata |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | 5,724.580 | -521.840 | 6,246.420 | 32.533 | 2.051 | 0.877 | 0.644 | 0.635 | 1000 | 16 |
| F1_5 | 5,724.580 | -634.960 | 6,359.540 | 41.296 | 2.330 | 0.975 | 0.841 | 0.839 | 1000 | 20 |
| A4 | 5,724.580 | 1,038.920 | 4,685.660 | 40.394 | 1.955 | 0.789 | 0.537 | 0.508 | 1000 | 34 |
| F1_A4 | 5,724.580 | -82.540 | 5,807.120 | 27.392 | 1.854 | 0.623 | 0.499 | 0.451 | 1000 | 11 |

## Costs, execution and stress

Native one-MNQ cost is $1.24 round-trip commission plus one 0.25-point tick per fill ($1.00 total slippage): $2.24/trade. Gross gate requires >$4.48 mean gross. A market fill at/beyond stop now exits immediately at its fill open and pays costs; prior zero-fee deletion is preserved only as a historical reference. Same shared grid minute walker: active entry-bar protection, worse stop gaps and 1-point target-through. The nearest-extreme same-minute collision assumption is stress-tested stop-first, not selected afterward.

| model | gross | commission | slippage | gross_mean | extra_cost_breakeven | double_cost_net | stop_first_net | collisions | entry_gap_stops |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BASE | 6,246.500 | 288.920 | 233.000 | 26.809 | 24.569 | 5,202.660 | 5,724.580 | 0 | 0 |
| F1 | -430.000 | 50.840 | 41.000 | -10.488 | -12.728 | -613.680 | -521.840 | 0 | 0 |
| F1_5 | -458.000 | 97.960 | 79.000 | -5.797 | -8.037 | -811.920 | -634.960 | 0 | 0 |
| A4 | 1,312.500 | 146.320 | 118.000 | 11.123 | 8.883 | 783.860 | 1,048.180 | 0 | 0 |
| F1_A4 | -35.500 | 26.040 | 21.000 | -1.690 | -3.930 | -129.580 | -82.540 | 0 | 0 |

Every original/corrected full reference, primary ledger, stop-first ledger, daily series, signal-feature table and 4h state table is retained. Synthetic checks include core-state parity, prefix/mirror/as-of/reset behavior, previous20-session clocks and missing-history rejection, future-fill invariance, entry gap charging, active stops, target-through, collision stress and early-close/time-open liquidation. Resolved trade P&L reconciles to daily P&L. Gaps not affecting known signals can still affect the full opportunity set; observed-subset performance is not a claim of a complete executable track record.

Independent saved-artifact checks reconciled all five ledgers, feature masks, costs, trade t/daily NW5 and all 4,000 random paths reconstructed from packed memberships. Cent-rounded comparisons change no p-values or ties. This is an artifact review, not a fresh raw-price/spec rebuild. The full derived [evidence archive](../../../analysis/outputs/codex_choch_filters_20261028/evidence.zip) includes the long selected-ID CSVs and all NPZ paths; [artifact manifest](../../../analysis/outputs/codex_choch_filters_20261028/artifact_manifest.json) records their hashes. No uploaded raw CSV is in this archive. A4 kept117 fixed-BASE trades but executed118 after signals were freed; the corresponding $1,038.92 subset and $1,048.18 executable totals are intentionally separate.

## Gates, selection history and five plan homes

Registered advancement requires >=30 resolved trades, trade t>=2, netpositive, gross hurdle, >=3/5 positive years and no unresolved paths; fixed-BASE kept total must exceed BASE, removed total negative, matched-subset profit and DD p<=.05; rerun executable total must improve BASE with no larger DD and positive stop-first/double-cost net. A prettier per-trade average, selected side/year or lower DD by itself cannot pass.

Five primary definitions inspected (reused BASE plus four active filters); four new active economic filter definitions. Six prior structural configurations/twelve prior economic definitions including ideal-close controls remain in family history: 16 active economic/control definitions after this phase, plus separately retained coverage, source rerun, entry-gap correction and execution stress references. The bounded Hunt v2/t6 budgets/programs stay closed. 4,000 matched diagnostic draws are selection diagnostics; all family selection history remains counted.

| home | verdict | evidence |
| --- | --- | --- |
| Personal19 | No earned slot | Filter design gates fail; paired ADD/REPLACE/EMPTY benches not run. |
| 50K funded | No earned slot | Design fails; current T_ONESIDE-fade book and valid paired account paths not tested. |
| 150K funded | No earned slot | Design fails; valid paired funded bootstrap not run. |
| 50K evaluation | No earned slot | Design fails; synchronized joint intraday account paths not tested. |
| 150K evaluation | No earned slot | Design fails; synchronized joint intraday account paths not tested. |

The stop rule applies before plan benches, Monte Carlo at plan size, random-time/random-side placebos or historical validation. No measured harm to every plan is claimed; the candidate has not earned those tests. Current personal/funded/evaluation source context is saved in [book review](../research/choch_filters_book_context.md).

## Limitations and verdict

The filter choices were motivated by previously observed weak baseline results and share price information; they have no identified forced participant. No full 2018–26 t, selection-adjusted promotion, dependence/placebo pass, fresh independent raw-spec rebuild, forward evidence or account pass/payout benefit is established. Independent code review before outcomes was completed, but is not an independent financial replication. No PowerLanguage or live deployment was produced.

Verdict: Reject these four frozen filters as advancement candidates; stop this approved filter experiment without retuning.

For Claude: review `agents/codex/results/choch_h1_r2_filters_20261028.md` and the retained ledgers/subset paths. Reproduce with `python -B analysis/codex_choch_filters.py --design` only in a clean output destination with the hash-bound local source mount; the script refuses to overwrite the original design. Render with `python -B analysis/codex_choch_filters_report.py`.
