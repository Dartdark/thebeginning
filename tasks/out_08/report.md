# Task 08 — NQ NFP Fade (`NQNFPFade`) Blind Verification Report

## 1. Objective & Configuration

- **Role**: Independent blind verification of the NQ NFP Fade rule from specification text (`agents/tasks/TASK_08_NFP_FADE.md` and `agents/tasks/COMMON_NQ.md`).
- **Instrument / Route**: `NQ-USD` on `Custom Data`, `5m` strategy timeframe (`fast_mode = False` for full 1-minute intrabar stop simulation).
- **Date Range**: `2018-01-02` to `2026-10-09` (`warm_up_candles = 210`).
- **Execution Settings**:
  - Fee rate: `0.0%`
  - Position size: `1.0` contract (raw index points reported directly; $20/pt)
  - Starting balance: `$1,000,000` (`futures_leverage = 10`, cross margin) so margin never restricts order execution.

### Jesse Backtest Sessions & Dashboard Links

1. **Completed Full-Precision Verification Run (`warm_up_candles = 210`, `fast_mode = False`)**
   - **Session ID**: `0d6a7448-180b-4d79-ac3b-39abfc8fdb84`
   - **Dashboard**: [View on dashboard](http://localhost:9000/#/backtest/0d6a7448-180b-4d79-ac3b-39abfc8fdb84)
   - **Status**: `finished` (78 trades across 3,107,473 1-minute candles)

---

## 2. Headline Results & Year-by-Year Breakdown

### Overall Summary (Jesse Backtest `0d6a7448-180b-4d79-ac3b-39abfc8fdb84`)

| Metric | Value |
| :--- | :--- |
| **Total Trades** | **78** (`35` longs, `43` shorts) |
| **Winning Trades** | **40** (`51.28%` win rate overall) |
| **Longs Win Rate** | **60.00%** (`21` wins / `35` longs) |
| **Shorts Win Rate** | **44.19%** (`19` wins / `43` shorts) |
| **Losing Trades** | **38** (`48.72%`) |
| **Stop-Loss Exits (`stop`)** | **2** (`2.56%` of trades) |
| **09:00 CT Time Exits (`time`)** | **76** (`97.44%` of trades; 40 wins, 36 losses) |
| **Total Raw Points** | **+1,379.4083 pts** (`+1,379.41` pts) |
| **Average Points per Trade** | **+17.6847 pts/trade** (`+17.68` pts/trade) |
| **Average Win / Average Loss** | `+75.3688 pts` / `-43.0353 pts` (ratio `1.7513`) |
| **Gross Profit / Gross Loss** | `+3,014.75 pts` / `-1,635.34 pts` |
| **Largest Winning Trade** | `+276.75 pts` |
| **Largest Losing Trade** | `-140.75 pts` |
| **Sharpe Ratio** | **0.6960** |
| **Sortino Ratio** | **1.4374** |
| **Calmar Ratio** | **0.3978** |
| **Max Drawdown ($1M base)** | `-0.0395%` (`-395.05` pts peak-to-trough) |

### Breakdown by Year

| Year | Trades | Longs | Shorts | Wins | Win Rate | Stops | Average Points | Total Points |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2018** | 8 | 4 | 4 | 3 | 37.50% | 0 | +4.62 | +37.00 |
| **2019** | 10 | 5 | 5 | 4 | 40.00% | 0 | -6.12 | -61.25 |
| **2020** | 4 | 2 | 2 | 0 | 0.00% | 1 | -40.05 | -160.19 |
| **2021** | 10 | 3 | 7 | 6 | 60.00% | 1 | +30.81 | +308.10 |
| **2022** | 12 | 9 | 3 | 7 | 58.33% | 0 | +26.69 | +320.25 |
| **2023** | 11 | 4 | 7 | 7 | 63.64% | 0 | +31.66 | +348.25 |
| **2024** | 12 | 5 | 7 | 7 | 58.33% | 0 | +17.54 | +210.50 |
| **2025** | 6 | 1 | 5 | 3 | 50.00% | 0 | +30.71 | +184.25 |
| **2026** *(to Oct 09)* | 5 | 2 | 3 | 3 | 60.00% | 0 | +38.50 | +192.50 |
| **Total (2018–2026)** | **78** | **35** | **43** | **40** | **51.28%** | **2** | **+17.68** | **+1379.41** |

*Note: Across 9 years, 7 years were net profitable, driven by a high win/loss ratio (1.75) and extraordinarily low stop incidence (only 2 stops out of 78 trades).*

---

## 3. Time Zone Conversion & Missing-Minute Handling

### Time Zone Conversion (`America/Chicago` Close -> UTC Open)

1. **Source Timestamps**:
   - The raw CSV data files (`NQ_1min_<year>.csv` and `NQ_1min_ON_<year>.csv`) contain `date` (`YYYYMMDD`) and `time` (`HHMM`) representing the **closing** minute of each 1-minute bar in `America/Chicago` (`US Central`).
2. **Epoch Conversion**:
   - Each row's open timestamp was calculated as $\text{open\_ct} = \text{close\_ct} - 1\text{ minute}$.
   - We applied US Central Daylight Saving Time rules (`CDT = UTC-5`, `CST = UTC-6`) to convert to standard Unix epoch milliseconds in UTC for Jesse's custom candle database.
3. **Bar Alignment**:
   - `07:30 CT` bar: opens at `07:25:00 CT` and closes at `07:30:00 CT`. Its close price is the Reference Price.
   - `07:35 CT` bar: opens at `07:30:00 CT` and closes at `07:35:00 CT`. Its range ($\text{high} - \text{low}$) is tested for release spike.
   - `07:45 CT` bar: opens at `07:40:00 CT` and closes at `07:45:00 CT`. Evaluates entry signal and enters next bar at market (07:45 close).
   - `09:00 CT` bar: opens at `08:55:00 CT` and closes at `09:00:00 CT`. Liquidates open trade at the 09:00 close (holding period: 75 minutes).

---

## 4. Ambiguities & Resolutions

1. **Median Range Calculation**:
   - "Compare it with the median of the previous 20 such ranges, not counting today's; with an even count, the median is the average of the middle two. It is a spike if range > 3.0 × that median. No spike can be flagged until 20 earlier ranges exist. Then add today's range to the history."
   - Computed as $(S[9] + S[10]) / 2.0$ where $S$ is the sorted array of the preceding 20 ranges. Range history accumulates on every Monday–Friday trading session.
2. **Friday Day-of-Month Rule**:
   - "today is a Friday with day-of-month $\le 10$".
   - This cleanly captures the first Friday of the month (days 1–7) or the second Friday if the first month day was Saturday (days 8–10), which corresponds to the standard NFP release calendar.
3. **Fade Direction**:
   - $\text{reaction} = \text{close}_{07:45} - \text{reference\_price}_{07:30}$.
   - If $\text{reaction} > 0$: Sell short 1 contract (fading upward reaction).
   - If $\text{reaction} < 0$: Buy long 1 contract (fading downward reaction).
4. **Good Friday 2023 Early Market Close**:
   - On Good Friday `2023-04-07`, an NFP trade entered at `07:45 CT`. Due to holiday rules, CME equity index futures closed early at `08:15 CT` for the Easter weekend. No bars occurred between 08:15 CT Friday and 17:00 CT Sunday.
   - Per the literal rule *"Otherwise close at the close of the first bar stamped at or after 09:00"*, Jesse liquidated the position on the Sunday evening reopening bar (`17:05 CT`) at `13,169.50` (entry: `13,165.50`, small 4-point loss).

---

## 5. Data Anomalies & Observations

1. **Rare Stop Triggers**:
   - The $0.50 \times \text{ATR}$ stop distance gives sufficient breathing room for the post-NFP noise to settle, resulting in a 97.4% time exit completion rate. Only 2 stops occurred across the entire 9-year dataset (2020-04-03 and 2021-03-05).
2. **Missing Minutes**:
   - All missing 1-minute bars during overnight intervals were zero-volume flat candles using the previous close price to preserve continuous timeflow.
