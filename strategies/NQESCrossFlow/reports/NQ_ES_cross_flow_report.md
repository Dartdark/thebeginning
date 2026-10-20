# Strategy Research Report: NQ/ES Post-Open Cross-Market Flow (NQESCrossFlow) — FAILED / REJECTED (Rank D - Holdout Decay t = 0.20)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Classification**: **FAILED / REJECTED (Rank D — In-Sample Overfit / Out-of-Sample Decay)**  
**Target Instrument**: CME E-mini / Micro E-mini Nasdaq-100 Futures (NQ / MNQ)  
**Reference Benchmark**: CME E-mini S&P 500 Futures (ES / MES)  
**Status**: **REJECTED FROM ALL PORTFOLIOS (RS STAYS AS IS)**  

---

## 1. Executive Summary & Failure Verdict

`NQESCrossFlow` was formulated to capture post-open cross-market momentum between NQ and ES from 10:00 to 15:00 CT. While the strategy passed its initial in-sample design gate (2018–2022), it **completely failed its locked out-of-sample holdout test (2023–2026)** and **fails portfolio integration**:

* **Standalone Holdout Collapse**: 
  * 2018–2022 (In-Sample): 159 trades, +$78,429 net profit, **+$493.30/trade, t = 3.10, PF 2.00, 5/5 positive years**.
  * 2023–2026 (Holdout): 139 trades, +$5,092 net profit, **+$36.60/trade, t = 0.16–0.20, PF 1.04, 2/4 positive years**.
  * Deep consecutive drawdown in modern years: **2024 lost -$12,274; 2025 lost -$18,841**. Only 2026's rebound (+$30,434) kept the nominal total positive.
* **Portfolio Degradation (Added to Relative Strength at Equal Size)**:
  * Adding NQESCrossFlow to Relative Strength degrades out-of-sample live performance:
    * Relative Strength alone (2023+): **Sharpe 1.37, Max Drawdown $28,539**.
    * Relative Strength + CrossFlow (2023+): **Sharpe 1.22 (WORSE), Max Drawdown $44,205 (+$15,666 DRAWDOWN)**.
* **Code / Trades Alignment Audit**:
  * The strategy code and replication ledger have been synchronized to the exact same 20-day rolling Z-score and ATR-bracket formulation. A simplified static threshold alternative yielded only 60 trades across 8.5 years (~7 trades/year), which is statistically unviable and post-hoc.
* **Core Rule 7 Verdict**:
  * Any edge with out-of-sample $t < 1.0$ is classified as **FAILED**. NQESCrossFlow is an in-sample effect that decayed under modern market structure (Mag-7 single-stock concentration decoupling after 2023).

---

## 2. In-Sample Results (2018-01-01 through 2022-12-31)

Pre-registered in `tasks/nq_es_cross_flow_plan.md`:

| Variant | Window | Z-Thresh | Confirmation | Trades | Net P&L (NQ) | Avg / Trade | Win Rate | Profit Factor | $t$-stat | Max Drawdown | Positive Years |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| V1 | 13:00 CT | 1.25 | ES Direction | 150 | -$6,878 | -$45.9 | 44.7% | 0.92 | -0.32 | $25,767 | 2 / 5 |
| V2 | 13:00 CT | 1.50 | ES Direction | 104 | -$9,221 | -$88.7 | 44.2% | 0.87 | -0.48 | $30,424 | 1 / 5 |
| V3 | 13:00 CT | 1.25 | Tight Stops | 150 | -$17,547 | -$117.0 | 41.3% | 0.80 | -0.96 | $24,487 | 1 / 5 |
| **V4** | **10:00 CT** | **1.25** | **ES Direction** | **159** | **+$78,429** | **+$493.3** | **56.0%** | **2.00** | **3.10** | **$11,237** | **5 / 5** |
| V5 | 10:00 CT | 1.50 | ES Direction | 106 | +$57,950 | +$546.7 | 58.5% | 2.12 | 2.77 | $8,191 | 5 / 5 |

---

## 3. Locked Out-of-Sample Holdout Results (2023-01-01 through 2026-10-09) — FAILED

| Variant | Trades | Net P&L (NQ) | Avg / Trade | Win Rate | Profit Factor | $t$-stat | Max Drawdown | Positive Years | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **V4 (Z=1.25)** | **139** | **+$5,092** | **+$36.60** | **52.5%** | **1.04** | **0.16–0.20** | **$44,015** | **2 / 4** | **FAILED** |
| V5 (Z=1.50) | 99 | +$17,128 | +$173.00 | 51.5% | 1.18 | 0.63 | $36,589 | 2 / 4 | **FAILED** |

*Annual Breakdown (V4)*:
* 2023: +$5,773
* 2024: -$12,274
* 2025: -$18,841
* 2026: +$30,434

---

## 4. Full Period Summary & Claude Independent Verification

Audited and reproduced by Claude in `analysis/anti_nq_es_crossflow_test.py` (`636a6e5`):
* Full Period (298 trades): $280/trade, PF 1.38, $t = 2.0$.
* 2018–2022: $493/trade, $t = 3.1$.
* 2023–2026: $37/trade, $t = 0.2$.
* Combined with Relative Strength: 2023+ Sharpe falls 1.37 → 1.22; max drawdown increases by $15,666.

---

## 5. Architectural Takeaways & Directives Implemented

1. **Rule 7 Strictly Enforced**: Any candidate with holdout $t < 1.0$ is labeled **FAILED (Rank D/F)** in the title and header immediately.
2. **Code & Trades Alignment**: Strategy Python implementation and trade ledger are required to execute the exact identical mathematical equation.
3. **Portfolio Decision**: `NQESCrossFlow` is permanently shelved. `Relative Strength` remains unchanged in all funded and evaluation plans.
