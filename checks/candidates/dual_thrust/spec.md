# Dual Thrust v4, NQ, Central-time build (candidate, 2026-10-24)

Source: the user's PowerLanguage file `NQ_Dual_Thrust_v4_CT.txt` in this folder (the BASE strategy; you may read it).
Instrument: NQ futures, 1-minute bars stamped with their CLOSE time, Central time (data/NQ_1min_20*.csv, day session
08:00-15:15 CT). Trades 2018-01-02 onward (2017 = warm-up). One contract (per NQ, $20 a point).

## Rules
- RTH bars = those stamped 08:31-15:00 CT. For each RTH day keep its high H, low L and close C (close of its last bar).
- On day D, using the PREVIOUS RTH day only: RR = max(H - C, C - L). ADR20 = mean of (H - L) over the last 20 RTH days
  (the 20 days before D). Needs 20 banked days.
- Skip day D if RR / ADR20 > 1.2, or if D is on the code's holiday list (MLK Monday, Presidents Monday, Memorial Monday,
  Jun 19 / Mon Jun 20 / Fri Jun 18, Jul 3 / Jul 4 / Mon Jul 5, Labor Day Monday, Thanksgiving Thursday and the Friday
  after, Dec 24 / 25 / Mon Dec 26).
- Day open O = open of the 08:31 bar. UpTrig = O + 0.5 x RR, DnTrig = O - 0.5 x RR.
- Scan bars stamped 08:31 to 14:30 in order; at the FIRST bar whose close > UpTrig buy (close < DnTrig: sell short) at the
  NEXT bar's open. At most one trade per day.
- Entry bar (the bar you filled at the open of): only a stop at (signal bar close - 50) for longs / (+ 50) shorts; no
  target. From the next bar on: stop = entry -/+ 50 points, target = entry +/- 100 points (limit).
- A stop fills at the stop price, or at the bar's open if the bar opens beyond it. The target fills only when the bar
  trades at least 1 tick through it (high >= target + 0.25 for longs), at the target (or the open if it opens beyond).
  A bar that reaches both counts as the stop.
- If a bar stamped 14:55 or later closes with the position open: exit at the next bar's open (normally the 14:56 bar).
  If the day's data ends first: exit at the last close.

## Costs
$7.25 per round trip + 1 tick ($5) per market or stop fill: entry always; stop and flatten exits too; target exits none.
So stop / flat trades pay $17.25, target trades $12.25.

## Mechanism (the maker's view)
Chalek's Dual Thrust: a break of the open by half the prior day's 'range' (max of high-close / close-low) marks a
trend day; the band filter skips days after an abnormally large prior range (exhausted). Public, widely known rule.

## Variants tried
The user's author reports ~33 looks in their own search (band 1.9 -> 1.2 and one trade a day were adopted from it);
the maker ran 10 sensitivity variants (K, band, holiday, stop / target) without changing the settings: `variants` 44.
Not pre-registered. `placebo.csv` = 20 runs at the same signal bars with a random side.

## trades.csv
date, side (+1 / -1), net ($ per NQ after costs), entry, exit, kind (stop / target / flat / close).
