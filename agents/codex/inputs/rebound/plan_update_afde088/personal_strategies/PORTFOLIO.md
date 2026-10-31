# Personal-account portfolio (2026-10-23; Dual Thrust, Kusho v9, S47 v2, S30 IBS and Overnight Tick / VIX added 2026-10-24; Overnight Anomaly replaced; BB_MRM added and removed 2026-10-25; Swing Target v3 and PAPERTREND v2 added 2026-10-25)

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
| Overnight Tick / VIX (long 17:05 → 03:00 CT after a down day, order-flow × VIX filter) | MNQ | $2,201 | $2,838 | $1,283 | 1.68 | A, MC-confirmed; personal + funded (50K 1, 150K 2) since 2026-10-24 (user); replaced Overnight Anomaly (C); data to 2026-07-07 |
| Bridge Monday | MNQ | $1,295 | $1,478 | $1,689 | 1.39 | live on Apex (combine) |
| Late-Day Flow | MNQ | $889 | $1,171 | $1,590 | 1.10 | funded plan |
| CL Sunday fade | MCL | $692 | $1,042 | $518 | 1.01 | funded plan |
| EOS | MNQ | $548 | $798 | $746 | 0.83 | live on Apex (combine) |
| ES MOC | MES | $342 | $172 | $701 | 1.09 | funded plan |
| Swing Target v3 (prior 2-day RTH level break, target 0.35 / stop 0.7 x range, BE, flat 14:59) | MNQ | $1,932 | $2,642 | $1,446 | 1.43 | B, MC-confirmed (t 4.55); personal (user 2026-10-25) + funded swaps; `funded_strategies/NQ_Swing_Target_v3.txt` |
| PAPERTREND v2 (RTH open ± 0.5 ATR break at 15-min marks, gap side only, flat 14:55, 2 x ATR disaster stop) | MNQ | $2,453 | $2,528 | $2,647 | 1.42 | B, MC-confirmed (Claude's code, t 4.35); personal only (user 2026-10-25); `checks/candidates/papertrend/PAPERTREND_v2_claude.txt` |
| NFP Fade | MNQ | $291 | $467 | $826 | 0.60 | funded plan |

## Whole portfolio, every piece at 1 micro (19 pieces since 2026-10-25: Swing Target and PAPERTREND in, BB_MRM out)
- **$41,500 a year**, every year positive.
- Sharpe 3.15, Sortino 6.88, PF 1.90, Calmar 6.3, Ulcer 0.90; max DD $6,592; worst month −$2,739; 13% losing months.
- Monte Carlo, 1 year: p5 $22,800 / p50 $40,500 / p95 $61,100; P(losing year) 0.0%; max DD p50 $4,490 / p95 $7,280;
  return / DD 9.0.
- **Needs about $36,400** to keep the 1-year p95 drawdown at 20% of the account.
- **PAPERTREND's effect (18 → 19 pieces, user 2026-10-25, `analysis/papertrend_personal18.py`):** +$2,450 a year, Sharpe 3.12 → 3.15,
  return/DD 8.5 → 9.0, capital $34.4k → $36.4k; corr with the book +0.31 (Swing Target +0.12, Dual Thrust +0.18). In place of
  Dual Thrust 8.3, of Swing Target 8.75: an addition, not a swap.
- **Swing Target's effect (17 → 18 pieces, user 2026-10-25):** +$1,900 a year, Sharpe 3.04 → 3.12, return/DD 8.3 → 8.5, max DD
  $5,903 → $6,256, capital $33.6k → $34.4k (MultiCharts trades; Codex's ledger gave 8.6). Corr with the rest +0.20 but it loses
  on the book's bad days (Codex): return, not protection.
- **BB_MRM removed (user, 2026-10-25), forward log only.** It went in the same morning on the Python rebuild (t 3.4, +$900 a year,
  return/DD 8.3 → 8.7). The MultiCharts report 2018-26 (user's run, Exchange clock) showed the rebuild overstated it: 1,657 trades vs
  1,704, the rebuild's 49 extra trades were mostly winners (+$13.9k gross per NQ). On the real trade list: $40.6 a trade per NQ net,
  PF 1.17, t 2.5 (below the 3.58 bar), 2023+ t 1.2 carried by 2026 alone (2024 −$11.0k, 2025 −$4.8k, 2026 +$41.1k per NQ), max DD
  $32.7k per NQ, 5/9 years up, and fragile to the band settings. Back in only if the forward log clears its checkpoint (TIER_LIST C).
- Overnight Tick / VIX in place of Overnight Anomaly (user, 2026-10-24): 17 pieces $36.6k → $37.1k a year, Sharpe 2.96 → 3.04,
  return/DD 7.7 → 8.3, capital $35.6k → $33.6k; core 16: Sharpe 3.17 → 3.24, return/DD 9.2 → 9.6 (`analysis/overnight_tick_bench.py`).
- S30's effect (16 → 17 pieces, user 2026-10-24): +$6,000 a year, but Sharpe 3.17 → 2.96, return/DD 9.2 → 7.7, max DD
  $4,590 → $6,182, capital $26.2k → $35.6k: more money, less per unit of risk. Below ~$35.6k run the 16 without S30.
- Kusho v9 + S47 v2's effect (14 → 16 pieces, user 2026-10-24): +$6,300 a year, Sharpe 3.00 → 3.17, return/DD 8.2 → 9.2,
  max DD $5,001 → $4,590, capital $25.0k → $26.2k (`analysis/forward_log_plans_test.py`). Both stay on the forward log;
  Kusho's overnight / weekend holds are booked on the exit day (not marked daily), so its drawdown may be understated.
- Dual Thrust's effect (13 → 14 pieces, user 2026-10-24): +$2,400 a year, Sharpe 2.97 → 3.00, return/DD 7.8 → 8.2, max DD
  $4,331 → $5,001, capital $23.0k → $25.0k (corr +0.33 with the rest: it trades the same RTH hours as VB / RS / FC 2B).
- (History) Overnight Anomaly's effect (12 → 13 pieces), replaced 2026-10-24: +$1,700 a year, max DD $4,663 → $4,331, Sharpe 2.84 → 2.97, capital
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
| ~$26,200 | **Core**: the 16 without S30, 1 micro each | $30,500 | $17,000 | $5,240 |
| ~$33,600 | Core + S30 at 1 micro (same weight: puts spare capital to work, return/DD 9.6 -> 8.3) | $36,400 | $20,200 | $6,730 |
| ~$54,100 | Core x 2 + S30 at 1 micro (half weight) | $66,800 | $38,200 | $10,830 |
| ~$104,100 | **Core x 4 + S30 at 1 micro (quarter weight: the best mix, return/DD 9.9)** | $127,800 | $72,800 | $20,830 |
| ~$260,900 | Core x 10 = **1 mini (NQ / ES / CL) per piece** + S30 at 3 MNQ + 3 MES | $322,400 | $185,500 | $52,180 |

**Units:** every '$ a year' is the backtest at the sizes in its row; '1 micro' = 1 MNQ / MES / MCL per piece, so the core
at 1 micro is ~$2,500 a month and at 1 mini per piece ~$25,000 a month (not $300k a month), with drawdowns 10x as large.
**S30's weight (2026-10-24):** at full weight it lowers return per risk (Sharpe 3.17 -> 2.96); at a quarter to half of the
other pieces' size it raises it (quarter: Sharpe 3.21, return/DD 9.44), because it barely moves with them (corr +0.11).
So it runs at full weight only between ~$33.6k and ~$54.1k, then at half, then a quarter. **Minis** change costs only:
1 NQ ~$4-5 commission vs ~$10-12 for 10 MNQ (very roughly +3% at 1 NQ per piece); mix them freely (1 NQ + 3 MNQ = 13).
**Live expectation:** these are in-sample backtests; our rule expects live >= 75% of them (the 1-mini row ~$240k a year at
75%, ~$190k at 60%).

A $10k start sits just under set B's line (p95 DD ~22% of $10k): acceptable if you're comfortable with that, or start
with ~$11.5k. Add the next set only when the account reaches its line, and drop back a step after a 20% drawdown.

## Capital-expansion bench (user, 2026-10-24)
Strategies that add money only by needing more capital (lower return per unit of drawdown at the current size) go here,
not into the plan, for later when the account is large enough or sizes can be weighted finely (minis / many micros).
| Strategy | Tier | Effect when added | Why it waits | Source |
|---|---|---|---|---|
| S30 IBS reversal (NQ + ES) | B | +$6k a year, return/DD 9.6 → 8.3, capital +$7.4k | in the ladder only from ~$33.6k, at reduced weight above ~$54k | `analysis/forward_log_plans_test.py` |
| FVB First Valid Breakout (whole rule) | B | +$3.8k a year, Sharpe 3.04 → 3.01, return/DD 8.3 → 8.2, capital +$3.9k (shorts only: return/DD 8.9, but a post-hoc split) | fat tail, longs weak (PF 1.13) | `analysis/fvb_bench.py` |
| Swing Target v3, 2nd MNQ | B | 1 → 2 MNQ: +$2.2k a year, return/DD 8.6 → 8.3, capital +$1.8k (Codex ledger) | the 2nd contract lowers return per drawdown; it also loses on the book's bad days | `analysis/swing_target_bench.py` personal |
| S03 Noise Area v2 | B | personal gains need more capital (Codex); Apex plans worse | thinned since mid-2024 | `agents/codex/results/s03_v2.md` (codex/work) |
| Anson momentum (4.5 / 20) | D | full + 1 MNQ: median year $23.7k → $25.6k, p95 DD $5.0k → $6.1k, capital $25.0k → $30.4k | weak standalone (2025+ t 0.97) | `agents/codex/results/anson_personal.md` |
| R2Vault | C | personal CT gains small at equal drawdown | weak standalone (t 2.9, DSR 0.5) | `agents/codex/results/r2vault.md` |
| DriftPullBack (user's simplified v3 of DriftPullback v2.1) | C | + all: +$2.9k a year, return/DD 8.3 → 8.0, capital $33.6k → $38.8k; shorts only 8.3 → 8.5 (+$1k) but shorts earn $9 a trade since 2023 | funded: blow-ups 3% → 13% (v2.1, 10/13) | `analysis/drift_pullback_v3_test.py` |
Review this list whenever the account steps up a ladder row: re-test each at that size before adding.

## Read this before trusting the numbers
- **These are backtests on the years the strategies were chosen on.** Expect live results lower; our rule is live ≥ 75%
  of the backtest (`DEVELOPMENT_PROCESS.md`). At 60% of the backtest the full portfolio is ~$13k a year at 1 micro.
- **FC 2B is not cleared yet:** forward log until 40-80 signals. Without it the full set is ~$19.6k a year.
- **Twin Continuation holds overnight with a wide swing stop** (worst trade −$1,172 per MNQ); needs overnight margin
  (check the broker). Without Twin the full set is $18.3k a year, DD p95 $4.4k. Since 2026-10-24 its overnight holds are
  marked at each 16:00 CT close instead of booked at exit (cross-review item): no material change (max DD $4,663, MC p95
  DD $4,687, capital $23.4k, all as before; only 50 of 1,074 trades hold overnight).
- **Overnight Tick / VIX holds 17:05 → 03:00 CT with no stop** (A, MultiCharts-confirmed; replaced Overnight Anomaly, C, on
  2026-10-24). Code: `funded_strategies/NQ_Overnight_Tick_VIX.txt` (5-min MNQ, VIX daily as Data2: `C:\TradingData\VIX\VIX_daily.csv`
  via Map ASCII, refreshed daily by `tools/vix_update.ps1`; if the day's VIX is missing it uses the previous day's, which
  earned $309 vs $374 per NQ). Its backtest ends 2026-07-07 (order-flow data); the 24 MultiCharts trades after that
  averaged −$280 per NQ (watch).
- RS and FC 2B overlap (both enter at 09:01 in the opening drive's direction, corr +0.36): they can lose together.
- When to start (`DEVELOPMENT_PROCESS.md` lifecycle): from Apex payouts, after the live record matches the backtest
  (early start from ~month 3 at small size if ≥ 100 live trades, live ≥ 75% of backtest, no drift alarm).
- Not included (too weak or untested): Gold Breakout (C), plain every-night overnight long, turn of month, trend portfolio, the untested
  ideas in `IDEAS.md` (all-weather ETFs, Weekend Trend Trader, Davey's ES Keltner).

## Conservative / current / aggressive versions (user, 2026-10-25; `analysis/personal_variants.py`)
| Version | Pieces / micros | $ a year | Sharpe | Max DD | MC DD p95 | Return/DD | Capital (DD p95 / 0.2) |
|---|---|---|---|---|---|---|---|
| Conservative: proven pieces only (no forward-log pieces S30, Kusho, S47, FC 2B; Dual Thrust kept out here; Swing Target and PAPERTREND in) | 14 / 14 | $24.4k | 3.20 | $5.4k | $4.6k | 9.0 | ~$23k |
| Current (Swing Target, PAPERTREND in, BB_MRM out, 2026-10-25) | 19 / 19 | $41.5k | 3.15 | $6.6k | $7.3k | 9.0 | ~$36k |
| Aggressive: 2 micros on the five pieces with Sharpe >= 1.4 (Twin, Overnight Tick, Kusho, Overnight Bias ML, Dual Thrust) | 19 / 24 | $55.8k | 3.29 | $7.3k | $8.3k | 10.0 | ~$41k |
**User 2026-10-25: Swing Target stays at 1 MNQ; plans to switch to the aggressive version eventually.** Keep the aggressive row current whenever the book changes, and before the switch re-check its five 2-micro pieces on live and forward-log results, not only backtest Sharpe.
The aggressive weights pick pieces by their backtest Sharpe, so part of its edge over 'current' is hindsight; two of the five
(Kusho, Dual Thrust) are not live-proven yet. Pieces promote from conservative to current as they clear the forward log.
