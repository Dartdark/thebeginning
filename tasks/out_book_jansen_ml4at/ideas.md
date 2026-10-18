# Stefan Jansen - Machine Learning for Algorithmic Trading (2nd ed., 2020)
Short name: `jansen_ml4at`
Book: Stefan Jansen, *Machine Learning for Algorithmic Trading: Predictive models to extract signals from market and alternative data for systematic trading with Python*, 2nd ed., Packt Publishing, 2020. ISBN: 978-1-83921-771-5.

---

### 1. Fama-French Cross-Sectional Multi-Factor Strategy
- Where: Chapter 4 ("Financial Feature Engineering - How to Research Alpha Factors", pp. 88-124) & Chapter 7 ("Linear Models - From Risk Factors to Return Forecasts", pp. 166-200)
- Quote: "To estimate the relationship between the price of security and the forces included in the five-factor model such as firm size, value-versus-growth dynamic, investment policy and profitability, in addition to the broad market, we can use the portfolio returns provided by Kenneth French's data library as exogenous variables in a rolling linear regression."
- Rule as written:
  - Market: US equity universe (large/mid-cap liquid stocks).
  - Bar size: Monthly returns (computed from daily adjusted close).
  - Entry: Estimate rolling factor betas (24 to 60-month window) for the 5 Fama-French factors: Market excess return (Mkt-RF), Size (SMB - Small Minus Big), Value (HML - High Minus Low), Profitability (RMW - Robust Minus Weak), and Investment (CMA - Conservative Minus Aggressive), plus Carhart Momentum (WML) and Short-Term Reversal (ST_Rev). Sort universe into deciles or quintiles by expected return / factor exposure. Go long top quintile, short bottom quintile (dollar-neutral).
  - Exit: Rebalance portfolio monthly on the first trading day of each month.
  - Stop loss: None stated (portfolio rebalanced periodically).
  - Sizing: Equal-weighted within quintile or inverse-volatility weighted.
  - Holding time: 1 month (21 trading days).
