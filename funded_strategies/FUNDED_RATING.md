# Funded set rating (2026-10-12)

> **Update (2026-10-12, later):** Overnight Drift, the weak link below, has been replaced by
> Monday Long (1 MNQ), and Late-Day Flow (2 MNQ) has been added. Current plan with cushion
> sizing: $7,676 within 1 year, $12,012 within 2 years, blown 4–6%; portfolio Sharpe 2.51,
> Calmar 4.33. See `FUNDED_PLAN.md`. The rating below is of the set before the changes.

Set: Vault Break 3 MNQ, Overnight Bias ML RiskPerTrade 300, Overnight Drift 500,
Expiration Open Short 500. All MultiCharts trade lists, 2018–2026, $7.25/NQ costs plus 1 tick
of slippage per fill. Simulator: Apex 50K EOD Performance Account (`analysis/funded_sim.py`),
one start every trading day. Code: `analysis/funded_rating.py`.

## Per strategy at funded size

| Strategy | Trades/yr | Win | Avg/trade | PF | $/yr | Max DD | Worst day |
|---|---|---|---|---|---|---|---|
| Vault Break (3 MNQ) | 107 | 62% | $51 | 1.41 | $5,448 | −$4,085 | −$1,366 |
| Overnight Bias ML ($300) | 42 | 56% | $92 | 2.14 | $3,893 | −$2,348 | −$342 |
| Overnight Drift ($500) | 117 | 54% | $9 | 1.10 | $1,026 | −$5,879 | −$514 |
| Expiration Open Short ($500) | 12 | 59% | $144 | 2.21 | $1,704 | −$1,149 | −$499 |
| **All** | 192 days | 55% of days | $63/day traded | 1.50 | **$12,071** | −$5,278 | −$1,692 |

Correlations of daily P&L: 0.16 (VB–ONB ML), all others −0.02 to 0.04. Years: 2018 −$2,923
(OND −$4,469), then +$9,127 to +$19,829 every year. 24% of months negative; worst −$2,144.
About 52 days a year make $250+ (the payout qualifying days).

## Standard metrics (2018–2026, funded sizes, `analysis/funded_metrics.py`)

Daily $ P&L, 252 days a year; drawdown % against the $50,000 account; "days" = days with a trade.

| Strategy | Days | Sharpe | Sortino | Profit factor | Calmar | Ulcer index | Max DD | $/yr |
|---|---|---|---|---|---|---|---|---|
| Vault Break (3 MNQ) | 942 | 1.35 | 2.07 | 1.41 | 1.31 | 1.46 | $4,085 | $5,341 |
| Overnight Bias ML ($300) | 373 | 1.82 | 4.35 | 2.14 | 1.63 | 1.18 | $2,348 | $3,816 |
| Overnight Drift ($500) | 1,029 | 0.40 | 0.57 | 1.10 | 0.17 | 4.38 | $5,879 | $1,006 |
| Expiration Open Short ($500) | 104 | 1.05 | 2.30 | 2.21 | 1.45 | 0.67 | $1,149 | $1,671 |
| **Portfolio** | 1,687 | **2.08** | **3.57** | 1.50 | **2.24** | 2.19 | $5,278 | $11,834 |
| Portfolio, recommended sizes (ONB ML $400, EOS $700) | 1,699 | 2.16 | 3.82 | 1.53 | 2.48 | 2.20 | $5,482 | $13,605 |

Overnight Drift is clearly the weak link on every measure (Sharpe 0.40, Calmar 0.17, the worst Ulcer).

## Payouts per account

| | 1 year | 2 years |
|---|---|---|
| Expected | $6,928 | $8,379 |
| Median | $7,500 | $13,000 |
| Blown | 34% | 37% |
| All 6 payouts ($13,000) | 24% | 63% |

Accounts are close to all-or-nothing: blown accounts go down early (median day 40–43,
$531–733 paid before), 27–31% are blown before any payout, and accounts that survive the
first two months reach 4–6 payouts. Weak start years: 2018 (96% blown), 2023–2024 (55–67%).

Leave one out (1 year / 2 years): without VB $3,982 / $9,008; without ONB ML $4,303 / $6,709;
without OND $6,099 / $8,830; without EOS $5,219 / $7,103. ONB ML and EOS carry the set; OND
helps the first year and costs the second. +1 tick of slippage per fill: $6,164 / $7,831,
blown 40%.

## Fix: size to the drawdown cushion

Each morning: cushion = balance − trailing drawdown threshold (what's left before
liquidation). Size factor f = cushion / $2,000, between 0.5 and 1.0. Multiply every
strategy's size by f (whole MNQ, rounded down). After the balance closes at $52,100 the
threshold locks at $50,100 and the cushion is $2,000+ for good: full size from then on.

| Plan | 1 year | 2 years | Blown | 1st payout |
|---|---|---|---|---|
| Current, fixed size | $6,928 | $8,379 | 34% / 37% | 53 days |
| Current + cushion sizing | $5,768 | $11,073 | 10% / 11% | 97 days |
| **Recommended: cushion sizing, VB 3, ONB ML $400, OND $500, EOS $700** | **$6,995** | **$11,485** | **12% / 11%** | 79 days |
| Same without Overnight Drift | $6,526 | $11,918 | 8% / 7% | 79 days |
| Current + cushion sizing, +1 tick extra slippage per fill | $5,015 | $10,805 | 10% / 11% | 105 days |

Raising Vault Break (4 MNQ) or everything at once (about 1.35x) brings blowups back
(39–43%). Staged sizes by payout number and a $500–1,000 payout buffer help less than
cushion sizing.

Caveats: the starts overlap, so there are only about 8 years of independent history; the
sizes were chosen on the same data; Overnight Bias ML's weights are fitted on 2018–2026.
Treat the numbers as directional.
