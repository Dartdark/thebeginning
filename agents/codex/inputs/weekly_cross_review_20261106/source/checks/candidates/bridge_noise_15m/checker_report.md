# Checker report: bridge_noise_15m

kind strategy, pre-registered False, variants 14, N (ranked items in TRIALS.csv) 367, t_threshold(N) 3.64

| Gate | Result | Detail |
|---|---|---|
| G1 significance | PASS | t 4.88, PSR 1.000, DSR(N=367) 0.969 |
| G2 holdout | PASS | 2018-22 $36.3 (t 3.32), 2023-26 $45.1 (t 3.58) |
| G3 years | PASS | 8/9 years positive: 2018 $28,882, 2019 $-1,476, 2020 $10,984, 2021 $31,734, 2022 $32,031, 2023 $24,414, 2024 $35,315, 2025 $25,928, 2026 $29,738 |
| G4 concentration | PASS | without the best 5% of trades: $84,998 total ($16.7 a trade) vs $217,548 |
| G5 placebo | PASS | 200 placebo runs, mean $-12.9; share >= real $40.5: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.001 |
| G7 MinTRL | PASS | 5372 trades vs MinTRL 646 |
| G8 regime stability | PASS | rho 0.72 (yearly Sharpe 2018 2.5, 2019 -0.2, 2020 0.8, 2021 2.1, 2022 1.7, 2023 1.6, 2024 1.9, 2025 1.5, 2026 1.7) |
| G10 fill sanity | PASS | 100.0% of fills inside their 15-min bar (+/- 2 ticks), clock +0 min |
| G11 one-bar delay | FAIL | net $-82 (t -7.6) -> $34 (t 3.6), Sharpe kept nan% |

**Gates: 9/10 pass -> FAIL**

## Standard metrics
```
       trades win avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all      5372 63% $40 $23,784   1.54    2.85          1.16 $13,615   1.75  3.17      15.01
longs    2579 63% $63 $17,739   1.65    3.29          1.28 $12,204   1.45  2.70      13.16
shorts   2793 62% $20  $6,045   0.55    0.97          1.07 $19,722   0.31  8.19       1.48
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe            1.66      0.81      1.63      2.44
       sortino           3.10      1.38      3.05      4.88
       pf_day            1.43      1.19      1.42      1.69
       calmar            2.20      0.55      1.70      3.63
       ulcer             3.94      2.76      5.41     12.66
       max_dd       13,205.00 10,716.48 16,639.62 28,726.24
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
longs  sharpe            1.97      1.20      1.98      2.76
       sortino           4.09      2.21      4.13      6.44
       pf_day            1.81      1.43      1.82      2.33
       calmar            2.03      0.98      2.54      5.09
       ulcer             2.42      1.64      3.07      6.68
       max_dd       12,203.50  6,399.68  9,743.00 16,456.17
       P(Sharpe<=0)       NaN       NaN      0.00       NaN
shorts sharpe            0.35     -0.54      0.30      1.11
       sortino           0.61     -0.84      0.52      2.13
       pf_day            1.11      0.85      1.09      1.40
       calmar            0.24     -0.18      0.17      1.09
       ulcer            17.14      5.48     13.98     39.70
       max_dd       18,153.50 11,543.15 21,175.25 40,380.84
       P(Sharpe<=0)       NaN       NaN      0.28       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $13,205      21% $16,016 $25,063 $31,238        100%        100%        100%
longs    $12,204      83%  $9,456 $14,863 $18,159        100%        100%        100%
shorts   $18,154      37% $19,832 $30,936 $36,359        100%        100%        100%
```