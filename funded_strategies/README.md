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
| Overnight Drift | `NQ_Overnight_Drift.txt` | **MultiCharts-confirmed** (`Backtesting Strategy Performance Report OND v1.xlsx`), holiday fix added | Long midnight to 3:00 CT after a down session. PF 1.25, 8/9 years positive, flat 2023–24. Correlation about 0 with everything else |
| **Expiration Open Short** | `NQ_Expiration_Open_Short.txt` | **MultiCharts-confirmed** (`Backtesting Strategy Performance Report EOS v1.xlsx`): same 105 trades, entries and P&L as Python | Short at the 8:30 open on monthly options expiration day, out at 10:00, stop 0.3 ATR. 105 trades, 59% winners, $474 a trade, PF 1.93, 8/9 years positive. **Benchmark + it at $500 risk: $6,516 vs $5,387** |

## Current funded set (all MultiCharts-confirmed, 2026-10-12)

| Strategy | Chart | Funded inputs |
|---|---|---|
| Vault Break (Apex strategy) | 30 min MNQ | `NumContracts` 3 |
| Overnight Bias (Apex strategy) | 15 min MNQ | `RiskPerTrade` 300 |
| Overnight Drift | 5 min MNQ | `RiskPerTrade` 500 |
| Expiration Open Short | 5 min MNQ | `RiskPerTrade` 500 |

Scored with all four MultiCharts trade lists plus 1 tick of slippage:

| | Expected payouts, 1 year | Expected payouts, 2 years | Blown within a year |
|---|---|---|---|
| Expected | **$6,495** | $7,280 | 42% |
| Without Expiration Open Short | $5,340 | $6,448 | 48% |

**Overnight Drift check:** the MultiCharts report has the same entry and P&L on all
1,037 days it shares with Python. Its extra trades were on holidays without a midnight
bar (25 Dec, 1 Jan, where it bought the 17:00 reopen and held to 3:00) and one data gap
(5 Nov 2018, 05:25). Fixed with `MaxEntryDelay` (entries only until 00:30). With the fix:
1,039 trades, 54% winners, $71 a trade, PF 1.22, 7/9 years positive.

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

## Release-fade and overnight-positioning round (2026-10-12)

**Fading the reaction to 7:30 CT reports** (from the citation review):
- **The detected days are real release days.** They fall mostly on Thursdays (jobless
  claims) and Fridays (jobs report), and 79 of the 102 first-Friday jobs reports were
  caught.
- **Without a stop**, the trade looks good: jobs-report Fridays make $152 net (t = 2.5).
- **With a stop** (needed live in that window):

  | Version | Avg trade | Years positive |
  |---|---|---|
  | All release days | $11–15 | 3/9 |
  | Jobs-report Fridays | $49–104 | 5/9, losing in 2018–22 |

- **In the funded bench**, adding it lowers payouts: benchmark + REL $4,149–4,415,
  + NFP $4,023–4,602, vs $5,387. **Dropped.**

**Overnight-positioning family** (`analysis/funded_candidates.py`: `on_context`,
`on_signals`):

| Idea | Trades | Win | Avg | PF | t | Years + |
|---|---|---|---|---|---|---|
| **Break of the overnight high/low** (first close beyond it 8:45–12:00), hold to 14:30, stop 0.15 ATR | 2,075 | 30% | $99 | 1.18 | 2.5 | 7/9 |
| … stop 0.2 ATR | 2,075 | 37% | $98 | 1.15 | 2.3 | 7/9 |
| … middle-third days only (the days Overnight Bias skips) | 677 | 30–36% | $10–52 | 1.02–1.09 | ≤ 0.8 | 4–6/9 |
| Fade the 8:30–8:45 range break on middle-third days | 722 | 36–46% | −$34 to $66 | 0.94–1.12 | ≤ 1.2 | 3–6/9 |
| Follow the same break (control) | 722 | 28–47% | −$108 to −$31 | 0.85–0.94 | < 0 | 1–3/9 |

The overnight-range breakout has a real edge (t = 2.5, stable in both periods), but
**in the funded bench it cuts payouts sharply**:

| Plan | Expected payouts within 1 year |
|---|---|
| Benchmark | $5,387 |
| Benchmark + breakout ($200–400 risk) | $1,558–3,097 |
| Benchmark + middle-days version ($200–400 risk) | $2,237–4,329 |
| Breakout + Overnight Drift alone | $700–1,030 |

It trades every day with a 30–37% win rate and correlates 0.53–0.59 with Overnight
Bias.

**Lesson (now confirmed four times):** under the payout rules an edge is not enough. A
funded strategy needs a decent win rate, has to sit out a lot of days, and must be nearly
uncorrelated with the others. Every-day, low-win-rate trend trades destroy payouts even
with t = 2.5.

## Quiet-day and unused-hours round (2026-10-12)

