# Task 04 — NQ Overnight Bias with ML Day Filter (`NQOvernightBiasML`) Blind Verification Report

## 1. Objective & Configuration

- **Role**: Independent blind verification of the NQ Overnight Bias with an ML day filter specification (`tasks/TASK_04_OVERNIGHT_BIAS_ML.md` and `tasks/COMMON_NQ.md`).
- **Instrument / Route**: `NQ-USD` on `Custom Data`, `15m` strategy timeframe (`fast_mode = False` for full 1-minute intrabar stop and limit order execution).
- **Date Range**: `2018-01-02` to `2026-10-09` (`warm_up_candles = 210`).
- **Execution Settings**:
  - Fee rate: `0.0%`
  - Position size: `1.0` contract (raw index points reported directly; $20/pt)
  - Starting balance: `$1,000,000` (`futures_leverage = 10`, cross margin) so margin never restricts order execution.

### Jesse Backtest Sessions & Dashboard Links

Dashboard: http://localhost:9000/#/backtest/db379996-6e03-493a-8ee2-8b107335d4ac

1. **Completed Full-Precision Verification Run (`warm_up_candles = 210`, `fast_mode = False`)**
   - **Session ID**: `db379996-6e03-493a-8ee2-8b107335d4ac`
   - **Dashboard**: [View on dashboard](http://localhost:9000/#/backtest/db379996-6e03-493a-8ee2-8b107335d4ac)
   - **Status**: `finished` (328 trades across 3,107,473 1-minute candles)

---

## 2. Headline Results & Year-by-Year Breakdown

### Overall Summary (Jesse Backtest `db379996-6e03-493a-8ee2-8b107335d4ac`)

| Metric | Value |
| :--- | :--- |
| **Total Trades** | **328** (`153` longs, `175` shorts) |
| **Winning Trades** | **191** (`58.23%` win rate overall) |
| **Longs Win Rate** | **65.36%** (`100` wins / `153` longs) |
| **Shorts Win Rate** | **52.00%** (`91` wins / `175` shorts) |
| **Losing Trades** | **137** (`41.77%`) |
| **Target Exits (`target`)** | **22** (`6.71%` of trades; 3x stop distance = 0.90x ATR) |
| **Stop-Loss Exits (`stop`)** | **83** (`25.30%` of trades; 0.30x ATR) |
| **14:30 CT Time Exits (`time`)** | **223** (`67.99%` of trades; `169` wins, `54` losses) |
| **Total Raw Points** | **+11,569.5450 pts** (`+11,569.55` pts) |
| **Average Points per Trade** | **+35.2730 pts/trade** (`+35.27` pts/trade) |
| **Average Win / Average Loss** | `+108.3842 pts` / `-66.6558 pts` (ratio `1.6260`) |
| **Gross Profit / Gross Loss** | `+20,701.39 pts` / `-9,131.85 pts` (profit factor `2.2670`) |
| **Largest Winning Trade** | `+447.75 pts` |
| **Largest Losing Trade** | `-303.85 pts` |
| **Sharpe Ratio** | **1.9068** |
| **Sortino Ratio** | **4.1641** |
| **Calmar Ratio** | **1.7025** |
| **Max Drawdown ($1M base)** | `-0.0771%` (`-770.68` pts peak-to-trough) |

### Breakdown by Year

| Year | Trades | Longs | Shorts | Wins | Win Rate | Targets | Stops | Time Exits | Average Points | Total Points |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2018** *(from Apr 02)* | 25 | 9 | 16 | 9 | 36.00% | 2 | 11 | 12 | +2.76 | +68.92 |
| **2019** | 32 | 15 | 17 | 19 | 59.38% | 3 | 6 | 23 | +21.10 | +675.04 |
| **2020** | 31 | 17 | 14 | 20 | 64.52% | 2 | 4 | 25 | +33.76 | +1046.57 |
| **2021** | 40 | 19 | 21 | 24 | 60.00% | 4 | 11 | 25 | +38.41 | +1536.39 |
| **2022** | 49 | 17 | 32 | 31 | 63.27% | 2 | 11 | 36 | +55.55 | +2721.76 |
| **2023** | 34 | 15 | 19 | 16 | 47.06% | 2 | 13 | 19 | +21.41 | +727.95 |
| **2024** | 38 | 17 | 21 | 25 | 65.79% | 3 | 6 | 29 | +52.95 | +2012.23 |
| **2025** | 47 | 25 | 22 | 30 | 63.83% | 1 | 12 | 34 | +20.74 | +974.89 |
| **2026** *(to Oct 09)* | 32 | 19 | 13 | 17 | 53.12% | 3 | 9 | 20 | +56.43 | +1805.79 |
| **Total (2018–2026)** | **328** | **153** | **175** | **191** | **58.23%** | **22** | **83** | **223** | **+35.27** | **+11569.55** |

*Note: All 9 years from 2018 through 2026 delivered net positive points. The ML day filter reduced trade count from 673 in Task 03 to 328 in Task 04 while increasing expectancy per trade from +19.71 pts to +35.27 pts (+78.9% improvement) and lifting the overall win rate from 51.26% to 58.23% (with Longs reaching 65.36% win rate).*

---

## 3. Time Zone Conversion & Missing-Minute Handling

### Time Zone Conversion (`America/Chicago` Close -> UTC Open)

1. **Source Timestamps**:
   - The raw CSV data files (`NQ_1min_<year>.csv` and `NQ_1min_ON_<year>.csv`) contain `date` (`YYYYMMDD`) and `time` (`HHMM`) representing the **closing** minute of each 1-minute bar in `America/Chicago` (`US Central`).
2. **Epoch Conversion**:
   - Each row's open timestamp was calculated as open_ct = close_ct - 1 minute.
   - We applied US Central Daylight Saving Time rules (`CDT = UTC-5`, `CST = UTC-6`) to convert to standard Unix epoch milliseconds in UTC for Jesse's custom candle database.
3. **15-Minute Bar Alignment**:
   - 15-minute candles align to `:00, :15, :30, :45` clock intervals.
   - The 15-minute bar closing at `23:15 CT` starts the Overnight Range.
   - The bar closing at `08:30 CT` concludes the Overnight Range.
   - The bar closing at `08:45 CT` forms the Opening Range and computes Bias.
   - The entry window spans from the 08:45 bar close up to but not including `14:00 CT` (`11:00 CT` on EARLY days).
   - The flatten time is `14:30 CT` (`11:30 CT` on EARLY days).

---

## 4. Ambiguities & Resolutions

1. **ML Day Score Computation and History Storage**:
   - Stored trading days require Monday–Friday, an RTH bar stamped `11:00–15:15`, and both `open830` and `close1500` present.
   - `open830` is the open of the 08:45 bar (the first bar stamped after 08:30 up to 08:45).
   - `close1500` is tracked as the close of the last bar stamped at or before 15:00.
   - `A[k]` stores the 15-day ATR as it stood on the last bar of that date before the new date's TR is added.
   - The score is computed on the first bar of each new date once at least 59 trading days have been stored. The 59th trading day was reached on March 26, 2018, and the first eligible trade was executed on April 2, 2018.
2. **Feature Math**:
   - `ret1`, `ret5`, `ret20`: Natural logs of `C[0] / C[k]`.
   - `rth1`: Natural log of `C[0] / O[0]`.
   - `atr_ratio`: Today's ATR (after yesterday's TR is added) divided by the 60-day average of `(today_ATR + A[0..58]) / 60`.
   - `dist50`: Natural log of `C[0] / mean(C[0..49])`.
   - `rv`: Unbiased sample standard deviation of `r_0..r_4` (ddof=1, denominator 4) divided by that of `r_0..r_19` (ddof=1, denominator 19); if denominator is 0, `rv = 1.0`.
   - `tdm3`: 1 if today is among the first 3 trading days of its month, counting stored trading days.
   - `opex`: 1 if today is Monday–Friday and Friday of the current week falls between the 15th and 21st.
3. **Filter Thresholds**:
   - Long entries require `score >= 0.03` and `ADX > 20`.
   - Short entries require `score >= 0.00` and `ADX > 20`.
   - Days with fewer than 59 stored trading days take zero trades.
4. **Exits & Asymmetric Risk/Reward**:
   - Stop distance: 0.30 x ATR.
   - Target distance: 3 x stop = 0.90 x ATR.
   - Time exit: Flatten at the close of 14:30 CT (11:30 CT on EARLY days).

---

## 5. Data Anomalies & Observations

1. **Filtering Efficacy**:
   - Requiring `score >= 0.03` for longs and `score >= 0.00` for shorts eliminated 345 lower-quality trades from Task 03, while boosting average points per trade from +19.71 to +35.27 and increasing the win rate from 51.26% to 58.23%.
2. **Missing Minutes**:
   - Missing minutes during overnight intervals and weekends were handled by flat candles with zero volume to preserve continuous timeflow.
