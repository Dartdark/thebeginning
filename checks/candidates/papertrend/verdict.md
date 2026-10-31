FAIL (narrowly: gate G1 only, deflated Sharpe 0.865 < 0.95 at N=291). The replication matches exactly and I found no leak. The edge is real in-sample but fragile at the edges and not promotable on this evidence.

## Replication (replica.py, from spec.md only, g24.pkl, rolls from rolls_index on Sym("NQ"): 55 roll bars)
- 592 replica trades vs 592 maker trades (2017-05-19 to 2026-10-08). 100% match on dates, side, signal mark, entry, exit and net (P&L corr 1.000, 0 mismatches). 2018+: 558 trades, $207,860, $372.5 a trade.
- The spec is unambiguous as written. With roll days kept: 571 trades, $387 a trade, t 4.3 (dropping the 13 roll days lowers the result, so the roll handling does not inflate it).
- **The Python rule is not proven to be the user's MultiCharts strategy.** Up to 2026-08-14 the rebuild gives 582 trades and $209k in 9.25 years. MC gives 535 trades and $167k in 9.9 years. That is about 15% more trades a year, though PF (1.68 vs 1.66) and win rate (60.3% vs 58.9%) are close. The maker also tried 39 variants (meta.json) to reach this rule.

## Gates (analysis/checker.py, maker trades = replica trades, identical reports)
| Gate | Result | Number |
|---|---|---|
| G1 significance | FAIL | t 4.05, PSR 1.000, DSR(N=291) 0.865 (0.925 at N=100, 0.962 at N=39) |
| G2 holdout | PASS | 2018-22 $364 (t 3.55); 2023-26 $385 (t 2.30); **2023-25 only $248 (t 1.4)** |
| G3 years | PASS | 8/9 positive (2019 -$5.0k; 2025 +$1.0k; 2023 +$7.4k) |
| G4 concentration | PASS | without the best 5%: $107 a trade. But the top 28 trades = $151k of $208k (73%), and the top 10 = $70k |
| G5 placebo (random side, same days, 500 runs) | PASS | placebo mean -$5; share >= $372.5: 0.000 |
| G6 resampling | PASS | 2023+ P(Sharpe <= 0) 0.003 |
| G7 MinTRL | PASS | 558 vs 103 |
| G8 regime | PASS | rho 0.63 |
Repo rule (CLAUDE.md): t 4.05 >= t_threshold(291) 3.58 would pass, but in ATR units the t is 3.6, right at the threshold. Metrics: Sharpe 1.33, Sortino 2.07, PF 1.67, Calmar 0.82, Ulcer 5.35. Longs Sharpe 0.96, PF 1.67; shorts Sharpe 0.92, PF 1.66.

## Leak and trap checks (robustness.py -> robustness_out.txt)
- **Timing:** O, the gap, ATR (14 prior sessions) and the skip filter (yesterday) are all known at 08:31. Every entry falls on the next 1-minute bar (0 late fills). Entering at the mark close gives the same result ($373), and entering 5 minutes late still gives $352 (t 3.9). No look-ahead.
- **Drift artefact:** I took all longs on the same days and same bars and got -$16 (t -0.2). Random side gave -$34. So the result is the direction rule, not NQ's upward drift.
- **Neighbourhood:**
  - Band k: 0.4 gives t 4.2, 0.6 gives 3.3, 0.75 gives 2.4, 0.25 gives 3.0.
  - ATR length: 10 gives t 3.5, 20 gives 3.8.
  - Signal marks every 5 minutes give t 3.6, every minute 3.6.
  - Without the skip filter: t 3.5.
  - Gap filter: the reversed filter gives t 1.4. With no gap filter the trade-level t is 3.4, and in ATR units it is 3.7 vs 3.6 for the base, so the gap filter mainly halves the trade count.
- **Exit-time fragility:** exiting at 15:00 instead of 14:55 gives $299 (t 3.1). Exiting at 13:00 gives $187 (t 2.3). The last 5 minutes are worth $74 a trade, and 14:55 sits at the peak.
- **Holdout carried by 2026:** 2023-25 longs made $49 a trade (t 0.2, 101 trades). 2026 longs made $43.5k, 21% of all P&L. P&L in dollars also grows with the price level (NQ about 5.7k to 31k).
- **Costs:** $17.25 a trade is included. Half days are dropped, and roll days are handled as specified.
- **Apex fit:** at 1 NQ the max DD is $27.8k and 32% of trades since 2023 have an MAE worse than -$2,000. The strategy needs MNQ, and even 1 MNQ has a ~$2.8k max DD, above the $2k trailing limit.

## What would change my mind
1. The user's MultiCharts trade list matching this rebuild (>= 90% of dates). Or the rule being fixed before the 39 variants, which would make it effectively pre-registered at <= 3 variants (G1 would then pass via t >= 2).
2. Out-of-sample months after 2026-10 at PF >= 1.4, or 2023-25 longs turning clearly positive. This matters most for the case for adding it.
3. A 15:00 exit (or a 14:50-15:00 average) still clearing t >= 3.58. Today it gives t 3.1, which says 14:55 was picked at its peak.
