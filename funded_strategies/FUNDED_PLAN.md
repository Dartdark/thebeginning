# Funded phase plan: Apex 50K EOD Performance Account

## Current plan (updated 2026-10-13): eight strategies, faster to $13k

Priority: collect all 6 payouts ($13,000) sooner. **New: the Bridge's Monday Long NQ** (it ships with The Bridge,
Strategies screen, `L644NQ_MondayLong_NQ` v2.1), MultiCharts-confirmed (`../analysis/bridge_monday_confirm.py`,
output in `..._output.txt`). It runs next to our Monday Long, not instead of it. NFP Fade and Vol-Control Sell
Flow are MultiCharts-confirmed (`../analysis/nfp_vcs_confirm.py`); full size starts at a **$1,500** cushion.

| Strategy | File | Chart | Funded inputs (full size) | Trades |
|---|---|---|---|---|
| Vault Break | `../apex_strategies/NQ_Vault_Break.txt` | 30 min MNQ | `NumContracts` 3 | ~107 a year |
| Overnight Bias ML (v2) | `NQ_Overnight_Bias_ML.txt` | 15 min MNQ | `RiskPerTrade` 400 | ~38 a year |
| Monday Long | `NQ_Monday_Long.txt` | 5 min MNQ | `NumContracts` 1, `RiskPerTrade` 0 | every Monday |
| Expiration Open Short | `NQ_Expiration_Open_Short.txt` | 5 min MNQ | `RiskPerTrade` 700 | 12 a year |
| Late-Day Flow | `NQ_Late_Day_Flow.txt` | 5 min MNQ | `NumContracts` 2, `RiskPerTrade` 0 | ~100 a year |
| NFP Fade | `NQ_NFP_Fade.txt` | 5 min MNQ | `RiskPerTrade` 500 | ~9 a year (payroll Fridays, 7:45–9:00 CT) |
| Vol-Control Sell Flow | `NQ_Vol_Control_Sell.txt` | 5 min MNQ + **5 min @ES as data2** | `NumContracts` 1, `RiskPerTrade` 0 | ~8 a year (14:00–15:00 CT, shorts) |
| **Bridge Monday Long (new)** | The Bridge → Strategies → `L644NQ_MondayLong_NQ` (import as a Signal) | 5 min MNQ, full Globex session, Exchange time | `NumContracts` 1, defaults otherwise (`TargetPts` 100, `StopPts` 0) | ~25 a year (Sunday 19:00 CT → Monday 15:55) |

**Cushion sizing:** cushion = balance − trailing threshold, each morning. f = cushion / **$1,500**,
kept between 0.5 and 1; multiply each full-size input by f and round down:

| Cushion | f | VB | ONB ML risk | Monday | EOS risk | LDF | NFP risk | VCS | Bridge Monday |
|---|---|---|---|---|---|---|---|---|---|
| $1,500 or more | 1.0 | 3 | 400 | 1 | 700 | 2 | 500 | 1 | 1 |
| $1,125 | 0.75 | 2 | 300 | 0 (off) | 525 | 1 | 375 | 0 (off) | 0 (off) |
| $750 or less | 0.5 | 1 | 200 | 0 (off) | 350 | 1 | 250 | 0 (off) | 0 (off) |

The Bridge Monday Long enters on Sunday evening, so use Sunday's cushion (Friday's close balance) for it.

| All MultiCharts trade lists, $7.25 + 1 tick per fill | 1 year | 2 years | Blown (1y / 2y) | Median days to all 6 payouts | All 6 within 1 year |
|---|---|---|---|---|---|
| Previous plan (5 strategies, $2,000 cushion) | $7,676 | $12,012 | 6% / 4% | 306 | 21% |
| Previous plan (7 strategies, $1,500 cushion) | $8,770 | $12,236 | 3% / 2% | 278 | 36% |
| **Current plan (8 strategies: + Bridge Monday Long 1 MNQ)** | **$9,313** | **$12,436** | **3% / 1%** | **255** | **48%** |

