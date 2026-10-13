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

## RSI + EMA + rolling VWAP pullback (Rule-Based Trader article on QQQ, 2026-10-13)

**What it is:** long QQQ when a fast RSI is oversold, a long EMA is rising and the close is well
below the 10-day rolling volume-weighted price; buy the next open, hold until RSI recovers (avg 3.6
days), no stop. Claimed 1999–2026: 215 trades, 79.5% win, PF 3.54 (RSI alone 2.19); 2018–2026 PF 2.66;
before costs. Exact RSI period / level, EMA length, discount and exit are not given.

**Why it might make money:** short-term reversal in an index with a rising trend (buy-the-dip);
the rebound is mostly earned overnight, like the overnight drift. It is a price-pattern signal, not
a forced flow.

**Can it be traded on Apex?** Not as written (multi-day holds; Apex needs flat by 15:59 CT). The
closest legal version closes at 15:55 and buys back at midnight each day ("NIGHT"); an RTH-only
version trades 8:30–15:00 each day of the hold. Code `../analysis/qqq_rsi_ema_vwap_test.py` (output in
`..._output.txt`). NQ daily bars from the 1-minute data (15:00 CT close), per NQ after $7.25 + 1 tick
per fill; signals from late 2018 (210 days of history needed). Base spec: RSI(2) < 10, EMA(200) rising
over 5 days, close < 10-day VWAP − 2%, exit RSI(2) > 70 (max 10 days).

