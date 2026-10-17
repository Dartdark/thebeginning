# Backtest Report: GoldenCross on NQ-USD (Real 2024 Historical Data)

## Executive Summary
This report documents the first end-to-end backtest of the `GoldenCross` strategy executed on real 1-minute historical data imported from the user's data store.

- **Strategy:** `GoldenCross`
- **Exchange:** `Custom Data`
- **Symbol:** `NQ-USD`
- **Timeframe:** `1h`
- **Period:** `2024-02-01` to `2024-12-01` (10 months)
- **Session ID:** `691965d0-3155-4308-b905-9c1508e3e6ec`
- **Dashboard:** http://localhost:9000/#/backtest/691965d0-3155-4308-b905-9c1508e3e6ec

---

## Ingestion & Pipeline Configuration
- **Source File:** `c:\NQData\NQ_1min_ON_2024.csv`
- **Rows Ingested:** 243,954 1-minute bars
- **Date Range Covered:** 2024-01-01 to 2024-12-31
- **Timezone Alignment:** Converted from CME local exchange time (`America/Chicago`) to UTC Unix millisecond timestamps.
- **Storage:** Stored atomically in Jesse's database under `Custom Data / NQ-USD / 1m`.

---

## Strategy Parameters
- `fast_period`: 50
- `slow_period`: 200
- `stop_loss_atr_mult`: 3.0
- `risk_percentage`: 1.5%

---

## Performance Metrics

| Metric | Value |
|---|---|
| **Starting Balance** | $10,000.00 |
| **Finishing Balance** | $9,477.78 |
| **Net Profit** | -$522.22 (-5.22%) |
| **Total Trades** | 25 |
| **Winning Trades** | 6 (24.0%) |
| **Losing Trades** | 19 (76.0%) |
| **Longs Win Rate** | 30.77% (4/13) |
| **Shorts Win Rate** | 16.67% (2/12) |
| **Win/Loss Ratio** | 1.64 |
| **Average Win** | $93.11 |
| **Average Loss** | $56.89 |
| **Max Drawdown** | -5.22% |
| **Sharpe Ratio** | -1.31 |
| **Sortino Ratio** | -1.99 |
| **Calmar Ratio** | -1.20 |
| **Fees Paid** | $195.18 |

---

## Analysis & Observations
1. **Trend Choppiness:** A pure 50/200 SMA cross on the 1h timeframe suffered from whipsaws during consolidation phases, leading to consecutive small stop-outs (19 losses vs 6 wins).
2. **Positive Win/Loss Payoff:** Winning trades averaged $93.11 vs $56.89 for losing trades (ratio 1.64), demonstrating that winners were allowed to run, but win rate was insufficient without a trend strength filter (e.g. ADX or volume confirmation).
3. **Execution Correctness:** The strategy sized positions accurately according to the 1.5% risk budget with fractional contracts (e.g. 0.566 units), trailing stops ratcheted properly, and all 25 trades exited cleanly.
