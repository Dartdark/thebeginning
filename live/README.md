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
