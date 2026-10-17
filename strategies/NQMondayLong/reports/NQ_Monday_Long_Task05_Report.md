# Task 05 — NQ Monday Long (NQMondayLong) Blind Verification Report

## 1. Objective & Configuration

- **Role**: Independent blind verification of the NQ Monday Long rule from specification text (agents/tasks/TASK_05_MONDAY_LONG.md and agents/tasks/COMMON_NQ.md).
- **Instrument / Route**: NQ-USD on Custom Data, 5m strategy timeframe (fast_mode = False for full 1-minute intrabar stop simulation).
- **Date Range**: 2018-01-02 to 2026-10-09 (warm_up_candles = 210).
- **Execution Settings**:
  - Fee rate: 0.0%
  - Position size: 1.0 contract (raw index points reported directly; $20/pt)
  - Starting balance: $1,000,000 (futures_leverage = 10, cross margin) so margin never restricts order execution.

### Jesse Backtest Sessions & Dashboard Links

1. **Completed Full-Precision Verification Run (warm_up_candles = 210, fast_mode = False)**
   - **Session ID**: f2fd9dcf-5d5d-4313-8cea-bab28873b9e5
   - **Dashboard**: http://localhost:9000/#/backtest/f2fd9dcf-5d5d-4313-8cea-bab28873b9e5
   - **Status**: finished (409 trades across 3,107,473 1-minute candles)

---

## 2. Headline Results & Year-by-Year Breakdown

### Overall Summary (Jesse Backtest f2fd9dcf-5d5d-4313-8cea-bab28873b9e5)

| Metric | Value |
| :--- | :--- |
| **Total Trades** | **409** (all long) |
| **Winning Trades** | **227** (55.50% win rate) |
| **Losing Trades** | **182** (44.50%) |
| **Stop-Loss Exits (stop)** | **101** (24.69% of trades) |
| **15:00 CT Time Exits (time)** | **308** (75.31% of trades; 227 wins, 81 losses) |
| **Total Raw Points** | **+9,814.7917 pts** (+9,814.79 pts) |
| **Average Points per Trade** | **+23.9970 pts/trade** (+24.00 pts/trade) |
| **Average Win / Average Loss** | +117.7687 pts / -92.9599 pts (ratio 1.2669) |
| **Gross Profit / Gross Loss** | +26,733.50 pts / -16,918.71 pts |
| **Largest Winning Trade** | +630.75 pts |
| **Largest Losing Trade** | -470.91 pts |
| **Winning Streak / Losing Streak** | 12 trades / 8 trades |
| **Sharpe Ratio** | 1.2469 |
| **Sortino Ratio** | 2.2366 |
| **Calmar Ratio** | 0.9934 |
| **Max Drawdown ($1M base)** | -0.1121% (-1,121.35 pts peak-to-trough) |

### Breakdown by Year

| Year | Trades | Wins | Win Rate | Stops | Average Points | Total Points |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **2018** | 47 | 18 | 38.30% | 19 | -11.93 | -560.51 |
| **2019** | 48 | 28 | 58.33% | 10 | +6.66 | +319.58 |
| **2020** | 45 | 31 | 68.89% | 9 | +51.23 | +2305.17 |
| **2021** | 47 | 23 | 48.94% | 18 | +6.98 | +327.98 |
| **2022** | 45 | 20 | 44.44% | 14 | -4.35 | -195.81 |
| **2023** | 45 | 33 | 73.33% | 5 | +49.71 | +2237.12 |
| **2024** | 48 | 22 | 45.83% | 11 | +15.69 | +753.14 |
| **2025** | 48 | 32 | 66.67% | 8 | +50.30 | +2414.57 |
| **2026** (to Oct 09) | 36 | 20 | 55.56% | 7 | +61.49 | +2213.54 |
| **Total (2018–2026)** | **409** | **227** | **55.50%** | **101** | **+24.00** | **+9814.79** |

