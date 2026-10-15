# Personal-account strategies

Strategies tested here that are NOT for Apex (they lower the funded plan or break Apex rules) but can run on a personal
account. Each file says why it is here and what the Python test found.

| Strategy | File | Chart | Notes |
|---|---|---|---|
| Gold Breakout 15M (user's TradingView idea) | `Gold_Breakout_15M.txt` | 15 min MGC / GC, Exchange time (CT), 24-hour session | $138 per GC, PF 1.23, t 3.1, 7/9 years (2018–26); max DD ~$4.3k per MGC; risk-based sizing (1% of equity, 1% stop), out 12:00 CT. Tier C: worse on the Apex funded bench (`analysis/gold_breakout_15m_bench.py`). |

## Twin_Continuation.txt (v2, 2026-10-15)

The user's Twin Continuation (Swing Breakout + Morning Momentum, NQ 1-minute) with a holiday fix: on CME early-close
days (12:00 CT halt) the original could not reach its 15:45 / 14:50 exits and held through the halt into the 17:00
reopen (4 such trades 2018-26, -$5.6k; SetExitOnClose only works in backtests). v2: no entries from 11:00 CT, flat at
11:30 CT, Morning Momentum skipped on those days (inputs UseHolidayTimes / EarlyLastEntry / EarlyFlatten; same holiday
list as NQ_Vault_Break.txt; Good Friday half days, when they happen, are not in the list). Edge and caveats:
`TIER_LIST.md` (B, pending a MultiCharts run) and `checks/candidates/twin_continuation/verdict.md`. For prop accounts set
BO_MaxStopMult 1 (the swing stop risks ~$6,000 per NQ); it does not improve the Apex plans either way.
