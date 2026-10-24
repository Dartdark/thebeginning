# Personal-account portfolio (2026-10-23)

From everything tested so far; numbers from `analysis/personal_portfolio.py` (output in
`analysis/outputs/personal_portfolio_output.txt`). Backtest 2018-01 → 2026-10, after costs, micro commissions charged at
~$1.25 a round trip. No Apex rules: overnight holds allowed, no trailing limit, no payout cap.

## The pieces (1 micro each)
| Piece | Market | $ a year | 2023+ a year | Max DD | Sharpe | Status |
|---|---|---|---|---|---|---|
| Relative Strength (both sides) | MNQ | $3,889 | $4,900 | $2,871 | 1.30 | B, MC-confirmed; funded plan (longs) |
| Twin Continuation v2.1 | MNQ | $3,589 | $5,648 | $1,629 | 1.73 | A, MC-confirmed, personal only (overnight, wide stop) |
| ONB ML | MNQ | $2,410 | $2,773 | $1,564 | 1.62 | S; funded plan (the combine runs plain ONB ADX30) |
| FC 2B v2 | MNQ | $2,366 | $2,213 | $1,534 | 1.33 | A, MC-confirmed, **forward log first** |
| Monday Long | MNQ | $2,104 | $3,912 | $2,086 | 1.09 | funded plan |
| Vault Break | MNQ | $1,723 | $2,237 | $1,385 | 1.30 | live on Apex (combine) |
| Bridge Monday | MNQ | $1,295 | $1,478 | $1,689 | 1.39 | live on Apex (combine) |
| Late-Day Flow | MNQ | $889 | $1,171 | $1,590 | 1.10 | funded plan |
| CL Sunday fade | MCL | $692 | $1,042 | $518 | 1.01 | funded plan |
| EOS | MNQ | $548 | $798 | $746 | 0.83 | live on Apex (combine) |
| ES MOC | MES | $342 | $172 | $701 | 1.09 | funded plan |
| NFP Fade | MNQ | $291 | $467 | $826 | 0.60 | funded plan |

## Whole portfolio, every piece at 1 micro
- **$20,100 a year** (2023+: $26,800), every year positive (2018 $4.7k, 2019 $3.0k, then $19-32k).
- Sharpe 2.83, Sortino 6.18, PF 1.82, Calmar 4.3, Ulcer 0.97; max DD $4,663; worst month −$2,063; 20% losing months.
- Monte Carlo, 1 year: p5 $9,200 / p50 $19,700 / p95 $32,000; P(losing year) 0.1%; max DD p50 $2,760 / p95 $4,711;
  return / DD 7.1. Worst day −$1,413.
- **Needs about $23,500** to keep the 1-year p95 drawdown at 20% of the account.

## Growing into it (capital at the 20% rule)
| Account | Set (1 micro each) | $ a year (MC p50) | Bad year (p5) | DD p95 |
|---|---|---|---|---|
| ~$11,500 | **A**: Twin, ONB ML, Bridge, CL Sunday, NFP | $8,100 | $3,000 | $2,300 |
| ~$11,300 | **B**: A + EOS (same risk, a bit more profit) | $8,600 | $3,600 | $2,260 |
| ~$13,600 | **C**: B + Vault Break | $10,400 | $4,400 | $2,730 |
| ~$20,400 | **D**: C + Relative Strength + ES MOC | $14,500 | $6,300 | $4,080 |
| ~$23,500 | **Full**: all 12 | $19,700 | $9,200 | $4,710 |
| ~$32,000 | **Full + S30 IBS** (NQ + ES, 1 micro each; holds days, no stop) | $25,400 | | $6,400 |
| ~$47,000 | Full x 2 | $39,400 | $18,500 | $9,420 |

A $10k start sits just under set B's line (p95 DD ~22% of $10k): acceptable if you're comfortable with that, or start
with ~$11.5k. Add the next set only when the account reaches its line, and drop back a step after a 20% drawdown.

## Read this before trusting the numbers
- **These are backtests on the years the strategies were chosen on.** Expect live results lower; our rule is live ≥ 75%
  of the backtest (`DEVELOPMENT_PROCESS.md`). At 60% of the backtest the full portfolio is ~$12k a year at 1 micro.
- **FC 2B is not cleared yet:** forward log until 40-80 signals. Without it the full set is ~$17.7k a year.
- **Twin Continuation holds overnight with a wide swing stop** (worst trade −$1,172 per MNQ); needs overnight margin
  (check the broker). Without Twin the full set is $16.6k a year, DD p95 $4.5k. Since 2026-10-24 its overnight holds are
  marked at each 16:00 CT close instead of booked at exit (cross-review item): no material change (max DD $4,663, MC p95
  DD $4,687, capital $23.4k, all as before; only 50 of 1,074 trades hold overnight).
- RS and FC 2B overlap (both enter at 09:01 in the opening drive's direction, corr +0.36): they can lose together.
- When to start (`DEVELOPMENT_PROCESS.md` lifecycle): from Apex payouts, after the live record matches the backtest
  (early start from ~month 3 at small size if ≥ 100 live trades, live ≥ 75% of backtest, no drift alarm).
- Not included (too weak or untested): Gold Breakout (C), overnight long, turn of month, trend portfolio, the untested
  ideas in `IDEAS.md` (all-weather ETFs, Weekend Trend Trader, Davey's ES Keltner).
