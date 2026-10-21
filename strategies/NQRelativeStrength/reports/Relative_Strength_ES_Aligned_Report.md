# Strategy Research Report: NQ Relative Strength with ES-Aligned Short Filter (NQRelativeStrength)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Classification**: **WATCHLIST #25 (Incubation Candidate / Post-Hoc Split Check)**  
**Target Instrument**: CME E-mini / Micro E-mini Nasdaq-100 Futures (NQ / MNQ)  
**Reference Benchmark**: CME E-mini S&P 500 Futures (ES / MES)  
**Live Plan Verdict**: **NO CHANGE TO LIVE PLANS (50K Longs Only, 150K Both Sides; Watchlist #25 Monitored)**  

---

## 1. Executive Summary & Funded Bench Evaluation

`NQRelativeStrength` evaluates whether adding the ES-Down Short Filter (`WATCHLIST #25`) to the user's live Relative Strength strategy produces an actionable improvement in the funded portfolio bench:

* **Standalone Numbers (Replication Confirmed by Claude)**:
  * RS Both Sides (Current): 1,161 trades, $306/trade, PF 1.36, $t = 4.0$ (2023+ $t = 2.7$).
  * RS Longs Only (50K Plan): 598 trades, $366/trade, PF 1.46, $t = 3.6$ (2023+ $t = 2.8$).
  * RS Aligned (Longs + ES-Down Shorts): 910 trades, $365/trade, PF 1.44, $t = 4.2$ (2023+ $t = 2.8$).
  * Kept Shorts (ES Down): 312 trades, $363/trade, PF 1.40, $t = 2.3$ (but 2023+ $t = 0.9$).
  * Dropped Shorts (ES Up): 251 trades, $93/trade, PF 1.10, $t = 0.6$.

* **Bootstrapped Funded Bench Test (Claude, `analysis/relative_strength_aligned_bench.py`)**:
  * **50K Funded (1,000 paired histories, 2-year horizon)**:
    * Current (RS Longs 1 MNQ): Year-1 payouts **$9,294**, 258 days to 6 payouts, blown **7.7%**.
    * RS Aligned 1 MNQ: Year-1 payouts **$9,492**, 252 days to 6 payouts, blown **7.8%**.
    * *Verdict*: The +$198 gain in Year-1 and 6 days faster payout pace is well within the statistical noise band of 1,000 resampled histories.
  * **150K Funded (Plan x 1.5, full size from $3,000 cushion)**:
    * Current (RS Both 1 MNQ): 2-year payouts **$20,038**, blown 0%.
    * RS Aligned 1 MNQ: 2-year payouts **$19,999**, blown 0%.
    * *Verdict*: Zero net gain ($20,038 vs $19,999).
* **Final Verdict**:
  * While looking attractive on full-history backtest metrics ($t = 4.2$), the kept shorts have been weak in modern markets (2023+ $t = 0.9$), and portfolio-level payout impact is negligible.
  * **Live trading plans remain unchanged**: 50K funded stays Longs Only; 150K funded stays Both Sides.
  * `NQRelativeStrength` is retained on **WATCHLIST #25** for observation across the next ~50 live short signals.

---

## 2. MultiCharts Clarification & Audit Attribution

* **Correction Note**: The 216/216 trade MultiCharts confirmation in `analysis/anti_aws_mc_confirm.py` was conducted specifically on the standalone `NQAlignedWeaknessShort` prototype (the ES-down short rule). 
* The unified strategy `NQRelativeStrength` itself does not have a separate MultiCharts backtest run.

---

## 3. Configuration Comparison (Full 2018–2026 History)

| Metric | 1. RS Raw (Both Sides) | 2. RS Longs Only (Current 50K) | **3. RS Aligned (Longs + ES-Down Shorts)** |
| :--- | :---: | :---: | :---: |
| **Total Trades** | 1,175 | 607 | **921** |
| **Net Profit (per NQ)** | $344,988 | $208,092 | **$322,226** |
| **Average per Trade** | $293.61 | $342.82 | **$349.87** |
| **Win Rate** | 52.7% | 57.2% | **54.4%** |
| **Profit Factor** | 1.34 | 1.43 | **1.42** |
| **$t$-statistic** | 3.86 | 3.39 | **4.08** |
| **In-Sample Avg (2018–22)** | $265.53 ($t=2.99$) | $255.06 ($t=2.25$) | **$324.74 ($t=3.24$)** |
| **Holdout Avg (2023–26)** | $324.02 ($t=2.57$) | $446.00 ($t=2.55$) | **$377.57 ($t=2.64$)** |
| **Max Drawdown (NQ)** | $29,475 | $22,985 | **$31,554** |
| **Positive Years** | 9 of 9 years | 9 of 9 years | **9 of 9 years** |

---

## 4. Implementation Files in Repo

* **Jesse Strategy Class**: `strategies/NQRelativeStrength/__init__.py`
* **Synchronized Trade Ledger**: `strategies/NQRelativeStrength/trades.csv` (921 trades matching exact math)
* **Backtest Script**: `scratch/test_relative_strength_upgrades.py`
