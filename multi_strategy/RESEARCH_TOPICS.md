# Research topics for intraday NQ strategies with more trades

Started 2026-10-11. The goal: intraday strategies (8:30–15:15 CT, flat by the close)
that trade more often than once a day, so the edge can be confirmed sooner, and that
are built on published research.

## First, what "the edge shows quicker" really needs

- The confidence in an edge grows with **√(independent trades) × (average trade ÷
  spread of trades)**. Going from 1 to 4 trades a day only helps if the extra trades
  are not just the same bet repeated: four entries in one trend day count as roughly
  one. Count trades and *days*.
- More trades means smaller moves per trade, so **costs take a larger share**. NQ
  costs here are $7.25 per round trip (0.36 point) before slippage. A strategy averaging
  3 points a trade loses about a quarter of its profit to that, plus slippage.
  Always test with costs and 1 tick of slippage on stop and market fills.
- It also helps the funded phase: more small, frequent wins mean more $250 qualifying
  days and an easier 50% consistency rule.
- Already tested and dropped in this repo (do not repeat as is): VWAP fade, plain
  30-minute opening-range breakout (PF 1.0–1.05), lunchtime RSI(2), prior-day
  high/low, late-day momentum at 14:00 (fragile), VWAP pullback ADX (PF 0.87), Vault
  Break short side.

## Topics, in the order to test them

Each has the papers to read, what to test on NQ with the 1-minute data, and why it
might fit the plan.

### 1. VWAP trend following, all day (many trades a day)
- **Zarattini & Aziz, "Volume Weighted Average Price (VWAP): The Holy Grail for Day
  Trading Systems"**, SSRN 4631351 (2023, revised 2025). Long while price is above
  VWAP, short below, 1-minute bars, flat at the close; tested on QQQ 2018–2023.
- **Caution:** independent QuantConnect replications got much weaker results. The
  repo's earlier VWAP strategies were pullback and fade versions, not this
  always-in-trend version.
- **Test:** VWAP from 8:30, positions flipped at 1/5/15-minute closes, with a buffer
  (e.g. price must be k × ATR beyond VWAP) to cut the whipsaw trades. Report trades a
  day, average trade after costs, and by year. A thousand-plus trades a year gives a
  verdict within one test.
- **Fit:** trend-following like Vault Break, so expect some correlation (both make
  money on trend days).

### 2. Noise-area momentum, the paper's full version (both sides, trailing exits)
- **Zarattini, Aziz & Barbon, "Beat the Market: An Effective Intraday Momentum
  Strategy for S&P500 ETF (SPY)"** (2024–25; Swiss Finance Institute RP 24-97). Vault
  Break is a long-only cut of this. The paper uses a band built from the average
  absolute move from the open at each time of day (not a flat 30% ATR), checks every
  30 minutes, exits on a VWAP/band trailing stop and can re-enter or reverse during the
  day.
- **Test:** the time-of-day noise band and the trailing exit with re-entries on NQ.
  Vault Break's short side lost from 2023, so judge the short side separately.
- **Fit:** an upgrade path for Vault Break rather than a new strategy, but it adds
  trades.

### 3. Intraday reversal after big moves, conditioned on volatility (low correlation)
- **Grant, Wolf & Yu (2005), "Intraday price reversals in the US stock index futures
  market: A 15-year study"**, Journal of Banking & Finance: large opening moves in S&P
  futures reverse during the day, but costs take much of it.
- **Fung, Mok & Lam (2000)**, JBF: reversals in S&P 500 and Hang Seng futures grow
  with the size of the initial move.
- **Nagel (2012), "Evaporating Liquidity"**, Review of Financial Studies: short-term
  reversal profits are liquidity provision and are much larger when the VIX is high.
- **Della Corte, Kosowski & Wang, "Market Closure and Short-Term Reversal"**, SSRN
  2730304: reversals also hold in equity-index futures.
- **Test:** fade 15–60-minute moves larger than x × the normal move for that time of
  day, only when recent volatility is high, small target, time stop. The earlier
  VWAP-fade test had no volatility condition and no move-size threshold.
- **Fit:** the best candidate for **negative correlation** with Vault Break and
  Overnight Bias (it profits when they get whipsawed).

### 4. Round numbers and order clustering (several events a day)
- **Osler (2003), "Currency Orders and Exchange Rate Dynamics: An Explanation for the
  Predictive Success of Technical Analysis"**, Journal of Finance (NY Fed Staff Report
  125). Take-profit orders cluster at round numbers, so trends tend to stall there.
  Stop-loss orders cluster just beyond them, so once a round number breaks, price runs.
- **Test:** NQ 100- and 50-point levels. (a) Fade the first touch of a level, with a
  stop a few points through it. (b) Trade the break once price closes x points through
  it. NQ crosses one or more 100-point levels most days, so there are hundreds of
  events a year.
- **Fit:** different trigger from everything in the plan. The evidence is from FX
  order books, so it is unproven on futures; that is the point of testing it.

