# Task 09 (ES MOC Follow) blind check: Claude's verdict (2026-10-17)

**PASS on the rule, with one time-stamp slip on Antigravity's side; the slip turned into a free robustness test.**

Antigravity (`antigravity/jesse` 9073646, `tasks/out_09/`): 198 trades, +3.21 pts ($161) a trade gross per ES, PF 2.19,
63% winners, 7 of 9 years positive.
Against MultiCharts it matched only 171 of 199 days, with entry prices rarely equal (`analysis/jesse/compare_antigravity.py`).

**Cause, proven** (`analysis/jesse/task09_shift_check.py`):
- Every Antigravity entry is the price one minute early (e.g. 2020-03-13: it entered at 2614.75, the close of the minute
  stamped 14:49; MultiCharts at 2617.00, the 14:50 price).
- It read the close-stamped `ES_1min_*.csv` as if stamped at the bar open, so its whole clock (the 14:00 reference, the
  14:50 decision, the 15:00 exit) runs one minute early.
- Our rebuild with the clock as is matches MultiCharts on all 199 days (same side, entry within a tick on 100%).
- The same rebuild with the clock shifted one minute matches Antigravity on 198 of 198 days (entry within a tick 99%).
- So the rule text was understood correctly. Only the data reading differed.

**What the slip tells us (useful):** the rule decided and traded one minute earlier still earns $156-161 per ES gross
(vs $183-190), PF 2.19, 7 of 9 years. The edge is not tied to one exact minute, which is what a real closing-auction
flow should look like. No change to the plan: ES MOC Follow stays at 2 MES.

**For Antigravity next time** (added to the brief): the repo's 1-minute CSVs are stamped at the bar CLOSE; check a known
price (e.g. ES 2020-03-13: the minute stamped 14:50 closed at 2617.00) before running.
