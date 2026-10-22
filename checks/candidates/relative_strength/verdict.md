PASS WITH CONCERNS (checker gates on the replica: 6/8, mechanical FAIL on G1 DSR and G4 concentration; replication and leak checks clean)

**Replication** (`replica.py`, built from RelStrength_v3.txt alone; NQ-bar loop as in MultiCharts, ES close carried forward): 1,164 trades
vs maker 1,161. All 1,161 maker trades matched on date, side, exit kind, entry price and net (largest net difference < $1; Z corr 0.999999).
The 3 extra replica trades are 2020-03-09 (-$2,615), 2020-03-18 (-$4,431), 2020-03-24 (-$3,927): limit-locked opens with no 08:30 bar
in ES (and NQ). MultiCharts anchors on Close[1] (the last bar before 08:31) and would trade them; the maker's "skip ES-gap minutes"
convention drops them (`--skip_es_gaps` reproduces the maker exactly). Effect: maker $355,449 / $306 a trade vs replica $344,477 / $296.
Small (3%) and in the maker's favour; trades.csv is not quite what the code does.

**Gates** (python3 analysis/checker.py; maker folder had no placebo -> 5/8; replica folder `../relative_strength_replica/` 6/8):
- G1 significance FAIL: t 3.85 (maker 3.98), DSR(N=266) 0.844 (maker 0.875) < 0.95. Note t > t_threshold(266) = 3.56, which meets the
  CLAUDE.md promotion alternative ("t >= t_threshold or DSR >= 0.95"); the checker uses DSR only.
- G2 holdout PASS: 2018-22 $252 (t 2.81), 2023-26 $344 (t 2.69).  G3 years PASS: 9/9 positive (2019 $7.3k and 2023 $12.1k weakest).
- G4 concentration FAIL: without the best 5% of trades -$43,276 (maker -$32,304). Top 5% = 111% of profit, top 1% = 27%, top 10 trades $84k.
- G5 placebo PASS (my placebo: same signal days, random side, 100 runs, `placebo_checker.csv`): placebo mean $2 (sd $73), 0/100 >= $296.
- G6 resampling PASS: 2023+ P(Sharpe<=0) 0.002.  G7 MinTRL PASS: 1,164 vs 204.  G8 regime PASS: rho 0.85.
- Metrics (replica, 1 NQ): Sharpe 1.27, Sortino 2.14, PF 1.34, Calmar 1.33, Ulcer 4.77, max DD $28.5k. Longs: Sharpe 1.13, PF 1.44.
  Shorts: Sharpe 0.68, PF 1.25, Calmar 0.39, 2023+ P(Sharpe<=0) 0.16 (shorts are the weak half).

**Leak / trap checks**
- Timing: signal uses closes up to the 09:00 bar; entry = open of the 09:01-stamped bar; stop/target from 09:02; avg range from prior
  clean RTH days only; beta/variance EWMA uses only bars up to the decision. No look-ahead found. Entry bar through the stop: 1 trade.
- Costs: verified in net ($7.25 RT + $5 per market/stop fill; target no slippage). Target needing 1 tick penetration: $293/trade
  (-1%). Tick-rounded stop/target: $295.6. Not fragile to fills.
- Roll/holiday: all inside 09:01-15:00 on one contract; NYSE holiday/half-day table applied; no artefact found beyond the 3 March-2020 days.
- Volatility scaling is not the source: mean +0.10R per trade (R = stop distance), t 3.97, positive every year (2023 weakest at 0.04R).
- Robustness of neighbours: ZMin 1.0 $251, 1.5 $319, 2.0 $344 a trade; decide 08:45 $232, 09:15 $205. Smooth, no knife-edge.
- "Z" is not a Z: sd 2.18, |Z| >= 1.25 on 53% of days (21% expected). Harmless for the backtest, but the threshold is not a 1.25-sigma event.
- Size trap: median stop $2,621 per NQ (2023+ $2,966) > the $2,000 Apex drawdown. Only MNQ is tradable: about $30 a trade, max EOD DD
  $2,854 at 1 MNQ, and 22% of one-year windows hit a $2,000 trailing DD at 1 MNQ (rough, monthly starts).

**What would most change my mind**
1. G4: if the edge needs the top 5% of trades, a short live sample will look flat or negative; a 2023+ check without the top 5% by year,
   or a version with a trailing exit that keeps the tail, would settle whether the tail is structural or luck (10 trades = $84k).
2. The 12-variant search on 2017-22: a walk-forward of ZMin / decide time (it should stay positive given the smooth neighbours) and
   adding the variants to TRIALS.csv; DSR failing at N=266 is the main formal objection.
3. Apex fit: Monte Carlo at 1 MNQ with the real EOD-trailing rule; at a 22% yearly breach rate it may be a funded-only / personal-account item.
