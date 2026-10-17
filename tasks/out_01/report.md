# Task 01 — CL Sunday Opening Gap Fade (`CLSundayFade`) Blind Verification Report

## 1. Objective & Configuration

- **Role**: Independent blind verification of the CL Sunday Opening Gap Fade rule from specification text only.
- **Instrument / Route**: `CL-USD` on `Custom Data`, `5m` strategy timeframe (`fast_mode = False` for full 1-minute intrabar stop and opening-gap simulation).
- **Date Range**: `2018-01-01` to `2026-10-14` (with `5,400` 5-minute warm-up candles from `2017-12-01` to `2017-12-29` to pre-populate the 15-day Monday–Friday Daily ATR before `2018-01-01`).
- **Execution Settings**:
  - Fee rate: `0` (`0.0%`)
  - Position size: `1.0` contract (`utils.size_to_qty` calibrated to 1 contract; raw price points reported directly)
  - Starting balance: `$1,000,000` (`futures_leverage = 10`, cross margin) so margin never blocks a trade.

### Jesse Backtest Sessions & Dashboard Links

1. **Initial Setup Check (`warm_up_candles = 6000`)**
   - **Session ID**: `9e3443ee-a6fd-48e0-856a-67ed14b1780c`
   - **Dashboard**: http://localhost:9000/#/backtest/9e3443ee-a6fd-48e0-856a-67ed14b1780c
   - **Outcome**: Stopped prior to execution because `CL_1min_2017.csv` contains only December 2017 (`27,124` 1-minute bars = `5,424` 5-minute bars), whereas `6,000` warm-up candles required data back to `2017-11-20`. Adjusted `warm_up_candles` to `5,400`.
2. **Completed Full-Precision Verification Run (`warm_up_candles = 5400`, `fast_mode = False`)**
   - **Session ID**: `5b98605c-ccfd-4428-878e-09a0ea3eb2a8`
   - **Dashboard**: http://localhost:9000/#/backtest/5b98605c-ccfd-4428-878e-09a0ea3eb2a8
   - **Status**: `finished` (99.84s execution across 3,124,999 1-minute bars)

---

## 2. Headline Results & Year-by-Year Breakdown

### Overall Summary (Jesse Backtest `5b98605c-ccfd-4428-878e-09a0ea3eb2a8`)

| Metric | Value |
| :--- | :--- |
| **Total Trades** | **96** |
| **Winning Trades** | **62** (`64.58%` win rate) |
| **Losing Trades** | **34** (`35.42%`) |
| **Stop-Loss Exits (`stop`)** | **6** |
| **Monday 10:00 ET Time Exits (`time`)** | **90** |
| **Total Raw Points** | **+54.9570 pts** (`+54.96` pts) |
| **Average Points per Trade** | **+0.5725 pts/trade** |
| **Average Win / Average Loss** | `+1.3032 pts` / `-0.7601 pts` (ratio `1.7146`) |
| **Largest Winning / Losing Trade** | `+9.5300 pts` / `-2.6955 pts` |
| **Sharpe Ratio / Sortino Ratio** | `1.2604` / `3.5754` |
| **Max Drawdown ($1M base)** | `-0.0425%` (`-4.25` pts underwater peak-to-trough) |

### Breakdown by Year (Primary Jesse Backtest: Literal CSV = `America/Chicago` -> `America/New_York`)

| Year | Trades | Wins | Win Rate | Stops | Average Points | Total Points |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **2018** | 7 | 4 | 57.14% | 0 | -0.0329 | -0.2300 |
| **2019** | 10 | 5 | 50.00% | 0 | +0.2790 | +2.7900 |
| **2020** | 8 | 5 | 62.50% | 0 | +0.4188 | +3.3500 |
| **2021** | 9 | 4 | 44.44% | 1 | -0.2176 | -1.9580 |
| **2022** | 7 | 6 | 85.71% | 0 | +1.9157 | +13.4100 |
| **2023** | 8 | 6 | 75.00% | 1 | +0.4106 | +3.2845 |
| **2024** | 10 | 8 | 80.00% | 0 | +0.3000 | +3.0000 |
| **2025** | 14 | 10 | 71.43% | 2 | +0.5176 | +7.2470 |
| **2026** *(to Oct 13)* | 23 | 14 | 60.87% | 2 | +1.0462 | +24.0635 |
| **Total (2018–2026)** | **96** | **62** | **64.58%** | **6** | **+0.5725** | **+54.9570** |

