# Multi-strategy plan for Apex 50K

Started 2026-10-10. Goal: more strategies that, together with NQ VWAP Momentum v3
(`final_v3/`), raise the chance of getting a funded Apex 50K account.

## Short version

- **Run each strategy in its own Apex account, and start the accounts on the same day.**
  The new strategies pass or fail almost independently of v3. With three accounts
  (v3, Vault Break, Opening Drive), **at least one passes 66% of the time (70% when the
  filter line is green, 73% for starts in 2023–2026)**. With v3 alone it is 33%.
- Putting all the strategies in **one** account does not raise its pass rate
  (about 35–37%, the same as v3 alone), even though the combined daily Sharpe ratio is
  almost twice as high. See "Why not one account" below.
- The cost per funded account stays about the same (about 3 fees per pass). What
  changes is that each round of attempts is far more likely to produce a funded
  account, the bad years are much less bad (worst year 30% instead of 5%), and the
  funded accounts end up running different strategies.
- The new strategies are tested in Python on the 1-minute exports. **Backtest each
  one in MultiCharts before trading it** (see "Next steps").

## The strategies

None of the new ones reuses v3's logic (no VWAP pullback, no momentum trigger), and
each trades mostly at a different time of day.

| | v3 (existing) | Vault Break (yours) | Opening Drive (new) | Gap Fill (new, experimental) |
|---|---|---|---|---|
| File | `final_v3/` | `NQ_Vault_Break.txt` | `NQ_Opening_Drive.txt` | `NQ_Gap_Fill.txt` |
| Chart | 5 min | 30 min, 24-hour session | 5 min | 5 min, with pre-open |
| Idea | Pullback in a VWAP trend | Long breakout above the open + 30% of ATR, above VWAP | Follow the first 30 minutes' direction | Fade the overnight gap back to yesterday's close |
| Window (CT) | 9:50–14:55 | 10:00–14:30 | 9:00–11:00 | 8:30–10:00 |
| Side | Both | Long only | Both | Both |
| Stop / target | 80 / 40–50 pts | 75 / 40 pts ($1,500 / $800) | 50 pts / none, out at 11:00 | Gap size / gap filled, out at 10:00 |
| Trades per day | 1.5 | 0.7 | 0.6 | 0.6 |

**Opening Drive rule:** at the close of the 9:00 CT bar, if price is at least 0.2% above
the first regular-session open, buy; at least 0.2% below, sell short. Stop 50 points,
no target, out at the close of the 11:00 bar. One trade a day.

**Vault Break** is written exactly to your spec (midnight open and midnight VWAP,
15-day ATR, 30%, longs only, 10:00–14:30, 3 trades max, $800 / $1,500, flat 14:30).
Because the 1-minute exports start at 08:00 CT, the Python test anchors the open and
VWAP at 08:00. Even so, 2021–2026 came out very close to the course's vaultbreak list:
1,225 trades vs 1,334, win rate 66% vs 67%, average $97 vs $98. The MultiCharts version
uses midnight, as you specified.

## Backtest results (Python, 2 Jan 2018 – 9 Oct 2026, per NQ, after $7.25 costs)

| | Trades | Win rate | Avg trade | Profit factor | Avg 2018–22 | Avg 2023–26 |
|---|---|---|---|---|---|---|
| v3 (MultiCharts list) | 3,497 | 63% | $61 | 1.14 | $81 | $36 |
| Vault Break | 1,656 | 64% | $75 | 1.21 | $59 | $90 |
| Opening Drive | 1,352 | 41% | $119 | 1.23 | $92 | $157 |
| Gap Fill ($1,000 risk a trade) | 1,273 | 54% | $48 | 1.14 | $76 | $12 |

**Correlation of daily P&L:**

| | v3 | Vault Break | Opening Drive | Gap Fill |
|---|---|---|---|---|
| v3 | 1 | 0.30 | 0.09 | −0.02 |
| Vault Break | | 1 | 0.08 | −0.04 |
| Opening Drive | | | 1 | −0.04 |

Vault Break is the most correlated with v3 (both are long-biased trend trades above
VWAP), but even 0.30 leaves a lot of independence.

## Apex 50K pass rates

Challenges started on every real trading day and run on the real days that followed
(the realistic method from `start_timing.py`), with the trades of each account laid
out minute by minute on the 1-minute bars.

