# Funded phase plan: Apex 50K EOD Performance Account

## Account and growth plan (agreed 2026-10-16)

Priority order (details in the sections below and in `../reports/Trading_Business_Plan.pdf`):
1. **Prove the edge live** on 3 accounts: #1 50K EOD (since 2026-10-12), #2 50K EOD (Tue 10/20), #3 150K No-Activation
   (~10/27, tests the 150K settings). Single evaluations 5–10 trading days apart (5-pack evaluations all start at purchase).
   Gate ~mid-December: ~40–70 live plan trades at ≥ 75% of backtest, no ALARM.
2. **Scale Apex with 150K No-Activation** ($249): ~$20k evaluation budget, +2 accounts a week to 20; 50K slots switch to 150K
   after their first funded account pays all 6 ($13,000) or blows; pause additions if cumulative cash falls below −$20k.
   Year 1 ~$175k, 3 years ~$1.03M (backtest; 75% edge ~$96k / $743k) — 'Ramp to 20 with 150K No-Activation accounts'.
   +3 a week instead of +2 (`../analysis/ramp150_speed_test.py`, #3 as 150K): year 1 $188k vs $182k, 3 years $1.049M vs
   $1.031M, worst cash p10 −$20.8k vs −$20.0k; at 75% edge identical ($98k vs $99k). Either is fine; +3 reaches 20 ~3 weeks sooner.
3. **Personal account from the first Apex payouts** (expected ~Feb 2027): ~$10k at 1/10 size, stepping up with the balance
   (~$25k = 1/4, ~$50k = 1/2, ~$100k = full 1 NQ). Per dollar, Apex evaluations earn far more in year 1, so the personal
   account is funded from payouts, not savings.

## Relative Strength NQ / ES added (2026-10-20)

The user's RelStrength_v3 (`NQ_Relative_Strength.txt`; research `../analysis/relative_strength_test.py`, checker PASS WITH
CONCERNS, TIER_LIST B): at 9:00 CT, NQ's move since 8:30 beyond its ES beta as a Z score; |Z| >= 1.25 follow at 9:01, stop
0.6 / target 1.0 x the 20-day average RTH range, flat 15:00. Per NQ 2018-26: $306 a trade, PF 1.36, t 4.0, 9/9 years.
Included in every plan where it helps (`../analysis/relative_strength_bench.py`, `../analysis/relative_strength_plans_test.py`):

| Plan | RS setting | Effect | Decision |
|---|---|---|---|
| 50K funded (bootstrapped bench, 1,000 histories) | **longs only, 1 MNQ** (`TradeDir` 1) | y1 $9,294 vs $8,810, median days to 6 payouts 258 vs 278, blown 7.7% vs 7.2% (both sides 1 MNQ: 250 days but blown +1.3 pt; 2 MNQ blown 34%) | **in the plan** |
| 150K funded (plan x 1.5, full from $3,000; single history) | **both sides, 1 MNQ** (`TradeDir` 0) | 1y $16,705 vs $16,067, 2y $20,038 vs $19,808, blown 0%, all 6 payouts 95% vs 93% (4 MNQ blows 20%) | **in the plan** |
| 50K evaluation | - | pass 50.1% -> 47.5% (1 MNQ both) / 48.8% (longs 1) | not used |
| 150K evaluation (combine set x 2.5) | - | pass 41.6% -> 40.5% (2 MNQ) / 41.4% (longs 2-3) | not used |
| Personal account | both sides, ~1 MNQ per $25,000 | 1 NQ: ~$39.6k a year, max DD $28.5k (Monte Carlo 95% $66k) | in the personal plan |

Cushion sizing: RS is 1 MNQ, so it is off (0) while f < 1 (cushion under $1,500 on 50K, under $3,000 on 150K). MultiCharts
confirmation skipped by the user (no backtests while trading live); the user's own MultiCharts run in the research note
matches the rebuild (PF 1.37 vs 1.38 before costs, longs PF 1.46 both). Live: the drift alarm decides (`../live/README.md`).

## Overnight Tick / VIX added to the funded plans (user, 2026-10-24)

The user's 'NQ Overnight Anomaly Strategy Optimized' (`NQ_Overnight_Tick_VIX.txt`; research `../analysis/overnight_tick_test.py`,
checker PASS WITH CONCERNS, **MultiCharts-confirmed**: 529 same nights, P&L corr 1.000; TIER_LIST A): after a down RTH
session (no early close), long 17:05 → 03:00 CT when (order-flow imbalance 14:15-15:15 CT < 0 and VIX > SMA 25) or (≥ 0 and
VIX ≤ SMA 25). Per NQ 2018 → 2026-07: $374 a trade, PF 1.98, t 5.2, 9/9 years, max DD $12.8k. Inside one Apex trading day.

| Plan | Setting | Effect (`../analysis/overnight_tick_bench.py`, bootstrapped 500 paired 2-year histories) | Decision |
|---|---|---|---|
| **50K funded** | **1 MNQ in place of the Monday Long** | 1y $9,818 vs $9,152, 2y $12,182 vs $11,994 (+$188, t 1.7), blown 6.4% vs 8.0%, 6th payout day 244 vs 262 | **in the plan** |
| **150K funded** (x 1.5 + RS 1 + DT 2) | **+ 2 MNQ** (Monday Long stays) | 1y $17,817 vs $16,879 (bad case $8,500 vs $5,500), 6th payout day 214 vs 228, blown 2.0% vs 2.6%, 2y +$138 (cap-bound) | **in the plan** |
| 50K / 150K evaluations | - | 50.7% vs 50.1% (2 MNQ) / 42.4% vs 41.6% (3 MNQ): a tie | not used |
| Personal | in place of Overnight Anomaly | core 16 return/DD 9.2 → 9.6 | in the personal plan |

Cushion sizing: 50K 1 MNQ, off while f < 1 (like RS); 150K 2 MNQ, 1 below a $3,000 cushion. **VIX:** dxFeed has no VIX
index: Data2 = `VIX_CBOE`, Map ASCII of `C:\TradingData\VIX\VIX_daily.csv`, refreshed each weekday by `../tools/vix_update.ps1`
(Cboe, Yahoo for the same day's close). If the day's VIX is missing the signal uses the previous day's (backtest $309 vs $374
per NQ). Watch: the 24 MultiCharts trades after 2026-07-07 (no order-flow data in our rebuild) averaged −$280 per NQ.

