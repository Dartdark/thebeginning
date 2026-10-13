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
| Overnight Drift (backup, off since 2026-10-12) | `NQ_Overnight_Drift.txt` | **MultiCharts-confirmed** (`Backtesting Strategy Performance Report OND v1.xlsx`), holiday fix added | Long midnight to 3:00 CT after a down session. PF 1.25, 8/9 years positive, flat 2023–24. Correlation about 0 with everything else |
| **Monday Long** | `NQ_Monday_Long.txt` | **MultiCharts-confirmed** (`Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx`): 449 of 450 days match Python | Long Mondays 8:30–15:00 CT, stop 0.5 ATR. 450 trades, 55% winners, $425 a trade, PF 1.55; 2023–26 PF 1.92, 2018–22 weak. In the funded set since 2026-10-12 (1 MNQ) |
| **Expiration Open Short** | `NQ_Expiration_Open_Short.txt` | **MultiCharts-confirmed** (`Backtesting Strategy Performance Report EOS v1.xlsx`): same 105 trades, entries and P&L as Python | Short at the 8:30 open on monthly options expiration day, out at 10:00, stop 0.3 ATR. 105 trades, 59% winners, $474 a trade, PF 1.93, 8/9 years positive. **Benchmark + it at $500 risk: $6,516 vs $5,387** |

## Current funded set (all MultiCharts-confirmed, updated 2026-10-12)

Full plan, cushion sizing table and payouts: `FUNDED_PLAN.md`. Rating: `FUNDED_RATING.md`.
Tier list of everything tested: `../TIER_LIST.md`.

| Strategy | Chart | Funded inputs (full size; scale with cushion sizing) |
|---|---|---|
| Vault Break (Apex strategy) | 30 min MNQ | `NumContracts` 3 |
| Overnight Bias ML v2 | 15 min MNQ | `RiskPerTrade` 400 |
| Monday Long (replaced Overnight Drift) | 5 min MNQ | `NumContracts` 1, `RiskPerTrade` 0 |
| Expiration Open Short | 5 min MNQ | `RiskPerTrade` 700 |
| **Late-Day Flow** (added 2026-10-12) | 5 min MNQ | `NumContracts` 2, `RiskPerTrade` 0 |

With cushion sizing: **$7,676 expected payouts within 1 year, $12,012 within 2 years, 4–6% of
accounts blown** (before Late-Day Flow: $7,153 / $11,612 / 9–10%). Portfolio Sharpe 2.51,
Sortino 4.76, Calmar 4.33, Ulcer 1.30. Overnight Drift is kept as a backup.

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

## Dealer gamma (GEX) and dark-pool (DIX) round (2026-10-12): real effects, too weak to trade

Data: `data/DIX.csv` (SqueezeMetrics, daily 2011 to 9 Oct 2026: S&P close, DIX, GEX). Each
day uses the previous day's values, because they are published after the close. GEX is
ranked against the past year, since its level grows with the market. Code:
`analysis/gex_flows.py`, `analysis/gex_flows_test.py`.

**The data behaves as the research says:**
- NQ's 8:30–15:00 range averages 2.49% after the lowest-GEX days and 1.09% after the
  highest. Dealers dampen moves when they are long gamma.
- Last 30 minutes vs the day so far (Baltussen et al.; Barbon et al.): correlation +0.17
  after negative-GEX days (momentum) and −0.12 after the top 20% (reversal). Each is only
  t ≈ 1.6–1.8, on NQ and ES alike.

**Your strategies by the previous day's GEX** (MultiCharts lists, per NQ):

| Strategy | Low GEX | Middle | High | GEX < 0 |
|---|---|---|---|---|
| Vault Break | $113 | $105 | $77 | $104 |
| Overnight Bias | $260 | $351 | $228 | **$51** |
| Overnight Drift | **$160** | $14 | $50 | **$220** |
| Expiration Open Short | $576 | $301 | $506 (PF 2.81) | $1,011 (18 trades) |

**Candidates in the funded bench** (current set: VB 3, ONB $300, OND $500, EOS $500 =
$6,495):

| Candidate | Stand-alone | Funded, 1 year |
|---|---|---|
| Overnight Bias skips the day after negative GEX | t = 4.1, 9/9 years | **$6,837** (+$342); 2 years $7,333 vs $7,280 |
| … the same filter from price only (6 versions: high ATR, below 20/50/100-day average, 5–8% drawdown) | The skipped trades were profitable | $5,706–6,640 (none better) |
| Overnight Drift only after low-GEX days | $150 a trade, but 2023–24 negative | $5,433–6,150 |
| Last 30 minutes: follow after negative GEX, fade after top-20% GEX | t = 1.4, 5/9 years | $3,835–5,006 |
| Long the session after a top-20% DIX day (stop 0.3 ATR) | t = 2.1; 2025 alone +$1,732, 2024 and 2026 negative | +$104 at $150 risk, worse at $300 |

