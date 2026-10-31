# FC 2B (Flow-Confirmed Opening Drive): Claude's first review, 2026-10-23

Source: the user's PowerLanguage code (`FC_2B.txt`) and overview (`FC_2B_Strategy_Overview.pdf`, MultiCharts backtest
2017-02 → 2026-10-16, 856 trades, PF 1.51, $22,126 per MNQ). Rebuild: `analysis/fc_2b_test.py`, output
`analysis/outputs/fc_2b_test_output.txt`, trades `python_trades.csv`.

## Rebuild vs the author's MultiCharts run
764 trades 2018-26 (MC ≈ 773 after removing its 83 trades of 2017); every year has the same sign and similar size (per NQ:
2021 $32.0k vs $34.4k, 2022 $56.1k vs $52.4k, 2024 $28.3k vs $27.5k; 2025 $26.5k vs $38.4k is the largest gap). Our
costs are stricter ($7.25 + 1 tick per market / stop fill). Trade-by-trade parity needs the MC report (.xlsx).

## Results (per NQ after our costs; 1 MNQ = 1/10)
| | Trades | Win | $/trade | PF | t | 2018-22 | 2023+ | Years + |
|---|---|---|---|---|---|---|---|---|
| All | 764 | 61% | $261 | 1.48 | 3.8 | $288 (t 3.6) | $224 (t 1.9) | 9/9 |
| Longs | 377 | 62% | $291 | 1.54 | 3.1 | $254 | $343 (t 2.0) | 8/9 |
| Shorts | 387 | 59% | $233 | 1.42 | 2.3 | $323 | $113 (t 0.7) | 6/9 |

Sharpe 1.26, Sortino 2.41, Calmar 1.32, Ulcer 3.3, max DD $16.7k per NQ; 2023+ bootstrap Sharpe 0.17-1.65 (P ≤ 0: 3%);
shorts 2023+ weak (Sharpe 0.34, P ≤ 0 25%). Monte Carlo at 1 MNQ: 1-year P&L p50 $2,211, P(loss) 8.5%, DD p95 $1,955,
return/DD 2.25, P(hit $2,000 trail, EOD) 4%; at 2 MNQ 29% (too big alone for a 50K account).

## Controls
- Random days + random side: $15 a trade (best of 20: $161); same days, random side: $13 (max $140); opposite side −$216
  (t −3.3, 1/9 years). The direction call carries the edge.
- Flow filter: every drive day (no filter) $119 (t 3.0); the filter doubles the per-trade edge.
- Smooth in z: 0.5 / 0.75 / 1.0 / 1.25 / 1.5 → $208 / $243 / $261 / $332 / $244 (t 4.2 / 4.2 / 3.8 / 4.0 / 2.4).
- Exits (**corrected 2026-10-23** after the checker: my first run treated BreakEvenR 0 as 'break-even at once', not
  'off'): stop 100 only $247 (t 3.2), break-even only $234, trail only $272, as coded $261; BE 0.5 / 0.8, trail 100 / 200,
  stop 75 / 150 all $215-270. **The edge is in the entry, not the exits**; the exits change the shape, not the sign.
