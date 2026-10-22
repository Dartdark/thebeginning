# overlap risk cap: REJECT
Summary: Test whether capping simultaneous same-direction NQ exposure or reducing ES MOC improves the 50K funded path.
Neither change qualified on 2018-22; retain the current portfolio with ES MOC at 2 MES and no NQ overlap cap.
On 2023+ histories, cap 2 cut mean two-year paid value by $441 and raised blowups from 6.7% to 9.9%.
The cap removed profitable units (holdout $19,659, t=6.73) and was worse than 98.05% of matched random removals on profit.
Plan: `agents/codex/plans/overlap_risk_cap.md`, commits `b6fc8c0`, `17baec8`   Script: `analysis/codex_overlap_risk_cap.py`   Output: `analysis/outputs/codex_overlap_risk_cap/`   Trials run: 5

## Rule (as tested)

The benchmark is the documented 50K plan: VB 2/1 MNQ, ONB ML $400 risk, Monday 1 MNQ, EOS $700 risk, LDF 2 MNQ,
NFP $500 risk, Bridge Monday 1 MNQ, CL Sunday fade 2 MCL, ES MOC 2 MES and Relative Strength long-only 1 MNQ, with
the existing $1,500 cushion scaling and funded-account rules.

Five fixed variants were run: current; MOC at 1 MES; MOC removed; NQ cap 2 with MOC 2; and NQ cap 2 with MOC 1. For
the cap, a later NQ entry was reduced only when another strategy already had a same-direction position active. Planned
same-direction exposure after the entry could not exceed 2 MNQ. Opposite positions and same-minute entries were not
counted against one another. Cushion scaling and integer rounding were applied after the cap. The cap reduced 1,216 of
4,417 NQ entries and removed 1,780 MNQ units over the full sample.

Selection used 2018-22 only. The script fixed that decision before opening 2023+. Each account comparison used 2,000
paired circular 20-day-block histories. The five variants are the complete trial count.

## Results

No alternative met the preregistered design gate. Cap 2 had slightly higher design mean two-year paid value (+$50) and
lower blowups (-1.4 points), but was 22.5 days slower to six payouts and therefore ineligible. Reducing or removing MOC
lowered paid value and raised blowups. The holdout independently favored the unchanged plan.

| Period | Variant | Year-1 paid | Year-2 paid | Blowup | All 6 payouts | Median days to 6 | Difference in year-2 paid | Difference in blowup |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2018-22 design | Current, MOC 2 | $8,313 | $11,854 | 7.9% | 88.7% | 276 | $0 | 0.0 pp |
| 2018-22 design | MOC 1 | $7,824 | $11,606 | 9.8% | 86.2% | 285 | -$248 | +2.0 pp |
| 2018-22 design | MOC 0 | $7,643 | $11,498 | 10.4% | 84.8% | 291 | -$357 | +2.5 pp |
| 2018-22 design | Cap 2, MOC 2 | $7,514 | $11,904 | 6.5% | 86.6% | 298 | +$50 | -1.4 pp |
| 2018-22 design | Cap 2, MOC 1 | $7,036 | $11,515 | 8.2% | 82.3% | 306 | -$340 | +0.3 pp |
| 2023+ holdout | Current, MOC 2 | $10,651 | $12,166 | 6.7% | 93.1% | 216 | $0 | 0.0 pp |
| 2023+ holdout | MOC 1 | $10,478 | $12,012 | 8.0% | 91.8% | 215 | -$154 | +1.3 pp |
| 2023+ holdout | MOC 0 | $10,380 | $12,016 | 7.9% | 91.8% | 218 | -$150 | +1.2 pp |
| 2023+ holdout | Cap 2, MOC 2 | $9,530 | $11,725 | 9.9% | 88.7% | 230 | -$441 | +3.2 pp |
| 2023+ holdout | Cap 2, MOC 1 | $9,348 | $11,650 | 10.5% | 87.6% | 232 | -$516 | +3.8 pp |

The paired holdout difference interval was [-$11,500, $0] for cap 2. Its wide, discrete range comes from the payout
schedule; the mean and blowup changes both failed the adoption rule. With the unchanged plan selected, 10-day and
60-day blocks gave mean paid values of $11,948 and $12,543 and blowups of 8.3% and 3.6%, respectively.

Full-size daily results below use net strategy P&L before the funded-account payout transform. `Days` is the number of
nonzero portfolio days and `Avg/day` is therefore more meaningful than dollars per NQ for this mixed NQ/ES/CL,
risk-sized portfolio. PF is daily profit factor.