---

## 3. Time Zone Conversion & Missing-Minute Handling

### Time Zone Conversion (`America/Chicago` Close -> UTC Open -> `America/New_York` Close)

Following the literal specification:
1. Each raw CSV row (`date=YYYYMMDD`, `time=HHMM`) is stamped at the **closing** minute of the 1-minute bar in `America/Chicago` (`CT`).
2. We first subtract `1 minute` from the bar's closing timestamp to obtain the 1-minute bar's **opening** local timestamp:
   $$\text{open\_local} = \text{close\_local} - 1\text{ minute}$$
3. We apply US Daylight Saving Time rules for `America/Chicago` (`CDT = UTC-5` from the second Sunday in March at `02:00` local time until the first Sunday in November at `02:00` local time; `CST = UTC-6` otherwise) to convert to Unix epoch milliseconds in UTC (`timestamp`).
4. Inside the Jesse strategy (`CLSundayFade`), each 5-minute candle `[open_ts_ms, open, close, high, low, volume]` has its closing timestamp computed as `close_ts_ms = open_ts_ms + 300_000` and converted to `ZoneInfo("America/New_York")` (`EST = UTC-5`, `EDT = UTC-4`). Because the 5-minute bar closing at `00:00:00 ET` (opening at `23:55:00 ET` of the prior day) has `close_dt_et.strftime("%H:%M") == "00:00"`, `close_dt_et.date()` automatically assigns the `00:00` bar to the **new Eastern calendar date**, matching the rule *"5-minute bars stamped at their close. A bar stamped `00:00` belongs to the new date."*

#### Verification on Sample Rows

| Raw CSV File & Row (`date,time`) | Bar Close (`America/Chicago`) | Bar Open (`America/Chicago`) | Offset | Jesse Open Timestamp (`UTC` & Unix ms) | 5m Bucket Close (`America/New_York`) |
| :--- | :--- | :--- | :---: | :--- | :--- |
| Spec Example: `20190101,1701` | `2019-01-01 17:01 CST` | `2019-01-01 17:00 CST` | `UTC-6` | `2019-01-01 23:00:00 UTC` (`1546383600000`) | `2019-01-01 18:05 EST` |
| `CL_1min_2017.csv`: `20171201,2` | `2017-12-01 00:02 CST` | `2017-12-01 00:01 CST` | `UTC-6` | `2017-12-01 06:01:00 UTC` (`1512108060000`) | `2017-12-01 01:05 EST` |
| `CL_1min_2019.csv`: `20190101,1801` | `2019-01-01 18:01 CST` | `2019-01-01 18:00 CST` | `UTC-6` | `2019-01-02 00:00:00 UTC` (`1546387200000`) | `2019-01-01 19:05 EST` |
| `CL_1min_2019.csv`: `20190701,1801` | `2019-07-01 18:01 CDT` | `2019-07-01 18:00 CDT` | `UTC-5` | `2019-07-01 23:00:00 UTC` (`1562022000000`) | `2019-07-01 19:05 EDT` |
| `CL_1min_2019.csv`: `20190915,1803` | `2019-09-15 18:03 CDT` | `2019-09-15 18:02 CDT` | `UTC-5` | `2019-09-15 23:02:00 UTC` (`1568588520000`) | `2019-09-15 19:05 EDT` |

### Missing-Minute Handling

