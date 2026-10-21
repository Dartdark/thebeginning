# Permanent Quantitative Strategy Engineering Rules

These rules are mandatory for all strategy development, evaluation, and reporting. They were established following the empirical failure and audit of `NQBreakoutATR`, where selective windowing and overnight drift disguised an unviable strategy.

---

## 1. Full 2018–2026 Dataset (Zero Window Truncation)
- **Mandate**: Every backtest and validation must span the full available history (**2018-01-01 through 2026-10-09**).
- **Prohibited**: Never truncate windows (e.g., testing only 2019–2024 or 2021–2022) to avoid warm-up issues or hide recent performance degradation.
- **Reporting**: Always include a year-by-year breakdown. Every single negative year (e.g., 2025–2026) must be explicitly reported in the primary summary table.

---

## 2. Realistic Futures Transaction Costs & Commissions
- **Mandate**: Backtesting with `fee = 0` is strictly prohibited.
- **Contract Cost Model**:
  - **E-mini NQ**: Standard friction of **\$17.25 per round-turn** (commission + exchange/NFA fees + conservative 1-tick slippage).
  - **Micro MNQ**: Standard friction of **\$1.72 per round-turn**.
- Any strategy whose profit factor falls below 1.25 under real friction is deemed non-viable.

---

## 3. Mandatory Intraday Flattening (15:55 / 15:59 CT)
- **Mandate**: Strategies must enforce an end-of-day exit: `self.liquidate()` before 15:59 CT (typically at 15:50–15:55 CT).
- **The "Overnight Mirage" Rule**: 
  - Passive index appreciation occurs heavily overnight. If an intraday strategy profits solely because 20–25% of trades run overnight, it is **not alpha**—it is unhedged equity risk premium.
  - A strategy must prove positive expectancy on **same-day intraday trades alone**.

---

## 4. Benchmark Against Random Entries (Statistical Significance)
- **Mandate**: An entry signal must be statistically benchmarked against identical exits applied to **random entries** within the same trading window.
- **Threshold**: The signal must beat random entry distributions with statistical significance ($p < 0.05$). If random entries produce comparable expectancy, the entry signal has no predictive power.

---

## 5. Objective Monte Carlo Interpretation (Zero Overfit Denial)
- **Mandate**: Monte Carlo distributions must be interpreted honestly without rationalization.
- **Overfit Criteria**:
  - `original > median`: The backtest sits in the upper half of resampled outcomes. If `original` is substantially higher than `median` (e.g., 2.02 vs 0.83), the strategy is **heavily overfit or path-dependent**.
  - `original ≈ median`: The strategy is representative of typical price paths.
  - `original < median`: Conservative, genuine robustness.
- **Downside Tail**: The 5th-percentile outcome (`worst_5`) must not breach account survival limits.

---

## 6. Real-World Drawdown Sizing (Apex & Funded Account Realism)
- **Mandate**: Drawdown must be measured in **dollars per contract** ($ / NQ or $ / MNQ), never masked by arbitrary starting balances ($1,000,000).
- **Survival Standard**: On 1 MNQ, maximum peak-to-valley drawdown must never exceed the evaluation/funded account limit (e.g., **\$2,000 trailing drawdown**). Any strategy breaching this in $> 10\%$ of years is ranked **F**.

---

## 7. In-Sample vs. Out-of-Sample Decision Rule ($t \ge 2.5$ Gate)
- **Mandate**: Strict chronological split to prevent in-sample leakage and curve-fitting:
  - **In-Sample (IS) Window**: **2018-04-01 through 2022-12-31**. All architecture design, rule selection, and parameter testing must be evaluated on this period ALONE.
  - **In-Sample Candidate Gate**: A strategy is **ONLY a candidate if $t \ge 2.5$** (target $t \ge 3.6$, $p < 0.01$) on 2018–2022 data under real friction.
  - **Out-of-Sample (OOS) Validation**: **2023-01-01 through 2026-10-09**. Strictly locked. Tested once without changes. The strategy must remain profitable on 2023–2026.
