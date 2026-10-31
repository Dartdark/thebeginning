# Funded-plan marginal contribution: scheduled NQ lines

## Question and benchmark

Which scheduled NQ strategies improve the current 50K funded account after account sequencing is included? Use the exact
benchmark and testing machinery preregistered in `agents/codex/plans/marginal_core.md`; ES MOC Follow is active at 2 MES.

## Mechanism

Rare calendar trades can make money per contract yet add little payout value, or can protect a funded path by growing the
cushion at useful times. Paired leave-one-out histories measure that marginal account effect without changing the other
signals.

## Variants (five total)

1. Current benchmark.
2. Remove Monday Long.
3. Remove Expiration Open Short.
4. Remove NFP Fade.
5. Remove Bridge Monday Long.

Every other strategy and all sizing, fills, exits, costs and account rules remain unchanged. Removed strategies are not
replaced.

## Design, holdout and decision

Design is 2018-22 and holdout is 2023 onward. Use at least 2,000 paired circular 20-day-block histories per period. Apply
the same eligibility and holdout rules stated in `marginal_core.md`: no lower design paid value, no higher blowups, no
more than five days slower to six payouts, plus either +$250 paid value or -1 percentage point blowups; then no worse on
all three holdout measures. Passing removals are candidates for a later sizing study, mixed results are WATCH, and failed
removals mean keep the strategy unchanged.

## Required evidence

Use the standard whole/long/short, design/holdout, annual, bootstrap, correlation and account-level evidence specified in
`marginal_core.md`. Count all five variants. The empty slot is the replacement test; addition is not applicable. No
MultiCharts or live files will be changed.

Planned script: `analysis/codex_marginal_contribution.py`

Planned output: `analysis/outputs/codex_marginal_contribution/`

Planned combined report: `agents/codex/results/marginal_contribution.md`
