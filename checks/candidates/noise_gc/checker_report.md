# Checker report: noise_gc

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t -3.09, PSR 0.001, DSR(N=374) 0.000 |
| G2 holdout | FAIL | 2018-22 $-21.5 (t -2.68), 2023-26 $-37.6 (t -2.11) |
| G3 years | FAIL | 1/9 years positive: 2018 $-1,627, 2019 $-2,721, 2020 $-6,841, 2021 $-5,388, 2022 $-23,550, 2023 $-8,889, 2024 $-6,756, 2025 $4,209, 2026 $-51,752 |
| G4 concentration | FAIL | without the best 5% of trades: $-248,118 total ($-73.6 a trade) vs $-103,315 |
| G5 placebo | FAIL | no placebo.csv supplied (required for a strategy) |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 0.978 |
| G7 MinTRL | FAIL | 3551 trades vs MinTRL inf |
| G8 regime stability | FAIL | rho 0.19 (yearly Sharpe 2018 -0.4, 2019 -0.6, 2020 -0.7, 2021 -0.7, 2022 -3.1, 2023 -1.0, 2024 -0.6, 2025 0.3, 2026 -2.8) |
| G13 invariance | CONCERN | outcome = net / risk; P3 time (years): SIS 0.139 vs Gaussian 95% 0.112 (DIFFERS; permutation p 0.000; 9 groups, n 3551); P2 VIX regime (past-only median): SIS 0.105 vs Gaussian 95% 0.071 (DIFFERS; permutation p 0.001; 2 groups, n 3551) |

**Gates: 0/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg   annual sharpe sortino profit_factor   max_dd calmar ulcer ulcer_perf
all      3551 53% $-29 $-11,399  -1.05   -1.50          0.88 $104,115  -0.11 82.59      -0.28
longs    1827 53% $-27  $-5,385  -0.70   -1.00          0.89  $49,783  -0.11 46.56      -0.23
shorts   1724 54% $-32  $-6,014  -0.77   -1.12          0.87  $61,241  -0.10 41.69      -0.29
```
## 2023+ bootstrap
```
                       actual        p5       p50        p95
name   metric                                               
all    sharpe           -1.10     -1.97     -1.05      -0.20
       sortino          -1.56     -2.58     -1.50      -0.32
       pf_day            0.77      0.63      0.78       0.95
       calmar           -0.25     -0.25     -0.22      -0.08
       ulcer            47.52     27.83     73.79     136.48
       max_dd       65,470.88 35,491.79 72,327.80 119,423.52
       P(Sharpe<=0)       NaN       NaN      0.98        NaN
longs  sharpe           -0.59     -1.34     -0.56       0.27
       sortino          -0.84     -1.78     -0.81       0.42
       pf_day            0.84      0.66      0.84       1.08
       calmar           -0.22     -0.25     -0.17       0.16
       ulcer            21.14     11.55     33.48      69.21
       max_dd       28,810.95 16,474.97 34,415.40  61,207.74
       P(Sharpe<=0)       NaN       NaN      0.88        NaN
shorts sharpe           -0.95     -1.88     -0.95      -0.11
       sortino          -1.37     -2.35     -1.37      -0.19
       pf_day            0.71      0.52      0.72       0.96
       calmar           -0.24     -0.26     -0.22      -0.04
       ulcer            30.07     18.00     48.39      91.62
       max_dd       40,668.16 21,418.65 46,591.91  78,769.37
       P(Sharpe<=0)       NaN       NaN      0.97        NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $65,471      10% $72,080 $85,862 $92,251        100%        100%        100%
longs    $28,811      12% $35,303 $46,051 $51,811        100%        100%        100%
shorts   $40,668      14% $45,799 $55,836 $60,395        100%        100%        100%
```