## Dual Thrust added to the 150K funded plan (user, 2026-10-24)

The user's Dual Thrust v4 (`NQ_Dual_Thrust.txt`; research `../analysis/dual_thrust_test.py`, checker PASS WITH CONCERNS,
TIER_LIST A): prior RTH day RR = max(high - close, close - low); the first 1-minute close beyond today's 08:31 open
± 0.5 RR (08:31-14:30) enters at the next bar, one trade a day, stop 50 / target 100 points, out 14:56, day skipped if
RR / ADR20 > 1.2. Per NQ 2018-26: $140 a trade, PF 1.28, t 4.4, 9/9 years, max DD $19.6k.

| Plan | DT setting | Effect | Decision |
|---|---|---|---|
| **150K funded** (plan x 1.5 + RS 1 MNQ, full size from $3,000; bootstrapped, 500 paired 2-year histories) | **2 MNQ, both sides** | 1y $17,024 vs $15,620 (bad case p5 $8,350 vs $5,500), all 6 payouts by day 226 vs 250, blown 2.2% vs 1.8%; 2y $20,077 vs $20,126 (both at the $20,500 cap) | **in the plan** |
| 150K funded, single history (every start day from 2018) | 2 MNQ | 1y $17,363 vs $16,707, 2y $20,285 vs $20,038, blown 0%, 6th payout day 216 vs 228 | |
| 150K funded, other sizes | 1 / 3 / 4 MNQ | 1 MNQ: 6th payout day 241, blown 1.4%; 3 MNQ blown 3.6%; 4 MNQ blown 7.6% | not used |
| 50K funded (1,000 histories) | - | + 1 MNQ −$124; best swap VB 2/1 -> 1/1 + DT 1 +$106 (t 1.1, a tie) | not used |
| 50K / 150K evaluation | - | 50K 50.1% -> 48.5-48.9%; 150K 41.6% -> 41.2% (2-3 MNQ) | not used |
| Personal account | 1 micro per portfolio unit | +$2,400 a year, Sharpe 2.97 -> 3.00, return/DD 7.8 -> 8.2, capital $23.0k -> $25.0k | in the personal plan |

Why it helps only the 150K: the 150K plan reaches its $20,500 cap within 2 years in nearly every history, so DT can only
make it faster; its ~$5,000-a-year at 2 MNQ fits the 150K's $4,000 drawdown but not the 50K's $2,000. Cushion sizing:
1 MNQ while the cushion is below $3,000 (f = 0.5), 2 MNQ from there. **Before the first 150K funded account starts:**
the user's MultiCharts report of v4 for the trade-by-trade check (`../TODO.md`); live, the drift alarm decides.
Code `../analysis/dual_thrust_150k_test.py`, output `../analysis/outputs/dual_thrust_150k_output.txt`.

## Current plan (updated 2026-10-13): seven strategies (Vol-Control Sell dropped), faster to $13k

Priority: collect all 6 payouts ($13,000) sooner. **New: the Bridge's Monday Long NQ** (it ships with The Bridge,
Strategies screen, `L644NQ_MondayLong_NQ` v2.1), MultiCharts-confirmed (`../analysis/bridge_monday_confirm.py`,
output in `..._output.txt`). It runs next to our Monday Long, not instead of it. NFP Fade and Vol-Control Sell
Flow are MultiCharts-confirmed (`../analysis/nfp_vcs_confirm.py`); full size starts at a **$1,500** cushion.

**Adopted 2026-10-15 (MultiCharts-confirmed: 262 / 274 flagged days identical, no false skips):** Vault Break via `../apex_strategies/NQ_Vault_Break_SP.txt` with
`NumContracts` 3 (**2 since 2026-10-17**, see 'Bootstrapped bench' below), `FlaggedContracts` 1 (1 MNQ on the session after an interior TPO single print; `TIER_LIST.md`, B):
1-year $10,184 vs $9,818, blown 3% vs 4%; beats every random-day placebo. Combine: leave `FlaggedContracts` -1.

| Strategy | File | Chart | Funded inputs (full size) | Trades |
|---|---|---|---|---|
| Vault Break | `../apex_strategies/NQ_Vault_Break_SP.txt` | 30 min MNQ | **`NumContracts` 2**, `FlaggedContracts` 1 (was 3 / 1 until 2026-10-17) | ~107 a year |
| Overnight Bias ML (v2) | `NQ_Overnight_Bias_ML.txt` | 15 min MNQ | `RiskPerTrade` 400 | ~38 a year |
| ~~Monday Long~~ **50K: replaced 2026-10-24** by Overnight Tick / VIX (150K keeps it at 1) | `NQ_Monday_Long.txt` | 5 min MNQ | `NumContracts` 1, `RiskPerTrade` 0 | every Monday |
| **Overnight Tick / VIX (2026-10-24)** | `NQ_Overnight_Tick_VIX.txt` | 5 min MNQ + VIX daily (Data2, Map ASCII) | `NumContracts` 1 | ~60 a year (17:05 → 03:00 CT after down days) |
| Expiration Open Short | `NQ_Expiration_Open_Short.txt` | 5 min MNQ | `RiskPerTrade` 700 | 12 a year |
| Late-Day Flow | `NQ_Late_Day_Flow.txt` | 5 min MNQ | `NumContracts` 2, `RiskPerTrade` 0 | ~100 a year |
| NFP Fade | `NQ_NFP_Fade.txt` | 5 min MNQ | `RiskPerTrade` 500 | ~9 a year (payroll Fridays, 7:45–9:00 CT) |
| Vol-Control Sell Flow | `NQ_Vol_Control_Sell.txt` | 5 min MNQ + **5 min @ES as data2** | `NumContracts` 1, `RiskPerTrade` 0 | ~8 a year (14:00–15:00 CT, shorts) |
| ~~Vol-Control Sell Flow~~ **dropped 2026-10-13** | — | — | — | without it: $9,313 / $12,569, blown 2% / 1%, median 255 days (with it: $9,313 / $12,436, 3% / 1%, 255); it adds nothing next to the Bridge Monday Long and needs @ES data2 (`../analysis/funded_today_check.py` and the session note) |
| **Bridge Monday Long (new)** | The Bridge → Strategies → `L644NQ_MondayLong_NQ` (import as a Signal) | 5 min MNQ, full Globex session, Exchange time | `NumContracts` 1, defaults otherwise (`TargetPts` 100, `StopPts` 0) | ~25 a year (Sunday 19:00 CT → Monday 15:55) |

