# OB v2 against the current plans: WATCH
Summary: Test the submitted ATR-regime ORB as an ONB replacement and a 1-MNQ addition.
Standalone replay: 568 trades, $374/NQ net, PF 1.69, t 4.73.
Funded BASE → replacement → addition: year-1 payouts $9,294 → $8,086 → $9,316.
Evaluation pass: 50.2% → 43.4% → 49.3%.
No OB v2 configuration clears the registered account gates; keep the current plans.

Plan: `agents/codex/plans/ob_v2_plan_test.md`, commit `7d7714b` (pushed before returns).

Scripts: `analysis/codex_ob_v2_{replay,accounts,diagnostics,report}.py`.

Outputs: `analysis/outputs/codex_ob_v2_plan_test/`. Two fixed strategy ledgers; five fixed configurations per account; trial accounting below.

## Rule (as tested)

User authorized assuming matching data. OBV2 retains the submitted 0.6–1.2 ATR15/ATR100 RTH ratio, ADX(16) ≥20, midnight-to-08:30 overnight bias, 08:30–08:45 opening range, close-confirmed breakout, OR/exhaustion gates, four-entry cap, signal-close 0.30 RTH-ATR stop and 3R target. Signals end at noon; flatten decision 14:30 CT. End-stamped 09:00 signals fill at the open of the minute labeled 09:01.

The existing plan's half-day overlay is explicit: no new signals at/after 11:00 CT and 11:30 flatten decision. This differs from the uploaded fixed-time source. BRIDGE100 disables only the ratio and retains identical 100-session warm-up and execution. It is a diagnostic comparator, never an alternative selected from results.

The 2017 May–December RTH export seeds indicators in memory; original cached indices and caches stay unchanged. Both ledgers run on common 2018-01-02–2026-10-09 history. Commission is $7.25/NQ RT, one adverse tick per market/stop fill, one-point target trade-through, gap-aware stops including entry minute, stop-first if both exits occur in one minute. Nominal stop-distance risk sizing preserves source-close anchors; actual entry gap risk can differ.

The 2018–22 cheap gate passed before any recent returns: 293 trades, $77,284.65 NQ net, PF 1.598, gross $280.75/trade versus $16.98 modeled costs, five profitable years. Longs: 154/$249.04 average; shorts: 139/$280.09. No side or parameter was selected. 2023+ is historical replication: the author had already used it when selecting the filter.

## Results

Dollar metrics below are per one NQ, after the stated costs. Daily risk ratios include zero-trade trading sessions. DSR uses the current ranked-item count; it does not erase original-author selection exposure.

| Ledger | Period | Side | n | Win | $/trade | Net | t | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD | DSR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OBV2 | full | all | 568 | 51.8% | $374 | $212,643 | 4.73 | 1.55 | 3.22 | 1.69 | 2.33 | 3.24 | $10,157 | 0.98 |
| OBV2 | full | long | 309 | 56.0% | $431 | $133,267 | 4.17 | 1.41 | 2.95 | 1.88 | 1.45 | 2.71 | $10,243 | 0.92 |
| OBV2 | full | short | 259 | 46.7% | $306 | $79,375 | 2.51 | 0.80 | 1.65 | 1.51 | 0.63 | 5.26 | $14,039 | 0.35 |
| OBV2 | design | all | 293 | 50.5% | $264 | $77,285 | 2.99 | 1.29 | 2.60 | 1.60 | 1.61 | 3.82 | $9,395 | 0.55 |
| OBV2 | design | long | 154 | 54.5% | $249 | $38,352 | 2.31 | 1.02 | 1.97 | 1.65 | 0.73 | 3.05 | $10,243 | 0.28 |
| OBV2 | design | short | 139 | 46.0% | $280 | $38,932 | 1.96 | 0.83 | 1.73 | 1.56 | 0.65 | 5.61 | $11,649 | 0.16 |
| OBV2 | recent | all | 275 | 53.1% | $492 | $135,358 | 3.69 | 1.85 | 3.89 | 1.76 | 3.45 | 4.93 | $10,157 | 0.81 |
| OBV2 | recent | long | 155 | 57.4% | $612 | $94,915 | 3.49 | 1.81 | 3.91 | 2.03 | 3.35 | 3.42 | $7,342 | 0.75 |
| OBV2 | recent | short | 120 | 47.5% | $337 | $40,443 | 1.64 | 0.79 | 1.63 | 1.48 | 0.75 | 6.94 | $14,039 | 0.09 |
| BRIDGE100 | full | all | 778 | 51.3% | $310 | $240,808 | 4.35 | 1.45 | 2.75 | 1.51 | 1.62 | 3.19 | $16,611 | 0.94 |
| BRIDGE100 | full | long | 432 | 55.3% | $308 | $133,161 | 3.55 | 1.21 | 2.16 | 1.56 | 1.05 | 4.28 | $14,195 | 0.76 |
| BRIDGE100 | full | short | 346 | 46.2% | $311 | $107,647 | 2.64 | 0.87 | 1.72 | 1.46 | 0.81 | 4.15 | $14,814 | 0.40 |
| BRIDGE100 | design | all | 428 | 50.2% | $236 | $100,927 | 3.07 | 1.37 | 2.60 | 1.49 | 1.19 | 3.73 | $16,535 | 0.58 |
| BRIDGE100 | design | long | 227 | 53.7% | $180 | $40,943 | 2.03 | 0.89 | 1.52 | 1.42 | 0.56 | 5.24 | $14,195 | 0.19 |
| BRIDGE100 | design | short | 201 | 46.3% | $298 | $59,983 | 2.31 | 1.04 | 2.14 | 1.55 | 1.30 | 4.01 | $9,010 | 0.27 |
| BRIDGE100 | recent | all | 350 | 52.6% | $400 | $139,882 | 3.14 | 1.59 | 3.00 | 1.54 | 2.18 | 5.33 | $16,611 | 0.61 |
| BRIDGE100 | recent | long | 205 | 57.1% | $450 | $92,218 | 2.92 | 1.53 | 2.80 | 1.66 | 2.68 | 3.90 | $8,926 | 0.52 |
| BRIDGE100 | recent | short | 145 | 46.2% | $329 | $47,664 | 1.51 | 0.74 | 1.45 | 1.39 | 0.83 | 7.51 | $14,814 | 0.07 |

