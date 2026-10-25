# Swing Target NQ: TEST for source replication

Summary: User supplied a prior-two-RTH-session breakout, with published backtest claims but no verifying trade export.
The uploaded code omits the description's breakeven exit; the user explicitly requested both versions separately.
Use a disclosed full-session proxy (user selected unknown template); inspect execution and holiday risks before account placement.
This is an empirical breakout replication, not established forced-flow evidence or a trading recommendation.

Sources: `agents/codex/inputs/swing_target/Swing_Target_NQ.txt` (user's 2026-10-25 upload);
Howard SSRN 6350238, primary abstract only (https://ssrn.com/abstract=6350238); repository minute-close Grid24 and current plan snapshots.
Prior trials: unknown author search, including timing and rejected filters; header says both eras were examined.
New planned economic models: two fixed versions, code and code plus described breakeven. No tuning/filter search.

1. Participant/mechanism: stops and trapped breakout traders are a plausible hypothesis, not observed participant flows.
   No mandate or forced net NQ demand is established. A near target and wide stop change payoff, not expected value by themselves.
2. Known before entry: prior stored RTH highs/lows and 20-session average range, first-15-minute invalidation;
   no use of today's final range. Check exact boundaries and missing session bars before accepting source state.
3. Instrument/transmission: cached NQ minute OHLC proxy for NQ/MNQ. Native MNQ price differences and limit queue are unobserved.
   No claim that ES paper findings transfer mechanically to NQ or that 0DTE causes this effect.
4. Data: existing `scratch_data/g24.pkl`, through 2026-10-09. Author's February2018–July2026 slice is descriptive;
   actual 584-trade match cannot be checked without the author's trade export. Reuse caches and configured Python.
5. Executable costs/risk: $7.25/NQ plus one tick market/stop fill; native MNQ RT $1.24, $1.04 sensitivity.
   Wide stops can consume account drawdown; one trade/day and high win rate do not prove smooth account equity.
6. Power/alternatives: roughly 600 claimed trades, much fewer per side/year. 2023+ is historical replication, not fresh holdout.
   Include block bootstrap, matched-exit placebos, source versus BE, and adverse intrabar-path stress; count every economic model.
7. Falsifiers/portfolio: fails if net costs remove the edge, replication fails, exits depend on favorable path, or no account benefit
   versus addition, VB replacement and empty slot. Expected common failure is choppy failed-breakout days with VB/Twin/other NQ risk;
   correlation is not a hedge. Assess whether any offset arrives before an account breach, and early-close/overnight exposure explicitly.
