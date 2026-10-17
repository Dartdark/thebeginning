# Task 08 (`NQNFPFade`) — Phase 2 Improvement Plan (Pre-Registered Before Testing)

## 1. Baseline Strategy & Market Mechanism
- **Baseline Rule (`NQNFPFade`)**:
  - Instrument: E-mini Nasdaq-100 (`NQ-USD`), 5-minute bars, US Central Time (`CT`).
  - Signal: On NFP Fridays (`weekday == Friday` and `day <= 10`), record `reference_price = close` of the `07:30 CT` (`08:30 ET`) bar. If the `07:35 CT` release bar's range exceeds `3.0 * median(prior 20 weekday 07:35 ranges)`, evaluate `reaction = close_0745 - reference_price` at `07:45 CT`. Fade the reaction (`reaction > 0 -> short`, `reaction < 0 -> long`).
  - Stop-Loss: `0.50 * ATR(15)` from entry price, checked on 1-minute bars.
  - Time Exit: `09:00 CT` (`10:00 ET`).
- **Why It Works**:
  - The `07:30 CT` (`08:30 ET`) Non-Farm Payrolls print triggers algorithmic headline sweeping across thin pre-market Globex order books (`07:30–07:45 CT`). Once the initial 15-minute liquidity vacuum clears, two-way institutional desk pricing and pre-RTH arbitrage mean-revert the exaggerated initial spike into the morning session.

## 2. Pre-Registered Improvement Variants (Maximum 5 Variants)

All 5 variants are formulated prior to testing, evaluated strictly on the **2018–2022 design period** first, and only the design winner(s) tested once on the **2023–2026 holdout period**.

### Variant 1 (`NQNFPFadeV1_MinReaction010ATR`): Require Minimum Un-Reverted Dislocation at `07:45 CT` (`abs(reaction) >= 0.10 * ATR(15)`)
- **Exact Change**: Only enter at `07:45 CT` if `abs(close_0745 - reference_price) >= 0.10 * ATR(15)`.
- **Market Mechanism**: The fade edge depends on an active dislocation still existing at `07:45 CT` (15 minutes after the `07:30 CT` release). When `abs(reaction) < 0.10 * ATR`, the `07:35 CT` spike has already mean-reverted back to `reference_price` before `07:45 CT`; entering anyway fades a move that has already completed.

### Variant 2 (`NQNFPFadeV2_ExitCashOpen0830CT`): Exit at US Equity Cash Open (`08:30 CT` instead of `09:00 CT`)
- **Exact Change**: Liquidate at the close of the `08:30 CT` (`09:30 ET`) 5-minute bar instead of `09:00 CT` (`10:00 ET`). Also prevents holding across the Good Friday `08:15 CT` early Globex close when `08:30 CT` is reached.
- **Market Mechanism**: Pre-market NFP mean reversion (`07:45–08:30 CT`) is driven by futures market-makers re-anchoring prices ahead of the `08:30 CT` (`09:30 ET`) NYSE/Nasdaq opening auction. Once the cash equity market opens at `08:30 CT`, real-money institutional equity orders enter and frequently resume the macro direction of the NFP surprise between `08:30` and `09:00 CT`.

### Variant 3 (`NQNFPFadeV3_RefPriceTarget`): Add Limit Take-Profit at Pre-Release Equilibrium (`reference_price`)
- **Exact Change**: Require `abs(reaction) >= 0.05 * ATR(15)` and place a resting limit take-profit order at `reference_price` (`close_0730`), keeping the `0.50 * ATR(15)` stop and `09:00 CT` time exit.
- **Market Mechanism**: `reference_price` (`07:30 CT` close) is the exact pre-announcement equilibrium level. Once the post-NFP spike retraces 100% back to `reference_price`, the liquidity overreaction is fully unwound; taking profit via a limit order at `reference_price` captures the complete retracement and eliminates the 1-tick (`$5.00`) market-exit slippage.

### Variant 4 (`NQNFPFadeV4_TightStop030ATR`): Tighten Protective Stop from `0.50 * ATR(15)` to `0.30 * ATR(15)`
- **Exact Change**: Reduce the protective stop-loss distance from `0.50 * ATR(15)` to `0.30 * ATR(15)` from `entry_price`.
- **Market Mechanism**: Because entry waits until `07:45 CT` (15 minutes post-release), an additional `0.30 * ATR` adverse expansion beyond the `07:45 CT` price indicates genuine macro repricing (trend continuation) rather than a fading liquidity spike; cutting at `0.30 * ATR` prevents deep losses on runaway NFP trend days.

### Variant 5 (`NQNFPFadeV5_MinReactionAndTightStop`): Combined Minimum Reaction (`>= 0.10 * ATR`) + Tight Stop (`0.30 * ATR`)
- **Exact Change**: Combine Variant 1 and Variant 4: require `abs(close_0745 - reference_price) >= 0.10 * ATR(15)` at `07:45 CT` and set the protective stop at `0.30 * ATR(15)`.
- **Market Mechanism**: Filters out NFP mornings where the spike already reverted prior to `07:45 CT` while cutting genuine macro trend-continuation days at `0.30 * ATR`.

## 3. Evaluation Protocol
- **Costs Applied**: `$7.25` per side (`$14.50` round-trip in `compare.py`; `$7.25` round-trip in `S_RANK_PROGRAM.md` — both reported) + `1 tick` (`0.25 pts = $5.00`) slippage per market or stop fill (`0` slippage on limit target fills).
- **Split**:
  - **Design Period**: `2018-01-02` to `2022-12-31` (select winner here only).
  - **Holdout Period**: `2023-01-01` to `2026-10-09` (run once on selected winner).
- **Promotion Gate**: Must beat baseline in **both** `2018–2022` and `2023–2026` on **both** Net $ per contract and Max Drawdown, flat by `15:59 CT`, max 1 contract.