By year, including each side:

| Ledger | Period | Side | n | Win | $/trade | Net | t | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD | DSR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OBV2 | 2018 | all | 44 | 45.5% | $22 | $972 | 0.22 | 0.18 | 0.33 | 1.09 | 0.18 | 4.04 | $5,251 | 0.00 |
| OBV2 | 2018 | long | 21 | 47.6% | $-46 | $-969 | -0.45 | -0.42 | -0.53 | 0.80 | -0.42 | 2.28 | $2,260 | 0.00 |
| OBV2 | 2018 | short | 23 | 43.5% | $84 | $1,941 | 0.49 | 0.41 | 0.84 | 1.32 | 0.61 | 2.77 | $3,102 | 0.01 |
| OBV2 | 2019 | all | 57 | 50.9% | $109 | $6,238 | 1.16 | 1.23 | 2.42 | 1.49 | 2.74 | 1.89 | $2,220 | 0.03 |
| OBV2 | 2019 | long | 34 | 55.9% | $102 | $3,465 | 0.95 | 0.94 | 1.82 | 1.53 | 1.53 | 1.64 | $2,212 | 0.02 |
| OBV2 | 2019 | short | 23 | 43.5% | $121 | $2,774 | 0.69 | 0.79 | 1.60 | 1.45 | 1.94 | 1.25 | $1,399 | 0.01 |
| OBV2 | 2020 | all | 49 | 51.0% | $384 | $18,818 | 1.75 | 1.76 | 3.91 | 1.90 | 3.16 | 2.57 | $5,823 | 0.11 |
| OBV2 | 2020 | long | 34 | 55.9% | $362 | $12,299 | 1.49 | 1.46 | 3.12 | 1.94 | 2.09 | 2.66 | $5,750 | 0.06 |
| OBV2 | 2020 | short | 15 | 40.0% | $435 | $6,519 | 0.92 | 0.98 | 2.36 | 1.84 | 2.12 | 1.64 | $3,008 | 0.02 |
| OBV2 | 2021 | all | 71 | 49.3% | $204 | $14,517 | 1.25 | 1.11 | 2.17 | 1.43 | 1.75 | 5.56 | $8,105 | 0.04 |
| OBV2 | 2021 | long | 40 | 57.5% | $315 | $12,592 | 1.63 | 1.69 | 3.42 | 1.86 | 3.44 | 1.83 | $3,577 | 0.10 |
| OBV2 | 2021 | short | 31 | 38.7% | $62 | $1,925 | 0.22 | 0.18 | 0.34 | 1.10 | 0.19 | 8.71 | $9,893 | 0.00 |
| OBV2 | 2022 | all | 72 | 54.2% | $510 | $36,738 | 1.92 | 1.88 | 3.79 | 1.72 | 3.82 | 5.54 | $9,395 | 0.15 |
| OBV2 | 2022 | long | 25 | 52.0% | $439 | $10,965 | 0.95 | 0.94 | 1.74 | 1.54 | 1.05 | 7.89 | $10,243 | 0.02 |
| OBV2 | 2022 | short | 47 | 55.3% | $548 | $25,773 | 1.67 | 1.64 | 3.50 | 1.84 | 3.09 | 4.66 | $8,141 | 0.09 |
| OBV2 | 2023 | all | 90 | 48.9% | $192 | $17,281 | 1.23 | 1.24 | 2.07 | 1.34 | 1.67 | 7.85 | $10,157 | 0.05 |
| OBV2 | 2023 | long | 47 | 55.3% | $346 | $16,251 | 1.49 | 1.47 | 2.62 | 1.63 | 2.79 | 4.00 | $5,712 | 0.08 |
| OBV2 | 2023 | short | 43 | 41.9% | $24 | $1,030 | 0.12 | 0.12 | 0.18 | 1.04 | 0.09 | 11.76 | $11,348 | 0.00 |
| OBV2 | 2024 | all | 80 | 55.0% | $638 | $51,005 | 2.78 | 2.58 | 5.86 | 2.15 | 5.19 | 6.56 | $9,567 | 0.45 |
| OBV2 | 2024 | long | 47 | 53.2% | $522 | $24,514 | 1.75 | 1.63 | 3.24 | 1.85 | 3.25 | 6.37 | $7,342 | 0.11 |
| OBV2 | 2024 | short | 33 | 57.6% | $803 | $26,491 | 2.21 | 2.04 | 6.12 | 2.74 | 8.69 | 1.75 | $2,966 | 0.22 |
| OBV2 | 2025 | all | 37 | 56.8% | $250 | $9,267 | 0.82 | 0.80 | 1.31 | 1.40 | 1.74 | 3.25 | $5,232 | 0.02 |
| OBV2 | 2025 | long | 22 | 63.6% | $402 | $8,852 | 1.12 | 1.07 | 1.82 | 1.81 | 1.92 | 2.01 | $4,518 | 0.04 |
| OBV2 | 2025 | short | 15 | 46.7% | $28 | $415 | 0.05 | 0.05 | 0.08 | 1.03 | 0.10 | 2.96 | $3,989 | 0.00 |
| OBV2 | 2026 | all | 68 | 54.4% | $850 | $57,805 | 2.22 | 2.48 | 5.88 | 1.98 | 7.49 | 3.00 | $9,718 | 0.24 |
| OBV2 | 2026 | long | 39 | 61.5% | $1,161 | $45,298 | 2.40 | 2.91 | 8.44 | 2.68 | 8.62 | 2.58 | $6,622 | 0.29 |
| OBV2 | 2026 | short | 29 | 44.8% | $431 | $12,507 | 0.70 | 0.72 | 1.52 | 1.39 | 1.12 | 7.15 | $14,039 | 0.01 |
| BRIDGE100 | 2018 | all | 89 | 46.1% | $43 | $3,832 | 0.46 | 0.42 | 0.74 | 1.13 | 0.70 | 4.80 | $5,381 | 0.01 |
| BRIDGE100 | 2018 | long | 47 | 46.8% | $-9 | $-437 | -0.09 | -0.08 | -0.13 | 0.97 | -0.08 | 6.54 | $5,283 | 0.00 |
| BRIDGE100 | 2018 | short | 42 | 45.2% | $102 | $4,269 | 0.63 | 0.57 | 1.09 | 1.30 | 1.18 | 3.36 | $3,554 | 0.01 |
| BRIDGE100 | 2019 | all | 74 | 47.3% | $110 | $8,141 | 1.25 | 1.36 | 2.78 | 1.46 | 2.33 | 2.65 | $3,420 | 0.04 |
| BRIDGE100 | 2019 | long | 43 | 53.5% | $127 | $5,481 | 1.24 | 1.22 | 2.59 | 1.65 | 2.60 | 1.82 | $2,058 | 0.04 |
| BRIDGE100 | 2019 | short | 31 | 38.7% | $86 | $2,660 | 0.55 | 0.66 | 1.32 | 1.28 | 1.14 | 1.90 | $2,271 | 0.01 |
| BRIDGE100 | 2020 | all | 77 | 51.9% | $303 | $23,351 | 1.81 | 1.81 | 3.44 | 1.69 | 3.92 | 2.93 | $5,823 | 0.13 |
| BRIDGE100 | 2020 | long | 50 | 58.0% | $363 | $18,156 | 1.95 | 1.86 | 3.59 | 2.03 | 3.08 | 2.63 | $5,750 | 0.16 |
| BRIDGE100 | 2020 | short | 27 | 40.7% | $192 | $5,196 | 0.57 | 0.61 | 1.15 | 1.32 | 1.69 | 2.99 | $3,008 | 0.01 |
| BRIDGE100 | 2021 | all | 93 | 51.6% | $228 | $21,162 | 1.35 | 1.29 | 2.48 | 1.42 | 2.78 | 4.76 | $7,437 | 0.05 |
| BRIDGE100 | 2021 | long | 50 | 60.0% | $267 | $13,333 | 1.48 | 1.52 | 2.70 | 1.66 | 5.00 | 1.86 | $2,602 | 0.08 |
| BRIDGE100 | 2021 | short | 43 | 41.9% | $182 | $7,829 | 0.60 | 0.56 | 1.12 | 1.26 | 0.85 | 7.27 | $9,010 | 0.01 |
| BRIDGE100 | 2022 | all | 95 | 53.7% | $468 | $44,440 | 1.88 | 1.93 | 3.67 | 1.58 | 2.63 | 9.42 | $16,535 | 0.15 |
| BRIDGE100 | 2022 | long | 37 | 48.6% | $119 | $4,411 | 0.31 | 0.31 | 0.50 | 1.12 | 0.33 | 13.87 | $12,870 | 0.00 |
| BRIDGE100 | 2022 | short | 58 | 56.9% | $690 | $40,030 | 2.13 | 2.20 | 4.86 | 2.00 | 4.80 | 3.62 | $8,141 | 0.20 |
| BRIDGE100 | 2023 | all | 90 | 48.9% | $192 | $17,281 | 1.23 | 1.24 | 2.07 | 1.34 | 1.67 | 7.85 | $10,157 | 0.05 |
| BRIDGE100 | 2023 | long | 47 | 55.3% | $346 | $16,251 | 1.49 | 1.47 | 2.62 | 1.63 | 2.79 | 4.00 | $5,712 | 0.08 |
| BRIDGE100 | 2023 | short | 43 | 41.9% | $24 | $1,030 | 0.12 | 0.12 | 0.18 | 1.04 | 0.09 | 11.76 | $11,348 | 0.00 |
| BRIDGE100 | 2024 | all | 100 | 56.0% | $584 | $58,428 | 2.66 | 2.51 | 5.17 | 1.94 | 5.94 | 6.48 | $9,567 | 0.41 |
| BRIDGE100 | 2024 | long | 62 | 54.8% | $433 | $26,846 | 1.64 | 1.55 | 2.78 | 1.65 | 2.93 | 7.12 | $8,926 | 0.10 |
| BRIDGE100 | 2024 | short | 38 | 57.9% | $831 | $31,582 | 2.14 | 2.01 | 5.36 | 2.52 | 6.37 | 1.96 | $4,821 | 0.20 |
| BRIDGE100 | 2025 | all | 81 | 51.9% | $74 | $6,010 | 0.26 | 0.26 | 0.41 | 1.08 | 0.40 | 6.99 | $14,602 | 0.00 |
| BRIDGE100 | 2025 | long | 48 | 60.4% | $93 | $4,474 | 0.32 | 0.33 | 0.45 | 1.12 | 0.49 | 4.19 | $8,907 | 0.01 |
| BRIDGE100 | 2025 | short | 33 | 39.4% | $47 | $1,536 | 0.08 | 0.08 | 0.14 | 1.04 | 0.13 | 7.90 | $11,941 | 0.00 |
| BRIDGE100 | 2026 | all | 79 | 53.2% | $736 | $58,162 | 2.11 | 2.37 | 5.22 | 1.82 | 7.54 | 3.26 | $9,718 | 0.20 |
| BRIDGE100 | 2026 | long | 48 | 58.3% | $930 | $44,647 | 2.21 | 2.70 | 6.62 | 2.25 | 8.49 | 2.81 | $6,622 | 0.23 |
| BRIDGE100 | 2026 | short | 31 | 45.2% | $436 | $13,515 | 0.71 | 0.74 | 1.52 | 1.38 | 1.21 | 7.15 | $14,039 | 0.01 |

