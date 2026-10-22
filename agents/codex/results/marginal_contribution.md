# funded-plan marginal contribution: WATCH
Summary: Remove each current strategy in paired funded-account histories to measure its payout and trailing-risk value.
No removal passed the design gate; keep the current roster, including ES MOC 2 MES.
Vault Break costs 3.1/1.2 blowup points but speeds six payouts by 47/31 days in design/holdout, so removal is too blunt.
Proceed to the preregistered next step: reduce Vault Break only on specified ONB/RS overlap days; if that fails, build new strategies.
Plans: `agents/codex/plans/marginal_{core,calendar,other}.md`, commit `f0629aa`   Script: `analysis/codex_marginal_contribution.py`   Output: `analysis/outputs/codex_marginal_contribution/`   Trials run: 13 registered slots / 11 unique configurations

## Rule (as tested)

The exact current 50K benchmark is confirmed as:

- Vault Break 2 MNQ normally / 1 MNQ after a single-print session;
- Overnight Bias ML v2 at $400 risk;
- Monday Long 1 MNQ;
- Expiration Open Short at $700 risk;
- Late-Day Flow 2 MNQ;
- NFP Fade at $500 risk;
- Bridge Monday Long 1 MNQ;
- CL Sunday Gap Fade 2 MCL;
- ES MOC Follow **active at 2 MES**;
- Relative Strength longs only 1 MNQ, subject to ordinary cushion scaling and integer rounding;
- full size from a $1,500 cushion and the existing Apex payout and trailing-drawdown rules.

Each test removes exactly one strategy and leaves its slot empty. Signals, exits, fills, costs, other sizes and account
rules do not change. Vault Break removal drops both its normal and single-print quantities.

To honor the five-variant limit, the work was preregistered in three batches: current plus four core removals, current
plus four scheduled removals, and current plus the two non-NQ removals. The shared baseline was simulated once, giving
11 unique configurations. Design used 2018-22; the script fixed eligibility before opening 2023+. Each period used 2,000
paired circular 20-trading-day block histories.

A removal needed all of the following on design: no lower two-year paid value, no higher blowups, no more than five days
slower to six payouts, plus either at least $250 more paid value or at least one percentage point fewer blowups. It then
had to be no worse on all three holdout measures. Passing would only nominate a later sizing study, not authorize a live
change.

## Results

### Exact current baseline

Using all available dates, the current roster produced mean year-one paid value **$9,532**, mean two-year paid value
**$12,099**, **6.7%** blowups, **91.6%** reaching all six payouts and median **242 trading days** to payout six. This is
the baseline for future optimization work; bootstrap sampling causes small differences from older runs with other seeds.

No removal passed the design gate. In the table, paid value is how much the strategy adds versus its empty slot; blowup
cost is the increase in blowup probability caused by retaining it; days faster is how much it shortens median time to
six payouts. Negative paid value means the empty slot paid slightly more.

| Strategy at current size | Design paid value | Design blowup cost | Design days faster | Holdout paid value | Holdout blowup cost | Holdout days faster | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| Vault Break | -$92 | +3.1 pp | 47 | -$75 | +1.2 pp | 31 | WATCH: size tradeoff |
| Overnight Bias ML v2 | +$1,051 | -0.4 pp | 69 | +$419 | -3.1 pp | 25 | KEEP |
| Monday Long | -$120 | +0.7 pp | 4 | -$8 | +0.1 pp | 4 | WATCH: small effect |
| Expiration Open Short | +$169 | +0.3 pp | 35 | -$150 | +1.6 pp | 26 | WATCH: period conflict |
| Late-Day Flow | +$279 | -1.8 pp | 17 | +$77 | -0.5 pp | 17 | KEEP |
| NFP Fade | -$38 | +0.3 pp | 6 | +$138 | -1.0 pp | 5 | WATCH: period conflict |
| Bridge Monday Long | +$91 | -0.4 pp | 14 | +$42 | -0.3 pp | 4 | KEEP |
| CL Sunday Gap Fade | +$231 | -1.2 pp | 13 | -$2 | +0.2 pp | 17 | WATCH: period conflict |
| ES MOC Follow | +$444 | -2.9 pp | 15 | +$177 | -1.3 pp | 3 | KEEP |
| Relative Strength longs | -$36 | +0.7 pp | 18 | -$60 | +0.5 pp | 15 | WATCH: size tradeoff |

