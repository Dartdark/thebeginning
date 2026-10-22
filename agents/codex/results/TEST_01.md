# TEST_01: REJECT adoption of Combined

Plan: `agents/codex/plans/TEST_01.md`, committed **6818838** before results. Script: `analysis/codex_test01.py`. Output: `analysis/outputs/codex_test01_output.txt`; machine-readable results: `analysis/outputs/codex_test01_details.json`; four trade CSVs alongside. Trials run: **3 filter configurations plus Base** (4 fixed configurations; no optimization).

## Rule (as tested)

Existing `candidates24.vault_break24` and `grid.execute`: NQ long on 30-minute close above the midnight open + 0.30 times prior 15-weekday ATR and above the **30-minute-bar** midnight VWAP. Decision closes 10:00 through 14:00 CT, next-minute open entry, 40-point target, 75-point stop, flat 14:30, three trades/day maximum. Early-close days retain decisions before 11:00 and flat 11:30. Combined adds decision close <=12:30 inclusive and close minus the same VWAP <=0.50 ATR. Individual filters are diagnostics, not alternative winners.

Costs: $7.25/NQ round trip plus $5 per market/stop fill; target limits need a one-point trade-through and have no exit slippage. Whole strategy **equals longs**; shorts have **0 trades**, with all trade metrics, confidence intervals and placebo comparisons N/A. All dates use the same trading-day calendar, 2018-01-02 through 2026-10-09; 2026 is partial.

## Results

The average trade rises, but the filter reduces holdout total net and does not establish an incremental edge. The removed base trades remain profitable. The positive t of the retained strategy tests whether Vault Break makes money; it does not test whether adding this filter helps.

| Period | Variant | Trades | Win | Net/NQ | Avg/NQ | t | Sharpe | Sortino | PF | Calmar | Ulcer | Daily max DD/NQ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full | Base | 1742 | 65.2% | $142,215.50 | $81.64 | 3.78 | 1.20 | 1.82 | 1.23 | 1.14 | 3.47 | $13,905.50 |
| full | Combined | 1303 | 67.4% | $132,803.25 | $101.92 | 3.95 | 1.25 | 1.90 | 1.28 | 1.09 | 3.01 | $13,550.00 |
| design | Base | 861 | 63.3% | $65,787.75 | $76.41 | 2.71 | 1.17 | 1.77 | 1.24 | 1.22 | 3.74 | $10,512.00 |
| design | Combined | 645 | 66.0% | $69,598.75 | $107.91 | 3.21 | 1.34 | 2.04 | 1.34 | 1.79 | 3.14 | $7,586.25 |
| holdout | Base | 881 | 67.1% | $76,427.75 | $86.75 | 2.66 | 1.26 | 1.91 | 1.22 | 1.42 | 5.56 | $13,905.50 |
| holdout | Combined | 658 | 68.7% | $63,204.50 | $96.06 | 2.46 | 1.19 | 1.82 | 1.23 | 1.21 | 5.32 | $13,550.00 |

Daily metrics include zero-trade days, 252 days/year; Ulcer is percent against $50,000 starting equity. PF is per trade. Maximum drawdown above is closed daily equity; trade-sequence drawdown is shown separately below.

Yearly whole/long results:

