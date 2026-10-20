# Pre-Registered Research Plan: NQ/ES Cross-Market Flow & Alignment (NQESCrossFlow)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Objective**: Evaluate whether cross-market factor divergence between E-mini Nasdaq-100 (NQ) and E-mini S&P 500 (ES), conditioned on broad market directional alignment, produces a tradable institutional momentum edge in windows non-overlapping with the existing portfolio.

---

## 1. Structural Market Mechanism & Portfolio Fit

1. **The Rationale**:
   * Institutional multi-asset and multi-factor desks reallocate risk between mega-cap tech growth (NQ) and broad core value/cyclicals (ES).
   * When NQ moves significantly beyond its expected beta-adjusted move relative to ES:
     $$\text{Residual} = \Delta \text{NQ} - \beta \cdot \Delta \text{ES}$$
     it signals idiosyncratic institutional capital rotation.
   * **The Alignment Filter**: 
     * If NQ is breaking down while ES is rallying, shorting fights broad-market macro liquidity.
     * If NQ is breaking down **while ES is also down**, macro beta and factor liquidation align, creating persistent unidirectional order flow.
2. **Upfront Day-Overlap & Portfolio Gate**:
   * The existing `Relative Strength` strategy trades at 09:00 CT (08:30–09:00 window).
   * To achieve **< 35% day overlap** and build a genuinely new strategy, this plan evaluates **untouched windows**:
     * **Window A (Afternoon Realignment: 13:00 CT)**: Following the European close (11:30 CT), hedge funds rebalance ahead of the 14:00 leveraged ETF reset.
     * **Window B (Post-Opening Balance: 10:00 CT)**: Evaluating 09:30–10:00 post-open factor momentum.
   * Day overlap will be explicitly calculated against all strategies in `plan_daily_pnl.csv`.

---

## 2. Rigorous Protocol & Execution Standards

* **In-Sample Design Window**: **2018-01-01 through 2022-12-31** (5 full calendar years).
* **Locked Out-of-Sample Holdout**: **2023-01-01 through 2026-10-09** (tested ONCE only if an in-sample variant passes).
* **Candidate Gate (Rule 7)**:
  * In-Sample $t \ge 2.50$ on 2018–2022 data under full CME commissions and slippage.
  * Profit Factor $\ge 1.30$.
  * Positive net P&L across $\ge 4/5$ in-sample years.
  * Max drawdown $\le \$15,000$ per contract.
* **Execution & Friction Standards**:
  * **Instrument**: CME E-mini Nasdaq-100 Futures (`NQ`, $20/pt, tick $0.25 = $5.00).
  * **Entry Execution**: Next-minute Open + 1 tick adverse slippage ($0.25 pt). Zero lookahead.
  * **Intrabar Exits**: Chronological 1-minute traversal (Stop Loss takes precedence on ties) + 1 tick adverse slippage.
  * **Commissions & Friction**: Full CME round-turn friction ($17.25 per NQ contract).
  * **Mandatory Flattening**: Hard liquidation before 15:55 CT (intraday only, zero overnight holding).

---

## 3. Mathematical Definitions

* **Rolling Beta ($\beta_{20}$)**: Trailing 20-day beta of 5-minute RTH returns between NQ and ES:
  $$\beta_{20} = \frac{\sum (R_{\text{NQ}} - \bar{R}_{\text{NQ}})(R_{\text{ES}} - \bar{R}_{\text{ES}})}{\sum (R_{\text{ES}} - \bar{R}_{\text{ES}})^2}$$
* **Residual & Z-Score**:
  $$\Delta \text{NQ} = \frac{\text{NQ}_t - \text{NQ}_{t_0}}{\text{NQ}_{t_0}}, \quad \Delta \text{ES} = \frac{\text{ES}_t - \text{ES}_{t_0}}{\text{ES}_{t_0}}$$
  $$\text{Residual} = \Delta \text{NQ} - \beta_{20} \cdot \Delta \text{ES}$$
  $$Z = \frac{\text{Residual} - \mu_{20}}{\sigma_{20}}$$
* **Macro Directional Confirmation**:
  * Long: $Z \ge Z_{\text{crit}}$ **AND** $\Delta \text{ES} > 0$
  * Short: $Z \le -Z_{\text{crit}}$ **AND** $\Delta \text{ES} < 0$

---

## 4. Pre-Registered Variants (Max 5)

* **Variant 1 (Afternoon Realignment / Baseline $Z=1.25$)**:
  * Decision Time: **13:00 CT** (window: 11:30–13:00 CT).
  * Threshold: $|Z| \ge 1.25$ with ES directional agreement.
  * Exits: Stop = $0.6 \times \text{ATR}(14)$, Target = $1.2 \times \text{ATR}(14)$, flat at 15:50 CT.

* **Variant 2 (Afternoon Realignment / High Conviction $Z=1.50$)**:
  * Decision Time: **13:00 CT** (window: 11:30–13:00 CT).
  * Threshold: $|Z| \ge 1.50$ with ES directional agreement.
  * Exits: Stop = $0.6 \times \text{ATR}(14)$, Target = $1.2 \times \text{ATR}(14)$, flat at 15:50 CT.

* **Variant 3 (Afternoon Realignment / Tight Risk $Z=1.25$)**:
  * Decision Time: **13:00 CT** (window: 11:30–13:00 CT).
  * Threshold: $|Z| \ge 1.25$ with ES directional agreement.
  * Exits: Stop = $0.4 \times \text{ATR}(14)$, Target = $0.8 \times \text{ATR}(14)$, flat at 15:50 CT.

* **Variant 4 (Post-Open Expansion / Baseline $Z=1.25$)**:
  * Decision Time: **10:00 CT** (window: 09:30–10:00 CT).
  * Threshold: $|Z| \ge 1.25$ with ES directional agreement.
  * Exits: Stop = $0.6 \times \text{ATR}(14)$, Target = $1.2 \times \text{ATR}(14)$, flat at 15:00 CT.

* **Variant 5 (Post-Open Expansion / High Conviction $Z=1.50$)**:
  * Decision Time: **10:00 CT** (window: 09:30–10:00 CT).
  * Threshold: $|Z| \ge 1.50$ with ES directional agreement.
  * Exits: Stop = $0.6 \times \text{ATR}(14)$, Target = $1.2 \times \text{ATR}(14)$, flat at 15:00 CT.
