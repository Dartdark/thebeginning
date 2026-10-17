# Task 03 (`NQOvernightBiasADX30`) — Phase 2 Improvement Plan (Pre-Registered Before Testing)

## 1. Baseline Strategy & Market Mechanism
- **Baseline Rule (`NQOvernightBiasADX30`)**:
  - Instrument: E-mini Nasdaq-100 (`NQ-USD`), 15-minute bars, US Central Time (`CT`).
  - Signal: Track the overnight range (`23:15 CT` to `08:30 CT`). At `08:45 CT` (close of the `08:30–08:45 CT` Opening Range bar), compute `pos = (open_0830 - on_low) / (on_high - on_low)`. Set `bias = +1` if `pos >= 0.6667`, `bias = -1` if `pos <= 0.3333`. Between `08:45 CT` and `14:00 CT` (`11:00 CT` on early-close days), if 15m `ADX(14) > 30.0`, enter on a break of `or_high` (`bias == +1`) or `or_low` (`bias == -1`), max 1 trade/day.
  - Exit: Stop-loss at `0.25 * ATR(15)` (`1.0R`), take-profit at `0.75 * ATR(15)` (`3.0R`), or time flatten at `14:30 CT` (`11:30 CT` on early-close days).
- **Why It Works**:
  - When the RTH cash open (`08:30 CT`) prints in the upper or lower third of the overnight Globex range and breaks the 15-minute Opening Range (`08:30–08:45 CT`) under strong trend strength (`ADX(14) > 30`), trapped overnight counter-trend inventory is forced to cover as RTH institutional volume enters.

## 2. Pre-Registered Improvement Variants (Maximum 5 Variants)

All 5 variants are formulated prior to testing, evaluated strictly on the **2018–2022 design period** first, and only the design winner(s) tested once on the **2023–2026 holdout period**.

### Variant 1 (`NQONBiasADX30V1_MorningWindow1130CT`): Restrict New Entries to the Morning Session (`08:45–11:30 CT`)
- **Exact Change**: On regular sessions, only allow new entries on 15-minute bars stamped `08:45` through `11:30 CT` (instead of `< 14:00 CT`), keeping the `14:30 CT` exit.
- **Market Mechanism**: The overnight range bias and `08:30–08:45 CT` Opening Range are morning auction anchors. Breakouts that fail to trigger until midday/afternoon (`11:45–13:45 CT`) act on stale overnight information and have insufficient time before `14:30 CT` to reach a `0.75 * ATR` (`3.0R`) target while still bearing full `0.25 * ATR` stop risk.

### Variant 2 (`NQONBiasADX30V2_CapORSize035ATR`): Skip Blown-Out Opening Ranges (`or_high - or_low > 0.35 * ATR(15)`)
- **Exact Change**: Only allow entries when the 15-minute Opening Range width satisfies `or_high - or_low <= 0.35 * ATR(15)`.
- **Market Mechanism**: When the first 15 minutes of RTH (`08:30–08:45 CT`) already span more than `35%` of a full daily ATR, the initial opening impulse has already expanded; buying above `or_high` or selling below `or_low` chases an exhausted opening candle prone to mean reversion.

### Variant 3 (`NQONBiasADX30V3_StrictBias75_25`): Require Top/Bottom Quartile Overnight Positioning (`pos >= 0.75` or `pos <= 0.25`)
- **Exact Change**: Set `bias = +1` only when `pos >= 0.75` and `bias = -1` only when `pos <= 0.25` (instead of `0.6667` / `0.3333`).
- **Market Mechanism**: Overnight inventory pressure is strongest when the cash open prints in the extreme top or bottom 25% of the overnight range, where offside overnight participants have no buffer before stops are triggered.

### Variant 4 (`NQONBiasADX30V4_Target2R`): Set Limit Take-Profit to `2.0R` (`0.50 * ATR(15)`) Instead of `3.0R` (`0.75 * ATR(15)`)
- **Exact Change**: Set `target_dist = 2.0 * stop_dist` (`0.50 * ATR(15)`) instead of `3.0 * stop_dist` (`0.75 * ATR(15)`).
- **Market Mechanism**: Because entry already occurs outside the `08:30–08:45 CT` Opening Range, a further `0.50 * ATR` extension represents a full intraday trend wave. Taking profit on a resting limit order at `2.0R` banks trends that stall before `0.75 * ATR` and eliminates the 1-tick (`$5.00`) time-exit slippage.

### Variant 5 (`NQONBiasADX30V5_MorningAndCapOR`): Combined Morning Entry Window (`<= 11:30 CT`) + Opening Range Cap (`<= 0.35 * ATR(15)`)
- **Exact Change**: Combine Variant 1 and Variant 2: allow entries only up to `11:30 CT` on days where `or_high - or_low <= 0.35 * ATR(15)`.
- **Market Mechanism**: Ensures the Opening Range breakout occurs while the overnight bias is fresh (morning session) and before the opening range itself is overextended.

## 3. Evaluation Protocol
- **Costs Applied**: `$7.25` per side (`$14.50` round-trip in `compare.py`; `$7.25` round-trip in `S_RANK_PROGRAM.md` — both reported) + `1 tick` (`0.25 pts = $5.00`) slippage per market or stop fill (`0` slippage on limit target fills).
- **Split**:
  - **Design Period**: `2018-01-02` to `2022-12-31` (select winner here only).
  - **Holdout Period**: `2023-01-01` to `2026-10-09` (run once on selected winner).
- **Promotion Gate**: Must beat baseline in **both** `2018–2022` and `2023–2026` on **both** Net $ per contract and Max Drawdown, flat by `15:59 CT`, max 1 contract.