**Verdict:** no change to the funded set. The Overnight Bias GEX filter is the best of
these, but:
- it adds about $340 in year 1 and nothing over 2 years;
- it needs yesterday's GEX typed in every morning;
- no price-only version matches it.

Keep it as an option if you ever automate a daily GEX feed.

## Structural calendar-flow round 2 (2026-10-12): nothing tradeable

Forced, calendar-timed flows (the kind behind Expiration Open Short), tested on NQ and ES
2018–2026 (`analysis/calendar_flows2_test.py`). Raw windows per contract (8:30–10:00,
8:30–15:00, last hour, last 30 minutes, 15:00 to the next 8:30), compared with all days:

| Event | Best window | Result |
|---|---|---|
| S&P quarterly rebalance (triple-witching close) | 8:30–15:00 down (−$552 NQ) | t = −1.0 NQ, −1.7 ES. The open is already traded by Expiration Open Short |
| Nasdaq-100 reconstitution (December) | 8:30–10:00 up | 8 days, t = 1.4: too few |
| Russell reconstitution (last Friday of June) | Overnight after it up | 9 days, t = 1.8: too few |
| VIX expiration Wednesday | 8:30–15:00 down, t = −1.5 | **FOMC overlap**: 23 of 105 are FOMC days; without them t = −0.4 |
| Roll week (the week before triple witching) | 8:30–15:00 down | ES t = −2.2, NQ −1.4 (without FOMC days) |
| Roll Thursday | none | t < 1.5 |
| Buyback blackout (about the 15th of the quarter's last month to the 25th of the next) vs open window | none | No difference (t < 0.7) |
| Day after triple witching | 8:30–15:00 up | t = 1.6 NQ, 1.3 ES |

As trades on NQ (stop 0.3–0.5 ATR, flat at 15:00), in the funded bench (current set $6,495):

| Candidate | Trades | Funded, 1 year |
|---|---|---|
| Roll-week short, 8:30–15:00 | 175, PF 1.06–1.13, t = 0.3–0.6, no weekday stands out | $5,113–6,050 (worse) |
| Day after triple witching, long | 35, PF 1.06, t = 0.1 | $5,947–6,155 (worse) |

**Verdict:** no change. The raw drifts do not survive a stop and a 15:00 exit.

## Forced-flow round 3 (2026-10-12): Late-Day Flow candidate

Code: `analysis/forced_flows3_test.py` (42 raw windows), `analysis/letf_rebalance_test.py`
(trade, neighbours, placebo, funded bench; outputs in the matching `_output.txt` files).

| Flow | Result |
|---|---|
| **Leveraged-ETF / last-hour flow: follow a big 8:30→14:00 move from 14:00** | **Candidate.** As a trade (move ≥ 0.4 ATR, stop 0.25 ATR, out 14:30): 898 trades, PF 1.44, t 3.5, 7/9 years, both sides positive; random side −$13 vs $94. Funded + 2 MNQ: $7,648 / $12,019 vs $7,153 / $11,612, blown 4–6% vs 9–10%. `NQ_Late_Day_Flow.txt`, needs a MultiCharts check |
| Futures settlement: 15:00–15:15 reverses the last hour | Consistent (t −4.0) but ~$29 gross: too thin |
| Vol-target funds de-/re-levering after realized-vol changes | Nothing (t ≤ 0.8) |
| Weekday × time of day | Only Monday (already traded) and Wednesday overnight (t 2.5, 1 of 20) |
| Quarter-end pension rebalancing (fade QTD, last 3 days) | Nothing (t −0.2) |
| European close / morning momentum at 10:30 | t 2.1 (unchanged, C) |

## CFTC positioning round (2026-10-12): nothing usable

Weekly Commitments of Traders, Traders in Financial Futures (`data/cot/`, 2017–2026,
`analysis/cot_flows.py`, `analysis/cot_test.py`). Net positions of leveraged funds, asset
managers, dealers and small traders as a share of open interest, ranked against the previous
3 years, used only from the Monday after the Friday release.

- **Next-week and next-month returns:** no relation on NQ or ES. Correlations −0.04 to
  +0.09, the largest t about 1.3; quintiles are not monotonic.
- **Funded strategies by positioning quintile:** noisy, non-monotonic patterns (e.g. Overnight
  Drift −$73 when leveraged funds are most long, Overnight Bias ML $169 when asset managers
  are least long), each one cell out of 12.
- **Those two as filters:** $6,757 and $6,805 vs $6,928 within 1 year; $8,204 and $8,344 vs
  $8,379 within 2 years.

**Verdict:** weekly positioning carries no timing information for NQ/ES day trades; no change.

## Vault Break robustness checks (2026-10-12, from an r/algotrading post)

The post ("I backtested 100+ retail trading strategies (~700 versions)") argues that a high win
rate often comes from the stop/target geometry, not the entry, and that limit orders filled "on
touch" flatter backtests. Both checks on Vault Break (`analysis/vb_random_entry_test.py`, 1,743
MultiCharts trades 2018–2026, same 40/75-point bracket and 14:30 exit, $7.25 + 1 tick):

