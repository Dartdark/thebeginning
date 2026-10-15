# Candidate: single-print day filter on Vault Break (NQ)

**Kind:** filter on an existing strategy (Vault Break, long-only NQ breakout, 30-minute bars, Exchange time CT).

**Rule:** skip (or size down) Vault Break on a session that follows an "interior single-print" session.
- Previous regular session = the 13 thirty-minute bars closing 9:00 .. 15:00 CT (8:30-15:00 CT = 9:30-16:00 ET).
- Each bar is one TPO period covering its low..high in ticks (0.25).
- Single print = a run of at least 8 consecutive ticks covered by exactly one period, not containing the session high or low tick.
- All 13 bars must exist (half days never flag).
- If such a run exists, the NEXT session is flagged.

**Mechanism / source:** Red Ledger Research field study RL-FS-2026-01 (Sept 2026, NQ 2017-2024): sessions after an interior
single print overlap the prior value area more, are less directional and ~17% narrower than expected; the paper's stated
use is to stand aside / size down breakout strategies on those days. Pre-registered: the prediction (breakouts earn less on
flagged days) and the definition were taken from the paper before looking at Vault Break; one variant tested.

**Data:** trades.csv = every Vault Break trade (MultiCharts backtest, 1 NQ, 2017-2026), `kept` = 1 if the filtered
MultiCharts run (skip flagged sessions) still took the trade. net = MultiCharts profit - $7.25 commission - 2 ticks ($10)
slippage per round trip (conservative flat cost).

**Raw data to replicate from:** NQ 1-minute bars (`NQ_1min_20*.csv`, `NQ_1min_ON_*.csv`, grid24.Grid24 / scratch_data/g24.pkl),
Vault Break rules in `apex_strategies/NQ_Vault_Break.txt` (the strategy itself, not the candidate's research).