Across the `3,106,933` raw 1-minute rows (`2017-12-01` to `2026-10-13`), grouping by clock-aligned 5-minute buckets `[T, T + 300_000 ms)` produces **`626,558` non-empty 5-minute buckets**:
- `19,144` of those 5-minute buckets have fewer than 5 observed 1-minute bars.
- `6,406` buckets are missing their opening minute (`T + 0`, e.g., Sunday `2019-09-15`, `2020-03-08`, and `2026-03-01` where the session opened at `1803` instead of `1801`).
- `4,778` buckets are missing their closing 5th minute (`T + 240_000 ms`).

Two critical traps exist when feeding 1-minute custom data with missing minutes into Jesse:
1. **Why naive forward-filling before bucket grouping corrupts OHLC**: If missing minutes are forward-filled from the prior bar's close *before* or *at the start* of a 5-minute bucket (for example, filling `1801` and `1802` on Sunday `2019-09-15` with Friday's `1700` close of `54.82` before the actual `1803` open at `61.48`), the Sunday opening 5-minute bar's `open` and `low` become `54.82` instead of `61.48`/`61.26`, erasing the `+6.66` point gap!
2. **Why leaving the 5th minute (`T + 240_000 ms`) missing skips strategy execution in Jesse**: In Jesse's `_timestamp_simulator` (`backtest_mode.py`), a 5-minute route is only added to `updated_routes` (which triggers `strategy._execute()`) when `int(generated[0]) + 300_000 == event['time']`—i.e., when the 5th minute (`:04` open / `:05` close) of that 5-minute bucket is present in the 1-minute stream.

**Our Solution**:
- Within each non-empty clock-aligned 5-minute bucket `[T, T + 300_000 ms)`:
  - We **never** synthesize or back-fill any minute prior to the **first observed 1-minute bar** in that bucket (`ts < first_observed_ts`). Thus the bucket's `open` is strictly the `open` of its first observed 1-minute bar.
  - For any missing minute *after* the first observed bar in that bucket (`first_observed_ts < ts <= T + 240_000 ms`), we insert a flat zero-volume 1-minute candle with `open = high = low = close = previous_observed_in_bucket.close` and `volume = 0` (`18,066` synthetic flat bars added across the 10-year dataset, bringing total imported rows to `3,124,999`).
- This guarantees:
  1. Every 5-minute bar is strictly aligned to `:00, :05, :10, ...` on the clock.
  2. No missing minute can ever alter any 5-minute bar's `open`, `high`, `low`, `close`, or `volume`, nor can it trigger a false 1-minute stop or opening gap.
  3. Every non-empty 5-minute bucket has its closing `:04` (open) / `:05` (close) minute present so Jesse executes the strategy at the exact end of every 5-minute bar.

---

## 4. Ambiguities Found & How They Were Resolved

