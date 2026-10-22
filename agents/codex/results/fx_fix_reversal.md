# London FX fixing reversal: REJECT
Summary: Test whether fading EUR/USD futures after London's 16:00 benchmark adds a new scheduled flow to the NQ-heavy plan.
Both design variants failed; selected 30-minute hold lost $19.17 per 6E trade on 2023+, t=-5.63, with random-control-like returns.
Holdout addition cut year-one paid value $2,312 and raised year-one blowups from 7.25% to 11.05%; replacement also failed.
Keep the current roster and ES MOC 2 MES. The proposed VB overlap test is withdrawn; do not tune this FX rule on 2023+.
Plan: `agents/codex/plans/fx_fix_reversal.md`, commit `aed463d`   Script: `analysis/codex_fx_fix_reversal.py`   Output: `analysis/outputs/codex_fx_fix_reversal/`   Trials run: 2 signal variants; 4 funded configurations

## Rule (as tested)

At 16:03 London, fade the 6E move since 15:30 London. Enter at the next minute open, stop 0.25 previous-15-weekday ATR
rounded up to a 6E tick, no target. A exits at 16:33 London; B at 17:03. Convert `Europe/London` to `America/Chicago`
per date; ordinary decisions are 10:03 CT and US/UK DST-mismatch decisions are 11:03 CT. No overnight holds or fitted
signal thresholds. Use the repository's minute walker with stops active on the entry bar and gap-through stop fills.
Charge $7.25 commission plus one 0.00005 tick per market/stop fill: **$19.75 per full 6E round trip**.

The preregistered mechanism was temporary price pressure from investors executing currency conversions at a benchmark.
LSEG establishes the fixing schedule and five-minute sampling window ending at 16:02:30 London. Michelberger and Witte
document unusual fixing-window volatility and extrema on old spot data. Neither establishes a profitable modern futures
reversal; that directional prediction was the hypothesis tested here.

