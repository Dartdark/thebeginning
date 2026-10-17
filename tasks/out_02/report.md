# Task 02 — NQ Vault Break (`NQVaultBreak`) Blind Verification Report

## 1. Objective & Configuration

- **Role**: Independent blind verification of the NQ Vault Break rule from specification text (`agents/tasks/TASK_02_VAULT_BREAK.md` and `agents/tasks/COMMON_NQ.md`).
- **Instrument / Route**: `NQ-USD` on `Custom Data`, `30m` strategy timeframe (`fast_mode = False` for full 1-minute intrabar stop and target simulation).
- **Date Range**: `2018-01-02` to `2026-10-09` (`warm_up_candles = 210`).
- **Execution Settings**:
  - Fee rate: `0.0%`
  - Position size: `1.0` contract (raw index points reported directly; $20/pt)
  - Starting balance: `$1,000,000` (`futures_leverage = 10`, cross margin) so margin never restricts order execution.

### Jesse Backtest Sessions & Dashboard Links

1. **Completed Full-Precision Verification Run (`warm_up_candles = 210`, `fast_mode = False`)**
   - **Session ID**: `c2305985-a2d9-4c49-bb49-d6c13674a80b`
   - **Dashboard**: [View on dashboard](http://localhost:9000/#/backtest/c2305985-a2d9-4c49-bb49-d6c13674a80b)
   - **Status**: `finished` (1,755 trades across 3,107,473 1-minute candles)

---

## 2. Headline Results & Year-by-Year Breakdown

### Overall Summary (Jesse Backtest `c2305985-a2d9-4c49-bb49-d6c13674a80b`)

| Metric | Value |
| :--- | :--- |
| **Total Trades** | **1,755** (all long; max 3/day) |
| **Winning Trades** | **1,159** (`66.04%` win rate; Jesse metric: `66.23%`) |
| **Losing Trades** | **591** (`33.68%`) |
| **Breakeven Trades** | **5** (`0.28%`) |
| **Target Exits (`target`)** | **904** (`51.51%` of trades; `+40.0 pts` exact) |
| **Stop-Loss Exits (`stop`)** | **334** (`19.03%` of trades; `-75.0 pts` exact) |
| **Flatten Time Exits (`time`)** | **517** (`29.46%` of trades; `255` wins, `257` losses, `5` breakeven) |
| **Total Raw Points** | **+9,621.2500 pts** (`+9,621.25` pts) |
| **Average Points per Trade** | **+5.4822 pts/trade** (`+5.48` pts/trade) |
| **Average Win / Average Loss** | `+34.4692 pts` / `-51.3173 pts` (ratio `0.6717`) |
| **Gross Profit / Gross Loss** | `+39,949.75 pts` / `-30,328.50 pts` |
| **Winning Streak / Losing Streak** | `12` trades / `7` trades |
| **Sharpe Ratio** | **1.7630** |
| **Sortino Ratio** | **2.7767** |
| **Calmar Ratio** | **1.7421** |
| **Max Drawdown ($1M base)** | `-0.0627%` (`-626.89` pts peak-to-trough) |

### Breakdown by Year

| Year | Trades | Wins | Win Rate | Targets | Stops | Time Exits | Average Points | Total Points |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2018** | 131 | 78 | 59.54% | 34 | 11 | 86 | +2.40 | +314.00 |
| **2019** | 122 | 68 | 55.74% | 18 | 4 | 100 | +2.04 | +249.00 |
| **2020** | 202 | 129 | 63.86% | 98 | 28 | 76 | +7.09 | +1432.75 |
| **2021** | 191 | 130 | 68.06% | 95 | 29 | 67 | +8.04 | +1536.25 |
| **2022** | 218 | 151 | 69.27% | 128 | 57 | 33 | +4.59 | +1000.25 |
| **2023** | 220 | 151 | 68.64% | 122 | 45 | 53 | +6.61 | +1454.00 |
| **2024** | 217 | 144 | 66.36% | 121 | 53 | 43 | +4.07 | +884.25 |
| **2025** | 227 | 159 | 70.04% | 144 | 46 | 37 | +9.15 | +2077.75 |
| **2026** *(to Oct 09)* | 227 | 149 | 65.64% | 144 | 61 | 22 | +2.96 | +673.00 |
| **Total (2018–2026)** | **1755** | **1159** | **66.04%** | **904** | **334** | **517** | **+5.48** | **+9621.25** |

*Note: Vault Break demonstrated extraordinary stability: every single year from 2018 through 2026 delivered net positive points, culminating in an overall Sharpe ratio of 1.7630 and Sortino ratio of 2.7767.*

---

## 3. Time Zone Conversion & Missing-Minute Handling

### Time Zone Conversion (`America/Chicago` Close -> UTC Open)

1. **Source Timestamps**:
   - The raw CSV data files (`NQ_1min_<year>.csv` and `NQ_1min_ON_<year>.csv`) contain `date` (`YYYYMMDD`) and `time` (`HHMM`) representing the **closing** minute of each 1-minute bar in `America/Chicago` (`US Central`).
2. **Epoch Conversion**:
   - Each row's open timestamp was calculated as $\text{open\_ct} = \text{close\_ct} - 1\text{ minute}$.
   - We applied US Central Daylight Saving Time rules (`CDT = UTC-5`, `CST = UTC-6`) to convert to standard Unix epoch milliseconds in UTC for Jesse's custom candle database.
3. **30-Minute Bar Alignment**:
   - 30-minute candles align to `:00` and `:30` clock intervals.
   - The 30-minute bar closing at `00:00 CT` corresponds to `23:30` to `00:00 CT` of the prior day, and per `COMMON_NQ.md` rules, belongs to the new date.
   - The bar closing at `10:00 CT` corresponds to `09:30` to `10:00 CT`.
   - The bar closing at `14:30 CT` corresponds to `14:00` to `14:30 CT` (flatten time on regular days).
   - On EARLY days, the bar closing at `11:00 CT` (`10:30–11:00 CT`) marks the last entry boundary, and `11:30 CT` marks the flatten time.

---

## 4. Ambiguities & Resolutions

1. **Session Open Definition**:
   - "Session open. The open of the first bar of each date. That is the bar stamped 00:00, which covers 23:30 to 00:00, if it has trades."
   - Handled directly: at the start of each new Central date, `self.session_open = b_open` of the first 30-minute bar.
2. **VWAP from Midnight**:
   - Accumulated from the first bar of each date:
     $$\text{typical\_price} = (\text{high} + \text{low} + \text{close}) / 3.0$$
     $$\text{VWAP} = \frac{\sum (\text{typical\_price} \times \text{volume})}{\sum \text{volume}}$$
   - Reset at each new date.
3. **Noise Level**:
   - $\text{noise\_level} = \text{session\_open} + 0.30 \times \text{ATR}$.
   - Entry requires both $\text{close} > \text{noise\_level}$ and $\text{close} > \text{VWAP}$.
4. **Re-Entry Logic**:
   - "After an exit the rule may enter again the same date (up to 3 trades) under the same conditions."
   - `self.trades_taken_today` is incremented on order placement, capped at 3 trades per calendar date.
5. **Intrabar Stop and Target Execution**:
   - Full-precision simulation (`fast_mode = False`) checks 1-minute intrabar candles inside each 30-minute bar.
   - Targets fill cleanly at `entry_price + 40.0`, stops fill at `entry_price - 75.0` (or 1m opening gap beyond).

---

## 5. Data Anomalies & Observations

1. **High Target-to-Stop Ratio**:
   - The fixed +40 pt target was reached in 904 trades (51.5% of all trades), exceeding stop-loss exits (334 trades, 19.0%) by almost 3 to 1, providing a strong statistical edge despite the asymmetric 75 pt stop.
2. **Missing Minutes**:
   - All missing 1-minute bars during overnight intervals were zero-volume flat candles using the previous close price to preserve continuous timeflow.
