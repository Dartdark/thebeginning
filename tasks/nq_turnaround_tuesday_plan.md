# Pre-Registered Research Plan: NQ Turnaround Tuesday Reversal (NQTurnaroundTuesday)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Objective**: Develop an independent, low-overlap strategy targeting the institutional Turnaround Tuesday mean-reversion flow on CME Nasdaq-100 Futures (NQ / MNQ).

---

## 1. Market Rationale & Structural Edge

1. **The Catalyst**:
   * On Mondays, passive institutional cash inflows, mutual fund dividend reinvestments, and retail orders create directional drift (which fuels the user's `MondayLong` strategy).
   * When Monday exhibits an aggressive, one-directional move (especially a liquidation/sell-off), institutional liquidity providers and market makers step in on Tuesday to accumulate inventory at discounted prices.
   * This institutional rotation produces the well-documented "Turnaround Tuesday" effect, where Tuesday mean-reverts against Monday's directional excess.

2. **Portfolio Fit (Gaps in `plan_daily_pnl.csv`)**:
   * **Zero Day Overlap with Monday Strategies**: `MondayLong` and `BridgeMondayLong` trade strictly on Mondays. An exclusive Tuesday strategy has **0% day overlap** with both strategies!
   * **Low Overlap with Other Strategies**: Vault Break, Overnight Bias ML, and Late-Day Flow trade across the full week, so a Tuesday-only strategy overlaps at most ~20% of trading days (well below our $\le 35\%$ overlap threshold).
   * **Apex-Compliant Risk**: Enters during Tuesday morning (08:30–10:30 CT) and liquidates flat by 15:00 CT (zero overnight holding risk, hours before the 15:59 CT cutoff).

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

* **Variant 1 (Down Monday $\rightarrow$ Tuesday Long Momentum Reversal)**:
  * Setup: Monday RTH close < Monday RTH open ($C_{\text{Mon}} < O_{\text{Mon}}$).
  * Entry Trigger: On Tuesday, if a 15m bar between 08:45 and 10:00 CT closes above the Tuesday 08:30 open and above the prior 15m high $\rightarrow$ Buy Long at next bar open + 0.25 pt slippage.
  * Exits: Stop = 0.6x 20-day range, Target = 1.0x 20-day range, flat at 15:00 CT.

* **Variant 2 (Extreme Down Monday $\rightarrow$ Tuesday Long Reversal)**:
  * Setup: Monday was an aggressive down day (Monday RTH return $\le -1.0\%$).
  * Entry Trigger: Tuesday 15m close between 08:45 and 10:00 CT > Tuesday 08:30 open $\rightarrow$ Buy Long at next bar open + 0.25 pt slippage.
  * Exits: Stop = 0.6x 20-day range, Target = 1.0x 20-day range, flat at 15:00 CT.

* **Variant 3 (Bidirectional Monday Extension Fade)**:
  * Setup: Monday range $> 1.0\times$ 20-day average range.
  * Long: If Monday was Down ($C < O$), enter Long when Tuesday 15m close > 08:30 open.
  * Short: If Monday was Up ($C > O$), enter Short when Tuesday 15m close < 08:30 open.
  * Exits: Stop = 0.6x range, Target = 1.0x range, flat at 15:00 CT.

* **Variant 4 (Tuesday 30m OR Breakout in Turnaround Direction)**:
  * Setup: Monday was Down ($C < O$).
  * Tuesday Opening Range (OR): High/Low of first two 15m bars (08:30–09:00 CT).
  * Entry Trigger: 15m bar between 09:00 and 10:30 CT closes ABOVE 30m OR High $\rightarrow$ Buy Long at next bar open + 0.25 pt slippage.
  * Exits: Stop = 0.6x range, Target = 1.0x range, flat at 15:00 CT.

* **Variant 5 (Tuesday Anchored VWAP Reclaim)**:
  * Setup: Monday was Down ($C < O$).
  * Entry Trigger: On Tuesday, after dipping below 08:30 open, price crosses and closes above the 08:30 Anchored VWAP between 09:00 and 10:30 CT $\rightarrow$ Buy Long at next bar open + 0.25 pt slippage.
  * Exits: Stop = 0.6x range, Target = 1.0x range, flat at 15:00 CT.