ES MOC's result settles the repository-status question. It is active and has positive account value in both periods.
Removing it reduced design/holdout paid value by $444/$177, raised blowups by 2.9/1.3 points and slowed six payouts by
15/3 days. Combined with the prior 0/1/2-MES study, keep it at 2 MES.

The detailed account paths were:

| Period | Configuration | Year 1 paid | Year 2 paid | Blowup | All six | Days to six | Change in year 2 |
|---|---|---:|---:|---:|---:|---:|---:|
| Design | Current | $8,338 | $11,832 | 8.2% | 88.2% | 274 | $0 |
| Design | Without VB | $6,919 | $11,924 | 5.1% | 86.0% | 321 | +$92 |
| Design | Without ONB | $5,707 | $10,781 | 8.5% | 69.3% | 343 | -$1,051 |
| Design | Without Monday | $8,435 | $11,952 | 7.5% | 89.6% | 278 | +$120 |
| Design | Without EOS | $7,150 | $11,663 | 7.9% | 83.7% | 309 | -$169 |
| Design | Without LDF | $7,653 | $11,554 | 10.0% | 84.9% | 291 | -$279 |
| Design | Without NFP | $8,197 | $11,870 | 7.8% | 88.3% | 280 | +$38 |
| Design | Without Bridge Monday | $7,914 | $11,742 | 8.6% | 86.7% | 288 | -$91 |
| Design | Without CL Sunday | $7,701 | $11,601 | 9.4% | 85.0% | 287 | -$231 |
| Design | Without ES MOC | $7,626 | $11,388 | 11.1% | 83.5% | 289 | -$444 |
| Design | Without RS longs | $7,776 | $11,868 | 7.5% | 87.4% | 292 | +$36 |
| Holdout | Current | $10,560 | $12,026 | 7.9% | 92.0% | 213 | $0 |
| Holdout | Without VB | $9,490 | $12,101 | 6.8% | 91.8% | 244 | +$75 |
| Holdout | Without ONB | $9,226 | $11,607 | 11.1% | 87.8% | 238 | -$419 |
| Holdout | Without Monday | $10,375 | $12,034 | 7.8% | 91.9% | 216 | +$8 |
| Holdout | Without EOS | $9,778 | $12,176 | 6.3% | 92.5% | 239 | +$150 |
| Holdout | Without LDF | $9,831 | $11,948 | 8.3% | 90.9% | 230 | -$77 |
| Holdout | Without NFP | $10,188 | $11,888 | 8.9% | 90.6% | 218 | -$138 |
| Holdout | Without Bridge Monday | $10,420 | $11,984 | 8.2% | 91.5% | 217 | -$42 |
| Holdout | Without CL Sunday | $9,939 | $12,028 | 7.8% | 91.8% | 230 | +$2 |
| Holdout | Without ES MOC | $10,247 | $11,849 | 9.2% | 90.6% | 216 | -$177 |
| Holdout | Without RS longs | $10,156 | $12,085 | 7.4% | 92.1% | 228 | +$60 |

The paired payout-difference intervals are discrete because payouts occur in fixed amounts. None of the apparent
improvements separated from zero: for example, without Vault Break the 5th-95th percentile difference was
-$3,000 to +$3,000 in design and $0 to $0 in holdout; the latter has rare tail differences despite identical quantiles.

### Standalone contribution at current plan size

These are net full-size strategy results before the funded payout transform. `Days` means nonzero strategy days and
`Avg/day` is the current-size daily contribution; this is preferable to dollars per NQ for risk-sized and mixed-market
lines.