**Other candidates checked 2026-10-13** (`../analysis/funded_today_check.py`): DriftPullback shorts 1 MNQ (Python
replica, not MC-confirmed) $9,453 / $12,492, blown 4% / 2%, median days to all 6 payouts 245 (vs 255), all 6 within
a year 51% (vs 48%). Within noise on money and speed, slightly more blowups, and the shorts are weak since 2023 ($20 a trade,
P(Sharpe <= 0) 28%): not worth adding (watch item only). No change: VCS 2 MNQ (blown 10%), Bridge Monday 2
MNQ (blown 11–12%), EOS $500 (slower, 269 days), dropping our Monday Long (274 days).

**Cushion sizing:** cushion = balance − trailing threshold, each morning. f = cushion / **$1,500**,
kept between 0.5 and 1; multiply each full-size input by f and round down:

| Cushion | f | VB normal / flagged | ONB ML risk | OT / VIX | EOS risk | LDF | NFP risk | Bridge Monday | CL Sunday | ES MOC | RS longs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| $1,500 or more | 1.0 | 2 / 1 | 400 | 1 | 700 | 2 | 500 | 1 | 2 MCL | 2 MES | 1 |
| $1,125 | 0.75 | 1 / 0 | 300 | 0 (off) | 525 | 1 | 375 | 0 (off) | 1 MCL | 1 MES | 0 (off) |
| $750 or less | 0.5 | 1 / 0 | 200 | 0 (off) | 350 | 1 | 250 | 0 (off) | 1 MCL | 1 MES | 0 (off) |

(Table updated 2026-10-23 to the current 10-strategy plan; the old one still listed VB 3 and VCS.) Any cushion in between:
f = cushion / 1,500, multiply, round DOWN to whole contracts (risk inputs: multiply, no rounding). Evaluations (combines)
are NOT cushion-sized: they run the combine set at fixed size.