| NQ 2018–2026, per position | Trades | Win | Avg | PF | t |
|---|---|---|---|---|---|
| RSI only, held (not Apex-legal) | 94 | 73% | $1,880 | 1.97 | 2.5 |
| RSI + EMA, held | 72 | 75% | $1,464 | 1.71 | 1.7 |
| RSI + VWAP, held | 57 | 70% | $1,218 | 1.46 | 1.0 |
| **RSI + EMA + VWAP, held (the article's version)** | 37 | 73% | $517 | **1.16** | 0.3 |
| RSI + EMA + VWAP, NIGHT (Apex-legal) | 37 | 65% | −$155 | 0.94 | −0.1 |
| RSI + EMA + VWAP, RTH only | 37 | 54% | −$1,996 | 0.51 | −1.3 |
| RSI only, NIGHT (Apex-legal) | 94 | 72% | $1,828 | 1.97 | 2.2 |
| RSI only, RTH only | 94 | 57% | $70 | 1.03 | 0.1 |

- **On NQ the filters do the opposite of the article's claim:** each one lowers the profit factor
  (1.97 → 1.71 / 1.46 → 1.16). The three-filter version is worse than random entries on rising-EMA
  days with the same hold lengths ($517 vs $890). 48 neighbouring specs range from PF 0.54 to 3.62:
  fragile, consistent with a fitted combination.
- **The edge is overnight:** the RTH-only part is ≈ $0 or negative in every version.
- **RSI only, NIGHT** is the one real effect: beats 96% of random-day placebos ($1,828 vs $586), but
  Sharpe 0.51 (2023–26 0.81), max drawdown $37,000 per NQ with no stop, and 2025 alone is 47% of the
  profit. In the funded bench it hurts: + 1 MNQ $7,134 / $11,898 (blown 7% / 5%) vs $7,676 / $12,012;
  + 2 MNQ $4,471 / $7,434 (46% blown). The three-filter NIGHT version: $7,155 / $11,869.
- **Verdict:** article's combination **F** on NQ (no edge after costs, filters hurt, below placebo);
  RSI(2) dip-buying held overnight **D** (real but regime-bound, and its unstopped drawdowns break
  the Apex drawdown rule). Not a foundation for a funded strategy.

## Bollinger Band reversals (2026-10-13, user idea): no edge

Code `../analysis/bollinger_reversal_test.py` (output in `..._output.txt`). Bands SMA(20) ± K·sd on
continuous 5- or 15-minute bars; "touch" fades a close outside a band, "reentry" fades the close back
inside after a close outside; target the middle band (limit), stop 0.15 ATR, out after 60 minutes;
day session (8:45–14:00 signals) or overnight (18:00–6:00); filters none / ADX(14) < 20 / narrow bands.
Per NQ after $7.25 + 1 tick per market/stop fill, 2018–2026.
- 72 versions: **none reaches t 2**; 92% lose money; 42% lose significantly (t ≤ −2), worst overnight
  (t −3 to −5.5, 0–2 of 9 years positive). Quiet-day filters lift the day-session versions to about
  break-even, no more.
- Best (5-min, K 3, re-entry, quiet days): 205 trades, $66, t 1.1; with other stops / holds t −0.1 to 1.3.
  Best of 72: noise.
- Daily version (close below the lower band → buy the next day 8:30–15:00): $483, t 0.8, 5/9 years;
  with a rising 200-day EMA $198, t 0.5; shorting upper-band closes $37.
- Same conclusion as every other fade tested here: NQ intraday moves continue more than they revert,
  and fading them pays the costs twice. The opposite (following band breaks) is what Vault Break and
  the noise-area breakout already do. **F.**

## 20/50 EMA zone pullback (2026-10-13, user spec): no edge

Code `../analysis/ema_zone_pullback_test.py` (output in `..._output.txt`). 10-minute NQ: trend = EMA20
vs EMA50; long when the bar's low touches the zone and it closes above it (short mirrored); optional
bullish / bearish confirmation (the signal bar, or the next bar); one position at a time; stop 30 /
target 65 points intrabar; flat 15:55 CT (Apex). Per NQ after $7.25 + 1 tick per market/stop fill.

| Version | Trades | Win | Avg | PF | t | Years + |
|---|---|---|---|---|---|---|
| **As specified** (confirm on the signal bar, 24h) | 11,627 | 33% | −$10 | 0.98 | −1.2 | 4/9 |
| · longs / shorts | 5,934 / 5,693 | 35% / 32% | $7 / −$28 | 1.02 / 0.93 | | |
| Day session only | 5,232 | 35% | −$9 | 0.98 | −0.8 | 3/9 |
| Stop / target scaled to price (0.12% / 0.26%) | 17,503 | 32% | −$9 | 0.96 | −2.2 | 3/9 |
| Best of 12 (next-bar confirmation, 24h) | 9,430 | 35% | $12 | 1.03 | 1.3 | 5/9 |

- **Placebo:** the same number of entries at random 10-minute closes, in the EMA-trend direction,
  average −$7 (random side −$16) vs −$10 for the real signals: the pullback trigger adds nothing.
- About 1,300 trades a year pay ~$17 each in costs and slippage (~$22,000 a year per NQ); the gross
  edge is about $7 a trade.
- **F.** The only positive variant is the best of 12, with t 1.3 and 5/9 years: noise.

## Multiple timeframes (2026-10-13, user idea): no improvement

Code `../analysis/multi_timeframe_test.py` (output in `..._output.txt`). Two meanings tested on the
plan's own strategies.

**A. Higher-timeframe trend filter** (keep a trade only if it agrees with the slower trend: previous
close vs its 20 / 50 / 200-day SMA, or the last 60-minute close vs its 60-minute EMA(20)), on the
MultiCharts lists of all 7 plan strategies:
- 28 strategy × measure comparisons, 1 with t ≥ 2: Overnight Bias ML with the 20-day SMA (agree $906 vs
  disagree $388, 8/9 years); expected by chance from 28 tries. Several go the other way (Vault Break and
  Late-Day Flow do better *against* the 200-day trend; Expiration Open Short better against the 20-day).
- Funded bench (current plan $8,770 / $12,236): filtering every strategy by SMA20 / SMA50 / SMA200 / H60
  gives $4,105 / $3,807 / $3,126 / $6,470 in year 1; filtering only ONB ML by SMA20 $7,915 / $11,826.
  The plan's edges come from flows that don't care about the trend; a trend filter just throws away
  good trades.

**B. Timeframe ensemble** (Vault Break on 15-, 30- and 60-minute bars at 1 MNQ each vs 30-minute at 3 MNQ;
Python version, which matches the MultiCharts 30-minute list within $10 a trade):

| Per NQ, 2018–26 | Trades | Avg | PF | t | Years + |
|---|---|---|---|---|---|
| 15-min | 1,877 | $64 | 1.17 | 3.1 | 8/9 |
| 30-min (the plan) | 1,742 | $82 | 1.23 | 3.8 | 9/9 |
| 60-min | 1,611 | $73 | 1.21 | 3.4 | 8/9 |

- The three are 0.77–0.84 correlated day to day, so the mix diversifies little: Sharpe 1.16 vs 1.20 for
  30-min alone, Calmar 1.11 vs 1.14.
- Funded bench: $7,350 / $11,749 vs $8,471 / $12,203 (also because 1-MNQ legs round to zero when the
  cushion factor drops below 1).
- Useful as a robustness check: Vault Break works on every bar size (t 3.1–3.8), so 30 minutes is not a
  lucky setting. **Verdict: keep single timeframes; D for both ideas.**

## Gold Breakout 15M ported to NQ (2026-10-13): no edge as written

Code `../analysis/range_breakout_gold_test.py` (output in `..._output.txt`). Range from the 17:00 CT
reopen to 23:00 CT (the TradingView default 00:00–07:00 GMT+3), buy stop at the high and sell stop at
the low (one cancels the other), stop 1% of entry, no target, out at 12:00 CT; 24 NQ variants (range
to 23:00 / 2:00 / 8:30, stop 1% / 0.5% / range / 0.3 ATR, out 12:00 / 15:00). Per NQ after $7.25 + 1
tick per fill, 2018–2026. (No gold data here beyond one week, so the gold claim itself is untested.)
- **Gold-literal on NQ:** 2,246 trades, 46% win, −$36, PF 0.97, t −0.6, 4/9 years; longs PF 1.06,
  shorts 0.87; worse than the same entries with a random side (−$20).
- Asia-only ranges (to 23:00 or 2:00): PF 0.97–1.07, t ≤ 1.1 in every version.
- Only the full overnight range (to 8:30, i.e. a US-session breakout) is positive: best of 24 (0.5%
  stop, out 12:00) $83, PF 1.13, t 2.0, 8/9 years; but the random-side placebo makes $46, it is 0.39
  correlated with Overnight Bias ML (same range), and in the funded bench it hurts: + 1 MNQ $8,531 /
  $11,755, blown 9% / 7% (plan $8,770 / $12,236, 3% / 2%). This is the C-tier overnight-range breakout
  already in the tier list.
- **F** for the gold strategy on NQ.

## Glow Ribbon Flip (2026-10-13, TradingView): no edge

Code `../analysis/glow_ribbon_flip_test.py` (output in `..._output.txt`). EMA(21) basis, band = EMA ∓
ATR(10) × 2 that only ratchets with the trend; a close beyond the band flips and reverses; pullback
re-entries on a close back across the EMA; the band is the intrabar stop, optional 2R target; flat
15:55 CT for Apex. 20 variants (5 / 15 / 30 / 60-min, 2R or no target, 2 or 3 ATR, day session only,
flips only). Per NQ after $7.25 + 1 tick per market/stop fill, 2018–2026.
- **Defaults (15-min):** 7,829 trades, 36% win, $2, PF 1.00, Sharpe −0.02, max drawdown $145,000 per NQ.
- Every variant: PF 0.99–1.07, t −0.7 to 1.2. Best of 20 (15-min, day session only): 2,954 trades, $45,
  t 1.2, 5/9 years (2022–24 and 2026 lose), Sharpe 0.38, $82,000 max drawdown; beats the random-side
  placebo (−$1) but not by enough to matter after picking the best of 20.
- Longs beat shorts in every variant (PF up to 1.15 vs ≤ 1.05): that is NQ's upward drift, not the system.
- 2,500–20,000 trades over 9 years means costs of $17 a trade dominate a gross edge of a few dollars.
  **F.**

## Forced-flow round 4 (2026-10-13): weekly expiries, MSCI reviews, JPMorgan collar — nothing tradeable

Code `../analysis/forced_flows4_test.py` (output in `..._output.txt`); 36 comparisons, so |t| ≥ 3 is the
bar. Per NQ after $7.25 + 1 tick per fill, 2018–2026.
- **Weekly options expiry Fridays** (344 non-monthly Fridays): the 13:00–15:00 move is only ~5% smaller
  than Mon–Thu (0.18–0.20 vs 0.19–0.21 ATR), so little pinning; following or fading the morning into the
  close t ≤ 0.5; trading toward the nearest 100-point level at 13:00 $28 (t 0.8; on monthly Fridays −$127);
  the Monday after t ≤ 0.6. Side finding: since 2022, Mon–Thu afternoons trend (follow 13:00→15:00 t 1.8,
  fade t −2.3), the 0DTE era; Late-Day Flow already trades that.
- **MSCI review days** (35): the close is clearly bigger (last 10 minutes 0.18 vs 0.08 ATR, last hour
  0.26 vs 0.14), so the flow is real, but its direction can't be told from the day's move (t −0.1).
  Across all month-ends, following the day into the close works a little (14:46→15:00 $235, t 2.1;
  other windows t −0.6 to 1.4; ES t 1.6): D, about 12 trades a year.
- **JPMorgan collar reset** (35 quarter-ends; strike estimated as the previous reset × 1.04): day ranges are
  ~9% lower in the 5 days before (0.75 vs 0.83 ATR) and higher after (0.86), consistent with a pin, but no
  direction: short near the strike −$104, long the 3 days after $373 (t 1.1).
- **Combination:** nothing passes on its own, so there is nothing to combine; stacking several t ≈ 1–2
  results from 36 tries would only add noise. **F / D.**

## The plan's forced flows on ES (2026-10-13): same direction, weaker — stay on NQ

Code `../analysis/es_forced_flows_test.py` (output in `..._output.txt`). Python versions of Expiration Open
Short, Monday Long, NFP Fade, Late-Day Flow and Vol-Control Sell Flow, run the same way on NQ and ES
(ES $50 a point, $5 costs, 1 tick per fill). 1 NQ ≈ 1.34 ES of notional.

| Per contract | NQ avg / PF / t | ES avg / PF / t | Daily corr NQ–ES |
|---|---|---|---|
| Expiration Open Short | $475 / 1.94 / 2.6 | $139 / 1.48 / 1.6 | 0.86 |
| Monday Long | $413 / 1.52 / 3.2 | $114 / 1.25 / 1.7 | 0.79 |
| NFP Fade | $354 / 1.82 / 1.9 | $30 / 1.09 / 0.3 | 0.71 |
| Late-Day Flow | $94 / 1.44 / 3.5 | $25 / 1.17 / 1.5 | 0.95 |
| Vol-Control Sell Flow | $455 / 2.15 / 2.2 | $182 / 1.64 / 1.5 | 0.92 |

- **Every strategy has the same sign on ES**, which supports the mechanisms (they are not NQ quirks),
  except NFP Fade, which barely shows on ES (t 0.3): treat it as the most fragile of the seven.
- Per dollar of notional ES is weaker everywhere (Sharpe 0.12–0.64 vs 0.62–1.16), and NQ and ES move
  together (0.71–0.95), so splitting between them lowers the risk-adjusted result: all five on NQ
  Sharpe 1.85, on ES 1.04, half / half 1.60.
- **Decision:** keep the plan on NQ / MNQ. ES is not a diversifier for these flows; a different market
  (GC, CL, ZN) would be.

## Crabel Stretch Breakout (2026-10-13, user's MultiCharts file v3): real edge, wrong shape for Apex

Code `../analysis/crabel_stretch_test.py` (output in `..._output.txt`), a Python replica of
`Crabel_Stretch_Breakout_NQ_v3`: stretch = 10-day average of min(high − open, open − low); stop entries
at open ± 1.4 × stretch from 8:31 to 9:30 CT; stop 0.7 × stretch; out at the 14:56 open; one trade a
day. Per NQ after $7.25 + 1 tick per fill.
- Defaults: 1,653 trades, **22% win**, $120, PF 1.25, t 2.7, 9/9 years; Sharpe 0.90, Sortino 2.57, Calmar
  0.95, Ulcer 7.67. Author's split: 2018–23 PF 1.26, 2024–26 PF 1.23, so the out-of-sample claim holds.
  Longs PF 1.28, shorts 1.22. Random-side placebo $44 vs $120.
- Neighbours: stops 0.7–1.0 × with entries 1.2–1.6 × all give PF 1.17–1.25, t 2.4–2.9 (a plateau);
  a 0.5 × stop kills it. NR7 / inside-day setups: fewer trades, worse after 2023; the 20-day trend filter
  on both sides PF 1.30 on half the trades.
- Correlation with the plan 0.23 (ONB ML), 0.19 (Late-Day Flow), 0.15 (VB).
- **Funded bench:** + 1 MNQ $8,591 / $11,969, blown 8% / 6% (plan $8,770 / $12,236, 3% / 2%); + 2 MNQ
  $7,083 / $9,965. **Combine:** + 2 MNQ 45.7% vs 46.9%; in place of Vault Break 34.1%.
- Like the "Beat the Market" noise-area breakout (B): a genuine opening-breakout edge, but a low win
  rate, long losing streaks and one big year (2022 = 36% of the profit) work against Apex's trailing
  drawdown and consistency rule. **B** as a strategy; not added.
- Two issues in the file if you ever run it: (1) on early-close days (no 15:55 ET bar) the EOD exit only fires on
  the first evening bar after the reopen, so a position is held through the close (an Apex violation) —
  add a session-end / holiday exit;
  (2) after an early close InRTH stays true, so stop orders can be placed overnight before the next
  open, relative to the previous day's open — reset InRTH at the date change.

## Bitcoin (2026-10-13): BTC Momentum file and Bitcoin forced flows — nothing tradeable yet

Data: CME Bitcoin futures 1-minute bars uploaded by the user (`BTC_1min_2018..2026.csv` in the repo root,
Dec 2018 – Oct 2026, CT; 83% of 8:00–15:00 minutes trade, prices carried forward). Code
`../analysis/btc_momentum_test.py` (output in `..._output.txt`). Costs per MBT $2.50 a round trip + 1 tick
($0.50) per fill; results per 1 BTC (= 10 MBT).
- **BTC Momentum ("September Winner")**, short if the morning window is down, hold to 15:00, no stop:
  as coded (the 5-minute bar stamped 8:00 opens at 7:55, so the window is 7:55→8:25) 993 trades, $47
  per BTC (= $4.70 per MBT), PF 1.14, t 1.3, 5/8 years; as documented (8:00→8:30) $34, t 0.9. All the
  profit is 2024–25. Random-side placebo −$42; shorting every day $4; longs after an up morning lose
  (t −1.2); 1–2% stops t 1.7; earlier exits lose. No September effect (September average $25 as coded,
  −$39 as documented). **D.**
- **Spot-ETF close** (creations / redemptions against a ~15:00 CT benchmark since 11 Jan 2024): following
  a ≥ 1% day into 15:00 loses (t −2.6 since the ETFs, −1.7 before); fading it is ≈ $0 after costs. **F.**
- **CME monthly settlement** (CF Bitcoin Reference Rate, last Friday ~10:00 CT): 9:00–10:00 is ~20% more
  volatile on expiry Fridays (0.85% vs 0.69%), no direction, no reversal after. **F.**
- For Apex: even the best version makes ~$5 per MBT per trade; a 3% Bitcoin day is ~$250 per MBT, so
  sizes that matter would dominate the drawdown. Not a candidate.

## VWAP pullback after an opening-range break (2026-10-13, user's file): no edge outside 2021+

Code `../analysis/vwap_orb_pullback_test.py` (output in `..._output.txt`), a replica of
`VWAP_Pullback_NQ_Margin_Vol_1min_TF` (8:30–9:00 CT opening range, a close beyond it sets the bias, VWAP
touch then reclaim, 20-bar swing stop, 5-bar swing target, one trade a day). Per NQ after $7.25 + 1 tick.
- **The replica reproduces the author's numbers:** from 2021, bracket-only as written, $74 a trade,
  PF 1.17, 57% win (author: ~$80, PF ~1.2, 58%).
- **But 2018–2020 lose $48,000 per NQ**: over 2018–2026 $23, PF 1.06, t 0.8, 5/9 years. Starting the test
  in 2021 is what makes it look good.
- **Apex version** (entries until 15:00, flat 15:55; the original holds 3% of trades past the day):
  −$2, PF 0.99; Sharpe −0.03, max drawdown $66,000 per NQ.
- **Random-side placebo** (same entry bars, random direction): $0, the same as the real signals, so the
  ORB bias + VWAP reclaim has no directional information. Shorts lose in 8 of 9 years; longs only $62
  (t 2.0), which is NQ's upward drift (the placebo shows no edge in direction).
- Variants (close-through retest, pullback-extreme stop, minimum reward:risk 1 or 1.5) are all worse.
- Funded bench: + 1 MNQ $8,423 / $11,672 vs $8,770 / $12,236.
- On the mechanism: VWAP execution algorithms trade on a volume schedule through the day; they don't
  buy because price touched VWAP, so "VWAP as a passive-flow zone" doesn't follow from benchmarking.
  The data agree (VWAP fade, VWAP trend and VWAP Pullback ADX also failed here). **F.**
- **Improvement attempt** (`../analysis/vwap_pullback_improve_test.py`): use the pullback only as an entry for a
  direction with a proven edge. With the plain Overnight Bias direction: $9, t 0.4 (nothing). On the days
  Overnight Bias ML trades, same side: $162, PF 1.70, t 3.2, 8/9 years (random side −$69), so the direction
  carries the edge; but on those same 304 days ONB ML's own entry makes $412, so the VWAP entry is the worse
  entry. As an extra 1-MNQ entry on ONB ML days: funded $8,986 / $12,194 vs $8,770 / $12,236 (within noise,
  and it is just more size on the same trades). Nothing to adopt.

## 0DTE dealer gamma from The Bridge (2026-10-13): real volatility effect, no trading edge

Code `../analysis/gamma_regime_test.py` (output in `..._output.txt`); data `GEX_1min_<year>.csv` exported with
`../multi_strategy/OFB_Gamma_Exporter.txt` (0DTE NDX dealer gamma, cumulative weighting only, so no look-ahead):
641 sessions, 2023-03-28 to 2026-07-07. The Bridge's NQ closes match the NQ grid on 97.6% of minutes (ET −1 h),
so flip + basis goes straight onto NQ. Regime = price above / below the flip with steepness > 0.02 (the
manual's "worth trusting"); 67% of 10:00 ET readings are above, 31% below. Design 2023-03-28 to 2024-12-31,
holdout 2025-01-01 to 2026-07-07. Data starts in 2023, so the 2018–2022 standard can't be met.
- **The regime is real but it is mostly volatility.** Below the flip the next 30 minutes move 30% more
  (20.0 vs 15.3 bp; design 18.4 vs 14.8, holdout 21.9 vs 15.8). Within quintiles of the last hour's realized
  volatility the gap shrinks to 1.33× in the quietest fifth and ~1.0–1.07× in the top three. After
  controlling for the first 30 minutes' range, the rest-of-day range is the same above and below.
  There's **no momentum vs mean-reversion difference**: correlation of the last 30 minutes with the next
  30 is −0.007 above and −0.004 below. The "dealers damp above, amplify below" story shows up only as
  slightly bigger moves, and realized vol already measures those.
- **As a filter on the plan's MultiCharts trades (regime at entry, each side):** no split with |t| ≥ 2
  except Vol-Control Sell Flow, above the flip $1,331 (n 15) vs below −$262 (n 12), t 2.5, same sign in
  both periods. That's 27 trades and one of ~20 splits, so not adopted; watch it. Others: LDF shorts
  below $94 vs above $29; ONB ML shorts below $1,165 vs above $228 (t −1.1); EOS above $1,068 vs below
  −$211 (t 1.3, 23 trades).
- **Previous session's regime** (read at 13:00, 14:00, 14:30, 14:55, 15:15 CT): it doesn't confirm the
  old SPX "ONB skips the day after negative GEX" filter. For ONB the sign flips with the reading time
  (below the flip better at 13:00, worse at 15:15) and 2023–24 contradicts 2025–26. Vault Break makes
  more after a below-flip close at every reading time (t −1.4 to −2.1), but almost all of it is
  2025–26 (2023–24 equal). Possible size tilt to recheck when more data exists, not a filter (above-flip
  days still make money).
- **Stand-alone ideas, all fail:**
  - Follow or fade the first hour by regime: follow −$105 a trade under the regime rule, PF 0.91. Following
    beats fading in both regimes, so the regime adds nothing.
  - Flip-cross breakout (trade the first close through the flip): −$79, PF 0.93, t −0.6. Fake levels at
    flip ±0.5% / ±1% do the same (−$406 to +$22). Fading the cross: $140, t 1.3.
  - Afternoon pin toward the major positive-gamma strike from 13:30 CT on above-flip days: price moves
    toward it 49% of the time; −$161 a trade (t −1.8) vs −$115 toward another 100-point NDX strike.
    No pin.
- Standard metrics for the stand-alone versions (2023-03-28 on, per NQ): regime rule Sharpe −0.54, PF
  0.91, Calmar −0.28, Ulcer 77.5; flip cross −0.39 / 0.93 / −0.23 / 54.9 (longs −1.46, shorts 0.37 with
  bootstrap P(Sharpe ≤ 0) 30%); pin −1.13 / 0.71 / −0.30 / 42.5. All bootstrap intervals include or sit
  below zero.
- **Verdict:** the 0DTE gamma regime is a volatility gauge (D), not a direction signal. The flip, the
  flip cross and the strike pin are F. Not tested yet: the order-flow columns (big prints, depth) and
  the Bridge's MBO history from 2017, which can be tested on the full 2018–2026 standard.

## CME order flow from The Bridge (2026-10-13): describes the move, doesn't predict it

Code `../analysis/orderflow_test.py` and `../analysis/orderflow_ldf_filter.py` (outputs in `..._output.txt`).
Data: `OF_1min_<year>_<part>.csv`, exported with `../multi_strategy/OFB_OrderFlow_Exporter.txt` from The Bridge's MBO
history. That's 1-minute RTH bars, 2018-01-02 to 2026-07-07 (2,117 full sessions), so the full 2018–2026
standard applies. Design 2018–2022, holdout 2023–2026. Notes on the export: MultiCharts' `Volume` came out
as buy volume (buys + `downvol` = the grid's volume on 97% of minutes), and `cum_delta` doesn't reset at
the RTH open, so the RTH delta is rebuilt from buys − sells.
- **Short-term prediction (5 / 15 / 30 minutes, 13 features):** delta over 5–30 min, RTH delta, book
  size and order-count imbalance, depth over 10 and 50 levels, pulled orders, queue depletion, icebergs,
  big prints, wall sizes. Every correlation with the next move is between −0.008 and +0.013. The best
  pooled one, RTH delta at 15 minutes, is +0.010, t 2.3, 8/9 years. Order flow does describe the move
  over the same window (delta vs the same 5 minutes +0.53). Costs need roughly |corr| > 0.05.
- **The best design-period feature as a trade** (50-level depth imbalance, top / bottom 10% by 2018–22
  thresholds, 15-minute hold): 2018–22 $4 a trade, 2023–26 −$24 (holdout correlation −0.005).
  2018–26 Sharpe −0.27, PF 0.97; holdout Sharpe −0.80 (bootstrap P(Sharpe ≤ 0) 98%). Longs and shorts
  both lose in the holdout (−$13 / −$31).
- **Opening flow:** trading the sign of the 8:30–9:30 RTH delta at 9:31 CT to 14:55 makes $8 a trade
  (PF 1.01, Sharpe 0.05). Following the price move instead makes $111 (t 2.0). When delta and price
  disagree, delta's side loses −$214 (t −1.8), so at the open the price move carries the information,
  not the flow. At 9:00 the two are equal ($100 vs $103).
- **Big prints** (largest trade in the minute ≥ the 99.5th percentile of the prior 20 sessions; follow for
  15 / 30 / 60 min): $2 / −$9 / −$2 a trade, PF 0.97–1.01; buys and sells alike. No information.
- **As a filter on the plan's MultiCharts trades** (RTH delta so far, or the last 30 minutes, agrees with
  the trade side; each side; about 40 splits): only Late-Day Flow longs with the last 30 minutes'
  delta agreeing hold in both periods ($138 vs −$4; 2018–22 $138 / −$7, 2023–26 $139 / $0; t 2.1).
  Dropping the disagreeing longs: LDF Sharpe 1.17 → 1.25, PF 1.44 → 1.57, Calmar 0.62 → 0.91, Ulcer
  7.4 → 5.4; 2023+ bootstrap Sharpe 0.50–2.02. But funded at 2 MNQ is $8,801 / $11,843, blown 8% / 7%,
  vs $8,770 / $12,236, blown 3% / 2% (3 MNQ worse). Fewer long trades leave the cushion growing more
  slowly. Filtering both sides: $8,836 / $12,220 (noise). The rest are noise or contradict each other:
  ONB ML agrees better (t 1.4) but ONB ADX30 disagrees better (t −1.9); EOS, Monday Long, NFP and VCS
  have no consistent split.
- **Verdict:** at minutes to hours on NQ, MBO order flow is a description of the price move, not a
  forecast. Short-horizon prediction, opening delta and big prints are F; the LDF long filter is D (real
  in both periods but no funded gain). The Bridge's built-in signals (`OFB_LargeTradePredictability`,
  `OFB_LiquidityPredictability`) weren't tested; the same data says not to expect much.

## The Bridge's Monday Long NQ (L644NQ) vs ours (2026-10-13): MultiCharts-confirmed, added to the funded plan

Code `../analysis/bridge_monday_long_test.py` (output in `..._output.txt`). It ports the Bridge's own code (v2.1,
pasted by the user). Buy the close of Sunday's 19:00 CT bar when the last regular session's ADX(7) is ≥ 10 and
< 50 and DI+ > DI−. Daily bars are regular sessions only (8:35–15:00, NYSE closures left out); Wilder smoothing
as coded. Take profit at 100 points, no stop, out at the close of Monday's 15:55 bar. No trade on NYSE-closure or
early-close Mondays. Holiday rules ported and checked. Ours: Monday 8:30 → 15:00, stop 0.5 ATR (MultiCharts
trades). Per NQ after $7.25 + 1 tick per market fill. A first version built from the manual's one-line
description (CME 17:00–16:00 daily bars) gave 203 trades, $508, PF 1.89. The exact port is better.
- **Bridge version:** 217 trades (53% of Mondays), 70% win, $563 a trade, PF 2.04, t 4.4, **9/9 years**
  positive. 2018–22 $505, 2023–26 $634; target hit 46%; worst trade −$6,172. Ours: 450 trades, $425,
  PF 1.55, t 3.3, 7/9 years; 2018–22 $153, 2023–26 $784.
