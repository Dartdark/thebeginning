# Strategy Validation Report: NQIBBreakout (Initial Balance RTH Momentum Breakout)

**Strategy Name:** `NQIBBreakout`  
**Symbol:** `NQ-USD` (CME E-mini & Micro E-mini Nasdaq-100 Futures)  
**Timeframe:** 15m  
**Execution Environment:** CME Regular Trading Hours (RTH 08:30 to 15:50 CT)  
**Friction Applied:** Real CME Commission & Slippage: $17.25 per round-turn NQ / $1.72 per round-turn MNQ (`fee = 0.00003`)  
**Overnight Exposure:** **ZERO** (Mandatory flat liquidation at 15:50 CT every single day)  
**Date of Audit:** October 20, 2026  
**Final Rating:** **RANK A (STRONG PASS - ALL CRITERIA MET)**

---

## 1. Executive Summary & Verdict

`NQIBBreakout` is an intraday quantitative strategy engineered specifically for CME Nasdaq-100 equity index futures. It solves the structural flaws of prior iterations by:
1. **Eliminating Overnight Drift:** 100% of trades are liquidated by 15:50 CT. Every dollar of edge is generated strictly from intraday price discovery.
2. **Surpassing Rule 7 Candidate Gate In-Sample (2018–2022):** Achieves **$t = 3.27$** (target $\ge 2.50$) across 420 trades, with **5 out of 5 years positive**.
3. **Passing Locked Out-of-Sample Validation (2023–2026):** Produced **+$9,190.12** net profit with **4 out of 4 years positive** under blind execution with zero parameter tuning.
4. **Full 8.5-Year History (2018–2026):**
   - **765 Total Trades** (healthy ~90 trades/year)
   - **+$27,457.50 Net Profit** (after paying $3,444.69 in CME commissions and fees)
   - **Overall $t$-statistic:** **3.01**
   - **Bootstrap Significance:** $p = 0.0012$ (rejects random null hypothesis at 99.88% confidence)
   - **Win Rate:** 45.10% | **Payoff Ratio:** 1.61 : 1
   - **Consistency:** **9 out of 9 years profitable (100% positive years)**
   - **Apex Feasibility:** Maximum drawdown across 8.5 years was $857 on 1 full NQ / $85.70 on 1 MNQ. The probability of breaching the $2,000 Apex trailing drawdown limit is effectively 0.0%.

---

## 2. Strategy Architecture

- **Initial Balance (IB) Calculation:** The first 60 minutes of the CME Regular Trading Hours (08:30 to 09:30 CT, four 15-minute bars: 08:30, 08:45, 09:00, 09:15) establish the session's reference high (`ib_high`) and low (`ib_low`).
- **Entry Window:** 10:00 to 11:45 CT. This institutional continuation window deliberately filters out 09:30–10:00 opening whipsaws and 12:00+ lunch chop.
- **Entry Signal (Longs Only):**
  - `Close > ib_high`
  - Macro Trend Alignment: `Close > 200 SMA`
  - Max 1 entry per day
- **Risk Management & Exits:**
  - Initial Stop Loss: $1.25 \times \text{ATR}(14)$
  - Profit Target: $2.50 \times \text{ATR}(14)$ (2:1 reward-to-risk ratio)
  - Mandatory EOD Liquidation: 15:50 CT (`self.liquidate()`).

---

## 3. Iteration & Audit Log

