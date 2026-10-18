# Book Summary: Advances in Financial Machine Learning (Marcos López de Prado, 2018)

**Title**: *Advances in Financial Machine Learning*  
**Author**: Marcos López de Prado  
**Publisher**: John Wiley & Sons, 2018 (ISBN: 978-1-119-48208-6)  
**Short Name**: `prado_afml`

---

## 1. What the Book Is About

Marcos López de Prado's *Advances in Financial Machine Learning* is a foundational treatise establishing the scientific and industrial standard for applying machine learning to financial markets. Moving away from the traditional model of individual researchers running isolated backtests, Prado outlines how institutional asset managers structure quantitative research like an industrial laboratory.

The book addresses the fundamental paradox of quantitative finance: while thousands of backtests boasting high Sharpe ratios are produced every year, the vast majority fail in live trading. Prado demonstrates that this widespread failure is not caused by weak ML algorithms, but by the naive application of general-purpose computer science techniques to non-IID, non-stationary, and path-dependent financial data. The book provides mathematically rigorous solutions spanning the entire quantitative pipeline: data curation, labeling, feature engineering, cross-validation, bet sizing, backtesting diagnostics, and structural risk management.

---

## 2. Main Claims and Theoretical Foundations

1. **Financial Data Is Not IID**: Standard machine learning assumes samples are independently and identically distributed. Financial observations overlap in time, exhibit heavy serial correlation, and suffer from structural regime shifts.
2. **Time Bars Are Statistically Flawed**: Sampling markets at fixed chronological intervals (e.g., 1-minute or daily bars) is an arbitrary artifact of pre-electronic trading. Time bars are severely heteroscedastic and oversample quiet periods while undersampling volatile bursts. Information-driven sampling (volume bars, dollar bars, imbalance bars) restores Gaussian-like statistical properties and synchronizes data with the arrival of informed traders.
3. **The Stationarity vs. Memory Dilemma**: Traditional econometrics differences price series ($d=1$) to achieve stationarity for regression models. However, integer differentiation obliterates all long-term memory (macroeconomic cycles, price anchors). **Fractional Differentiation** ($0 < d < 1$) finds the minimal degree of differentiation required to achieve stationarity while preserving maximum historical predictive memory.
4. **Labeling Must Be Path-Dependent (The Triple-Barrier Method)**: Fixed-time horizon labels ($r_t = p_{t+h}/p_t - 1$) ignore what occurs between $t$ and $t+h$. The Triple-Barrier Method brackets every trade with two dynamic volatility-scaled horizontal barriers (profit-taking and stop-loss) and one vertical barrier (holding-period limit), matching real-world trading constraints.
5. **Decoupling Side from Size (Meta-Labeling)**: Machine learning models should not be forced to predict both direction and position sizing simultaneously. A primary fundamental or econometric model should determine trade direction (maximizing recall), while a secondary ML model learns when to bet and how much to size (maximizing precision and filtering false positives).
6. **Standard Cross-Validation Leaks Information**: Standard K-Fold CV randomly splits data, causing extreme lookahead leakage because overlapping labels in the training set contain information about testing observations. Practitioners must use **Purged and Embargoed K-Fold Cross-Validation** and **Combinatorial Purged Cross-Validation (CPCV)** to generate valid out-of-sample performance paths.
7. **Backtesting Is an Audit Tool, Not a Discovery Tool**: Using a historical backtest to search for profitable parameters guarantees backtest overfitting. Overfitting probability can be measured via the **Probability of Backtest Overfitting (PBO)** and the **Deflated Sharpe Ratio (DSR)**, which penalizes performance for the number of historical trials tested.

---

## 3. General Advice vs. Trading Rules

Prado explicitly separates methodological principles and research hygiene from specific trading implementations:

### A. Data Curation & Feature Engineering (Chapters 2, 4, 5, 8)
- **Bar Construction**: Shift away from calendar-time bars to volume bars, dollar bars, and information-driven imbalance/runs bars to stabilize variance.
- **Sample Weighting by Uniqueness**: Because trade holding periods overlap, observations share common return innovations. Training samples must be weighted by their average uniqueness ($u_i$) and absolute attribution to prevent bagging classifiers from overfitting identical historical market moves.
- **Fractional Differentiation ($d$)**: Systematically determine the minimum $d \in (0, 1)$ that achieves stationarity via the Augmented Dickey-Fuller test ($p < 0.05$) while preserving maximum correlation with the original series.
- **Feature Importance Diagnostics**: Standard Mean Decrease Impurity (MDI) is biased toward high-cardinality features. Prado advocates **Mean Decrease Accuracy (MDA)** and **Single Feature Importance (SFI)** to guard against collinearity and substitution effects.

### B. Validation, Overfitting & Multiple Testing Hygiene (Chapters 7, 11, 12, 14)
- **Purging and Embargoing**: Purge all training observations whose label evaluation window overlaps with the test set; embargo training observations immediately following the test set to account for auto-regressive memory.
- **Combinatorial Purged Cross-Validation (CPCV)**: Given $N$ splits and $k$ testing groups, generate all $\binom{N}{k}$ combinations to produce thousands of historical out-of-sample equity paths, establishing the full distribution of performance.
- **Deflated Sharpe Ratio (DSR)**: A reported Sharpe ratio is meaningless without knowing the number of trials tried. DSR deflates the Sharpe ratio based on non-normality (skewness, kurtosis), sample length, and the variance of Sharpe ratios across all historical attempts.
- **Backtest Fallacies ("The Seven Sins")**: Backtesting is not a research tool; simulating a strategy on historical data should only be executed once the entire strategy has been formulated, calibrated on synthetic data, and audited.

### C. Bet Sizing, Strategy Risk & Asset Allocation (Chapters 10, 15, 16)
- **Probabilistic Bet Sizing**: Bet size should be mapped continuously from the ML classifier's predicted probability using a standard normal CDF transform ($m = 2Z[z] - 1$). Discretize bet sizes into stepped buckets to eliminate excessive transaction costs from noise rebalancing.
- **Strategy Risk vs. Portfolio Risk**: Strategy risk is the probability that a strategy will fail to achieve its target Sharpe ratio ($P[p < p^*]$), derived by modeling trade precision and asymmetric payouts through a binomial process, independent of short-term portfolio volatility.
- **Hierarchical Risk Parity (HRP)**: Markowitz quadratic optimization is fatally flawed because inverting an empirical covariance matrix treats all assets as fully connected, magnifying small estimation errors. HRP applies machine learning graph theory (hierarchical tree clustering on correlation distances, quasi-diagonalization, and recursive bisection) to allocate risk robustly without matrix inversion.