| Period | Variant | Trades | Win | Net/NQ | Avg/NQ | t | Sharpe | Sortino | PF | Calmar | Ulcer | Daily max DD/NQ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | Base | 135 | 58.5% | $3,916.25 | $29.01 | 0.49 | 0.46 | 0.65 | 1.11 | 0.50 | 4.52 | $7,711.75 |
| 2018 | Combined | 103 | 59.2% | $2,913.25 | $28.28 | 0.40 | 0.39 | 0.55 | 1.10 | 0.39 | 4.21 | $7,262.25 |
| 2019 | Base | 121 | 56.2% | $2,742.75 | $22.67 | 0.47 | 0.49 | 0.69 | 1.12 | 0.54 | 3.14 | $4,995.50 |
| 2019 | Combined | 97 | 58.8% | $5,421.75 | $55.89 | 1.02 | 0.99 | 1.50 | 1.30 | 1.06 | 2.83 | $5,001.00 |
| 2020 | Base | 201 | 63.7% | $22,087.75 | $109.89 | 1.83 | 1.91 | 3.04 | 1.34 | 2.59 | 3.78 | $8,323.00 |
| 2020 | Combined | 145 | 67.6% | $26,328.75 | $181.58 | 2.50 | 2.44 | 4.01 | 1.59 | 3.65 | 2.97 | $7,045.00 |
| 2021 | Base | 189 | 65.1% | $23,054.75 | $121.98 | 1.99 | 1.99 | 3.12 | 1.40 | 4.01 | 2.59 | $5,613.25 |
| 2021 | Combined | 143 | 71.3% | $26,968.25 | $188.59 | 2.65 | 2.41 | 3.90 | 1.65 | 4.64 | 2.42 | $5,671.50 |
| 2022 | Base | 215 | 68.4% | $13,986.25 | $65.05 | 0.96 | 0.88 | 1.30 | 1.16 | 1.39 | 6.43 | $9,815.25 |
| 2022 | Combined | 157 | 68.8% | $7,966.75 | $50.74 | 0.61 | 0.55 | 0.79 | 1.11 | 1.03 | 5.66 | $7,586.25 |
| 2023 | Base | 217 | 68.2% | $24,261.75 | $111.81 | 1.80 | 1.67 | 2.70 | 1.32 | 3.38 | 4.02 | $7,033.75 |
| 2023 | Combined | 146 | 70.5% | $21,316.50 | $146.00 | 1.87 | 1.69 | 2.62 | 1.41 | 2.53 | 4.86 | $8,257.50 |
| 2024 | Base | 214 | 65.4% | $11,843.50 | $55.34 | 0.83 | 0.77 | 1.16 | 1.13 | 0.88 | 10.27 | $13,054.25 |
| 2024 | Combined | 153 | 68.0% | $10,915.75 | $71.34 | 0.86 | 0.82 | 1.24 | 1.16 | 0.78 | 8.92 | $13,550.00 |
| 2025 | Base | 226 | 69.0% | $30,871.50 | $136.60 | 2.16 | 1.93 | 2.91 | 1.37 | 5.52 | 3.93 | $5,483.75 |
| 2025 | Combined | 178 | 69.1% | $20,849.50 | $117.13 | 1.59 | 1.43 | 2.15 | 1.29 | 2.30 | 6.39 | $8,893.75 |
| 2026 | Base | 224 | 65.6% | $9,451.00 | $42.19 | 0.61 | 0.65 | 0.96 | 1.09 | 1.11 | 8.55 | $10,756.50 |
| 2026 | Combined | 181 | 67.4% | $10,122.75 | $55.93 | 0.72 | 0.80 | 1.25 | 1.12 | 1.50 | 4.94 | $8,505.25 |

All fixed configurations (all also appear by year in the output):

| Period | Variant | Trades | Win | Net/NQ | Avg/NQ | t | Sharpe | Sortino | PF | Calmar | Ulcer | Daily max DD/NQ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full | Runway | 1391 | 66.9% | $129,590.25 | $93.16 | 3.71 | 1.19 | 1.83 | 1.25 | 1.01 | 3.28 | $14,279.50 |
| full | Stretch | 1633 | 65.6% | $141,320.75 | $86.54 | 3.89 | 1.22 | 1.83 | 1.24 | 1.17 | 3.28 | $13,462.00 |
| design | Runway | 684 | 65.5% | $65,231.00 | $95.37 | 2.90 | 1.25 | 1.90 | 1.29 | 1.40 | 3.36 | $9,085.75 |
| design | Stretch | 809 | 64.0% | $67,584.75 | $83.54 | 2.88 | 1.22 | 1.84 | 1.27 | 1.61 | 3.48 | $8,208.50 |
| holdout | Runway | 707 | 68.3% | $64,359.25 | $91.03 | 2.41 | 1.17 | 1.81 | 1.22 | 1.17 | 5.85 | $14,279.50 |
| holdout | Stretch | 824 | 67.2% | $73,736.00 | $89.49 | 2.66 | 1.25 | 1.87 | 1.23 | 1.42 | 5.68 | $13,462.00 |