Max DD above includes the initial zero-equity peak (`resampling.max_dd`). The CSV also retains the unmodified `metrics.perf` convention. Recent block-bootstrap 5/95 bands:

| Ledger | Side | Metric | Actual | 5% | 50% | 95% |
| --- | --- | --- | --- | --- | --- | --- |
| OBV2 | all | sharpe | 1.8499 | 1.18585 | 1.8919 | 2.57339 |
| OBV2 | all | sortino | 3.89492 | 2.19576 | 4.01675 | 6.15491 |
| OBV2 | all | pf_day | 1.89065 | 1.48389 | 1.92364 | 2.5034 |
| OBV2 | all | calmar | 3.45147 | 1.11286 | 2.73169 | 5.52945 |
| OBV2 | all | ulcer | 4.92858 | 1.8989 | 3.61508 | 8.32794 |
| OBV2 | all | max_dd | 10157.1 | 8138.83 | 12803.2 | 22011.6 |
| OBV2 | all | annual | 35056.7 | 20733 | 35642.2 | 51081.7 |
| OBV2 | all | P(Sharpe<=0) | — | — | 0 | — |
| OBV2 | long | sharpe | 1.80551 | 1.09459 | 1.85569 | 2.56105 |
| OBV2 | long | sortino | 3.90825 | 2.035 | 4.05171 | 6.77788 |
| OBV2 | long | pf_day | 2.22216 | 1.59247 | 2.28655 | 3.34665 |
| OBV2 | long | calmar | 3.34812 | 0.945936 | 2.52984 | 5.47925 |
| OBV2 | long | ulcer | 3.42436 | 1.541 | 3.12106 | 7.47004 |
| OBV2 | long | max_dd | 7342.1 | 5955.13 | 9682.18 | 17141.2 |
| OBV2 | long | annual | 24582.2 | 13774.5 | 24957.8 | 36891.9 |
| OBV2 | long | P(Sharpe<=0) | — | — | 0 | — |
| OBV2 | short | sharpe | 0.789995 | -0.0623861 | 0.811354 | 1.52053 |
| OBV2 | short | sortino | 1.62695 | -0.0976942 | 1.64809 | 4.07086 |
| OBV2 | short | pf_day | 1.54421 | 0.96882 | 1.54843 | 2.42722 |
| OBV2 | short | calmar | 0.746105 | -0.0295072 | 0.698163 | 2.35455 |
| OBV2 | short | ulcer | 6.93711 | 3.25867 | 7.86051 | 23.618 |
| OBV2 | short | max_dd | 14038.9 | 8168.77 | 14799.1 | 29335.9 |
| OBV2 | short | annual | 10474.5 | -690.403 | 10510.5 | 22902 |
| OBV2 | short | P(Sharpe<=0) | — | — | 0.0592 | — |
| BRIDGE100 | all | sharpe | 1.59095 | 0.870251 | 1.62494 | 2.30679 |
| BRIDGE100 | all | sortino | 3.00069 | 1.48651 | 3.07306 | 4.802 |
| BRIDGE100 | all | pf_day | 1.60531 | 1.28657 | 1.62258 | 2.01716 |
| BRIDGE100 | all | calmar | 2.18098 | 0.713315 | 2.02252 | 4.20777 |
| BRIDGE100 | all | ulcer | 5.32544 | 2.53491 | 5.11528 | 12.7572 |
| BRIDGE100 | all | max_dd | 16611.1 | 11442.3 | 17876.6 | 31071.6 |
| BRIDGE100 | all | annual | 36228.4 | 18913.8 | 36839 | 54510 |
| BRIDGE100 | all | P(Sharpe<=0) | — | — | 0.0002 | — |
| BRIDGE100 | long | sharpe | 1.52609 | 0.781686 | 1.56124 | 2.30153 |
| BRIDGE100 | long | sortino | 2.79689 | 1.26499 | 2.87128 | 4.86745 |
| BRIDGE100 | long | pf_day | 1.76844 | 1.33156 | 1.79751 | 2.44032 |
| BRIDGE100 | long | calmar | 2.67561 | 0.592055 | 1.84745 | 4.24856 |
| BRIDGE100 | long | ulcer | 3.89933 | 2.17188 | 4.4472 | 11.0138 |
| BRIDGE100 | long | max_dd | 8926.45 | 7962.55 | 12954.7 | 23084.8 |
| BRIDGE100 | long | annual | 23883.7 | 11794.2 | 24296.7 | 37595.8 |
| BRIDGE100 | long | P(Sharpe<=0) | — | — | 0.0008 | — |
| BRIDGE100 | short | sharpe | 0.743123 | -0.100223 | 0.747992 | 1.49919 |
| BRIDGE100 | short | sortino | 1.44638 | -0.166712 | 1.44597 | 3.56286 |
| BRIDGE100 | short | pf_day | 1.42908 | 0.954464 | 1.42696 | 2.11956 |
| BRIDGE100 | short | calmar | 0.833328 | -0.0482513 | 0.599384 | 2.10182 |
| BRIDGE100 | short | ulcer | 7.50992 | 4.02088 | 9.96549 | 30.9876 |
| BRIDGE100 | short | max_dd | 14813.7 | 11388.4 | 20236.8 | 39293.2 |
| BRIDGE100 | short | annual | 12344.7 | -1538.09 | 12315.3 | 27428.6 |
| BRIDGE100 | short | P(Sharpe<=0) | — | — | 0.0758 | — |