Note: Across the 9-year backtest span, 7 out of 9 years produced solid net positive performance. Only 2018 (-560.51 pts) and 2022 (-195.81 pts, bear market) had modest drawdowns, while 2020 (+2,305.17), 2023 (+2,237.12), 2025 (+2,414.57), and 2026 (+2,213.54) delivered extraordinary performance.

---

## 3. Time Zone Conversion & Missing-Minute Handling

### Time Zone Conversion (America/Chicago Close -> UTC Open)

1. **Source Timestamps**:
   - The raw CSV data files (NQ_1min_<year>.csv and NQ_1min_ON_<year>.csv) contain date (YYYYMMDD) and time (HHMM) representing the closing minute of each 1-minute bar in America/Chicago (US Central).
   - For example, 20190102,801 represents the bar from 08:00 to 08:01 CT.
2. **Epoch Conversion**:
   - Each row's open timestamp was calculated as open_ct = close_ct - 1 minute.
   - We applied US Central Daylight Saving Time rules (CDT = UTC-5, CST = UTC-6) to convert to standard Unix epoch milliseconds in UTC for Jesse's custom candle database.
3. **5-Minute Bar Alignment**:
   - In Jesse, 5-minute candles align to clock intervals :00, :05, :10, :15, :20, :25, :30, ...
   - The 5-minute bar closing at 08:30 CT corresponds to 08:25:00 to 08:30:00 CT (open_ts = 08:25 CT, close_ts = 08:30 CT).
   - The 5-minute bar closing at 15:00 CT corresponds to 14:55:00 to 15:00:00 CT.
4. **Calendar Transitions**:
   - The 5-minute bar closing at 00:00 CT (opening at 23:55 CT on Sunday evening) belongs to the new Monday date, in accordance with the rule that a bar stamped 00:00 belongs to the new date.

---

## 4. Ambiguities & Resolutions

1. **Task-Specific Early-Close Monday List**:
   - The specification explicitly stated: Early-close Mondays are skipped (this task's own list; it is NOT the EARLY list). A Monday counts as early-close if it is: Jan 1 or Jan 2; Jan 15-21; Feb 15-21; May 25 or later; from 2022, Jun 19 or Jun 20; Jul 4 or Jul 5; Sep 1-7; Dec 25 or Dec 26.
   - We adhered strictly to this exact list rather than the general holiday table from COMMON_NQ.md. For example, Monday Dec 24 and Monday Jul 2 are NOT in this task's skip list and were correctly traded.
2. **Entry Fill Timing ("Buy 1 contract next bar at market")**:
   - Triggered at the close of the 08:30 CT bar (08:25–08:30 CT), the strategy sets self.buy = qty, self.price. Jesse executes the market order at the close price of the 08:30 bar (identical to the open of the 08:31 1m bar).
3. **Intrabar Stop-Loss Simulation**:
   - Stop is set to 0.50 * ATR below entry fill price: stop_price = entry_price - 0.50 * ATR.
   - Jesse's full-precision simulation (fast_mode = False) inspects 1-minute intrabar candles inside each 5-minute bar. If a 1-minute bar's low touches the stop price, the stop is filled.
4. **Time Exit at 15:00 CT**:
   - At the close of the first bar stamped at or after 15:00 CT (14:55–15:00 CT), the strategy calls self.liquidate(), exiting the trade at the 15:00 close.

---

## 5. Data Anomalies & Observations

1. **Continuous 24/5 Monday Session**:
   - Mondays begin with the Sunday evening Globex open (17:00 CT Sunday) and run continuously into the Monday day session. The strategy processes all overnight bars from Sunday evening through Monday morning to accumulate intraday highs and lows, and safely calculates ATR from completed prior Monday–Friday daily sessions.
2. **Missing Minutes**:
   - Missing 1-minute bars during overnight intervals were filled with flat zero-volume candles carrying the previous close price to preserve uninterrupted continuity for Jesse's candle parser.