- Tail: the top 9% of trades make $304k, the rest −$104k per NQ (the author's 'the strategy is its tail').

## Concerns
1. **Selection:** ~40 builds by the author; the current exits were set on the full 2017-2026 sample (2026-07-19), so
   2023+ is not out of sample. t 3.8 clears the 3.57 bar only narrowly; the original 2B rule's Feb 2024 → Jun 2026
   holdout (PF 1.42) is the cleanest evidence. Forward log from now.
2. **Overlap:** corr +0.36 with Relative Strength (509 shared days; both enter at 09:01 in the direction of the
   08:30-09:00 move), +0.16-0.19 with VB / ONB ML, +0.37 with the plan total. Test as an addition AND as a
   replacement for RS (CLAUDE.md add-or-replace rule) on the bootstrapped funded bench.
3. **Code, before live use:**
   - The entry bar has no working stop (stops are issued only once MarketPosition = 1, from the 09:01 bar's close).
     Add a backstop `SetStopContract; SetStopLoss(SLpoints * BigPointValue);` or issue the stop with the entry.
   - Early closes (12:00 CT): ExitTime 14:58 is never reached and `SetExitOnClose` fires after the last bar, when the
     market is closed: a position could be carried into the next session (Apex violation). Add the `IsEarlyClose`
     list + `EarlyFlatten 1130` as in Vault Break.
   - The z-score needs ≥ 20 (ideally 60) days of 1-minute history loaded on the chart; it restarts with the chart.

## Next steps
1. User: export the MultiCharts report (.xlsx) for trade-by-trade parity.
2. Independent checker (`strategy-checker`, this folder).
3. Funded bench (bootstrap): + FC 2B 1 MNQ; replacing RS longs; challenge set + FC 2B.
4. If it holds: forward log entry with its decision rule written first.

## Update 2026-10-23: MultiCharts report (user's export) vs the rebuild (`analysis/fc_2b_mc_confirm.py`)
- MC 826 trades (2017-05-30 → 2026-10-16), Python 818; 773 on the same day: **side 100%, entry price 100%**, exit
  price 97.4%, gross within $20 97.7%, gross correlation 0.998. 53 MC-only / 45 Python-only days, mostly near the
  z threshold (median |z| ≈ 1.0). **Correction (after Codex's review):** not missing holidays (they are in our data)
  but the volume definition: MultiCharts' intraday `Volume` is up-tick volume, `Ticks` the total, and our exporter
  writes `Ticks`. The live strategy uses `Volume`, so the MC report, not the Python rebuild, is the reference for this
  rule; the rebuild is a close approximation (same side and entry on all 773 shared days).
- **MC trades under our costs, 2018-26:** 773 trades, $272 per NQ, PF 1.49, **t 3.94**, 9/9 years; 2018-22 $290
  (t 3.6), 2023+ $247 (t 2.1); longs $297 (t 3.2), shorts $248 (t 2.5; 2023+ t 0.9); Sharpe 1.30, Sortino 2.52,
  Calmar 1.52, Ulcer 2.8, max DD $15.2k; DSR at N = 282: 0.87. Clears the t bar (3.57), not the DSR bar.
- **26 holiday trades were held through the 12:00 CT halt and exited at the 17:00 reopen** (e.g. 2025-06-19 short
  stopped at 17:01 for −$2,000 per NQ; 2022-02-21 +$4,475). Small in total (+$3.4k gross) but each one is an Apex
  breach live. Fixed in **`FC_2B_v2.txt`**: holiday half-day list + flat at 11:30, entry-bar backstop
  `SetStopLoss(SLpoints x BigPointValue)`, `SetExitOnClose` removed. Rule otherwise unchanged; rerun v2 in MC.

## Codex's review (2026-10-23) and what changed
1. Exits have no clean holdout (selected on the full sample; the 211-trade holdout belongs to the range-stop version):
   agreed; forward log needed.
2. Entry minute unprotected: agreed; v2 adds `SetStopLoss`. Check in the v2 report and live that the stop appears
   right after the fill (Order and Position Tracker).
3. `Volume` (up-ticks) vs our CSV (`Ticks`, total): agreed, it explains the ~50 near-threshold mismatched days (above).
   Don't change the code's `Volume`: the MC report is the reference. A Python replay would need an up-volume export.
4. A raised break-even / trail stop can already be through the market when sent: v2 exits at market next bar in that
   case. (The Python replay already applies stop updates only after the bar closes and fills at the next open.)
5. Account risk (open-loss drawdown vs closed-trade MC; MNQ costs are not 1/10 of NQ's): agreed; decided only on the
   funded bootstrap bench with intraday paths and MNQ commissions.
Also: 'flow' is a candle-and-volume proxy, not measured aggressor volume; the code accepts an incomplete opening range
(if the 09:00 bar is missing the signal comes one bar later). Neither changes the verdict.

## Update 2026-10-23: v2 MultiCharts report (user's export)
- Same 826 signal days as v1; 31 trades changed, all for the intended reasons: **0 exits after 15:00** (the 26 holiday
  trades now exit at 11:31; the 12:15 CT close days now 11:31 too); **3 entry-bar backstop stops** ("Stop Loss" at 09:01:
  2020-03-03 −$2,000 instead of −$3,835 per NQ, 2024-09-04 −$2,000 instead of −$2,390), which confirms the v1 entry
  minute was unprotected. The stop-through-market fallback didn't fire in the backtest.
- v2 under our costs, 2018-26: 773 trades, $275 per NQ, PF 1.51, **t 4.0**, 9/9 years; 2018-22 $292 (t 3.7), 2023+ $252
  (t 2.1); longs $305 (t 3.3, 9/9 years), shorts $246 (t 2.5; 2023+ t 0.9); Sharpe 1.32, Sortino 2.58, Calmar 1.53,
  Ulcer 2.7, max DD $15.3k per NQ. v2 is the version to test further.

## Independent checker (2026-10-23): PASS WITH CONCERNS (`verdict.md`, `checker_report.md`)
- Replica from `FC_2B_v2.txt` alone: identical side / entry / exit / net on all 725 shared days vs the MC v2 report;
  mismatched days are near-threshold (volume definition) plus 3 after our data and 5 holidays. Reproduces my v1 trades
  764 / 764. No look-ahead, no holiday carry in v2.
- Gates 7/8 (MC list): G1 fails on DSR (0.89 < 0.95) but t 4.02 clears the 3.57 bar (3.61 even with the author's ~40
  builds added to N); holdout, years, concentration (MC list), placebo (random side $31, random drive days $119 vs
  $261-275, p < 0.003), resampling, MinTRL, regime pass; PBO 0.45 over 16 neighbouring variants.
- Concerns: (1) my exit ablation was wrong (fixed above); (2) the z filter's lift over 'trade every drive' is t 2.66 in
  2018-22 but only t 1.06 in 2023+ (2023 lost); (3) all the profit sits in the top 5% of trades, 31 of 39 from 2022+,
  and full stop-outs rose from 3-8% (2018-19) to 20-37% (2022-26) as NQ quadrupled under fixed-point exits (price-scaled
  exits keep t 3.0-3.8: drift, not a break); (4) MNQ only on Apex: one NQ stop = −$2,017; P(hit the EOD trail in a year,
  2023+) 10% at 1 MNQ, 43% at 2 MNQ (checker's MNQ cost assumption $3 round trip).
