# FVB 'First Valid Breakout', NQ (candidate, 2026-10-25)

Source: the user's Python file `fvb_final_author.py` (the author's backtest, ET bars stamped at their OPEN, back-adjusted
data) and `SOURCE_SUBMISSION.md` in this folder; you may read both. Our port: `trades.csv` (built from our data).
Data: `scratch_data/g24.pkl` (analysis/grid24.Grid24: calendar rows x 1440 columns, column j = the 1-minute bar CLOSING at
00:00 + j minutes, Central time). Mapping: the author's bar opening at ET minute m = our column m - 59.
One NQ contract ($20 a point, tick 0.25). Trades 2018-01-02 onward (2017 = warm-up). Continuous contract NOT back-adjusted.

## Rules (the author's locked config, VP2 sizing left out)
- RTH bars: columns 511-915 (08:31-15:15 CT = bars opening 09:30-16:14 ET). Premarket: columns 181-510 (03:01-08:30 CT).
  A day needs >= 10 RTH bars and premarket bars.
- Daily RTH stats: high, low, open (first RTH bar's open), close (last RTH close), range, body ratio |close-open|/range.
  ATR = simple mean of the last 14 RTH ranges, known the day before (excludes today).
- Skip a day if the prior RTH range > 1.5 x ATR, or the premarket range > 1.0 x ATR, or premarket high <= low.
- Drop days whose window (previous RTH day's 15:15 bar -> today's 15:15 bar) contains a contract roll (rolls from
  analysis/s_rank_gap_round2_test.rolls_index on Sym("NQ")).
- Levels (pdh/pdl = prior RTH high/low, pmh/pml = premarket high/low):
  gap day (pdh < pml or pdl > pmh): long level pmh, short level pml.
  otherwise: long level pdh, short level pdl, plus pmh (long) if != pdh and pml (short) if != pdl.
- Scan RTH bars closing 08:31 to 10:30 CT in order (signal bar must close before column 631). Levels are checked in the
  order above; the first level whose close is beyond it (long: close > level; short: close < level) triggers. Shorts are
  skipped (try the next level) when the prior day's body ratio >= 0.6.
- Entry at the next bar's open (tick-rounded). Stop = entry -/+ round_to_tick(0.18 x ATR). No target. The stop is live from
  the entry bar on: long stops when low <= stop, fills AT the stop. Otherwise exit at the close of the bar in column 911
  (15:11 CT = the bar opening 16:10 ET); if the day ends first, the last RTH close.
- After a stop: one more trade allowed that day (max 2), scanning from the bar after the stop bar, with the stopped level
  removed (same entry window). After an EOD exit: done.

## Costs
$7.25 per round trip + 1 tick ($5) on the entry and on the exit: $17.25 per trade.

## Mechanism (the maker's view)
Resting liquidity and stops at prior-session levels; a confirmed close beyond one starts a continuation that persists into
the close; failed breaks are cut quickly. Low win rate (~25-30%), fat right tail.

## What to check
1. Rebuild from this spec and compare with trades.csv. 2. analysis/checker.py checks/candidates/fvb. 3. Placebo: the same
entries in the opposite direction with the mirrored stop; random side. 4. Our port vs the author's code: any mismatch in
the session mapping or the level logic.
