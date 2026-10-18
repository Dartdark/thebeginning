# Candidate: NR7 day sizing filter on Vault Break (NQ)

**Kind:** filter / sizing on an existing strategy (Vault Break, long-only NQ breakout, 30-minute bars, Exchange time CT).

**Rule:** trade MORE contracts on a session that follows an NR7 day.
- Regular session = 8:30-15:00 CT (the 30-minute bars closing 9:00 .. 15:00; on CME early-close days, the bars up to the
  early close). Session range = highest high - lowest low of those bars.
- Sessions = weekdays that have regular-session bars (half days count, with their shortened range).
- NR7 day = a session whose range is <= the minimum range of the previous 6 sessions (narrowest of the last 7, ties count).
- The NEXT session is flagged (known before it opens: it uses only completed sessions).

**Mechanism / source:** Toby Crabel's narrow-range day (volatility contraction is followed by expansion), as described in
Kaufman, *Trading Systems and Methods* (5th ed.), ch. 16. Vault Break is a volatility-band breakout, so it should earn more
after contraction. Pre-registered: 4 trials (inside-day and NR7 day, on Vault Break and on Overnight Bias ADX30); this is
the one that worked. The sizing choice (1 contract normally, 3 after NR7) was picked afterwards on a funded-account bench.

**Data:** trades.csv = every Vault Break trade from the user's MultiCharts backtest (1 NQ, 2018-01 .. 2026-10) with the NR7
input on (`flagged` = 1 if MultiCharts traded 2 contracts, i.e. the session followed an NR7 day). net = per-contract
MultiCharts profit - $14.50 commission - 2 ticks ($10) per round trip (conservative flat cost).

**Claim to check:** flagged trades earn clearly more per contract than the others (about $217 vs $60), in both 2018-22 and
2023-26, and it is not explained by chance days, a few trades, or a leak.

**Raw data to replicate from:** NQ 1-minute bars (`NQ_1min_20*.csv`, `NQ_1min_ON_*.csv`, grid24.Grid24 / scratch_data/g24.pkl),
Vault Break rules in `apex_strategies/NQ_Vault_Break.txt` (the base strategy, not the candidate's research).
