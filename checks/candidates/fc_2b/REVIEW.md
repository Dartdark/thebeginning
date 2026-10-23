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
- Exits: the break-even step is what matters. No BE and no trail $29 (2023+ −$82); BE only $234; trail only $43
  (2023+ −$46); BE at 0.5 / 0.66 / 0.8 R all $235-267; trail 100 / 150 / 200 $215-261; stop 75 / 100 / 150 $218-270.
  Not knife-edge, but the edge depends on scratching drives that reverse after +66 points.
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
