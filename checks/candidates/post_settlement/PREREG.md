# Post-settlement reversal, cheaper execution: pre-registration (2026-10-25, before any run)

Idea (user + Claude): NQ's 15:00 -> 15:15 CT window reverses the last hour (round 3: following it t -4.0, 1/9 years) but
only ~$29 gross a trade. Who is forced: desks marking to the 15:00 settlement and MOC flows push the last hour; after
the settlement the push is gone and part of it comes back. Goal: an S-rank candidate with >= 300 trades a year.

Data: NQ 1-minute grid (scratch_data/g24.pkl, CT, close-stamped), 2018-2026; ES and YM as checks. Per 1 NQ.
M = close(15:00) - close(14:00) (last hour); side = -sign(M) (fade). ATR = daily ATR(15) (grid24.daily_atr).
Exit: market at the 15:15 close. Costs: $7.25 + 1 tick per market fill (entry and exit); limit entries pay no tick.

Variants (fixed list, nothing else will be tried before the verdict):
  V0 market entry at the 15:01 open, every day with M != 0.
  V1 limit entry at the 15:00 close price, working 15:01-15:05, filled only when traded 1 tick through.
  V2 V0 on days with |M| >= 0.3 ATR (also reported: 0.2 ATR).
  V3 V1 on days with |M| >= 0.3 ATR (also reported: 0.2 ATR).
  Also: each at Apex real micro fees ($1.04 + 1 tick per MNQ = $10.40 + $5 per NQ-equivalent fill).
Controls: random side on the same days and fills; following instead of fading.
Design 2018-2022, holdout 2023-2026.
Pass (S-rank track): t >= 3.58 over 2018-2026 (t_threshold of the program's N_items), holdout same sign with t >= 1.5,
at our costs, and >= 300 trades a year (V2 / V3 may fall short of 300: then they are reported but cannot meet the goal).
Script: analysis/post_settlement_test.py
