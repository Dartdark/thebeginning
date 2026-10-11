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

## Test bench

`analysis/funded_lab.py` takes any trade lists, adds costs plus 1 tick of slippage, and
scores a plan (sizes per strategy) on expected PA payouts:
`lab.score({"VB": 3, "OND": ("risk", 500)})`. Candidate generators are in
`analysis/funded_candidates.py`. The grid (`analysis/grid24.py`) now loads any
instrument's 1-minute exports: `Grid24("data/GC_1min_20*.csv", night_pattern="")`.

## First build round (2026-10-11): NQ only

| Plan (payouts within 1 year, with slippage) | Expected | Blown |
|---|---|---|
| **Benchmark: VB 3, ONB $300, OND $500** | **$5,387** | 48% |
| VB 3 + ONB $300 (no OND) | $4,401 | 50% |
| VB 3 alone | $2,440 | 45% |
| ONB $300 alone | $2,020 | 17% |
| OND $500 alone | $253 | 37% |
| VB entry, 40/40 bracket, 4 MNQ + OND $500 | $3,626 | 55% |
| VB entry, 40/50 bracket, 4 MNQ + OND $500 | $3,176 | 63% |
| VB entry, 30/40 or 25/50 bracket + OND $500 | $2,284–2,858 | 47–66% |

- **Small targets do not help.** Costs and slippage take the edge: Overnight Drift with a
  0.05-ATR target wins 75% but makes about $10 a trade, and Vault Break's entry with a
  15-point target makes $20–25.
- **The payouts come from combining uncorrelated edges.** Vault Break and Overnight Bias
  each make about $2,000–2,400 alone, and $4,400 together. Overnight Drift adds about
  $1,000 on top, while alone it makes only $250.
- **So the best route to new funded strategies is new uncorrelated edges, most likely on
  other markets** (gold, crude, ES), not new exits on the same NQ entries. Intraday
  momentum is documented across 60+ futures (Baltussen et al. 2021), and the noise-band
  breakout across markets (Zarattini et al.), so the first test on GC/CL/ES is the
  momentum breakout and the overnight-bias idea, each on its own market.

## ES round (2026-10-11): no edge worth adding

`data/ES_1min_<year>.csv` covers 2017 to 9 Oct 2026, full 24-hour days. Results are per
ES contract for 2018–2026, with a $5 round trip plus 1 tick ($12.50) of slippage per
market or stop fill.

