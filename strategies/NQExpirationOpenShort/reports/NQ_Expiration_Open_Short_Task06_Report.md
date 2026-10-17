# Task 06 — NQ Expiration Open Short (NQExpirationOpenShort) Blind Verification Report

## 1. Objective & Configuration

- **Role**: Independent blind verification of the NQ Expiration Open Short rule from specification text (agents/tasks/TASK_06_EXPIRATION_OPEN_SHORT.md and agents/tasks/COMMON_NQ.md).
- **Instrument / Route**: NQ-USD on Custom Data, 5m strategy timeframe (fast_mode = False for full 1-minute intrabar stop and limit simulation).
- **Date Range**: 2018-01-02 to 2026-10-09 (warm_up_candles = 210).
- **Execution Settings**:
  - Fee rate: 0.0%
  - Position size: 1.0 contract (raw index points reported directly; $20/pt)
  - Starting balance: $1,000,000 (futures_leverage = 10, cross margin) so margin never restricts order execution.

### Jesse Backtest Sessions & Dashboard Links

1. **Warm-Up Investigation Run (warm_up_candles = 4000)**
   - **Session ID**: 4f196d99-61bc-4424-b65b-912e3c99e7b8
   - **Dashboard**: http://localhost:9000/#/backtest/4f196d99-61bc-4424-b65b-912e3c99e7b8
   - **Outcome**: Stopped prior to execution because NQ_1min_ON_2017.csv only contains overnight bars (no day bars 08:00–15:15 CT in December 2017), causing Jesse candle validation to identify daytime gaps when looking back 4,000 candles.
2. **Completed Full-Precision Verification Run (warm_up_candles = 210, fast_mode = False)**
   - **Session ID**: 8c0367c3-26a4-4390-b910-020887387d80
   - **Dashboard**: http://localhost:9000/#/backtest/8c0367c3-26a4-4390-b910-020887387d80
   - **Status**: finished (105 trades across 3,107,473 1-minute candles)

---

## 2. Headline Results & Year-by-Year Breakdown

### Overall Summary (Jesse Backtest 8c0367c3-26a4-4390-b910-020887387d80)

| Metric | Value |
| :--- | :--- |
| **Total Trades** | **105** (all short) |
| **Winning Trades** | **63** (60.00% win rate) |
| **Losing Trades** | **42** (40.00%) |
| **Stop-Loss Exits (stop)** | **22** (20.95% of trades) |
| **10:00 CT Time Exits (time)** | **83** (79.05% of trades; 63 wins, 20 losses) |
| **Total Raw Points** | **+2,578.435 pts** (+2,578.44 pts) |
| **Average Points per Trade** | **+24.5565 pts/trade** (+24.56 pts/trade) |
| **Average Win / Average Loss** | +82.8333 pts / -62.8587 pts (ratio 1.3178) |
| **Largest Winning Trade** | +255.50 pts (2025-06-20) |
| **Largest Losing Trade** | -181.59 pts (2026-07-17) |
| **Sharpe Ratio** | 0.9516 |
| **Sortino Ratio** | 1.8457 |
| **Calmar Ratio** | 0.7990 |
| **Max Drawdown ($1M base)** | -0.0367% (-367.45 pts peak-to-trough) |

### Breakdown by Year

| Year | Trades | Wins | Win Rate | Stops | Average Points | Total Points |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **2018** | 12 | 7 | 58.33% | 2 | +1.87 | +22.43 |
| **2019** | 12 | 7 | 58.33% | 3 | +0.26 | +3.18 |
| **2020** | 12 | 7 | 58.33% | 2 | +23.90 | +286.75 |
| **2021** | 12 | 7 | 58.33% | 3 | +9.61 | +115.32 |
| **2022** | 12 | 7 | 58.33% | 3 | +46.81 | +561.67 |
| **2023** | 12 | 8 | 66.67% | 2 | +36.26 | +435.09 |
| **2024** | 12 | 7 | 58.33% | 2 | +24.69 | +296.27 |
| **2025** | 12 | 9 | 75.00% | 2 | +65.83 | +789.98 |
| **2026** (to Oct 09) | 9 | 4 | 44.44% | 3 | +7.52 | +67.72 |
| **Total (2018–2026)** | **105** | **63** | **60.00%** | **22** | **+24.56** | **+2578.43** |