| Variant | Period | Days | Win | Avg/day | t | Total | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Design | 1,045 | 54.7% | $81 | 6.78 | $84,214 | 2.98 | 6.17 | 1.87 | 5.34 | 1.23 | $3,081 |
| MOC 1 | Design | 1,045 | 54.5% | $78 | 6.62 | $81,734 | 2.91 | 5.98 | 1.84 | 5.23 | 1.27 | $3,054 |
| MOC 0 | Design | 1,026 | 54.5% | $77 | 6.44 | $79,255 | 2.83 | 5.78 | 1.82 | 5.12 | 1.32 | $3,026 |
| Cap 2, MOC 2 | Design | 1,045 | 56.1% | $69 | 6.61 | $71,707 | 2.91 | 5.78 | 1.82 | 5.20 | 1.07 | $2,695 |
| Cap 2, MOC 1 | Design | 1,045 | 55.6% | $66 | 6.43 | $69,227 | 2.83 | 5.58 | 1.80 | 5.00 | 1.11 | $2,705 |
| Current | Holdout | 801 | 55.4% | $125 | 6.79 | $100,414 | 3.44 | 7.51 | 2.05 | 5.41 | 0.92 | $4,809 |
| MOC 1 | Holdout | 801 | 55.1% | $124 | 6.76 | $99,711 | 3.42 | 7.49 | 2.04 | 5.46 | 0.93 | $4,728 |
| MOC 0 | Holdout | 786 | 55.1% | $126 | 6.72 | $99,009 | 3.40 | 7.42 | 2.03 | 5.52 | 0.94 | $4,646 |
| Cap 2, MOC 2 | Holdout | 801 | 56.2% | $101 | 6.63 | $80,755 | 3.36 | 6.76 | 1.95 | 5.30 | 0.88 | $3,947 |
| Cap 2, MOC 1 | Holdout | 801 | 55.9% | $100 | 6.60 | $80,053 | 3.34 | 6.73 | 1.94 | 5.36 | 0.90 | $3,865 |

The cap's lower raw max drawdown did not improve the funded path. It removed enough profitable exposure that the account
reached payouts more slowly and encountered the trail more often on holdout histories.

Long and short results are separated below. Days can overlap because a portfolio can trade both directions in one day.

| Side | Variant | Period | Days | Win | Avg/day | t | Total | Sharpe | PF | Max DD |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Long | Current | Design | 836 | 53.2% | $54 | 4.39 | $45,228 | 1.93 | 1.57 | $3,865 |
| Long | MOC 1 | Design | 836 | 53.1% | $53 | 4.29 | $43,945 | 1.89 | 1.55 | $3,811 |
| Long | MOC 0 | Design | 818 | 53.2% | $52 | 4.17 | $42,661 | 1.84 | 1.54 | $3,756 |
| Long | Cap 2, MOC 2 | Design | 836 | 54.3% | $40 | 4.09 | $33,535 | 1.80 | 1.48 | $3,636 |
| Long | Cap 2, MOC 1 | Design | 836 | 54.1% | $39 | 3.96 | $32,251 | 1.75 | 1.47 | $3,622 |
| Long | Current | Holdout | 633 | 54.2% | $110 | 5.22 | $69,464 | 2.64 | 1.84 | $3,852 |
| Long | MOC 1 | Holdout | 633 | 54.2% | $109 | 5.18 | $68,914 | 2.62 | 1.83 | $3,927 |
| Long | MOC 0 | Holdout | 623 | 54.1% | $110 | 5.14 | $68,364 | 2.59 | 1.82 | $4,003 |
| Long | Cap 2, MOC 2 | Holdout | 633 | 55.3% | $79 | 4.84 | $49,743 | 2.45 | 1.69 | $3,454 |
| Long | Cap 2, MOC 1 | Holdout | 633 | 55.3% | $78 | 4.79 | $49,193 | 2.42 | 1.68 | $3,529 |
| Short | Current | Design | 415 | 53.7% | $94 | 4.82 | $38,986 | 2.10 | 2.12 | $1,720 |
| Short | MOC 1 | Design | 415 | 53.7% | $91 | 4.71 | $37,790 | 2.05 | 2.10 | $1,743 |
| Short | MOC 0 | Design | 376 | 53.2% | $97 | 4.59 | $36,593 | 1.99 | 2.07 | $1,804 |
| Short | Cap 2, MOC 2 | Design | 415 | 54.2% | $92 | 4.80 | $38,172 | 2.09 | 2.10 | $1,613 |
| Short | Cap 2, MOC 1 | Design | 415 | 54.2% | $89 | 4.69 | $36,976 | 2.04 | 2.08 | $1,637 |
| Short | Current | Holdout | 347 | 57.1% | $89 | 4.30 | $30,950 | 2.15 | 2.01 | $2,565 |
| Short | MOC 1 | Holdout | 347 | 57.1% | $89 | 4.30 | $30,797 | 2.15 | 2.03 | $2,528 |
| Short | MOC 0 | Holdout | 321 | 57.3% | $95 | 4.29 | $30,644 | 2.14 | 2.04 | $2,492 |
| Short | Cap 2, MOC 2 | Holdout | 347 | 57.1% | $89 | 4.34 | $31,012 | 2.17 | 2.02 | $2,565 |
| Short | Cap 2, MOC 1 | Holdout | 347 | 57.1% | $89 | 4.34 | $30,860 | 2.17 | 2.03 | $2,528 |

The long side explains nearly all cap damage. Only 48 of 974 removed design units and 25 of 806 removed holdout units
were shorts.

