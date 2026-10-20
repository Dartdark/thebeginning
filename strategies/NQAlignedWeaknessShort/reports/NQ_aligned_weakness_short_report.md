# Improvement Report: Relative Strength Shorts Filter (NQAlignedWeaknessShort)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Classification**: **Strategy Improvement (Relative Strength Shorts / WATCHLIST #25)**  
**Target Instrument**: CME E-mini / Micro E-mini Nasdaq-100 Futures (NQ / MNQ)  
**Execution Standard**: Next-minute Open + 1 tick slippage (0.25 pt); chronological 1-minute stop/target evaluation; $17.25 RT friction per NQ contract.

---

## 1. Classification & Portfolio Role

Per the portfolio mandate, a new strategy must trade on days, hours, or mechanisms that the portfolio does not already cover. 

An audit of `NQAlignedWeaknessShort` against `plan_daily_pnl.csv` reveals that **98% of its trade days (212 of 216 days) directly overlap the user's Relative Strength strategy short days**. Therefore, this work is formally classified as an **Improvement to Relative Strength Shorts**, rather than a standalone strategy.

### The Underlying Problem in Relative Strength:
In the user's plan, Relative Strength is traded **longs only** on 50K funded accounts, while taking both sides on 150K funded and personal accounts. The short side was previously excluded from 50K accounts because its uncalibrated performance was relatively weak ($t = 2.1$, PF 1.26, holdout $t = 1.1$).

### The Solution (The "ES Down" Filter):
When NQ exhibits relative weakness at 09:00 CT ($Residual \le -0.20\%$), the trade performance bifurcates dramatically based on broad market direction:
* **When ES is UP 08:30–09:00 (Shorting against broad market rally)**: 251 trades, **$93/trade ($t = 0.6)**, PF 1.10.
* **When ES is DOWN 08:30–09:00 (Broad market confirmation)**: 312 trades, **$363/trade ($t = 2.3)**, PF 1.40 (In-sample $497, $t = 2.5$).

Adding the `ret_es < 0` gate filters out the unprofitable bull-market shorts and preserves the high-expectancy breakdown shorts. Claude's independent audit (`analysis/anti_nq_aligned_weakness_short_test.py`) confirmed our trades with a **1.00 P&L correlation (216 of 217 trades matched)**, and cataloged the improvement as **WATCHLIST #25**.

---

## 2. Verified Metrics (Strict 1 NQ Contract, $17.25 RT Cost, Next-Bar Fill)

| Period | Trades | Net PnL ($) | Avg / Trade ($) | Win Rate | Profit Factor | $t$-stat | Max Drawdown | Positive Years |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **In-Sample Design (2018–2022)** | 120 | +$71,941 | +$599.5 | 55.8% | 1.81 | **2.51** | $11,293 | **5 / 5 (100%)** |
| **Out-of-Sample Holdout (2023–2026)** | 97 | +$41,682 | +$429.7 | 46.4% | 1.38 | **1.26** | $18,237 | **4 / 4 (100%)** |
| **Full History (2018–2026)** | 217 | +$113,623 | +$523.6 | 51.6% | 1.57 | **2.61** | $18,237 | **9 / 9 (100%)** |

*Claude's independent rebuild (`analysis/anti_nq_aligned_weakness_short_output.txt`):*
* 216 trades, **$501/NQ avg**, **PF 1.54**, **$t = 2.4$**, 8/9 years positive (2018–2022: $660 avg, $t = 2.6$).
* Shared with RS Shorts: 212 of 216 days (98%), averaging **$510/trade ($t = 2.5$)**.

---

## 3. Mandatory Rule Codified: Pre-Screening Day Overlap

Before developing any future candidate strategy, we enforce the following pre-registered screening rule:
1. **Day Overlap Gate**: Measure the percentage of trade days that coincide with any active strategy in `plan_daily_pnl.csv`.
2. **Classification**:
   * If day overlap $> 35\%$, it must be pre-registered and submitted as an **Improvement / Filter on that existing strategy**.
   * Only candidates with low day overlap ($\le 35\%$) and uncorrelated market mechanisms qualify as **New Strategy Candidates**.