## Placebos and account level

### Filter diagnostics

OBV2 is an exact subset of BRIDGE100 at the common warm-up; kept trades have identical fills and exits. The removed trades test the bad-trade-removal claim separately from whether less exposure improves payouts.

The filter reduces drawdown, but the 210 removed trades earned $134 each (t 0.87). It does not meet the development process's requirement that removed trades lose money; improved average profit alone does not establish a useful filter. The pre-registered account tests were still completed to assess its exposure reduction.

| Group | Period | n | $/trade | Net | t | Max DD |
| --- | --- | --- | --- | --- | --- | --- |
| kept | full | 568 | $374 | $212,643 | 4.73 | $10,157 |
| kept | design | 293 | $264 | $77,285 | 2.99 | $9,395 |
| kept | recent | 275 | $492 | $135,358 | 3.69 | $10,157 |
| removed | full | 210 | $134 | $28,166 | 0.87 | $14,939 |
| removed | design | 135 | $175 | $23,642 | 1.16 | $13,310 |
| removed | recent | 75 | $60 | $4,524 | 0.18 | $14,939 |
| unfiltered | full | 778 | $310 | $240,808 | 4.35 | $16,611 |
| unfiltered | design | 428 | $236 | $100,927 | 3.07 | $16,535 |
| unfiltered | recent | 350 | $400 | $139,882 | 3.14 | $16,611 |

