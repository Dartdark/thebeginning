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
