# Task 07 (`NQLateDayFlow`) — Phase 2 Improvement Plan (Pre-Registered Before Testing)

## 1. Baseline Strategy & Market Mechanism
- **Baseline Rule (`NQLateDayFlow`)**:
  - Instrument: E-mini Nasdaq-100 (`NQ-USD`), 5-minute bars, US Central Time (`CT`).
  - Signal: On every non-early-close weekday at the close of the `14:00 CT` (`15:00 ET`) 5-minute bar, compute `move = close_1400 - session_open_0830`. If `abs(move) >= 0.40 * ATR(15)`, enter 1 contract at market in the direction of `move` (`move > 0 -> long`, `move < 0 -> short`).
  - Stop-Loss: `0.25 * ATR(15)` from entry price, checked on 1-minute bars.
  - Time Exit: `14:30 CT` (`15:30 ET`, 30-minute hold).
- **Why It Works**:
  - Entering the final hour of US cash equity trading (`14:00 CT` / `15:00 ET`), 0DTE option dealers hedging gamma exposure, leveraged ETFs rebalancing daily exposure, and intraday margin/VWAP algorithms are forced to trade in the direction of a large intraday trend (`abs(move) >= 0.40 * ATR`), driving continuation from `14:00` to `14:30 CT` before late-session MOC imbalance noise begins at `14:50 CT`.

## 2. Pre-Registered Improvement Variants (Maximum 5 Variants)

All 5 variants are formulated prior to testing, evaluated strictly on the **2018–2022 design period** first, and only the design winner(s) tested once on the **2023–2026 holdout period**.

### Variant 1 (`NQLateDayV1_HigherMove050ATR`): Raise Session Move Threshold from `0.40 * ATR(15)` to `0.50 * ATR(15)`
- **Exact Change**: Require `abs(move) >= 0.50 * ATR(15)` at `14:00 CT` instead of `0.40 * ATR(15)`.
- **Market Mechanism**: Forced late-day dealer delta/gamma hedging and leveraged ETF rebalancing scale non-linearly with the day's displacement from the `08:30 CT` cash open. Days with `0.40 <= abs(move) < 0.50 * ATR` represent modest drift where forced institutional chasing is weak and transaction costs (`$24.50` round-trip) erode expectancy; requiring `>= 0.50 * ATR` restricts entries to genuine trend days.

### Variant 2 (`NQLateDayV2_CapExhaustion150ATR`): Skip Extreme Exhaustion Days (`abs(move) > 1.50 * ATR(15)`)
- **Exact Change**: Require `0.40 * ATR(15) <= abs(move) <= 1.50 * ATR(15)` at `14:00 CT`.
- **Market Mechanism**: When NQ has already traveled more than `1.50 * ATR(15)` from the `08:30 CT` cash open by `14:00 CT`, the session is in a 95th-percentile extension where intraday trend traders and 0DTE option holders take profits ahead of the close, causing sharp `14:00–14:30 CT` counter-trend snap-backs.

### Variant 3 (`NQLateDayV3_BarConfirm`): Require `14:00 CT` Signal Bar (`13:55–14:00 CT`) to Close in Trend Direction
- **Exact Change**: In addition to `abs(move) >= 0.40 * ATR(15)`, require `b_close > b_open` on the `14:00 CT` bar for long entries and `b_close < b_open` for short entries.
- **Market Mechanism**: Institutional late-day TWAP/rebalancing flows begin executing into the `14:00 CT` clock boundary. If the `13:55–14:00 CT` bar closes against the session trend, active profit-taking is already overpowering trend continuation at the entry point.

### Variant 4 (`NQLateDayV4_Target025ATR`): Add Limit Take-Profit at `0.25 * ATR(15)` (`1.0R`)
- **Exact Change**: Place a resting limit take-profit order at `entry_price + 0.25 * ATR(15)` for longs (`entry_price - 0.25 * ATR(15)` for shorts), keeping the `0.25 * ATR` stop and `14:30 CT` time exit.
- **Market Mechanism**: Because the trade window is only 30 minutes (`14:00–14:30 CT`) after the market has already moved `>= 0.40 * ATR`, an additional `0.25 * ATR` burst captures the primary `14:00 CT` rebalancing impulse while avoiding late-window giveback and eliminating the 1-tick (`$5.00`) market-exit slippage.

### Variant 5 (`NQLateDayV5_Move050AndCap150`): Combined Sweet-Spot Trend Window (`0.50 * ATR(15) <= abs(move) <= 1.50 * ATR(15)`)
- **Exact Change**: Combine Variant 1 and Variant 2: enter at `14:00 CT` only when `0.50 * ATR(15) <= abs(move) <= 1.50 * ATR(15)`.
- **Market Mechanism**: Captures days with sufficient displacement (`>= 0.50 ATR`) to force dealer/ETF late-day chasing while avoiding blown-out exhaustion days (`> 1.50 ATR`) prone to pre-close profit-taking reversals.

## 3. Evaluation Protocol
- **Costs Applied**: `$7.25` per side (`$14.50` round-trip in `compare.py`; `$7.25` round-trip in `S_RANK_PROGRAM.md` — both reported) + `1 tick` (`0.25 pts = $5.00`) slippage per market or stop fill (`0` slippage on limit target fills).
- **Split**:
  - **Design Period**: `2018-01-02` to `2022-12-31` (select winner here only).
  - **Holdout Period**: `2023-01-01` to `2026-10-09` (run once on selected winner).
- **Promotion Gate**: Must beat baseline in **both** `2018–2022` and `2023–2026` on **both** Net $ per contract and Max Drawdown, flat by `15:59 CT`, max 1 contract.
