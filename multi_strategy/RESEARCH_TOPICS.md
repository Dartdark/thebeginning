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
