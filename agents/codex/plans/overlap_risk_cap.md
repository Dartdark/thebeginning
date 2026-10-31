# Overlap-aware funded-plan risk cap

## Question

Can the current 50K funded portfolio improve its Apex payout path by reducing simultaneous same-direction NQ exposure,
and should ES MOC Follow remain at 2 MES given its weaker 2023+ record and overlap with Late-Day Flow?

## Current benchmark

Use the current 50K funded plan exactly as documented on 2026-10-20:

- Vault Break 2 MNQ on normal days / 1 MNQ after a single-print session;
- Overnight Bias ML v2 at $400 risk;
- Monday Long 1 MNQ;
- Expiration Open Short at $700 risk;
- Late-Day Flow 2 MNQ;
- NFP Fade at $500 risk;
- Bridge Monday Long 1 MNQ;
- CL Sunday up-gap fade 2 MCL;
- ES MOC Follow 2 MES;
- Relative Strength longs only 1 MNQ, off below the full-size cushion as in the existing simulator;
- the existing $1,500 cushion rule, Apex payout rules and costs.

The benchmark must be reconstructed from the same trade paths used by `analysis/funded_bootstrap.py`, with ES MOC and
Relative Strength added by the repository's existing functions. No live files or strategy settings will be changed.

## Mechanism

The $2,000 Apex trailing drawdown is shared by the whole account. When two NQ strategies hold the same direction at the
same time, the later entry adds exposure to the same index move while the account has no additional drawdown allowance.
The portfolio's backtests show low daily correlations, but daily correlation can hide intraday risk stacking. A cap on
the later entry may preserve the first signal while reducing the loss from a common adverse move.

ES MOC Follow and Late-Day Flow are both closing-flow momentum strategies on highly correlated equity indices. ES MOC
has a valid closing-auction mechanism and independent confirmation, but its result weakened after 2022. Reducing it from
2 MES to 1 MES may retain diversification with less use of the account's risk budget; removing it is the empty-slot
control.

## Rules and variants (five total, including the benchmark)

All overlap decisions use only information available at the new trade's entry. Entries are processed chronologically.
An NQ position remains active through its recorded exit minute. "Full-size planned quantity" is the existing plan's
quantity before cushion scaling, including each day's ATR-based integer size for risk-sized strategies.
Entries stamped in the same minute are treated as simultaneous: they see positions open before that minute but do not
consume capacity from one another. This avoids assigning an arbitrary chart priority that does not exist in the plan.

For the overlap-cap variants, a strategy with no active same-direction NQ position keeps its normal quantity. If one or
more other NQ strategies are already active in the same direction, reduce only the new entry so total active planned
same-direction exposure does not exceed 2 MNQ. Never enlarge a position, alter its exits, or suppress an opposite-side
entry. Apply the ordinary cushion multiplier and integer rounding after this cap. ES, CL and MCL positions do not count
toward the NQ cap.

1. **Current plan:** benchmark above, including ES MOC 2 MES.
2. **ES MOC 1:** current plan with ES MOC Follow reduced to 1 MES.
3. **ES MOC 0:** current plan without ES MOC Follow (empty-slot control).
4. **NQ cap 2:** current plan with the overlap cap; ES MOC remains 2 MES.
5. **NQ cap 2 + ES MOC 1:** apply both changes.

No threshold, priority order or additional combination will be tried after results are seen. A materially different cap
is a new trial and requires a new plan.

## Design, holdout and selection

- Design period: 2018-01-01 through 2022-12-31 only.
- Holdout: 2023-01-01 onward, opened once after the design-period tables and selection are fixed in the script output.
- Use paired circular 20-trading-day block bootstrap histories. Run at least 2,000 histories per period with fixed seeds.
- Rank the four alternatives on design data only. An alternative is eligible only if, versus the current plan, it has:
  - mean two-year payouts no lower;
  - blow-up probability no more than 0.5 percentage point higher;
  - median time to six payouts no more than 5 trading days slower; and
  - either at least $250 higher mean two-year payouts or at least 1 percentage point lower blow-up probability.
- Among eligible alternatives choose the highest mean two-year payout; break a difference under $100 in favour of the
  lower blow-up probability, then the simpler rule. If none is eligible, retain the current plan.
- Holdout adoption requires the selected alternative to remain no worse than the current plan on mean two-year payouts,
  blow-up probability and median days to six payouts. Otherwise reject the change. A small design-only improvement or a
  mixed holdout result is WATCH, not adoption.

## Required evidence

The script will reproduce every reported number and save machine-readable tables under
`analysis/outputs/codex_overlap_risk_cap/`.

Report for the current plan and all four alternatives:

- full-period, design and holdout total dollars and daily Sharpe, Sortino, profit factor, Calmar, Ulcer and max drawdown;
- results by calendar year;
- long and short portfolio P&L separately where direction is defined;
- paired bootstrap intervals for payout differences and the standard holdout bootstrap intervals;
- one-year and two-year payouts, blow-up probability, all-six-payout probability and median days to six payouts;
- results under 10-day and 60-day bootstrap blocks as sensitivity checks for the selected rule only.

Because the overlap cap removes marginal contract units, treat it as a filter:

- show the removed units' total, average and t-stat, overall and by strategy, for design and holdout;
- compare total dollars with the unchanged portfolio on the same dates;
- randomly remove the same number of same-strategy contract units at least 2,000 times, preserving the number removed by
  strategy and period, and report where the cap ranks on total profit and max drawdown;
- disclose how many entries and contract units are reduced, including longs and shorts separately.

For ES MOC, show its whole, long and short results for design, holdout and by year, plus its marginal account-level effect
at 0, 1 and 2 MES. The strategy it overlaps most is Late-Day Flow; report shared trade days, same-direction days and daily
P&L correlation.

## Decision and implementation boundary

Adopt only under the preregistered design and holdout rule above. If a change passes, it remains a research candidate for
Claude's independent review. MultiCharts coordination code is written only after that review because an intraday
cross-chart exposure cap requires a shared account-level signal. This task will not edit live strategy files, broker
settings, the VPS, API keys, `TIER_LIST.md`, `TODO.md` or the funded plan.

Planned script: `analysis/codex_overlap_risk_cap.py`

Planned output: `analysis/outputs/codex_overlap_risk_cap/`

Planned report: `agents/codex/results/overlap_risk_cap.md`