Each null uses 1,000 fixed-seed draws per period. Trade drops preserve year/side retained counts; event-day drops preserve yearly retained-day counts and entire within-day sequences. Lower tail probabilities below mean the actual filter beat more random drops; joint dominance is descriptive.

| Period | Null | Actual net | Null median net | Actual DD | Null median DD | P(null profit ≥ actual) | P(null DD ≤ actual) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full | year_side_exact_trade_count | $212,643 | $191,341 | $10,157 | $15,919 | 16.6% | 1.7% |
| full | year_exact_event_day_count | $212,643 | $190,758 | $10,157 | $16,042 | 16.1% | 1.1% |
| design | year_side_exact_trade_count | $77,285 | $75,171 | $9,395 | $12,759 | 44.5% | 12.5% |
| design | year_exact_event_day_count | $77,285 | $73,710 | $9,395 | $13,709 | 40.4% | 5.0% |
| recent | year_side_exact_trade_count | $135,358 | $118,056 | $10,157 | $13,919 | 14.4% | 10.1% |
| recent | year_exact_event_day_count | $135,358 | $118,411 | $10,157 | $13,118 | 17.0% | 14.8% |

Random side and random entry time use 100 replays each, fixed observed event days and stop distances. One-position collisions can reduce counts, so effective counts and total net accompany averages. No control becomes a selected strategy.

The precise breakout timing is not supported by this timing null: 77/100 random-time paths exceeded actual full-period total profit despite fewer effective trades. This is descriptive and conditional on observed event days, not an independently validated replacement rule.

| Control | Period | Actual n | Min n | Median n | Max n | Actual net | Null median net | P(null profit ≥ actual) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| random_side | full | 568 | 540 | 546 | 553 | $212,643 | $31,598 | 0.0% |
| random_side | design | 293 | 278 | 283 | 287 | $77,285 | $20,135 | 2.0% |
| random_side | recent | 275 | 258 | 263 | 268 | $135,358 | $8,785 | 0.0% |
| random_entry_time | full | 568 | 522 | 530 | 537 | $212,643 | $233,916 | 77.0% |
| random_entry_time | design | 293 | 272 | 275 | 280 | $77,285 | $81,874 | 70.0% |
| random_entry_time | recent | 275 | 248 | 254 | 261 | $135,358 | $150,180 | 78.0% |

Standalone 1-MNQ daily Monte Carlo (5,000 ten-day-block paths, 252-session horizon):

| Ledger | Period | Cost | P&L 5% | P&L 50% | P&L 95% | DD 95% | EOD trail hit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OBV2 | full | scaled_NQ | $195 | $2,285 | $4,927 | $1,418 | 0.7% |
| OBV2 | full | candidate_extra_1.275_MNQ_RT | $109 | $2,203 | $4,838 | $1,449 | 0.8% |
| OBV2 | design | scaled_NQ | $-117 | $1,471 | $3,301 | $1,187 | 0.2% |
| OBV2 | design | candidate_extra_1.275_MNQ_RT | $-190 | $1,398 | $3,226 | $1,219 | 0.2% |
| OBV2 | recent | scaled_NQ | $728 | $3,558 | $6,687 | $1,661 | 1.4% |
| OBV2 | recent | candidate_extra_1.275_MNQ_RT | $641 | $3,471 | $6,588 | $1,697 | 1.5% |
| BRIDGE100 | full | scaled_NQ | $35 | $2,645 | $5,690 | $1,954 | 3.6% |
| BRIDGE100 | full | candidate_extra_1.275_MNQ_RT | $-70 | $2,534 | $5,579 | $2,000 | 4.0% |
| BRIDGE100 | design | scaled_NQ | $-162 | $1,962 | $4,243 | $1,547 | 1.1% |
| BRIDGE100 | design | candidate_extra_1.275_MNQ_RT | $-276 | $1,853 | $4,134 | $1,590 | 1.3% |
| BRIDGE100 | recent | scaled_NQ | $414 | $3,676 | $7,222 | $2,305 | 6.9% |
| BRIDGE100 | recent | candidate_extra_1.275_MNQ_RT | $305 | $3,560 | $7,101 | $2,344 | 7.5% |

