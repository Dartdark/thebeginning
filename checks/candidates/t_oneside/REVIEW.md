# T_ONESIDE, night-volume switch (user's upload 2026-10-24: `T_ONESIDE.txt` + `T_ONESIDE_research_note.pdf`)

## The rule (frozen by its author, 'do not optimize')
NQ 1-min Globex chart in CT, IOG off, one trade a day, never both legs.
- **Heavy night** = night volume (17:00 reopen → the 08:29 bar, >= 30 bars) > 1.4 x the median of the prior 20 nights.
- **T (open fade), heavy nights:** fade the night's move (first night bar's open → 08:29 close): market at 08:29:00 CT
  (a minute before the bell), out at 08:44:00.
- **OS (one-sided long), other nights:** at the 09:59 bar, (morning high − 08:29 open) > 2 x (08:29 open − morning low) and
  close > session VWAP → long at 09:59:00; out at the next open after a close below VWAP, else 10:59:00.
- The note's headline uses a stop: 0.40 (T) / 0.30 (OS) x ATRd (mean 08:31-15:00 range of the last 20 full sessions),
  chosen on 2016-20 with worst-case fills, confirmed once on 2021-23. **The uploaded file has no stop** → `T_ONESIDE_v2.txt`
  adds exactly that stop (`UseStop false` = the original).

Note (MultiCharts, 1 NQ, $13.50 a round trip, 2016-10 → 2026-08): 988 trades, $125 (no stop $116), PF 1.47; IS (< 2023-09-08)
PF 1.64, OOS PF 1.28 (t 1.58); fade OOS PF 1.51, OS long OOS PF 1.06; 10/11 years. The author pre-declared five
falsification cells and had run none.

## Rebuild (`analysis/t_oneside_test.py`, 2018-2026, per NQ, our costs $7.25 + 1 tick per fill)
Parity at the note's costs, 2018 → 2026-08-13: 865 trades (101 a year vs the note's 99), no stop $138 PF 1.45, stop $147
PF 1.50 (note $116 / $125 over 2016-26, which includes its losing 2017). Volume: our exports carry total volume (`Ticks`);
the file sums `Volume`, which is up-tick volume on intraday MultiCharts bars, so its heavy-night flag can differ a little
from ours; the MultiCharts report is the reference.

| per NQ | trades | avg | PF | t | years + | 2018-22 | 2023-26 |
|---|---|---|---|---|---|---|---|
| book, no stop (the file) | 874 | $141 | 1.46 | 3.9 | 9/9 | $122 | $169 |
| **book, note's stop** | 874 | $150 | 1.51 | **4.3** | 9/9 | $135 | $172 |
| T fade (stop) | 363 | $239 | 1.65 | 3.6 | 9/9 | $197 | $314 |
| T longs / shorts (stop) | 214 / 149 | $225 / $258 | 1.57 / 1.78 | 2.5 / 2.6 | 8/9, 7/9 | | |
| OS long (stop) | 511 | $88 | 1.35 | 2.4 | 8/9 (2025 −$3.2k) | $85 | $92 |
| book after their split 2023-09-08 (stop) | 294 | $148 | 1.34 | 1.9 | | | |

Daily metrics (stop): book Sharpe 1.42, Sortino 2.47, PF 1.51, Calmar 1.19, Ulcer 2.8, max DD $12.3k per NQ; T 1.18 / 2.04 /
1.65 / 0.95 / 2.3; OS 0.80 / 1.40 / 1.35 / 0.55 / 3.6; longs 1.15 / 1.98 / 1.44; shorts 0.86 / 1.56 / 1.78.
2023+ bootstrap: book Sharpe 5-95% 0.53-2.09, P(Sharpe <= 0) 0%; T 0.33-1.84, 1%. Drawdown permutation rank 47-51% (typical).
Monte Carlo 1 MNQ: book one-year p50 $1,462, P(loss) 6.9%, DD p95 $1,230, P(hit $2,000 EOD trail) 0.2%.
Multiple testing (291 items, bar t 3.58): book t 4.28, DSR 0.93; T t 3.58, DSR 0.75; OS t 2.39, DSR 0.29. The rule was
frozen and the stop chosen on 2016-20 by its author (pre-registered in spirit, not by us).

## The author's falsification cells (no stop) - all run, all on his side except the OS symmetry
1. **Fade on quiet nights: −$15 (t −0.7, 1,870 trades)** vs heavy nights $214: the volume switch is real for the fade.
2. OS long on heavy nights: $40 (t 0.3, 102) vs quiet nights $90: weaker, as predicted.
3. **Dose-response**, fade by volume-ratio tercile: −$59 / $31 / $95; quintiles −$51 / −$10 / −$3 / $12 / $162: monotonic.
4. Symmetry, quiet night one-sided DOWN morning below VWAP → short: $6 (t 0.1): fails. **The OS long is mostly the Nasdaq
   up-drift in a trending morning**, as the author feared; it is still positive both periods ($81 / $101).
5. Fade entered at the bell (08:30:00) instead of 08:29:00: $190 vs $214: the pre-open minute is worth ~$24, not the edge.
- Random side on the fade days: $214 vs −$18, beaten by 0.1% of 1,000 runs.

## Apex benches (`analysis/t_oneside_bench.py`, stop version, MNQ)
- Evaluation (combine set 50.1%): + book 1-4 MNQ 49.9 / 50.5 / 50.9 / 50.2%; + T only 1-4 MNQ 50.6 / 50.6 / 50.3 / 50.2%;
  in place of EOS 49.3-49.5%; in place of ONB ADX30 41-43%. Median days to pass 6 throughout. No material gain (+0.8 pt
  at best, within noise).
- Funded: pending (bootstrap running, 2026-10-24).

## Code notes
1. No stop in the file (headline numbers need one): v2 adds it (`SetStopContract` + `SetStopLoss`, entry bar covered).
2. `Volume` = up-tick volume intraday (`MULTICHARTS_PITFALLS.md`): fine as long as the live chart uses the same field the
   backtest did; do not switch to `Ticks` without re-running the 1.4 x threshold.
3. The fade fills at 08:29:00, a minute before the bell: thinner book, live slippage may exceed 1 tick (cell 5 shows the edge
   survives entering at the bell).
4. Holidays: both legs finish by 11:00 CT, before the 12:00 CT early close: no halt problem.
5. `shares` in the orders is fine for futures; `Qty` 1 = 1 NQ; for MNQ use an @MNQ chart (the file prints a warning only).

## Verdict
Pending the funded bench (rank after it). Rebuild: book t 4.3, 9/9 years, the volume switch confirmed by the author's own cells.