- **Standard metrics, 2018–26:** Bridge Sharpe 1.43, Sortino 2.17, PF 2.04, Calmar 1.04, Ulcer 3.4;
  ours 1.11 / 1.97 / 1.55 / 1.03 / 10.5. 2023+ holdout: Bridge Sharpe 1.44 (bootstrap 0.58–2.34,
  P ≤ 0 0%), PF (days) 1.98, Calmar 1.23; ours 1.64 (0.88–2.37). Max drawdown $13,048 per NQ (70th
  percentile of shuffled orders). Daily correlation with ours 0.31. Long-only, so longs = all.
- **Where it comes from:** the filter picks Mondays after a trending-up week. Skipped Mondays make $220
  (2018–22 −$288, 2023–26 +$942), so since 2023 the filter leaves money on the table, but the kept days
  are good in both eras. Without the filter: $403, 2018–22 only $122. The Sunday-evening part alone is
  $184 (t 1.5). Holding to 15:55 without the target: $782 but a bigger worst trade (−$9,102). Our trade
  on the Bridge-filter Mondays makes $492 vs $364 on the others.
- **Placebo:** the same rule on Tuesday–Friday makes −$164 to +$173 (t ≤ 1.0). Monday is special.
- **Funded bench** (cushion sizing from $1,500):

