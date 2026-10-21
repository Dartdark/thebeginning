# Pre-Registered Research Plan: Late-Day Flow VWAP Climax & Stretch Guard (HYP-027)

**Date**: 2026-10-21  
**Author**: Quantitative Strategy Team / Antigravity  
**Target Strategy**: `Late-Day Flow` (`NQLateDayFlow` / Task 07)  
**Instrument**: CME E-mini Nasdaq-100 Futures (`NQ`) / Micro E-mini (`MNQ`)  
**Timeframe**: 5-Minute Bars (`fast_mode = False`, full 1m intrabar execution)  
**Direction**: Longs and Shorts  
**Evaluation Time**: 14:00 CT Bar Close (Execution next bar at market, 14:05 CT)  
**Displacement Gate**: `|Move| >= 0.40 * ATR-15` from 08:35 CT Open  
**Target / Stop**: Systematic Time Exit at `14:30 CT` / Dynamic Stop Loss at `Entry ± 0.25 * ATR-15`  
**Holding Period**: Exactly 25 Minutes (14:05 to 14:30 CT)  

---

## 1. Problem Statement: Microstructure Failure Signatures of Late-Day Flow

`Late-Day Flow` profits from non-discretionary Leveraged ETF rebalancing (e.g. TQQQ/SQQQ) and Market-On-Close (MOC) index continuation during Wall Street's "Power Hour" (14:00–14:30 CT).

However, historical trade audits show a pronounced failure mode:
1. **The 14:00 Climax Exhaustion Trap**:
   - On days where NQ has already surged +150 to +250 points, intraday CTA momentum algorithms, scalpers, and day traders reach daily profit limits by 14:00 CT.
   - Between 14:00 and 14:15 CT, these participants submit heavy market-sell (for longs) or market-buy (for shorts) orders to flatten out before the closing bell.
   - Because `Late-Day Flow` only measures displacement from 08:35 CT open (`|Move| >= 0.40 ATR`), it blindly enters at 14:05 CT even when price is severely overextended from the true institutional average (session VWAP).
   - The ensuing 25-to-40 point profit-taking mean-reversion retest clips the tight `0.25 * ATR` stop loss within minutes.

---

## 2. Hypothesis Triplet ($h_{27}$)

- **Economic Mechanism ($m_{27}$)**: Session VWAP calculated from the 08:30 CT cash open represents the true volume-weighted institutional consensus over 5.5 hours of Regular Trading Hours. When price at 14:00 CT is overextended beyond a threshold distance from VWAP, the trend is climactic and at peak risk of an intraday profit-taking retracement. Capping the maximum allowable entry distance from session VWAP eliminates climactic entries while preserving institutional trend continuation.
- **Executable Expression ($e_{27}$)**:
  - Track RTH session VWAP from 08:30 CT cash open.
  - At 14:00 CT close:
    - Long signal: `Move >= +0.40 * ATR` AND `(Close - VWAP) <= Stretch_Cap * ATR`
    - Short signal: `Move <= -0.40 * ATR` AND `(VWAP - Close) <= Stretch_Cap * ATR`
- **Declared Return Direction ($d_{27}$)**: Trend continuation (Longs for positive displacement, Shorts for negative displacement).

---

## 3. Pre-Registered Variants to Evaluate (In-Sample: 2018–2022)

All variants evaluated under full institutional friction (**$17.25 round-turn commission + 1 tick ($5.00) slippage per fill ($10.00 RT) = $27.25 per trade**):

| Variant | Strategy Name | Modification |
|---|---|---|
| **Base** | `NQLateDayFlow` | Baseline: `|Move| >= 0.40 * ATR`, no VWAP check |
| **V1** | `NQLDFStretch100` | Capped at `Stretch <= 1.00 * ATR` from session VWAP |
| **V2** | `NQLDFStretch075` | Capped at `Stretch <= 0.75 * ATR` from session VWAP |
| **V3** | `NQLDFStretch050` | Capped at `Stretch <= 0.50 * ATR` from session VWAP |
| **V4** | `NQLDFPullbackVWAP`| Requires pullback toward VWAP: Longs require `Low(14:00 bar) <= VWAP + 0.25 ATR`; Shorts require `High(14:00 bar) >= VWAP - 0.25 ATR` |

---

## 4. Evaluation Protocol

1. **In-Sample Period**: `2018-01-01` to `2022-12-31`. Strict candidate hurdle: $t \ge 2.50$, higher Net Profit or significantly reduced Max Drawdown with improved NP/DD ratio.
2. **Out-of-Sample Holdout**: `2023-01-01` to `2026-10-09`. Tested **once** for the single winner of the In-Sample evaluation.
3. **Mandatory MCP Report**: Save via `save_strategy_report` inside `strategies/NQLateDayFlow/reports/`.