### Claim-by-claim audit

| Claim | Finding |
|---|---|
| Base 1,744 / $143,396 / $82.22 / $17,204 DD / t 3.83 | Not reproduced: 1,742 / $142,215.50 / $81.64 / daily DD $13,905.50, trade DD $15,802.25 / t 3.78 at repo costs. |
| Combined 1,307 / $136,764 / $104.64 / $12,609 DD / t 4.09 | Not reproduced: 1,303 / $132,803.25 / $101.92 / daily DD $13,550.00, trade DD $14,629.00 / t 3.95. |
| $17.25 commission plus 1 tick/fill | This is $10/trade above repo commission. At that convention Base = $124,795.50, Combined = $119,773.25; claim still not reproduced. If $17.25 meant all-in market/stop costs, that is our $7.25 + two $5 slips, not $17.25 commission plus slips. |
| Design t 3.16 and holdout t 2.68 passed | Repo-cost Combined t = 3.21 / 2.46; both positive, but incremental totals vs Base = $3,811.00 / -$13,223.25. At claimed commission t = 2.91 / 2.21. Strategy significance is not filter validation. |
| Drawdown cut 26.7% | Correct arithmetic for the supplied numbers, not replicated. Our daily reduction = 2.6%; trade-sequence reduction = 7.4%. |
| 2 MNQ worst DD $1,260.90, below $2,000 | Wrong units: 2 MNQ = 0.20 NQ, so supplied $12,609 becomes $2,521.80. $1,260.90 is 1 MNQ. Our Combined at 2 MNQ: daily DD $2,710.00, trade DD $2,925.80. Historical DD is not a risk bound. |
| Chosen after testing each alone | At least three filter trials; no fresh <=3-variant economic preregistration exemption. Their actual search history and original trade list were not supplied. |
| Late entries lack runway; stretched entries climax then retest | Plausible hypotheses, not demonstrated mechanisms. Runway removes profitable holdout trades; stretch alone also lowers holdout total. No evidence here identifies a forced participant or establishes the claimed causal story. |

## Placebos and account level

### Removed trades and execution state

| Period | Filter | Removed n | Removed total | Removed avg | Removed t | New n | New total |
|---|---|---|---|---|---|---|---|
| full | Runway | 351 | $12,625.25 | $35.97 | 0.91 | 0 | $0.00 |
| full | Stretch | 191 | $12,335.25 | $64.58 | 1.00 | 82 | $11,440.50 |
| full | Combined | 482 | $20,780.50 | $43.11 | 1.17 | 43 | $11,368.25 |
| design | Runway | 177 | $556.75 | $3.15 | 0.06 | 0 | $0.00 |
| design | Stretch | 96 | $4,934.00 | $51.40 | 0.61 | 44 | $6,731.00 |
| design | Combined | 241 | $1,902.75 | $7.90 | 0.16 | 25 | $5,713.75 |
| holdout | Runway | 174 | $12,068.50 | $69.36 | 1.13 | 0 | $0.00 |
| holdout | Stretch | 95 | $7,401.25 | $77.91 | 0.79 | 38 | $4,709.50 |
| holdout | Combined | 241 | $18,877.75 | $78.33 | 1.41 | 18 | $5,654.50 |

The filtered execution list is not a simple subset. For Combined, skipping an earlier position can free a later entry or a daily trade slot. We reran signals through the repo executor; removed and newly enabled trades reconcile exactly to the total difference. A matched-count random deletion is therefore a thinning benchmark, supplemented by signal deletion with execution replay.

| Period | Filter beats random profit | Beats random daily DD | Beats both |
|---|---|---|---|
| full | 93.9% | 52.1% | 50.5% |
| design | 96.7% | 90.6% | 88.4% |
| holdout | 69.0% | 50.1% | 41.0% |

5,000 fixed-count deletions per configuration/period, preserving calendar order. Holdout Combined random-profit p = 0.310; 95% superiority is not met. The paired ten-day-block bootstrap of Combined minus Base gives holdout total delta -$13,223.25, 90% interval -$33,366.57 to $6,481.31, daily t -0.99. Bootstrap share delta <=0: 86.7%; this is a resampling frequency, not a posterior probability.

