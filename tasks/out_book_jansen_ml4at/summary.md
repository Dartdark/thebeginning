# Stefan Jansen - Machine Learning for Algorithmic Trading (2nd ed., 2020)
Short name: `jansen_ml4at`
Book: Stefan Jansen, *Machine Learning for Algorithmic Trading: Predictive models to extract signals from market and alternative data for systematic trading with Python*, 2nd ed., Packt Publishing, 2020. ISBN: 978-1-83921-771-5.

---

## 1. What the Book Is About

Stefan Jansen’s *Machine Learning for Algorithmic Trading* is an encyclopedic guide to designing, implementing, and backtesting systematic trading strategies using Python. Across 23 chapters and over 800 pages, the book covers the entire modern quantitative investment pipeline:
- **Data Engineering**: Sourcing, parsing, and storing market microstructure (Nasdaq ITCH, AlgoSeek tick/minute data), fundamental data (SEC 10-K/10-Q XBRL), and alternative data (satellite imagery, geolocation, OpenTable bookings, financial news, and earnings calls).
- **Alpha Factor Research**: Generating technical, fundamental, and alternative alpha factors, evaluating them rigorously with information theory, mutual information, and `Alphalens` factor tear sheets.
- **Machine Learning Models**: Spanning linear models (Ridge, Lasso, Fama-MacBeth), time-series econometrics (ARIMA, GARCH, cointegration, Kalman filters), tree ensembles (Random Forests, XGBoost, LightGBM, CatBoost), unsupervised learning (PCA, Hierarchical Risk Parity), natural language processing (Loughran-McDonald dictionaries, Word2Vec, GloVe), deep learning (MLPs, CNNs, LSTMs, Autoencoders, TimeGANs), and reinforcement learning (Double Deep Q-Networks).
- **Strategy Backtesting & Portfolio Management**: Simulating execution in `Zipline` and `Backtrader`, managing risk with mean-variance optimization and risk parity, and evaluating performance in `pyfolio`.

---

## 2. Main Claims and Core Findings

1. **Alpha Factors Are Fleeting**: Standalone single-factor anomalies (simple moving average crosses, standalone RSI or MACD) have largely been arbitraged away in liquid public equity and futures markets. Modern systematic trading requires combining dozens of weakly predictive, low-correlation features into unified predictive models.
2. **Information Coefficient (IC) Dictates Strategy Viability**: Across all machine learning models tested (from linear regression to deep neural networks), out-of-sample monthly rank correlation (Information Coefficient) rarely exceeds 0.02 to 0.05 on individual stocks. Even modest ICs can generate high Sharpe ratios, but only if applied across hundreds of liquid assets with strict transaction cost management.
3. **Complexity Does Not Guarantee Alpha**: Deep neural networks (CNNs, LSTMs, DDQN) often underperform simpler, regularized models (Ridge regression, LightGBM) out-of-sample due to non-stationarity, low signal-to-noise ratios, and regime shifts. Tree-based gradient boosting (LightGBM) consistently offers the best trade-off between expressive non-linear power, training speed, and generalization.
4. **Transaction Costs Destroy Naive ML**: Models optimized purely on predictive accuracy ($R^2$ or classification accuracy) frequently generate excessive turnover, trading on high-frequency noise. Once realistic bid-ask spreads, exchange fees, and market impact are incorporated, high-turnover strategies almost invariably fail.

---

## 3. General Advice vs. Trade Rules

A massive portion of Jansen’s book constitutes rigorous quantitative engineering methodology rather than standalone directional trade rules. These best practices provide critical institutional standards:

### A. Backtesting Hygiene & Walk-Forward Validation
- **Lookahead Bias & Data Snooping**: Never compute rolling statistics, z-scores, or normalizations across the entire dataset prior to cross-validation. Normalization parameters ($\mu, \sigma$, min/max) must be fit strictly on in-sample training splits.
- **Purged and Embargoed Cross-Validation**: Standard k-fold cross-validation is completely invalid for financial time series due to serial correlation. Training and test sets must be separated by an embargo window to eliminate data leakage across overlapping return horizons.
- **Point-in-Time Data**: Fundamental data and economic indicators must be lagged to their actual public disclosure dates (incorporating publication reporting lag and filing revision history).

### B. Alpha Factor Evaluation with Alphalens
- Before building a strategy, evaluate raw alpha factor quality using the **Information Coefficient (Spearman rank correlation)** between factor ranks and forward asset returns.
- Evaluate factor monotonicity: assets sorted into quantiles by factor value must exhibit monotonically increasing forward returns. If quantiles 2, 3, and 4 exhibit erratic returns, the factor is noisy and prone to overfitting.
- Track factor turnover: calculate the autocorrelation of factor ranks across time. High turnover implies excessive trading costs to maintain factor exposures.

### C. Portfolio Construction & Risk Sizing
- **Covariance Inversion Pitfall**: Standard Markowitz mean-variance optimization requires inverting a sample covariance matrix. In financial data, small estimation errors in correlation are magnified into massive, unstable portfolio weights. Marcos López de Prado's **Hierarchical Risk Parity (HRP)** replaces matrix inversion with hierarchical tree clustering, offering robust out-of-sample risk balancing.
- **Dynamic Volatility Scaling**: Financial returns exhibit strong volatility clustering ($\text{GARCH}(1,1)$). Static contract sizing exposes accounts to catastrophic tail risk during volatility spikes; position sizes must scale inversely with conditional volatility ($\text{Size}_t \propto 1/\sigma_t$).
- **Kelly Sizing Realities**: Full Kelly sizing maximizes long-term compound growth but suffers from brutal ~33% to 50% drawdowns. Real-world prop firm implementations require fractional Kelly (e.g. 10% to 20% Kelly or risk-budgeted cushion sizing) to prevent account termination.