**Per account:**

| Account | Any start day | Same trades, no edge | Line green | Green 3 days in a row | Starts 2023–26 | Worst start year |
|---|---|---|---|---|---|---|
| A: v3, 10 MNQ | 33% | 28% | 40% | 41% | 38% | 5% (2019) |
| B: Vault Break, 12 MNQ | 34% | 28% | 39% | 39% | 39% | 10% (2019) |
| C: Opening Drive, 10 MNQ | 33% | 26% | 31% | 30% | 37% | 21% (2019) |
| D: Gap Fill, $1,000 risk | 21% | 17% | 21% | 20% | 15% | 11% |

"No edge" is the same trade list with its average profit removed. The difference shows
how much of each pass rate is the strategy and how much is the challenge's structure.

**Accounts started on the same day; chance that at least one passes:**

| Accounts | Any day | Line green | Starts 2023–26 | Worst start year | Expected passes |
|---|---|---|---|---|---|
| A (v3 only) | 33% | 40% | 38% | 5% | 0.33 |
| A + B | 52% | 60% | 57% | 14% | 0.67 |
| **A + B + C** | **66%** | **70%** | **73%** | **30%** | **1.00** |
| A + B + C + D | 73% | 75% | 78% | 42% | 1.21 |

The pass/fail correlation between accounts started the same day is 0.20 for A–B and
0.02–0.11 for every other pair. Two accounts running the **same** strategy are
correlated 1.0: they take the same trades, so the second one adds nothing.

## Challenge plan

1. Buy three Apex 50K accounts and start them on the same day:
   A = v3 at 10 MNQ, B = Vault Break at 12 MNQ, C = Opening Drive at 10 MNQ.
2. Start when the Filter Status line is green (this helps A and B, not C). C can also
   start on its own at any time.
3. Same size on every trade; follow every signal; never move a strategy into another
   account.
4. Stop size per trade at these sizes: A $1,600, B $1,800, C $1,000. All are below the
   $2,000 drawdown, but A and B leave little room for a second loss early on. Do not
   size up: Vault Break "passes" more at 20 MNQ only because one $3,000 stop-out ends the
   account, which is a coin flip, not an edge.
5. Budget: about 3 accounts ($150) per funded account, the same as v3 alone, with much
   steadier results from round to round.

## Why not one account with all the strategies

Weighting each strategy by its risk, the combined book's daily Sharpe ratio is about
1.9, against 1.0 for v3 alone (1.7 vs 0.6 for 2023–2026). But the Apex challenge
mostly rewards luck in the first few days: even a strategy with no edge reaches
+$3,000 before −$2,000 about 30–40% of the time, and the trailing drawdown takes away
the cushion as soon as you are up. In the simulations, the best combined account
passed 35–38% (2018–2022 sizes looked like 43% but fell back to 31–36% for 2023–2026).
Daily stop-loss and profit-lock rules on the combined account lowered it further.
Separate accounts turn the low correlation into something the challenge does reward:
more independent attempts at the same time.

(It also avoids a practical problem: Apex nets positions in one account, so a long
from one strategy and a short from another would cancel each other.)

## What was tested and dropped