This existing standalone tool checks EOD equity only. The account comparisons below use minute adverse equity and daily limits. Primary MNQ costs scale NQ costs by 0.1; the mandatory stress adds $1.275/MNQ RT to challenger trades only ($2 commission plus existing slippage). It is an adverse sensitivity, not verified native MNQ accounting.

### Current funded plan

Roster: VB normal 2/flagged 1 MNQ, ONB ML risk $400, Monday 1, EOS risk $700, LDF 2, NFP risk $500, Bridge Monday 1, CL Sunday 2 MCL, ES MOC 2 MES, RS longs 1 MNQ. Existing cushion factor clips to [0.5,1], full size at $1,500 cushion, then floors whole micros. A 1-MNQ addition therefore trades zero when the floored scaled size is below one.

1,000 paired 500-session circular histories, 20-day blocks, seed 1. Same complete days for all configurations. Days to six uses infinity for noncompletion; outcome bands describe histories, whereas paired intervals estimate mean differences. Baseline differs slightly from the earlier FC 2B table because that run pooled four worker seeds; this preregistration fixes one 1,000-history seed-1 sample.

| Configuration | Year 1 | Y1 5% | Y1 95% | Year 2 | Y2 5% | Y2 95% | Blown | Six payouts | Days to six |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BASE | $9,294 | $0 | $13,000 | $12,012 | $0 | $13,000 | 7.7% | 91.4% | 258.5 |
| EMPTY_ONB | $7,230 | $0 | $13,000 | $11,368 | $0 | $13,000 | 10.5% | 81.3% | 322 |
| REPLACE_OBV2 | $8,086 | $0 | $13,000 | $10,474 | $0 | $13,000 | 19.4% | 78.2% | 283 |
| ADD_OBV2 | $9,316 | $0 | $13,000 | $11,904 | $0 | $13,000 | 8.3% | 90.3% | 252 |
| REPLACE_BRIDGE100 | $7,622 | $0 | $13,000 | $9,640 | $0 | $13,000 | 26.4% | 71.5% | 291 |

Paired differences, 95% intervals from 5,000 resamples (seed 902); dollar rows use dollars, blown rows use proportions:

| Configuration | Reference | Metric | Difference | 95% low | 95% high |
| --- | --- | --- | --- | --- | --- |
| EMPTY_ONB | BASE | year1 | -2064.5 | -2277.01 | -1846.98 |
| EMPTY_ONB | BASE | year2 | -643.5 | -878 | -401.488 |
| EMPTY_ONB | BASE | blown | 0.028 | 0.008 | 0.047 |
| REPLACE_OBV2 | BASE | year1 | -1208 | -1456.51 | -956.975 |
| REPLACE_OBV2 | BASE | year2 | -1538 | -1839.51 | -1229.49 |
| REPLACE_OBV2 | BASE | blown | 0.117 | 0.092 | 0.142 |
| REPLACE_OBV2 | EMPTY_ONB | year1 | 856.5 | 620.987 | 1094.01 |
| REPLACE_OBV2 | EMPTY_ONB | year2 | -894.5 | -1210 | -588.488 |
| REPLACE_OBV2 | EMPTY_ONB | blown | 0.089 | 0.064 | 0.115 |
| ADD_OBV2 | BASE | year1 | 21.5 | -101.513 | 145.537 |
| ADD_OBV2 | BASE | year2 | -107.5 | -237.5 | 18.5 |
| ADD_OBV2 | BASE | blown | 0.006 | -0.005 | 0.017 |
| REPLACE_BRIDGE100 | BASE | year1 | -1672 | -1941.53 | -1406.95 |
| REPLACE_BRIDGE100 | BASE | year2 | -2371.5 | -2715 | -2035.5 |
| REPLACE_BRIDGE100 | BASE | blown | 0.187 | 0.16 | 0.215 |
| REPLACE_BRIDGE100 | EMPTY_ONB | year1 | 392.5 | 126 | 649 |
| REPLACE_BRIDGE100 | EMPTY_ONB | year2 | -1728 | -2087.51 | -1387.5 |
| REPLACE_BRIDGE100 | EMPTY_ONB | blown | 0.159 | 0.131 | 0.188 |

Challenger-only higher-cost sensitivity:

| Configuration | Year 1 | Year 2 | Blown | Six payouts | Days to six |
| --- | --- | --- | --- | --- | --- |
| BASE | $9,294 | $12,012 | 7.7% | 91.4% | 258.5 |
| EMPTY_ONB | $7,230 | $11,368 | 10.5% | 81.3% | 322 |
| REPLACE_OBV2 | $7,848 | $10,295 | 21.1% | 76.6% | 288 |
| ADD_OBV2 | $9,299 | $11,886 | 8.3% | 90.2% | 252.5 |
| REPLACE_BRIDGE100 | $7,432 | $9,480 | 27.4% | 69.7% | 299 |

### Current evaluation plan

VB 8 MNQ, ONB ADX30 risk $1,100, Bridge Monday 2, EOS risk $500. $3,000 target, $2,000 EOD trail, $1,000 daily limit, 21-session window. All full-length starts are included. The legacy truncated-tail convention is recorded separately. Period labels identify start dates; a late-2022 start can finish in 2023.