**Automatic cushion sizing (planned 2026-10-23, user asked).** MultiCharts can't read Apex's dashboard, so automation
depends on Rithmic reporting the account balance to MultiCharts. Step 1 (now, on an evaluation account; nothing trades):
put `../tools/checks/Apex_Account_Check.txt` (indicator, no orders) on a live chart and compare its NetWorth line with the
Apex balance. If they match, step 2: one shared function used by every funded signal:
- threshold = max(threshold, end-of-day balance − $2,000), locked at start + $100 once reached (Apex's EOD trail); seeded
  by an input `StartThreshold` (today's threshold from the dashboard) so a chart restart doesn't lose it;
- f = (balance at the session open − threshold) / $1,500, between 0.5 and 1, frozen for the day;
- each signal's contracts = floor(full size × f), risk inputs × f; a missing or zero balance falls back to f = 0.5 and
  prints a warning.
It is compared with the manual table for a week (paper) before it replaces the morning routine. Until a funded account
exists (earliest ~December), the manual table above is the method.

The Bridge Monday Long enters on Sunday evening, so use Sunday's cushion (Friday's close balance) for it.

| All MultiCharts trade lists, $7.25 + 1 tick per fill | 1 year | 2 years | Blown (1y / 2y) | Median days to all 6 payouts | All 6 within 1 year |
|---|---|---|---|---|---|
| Previous plan (5 strategies, $2,000 cushion) | $7,676 | $12,012 | 6% / 4% | 306 | 21% |
| Previous plan (7 strategies, $1,500 cushion) | $8,770 | $12,236 | 3% / 2% | 278 | 36% |
| Plan with 8 strategies (+ Bridge Monday Long 1 MNQ) | $9,313 | $12,436 | 3% / 1% | 255 | 48% |
| **Current plan (7: the 8 without Vol-Control Sell)** | **$9,313** | **$12,569** | **2% / 1%** | **255** | **47%** |

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
`analysis/funded_plan_ldf.py` (output in `analysis/outputs/funded_plan_ldf_output.txt`).

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
`analysis/funded_plan_monday.py` (output in `analysis/outputs/funded_plan_monday_output.txt`).

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
- **Rechecked against the user's Apex dashboard on 2026-10-15:** $2,000 drawdown, 5 days of $250+,
  safety net $52,100, minimum balance to request $52,600, 6 payouts then the account closes.
  All match `funded_sim.py`; no change to the bench numbers.

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
   `mc_reports/Backtesting Strategy Performance Report OND v1.xlsx`;
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

## CL Sunday Gap Fade added (2026-10-14)

First strategy on another market: `CL_Sunday_Gap_Fade.txt` on a 5-minute **MCL** chart (Eastern exchange time,
`NumContracts` 2, `ExitTime` 1000 = 9:00 CT). MultiCharts-confirmed (96/97 trades). Trades about 11 Sundays a year
(17:05 CT → Monday 9:00 CT, stop 0.75 ATR); uncorrelated with the NQ strategies (≤ 0.08). Funded bench: $9,818 (1y) /
$12,595 (2y) vs $9,313 / $12,569, blown 4% / 2%, median days to all 6 payouts 255 → 239. Check that Apex allows
MCL on the account before turning it on; it runs on its own chart and the copier like the other funded strategies.

## Monte Carlo at plan size (2026-10-17)

`analysis/plan_montecarlo_test.py` (output `analysis/outputs/plan_montecarlo_test_output.txt`) runs `analysis/montecarlo.py` on every
plan strategy at its funded size (full size, i.e. a cushion of $1,500 or more) and on the whole plan. The bench reproduces
exactly ($10,184 / $12,450, blown 3% / 3%).

| Strategy (size) | Trades | Max DD actual | Reshuffled DD p95 | One year p5 / p50 | P(losing year) | P(hit $2,000 trail in a year, alone) |
|---|---|---|---|---|---|---|
| Vault Break (3 / 1 flagged) | 942 | $3,509 | $7,106 | −$136 / $5,152 | 5.4% | 28.6% |
| Overnight Bias ML v2 ($400) | 343 | $2,417 | $3,814 | $439 / $4,225 | 3.1% | 6.4% |
| Monday Long (1) | 450 | $2,078 | $4,430 | −$887 / $2,029 | 12.9% | 11.1% |
| Expiration Open Short ($700) | 105 | $1,362 | $4,666 | −$1,143 / $2,432 | 13.6% | 9.9% |
| Late-Day Flow (2) | 895 | $3,028 | $3,579 | −$766 / $1,846 | 12.8% | 6.9% |
| NFP Fade ($500) | 78 | $2,034 | $2,332 | −$719 / $331 | 31.3% | 0.0% |
| Bridge Monday Long (1) | 217 | $1,683 | $2,161 | −$195 / $1,310 | 7.4% | 0.1% |
| CL Sunday fade (2 MCL) | 96 | $1,031 | $2,111 | −$519 / $1,059 | 15.3% | 0.2% |
| **Whole plan, full size** | 1,700 | $3,963 | $6,989 | $8,955 / $18,857 | 0.1% | 22.7% |

What it says:
- **The cushion sizing carries the risk control.** The whole plan at full size with no cushion rule would hit the $2,000
  EOD trail in about 23% of years (2023 onward the same); the bench, with half size below a $1,500 cushion, blows 3%.
  Keep the cushion rule exactly as set; never run the funded plan at full size from a fresh account.
- **Vault Break is the plan's main drawdown source** (alone 28.6% / year at 3 MNQ; reshuffled DD p95 $7,106). It is also
  the largest earner ($5,134 / yr), so it stays, but it is the first thing to cut if the drift alarm fires.
- **NFP Fade adds little:** $375 / yr, Sharpe 0.53, P(losing year) 31%, its 10-trade losing streak was above the reshuffled
  p95 (9) and its drawdown at the 91st percentile (2018–22; 2023 onward it is fine, Sharpe 0.96). It costs no trail risk.
  No change (it is a pre-registered forced-flow item), but it is the weakest line to watch live.
- **Overnight Bias ML longs lost all of 2018** (−$2,491; max DD $3,916 is worse than 99% of reshuffles, so the losses
  cluster in time); positive every year since. Shorts have no such cluster. A regime, not a broken rule; the drift alarm
  covers a repeat.
- Every strategy's whole-period total is positive in ≥ 95% of reshuffles (NFP 94.7%); every strategy's Sharpe 5th
  percentile on 2023 onward is above 0.

## Bootstrapped bench: realistic numbers and a better sizing (2026-10-17)

`analysis/funded_bootstrap.py` runs the same Apex PA simulator on 600-1,000 resampled histories (20-day blocks of whole
trading days, all strategies kept together; paired across plans). Check: on the real, unshuffled history it reproduces
the old bench exactly ($12,433, blown 3.1%).

**Realistic plan numbers** (the old single-history bench in brackets):

| | 1 year | 2 years | Blown (2y) | All 6 payouts in 2y | Median days to 6th payout |
|---|---|---|---|---|---|
| Current plan (VB 3 / 1) | ~$8,450 ($10,184) | ~$11,200 ($12,450) | **12-16%** (3%) | 83-86% | ~279 (229) |

The real 2018-26 order of days was kind to the plan. Budget for roughly 1 in 7 funded accounts blowing within 2 years,
and about 13 months to all 6 payouts.

**Decisions on paired histories** (2-year payouts / blown; three block lengths and seeds agree):

| Plan | 2 years | Blown | Days to 6 | vs plan |
|---|---|---|---|---|
| Current (VB 3 / 1) | $11,032-11,508 | 11-16% | ~279 | - |
| VB 2 / 1 | +$481 to +$701 | **−4 to −6 pts** | +6 to +12 | safer, slightly slower |
| **VB 2 / 1 + ES MOC follow 2 MES** | **+$762 to +$878** | **−6 to −7 pts (5-9%)** | **−3 to −9** | safer AND as fast or faster |
| Drop NFP | −$102 | +0.5 pt | +9 | a wash (NOT the 3% → 8% the single history showed) |
| Cushion ref $2,000 (VB 2 / 1) | +$315 | 3.6% | +25 | safest, slower |
| Cushion ref $1,000 | −$966 | 23% | ≈ | worse |

**Decided 2026-10-17 (user): ES MOC Follow is in the funded plan at 2 MES** (MultiCharts-confirmed 199/199). **Decided 2026-10-17 (user): Vault Break funded size 2 / 1** (`NumContracts` 2, `FlaggedContracts` 1).

**Recommendation for the funded phase:**
1. **VB 2 / 1 instead of 3 / 1** (adopted). This only changes `NumContracts`, ready when an account goes funded.
2. **Add ES MOC follow at 2 MES.**
   - It is a B-rated forced flow: $158 per ES, t 3.5, uncorrelated with the plan.
   - It needs, before use: a MultiCharts version and its confirmation, a blind check, and confirmation that Apex allows
     MES.

The evaluation set is unchanged: this is about the funded account only.

## How many accounts to run: the full pipeline (2026-10-14)

Code `../analysis/account_pipeline_test.py` (output in `..._output.txt`). Each "slot" cycles through:
- buy a 50K challenge ($50 a try) with the combine set (VB 8 + ONB ADX30 $1,100 + Bridge Monday 2 + EOS $500; pass
  50.1%, median 6 days a try);
- on a pass, activate a funded PA ($0 / $85 / $140 tested) and run the 7-strategy funded plan (full size from a
  $1,500 cushion) until the 6th payout or until it is blown;
- then the next challenge.

N slots run in parallel, started together or staggered. 70 start months 2018-01 → 2023-10, 3-year windows, real day
order. Accounts with the same strategies get the same trades, so their correlation is whatever the real history
gives.

**With the backtest edge as it is** (activation $85, medians over start months):

| Slots | Net after 6 months | 12 months | 24 months | 36 months | Months to $13k net | Worst cash point | Challenges / funded over 3 years |
|---|---|---|---|---|---|---|---|
| 1 | $1,365 | $9,865 | $20,180 | $28,545 | 17.6 | −$160 | 6 / 3 |
| 2 | $2,730 | $19,730 | $40,360 | $57,090 | 9.4 | −$320 | 12 / 6 |
| 3 | $4,095 | $29,595 | $60,540 | $85,635 | 8.2 | −$480 | 18 / 9 |
| 5 | $6,825 | $49,325 | $100,900 | $142,725 | 7.0 | −$800 | 30 / 15 |
| 10 (staggered 10 days) | $6,725 | $62,700 | $174,525 | $283,300 | 7.3 | −$1,280 | 62 / 30 |

- About $790–800 a month per slot, nearly linear in the number of slots, because the backtest funded plan almost
  never blows (median 0 blown over 3 years).
- Fees hardly matter: $0 vs $140 activation changes 3-year results by about 1%.
- Staggering the starts changes little. Starting together is faster (accounts pass on the same days); a 10-day
  stagger spreads the risk.

**Stress test, the edge assumed weaker live** (each strategy's average daily profit cut by 25% or 50%, volatility
unchanged; activation $85, stagger 10 days):

| Edge kept | Challenge pass | Funded PA: all 6 / blown | Slots | Net 12 months (10th pct) | Net 36 months (10th pct) | Worst cash, 10th pct | Months to $13k |
|---|---|---|---|---|---|---|---|
| 75% | 40.7% | 77% / 23% | 1 | $3,740 (−$638) | $20,055 ($9,545) | −$642 | 25.4 |
| 75% | | | 3 | $10,110 (−$1,720) | $60,165 ($28,616) | −$1,806 | 12.8 |
| 75% | | | 5 | $15,955 (−$2,685) | $101,575 ($47,718) | −$2,825 | 10.8 |
| 50% | 34.3% | 38% / 61% | 1 | $1,755 (−$920) | $13,852 ($4,606) | −$1,608 | 32.1 |
| 50% | | | 3 | $4,735 (−$2,565) | $41,508 ($13,852) | −$4,794 | 16.6 |
| 50% | | | 5 | $9,045 (−$4,248) | $69,048 ($23,158) | −$7,917 | 13.3 |
| 50% | | | 10 | $17,192 (−$7,996) | $134,552 ($47,828) | −$14,322 | 11.4 |

- Even at half the edge, every slot count is positive over 3 years in the median and at the 10th percentile. But
  the first year can be negative (10th percentile −$2.6k to −$8k for 3–10 slots), and the fees you might spend
  before the payouts arrive grow with the number of slots.
- Blow-up clustering is mild: with 5 slots, 3+ funded accounts blew within the same 10 days in 0–3% of start
  months.

**Recommendation:**
1. **Start with 3 slots** (3 challenges at a time; each pass becomes a funded account; each finished or blown
   account is replaced by a new challenge). Median about $30k net in the first year with the backtest edge, about
   $10k at 75% of the edge, and the worst cash point stays under about $1,800 at the 10th percentile.
2. **Scale to 5, then 10, only when live results confirm the edge.** After about 2 months (roughly 40 plan trades)
   the live average per trade should be at least ~75% of the backtest's for the same days (tracked with
   `../analysis/live_vs_backtest.py`).
