# Checker report: absorption

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 2.19, PSR 0.997, DSR(N=374) 0.163 |
| G2 holdout | PASS | 2018-22 $132.7 (t 1.41), 2023-26 $371.7 (t 1.70) |
| G3 years | PASS | 8/9 years positive: 2018 $5,341, 2019 $1,511, 2020 $-9,760, 2021 $6,477, 2022 $43,919, 2023 $4,301, 2024 $18,895, 2025 $61,507, 2026 $6,356 |
| G4 concentration | FAIL | without the best 5% of trades: $-58,472 total ($-102.2 a trade) vs $138,548 |
| G5 placebo | PASS | 200 placebo runs, mean $-0.6; share >= real $229.8: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.034 |
| G7 MinTRL | PASS | 603 trades vs MinTRL 214 |
| G8 regime stability | PASS | rho 0.71 (yearly Sharpe 2018 0.7, 2019 0.2, 2020 -0.6, 2021 0.5, 2022 1.8, 2023 0.3, 2024 1.1, 2025 1.3, 2026 0.5) |
| G13 invariance | PASS | outcome = net / risk; P3 time (years): SIS 0.201 vs Gaussian 95% 0.265 (ok; permutation p 0.484; 9 groups, n 603); P2 VIX regime (past-only median): SIS 0.058 vs Gaussian 95% 0.174 (ok; permutation p 0.931; 2 groups, n 603) |

**Gates: 7/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       603 48% $230 $16,179   0.75    1.66          1.33 $21,176   0.76  9.34       3.47
longs     294 52% $255  $8,765   0.51    1.31          1.39 $13,717   0.64  8.08       2.17
shorts    309 45% $205  $7,414   0.55    1.05          1.29 $20,540   0.36 10.69       1.39
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            0.89      0.13      0.89      1.45
       sortino           2.30      0.22      2.19      5.26
       pf_day            1.45      1.04      1.43      2.06
       calmar            1.57      0.08      1.18      3.69
       ulcer             6.60      3.59      8.47     24.25
       max_dd       15,949.70 12,156.31 19,759.87 36,450.34
       P(Sharpe<=0)       NaN       NaN      0.03       NaN
longs  sharpe            0.63     -0.35      0.64      1.14
       sortino           2.09     -0.49      1.90      5.97
       pf_day            1.61      0.86      1.55      2.82
       calmar            1.26     -0.15      0.84      3.57
       ulcer             6.02      3.23      8.57     27.41
       max_dd       11,444.70  8,405.66 15,360.20 30,454.49
       P(Sharpe<=0)       NaN       NaN      0.12       NaN
shorts sharpe            0.65     -0.08      0.65      1.28
       sortino           1.26     -0.13      1.27      2.94
       pf_day            1.34      0.97      1.34      1.81
       calmar            0.76     -0.04      0.63      2.13
       ulcer             6.12      3.87      8.87     25.18
       max_dd       14,114.50  9,539.28 16,366.02 30,786.16
       P(Sharpe<=0)       NaN       NaN      0.07       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $15,950       7% $22,948 $36,264 $44,715        100%        100%        100%
longs    $11,445      12% $15,638 $24,624 $29,751        100%        100%        100%
shorts   $14,115      11% $19,359 $30,962 $37,882        100%        100%        100%
```