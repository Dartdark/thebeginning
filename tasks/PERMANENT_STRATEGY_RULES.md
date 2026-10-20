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