3. **Trade copying: allowed by Apex (user confirmed 2026-10-14).** Still check the current limit on simultaneous PA
   accounts before going past 5.
   - One master per phase: the challenge accounts copy a master running the combine set, the funded accounts copy
     a master running the funded plan.
   - The funded plan sizes by each account's own cushion, but a copier mirrors the master's size. If a follower's
     cushion falls well below the master's (e.g. under ~$1,100 while the master is at full size), set that
     follower's multiplier to 0.5–0.75 or put it on its own chart until it recovers.
   - Starting the 3 slots together is fine (simulated: $29,595 net in 12 months vs $27,095 staggered). Accounts
     drift apart naturally as each one passes, finishes or blows.
   - Live tracking: export the master's report (one per phase) into `live/` weekly.

Caveats: the backtest edge is in-sample (the strategies were chosen on this history); the simulator assumes the
Apex rules in `../analysis/funded_sim.py`; payouts are counted when requested.

### Combine levers and staggering (2026-10-15)

Code `../analysis/combine_levers_test.py`, `../analysis/combine_swap_test.py` (outputs in `..._output.txt`). Every start
day 2018–26, Apex 50K combine rules (+$3,000, $2,000 EOD trailing floor locking at $50,100, $1,000 daily pause, 30 calendar
days = 21 trading days). Current set: 50.1% pass (2018–22 46.7%, 2023–26 54.5%), 48.1% blown, 1.9% out of time.

- **State-dependent sizing and daily stops do not lift it** (12 pre-specified variants): scale 0.75 / 1.25 / 1.5 →
  47.6 / 48.8 / 46.3%; halve when the cushion < $1,000 46.3%; press while the cushion ≥ $1,500 48.6%; press when behind
  after day 10 50.2%; halve once up $2,000 51.2%; daily stop −$500 45.9%, −$750 50.9%; profit lock +$1,000 41.7%,
  +$1,500 46.5%. The best post-hoc pair (halve at +$2,000 and stop the day at −$750) 52.4% — within noise.
- **Swap Overnight Bias ADX30 for the funded Overnight Bias ML at $1,100 risk: 52.0%** (2018–22 48.8%, 2023–26 56.3%),
  blown 39% instead of 48%, but 9% run out of time (median 9 days to pass instead of 6). Better in both halves but small
  (+2 points). Optional; it also means one Overnight Bias code for both phases (`NQ_Overnight_Bias_ML.txt`,
  `RiskPerTrade` 1100). Adding it on top of ADX30, raising VB to 10, or the funded plan scaled 1.5–3x (42–51%) do not help.
- **The pass rate is near its ceiling for this edge**: a zero-edge strategy passes about 40% (target $3,000 against a
  $2,000 floor), the plan 50–52%. More pass rate needs more edge per unit of risk, not different sizing.
