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

## Stage 0 verdict (2026-10-25): CLOSED - already tested as a strategy (missed in the first evidence check)
`analysis/gamma_regime_test.py` / `gamma_momentum_test.py` (2026-10-13/14, outputs in analysis/outputs/): 30-minute
autocorrelation above / below the flip -0.007 / -0.004; the bigger moves below the flip are explained by realized vol;
regime rule (fade above, follow below) -$105 a trade (632 trades); afternoon pin toward maj_pos -$161; last-30 momentum by
regime = shuffled-label placebo (p 0.67). Gamma sizes moves, it doesn't direct them.
Live feed (for the record): The Bridge's OFB_Gex* PowerLanguage functions on its NQ bar feed would give the levels live in
MultiCharts, if that feed updates in real time (manual section 4.3).
Process fix: the stage-0 evidence check searches TIER_LIST, HANDOFF.md, NEW_CHAT_BRIEF.md and analysis/outputs/*.