1. **Raw CSV Timezone Specification (`America/Chicago` in text vs `America/New_York` in file hours)**:
   - **Ambiguity**: The task text states: *"`date` = YYYYMMDD, `time` = HHMM, in US Central time (`America/Chicago`). Each row is stamped with the bar's closing minute: `20190101,1701` is the bar from 17:00 to 17:01 CT."* However, inspecting `CL_1min_2017.csv` through `CL_1min_2026.csv` reveals that the first row of `CL_1min_2019.csv` is actually `20190101,1801`, and the daily 1-hour Globex maintenance break across all 10 `CL` files is `1700`–`1801` (with zero bars between `17:01` and `18:00`), whereas NYMEX CL breaks from `17:00`–`18:00 ET` (`16:00`–`17:00 CT`). Thus the raw `CL_1min_*.csv` files are already stamped in `America/New_York` (`ET`), unlike `ES`/`NQ`/`YM`/`6E`/`ZN` in `c:\NQData\` which break at `1600`–`1701` (`CT`).
   - **Resolution**: Per the instruction *"If something in the text is ambiguous, pick the most literal reading, keep going, and list the ambiguity in your report"*, we followed the literal text specification (`CSV = America/Chicago` converted to UTC and evaluated in `America/New_York`) for the primary Jesse backtest and `trades.csv`. Under this literal conversion, `1801` in the CSV becomes `19:01 ET` (so the Sunday first 5-minute bar closes at `19:05 ET`, the midnight boundary falls at `2300` CSV / `00:00 ET`, and the Monday `10:00 ET` exit falls at `0900` CSV). For completeness, Section 6 below also reports the exact results if the CSV is treated as already in `America/New_York` (`97` trades, `+66.29` / `+66.02` points).

2. **Rule 3 Entry Price ("open of the next 5-minute bar") vs Jesse's `5m` Market Order Execution**:
   - **Ambiguity**: Rule 2 triggers on the first 5-minute bar of Sunday, and Rule 3 says *"Sell short 1 contract at the open of the next 5-minute bar."* In Jesse's 5-minute execution model, `should_short()` and `go_short()` execute at the close timestamp of the signal 5-minute bar (`19:05 ET`, which equals the open timestamp of the next 5-minute bar), and a market order `self.sell = qty, self.price` fills immediately at `self.price` (the signal bar's close, `1805` close) rather than the first trade price of the next minute (`1806` open). Across the 96 qualifying Sundays, `1805.close` and `1806.open` differ by 1–2 ticks on several dates.
   - **Resolution**: We used standard Jesse market order execution (`self.sell = qty, self.price` in `go_short()`) for the Jesse backtest (`+54.96` total points, `+0.5725` avg points). Checking the exact `next_5m_bar.open` (`1806.open`) fill produces the **exact same 96 trades, 62 wins (`64.58%`), and 6 stops**, with total points of **`+54.68` points** (`+0.5696` avg points)—a difference of only `0.28` points across 9 years (see Section 6).

3. **Warm-Up of the 15-Day Daily ATR Prior to `2018-01-01`**:
   - **Ambiguity**: Rule 1 requires 15 scored Monday–Friday TRs before any Sunday signal can fire, and Rule 6 states *"Trade every qualifying Sunday from `2018-01-01` to the end of the data."* In Jesse, `before()` is not called during the `warm_up_candles` phase prior to `start_date`.
   - **Resolution**: On the first call to `before()` at the start of `2018-01-01`, the strategy iterates through `self.candles[:-1]` (the `5,400` warm-up 5-minute bars from December 2017 loaded from `CL_1min_2017.csv`, which contains 20 Monday–Friday dates and yields 19 scored daily TRs) so that all 15 TRs are already available for the first Sundays of January 2018.

4. **Stop Price Tick Rounding (`entry + 0.75 * ATR`)**:
   - **Ambiguity**: Since `ATR` is an average of 15 TRs, `entry + 0.75 * ATR` can have fractional sub-cent decimals (e.g., `.0045`).
   - **Resolution**: We passed the exact floating-point `entry + 0.75 * ATR` to `self.stop_loss`. Testing tick-rounded stops (`round(entry + 0.75 * ATR, 2)`) across the entire 2018–2026 dataset yields the exact same 96 trades, 62 wins, and 6 stops (`+54.94` vs `+54.96` total points).

---

## 5. Anomalies & Observations in the Raw Data (`CL_1min_2017.csv` – `2026.csv`)

1. **Timestamps Are Already in `America/New_York` (`ET`), Not `America/Chicago` (`CT`)**:
   - Every file from `CL_1min_2017.csv` to `CL_1min_2026.csv` has its daily Globex session close at `1700` and reopen at `1801` (with 0 rows between `1701` and `1800` across all `3,106,933` rows). By contrast, `ES`, `NQ`, `YM`, `6E`, `ZN`, and `BTC` in `c:\NQData\` close at `1600` and reopen at `1701` (`America/Chicago`).
2. **Delayed / Non-`1801` Sunday Opens (Including the Historic Sept 15, 2019 Abqaiq Gap)**:
   - Out of 454 Sundays in the dataset, 447 open at `1801`, while 7 Sundays open later:
     - `2019-09-15` (Saudi Aramco Abqaiq attack weekend): `1801` and `1802` are missing; the first bar is `1803`, opening at `61.48` vs Friday's `54.82` close (`+6.66` pt gap; spiked to `63.34` on `1803`, entered at `61.85` at `1805` close, and exited Monday 10:00 at `62.20`).
     - `2020-03-08` (Saudi–Russia price war weekend) and `2026-03-01`: first bar is `1803` (missing `1801`, `1802`). On `2020-03-08`, `1804` is also missing (`1803`, `1805`).
     - `2018-01-21`: first bar is `1820` (`18:15–18:20` 5m bucket).
     - `2018-04-29`: first bar is `1831` (`18:30–18:35` 5m bucket; triggered a valid signal and entered at `19:35 ET`).
     - `2022-07-17`: first bar is `1950` (`19:45–19:50` 5m bucket).
     - `2023-04-23`: first bar is `2215` (`22:10–22:15` 5m bucket).
3. **Partial Coverage in `2017` and `2026`**:
   - `CL_1min_2017.csv` only contains December 2017 (`20171201,0002` through `20171229,1700`, `27,124` rows).
   - `CL_1min_2026.csv` ends on `20261013,2220` (`275,618` rows).
4. **April 20, 2020 Negative WTI Futures Price Not Present in Continuous Series**:
   - On `2020-04-20` (when the expiring May 2020 `CLK20` contract traded at `-37.63`), the continuous contract in `CL_1min_2020.csv` had already rolled to the June 2020 contract (`CLM20`), so the minimum price in `CL_1min_2020.csv` is `+6.50` (on `2020-04-21`).
5. **Cleanliness of OHLCV Rows**:
   - Across all `3,106,933` raw rows, there are `0` duplicate timestamps, `0` out-of-order rows, `0` inverted OHLC bars (`high < max(open, close, low)` or `low > min(open, close, high)`), and `0` negative/zero volume rows.

---

## 6. Sensitivity Summary Across Ambiguity Variants

| Variant | Trades | Wins | Win Rate | Stops | Avg Points | Total Points |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Primary Jesse Run (`CSV = CT -> ET`, Jesse `5m` market fill)** | **96** | **62** | **64.58%** | **6** | **+0.5725** | **+54.96** |
| **2. Next-Bar Open Fill (`CSV = CT -> ET`, `1806.open` fill)** | 96 | 62 | 64.58% | 6 | +0.5696 | +54.68 |
| **3. Direct ET CSV (`CSV = ET`, Jesse `5m` market fill)** | 97 | 65 | 67.01% | 8 | +0.6834 | +66.29 |
| **4. Direct ET CSV (`CSV = ET`, `1806.open` fill)** | 97 | 65 | 67.01% | 8 | +0.6806 | +66.02 |

### Yearly Breakdown for Direct ET CSV Variant (`CSV = America/New_York`)

| Year | Trades | Wins | Win Rate | Stops | Avg Points (Jesse Fill) | Total Points (Jesse Fill) | Total Points (`1806.open` Fill) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2018** | 8 | 6 | 75.00% | 0 | +0.2025 | +1.6200 | +1.6400 |
| **2019** | 10 | 6 | 60.00% | 0 | +0.3520 | +3.5200 | +3.5300 |
| **2020** | 8 | 7 | 87.50% | 0 | +0.4425 | +3.5400 | +3.5300 |
| **2021** | 9 | 5 | 55.56% | 1 | +0.1117 | +1.0055 | +0.9455 |
| **2022** | 7 | 6 | 85.71% | 0 | +2.0086 | +14.0600 | +14.0300 |
| **2023** | 8 | 6 | 75.00% | 1 | +0.4080 | +3.2640 | +3.2640 |
| **2024** | 10 | 8 | 80.00% | 1 | +0.5451 | +5.4505 | +5.4105 |
| **2025** | 14 | 7 | 50.00% | 2 | +0.5632 | +7.8845 | +7.9245 |
| **2026** *(to Oct 13)* | 23 | 14 | 60.87% | 3 | +1.1280 | +25.9445 | +25.7445 |
| **Total (2018–2026)** | **97** | **65** | **67.01%** | **8** | **+0.6834** | **+66.2890** | **+66.0190** |