| Test | Avg / trade | Win |
|---|---|---|
| Vault Break, target filled on touch | $97 | 66% |
| Vault Break, target must trade 1 tick through | $92 | 66% |
| Random long entries 10:00–14:00, all days (10 runs) | $6 | 59% |
| Random entry after VB's first signal, same days (30 runs) | $42 (range −$26 to $79) | 61% |
| VB's first trade each day | $90 | 65% |

- **The post is right about win rate:** random entries with the same bracket win 59–61%, so most of
  VB's 66% comes from the 40-point target being closer than the 75-point stop.
- **VB still has a real edge:** its first trade makes $90 vs $42 for a random entry after the
  same signal (beat all 30 random runs) and $6 for random days. Both the day selection and the
  entry timing add value.
- **Fills:** requiring a 1-tick trade-through costs about $5 a trade; target exits drop from 52% to 51%.

**Same placebo for Overnight Bias ML and Expiration Open Short** (`analysis/placebo_onb_eos_test.py`;
same stop, target and exit; 20–30 random runs each; the strategy beat every run in every test):

| Strategy (own trades) | Placebo | Avg / trade | Win |
|---|---|---|---|
| **Overnight Bias ML: $550**, 55% win (411 trades) | Same days and direction, random time after its entry | $156 | 53% |
| | Same days and entry time, random direction | $148 | 46% |
| | Same days and entry time, opposite direction | −$238 | 35% |
| | Random days, random time, random direction | $4 | 46% |
| **Expiration Open Short: $474**, 59% win (105 trades) | Short 8:30–10:00 on random days | −$20 | 44% |
| | Short 8:30–10:00 on other Fridays | −$39 | 39% |
| | Expiration days, short a random 90 minutes later in the day | −$3 | 47% |
| | Expiration days 8:30–10:00, random direction | $47 | 48% |

- **Overnight Bias ML:** the day choice (bias plus ML filter) is worth about $150 a trade on its
  own, the direction about $300 more, and entering on the breakout beats entering later.
- **Expiration Open Short:** the edge is specific to that one window: same time on other days,
  other times on the same day, or the other direction all make about nothing.

**Overnight Drift** (same placebo; own trades **$71**, 54% win, 1,039 trades, t = 2.1):

| Placebo | Avg / trade | Win | Own beats |
|---|---|---|---|
| Long 0:00–3:00 on random days | $36 | 52% | 97% of runs |
| Long 0:00–3:00 after up days (opposite condition) | $10 | 51% | 97% |
| Same days, a random 3-hour window starting 3:00–5:00 | −$35 | 51% | 100% |
| Same days 0:00–3:00, random direction | −$39 | 48% | 100% |

Passes, but less decisively: about half its profit is the general midnight-to-3:00 upward
drift that any long in that window gets; the down-day condition adds the rest (about $35–60 a
trade). Consistent with its B tier.


## Mean reversion, scheduled news and headline round (2026-10-12)

Code: `../analysis/news_meanrev_test.py` (first pass, output `..._output.txt`) and
`../analysis/headline_shock_test.py` (full checks, output `..._output.txt`). Per NQ after $7.25 + 1
tick per market/stop fill, 2018–2026. Not re-tested (already ranked): RTH big-move fades, round
numbers, VWAP fade, RSI(2), IBS, quiet-day fade, gap fill, the 7:30 release fade, pre-FOMC drift.

**Mean reversion: nothing works.**

| Idea | Best version | Verdict |
|---|---|---|
| Asia-session VWAP fade (17:00–23:59, target VWAP) | PF 0.57–0.93, t −0.8 to −3.2, 2–4/9 years | F |
| London / pre-market VWAP fade (0:00–7:25) | PF 0.86–1.05, t ≤ 0.3; 2023+ negative | F |
| Multi-day pullback (2–4 sessions the same way → fade next session) | PF 1.02–1.18, t ≤ 0.9; 2023+ negative | F |

**Scheduled news: one small lead.**

| Idea | Result | Verdict |
|---|---|---|
| FOMC 13:00 statement, follow / fade the first 5–15 min, out 13:29 / 14:00 / 15:00; press conference 13:30 | 69 days; best (fade 13:00→13:10, out 13:29) PF 1.62, t 1.5, best of 22; the sign flips by exit and in 2023+ | D |
| 9:00 CT releases (ISM, JOLTS...; 44 spike days) | t ≤ 0.8 | F |
| 7:30 releases other than payrolls (CPI, PPI, retail...; 179 days) | t ≤ 0.9 | F |
| **NFP Fade**: payroll Friday, fade the 7:29→7:45 reaction from 7:46 to 9:00, stop 0.5 ATR | 76 trades, 51% win, $319, PF 1.71, t 1.7, 7/9 years (2021–26 all positive); all 20 timing cells positive (t 1.4–3.0); random-side placebo $−8 (95% $315); funded + $500 risk: $8,093 / $12,086 vs $7,676 / $12,012, blown 4% / 3% | C: within noise, ~9 trades a year, found as a subgroup of a D idea |