Bridge Monday Long at 2 MNQ: $8,747 / $11,212, blown 11% / 12%, so keep it at 1. Same-method portfolio metrics
at full size, 2018–2026 (`bridge_monday_confirm.py`): 8 strategies Sharpe 2.82, Sortino 5.65, PF (days) 1.82,
Calmar 5.05, Ulcer 1.33, max drawdown $4,004, $20,221 a year; the 7-strategy set on the same method 2.71 /
5.35 / 1.78 / 4.72 / 1.35 / $4,004 / $18,912. 2023+ bootstrap Sharpe 3.09 (2.35–3.87). Every year better.
The block below describes the 7-strategy set as it was measured on 2026-10-13 (portfolio script).

Portfolio at full size 2018–2026: Sharpe 2.61 (was 2.51), Sortino 5.00, PF (days) 1.73, Calmar 4.53,
Ulcer 1.30, max drawdown $3,743 (unchanged), $16,939 a year. Bootstrap Sharpe 2023–26 2.84
(2.12–3.64). Daily correlations of the two new strategies with the rest ≤ 0.05. Every year positive
(2018 +$3,784 … 2025 +$25,046; 2026 to date +$16,427).

**Setup notes for the two new charts:**
- NFP Fade: 5-minute MNQ, CME 24-hour session (it needs the 7:30 CT bar), load at least 30 trading
  days of history.
- Vol-Control Sell Flow: data1 5-minute MNQ, data2 5-minute @ES, same session; load at least a year of
  history so the EWMA vols have converged (the January 2018 trades in the backtest are warm-up noise).

