# Checker report: eos_late

kind strategy, pre-registered False, variants 2, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 2.72, PSR 0.999, DSR(N=374) 0.383 |
| G2 holdout | PASS | 2018-22 $825.6 (t 2.78), 2023-26 $737.8 (t 1.35) |
| G3 years | PASS | 9/9 years positive: 2018 $4,411, 2019 $1,271, 2020 $19,803, 2021 $5,942, 2022 $18,108, 2023 $7,416, 2024 $9,935, 2025 $7,539, 2026 $9,047 |
| G4 concentration | PASS | without the best 5% of trades: $31,276 total ($312.8 a trade) vs $83,473 |
| G5 placebo | PASS | 500 placebo runs, mean $-21.6; share >= real $787.5: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.160 |
| G7 MinTRL | PASS | 106 trades vs MinTRL 30 |
| G8 regime stability | PASS | rho 0.85 (yearly Sharpe 2018 0.8, 2019 0.4, 2020 1.9, 2021 0.8, 2022 1.4, 2023 0.9, 2024 1.0, 2025 0.6, 2026 0.6) |
| G13 invariance | PASS | outcome = net / trailing 50-trade sd; P2 VIX regime (past-only median): SIS 0.299 vs Gaussian 95% 0.550 (ok; permutation p 0.423; 2 groups, n 56); not evaluable: P3 time (years) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       106 55% $787 $9,222   0.88    2.18          2.10 $14,010   0.66  2.89       6.39
shorts    106 55% $787 $9,222   0.88    2.18          2.10 $14,010   0.66  2.89       6.39
```
## 2023+ bootstrap
```
                       actual       p5       p50       p95
name   metric                                             
all    sharpe            0.67    -0.39      0.51      1.22
       sortino           1.60    -0.61      1.06      3.35
       pf_day            1.72     0.75      1.48      2.72
       calmar            0.62    -0.14      0.41      1.84
       ulcer             6.34     3.35      8.74     27.33
       max_dd       14,009.65 6,949.66 13,819.43 28,753.83
       P(Sharpe<=0)       NaN      NaN      0.16       NaN
shorts sharpe            0.67    -0.39      0.51      1.22
       sortino           1.60    -0.61      1.06      3.35
       pf_day            1.72     0.75      1.48      2.72
       calmar            0.62    -0.14      0.41      1.84
       ulcer             6.34     3.35      8.74     27.33
       max_dd       14,009.65 6,949.66 13,819.43 28,753.83
       P(Sharpe<=0)       NaN      NaN      0.16       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $14,010      62% $12,643 $20,212 $24,425        100%        100%        100%
shorts   $14,010      62% $12,643 $20,212 $24,425        100%        100%        100%
```