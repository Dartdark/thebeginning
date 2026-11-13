# Checker report: noise_cl

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t -9.30, PSR 0.000, DSR(N=374) 0.000 |
| G2 holdout | FAIL | 2018-22 $-18.7 (t -5.80), 2023-26 $-30.0 (t -7.38) |
| G3 years | FAIL | 0/9 years positive: 2018 $-8,224, 2019 $-12,672, 2020 $-15,884, 2021 $-9,769, 2022 $-10,252, 2023 $-14,951, 2024 $-20,266, 2025 $-18,449, 2026 $-16,384 |
| G4 concentration | FAIL | without the best 5% of trades: $-174,298 total ($-34.1 a trade) vs $-126,853 |
| G5 placebo | FAIL | no placebo.csv supplied (required for a strategy) |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 1.000 |
| G7 MinTRL | FAIL | 5375 trades vs MinTRL inf |
| G8 regime stability | FAIL | rho 0.08 (yearly Sharpe 2018 -2.2, 2019 -3.4, 2020 -6.0, 2021 -2.3, 2022 -1.7, 2023 -2.9, 2024 -4.5, 2025 -4.9, 2026 -4.3) |
| G13 invariance | CONCERN | outcome = net / risk; P3 time (years): SIS 0.100 vs Gaussian 95% 0.090 (DIFFERS; permutation p 0.000; 9 groups, n 5375); P2 VIX regime (past-only median): SIS 0.059 vs Gaussian 95% 0.058 (DIFFERS; permutation p 0.035; 2 groups, n 5375) |

**Gates: 0/8 pass -> FAIL**

## Standard metrics
```
       trades win  avg   annual sharpe sortino profit_factor   max_dd calmar  ulcer ulcer_perf
all      5375 61% $-24 $-13,984  -3.29   -4.03          0.75 $127,760  -0.11 130.85      -0.21
longs    2620 60% $-25  $-7,114  -2.37   -2.91          0.74  $65,541  -0.11  68.90      -0.21
shorts   2755 62% $-23  $-6,869  -2.24   -2.80          0.76  $62,464  -0.11  63.34      -0.22
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe           -4.06     -4.91     -4.06     -3.26
       sortino          -4.71     -5.41     -4.71     -3.96
       pf_day            0.43      0.35      0.43      0.51
       calmar           -0.25     -0.26     -0.25     -0.25
       ulcer            78.60     64.40     81.32     98.92
       max_dd       70,763.12 57,237.32 70,520.94 84,229.33
       P(Sharpe<=0)       NaN       NaN      1.00       NaN
longs  sharpe           -2.92     -3.64     -2.88     -2.07
       sortino          -3.40     -4.03     -3.34     -2.54
       pf_day            0.42      0.33      0.43      0.55
       calmar           -0.26     -0.26     -0.25     -0.24
       ulcer            43.27     28.03     41.12     53.50
       max_dd       35,733.54 25,572.44 35,793.49 45,786.20
       P(Sharpe<=0)       NaN       NaN      1.00       NaN
shorts sharpe           -2.73     -3.71     -2.82     -1.88
       sortino          -3.27     -4.15     -3.36     -2.41
       pf_day            0.45      0.33      0.44      0.58
       calmar           -0.23     -0.26     -0.25     -0.24
       ulcer            38.81     27.40     41.41     54.85
       max_dd       37,995.37 24,787.84 36,315.56 46,472.94
       P(Sharpe<=0)       NaN       NaN      1.00       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $70,763      62% $70,536 $72,162 $73,096        100%        100%        100%
longs    $35,734      15% $36,189 $37,646 $38,534        100%        100%        100%
shorts   $37,995     100% $34,884 $36,569 $37,374        100%        100%        100%
```