| Monday set | 1 year | 2 years | Blown 1y / 2y |
|---|---|---|---|
| Current plan (ours 1 MNQ) | $8,770 | $12,236 | 3% / 2% |
| **Ours + Bridge 1 MNQ** | **$9,300** | **$12,438** | 3% / 1% |
| Bridge 1 MNQ instead of ours | $8,718 | $12,271 | 4% / 1% |
| Bridge 2 MNQ instead of ours | $8,717 | $11,512 | 9% / 9% |
| Ours at 2 MNQ (control: just more Monday size) | $8,422 | $10,573 | 18% / 19% |
| No Monday strategy | $8,218 | $11,964 | 4% / 1% |

- **MultiCharts confirmation** (`../analysis/bridge_monday_confirm.py`; 5-min @NQ, Bar Magnifier): all 217 trades
  match the Python port (same Mondays, entry prices, exit types; P&L correlation 0.988). With $7.25 + 1 tick:
  $541 a trade, PF 1.99, t 4.4, 9/9 years (2018–22 $503, 2023–26 $588; 2024 the weak year +$828). Sharpe 1.40,
  Sortino 2.08, Calmar 0.78, Ulcer 3.7; 2023+ Sharpe 1.38 (bootstrap 0.49–2.31, P ≤ 0 0%), Calmar 0.89,
  Ulcer 7.4. The 2023+ drawdown ($16,827 per NQ) is at the 91st percentile of shuffled orders (losses came
  together), so plan for that. Daily correlation: ours 0.30, the rest −0.01 to 0.06. Funded + 1 MNQ:
  $9,313 / $12,436, blown 3% / 1%; median days to all 6 payouts 278 → 255, all 6 within a year 36% → 48%.
  **Adopted (A).**
