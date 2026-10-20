# Pre-Registered Research Plan: Midday Institutional Lull on YM / ES (MiddayYMES)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Objective**: Test whether the midday institutional volume drop following the European cash close (11:30 CT / 16:30 London) provides a tradable edge on E-mini Dow Jones (YM / MYM) or E-mini S&P 500 (ES / MES).

---

## 1. Market Rationale & Structural Mechanism

1. **The Catalyst**:
   * At **11:30 CT** (12:30 ET / 17:30 CET / 16:30 London), London and all European equity exchanges close for the day.
   * Transatlantic institutional order flow ends. New York institutional desks rotate out for lunch.
   * Total trading volume drops by 40–60% to its lowest intraday level between 11:30 and 13:30 CT.

2. **Portfolio Fit & Day Overlap**:
   * Operates strictly between **11:30 and 13:30 CT**, closing flat before 13:45 CT.
   * Vault Break trades morning breakouts (10:00–11:00 CT). Late-Day Flow trades from 14:00 to 14:30 CT.
   * A strategy flat by 13:45 CT operates in the empty midday window with **< 20% day overlap** against active portfolio strategies.

---

## 2. Execution & Fill Standards (Strict Compliance)

* **Entry Execution**: Market orders MUST fill at **Next Bar Open + 1 tick slippage** (1.0 pt on YM = $5.00; 0.25 pt on ES = $12.50). Zero lookahead.
* **Intrabar Exits**: Chronological 1-minute traversal (Stop Loss takes precedence on ties).
* **Friction**: Full CME round-turn commissions + 2 ticks slippage ($22.25 on YM, $32.25 on ES).
* **Testing Protocol**:
  * **In-Sample Design**: 2018-01-01 through 2022-12-31.
  * **Candidate Gate**: $t \ge 2.5$, PF $\ge 1.30$, positive across majority of years, max drawdown $\le \$15,000$ per full contract ($\le \$1,500$ per micro contract).
  * **Out-of-Sample Holdout**: 2023-01-01 through 2026-10-09 (tested ONCE after parameter selection).

---

## 3. Pre-Registered Variants (Max 5)

* **Variant 1 (YM Lunch Range Breakout Follow)**:
  * Range: High/Low of the 11:30 to 12:00 CT window.
  * Trigger: Minute bar between 12:01 and 13:00 CT closes above Lunch High (Long) or below Lunch Low (Short) $\rightarrow$ Enter at next bar open + 1 tick.
  * Exits: Stop = 0.5x Lunch Range, Target = 1.0x Lunch Range, flat at 13:30 CT.

* **Variant 2 (YM Lunch Range False Breakout Fade)**:
  * Range: High/Low of the 11:30 to 12:00 CT window.
  * Trigger: Minute bar between 12:01 and 13:00 CT breaks outside the Lunch Range but fails to hold $\rightarrow$ Enter opposite direction at next bar open + 1 tick.
  * Exits: Stop = 0.5x Lunch Range, Target = Lunch Midpoint, flat at 13:30 CT.

* **Variant 3 (ES Extended Morning Trend Fade at London Close)**:
  * Setup: Morning move (08:30 to 11:30 CT) is extended ($|R_{\text{AM}}| \ge 1.25\times$ ATR).
  * Trigger: At 11:30 CT, enter counter-trend (Short if AM was strongly up, Long if AM was strongly down) at 11:31 open + 1 tick.
  * Exits: Stop = 0.5x ATR, Target = 0.5x ATR, flat at 13:30 CT.

* **Variant 4 (ES Midday Anchored VWAP Mean Reversion)**:
  * Setup: At 11:30–12:30 CT, price is extended $\ge 1.5$ standard deviations away from the 08:30 Anchored VWAP.
  * Trigger: Minute closes back toward VWAP $\rightarrow$ Enter mean reversion at next bar open + 1 tick.
  * Exits: Target = Anchored VWAP, Stop = 0.5x ATR, flat at 13:30 CT.

* **Variant 5 (YM Post-Lunch Early Afternoon Expansion)**:
  * Setup: Lunch range (11:30–12:30 CT) is compressed (Range $< 0.4\times$ Morning Range).
  * Trigger: 15m bar between 12:30 and 13:15 CT breaks out of the 11:30–12:30 compression channel $\rightarrow$ Enter breakout at next bar open + 1 tick.
  * Exits: Stop = 0.5x channel range, Target = 1.0x channel range, flat at 13:45 CT.