- **Staggering matters more than any lever.** Combines on one copier take identical trades, so accounts started the
  same day share one outcome:

  | Start gap (trading days) | Both pass | Both blown | At least one passes | Outcome correlation |
  |---|---|---|---|---|
  | 0 (same day) | 50.1% | 48.1% | 50.1% | +1.00 |
  | 2 | 41.6% | 40.4% | 58.5% | +0.66 |
  | 5 | 34.9% | 33.6% | 65.4% | +0.39 |
  | 10 | 30.1% | 28.2% | 70.4% | +0.19 |
  | 21 | 25.5% | 22.6% | 75.3% | +0.00 |

  Expected passes are the same either way (0.5 per account), but same-day starts are one bet placed 3 times: all pass or
  all fail together. **Start each new combine at least 5, ideally 10, trading days after the previous one** (the
  simplest way: replace each finished or failed combine immediately, which staggers them naturally, and buy the next
  slot's combine a week or two after the last). Live: one combine since 2026-10-12 (shakedown week); add the next ones 5–10 trading days apart.

### Income target → number of accounts (2026-10-23)

Per slot (one account at a time: evaluation → funded → next evaluation), net of fees, 3-year means from
`../analysis/apex_paths_test.py`; '75% edge' scales by the ramp test's 36-month ratio (0.72). Steady state, after the
~4-month wait for the first payout; every account copies the same plan, so they win and lose together.

| Monthly target | 150K slots (backtest / 75% edge) | 50K slots (backtest / 75% edge) |
|---|---|---|
| per slot | $1,466 / $1,056 a month | $961 / $692 a month |
| $2,500 | 2 / 3 | 3 / 4 |
| $5,000 | 4 / 5 | 6 / 8 |
| $10,000 | 7 / 10 | 11 / 15 |
| $20,000 | 14 / 19 | 21 / 29 (over Apex's 20 cap) |
| 20 slots (the cap) | $29.3k / $21.1k a month | $19.2k / $13.8k a month |

### Ramp to Apex's 20-account limit (2026-10-15)

Code `../analysis/ramp_to_20_test.py` (output in `..._output.txt`). Slots = accounts (challenge → funded → next
challenge), all on the same copier plan; $50 a challenge, $85 activation; every 10th start day 2018–2023, 3 years.
Cash = payouts − fees, medians (p10 = bad case):

| Schedule | 3 m | 6 m | 12 m | 24 m | 36 m | 12 m p10 | Worst cash p10 |
|---|---|---|---|---|---|---|---|
| A 3 slots | −$455 | $3,995 | $29,295 | $60,440 | $89,685 | $2,915 | −$805 |
| B +1 a week to 20 | −$1,785 | $11,650 | $129,650 | $349,200 | $568,550 | $11,220 | −$4,300 |
| C +2 a week to 20 | −$2,855 | $19,300 | $151,300 | $366,100 | $578,000 | $16,780 | −$4,450 |
| **D 3 for 2 months, then +2 a week** | −$1,405 | $8,200 | $115,500 | $340,650 | $564,200 | $8,970 | −$4,350 |
| E 20 at once | −$2,700 | $27,300 | $196,300 | $403,600 | $603,900 | $25,300 | −$5,700 |

At 75% of the edge (challenge pass 40.7%): A $9,445 / $62,540 (12 / 36 m), B–E $46k–93k / $402k–409k, 12-month p10
−$10k to −$12k for any 20-slot schedule (A −$1,670).
- Faster is richer IF the edge is real (each slot is worth ~$13k per funded cycle); the cost of ramping is fees spent
  before the first payouts (worst cash −$4k to −$6k) and, if the edge is weaker or gone, fees keep burning: with no edge
  20 slots buy about 20 challenges a month (~$1,000 a month at $50 each, more at full price).
- **Recommended: D.** Run 3 slots for ~2 months (~40 live plan trades), then add 2 accounts a week to 20 only if the live
  edge ratio is ≥ 0.75 (`../analysis/live_vs_backtest.py`); costs ~$36k of first-year median vs C, buys the live check.
- Every account copies the same plan, so 20 accounts are one bet sized 20x (staggering only spreads start dates):
  a bad month hits all of them. Check whether Apex's 20 counts evaluations + PAs together, and that the copier and
  MultiCharts handle 20 followers.

### 150K accounts (2026-10-15)

Code `../analysis/plan_150k_test.py`, `../analysis/slot_150k_vs_50k_test.py` (simulators `../analysis/funded_sim150.py`,
`../analysis/account_pipeline150.py` = the 50K ones with 150K numbers; the 50K check reproduces the funded bench exactly).
150K rules used: evaluation +$9,000 in 30 days, $4,000 EOD trailing drawdown (locks $150,100), $2,000 daily loss pause;
funded: 6 payouts, $20,500 in all (ladder 2,500 / 3,000 / 3,000 / 3,000 / 4,000 / 5,000, $350 qualifying days, request from
$154,600: Apex's pages, user's screenshots in reports/screenshots/, 2026-10-15).
- **Evaluation:** the combine set x 2.5 passes 41.6% (2018–22 38.9%, 2023–26 45.4%; x 2 38.7%, x 3 40.7%), vs 50.1% on the
  50K: the 150K target is 2.25x its drawdown (50K 1.5x). Adding Twin cap1 does not help (39–42%).
  Inputs x 2.5: VB 20 MNQ, ONB ADX30 `RiskPerTrade` 2750, Bridge Monday 5 MNQ, EOS `RiskPerTrade` 1250.
- **Funded:** the funded plan x 1.5 with full size from a **$3,000** cushion: $15,731 / $19,743 (1 / 2 years), **blown 0% /
  0%**, all 6 payouts within 2 years 91% (real ladder; the assumed one gave $15,866 / $19,725). Bigger (x 2–3) or a faster cushion blows 9–37%; Twin adds nothing.
  Inputs x 1.5 (whole MNQ, rounded down): VB 4 (`FlaggedContracts` 1), ONB ML $600, Monday 1, EOS $1,050, LDF 3, NFP $750,
  Bridge Monday 1, CL fade 3 MCL; half size while the cushion is under $1,500, full from $3,000.
- **Per slot over 3 years** (before fees): 50K $35.4k mean payouts (6.1 challenges, 3.5 funded); **150K $54.8k** (7.7
  challenges, 3.3 funded) = **+55% per slot**. With Apex's 20-account cap, a 150K slot is worth more as long as its
  evaluation + activation cost less than about $2,500 more per funded account than the 50K's.

### Which Apex path: 50K or 150K, with or without the activation fee (2026-10-15)

Code `../analysis/apex_paths_test.py` (output in `..._output.txt`). Prices from the user's screenshots: 50K EOD $59 (5-pack
$24.50 each) + $130 activation; 50K no-activation $119 (5-pack $109); 150K EOD $219 (5-pack $199) + $150 activation; 150K
no-activation $249. One slot = one account at a time, every 5th start day 2018–2023, 3 years, means:

| Rank | Path | Cost per funded account | Fees over 3 years | Net 12 months | Net 36 months | Net per $1 of fees |
|---|---|---|---|---|---|---|
| 1 | **150K no-activation ($249)** | $598 | $1,954 | $13,351 | **$52,788** | 27 |
| 2 | 150K EOD 5-pack ($199 + $150) | $628 | $2,060 | $13,316 | $52,682 | 26 |
| 3 | 150K EOD single ($219 + $150) | $676 | $2,216 | $13,264 | $52,525 | 24 |
| 4 | **50K EOD 5-pack ($24.50 + $130)** | $179 | $598 | $9,248 | $34,813 | **58** |
| 5 | 50K no-activation 5-pack ($109) | $218 | $661 | $9,227 | $34,751 | 53 |
| 6 | 50K no-activation single ($119) | $238 | $721 | $9,207 | $34,690 | 48 |
| 7 | 50K EOD single ($59 + $130) | $248 | $808 | $9,178 | $34,604 | 43 |

- Payouts per slot: 50K $9,447 / $22,029 / $35,411 (12 / 24 / 36 months), 150K $14,003 / $32,802 / $54,742.
- Speed: median trading days from the first evaluation to the first payout 87 (50K) vs 95 (150K); to one full
  account's worth ($13,000 / $20,500) 249 vs 263. The 50K is about 2 weeks quicker to each milestone, the 150K pays ~50%
  more per slot. Fees are 2–4% of payouts on every path, so the account size decides, not the fee option.
- Within a size the fee option changes the 3-year net by under $300. 150K: no-activation is cheapest (fails cost $249,
  the $150 activation is paid only on a pass, but 2.4 tries x $30 more for EOD + $150 > $0). 50K: EOD 5-pack is cheapest.
- **5-packs start all five evaluations at purchase (user, 2026-10-16).** On one copier they trade identical days, so the five
  pass or fail together (one bet x 5; same expected passes, no diversification). Use single 50K EOD ($59, ~$248 per funded
  account, +$69 vs the 5-pack) to keep accounts 5-10 trading days apart. A 5-pack only makes sense when deliberately adding
  five accounts at once after the live gate.

### Scaling up while the account grows (2026-10-15)

Code `../analysis/payout_scaling_test.py`. Letting the cushion rule go above full size (fmax 1.25–2) or stepping sizes up
after each payout (x1.25–2) does not speed up the payouts:
- **50K:** current $10,184 / $12,450, blown 3%, all 6 in 2 years 94%, median 230 trading days to the 6th payout. Above-full
  cushion sizing: blown 6–7%, $11.95–12.02k; stage 'mild' / 'ladder' the same as now; 'bold' blown 10–11%. Keep as is.
- **150K:** current $15,731 / $19,743, blown 0%, all 6 91%, 238 days. Cushion fmax 1.5: $16,276 / $19,887, blown 0%,
  all 6 94%, 223 days (+$550 in year 1, ~15 days sooner) — small; optional once a 150K account is past its first payout.
- Why: the payouts are paced by Apex's rules (5 days of $250 / $350+ between payouts, the 50% consistency rule, fixed caps),
  not by how fast the balance grows; bigger size makes bigger single days, which trips the consistency rule, and adds
  drawdown risk.

### Apex vs a personal account (2026-10-15)

Code `../analysis/personal_account_test.py`. The plan without Apex's rules, every strategy at 1 NQ (CL fade 1 CL), 2018–26
backtest: **$101k a year, max drawdown $24k**, worst month −$15.9k, 19% losing months, Sharpe 2.75 (2018–22 $72k / DD
$22.6k; 2023–26 $141k / DD $24.1k; 2018 itself only +$538). Capital for a 20% / 30% max drawdown: $121k / $80k →
84% / 126% a year on capital (in-sample; live will be lower).
- Apex caps each account ($13,000 / $20,500, 5-day + consistency pacing), not the edge; but with 20 accounts the total is
  ~20 x $17–18k a year on 150K slots for ~$13k a year of fees and no trading capital at risk.
- A personal account is uncapped and compounds, but needs ~$80–120k per 1-NQ plan and the losses are real.
- Path: Apex first (no capital at risk) while the live edge is confirmed; move payouts into a personal account once
  ~6–12 months of live results match the backtest, start it at MNQ size and scale with the account.

### Ramp to 20 with 150K No-Activation accounts (2026-10-16)

Code `../analysis/ramp150_test.py` (output in `..._output.txt`). Real prices (50K EOD single $59 + $130, 150K No-Activation
$249); 3 x 50K at 0 / +6 / +11 trading days, +2 accounts a week from day 42 to 20; medians, 10th percentile = bad case.

| Schedule | 6 m | 12 m | 24 m | 36 m | 12 m p10 | Worst cash p10 | Months to $100k |
|---|---|---|---|---|---|---|---|
| A 3 x 50K, then 150K | $2k | $176k | $557k | $986k | −$8k | −$18.7k | 10.0 |
| **B as A, 50K slots switch to 150K after their 1st account** | $2k | $175k | $569k | $1,033k | −$8k | −$18.8k | 10.0 |
| C all 20 slots 150K | $5k | $194k | $591k | $1,043k | −$16k | −$22.6k | 9.6 |
| D all 20 slots 50K | $11k | $152k | $390k | $672k | +$9k | −$5.7k | 10.7 |

At 75% of the edge (150K evaluation pass 30.9%, 50K 40.7%): A / B / C $95k–104k at 12 months, $715k–756k at 36,
12-month p10 −$31k to −$34k, worst cash p10 −$35k to −$39k, $100k after ~12 months; D $65k / $494k, worst −$14.6k.
- 150K roughly doubles the 3-year total (+$340k vs all-50K) but the fees come first: 17 new slots x $249 evaluations
  (2.4 tries per funded account, 3.2 if the edge is weaker) need a budget of ~$19k (backtest edge) to ~$35k (75% edge) before
  the payouts catch up; the all-50K ramp needs ~$6k–15k.
- Recommended: B, with an evaluation budget set aside up front (~$20k), and new 150K slots added only while the live edge
  ratio stays ≥ 0.75; pause additions if cumulative cash falls below −$20k.

### Tuning the sizing for the whole pipeline (2026-10-14)

Code `../analysis/pipeline_tuning_test.py` (output in `..._output.txt`). One slot, 70 start months, 3 years, net of
fees. Scored at the backtest edge and at 75% of it.
- **Combine sizing doesn't matter much.** 72 sets (VB 4–10 MNQ × ONB $700–1,500 × Bridge Monday 1–3 × EOS off /
  $500) all land at about $29–31k net over 3 years at the full edge and about $20–22k at 75%. The pipeline is driven
  by the funded phase, and the challenge only decides how fast you get there. The current combine (pass 50.1%, the
  highest) stays.