| Start period | Configuration | Starts | Pass | Blown | Timeout | Median pass days |
| --- | --- | --- | --- | --- | --- | --- |
| full | BASE | 2242 | 50.2% | 47.9% | 1.9% | 6 |
| full | EMPTY_ONB | 2242 | 38.9% | 34.6% | 26.5% | 11 |
| full | REPLACE_OBV2 | 2242 | 43.4% | 50.7% | 5.9% | 7 |
| full | ADD_OBV2 | 2242 | 49.3% | 49.0% | 1.7% | 6 |
| full | REPLACE_BRIDGE100 | 2242 | 41.3% | 56.4% | 2.2% | 6 |
| 2018_22 | BASE | 1289 | 46.7% | 50.7% | 2.6% | 7 |
| 2018_22 | EMPTY_ONB | 1289 | 29.6% | 30.6% | 39.7% | 12 |
| 2018_22 | REPLACE_OBV2 | 1289 | 37.0% | 53.5% | 9.5% | 7 |
| 2018_22 | ADD_OBV2 | 1289 | 47.1% | 50.5% | 2.4% | 7 |
| 2018_22 | REPLACE_BRIDGE100 | 1289 | 37.5% | 59.7% | 2.8% | 7 |
| 2023_plus | BASE | 953 | 55.0% | 44.1% | 0.9% | 6 |
| 2023_plus | EMPTY_ONB | 953 | 51.5% | 39.9% | 8.6% | 10 |
| 2023_plus | REPLACE_OBV2 | 953 | 52.0% | 46.9% | 1.0% | 7 |
| 2023_plus | ADD_OBV2 | 953 | 52.3% | 47.0% | 0.7% | 6 |
| 2023_plus | REPLACE_BRIDGE100 | 953 | 46.6% | 51.9% | 1.5% | 6 |

Paired pass-rate differences (95% intervals from 5,000 circular 60-start-block resamples, seed 903):

| Start period | Configuration | Reference | Difference | 95% low | 95% high |
| --- | --- | --- | --- | --- | --- |
| full | EMPTY_ONB | BASE | -11.28pp | -18.06pp | -5.00pp |
| full | REPLACE_OBV2 | BASE | -6.82pp | -11.86pp | -1.69pp |
| full | REPLACE_OBV2 | EMPTY_ONB | +4.46pp | -1.69pp | +11.06pp |
| full | ADD_OBV2 | BASE | -0.94pp | -2.63pp | +0.45pp |
| full | REPLACE_BRIDGE100 | BASE | -8.88pp | -13.83pp | -3.75pp |
| full | REPLACE_BRIDGE100 | EMPTY_ONB | +2.41pp | -4.06pp | +9.23pp |
| 2018_22 | EMPTY_ONB | BASE | -17.07pp | -26.45pp | -7.84pp |
| 2018_22 | REPLACE_OBV2 | BASE | -9.70pp | -15.75pp | -3.26pp |
| 2018_22 | REPLACE_OBV2 | EMPTY_ONB | +7.37pp | -2.48pp | +17.30pp |
| 2018_22 | ADD_OBV2 | BASE | +0.39pp | -0.23pp | +1.09pp |
| 2018_22 | REPLACE_BRIDGE100 | BASE | -9.23pp | -15.36pp | -3.10pp |
| 2018_22 | REPLACE_BRIDGE100 | EMPTY_ONB | +7.84pp | -1.48pp | +17.15pp |
| 2023_plus | EMPTY_ONB | BASE | -3.46pp | -10.91pp | +4.20pp |
| 2023_plus | REPLACE_OBV2 | BASE | -2.94pp | -10.50pp | +4.30pp |
| 2023_plus | REPLACE_OBV2 | EMPTY_ONB | +0.52pp | -5.46pp | +6.61pp |
| 2023_plus | ADD_OBV2 | BASE | -2.73pp | -6.40pp | +0.31pp |
| 2023_plus | REPLACE_BRIDGE100 | BASE | -8.39pp | -16.58pp | -0.21pp |
| 2023_plus | REPLACE_BRIDGE100 | EMPTY_ONB | -4.93pp | -12.17pp | +2.41pp |

Challenger-only higher-cost sensitivity:

| Start period | Configuration | Pass | Blown | Timeout | Median pass days |
| --- | --- | --- | --- | --- | --- |
| full | BASE | 50.2% | 47.9% | 1.9% | 6 |
| full | EMPTY_ONB | 38.9% | 34.6% | 26.5% | 11 |
| full | REPLACE_OBV2 | 42.6% | 51.6% | 5.8% | 7 |
| full | ADD_OBV2 | 49.3% | 49.0% | 1.7% | 6 |
| full | REPLACE_BRIDGE100 | 40.0% | 57.9% | 2.1% | 6 |
| 2018_22 | BASE | 46.7% | 50.7% | 2.6% | 7 |
| 2018_22 | EMPTY_ONB | 29.6% | 30.6% | 39.7% | 12 |
| 2018_22 | REPLACE_OBV2 | 36.2% | 54.4% | 9.4% | 8 |
| 2018_22 | ADD_OBV2 | 47.1% | 50.5% | 2.4% | 7 |
| 2018_22 | REPLACE_BRIDGE100 | 35.9% | 61.5% | 2.6% | 6 |
| 2023_plus | BASE | 55.0% | 44.1% | 0.9% | 6 |
| 2023_plus | EMPTY_ONB | 51.5% | 39.9% | 8.6% | 10 |
| 2023_plus | REPLACE_OBV2 | 51.2% | 47.7% | 1.0% | 7 |
| 2023_plus | ADD_OBV2 | 52.3% | 47.0% | 0.7% | 6 |
| 2023_plus | REPLACE_BRIDGE100 | 45.5% | 53.0% | 1.5% | 6 |

### Frozen decision

Funded route A needs ≥$250 year-1 gain with positive paired lower bound, year-2 no worse than −$100 and blown increase ≤1pp. Route B needs both payout means within $100, ≥2pp lower blown with negative paired upper bound, and days-to-six within +10. Replacements must beat the empty slot with positive year-1 lower bound. Evaluation needs ≥2pp pass gain, positive paired lower bound, nonnegative recent gain, blown increase ≤1pp, and improvement over the empty slot. The direction must survive higher challenger costs.

