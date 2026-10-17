# Task 06 (`NQExpirationOpenShort`) — Phase 2 Improvement Plan (Pre-Registered Before Testing)

## 1. Baseline Strategy & Market Mechanism
- **Baseline Rule (`NQExpirationOpenShort`)**:
  - Instrument: E-mini Nasdaq-100 (`NQ-USD`), 5-minute bars, US Central Time (`CT`).
  - Signal: On every monthly Equity Index Option Expiration Friday (3rd Friday of the month, or the Thursday prior if the 3rd Friday is a market holiday: `2019-04-19`, `2022-04-15`, `2025-04-18`, `2026-06-19`), at the close of the `08:30 CT` (`09:30 ET`) 5-minute bar, sell short 1 contract at market.
  - Stop-Loss: `entry_price + 0.30 * ATR(15)` checked on 1-minute bars.
  - Time Exit: `10:00 CT` (`11:00 ET`).
- **Why It Works**:
  - Standard monthly/quarterly AM-settled equity index options (SPX/NDX) settle against the `08:30 CT` (`09:30 ET`) RTH opening auction print (Special Opening Quotation, SOQ). Into the open, options dealers hold long-delta futures hedges against expiring in-the-money and at-the-money call open interest. Once the `08:30 CT` opening print passes and the SOQ is locked in, dealers mechanically unwind (sell) those long futures hedges during the opening session (`08:30–10:00 CT`).

## 2. Pre-Registered Improvement Variants (Maximum 5 Variants)

All 5 variants are formulated prior to testing, evaluated strictly on the **2018–2022 design period** first, and only the design winner(s) tested once on the **2023–2026 holdout period**.

### Variant 1 (`NQExpShortV1_SkipDeepDownGap`): Skip Overnight Crash / Deep Down-Gap OPEX Mornings (`open_0830 - prev_day_close < -0.50 * ATR(15)`)
- **Exact Change**: Only enter short at `08:30 CT` if `self.close - self.prev_date_last_close >= -0.50 * ATR(15)` (skip OPEX mornings where NQ has already sold off more than `0.50 * ATR(15)` below the prior day's settlement close before `08:30 CT`).
- **Market Mechanism**: The OPEX open short depends on dealers unwinding *long-delta* call hedges after the SOQ. When the market has already gapped down or crashed `> 0.50 * ATR` overnight into the `08:30 CT` open, near-the-money calls have lost their delta and dealers are instead heavily short-delta on in-the-money puts. Post-open unwinding of expiring put hedges requires dealers to *buy* futures (a vanna/charm short-covering rally), turning the `08:30 CT` short into a counter-flow trade.

### Variant 2 (`NQExpShortV2_Target050ATR`): Add Limit Take-Profit at `entry_price - 0.50 * ATR(15)`
- **Exact Change**: Place a resting limit take-profit order at `entry_price - 0.50 * ATR(15)` (`1.67R` vs the `0.30 * ATR` stop), keeping the `0.30 * ATR` stop-loss and `10:00 CT` time exit.
- **Market Mechanism**: Post-SOQ dealer delta-hedge liquidation is a finite, front-loaded inventory flow. Once NQ drops `0.50 * ATR` (half of a full daily range within the first 90 minutes of RTH), the mechanical hedge unwind has cleared and dip-buyers / two-way institutional flows frequently trigger a snap-back before `10:00 CT`. Exiting via a limit order at `-0.50 * ATR` banks the full unwind impulse and eliminates the 1-tick (`$5.00`) market-exit slippage.

### Variant 3 (`NQExpShortV3_Exit0930CT`): Exit at End of Initial Balance (`09:30 CT` instead of `10:00 CT`)
- **Exact Change**: Exit at the close of the `09:30 CT` (`10:30 ET`) 5-minute bar (60 minutes after RTH open) instead of `10:00 CT` (90 minutes after RTH open).
- **Market Mechanism**: Component stocks finish their opening auctions within the first 5–15 minutes after `08:30 CT`, and dealer SOQ hedge unwinds are concentrated in the first 60 minutes of RTH (`08:30–09:30 CT`, the Initial Balance hour). Holding through `09:30–10:00 CT` exposes the trade to post-IB mean reversion after the forced expiration flow has dissipated.

### Variant 4 (`NQExpShortV4_TightStop025ATR`): Tighten Protective Stop from `0.30 * ATR(15)` to `0.25 * ATR(15)`
- **Exact Change**: Reduce the protective stop-loss distance from `0.30 * ATR(15)` to `0.25 * ATR(15)` above `entry_price`.
- **Market Mechanism**: On mornings where dealer hedge unwinding dominates, selling pressure caps upside extension immediately after `08:30 CT`. If NQ rallies `+0.25 * ATR` above the `08:30 CT` open, dealer flow is net bullish (call-buying squeeze or upward pin), and waiting until `+0.30 * ATR` only adds `0.05 * ATR` of dead loss on every stopped trade.

### Variant 5 (`NQExpShortV5_CombinedSkipAndTarget`): Combined Skip Deep Down-Gap (`>= -0.50 * ATR`) + Limit Target (`-0.50 * ATR`)
- **Exact Change**: Combine Variant 1 and Variant 2: enter short at `08:30 CT` only when `self.close - self.prev_date_last_close >= -0.50 * ATR(15)`, with a limit take-profit at `entry_price - 0.50 * ATR(15)`, stop-loss at `entry_price + 0.30 * ATR(15)`, and time exit at `10:00 CT`.
- **Market Mechanism**: Filters out deeply oversold overnight put-unwind squeezes while banking `-0.50 * ATR` post-SOQ unwind waves without exit slippage.

## 3. Evaluation Protocol
- **Costs Applied**: `$7.25` per side (`$14.50` round-trip in `compare.py`; `$7.25` round-trip in `S_RANK_PROGRAM.md` — both reported) + `1 tick` (`0.25 pts = $5.00`) slippage per market or stop fill (`0` slippage on limit target fills).
- **Split**:
  - **Design Period**: `2018-01-02` to `2022-12-31` (select winner here only).
  - **Holdout Period**: `2023-01-01` to `2026-10-09` (run once on selected winner).
- **Promotion Gate**: Must beat baseline in **both** `2018–2022` and `2023–2026` on **both** Net $ per contract and Max Drawdown, flat by `15:59 CT`, max 1 contract.
