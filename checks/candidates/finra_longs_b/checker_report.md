# Checker report: finra_longs_b

kind strategy, pre-registered False, variants 4, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t 1.85, PSR 0.973, DSR(N=374) 0.121 |
| G2 holdout | PASS | 2018-22 $117.6 (t 1.09), 2023-26 $286.9 (t 1.50) |
| G3 years | PASS | 6/9 years positive: 2018 $-4,586, 2019 $14,002, 2020 $7,116, 2021 $16,537, 2022 $-8,128, 2023 $15,949, 2024 $-10,045, 2025 $11,422, 2026 $29,156 |
| G4 concentration | FAIL | without the best 5% of trades: $-28,624 total ($-80.6 a trade) vs $71,423 |
| G5 placebo | PASS | 500 placebo runs, mean $16.2; share >= real $191.0: 0.026 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.022 |
| G7 MinTRL | PASS | 374 trades vs MinTRL 271 |
| G8 regime stability | FAIL | rho 0.40 (yearly Sharpe 2018 -3.1, 2019 2.1, 2020 0.7, 2021 1.4, 2022 -0.5, 2023 1.5, 2024 -0.7, 2025 0.9, 2026 1.5) |
| G13 invariance | PASS | outcome = net / risk; P3 time (years): SIS 0.277 vs Gaussian 95% 0.326 (ok; permutation p 0.137; 8 groups, n 357); P2 VIX regime (past-only median): SIS 0.143 vs Gaussian 95% 0.221 (ok; permutation p 0.231; 2 groups, n 374) |

**Gates: 5/8 pass -> FAIL**

## Standard metrics
```
      trades win  avg annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      374 48% $191 $8,708   0.64    1.16          1.28 $17,444   0.50  6.20       2.81
longs    374 48% $191 $8,708   0.64    1.16          1.28 $17,444   0.50  6.20       2.81
```
## 2023+ bootstrap
```
                      actual       p5       p50       p95
name  metric                                             
all   sharpe            0.76     0.15      0.79      1.39
      sortino           1.43     0.25      1.50      2.85
      pf_day            1.35     1.06      1.37      1.72
      calmar            0.69     0.10      0.87      2.30
      ulcer             9.28     3.68      7.35     17.44
      max_dd       17,444.33 9,132.08 14,285.38 24,704.58
      P(Sharpe<=0)       NaN      NaN      0.02       NaN
longs sharpe            0.76     0.15      0.79      1.39
      sortino           1.43     0.25      1.50      2.85
      pf_day            1.35     1.06      1.37      1.72
      calmar            0.69     0.10      0.87      2.30
      ulcer             9.28     3.68      7.35     17.44
      max_dd       17,444.33 9,132.08 14,285.38 24,704.58
      P(Sharpe<=0)       NaN      NaN      0.02       NaN
```
## 2023+ drawdown permutation
```
      actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all     $17,444      39% $18,807 $29,708 $35,728        100%        100%        100%
longs   $17,444      39% $18,807 $29,708 $35,728        100%        100%        100%
```