- **Earlier verdict (before the MC run): B, A once MultiCharts confirms it.** It's the strongest Monday version tested (9/9 years,
  steady across eras). Added at 1 MNQ next to ours it gives +$530 in year 1 (the speed goal) and +$202 in
  year 2 with no extra blowups. Doubling ours instead blows 18%, so the gain is diversification (different
  entry and days), not size. The Bridge's own note applies: never run it alone, because it trades about
  once every two weeks (inactivity rule). The Apex PA $1,000 daily loss limit isn't modelled; the worst
  trade is −$617 per MNQ.

## DriftPullback v2.1 (2026-10-13, F. Agnello via The Bridge's Strategies Feedbacks): real edge, wrong shape for Apex

Code `../analysis/drift_pullback_test.py` (output in `..._output.txt`), a Python replica of the pasted v2.1 code on
the 1-minute grid (Central time). It uses 15-minute signal bars: session VWAP from 8:30, drift = 15-min close vs 4
bars back. Arm long when the close is above a rising VWAP and drift ≥ +0.10% (short mirrored). It enters on the
next red 5-minute bar (green for shorts) from 9:30 to 14:25 CT. Long stop 80 / target 40 points, short 80 / 50;
the code's 2 extra ticks on stops; at most 4 trades and 2 losses a day; flat 15:00. Fills on 1-minute bars
(Bar Magnifier), with exits from the bar after the entry bar as MultiCharts places them. Per NQ after $7.25 +
1 tick on market fills.
- **Defaults:** 5,733 trades (637 a year), 63% win, $56 a trade, PF 1.12, t 4.0, **9/9 years** positive;
  2018–22 $62 (PF 1.15), 2023–26 $50 (PF 1.10). Exits: target 55%, stop 24%, flat 20%.
