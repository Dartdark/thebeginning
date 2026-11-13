# Checker report: letf_flow

kind strategy, pre-registered True, variants 1, N (ranked items in TRIALS.csv) 374, t_threshold(N) 3.65

| Gate | Result | Detail |
|---|---|---|
| G1 significance | FAIL | t -3.58, PSR 0.000, DSR(N=374) 0.000 |
| G2 holdout | FAIL | 2018-22 $-41.6 (t -0.84), 2023-26 $-261.7 (t -4.30) |
| G3 years | FAIL | 3/9 years positive: 2018 $-3,127, 2019 $1,473, 2020 $4,906, 2021 $-6,771, 2022 $-10,494, 2023 $-13,080, 2024 $3,557, 2025 $-36,581, 2026 $-24,042 |
| G4 concentration | FAIL | without the best 5% of trades: $-156,154 total ($-272.0 a trade) vs $-84,159 |
| G5 placebo | FAIL | 200 placebo runs, mean $-1.9; share >= real $-139.1: 1.000 |
| G6 resampling | FAIL | 2023+ P(Sharpe <= 0) 1.000 |
| G7 MinTRL | FAIL | 605 trades vs MinTRL inf |
| G8 regime stability | FAIL | rho 0.25 (yearly Sharpe 2018 -0.9, 2019 0.6, 2020 0.4, 2021 -0.9, 2022 -1.3, 2023 -2.3, 2024 0.5, 2025 -3.4, 2026 -2.9) |
| G13 invariance | CONCERN | outcome = net / risk; P3 time (years): SIS 0.291 vs Gaussian 95% 0.260 (DIFFERS; permutation p 0.005; 9 groups, n 605); P2 VIX regime (past-only median): SIS 0.230 vs Gaussian 95% 0.172 (DIFFERS; permutation p 0.004; 2 groups, n 605) |

**Gates: 0/8 pass -> FAIL**

## Standard metrics
```
       trades win   avg  annual sharpe sortino profit_factor  max_dd calmar ulcer ulcer_perf
all       605 41% $-139 $-9,241  -1.18   -1.57          0.65 $90,546  -0.10 59.44      -0.31
longs     277 42% $-179 $-5,444  -0.90   -1.17          0.63 $52,937  -0.10 43.83      -0.25
shorts    328 40% $-105 $-3,797  -0.76   -1.06          0.69 $45,496  -0.08 26.53      -0.29
```
## 2023+ bootstrap
```
                       actual        p5       p50       p95
name   metric                                              
all    sharpe           -2.12     -2.82     -2.07     -1.29
       sortino          -2.51     -3.16     -2.46     -1.65
       pf_day            0.48      0.38      0.49      0.64
       calmar           -0.25     -0.25     -0.25     -0.22
       ulcer            64.71     46.52     79.05    114.90
       max_dd       70,146.00 45,465.08 70,166.46 98,196.63
       P(Sharpe<=0)       NaN       NaN      1.00       NaN
longs  sharpe           -1.21     -1.93     -1.15     -0.37
       sortino          -1.46     -2.15     -1.40     -0.50
       pf_day            0.52      0.34      0.53      0.81
       calmar           -0.25     -0.25     -0.23     -0.14
       ulcer            26.69     14.65     35.03     62.98
       max_dd       31,315.17 15,442.05 31,957.71 53,295.44
       P(Sharpe<=0)       NaN       NaN      0.99       NaN
shorts sharpe           -1.85     -2.64     -1.83     -0.99
       sortino          -2.14     -2.86     -2.12     -1.27
       pf_day            0.45      0.31      0.46      0.66
       calmar           -0.25     -0.25     -0.25     -0.21
       ulcer            38.60     24.37     45.34     70.16
       max_dd       39,584.75 23,078.17 40,647.42 59,302.08
       P(Sharpe<=0)       NaN       NaN      1.00       NaN
```
## 2023+ drawdown permutation
```
       actual_dd pct_rank    dd50    dd95    dd99 P(dd>=1000) P(dd>=2000) P(dd>=3000)
all      $70,146       0% $72,117 $77,387 $80,039        100%        100%        100%
longs    $31,315      15% $33,568 $39,289 $42,602        100%        100%        100%
shorts   $39,585      22% $40,475 $43,841 $45,644        100%        100%        100%
```