# Quantitative Strategy Validation & Account Phase Classification Mandates

These rules are mandatory for all futures strategy engineering, evaluation, and reporting. They enforce strict mathematical rigor, realistic friction, and proper phase classification across Evaluation, Funded, and Personal accounts.

---

## Rule 1: Full 2018–2026 Test Window (Zero Truncation)
- **Mandate**: Every strategy evaluation, benchmark, and report must span the entire available historical dataset (**2018-01-01 through 2026-10-09**).
- **Prohibited**: Never truncate date ranges (e.g., testing only 2019–2024 or 2021–2022) to avoid warm-up setup or bypass difficult market cycles.
- **Reporting**: Always include a year-by-year breakdown table for every single year (2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026). Every losing year must be prominently reported.

---

## Rule 2: Realistic Futures Friction & Commission Models
- **Mandate**: Backtesting with `fee = 0` is strictly prohibited.
- **Standard Cost Specifications**:
  - **E-mini NQ**: Minimum **$17.25 per round-turn** (exchange fees, NFA fees, broker commission, and 1-tick slippage).
  - **Micro MNQ**: Minimum **$1.72 per round-turn**.
  - **Crude Oil (CL) / Gold (GC)**: Minimum **$15.00 per round-turn**.
- Any strategy with an overall Profit Factor below **1.25** under real friction is classified as non-viable for any phase.

---

## Rule 3: Intraday vs. Overnight Transparency
- **Intraday Strategies (Phase 1 / Phase 2 Focus)**:
  - Must enforce a strict daily exit: `self.liquidate()` before 15:59 CT (scheduled between 15:50 and 15:55 CT).
  - Must prove positive expectancy on same-day trades alone. Passive index appreciation concentrates in overnight hours; an intraday breakout rule cannot use overnight holds to mask losing intraday trades.
- **Swing Strategies (Phase 3 Personal Account Focus)**:
  - Multi-day holds are permitted only when explicitly designed as a swing system.
  - Must report intraday vs. overnight P&L contributions separately to verify genuine alpha rather than pure equity beta.

---

## Rule 4: Random Entry Statistical Benchmark ($p < 0.05$)
- **Mandate**: Every entry signal must be tested against an identical number of random entries executed during the same trading window with identical exit rules.
- **Statistical Significance**: The entry signal must outperform random entry distributions with $p < 0.05$ (beating random entries $\ge 95\%$ of the time). If random entries produce comparable expectancy, the entry signal has no predictive edge and must be discarded.

---

## Rule 5: Objective Monte Carlo Interpretation (Zero Overfit Denial)
- **Mandate**: Monte Carlo resampled distributions must be interpreted objectively:
  - If `original > median` by a substantial margin (e.g., $> 1.3\times$), the strategy is **overfit or path-dependent**. Never rationalize an inflated original Sharpe by citing that it is below the 95th percentile (`best_5`).
  - An authentic, robust strategy exhibits `original ≈ median` or `original < median`.
  - The 5th-percentile downside tail (`worst_5`) must not breach account survival limits for its assigned phase.

---

## Rule 6: Account Phase Fit & Drawdown Classification
Drawdown must always be tracked and reported in **dollars per contract** ($ / NQ, $ / MNQ), never masked by arbitrary account balances ($1,000,000). Every viable strategy must be classified into its intended Phase:

1. **Phase 1 Fit: Evaluation (Apex / Prop Firms)**
   - Strict maximum trailing drawdown $\le \mathbf{\$2,000}$ per contract on 1 MNQ.
   - Mandatory flat by 15:55 CT.
   - Consistent trade frequency and positive expectancy across rolling 30-day windows.

2. **Phase 2 Fit: Funded Accounts (PA / Payout Extraction)**
   - Drawdown cushioned within funded payout threshold buffers.
   - Intraday or tightly hedged positions designed to protect payout consistency.

3. **Phase 3 Fit: Personal / Private Accounts**
   - Can accommodate wider dollar drawdowns (e.g., \$4,000–\$10,000+ per contract or swing multi-day holding).
   - Evaluated on long-term compound growth, multi-year Sharpe $> 1.25$, and full-cycle survival without prop firm rule constraints.

*A strategy is only ranked F if it fails statistical validity across ALL phases (e.g., negative in recent years, fails random entry test, or loses money under real costs).*
