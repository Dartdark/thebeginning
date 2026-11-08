# Checker report: ldf_stop50

kind strategy, pre-registered True, variants 2, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 3.30, PSR 1.000, DSR(N=374) 0.638 |
| G2 holdout | PASS | 2018-22 $84.5 (t 3.04), 2023-26 $97.9 (t 1.95) |
| G3 years | PASS | 8/9 years positive: 2018 $8,456, 2019 $-6,852, 2020 $3,350, 2021 $11,208, 2022 $25,426, 2023 $20,031, 2024 $929, 2025 $5,085, 2026 $14,374 |
| G4 concentration | FAIL | without the best 5% of trades: $-18,186 total ($-21.2 a trade) vs $82,006 |
| G5 placebo | PASS | 100 placebo runs, mean $-16.9; share >= real $90.6: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.024 |
| G7 MinTRL | PASS | 905 trades vs MinTRL 203 |
| G8 regime stability | FAIL | rho 0.49 (yearly Sharpe 2018 2.0, 2019 -2.8, 2020 0.6, 2021 1.5, 2022 2.8, 2023 3.0, 2024 0.1, 2025 0.4, 2026 1.3) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P3 time (years): SIS 0.295 vs Gaussian 95% 0.227 (DIFFERS; permutation p 0.000; 9 groups, n 855); P2 VIX regime (past-only median): SIS 0.243 vs Gaussian 95% 0.151 (DIFFERS; permutation p 0.001; 2 groups, n 855) |

**Gates: 6/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       905 55%  $91 $8,965   1.09    1.84          1.41 $11,893   0.75  5.79       3.10
longs     490 57%  $77 $4,145   0.74    1.30          1.41 $12,920   0.32  4.02       2.06
shorts    415 54% $106 $4,820   0.80    1.30          1.41  $7,312   0.66  4.31       2.24
```
## 2023+ bootstrap
```
                       actual       p5       p50       p95
name   metric                                             
all    sharpe            0.97     0.18      1.02      1.76
       sortino           1.63     0.27      1.71      3.35
       pf_day            1.35     1.06      1.37      1.73
       calmar            0.86     0.09      0.88      2.31
       ulcer             5.24     2.65      5.79     15.48
       max_dd       11,892.67 6,975.94 11,954.88 21,846.22
       P(Sharpe<=0)       NaN      NaN      0.02       NaN
longs  sharpe            0.56    -0.24      0.59      1.24
       sortino           0.98    -0.34      1.04      2.68
       pf_day            1.29     0.91      1.30      1.81
       calmar            0.32    -0.10      0.46      1.65
       ulcer             6.00     2.49      5.80     17.88
       max_dd       12,919.75 5,176.30  9,269.38 19,266.62
       P(Sharpe<=0)       NaN      NaN      0.12       NaN
shorts sharpe            0.82     0.03      0.88      1.62
       sortino           1.31     0.05      1.42      3.13
       pf_day            1.40     1.01      1.43      1.98
       calmar            0.83     0.01      0.71      2.13
       ulcer             4.20     2.11      5.05     14.36
       max_dd        7,311.50 4,751.75  9,109.58 17,789.86
       P(Sharpe<=0)       NaN      NaN      0.04       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $11,893      53% $11,734 $18,820 $22,401        100%        100%        100%
longs    $12,920      86%  $9,528 $15,346 $18,146        100%        100%        100%
shorts    $7,312      20%  $9,021 $14,444 $17,024        100%        100%        100%
```