| Rules on ES | Trades | Win | Avg | PF | Years + |
|---|---|---|---|---|---|
| Noise breakout (Vault Break rules, target/stop scaled by ATR) | 1,720 | 62% | $3 | 1.01 | 6/9 |
| Overnight Bias rules | 1,077 | 46% | $56 | 1.13 | 6/9 |
| Overnight Drift rules | 1,021 | 50% | $6 | 1.03 | 4/9 |
| "Beat the Market" (the paper's own SPY rules), long + short | 1,967 | 38% | $35 | 1.12 | 7/9 |

The same ideas that work on NQ are much weaker on ES. Even the paper written for SPY
makes only $5 a trade from 2023 on. ES would also be highly correlated with NQ, so it
adds little diversification. ES is parked.

**GC and CL:** the MultiCharts data feed only has about a week of 1-minute history for
them, so they cannot be tested for now. The search continues with NQ and ES data.

## NQ–ES spread (2026-10-11): too thin after costs

Long NQ / short beta-weighted ES (or the reverse), using spread moves from the 8:30 open
measured against their normal size at that time of day:
- **Fading large spread moves loses** at every threshold and horizon (−$1 to −$34
  per NQ of notional, gross). Spread moves keep going.
- **Following them**, first signal of the day, held to 15:00: +$79 gross per NQ of
  notional at 2x normal (752 days, t = 2.4, 7/9 years positive). A round trip in both legs
  costs about $60 (NQ $7.25 + 1.5 ES x $5 + 1 tick per fill on both legs), so about $20 is
  left. Not worth trading.

## Papers reviewed for funded strategies

- **Bhatti (2026), "A Regime-Filtered Intraday Trading Framework for Gold", SSRN
  6650958.** The results (PF 1.76, Sharpe 3.99) are **not a backtest**: section 6.1 says
  the 247 trades were drawn from outcome probabilities the author assumed. The rules
  are precise, so we coded them (`vwap_ema_pullback`):
  - 200-EMA regime
  - pullback to the 50 EMA with a pin-bar or engulfing candle, above VWAP
  - stop 0.5 ATR beyond the signal bar, 3R target, close-only 50-EMA trailing stop

  On NQ, 15-minute bars, 2018–2026: 596 trades, 30% winners, PF 0.94, losing since 2023
  (longs PF 1.07, shorts 0.82). Its real test is on gold data (pending).

- **Kakushadze & Serur (2018), "151 Trading Strategies", SSRN 3247865** (in the repo as
  `ssrn-3247865.pdf`). A 361-page catalogue of strategy formulas across asset classes,
  with no backtests. The parts that apply to NQ/ES day trading, tested here
  (2018–2026, per contract, after costs):

  | Idea | Result |
  |---|---|
  | IBS (where yesterday closed in its range): buy next day's session | Not monotonic and not significant (NQ t = 1.4 after IBS < 0.2, −1.1 for 0.5–0.8; ES flat) |
  | IBS < 0.2 then long midnight to 3:00 | NQ t = 1.8; weaker than Overnight Drift's "down day" condition (t = 2.5) |
  | Pivot points (side of the pivot at 9:00, exit at R1/S1 or 15:00) | Loses (NQ −$74, ES −$74 net) |

  Other relevant entries were already tested in this repo or need data or infrastructure
  we lack: futures trend/contrarian (cross-market), volatility targeting, VIX basis,
  ETF arbitrage (high-frequency), leveraged-ETF rebalancing (late-day momentum, fragile).

- **Citations of "151 Trading Strategies"** (1,890 references). Of the 147 on intraday
  trading, overnight returns, futures, announcements or technical rules, the ones that
  fit NQ/ES day trading were tested (`analysis/event_days.py`, `event_days_test.py`):

  | Paper | Test on NQ / ES, 2018–2026, per contract after costs | Verdict |
  |---|---|---|
  | Lucca & Moench (2015), pre-FOMC drift | Long 8:30 to 12:55 CT on FOMC days: NQ −$12, ES −$44 (69 days). From midnight: NQ +$255, t = 1.0 | **Gone** since 2018 (as later studies also report) |
  | Savor & Wilson (2013), announcement-day premium | Long on 8:30 ET release days: NQ +$93 vs +$49 on normal days, t = 0.4; ES −$41 | No premium |
  | Reaction to 8:30 ET releases (7:30 CT) | **Fading the 7:30–8:00 CT reaction from 8:00 to 8:30 CT: NQ +$63 net, t = 2.9, 485 days, 6/9 years** (spike above 2x normal); +$84, t = 2.3 above 3x. ES +$6, t = 1.5 | **Candidate**: small, NQ only, and found after trying about 24 variants |
  | Brock et al. (1992), Sullivan–Timmermann–White (1999), Dempster & Jones (2002), Lo et al. (2000) | Technical rules on index data; the later papers find the edge disappears after correcting for data-snooping | Supports our caution with technical rules |
  | Osler (2000, 2003) | Round numbers, already tested | Too small |
  | Shum et al. (2016), leveraged-ETF rebalancing | Late-day momentum, already tested | Fragile |
  | Index arbitrage papers (Yadav & Pope, Richie et al., Marshall et al.) | Futures vs cash, high-frequency | Not for us |

  FOMC dates are in `event_days.FOMC_DATES`. Each was confirmed against the 13:00 CT
  volatility spike: median 3.6x normal on NQ, 4.0x on ES.

## Tested and not good enough for funded

- Vault Break with the "Beat the Market" trailing exit: $4,100 vs the $5,400 benchmark
- Fading large intraday moves: loses money
- Round-number levels: too small to trade

See `../multi_strategy/RESEARCH_TOPICS.md` for details.
