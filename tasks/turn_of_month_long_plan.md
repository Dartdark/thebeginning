# Pre-Registered Research Plan: Turn-of-Month Cash Open Inflow (TurnOfMonthLong)

**Date**: 2026-10-21  
**Author**: Antigravity (under SignalLab Institutional Standards & Rule 9)  
**Target Instrument**: CME E-mini / Micro E-mini Nasdaq-100 Futures (`NQ` / `MNQ`)  
**Data Horizon**: 2018-01-02 to 2026-10-09 (Full 1-minute unadjusted data aggregated to 5-minute bars)  
**In-Sample Window**: 2018-04-01 to 2022-12-31  
**Holdout Window**: 2023-01-01 to 2026-10-09  
**Friction Model**: $17.25 per round-turn on full NQ ($1.72 on MNQ) + 1 tick adverse slippage  

---

## 1. Economic Mechanism & Hypothesis Triplet ($h_j = (m_j, e_j, d_j)$)

### Economic Mechanism ($m_j$)
This strategy transfers two proven institutional mechanics already verified in our live funded portfolio:
1. **The 08:30 CT Cash Open Long Entry** (from `Monday Long` — Task 05, $t = 2.80$ IS, $t = 2.50$ OOS).
2. **The `tdm3` Turn-of-Month Feature** (from `Overnight Bias ML` — Task 04, where the first 3 trading days of each calendar month displayed the single highest positive ridge-regression coefficient of $+0.165$).

The market driver is **systematic passive retirement and institutional capital deployment**. At the beginning of each calendar month, automatic 401(k) payroll deductions, employer matching funds, target-date retirement rebalancing, and corporate pension contributions execute mechanically. Institutional asset managers allocate cash into broad equity index futures at the 08:30 CT (09:30 ET) NYSE cash open, creating persistent upward drift.

### Executable Expression ($e_j$)
1. **Date Qualification**:
   - Determine the Trading Day of the Month (TDM) for each date ($TDM \in \{1, 2, 3\}$).
   - Skip early-close days and holiday half-days.
2. **Entry**:
   - At the close of the 5-minute bar stamped **08:30 CT** (the NYSE cash open), enter **Long** next bar at market (08:31 CT open).
3. **Risk Management**:
   - Stop Loss = $0.50 \times \text{15-day ATR}$ below entry fill (matching `Monday Long` and `NFP Fade`).
4. **Pre-Registered Holding Horizon Variants**:
   - **Variant 1 (TDM 1–3, Out at 10:00 CT)**: Morning cash drive; exits at 10:00 CT (giving **0.0% time overlap** with `Vault Break`).
   - **Variant 2 (TDM 1–3, Out at 11:30 CT)**: Extended morning trend; exits before midday European close.
   - **Variant 3 (TDM 1–3, Out at 15:00 CT)**: Full cash session hold (identical structure to `Monday Long`).
   - **Variant 4 (TDM 1 & 2 only, Out at 10:00 CT)**: Isolating the two peak cash-inflow days.
   - **Variant 5 (TDM 1 only, Out at 15:00 CT)**: Pure Day 1 monthly deployment.

### Declared Return Direction ($d_j$)
* $d_j = +1$ (Long). Declared in advance prior to backtesting.

---

## 2. In-Sample vs. Holdout Candidate Gates

* **In-Sample Gate (2018-04-01 to 2022-12-31)**:
  - Must achieve $t \ge 2.50$ under full $\$17.25$ friction per NQ.
  - Profit Factor $\ge 1.30$.
  - Positive net P&L across a majority of in-sample years.
* **Holdout Validation (2023-01-01 to 2026-10-09)**:
  - Must remain net positive ($t \ge 1.50$, positive net PnL).
  - Rolling performance slope must not decay ($t_{\text{decay}} > -1.96$).
* **Portfolio Spanning**: Variants exiting at 10:00 CT offer zero intraday position clash with `Vault Break`.
