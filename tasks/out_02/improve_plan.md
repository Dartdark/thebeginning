# Task 02 (`NQVaultBreak`) — Phase 2 Improvement Plan (Pre-Registered Before Testing)

## 1. Baseline Strategy & Market Mechanism
- **Baseline Rule (`NQVaultBreak`)**:
  - Instrument: E-mini Nasdaq-100 (`NQ-USD`), 30-minute bars, US Central Time (`CT`).
  - Signal: Between `10:00 CT` and `14:30 CT` (`11:00 CT` on early-close days), if `close > session_open_0000 + 0.30 * ATR(15)` (`noise_level`) and `close > VWAP`, buy 1 contract at market (up to 3 trades per day).
  - Exit: Limit take-profit at `entry_price + 40.0 pts`, stop-loss at `entry_price - 75.0 pts`, or time flatten at `14:30 CT` (`11:30 CT` on early-close days).
- **Why It Works**:
  - When NQ clears the upper volatility noise boundary (`session_open + 0.30 * ATR(15)`) after `10:00 CT` (`11:00 ET`, post-Initial-Balance) while trading above cumulative session `VWAP`, institutional trend-following and dealer gamma-hedging flows drive intraday upward continuation.

## 2. Pre-Registered Improvement Variants (Maximum 5 Variants)

All 5 variants are formulated prior to testing, evaluated strictly on the **2018–2022 design period** first, and only the design winner(s) tested once on the **2023–2026 holdout period**.

### Variant 1 (`NQVaultBreakV1_OneTradePerDay`): Cap Entries at 1 Trade Per Day (`trades_taken_today < 1` instead of `< 3`)
- **Exact Change**: Allow at most 1 trade per calendar date (`self.trades_taken_today < 1` instead of `< 3`).
- **Market Mechanism**: The primary institutional breakout occurs on the first post-`10:00 CT` expansion above `noise_level` and `VWAP`. Once the first trade of the day has either banked its target (exhausting the initial impulse) or hit its stop (indicating a failed breakout reversal), 2nd and 3rd re-entries chase late-day extensions or re-enter broken trend days while multiplying transaction cost drag.

### Variant 2 (`NQVaultBreakV2_LastEntry1230CT`): Restrict New Entries to `[10:00 CT, 12:30 CT]` (`bar_time <= (12, 30)`)
- **Exact Change**: On regular sessions, only allow new entries on 30-minute bars stamped `10:00` through `12:30 CT` (instead of through `14:00 CT`), while keeping the `14:30 CT` flatten time.
- **Market Mechanism**: Entries taken at `13:00`, `13:30`, or `14:00 CT` have only 30–90 minutes before the mandatory `14:30 CT` flatten, giving insufficient time to reach the target while remaining fully exposed to intrabar stop-outs.

### Variant 3 (`NQVaultBreakV3_ATRTargetAndStop`): Volatility-Scaled Target (`0.20 * ATR(15)`) and Stop (`0.35 * ATR(15)`)
- **Exact Change**: Replace fixed `+40.0 pt` target and `-75.0 pt` stop with `entry_price + 0.20 * ATR(15)` target and `entry_price - 0.35 * ATR(15)` stop.
- **Market Mechanism**: As NQ rose from `6,500` in 2018 to `21,000+` in 2025–2026, fixed `40 / 75 pt` brackets went from wide (`~0.40 / 0.75 ATR` in 2018–2019) to ultra-tight noise (`~0.12 / 0.22 ATR` in 2022–2026). Scaling the target (`0.20 * ATR`) and stop (`0.35 * ATR`) to `ATR(15)` preserves a consistent volatility-adjusted payoff profile across all price levels.

### Variant 4 (`NQVaultBreakV4_BullishBreakoutBar`): Require Bullish 30-Minute Signal Candle (`b_close > b_open`)
- **Exact Change**: Require `b_close > b_open` on the 30-minute signal bar in addition to `b_close > noise_level` and `b_close > current_vwap`.
- **Market Mechanism**: On an already-extended day, a bearish 30-minute pullback candle (`b_close < b_open`) can still close above `noise_level` and `VWAP`. Requiring `b_close > b_open` ensures entry is triggered by positive 30-minute order-flow expansion rather than a red retrace bar.

### Variant 5 (`NQVaultBreakV5_OneTradeAndATRBrackets`): Combined 1 Trade/Day (`< 1`) + Volatility-Scaled Brackets (`+0.20 * ATR` Target / `-0.35 * ATR` Stop)
- **Exact Change**: Combine Variant 1 and Variant 3: allow at most 1 trade per day (`self.trades_taken_today < 1`) with limit take-profit at `entry_price + 0.20 * ATR(15)` and stop-loss at `entry_price - 0.35 * ATR(15)`.
- **Market Mechanism**: Isolates the single best post-`10:00 CT` breakout per day with regime-invariant ATR brackets, slashing transaction costs and avoiding midday re-entry chop.

## 3. Evaluation Protocol
- **Costs Applied**: `$7.25` per side (`$14.50` round-trip in `compare.py`; `$7.25` round-trip in `S_RANK_PROGRAM.md` — both reported) + `1 tick` (`0.25 pts = $5.00`) slippage per market or stop fill (`0` slippage on limit target fills).
- **Split**:
  - **Design Period**: `2018-01-02` to `2022-12-31` (select winner here only).
  - **Holdout Period**: `2023-01-01` to `2026-10-09` (run once on selected winner).
- **Promotion Gate**: Must beat baseline in **both** `2018–2022` and `2023–2026` on **both** Net $ per contract and Max Drawdown, flat by `15:59 CT`, max 1 contract.
