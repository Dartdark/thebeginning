# Task 04 (`NQOvernightBiasML`) — Phase 2 Improvement Plan (Pre-Registered Before Testing)

## 1. Baseline Strategy & Market Mechanism
- **Baseline Rule (`NQOvernightBiasML`)**:
  - Instrument: E-mini Nasdaq-100 (`NQ-USD`), 15-minute bars, US Central Time (`CT`).
  - Signal: Same Overnight Bias (`pos >= 0.6667` long, `pos <= 0.3333` short) and `08:30–08:45 CT` Opening Range breakout structure as Task 03, gated by `ADX(14) > 20.0` and the linear daily macro/volatility score (`today_score >= 0.03` for longs, `today_score >= 0.0` for shorts).
  - Exit: Stop-loss at `0.30 * ATR(15)` (`1.0R`), take-profit at `0.90 * ATR(15)` (`3.0R`), or time flatten at `14:30 CT` (`11:30 CT` on early-close days).
- **Why It Works**:
  - Combines the intraday auction mechanism of an Opening Range breakout aligned with Overnight Range positioning with a multi-horizon daily regime score (1d/5d/20d returns, RTH body, ATR ratio, 50d distance, realized vol ratio, and calendar effects) that predicts whether intraday breakouts will follow through.

## 2. Pre-Registered Improvement Variants (Maximum 5 Variants)

All 5 variants are formulated prior to testing, evaluated strictly on the **2018–2022 design period** first, and only the design winner(s) tested once on the **2023–2026 holdout period**.

### Variant 1 (`NQONBiasMLV1_MorningWindow1130CT`): Restrict New Entries to the Morning Session (`08:45–11:30 CT`)
- **Exact Change**: On regular sessions, only allow new entries on 15-minute bars stamped `08:45` through `11:30 CT` (instead of `< 14:00 CT`), keeping the `14:30 CT` exit.
- **Market Mechanism**: Both the overnight range bias (`23:15–08:30 CT`) and the prior-close daily ML regime score are pre-open state variables whose predictive power decays after the morning institutional session (`08:30–11:30 CT`). Afternoon breakouts (`11:45–13:45 CT`) have insufficient time to reach a `0.90 * ATR` target before `14:30 CT`.

### Variant 2 (`NQONBiasMLV2_SymmetricScore003`): Require High-Conviction Regime Score (`today_score >= 0.03`) for Both Longs and Shorts
- **Exact Change**: Require `today_score >= 0.03` for short entries as well as long entries (instead of `today_score >= 0.0` for shorts).
- **Market Mechanism**: The baseline requires `today_score >= 0.03` on longs but accepts marginal `0.00 <= today_score < 0.03` readings on shorts. Because equity index futures carry a positive secular drift, short breakouts on near-zero regime-score days face adverse upward drift and higher false-breakdown rates.

### Variant 3 (`NQONBiasMLV3_CapORSize035ATR`): Skip Exhausted Opening Ranges (`or_high - or_low > 0.35 * ATR(15)`)
- **Exact Change**: Only allow entries when the `08:30–08:45 CT` Opening Range width satisfies `or_high - or_low <= 0.35 * ATR(15)`.
- **Market Mechanism**: When the first 15 minutes of RTH already consume `> 0.35 * ATR(15)`, the opening displacement is stretched and subsequent breakout entries buy the top / sell the bottom of an exhausted opening spike.

### Variant 4 (`NQONBiasMLV4_TightStop025ATR`): Tighten Protective Stop from `0.30 * ATR(15)` to `0.25 * ATR(15)` (Keeping `0.90 * ATR(15)` Target)
- **Exact Change**: Set `stop_dist = 0.25 * ATR(15)` while retaining `target_dist = 0.90 * ATR(15)` (`3.6R`).
- **Market Mechanism**: Genuine Opening Range breakouts backed by `ADX > 20` and a favorable daily regime score hold within `0.25 * ATR(15)` of the breakout trigger (matching Task 03's stop distance). If price reverses `0.25 * ATR` against the breakout, the auction has failed, and cutting at `0.25 * ATR` instead of `0.30 * ATR` saves `16.7%` on every stopped trade without disturbing the `0.90 * ATR` winners.

### Variant 5 (`NQONBiasMLV5_SymScoreAndTightStop`): Combined Symmetric Score (`today_score >= 0.03` Both Sides) + Tight Stop (`0.25 * ATR(15)`)
- **Exact Change**: Combine Variant 2 (`today_score >= 0.03` for both longs and shorts) and Variant 4 (`stop_dist = 0.25 * ATR(15)`, `target_dist = 0.90 * ATR(15)`).
- **Market Mechanism**: Filters out low-conviction short breakouts while truncating failed breakout losses at `0.25 * ATR`.

## 3. Evaluation Protocol
- **Costs Applied**: `$7.25` per side (`$14.50` round-trip in `compare.py`; `$7.25` round-trip in `S_RANK_PROGRAM.md` — both reported) + `1 tick` (`0.25 pts = $5.00`) slippage per market or stop fill (`0` slippage on limit target fills).
- **Split**:
  - **Design Period**: `2018-01-02` to `2022-12-31` (select winner here only).
  - **Holdout Period**: `2023-01-01` to `2026-10-09` (run once on selected winner).
- **Promotion Gate**: Must beat baseline in **both** `2018–2022` and `2023–2026` on **both** Net $ per contract and Max Drawdown, flat by `15:59 CT`, max 1 contract.