- **Funded sizing does matter.** Recycling a blown account costs only a few challenges, so being a bit more
  aggressive in the funded phase pays:

  | Full size from cushion | Scale | Net 3 years (edge) | Blown per slot | Net 3 years (75% edge) | Blown per slot |
  |---|---|---|---|---|---|
  | $1,500 (current) | 1.0 | $30,420 | 0.04 | $21,212 | 0.53 |
  | **$1,000** | **1.0** | **$32,702** | 0.49 | **$22,570** | 2.53 |
  | $1,500 | 1.25 | $32,828 | 0.33 | $22,680 | 1.61 |
  | $1,000 | 1.25 | $36,100 | 1.43 | $26,558 | 2.73 |
  | $2,000 | 1.0 | $28,478 | 0.14 | $15,655 | 0.31 |
  | $1,500 | 0.75 | $25,445 | 0.00 | $19,955 | 0.16 |

- **Contract use stays within Apex's caps:** at full size a median 3 MNQ a day, 99th percentile 14, at scale 1.25
  17. Over 20 MNQ on 0.1–0.4% of days, all on low-volatility 2018 days.
- **Recommendation:**
  - **User's decision (2026-10-14): full size from a $1,500 cushion** (f = cushion / $1,500, kept between 0.5 and 1;
    the table at the top of this file). The $1,000 setting nets about +7% per slot only by counting blown accounts as
    cheap restarts; per account the funded bench (current plan + CL fade) gives $1,500: $9,818 / $12,595, blown 4% / 2%
    vs $1,000: $9,293 / $10,734, blown 17% / 18%. Protecting each funded account comes first.
    Re-checked against Tran 2026 ('From Funded to Paid', `../analysis/funded_to_paid_check.py`): $1,500 is best on every
    measure - expected payouts, chance of any payout (93%), blown (4% / 2%) and all 6 payouts within 2 years (95%); fixed or
    bolder sizing is worse on all of them (fixed 2x: paid 46%, blown 62% / 66%).
  - **Netting (several strategies on one account), checked 2026-10-14 (`../analysis/plan_overlap_check.py`):** only 2.5% of
    the plan's NQ trades start while an opposite plan trade is open (Overnight Bias ML / Late-Day Flow against a Monday long);
    the broker nets them and the P&L is the same as the sum, so the bench is right to keep them. Operational rules:
    (1) run every NQ strategy on the SAME symbol (all MNQ) - long NQ with short MNQ is a hedge Apex prohibits, while one
    symbol simply nets; (2) let each chart send its own entries / exits (do not let MultiCharts 'sync' a chart to the
    broker's net position); (3) on a netted account the broker shows the NET position, so a chart can be 'long' while the
    account is flat - check fills per chart, not the account position.
  - **Anti-hedging 'global lock' (user's PDF, 2026-10-15, `../analysis/anti_hedge_lock_check.py`):** blocking any entry while
    another plan strategy holds a position removes 1,092 of 3,834 NQ trades (28.5%; ONB ML 155, VB 386, LDF 374, Monday 177;
    they average $239 vs $221) and drops the bench from $9,818 / $12,595, paid 93%, blown 4% / 2% to $6,933 / $11,375, paid
    81%, blown 9% / 5%. Do NOT use it. Netting on one account / one symbol is not a hedge; never split different strategies
    across accounts -- give every account the whole plan (copier), so all accounts always hold the same direction.
  - Scale 1.25 (+19% at the edge, +25% at 75%) costs more blown accounts (1.4–2.7 per slot over 3 years). Consider
    it only after the live edge ratio is ≥ 0.9 over ~40 trades.
  - Caveat: in-sample, and medians move in steps of the payout amounts.

## Replacement sweep (2026-10-18): no swap beats the plan

User rule (CLAUDE.md, 2026-10-18): candidates are also tested as replacements, not only additions. `analysis/replacement_sweep.py`
(stage 1, one history) and `analysis/replacement_sweep_stage2b.py` (bootstrapped bench, 1,000 paired 2-year histories) put
15 tested candidates (noise-band, NQ MOC follow, Headline Shock, Crabel, Bridge ORB, Morning Momentum tight, release fade,
VWAP / open pullbacks, gold breakout, NFP 8:45, DriftPullback shorts, Overnight Drift, Vol-Control Sell, LDF / ONB halves)
in place of each plan slot (whole, and in part for VB / LDF / ES MOC / CL), each against the slot left EMPTY as control.
- The one-history screen overstates swaps badly (2 MNQ swaps that looked +$700 blew 17-22% on the bootstrapped bench).
- On the bootstrapped bench every swap is within noise of the plan (best +$114 on $12,035, P(beats plan) ≤ 50.3%):
  VB 1 / 1 + NQ MOC $400 +$114 (blown 5.8%, 10 days slower); Monday Long -> NFP 8:45 $400 +$80; CL 1 MCL +$82 with nothing added.
- Removing Monday Long, Bridge Monday or the CL fade changes the 2-year payout by under $30: at bench level the plan is
  saturated; its drawdown budget, not missing edges, is the limit. Swaps only trade speed against blow-up risk.
Decision: keep the plan. Live data (drift alarm, mid-December gate) decides the next change.