| Strategy | Period | Days | Win | Avg/day | t | Total | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Vault Break | Design | 527 | 60.3% | $25 | 3.06 | $12,984 | 1.35 | 2.10 | 1.44 | 1.86 | 0.81 | $1,367 |
| Vault Break | Holdout | 415 | 63.4% | $43 | 3.27 | $18,049 | 1.65 | 2.62 | 1.51 | 2.00 | 1.23 | $2,342 |
| ONB ML v2 | Design | 192 | 55.2% | $125 | 3.93 | $23,913 | 1.68 | 4.00 | 2.11 | 1.93 | 1.72 | $2,417 |
| ONB ML v2 | Holdout | 142 | 57.7% | $112 | 3.61 | $15,837 | 1.77 | 3.89 | 2.11 | 2.34 | 0.88 | $1,753 |
| Monday Long | Design | 256 | 52.0% | $15 | 1.18 | $3,924 | 0.52 | 0.83 | 1.21 | 0.37 | 1.73 | $2,078 |
| Monday Long | Holdout | 194 | 59.3% | $78 | 3.30 | $15,212 | 1.64 | 3.13 | 1.92 | 2.50 | 0.80 | $1,575 |
| EOS | Design | 60 | 58.3% | $193 | 2.36 | $11,598 | 1.01 | 2.09 | 2.07 | 1.66 | 1.01 | $1,362 |
| EOS | Holdout | 45 | 60.0% | $228 | 2.29 | $10,281 | 1.12 | 2.56 | 2.39 | 2.51 | 0.79 | $1,063 |
| Late-Day Flow | Design | 492 | 54.1% | $15 | 2.69 | $7,453 | 1.18 | 1.99 | 1.43 | 0.48 | 2.15 | $3,028 |
| Late-Day Flow | Holdout | 403 | 57.1% | $24 | 2.40 | $9,486 | 1.22 | 2.20 | 1.45 | 1.17 | 1.29 | $2,097 |
| NFP Fade | Design | 43 | 46.5% | $20 | 0.52 | $863 | 0.23 | 0.39 | 1.22 | 0.08 | 2.11 | $2,034 |
| NFP Fade | Holdout | 32 | 59.4% | $78 | 1.97 | $2,503 | 0.96 | 2.67 | 2.58 | 1.36 | 0.38 | $478 |
| Bridge Monday | Design | 119 | 68.1% | $50 | 3.42 | $5,986 | 1.46 | 2.29 | 2.10 | 1.15 | 0.38 | $1,018 |
| Bridge Monday | Holdout | 98 | 71.4% | $59 | 2.80 | $5,759 | 1.38 | 1.98 | 1.91 | 0.89 | 1.04 | $1,683 |
| CL Sunday | Design | 41 | 70.7% | $108 | 2.02 | $4,426 | 0.86 | 2.88 | 3.40 | 1.37 | 0.35 | $631 |
| CL Sunday | Holdout | 55 | 61.8% | $147 | 2.46 | $8,106 | 1.20 | 3.32 | 2.85 | 2.04 | 0.42 | $1,031 |
| ES MOC | Design | 131 | 55.7% | $38 | 3.60 | $4,959 | 1.53 | 4.33 | 2.71 | 2.55 | 0.20 | $380 |
| ES MOC | Holdout | 71 | 62.0% | $20 | 1.16 | $1,405 | 0.59 | 0.90 | 1.50 | 0.26 | 1.36 | $1,381 |
| RS longs | Design | 324 | 57.7% | $25 | 2.20 | $8,108 | 0.97 | 1.53 | 1.38 | 0.68 | 0.86 | $2,345 |
| RS longs | Holdout | 274 | 56.6% | $50 | 2.81 | $13,776 | 1.42 | 2.44 | 1.52 | 1.88 | 1.03 | $1,895 |

### Long and short sides

One-direction strategies are shown on their traded side only. Values are current-size total / t / PF.

| Strategy and side | Design | Holdout |
|---|---:|---:|
| Vault Break long | $12,984 / 3.06 / 1.44 | $18,049 / 3.27 / 1.51 |
| ONB long | $6,796 / 1.98 / 1.74 | $10,828 / 3.79 / 2.91 |
| ONB short | $17,117 / 3.41 / 2.37 | $5,009 / 1.51 / 1.58 |
| Monday Long long | $3,924 / 1.18 / 1.21 | $15,212 / 3.30 / 1.92 |
| EOS short | $11,598 / 2.36 / 2.07 | $10,281 / 2.29 / 2.39 |
| LDF long | $3,877 / 2.22 / 1.52 | $3,324 / 1.17 / 1.31 |
| LDF short | $3,575 / 1.65 / 1.37 | $6,162 / 2.25 / 1.59 |
| NFP long | $985 / 0.91 / 1.71 | $1,416 / 2.07 / 4.84 |
| NFP short | -$123 / -0.10 / 0.95 | $1,087 / 1.01 / 1.89 |
| Bridge Monday long | $5,986 / 3.42 / 2.10 | $5,759 / 2.80 / 1.91 |
| CL Sunday short | $4,426 / 2.02 / 3.40 | $8,106 / 2.46 / 2.85 |
| ES MOC long | $2,567 / 2.54 / 3.23 | $1,100 / 1.93 / 2.80 |
| ES MOC short | $2,392 / 2.55 / 2.37 | $305 / 0.29 / 1.14 |
| RS long | $8,108 / 2.20 / 1.38 | $13,776 / 2.81 / 1.52 |