**Headlines.** There is no headline feed for NQ here, so the stand-in for a headline is an
unscheduled 5-minute move far above normal for that time of day: |move| > K x the same slot's
mean |move| over the last N trading days, excluding scheduled minutes (7:30, 8:30–8:40, 9:00–9:10,
10:00, 15:00, FOMC afternoons). Jeon, McCurdy & Zhao (2022, JFE): jumps with news continue.
- Fading jumps loses (day and overnight). Overnight jumps go nowhere either way.
- **Headline Shock Follow** (day session 8:40–14:15): follow the jump from the next minute, stop =
  the jump's size, out after H minutes (by 14:55). Grid of 100 (K 5–7, N 10–30 days, H 45 min–14:55):
  PF > 1 in 88% of combinations on 2018–22 and 99% on 2023–26. The largest top cluster's medoid
  (K 5.5, N 14, H 60) is used:

| HSF, per NQ | Trades | Win | Avg | PF | t | Sharpe | Sortino | Calmar | Ulcer | Max DD |
|---|---|---|---|---|---|---|---|---|---|---|
| Both, 2018–26 | 835 | 43% | $142 | 1.31 | 2.5 | 0.81 | 1.82 | 0.71 | 7.43 | $18,486 |
| Longs | 352 | 45% | $142 | 1.31 | 1.5 | 0.54 | 1.15 | 0.40 | 5.07 | $14,072 |
| Shorts | 483 | 41% | $141 | 1.31 | 2.1 | 0.68 | 1.44 | 0.55 | 7.14 | $13,815 |
| Both, 2023–26 | 331 | 46% | $232 | 1.39 | – | 0.95 | 2.32 | 1.19 | 13.0 | $16,710 |

  - Placebo (same days, random times, follow the last 5 minutes): $32 vs $142 (20 runs, max $117).
  - Bootstrap Sharpe 2023–26: 0.95 (0.27–1.50), P(≤ 0) 1%; longs 9%, shorts 5%.
  - **Regime-bound:** by year 2018 +$2k, 2019 −$0.1k, 2020 +$16k, 2021 +$3k, 2022 +$21k, 2023 −$3k,
    2024 −$2k, 2025 +$53k, 2026 +$29k. It earns in headline-heavy years (Covid, 2022 rate shock,
    2025 tariffs) and loses a little in calm ones.
  - Correlation ≤ 0.15 with every strategy in the plan (0.15 with Late-Day Flow).
  - Funded bench (cushion sizing): + 1 MNQ $7,922 / $12,097 (blown 5% / 4%); + 2 MNQ $8,413 /
    $11,690 (8% / 10%); shorts only 2 MNQ $8,386 / $11,701. Year 1 up, year 2 flat or down: within
    noise, **not added**. Portfolio Sharpe 2.51 → 2.53 at 2 MNQ, max drawdown $3,743 → $4,482.
  - Tier C: a real, uncorrelated edge, but small per unit of risk (Sharpe 0.8) and carried by
    headline years. Python only; it would need a MultiCharts version before any use.

## CTA trigger levels and vol-control rebalancing (2026-10-12)

The two untested forced flows from `../multi_strategy/PRACTITIONER_SOURCES.md`, rebuilt from the
public descriptions bank flow desks give. Code: `../analysis/cta_volcontrol_test.py` (first pass)
and `../analysis/cta_fade_test.py` (follow-up); outputs in the matching `_output.txt` files. Per NQ
after $7.25 + 1 tick per market/stop fill, 2018–2026; about 45 comparisons in all, so |t| ≥ 3 is
the bar.

**CTA model:** signals sign(close − close N days ago), N = 21 / 63 / 126 / 252, position = mean
signal × min(2, 15% / 63-day vol); trigger level = the close N days ago. About 39 flips a year.
- *Following* CTA flows loses or does nothing: next day after a flip −$370 (t −1.9); after 2+
  flips −$2,432 (22 days, t −4.1); 14:00 → 15:00 when the 14:00 price would flip a signal +$40
  (t 0.4); buying / selling the break of the nearest trigger −$409 (t −2.4). **F.**
- *Fading* the next day looks good at first (2+ flips: +$2,397, t 4.0, 22 days; 1+ flips +$335, t 1.7),
  but **200 random lookback sets that CTAs don't use fade just as well** (the real set beats 56% of
  them). So it is generic reversal after trend-signal flips, not CTA flow. As a trade with a 0.3 /
  0.5 ATR stop: t 0.7 / 1.4. Fading the trigger touch intraday: $183, t 0.9. **D.**