| Idea | Result |
|---|---|
| Fade moves stretched far from VWAP | Lost money at every setting (NQ trends intraday) |
| Opening-range (8:30–9:00) breakout | Profit factor about 1.0–1.05 |
| Fading the first 30 minutes | Lost money; following it works (Opening Drive) |
| Lunchtime RSI(2) mean reversion | Lost money |
| Prior-day high/low breakout or failure | Profit factor about 1.0–1.09, unstable |
| Late-day momentum (at 14:00, trade the day's direction to 15:10) | Profit factor 1.26, but only works at exactly 14:00 (13:30 and 14:30 fail) and passes 16–22% from 2023 on |

All of them are in `analysis/candidates.py`.

## Next steps

1. Backtest `NQ_Opening_Drive.txt` and `NQ_Vault_Break.txt` in MultiCharts, from
   2 Jan 2018, 1 NQ, no commission or slippage, Bar Magnifier at 1 minute, same
   fill settings as v3.
   - Opening Drive: the first trades should be stamped 9:05 CT. If MultiCharts again
     skips the early entries (the v3 "9:50 mystery"), this strategy will show it at once.
   - Vault Break needs a chart with the overnight session for the midnight open and VWAP.
2. Re-run the analysis with the MultiCharts reports:
   `python3 analysis/multi_strategy.py --VB "<vault break report>.xlsx" --DRIVE "<drive report>.xlsx"`
3. Optional: re-export the 1-minute bars with `StartTime(0)` to test Vault Break with
   the true midnight anchor in Python as well.

## MultiCharts confirmation (2026-10-10)

Reports: `Backtesting Strategy Performance Report OD v1.xlsx` (Opening Drive, 5-minute
chart) and `Backtesting Strategy Performance Report VB v1.xlsx` (Vault Break, 30-minute
chart with the overnight session), 1 NQ, 2018–2026, Bar Magnifier at 1 minute.

- **Opening Drive matches the Python test exactly:** the same 1,352 trades (same days,
  sides and entry bars, identical P&L), all entered at 9:05. MultiCharts did not skip
  the early entries, so whatever causes v3's 9:50 start is specific to v3.
- **Vault Break with the real midnight anchor is better than the Python
  approximation:** 1,743 trades, 66% winners, average $99, profit factor 1.28
  ($91 for 2018–22, $107 for 2023–26), positive in every year. From 26 Jan 2021 it
  closely matches the course's vaultbreak list: 1,285 trades vs 1,334, 68% winners vs
  67%, best trade $800 and worst −$1,500 in both.

**Per strategy, per NQ, after costs (MultiCharts lists):**

| | Trades | Win rate | Avg trade | Profit factor | Avg 2018–22 | Avg 2023–26 |
|---|---|---|---|---|---|---|
| v3 | 3,497 | 63% | $61 | 1.14 | $81 | $36 |
| Vault Break | 1,743 | 66% | $99 | 1.28 | $91 | $107 |
| Opening Drive | 1,352 | 41% | $119 | 1.23 | $92 | $157 |

Daily P&L correlation: v3 / Vault Break 0.24, v3 / Opening Drive 0.09,
Vault Break / Opening Drive 0.02.

**Per account:**

| Account | Any start day | No edge | Line green | Green 3 days | Starts 2023–26 | Worst start year |
|---|---|---|---|---|---|---|
| A: v3, 10 MNQ | 33% | 28% | 40% | 41% | 38% | 5% |
| B: Vault Break, 12 MNQ | **41%** | 31% | **48%** | **50%** | **51%** | 14% |
| C: Opening Drive, 10 MNQ | 33% | 26% | 31% | 30% | 37% | 21% |

**Accounts started together; chance that at least one passes:**

| Accounts | Any day | Line green | Starts 2023–26 | Worst start year | Expected passes |
|---|---|---|---|---|---|
| A (v3 only) | 33% | 40% | 38% | 5% | 0.33 |
| A + B | 55% | 65% | 63% | 18% | 0.74 |
| **A + B + C** | **69%** | **74%** | **78%** | **34%** | **1.07** |

Reproduce with:
`python3 analysis/multi_strategy.py --VB "Backtesting Strategy Performance Report VB v1.xlsx" --DRIVE "Backtesting Strategy Performance Report OD v1.xlsx"`

## Files

| File | What it is |
|---|---|
| `NQ_Opening_Drive.txt` | Opening Drive signal |
| `NQ_Vault_Break.txt` | Vault Break signal (your spec) |
| `NQ_Gap_Fill.txt` | Gap Fill signal, experimental |
| `../analysis/multi_strategy.py` | Reproduces every table above (about 15 s) |
| `../analysis/grid.py` | 1-minute grid and execution engine (matches the v3 MultiCharts trades on 99.4%) |
| `../analysis/portfolio.py` | Apex challenges for one or several strategies on real days, minute by minute; loads any MultiCharts trade list |
| `../analysis/candidates.py` | Python versions of all strategies tested |

## Caveats

- The new strategies are Python backtests on MultiCharts' own 1-minute data, not
  MultiCharts backtests. The engine reproduces v3's MultiCharts trades almost exactly,
  but each new strategy still needs its own MultiCharts confirmation.
- Parameters were chosen from small grids, and kept only where the neighbouring
  settings also worked, but they were still picked on the same 2018–2026 data.
- Neighbouring start days share most of the same days, so all pass rates are rough
  estimates (a few points either way).
- Live trading is usually a bit worse than the backtest (stop slippage, news days).