- **Longs:** 3,032 trades, $60, PF 1.14, t 3.3, 8/9 years (2018–22 $42, 2023–26 $77). **Shorts:** 2,701 trades,
  $53, PF 1.10, t 2.4, 8/9 years (2018–22 $84, 2023–26 $20; 2023 −$20,736).
- **Placebo** (same entry bars, random side with that side's stop / target, 10 runs): −$16 (−$40 to +$13)
  vs $56; longs −$5, shorts −$27. The direction carries real information.
- **Neighbours** are all positive with t 2.3–3.9: drift 0.05–0.20%, stops 60 / 100, targets 30–75, the first
  hour included, no daily caps, an SMA(20) anchor instead of VWAP. The validated defaults are the best of
  them. The ATR exits (ExitMode 1, "to be calibrated") are $19, t 1.1. Stricter target fills (price must
  trade through, as in your MultiCharts settings): 1 tick $53, t 3.7; 1 point $43, t 3.0.
- **Standard metrics, 2018–26:** Sharpe 1.30, Sortino 1.99, PF 1.12, Calmar 1.02, Ulcer 5.6, max drawdown
  $35,301 per NQ. Longs Sharpe 1.06 / Calmar 1.15 / Ulcer 6.7; shorts 0.75 / 0.45 / 8.2. 2023+ holdout:
  all Sharpe 1.16 (bootstrap 0.38–1.93, P ≤ 0 1%); longs 1.39 (0.61–2.16); shorts 0.30 (−0.49 to 1.06,
  P ≤ 0 28%).
- **Correlation:** longs 0.46 with Vault Break (both buy strength in the RTH trend) and 0.22 with Monday Long;
  shorts −0.10 to 0.15 with everything.
- **Funded bench** (8-strategy plan $9,313 / $12,436, blown 3% / 1%): + 1 MNQ $9,170 / $11,182, blown 13%;
  + 2 MNQ $6,553 / $7,117, blown 43%; longs only $8,238 / $10,945, blown 15%; shorts only $9,453 / $12,492,
  blown 4% / 2% (within noise). It's many small edges with 80-point stops, two losses allowed a day, so
  daily swings are big against a $2,000 trailing drawdown. The longs also double up on Vault Break days.
- **Verdict: B.** It's a genuine intraday trend-pullback edge, one of the few price-pattern signals here
  with a clean placebo and 9/9 years. But, as with Crabel, the shape doesn't fit Apex funded rules, and
  the short side is weak since 2023. Not adopted; shorts-only is a watch item if MultiCharts later
  confirms it. Better suited to a larger account without a tight trailing drawdown.

## VaultBreak v8 (2026-10-13, the Bridge's version) vs our Vault Break v1: keep v1

Code `../analysis/vault_break_v8_test.py` (output in `..._output.txt`). One 30-minute-bar engine with switches for
each v8 change; fills on 1-minute bars (Bar Magnifier); per NQ after $7.25 + 1 tick per market / stop fill.
- **Validation:** with v1 settings the engine matches the MultiCharts VB v1 trade list: 1,731 of 1,743 entries,
  P&L correlation 0.993, $91 vs $92 a trade, PF 1.26 both.
- **What v8 changes:** (1) the noise band uses the 15-session average of each calendar date's high − low,
  counting Sunday-evening and holiday sessions; v1 uses weekday true range. (2) A VWAP exit after 7 closes
  below VWAP. (3) The time exit is at the next bar's open instead of the 14:30 close. (4) No holiday times.
- **Results:** v8 1,880 trades, $82, PF 1.23, t 3.9, 9/9 years (2018–22 $81, 2023–26 $84) vs MC v1 1,743,
  $92, PF 1.26, t 4.3 (2018–22 $83, 2023–26 $100). Sharpe 1.25 vs 1.35, Sortino 1.89 vs 2.07, Calmar 1.02
  vs 1.31, Ulcer 3.4 vs 3.2, max drawdown $16,886 vs $13,618 per NQ. 2023+ bootstrap Sharpe v8 0.47–2.04,
  v1 0.67–2.26. Daily correlation 0.96. Long-only, so longs = all.
- **Which change does it:** only the band. v1 with the v8 band = $83, PF 1.23: short Sunday sessions shrink
  the average range, the band gets closer to the open, and more weaker breakouts trade. The VWAP exit never
  fires (0% of exits, at 4, 7 or 10 bars): the bracket or the 14:30 exit always comes first. The time exit
  and the holiday handling change nothing ($91 either way).
- **Funded** (8-strategy plan, VB swapped at 3 MNQ): v8 $8,750 / $12,259, blown 5% / 4% vs $9,313 / $12,436,
  3% / 1%; v8 2 MNQ $9,050 / $12,320. **Combine** (VB 8 MNQ + ONB ADX30): v8 pass 43.1% vs v1 46.9%
  (2023–26 45.5% vs 51.1%).
- **Verdict:** keep v1 in both plans. v8 is the same strategy with a slightly worse noise band (C as a
  variant).

## VWAP Pullback + ADX gate (2026-10-13, the Bridge's "C.S." profile): the gate adds little, funded worse

Code `../analysis/vwap_pullback_adx_test.py` (output in `..._output.txt`), on the replica of the VWAP pullback tested
earlier (`vwap_orb_pullback_test.py`, F) plus this profile's changes: ADX(14) of the 1-minute bars ≥ 20 and falling
on the signal bar (delays, doesn't cancel), long only, 1 trade a day, entries 9:01–17:00, flat 15:55 CT. Per NQ
after $7.25 + 1 tick per market / stop fill.
- **C.S. profile:** 1,052 trades (117 a year), 61% win, $60, PF 1.23, t 2.2, **6/9 years**. 2018–20 lose
  (−$2,110, −$3,129, −$5,505); 2023+ $152 a trade (2025 +$23,990, 2026 +$26,697).
- **The gate:** no gate $59 (PF 1.19), ADX ≥ 20 only $59, falling only $53, ADX ≥ 25 and falling $38,
  inverted (ADX < 20) $21. A random gate passing the same 31% of bars makes $47 ($20–62). The gate adds a
  little win rate (61% vs 55%), not much money.
- **Placebo** (same entry bars, random side): $0, vs $60 for the longs. The long side's edge looks like NQ's
  upward drift since 2021 (the earlier test found the same: longs only $62, t 2.0). The short side with the
  gate: −$19, PF 0.94. MinRR 1: −$28; StopMode 2: $23.
- **Standard metrics, 2018–26 (longs):** Sharpe 0.73, Sortino 0.98, PF 1.23, Calmar 0.27, Ulcer 16.8, max
  drawdown $26,411. 2023+: Sharpe 1.63 (bootstrap 0.78–2.57), Calmar 2.31, Ulcer 3.9. It's a recent-regime
  strategy. Shorts 2023+ Sharpe 0.06.
- **Funded** (8-strategy plan $9,313 / $12,436, blown 3% / 1%): + 1 MNQ $9,250 / $11,841, blown 7%; + 2 MNQ
  $8,626 / $10,355, blown 18%. Correlation ≤ 0.11.
- **Verdict: D.** Positive only since 2021, no directional information beyond the drift, and the ADX gate is
  close to a random filter. Not adopted.

## The Bridge's Overnight Bias ORB vs ours (2026-10-13): same idea, ours is better

Code `../analysis/bridge_onb_orb_test.py` (output in `..._output.txt`). It's a Python replica of the pasted
`OFB_OvernightBiasORB_Signal` on 15-minute bars, with fills on 1-minute bars and Central-time inputs (8:30 /
8:45 / 12:00 / 14:30 / 15:00). Ours = the MultiCharts trade lists. Per NQ after $7.25 + 1 tick per market /
stop fill.
- **What's different:** the Bridge's version enters on a 15-min close beyond the opening range (market next
  bar), not a stop order at the level. It allows up to 4 trades a day and uses ADX(16) ≥ 20. It skips
  breakout bars over 2.5× the 20-bar average range, and days whose opening range is over 2× its 20-day EMA.
  The stop is 0.30 × the regular-session ATR, measured from the signal close. Last entry 12:00, flat after
  14:30, overnight range from 23:45.
- **Results:** Bridge 779 trades, 52% win, $313, PF 1.52, t 4.4, 9/9 years (2018–22 $241, 2023–26 $402).
  Longs $308 (t 3.5), shorts $320 (t 2.7). Random-side placebo $56. Ours: **ONB ADX30** 676 trades, $372,
  PF 1.66, t 4.9, 9/9 years; **ONB ML v2** 343, $636, PF 2.12, t 5.0. Exits: the Bridge's target is hit only
  6% of the time (stop 37%, time 58%).
- **Standard metrics, 2018–26:** Bridge Sharpe 1.47, Sortino 2.79, Calmar 1.64, Ulcer 3.1, max DD $16,611.
  ONB ADX30 1.60 / 3.31 / 2.06 / 3.0 / $13,614. ONB ML v2 1.63 / 3.48 / 1.56 / 3.1 / $15,627. On the 2023+
  holdout all three are close (Sharpe 1.60 / 1.54 / 1.55). Bridge shorts 2023+ Sharpe 0.76 (P ≤ 0 6%).
  Daily correlation with ours 0.70 (ADX30) and 0.53 (ML v2).
- **Each difference undone:** our ADX gate (ADX(14) > 30) on the Bridge's mechanics gives $364, PF 1.66, the
  same as ours, so the ADX threshold is most of the gap. One trade a day: $288, so re-entries help them a
  little (second trades average $557). Without the OR-size band: $283. Without the bar-range skip: $331.
  Our ATR or stop anchor: no change. Last entry 14:00: $280. Stop 0.25: $252.
- **Their OR-size band on our trades:** it skips only 20 ADX30 trades ($18 average) and 5 ML trades. Combine
  pass 46.5% vs 46.9%; funded $9,098 / $12,143 vs $9,313 / $12,436. No gain.
- **Funded** (Overnight Bias ML $400 swapped): Bridge $400 $6,860 / $8,833, blown 31%; $300 $7,712 / $10,491,
  blown 13%; added at $200 next to ML $9,295 / $11,378, blown 11%. **Combine** (VB 8 MNQ + $1,100 risk):
  Bridge pass 38.9% vs our ADX30 46.9% (2023–26 44.0% vs 51.1%).
- **Verdict: B, not adopted.** A real edge, but a weaker version of the strategy we already run. Keep ONB
  ADX30 for the combine and ONB ML v2 for funded.

## The Bridge's VWAP Fade (2026-10-13): loses money

Code `../analysis/bridge_vwap_fade_test.py` (output in `..._output.txt`). Rules, on a 1-minute chart in Central time:
fade a close beyond the Globex VWAP (from 17:00 CT) ± 2 sigma, target VWAP ± 1 sigma, no stop, out after 60 bars
or at 14:00. Entries 8:30–14:00. VWAP and sigma are rebuilt from 1-minute bars; against the Bridge's
tape-exact RTH values they're within 0.1 point and 0.99× sigma. Per NQ after $7.25 + 1 tick per market fill.
- **Defaults:** 4,009 trades (445 a year), 62% win, −$25 a trade, PF 0.93, t −1.5, 3/9 years. Longs −$26,
  shorts −$24. Worst trade −$17,857 (no stop). Exits: target 64%, time 28%, end of day 8%. Random-side
  placebo −$13, so fading is worse than random.
- **Variants** (10): every one loses except 3 sigma in, target at VWAP, stop at 4 sigma ($22, t 0.4, 543
  trades). Wider bands lose more (2.5σ −$41, 3σ −$94); stops at 3 / 3.5 σ −$16.
- **Standard metrics:** Sharpe −0.52, Sortino −0.64, PF 0.93, Calmar −0.10, Ulcer 90, max drawdown
  $107,963 per NQ; longs Sharpe −0.34, shorts −0.41; 2023+ P(Sharpe ≤ 0) 90%.
- **Funded:** + 1 MNQ $8,644 / $11,986, blown 7% / 4% vs $9,313 / $12,436; best variant $9,296 / $12,358.
- **Verdict: F.** It agrees with earlier tests here (VWAP fade, VWAP 2σ). Moves beyond 2σ of the Globex VWAP
  keep going more often than they snap back. The Bridge's manual calls it an example to adapt, not a strategy.

## The Bridge's Large Trade Predictability (2026-10-13): a small real gross edge, far below costs

Code `../analysis/bridge_large_trade_test.py` (output in `..._output.txt`), the horizon-matched version. At each bar
close the direction comes from the candle colour (mode 1), the bar's largest print if ≥ 100 / 200 contracts
(mode 2), or both agreeing (mode 3). It holds one bar from the next open and keeps the position while the signal
repeats. Data: the Bridge's big_trade per minute (2018–2026 RTH), 8:31–15:00 CT, 1- and 5-minute bars.
- **1-minute bars, before costs:** every mode is slightly positive. Candle colour +0.05 points a bar, whale
  ≥ 100 +0.22, both ≥ 200 +0.40, i.e. $2–8 a trade. There is short-lived momentum after big prints. A round
  trip costs $17.25 (0.86 points).
- **After costs:** candle −$15 a trade (421,670 trades, t −45), whale ≥ 100 −$13 (4,385, PF 0.85), whale
  ≥ 200 −$14, both ≥ 100 −$14, both ≥ 200 −$9 (647 trades, PF 0.89). Sharpe −0.33 to −13.
- **5-minute bars:** the gross edge turns negative (−0.12 to −1.25 points a bar), so the effect is gone
  within minutes. Net −$21 to −$44 a trade.
- **Verdict: F.** This matches the earlier order-flow result (big prints followed for 15–60 minutes ≈ $0).
  The information in a whale print lasts about a minute and is worth less than the spread plus commission.
  It needs market-maker economics, not a retail futures account.

## Donchian breakout + Larry Williams Large Trade Index (2026-10-13, user's paste): weak, gone since 2024

Code `../analysis/donchian_lwti_test.py` (output in `..._output.txt`). The 96-bar Donchian breakout (current bar
included) with LWTI on the right side of 50 and volume above its 30-bar average; one entry a calendar day. Exits as
coded: the bar's high/low against the signal close + 100 / − 50 points, then out at the next open. The LWTI
function wasn't pasted; the common definition is used, 50 + 50 × SMA(close − close[25], 20) / ATR(25), and only
its side of 50 matters. Bar size not given: 15-minute assumed (96 bars = a day), 5 and 30 also run. Per NQ after
$7.25 + 1 tick per market fill.
- **As coded** (24 h, no time exit, 18% held overnight, not Apex-legal): 15-min 1,871 trades, $67, PF 1.10,
  t 1.8, 7/9 years; 5-min $18; 30-min $90 (t 1.9). The next-open exits overshoot: 30% of trades lose more than
  the 50-point stop; worst −$6,987.
- **Apex version** (signals 8:30–15:00 CT, flat after 15:00), 15-min: 1,631 trades, $61, PF 1.11, t 1.8, 6/9
  years. 2018–22 $113, 2023–26 −$6 (2025 −$14,138, 2026 −$18,947). Longs $92 (t 2.2), shorts $21 (t 0.4,
  3/9 years). Random-side placebo $6 (−$50 to $90).
- **The LWTI filter does the work:** without it $21; without the volume filter $54. Other targets / stops
  are worse (50/50 $41, 150/75 $33).
- **Standard metrics (15-min Apex):** Sharpe 0.61, Sortino 0.96, PF 1.11, Calmar 0.22, Ulcer 8.9, max DD
  $51,462 per NQ; longs Sharpe 0.72, shorts 0.13. 2023+: Sharpe −0.05 (P ≤ 0 60%); longs 0.30, shorts −0.40.
- **Verdict: D.** A momentum filter on breakouts helped in 2018–22 and has stopped working. The longs are
  mostly NQ's trend. No funded bench run: it's negative on the 2023+ holdout.

## The Bridge's Liquidity Predictability (2026-10-13): the resting book doesn't predict the next bar

Code `../analysis/bridge_liquidity_test.py` (output in `..._output.txt`). Imbalance = (bid − ask depth) / (bid + ask)
over 10 / 20 / 50 levels (the Bridge's MBO depth, 2018–2026 RTH). Follow the book at ±20% or ±40%, or the candle,
or both agreeing; next bar at market, out after exactly 1 bar. 1- and 5-minute bars, 8:31–15:00 CT. Per NQ after
$7.25 + 1 tick per fill. The book is rarely lopsided: 50 levels ≥ +20% on 1% of minutes, ≤ −20% on 2%.
- **1-minute bars:** following the book is negative before costs at 10 and 20 levels (−0.04 to −0.30 points)
  and +0.05 at 50 levels (t 0.7). "Both agree" at 50 levels +0.35 points (t 2.5) is the best of 22 rows, still
  −$10 a trade net. Every row nets −$10 to −$23 a trade (PF 0.72–0.84).
- **5-minute bars:** two of 11 rows are net positive, both ±40% on few trades: 20 levels $26 (612 trades,
  gross t 1.9; 2018–22 $36, 2023–26 $8) and 50 levels $27 (292 trades; 2023–26 −$21). The rest −$4 to −$29.
- Fading the book doesn't work either (−$18 / −$29).
- **Verdict: F.** This matches the earlier finding (depth imbalance vs the next 5–30 minutes, |corr| ≤ 0.024).
  Resting size is easy to cancel and gets pulled; it doesn't carry direction beyond costs. The two positive
  5-minute rows are what chance gives among 22 tries and fail the holdout.

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