Sources: [LSEG WMR](https://www.lseg.com/en/ftse-russell/benchmarks/wmr-fx-benchmarks),
[WMR methodology, section 4.4.2](https://www.lseg.com/content/dam/ftse-russell/en_us/documents/ground-rules/wmr-fx-methodology.pdf),
[Michelberger and Witte, arXiv:1501.07778v2](https://arxiv.org/html/1501.07778v2),
[CME 6E contract specifications](https://www.cmegroup.com/markets/fx/g10/euro-fx/specs).

The design period is 2018-22. Choose B only if its design Calmar improves at least 10% over A; favor the shorter hold
otherwise. B improved Calmar only about 3.4%, so A was fixed before its holdout was constructed. Both failed the design
gate (positive mean, t>=2 and both placebo p<=0.05). `design_selection.json` records that failure and the replacement
slot before any selected-rule 2023+ output. The unselected 60-minute rule was not run on holdout.

## Results

All strategy dollars below are **per one full 6E contract**, not per NQ or M6E. The dates match the confirmed plan's
2018-01-02 through 2026-10-09 trading calendar; 2026 is partial.

| Design rule | Trades | Gross total | All costs | Net total | Net/trade | t | Calmar |
|---|---:|---:|---:|---:|---:|---:|---:|
| A: 30 minutes | 1,261 | -$1,000 | $24,905 | -$25,905 | -$20.54 | -6.30 | -0.192 |
| B: 60 minutes | 1,261 | +$1,431 | $24,905 | -$23,474 | -$18.61 | -4.42 | -0.186 |

The selected rule's whole/long/short standard metrics:

| Period | Side | Trades | Win | Net/trade | t | Net total | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2018-22 | Whole | 1,261 | 41.1% | -$20.54 | -6.30 | -$25,905 | -2.79 | -3.48 | 0.621 | -0.192 | 30.00 | $26,331 |
| 2018-22 | Long | 637 | 41.3% | -$18.81 | -4.17 | -$11,981 | -1.83 | -2.37 | 0.638 | -0.187 | 14.63 | $12,493 |
| 2018-22 | Short | 624 | 40.9% | -$22.31 | -4.74 | -$13,924 | -2.08 | -2.55 | 0.604 | -0.188 | 15.75 | $14,482 |
| 2023+ | Whole | 955 | 41.4% | -$19.17 | -5.63 | -$18,305 | -2.86 | -3.60 | 0.615 | -0.256 | 22.04 | $18,551 |
| 2023+ | Long | 499 | 40.3% | -$20.00 | -4.38 | -$9,980 | -2.21 | -2.72 | 0.595 | -0.254 | 11.25 | $10,182 |
| 2023+ | Short | 456 | 42.5% | -$18.26 | -3.59 | -$8,325 | -1.81 | -2.36 | 0.636 | -0.248 | 11.31 | $8,706 |
| Full | Whole | 2,216 | 41.2% | -$19.95 | -8.44 | -$44,210 | -2.82 | -3.52 | 0.618 | -0.110 | 52.22 | $44,635 |
| Full | Long | 1,136 | 40.8% | -$19.33 | -5.99 | -$21,961 | -1.98 | -2.52 | 0.620 | -0.111 | 24.77 | $21,961 |
| Full | Short | 1,080 | 41.6% | -$20.60 | -5.94 | -$22,249 | -1.97 | -2.47 | 0.617 | -0.108 | 27.87 | $22,911 |

Gross holdout P&L was only **+$556** against **$18,861** in commission and slippage. Gross full-sample P&L was -$444.
Costs explain almost the entire loss; there is no gross edge here large enough to rescue through execution assumptions.

| Year | Whole net | Long net | Short net |
|---:|---:|---:|---:|
| 2018 | -$5,585 | -$3,230 | -$2,356 |
| 2019 | -$5,084 | -$2,319 | -$2,766 |
| 2020 | -$4,601 | -$1,849 | -$2,752 |
| 2021 | -$4,851 | -$2,713 | -$2,138 |
| 2022 | -$5,783 | -$1,871 | -$3,913 |
| 2023 | -$5,193 | -$2,352 | -$2,840 |
| 2024 | -$6,015 | -$3,124 | -$2,891 |
| 2025 | -$4,091 | -$2,371 | -$1,720 |
| 2026 partial | -$3,008 | -$2,134 | -$874 |

The 5,000-sample holdout daily block bootstrap gives whole Sharpe **[-3.77, -1.98]**, annual net
**[-$6,109, -$3,354]**, PF **[0.529, 0.713]** and max drawdown **[$13,527, $23,885]** at the 5th-95th percentiles.
Long and short Sharpe intervals are [-3.03, -1.37] and [-2.72, -0.95]. P(Sharpe<=0) is 100% for all three.
All metric intervals, including Sortino, Calmar and Ulcer, are in `bootstrap.csv`.

## Placebos and account level

Each placebo uses 1,000 randomized paths, preserving dates, stops and holding period. Random side **re-executes** each
side's stop; it does not flip P&L from an already-stopped trade. Random time uses uniform valid 08:00-13:00 CT decision
minutes outside 90 minutes of the true fixing decision, with the same 33-minute lookback and re-executed stops.

| Rule/period | Real net | Random-side median | Random-side p | Random-time median | Random-time p |
|---|---:|---:|---:|---:|---:|
| A design | -$25,905 | -$26,370 | 0.452 | -$24,286 | 0.669 |
| B design | -$23,474 | -$25,820 | 0.340 | -$25,352 | 0.352 |
| A holdout | -$18,305 | -$18,105 | 0.522 | -$18,346 | 0.493 |

The selected rule looks like random activity after costs. Correct London-clock DST-mismatch trades also lose: design
-$3,590, holdout -$1,373. The fixed 10:03 CT clock control loses -$2,577/-$2,121. Neither supports a usable fixing edge.

The candidate traded on 267 of the plan CSV's 274 zero-P&L dates and lost $4,623 on those dates. Filling an activity gap
does not establish positive expectancy. Zero daily P&L is only an activity proxy, not proof of no intraday position.

The replacement slot was selected mechanically by greatest absolute design daily correlation: **NFP Fade, -0.060**.
This is weak and does not establish a shared economic mechanism; there were **zero actual intraday overlap dates** with
NFP. The rule prevents a favorable replacement slot being chosen after holdout, and the empty-slot control is explicit.

Funded tests use one full 6E contract and the exact current roster (VB 2/1, ES MOC 2 MES, RS longs 1 MNQ, other sizes
unchanged), with $1,500 cushion scaling. Ordinary floor(1*f) makes 6E inactive below full cushion. No fractional 6E or
micro-futures fills are assumed. Each period uses 2,000 paired circular 20-day-block, 500-day histories.

| Period | Portfolio | Year 1 paid | Year 2 paid | Blown year 1 | Blown year 2 | All six | Median days to six |
|---|---|---:|---:|---:|---:|---:|---:|
| Design | Current | $8,481 | $11,929 | 7.20% | 7.75% | 89.55% | 286 |
| Design | Add FX | $5,341 | $9,778 | 13.25% | 16.55% | 60.90% | 441 |
| Design | Empty NFP slot | $8,392 | $11,983 | 6.55% | 7.25% | 89.45% | 290 |
| Design | Replace NFP with FX | $5,292 | $9,800 | 12.30% | 15.95% | 59.70% | 448 |
| Holdout | Current | $10,602 | $12,079 | 7.25% | 7.40% | 92.30% | 219 |
| Holdout | Add FX | $8,290 | $11,402 | 11.05% | 11.80% | 84.75% | 288 |
| Holdout | Empty NFP slot | $10,224 | $11,888 | 8.70% | 8.85% | 90.60% | 227 |
| Holdout | Replace NFP with FX | $7,942 | $11,274 | 11.25% | 12.50% | 83.15% | 301 |

For all six-payout medians above, non-completing paths count as infinite as preregistered. `account_results.csv` also
includes the median among completers, matching the older report's convention. For example, the holdout current-plan
median is 219 including non-completers and 211 among completers; do not compare those two definitions interchangeably.

The paired 90% Monte Carlo confidence interval for the holdout addition's mean paid-value change is **[-$2,429, -$2,195]**
in year one and **[-$802, -$552]** in year two. Replacement versus empty is **[-$2,399, -$2,165]** and
**[-$735, -$492]**. These intervals measure simulation sampling error conditional on the historical bootstrap model,
not uncertainty about future markets. Raw paired outcomes are saved in `accounts_*.npz`.

At one full 6E without cushion protection, holdout one-year Monte Carlo gives **99.02%** probability of hitting the
$2,000 EOD trail and **99.74%** probability of a losing year. Trade-bootstrap total P&L has 5th-95th percentiles
[-$23,630, -$12,861]. Daily-P&L permutation gives 95th-percentile holdout max drawdown $19,506 (long $11,017;
short $9,578). The funded bench above includes cushion protection and the rest of the portfolio.

## What could make this wrong (data, fills, look-ahead, multiple testing)

- The source study used spot data from before the 2015 fixing-window reform. The tested 2018-26 futures series and
  post-window rule are different; the sources motivated the hypothesis rather than supplying these exact parameters.
- There is no benchmark-order feed or complete historical record of exceptional fixing schedules in this test. The
  weekday London-clock rule is a proxy for the flow; introducing a holiday or order-imbalance filter now would be a new
  trial and could not reuse this period as an untouched holdout.
- Unadjusted continuous-contract rolls can inflate daily ATR. These trades are intraday and do not straddle the nightly
  roll, but the stop estimate can still inherit an inflated prior range.
- One design date lacked required signal/ATR data; flat pre-fix moves skipped 27 design and 18 holdout dates. No entries
  were missing and no sessions truncated. Two planned exit observations were missing (B design on 2022-03-08 and A
  holdout on 2025-12-12); the repository walker uses the last available close before the exit. All are in `data_audit.csv`.
- The test uses front-month 6E data and full-contract costs. Lower M6E transaction costs or real micro-futures liquidity
  are not established by these data. There is no profitable gross effect here to support assuming cheaper fills.
- No holdout threshold or side was tuned. The paper exception for two ex-ante variants required t>=2 plus clean
  placebos; both failed. At the repository's pre-study count of 274 items, the standard t bar is 3.564 and the selected
  full-sample deflated Sharpe is 0.0. No promotion is warranted under either standard.
- Executable assertions verify realized 6E component P&L equals trade P&L, real-side placebo replays equal actual trades,
  next-minute entry timing and flat-before-15:59. Synthetic checks also passed DST conversion, currency-to-dollar path
  conversion, exact cost arithmetic and entry-bar stop activation.

## Differences between the MultiCharts code and the test

No MultiCharts code was written because the idea failed. Existing execution and path tools were extended only inside
`analysis/codex_fx_fix_reversal.py` to support native 6E dollar units. No live trading, broker, VPS or API changes.
