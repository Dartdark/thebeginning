PASS WITH CONCERNS (7/8 gates; G1 fails only on deflated Sharpe 0.939 vs 0.95. t 4.39 clears t_threshold(287) = 3.58, which is the CLAUDE.md promotion rule.)

## Replication (replica.py, built from spec.md + the v4 file only, raw data/NQ_1min_20*.csv, 2017 as warm-up)
- 1,611 trades vs 1,611 in trades.csv. Same 1,611 dates, and side, entry, exit, kind and net agree on 100% of them. P&L correlation 1.000, net $226,255.25 on both. There are no mismatches, so I did not build a separate _replica folder.
- I checked the spec against the PowerLanguage source and they agree: RR and ADR20 come from banked prior days (ADR includes D-1, never D), O = open of the 08:31 bar, the scan runs 08:31-14:30 on closes, the entry-bar stop is the trigger close -/+ 50, the bracket is 50/100 from the next bar, and the flatten fires on the 14:55 close and fills at the 14:56 open. The target needs price to trade 1 tick through it, and a bar that hits both counts as the stop. Both of these are stricter than MultiCharts.

## Gates (analysis/checker.py, checker_report.md)
G1 FAIL: t 4.39, PSR 1.000, DSR(N=287) 0.939 | G2 PASS: 2018-22 $125/trade (t 3.14), 2023-26 $159 (t 3.07) | G3 PASS: 9/9 years
positive (weakest 2023 $6.8k, Sharpe 0.4) | G4 PASS: still +$65k ($42.6/trade) without the best 5% | G5 PASS: 0/20 maker placebo runs
reach the real mean (their placebo mean $18.8). My own 60 random-side runs average $12.4 (sd 27.5, max 65.9), p = 0 | G6 PASS: 2023+ P(Sharpe<=0)
0.000 | G7 PASS: 1,611 trades vs MinTRL 215 | G8 PASS: rho 0.80.
Metrics: Sharpe 1.46, Sortino 2.64, PF 1.28, Calmar 1.27, Ulcer 3.55, max DD $19.6k (1 NQ). Longs Sharpe 0.97 / PF 1.26; shorts
1.08 / 1.30. On 2023+ the longs are weak: Sharpe 0.69, bootstrap p5 -0.11, P(Sharpe<=0) 0.07.

## Leak / trap checks
- **Look-ahead:** none found. Every level comes from earlier days or from the closes of finished bars, and entries fill at the next bar's open. The data has its time stamp at the bar's close: volume spikes at 08:31 and 15:00, which matches.
- **Holidays and half-days:** short days (12:00 / 12:15 CT closes) still count as banked days, as they do in MultiCharts. Good Friday 2023 and 2026 and 2025-01-09 have no RTH bars, so they are not banked. Every trade day has its 08:31 bar and data up to 15:15, and no trade ends as 'close'. Turning the holiday filter off adds 28 trades worth +$117 in total, so the list has no effect and does not hide anything. One normal day, 2020-11-30, is missing from the data. That is minor.
- **Rolls:** no trade day has a jump within the session that looks like a contract roll. The only bar-to-bar jumps over 25 pts are real: the limit moves in March 2020 (two trades, both normal stops) and one thin bar on 2022-03-08 (no trade). RR, ADR and the triggers all use one contract per day, so overnight roll gaps cannot leak in.
- **Fills:** 5 entry-bar stops. Stops average -$1,017, so there are no favourable gap fills. Extra stop slippage costs little: +1/+2/+4 ticks on stops gives $222k/$219k/$211k, and 3 ticks on every market or stop fill gives $198k ($123/trade). If targets fill on a touch, the total rises by only $3k.
- **Knife-edge:** none. Sweeping my replica's settings: K 0.4/0.6/0.7 gives t 3.7-3.8 and K 0.3 gives t 2.2. Band 1.0/1.5/none gives t 4.2/4.0/3.6. SL 40/60 gives t 4.7/4.2. TP 80/150/none gives t 3.6/4.7/4.4. Every 2023+ mean is above $79.

## What would change my mind
1. The real MultiCharts report on the v4 file. If it misses the Python net by more than about 10%, or its trade dates differ by more than 5%, something in this rebuild is wrong (bar stamps, session roll, Date vs session date).
2. Size for Apex. One NQ means a $1,017 stop against a $2,000 trailing drawdown, with a $19.6k historical drawdown. At a tradable size (1-2 MNQ) the result needs the funded bench and Monte Carlo. The checker gates do not answer this.
3. Multiple testing. The author made about 33 looks and the maker about 44. DSR is 0.939, just under the bar. If that count is understated, or the 2023+ longs (P(Sharpe<=0) 0.07) keep fading, I would treat it as a shorts-led strategy and re-gate.
