# Checker report: rrp_liquidity

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t -0.01, PSR 0.497, DSR(N=374) 0.001 |
| G2 holdout | FAIL | 2018-22 $-567.3 (t -2.37), 2023-26 $576.4 (t 1.41) |
| G3 years | FAIL | 4/7 years positive: 2018 $701, 2020 $-6,162, 2021 $-33,819, 2022 $-39,014, 2023 $30,526, 2024 $17,703, 2025 $29,590 |
| G4 concentration | FAIL | without the best 5% of trades: $-139,912 total ($-540.2 a trade) vs $-474 |
| G5 placebo | FAIL | 200 placebo runs, mean $170.4; share >= real $-1.7: 0.775 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.059 |
| G7 MinTRL | FAIL | 273 trades vs MinTRL inf |
| G8 regime stability | FAIL | rho 0.40 (yearly Sharpe 2018 0.5, 2019 0.0, 2020 -0.6, 2021 -1.8, 2022 -1.5, 2023 1.5, 2024 1.0, 2025 0.8) |
| G13 invariance | CONCERN | outcome = net / risk; P3 time (years): SIS 0.344 vs Gaussian 95% 0.354 (ok; permutation p 0.040; 5 groups, n 261); P2 VIX regime (past-only median): SIS 0.307 vs Gaussian 95% 0.260 (DIFFERS; permutation p 0.017; 2 groups, n 273) |

**Gates: 1/8 pass -> FAIL**

## Standard metrics
```
       trades win   avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       273 47%   $-2    $-60  -0.00   -0.00          1.00 $81,743  -0.00 72.72      -0.00
longs     143 53%  $446  $8,115   0.41    0.97          1.41 $35,977   0.23 19.74       0.82
shorts    130 41% $-494 $-8,175  -0.69   -0.93          0.64 $67,176  -0.12 78.42      -0.21
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            0.85     -0.04      0.84      1.43
       sortino           2.05     -0.06      1.89      3.94
       pf_day            1.56      0.98      1.50      2.09
       calmar            1.14     -0.02      1.15      3.79
       ulcer             7.52      3.58      9.50     33.19
       max_dd       25,395.33 11,270.50 22,413.79 47,078.53
       P(Sharpe<=0)       NaN       NaN      0.06       NaN
longs  sharpe            1.04      0.43      1.05      1.65
       sortino           2.86      0.72      2.65      4.56
       pf_day            1.91      1.21      1.83      2.50
       calmar            2.76      0.41      2.07      4.73
       ulcer             4.10      2.60      5.56     14.48
       max_dd       12,129.33  8,313.65 14,555.75 25,999.73
       P(Sharpe<=0)       NaN       NaN      0.01       NaN
shorts sharpe           -0.45     -1.46     -0.46      0.59
       sortino          -0.59     -1.56     -0.61      1.36
       pf_day            0.69      0.27      0.70      1.74
       calmar           -0.28     -0.37     -0.21      0.74
       ulcer            17.79      4.15     20.07     57.58
       max_dd       16,821.17  6,606.75 21,613.67 48,290.49
       P(Sharpe<=0)       NaN       NaN      0.74       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $25,395      53% $24,790 $39,951 $46,200        100%        100%        100%
longs    $12,129       4% $18,637 $30,675 $36,158        100%        100%        100%
shorts   $16,821      15% $21,582 $29,366 $32,203        100%        100%        100%
```