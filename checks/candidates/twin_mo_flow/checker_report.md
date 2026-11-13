# Checker report: twin_mo_flow

kind filter, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | kept $495.5 (n 151) vs skipped $579.1 (n 178), t -0.36 |
| G2 holdout | FAIL | kept - skipped: 2018-22 $+379.8, 2023-26 $-749.0 |
| G3 years | FAIL | kept beats skipped in 5/9 years: 2018 -44, 2019 +282, 2020 +1413, 2021 +142, 2022 +471, 2023 -445, 2024 +1, 2025 -1435, 2026 -1506 |
| G5 placebo | FAIL | labels shuffled within years (2,000): p 0.6650 |
| G6 resampling | PASS | kept trades 2023+ P(Sharpe <= 0) 0.134 |
| G7 MinTRL | PASS | 151 trades vs MinTRL 38 |
| G8 regime stability | PASS | rho 0.70 (yearly Sharpe 2018 0.7, 2019 0.2, 2020 1.4, 2021 1.1, 2022 2.2, 2023 0.5, 2024 1.3, 2025 0.1, 2026 -0.4) |
| G13 invariance | CONCERN | outcome = net / trailing 50-trade sd; P2 VIX regime (past-only median): SIS 0.422 vs Gaussian 95% 0.420 (DIFFERS; permutation p 0.039; 2 groups, n 101); not evaluable: P3 time (years) |

**Gates: 3/7 pass -> FAIL**

## Standard metrics
```
            trades win  avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all trades     329 52% $541 $20,193   1.51    3.70          1.95 $12,138   1.66  4.73       8.53
kept           151 52% $495  $8,493   0.97    2.27          1.85 $11,818   0.72  2.89       5.87
kept longs      81 52% $343  $3,151   0.62    1.25          1.67  $4,899   0.64  3.24       1.94
kept shorts     70 53% $672  $5,341   0.75    1.92          2.02  $8,783   0.61  2.89       3.70
```
## 2023+ bootstrap
```
                            actual       p5       p50       p95
name        metric                                             
all trades  sharpe            1.59     0.88      1.66      2.38
            sortino           3.77     1.83      3.98      6.65
            pf_day            1.92     1.42      1.98      2.81
            calmar            1.91     0.71      2.09      4.82
            ulcer             3.42     2.14      4.26      9.79
            max_dd       12,138.00 7,022.59 11,224.75 19,546.52
            P(Sharpe<=0)       NaN      NaN      0.00       NaN
kept        sharpe            0.51    -0.37      0.55      1.32
            sortino           0.98    -0.59      1.06      3.09
            pf_day            1.33     0.82      1.35      2.16
            calmar            0.37    -0.14      0.40      1.71
            ulcer             5.49     3.15      7.44     20.82
            max_dd       11,817.50 6,069.00 11,356.75 23,295.42
            P(Sharpe<=0)       NaN      NaN      0.14       NaN
kept longs  sharpe            0.78     0.03      0.80      1.50
            sortino           1.62     0.05      1.71      4.31
            pf_day            1.88     1.03      1.93      3.88
            calmar            1.23     0.02      0.87      3.07
            ulcer             2.82     1.30      3.19      8.82
            max_dd        3,531.25 3,034.50  4,963.62 10,334.19
            P(Sharpe<=0)       NaN      NaN      0.04       NaN
kept shorts sharpe            0.01    -0.95      0.02      0.77
            sortino           0.02    -1.33      0.03      1.76
            pf_day            1.01     0.50      1.02      1.84
            calmar            0.01    -0.25      0.01      0.87
            ulcer             6.99     3.72     10.14     26.72
            max_dd        8,783.00 5,716.30 11,527.38 24,530.70
            P(Sharpe<=0)       NaN      NaN      0.49       NaN
```
## 2023+ drawdown permutation
```
            actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all trades    $12,138      67% $10,698 $17,517 $21,326        100%        100%        100%
kept          $11,818      60% $11,026 $17,461 $20,460        100%        100%        100%
kept longs     $3,531       6%  $5,452  $8,836 $10,583        100%        100%        100%
kept shorts    $8,783      16% $11,553 $17,922 $20,887        100%        100%        100%
```