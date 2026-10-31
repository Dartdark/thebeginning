PASS WITH CONCERNS (checker gates 6/8. G1 deflated Sharpe and G4 concentration fail. Replication is exact and I found no leak.)

**Replication.** I rebuilt the rule from spec.md alone (`replica.py`, g24.pkl, rolls from `rolls_index`). It gives 2,150 trades. All 2,150 match trades.csv on date and trade number, with 100% agreement on side, entry, stop, exit price, exit kind, entry and exit column. P&L correlation is 1.000 and total net is $356,572.5 in both. Our port against the author's code: the session mapping (ET open stamp m = CT close column m-59; RTH 511-915, premarket 181-510, entry cutoff before 631, force-close 911) and the level logic are equivalent. The author lists the levels as structural_pdh, structural_pdl, pdh_break, pdl_break, then pmh, pml. The spec lists them as pdh, pdl, pmh, pml. These can differ only between a long level and a short level, and in a non-gap day no single close can break both, so the order never matters. Our 2018-25 count is 1,944 against the author's 2,041 (we drop roll days and use different data). Our +447R is close to the author's +438R, and our PF of 1.29 is close to their 1.31/1.34. Without the roll filter there are 2,190 trades at the same $165.8 mean, so the roll drop changes nothing.

**Gates** (`checker_report.md`, N=291, variants 27, not pre-registered)
- G1 significance FAIL: t 3.82, DSR 0.854 (below 0.95). The t is above t_threshold(291) = 3.58, which CLAUDE.md accepts as the other route above C.
- G2 holdout PASS: 2018-22 $126.5 a trade (t 2.86), 2023-26 $216.3 (t 2.66).
- G3 years PASS: 9/9 years positive. The weakest are 2019 ($63 a trade) and 2023 ($81).
- G4 concentration FAIL: the best 5% (108 trades) make $688k. Without them the total is -$336k. Capping winners at 3R gives -$49.6 a trade, at 5R +$81, at 10R +$152.5.
- G5 placebo PASS: 500 runs of a random side on the same entry bars with a mirrored stop average $59.2. None reaches $165.8 (p 0.000). Reversing every trade gives -$45.7 a trade.
- G6 PASS: P(Sharpe ≤ 0) on 2023+ is 0.000. G7 PASS: 2,150 trades against a MinTRL of 313. G8 PASS: rho 0.85.
- Metrics: Sharpe 1.28, Sortino 2.83, PF 1.29, Calmar 1.40, Ulcer 3.46. Longs: 1,335 trades, $75 a trade, Sharpe 0.53, PF 1.13, 2023+ P(Sharpe ≤ 0) 0.18. Shorts: 815 trades, $314 a trade, Sharpe 1.23, PF 1.55. The pm_low level alone (572 trades, $374 a trade) gives $214k of the $357k.

**Leak and trap checks** (`extra_checks.py`)
- Every input is known before the signal bar closes: prior-day RTH stats, premarket that ends at 08:30, ATR excluding today. Entry is at the next bar's open, so the entry and the stop are always on the right side. The stop is checked from the entry bar on, and before the EOD exit on the same bar (the conservative order).
- Stop fills: none of the 1,480 stop fills is a gap-through, so fill-at-stop costs nothing extra. Only 1.4% of stops hit on the entry bar.
- Costs are in: $17.25 a trade. With 2 / 3 / 4 ticks a fill the mean is $155.8 / $145.8 / $135.8 (t 3.59 / 3.36 / 3.13).
- Parameter plateau, with 0.18 as the local peak (stop share of ATR: t / mean): 0.10 3.01 / $100, 0.15 3.12 / $122, 0.18 3.82 / $166, 0.25 3.38 / $166, 0.30 2.59 / $136. Entry window ending 10:10 to 11:30 CT: t 3.4 to 3.56.
- Structural baselines on the same days and stop:
  - A random time and random side earns +$40.4 a trade; the tight stop held to the close is skewed in its favour on its own.
  - A random time in the window with side = sign(close minus RTH open) earns $111.5 (p95 $160.3). FVB's first trade of the day earns $164.6, so the levels add about $50 a trade over plain momentum from the open.
  - On the same signal bar, side = sign(close minus open) agrees with FVB 90% of the time and earns $160.9.
- Size: at 1 NQ the median stop is $1,375 in 2026 and the max drawdown is $28k. That does not fit a $2,000 trailing account, so it needs MNQ, where costs take a larger share of each trade.

**What would change my mind**
1. The fat tail. Everything rests on about 100 runner days in 8.8 years. A drought of 2019 or 2023 type (about $70 a trade) on MNQ with full costs could fail an Apex account. This needs a funded_bootstrap / Monte Carlo run at MNQ size.
2. Momentum from the open explains most of the result ($111 of $165). If the extra value of the levels over that baseline does not hold up (my $165 sits only just above the baseline's p95), this is a re-labelled intraday-momentum rule. The tier should then be set against existing momentum strategies, and the correlation with them checked.
3. The longs are weak (PF 1.13, 2023+ P(Sharpe ≤ 0) 0.18), and the author tuned the 0.18 stop with OOS information. A shorts-only or pm_low-only version would have to be pre-registered before anyone believes it.
