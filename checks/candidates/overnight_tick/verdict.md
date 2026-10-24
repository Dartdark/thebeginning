PASS WITH CONCERNS

# overnight_tick: checker verdict (2026-10-24)

**Replication.** I rebuilt it from spec.md alone (`replica.py`: g24.pkl, OF 15:16-16:15 ET, VIX SMA25 of D, entry at the 17:06 open of the next
evening session, exit at the 03:01 open, $17.25 a trade). Result: 536/536 trades on the same dates, P&L correlation 1.000, 0 nets differing
by more than $1, $200,534 in both. No mismatches.

**Gates** (`checker_report.md`; the replica folder `overnight_tick_replica/` gives the same numbers). G1 t 5.21, DSR(N=291) 0.991 | G2 2018-22
$279 (t 3.78), 2023-26 $518 (t 3.67) | G3 9/9 years positive (2018 only $3.3k, $52 a trade) | G4 without the top 5%: $67,970 left (top 5% =
$129k of $200k) | G5 placebo share 0.000 (placebo mean $165) | G6 P(Sharpe<=0) 0.000 | G7 536 vs MinTRL 52 | G8 rho 0.81. All 8 pass.
Sharpe 1.73, Sortino 3.26, PF 1.98, Calmar 1.78, Ulcer 2.91. The strategy is long only, so the long rows are the whole strategy. Max DD per NQ is $12,801.

**Leak and trap checks**
- *Is VIX(D) known at 17:05 CT?* Yes. dVIX(D) vs the NQ RTH return of D: corr -0.555. Its residual loads on the 15:00-15:15 CT move
  (-0.106), which fits a 16:15 ET close, and it has zero correlation with the 15:15 -> next 08:30 move (0.015 / 0.000). No date shift.
  Live risk: MultiCharts may still show D-1's bar at 17:05. With VIX(D-1) the regime changes on 14% of nights and the result is
  $309 a trade, t 4.22 (skipped $30). That still holds up.
- *ET vs CT alignment of order flow:* the OF close at ET t matches the NQ grid close at CT t-1h on 96.9% of bars, the same in summer and
  winter (DST is fine). The mismatches are contract differences around rolls (March 90.7%). OF bars are stamped at the close (the 09:30 bar is
  the quiet pre-open minute). The window ends 15:15 CT, before entry. Note: in the OF files `volume` == `upvol` on 100% of rows
  (MultiCharts' intraday Volume = UpTicks quirk), so upvol+downvol is the total. No leak.
- *Roll nights:* `roll_minutes` finds 36 switches, all at 17:01-17:04 / 03:32-03:33 / 05:24. None falls inside 17:06-03:01, so the exclusion
  removes 0 nights and none is needed. The largest 1-minute moves inside the held nights are news (2020-03, 2025-04-09, 2025-05-12), not rolls.
- *Sunday / holiday:* entries are Mon 87, Tue 104, Wed 126, Thu 105, Sun 114. Two longer gaps: 2023-12-22 -> Christmas-evening entry, and Good
  Friday 2025-04-17 -> Sunday entry (-$2,972). Both follow the spec's "next evening session". Costs are included. No survivorship issue
  (one continuous contract).
- *Is the four-cell interaction a post-hoc fit?* Partly. Base down-day nights: $175, t 3.08. Taken $374 (t 5.21) vs skipped -$74;
  taken minus skipped is $448, t 3.90 (2018-22 t 3.42, 2023-26 t 2.35; author's OOS after 2024-02-12: taken $632 vs skipped -$17).
  By cell, 2018-22 / 2023-26: neg_hi $351 / $518, pos_lo $169 / $517, neg_lo **-$242 / +$200**, pos_hi $50 / -$280. Only neg_hi is
  positive in every year. The excluded neg_lo cell turned positive in 2025 (+$640) and 2026. Each factor alone is weaker (high VIX
  t 2.85, RSV<0 t 2.94).
- *Threshold:* t peaks exactly at the natural 0 (5.21). At ±0.005 (0.22 sd of RSV) it is 3.9 / 4.5; at -0.02 it is 2.3 and at +0.02 it is 3.0. 62% of nights have |RSV| < 0.02,
  so much of the edge comes from the SIGN of a near-zero imbalance.
- *RSV data source:* with an NQ bar-direction proxy (signs agree with the order flow on only 62.6% of nights), taken is $272 (t 3.23) vs skipped $59.
  Taken minus skipped falls to t 1.84 (2023-26: t 0.94). VIX length 10/20/30/40: $335-346 a trade (25 is the best at $374, as the author chose).

**What would most change my mind**
1. The MultiCharts UpTicks/DownTicks on the live feed. They are neither The Bridge aggressor volume nor my bar proxy. If their signs agree
   with the OF RSV on under ~75% of nights, expect the bar-proxy result (filter t < 2), not t 5.2. Run PrintDiag against OF for 2024-26 before promoting.
2. The neg_lo cell. If it stays positive (2023-26 is already +$200, n=98), the interaction reduces to "high VIX, negative flow" plus the
   plain down-day drift, and the extra edge of the second cell is a fit.
3. Size: the $12.8k max DD per NQ means only MNQ fits a $2,000 Apex trailing drawdown. Check the funded bench at 1-2 MNQ before any rank.
