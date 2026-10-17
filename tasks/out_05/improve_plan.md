# Task 05 (`NQMondayLong`) — Phase 2 Improvement Plan (Pre-Registered Before Testing)

## 1. Baseline Strategy & Market Mechanism
- **Baseline Rule (`NQMondayLong`)**:
  - Instrument: E-mini Nasdaq-100 (`NQ-USD`), 5-minute bars, US Central Time (`CT`).
  - Signal: Every non-early-close Monday at the close of the `08:30 CT` (`09:30 ET`) 5-minute bar, buy 1 contract at market.
  - Stop-Loss: `entry_price - 0.50 * ATR(15)` checked on 1-minute bars.
  - Time Exit: `15:00 CT` (`16:00 ET` RTH close).
- **Why It Works**:
  - Systematic weekly retirement/passive fund inflows, weekend hedge unwinds, and 3-day weekend short-put theta decay create a structural net-buying drift during the Monday US cash equity session (`08:30–15:00 CT`).

## 2. Pre-Registered Improvement Variants (Maximum 5 Variants)

All 5 variants are formulated prior to testing, evaluated strictly on the **2018–2022 design period** first, and only the design winner(s) tested once on the **2023–2026 holdout period**.

### Variant 1 (`NQMondayLongV1_SkipWeekendCrash`): Skip Mondays with Deep Bearish Overnight/Weekend Gaps (`close_0830 - prev_day_close < -0.25 * ATR(15)`)
- **Exact Change**: Only enter long at `08:30 CT` if `self.close - self.prev_date_last_close >= -0.25 * ATR(15)` (skip Mondays where NQ is down more than `0.25 * ATR(15)` from Friday's close at the `08:30 CT` cash open).
- **Market Mechanism**: Routine Monday passive inflows only dominate in stable or constructive weekend regimes. When NQ gaps down `> 0.25 * ATR` over the weekend into the Monday cash open, weekend macro shocks, margin calls, and dealer short-gamma hedging trigger institutional de-risking at `08:30 CT` that overwhelms passive inflows.

### Variant 2 (`NQMondayLongV2_SkipExhaustedUpGap`): Skip Overextended Overnight Up-Gaps (`close_0830 - prev_day_close > 0.50 * ATR(15)`)
- **Exact Change**: Only enter long at `08:30 CT` if `self.close - self.prev_date_last_close <= 0.50 * ATR(15)`.
- **Market Mechanism**: When NQ has already rallied more than `0.50 * ATR(15)` during thin Sunday/London Globex trading prior to `08:30 CT`, half of a typical daily range has already been realized overnight; buying the `08:30 CT` open buys directly into overnight profit-taking and gap-fill reversion.

### Variant 3 (`NQMondayLongV3_GoldilocksGapFilter`): Combined Overnight Regime Window (`-0.25 * ATR(15) <= gap <= +0.50 * ATR(15)`)
- **Exact Change**: Combine Variant 1 and Variant 2: enter long at `08:30 CT` only when `-0.25 * ATR(15) <= self.close - self.prev_date_last_close <= 0.50 * ATR(15)`.
- **Market Mechanism**: Isolates Mondays where neither weekend panic liquidation (`< -0.25 ATR`) nor overnight gap exhaustion (`> +0.50 ATR`) distorts the RTH cash session.

### Variant 4 (`NQMondayLongV4_Target100ATR`): Add Limit Take-Profit at `entry_price + 1.00 * ATR(15)` (`2.0R`)
- **Exact Change**: Place a resting limit take-profit order at `entry_price + 1.00 * ATR(15)` while retaining the `0.50 * ATR(15)` stop-loss and `15:00 CT` time exit.
- **Market Mechanism**: Once NQ expands by a full `1.00 * ATR(15)` above the `08:30 CT` cash open, the expected daily range is exhausted and late-day rebalancing can give back open profits. Exiting via a limit order at `+1.00 * ATR` locks in a `2.0R` win and eliminates the 1-tick (`$5.00`) market-exit slippage.

### Variant 5 (`NQMondayLongV5_TightStop035ATR`): Tighten Protective Stop from `0.50 * ATR(15)` to `0.35 * ATR(15)`
- **Exact Change**: Reduce the protective stop-loss distance from `0.50 * ATR(15)` to `0.35 * ATR(15)` below `entry_price`.
- **Market Mechanism**: On genuine institutional accumulation Mondays, opening-range dip buyers defend the `08:30 CT` opening print; a drop of `0.35 * ATR` below the cash open signals a failed opening auction and seller control, saving `0.15 * ATR` of loss on trend-down Mondays.

## 3. Evaluation Protocol
- **Costs Applied**: `$7.25` per side (`$14.50` round-trip in `compare.py`; `$7.25` round-trip in `S_RANK_PROGRAM.md` — both reported) + `1 tick` (`0.25 pts = $5.00`) slippage per market or stop fill (`0` slippage on limit target fills).
- **Split**:
  - **Design Period**: `2018-01-02` to `2022-12-31` (select winner here only).
  - **Holdout Period**: `2023-01-01` to `2026-10-09` (run once on selected winner).
- **Promotion Gate**: Must beat baseline in **both** `2018–2022` and `2023–2026` on **both** Net $ per contract and Max Drawdown, flat by `15:59 CT`, max 1 contract.
