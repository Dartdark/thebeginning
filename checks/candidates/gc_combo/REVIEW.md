# GC_COMBO v2 (user's upload 2026-10-24: `GC_COMBO_v2_community.txt`, `GCCOMBO.txt` daily vote file, research note)

## The rule (frozen; defaults = the author's tested strategy)
Gold (GC), 1-min full Globex chart; data2 @CL, data3 the GCCOMBO file (GLD vote, dollar-decoupled flag). One position at a time.
- **Blend** at 10:00 ET (09:00 CT): five fixed-sign votes, A morning price (08:20 → 10:00 ET), B AGAINST the morning taker flow
  (UpTicks − DownTicks), C GLD creations / redemptions, D yesterday's big crude move, E A again on dollar-decoupled days.
  |score| >= 2 → 1 GC (2 at >= 3) next bar, out at the 13:30 ET bar close. No stop.
- **Stretch short:** a close 0.5 ATR under the session VWAP, 08:20-15:00 ET; stop 0.505 ATR, target 2R, out 16:00 ET.
Note (MultiCharts, $2.30/side + 1 tick, 2017-09 → 2026-08): 1,204 trades, $188, PF 1.37; IS $164, sealed OOS 2025-26 230 trades
$289 (4.4 bp vs IS 7.5 bp). The author's own programme ledger is N = 10,831 tests; he says the deflated Sharpe fails at that N.

## Rebuild (`analysis/gc_combo_test.py`, 2018-01 → 2026-10, per GC, $7.25 + 1 tick per market / stop fill)
**Vote B needs UpTicks / DownTicks; our GC exports carry total volume only.** The minute tick-rule proxy does not reproduce
it (B alone −0.8 bp, t −0.7 vs the note's +3.1 bp, t 3.2), so the rebuilt blend is the note's blend with a noise vote. Every
other piece reproduces the note:

| research panel 2018-24, gross bp (note 2016-24) | ours | note |
|---|---|---|
| A price alone | 1.3 (t 1.3) | 1.3 (t 1.4) |
| C GLD alone | 2.8 (t 1.9) | 2.6 (t 1.9) |
| D crude alone | 4.2 (t 1.8) | 3.8 (t 1.8) |
| E decoupled alone | 6.1 (t 2.2) | 6.4 (t 2.5) |
| blend without B | 672 days, 5.2 bp, t 2.8 | 769 days, 5.4 bp, t 3.1 |
| stretch IS | 315 trades, 7.8 bp | 314 trades, 9.4 bp |
| stretch OOS | 80 trades, 1.4 bp | 67 trades, −1.4 bp |

Full rebuild (with the proxy B): 892 trades (1.9 a week vs the note's 2.6-2.8), $133 per contract, PF 1.30, t 2.3, 9/9 years;
IS $105 (t 2.7), OOS 2025-26 $238 (t 1.0). Blend $108 (score 2: $30, t 0.5; score >= 3: $278, t 2.6); stretch $163 (OOS
1.4 bp). Random side on the blend days: beaten by 0.4% of 1,000 runs.
Daily metrics (1-2 GC): Sharpe 0.93, Sortino 1.72, PF 1.37, Calmar 0.86, Ulcer 4.3, max DD $20.8k; longs Sharpe 0.66 / shorts
0.68. 2023+ P(Sharpe <= 0) 1%. Monte Carlo at 1-2 MGC: one-year P(loss) 15.6%, P(hit $2,000 trail) 8.9%. DSR (293) 0.46.

## Apex (`analysis/gc_combo_bench.py`, MGC = GC / 10)
- Evaluation (combine set 50.1%): + 1x / 2x / 3x MGC 50.4 / 49.8 / 48.3%. No gain.
- Funded: queued after the T_ONESIDE bootstrap (2026-10-24).

## Code notes
1. Vote B uses `UpTicks` / `DownTicks` with "Build volume on: Trade volume": correct for the file; our exports cannot rebuild it.
2. The GCCOMBO file is the author's own computation (GLD holdings, the decoupled flag) and ends 2026-09-25: live use needs his
   updates; check that a date's row only uses data known before 10:00 ET that day (GLD holdings publish after the close).
3. `this bar at close` exits = market orders at the bar close live.
4. Stretch `sigCount` counts signals even when not taken (as tested).
5. Gold at $4,000+: 1 GC is too big for a 50K account (the note says so); MGC only.

## Verdict
C pending a MultiCharts report: what we can rebuild matches the note, but the rebuilt combo is t 2.3 (bar 3.58), the author's
own multiple-testing count is 10,831, and the one vote we cannot rebuild (B) is the note's strongest. Next step if wanted:
the user runs the community file in MultiCharts (setup on the note's page 5) and exports the Performance Report to
`mc_reports/`; then the MC trades replace the proxy and the benches are re-run.
