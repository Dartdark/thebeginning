# Funded-plan marginal contribution: cross-market and close lines

## Question and benchmark

Do CL Sunday Gap Fade and ES MOC Follow improve the current 50K funded account at their current sizes? Use the exact
benchmark and testing machinery preregistered in `agents/codex/plans/marginal_core.md`; ES MOC Follow is confirmed active
at 2 MES.

## Mechanism

The two non-NQ allocations may diversify the NQ-heavy roster, but their value depends on when gains and losses occur
relative to the shared trailing threshold and payout cap. Paired empty-slot histories measure their marginal account value.

## Variants (three total)

1. Current benchmark.
2. Remove CL Sunday Gap Fade.
3. Remove ES MOC Follow.

Every other strategy and all sizing, fills, exits, costs and account rules remain unchanged. Removed strategies are not
replaced. ES MOC 1 MES was already tried in the preregistered overlap study and is not a new variant here.

## Design, holdout and decision

Design is 2018-22 and holdout is 2023 onward. Use at least 2,000 paired circular 20-day-block histories per period. Apply
the same eligibility and holdout rules stated in `marginal_core.md`. Passing removals are candidates for a later sizing
study, mixed results are WATCH, and failed removals mean keep the strategy unchanged.

## Required evidence

Use the standard whole/long/short, design/holdout, annual, bootstrap, correlation and account-level evidence specified in
`marginal_core.md`. Count all three variants. The empty slot is the replacement test; addition is not applicable. No
MultiCharts or live files will be changed.

Planned script: `analysis/codex_marginal_contribution.py`

Planned output: `analysis/outputs/codex_marginal_contribution/`

Planned combined report: `agents/codex/results/marginal_contribution.md`