- **Hard Stop Decision Rule**: If $t < 2.5$ on 2018–2022, OR if performance turns negative on 2023–2026 out-of-sample, the strategy **FAILS IMMEDIATELY and must be reported as Ranked F**. No rationalizations, no "viable seed", and no passing grade allowed.

---

## 8. Observable Search Denominator & Multiplicity Penalty (SignalLab Standard)
- **Mandate**: Every tested strategy, variation, parameter sweep, or filter combination—whether successful, shelved, or failed—must be logged in the centralized hypothesis registry (`tasks/SEARCH_DENOMINATOR_REGISTRY.csv`).
- **Search-Adjusted $t$-Hurdle**:
  - The evidentiary bar increases with the number of trials ($N$) evaluated:
    - $N = 1$ (single pre-registered thesis): $t \ge 2.50$ ($p \le 0.01$).
    - $N \ge 10$ (variant / sweep search): $t \ge 3.00$ (Harvey minimum Bayes factor bound).
    - $N \ge 100$: $t \ge 3.50$ (Harvey–Liu bootstrap / Bonferroni standard).
  - Reporting an edge from trial #15 out of 20 without adjusting the significance threshold for the 19 unselected variations is strictly prohibited.

---

## 9. Pre-Evaluation Economic Mechanism & Critic Gate
- **Mandate**: Prior to backtesting on historical price series, the researcher must declare the hypothesis triplet: $h_j = (m_j, e_j, d_j)$:
  1. **Economic Mechanism ($m_j$)**: A structural market justification (e.g., forced institutional flow, index rebalance, retail overnight imbalance, dealer hedging unwind). Pure statistical data patterns ("EMA 9 crossed EMA 21") without an economic mechanism are rejected.
  2. **Executable Expression ($e_j$)**: Explicit, unambiguous mathematical rule and entry/exit condition.
  3. **Declared Return Direction ($d_j \in \{-1, +1\}$)**: Must be specified *before* running data. Inverting the trade direction after seeing an unfavorable backtest is strictly prohibited.
- **Independent Critic Gate**: Before testing, an independent review (Claude or Antigravity) audits the mechanism for construct validity, measurement leakage, and redundancy against existing strategies. Flagged proposals must be revised before data execution.

---

## 10. Portfolio Spanning & Temporal Non-Decay Gate (The Institutional Funnel)
- **Mandate**: High standalone $t$-statistic is a necessary condition, but never sufficient. A strategy must survive the full institutional attrition funnel:
  1. **Temporal Stability & Non-Decay**: Performance must hold across multi-year sub-windows (e.g., 2018–2020, 2021–2023, 2024–2026). Rolling performance slope must not be negative ($t_{decay} > -1.96$).
  2. **Portfolio Spanning**: The strategy must provide incremental conditional alpha beyond the deployed live portfolio (`Vault Break`, `Overnight Bias`, `Relative Strength`, `Late-Day Flow`, `EOS`, `Monday Long`, `CL Gap Fade`). 
  3. **Funded Plan Bench**: Must be evaluated via 1,000 resampled iterations on the funded account simulator. If adding the strategy does not improve payout velocity or reduce blown-account probability without increasing peak-to-valley drawdown, it remains on the Watchlist and is NOT added to live charts.

---

## 11. Agent-Native Audit Trail with Minute-Level Timestamps
- **Mandate**: To ensure complete cross-agent auditability, every strategy evaluation must output a standardized `trades.csv` containing minute-level precision:
  - Required columns: `date, year, entry_time, exit_time, side, entry_px, exit_px, pts, pnl, reason`.
  - Timestamps must allow independent models and auditors (Claude/MultiCharts) to verify every entry, stop, and exit in minutes without ambiguity or guesswork.
