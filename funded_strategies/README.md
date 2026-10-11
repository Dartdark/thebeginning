# Funded strategies (Apex 50K Performance Account)

Strategies built for one job: **taking the most money out of a funded account**. The
challenge strategies in `../apex_strategies/` are only the benchmark here. They were
tuned to pass, not to earn.

## The goal, in numbers

A 50K Performance Account (PA) pays at most 6 payouts, capped at $1,500 / $1,500 / $2,000 /
$2,500 / $2,500 / $3,000 = **$13,000**, then closes. Each payout needs, since the last one:
- 5 days with at least $250 profit
- 50% consistency: the best day is under 50% of the profit
- a balance of at least $52,600

Once the drawdown locks at $50,100, every payout cycle is the same game: make the cap
before losing the $2,000 cushion. Full rules and assumptions are in
`../analysis/funded_sim.py`.

**Score for a funded strategy:** expected payouts per PA within 1 year (also 2 years),
from PAs started on every real day. Costs are $7.25 per NQ plus 1 tick of slippage on
every market or stop fill.

## What a funded strategy should look like (from the tests so far)

- **A high win rate with small, steady winning days.** Each $250 day counts, and no
  single day may dominate (consistency rule). A trend-follower that wins 43% with big
  winners did worse than Vault Break's 66% fixed-target trade, even though its profit
  factor was higher (1.45 vs 1.26). See `../multi_strategy/RESEARCH_TOPICS.md`.
- **Edge per unit of risk (Sharpe), not profit per trade.** Smaller sizes always survive
  longer; a better edge is what lets you size up.
- **Low correlation** with the other funded strategies, so the bad days don't stack
  against the fixed $2,000 cushion.
- **Many independent trades**, so the edge shows in a few weeks rather than a year.
- **Flat by 15:59 CT every day** (Apex rule). Overnight-session trades that close
  before then are fine.

## Roster

| Strategy | File | Status | Notes |
|---|---|---|---|
| Overnight Drift | `NQ_Overnight_Drift.txt` | Python-tested; needs a MultiCharts backtest | Long midnight to 3:00 CT after a down session. PF 1.25, 8/9 years positive, flat 2023–24. Correlation about 0 with everything else |

## Benchmark (to beat)

The interim plan in `FUNDED_PLAN.md` runs the Apex strategies at small sizes plus Overnight
Drift (Vault Break 3 MNQ, Overnight Bias $300, Overnight Drift $500). It expects
**about $5,400** in payouts within 1 year with 1 tick of slippage ($5,900 without), with
45–48% of PAs blown within the year. A new funded strategy, or a funded set, has to beat
that on the score above.

## Tested and not good enough for funded

- Vault Break with the "Beat the Market" trailing exit: $4,100 vs the $5,400 benchmark
- Fading large intraday moves: loses money
- Round-number levels: too small to trade

See `../multi_strategy/RESEARCH_TOPICS.md` for details.
