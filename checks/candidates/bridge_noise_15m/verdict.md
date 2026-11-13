PASS WITH CONCERNS (longs-only). Both-sides as posted: weaker, more fragile, not recommended.

**Replication (replica.py, from spec.md only, g24.pkl 15-min RTH bars, 1-min stop/target path).** Longs-only: 2,580 vs the
maker's 2,579 trades; 2,579 match exactly (same date, entry and exit price), P&L correlation 1.000. The one extra trade
(2025-03-05, 14:00 signal after 2 stops, +$492.75) is allowed by the spec (StopsToday 2 < 3, close 20651 vs upper band
20615): a small maker-side difference, not material. Both sides: 5,372/5,372 identical. Longs: $63.1 a trade, PF 1.28,
t 5.55 (daily t 5.06, 733 trading days), 9/9 years positive.

**Gates (checker.py).** Longs (`../bridge_noise_15m_longs/`): G1 PASS (t 5.54, DSR 0.993 at N=367), G2 PASS (2018-22 $49.7
t 3.3; 2023-26 $76.0 t 4.5), G3 PASS 9/9, G4 PASS (without the best 5%: $40.3 a trade), G5 PASS (my time-matched
random-day placebo, 200 runs, mean -$11.4, max +$11.3, p 0.000), G6 PASS (P(Sharpe<=0) 0.000), G7 PASS, G8 PASS (rho 0.80),
G9 FAIL (PBO 0.71 over 11 nearby parameter sets), G10 PASS (100% of fills inside their bar, clock +0), G11 FAIL (mechanical),
G12 not applicable (no fitted parts). Both sides: G1-G8 and G10 PASS (DSR 0.969; 2019 -$1,476; shorts $20 a trade, PF 1.07,
Sharpe 0.55), G11 FAIL (mechanical).
- G11 is not valid for this exit structure: L2 drops every trade closed inside its fill bar (mostly quick 25-pt targets), so
  the survivors start negative (-$23) and the "Sharpe kept" cannot be computed. A full re-simulation with entries one bar later
  gives longs $45.9 a trade, t 3.68, 7/9 years positive: 75% of the per-trade Sharpe kept, so it holds up (BEND).
- G9: all 11 sets earn $44-78 a trade with 9/9 years positive. The high PBO means the in-sample best parameter set changes
  between periods, not that the edge disappears. The posted defaults sit mid-pack and were not tuned. Do not optimize them.

**Leak and trap checks.** The band uses only completed earlier days: each day's move is stored after that bar's decision, and
lagging the band one more day still gives $57.9 (t 5.1). The EMA, TodayOpen (08:30) and PrevClose (15:00) are all known at
the bar close. Entry is at the next bar's open + 1 tick: mean gap to the signal close is 0.06 pt (median 0). No roll
artefact: skipping Mar/Jun/Sep/Dec days 7-16 gives $68.4. Costs are in. Requiring the price to trade through the target:
$59.4. A 2-tick slip: $55.7. Both together: $53.5. The top 5% of trades carry 39% of P&L, but wins are capped at +$492.75
(top 1% = 8%). Coin-flip entries with the same exits (placebo A, 10 runs): mean -$10.8. Knife-edge check (longs, $/trade,
t): LB14 64.9/5.8, LB30 63.6/5.5, EMA10 56.8/5.1, EMA40 62.8/5.6, stop/target 40/20 48.2/5.4, 60/30 70.9/5.2. All 9/9 years.

**Concerns.**
1. **Latency.** Entering 1 minute late cuts longs to $41.7 (t 3.6). 2 minutes: $31.3 (t 2.7). 5 minutes: $30.3. The 2-minute
   and 5-minute cases keep only about 49% of the Sharpe. With a 1-minute delay, 2026 drops to $2 a trade. After a signal the
   next minute moves +0.85 pt on average, so filling anywhere in that first minute costs about $11 a trade. The pessimistic
   case (trade-through target + 2 ticks + 1 minute late) gives $34.1, t 2.9, 8/9 years.
2. **Weak early years.** 2018-2020 earn only $20-27 a trade (yearly t 0.6-0.95). Fixed 50/25-pt brackets were about 3x wider
   relative to price then. Most of the t comes from 2021 onward.
3. **Live mechanics.** On early-close days the code has no exit: 4 longs were held past the session and 1 signal on a day's
   last bar was skipped. Apex needs an explicit session-end exit. MultiCharts needs Bar Magnifier (1-min) for its
   stop/target fills to match this resolution. Drawdown is $12.2k per 1 NQ (2023+ bootstrap p95 $14.9k) against the $4k
   trailing limit on 150K, so trade it as MNQ.

**What would change my mind:** (a) live or sim fills averaging more than ~1 pt worse than the next bar's open (the edge then
falls toward $30 a trade); (b) 2026 out-of-sample under realistic latency staying near zero; (c) a MultiCharts report with
Bar Magnifier that does not reproduce this trade list (target and stop order inside a bar).