- Bridge Monday Long: import from The Bridge's Strategies screen as a **Signal**. Use a 5-minute MNQ chart
  from your normal feed (not the Bridge's bars; it needs Sunday evening), CME full Globex session 17:00–16:00,
  Exchange (Central) time, Bar Magnifier 1 minute, a few months of history for the daily ADX. Never run it
  alone (it trades about once every two weeks; inactivity rule). If an ad-hoc market closure is announced
  for a Monday, don't run it that week (see its header).

**Apex rules** in `../analysis/funded_sim.py` confirmed by the user (2026-10-13). Each challenge costs $50.

**Faster still:** run 2–3 PAs in parallel with the same trades ($13k in total after ~225 / ~200
trading days instead of ~300; see the speed section below).

## Previous plan (2026-10-12): five strategies, Late-Day Flow added

Five MultiCharts-confirmed strategies, sized to the drawdown cushion. Code and numbers:
`analysis/funded_plan_ldf.py` (output in `analysis/funded_plan_ldf_output.txt`).

| Strategy | File | Chart | Funded inputs (full size) | Trades |
|---|---|---|---|---|
| Vault Break | `../apex_strategies/NQ_Vault_Break.txt` | 30 min MNQ | `NumContracts` 3 | ~107 a year |
| Overnight Bias ML (v2) | `NQ_Overnight_Bias_ML.txt` | 15 min MNQ | `RiskPerTrade` 400 | ~38 a year |
| Monday Long | `NQ_Monday_Long.txt` | 5 min MNQ | `NumContracts` 1, `RiskPerTrade` 0 | every Monday, 8:30–15:00 CT |
| Expiration Open Short | `NQ_Expiration_Open_Short.txt` | 5 min MNQ | `RiskPerTrade` 700 | 12 a year |
| **Late-Day Flow (new)** | `NQ_Late_Day_Flow.txt` | 5 min MNQ | `NumContracts` 2, `RiskPerTrade` 0 | ~100 a year, 14:00–14:30 CT |
| ~~Overnight Drift~~ | `NQ_Overnight_Drift.txt` | — | **off** (backup) | — |

**Cushion sizing (part of the plan).** Each morning, before the session: cushion = account
balance − trailing drawdown threshold. Size factor f = cushion / $2,000, kept between 0.5 and
1.0. Multiply each full-size input by f and round down:

| Cushion | f | Vault Break | ONB ML risk | Monday Long | EOS risk | Late-Day Flow |
|---|---|---|---|---|---|---|
| $2,000 or more (always true after the $52,100 lock) | 1.0 | 3 | 400 | 1 | 700 | 2 |
| $1,500 | 0.75 | 2 | 300 | 0 (off) | 525 | 1 |
| $1,000 or less | 0.5 | 1 | 200 | 0 (off) | 350 | 1 |

Monday Long and Late-Day Flow use fixed contracts, not RiskPerTrade: their ATR stops are
about $467 and $235 per MNQ at October 2026 prices, so a small RiskPerTrade would skip most
trades.

**Expected payouts per account** (all MultiCharts trade lists, $7.25/NQ + 1 tick per fill, a
start on every trading day 2018–2026):

| Plan | 1 year | Starts 2023+ | 2 years | Blown (1y / 2y) | Days to 1st payout |
|---|---|---|---|---|---|
| VB 3, ONB ML $400, OND $500, EOS $700 (before Monday Long) | $6,876 | $7,350 | $11,366 | 10% / 11% | 84 |
| VB 3, ONB ML $400, Monday 1 MNQ, EOS $700 (previous plan) | $7,153 | $8,776 | $11,612 | 9% / 10% | 77 |
| **+ Late-Day Flow 2 MNQ (current plan)** | **$7,676** | **$8,606** | **$12,012** | **6% / 4%** | **72** |
| Current plan at fixed size (no cushion sizing) | $7,619 | $7,860 | — | 32% | 42 |

Neighbours (sizes not re-optimized): VB 2 $7,332 / $11,975 (blown 3%); ONB ML $300 $7,352 /
$11,945; EOS $500 $7,509 / $12,226 (blown 1–2%); Late-Day Flow 3 MNQ $7,489 / $11,811. All
within noise of the plan.

**Portfolio at full size, 2018–2026** (standard metrics, `analysis/metrics.py`):

| | Sharpe | Sortino | PF (days) | Calmar | Ulcer | Max DD | $/yr |
|---|---|---|---|---|---|---|---|
| **Current portfolio (5 strategies)** | **2.51** | **4.76** | 1.70 | **4.33** | **1.30** | $3,743 | $16,226 |
| Previous (4 strategies) | 2.35 | 4.36 | 1.68 | 3.51 | 1.55 | $4,082 | $14,339 |
| Late-Day Flow 2 MNQ alone | 1.17 | 2.05 | 1.44 | 0.62 | 1.78 | $3,028 | $1,887 |

Bootstrap (10-day blocks) Sharpe 90% interval: 2.01–3.00 (2018–26), 1.95–3.49 (2023–26). The
real max drawdown ($3,743) is smaller than 99% of shuffled orders of the same days; plan for
about $5,500 typical and $8,200 in a bad order. Daily P&L correlations all ≤ 0.18. Portfolio
by year: 2018 +$2,587, 2019 +$7,257, then +$14,894 to +$24,157 a year (2026 to date +$15,512).

**Why Late-Day Flow:** forced flow (leveraged-ETF rebalancing and last-hour flows follow a big
day's move), MultiCharts-confirmed (895 trades, PF 1.44, every trade matches Python),
uncorrelated with the rest, and it cuts blown accounts from 9–10% to 4–6%. Its long side is
weaker since 2023 (Sharpe 0.59); watch it.

**Risks to watch:** Monday Long is regime-dependent (weak 2018–2022); if it loses for a few
months in a row, Overnight Drift can be switched back on in its place.

**Payouts:** request each payout as soon as the balance is at least $52,100 + the next cap,
with 5 qualifying days ($250+) and the 50% consistency rule met.

**Update 2026-10-13:** NFP Fade and Vol-Control Sell Flow were MultiCharts-confirmed and added (see the
current plan at the top).

## Speed to the full $13,000 (2026-10-13): new priority

Goal: collect all 6 payouts ($13,000) of a PA sooner. Code `../analysis/speed_to_13k.py` and
`../analysis/speed_to_13k_followup.py` (outputs in the matching `_output.txt`). Every start day from
2018 to late 2023, 3-year horizon, the funded-bench simulator. "Median" = median trading days to the
6th payout over all accounts (blown ones count as never); 21 trading days = 1 month.

**Why it takes about 14 months now:** six payouts need $13,000 out plus the $2,100 buffer, at least 30
qualifying days ($250+) and the 50% consistency rule each cycle. At full size the plan makes about
$16,000 a year, so roughly a year is the floor at this size. Faster means more dollars a day (bigger
size or more edge) or more accounts.

| Setup (one account) | Median days to $13k | All 6 within 1 year | Within 2 years | Blown (3 years) | Max MNQ |
|---|---|---|---|---|---|
| **Current plan** (full size at $2,000 cushion) | 306 (≈14.5 months) | 21% | 89% | 1% | 21 |
| Full size from a **$1,500** cushion (available now) | 289 | 31% | 90% | 4% | 21 |
| + NFP Fade $500 + Vol-Control Sell 1 MNQ | 287 | 27% | 88% | 0% | 21 |
| **+ NFP + VCS, full size from $1,500** | **278 (≈13 months)** | **36%** | 89% | 1% | 21 |
| + NFP + VCS + Headline Shock 1, ramp, $1,500 | 270 | 42% | 87% | 2% | 37 |
| Size ramp after payouts (×1.25 after 2, ×1.5 after 3–4, ×1.75 after 5) | 295 | 25% | 88% | 1% | 37 |
| Whole plan × 1.25 | 293 | 28% | 86% | 10% | 26 |
| Whole plan × 1.5 | 267 | 41% | 80% | 20% | — |
| Whole plan × 2 | 320 | 41% | 51% | 49% | — |

- **Bigger size is a bad trade.** × 1.5 saves about 6 weeks but blows 1 account in 5; × 2 is slower
  overall because half the accounts blow up.
- **The size ramp barely helps** (−11 days) and pushes rare days to 37 MNQ, above Apex's contract
  tiers; not recommended.
- **Full size from a $1,500 cushion** is the one change you can make today: f = cushion / $1,500,
  kept between 0.5 and 1 (cushion $1,500 or more: full size; $1,125: 0.75; $750 or less: 0.5).
  −17 days, all-6-within-a-year 21% → 31%, blown 1% → 4%.
- With NFP Fade and Vol-Control Sell Flow (after MultiCharts confirms them): **278 days, 36% within a
  year, blown 1%**.

**The biggest lever: several accounts with the same trades.** Median trading days until one
account's cumulative payouts reach each amount (25-day steps):

| Plan | $3,000 (2 payouts) | $5,000 (3) | $7,500 (4) | $10,000 (5) | $13,000 (6) |
|---|---|---|---|---|---|
| Current plan | 150 | 200 | 225 | 275 | 325 |
| Full size from $1,500 | 150 | 175 | 200 | 250 | 300 |
| + NFP + VCS | 150 | 175 | 225 | 250 | 300 |

$13,000 in total arrives after about **325 days with 1 account, about 225 with 2 accounts** ($7,500
each), **about 200 with 3** ($5,000 each) and **about 150 with 5** ($3,000 each). Each extra account
costs a challenge (about $117 per funded account at a 44% pass rate) plus Apex's account fees, and
every account still goes on to its own $13,000. The catch: identical trades mean the accounts win
and lose together (a bad stretch can blow several at once; at these sizes 1–4% of accounts blow).
Check Apex's current limit on simultaneous PA accounts and its rules on copying trades between
your own accounts before doing this.

**Recommended for speed:** (1) now: full size from a $1,500 cushion; (2) run 2–3 PAs in parallel as
soon as they are funded; (3) add NFP Fade ($500) and Vol-Control Sell Flow (1 MNQ) once the
MultiCharts backtests match (`NQ_NFP_Fade.txt`, `NQ_Vol_Control_Sell.txt`).

Caveats: the $1,500 setting and the add-ons were chosen on the same 2018–2026 history; the add-ons
are Python-only so far.

### Before Late-Day Flow (2026-10-12): Monday Long replaced Overnight Drift

Four MultiCharts-confirmed strategies, sized to the drawdown cushion. Code and numbers:
`analysis/funded_plan_monday.py` (output in `analysis/funded_plan_monday_output.txt`).

| Strategy | File | Chart | Funded inputs (full size) | Trades |
|---|---|---|---|---|
| Vault Break | `../apex_strategies/NQ_Vault_Break.txt` | 30 min MNQ | `NumContracts` 3 | ~107 a year |
| Overnight Bias ML (v2) | `NQ_Overnight_Bias_ML.txt` | 15 min MNQ | `RiskPerTrade` 400 | ~38 a year |
| **Monday Long (new)** | `NQ_Monday_Long.txt` | 5 min MNQ | `NumContracts` 1, `RiskPerTrade` 0 | every Monday, 8:30–15:00 CT |
| Expiration Open Short | `NQ_Expiration_Open_Short.txt` | 5 min MNQ | `RiskPerTrade` 700 | 12 a year |
| ~~Overnight Drift~~ | `NQ_Overnight_Drift.txt` | — | **turn off** (kept as a backup) | — |

**Cushion sizing (part of the plan, not optional).** Each morning, before the session:
cushion = account balance − trailing drawdown threshold. Size factor f = cushion / $2,000,
kept between 0.5 and 1.0. Multiply each full-size input above by f and round down:

| Cushion | f | Vault Break | ONB ML RiskPerTrade | Monday Long | EOS RiskPerTrade |
|---|---|---|---|---|---|
| $2,000 or more (always true after the $52,100 lock) | 1.0 | 3 | 400 | 1 | 700 |
| $1,500 | 0.75 | 2 | 300 | 0 (off) | 525 |
| $1,000 or less | 0.5 | 1 | 200 | 0 (off) | 350 |

Monday Long at 1 MNQ rounds to 0 whenever f < 1, so it only trades when the cushion is
the full $2,000. Use 1 MNQ, not RiskPerTrade: its 0.5 ATR stop is about $467 per MNQ at
October 2026 prices, so RiskPerTrade 300 would skip every trade (it took 284 of 450 in the
test, none in 2026).

**Expected payouts per account** (all MultiCharts trade lists, $7.25/NQ + 1 tick per fill,
a start on every trading day 2018–2026):

| Plan | 1 year | Starts 2023+ | 2 years | Blown (1y / 2y) | All 6 payouts (2y) | Days to 1st payout |
|---|---|---|---|---|---|---|
| Old: VB 3, ONB ML $400, **OND $500**, EOS $700, cushion | $6,876 | $7,350 | $11,366 | 10% / 11% | 84% | 84 |
| **New: VB 3, ONB ML $400, Monday 1 MNQ, EOS $700, cushion** | **$7,153** | **$8,776** | **$11,612** | **9% / 10%** | 87% | 77 |
| New at fixed size (no cushion sizing) | $6,685 | $7,124 | — | 39% | — | 42 |

Neighbours of the chosen sizes (cushion sizing; the sizes were not re-optimized):
VB 2 $6,807 / $12,508 (slower, fewest blowups); VB 4 $6,720 / $9,765 (blown 24%);
ONB ML $500 $7,615 / $11,583; Monday 2 MNQ $7,012 / $10,313 (blown 22%); EOS $900
$7,376 / $11,618. All within noise of the plan except the bigger VB / Monday sizes, which
bring blowups back.

**Portfolio at full size, 2018–2026** (standard metrics, `analysis/metrics.py`):

| | Sharpe | Sortino | PF (days) | Calmar | Ulcer | Max DD | $/yr |
|---|---|---|---|---|---|---|---|
| **New portfolio** | **2.35** | **4.36** | 1.68 | **3.51** | **1.55** | $4,082 | $14,339 |
| Old portfolio (with OND) | 2.16 | 3.79 | 1.53 | 2.46 | 2.04 | $5,377 | $13,213 |
| Monday Long 1 MNQ alone | 1.11 | 1.97 | 1.55 | 1.03 | 1.47 | $2,078 | $2,132 |

Daily P&L correlations in the new set are all ≤ 0.18. New portfolio by year: 2018 +$903, then
+$9,750 to +$19,483 a year (2026 to date +$7,264).

**Why the change:** Overnight Drift was the weak link on every measure (Sharpe 0.40, bootstrap
Sharpe interval including zero, half its edge is generic overnight drift). Monday Long is
MultiCharts-confirmed (450 trades, PF 1.55, 449 of 450 days match Python) and uncorrelated with
the rest. **Risk:** Monday Long is regime-dependent — weak in 2018–2022 (2018 and 2022 lost),
strong since 2023. If it loses for a few months in a row, Overnight Drift can be switched
back on.

**Payouts:** request each payout as soon as the balance is at least $52,100 + the next cap,
with 5 qualifying days ($250+) and the 50% consistency rule met.

---

## History: interim plan of 2026-10-11 (superseded)


> **Status (2026-10-11): interim.** This plan runs the Apex strategies (Vault Break,
> Overnight Bias) at smaller sizes plus Overnight Drift. The Apex strategies were built
> to pass the challenge, not to maximize payouts. They are the benchmark until purpose-built
> funded strategies replace them (see `README.md` in this folder). With 1 tick of
> slippage on every strategy, the Balanced plan's estimate is about $5,400, not $5,900.
> **Update 2026-10-12:** adding the new funded strategy `NQ_Expiration_Open_Short.txt`
> (RiskPerTrade 500, about 12 trades a year) raises the estimate to about $6,500 (see README).

Started 2026-10-11. The goal changes once an account is funded: it is no longer
passing, it is **the money taken out**. A 50K Performance Account (PA) pays at most 6
payouts (caps $1,500 / $1,500 / $2,000 / $2,500 / $2,500 / $3,000 = **$13,000**), then
closes. Everything here is measured as **expected payouts per PA**.

## Short version

- **Do not keep the challenge sizes once funded.** VB 8 MNQ + ONB $1,100 expects only
  **$2,700** in payouts in the PA's first year. 75% of PAs are blown within the year,
  and only 31% ever get a payout.
- **Size down and add the new Overnight Drift strategy** (`NQ_Overnight_Drift.txt`).
  The recommended plan, *Balanced* (VB 3 MNQ, ONB RiskPerTrade $300, OND RiskPerTrade
  $500), expects **$5,900 within 1 year** and $6,800 within 2 years. That is 2.2x
  the challenge sizes, and 65% of PAs get at least one payout.
- **Smaller sizes pay more per PA but take longer.** Slow plans reach $8,000–$9,700
  within 2 years (57–69% collect all 6 payouts), but a payout cycle takes months.
- **Request each payout as soon as the full cap is allowed.** Keeping a buffer of
  $1,000 or more above the cap lowered the expected payouts.
- With the 44% challenge pass rate, every $50 challenge bought is worth about
  **$2,550 in expected payouts within a year** with Balanced, against $1,125 with the
  challenge sizes.

## Rules modelled (`analysis/funded_sim.py`)

From the payout pages you sent (50K EOD):
- Since the last payout (or the start): at least **5 days with $250+ profit**, balance at
  least **$52,600**, and **50% consistency** (best day < 50% of the profit since the last
  payout; losing days reduce that profit).
- A payout is $500 minimum and at most the cap for its number. It cannot take the
  balance below the **$52,100 safety net**. Maximum 6 payouts, then the PA closes.

From Apex's help center as quoted by third-party guides. The help center itself was
not reachable from here (**confirmed by the user on 2026-10-13**):
- $2,000 drawdown trailing the end-of-day balance, locking at $50,100 once the balance
  closes at $52,100. Open equity touching it closes the PA.
- Daily loss limit: $1,000 under $3,000 profit, $2,000 from $3,000, $3,000 from
  $6,000. It liquidates and ends the day; the PA stays open.
- Contract cap: 2 NQ (20 MNQ) under $1,500 profit, then 3, then 4. Every plan below
  stays under 20 MNQ.

**What this means:** after the lock, the drawdown is fixed at $50,100 and each payout
resets the balance to about $52,100. So every payout cycle is the same game: make the
cap (plus 5 qualifying days and the consistency rule) before losing $2,000. Smaller
sizes win that game more often but more slowly. The edge (profit per unit of risk) is
what moves the whole trade-off, which is why a low-correlation fourth strategy matters
more here than in the challenge.

## The new strategy: Overnight Drift (`NQ_Overnight_Drift.txt`)

**Rule:** if the previous regular session closed down (15:00 close below the 8:30
close), buy at midnight CT and sell at the close of the 3:00 bar. Stop = 30% of the
15-day ATR (the same ATR as VB/ONB), no target. Sized by `RiskPerTrade` like ONB.

**Why it should work:** Boyarchenko, Larsen & Whelan, *The Overnight Drift* (Review of
Financial Studies, 2023). US index futures earn a large part of their return in the
early overnight hours around the European open, and more so after US sell-offs: dealers
who absorbed the day's selling are paid to carry the inventory overnight. It is a
structural pattern, not a market regime. It trades while VB/ONB/OD are flat.

| Per NQ, after $7.25 costs (Python, 2018–2026) | Trades | Win | Avg | PF | Years + |
|---|---|---|---|---|---|
| **As specified** (stop 30% ATR, out 3:00, down days only) | 1,041 | 55% | $83 | 1.25 | 8 of 9 |
| Stop 20% / 50% ATR / no stop | 1,041 | 53–55% | $59 / $89 / $91 | 1.18 / 1.28 / 1.29 | 7–8 |
| Out 2:00 / 2:30 / 4:00 | 1,041 | 53–55% | $47 / $82 / $74 | 1.19 / 1.28 / 1.18 | 7–8 |
| Every night (no down-day filter) | 2,255 | 53% | $46 | 1.15 | 6 |

By year: 2018 −$47, 2019 $45, 2020 $87, 2021 $136, 2022 $83, 2023 $19, 2024 $2, 2025
$194, 2026 $260. **2023–24 were flat**, so it is not a smooth earner on its own.

Daily P&L correlation: **0.06 with Vault Break, −0.06 with Overnight Bias, −0.05 with
Opening Drive** (the lowest of any strategy in the repo).

The chosen settings (midnight to 3:00, 30% stop) come from a coarse hour-by-hour grid,
so they are partly fitted. The down-day filter comes from the paper, not from the data.

## Expected payouts per PA

PAs started on every real trading day, walking the real days that followed (whole
MNQ, the same paths and costs as the challenge simulations). "Days to 1st" is the
typical number of trading days to the first payout.

**Payouts within 1 year (250 trading days):**

| Plan | Expected | Starts 2018–22 | Starts 2023+ | All 6 | Blown | Any payout | Days to 1st |
|---|---|---|---|---|---|---|---|
| Challenge sizes: VB 8, ONB $1,100 | $2,671 | $2,264 | $3,396 | 10% | 75% | 31% | 16 |
| Fast: VB 4, ONB $500, OND $500 | $4,495 | $4,328 | $4,791 | 22% | 61% | 49% | 26 |
| **Balanced: VB 3, ONB $300, OND $500** | **$5,919** | $6,000 | $5,776 | 16% | 45% | 65% | 50 |
| Balanced without OND | $4,941 | $4,777 | $5,232 | 8% | 45% | 66% | 53 |
| Slow: VB 2, ONB $300, OND $500 | $5,997 | $6,123 | $5,772 | 9% | 35% | 73% | 63 |
| Slow without OND | $4,620 | $4,391 | $5,028 | 5% | 35% | 74% | 71 |
| Slowest: VB 1, ONB $300, OND $300 | $4,458 | $4,180 | $4,954 | 0% | 21% | 83% | 93 |

**Payouts within 2 years (500 days; starts only through late 2024):**

| Plan | Expected | Starts 2018–22 | Starts 2023–24 | All 6 | Blown |
|---|---|---|---|---|---|
| Challenge sizes | $3,012 | $3,009 | $3,020 | 22% | 78% |
| Fast | $4,623 | $5,189 | $3,081 | 34% | 66% |
| **Balanced** | **$6,823** | $7,990 | $3,645 | 49% | 51% |
| Balanced without OND | $7,002 | $7,847 | $4,698 | 52% | 48% |
| Slow | $8,024 | $9,361 | $4,381 | 57% | 43% |
| Slow without OND | $8,118 | $8,914 | $5,947 | 60% | 40% |
| Slowest | $9,704 | $9,939 | $9,063 | 69% | 27% |

- Overnight Drift adds about **$1,000–1,400 per PA within the first year**. Over 2 years
  it adds nothing, because the 2-year window ends with 2023–24 starts, its two flat
  years.
- **No-edge check:** with each strategy's average trade removed, both the challenge
  sizes and Balanced expect about $440, and 96–97% are blown. Almost all of the
  payouts come from the strategies' edge, not from the rules.
- PAs started in 2018 earn little in every plan ($190–$400 within a year): late-2018
  sell-off and the weakest year for VB and OND.

## Payout timing (Balanced, 1 year)

| Request the payout when the balance reaches | Expected | Blown |
|---|---|---|
| **Safety net + cap (take it as soon as allowed)** | $5,919 | 45% |
| Safety net + cap + $500 | $5,982 | 42% |
| Safety net + cap + $1,000 | $5,744 | 41% |
| Safety net + cap + $2,000 | $5,089 | 39% |

Take the full cap as soon as it is allowed (or leave up to about $500). Waiting longer
saves a few PAs but loses more in payouts. The consistency rule costs little in
expected payouts ($6,086 without it vs $5,919). It mostly delays payouts, which keeps
a bit more cushion in the account.

## Tested and dropped for the funded phase

| Idea | Result (1 year) |
|---|---|
| Size with the cushion (contracts ∝ balance − threshold) | Worse at every setting tried (e.g. VB 4 + ONB $500: $4,291 fixed vs $3,041–3,935) |
| Bigger size before the first payout (to lock faster) | Worse ($4,495 → $4,154 at 1.5x) |
| Smaller size before the first payout (0.75x) | Better ($4,495 → $5,201), the same as simply trading smaller |
| Size up for payouts 4–6 (bigger caps) | Slightly worse ($4,401 vs $4,495) |
| ONB target 2R or 1.5R instead of 3R | Worse (VB 4 + ONB $500: 3R $4,291, 2R $4,011, 1.5R $3,762) |
| Adding Opening Drive (1 MNQ) | Mixed: −$400 to +$80 against the same plan without it |
| Fixed 1 MNQ for ONB and OND instead of RiskPerTrade | Worse within 1 year ($5,064 vs $5,919) |

## Recommended funded setup

On the day the challenge passes, change the inputs (do not reuse the challenge sizes):

| Strategy | File | Chart | Funded inputs | At October 2026 prices |
|---|---|---|---|---|
| Vault Break | `../apex_strategies/NQ_Vault_Break.txt` | 30 min MNQ | `NumContracts` 3 | 3 MNQ |
| Overnight Bias | `../apex_strategies/NQ_Overnight_Bias.txt` | 15 min MNQ | `RiskPerTrade` 300 | 1 MNQ (0 = skipped when the stop is over $300, i.e. 15-day ATR above 500 points) |
| Overnight Drift (new) | `NQ_Overnight_Drift.txt` | 5 min MNQ | `RiskPerTrade` 500 | 1 MNQ |

- Request a payout as soon as the balance is at least $52,100 + the next cap, with
  5 qualifying days and consistency met.
- Choose **Slow** (VB 2) instead if expected payouts per PA matter more than time. It
  gets the first payout about 3 months in, and averages $8,000 within 2 years.
- Choose **Fast** (VB 4, ONB $500) if you would rather get to the first payout in about
  5 weeks and recycle accounts quickly.

## Next steps

1. **Backtest Overnight Drift in MultiCharts:** 5-minute @NQ chart, CME 24-hour
   session, Exchange time zone, Bar Magnifier 1 minute, from 2 Jan 2018,
   `RiskPerTrade` 0, `NumContracts` 1, no commission/slippage. Entries should be stamped
   at the bar after midnight and exits at 3:00. Save the report as
   `Backtesting Strategy Performance Report OND v1.xlsx` in the repo root;
   `analysis/funded24.py` then uses it instead of the Python version.
2. Check the assumed rules (trailing/lock, daily loss limit tiers, contract tiers) on
   Apex's help center. If any differ, change the constants at the top of
   `analysis/funded_sim.py` and re-run.
3. Re-run: `python3 analysis/funded24.py` (about 1 minute).
4. Sim-trade Overnight Drift on Paper Trader alongside the other two. It trades
   midnight–3:00 CT, so the auto-trading PC must be on overnight.

## Caveats

- Overnight Drift is a Python backtest only, and 2023–24 were flat for it.
- All the numbers are estimates from one 2018–2026 history; neighbouring start days
  share most of the same trades. The differences between Balanced and Slow within 1
  year are inside the noise.
- The model assumes live fills like the backtest. Overnight liquidity is thinner, so
  expect some extra slippage on Overnight Drift's stop.
