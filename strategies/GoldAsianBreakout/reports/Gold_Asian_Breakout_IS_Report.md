# Strategy Research Report: COMEX Gold Asian Breakout (GoldAsianBreakout) — FAILED IN-SAMPLE GATE (Rank F)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Target Instrument**: CME Micro Gold Futures (`MGC` — $10 / pt, tick $0.10 = $1.00; Full GC = $100 / pt)  
**Classification**: **FAILED IN-SAMPLE GATE (Rank F — Pre-2023 Expectancy Flat, Driven by Bull Run)**  
**Status**: **REJECTED (Candidate Gate Failed; Holdout Untouched)**  

---

## 1. Executive Summary & Verdict

Following the pre-registered plan in `tasks/gold_asian_breakout_plan.md`, 4 systematic variants of the COMEX Gold Asian-range breakout were evaluated on **In-Sample data (2018-01-01 through 2022-12-31)** under full CME commissions ($3.00/MGC, $7.25/GC) and 1 tick adverse slippage on entry and exit.

* **Candidate Gate Requirement**: In-Sample $t \ge 2.00$, Profit Factor $\ge 1.25$, positive P&L across $\ge 4/5$ years.
* **Result**: **ALL 4 VARIANTS FAILED**.
  * The baseline breakout (V1) achieved only **$t = 0.74$ (PF 1.09)** with **3 of 5 years negative** (2018: -$106, 2019: -$755, 2020: -$323 on MGC).
  * Adding daily counter-trend filters (V2, V4) or profit targets (V3, V4) resulted in **net losses ($t = -0.74$ to $-1.43$)**.
* **Core Discovery**: 
  * The previously reported full-period profitability of the Gold Asian Breakout was almost entirely an artifact of the **2024–2026 gold bull market** (where gold rallied from $1,800 to $4,100).
  * During normal, non-trending market regimes (2018–2022), the low win rate (~35%) and wide stops are completely eroded by bid-ask spread and execution friction.
* **Rule 7 Verdict**: Under pre-registered protocol, any idea that fails the in-sample design gate ($t < 2.00$) is **REJECTED IMMEDIATELY** without evaluating out-of-sample holdout data.

---

## 2. In-Sample Results (2018-01-01 through 2022-12-31)

| Variant | Logic | Trades | Net MGC | Net GC | Avg / MGC | Win Rate | Profit Factor | $t$-stat | Max DD (MGC) | Positive Years | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **V1** | Base (Fills < 02:00, Out 12:00) | 656 | +$2,105.00 | +$22,854.00 | +$3.21 | 35.4% | 1.09 | **0.74** | $1,729.00 | 3 / 6 (2017–22) | **FAILED** |
| **V2** | Base + Opp. Yesterday (Filter D) | 329 | -$2,313.00 | -$22,225.25 | -$7.03 | 32.8% | 0.82 | **-1.42** | $3,320.00 | 2 / 6 | **FAILED** |
| **V3** | Base + Target 1.5R | 656 | -$1,554.50 | -$13,741.00 | -$2.37 | 43.1% | 0.93 | **-0.74** | $2,593.00 | 1 / 6 | **FAILED** |
| **V4** | Base + Filter D + Target 1.5R | 329 | -$1,998.50 | -$19,080.25 | -$6.07 | 40.1% | 0.83 | **-1.43** | $2,620.00 | 1 / 6 | **FAILED** |

*Year-by-Year P&L on 1 MGC (Variant 1)*:
* 2017 (partial): +$148
* 2018: -$106
* 2019: -$755
* 2020: -$323
* 2021: +$2,494
* 2022: +$647

---

## 3. Replication & Audit References

* **Pre-Registered Plan**: `tasks/gold_asian_breakout_plan.md`
* **Strategy Code**: `strategies/GoldAsianBreakout/__init__.py`
* **Evaluation Script**: `scratch/test_gold_asian_breakout.py`
* **Full Trade Ledger**: `scratch/gold_breakout_V1_trades_all.csv` (and V2–V4)