The weakest cells are NFP shorts in design and ES MOC shorts in holdout, but both are small samples and the requested
test concerns whole strategy allocations. Directional changes would require separate preregistration.

### Calendar-year contribution

All values are net at current plan size; 2026 is partial.

| Year | VB | ONB | Monday | EOS | LDF | NFP | Bridge | CL | MOC | RS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2018 | $16 | -$654 | -$1,136 | $1,727 | $1,832 | $1,126 | $120 | $202 | $252 | $1,056 |
| 2019 | $531 | $6,128 | $370 | $1,219 | -$1,337 | -$829 | $739 | $652 | $60 | $1,200 |
| 2020 | $4,727 | $3,889 | $4,652 | $3,130 | -$244 | -$569 | $2,788 | $662 | $2,312 | $2,107 |
| 2021 | $4,811 | $7,776 | $590 | $2,361 | $2,361 | $470 | $2,219 | $142 | $890 | $1,734 |
| 2022 | $2,899 | $6,775 | -$552 | $3,161 | $4,841 | $665 | $120 | $2,768 | $1,445 | $2,011 |
| 2023 | $5,468 | $2,674 | $4,304 | $3,830 | $4,138 | $981 | $1,429 | $532 | $400 | $2,503 |
| 2024 | $3,036 | $7,192 | $1,631 | $1,904 | $297 | $920 | $83 | $1,029 | $1,658 | $2,080 |
| 2025 | $6,529 | $3,455 | $4,738 | $3,404 | $1,044 | $354 | $2,480 | $1,512 | -$955 | $5,265 |
| 2026 | $3,016 | $2,516 | $4,539 | $1,143 | $4,007 | $249 | $1,768 | $5,033 | $303 | $3,927 |

The 5,000-sample holdout bootstrap reinforces the difference between standalone and account value. Annual P&L 5th-95th
percentiles were: VB $2,400-$6,900; ONB $2,417-$6,068; Monday $1,979-$5,786; EOS $807-$4,723; LDF $818-$4,175;
NFP $113-$1,233; Bridge $579-$2,323; CL $573-$3,797; MOC -$190-$900; and RS $1,741-$5,437. Holdout Sharpe intervals
excluded zero for every strategy except MOC (-0.29 to 1.52), yet removing MOC still worsened account payouts and blowups.

Daily correlations remain low. The highest absolute partner for each key concentration was VB-RS **0.23**, ONB-VB
**0.14**, LDF-VB **0.12**, Monday-Bridge **0.30**, MOC-ONB **0.03**, and CL-Monday **-0.08**. Low daily correlation
does not eliminate intraday stacking, which is why the narrower Vault Break overlap test remains justified.

## Placebos and account level

The paired funded bootstrap is the primary account-level test and directly answers both questions: each strategy's
marginal paid value and its marginal trailing-drawdown cost. Every removal uses identical sampled market days as the
current portfolio, preserving cross-strategy dependence and volatility clusters.

A random-removal placebo is not applicable here. Each variant removes a named, already-live strategy in full; randomly
removing another strategy or arbitrary days would answer a different allocation question. The empty slot is the required
replacement control. Addition tests are also inapplicable because all ten lines are already in the benchmark.

The results do not support dropping a line. VB, Monday and RS have the same qualitative tradeoff in both periods:
removing them marginally raises capped two-year paid value and lowers blowups, but delays payout six. VB is the only
tradeoff large enough to justify the already-planned targeted size test. EOS, NFP and CL flip between design and holdout,
so changing them now would select on the holdout.

## What could make this wrong (data, fills, look-ahead, multiple testing)

- Results inherit the repository's MultiCharts trade lists and Python reconstructions. Historical-data revisions or
  unmatched live fills can change the sequence that reaches the trailing threshold.
- Circular blocks preserve local dependence but cannot model every future volatility regime or prop-firm rule change.
  Payout discreteness makes small mean differences sensitive to a few path outcomes.
- The study measures the current sizes. A partial size can behave differently from both current and zero, so WATCH means
  preregister a separate sizing test rather than interpolate this table.
- The ten removals were divided into three plans solely to respect the five-variant cap, and all were committed before
  results. Design eligibility was fixed before holdout output. No removal passed it.
- Executable assertions verify that every reconstructed standalone strategy equals its exact account component and that
  each whole strategy equals its long plus short paths.

## Differences between the MultiCharts code and the test

No MultiCharts code was written. The test uses the repository's existing confirmed trade paths and account simulator;
it changes portfolio membership only. No live file, broker setting, VPS configuration or API key was touched.
