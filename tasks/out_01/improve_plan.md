# Task 01 (`CLSundayFade`) — Phase 2 Improvement Plan (Pre-Registered Before Testing)

## 1. Baseline Strategy & Market Mechanism
- **Baseline Rule (`CLSundayFade`)**:
  - Instrument: WTI Crude Oil (`CL-USD`), 5-minute bars, Eastern Time (`ET`).
  - Signal: On Sunday's first 5-minute bar (`18:05 ET` close), if `gap = open - prev_close >= 0.10 * ATR(15)`, sell short 1 contract at the next bar's open.
  - Stop-Loss: `entry_price + 0.75 * ATR(15)` checked on 1-minute bars.
  - Time Exit: Monday `10:00 ET` (first 5-minute bar stamped `>= 10:00 ET`).
- **Why It Works**:
  - Weekend geopolitical/OPEC headlines create an upward risk-premium markup in thin Sunday-evening Globex liquidity (`18:00 ET`). As Asian, London, and NY commercial hedgers enter the market overnight, that weekend premium is sold into and mean-reverts into Monday morning.

## 2. Pre-Registered Improvement Variants (Maximum 5 Variants)

All variants are formulated prior to testing, designed to be evaluated strictly on the **2018–2022 design period** first, and only the winner(s) tested once on the **2023–2026 holdout period**.

### Variant 1 (`CLSundayFadeV1_GapFillTarget`): Limit Take-Profit at Friday's Settlement Close (`prev_5m_close`)
- **Exact Change**: Add a limit take-profit order at `prev_5m_close` (100% fill of the Sunday weekend gap, i.e., `target_price = prev_5m_close`), while keeping the `0.75 * ATR` stop and Monday `10:00 ET` time exit.
- **Market Mechanism**: The entire economic premise of the trade is that the Sunday opening gap is an overreaction relative to Friday's closing equilibrium price. Once price reverts all the way back to Friday's close (`prev_5m_close`), the weekend premium has been 100% unwound; Friday's close frequently acts as technical and commercial support where dip-buyers step in. Exiting via a limit order at Friday's close locks in the full gap reversion and eliminates the 1-tick (`$10.00`) market-order exit slippage.

### Variant 2 (`CLSundayFadeV2_CapShockGap`): Skip Extreme Physical Supply-Shock Gaps (`gap > 1.00 * ATR`)
- **Exact Change**: Require `0.10 * ATR <= gap <= 1.00 * ATR` (skip Sundays where the opening gap exceeds `1.00 * ATR`).
- **Market Mechanism**: Routine weekend gaps (`0.10–1.00 ATR`) are liquidity-driven markups that mean-revert. Gaps exceeding a full daily ATR (`> 1.00 ATR`, e.g., major infrastructure attacks or war outbreaks) represent genuine physical supply shocks where shorts face severe tail risk and runaway continuation.

### Variant 3 (`CLSundayFadeV3_NYMEXOpenExit`): Exit at NYMEX RTH Open (`09:00 ET` instead of `10:00 ET`)
- **Exact Change**: Exit at the close of the first Monday 5-minute bar stamped `>= 09:00 ET` instead of `10:00 ET`.
- **Market Mechanism**: The NYMEX WTI crude oil RTH session opens at `09:00 ET` (`08:00 CT`). By `09:00 ET`, London and NY pre-market commercial flows have completed the overnight gap unwind, whereas the `09:00–10:00 ET` hour overlaps with the `09:30 ET` US equity cash open, introducing cross-asset risk-on volatility unrelated to the Sunday gap fade.

### Variant 4 (`CLSundayFadeV4_GapTargetAndCap`): Combined Gap-Fill Target (`prev_5m_close`) + Shock-Gap Cap (`<= 1.00 * ATR`)
- **Exact Change**: Combine Variant 1 and Variant 2: enter short when `0.10 * ATR <= gap <= 1.00 * ATR`, with a limit take-profit at `prev_5m_close`, a stop at `entry + 0.75 * ATR`, and a time exit at Monday `10:00 ET`.
- **Market Mechanism**: Captures the full weekend gap unwind at Friday's close without exit slippage while filtering out extreme >1 ATR physical supply shocks.

### Variant 5 (`CLSundayFadeV5_TightStop050ATR`): Tighten Protective Stop from `0.75 * ATR(15)` to `0.50 * ATR(15)`
- **Exact Change**: Reduce the protective stop-loss distance from `0.75 * ATR(15)` to `0.50 * ATR(15)` above `entry_price`, keeping the entry rule and Monday `10:00 ET` exit unchanged.
- **Market Mechanism**: Because the entry already occurs after an upward Sunday gap (`>= 0.10 * ATR` above Friday's close), an additional `+0.50 * ATR` adverse extension above the Sunday open means price is trading `0.60+ * ATR` above Friday's settlement — signaling genuine institutional demand / physical supply repricing rather than a thin Sunday-evening markup. Cutting adverse continuation at `+0.50 * ATR` instead of waiting for `+0.75 * ATR` truncates left-tail losses on trend Mondays without choking normal overnight oscillations.

## 3. Evaluation Protocol
- **Costs Applied**: `$7.25` round-trip commission (`$14.50` if counted per side; both reported) + `1 tick` (`0.01 pts = $10.00`) slippage per market or stop fill (`0` slippage on limit target fills).
- **Split**:
  - **Design Period**: `2018-01-01` to `2022-12-31` (select winner here only).
  - **Holdout Period**: `2023-01-01` to `2026-10-13` (run once on selected winner).
- **Promotion Gate**: Must beat baseline in **both** `2018–2022` and `2023–2026` on **both** Net $ per contract and Max Drawdown, flat by `15:59 CT`, max 1 contract.