Ideas were pre-filtered by the funded rules (win rate, sit out days, uncorrelated, fixed
risk). `funded_candidates.window_signals` builds fixed-bracket trades in hours no strategy
uses:
- midday 11:00–13:00 or 12:00–14:00 CT
- pre-market 3:00–7:00 or 5:00–7:15 CT

Each follows or fades the preceding move. The test covers all days, and "quiet" days
(no Vault Break or Overnight Bias entry yet, known in real time). About 140 variants in
total (`analysis/window_trades_test.py`).

- **Nothing is significant.** The best is t = 1.4, while about 2.5 would be expected by
  luck alone from 140 tries.
- **The one sensible pattern:** on quiet days, fading the 8:30–12:00 move from 12:00 to
  14:00 makes +$30–53 a trade, with a 66% win rate on the 0.15/0.08 ATR bracket.
  Following the move on those same days loses (t = −3.5). Days without a trend drift
  back after noon.
- **Funded check (QMF):** correlation with VB, ONB and OND is −0.01, 0.00 and 0.04, as
  intended. But it does not raise payouts:

  | Plan | Expected payouts within 1 year |
  |---|---|
  | Benchmark | $5,387 |
  | Benchmark + QMF | $3,732–5,153 |
  | Best re-sized plan with QMF (VB 2, ONB $300, OND $500, QMF $150) | $5,363 |

  The edge is too thin (t = 1.4) to pay for the risk it adds.

**Where the funded search stands:** five rounds of NQ/ES candidates (new exits, ES, the
NQ–ES spread, event days, the overnight-positioning family, quiet days and unused hours)
have not beaten the benchmark. A new funded strategy needs an edge about as strong as
Vault Break's or Overnight Bias's (t of about 4 or more on its own), not just low
correlation.

## Calendar-flow round (2026-10-12): first funded strategy that beats the benchmark

Code: `analysis/calendar_flows.py` (calendar flags) and `analysis/calendar_flows_test.py`.
Results are NQ, 8:30–15:00 long, per contract after costs (2018–2026), with about 40
comparisons:

| Effect | Result |
|---|---|
| Turn of month: first 3 trading days | +$376, t = 2.0, 7/9 years (ES +$187, t = 2.1); with a 0.3-ATR stop t = 3.7, 9/9 years, but $188 in 2018–22 vs $1,009 from 2023 |
| Last trading day; the 3 days before it | Not significant |
| Month-end rebalancing (fade the month-to-date move over the last 3 days) | NQ +$188 to +$338, t ≤ 1.7; ES nothing |
| Expiration week / week after / Monday after | Not significant |
| **Options expiration day** | **NQ −$639 long, t = −2.0, 1/9 years positive**; ES weaker in the same direction |

**Expiration day, examined further (NQ, short):**
- **By time of day:** 8:30–10:00 +$529 gross (t = 2.7); 10:00–12:00 −$97;
  12:00–15:00 +$190.
- **All-day short fades:** 2025 +$16, 2026 −$530. **The 8:30–10:00 window holds:**
  2025 +$1,302, 2026 +$132.
- **Placebo:** shorting other Fridays loses money (−$126).
- **Reason:** monthly SPX and NDX options settle on Friday's opening prices, so hedges tied
  to them come off at the open.

**Funded bench (1 year):**

| Plan | Expected | Blown |
|---|---|---|
| Benchmark | $5,387 | 48% |
| + Expiration short 8:30–10:00, $300 risk | $6,207 | 43% |
| **+ Expiration short 8:30–10:00, $500 risk** | **$6,516** | **41%** |
| + Expiration short all day, $500 risk | $6,371 | 42% |
| + Expiration short $500 + turn of month $150 | $6,567 | 41% |
| + Turn of month alone ($150–400 risk) | $3,840–5,648 | 46–61% |

Over 2 years: $7,320 vs $6,467. The turn-of-month long adds almost nothing on top, so it
is parked; it is a watch item because it has been much stronger since 2023.

**MultiCharts confirmation (2026-10-12):** `Backtesting Strategy Performance Report EOS v1.xlsx`
(5-minute @NQ, Bar Magnifier 1 minute, RiskPerTrade 0, NumContracts 1, from 19 Jan 2018)
matches the Python test:
- the same 105 trades on the same days
- the same entry price on 100%
- P&L within $25 on 100% (the exit price differs on 21%, where MultiCharts rounds the stop
  to the tick)

After $7.25 plus 1 tick per fill: 59% winners, $474 a trade, PF 1.93, 8/9 years positive.
With the MultiCharts list in the funded bench, benchmark + it at $500 = **$6,516**
($7,320 within 2 years).

**Caveats:**
- Only 105 trades (12 a year), t = 2.6, found among about 40 comparisons.
- The calendar needs the exchange holiday list: Good Friday and Juneteenth move expiration
  to Thursday. The known ones are hard-coded.

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