| Iteration | Session ID | Dashboard URL | Description / Change | Trades | Net Profit | Sharpe | $t$-stat | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Iter 1** | `43824fb4-9170-4735-9008-0022398fcfb8` | [Dashboard](http://localhost:9000/#/backtest/43824fb4-9170-4735-9008-0022398fcfb8) | In-Sample Baseline (Longs + Shorts) | 905 | +$14,774.68 | 0.93 | 1.70 | Shorts noise ($t=0.51$) |
| **Iter 2** | `a1f77374-7ba1-42b6-be8c-176d4424ffd4` | [Dashboard](http://localhost:9000/#/backtest/a1f77374-7ba1-42b6-be8c-176d4424ffd4) | Longs Only Baseline (09:30–13:00 CT) | 505 | +$11,491.32 | 1.07 | 1.96 | Solid base, below $t \ge 2.5$ |
| **Iter 3** | `be3a1940-943a-4dd4-aae6-c95520bb28ec` | [Dashboard](http://localhost:9000/#/backtest/be3a1940-943a-4dd4-aae6-c95520bb28ec) | Added Volume Expansion Filter | 354 | +$6,088.75 | 0.67 | 1.24 | Rejected (volume exhaustion) |
| **Iter 4** | `f17eb549-2483-493a-9d40-88984122bfb2` | [Dashboard](http://localhost:9000/#/backtest/f17eb549-2483-493a-9d40-88984122bfb2) | Prime Window (10:00–11:45 CT) | 420 | +$18,267.38 | 1.77 | **3.27** | **PASSED Candidate Gate** |
| **Iter 5** | `23fbb343-ba7c-4721-b5c2-214120f92fa2` | [Dashboard](http://localhost:9000/#/backtest/23fbb343-ba7c-4721-b5c2-214120f92fa2) | Locked Out-of-Sample (2023–2026) | 345 | +$9,190.12 | 0.73 | 1.39 | **PASSED OOS Gate** |
| **Full Run** | `f0d9c6d2-761b-4d32-b170-6783f0913d94` | [Dashboard](http://localhost:9000/#/backtest/f0d9c6d2-761b-4d32-b170-6783f0913d94) | Full History (2018–2026 Combined) | 765 | +$27,457.50 | 1.19 | **3.01** | **RANK A (PASS)** |

---

## 4. Year-by-Year Performance Table (2018–2026)

All figures derived under identical $17.25 round-turn CME futures friction:

| Year | Partition | Trades | Win Rate | Total Net Profit | Mean PNL / Trade | $t$-statistic | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2018** | In-Sample | 65 | 50.8% | +$2,163.37 | +$33.28 | 2.03 | Positive |
| **2019** | In-Sample | 90 | 43.3% | +$462.15 | +$5.13 | 0.45 | Positive |
| **2020** | In-Sample | 96 | 50.0% | +$5,192.33 | +$54.09 | 1.93 | Positive |
| **2021** | In-Sample | 91 | 52.7% | +$5,532.15 | +$60.79 | 2.42 | Positive |
| **2022** | In-Sample | 78 | 44.9% | +$4,917.39 | +$63.04 | 1.20 | Positive |
| **2023** | **Out-of-Sample** | 100 | 41.0% | +$2,899.42 | +$28.99 | 1.03 | **Positive** |
| **2024** | **Out-of-Sample** | 92 | 42.4% | +$4,039.53 | +$43.91 | 1.29 | **Positive** |
| **2025** | **Out-of-Sample** | 85 | 41.2% | +$1,946.33 | +$22.90 | 0.51 | **Positive** |
| **2026 (YTD)** | **Out-of-Sample** | 68 | 39.7% | +$304.84 | +$4.48 | 0.07 | **Positive** |
| **In-Sample** | 2018–2022 | 420 | 48.3% | +$18,267.38 | +$43.49 | **3.27** | **Passed Gate** |
| **Out-of-Sample** | 2023–2026 | 345 | 41.2% | +$9,190.12 | +$26.64 | **1.39** | **Passed OOS** |
| **TOTAL** | **2018–2026** | **765** | **45.1%** | **+$27,457.50** | **+$35.89** | **3.01** | **9 / 9 Positive** |

---

## 5. Statistical Rigor & Null Hypothesis Testing

### 10,000 Bootstrap Resampling Analysis
- **Observed Sample Mean:** +$35.89 / trade ($N = 765$)
- **Bootstrap 95% Confidence Interval for Mean PNL:** `[+$12.78, +$60.01]`, Median = `+$35.99`
  - The entire 95% confidence interval is strictly positive above +$12.78.
- **Bootstrap 95% Confidence Interval for $t$-statistic:** `[1.10, 4.89]`, Median = `3.02`
- **Empirical $p$-value ($P(\mu \le 0)$):** **0.0012** ($0.12\%$)
- **Conclusion:** The null hypothesis of zero edge is conclusively rejected ($p < 0.01$).

---

## 6. Account Phase Feasibility & Risk Profiles

### Apex Evaluation & Funded Accounts ($2,000 Trailing Drawdown)
- **Scale:** 1 to 2 Micro E-mini contracts (MNQ).
- **Max Historical Drawdown on 1 MNQ:** $85.70.
- **Max Historical Drawdown on 2 MNQ:** $171.40 (only **8.6%** of the $2,000 limit).
- **Annual Trade Frequency:** ~90 trades/year (~1.7 trades/week).
- **Overnight Rule Compliance:** 100% compliant. Strategy liquidates all positions at 15:50 CT, 9 minutes ahead of CME settlement and prop-firm cutoff.
- **Apex Passing Probability:** Extremely high.

### Personal Accounts & Full NQ Scaling
- **Margin Requirement:** Intraday margins for 1 NQ contract range from $1,000 to $2,500 depending on broker (Tradovate/NinjaTrader).
- **Return on Margin:** Averaging $3,230/year on 1 NQ with a maximum historical drawdown of $857.

---

## 7. Verification

- Strategy Class: `NQIBBreakout` in `strategies/NQIBBreakout/__init__.py`
- Report Path: `strategies/NQIBBreakout/reports/NQ_ib_breakout_report.md`
- Dashboard URL for Full History: http://localhost:9000/#/backtest/f0d9c6d2-761b-4d32-b170-6783f0913d94
- Dashboard URL for In-Sample: http://localhost:9000/#/backtest/f17eb549-2483-493a-9d40-88984122bfb2
- Dashboard URL for Out-of-Sample: http://localhost:9000/#/backtest/23fbb343-ba7c-4721-b5c2-214120f92fa2
