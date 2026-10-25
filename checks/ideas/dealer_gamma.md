# Idea card: dealer gamma positioning (user + Claude, 2026-10-25; process: S_RANK_PROGRAM.md)

Status: stage 0 drafted; waiting on the user: (1) is The Bridge's gamma flip available live (MultiCharts / VPS)?
(2) OK with ~2.5 years of holdout?

- Who is forced: dealers short / long 0DTE and weekly NDX / QQQ options must delta-hedge continuously in NQ / QQQ.
- Mechanism (two sides): above the gamma flip (dealers long gamma) hedging sells rallies / buys dips -> moves fade, pull
  toward big positive-gamma strikes; below the flip (short gamma) hedging chases -> moves extend. Hedges unwind at the
  15:00 CT expiry (temporary).
- When: every day, strongest in the afternoon as 0DTE gamma builds; ~1-2 trades a day possible (250+ a year).
- Direction: fade above the flip, follow below; the regime picks the side.
- Prior evidence (filters only): LDF below the flip $158 vs above $36; 14:00 -> 14:30 follow below $127 vs above $28
  (placebo p 0.09) (TIER_LIST rows 'Late-Day Flow sized by the 0DTE gamma flip', 'Gamma last-30', '0DTE NDX gamma regime').
- Placebo: both sides must show (mean reversion above AND momentum below); shuffled regime labels must kill it.
- Kills: no difference above vs below; a few days carry it; flip not known in real time; no live flip feed for the user.
- Data: data/GEX_1min_*.csv (The Bridge, 2022-09 -> 2026-07-07, ET times). Look / design 2022-09 -> 2023-12; 2024 ->
  2026-07 untouched holdout. Caveat: 2023 partly seen in the LDF filter test.
- Stage 1 (look only): persistence / reversal of 15 / 30-minute NQ moves above vs below the flip by hour; drift toward
  maj_pos in the afternoon; after big moves, continuation below vs reversal above.