**Vol-control model** (S&P Daily Risk Control style): exposure = min(150%, 10% / vol), vol = the
larger of the EWMA(0.94) and EWMA(0.97) vols of daily ES returns; flow = new exposure − drifted
exposure. Vol-control funds almost only *sell* in size (vol jumps fast, falls slowly).
- Lag 0 (today's return in the vol, estimated at 14:00), follow 14:01 → 15:00: t −0.5 to 0.6. **F.**
- It does not explain Late-Day Flow: LDF trades earn the same whether the vol-control flow agrees
  ($87) or opposes ($102), longs too ($69 vs $81).
- **Vol-Control Sell Flow (lag 1: exposure set from yesterday's vol, so the sell is known before
  the open)**: when the model must sell more than 6% of fund size, short NQ 14:01 → 15:00
  (the funds trade into the close), stop 0.25 ATR:

| VCS, per NQ | Trades | Win | Avg | PF | t | Sharpe | Sortino | Calmar | Ulcer | Max DD |
|---|---|---|---|---|---|---|---|---|---|---|
| 2018–26 | 67 | 55% | $455 | 2.15 | 2.2 | 0.70 | 1.74 | 0.62 | 4.40 | $5,509 |
| 2023–26 | 32 | 66% | $695 | 3.13 | – | 1.00 | 2.88 | 1.83 | 1.57 | $3,148 |

  - Shorts only by construction (no large buy flows exist). 8/9 years positive; 2018 and 2020 lost.
  - Thresholds 0.04 / 0.08 and stops 0.15 / none: t 1.1–2.7, all positive. Shorting the whole day
    instead of the last hour: ≈ $0, so it is the closing flow.
  - Random-day placebo: last-hour shorts average $7 a day; 95% of random 67-day samples ≤ $269 vs
    $591 (no stop).
  - Bootstrap Sharpe 2023–26: 1.00 (0.32–1.56); 2018–26: 0.70 (0.23–1.09); P(Sharpe ≤ 0) 1%.
  - Correlation with every plan strategy ≤ 0.05 (Late-Day Flow −0.03, even though they trade the
    same afternoon on 34 of the 67 days).
  - Funded bench: + 1 MNQ $7,785 / $11,938 (blown 6% / 4%); + 2 MNQ $8,049 / $11,789 (7% / 8%). Within
    noise: **not added.** Tier **C** (real, uncorrelated, but ~8 trades a year and t 2.2).

## Combined add-on of the three small edges (2026-10-13)

Headline Shock Follow (HSF), NFP Fade (NFP) and Vol-Control Sell Flow (VCS), each tier C and
within noise alone, tested together on top of the current plan. Code `../analysis/addon_combo_test.py`
(output in `..._output.txt`). They barely overlap (30–33 shared days with HSF, 4 between NFP and VCS);
daily correlations −0.08 to 0.05; correlation of the bundle with the plan 0.06.

| Per NQ (1 NQ each) | Trades | Win | Avg | PF | Sharpe | Sortino | Calmar | Ulcer |
|---|---|---|---|---|---|---|---|---|
| Bundle 2018–26 | 978 | 44% | $177 | 1.39 | 1.11 | 2.49 | 1.39 | 6.90 |
| · longs | 386 | 46% | $156 | 1.35 | 0.63 | 1.31 | 0.56 | 4.36 |
| · shorts | 592 | 43% | $191 | 1.42 | 0.99 | 2.21 | 1.00 | 8.36 |
| Bundle 2023–26 | 396 | 48% | $289 | 1.51 | 1.34 | 3.30 | 2.14 | 7.32 |

Bundle by year: 2019 −$1.1k, all other years positive (2025 +$62k, mostly HSF).

**Funded bench** (27 size combinations; current plan $7,676 / $12,012):

| Add-on | 1 year | 2 years | Blown 1y / 2y | 1-year gain, 90% interval | 2-year gain, 90% interval |
|---|---|---|---|---|---|
| NFP $500 + VCS 1 MNQ | $8,131 | $12,022 | 4% / 3% | **+$456 ($123 to $826)**, 6/8 start years | +$10 (−$183 to $252) |
| HSF 1 + NFP $500 + VCS 1 | $8,272* | $11,747* | – | +$596 ($151 to $1,011), 6/8 | −$265 (−$634 to $18) |
| NFP $500 + VCS 2 MNQ | $8,281 | $11,976 | 3% / 3% | – | – |
| Best of grid: HSF 2 + NFP $500 + VCS 2 | $8,733 | $11,653 | 8% / 10% | +$1,057 ($423 to $1,488) | −$359 (−$1,243 to $423) |

\* plan + gain. Intervals: block bootstrap over start days (60-day blocks), paired against the plan.

- **Year 1 gains clear the noise; year 2 does not.** Anything with HSF lowers the 2-year payout (the
  2-year window ends with 2023–24 starts, HSF's two losing years). NFP + VCS lifts year 1 by ~$450,
  leaves year 2 unchanged and lowers blowups (6% → 4%, 4% → 3%).
- Portfolio at full size with HSF 1 + NFP $500 + VCS 1: Sharpe 2.51 → 2.68, Sortino 4.76 → 5.21,
  Calmar 4.33 → 4.52, Ulcer 1.30 → 1.34, max drawdown $3,743 → $4,028. 2023–26 bootstrap Sharpe
  2.90 (2.19–3.66) vs 2.68 (1.95–3.49).
- **Decision: not adopted yet.** The rule (beat the plan by more than noise in both 1 and 2 years) is
  not met, and all three are Python-only and were picked from ~150 tests (selection bias makes these
  gains optimistic). **Best candidate: NFP Fade $500 + Vol-Control Sell Flow 1–2 MNQ**, the one
  version that helps year 1 without costing year 2. Next step if wanted: MultiCharts versions of
  both, then re-score with the MultiCharts trade lists.

**Nasdaq-100 special rebalance:** only one in 2018–2026 (announced 7 July 2023, traded at the close
on 21 July 2023). That day NQ fell 113 points by 14:00, 38 more into 15:00 and rose 10 after
settlement. One event can't be tested; the next one only happens if Nasdaq's concentration limit is
breached. **F (not testable).** Regular December reconstitution and quarterly rebalances were
already tested (F).

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

- **Gorton, Hayashi & Rouwenhorst (2008), "The Fundamentals of Commodity Futures
  Returns", SSRN 996930.** 31 commodity futures, 1969–2006. Low inventories mean higher
  risk premiums. High-basis (backwardated) and 12-month-momentum commodities beat the
  low ones by 10–14% a year (t = 3.7–4.9), held a month at a time. Trader positions
  (COT "hedging pressure") do **not** predict returns. **Not usable here:** it is a
  monthly long-short across many commodities, and equity-index futures have no
  inventory or convenience yield (the basis is just rates minus dividends). As a
  foundation it would need a multi-commodity monthly book, not NQ/ES day trades.
  The price-only trend filters it suggests were already tried in the GEX round and did not help.

- **Baltussen, Da, Lammers & Martens (2021), "Hedging demand and market intraday
  momentum", SSRN 3760365.** 60+ futures, 1974–2020. The return from the previous close
  to 30 minutes before today's close ("rest of day") predicts the last 30 minutes in the
  same direction (equity futures t = 7.3; Sharpe 0.9–1.7 before costs). The explanation is
  hedging that has to happen near the close: dealers short options gamma, leveraged ETFs,
  vol-targeting funds. The effect is only present when dealer gamma is negative. Tested exactly on NQ/ES
  2018–2026 (`analysis/intraday_momentum_test.py`, 15:00 CT close, trade 14:30–15:00):
  - **gone on average:** NQ gross +$2 per trade (−$15 net, t = −0.8), ES +$1 (−$29 net);
    the regression t is 1.05 on NQ and 0.54 on ES, against 7.3 in the paper
  - no better on big days (|ROD| > 1–2 sd: −$48 to +$84 net, t ≤ 1.1)
  - only after negative-GEX days: NQ +$102 net (t = 1.1), +$261 with |ROD| > 1 sd
    (t = 1.6, 117 trades), but carried by 2020 and 2025; this is the "gamma last 30"
    trade that already lowered funded payouts in the GEX round
  **Verdict:** the published edge has been arbitraged away in NQ/ES since 2018, except
  in crash regimes. Not a foundation for a funded strategy.

- **Kelly & Xiu (2023), "Financial Machine Learning", SSRN 4501707** (in the repo as
  `ssrn-4501707.pdf`). A 159-page survey, not a strategy. Main points:
  - "complex" models with heavy shrinkage (ridge) beat small, simple ones out of sample,
    even with few observations
  - judge a model by trading results, not R²; a tiny R² can still be very profitable
  - machine learning works best across thousands of stocks; on a single market
    (one time series) the data is small and overfitting is the main risk
  - the price-chart CNN (Jiang, Kelly & Xiu) and news/LLM signals are stock-picking tools

  **Built on top of it (`analysis/ml_filter_test.py`):** a walk-forward ridge model that
  predicts each funded strategy's next-day P&L from about 20 inputs known at the previous
  close (returns over 1/5/20 days, yesterday's 8:30–15:00 move, ATR vs its 60-day average,
  distance from the 50-day average, short vs long volatility, weekday, month start/end,
  expiration week; optionally VIX, GEX, DIX). Retrained every January from 2019, trading only
  on days with a positive prediction.

  | Strategy filtered | Kept vs skipped trades (2019+) | Funded bench (current set, 2019+ starts: $6,489 / $7,268) |
  |---|---|---|
  | Overnight Bias, all inputs | $565 vs $86 per NQ, 7/8 years kept > skipped | **$6,666 (1 year) / $9,650 (2 years)**; blown 40% → 19% |
  | Overnight Bias, price + calendar only (no VIX/GEX) | $510 vs $146, 6–7/8 years | $6,464 / $9,491 |
  | Overnight Bias, 55% of days skipped **at random** (30 draws) | – | $5,311 ± 526 / $7,664 ± 873; the model beat all 30 |
  | Overnight Drift | $187 vs −$9 | Worse ($3,838–5,657): fewer trades and qualifying days |
  | Vault Break | Kept trades better, but no clean split | Not benched |

  **Frozen (2026-10-12): `NQ_Overnight_Bias_ML.txt`.** Price and calendar inputs only,
  with the month-end flag dropped (MultiCharts can't know future holidays). Walk-forward with
  this exact input set: kept $476 vs skipped $171, 6/8 years; funded bench $6,466 / **$9,569**
  (1 / 2 years) vs $6,489 / $7,268, blown 22% vs 40%. The weights are fitted on all
  2018–2026 trades, so a backtest over that period is in-sample. On the ONB v2
  MultiCharts trades from April 2018 it keeps 396 of 973 (avg $597, PF 2.01, every year
  positive) and skips 577 (avg $86, PF 1.11). The PowerLanguage score was replayed in
  Python on 2,203 days: identical, except a 0.004 difference on Juneteenth 2026 that
  changes no decision. **MultiCharts-confirmed** (`Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ
  Overnight Bias v2.xlsx`): 411 trades 2018–2026, $558 average, PF 1.95, 55% winners.
  From April 2018 every trade-or-skip decision matches the Python model (405 common days;
  the 7 differences are January–March 2018, when the Python model lacked 60 days of
  history). On 12 holiday half-days the exit differs from the older ONB v2 report
  (early-close exit), not because of the filter. Funded bench with the MultiCharts lists
  (VB 3, OND $500, EOS $500): **$6,928 within 1 year (vs $6,495), $8,379 within 2 years
  (vs $7,280), blown 34% (vs 42%)** at RiskPerTrade 300 ($400–500 are no better). It is now
  in the funded set in place of Overnight Bias.

  **50K challenge (combine) check:** VB 8 + Overnight Bias $1,100 passes 43.8% (2019+:
  45.7%, median 6 days). With Overnight Bias ML at $1,100 the MultiCharts list passes 49.0%
  (2019+: 51.7%), but that list is in-sample; the walk-forward version passes 46.1% from
  2019 (+0.4 points) and needs a median 9 days instead of 6. Larger sizes ($1,500–2,000) are worse. **Verdict:
  keep plain Overnight Bias for the challenge** and Overnight Bias ML for funded accounts.

- **Baldi-Lanfranchi, Collin-Dufresne & Daniel (2026), "Asymmetric Reversals", NBER
  w35840.** US stocks 1972–2022. They split each stock's return into a part explained by
  systematic factors and public news (SYS) and a residual (RES). SYS continues, RES
  reverses (order-flow pressure that liquidity providers get paid to absorb), and negative
  residual shocks reverse much faster than positive ones (29% on the first day vs 4%).
  A long-short stock factor built on this has a Sharpe ratio of 2.55, declining over time.
  The paper's factor is a stock-picking strategy; we tested the time-series version on NQ
  (`analysis/asymmetric_reversal_test.py`):
  - the asymmetry shows up: after a big **no-news** down day (RTH move < −1 sd) the next
    8:30–15:00 session gains 23 bp on average (t = 2.4, 235 days); big up days don't reverse
  - news days don't continue as the paper predicts (big news down days rebound even more
    over 5 days, t = 3.1); the NQ-vs-ES residual has no reversal; splitting Overnight Drift
    by news or residual doesn't help
  - as a trade (long next 8:30–15:00, stop 0.3–0.5 ATR): PF 1.20–1.44, t = 0.7–1.8, 2026
    negative; funded bench $6,184–7,049 vs $6,928 (within noise, best version cherry-picked)

  **Verdict:** real but too weak to trade after a stop; nothing added.

  **Yes/no version tested (2026-10-12)**, after Vilkov (2026) "0DTE Trading Rules" (SSRN
  4641356), where a logistic win/lose model beat return prediction: same inputs, logistic
  regression on "trade wins", walk-forward. Worse for Overnight Bias: kept vs skipped
  $326–487 vs $142–284 and kept better in only 2–5 of 8 years (ridge: 6/8). Overnight Bias
  has a 3R target, so how much a day wins matters, not just whether it wins. Ridge stays.

- **Vilkov (2026), "0DTE Trading Rules", SSRN 4641356**: same-day SPX options; selling
  premium earns little after costs; 10:00 ET logistic timing rules reach net Sharpe 1.0–1.3
  out of sample. Not tradable on Apex (futures only; needs 0DTE option-chain data).
- **Dim, Eraker & Vilkov (2025), "0DTEs: Trading, Gamma Risk and Volatility Propagation",
  SSRN 4692190**: market makers are mostly long 0DTE gamma, which lowers intraday
  volatility; low 0DTE gamma means intraday momentum, high gamma means reversal (about 10 bp per hour
  apart); longer-dated gamma doesn't show the momentum effect. Needs intraday 0DTE
  market-maker positions (Cboe Open-Close data); our daily all-expiry GEX test already found
  the effect too weak to trade.

- **Zarattini, Barbon & Aziz (2024), "A Profitable Day Trading Strategy For The U.S.
  Equity Market", SSRN 4729284.** 5-minute opening range breakout (trade the break in the
  direction of the first candle, stop 10% of ATR, hold to the close) on 7,000 US stocks
  2016–2023. On all stocks it barely works (Sharpe 0.48); limited to the top 20 "stocks in
  play" (opening volume far above normal, usually company news) it made 1,600% (Sharpe 2.81).
  NQ/ES version with opening volume vs its 14-day average (`analysis/orb_rvol_test.py`, 18
  variants each):
  - ES: loses in every variant
  - NQ: only the 15-minute range, stop 0.2 ATR, above-average opening volume holds up
    (991 trades, 34% winners, $181 avg, PF 1.26, t = 2.6, 9/9 years); 5-minute versions and
    "very high volume" days (≥1.5x) don't
  - it overlaps Overnight Bias (same 8:30–8:45 breakout; correlation 0.33 with plain ONB)
  - funded bench: $6,798 vs $6,928 at $200 risk, worse at $400; with the recommended
    cushion sizing $6,546 / $10,129 vs $6,995 / $11,485, blown 22% vs 12%

  **Verdict:** a low-win-rate trend trade that duplicates Overnight Bias; not added.

- **Zarattini & Aziz (2023, rev. 2025), "Can Day Trading Really Be Profitable?", SSRN
  4416622.** 5-minute ORB on QQQ 2016–2023: enter at the second 5-minute candle's open in the
  first candle's direction, stop at the other side of the first candle, 10R target or the
  close. 24% winners, +0.13R a trade, Sharpe 1.12, no slippage assumed. On NQ 2018–2026
  (`analysis/orb_qqq_test.py`) the paper replicates exactly before costs (24% winners,
  +0.132R), but after $7.25 and 1 tick of slippage: $42 a trade, PF 1.07, t = 1.1, 2023 and
  2026 negative; 5R/3R targets and 15/30-minute ranges are no better than t = 2.0. ES loses in every
  version. **Verdict:** the edge is real but too thin for futures costs; not added
  (the volume-filtered version above already failed the funded bench).

- **Erb & Harvey (2013), "The Golden Dilemma", SSRN 2078535.** Gold is not a reliable
  inflation hedge over 1–20 years; when gold's real price is above its long-run average,
  later real returns have been below average; mine supply barely responds to price;
  emerging-market central-bank buying could push prices higher anyway. Long-horizon
  valuation, no trading rule; not usable for intraday futures. Tier F.

- **Goulding, Harvey & Mazzoleni, "Momentum Turning Points", SSRN 3489539.** US stocks
  1969–2018: slow (12-month) and fast (1-month) trend signals define Bull, Correction, Bear and
  Rebound states; Bear months are followed by negative returns (−7.7% a year) and a blend of
  slow and fast momentum earns alpha. On NQ 2018–2026 (`analysis/momentum_states_test.py`,
  states known at the previous close): Bear states were followed by **gains** (+278 bp next
  month; V-shaped recoveries), and the funded strategies make money in every state, with
  splits that flip between 12m/1m and 6m/2w windows. No filter. Tier F.

- **Asness, Frazzini, Israel & Moskowitz (2014), "Fact, Fiction and Momentum Investing",
  SSRN 2435323.** AQR essay refuting ten myths about cross-sectional momentum (buy the past
  12-month winners, short the losers, skipping the last month): it is large and robust (212
  years, 40 countries, many asset classes), works on both long and short sides and in large
  stocks, survives realistic costs, and works best combined with value. It's about ranking
  many securities against each other over months, not about trading one index intraday.
  Tier F for us.

## Tested and not good enough for funded

- Vault Break with the "Beat the Market" trailing exit: $4,100 vs the $5,400 benchmark
- Fading large intraday moves: loses money
- Round-number levels: too small to trade

See `../multi_strategy/RESEARCH_TOPICS.md` for details.
- Mean reversion (overnight VWAP fades, multi-day pullbacks), FOMC, 9:00 and non-payroll 7:30
  releases, fading headline jumps: no edge (see the 2026-10-12 news round above)
