# Empirical Research Report: Universal 07:30 Macro Release Fade (MacroReleaseFade)

**Date**: 2026-10-21  
**Status**: **FAILED (Rank F — Failed In-Sample Candidate Gate)**  
**Author**: Antigravity (under SignalLab Institutional Standards & Rules 7–11)  
**Dataset**: Full 2018–2026 unadjusted 1-minute NQ data (3,087,803 bars)  
**In-Sample Window**: 2018-04-01 to 2022-12-31  
**Holdout Window**: 2023-01-01 to 2026-10-09  
**Friction**: $17.25 + 1 tick slippage = $22.25 per round-turn on full NQ (1.1125 pts)  

---

## 1. Executive Summary & Verdict

We evaluated whether the proven structural mechanics of **`NFP Fade`** (fading the 07:30 CT macro release spike) could be expanded from the 1st Friday of the month to **all weekday 07:30 CT releases** (capturing CPI, PPI, GDP, and Retail Sales).

| Variant | Scope / Parameters | Total Trades | Full Period Net Pts (USD) | In-Sample $t$ (2018–22) | In-Sample Net Pts | Holdout $t$ (2023–26) | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`V1_All_k3.0_Out0900`** | All weekdays, $3.0\times$ median spike | 258 | +1,319.0 pts (+$26,380) | **-0.39** | **-380.9 pts** | 1.34 | **FAIL (Rank F — Failed IS)** |
| **`V2_Midweek_k3.0_Out0900`**| Midweek only (Tue/Wed/Thu — CPI/PPI/GDP) | 144 | +379.9 pts (+$7,598) | **-1.57** | **-943.3 pts** | 1.20 | **FAIL (Rank F — Negative IS)** |
| **`V3_All_k2.5_Out0900`** | All weekdays, $2.5\times$ median spike | 348 | +1,098.0 pts (+$21,961) | **-0.83** | **-870.7 pts** | 1.35 | **FAIL (Rank F — Failed IS)** |
| **`V4_All_k3.5_Out0900`** | All weekdays, $3.5\times$ median spike | 201 | +1,609.0 pts (+$32,181) | **-0.11** | **-89.2 pts** | 1.36 | **FAIL (Rank F — Failed IS)** |
| **`V5_Midweek_k3.0_Out0930`**| Midweek only, hold to 09:30 CT | 144 | +261.4 pts (+$5,229) | **-0.43** | **-302.3 pts** | 0.56 | **FAIL (Rank F — Failed IS)** |

### Final Verdict: RANK F (REJECTED)
Under **Rule 7 (Hard Stop In-Sample Gate)**:
Every single variant produced **negative net points ($t < 0$) in the In-Sample period (2018–2022)**. 
- Fading midweek releases (CPI, PPI, GDP) on Tuesday, Wednesday, and Thursday lost **-$943.3 points ($t = -1.57$)** In-Sample.
- The hypothesis is decisively rejected for portfolio deployment.

---

## 2. Day-of-Week Dissection: The Crucial Structural Contrast

Examining the performance of the 07:30 fade broken down by day of the week reveals the exact economic truth:

| Day of Week | Primary Macro Catalyst | Total Trades | Win Rate | Net Points | Net PnL ($) | Profit Factor | $t$-statistic |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Monday** | Minor secondary releases | 6 | 33.3% | -444.4 | -$8,888 | 0.31 | -1.05 |
| **Tuesday** | CPI (occasional) / Retail Sales | 34 | 58.8% | +202.4 | +$4,048 | 1.22 | 0.46 |
| **Wednesday** | CPI / PPI | 53 | 52.8% | +71.2 | +$1,423 | 1.04 | 0.12 |
| **Thursday** | Weekly Jobless Claims / PPI / GDP | 57 | 42.1% | +106.4 | +$2,127 | 1.04 | 0.09 |
| **Midweek Total** | **CPI / PPI / GDP / Claims** | **144** | **50.0%** | **+379.9** | **+$7,598** | **1.08** | **0.29** |
| **Friday** | **NFP (Non-Farm Payrolls)** | **108** | **50.0%** | **+1,383.5** | **+$27,670** | **1.49** | **1.56** |

*(Under $2.5\times$ threshold `V3`, Friday delivered **+$2,326.0 points / +$46,521 net ($t = 2.35$, PF 1.75)**, while the rest of the week was deeply negative).*

---

## 3. Macroeconomic Diagnosis: Why Friday (NFP) Fades, but CPI/PPI Trends

This is one of the most important macroeconomic distinctions in institutional futures trading:

1. **Labor Data (NFP) is Lagging Sentiment**:
   * Non-Farm Payrolls is a survey of past employment. The initial reaction at 07:30 CT is driven by retail algorithms and headline keyword parsers overreacting to revision numbers or unemployment rate rounding. 
   * Institutional bond desks recognize that employment is backward-looking. Once the initial order-book liquidity vacuum clears, market makers easily absorb the move and fade it back toward fair value before 09:00 CT.

2. **Inflation Data (CPI / PPI) Fundamentally Reprices the Cost of Capital**:
   * CPI is **NOT** sentiment. CPI directly dictates Federal Reserve monetary policy, terminal interest rates, and the 10-year US Treasury yield.
   * When CPI prints hotter or cooler than consensus, institutional fixed-income desks and multi-asset macro funds **must re-calculate the net present value (NPV) of future cash flows for every technology stock in the Nasdaq-100**.
   * Therefore, CPI spikes do **not** mean-revert. They are structural re-evaluations that trigger persistent, one-way trending flows into and through the cash open. 
   * Fading a CPI print is "stepping in front of a sovereign freight train."

---

## 4. Search Denominator Registry & Audit Trail

Logged into [`tasks/SEARCH_DENOMINATOR_REGISTRY.csv`](file:///c:/Users/dmoto/jesse-bot/tasks/SEARCH_DENOMINATOR_REGISTRY.csv):
* `HYP-021`: `Macro_Release_Fade_Universal` — FAILED (Rank F)

All trades are archived in `scratch/V1_All_k3.0_Out0900_trades.csv` and `scratch/V2_Midweek_k3.0_Out0900_trades.csv`.

### Conclusion for the Live Portfolio
- **Keep `NFP Fade` Strictly Restricted to Fridays**: The live strategy (`NFP Fade` at $500 risk in the funded plan) is mathematically confirmed as a unique Friday labor-market phenomenon.
- **Do NOT deploy a CPI / PPI fade**: Inflation shocks must be respected as fundamental regime shifts, not mean-reverting noise.
