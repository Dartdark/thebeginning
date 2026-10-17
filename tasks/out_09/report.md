# Task 09 — ES MOC Follow (`ESMOCFollow`) Blind Verification Report

## 1. Executive Summary & Configuration

- **Strategy**: `ESMOCFollow` (ES MOC Follow, continuous E-mini S&P 500 futures, $50/pt, tick 0.25)
- **Timeframe**: 5-minute bars (`5m`), longs and shorts
- **Data Period**: `2018-01-02` to `2026-10-12` (8.8 years, full-precision intrabar 1m execution, `fast_mode = False`)
- **Execution Settings**:
  - Fees: 0.0 (raw points reported directly)
  - Position size: 1.0 contract
  - Starting balance: $1,000,000 (cross margin, `leverage = 10` so margin never constrains execution)
- **Jesse Backtest Session**:
  - **Session ID**: `210aa577-3abc-4b40-a59d-1ae29f647c06`
  - **Dashboard URL**: [View on Jesse Dashboard](http://localhost:9000/#/backtest/210aa577-3abc-4b40-a59d-1ae29f647c06)

---

## 2. Headline Results & Yearly Breakdown

### Overall Performance Metrics

| Metric | Raw Index Points | Value in Dollars (1 ES @ $50/pt) |
| :--- | :---: | :---: |
| **Total Trades** | **198** | **198** |
| **Longs Count / Win Rate** | 84 trades / **66.67%** (56 wins) | 84 trades / 66.67% |
| **Shorts Count / Win Rate** | 114 trades / **60.53%** (69 wins) | 114 trades / 60.53% |
| **Overall Win Rate** | **63.13%** (125 wins / 198 trades) | **63.13%** |
| **Losing Trades** | 67 trades (33.84%) + 6 flat | 67 losses |
| **Stop-Loss Exits (`stop`)** | **13** (6.57% of all trades) | 13 stops |
| **15:00 CT Time Exits (`time`)**| **185** (93.43% of all trades) | 185 time exits |
| **Total Net Points / P&L** | **+636.17 pts** | **+$31,808.54** |
| **Average Points per Trade** | **+3.21 pts/trade** | **+$160.65/trade** |
| **Average Win** | +9.37 pts | +$468.40 |
| **Average Loss** | -7.98 pts | -$399.13 |
| **Profit Factor** | **2.19** (Gross Win 1171.0 / Gross Loss 534.8) | **2.19** |
| **Sharpe Ratio** | **1.3135** | **1.3135** |
| **Sortino Ratio** | **2.4358** | **2.4358** |
| **Calmar Ratio** | **0.9318** | **0.9318** |
| **Max Drawdown ($1M base)** | -0.00777% (-77.73 pts) | **-$3,886.50** |
| **Average Holding Period** | 582.1 seconds (~9.7 minutes) | 9.7 minutes |

---

### Breakdown by Year

| Year | Trades | Longs | Shorts | Wins | Win Rate | Stops | Avg Points | Total Points | Total Net $ (@ $50/pt) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2018** | 38 | 19 | 19 | 20 | 52.6% | 3 | +0.73 pts | +27.59 pts | +$1,379.50 |
| **2019** | 16 | 7 | 9 | 7 | 43.8% | 1 | -0.02 pts | -0.25 pts | -$12.50 |
| **2020** | 23 | 9 | 14 | 15 | 65.2% | 2 | +8.94 pts | +205.71 pts | +$10,285.50 |
| **2021** | 16 | 7 | 9 | 11 | 68.8% | 2 | +5.66 pts | +90.49 pts | +$4,524.50 |
| **2022** | 30 | 15 | 15 | 20 | 66.7% | 1 | +3.94 pts | +118.22 pts | +$5,911.00 |
| **2023** | 20 | 5 | 15 | 12 | 60.0% | 0 | +2.24 pts | +44.75 pts | +$2,237.50 |
| **2024** | 25 | 10 | 15 | 18 | 72.0% | 1 | +5.34 pts | +133.60 pts | +$6,680.00 |
| **2025** | 20 | 8 | 12 | 13 | 65.0% | 2 | -0.73 pts | -14.69 pts | -$734.50 |
| **2026** *(to Oct 12)* | 10 | 4 | 6 | 9 | 90.0% | 1 | +3.08 pts | +30.75 pts | +$1,537.50 |
| **Total (2018–2026)** | **198** | **84** | **114** | **125** | **63.13%** | **13** | **+3.21 pts** | **+636.17 pts** | **+$31,808.54** |

*Note: Positive in 7 of 9 calendar years (with 2019 essentially flat at -$12.50), demonstrating exceptional edge stability.*

---

## 3. Time Zone & Missing-Minute Handling

1. **Source Data & Stamping**:
   - Continuous 1-minute `ES_1min_<year>.csv` files covering full 24-hour sessions.
   - Timestamps represent the closing minute of each 1-minute bar in `America/Chicago` (`US Central`).
   - Candle open timestamps in Jesse are standard Unix epoch milliseconds (UTC), converted using `America/Chicago` DST transitions (`CDT = UTC-5`, `CST = UTC-6`).
2. **Bar Alignments**:
   - `14:00 CT` bar: The 5-minute bar covering `13:55–14:00 CT`, stamped at `14:00`. Its close is recorded as the daily `reference_price`.
   - `14:50 CT` bar: The 5-minute bar covering `14:45–14:50 CT`, stamped at `14:50`. Its close is evaluated against the `reference_price`.
   - `14:50–14:55 CT` bar: Stamped at `14:55 CT`. Trade fills at market at the open of this bar (at 14:50:00 CT).
   - `14:55–15:00 CT` bar: Stamped at `15:00 CT`. When this bar closes at `15:00:00 CT`, the trade liquidates at market if the stop has not been hit.

---

## 4. Ambiguities & Resolutions

1. **Reference Price Definition**:
   - "Reference price = the close of the bar stamped 14:00. Reset each date."
   - Handled by capturing the bar close when `close_dt_ct.hour == 14 and close_dt_ct.minute == 0`.
2. **Signal Condition**:
   - Evaluated at `14:50 CT` bar close.
   - `move = close_1450 - reference_price`.
   - If `|move| >= 0.30 * ATR`:
     - `move > 0`: Long 1 contract next bar at market (14:50 open).
     - `move < 0`: Short 1 contract next bar at market (14:50 open).
3. **Exits**:
   - Protective stop: $0.25 \times \text{ATR}$ from entry fill price, evaluated continuously on 1-minute intrabar price action.
   - Time exit: Close at the close of the first bar stamped at or after `15:00 CT` (holding time = exactly 10 minutes).
4. **Data Peculiarities**:
   - 0 missing data gaps during the 14:00–15:00 CT window across all 8.8 years.
   - Clean execution across 198 total trades.