### 5. Intraday momentum by time of day and conditions
- **Gao, Han, Li & Zhou (2018), "Market Intraday Momentum"**, Journal of Financial
  Economics: the first half-hour predicts the last half-hour.
- **Baltussen, Da, Lammers & Martens (2021), "Hedging Demand and Market Intraday
  Momentum"**, JFE (SSRN 3760365): over 60 futures; the momentum comes from short-gamma
  hedging by option dealers and leveraged ETFs.
- **Barbon, Beckmeyer, Buraschi & Moerke, "Liquidity Provision to Leveraged ETFs and
  Equity Options Rebalancing Flows"**, SSRN 3925725: end-of-day momentum when dealer
  gamma is negative, reversal when positive. The leveraged-ETF effect has shrunk.
- **Li, Sakkas & Urquhart (2022), "Intraday Time Series Momentum: Global Evidence and
  Links to Market Characteristics"**, Journal of Financial Markets (SSRN 3460965):
  stronger when liquidity is low and volatility high.
- **Heston, Korajczyk & Sadka (2010), "Intraday Patterns in the Cross-Section of Stock
  Returns"**, Journal of Finance: a half-hour's return repeats at the same half-hour
  on later days.
- **Note:** the plain 14:00 version was tested here and was fragile. What is new is
  the **condition**: dealer gamma (needs outside data, e.g. a daily gamma-exposure
  series) or high volatility. One trade a day, so low priority given the goal.
  Heston–Korajczyk–Sadka gives up to 13 half-hour signals a day, but it is a
  cross-section-of-stocks result and may be weak on one index.

### 6. Order-flow imbalance (needs tick data)
- **Cont, Kukanov & Stoikov (2014), "The Price Impact of Order Book Events"**,
  Journal of Financial Econometrics: price changes over seconds to minutes follow
  best-bid/ask order-flow imbalance.
- **Test** only with tick or bid/ask-volume data (MultiCharts can build volume delta
  from tick data). Horizons are short, costs are large relative to the moves, and it is
  hard to run as a bar-based signal. Last on the list.

## How to search SSRN yourself

- Search: https://papers.ssrn.com/sol3/results.cfm (sort by downloads, and filter
  2015 onwards).
- Useful phrases: "intraday momentum futures", "intraday return predictability",
  "intraday reversal index futures", "time-of-day seasonality returns", "noise
  area", "VWAP trading strategy", "gamma exposure intraday", "leveraged ETF rebalancing",
  "order flow imbalance futures", "round number clustering", "liquidity provision
  short-term reversal volatility".
