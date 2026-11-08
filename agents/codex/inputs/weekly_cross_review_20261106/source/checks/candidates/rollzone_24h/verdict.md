# RollZone 24h NQ Long: verdict (Claude, 2026-10-31): C, not for any Apex plan; capital-expansion bench (personal)

Rule and conventions: `spec.md`. Outputs:
- `analysis/outputs/rollzone_24h_test_output.txt`: metrics, holdout, Monte Carlo, placebo.
- `analysis/outputs/rollzone_bench_evals.txt`, `rollzone_bench_funded.txt`, `rollzone_bench_personal.txt`: the benches.

## Standalone (per 1 NQ, after $7.25 + 1 tick per stop / market fill, 2018-01 to 2026-10, long only, so longs = whole)

| Version | Trades | Avg | PF | Sharpe | Sortino | Calmar | Ulcer | Max DD | daily t whole / 2018-22 / 2023+ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| NQCAP (note's run, $150 budget per MNQ) | 2,834 | $79 | 1.13 | 0.82 | 1.62 | 0.42 | 17.0 | $58.9k | 2.46 / **0.50** / 2.82 |
| ATR (plain 0.8 x range stop) | 3,319 | $123 | 1.17 | 0.97 | 1.43 | 0.72 | 8.9 | $62.6k | 2.92 / 1.75 / 2.34 |

Per year, NQCAP net: 2018 -$17k, 2019 +$41k, 2020 +$26k, 2021 +$21k, **2022 -$41k**, 2023 +$35k, 2024 +$111k,
2025 +$66k, **2026 -$19k**. Day entries carry it (NQCAP $145 a trade, PF 1.26); night entries earn $49 (PF 1.08).

- **2023+ holdout, bootstrap (NQCAP):** Sharpe 1.43 (p5 0.64), P(Sharpe <= 0) 0.00; the drawdown sits at the 60th
  percentile of the permutations.
- **Placebo (random entry bar, same windows, budget and exits, 20 seeds):**
  - NQCAP beats 95% of the runs overall, but **2018-22 is below placebo** ($18 vs $37 a trade). All of its edge is
    since 2023 ($168 vs $55).
  - ATR beats 100% ($123 vs $41; 2018-22 $75 vs $18).
- **Monte Carlo, 1 MNQ:** one-year chance of an EOD $2,000 trailing hit is **48% (NQCAP) / 55% (ATR)** on its own.
- **Multiple testing:** the bar is t 3.63 (N_items 356); the best is 2.92, so it can't go above C. The note also chose its
  01:00-07:00 entry block after seeing the 2023+ trades.
- **Parity:** trade counts match the note, but gross P&L per year doesn't (2022 -$36k here vs +$13k). The author's MC
  trade list is needed to settle it.

## Apex benches (MNQ = NQ / 10; worst point of the day placed at its start)

**Evaluation pass rate (every start day):**
- 50K: 50.0% without RollZone, 44.1% with 1 MNQ, 38.8% with 2.
- 150K: 41.0% without, 36.7% with 2 MNQ.

**50K funded (500 paired 2-year histories):**

| Plan | 2-year payouts vs plan | Blown |
|---|---:|---|
| Plan | - | 6.8% |
| + RZ 1 MNQ | -$401 | 10.4% |
| + RZ 2 MNQ | -$5,331 | 49.6% |
| + RZA 1 MNQ | -$1,661 | 20.2% |
| OT -> RZ 1 | -$369 | 9.8% (OT slot empty: +$22, 6.6%) |
| VB 2/1 -> 1/1 + RZ 1 | -$200 | 7.0% (empty: +$262, 4.0%) |

**150K funded:**

| Plan | 2-year payouts vs plan | Blown |
|---|---:|---|
| Plan | - | 3.0% |
| + RZ 1 MNQ | -$181 | 3.8% |
| + RZ 2 MNQ | -$1,523 | 10.6% |
| + RZ 3 MNQ | -$3,197 | 19.0% |
| OT 2 -> RZ 2 | -$1,647 | 11.4% (OT slot empty: +$81, 2.4%) |
| DT 2 -> RZ 2 | -$1,539 | 10.4% |

Every addition and every replacement is worse than the plan and worse than the slot left empty.

## Personal portfolio (17 pieces at 1 micro)

| Version | Per year alone | Correlation with the book | Return/DD when added | Capital needed |
|---|---:|---:|---|---|
| RZ | +$2.6k | +0.32 | 9.0 -> 8.7 | +$5.1k |
| RZA | +$4.9k | +0.44 | 9.0 -> 7.5 | +$12.5k |

In place of Overnight Tick or Dual Thrust, both versions are worse. They add money only by needing more capital, so per the
CLAUDE.md rule they go on the capital-expansion bench, not into the plan.

## Not done
- **Checker:** the strategy-checker agent wasn't run. It's only required before a promotion above C.
- **MultiCharts parity:** needs the author's trade list.
