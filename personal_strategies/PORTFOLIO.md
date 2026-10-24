# Personal-account portfolio (2026-10-23; Overnight Anomaly, Dual Thrust, Kusho v9, S47 v2 and S30 IBS added 2026-10-24)

From everything tested so far; numbers from `analysis/personal_portfolio.py` (output in
`analysis/outputs/personal_portfolio_output.txt`). Backtest 2018-01 → 2026-10, after costs, micro commissions charged at
~$1.25 a round trip. No Apex rules: overnight holds allowed, no trailing limit, no payout cap.

## The pieces (1 micro each)
| Piece | Market | $ a year | 2023+ a year | Max DD | Sharpe | Status |
|---|---|---|---|---|---|---|
| S30 IBS reversal (NQ + ES, long only, holds days, no stop) | MNQ + MES | $5,966 | $5,815 | $8,704 | 0.90 | B; personal only (user 2026-10-24); **still on the forward log**; `checks/candidates/s30_ibs/S30_IBS.txt` |
| Relative Strength (both sides) | MNQ | $3,889 | $4,900 | $2,871 | 1.30 | B, MC-confirmed; funded plan (longs) |
| Kusho v9 (21:00 exit, weekend holds) | MNQ | $3,573 | $3,398 | $1,757 | 1.68 | B; personal only (user 2026-10-24); **still on the forward log**; roll-adjusted rule `checks/candidates/kusho/Kusho_v9.txt` |
| Twin Continuation v2.1 | MNQ | $3,673 | $5,711 | $1,629 | 1.77 | A, MC-confirmed, personal only (overnight, wide stop) |
| Dual Thrust v4 | MNQ | $2,422 | $2,879 | $2,010 | 1.41 | A, checker PASS WITH CONCERNS; MultiCharts check pending; also 150K funded at 2 MNQ (user 2026-10-24) |
| S47 v2 (Europe-open impulse) | MNQ | $2,705 | $2,638 | $1,583 | 1.33 | B; personal only (user 2026-10-24); **still on the forward log**; `checks/candidates/s47_v2/S47_v2_fixed.txt` |
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
- **$36,600 a year** (2023+: $44,000), every year positive (2018 $8.5k, 2019 $9.7k, then $31.4-56.0k).
- Sharpe 2.96, Sortino 6.22, PF 1.83, Calmar 5.9, Ulcer 0.99; max DD $6,182; worst month −$1,987; 13% losing months.
- Monte Carlo, 1 year: p5 $19,400 / p50 $35,700 / p95 $54,800; P(losing year) 0.0%; max DD p50 $4,640 / p95 $7,120;
  return / DD 7.7.
- **Needs about $35,600** to keep the 1-year p95 drawdown at 20% of the account (without S30: $26,200).
- S30's effect (16 → 17 pieces, user 2026-10-24): +$6,000 a year, but Sharpe 3.17 → 2.96, return/DD 9.2 → 7.7, max DD
  $4,590 → $6,182, capital $26.2k → $35.6k: more money, less per unit of risk. Below ~$35.6k run the 16 without S30.
- Kusho v9 + S47 v2's effect (14 → 16 pieces, user 2026-10-24): +$6,300 a year, Sharpe 3.00 → 3.17, return/DD 8.2 → 9.2,
  max DD $5,001 → $4,590, capital $25.0k → $26.2k (`analysis/forward_log_plans_test.py`). Both stay on the forward log;
  Kusho's overnight / weekend holds are booked on the exit day (not marked daily), so its drawdown may be understated.
- Dual Thrust's effect (13 → 14 pieces, user 2026-10-24): +$2,400 a year, Sharpe 2.97 → 3.00, return/DD 7.8 → 8.2, max DD
  $4,331 → $5,001, capital $23.0k → $25.0k (corr +0.33 with the rest: it trades the same RTH hours as VB / RS / FC 2B).
- Overnight Anomaly's effect (12 → 13 pieces): +$1,700 a year, max DD $4,663 → $4,331, Sharpe 2.84 → 2.97, capital
  $23.4k → $23.0k. It barely moves with the rest (corr +0.02), so it adds profit without adding drawdown.

## Growing into it (capital at the 20% rule)
| Account | Set (1 micro each) | $ a year (MC p50) | Bad year (p5) | DD p95 |
|---|---|---|---|---|
| ~$11,500 | **A**: Twin, ONB ML, Bridge, CL Sunday, NFP | $8,100 | $3,000 | $2,300 |
| ~$11,300 | **B**: A + EOS (same risk, a bit more profit) | $8,600 | $3,600 | $2,260 |
| ~$13,600 | **C**: B + Vault Break | $10,400 | $4,400 | $2,730 |
| ~$20,400 | **D**: C + Relative Strength + ES MOC | $14,500 | $6,300 | $4,080 |
| ~$23,000 | Full without Dual Thrust (13) | $21,300 | $10,500 | $4,610 |
| ~$25,000 | Full without Kusho / S47 (14) | $23,700 | $12,500 | $5,000 |
| ~$26,200 | Full without S30 (16) | $29,900 | $16,400 | $5,240 |
| ~$35,600 | **Full**: all 17 (with S30 IBS) | $35,700 | $19,400 | $7,120 |
| ~$71,200 | Full x 2 | $71,500 | $38,800 | $14,230 |

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