- Also look at Quantpedia (strategy summaries with paper links) and the Concretum Group
  site (Zarattini's papers and code).
- Filter papers with these questions:
  - Is it on futures or index ETFs, intraday, with costs?
  - Does it hold after its publication date?
  - Is there an independent replication?
  - Is the explanation a structural flow (hedging, rebalancing, liquidity), not just a
    pattern?

## Results on NQ (2026-10-11, `analysis/intraday_research.py`)

1-minute data from 2018 to 9 Oct 2026, regular session (flat at the 15:00 close), per
NQ, after $7.25 costs **and 1 tick of slippage on every market and stop fill**.
"Sharpe" is the annualized daily Sharpe ratio (Vault Break 1.46, Overnight Bias 1.32
on the same basis).

| Topic | Best setting | Trades/day | Avg trade | PF | Years + | Verdict |
|---|---|---|---|---|---|---|
| 1. VWAP trend (Zarattini & Aziz) | 30-min checks, buffer 5% ATR | 2.0 | $51 | 1.08 | 7 of 9 | **No** (2023–26 ≈ $0) |
| 1. VWAP trend, as in the paper | 1-min checks, no buffer | 16 | −$1 | 0.99 | 4 of 9 | **No**: +$6 a trade before costs, $17 of costs |
| 2. Noise area, full paper version | 30-min checks, both sides, VWAP trail | 0.79 | $133 | 1.26 | 8 of 9 | **Real edge**, but no better than VB in the plan |
| 2. Same, long only | | 0.41 | $167 | 1.39 | 9 of 9 | Real edge; optional 1 MNQ |
| 3. Big-move reversal (any setting) | 30-min move > 3x normal, high-vol days | 0.6 | −$7 | 0.99 | 4 of 9 | **No**: every setting loses |
| 4. Round numbers, fade | | 2–3.4 | −$39 to −$53 | 0.59–0.85 | 0–1 | **No** |
| 4. Round numbers, break | | 3–4.3 | −$16 to −$32 | 0.89–0.95 | 0–2 | **No** |

**What this says about NQ:** on these data and these rules, every mean-reversion idea
lost money and every high-frequency idea was eaten by costs. The edges that survive
hold a trend for hours (Vault Break, Overnight Bias, noise area). The VWAP paper's
QQQ result had almost no costs. On NQ the 1-minute version makes about 6 dollars a
trade before costs, against $17 of costs (commission plus 2 ticks of slippage).

**Noise area in detail** (the paper's version: band from the average absolute move from
the open at each minute, 14-day lookback, checks every 30 minutes from 9:00, trailing
stop at max(band, VWAP), reversals allowed):
- Robust: profit factor 1.23–1.31 for lookback 10/14/20, first check 9:00/9:30, last
  entry 14:00/14:30.
- Short side weak and erratic: profit factor 1.16, with −$177 a trade in 2026 and −$74
  in 2019. Long side: profit factor 1.39, positive every year (2020 only +$5).
- Daily correlation 0.25 with Vault Break (0.39 long only), 0.31 with Overnight Bias.
- Daily Sharpe 1.0, lower than Vault Break's 1.46: fewer, larger wins (39% win rate),
  so the funded consistency rule bites harder.

**In the funded plan** (expected payouts per PA, `analysis/funded_sim.py`):

| Plan | Within 1 year | Within 2 years | Blown (1 yr) |
|---|---|---|---|
| Balanced: VB 3, ONB $300, OND $500 | $5,919 | $6,823 | 45% |
| VB 2 + noise area long only 1 MNQ + ONB $300 + OND $500 | $5,991 | $8,008 | 36% |
| VB 2 + noise area both sides 1 MNQ + ONB + OND | $5,215 | $7,086 | 48% |
| Balanced + noise area both sides 1 MNQ | $5,094 | $6,286 | 51% |
| Noise area both sides 3 MNQ instead of VB | $2,002 | $3,749 | 72% |

Swapping one Vault Break contract for 1 MNQ of long-only noise area is about equal
within 1 year and better within 2 years, but the gain is within the noise of these
estimates. Adding the both-sides version lowers payouts.

## Results of the first three tests (2026-10-11, `analysis/intraday_research.py`)

All tests are per NQ, with $7.25 costs plus 1 tick (0.25 point) of slippage on every
market or stop fill. Data: the 1-minute bars, 2018–2026.

### 1. "Beat the Market" full version: better per trade, worse for Apex

| | Trades | Win | Avg | PF | Years + |
|---|---|---|---|---|---|
| Vault Break (MultiCharts list, + slippage) | 1,743 | 66% | $92 | 1.26 | 9/9 |
| Paper version, long + short, trailing exit | 2,068 | 40% | $120 | 1.25 | 8/9 |
| … longs only | 1,012 | 44% | $155 | 1.38 | 9/9 |
| … shorts only | 1,056 | 37% | $87 | 1.16 | 7/9 (2023–26: $53) |
| Long only, trailing exit + 75-pt stop | 1,036 | 43% | $174 | 1.45 | 9/9 |
| Long only, Vault Break's 40/75 exits | 1,654 | 64% | $74 | 1.19 | 8/9 |

Daily correlation with Vault Break: 0.38. **In the accounts it loses**, with 1 tick of
slippage on every strategy:

| Plan | Funded payouts, 1 year | Blown | Challenge pass |
|---|---|---|---|
| Balanced: VB 3, ONB $300, OND $500 | **$5,387** | 48% | VB 8 + ONB $1,100: **42.8%** |
| Trailing version 2 instead of VB | $4,100 | 39% | (8 MNQ instead of VB) 34.7% |
| VB 2 + trailing version 1 | $5,208 | 41% | VB 6 + trailing 4: 40.2% |

The trailing exit wins bigger but less often (43%). The Apex rules punish that: fewer
$250 days, big days that break the 50% consistency rule, and runs of losses against a
fixed $2,000 cushion. **For prop accounts, a high win rate and smooth days matter more
than profit factor.** Vault Break's fixed 40-point target stays.

### 2. Fading large intraday moves: loses everywhere

Every version lost money: 30- or 60-minute moves above 2–3x normal, all days, high-ATR
days, low-ATR days, and the VIX regimes (PF 0.71–0.95). The only positive cell was the
VIX "long vol" regime, with 94–175 trades, which is noise. NQ keeps moving after large
intraday moves (momentum), which is consistent with Vault Break working.

### 3. Round numbers: a real but tiny effect, the opposite of the fade idea

There are about 4,400 first touches each of 100- and 50-point levels, against
8,800–8,900 for each pair of non-round "placebo" levels (12/88, 25/75, 37/63).

| Level | Reverses 10 pts first | Moves 30 min later (pts, in the approach direction) |
|---|---|---|
| 100s | 48.9% | +1.1 |
| 50s | 49.1% | +0.6 |
| Placebo | 51.7–52.0% | +0.2 to +0.5 |

Price goes *through* round levels slightly more often than through other levels
(about 3 points, about 3 standard errors, in 7 of 9 years). There is no extra follow-through
after a 5-point close through the level. Worth about 0.4 point per trade, below the
costs, so it is not a strategy. At most it is a small tilt: do not place Vault Break's
target just short of a round number.

### Where this leaves the list
- Topics 2–4 are done. None beats the current funded plan.
- Lesson for the funded search: look for **high-win-rate, many-small-wins** edges, the
  same shape as Vault Break (fixed target closer than the stop) and unlike trend
  followers. Next candidates in that shape:
  - Vault Break's entry at other times or on other bands (e.g. a short-side version
    with a 40/75 bracket gated to downtrend days)
  - an Overnight Drift-style fixed-time trade with a small target
