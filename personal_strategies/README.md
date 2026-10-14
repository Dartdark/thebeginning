# Personal-account strategies

Strategies tested here that are NOT for Apex (they lower the funded plan or break Apex rules) but can run on a personal
account. Each file says why it is here and what the Python test found.

| Strategy | File | Chart | Notes |
|---|---|---|---|
| Gold Breakout 15M (user's TradingView idea) | `Gold_Breakout_15M.txt` | 15 min MGC / GC, Exchange time (CT), 24-hour session | $138 per GC, PF 1.23, t 3.1, 7/9 years (2018–26); max DD ~$4.3k per MGC; risk-based sizing (1% of equity, 1% stop), out 12:00 CT. Tier C: worse on the Apex funded bench (`analysis/gold_breakout_15m_bench.py`). |
