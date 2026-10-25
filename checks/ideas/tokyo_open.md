# Idea card: the Tokyo open (user + Claude, 2026-10-25; process: S_RANK_PROGRAM.md 'Idea-to-strategy process')

Status: stage 0 agreed (user 2026-10-25) -> stage 1 (look only, 2018-2022 data only; 2023-26 kept for the stage-3 holdout).

- Who is forced: (1) Japanese institutions (life insurers, pension funds, investment trusts) adjusting US-equity exposure
  and FX hedges when Tokyo desks open; (2) market makers repricing NQ / Nikkei risk together as Tokyo cash opens after a
  quiet stretch; (3) gotobi days (5th / 10th / 15th / 20th / 25th / 30th, or the business day before when that is a
  weekend or holiday): Japanese importers must buy USD before the 09:55 JST fix, a known forced flow in USD/JPY that may
  spill into US futures.
- When: 09:00 JST = 18:00 CT (US winter) / 19:00 CT (US summer); every weekday, ~250 a year (~100-150 after a size filter).
- Direction (hypothesis): the first push after the open is liquidity-driven and partly reverses within 1-2 hours.
  Prior evidence: following the first 15 / 30 minutes lost $8-88 a trade, t to -2.3 (TIER_LIST round 4,
  analysis/forced_groups_round4_test.py); Asia VWAP fades (17:00-23:59) also lost.
- Why not arbitraged: middle of the US night, thin, small per trade, ignored by US systematic traders.
- Built-in placebo: Japan has no DST, so the open moves between 18:00 and 19:00 CT; a real effect moves with the Tokyo
  clock, and the same clock time in the other season (no open) shows nothing.
- What kills it: no reversal in stage 1; the reversal also appears at the clock-shifted placebo time; under ~$40 gross a
  trade; or it is Overnight Tick / Overnight Bias again (overlap check).
- Stage 1 plan: average NQ path 17:00-23:00 CT aligned to the Tokyo open, signed by the first 15 / 30-minute push, in ATR
  units; by push size; vs the clock-shifted placebo and random times; gotobi vs ordinary days from the open to the 09:55
  JST fix (NQ 2018-22), plus a sanity check that the USD/JPY flow exists (Yahoo hourly, recent years only).

## Stage 1 result (2026-10-25, `analysis/tokyo_open_stage1.py`, NQ 2018-22 only) -> DROPPED at the stage-1 gate
- The open is a real event: the first 15-minute push is ~40% bigger than at the same evenings' other clock hour
  (0.042 vs 0.029 ATR), so Tokyo's open does move NQ.
- But the push does not reverse (next 60 min +0.003 ATR, t +1.1; a fade would make -$18.5 gross per NQ) and does not
  continue much either: it is a permanent repricing, not a liquidity overshoot. No push-size tercile or year reverses
  reliably; the placebo hour shows the same flat shape.
- Gotobi: nothing on NQ (open -> 09:55 fix, gotobi vs ordinary t -0.6). The USD/JPY flow itself still exists but runs
  the other way in 2024-26 (the 00:00-01:00 UTC hour falls 2.0 bp on gotobi days, t -2.1).
- Lesson: an open that moves price a lot is not enough; the move must be forced AND temporary. Look for actors who have
  to trade regardless of price and whose trade is undone later (hedges, rebalances, settlements), not for activity.
