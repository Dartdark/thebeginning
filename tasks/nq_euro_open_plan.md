# Pre-Registered Research Plan: NQ European Open Cash Expansion (NQEuroOpenExp)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Objective**: Develop an independent, zero-correlation strategy targeting the European Cash Open (02:00–06:00 CT) on CME Nasdaq-100 Futures (NQ / MNQ).

---

## 1. Market Rationale & Structural Edge

1. **The Catalyst**:
   * At **02:00 CT** (08:00 London / 09:00 Frankfurt), continuous cash equity trading opens across major European bourses (Frankfurt DAX 40, London FTSE 100, Paris CAC 40, Euro Stoxx 50).
   * After the overnight Asian session (17:00–01:59 CT, characterized by low volume and tight ranges), European cash market opening creates an immediate surge in institutional liquidity and cross-asset order flow.
   * If European equity desks commit directional capital at the open, US equity index futures (NQ, ES) exhibit strong directional momentum during the European morning (02:00 to 06:00 CT).

2. **Portfolio Fit (Gaps in `plan_daily_pnl.csv`)**:
   * **Zero Correlation**: Existing active strategies (Vault Break, Overnight Bias ML, Monday Long, Expiration Open Short, Late-Day Flow) trade during US RTH (08:30–15:00 CT) or Sunday open (CL). None trade the European open.
   * **Apex-Compliant Risk**: The strategy enters between 02:00 and 04:00 CT and liquidates flat by 06:00 CT—hours before the US 07:30 CT macroeconomic releases, the 08:30 CT RTH open, and the 15:59 CT Apex trailing drawdown liquidation cutoff.
   * **Both Directions**: Trades both Long and Short, balancing the plan's long-heavy exposure.

---

## 2. Execution & Fill Standards (Strict Compliance)

* **Entry Execution**: Market orders MUST fill at **Next Bar Open + 1 tick slippage** (0.25 pt on NQ). Zero lookahead into the signal bar.
* **Intrabar Exits**: Evaluated minute-by-minute in chronological order. If both stop and target are touched within the same minute, the **stop-loss is executed first**.
* **Contract Sizing**: Strictly **1 contract** ($20/pt for NQ, $2/pt for MNQ).
* **Friction**: $17.25 round turn per NQ ($1.72 per MNQ) deducted from every trade.
* **Testing Protocol**:
  * **In-Sample Design**: 2018-01-01 through 2022-12-31.
  * **Candidate Gate**: $t \ge 2.5$, PF $\ge 1.30$, positive across majority of years, max drawdown $\le \$15,000$ per NQ ($\le \$1,500$ per MNQ to survive Apex's $2,000 trail).
  * **Out-of-Sample Holdout**: 2023-01-01 through 2026-10-09 (tested ONCE after parameter selection).

---

## 3. Pre-Registered Variants (Max 5)

* **Variant 1 (15m Opening Range Breakout)**:
  * Opening Range (OR): High/Low of the first 15m candle (02:00–02:15 CT).
  * Entry Window: 02:15 to 03:30 CT.
  * Long: 15m Close > OR High. Short: 15m Close < OR Low.
  * Stops/Targets: Stop = 1.25x ATR(14), Target = 2.5x ATR(14) (2:1 R:R). Flat at 06:00 CT.

* **Variant 2 (30m Opening Range Breakout - Institutional Confirmation)**:
  * Opening Range (OR): High/Low of the first two 15m candles (02:00–02:30 CT).
  * Entry Window: 02:30 to 04:00 CT.
  * Long: 15m Close > OR High. Short: 15m Close < OR Low.
  * Stops/Targets: Stop = 1.25x ATR(14), Target = 2.5x ATR(14). Flat at 06:00 CT.

* **Variant 3 (Asian Session High/Low Breakout at Euro Open)**:
  * Range: Asian Session High/Low (17:00 to 01:59 CT).
  * Entry Window: 02:00 to 03:30 CT.
  * Long: 15m Close > Asian High. Short: 15m Close < Asian Low.
  * Stops/Targets: Stop = 1.25x ATR(14), Target = 2.5x ATR(14). Flat at 06:00 CT.

* **Variant 4 (30m OR Breakout with Volume Expansion Filter)**:
  * Same as Variant 2, but requires breakout candle volume > 1.25x 20-period average volume (confirming genuine institutional expansion).

* **Variant 5 (30m OR Breakout with Higher-Timeframe Trend Filter - 200 SMA)**:
  * Same as Variant 2, but Long only if Close > 200-period SMA on 15m candles, and Short only if Close < 200-period SMA.
