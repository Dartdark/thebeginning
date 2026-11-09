# S30 IBS, NQ, entry IBS < 0.10 (WATCHLIST #34; 2026-11-09)
Rule: on each full 08:30-15:00 CT cash session, IBS = (close - session low) / (session high - session low) at the 15:00 bar.
Flat and IBS < 0.10 -> buy 1 NQ next bar at market (the 15:00-15:15 bar's open); long and IBS > 0.80 -> sell next bar at market.
No stop, no target, no time exit: positions are held through nights, weekends and holidays (personal account only; not Apex-legal).
Instrument: NQ, MultiCharts 15-minute chart (checks/candidates/s30_ibs/S30_IBS.txt, IbsEntry 0.10), 2018-01 -> 2026-11-08.
Costs: $7.25 commission + 1 tick per market fill (entry and exit) = $17.25 a round trip per NQ.
Trades: the MultiCharts List of Trades (mc_reports/... S30 IBS 010.xlsx), 171 MC trades from 2018; 169 matched to the Python rebuild, all identical (the 2 others: 2020-03-12 / 03-16, sessions the rebuild skips as incomplete) (analysis/mc_confirm_3.py).
Raw (unadjusted) continuous prices: a roll inside a hold books the roll gap (the Python match uses the same prices).
Mechanism: short-term mean reversion in equity indices after a session closing near its low (Pagonidis 2014, IBS effect).
Selection: post hoc. Source rule IBS < 0.20; 0.10 found in an ingredient ablation (analysis/ingredient_ablation6.py); thresholds
0.05 / 0.075 / 0.10 / 0.125 / 0.15 / 0.20 compared (analysis/s30_threshold_sensitivity.py) -> 6 variants. Not pre-registered.
Known risk: trade-exit bookings understate the drawdown; marked daily, max DD is $45.3k per NQ (analysis/s30_marked_check.py).
Placebo: random entry days (same count per year), same IBS > 0.80 exit rule, 200 runs: is the IBS < 0.10 entry better than
being long NQ for a comparable hold?