| Year | Current | MOC 1 | MOC 0 | Cap 2, MOC 2 | Cap 2, MOC 1 |
|---:|---:|---:|---:|---:|---:|
| 2018 | $4,541 | $4,415 | $4,289 | $5,328 | $5,202 |
| 2019 | $8,731 | $8,701 | $8,671 | $7,508 | $7,478 |
| 2020 | $23,454 | $22,298 | $21,142 | $18,565 | $17,409 |
| 2021 | $23,355 | $22,910 | $22,465 | $18,392 | $17,947 |
| 2022 | $24,133 | $23,410 | $22,688 | $21,913 | $21,190 |
| 2023 | $26,259 | $26,059 | $25,859 | $20,752 | $20,552 |
| 2024 | $19,829 | $19,000 | $18,171 | $15,151 | $14,322 |
| 2025 | $27,825 | $28,303 | $28,780 | $24,084 | $24,562 |
| 2026 partial | $26,500 | $26,349 | $26,197 | $20,768 | $20,616 |

The 5,000-sample holdout block bootstrap for the current plan gave Sharpe 2.70-4.20, annual P&L
$20,035-$32,115, and max drawdown $2,945-$6,615 at the 5th-95th percentiles. Cap 2 gave Sharpe 2.57-4.20,
annual P&L $15,734-$26,423 and max drawdown $2,683-$6,175. Estimated P(Sharpe <= 0) was 0 in both sets of 5,000
samples. These intervals describe daily strategy P&L, not the Apex account trail.

ES MOC itself remained positive but weakened after the design period. At the native one-ES research scale it made
$24,795 over 131 design trades (t=3.60) and $7,026 over 71 holdout trades (t=1.16). Holdout longs made $5,499 over 26
trades (t=1.93); shorts made $1,527 over 45 trades (t=0.29). The funded plan trades 2 MES, so its full-sample portfolio
contribution was $6,364 after the MES conversion. Reducing it to 1 MES removed half that contribution.

| Year | ES MOC trades | Native 1-ES net | Average/trade | t |
|---:|---:|---:|---:|---:|
| 2018 | 37 | $1,259 | $34 | 0.45 |
| 2019 | 17 | $301 | $18 | 0.37 |
| 2020 | 28 | $11,561 | $413 | 2.39 |
| 2021 | 19 | $4,449 | $234 | 1.75 |
| 2022 | 30 | $7,224 | $241 | 2.64 |
| 2023 | 15 | $2,000 | $133 | 0.99 |
| 2024 | 25 | $8,289 | $332 | 2.58 |
| 2025 | 21 | -$4,776 | -$227 | -1.17 |
| 2026 partial | 10 | $1,514 | $151 | 0.86 |

MOC and Late-Day Flow shared 112 dates, with the same direction on 64. Their all-day daily P&L correlation was -0.021;
on shared dates it was -0.083. The proposed overlap concern was not supported at daily resolution.

## Placebos and account level

The overlap cap removed winners rather than losers. It removed 974 MNQ units in design for +$12,507, $12.84 per unit,
t=5.50. It removed 806 units in holdout for +$19,659, $24.39 per unit, t=6.73. Holdout VB normal units alone added
$11,602 (420 units, t=6.55); ONB added $3,237 (47, t=2.68); LDF added $2,538 (272, t=1.98); RS added $2,317
(25, t=1.79). Only VB single-print units were slightly negative: -$35 over 42 units, t=-0.05.

In 2,000 matched random-removal placebos per period, preserving strategy and removal counts, the cap was ordinary in
design profit (52.10% of random drops made at least as much) and poor in holdout profit (98.05% made at least as much).
Its drawdown was lower than only 15.55% of random design drops and 18.45% of random holdout drops. Thus the cap did not
select unusually dangerous marginal units.

The funded bootstrap is the account-level test. Removing or halving MOC failed both as a replacement for the current
MOC allocation and as an empty-slot control. The NQ cap failed as a portfolio overlay, alone and combined with MOC 1.
No addition was applicable because both tested ideas reduce existing exposure rather than introduce a strategy.

## What could make this wrong (data, fills, look-ahead, multiple testing)

- Trade paths inherit the repository's MultiCharts reports and Python reconstructions. Missing reports, timestamp
  mismatches or historical-data revisions would change overlap detection and P&L.
- The cap uses recorded entry and exit minutes. Same-minute entries are deliberately simultaneous; a real cross-chart
  coordinator would need a defined ordering if fills occur within that minute.
- Slippage is the repository standard. Fast common index moves could create correlated live slippage absent from the
  reports, although the cap would need enough savings to offset its large loss of positive expectancy.
- Circular block histories preserve local dependence but do not model every regime or prop-firm rule change. The 2026
  calendar year is partial.
- Five variants were preregistered. No thresholds or priority rules were fitted after viewing holdout results. The
  accounting assertions verify whole P&L equals long plus short, cap differences equal removed-unit P&L, and the MOC
  size effect is identical with and without the cap.

## Differences between the MultiCharts code and the test

No MultiCharts code was written because neither change passed. The tested cap would require shared account-level state
across charts; individual strategy code cannot reproduce it independently.
