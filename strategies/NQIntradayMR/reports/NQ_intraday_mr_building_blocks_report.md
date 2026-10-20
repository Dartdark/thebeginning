# Quantitative Strategy Report: NQIntradayMR (Intraday Mean Reversion)

## STATUS: FAILED AUDIT — RANK F

> [!CAUTION]
> **Audit Failure Verdict**: This strategy fails the quantitative validation standard. Its previous "B+" rating has been officially revoked and degraded to **Rank F**. 
> - **In-Sample t-Statistic**: **t = 1.01** on 2018–2022 data alone (Standard candidate gate requires **t ≥ 2.5**, target **t ≥ 3.6**).
> - **Statistical Insignificance**: A t-statistic of 1.01 ($p = 0.31$) indicates that the results are statistically indistinguishable from luck.
> - **Extreme Year Clustering**: 2022 alone accounted for **70% of total 8.5-year profit** (\$5,992 of \$8,601).
> - **In-Sample Data Leakage**: Iterations (200 SMA trend filter, 2:1 target) were evaluated on the full 2018–2026 period rather than locked in-sample.

---

## 1. Executive Summary & Strategy Specification

- **Strategy Name**: `NQIntradayMR`
- **Asset**: CME Micro / E-mini Nasdaq-100 Futures (`NQ-USD` / `MNQ`)
- **Timeframe**: `15m`
- **Friction**: Realistic CME futures friction (`fee = 0.00003`, \$17.25 round-turn per NQ / \$1.72 per MNQ)
- **Mandate**: Intraday flat at 15:50 CT (0 overnight exposure)
- **Architecture**:
  - Entry: 8-bar low/high fade when volume < 10-bar SMA and ADX < 25
  - Filter: 200 SMA macro trend alignment
  - Exits: Stop at 1.25 $\times$ ATR, Target at 2.5 $\times$ ATR (2:1 R:R), flat at 15:50 CT

---

## 2. In-Sample vs. Out-of-Sample Audit (Rule 7 Enforcement)

| Dataset Partition | Date Window | Trades | Win Rate | Profit Factor | Net Profit (1 MNQ) | Expectancy / Trade | t-Statistic | Gate Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **In-Sample (IS)** | 2018-04-01 to 2022-12-31 | 143 | 40.6% | 1.26 | +\$847.99 | +\$5.93 | **t = 1.01** | **FAILED (Target t ≥ 2.5)** |
| **Out-of-Sample (OOS)** | 2023-01-01 to 2026-10-09 | 119 | 44.5% | 1.23 | +\$872.31 | +\$7.33 | **t = 0.90** | Unverified edge |
| **Combined 8.5 Years** | 2018-04-01 to 2026-10-09 | 262 | 42.4% | 1.25 | +\$1,720.30 | +\$6.57 | **t = 1.34** | **FAILED (p = 0.18)** |

---

## 3. Autopsy: Why NQIntradayMR Fails

1. **Failure of the t-Statistic Gate (t = 1.01 vs 2.50 threshold)**:
   - To prove that an edge is real rather than noise, a candidate strategy must achieve $t \ge 2.5$ ($p < 0.01$) on in-sample data (2018–2022).
   - `NQIntradayMR` achieved only $t = 1.01$. Its own statistics indicate a 31% probability that the in-sample profit was pure luck.
2. **Extreme Profit Concentration in 2022**:
   - The strategy was profitable in only 5 of 9 years.
   - Out of the \$8,601 total profit over 8.5 years, **\$5,991.62 came from 2022 alone** (a massive tech bear market with elevated volatility). Across all other 7.5 years combined, the strategy earned only \$2,609 total (~$50/year per MNQ).
3. **Severe Trade Starvation**:
   - At only ~31 trades per year (~2.5 trades/month), sample size accumulates too slowly to overcome variance or justify live prop capital deployment.
4. **Data Snooping Across the Whole Sample**:
   - Modifying the trend filter and exit brackets by inspecting full 2018–2026 runs created the illusion of improvement on data that should have remained strictly out-of-sample.

---

## 4. Final Verdict: Ranked F

Under Workspace Rule 7, any strategy with $t < 2.5$ in-sample fails automatically. `NQIntradayMR` is decommissioned.
