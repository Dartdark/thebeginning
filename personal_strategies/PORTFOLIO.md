# Personal-account portfolio (2026-10-23; Overnight Anomaly added 2026-10-24)

From everything tested so far; numbers from `analysis/personal_portfolio.py` (output in
`analysis/outputs/personal_portfolio_output.txt`). Backtest 2018-01 → 2026-10, after costs, micro commissions charged at
~$1.25 a round trip. No Apex rules: overnight holds allowed, no trailing limit, no payout cap.

## The pieces (1 micro each)
| Piece | Market | $ a year | 2023+ a year | Max DD | Sharpe | Status |
|---|---|---|---|---|---|---|
| Relative Strength (both sides) | MNQ | $3,889 | $4,900 | $2,871 | 1.30 | B, MC-confirmed; funded plan (longs) |
| Twin Continuation v2.1 | MNQ | $3,673 | $5,711 | $1,629 | 1.77 | A, MC-confirmed, personal only (overnight, wide stop) |
| ONB ML | MNQ | $2,410 | $2,773 | $1,564 | 1.62 | S; funded plan (the combine runs plain ONB ADX30) |
| FC 2B v2 | MNQ | $2,366 | $2,213 | $1,534 | 1.33 | A, MC-confirmed, **forward log first** |
| Monday Long | MNQ | $2,104 | $3,912 | $2,086 | 1.09 | funded plan |
| Vault Break | MNQ | $1,723 | $2,237 | $1,385 | 1.30 | live on Apex (combine) |
| Overnight Anomaly (Block B) | MNQ | $1,706 | $2,426 | $2,044 | 0.94 | C, personal only (user 2026-10-24); long 17:30 → 02:30 CT after a down day; corr +0.02 |
| Bridge Monday | MNQ | $1,295 | $1,478 | $1,689 | 1.39 | live on Apex (combine) |
| Late-Day Flow | MNQ | $889 | $1,171 | $1,590 | 1.10 | funded plan |
| CL Sunday fade | MCL | $692 | $1,042 | $518 | 1.01 | funded plan |
| EOS | MNQ | $548 | $798 | $746 | 0.83 | live on Apex (combine) |
| ES MOC | MES | $342 | $172 | $701 | 1.09 | funded plan |
| NFP Fade | MNQ | $291 | $467 | $826 | 0.60 | funded plan |

## Whole portfolio, every piece at 1 micro
- **$21,900 a year** (2023+: $29,300), every year positive (2018 $4.6k, 2019 $4.1k, then $20.6-37.3k).
- Sharpe 2.97, Sortino 6.38, PF 1.85, Calmar 5.1, Ulcer 0.88; max DD $4,331; worst month −$1,835; 20% losing months.
- Monte Carlo, 1 year: p5 $10,500 / p50 $21,300 / p95 $34,200; P(losing year) 0.0%; max DD p50 $2,740 / p95 $4,607;
  return / DD 7.8. Worst day −$2,064.
- **Needs about $23,000** to keep the 1-year p95 drawdown at 20% of the account.
- Overnight Anomaly's effect (12 → 13 pieces): +$1,700 a year, max DD $4,663 → $4,331, Sharpe 2.84 → 2.97, capital
  $23.4k → $23.0k. It barely moves with the rest (corr +0.02), so it adds profit without adding drawdown.

## Growing into it (capital at the 20% rule)
| Account | Set (1 micro each) | $ a year (MC p50) | Bad year (p5) | DD p95 |
|---|---|---|---|---|
| ~$11,500 | **A**: Twin, ONB ML, Bridge, CL Sunday, NFP | $8,100 | $3,000 | $2,300 |
| ~$11,300 | **B**: A + EOS (same risk, a bit more profit) | $8,600 | $3,600 | $2,260 |
| ~$13,600 | **C**: B + Vault Break | $10,400 | $4,400 | $2,730 |
| ~$20,400 | **D**: C + Relative Strength + ES MOC | $14,500 | $6,300 | $4,080 |
| ~$23,000 | **Full**: all 13 | $21,300 | $10,500 | $4,610 |
| ~$34,200 | **Full + S30 IBS** (NQ + ES, 1 micro each; holds days, no stop) | $27,100 | | $6,840 |
| ~$46,000 | Full x 2 | $42,600 | $20,900 | $9,220 |

A $10k start sits just under set B's line (p95 DD ~22% of $10k): acceptable if you're comfortable with that, or start
with ~$11.5k. Add the next set only when the account reaches its line, and drop back a step after a 20% drawdown.

## Read this before trusting the numbers
- **These are backtests on the years the strategies were chosen on.** Expect live results lower; our rule is live ≥ 75%
  of the backtest (`DEVELOPMENT_PROCESS.md`). At 60% of the backtest the full portfolio is ~$13k a year at 1 micro.
- **FC 2B is not cleared yet:** forward log until 40-80 signals. Without it the full set is ~$19.6k a year.
- **Twin Continuation holds overnight with a wide swing stop** (worst trade −$1,172 per MNQ); needs overnight margin
  (check the broker). Without Twin the full set is $18.3k a year, DD p95 $4.4k. Since 2026-10-24 its overnight holds are
  marked at each 16:00 CT close instead of booked at exit (cross-review item): no material change (max DD $4,663, MC p95
  DD $4,687, capital $23.4k, all as before; only 50 of 1,074 trades hold overnight).
- **Overnight Anomaly holds 17:30 → 02:30 CT with a wide disaster stop** (4 x the window range EMA): worst night −$1,263
  per MNQ (2026-06-23), it is behind the worst portfolio day (−$2,064). Ranked C (t 2.9, below the multiple-testing bar):
  in only because it fills the empty overnight hours. Code: `personal_strategies/Overnight_Anomaly.txt` (Block B on its own,
  `Max_Contracts 1`, @MNQ 15-min 24-hour chart; review `checks/candidates/overnight_anomaly/REVIEW.md`).
- RS and FC 2B overlap (both enter at 09:01 in the opening drive's direction, corr +0.36): they can lose together.
- When to start (`DEVELOPMENT_PROCESS.md` lifecycle): from Apex payouts, after the live record matches the backtest
  (early start from ~month 3 at small size if ≥ 100 live trades, live ≥ 75% of backtest, no drift alarm).
- Not included (too weak or untested): Gold Breakout (C), plain every-night overnight long, turn of month, trend portfolio, the untested
  ideas in `IDEAS.md` (all-weather ETFs, Weekend Trend Trader, Davey's ES Keltner).