State-aware holdout placebo: 1,000 uniform candidate-signal deletions, same signal count as Combined, then `grid.execute`; beats 69.7% on profit, 65.1% on DD, 50.8% jointly. Executed counts vary: 5/50/95% = [724.0, 739.0, 754.0].

| Holdout control (1,000 runs) | Total net p5 / median / p95 | p(control >= Combined) |
|---|---|---|
| random_time_long | $43,693.97 / $68,955.75 / $94,946.89 | 0.630 |
| random_side_same_time | -$70,162.26 / -$29,812.00 / $8,021.35 | 0.001 |

Random-time longs retain Combined's realised days/counts and randomize 30-minute decisions from 10:00 through 14:00 (through 11:00 on early-close days), with identical brackets/holiday flats. The early-day control thus permits one decision later than Base's 11:00 cutoff. Random-side control retains actual times. The executor can skip overlapping control signals. These assess the retained strategy, not its incremental filter effect.

### Uncertainty and trailing drawdown

| Holdout variant | Metric | Actual | Bootstrap p5 | Bootstrap p95 |
|---|---|---|---|---|
| Base | sharpe | 1.260 | 0.477 | 2.111 |
| Base | sortino | 1.909 | 0.684 | 3.402 |
| Base | pf_day | 1.353 | 1.121 | 1.665 |
| Base | calmar | 1.423 | 0.299 | 2.945 |
| Base | ulcer | 5.564 | 3.163 | 16.419 |
| Base | max_dd | 13,905.500 | 10,040.250 | 29,093.013 |
| Base | annual | 19,794.237 | 7,459.695 | 32,890.989 |
| Combined | sharpe | 1.188 | 0.387 | 2.032 |
| Combined | sortino | 1.815 | 0.552 | 3.332 |
| Combined | pf_day | 1.337 | 1.098 | 1.652 |
| Combined | calmar | 1.208 | 0.226 | 2.731 |
| Combined | ulcer | 5.320 | 3.120 | 16.380 |
| Combined | max_dd | 13,550.000 | 9,251.938 | 26,921.525 |
| Combined | annual | 16,369.511 | 5,261.452 | 28,040.640 |

5,000 moving ten-day block resamples. Bootstrap PF is per day, unlike trade PF in the main table. Full-period intervals, daily-order permutations, shuffled DD percentiles, and 10,000 trade resamples are printed in the output. Whole/long resampling is identical; shorts N/A.

| Period | Variant | Size | One-year P(EOD trail hit) | P(losing year) | One-year DD p95 |
|---|---|---|---|---|---|
| full | Base | 2 MNQ | 24.5% | 10.0% | $3,464.15 |
| full | Base | 8 MNQ | 68.9% | 10.0% | $13,856.59 |
| full | Combined | 2 MNQ | 19.0% | 9.4% | $3,048.44 |
| full | Combined | 8 MNQ | 65.4% | 9.4% | $12,193.76 |
| holdout | Base | 2 MNQ | 32.6% | 8.9% | $4,075.28 |
| holdout | Base | 8 MNQ | 69.9% | 8.9% | $16,301.13 |
| holdout | Combined | 2 MNQ | 29.2% | 10.6% | $3,691.53 |
| holdout | Combined | 8 MNQ | 69.4% | 10.6% | $14,766.12 |

These standalone constant-size Monte Carlos use the existing $2,000 trail locking at start +$100, 252 days/year and 5,000 ten-day-block paths. EOD-only breach checks omit intraday floor breaches, daily loss limits, other strategies and cushion sizing; the 8-MNQ stress is not a full evaluation pass-rate estimate.

### Funded plan: additions, replacement, empty-slot control

Existing Lab/Boot simulator, 1,000 paired 20-day-block histories, 500 trading days, full size from $1,500 cushion. Current plan includes report-derived VB with 2/1 MNQ single-print sizing, ONB ML, Monday, EOS, LDF, NFP, Bridge Monday, 2 MCL CL fade, 2 MES ES MOC, and 1 MNQ Relative Strength longs. Base/Combined replacements keep the same 2/1 sizing; addition is Combined 1 MNQ. Empty VB retains all other slots.

