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
- Funded: see the MultiCharts section below.

## Code notes
1. Vote B uses `UpTicks` / `DownTicks` with "Build volume on: Trade volume": correct for the file; our exports cannot rebuild it.
2. The GCCOMBO file is the author's own computation (GLD holdings, the decoupled flag) and ends 2026-09-25: live use needs his
   updates; check that a date's row only uses data known before 10:00 ET that day (GLD holdings publish after the close).
3. `this bar at close` exits = market orders at the bar close live.
4. Stretch `sigCount` counts signals even when not taken (as tested).
5. Gold at $4,000+: 1 GC is too big for a 50K account (the note says so); MGC only.

## The user's MultiCharts report (2026-10-24, `mc_reports/... @GC - 1 Minute GC COMBO v2.xlsx`, `analysis/gc_combo_mc_check.py`,
`analysis/gc_combo_mc_eval.py`, trades `mc_trades.csv`)
- First run was an hour early: on our MultiCharts **@GC runs on New York time**, so `ETminusChart` must be **0** (the author's
  'exchange chart = 1' assumes a Chicago chart). Second run (ETminusChart 0): **1,204 trades in the author's window, and every
  year's count and bp equal the note** (2018 122 / 3.5 ... 2025 157 / 1.6). Parity: exact.
- At our costs ($7.25 + 1 tick per market / stop fill, per contract), 2018 → 2026-09-23, 1,188 trades:
  **$104 per contract, PF 1.24, t 2.1**, 9/9 years; IS 2018-24 $109 (t 3.5), **OOS 2025-26 $83 (t 0.4)**; blend $87 (OOS $93,
  t 0.4; score 2 $41, score >= 3 $146), stretch $141 (OOS $57, t 0.1); blend longs $95 / shorts $77.
- **After the note's cutoff (2026-08-08 → 09-23, 14 trades): −$39.2k** at 1-2 GC (Aug −$38.2k, Sep −$8.6k). 2026 total $3.5k.
- Daily (as traded): Sharpe 0.76, Sortino 1.18, PF 1.27, Calmar 0.31, Ulcer 4.6, **max DD $62.5k**; longs Sharpe 0.44, shorts 0.62.
  2023+ Sharpe 0.51 (5-95% −0.43 to 1.42, P(≤ 0) 18%). MC at 1-2 MGC: P(hit the $2,000 trail in a year) 29%.
  DSR 0.27 at our 296 items, 0.06 at the author's 10,831.
- **13 trades are held over a holiday halt** (Presidents / Memorial / Labor / MLK / July 4 / Thanksgiving / Christmas): the 13:30
  ET exit bar does not exist, so the position rides to the next session (worst −$3,960). Not Apex-legal; needs a holiday flatten.
- Evaluation with these trades (holiday holds left out): 50.1% → 50.0 / 48.7 / 46.3% at 1 / 2 / 3x MGC. Funded (bootstrap on the
  MultiCharts trades, year 1 / year 2 / blown): plan $9,354 / $12,088 / 7.0%; + 1x MGC $9,278 / $11,604 / 11.5%; + 2x MGC $7,474 /
  $8,488 / 38.2%; in place of CL Sunday $8,800 / $11,838 / 8.8%. Worse in every case (the proxy-B rebuild said the same).

## Verdict
**C.** Rebuilt exactly in MultiCharts, but at our costs it is t 2.1 with nothing left out of sample (2025-26 t 0.4, and −$39k in
the six weeks after the author's cutoff), a $62.5k drawdown per 1-2 GC and holiday holds. No gain in either Apex plan.
