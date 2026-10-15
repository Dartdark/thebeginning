# Live / sim trade reports

Put one MultiCharts Strategy Performance Report per strategy here, exported weekly from the **live (auto-trading)**
chart, named `<KEY>_live.xlsx`:

| KEY | Strategy |
|---|---|
| `VB` | Vault Break |
| `ONB_ML2_MC` | Overnight Bias ML (funded) |
| `MON_MC` | Monday Long |
| `EOS` | Expiration Open Short |
| `LDF_MC` | Late-Day Flow |
| `NFP_MC` | NFP Fade |
| `MON_BR` | Bridge Monday Long |

How to export (MultiCharts): on the live chart, View → Strategy Performance Report → File → Save As → Excel (.xlsx).
The report must contain the "List of Trades" sheet (the default).

Then re-run each strategy's **backtest** on the same chart so it covers the live dates, and save it under its usual
name in the repo root (the names in `analysis/live_vs_backtest.py`, `KEYS`).

Run:

    python3 analysis/live_vs_backtest.py --all live/

It prints, per strategy: matched / missed / extra trades, entry and exit slippage in ticks, and the **edge ratio**
(live points per contract ÷ backtest points per contract over the same days).

Decision rule (from `funded_strategies/FUNDED_PLAN.md`, account pipeline):
- After about 40 trades, an edge ratio of 0.75 or more means it's OK to go from 3 account slots to 5–10.
- 0.5–0.75: hold the current number of slots.
- Below 0.5: stop scaling and investigate.

## Drift alarm (added 2026-10-15)

`--all` now also prints a **drift alarm** per strategy: a one-sided CUSUM on % return per trade (points ÷ entry price)
against the strategy's backtest from 2023 up to the first live trade. It asks "has this strategy's edge gone?", separately
from the edge ratio, which asks "is my execution matching the backtest?".

| Status | Meaning | Action |
|---|---|---|
| OK | CUSUM below half the alarm level | nothing |
| WATCH | between half and the alarm level | check the strategy's recent trades and the market regime |
| ALARM | at or above the alarm level | cut that strategy to **half size** and review; restart the monitoring after acting |

The alarm level is calibrated per strategy so a healthy strategy false-alarms only ~5% of the time over about a year of its
trades. It is slow for small edges: a complete loss of edge is caught in a median ~31–73 trades for Bridge Monday,
Overnight Bias ML, EOS and Monday Long, but ~220 trades (about 2 years) for Vault Break and Late-Day Flow — a safety net
for a real breakdown, not a quick switch. History demo (`--drift-demo`, reference 2018–20, monitored 2021–26): no alarms
except Bridge Monday in Feb 2023 (its weak 2023–24 stretch).