Note: Every single year from 2018 through 2026 delivered net positive performance. Stop-loss frequency was remarkably steady across the entire 9-year span, experiencing exactly 2 or 3 stops per year.

---

## 3. Time Zone Conversion & Missing-Minute Handling

### Time Zone Conversion (America/Chicago Close -> UTC Open)

1. **Source Timestamps**:
   - The raw CSV data files (NQ_1min_<year>.csv and NQ_1min_ON_<year>.csv) contain date (YYYYMMDD) and time (HHMM) representing the closing minute of each 1-minute bar in America/Chicago (US Central).
   - For example, 20190102,801 represents the bar from 08:00 to 08:01 CT.
2. **Epoch Conversion**:
   - Each row's open timestamp was calculated as open_ct = close_ct - 1 minute.
   - We mapped each timestamp through US Central Daylight Saving Time rules (CDT = UTC-5, CST = UTC-6) to produce standard Unix epoch milliseconds in UTC for Jesse's custom candle database.
3. **5-Minute Bar Alignment**:
   - In Jesse, 5-minute candles are anchored to clock intervals :00, :05, :10, :15, :20, :25, :30, ...
   - The 5-minute bar closing at 08:30 CT corresponds to the interval 08:25:00 to 08:30:00 CT (open_ts = 08:25 CT, close_ts = 08:30 CT).
   - The bar closing at 10:00 CT corresponds to 09:55:00 to 10:00:00 CT.
4. **Calendar Day Transitions**:
   - The 5-minute bar closing at 00:00 CT (opening at 23:55 CT on the previous day) is assigned to the new Central date, satisfying the rule that a bar stamped 00:00 belongs to the new date.

---

## 4. Ambiguities & Resolutions

1. **Entry Fill Timing ("Sell short next bar at market" vs "At close of 08:30 bar")**:
   - In Jesse, when a strategy signals self.sell = qty, self.price inside go_short() triggered by should_short() at the close of the 08:30 bar, the market order executes at the close price of that bar (which equals the opening print of the 08:31 1m candle).
   - In pure Python simulation, we tested both variations:
     - Fill at 08:30 bar close: 105 trades, +2,578.44 points (+24.56 pts/trade)
     - Fill at next 1-minute bar open (08:31 open): 105 trades, +2,580.69 points (+24.58 pts/trade)
     - Both implementations produce the exact same 105 trades, 63 wins, 22 stops, with only +2.25 total points difference across 9 years (+0.02 pts/trade). Jesse backtest 8c0367c3 matches the primary fill.
2. **Holiday / Closed Expiration Fridays**:
   - The rule explicitly lists four closed third Fridays:
     - 2019-04-19 (Good Friday) -> Traded Thursday 2019-04-18 (+24.75 pts)
     - 2022-04-15 (Good Friday) -> Traded Thursday 2022-04-14 (+178.00 pts)
     - 2025-04-18 (Good Friday) -> Traded Thursday 2025-04-17 (+75.25 pts)
     - 2026-06-19 (Juneteenth) -> Traded Thursday 2026-06-18 (-29.50 pts)
   - The strategy accurately identifies these dates, suppresses entry on the closed Friday, and executes on the Thursday before.
3. **15-Day Monday–Friday Daily ATR**:
   - ATR is computed using calendar date True Range: TR = max(day_high, prev_date_close) - min(day_low, prev_date_close).
   - Only Monday–Friday sessions are scored.
   - On the first expiration date of 2018 (2018-01-19), 13 trading days had elapsed since Jan 2. With 2 prior TRs scored from late December 2017 data, 15 TRs existed and Jan 19 was traded.

---

## 5. Data Anomalies & Observations

1. **December 2017 Day Session Missing**:
   - The raw data directory research_scripts/data/ contained NQ_1min_ON_2017.csv (overnight hours 15:16–07:59 CT) but lacked NQ_1min_2017.csv (day hours 08:00–15:15 CT). Continuous 24/5 day bars began on 2018-01-02.
   - Initial backtest drafts with warm_up_candles = 4000 failed Jesse's candle validation due to daytime gaps in December 2017.
   - Configuring warm_up_candles = 210 perfectly accommodated continuous intraday data while ensuring the 15-day ATR was fully active for all 2018 expiration sessions.
2. **Missing Minutes**:
   - Missing 1-minute bars during quiet market hours were correctly filled with zero-volume flat candles using the previous close price to preserve continuous timeflow for Jesse's candle engine.