- Book's evidence: Kenneth French data library historical returns (1963-2019). Reported annualized return spreads between top and bottom quintiles ranging from 3% to 8% historically across factors, with factor decay documented post-2000.
- Mechanism (the book's): Risk compensation and behavioral anomalies. Fama and French argue size and value represent compensation for undiversifiable distress risk; behavioral literature attributes momentum and reversal to investor cognitive biases (underreaction to news followed by delayed overreaction).
- Mechanism (my inference): None needed; book provides standard academic equilibrium and behavioral explanations.
- Apex fit: No. Holds dozens of individual equities long and short across monthly intervals. Cannot trade on Apex (Apex trades outright futures: NQ/ES/CL/GC/ZN). Violates the mandatory daily closeout rule (flat by 15:59 CT).
- Already tested? No (matches multi-day equity cross-sectional factor investing, not intraday futures).

---

### 2. Mean-Variance Optimization & Risk Parity Asset Allocation
- Where: Chapter 5 ("Portfolio Optimization and Performance Evaluation", pp. 125-165)
- Quote: "The risk parity approach allocates capital such that each asset or asset class contributes an equal amount of risk to the overall portfolio... Unlike mean-variance optimization, it does not rely on expected return estimates, which are notoriously difficult to predict."
- Rule as written:
  - Market: Multi-asset universe (equities, bonds, real estate, commodities).
  - Bar size: Daily or monthly returns.
  - Entry: Estimate asset covariance matrix $\Sigma$. In Mean-Variance Optimization, solve $\max w^T \mu - \frac{\lambda}{2} w^T \Sigma w$ subject to budget $\sum w_i = 1$. In Risk Parity (Equal Risk Contribution), solve for weights $w$ such that $w_i (\Sigma w)_i = \frac{1}{N} w^T \Sigma w$ for all $i$.
  - Exit: Periodic rebalancing (monthly, quarterly, or when asset risk contributions deviate past predefined bandwidth).
  - Stop loss: None stated.
  - Sizing: Derived directly from the optimization solution weights $w$.
  - Holding time: Multi-month / multi-year continuous allocation.
- Book's evidence: Evaluated on ETF baskets representing US Equities (SPY), Treasuries (IEF, TLT), Real Estate (VNQ), and Commodities (DBC) from 2000 to 2019 using `pyfolio`. Risk parity reduced maximum drawdown from -50% (60/40 equity-heavy) to approximately -18% during the 2008 crisis.
- Mechanism (the book's): Equities dominate ~90% of the risk in traditional market-cap weighted portfolios. Equalizing marginal risk contributions prevents single-asset drawdown contagion and exploits the diversification benefit of uncorrelated return streams.
- Mechanism (my inference): None needed; book states structural portfolio risk balance.
- Apex fit: No. Portfolio allocation and sizing framework across multiple asset classes over long horizons. Not an intraday directional trading rule. Apex trades single intraday futures contracts with a $2,000 drawdown limit.
- Already tested? No.

---

### 3. Regularized Linear Regression (Ridge & Lasso) Return Forecasting
- Where: Chapter 7 ("Linear Models - From Risk Factors to Return Forecasts", pp. 166-200) & Chapter 8 ("The ML4T Workflow - From Model to Strategy Backtesting", pp. 201-224)
- Quote: "Linear regression models with L1 (Lasso) and L2 (Ridge) regularization predict future returns based on lagged returns, technical indicators, and fundamental data, mitigating overfitting by shrinking coefficients toward zero."
- Rule as written:
  - Market: US equities (universe of top 500 liquid stocks from Quandl / US Equities bundle).
  - Bar size: Daily close / monthly resampled data.
  - Features: Rolling 1- to 12-month returns, 5-day and 21-day RSI, Bollinger Band bandwidth, MACD signal, ATR, and fundamental ratios.
  - Model: Ridge regression ($\min \|y - X\beta\|_2^2 + \alpha \|\beta\|_2^2$) and Lasso ($\min \|y - X\beta\|_2^2 + \lambda \|\beta\|_1$). Hyperparameters tuned via walk-forward rolling cross-validation. Target is 1-month forward return.
  - Entry: Rank universe by predicted forward return on the first trading day of the month. Long top decile (top 10%), short bottom decile (bottom 10%), dollar-neutral equal-dollar weighting.
  - Exit: Rebalance portfolio monthly on schedule.
  - Stop loss: None stated.
  - Sizing: Dollar-neutral portfolio allocation ($w_i = +1/(2N_{\text{long}})$ for longs, $-1/(2N_{\text{short}})$ for shorts).
  - Holding time: 1 month (21 trading days).
- Book's evidence: Backtested in Zipline (2010-2017). Information Coefficient (IC) achieved 0.02 to 0.04 out-of-sample. Annualized Sharpe ratio was 0.72 before transaction costs; dropped significantly when standard 5 bps per trade slippage/costs were applied.
- Mechanism (the book's): Regularization penalizes collinear and noisy features, extracting genuine cross-sectional alpha from price momentum and mean-reverting technical anomalies across hundreds of liquid equities.
- Mechanism (my inference): None needed; book explains bias-variance tradeoff and cross-sectional anomaly aggregation.
- Apex fit: No. Multi-day holding period (21 days) across a broad equity basket. Violates flat by 15:59 CT daily closeout. Not applicable to outright intraday index futures.
- Already tested? No (matches multi-day equity ML portfolios).

---

### 4. GARCH(1,1) Volatility Timing & Dynamic Risk Scaling
- Where: Chapter 9 ("Time-Series Models for Volatility Forecasts and Statistical Arbitrage", pp. 225-257)
- Quote: "The GARCH model captures volatility clustering—the observation that large price changes tend to be followed by large price changes, of either sign, and small changes tend to be followed by small changes... Volatility forecasts allow systematic strategies to scale position sizes inversely to current market risk."
- Rule as written:
  - Market: Broad market equity indices (S&P 500 / NASDAQ) or individual liquid assets.
  - Bar size: Daily returns.
  - Model: GARCH(1,1) process: $\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$, estimated via maximum likelihood.
  - Entry / Sizing rule: Forecast forward conditional volatility $\hat{\sigma}_{t+1}$. Dynamically size positions inversely proportional to forecast volatility: $\text{Size}_t = \text{Target Volatility} / \hat{\sigma}_{t+1}$. Alternatively, define volatility threshold $\sigma_{\text{cutoff}}$; halt or exit long positions when $\hat{\sigma}_{t+1} > \sigma_{\text{cutoff}}$.
  - Exit: Position adjusted daily based on updated $\hat{\sigma}_{t+1}$.
  - Stop loss: Not stated as fixed points; risk controlled via dynamic deleveraging.
  - Holding time: Daily continuous updating.
- Book's evidence: Fitted to S&P 500 daily returns (1988-2019). Reported parameters $\alpha \approx 0.10$, $\beta \approx 0.88$, confirming strong volatility persistence ($\alpha + \beta \approx 0.98$). Volatility-targeted portfolios displayed substantially lower maximum drawdown compared to unhedged static buy-and-hold during the 2008 and 2011 market selloffs.
- Mechanism (the book's): Volatility clustering is driven by the arrival of market news and the time required for market participants to reach price consensus. High volatility environments exhibit asymmetric downside skew and liquidity dry-ups.
- Mechanism (my inference): None needed; book outlines volatility clustering and risk parity mechanics.
- Apex fit: Sizing/risk filter only (not a directional trade signal). Can dynamically scale intraday MNQ contract count or widen/tighten stop distance. As a standalone directional rule: No.
- Already tested? Mentioned in brief ("only volatility persists", but regime filters failed).

---

### 5. Cointegration & Statistical Arbitrage Pairs Trading
- Where: Chapter 9 ("Time-Series Models for Volatility Forecasts and Statistical Arbitrage - Statistical arbitrage with cointegration", pp. 248-257)
- Quote: "Pairs trading identifies two comoving assets whose price relationship is stationary. When the price spread diverges beyond two standard deviations from its historical mean, the strategy buys the undervalued asset and sells the overvalued asset, anticipating mean reversion to the equilibrium relationship."
- Rule as written:
  - Market: Pairs of liquid equities or sector ETFs (e.g. energy or utility stocks).
  - Bar size: Daily close.
  - Pair selection: Engle-Granger two-step method. Step 1: OLS regression $P_{1,t} = \alpha + \gamma P_{2,t} + \epsilon_t$. Step 2: Augmented Dickey-Fuller (ADF) test on residuals $\epsilon_t$ to confirm stationarity ($p < 0.05$).
  - Spread calculation: $S_t = P_{1,t} - \gamma P_{2,t}$. Compute rolling mean $\mu_S$ and rolling standard deviation $\sigma_S$ over lookback window (e.g. 60 days). Normalized spread: $z_t = (S_t - \mu_S) / \sigma_S$.
  - Entry: When $z_t \le -2.0$, buy asset 1 and short $\gamma$ units of asset 2. When $z_t \ge +2.0$, short asset 1 and buy $\gamma$ units of asset 2.
  - Exit: When $z_t$ crosses 0 (reverts to mean), or hit stop loss if $|z_t| \ge 3.0$ or maximum holding period (e.g. 30 days) is reached.
  - Sizing: Dollar-neutral weighting adjusted by hedge ratio $\gamma$.
  - Holding time: Typically 3 to 20 trading days.
- Book's evidence: Backtested in Backtrader on selected cointegrated US stock pairs. Showed positive returns during normal markets, but highlighted severe tail risk when cointegrating relationships broke down permanently during corporate events or regime shifts.
- Mechanism (the book's): Cross-asset economic substitution. Competing companies in the same industry share common cost and revenue drivers; divergence reflects temporary order flow imbalances or noise trader activity that rational arbitrageurs trade back to parity.
- Mechanism (my inference): None needed; book explains common factor exposure and cross-sectional arbitrage.
- Apex fit: No. Requires simultaneous long/short legs in two assets, holding positions overnight across multiple days until mean reversion. Violates flat by 15:59 CT daily closeout. Crucially, explicitly barred by brief: "Already tested and failed: mean reversion on NQ / ES".
- Already tested? Yes ("Already tested and failed: mean reversion on NQ / ES").

---

### 6. Dynamic Pairs Trading with the Kalman Filter
- Where: Chapter 10 ("Bayesian ML - Dynamic Sharpe Ratios and Pairs Trading", pp. 258-285)
- Quote: "The Kalman filter provides an online estimate of the time-varying hedge ratio between two assets without requiring arbitrary fixed rolling windows. By dynamically adjusting the hedge ratio to recent market conditions, it improves spread stationarity for statistical arbitrage."
- Rule as written:
  - Market: Liquid ETF pairs (e.g. EWA and EWC) or equity pairs.
  - Bar size: Daily close.
  - Model: State space model where the state vector represents the time-varying hedge ratio $\beta_t = [\alpha_t, \gamma_t]^T$, evolving as a random walk: $\beta_t = \beta_{t-1} + w_t$ with state noise covariance $W$. Observation equation: $y_t = x_t \beta_t + v_t$ with measurement variance $V$.
  - Spread & Error: Measurement error $e_t = y_t - \hat{y}_t$ and variance of prediction error $Q_t$. Normalized prediction error: $z_t = e_t / \sqrt{Q_t}$.
  - Entry: If $z_t \le -2.0$, buy asset $y$ and short $\hat{\gamma}_t$ of asset $x$. If $z_t \ge +2.0$, short asset $y$ and buy $\hat{\gamma}_t$ of asset $x$.
  - Exit: Exit when $z_t$ crosses 0.
  - Stop loss: Exit if $|z_t| \ge 3.0$ (breakdown of cointegration).
  - Sizing: Proportional to hedge ratio $\hat{\gamma}_t$.
  - Holding time: Multi-day (average 5 to 15 days).
- Book's evidence: Evaluated on EWA (Australia ETF) vs EWC (Canada ETF) commodity currency pairs. Kalman filter adapted faster to commodity regime shifts than 60-day rolling OLS, reducing spread drawdown by ~30%.
- Mechanism (the book's): Dynamic Bayesian state updating allows continuous tracking of evolving economic relationships without the lag or arbitrary lookback windows of rolling regressions.
- Mechanism (my inference): None needed; book provides state space filtering mechanics.
- Apex fit: No. Overnight multi-day spread trading requiring two simultaneous legs. Violates flat by 15:59 CT daily. Furthermore, barred by the brief's prohibition on mean reversion.
- Already tested? Yes ("Already tested and failed: mean reversion on NQ / ES").

---

### 7. Random Forest Long-Short Strategy for Japanese Equities
- Where: Chapter 11 ("Random Forests - A Long-Short Strategy for Japanese Stocks", pp. 286-324)
- Quote: "We apply random forests to monthly stock returns of Japanese companies from 2000 to 2019 using technical indicators and factor exposures... The strategy constructs a long-short portfolio by buying the top quintile of predicted performers and shorting the bottom quintile, rebalancing monthly."
- Rule as written:
  - Market: Japanese equities (TOPIX universe, ~1,000 liquid stocks).
  - Bar size: Monthly resampled bars.
  - Features: 20+ features including 1- to 12-month historical returns, 14-day RSI, MACD histogram, Bollinger Band %B, ATR, historical volatility, and sector indicators.
  - Model: Random Forest Regressor / Classifier (scikit-learn / LightGBM) trained with rolling purged cross-validation (5-year rolling train, 1-year test). Target is 1-month forward return.
  - Entry: On the first trading day of the month, rank universe by model prediction. Long top quintile (top 20%), short bottom quintile (bottom 20%).
  - Exit: Rebalance monthly at month-end.
  - Stop loss: None stated.
  - Sizing: Equal dollar weighting within each quintile, dollar-neutral (50% long, 50% short).
  - Holding time: 1 month (21 trading days).
- Book's evidence: Backtested in Zipline and evaluated in `pyfolio` (2000-2019). Reported annualized out-of-sample Sharpe ratio around 0.65 (gross of fees). Performance deteriorated in post-2015 period due to increased quantitative competition and lower market volatility.
- Mechanism (the book's): Non-linear feature interactions. Tree ensembles capture complex non-linear combinations between short-term mean reversion and medium-term momentum without requiring prior parametric assumptions.
- Mechanism (my inference): None needed; book details non-linear factor interactions.
- Apex fit: No. Equity stock-picking portfolio across hundreds of Japanese stocks held over 1-month rebalancing intervals. Violates flat by 15:59 CT daily closeout.
- Already tested? No.

---

### 8. Gradient Boosting (LightGBM) Intraday Return Forecasting
- Where: Chapter 12 ("Boosting Your Trading Strategy - Boosting for an intraday strategy", pp. 325-364)
- Quote: "We use AlgoSeek minute bars to compute features reflecting order flow, price discovery, and trade intensity... A LightGBM model predicts forward returns over 1- to 5-minute horizons, generating intraday trading signals based on order flow imbalance and short-term price momentum."
- Rule as written:
  - Market: Nasdaq-100 equities (high-frequency AlgoSeek 1-minute quote and trade data).
  - Bar size: 1-minute bars (9:30 to 16:00 ET).
  - Features: Order book depth, bid-ask spread, trade volume, trade size, relative volume, short-term RSI (5, 15 min), and order flow imbalance: "the difference between shares traded at the ask and bid price divided by total volume".
  - Model: LightGBM gradient boosted decision tree predicting forward 1-minute and 5-minute forward VWAP returns. Walk-forward cross-validation with daily retraining.
  - Entry: Buy when predicted forward 1-minute/5-minute return exceeds positive threshold $+k$; short when predicted return falls below negative threshold $-k$.
  - Exit: Exit after fixed holding period of 1 to 5 minutes, or at the 16:00 ET market close.
  - Stop loss: None explicitly modeled in the chapter (pure signal-based exit).
  - Sizing: Fixed dollar size per signal.
  - Holding time: 1 to 5 minutes (strictly intraday).
- Book's evidence: Evaluated on high-frequency Nasdaq equity data. Achieved Information Coefficient (IC) of 0.03 to 0.06 at 1-minute horizon; IC decayed rapidly to near zero past 15 minutes. Profitable gross of trading costs, but execution slippage and bid-ask spread crossing severely degraded net PnL.
- Mechanism (the book's): Market microstructure liquidity consumption. Aggressive market orders hitting the bid or lifting the ask consume limit order depth, creating short-term order imbalance that forces prices to move in the direction of the aggressive order flow.
- Mechanism (my inference): None needed; book details order book imbalance and market microstructure liquidity dynamics.
- Apex fit: No. While it is strictly intraday, it directly triggers the brief's explicit prohibition: "Already tested and failed: order-flow indicator filters". Furthermore, the primary signal feature is order-flow trade classification (shares traded at ask vs bid), which failed on NQ futures after transaction costs.
- Already tested? Yes ("Already tested and failed: order-flow indicator filters").

---

### 9. Hierarchical Risk Parity (HRP) Asset Allocation
- Where: Chapter 13 ("Data-Driven Risk Factors and Asset Allocation with Unsupervised Learning - Hierarchical Risk Parity", pp. 365-397)
- Quote: "Hierarchical Risk Parity (HRP) uses machine learning to address the instability of mean-variance optimization caused by covariance matrix inversion... It organizes assets into a hierarchical tree based on their correlation distance, clusters similar assets, and allocates weights using recursive bisection."
- Rule as written:
  - Market: Multi-asset universe (equities, bonds, currencies, commodities ETFs).
  - Bar size: Daily returns.
  - Algorithm (Marcos López de Prado):
    1. Tree Clustering: Compute correlation matrix $C$. Convert to correlation distance $D(i,j) = \sqrt{\frac{1}{2}(1 - C_{i,j})}$. Cluster assets using hierarchical tree clustering (Ward's linkage or single linkage).
    2. Quasi-Diagonalization: Reorganize the rows and columns of the covariance matrix so that highly correlated assets are grouped together along the diagonal.
    3. Recursive Bisection: Split asset tree into two sub-clusters. Allocate capital between the two clusters inversely proportional to their aggregate cluster variance. Recursively bisect sub-clusters until individual asset weights are assigned.
  - Exit / Rebalance: Monthly or quarterly rebalancing.
  - Stop loss: None stated.
  - Sizing: Weights $w_i$ output by the recursive bisection algorithm.
  - Holding time: Multi-month continuous allocation.
- Book's evidence: Evaluated on a diverse 10-ETF asset allocation universe (1998-2018). HRP achieved higher out-of-sample Sharpe ratio (0.84) and lower maximum drawdown (-15.2%) than traditional Markowitz mean-variance optimization (Sharpe 0.62, max DD -27.4%) and equal-risk parity.
- Mechanism (the book's): Eliminates matrix inversion. Standard Markowitz quadratic optimization inverts a sample covariance matrix, magnifying estimation errors into extreme, unstable asset weights. HRP replaces matrix inversion with hierarchical tree traversal, ensuring stable weights even with collinear assets.
- Mechanism (my inference): None needed; book provides full algorithmic and mathematical rationale.
- Apex fit: No. Portfolio-level multi-asset allocation framework over multi-month horizons. Not an intraday single-instrument directional strategy.
- Already tested? No.

---

### 10. Financial Text NLP Sentiment Event Strategy
- Where: Chapter 14 ("Text Data for Trading - Sentiment Analysis", pp. 398-433) & Chapter 16 ("Word Embeddings for Earnings Calls and SEC Filings", pp. 466-499)
- Quote: "Loughran and McDonald (2011) showed that general-purpose sentiment dictionaries misclassify financial texts... We compute sentiment scores for 10-K filings using the Loughran-McDonald dictionary to identify firms with unexpected tone changes and predict subsequent stock price performance."
- Rule as written:
  - Market: US equities filing annual (10-K) and quarterly (10-Q) reports with the SEC.
  - Bar size: Daily close post-filing date.
  - Model: Parse Section 7 (Management's Discussion and Analysis - MD&A) of SEC filings. Calculate sentiment using the Loughran-McDonald financial dictionary: Count positive, negative, uncertain, litigious, and constraining words. Compute net sentiment score: $\text{Sentiment} = \frac{\text{Positive} - \text{Negative}}{\text{Total Words}}$. Alternatively, train word embedding models (Word2Vec / GloVe) to predict filing-to-filing semantic shift.
  - Entry: When a firm files with the SEC, calculate sentiment score change relative to previous filing. If sentiment shift is in the top decile (strongest improvement/least negative), go long. If sentiment shift is in the bottom decile (strongest negative increase), go short.
  - Exit: Hold position for 1 to 21 trading days post-filing date.
  - Stop loss: None stated.
  - Sizing: Equal dollar weighting across active post-filing events.
  - Holding time: 1 to 21 trading days.
- Book's evidence: Backtested on SEC filings across Russell 3000 stocks (2000-2018). Portfolios sorted on Loughran-McDonald negative sentiment delta generated significant post-filing drift, yielding annualized long-short spreads of ~4.5% to 6.2%.
- Mechanism (the book's): Market underreaction to complex textual disclosures. Human analysts and market participants take time to thoroughly read, parse, and price the nuanced linguistic tone and risk factor shifts buried in lengthy regulatory filings.
- Mechanism (my inference): None needed; book details institutional information processing delays.
- Apex fit: No. Event-driven equity stock-picking strategy holding positions overnight across days/weeks. Cannot trade on Apex futures and violates flat by 15:59 CT daily closeout.
- Already tested? No.

---

### 11. CNN-TA: 2D Convolutional Neural Network Pattern Recognition
- Where: Chapter 18 ("CNNs for Financial Time Series and Satellite Images - CNN-TA: clustering time series in 2D format", pp. 531-565)
- Quote: "The CNN-TA approach transforms 15 technical indicators calculated over multiple timeframes into 2D images, allowing a convolutional neural network to learn spatial relationships and visual chart patterns... The model outputs classification probabilities for Buy, Hold, and Sell signals to drive a long-short equity strategy."
- Rule as written:
  - Market: S&P 500 / Dow Jones 30 equities.
  - Bar size: Daily bars.
  - Feature representation: Calculate 15 technical indicators (RSI, Bollinger Bands, ATR, MACD, STOCH, Williams %R, etc.) across multiple rolling windows (e.g. 5, 10, 15, 20, 25 days). Reorganize indicators into a 2D image matrix ($15 \times 15$ or $28 \times 28$) using hierarchical clustering so correlated features are adjacent.
  - Model: 2D Convolutional Neural Network (LeNet-5 architecture: two convolutional layers with ReLU, 2D max pooling, dropout, followed by fully connected dense layers). Output is 3-class softmax probability: [Sell, Hold, Buy] predicting 5-day forward return direction.
  - Entry: Go long if $P(\text{Buy}) > 0.50$; go short if $P(\text{Sell}) > 0.50$.
  - Exit: Hold for fixed 5-day forward horizon, or exit when opposite signal triggers.
  - Stop loss: None stated.
  - Sizing: Equal dollar weighting across active signals.
  - Holding time: 5 trading days.
- Book's evidence: Based on Sezer and Ozbayoglu (2018). Tested on Dow Jones 30 stocks (2007-2017). Reported modest outperformance over buy-and-hold (Sharpe ~0.75 vs ~0.55), but showed high turnover and degraded performance under realistic execution costs.
- Mechanism (the book's): Automated visual pattern recognition. Convolutions extract translation-invariant local technical features across indicator spaces, aiming to systematically detect chart setups without human subjectivity.
- Mechanism (my inference): None needed; book replicates Sezer & Ozbayoglu (2018).
- Apex fit: No. 5-day multi-day holding period holding equity positions overnight, violating flat by 15:59 CT daily closeout. Furthermore, it stacks traditional technical indicators (RSI, MACD, BB) which failed in prior NQ futures testing.
- Already tested? No (matches technical indicator stacking / multi-day equity holding).

---

### 12. Stacked LSTM Sequential Return Forecasting
- Where: Chapter 19 ("RNNs for Multivariate Time Series and Sentiment Analysis - Stacked LSTM: predicting price moves and returns", pp. 566-601)
- Quote: "Recurrent neural networks, and LSTMs in particular, are designed to learn temporal dependencies in sequence data without requiring fixed lookback parameters... We train a stacked LSTM on rolling windows of daily returns and volume to predict the direction of weekly stock moves."
- Rule as written:
  - Market: S&P 500 equities.
  - Bar size: Daily bars.
  - Input: Rolling 60-day sequence of daily features (lagged returns, volume, volatility, technical indicators).
  - Model: 2-layer stacked LSTM (64 units each) with dropout (0.2) and dense output layer with sigmoid (for binary direction) or linear activation (for forward return). Trained using Adam optimizer with early stopping. Target: forward 5-day or 21-day return.
  - Entry: Rank stocks by predicted forward return. Long top decile, short bottom decile.
  - Exit: Rebalance weekly or monthly.
  - Stop loss: None stated.
  - Sizing: Dollar-neutral equal weighting.
  - Holding time: 5 to 21 trading days.
- Book's evidence: Evaluated on S&P 500 stocks (2010-2019). Reported out-of-sample directional accuracy of 52.8% and Information Coefficient (IC) around 0.025. Marginally beat linear Ridge models in raw IC, but exhibited training instability across random seeds.
- Mechanism (the book's): Temporal memory cells. LSTM gates (input, forget, output) preserve gradients over long time horizons, capturing non-linear sequential dependencies and delayed market adjustments.
- Mechanism (my inference): None needed; book outlines recurrent gating dynamics.
- Apex fit: No. Multi-day equity holding period (5 to 21 days), violating flat by 15:59 CT daily closeout.
- Already tested? No.

---

### 13. Deep Autoencoders for Conditional Asset Pricing
- Where: Chapter 20 ("Autoencoders for Conditional Risk Factors and Asset Pricing - A conditional autoencoder for trading", pp. 602-633)
- Quote: "Gu, Kelly, and Xiu (2020) demonstrate that deep autoencoders capture nonlinear risk factor dynamics and interactions between macroeconomic states and firm characteristics far better than linear factor models... The autoencoder extracts latent market factors while simultaneously estimating individual asset betas to forecast cross-sectional returns."
- Rule as written:
  - Market: Broad US equity panel (CRSP/Compustat universe).
  - Bar size: Monthly data.
  - Architecture: Conditional Autoencoder replicating Gu, Kelly, and Xiu (2020). Input: 90+ firm characteristics (momentum, volatility, size, accounting ratios) and macroeconomic indicators. Encoder compresses characteristics into 4 to 6 latent risk factor portfolios $F_t$. Decoder generates individual asset factor loadings $\beta_{i,t-1}$ conditioned on asset characteristics, predicting cross-sectional return $r_{i,t} = \beta_{i,t-1}^T F_t$.
  - Entry: Sort universe into deciles based on model-predicted risk-adjusted forward return. Long top decile, short bottom decile (dollar-neutral).
  - Exit: Rebalance monthly.
  - Stop loss: None stated.
  - Sizing: Value-weighted or equal-weighted within deciles.
  - Holding time: 1 month (21 trading days).
- Book's evidence: Evaluated on US equities (1957-2016). Reported out-of-sample predictive $R^2$ of 1.47% for individual stocks, translating to an annualized Sharpe ratio of 1.55 in a long-short decile portfolio, significantly outperforming linear PCA and Fama-French benchmarks.
- Mechanism (the book's): Nonlinear conditional asset pricing. Asset risk exposures depend nonlinearly on firm state and macroeconomic regimes; deep autoencoders learn latent economic factors directly from data without prespecifying factor definitions.
- Mechanism (my inference): None needed; book provides asset pricing theoretical foundation.
- Apex fit: No. Cross-sectional monthly equity long-short portfolio held overnight for 30+ days. Violates flat by 15:59 CT daily closeout.
- Already tested? No.

---

### 14. Deep Reinforcement Learning (DDQN) Trading Agent
- Where: Chapter 22 ("Deep Reinforcement Learning - Building a Trading Agent - Deep RL for trading with the OpenAI Gym", pp. 660-705)
- Quote: "We implement a Double Deep Q-Network (DDQN) trading agent within an OpenAI Gym trading environment... The agent learns an optimal policy mapping market state observations directly to trading actions—short, flat, or long—maximizing cumulative risk-adjusted return over multi-month episodes."
- Rule as written:
  - Market: Single liquid equity asset (SPY ETF).
  - Bar size: Daily bars.
  - State space: Rolling 10 to 50 daily returns, technical indicators (MACD, RSI, ATR), and current position state $\{-1, 0, +1\}$.
  - Action space: Discrete $\{0: \text{Short}, 1: \text{Flat}, 2: \text{Long}\}$.
  - Reward function: Realized daily return or differential Sharpe ratio: $R_t = \text{PnL}_t - \frac{\eta}{2} \text{PnL}_t^2$.
  - Agent architecture: Double Deep Q-Network (DDQN) with experience replay buffer (size 100,000) and target network updated every $C$ steps. Epsilon-greedy exploration decaying from 1.0 to 0.01.
  - Entry / Exit: Agent takes actions dynamically at each daily bar close based on $\arg\max_a Q(s, a)$.
  - Stop loss: None explicitly programmed; learned via negative Q-values.
  - Sizing: Binary position sizing ($\pm 1$ unit).
  - Holding time: Dynamic (bars held determined by policy).
- Book's evidence: Trained on daily SPY data (2000-2018). In-sample convergence achieved, but out-of-sample performance showed extreme policy sensitivity, high turnover, and severe drawdown when realistic execution costs were applied.
- Mechanism (the book's): Dynamic policy discovery through reinforcement. The agent balances exploration of novel actions against exploitation of high-reward states, discovering non-linear state-action mappings without supervised teacher signals.
- Mechanism (my inference): None needed; book details RL Bellman optimality and Q-learning dynamics.
- Apex fit: No. Trained on daily bars holding positions across days/weeks; violates flat by 15:59 CT daily closeout. Severe policy instability and risk of ruin under a $2,000 trailing drawdown limit.
- Already tested? No (Markov state and regime models failed; discrete RL on price bars fails similarly).

---

## Ranked Short List

Under the strict criteria of `tasks/TASK_BOOK_READING.md` and `tasks/ANTIGRAVITY_BRIEF.md`, candidate rules must be:
1. **Apex-compatible**: Trade outright futures (NQ/ES/CL/GC/ZN), strictly flat by 15:59 CT daily, and use a single stop loss that respects a $2,000 trailing drawdown limit.
2. **Not already tested and failed**: Must not violate the brief's failure list (mean reversion on NQ/ES, order-flow indicator filters, moving average cross, regime filters).
3. **Have a stated economic mechanism**: Identify who is forced or paid to trade and why they accept losing.

### Result: 0 Directional Candidate Strategies Qualify

Every directional strategy in Stefan Jansen's book fails Apex qualification for distinct structural reasons:

1. **Multi-Day Equity Long-Short Strategies (Rules 1, 3, 7, 10, 11, 12, 13, 14)**:
   - Fama-French Factor Investing, Ridge/Lasso Linear Models, Random Forests on Japanese Stocks, Loughran-McDonald NLP Sentiment, CNN-TA, Stacked LSTM, Conditional Autoencoders, and DDQN Reinforcement Learning all operate on daily or monthly bars holding large stock baskets overnight for weeks to months. They violate the primary Apex requirement: **flat by 15:59 CT daily closeout**.
2. **Pairs Trading & Statistical Arbitrage (Rules 5 & 6)**:
   - Both Engle-Granger Cointegration and Kalman Filter pairs trading require holding multi-day overnight spread positions across two legs (violating flat by 15:59 CT), and are explicitly barred by the brief's testing record: **"Already tested and failed: mean reversion on NQ / ES"**.
3. **High-Frequency Intraday Boosting (Rule 8)**:
   - LightGBM on 1-minute AlgoSeek data is strictly intraday, but its primary predictive signal is order-flow trade classification (shares traded at ask vs bid divided by total volume). This directly triggers the brief's explicit prohibition: **"Already tested and failed: order-flow indicator filters"**. Furthermore, crossing bid-ask spreads on 1-minute bars is eaten alive by transaction costs ($7.25/NQ + 1 tick slippage).

### Architectural Value for Apex Prop Trading

While 0 directional entry rules qualify, the book provides two institutional quantitative algorithms that directly improve sizing and risk management within the user's Apex execution plan:

1. **GARCH(1,1) Volatility Scaling (Rule 4)**:
   - Instead of static contract sizing, scale intraday MNQ contract count dynamically: $\text{Size}_t \propto 1 / \hat{\sigma}_{t,\text{GARCH}}$. Widens stops during quiet regimes and contracts sizing during high-volatility expansions to protect the $2,000 trailing drawdown.
2. **Hierarchical Risk Parity (HRP) Portfolio Clustering (Rule 9)**:
   - Eliminates unstable covariance inversion when allocating risk across multiple funded strategies (Vault Break, Overnight Bias ADX30, Monday Long, Expiration Open Short), allocating capital stably across strategy returns based on hierarchical clustering distance.