- Funded REPLACE_OBV2: FAIL. Route A failed: year1_gain_250, year1_CI_lower_positive, year2_not_100_worse, blown_not_1pp_worse; route B failed: year1_not_100_worse, year2_not_100_worse, blown_reduction_2pp, blown_CI_upper_negative, days6_not_10_slower; beats empty gate=True; stress route A/B=False/False.
- Evaluation REPLACE_OBV2: FAIL. Failed: pass_gain_2pp, paired_CI_lower_positive, recent_pass_not_worse, blown_not_1pp_worse, stress_direction.
- Funded ADD_OBV2: FAIL. Route A failed: year1_gain_250, year1_CI_lower_positive, year2_not_100_worse; route B failed: year2_not_100_worse, blown_reduction_2pp, blown_CI_upper_negative; beats empty gate=True; stress route A/B=False/False.
- Evaluation ADD_OBV2: FAIL. Failed: pass_gain_2pp, paired_CI_lower_positive, recent_pass_not_worse, blown_not_1pp_worse, stress_direction.
- Funded REPLACE_BRIDGE100: FAIL. Route A failed: year1_gain_250, year1_CI_lower_positive, year2_not_100_worse, blown_not_1pp_worse; route B failed: year1_not_100_worse, year2_not_100_worse, blown_reduction_2pp, blown_CI_upper_negative, days6_not_10_slower; beats empty gate=True; stress route A/B=False/False.
- Evaluation REPLACE_BRIDGE100: FAIL. Failed: pass_gain_2pp, paired_CI_lower_positive, recent_pass_not_worse, blown_not_1pp_worse, stress_direction.

A small observed gain is no demonstrated improvement, not proof that portfolios are equivalent. No current plan changes follow from this report.

## What could make this wrong

- Matching market data is the user's assumption. No native OB v2 MultiCharts trade-by-trade pairing or broker fill validation was performed. Target trade-through, same-minute stop priority and source-close brackets are explicitly modeled.
- 2023+ was already observed by the original filter designer. Unknown prior filter trials, platform/feed differences and the existing full-sample-fitted funded ML comparator limit causal/out-of-sample claims. No new parameters were chosen here.
- Whole-day block resampling preserves contemporaneous strategy dependence and short clusters; it cannot create unseen regimes. Paired confidence intervals are conditional on the historical sample and the model.
- Existing CL whole-Monday constant adverse paths and MOC close-only paths remain unchanged. Existing account simulators do not enforce combined position tier caps. Existing evaluation same-minute target/breach ties award the target first. These are account-model limitations, not deployment permission.
- Native MNQ commissions and execution are not established by dividing NQ costs by ten. The challenger-only higher-cost test is deliberately unfavorable to OB v2, while retaining baseline costs for paired comparability.

### Validation and trial accounting

The current tier parser counts 274 ranked items / 1226 logged variants; promotion t threshold 3.564. TRIALS.csv separately contains 274 rows; it was read, never rebuilt. Two frozen rule ledgers are this experiment's research candidates. The bridge diagnostic is not eligible for post-result selection.

Diagnostic evaluations: 6000 matched-removal draws across two families/three periods; 100 random-side and 100 random-time paths (600 period evaluations); 6 recent bootstrap/permutation series; 16 standalone MC evaluations. Account tests: five configurations × two cost conventions × two account types; duplicate BASE/EMPTY results reused, 1,000 paired funded histories per configuration, evaluation every full-length start. No best control/stress path is selected.

The finite-quantity funded acceleration enumerates every reachable daily whole-micro vector and preserves sorted-key sums and the original account state machine. `synthetic_parity.json` and `real_funded_parity.json` record exact equality for all five original simulator outputs, on synthetic fixtures and fixed real histories at 250/500-session horizons. Execution audit CSVs retain missing-bar/flat/gap flags; the cached grid was not rebuilt.

Validation: 80/80 real-history five-output comparisons and 48 synthetic comparisons match exactly; 22,020 quantity probes pass. All 6 execution branch self-checks pass. Combined historical execution-warning count is 0. A separate two-trade fixture verifies that stress fees affect both open risk and realized paths at the correct entries/exits.

## Differences between the MultiCharts code and the test

No new trading code was written. The replay uses the declared half-day overlay, common 100-session warm-up for its unfiltered diagnostic, account risk sizing instead of source fixed contracts, and the frozen execution/cost conventions. The uploaded source's chart IOG settings, bracket activation and `SetExitOnClose` behavior were not independently verified in MultiCharts. No live, VPS, broker, trading-plan or TIER_LIST files were changed.

Reproduce with the configured Python environment:

```bash
/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_replay.py --phase design
# Only after confirming design_summary.json passes the committed gate:
/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_replay.py --phase recent --authorize-recent
/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_replay.py --selfcheck
/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_accounts.py --stage synthetic-parity
/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_accounts.py --stage all --gate-passed
/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_diagnostics.py --obv2 analysis/outputs/codex_ob_v2_plan_test/replay/OBV2_design_trades.csv analysis/outputs/codex_ob_v2_plan_test/replay/OBV2_recent_trades.csv --bridge100 analysis/outputs/codex_ob_v2_plan_test/replay/BRIDGE100_design_trades.csv analysis/outputs/codex_ob_v2_plan_test/replay/BRIDGE100_recent_trades.csv --days analysis/outputs/codex_ob_v2_plan_test/replay/trading_days.csv --generate-controls --allow-return-analysis --design-gate-passed
/workspace/venvs/thebeginning/bin/python analysis/codex_ob_v2_report.py
```
