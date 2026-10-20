# Quantitative Audit & Failure Post-Mortem: NQBreakoutATR

> **STRATEGY STATUS**: **FAILED AUDIT (RANK: F)**  
> **CAUSE**: Overfitting to truncated 2019–2024 window, unmodeled transaction costs, unhedged overnight equity drift masquerading as breakout alpha, failure to beat random entries ($p = 0.11$), and severe Apex drawdown failure (breaches \$2,000 trailing drawdown in 36% of years).

---

## 1. The Audit Findings vs Reported Illusions

An independent, rigorous audit on the complete **2018–2026** dataset under realistic CME futures costs (\$17.25 round-turn per NQ contract) revealed that `NQBreakoutATR` completely fails.

### Rebuild Comparison Across Full History (2018–2026, \$17.25 Cost / NQ)

| Strategy Variant | Trades | Avg / NQ | Profit Factor | $t$-stat | Profitable Years | 2023+ Avg / NQ | Audit Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **As Coded (Runs Overnight)** | 1,830 | \$55 | 1.11 | 1.5 | 5 / 9 | \$24 ($t = 0.4$) | **FAIL** |
| **Without ADX + Time Filter** | 4,279 | \$57 | 1.11 | 2.4 | 6 / 9 | \$37 | **FILTER ADDS NO VALUE** |
| **Apex Compliant (Flat 15:55 CT)** | 1,877 | \$39 | 1.08 | 1.2 | 5 / 9 | **-\$3 / trade** | **CATASTROPHIC DECAY** |

---

## 2. Anatomical Autopsy of the Failures

### 1. The Truncated Window Illusion
- The original optimization was evaluated on 2019–2024 (and 2021–2022 discovery), which was the strategy's lone favorable stretch (\$113/trade).
- **The Hidden Reality**: In 2025 and 2026, the strategy experienced brutal regime decay, **losing -\$51,000 per NQ contract**. 2019–2020 was also unprofitable. Truncating the test period artificially created an illusion of multi-year profitability.

### 2. The Overnight Drift Mirage (Zero Intraday Alpha)
- The strategy lacked an end-of-day exit rule.
- **The Breakdown**:
  - The **23% of trades running overnight** earned **+\$1,055 each**.
  - The **77% of same-day intraday trades** actually **LOST -\$244 each**.
- What appeared to be a "breakout edge" was nothing more than passive long-bias equity drift during the overnight Globex session. When forced to close before the cash market close (15:55 CT), the strategy collapsed to **-\$3 per trade** from 2023 onward.

### 3. Failure to Beat Random Entries ($p = 0.11$)
- When benchmarked against random entries during the exact same hours with identical exits, random entries averaged **+\$12 / trade**.
- The real 10-bar Donchian rule beat random entries only **89% of the time** ($p = 0.11$). It fails standard statistical significance thresholds ($p < 0.05$).

### 4. The Regime Filter Was Inert
- Adding Filter Case 9128 (ADX > 30 + RTH window) produced \$55/NQ, while omitting it completely produced \$57/NQ. The filter merely eliminated trade volume without generating a single dollar of net alpha per contract.

### 5. Monte Carlo Denial of Overfitting
- The original Sharpe of **2.02** was more than **2.4x higher than the Monte Carlo median (0.83)**.
- In quantitative modeling, an original metric substantially higher than the median of resampled candle paths is the textbook signature of curve-fitting and lucky sample alignment. Rationalizing it as "not overfit" was an empirical failure.

### 6. Real-World Risk (Apex Drawdown Breach)
- On a single Micro contract (1 MNQ), the strategy would breach the **\$2,000 trailing drawdown in 36% of years**. It is completely unviable for prop firm evaluations, funded accounts, or personal capital.

---

## 3. Permanent Engineering Mandates Established

From this failure, six non-negotiable quantitative rules have been established in `tasks/PERMANENT_STRATEGY_RULES.md`:
1. **Full 2018–2026 Data Only**: Zero window truncation. Every bad year (2025, 2026, 2019) must be front and center.
2. **Realistic Costs**: Always backtest with realistic friction (\$17.25/NQ or \$1.72/MNQ).
3. **Mandatory Daily Flat (15:55 CT)**: Separate genuine intraday edge from passive overnight drift.
4. **Random Entry Benchmarking**: Must beat random entries with $p < 0.05$.
5. **Objective Monte Carlo**: A backtest beating the MC median by $2\times$ is overfit by definition.
6. **Dollar-Per-Contract Drawdown Tracking**: Must survive \$2,000 trailing drawdown limits on 1 MNQ.
