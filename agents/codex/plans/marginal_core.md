# Funded-plan marginal contribution: core NQ lines

## Question and benchmark

Which core NQ strategies improve the current 50K funded account after their interaction with the Apex trailing drawdown,
payout cap and $1,500 cushion sizing is included?

The benchmark is the roster confirmed for this study: Vault Break 2 MNQ on normal days / 1 after a single-print session,
Overnight Bias ML v2 at $400 risk, Monday Long 1 MNQ, Expiration Open Short at $700 risk, Late-Day Flow 2 MNQ, NFP
Fade at $500 risk, Bridge Monday Long 1 MNQ, CL Sunday fade 2 MCL, ES MOC Follow 2 MES and Relative Strength longs only
1 MNQ. ES MOC is active. Relative Strength remains off below the full-size cushion when ordinary integer rounding makes
its scaled quantity zero.

## Mechanism

A strategy can have positive standalone expectancy and still harm a funded account if its losses arrive while the
trailing threshold is close, if it delays cushion growth, or if its gains arrive after the account has reached the payout
cap. Paired leave-one-out histories measure the cash-flow and survival value of each line in the actual portfolio sequence.

## Variants (five total)

1. Current benchmark.
2. Remove Vault Break completely (both normal and single-print-day quantities).
3. Remove Overnight Bias ML v2.
4. Remove Late-Day Flow.
5. Remove Relative Strength longs.

Every other strategy and all sizing, fills, exits, costs and account rules remain unchanged. This is an empty-slot test;
removed strategies are not replaced.

## Design, holdout and decision

- Design: 2018-01-01 through 2022-12-31. Holdout: 2023-01-01 onward, opened only after design results are recorded.
- Use at least 2,000 paired circular 20-trading-day block histories per period and the same sampled days for every variant.
- Also reproduce the current benchmark on all available dates and report one-year paid value, two-year paid value,
  blow-up probability, all-six-payout probability and median days to six payouts.
- A removal is design-eligible only if mean two-year paid value is no lower, blow-up probability is no higher, median
  time to six payouts is no more than five trading days slower, and either paid value improves by at least $250 or
  blow-up probability falls by at least one percentage point.
- A design-eligible removal becomes a candidate for a later sizing study only if it is also no worse on holdout paid
  value, blow-up probability and days to six payouts. A mixed result is WATCH. Otherwise keep the strategy unchanged.

## Required evidence

For each strategy, report its leave-one-out paired payout difference and interval, blow-up difference, all-six rate and
time to six payouts in design and holdout. Report standalone full-size total, active days, daily win rate, average, t,
Sharpe, Sortino, profit factor, Calmar, Ulcer and max drawdown for the whole strategy and long/short sides, split by design
and holdout and by calendar year. Include 5,000-sample holdout block-bootstrap intervals and daily correlations with the
rest of the plan. Count all five variants. No MultiCharts or live files will be changed.

Most-overlapping portfolio lines are identified empirically by daily P&L correlation. The leave-one-out comparison is
both the replacement-by-empty-slot test and the account-level test; an addition test is not applicable to an existing
roster line.

Planned script: `analysis/codex_marginal_contribution.py`

Planned output: `analysis/outputs/codex_marginal_contribution/`

Planned combined report: `agents/codex/results/marginal_contribution.md`
