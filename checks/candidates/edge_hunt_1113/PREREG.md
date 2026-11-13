# Edge hunt for the evaluation book: untested mechanisms in the hours the book does not use (user 2026-11-13: "yes run it")
Written before any result. Survey first (TIER_LIST grep, 2026-11-13): already tested and NOT repeated here: midday direction / European
close (follow and fade), MAGNET18, Asia / Europe open follows, Tokyo reversal, overnight VWAP fades, FOMC / CPI / NFP reactions, month-end,
gap fill, Gao first-to-last half-hour, order-flow prediction (39 features), pairs / spreads, failure tests at swing points, mega-cap earnings.
The evaluation needs ACTIVE pieces (EOS / NFP showed rare trades cannot move a 21-day evaluation), so 6 of 7 trade often.

NQ, 1-minute 24h grid, per NQ, costs $7.25 + 1 tick per market / stop fill (targets: limit, no slip). ATR = 15-day (known at the open).
Early-close days skipped. Each rule fixed here; no parameter is tuned after seeing results.

H1a INTRADAY PERIODICITY, RTH (Heston, Korajczyk & Sadka 2010: a half-hour's return predicts the same half-hour on later days; recurring
    institutional flow at fixed clock times). 13 slots 08:30-15:00. For slot k today: the previous 20 sessions' slot-k returns (open of the
    first minute to close of the last, / ATR); if |mean / sd x sqrt(20)| >= 2 -> trade sign(mean) for that slot; stop 0.15 ATR.
H1b the same on the 15 overnight hours 17:00-08:00 CT (hour slots).
H2  OVERNIGHT-EXTREME SWEEP (stops rest beyond the Globex high / low; a breach that fails = a stop run). ONH / ONL = high / low 17:00-08:30.
    08:31-13:00: after the first trade >= 0.02 ATR beyond ONH, the first 5-minute bar (within 30 min) that closes back below ONH -> short
    next minute; stop = the sweep's high + 1 tick (at least 0.05 ATR); target 2 x stop distance; out 14:30. Mirror at ONL. First setup only.
H3  RANGE-REGIME OPENING-RANGE FADE (the complement of Overnight Bias, which trades breaks only when ADX > 30). 15-min ADX(14) at the 08:45
    bar < 20: the first 15-min close (09:00-11:00) beyond the 08:30-08:45 range -> fade next bar; target the range midpoint; stop 0.25 ATR;
    out 14:30. One trade a day.
H4  OPENING RELATIVE VOLUME (Zarattini-Aziz 'in play': abnormal opening volume = participation -> continuation). Volume 08:31-08:45 / its
    20-session mean >= 1.5 -> follow sign(08:45 close - 08:30 open) from 08:46; stop 0.25 ATR; out 14:30. Control (info): ratio < 1.
H5  LONDON BREAK OF THE ASIA RANGE (European flow resolves the thin Asian range). Range 17:00-01:00 CT; the first 15-min close 02:15-07:00
    beyond it -> follow next minute; stop = range midpoint (distance 0.05-0.25 ATR); out 08:25. One trade a night.
H6  FRIDAY AFTERNOON DE-RISK (weekend risk is cut against the week's trend). Fridays: week move = Fri 13:00 - the week's first 08:30 open;
    |move| >= 1 ATR -> fade 13:01 -> 14:55, stop 0.3 ATR. (The one rare rule, ~20 a year.)

GATES (as lab/README): G1 design 2018-22: avg > 0 and t >= 2.0. Fail -> stop, the 2023-26 holdout is NOT opened.
G2 one holdout look 2023-26: avg > 0 and t >= 1.5; whole sample t >= 2.45 (7 trials, one-sided 5%). G3 random-side placebo (200 runs) p < 0.05.
G4 evaluation bench on bench150.LIVE_EVAL at 1-3 MNQ: the 2023-26 band AND the account-now band above 0, then the resize rule.
G5 strategy-checker + MultiCharts code before any live use. Expected before running: 0 or 1 of 7 reach G4.

## Result of the 7 (2026-11-13, `analysis/outputs/edge_hunt_1113_output.txt`): 0 of 7 pass G1; no holdout opened
Design 2018-22, per NQ: H1a -$3 (t -0.2), H1b -$20 (t -1.3), H2 +$10 (t 0.3), H3 -$19 (t -0.3; longs +$75, shorts -$100), H4 +$64 on 50 trades
(the 1.5x volume threshold fires 8 times a year: too rare to judge; control ratio < 1: +$104, t 1.4 = the plain opening-drive follow),
H5 -$46 (t -1.4, every year negative), H6 +$65 (t 0.6) but LONGS (after down weeks) +$498 (t 2.3) and SHORTS (after up weeks) -$258 (t -3.1).

## Amendment 1 (written after the design results above, BEFORE any run of it; the 2023-26 holdout is still unopened for every rule)
H6's two sides say the same thing: NQ rose on Friday afternoons in 2018-22 whatever the week did. Post hoc from design years only, so it
gets its own gates: H6b FRIDAY AFTERNOON LONG: every Friday (no early close), long 13:01 -> 14:55 CT, stop 0.3 ATR. Mechanism candidates:
short-covering / dealer hedging into the weekly options expiry and the weekend. Controls (design only): the same window Mon-Thu.
Same gates: G1 design avg > 0, t >= 2.0 AND Fridays beat Mon-Thu; G2 holdout avg > 0, t >= 1.5, whole t >= 2.45 (now 8 trials: 2.50);
G3 placebo = random weekday instead of Friday (same count), p < 0.05; G4 evaluation bench.

## Result of Amendment 1 (`analysis/outputs/edge_hunt_1113_h6b_output.txt`): G1 PASS, G2 FAIL
Design 2018-22: Fridays +$156 a trade (t 2.25, 247 trades) vs Mon-Thu -$27; Friday minus Mon-Thu +$183 (t 2.33). ONE holdout look 2023-26:
Fridays -$80 (t -0.76, 191 trades; 2026 -$17.0k), Mon-Thu -$51. Whole sample t 0.88; random-weekday placebo p 0.10. Dead: a 2020-22 effect.
ROUND TOTAL: 8 pre-registered rules, 0 reach the evaluation bench. The holdout stayed unopened for the 7 that failed design.
