# Empirical Research Report: Turn-of-Month Cash Open Long (TurnOfMonthLong)

**Date**: 2026-10-21  
**Status**: **FAILED (Rank F — Failed In-Sample Candidate Gate & Bull Market Mirage)**  
**Author**: Antigravity (under SignalLab Institutional Standards & Rules 7–11)  
**Dataset**: Full 2018–2026 unadjusted 1-minute NQ data (3,087,803 bars)  
**In-Sample Window**: 2018-04-01 to 2022-12-31  
**Holdout Window**: 2023-01-01 to 2026-10-09  
**Friction**: $17.25 + 1 tick slippage = $22.25 per round-turn on full NQ (1.1125 pts)  

---

## 1. Executive Summary & Verdict

We evaluated transferring the `tdm3` Turn-of-Month mechanic (from `Overnight Bias ML`) and the 08:30 CT cash open entry (from `Monday Long`) into a standalone strategy: buying the 08:30 CT cash open on the first 3 trading days of each month (TDM 1–3).

| Variant | Horizon / Days | Total Trades | Full Period Net Pts (USD) | In-Sample $t$ (2018–22) | In-Sample Net Pts | Holdout $t$ (2023–26) | Holdout Net Pts | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`V1_TDM1-3_Out1000`** | TDM 1–3, out at 10:00 CT | 307 | +2,616.7 pts (+$52,334) | **-0.79** | **-797.0 pts** | 2.05 | +3,291.5 pts | **FAIL (Rank F — Negative IS)** |
| **`V2_TDM1-3_Out1130`** | TDM 1–3, out at 11:30 CT | 307 | +5,126.6 pts (+$102,532) | **-0.31** | **-377.3 pts** | 2.76 | +5,335.7 pts | **FAIL (Rank F — Negative IS)** |
| **`V3_TDM1-3_Out1500`** | TDM 1–3, out at 15:00 CT | 305 | +6,435.8 pts (+$128,715) | **0.23** | **+342.6 pts** | 2.86 | +6,027.1 pts | **FAIL (Rank F — Flunked IS Gate)** |
| **`V4_TDM1-2_Out1000`** | TDM 1–2, out at 10:00 CT | 203 | +1,385.9 pts (+$27,718) | **-0.05** | **-37.4 pts** | 1.05 | +1,413.9 pts | **FAIL (Rank F — Negative IS)** |
| **`V5_TDM1_Out1500`** | TDM 1 only, out at 15:00 CT | 99 | +1,869.7 pts (+$37,395) | **-0.44** | **-340.1 pts** | 1.98 | +2,297.8 pts | **FAIL (Rank F — Negative IS)** |

### Final Verdict: RANK F (REJECTED)
Under **Rule 7 (In-Sample Candidate Gate)**:
* A strategy is **ONLY a candidate if $t \ge 2.50$** on 2018–2022 data under real friction.
* Across all 5 variants, in-sample performance was either **flat or net negative** ($t = -0.79 \text{ to } +0.23$, PF $0.85 \text{ to } 1.05$).
* The strategy is rejected for standalone deployment.

---

## 2. Quantitative Diagnosis: The "Bull Market Beta Mirage"

Look at the extreme contrast between the In-Sample and Holdout periods on `V3_TDM1-3_Out1500`:
* **In-Sample (2018–2022 — 167 trades)**: +342.6 pts (+$6,852 total, or only **+$2.05 pts/trade**). At $t = 0.23$ and PF 1.05, it was pure random chop.
* **Holdout OOS (2023–2026 — 132 trades)**: **+6,027.1 pts (+$120,542 total, or +$45.66 pts/trade)**, $t = 2.86$, PF 1.82!

### Why Did This Happen?
1. **The AI / Mega-Cap Tech Run (2023–2026)**:
   Between January 2023 and October 2026, the Nasdaq-100 surged from ~10,800 to ~20,500. During this historic trending regime, buying the open on *any* calendar day and holding until 15:00 CT produced massive profits simply by being long equity index beta.
2. **Failure Under Bear & Chop Regimes (2018–2022)**:
   In 2018 (trade war chop), 2020 (pandemic crash), and 2022 (Fed rate hiking bear market), the first 3 days of the month had **zero standalone edge**.
3. **Contrast with `Monday Long`**:
   `Monday Long` produced $t = 2.80$ in 2018–2022 AND $t = 2.50$ in 2023–2026, proving it captures genuine weekly institutional re-allocation across all market cycles. Turn-of-Month, by contrast, only works when the broader market is already in a raging bull trend.

---

## 3. Search Denominator Registry & Audit Trail

Logged into [`tasks/SEARCH_DENOMINATOR_REGISTRY.csv`](file:///c:/Users/dmoto/jesse-bot/tasks/SEARCH_DENOMINATOR_REGISTRY.csv):
* `HYP-022`: `Turn_Of_Month_Long` — FAILED (Rank F)

All trades are preserved in `scratch/V1_TDM1-3_Out1000_trades.csv` and `scratch/V3_TDM1-3_Out1500_trades.csv`.

### Conclusion
* `tdm3` remains valid as a **conditioning filter** inside `Overnight Bias ML` (boosting an existing breakout), but buying the open blindly based on turn-of-month is not a standalone alpha.
