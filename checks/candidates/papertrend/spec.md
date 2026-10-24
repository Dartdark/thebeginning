# PAPERTREND v2, NQ (candidate, 2026-10-24)

Source: the user's description and MultiCharts report (@NQ 5 minutes, 2016-09-29 -> 2026-08-14: 535 trades, +$167,378,
PF 1.66, 58.9% win, max strategy DD -$25,177). No code was supplied (the attached file was a different strategy).
Instrument: NQ futures, 1-minute bars stamped with their CLOSE time, Central time. Use the 24-hour grid
`scratch_data/g24.pkl` (analysis/grid24.Grid24: calendar rows x 1440 minute columns, column j = bar closing at 00:00 + j min)
or data/NQ_1min_20*.csv (day session 08:00-15:15 CT). The continuous contract is NOT back-adjusted. One contract ($20 a
point). Trades from 2017 on (late 2016 = warm-up); the comparison period is 2018-01-01 onward.

## Rules
- RTH bars = those stamped 08:31-15:00 CT. Only full sessions: the 14:55 and 15:00 bars must exist (half days are dropped).
- For each full RTH session: open O = open of the 08:31 bar; range = max high - min low of the RTH bars; close = close of
  the 15:00 bar.
- ATR = simple mean of the RANGES of the previous 14 full sessions (not including today). Needs 14 banked sessions.
- Bands: Up = O + 0.5 x ATR, Dn = O - 0.5 x ATR.
- Skip filter: no trade today if YESTERDAY's range is >= the max of the ranges of the last 7 sessions up to and including
  yesterday (i.e. yesterday was the widest of the last 7).
- Gap = O - previous full session's close (15:00 bar). Long only if gap > 0, short only if gap < 0 (gap = 0: no trade).
- Roll days: drop a day if a contract roll falls between the previous session's 15:00 close and today's 08:31 open (the
  gap there is the roll spread). Rolls as found by analysis/s_rank_gap_round2_test.rolls_index (the 'Sym("NQ")' frame).
  If you cannot reproduce the roll list, say so and give results with roll days kept too (the difference is ~14 trades).
- Signal marks: the 1-minute bars closing at 08:45, 09:00, 09:15, ..., 14:00 CT (every 15 minutes; equals a 5-minute bar
  closing on a 15-minute mark). At the FIRST mark whose close > Up (with gap > 0) buy, or whose close < Dn (with gap < 0)
  sell short, at the NEXT 1-minute bar's open. One trade a day. (A mark beyond the band on the side the gap forbids is
  ignored and the scan continues.)
- No target, no stop. Exit at the close of the 14:55 CT bar.

## Costs
$7.25 per round trip + 1 tick ($5) on the entry and 1 tick on the exit: $17.25 a trade.

## Mechanism (the maker's view)
Intraday trend continuation: once price is displaced ~0.5 ATR from the RTH open, slower systematic flow (vol-target,
option hedging, momentum) chases the same direction into the close. The maker reports YM makes nothing with the same rule.

## What to check
1. Rebuild the trades from this spec alone and compare with trades.csv (date, side, entry, exit, net).
2. analysis/checker.py on the rebuilt trades. 3. Placebo: random side on the same days.