Source history from 2018-01-01:

| Plan | Mean payouts 1y | Mean payouts 2y | 2y history p5 / p95 | Blown | Median days to 6 | Delta 2y vs rebuilt Base |
|---|---|---|---|---|---|---|
| current_MC | $9,429.50 | $12,062.50 | $0.00 to $13,000.00 | 7.0% | 257.0 | $181.00 |
| empty_VB | $8,142.50 | $12,132.00 | $1,500.00 to $13,000.00 | 5.1% | 297.0 | $250.50 |
| rebuilt_Base | $9,162.50 | $11,881.50 | $0.00 to $13,000.00 | 8.4% | 263.5 | $0.00 |
| replace_Combined | $9,015.50 | $11,856.50 | $0.00 to $13,000.00 | 8.4% | 265.0 | -$25.00 |
| add_Combined_1MNQ | $9,242.50 | $11,766.00 | $0.00 to $13,000.00 | 9.2% | 253.0 | -$115.50 |

Source history from 2023-01-01:

| Plan | Mean payouts 1y | Mean payouts 2y | 2y history p5 / p95 | Blown | Median days to 6 | Delta 2y vs rebuilt Base |
|---|---|---|---|---|---|---|
| current_MC | $10,730.50 | $12,171.50 | $0.00 to $13,000.00 | 6.9% | 213.5 | $195.50 |
| empty_VB | $9,718.50 | $12,339.50 | $5,000.00 to $13,000.00 | 5.0% | 254.0 | $363.50 |
| rebuilt_Base | $10,482.00 | $11,976.00 | $0.00 to $13,000.00 | 8.1% | 219.0 | $0.00 |
| replace_Combined | $10,084.00 | $11,790.50 | $0.00 to $13,000.00 | 9.8% | 229.0 | -$185.50 |
| add_Combined_1MNQ | $10,186.00 | $11,701.50 | $0.00 to $13,000.00 | 10.2% | 220.0 | -$274.50 |

Paired mean simulation-error intervals and history-level delta bands vs current_MC are in the JSON/output. They quantify simulation variability conditional on this history; they do not establish independent future-market confidence. Compare replace_Combined with rebuilt_Base to isolate filtering from Python-versus-MultiCharts differences. Compare both with empty_VB to identify benefits merely from less exposure.

## What could make this wrong

- The supplied claim has no trade list or exact dataset/version. The current VB report on common dates contains 1,743 trades, net $159,813.25; 1,700 exact day/entry-minute/side keys match the 1,742-trade rebuild, and 99.4% of these match gross P&L within $5. Report parity details are in the output. We cannot identify the claimant's exact discrepancy from headline numbers alone.

- Signals use information available at the decision close; ATR is shifted to prior completed weekdays. Entry-bar stops/targets are active. The repository approximates intraminute order using OHLC; gaps, target trade-through and missing minute bars can affect fills. No tick data or MultiCharts compile was run here.

- The 30-minute midnight bar can include minutes of the previous date; the Grid24 ATR uses one-minute calendar-date extremes, whereas the live source accumulates chart bars. Existing rebuild/report differences must be reconciled before any implementation. Continuous futures are not back-adjusted; roll jumps can affect ATR.

- Claimed holdout results were already visible before this audit. Combined is a fixed external selection, not untouched original discovery. The current trial log plus our three configurations has 276 items; the repo one-sided multiple-testing t bar is 3.57. The incremental holdout t is negative. A retained-strategy DSR cannot rescue the filter.

- Funded paths inherit the repo's conservative CL daily worst-loss proxy spread across the day, per-micro scaled costs and signal-level netting approximations. ES MOC and RS use the current repo rebuild rules; RS entry-bar exit delay is inherited from that separate strategy. Paired blocks preserve cross-strategy correlations within blocks but not long market regimes. No live accounts or settings were touched.

## Differences between MultiCharts code and the test

No Combined PowerLanguage code was written. The existing base is rebuilt with the established repo tools, with differences and report parity disclosed above. There is no basis here to change the live strategy. Keep Base; any new filter thresholds or altered time boundaries require a new registered trial and new forward evidence.
