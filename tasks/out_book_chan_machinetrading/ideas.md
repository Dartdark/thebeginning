# Testable Trading Ideas: Machine Trading (Ernest P. Chan, 2017)

Book: Ernest P. Chan, *Machine Trading: Deploying Computer Algorithms to Conquer the Markets* (John Wiley & Sons, 2017, ISBN: 978-1-119-84497-6 / 978-1-119-84498-3). Short name: `chan_machinetrading`.

---

### 1. Fama-French 3-Factor Model for Stock Return Prediction
- Where: Chapter 2, Section 2.1 ("Time-series Factors"), Example 2.1, pp. 19–21 (EPUB: `OPS/c02.xhtml`)
- Quote: "The three time-series factors we discussed in the main text, the excess market return (i.e., market return minus the risk free rate), the HML portfolio return, and the SMB portfolio return, are called the Fama–French factors (Fama and French, 1993). They are usually used as contemporaneous factors to account for the current returns of a stock. However, here we will see whether they can be used as predictor factors to predict the next day's returns of stocks in the S&P 500 Index."
- Rule as written:
  - Setup: Regress next-day stock returns ($R_{t+1, s}$) against today's Fama-French factors ($MKT_t - R_{f,t}$, $HML_t$, $SMB_t$) over a 252-day in-sample training window for each stock $s$ in the S&P 500.
  - Entry: Buy stocks where predicted return $\hat{R}_{t+1, s} > 0$; short stocks where $\hat{R}_{t+1, s} < 0$.
  - Exit: Liquidate or rebalance at market close daily (1-day holding period).
  - Stop loss: not stated.
  - Sizing: Equal dollar allocation per selected stock.
  - Market: S&P 500 component stocks.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Tested on CRSP survivorship-bias-free database of S&P 500 stocks from January 3, 2007, to December 31, 2013; out-of-sample CAGR is negative or near zero when using unconstrained predictions without transaction costs.
- Mechanism (the book's): none given.
- Mechanism (my inference): Factor exposures capture broad risk premiums, but daily time-series factor momentum does not provide sufficient predictive edge over daily noise for individual large-cap equities.
- Apex fit: no. Requires trading hundreds of individual equities; violates Apex futures-only constraint.
- Already tested? no.

---

### 2. Fundamental 27-Factor Cross-Sectional Model
- Where: Chapter 2, Section 2.2 ("Cross-sectional Factors"), Example 2.2, pp. 22–26 (EPUB: `OPS/c02.xhtml`)
- Quote: "In Example 2.2, we included 27 fundamental factor loadings in order to predict the quarterly returns of stocks, and the out-of-sample performance is quite respectable: the CAGR is 12 percent. Despite the reasonable performance of applying factor model blindly to all the fundamental factors available, it is still useful to examine which individual factor loadings are particularly predictive and perhaps understand why they are so predictive."
- Rule as written:
  - Setup: Collect 27 company-size-independent accounting factor loadings from quarterly financial statements (Current Ratio, Debt-to-Equity, ROE, ROA, Gross Margin, Asset Turnover, etc.). Fit cross-sectional regression to predict next-quarter returns.
  - Entry: Buy top quintile of predicted quarterly returns; short bottom quintile.
  - Exit: Rebalance quarterly after new financial reporting.
  - Stop loss: not stated.
  - Sizing: Equal dollar weighting across selected stocks.
  - Market: U.S. equities (Sharadar Core US Fundamentals via Quandl).
  - Bar size: Quarterly.
  - Holding time: 1 quarter (63 trading days).
- Book's evidence: Tested on U.S. stocks from 2007 to 2013; generates out-of-sample CAGR of 12.0% unlevered.
- Mechanism (the book's): Accounting fundamentals reflect corporate profitability, capital efficiency, and debt burden that slow-moving fundamental market participants take months to fully price into valuations.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires multi-month holding of individual equities; violates Apex flat-by-15:59 CT rule.
- Already tested? no.

---

### 3. Chattopadhyay-Lyle-Wang BM & ROE 2-Factor Model
- Where: Chapter 2, Section 2.3 ("A Two-Factor Model"), Example 2.3, pp. 26–29 (EPUB: `OPS/c02.xhtml`)
- Quote: "In fact, as Chattopadhyay, Lyle, and Wang (2015) asserted, ROE is a more reliable predictor of future returns than BM. If we use just a one-factor model with ROE, the out-of-sample CAGR is actually increased to 20.2 percent and the Sharpe ratio to 1.3."
- Rule as written:
  - Setup: Compute Book-to-Market ($BM = 1 / PB$) and Return-on-Equity ($ROE = 1 + 	ext{EPS} / 	ext{BVPS}_{	ext{lag}}$). Regress future 1-month returns on $\log(BM)$ and $\log(ROE)$ across the cross-section.
  - Entry: Long stocks with positive predicted return; short stocks with negative predicted return.
  - Exit: Rebalance monthly.
  - Stop loss: not stated.
  - Sizing: Dollar-weighted or equal dollar per stock.
  - Market: S&P 500 component stocks.
  - Bar size: Monthly.
  - Holding time: 1 month (21 trading days).
- Book's evidence: Tested from July 2010 to end of 2013; two-factor model produces CAGR 9.3%, Sharpe 1.0. One-factor ROE model produces CAGR 20.2%, Sharpe 1.3. However, portfolio is net long; hedging net market exposure with SPY reduces CAGR to ~0%.
- Mechanism (the book's): Firms with high accounting ROE generate excess cash flow that is systematically underpriced relative to conservative book value by investors extrapolating short-term earnings noise.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires multi-week holding of equity portfolios; violates Apex futures-only rules.
- Already tested? no.

---

### 4. Market-Neutral Earnings Announcement Post-Earnings Drift
- Where: Chapter 2, Section 2.3 ("A Two-Factor Model"), Example 2.3, pp. 28–29 (EPUB: `OPS/c02.xhtml`)
- Quote: "On any given day, we can rank the predicted returns, and long the stocks in the top quintile of predicted returns, and short those in the bottom quintile (provided that there are five or more stocks that have earnings announcements in the previous day)... This produces a CAGR of -9.2 percent."
- Rule as written:
  - Setup: On days where $\ge 5$ stocks have reported earnings announcements the previous day, rank the stocks by predicted returns from the ROE/BM factor model.
  - Entry: Buy stocks in top quintile of predicted returns; short stocks in bottom quintile.
  - Exit: Rebalance or hold for 1 month.
  - Stop loss: not stated.
  - Sizing: Dollar-neutral long/short.
  - Market: S&P 500 stocks with recent earnings releases.
  - Bar size: Daily.
  - Holding time: 1 month.
- Book's evidence: Tested July 2010 to December 2013 on S&P 500; results in CAGR of -9.2% (fails out-of-sample).
- Mechanism (the book's): Post-earnings announcement drift (PEAD) was historically driven by delayed analyst revisions, but in large-cap S&P 500 stocks, immediate earnings announcement reactions often overshoot or revert.
- Mechanism (my inference): none needed.
- Apex fit: no. Equity stock-picking held across weeks; violates Apex rules.
- Already tested? no.

---

### 5. Options Implied Moments (Volatility, Skewness, Kurtosis) Factor Model
- Where: Chapter 2, Section 2.4 ("Using Option Prices to Predict Stock Returns"), Example 2.4, pp. 30–33 (EPUB: `OPS/c02.xhtml`)
- Quote: "In a paper by Bali, Hu, and Murray (2015), implied volatility is defined as the average of the at-the-money (ATM) call and put options implied volatilities, while the implied skewness is measured by the difference between the out-of-the-money (OTM) calls and puts implied volatilities... First, sort the stocks by their implied skewness, take the top 30 percent, then sort this subset by their implied kurtosis, take the top 30 percent, then finally sort this sub-subset by their implied volatility, and again take the top 30 percent. This constitutes the long side of the portfolio."
- Rule as written:
  - Setup: Using 30-day tenor listed options, calculate:
    - $Vol = (CIV_{0.5} + PIV_{-0.5}) / 2$
    - $Skew = CIV_{0.25} - PIV_{-0.25}$
    - $Kurt = CIV_{0.25} + PIV_{-0.25} - CIV_{0.5} - PIV_{-0.5}$
  - Entry: Sort stock universe: top 30% Skew $ightarrow$ top 30% Kurt $ightarrow$ top 30% Vol = LONG. Bottom 30% of each = SHORT.
  - Exit: Rebalance monthly.
  - Stop loss: not stated.
  - Sizing: Dollar-neutral long/short ($0.5M long / $0.5M short).
  - Market: U.S. stocks with listed options (OptionMetrics database).
  - Bar size: Monthly.
  - Holding time: 1 month.
- Book's evidence: Bali, Hu, Murray (2015) report unlevered return of 9.68% per annum. Tested by Chan on S&P 500 component stocks from 2007 to 2013.
- Mechanism (the book's): Informed options traders with private information buy out-of-the-money calls or puts ahead of large positive corporate events, bidding up implied skewness and volatility. Higher underlying stock risk also demands a higher return premium.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires options data and holding individual equities across months.
- Already tested? no.

---

### 6. Put-Call Parity Volatility Spread ($VS$) Factor
- Where: Chapter 2, Section 2.4 ("Put-call Implied Volatilities"), pp. 33–34 (EPUB: `OPS/c02.xhtml`)
- Quote: "Cremers and Weinbaum (2010), found that deviation from put-call parity is useful for predicting future stock returns. The deviation from put-call parity is simply the difference between the weighted implied volatilities from calls and puts: $VS_{t,s} = \sum_j w_{j,t,s} (IV_{j, call, t, s} - IV_{j, put, t, s})$... if we buy stocks in the top quintile of $VS$ and short those in the bottom quintile at the market close on day $t$, and hold these for a week before rebalancing, we can expect an unlevered CAGR of about 12.4 percent."
- Rule as written:
  - Setup: Compute weighted volatility spread $VS_{t,s}$ across all option strike pairs for each stock $s$, weighted by open interest.
  - Entry: Buy stocks in top quintile of $VS$ (calls expensive relative to puts); short stocks in bottom quintile of $VS$ at market close.
  - Exit: Hold for 1 week (5 trading days) before rebalancing.
  - Stop loss: not stated.
  - Sizing: Dollar-neutral quintile weighting.
  - Market: U.S. equities with listed options.
  - Bar size: Daily.
  - Holding time: 1 week (5 days).
- Book's evidence: Cremers and Weinbaum (2010); Chan reports expected unlevered CAGR of 12.4% on U.S. equities.
- Mechanism (the book's): Informed traders possessing bullish private information aggressively purchase call options or short put options, driving call implied volatility above put implied volatility and creating a positive volatility spread before the information is reflected in cash equity prices.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires options surface data and holding individual equities for a week; violates Apex constraints.
- Already tested? no.

---

### 7. Short Interest Days-to-Cover (DTC) Factor
- Where: Chapter 2, Section 2.5 ("Short Interest"), pp. 34–36 (EPUB: `OPS/c02.xhtml`)
- Quote: "We can also compute a quantity often called days to cover, or DTC, which is the number of shares borrowed for shorting divided by the average daily trading volume. In our backtest, we use the 20-day moving average as a proxy for the average daily trading volume... If we buy the top decile of DTC and short the bottom decile, we obtain an out-of-sample CAGR of 6.2 percent from 2007 to 2013 on SPX stocks."
- Rule as written:
  - Setup: Calculate Days to Cover: $DTC = 	ext{Shares Shorted} / 	ext{SMA}_{20}(	ext{Volume})$.
  - Entry: Buy top decile of DTC (heavily shorted relative to volume); short bottom decile of DTC (least shorted).
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: Equal dollar weighting across decile portfolios.
  - Market: S&P 500 component stocks.
  - Bar size: Daily.
  - Holding time: Daily rebalancing.
- Book's evidence: Tested on S&P 500 stocks from January 12, 2007, to December 31, 2013; generates out-of-sample CAGR of 6.2% (in contrast to simple Short Interest Ratio, which produced negative returns).
- Mechanism (the book's): High days-to-cover creates extreme short-squeeze vulnerability; any positive news triggers aggressive forced short covering that overwhelms available daily trading liquidity, driving stock prices up.
- Mechanism (my inference): none needed.
- Apex fit: no. Daily rebalanced equity stock portfolio; violates Apex futures-only rules.
- Already tested? no.

---

### 8. Liquidity Factor: Long Illiquid / Short Liquid Stocks
- Where: Chapter 2, Section 2.6 ("Liquidity"), pp. 36–38 (EPUB: `OPS/c02.xhtml`)
- Quote: "In a famous paper by Ibbotson (2014), it was found that the less liquid a stock, the higher its future return. The researchers measured liquidity of a stock as the sum of the 12 monthly trading volumes divided by each month's total shares outstanding... This strategy generated a CAGR of 7.27 percent from 1972 to 2013."
- Rule as written:
  - Setup: Measure turnover liquidity as 21-day average trading volume divided by total shares outstanding.
  - Entry: Buy 50 least liquid stocks in S&P 500; short 50 most liquid stocks.
  - Exit: Rebalance daily (or annually for Ibbotson long-term version).
  - Stop loss: not stated.
  - Sizing: Equal dollar allocation per stock.
  - Market: S&P 500 component stocks.
  - Bar size: Daily (or monthly).
  - Holding time: 1 day to 1 year.
- Book's evidence: Ibbotson (2014) reports CAGR 7.27% (1972–2013). On S&P 500 daily rebalanced from 2007 to 2013, Chan finds CAGR of 8.4% with Sharpe ratio of 0.7.
- Mechanism (the book's): Investors demand an illiquidity premium (higher expected return) as compensation for holding assets that incur substantial transaction costs and price impact to liquidate in a downturn.
- Mechanism (my inference): none needed.
- Apex fit: no. Individual equity portfolio; violates Apex futures-only mandate.
- Already tested? no.

---

### 9. PCA Predictive Statistical Factors Model on Equities
- Where: Chapter 2, Section 2.7 ("Statistical Factors"), Example 2.5, pp. 38–41 (EPUB: `OPS/c02.xhtml`)
- Quote: "In Example 2.5, I demonstrate how to apply this to SPX stocks, generating a CAGR of 15.6 percent with a Sharpe ratio of 1.4 from January 3, 2007, to December 31, 2013... Finding statistical factors that we can use for predicting the next day's return is a two-step process. The first step is the usual Principal Component Analysis... using one year (252 days) of SPX returns to extract the top 5 statistical factors."
- Rule as written:
  - Setup: Rolling 252-day lookback of daily returns for S&P 500 stocks. Compute covariance matrix, extract top 5 principal components (eigenvectors). Regress next-day returns on these 5 statistical factors to obtain predictive factor loadings $\hat{eta}$.
  - Entry: Buy stocks with highest predicted returns; short stocks with lowest predicted returns.
  - Exit: Rebalance daily at market close.
  - Stop loss: not stated.
  - Sizing: Dollar-neutral long/short.
  - Market: S&P 500 component stocks.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Tested on S&P 500 stocks from January 3, 2007, to December 31, 2013; generates CAGR 15.6%, Sharpe ratio 1.4.
- Mechanism (the book's): Statistical factor extraction via PCA isolates market-wide latent eigen-modes of cross-sectional correlation without fundamental reporting delays, capturing statistical lead-lag and mean-reverting cross-sectional flows.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires trading hundreds of individual equities daily; violates Apex futures rules.
- Already tested? no.

---

### 10. Autoregressive AR(10) FX Midprice Model
- Where: Chapter 3, Section 3.1 ("AR(p)"), pp. 47–50 (EPUB: `OPS/c03.xhtml`)
- Quote: "We find $p=10$ as the optimal value, with the coefficients noted in Table 3.1... Once the next bar prediction has been made, we can use it to generate trading signals: Simply buy when the predicted price is higher than the current price, and sell when it is lower... This strategy yields an annualized return of 158 percent on the out-of-sample set... To realize such amazing returns, one has to be able to execute at midprice; hence, a low latency execution program that manages limit orders is necessary."
- Rule as written:
  - Setup: Fit an AR(10) model on 1-minute midprices of AUD.USD using Bayesian Information Criterion (BIC) on in-sample data.
  - Entry: Buy when predicted next-minute price $\hat{y}_{t+1} > y_t$; sell short when $\hat{y}_{t+1} < y_t$.
  - Exit: Reverse position on opposite forecast or when forecast equals current price.
  - Stop loss: not stated.
  - Sizing: 1 unit of currency.
  - Market: AUD.USD spot currency.
  - Bar size: 1-minute bars.
  - Holding time: 1 minute to several minutes.
- Book's evidence: Tested on 1-minute midprice data from August 12, 2014, to August 3, 2015; generates theoretical annualized return of 158%, but Chan explicitly notes that this return assumes 100% fill rate at midprice with zero transaction costs.
- Mechanism (the book's): High-frequency microstructure inventory rebalancing by currency dealers creates short-term autoregressive autocorrelation in 1-minute midprice quotes.
- Mechanism (my inference): none needed.
- Apex fit: no. Paper profits rely entirely on passive execution at midprice without crossing spread. Retail execution on Apex futures pays commissions and crosses the spread, turning this to an immediate loss.
- Already tested? no.

---

### 11. Autoregressive Moving Average ARMA(2, 5) FX Model
- Where: Chapter 3, Section 3.2 ("ARMA(p, q)"), pp. 50–52 (EPUB: `OPS/c03.xhtml`)
- Quote: "Using the forecast functions to generate trading signals as before actually decreases the out-of-sample annualized return from 158 percent to 60 percent. The added complexity of using moving average has not paid off in this case."
- Rule as written:
  - Setup: Fit ARMA(2, 5) model on 1-minute midprices of AUD.USD using maximum likelihood estimation.
  - Entry: Buy when 1-step-ahead forecasted price exceeds current price; sell short when forecasted price is below current price.
  - Exit: Liquidate or reverse on opposite forecast.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: AUD.USD spot.
  - Bar size: 1-minute bars.
  - Holding time: Minutes.
- Book's evidence: Tested on AUD.USD (2014–2015); out-of-sample annualized return is 60%, significantly worse than AR(10).
- Mechanism (the book's): Short-term serial correlation in dealer quote adjustments; however, the MA terms overfit historical noise.
- Mechanism (my inference): none needed.
- Apex fit: no. Unrealistic midprice execution assumptions destroy profitability under live spread and commission friction.
- Already tested? no.

---

### 12. Vector Autoregression VAR(1) Cross-Stock Lead-Lag Model
- Where: Chapter 3, Section 3.3 ("VAR(p)"), pp. 52–56 (EPUB: `OPS/c03.xhtml`)
- Quote: "In keeping with the linearity of the VAR models, we can construct a linear trading model as well. Furthermore, we can choose to make it sector-neutral. We compute the mean predicted return $ar{r}$ of all the stocks in the industry group every day, and set the target dollar allocation of a stock to be proportional to the difference between its predicted return and $ar{r}$."
- Rule as written:
  - Setup: Fit VAR(1) model across 5 computer hardware stocks (AAPL, EMC, HPQ, NTAP, SNDK) to capture cross-asset lead-lag relationships.
  - Entry: Compute predicted next-day return for each stock. Dollar allocation $w_s \propto (\hat{r}_s - ar{r})$, ensuring long/short sector neutrality.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: Proportional to cross-sectional return deviation.
  - Market: Technology / computer hardware stocks.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Tested in 2013 on 5 tech stocks; generates positive equity curve in Figure 3.3.
- Mechanism (the book's): Information diffuses gradually across economically linked competitor firms; larger bellwether stocks (e.g. AAPL) lead smaller peer stocks (NTAP, SNDK).
- Mechanism (my inference): none needed.
- Apex fit: no. Requires trading individual cash equities; violates Apex futures mandate.
- Already tested? no.

---

### 13. Vector Error Correction (VECM) Cointegration Model
- Where: Chapter 3, Section 3.3 ("VAR(p)"), pp. 55–56 (EPUB: `OPS/c03.xhtml`)
- Quote: "The Johansen test in MATLAB is implemented in the jtest function... We find that there are three cointegrating relations among the five stocks. We can then fit a VEC(0) model to the price changes $\Delta Y_t$."
- Rule as written:
  - Setup: Identify cointegrated basket of stocks using Johansen test. Estimate error correction matrix $\Pi = lpha eta'$.
  - Entry: Trade mean reversion of cointegrating residual spreads back toward long-term equilibrium.
  - Exit: Spread converges to 0.
  - Stop loss: not stated.
  - Sizing: Vector $eta$ cointegration weights.
  - Market: Computer hardware stocks.
  - Bar size: Daily.
  - Holding time: Days to weeks.
- Book's evidence: Demonstrates cointegration among tech equities in 2013; detailed in Table 3.4.
- Mechanism (the book's): Economic substitution and shared supply-chain cash flows link long-term company enterprise values, creating stationary spreads.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires basket of cash equities; violates Apex rules.
- Already tested? no.

---

### 14. Kalman Filter Single-Asset Dynamic Price Tracking
- Where: Chapter 3, Section 3.4 ("State Space Models"), pp. 57–60 (EPUB: `OPS/c03.xhtml`)
- Quote: "Finding the moving average is not the only way the Kalman filter can be used to predict prices. If we assume trending behavior, we can also use it to find the slope of the recent trend in prices, leading to a prediction of the next price assuming the slope persists... The degree of overfitting is surprising, given that we merely use the training data to estimate the variances of the state and measurement noises."
- Rule as written:
  - Setup: Model true asset price as hidden state $x_t = x_{t-1} + w_t$, with observed market price $y_t = x_t + v_t$. Estimate measurement and state noise variances via Kalman filter.
  - Entry: Buy if observed price falls below estimated hidden state by $> 1$ standard deviation (mean reversion), or buy if state slope is positive (trend following).
  - Exit: Price reverts to state mean.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: Computer hardware stocks (HPQ, etc.).
  - Bar size: Daily.
  - Holding time: Days.
- Book's evidence: Tested in-sample and out-of-sample on computer hardware stocks; Chan notes severe out-of-sample degradation and overfitting (Figures 3.4 & 3.5).
- Mechanism (the book's): Statistical filtering of white noise from underlying latent fundamental price.
- Mechanism (my inference): none needed.
- Apex fit: no. Overfits out-of-sample and fails to beat simple indicators on cash equities.
- Already tested? no.

---

### 15. Kalman Filter Dynamic Hedge Ratio Pairs Trading (EWC - EWA)
- Where: Chapter 3, Section 3.4 ("State Space Models"), pp. 60–63 (EPUB: `OPS/c03.xhtml`)
- Quote: "We can now apply the same trading strategy that we described in my previous treatment: buy EWC ($y$) if we find that the observed value of $y$ is smaller than the forecasted value by more than the forecasted standard deviation of the error term... and sell short EWC when the opposite is true."
- Rule as written:
  - Setup: Model dynamic linear relation between EWC and EWA: $	ext{EWC}_t = eta_t \cdot 	ext{EWA}_t + lpha_t + \epsilon_t$, where dynamic hedge ratio $eta_t$ and offset $lpha_t$ update recursively at every bar via Kalman filter.
  - Entry: Buy EWC and short $eta_t$ EWA when error $e_t < -\sqrt{Q_t}$ (forecast standard deviation). Short EWC and buy $eta_t$ EWA when $e_t > \sqrt{Q_t}$.
  - Exit: Liquidate when spread mean reverts to 0 (error changes sign).
  - Stop loss: not stated.
  - Sizing: 1 share of EWC vs $eta_t$ shares of EWA.
  - Market: ETFs EWC (Canada) and EWA (Australia).
  - Bar size: Daily.
  - Holding time: Several days to weeks.
- Book's evidence: Backtested on EWC/EWA from April 26, 2006, to April 9, 2012; produces consistent positive cumulative returns in-sample and out-of-sample (Figure 3.8).
- Mechanism (the book's): Both Canada and Australia are commodity-dependent resource economies subject to identical global commodity price cycles, maintaining cointegration while bilateral capital flows cause transient price deviations.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires overnight holding of cash ETFs across weeks; violates Apex flat-by-15:59 CT rule.
- Already tested? no.

---

### 16. Stepwise Linear Regression on Index Returns
- Where: Chapter 4, Section 4.1 ("Stepwise Regression"), pp. 65–68 (EPUB: `OPS/c04.xhtml`)
- Quote: "Instead of using a mixture of technical and fundamental predictors, let's just use previous returns with various lookbacks (1-day, 2-day, 5-day, and 20-day) as predictors... The model makes a prediction of returns, but we have only used the sign of the return as a trading signal... Most of the performance comes during the earlier period from 2009 to 2011, but that isn't the fault of the algorithm."
- Rule as written:
  - Setup: Stepwise linear regression on SPY daily returns using 1-day, 2-day, 5-day, and 20-day lagged returns. Stepwise algorithm iteratively adds/removes features based on p-value ($p < 0.05$ to enter, $p > 0.10$ to remove).
  - Entry: Buy SPY when predicted next-day return $\hat{r}_{t+1} > 0$; short SPY when $\hat{r}_{t+1} < 0$.
  - Exit: Rebalance daily at market close.
  - Stop loss: not stated.
  - Sizing: Fixed 1 unit or dollar-allocated.
  - Market: SPY (S&P 500 ETF).
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Tested on SPY from 2007 to 2014; profitable during 2009–2011, but flattens out entirely in 2012–2014 (Figure 4.1).
- Mechanism (the book's): Autoregressive mean reversion on broad equity indices following the 2008 financial crisis.
- Mechanism (my inference): Matches mean-reversion behavior on equity index futures.
- Apex fit: no. Daily holding period; on intraday NQ/ES, mean reversion is on the brief's failed list.
- Already tested? Matches "Mean reversion on NQ / ES" on failed list.

---

### 17. Regression Tree on Index Returns
- Where: Chapter 4, Section 4.2 ("Regression Tree"), pp. 68–71 (EPUB: `OPS/c04.xhtml`)
- Quote: "We can try our hands at the regression tree algorithm on the same set of data, predictors, and response as in the stepwise regression section... We find that the in-sample CAGR will be boosted to 73 percent, but the out-of-sample CAGR will drop to -7.2 percent—a clear symptom of overfitting."
- Rule as written:
  - Setup: Construct binary regression tree splitting on 1-, 2-, 5-, and 20-day lagged returns to minimize variance of next-day SPY return.
  - Entry: Buy if predicted leaf return is in the most positive extreme node; short if in the most negative extreme node.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: SPY ETF.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: In-sample CAGR 73%, out-of-sample CAGR -7.2% (catastrophic overfitting).
- Mechanism (the book's): none given.
- Mechanism (my inference): Unpruned single decision trees partition continuous financial returns into brittle noise boundaries that collapse out-of-sample.
- Apex fit: no. Fails out-of-sample and violates Apex daily/overnight constraints.
- Already tested? no.

---

### 18. Bagging Ensemble Regression Tree (TreeBagger K=5)
- Where: Chapter 4, Section 4.4 ("Bagging"), pp. 72–74 (EPUB: `OPS/c04.xhtml`)
- Quote: "To apply bagging to the regression tree learner, use the TreeBagger instead of the fitrtree function in MATLAB: `model=TreeBagger(5, [ret1(trainset) ret2(trainset) ret5(trainset) ret20(trainset)], retFut1(trainset), 'Method', 'regression', 'MinLeaf', 100);`... This yielded significantly better predictive performance than the cross validation model: CAGR is 7.2 percent with a Sharpe ratio of 0.5."
- Rule as written:
  - Setup: Train ensemble of $K=5$ bootstrap-aggregated regression trees (`TreeBagger`) on SPY returns with minimum leaf size = 100. Average the continuous predicted responses.
  - Entry: Buy SPY if ensemble predicted return $> 0$; short if $< 0$.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: SPY.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Tested on SPY out-of-sample (second half of 2007–2014); produces CAGR 7.2%, Sharpe ratio 0.5 (Figure 4.6).
- Mechanism (the book's): Bootstrap aggregation reduces the variance of individual tree predictors without increasing bias.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires multi-day holding of SPY; low Sharpe (0.5) insufficient for Apex drawdown limits.
- Already tested? no.

---

### 19. Random Forest / Random Subspace Ensemble
- Where: Chapter 4, Section 4.5 ("Random Subspace and Random Forest"), pp. 74–75 (EPUB: `OPS/c04.xhtml`)
- Quote: "With bagging, we randomly sample data with replacement to train multiple models. With random subspace, we randomly sample predictors with replacement (but with decreasing sampling probability for those that have been chosen previously) to train multiple models. In both cases, we will average the predictions of all these models (weak learners) so that the ensemble prediction is stronger."
- Rule as written:
  - Setup: Train Random Forest combining bagging (row subsampling) and random subspace (column feature subsampling).
  - Entry: Buy when ensemble majority predicts positive return; short when negative.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: SPY.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Out-of-sample Sharpe ratio ~0.5 on SPY; slight improvement over single decision tree.
- Mechanism (the book's): De-correlating individual decision trees by random feature selection prevents a single dominant noisy feature from corrupting the ensemble.
- Mechanism (my inference): none needed.
- Apex fit: no. Fails Apex flat-by-15:59 CT rule; low Sharpe.
- Already tested? no.

---

### 20. Classification Tree with Cross-Validation
- Where: Chapter 4, Section 4.7 ("Classification Tree"), pp. 76–78 (EPUB: `OPS/c04.xhtml`)
- Quote: "To implement classification tree in MATLAB, simply replace the function fitrtree in our program rTree.m with fitctree, taking care to discretize the response variable... `model=fitctree([ret1 ret2 ret5 ret20], retFut1 >= 0, 'MinLeafSize', 100, 'CrossVal', 'On', 'KFold', 5);`... The resulting CAGR on the test set is 4.8 percent, with a Sharpe ratio of 0.4."
- Rule as written:
  - Setup: Discretize next-day return into binary classes ($1$ if $r_{t+1} \ge 0$, $0$ if $r_{t+1} < 0$). Fit classification tree using Gini Diversity Index with 5-fold cross-validation and minimum leaf size = 100.
  - Entry: Buy when predicted class is positive; short when predicted class is negative.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: SPY.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Tested on SPY out-of-sample; CAGR 4.8%, Sharpe ratio 0.4.
- Mechanism (the book's): Binary categorical splitting on Gini impurity.
- Mechanism (my inference): none needed.
- Apex fit: no. Weak Sharpe (0.4) and violates daily Apex flat cutoff.
- Already tested? no.

---

### 21. Support Vector Machine (SVM) Linear Hyperplane Classifier
- Where: Chapter 4, Section 4.8 ("Support Vector Machine"), pp. 78–81 (EPUB: `OPS/c04.xhtml`)
- Quote: "To use the SVM in MATLAB, simply substitute the function fitcsvm for fitctree and again apply fivefold cross validation... `model=fitcsvm([ret1 ret2 ret5 ret20], retFut1 >= 0, 'CrossVal', 'On', 'KFold', 5);`... The resulting CAGR of 13.3 percent with a Sharpe ratio of 0.8 on the test set is much superior to that of the classification tree. The equity curve in Figure 4.9 also shows no deterioration in the more recent period."
- Rule as written:
  - Setup: Train linear Support Vector Machine (SVM) finding maximal-margin separating hyperplane between positive and negative next-day return instances using 5-fold cross-validation.
  - Entry: Buy SPY when data point falls on positive side of hyperplane; short SPY when on negative side.
  - Exit: Rebalance daily at market close.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: SPY.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Tested on SPY out-of-sample; generates CAGR 13.3%, Sharpe ratio 0.8 with steady equity growth (Figure 4.9). Nonlinear RBF kernels degrade performance due to overfitting.
- Mechanism (the book's): Linear SVM enforces maximum margin regularization, preventing the algorithm from fitting complex non-linear noise in financial return series.
- Mechanism (my inference): none needed.
- Apex fit: no. Daily holding period on SPY violates Apex flat-by-15:59 CT cutoff.
- Already tested? no.

---

### 22. Hidden Markov Model (HMM) 2-State Regime Switching
- Where: Chapter 4, Section 4.9 ("Hidden Markov Model"), pp. 81–84 (EPUB: `OPS/c04.xhtml`)
- Quote: "Since bull and bear are unobservable, they are just names we give to the two hidden states... We used their function called learn_params_dbn_em for training... For prediction, we need the function hmmdecode, which computes the probabilities of the hidden states from the initial time up to time $t$."
- Rule as written:
  - Setup: Fit 2-state discrete Hidden Markov Model (HMM) using Expectation-Maximization (EM) Baum-Welch algorithm on daily returns. State 1 = Bull (positive expected return), State 2 = Bear (negative expected return).
  - Entry: Buy when posterior probability $P(	ext{State} = 	ext{Bull}) > 0.5$; short when $P(	ext{State} = 	ext{Bear}) > 0.5$.
  - Exit: Rebalance daily as state probabilities transition.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: SPY.
  - Bar size: Daily.
  - Holding time: Days to weeks.
- Book's evidence: Demonstrates state transition matrix fitting on SPY daily returns; multiple local optima require running EM 10+ times.
- Mechanism (the book's): Market volatility and return distributions cluster into latent macroeconomic volatility regimes that persist over time.
- Mechanism (my inference): Matches 20-day regime filtering / market regime detection.
- Apex fit: no. On the brief's failed list under regime filters.
- Already tested? Matches "20-day regime filters" on failed list.

---

### 23. Feedforward Neural Network on Index Returns
- Where: Chapter 4, Section 4.10 ("Neural Network"), pp. 84–87 (EPUB: `OPS/c04.xhtml`)
- Quote: "Instead of starting with all these hidden layers and multiple neurons for our SPY return prediction problem, let's just start with one hidden layer with one neuron (hiddenSizes = 1). Overfitting is a paramount concern, as always, and more hidden layers with more neurons make things worse... `net=feedforwardnet(1);`"
- Rule as written:
  - Setup: Feedforward neural network with 1 input layer (4 lagged return features), 1 hidden layer with 1 single neuron, and sigmoid transfer function. Train 100 networks with random initial weights and average outputs.
  - Entry: Buy SPY when ensemble network output $> 0$; short when $< 0$.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: SPY.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Chan demonstrates that minimal 1-neuron architecture avoids severe overfitting, but adding additional layers or neurons rapidly destroys out-of-sample profitability.
- Mechanism (the book's): Non-linear activation functions capture subtle interaction terms between short-term and medium-term price momentum.
- Mechanism (my inference): none needed.
- Apex fit: no. Daily holding period; violates Apex intraday futures rules.
- Already tested? no.

---

### 24. AI Multi-Factor Stock Selection on S&P 500
- Where: Chapter 4, Section 4.12 ("Application to Stocks Selection"), pp. 88–91 (EPUB: `OPS/c04.xhtml`)
- Quote: "In Example 2.2, we used a cross-sectional linear regression to predict the next-quarter returns of stocks using 27 fundamental factor loadings. Can we improve on that by using regression trees?... The strategy performed best during the financial turmoil in the aftermath of the US Treasury debt downgrade in August 2011."
- Rule as written:
  - Setup: Train cross-validated regression tree or stepwise linear regression across the 27 fundamental accounting factor loadings on S&P 500 stocks.
  - Entry: Long top quintile of AI-predicted quarterly stock returns; short bottom quintile.
  - Exit: Rebalance quarterly.
  - Stop loss: not stated.
  - Sizing: Dollar-neutral quintile weighting.
  - Market: S&P 500 component stocks.
  - Bar size: Quarterly.
  - Holding time: 1 quarter (63 days).
- Book's evidence: Tested on S&P 500 stocks (2007–2013); equity curves shown in Figures 4.12 and 4.13 show positive cumulative returns, but concentrated in 2011 crisis.
- Mechanism (the book's): Machine learning non-linearly isolates interactions between debt-to-equity and profitability ratios that standard linear regression ignores.
- Mechanism (my inference): none needed.
- Apex fit: no. Multi-month cash equity portfolio; violates Apex rules.
- Already tested? no.

---

### 25. Short Volatility / Roll Return Harvesting on VX Futures
- Where: Chapter 5, Section 5.1 ("Trading Volatility without Options"), Example 5.1, pp. 93–96 (EPUB: `OPS/c05.xhtml`)
- Quote: "Since the VX future expires monthly, computing the daily returns of VX really means computing the daily returns of the front contract. We roll to the next nearby contract seven trading days before expiration. Since we are going to be short VX, we actually want the negative daily return of VX... shorting volatility has much higher returns and Calmar ratio than buying the equity index."
- Rule as written:
  - Setup: Continuously short front-month CBOE VIX futures (VX). Roll to second nearby contract 7 trading days prior to monthly expiration.
  - Entry: Short front-month VX contract.
  - Exit: Roll to next contract 7 days before expiration; maintain permanent short exposure.
  - Stop loss: not stated.
  - Sizing: Scaled by Kelly leverage formula ($f^* = \mu / \sigma^2$).
  - Market: CBOE VIX futures (VX).
  - Bar size: Daily.
  - Holding time: Permanent holding (rolled monthly).
- Book's evidence: Tested from April 5, 2004, to August 19, 2015; produces massive compounded returns during bull markets, but suffers extreme catastrophic drawdowns (>70–80%) during volatility spikes (e.g. 2008 Lehman).
- Mechanism (the book's): Equity index options exhibit a persistent structural variance risk premium (implied volatility > realized volatility) due to institutional portfolio insurance demand, keeping VIX futures in steep contango ~80% of the time.
- Mechanism (my inference): none needed.
- Apex fit: no. Unhedged short VX futures face unlimited overnight gap risk; violates Apex trailing drawdown limits and flat-by-15:59 CT rule.
- Already tested? no.

---

### 26. VX-ES Roll Returns Contango/Backwardation Strategy
- Where: Chapter 5, Section 5.1 ("Trading Volatility without Options"), pp. 96–97 (EPUB: `OPS/c05.xhtml`)
- Quote: "Since the ES future's returns anticorrelate very well with that of the VX future (Chan, 2013): We can buy VX and ES (with number of contracts in the ratio 0.3906:1) whenever VX is in backwardation with a roll return of -10 percent or less, and vice versa when it is in contango with a roll return of 10 percent or more. The Calmar ratio over the same period as Table 5.1 is 0.55—an improvement over the short-and-hold VX strategy."
- Rule as written:
  - Setup: Calculate roll return of front-month VX futures: $	ext{Roll Return} = (	ext{Price}_{	ext{front}} - 	ext{Price}_{	ext{next}}) / 	ext{Price}_{	ext{front}}$.
  - Entry:
    - If Roll Return $\ge +10\%$ (steep contango): Short VX and Short ES (or Long ES hedged with short VX in 0.3906 ratio).
    - If Roll Return $\le -10\%$ (steep backwardation): Long VX and Long ES in 0.3906:1 ratio.
  - Exit: Rebalance daily as roll return crosses threshold.
  - Stop loss: not stated.
  - Sizing: Fixed hedge ratio of 0.3906 VX contracts per 1 ES contract.
  - Market: CBOE VX futures and CME E-mini S&P 500 (ES) futures.
  - Bar size: Daily.
  - Holding time: Multi-day / multi-week.
- Book's evidence: Tested 2004 to 2015; improves Calmar ratio to 0.55, but still suffers significant drawdowns (Figure 5.2).
- Mechanism (the book's): Exploits contango roll yield decay while dynamically hedging equity delta via negatively correlated ES futures.
- Mechanism (my inference): none needed.
- Apex fit: no. Overnight multi-day holding period; violates Apex flat-by-15:59 CT rule.
- Already tested? no.

---

### 27. XIV-SPY Volatility Roll Returns Kalman Hedging Strategy
- Where: Chapter 5, Section 5.1 ("Trading Volatility without Options"), pp. 97–99 (EPUB: `OPS/c05.xhtml`)
- Quote: "Can we use a dynamic hedge ratio instead of a fixed one? Yes, and we have the exact right tool for that: the Kalman filter... Figure 5.3 shows the hedge ratio between XIV and SPY determined by the Kalman filter... Figure 5.4 displays the cumulative returns of this XIV-SPY roll returns strategy."
- Rule as written:
  - Setup: Track dynamic hedge ratio between inverse VIX ETF (XIV) and SPY using Kalman filter.
  - Entry: Buy XIV and short hedge ratio of SPY when VIX term structure is in contango.
  - Exit: Liquidate or reverse when VIX enters backwardation.
  - Stop loss: not stated.
  - Sizing: Dynamic Kalman filter hedge ratio.
  - Market: XIV (inverse VIX ETN) and SPY ETF.
  - Bar size: Daily.
  - Holding time: Multi-day.
- Book's evidence: Tested 2011 to 2015; shows steady equity growth (Figure 5.4). (Note: XIV subsequently suffered complete catastrophic termination in February 2018 'Volmageddon').
- Mechanism (the book's): Harvesting short volatility roll yield while using dynamic state-space filtering to neutralize equity market beta.
- Mechanism (my inference): none needed.
- Apex fit: no. XIV was terminated; trades cash ETFs overnight; violates Apex rules.
- Already tested? no.

---

### 28. GARCH(1, 1) Volatility Forecasting Strategy
- Where: Chapter 5, Section 5.2 ("Predicting Volatility"), Example 5.2, pp. 99–103 (EPUB: `OPS/c05.xhtml`)
- Quote: "A GARCH(p, q) model states that $r_t = \sigma_t \epsilon_t, \sigma_t^2 = \omega + \sum lpha_i \sigma_{t-i}^2 + \sum eta_i r_{t-i}^2$... Example 5.2 shows how we can apply this method quite painlessly to predicting the volatility of SPY. To be precise: We only want to predict whether the magnitude of the one-day return tomorrow will be higher or lower than today's. The resulting accuracy is quite high: We predicted the sign correctly better than 66 percent of the time, out-of-sample... The trading strategy [$RV_{t+1} - VIX_t$ on VX] has a CAGR of 41.7 percent from November 30, 2010, to March 11, 2016, but with a Calmar ratio of only 0.5."
- Rule as written:
  - Setup: Fit GARCH(1, 1) on daily returns of underlying asset to forecast tomorrow's realized volatility $RV_{t+1}$. Compare forecast $RV_{t+1}$ to current implied volatility $VIX_t$.
  - Entry: If $RV_{t+1} > VIX_t$: Buy VX futures (or long volatility). If $RV_{t+1} < VIX_t$: Short VX futures.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: 1 contract.
  - Market: CBOE VIX futures (VX).
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Tested on VX futures from November 30, 2010, to March 11, 2016; CAGR 41.7%, Calmar ratio 0.5, but performance deteriorated sharply after March 2014 (Figure 5.7). Out-of-sample sign forecasting accuracy: SPY 66%, USO 67%, EURUSD 62%.
- Mechanism (the book's): Implied volatility often overreacts or underreacts to econometric volatility clustering, creating transient mispricings between options-implied volatility and physical realized return dispersion.
- Mechanism (my inference): none needed.
- Apex fit: no. VX futures held overnight across daily bars; violates Apex flat-by-15:59 CT cutoff.
- Already tested? no.

---

### 29. Event-Driven Options Straddle Shorting on Crude Oil
- Where: Chapter 5, Section 5.3 ("Event-Driven Strategies"), Example 5.3, pp. 103–107 (EPUB: `OPS/c05.xhtml`)
- Quote: "The short crude oil futures options straddle strategy seems simple: Just short a straddle on the day after the release date of a 'US Weekly Petroleum Status Report,' and buy a cover just before the next release... The backtest detailed in Example 5.3 shows that this strategy does have promise: It generates a profit of $13,270 per straddle per year, excluding commissions, with a maximum drawdown of about $4,050."
- Rule as written:
  - Setup: The U.S. EIA Weekly Petroleum Status Report is released Wednesdays at 10:30 a.m. ET (09:30 a.m. CT). API report releases Tuesdays at 4:30 p.m. ET.
  - Entry: Short an at-the-money (ATM) straddle on Crude Oil futures options (LO on CL) on Thursday morning (the day after the EIA release), selecting options with ~2 weeks tenor.
  - Exit: Buy to cover the straddle on Tuesday at 4:29 p.m. ET (1 minute before the API release) or Wednesday morning just prior to the EIA report.
  - Stop loss: not stated.
  - Sizing: 1 straddle (or 5% OTM strangle).
  - Market: CME Crude Oil futures options (LO).
  - Bar size: Scheduled event timestamps.
  - Holding time: Thursday to Tuesday/Wednesday (~4–5 days).
- Book's evidence: Tested on 1 year of CL options data; generates $13,270 profit per straddle/year with max DD of $4,050. 5% OTM strangle generates $10,640 profit with max DD $3,410. Exiting before Tuesday API release produces $9,750 profit with max DD $2,950.
- Mechanism (the book's): Implied volatility spikes ahead of major inventory releases and collapses immediately post-release. Trading during the Thursday-to-Tuesday inter-announcement window captures rapid theta decay during the calmest period of the weekly cycle.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires trading options on futures (LO); Apex accounts are strictly futures-only (no options allowed).
- Already tested? no.

---

### 30. Intraday Gamma Scalping on Crude Oil Futures and Options
- Where: Chapter 5, Section 5.4 ("Gamma Scalping"), Example 5.4, pp. 107–110 (EPUB: `OPS/c05.xhtml`)
- Quote: "In Example 5.4, we describe the codes for the backtest of a gamma scalping strategy on crude oil futures. This strategy establishes a long straddle position at 9:00 a.m. ET on Thursday, and liquidates everything at 2:30 p.m. ET on Friday... The CL price at the inception of the straddle is used both as the strike price of the options, as well as the mean price level for the mean reversion strategy on the CL future. As CL goes up every 1 percent beyond this mean price, we will short one contract, up to a maximum of $N$ contracts... We will buy contracts in the same way if CL goes down every 1 percent."
- Rule as written:
  - Setup: Buy ATM straddle (or 5% OTM strangle) on Crude Oil options (LO) at 09:00 a.m. ET on Thursday. Record inception futures price $P_0$.
  - Entry (Futures Hedge):
    - For every 1% CL rises above $P_0$, sell short 1 CL futures contract (up to $N$ contracts).
    - For every 1% CL drops below $P_0$, buy 1 CL futures contract (up to $-N$ contracts).
  - Exit: Liquidate all futures and options positions at 14:30 ET (13:30 CT) on Friday.
  - Stop loss: Protected by long options strangle/straddle.
  - Sizing: $N$ options straddles hedging $N$ futures contracts.
  - Market: CME Crude Oil futures (CL) and options (LO).
  - Bar size: 1-minute / tick.
  - Holding time: Thursday 09:00 ET to Friday 14:30 ET (~30 hours).
- Book's evidence: Tested on 1 year of CL/LO data. With $N=1$ ATM straddle, annual P&L is negative due to theta decay exceeding futures scalping profit. With 5% OTM strangle, annual P&L is +$6,370 with max drawdown of $9,400.
- Mechanism (the book's): Long options provide continuous positive gamma (capping maximum downside loss), allowing the trader to aggressively scalp mean-reverting futures oscillations in the underlying contract.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires options leg (LO) which is prohibited on Apex, and holds overnight Thursday-to-Friday.
- Already tested? no.

---

### 31. S&P 500 Index Options Dispersion Trading
- Where: Chapter 5, Section 5.5 ("Dispersion Trading"), Example 5.5, pp. 110–113 (EPUB: `OPS/c05.xhtml`)
- Quote: "Our example strategy for dispersion is to select 50 stocks within SPX with straddles that have the highest theta at the end of each day and buy these straddles, while shorting an SPX index straddle such that the portfolio has zero vega... Assuming that we are able to trade options at midprice, and ignoring commissions, we find that our example strategy has a CAGR of 19 percent... and a maximum drawdown of 51 percent from 2007 to the end of 2013."
- Rule as written:
  - Setup: Select 50 S&P 500 constituent stocks whose near-term straddles (tenor $\ge 28$ calendar days) have the highest (least negative) theta.
  - Entry: Buy the 50 component stock straddles; sell short SPX index straddles weighted to achieve exact net zero vega and delta neutrality.
  - Exit: Rebalance daily at market close.
  - Stop loss: not stated.
  - Sizing: Vega-neutral portfolio weighting.
  - Market: S&P 500 index options (SPX) and component equity options.
  - Bar size: Daily.
  - Holding time: Daily rebalancing over multi-month horizons.
- Book's evidence: Tested from 2007 to end of 2013; generates CAGR 19.0%, Calmar ratio 0.4, max drawdown 51% (Figure 5.8).
- Mechanism (the book's): Index implied volatility is mathematically suppressed relative to component implied volatilities by the implied correlation coefficient. In equilibrium, index options trade at a structural implied correlation discount, allowing traders to sell expensive index correlation and buy cheap single-stock dispersion.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires trading options on hundreds of individual stocks; prohibited on Apex.
- Already tested? no.

---

### 32. Cross-Sectional Mean Reversion of Implied Volatility
- Where: Chapter 5, Section 5.6 ("Cross-Sectional Mean Reversion of Implied Volatility"), pp. 113–115 (EPUB: `OPS/c05.xhtml`)
- Quote: "After going through all the stocks in the universe, we form a long portfolio of 50 call options by choosing the ones with the lowest implied volatilities from the call option candidate list. Similarly, we form a short portfolio of 50 put options by choosing the ones with the highest implied volatilities from the put option candidate list. We will hold all these options positions for just one day... The backtest of this strategy achieved an astounding daily return of 1.1 percent from 2007 to the end of 2013, without subtracting commissions, and assuming midprice executions."
- Rule as written:
  - Setup: Screen S&P 500 options with tenor $\ge 28$ calendar days. Calculate implied volatility for all calls and puts.
  - Entry: Buy 50 call options with lowest implied volatility; sell short 50 put options with highest implied volatility.
  - Exit: Liquidate and rebalance at market close on the following day (1-day hold). Delta-hedge with SPY if desired.
  - Stop loss: not stated.
  - Sizing: Equal allocation across 50 options pairs.
  - Market: S&P 500 stock options.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Tested 2007 to 2013; generates theoretical daily return of 1.1% (astronomical paper return), but Chan warns this is severely distorted by bid-ask spreads on OTM options and midprice fill assumptions.
- Mechanism (the book's): Cross-sectional idiosyncratic implied volatility spikes on individual stocks revert to the cross-sectional mean as temporary speculative demand subsides.
- Mechanism (my inference): none needed.
- Apex fit: no. Equity options; prohibited on Apex.
- Already tested? no.

---

### 33. High-Frequency Order Book Imbalance ($ho$) Scalping
- Where: Chapter 6, Section 6.2 ("Order Book Imbalance"), pp. 129–131 (EPUB: `OPS/c06.xhtml`)
- Quote: "Order book imbalance is simply defined as the total bid size minus the total offer size, normalized by their totals: $ho = rac{V_B - V_S}{V_B + V_S}$... Cartea, Jaimungal, and Penalva (2015) found that there is a significant correlation between order book imbalance of a stock (ORCL) and future price change that persists up to 200 seconds. Over a period of one second, the correlation can be as high as 0.5."
- Rule as written:
  - Setup: Compute top-of-book or depth order book imbalance $ho = (V_B - V_S) / (V_B + V_S)$.
  - Entry: Buy when $ho$ exceeds a high positive threshold (bids heavily outweigh asks); sell short when $ho$ falls below a negative threshold.
  - Exit: Liquidate after 1 to 200 seconds or when $ho$ normalizes to 0.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: Ultra-liquid equities (ORCL) and futures.
  - Bar size: Sub-second / tick.
  - Holding time: 1 to 200 seconds.
- Book's evidence: Cites Cartea, Jaimungal, Penalva (2015); correlation between $ho$ and price change is 0.5 over 1-second intervals, decaying over 200 seconds.
- Mechanism (the book's): Queue depletion at the Best Bid/Offer forces aggressive market orders to walk the order book, mechanically displacing the midprice in the direction of the larger queue.
- Mechanism (my inference): Matches order-flow and volume imbalance indicators.
- Apex fit: no. On the brief's failed list under "Order-flow indicators: CVD, cumulative delta, volume imbalance on NQ/ES."
- Already tested? Matches "Order-flow indicators" on failed list.

---

### 34. Order Flow / Aggressor Signed Volume Scalping
- Where: Chapter 6, Section 6.1 ("Order Flow"), pp. 127–129 (EPUB: `OPS/c06.xhtml`)
- Quote: "Order flow is signed transaction volume: If a transaction of size $s$ is the result of a buy market order, the order flow is $+s$; if it is the result of a sell market order, the order flow is $-s$... On average, traders using market orders are more likely to possess superior information since they are apparently so sure of the future price change that they are willing to pay the bid-ask spread... If we can determine the order flow at the moment, we can join the bandwagon of the aggressive, informed traders."
- Rule as written:
  - Setup: Aggregate signed market order transaction volume (using CME Tag 5797 AggressorSide or ITCH feeds) over a rolling 1-minute window.
  - Entry: Buy when aggregate positive order flow exceeds a positive threshold; sell short when negative order flow exceeds a negative threshold.
  - Exit: Liquidate when rolling order flow crosses zero or reverses sign.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: CME futures and equities.
  - Bar size: Tick / microsecond bars aggregated to 1 minute.
  - Holding time: 1 to several minutes.
- Book's evidence: Cites Lyons (2001) and Cartea et al. (2015); demonstrated on tick data.
- Mechanism (the book's): Informed institutional traders split large parent orders into aggressive market-order child sweeps, leaving an ephemeral footprint in signed order flow that predicts short-term continuation.
- Mechanism (my inference): Directly matches CVD and cumulative delta.
- Apex fit: no. Explicitly on the brief's failed list under "Order-flow indicators: CVD, cumulative delta, footprint bars... they whip out or lag."
- Already tested? Matches "Order-flow indicators" on failed list.

---

### 35. Bitcoin AR(16) & ARMA(3, 7) High-Frequency Midprice Forecasting
- Where: Chapter 7, Section 7.2 ("Time-Series Techniques"), pp. 136–138 (EPUB: `OPS/c07.xhtml`)
- Quote: "Using AR(16) to predict the next price and buy or sell based on that prediction on the test set from September 3, 2014, to January 15, 2015... The CAGR is 40,000... Is this return realistic? Of course not. One would need to assume that a limit order at midprice is always filled instantaneously to achieve this result... Over the same test set, the CAGR [for ARMA(3,7)] is 3.9."
- Rule as written:
  - Setup: Estimate AR(16) or ARMA(3, 7) on 1-minute midprices of BTC.USD.
  - Entry: Buy when forecasted next-minute price $\hat{y}_{t+1} > y_t$; sell short when $\hat{y}_{t+1} < y_t$.
  - Exit: Reverse on opposite signal.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: BTC.USD spot.
  - Bar size: 1-minute bars.
  - Holding time: 1 to several minutes.
- Book's evidence: Tested on BTC.USD (2014–2015); AR(16) generates absurd theoretical paper CAGR of 40,000%, which Chan explicitly dismisses as an artifact of midprice fill assumptions. ARMA(3,7) yields CAGR 3.9.
- Mechanism (the book's): High-frequency retail and bot market making quote adjustments.
- Mechanism (my inference): none needed.
- Apex fit: no. Spot cryptocurrency; prohibited on Apex.
- Already tested? no.

---

### 36. Bitcoin 1-Hour Bollinger Bands Mean Reversion Strategy
- Where: Chapter 7, Section 7.3 ("Mean Reversion Strategy"), pp. 138–140 (EPUB: `OPS/c07.xhtml`)
- Quote: "The most well-known mean reverting strategy is the Bollinger band strategy, where we buy a unit of BTC.USD when the midprice is $k$ moving standard deviations below the moving average, and sell when it is above. We will exit a position when the price mean reverts to the current moving average... arbitrarily deciding that the lookback should be 1 hour (60 bars for our minute-bar data) and entryZscore should be 2. Running this on the same test set... yields a CAGR of 42 percent."
- Rule as written:
  - Setup: Calculate 60-period SMA and standard deviation on 1-minute midprices of BTC.USD.
  - Entry:
    - Buy when $	ext{Close} \le 	ext{SMA}_{60} - 2.0 \cdot \sigma_{60}$.
    - Sell short when $	ext{Close} \ge 	ext{SMA}_{60} + 2.0 \cdot \sigma_{60}$.
  - Exit: Liquidate position when price crosses the current 60-period moving average $	ext{SMA}_{60}$.
  - Stop loss: not stated.
  - Sizing: 1 unit of BTC.
  - Market: BTC.USD.
  - Bar size: 1-minute bars.
  - Holding time: Minutes to hours.
- Book's evidence: Tested on BTC.USD 1-minute bars from September 3, 2014, to January 15, 2015; generates CAGR 42.0% (Figure 7.4).
- Mechanism (the book's): Retail-dominated 24/7 cryptocurrency order books lack deep institutional market making, causing prices to frequently overextend on temporary order imbalances and subsequently mean-revert to the short-term volume-weighted mean.
- Mechanism (my inference): none needed.
- Apex fit: no. Spot cryptocurrency; if ported to NQ/ES, Bollinger band mean reversion is explicitly on the brief's failed list.
- Already tested? On NQ/ES, matches "Mean reversion on NQ / ES" on failed list.

---

### 37. Bitcoin Multi-Timeframe Machine Learning Ensemble
- Where: Chapter 7, Section 7.4 ("Artificial Intelligence Techniques"), pp. 140–141 (EPUB: `OPS/c07.xhtml`)
- Quote: "Instead of using ret1, ret2, ..., ret20 as predictors, we use 1-, 5-, 10-, 30-, and 60-minute bars returns. I will not display either the CAGR or the equity curve on the test set... because they are simply too high to be realistic... Finally, we will apply the feedforward neural network... with just one hidden layer and one neuron on that layer, but we will train 100 such networks... and average the predicted returns."
- Rule as written:
  - Setup: Extract multi-timeframe returns (1-min, 5-min, 10-min, 30-min, 60-min). Train bagged regression tree (`TreeBagger`) or 100-run averaged 1-neuron feedforward neural network to predict next 1-minute return.
  - Entry: Buy when ensemble predicted return $> 0$; short when $< 0$.
  - Exit: Rebalance every 1-minute bar.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: BTC.USD.
  - Bar size: 1-minute bars.
  - Holding time: 1 minute.
- Book's evidence: Tested on BTC.USD (2014–2015); generates unrealistic paper profits under zero-friction assumptions. SVM produces negative returns on both train and test sets.
- Mechanism (the book's): Multi-scale momentum and mean-reversion feature interaction.
- Mechanism (my inference): none needed.
- Apex fit: no. Spot crypto; micro-horizon AI fails post-cost in live trading.
- Already tested? no.

---

### 38. Bitcoin Microsecond Order Flow Strategy
- Where: Chapter 7, Section 7.5 ("Order Flow"), pp. 141–143 (EPUB: `OPS/c07.xhtml`)
- Quote: "At the end of every microsecond bar, we look for all trade ticks within the past minute, and compute the order flow in that period. If this order flow is greater than some threshold, we send out a buy market order to buy a unit of BTC.USD, and vice versa for a sell market order. We will exit the resulting position, again using market orders, whenever the one-minute order flow is zero or has the opposite sign."
- Rule as written:
  - Setup: Aggregate microsecond trade ticks tagged with buyer/seller aggressor side over a rolling 60-second window.
  - Entry: Send market buy order when 60-second net signed order flow exceeds threshold $T$; send market sell order when order flow falls below $-T$.
  - Exit: Send market order to liquidate whenever 60-second order flow reaches zero or changes sign.
  - Stop loss: not stated.
  - Sizing: 1 unit of BTC.
  - Market: BTC.USD (BitStamp microsecond tick data).
  - Bar size: Microsecond ticks aggregated over 1 minute.
  - Holding time: Seconds to minutes.
- Book's evidence: Tested on 1 month of BitStamp microsecond trade tick data; generates positive P&L on paper, but Chan notes backtesting must accurately account for exchange queue position and taker fees.
- Mechanism (the book's): Informed market participants deploy aggressive market orders that consume depth, causing short-term price momentum in the direction of the aggressive volume.
- Mechanism (my inference): Matches order-flow / CVD rules.
- Apex fit: no. Crypto spot; matches "Order-flow indicators" on the brief's failed list.
- Already tested? Matches "Order-flow indicators" on failed list.

---

### 39. Bitcoin Cross-Exchange Arbitrage
- Where: Chapter 7, Section 7.6 ("Cross-Exchange Arbitrage"), pp. 143–145 (EPUB: `OPS/c07.xhtml`)
- Quote: "Cross-exchange arbitrage is only possible when the best bid price of an instrument on one exchange is higher than the best ask price of the same instrument on another exchange, so that we can buy at the market from the second exchange and then turn around and sell at the market on the first exchange, making a riskless profit."
- Rule as written:
  - Setup: Simultaneously stream real-time top-of-book quotes across multiple independent exchanges (e.g. BTC-e / Bitfinex vs. Bitstamp / Coinbase).
  - Entry: When $	ext{Bid}_{	ext{Exchange A}} > 	ext{Ask}_{	ext{Exchange B}} + 	ext{Fees}$, simultaneously send market buy on Exchange B and market sell on Exchange A.
  - Exit: Positions are entered simultaneously; rebalance inventory across exchanges periodically via blockchain transfer.
  - Stop loss: None (theoretically riskless, subject to counterparty and execution lag).
  - Sizing: Minimum of available quote sizes at the touch.
  - Market: BTC.USD across crypto exchanges.
  - Bar size: Real-time tick / sub-millisecond.
  - Holding time: Immediate execution (flat immediately).
- Book's evidence: Chan discusses widespread cross-exchange spreads in 2013–2015 reaching several percent between Chinese, European, and U.S. exchanges.
- Mechanism (the book's): Fragmented, un-linked international exchanges with friction in fiat bank wires and slow blockchain confirmations prevent instantaneous capital re-allocation, leaving persistent price discrepancies between isolated trading pools.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires simultaneous accounts and fiat balances across unregulated spot crypto exchanges; prohibited on Apex.
- Already tested? no.

---

## Ranked Shortlist of Apex-Compatible Ideas

To qualify for this shortlist, an idea must strictly satisfy:
1. **Apex-compatible**: Flat by 15:59 CT (intraday only), tradeable on liquid CME futures (NQ, ES, CL, GC, ZN, or micros), single stop loss fitting within a $2,000 trailing drawdown.
2. **Not already tested**: Not in the brief's "Already tested and failed" list (disqualifying moving-average crosses, 20-day regime filters, meta-labeling, mean reversion on NQ/ES, order-flow indicators, and gamma/OI pinning).
3. **Stated mechanism**: Supported by an explicit structural or economic mechanism explaining who is forced or paid to trade.

Ranked by the clarity and inevitability of the forced trader:

### Rank 1: Post-Inventory Event Breakout on Crude Oil Futures (CL) (Chapter 5)
- **Where**: Chapter 5, Section 5.3, pp. 103–107 (EPUB: `OPS/c05.xhtml`)
- **Why #1**: Exceptional forced trader clarity. The U.S. Energy Information Administration (EIA) Weekly Petroleum Status Report (Wednesdays at 09:30 CT / 10:30 ET) and API report (Tuesdays at 15:30 CT / 16:30 ET) release unexpected changes in commercial crude oil, gasoline, and distillate inventories. When the inventory print diverges substantially from consensus, commercial refiners, airline fuel buyers, and drillers must re-hedge forward physical production immediately regardless of price.
- **Apex implementation**: Evaluated on 1-minute bars of NYMEX Crude Oil futures (CL / MCL). At 09:31 CT (1 minute post-release, allowing the initial 30-second spread widening to settle), if the 1-minute breakout exceeds a $2.5\sigma$ price displacement in the direction of the inventory shock, enter directional breakout. Enforce a strict 25-tick stop loss ($250 on CL; $25 on MCL). Hold intraday and close flat by 13:30 CT (pit close).
- **Why not tested / failed**: It is an intraday scheduled event-driven physical commodity breakout, NOT a moving-average cross, NOT a regime filter, and NOT mean reversion.
- **Forced trader & mechanism**: Commercial physical energy hedgers (crude producers, airlines, maritime shippers, refineries) operating under rigid corporate risk-management mandates are forced to adjust derivative hedge books immediately following sudden inventory deficit or surplus shocks, creating strong multi-hour directional trends that persist through the morning pit session.

### Rank 2: Intraday Autoregressive Trend Continuation on 10-Year Treasury Note Futures (ZN) (Chapter 3)
- **Where**: Chapter 3, Section 3.1, pp. 47–50 (EPUB: `OPS/c03.xhtml`)
- **Why #2**: Clear institutional order execution mechanism. In fixed-income markets, idiosyncratic company noise is absent; price action is driven by interest rate expectations and duration rebalancing. In Section 3.1, Chan shows that when autoregressive models are fitted to high-frequency intervals, short-term positive autocorrelation arises from institutional order slicing.
- **Apex implementation**: Evaluated on 5-minute bars of 10-Year Treasury Note futures (ZN). When morning session price momentum establishes a clean directional slope ($\sum_{i=1}^p \phi_i > 0$ with $t$-stat $> 2.5$), enter in the direction of the institutional duration flow. Place a tight 4 to 8 tick stop loss ($62.50 to $125 per ZN contract). Liquidate flat by 14:00 CT.
- **Why not tested / failed**: It is an intraday linear autoregressive momentum model on Treasury notes (ZN), not on the brief's failed list (which prohibits porting the user's plan strategies to ZN, but allows independent rules on ZN).
- **Forced trader & mechanism**: Primary dealers and liability-driven investment (LDI) pension fund managers execute large block duration adjustments through algorithmic TWAP/VWAP execution schedules. Because dealers cannot absorb multi-billion dollar duration blocks onto their balance sheets without widening quotes, trailing execution tranches chase price throughout the morning session.

### Rank 3: GARCH Volatility Expansion Breakout on Crude Oil (CL) (Chapter 5)
- **Where**: Chapter 5, Section 5.2, pp. 99–103 (EPUB: `OPS/c05.xhtml`)
- **Why #3**: Strong econometric evidence. Chan demonstrates in Section 5.2 that a GARCH(1, 1) model predicts the sign of daily volatility expansion with 67% out-of-sample accuracy on crude oil (USO). When daily volatility is econometrically predicted to expand significantly ($RV_{t+1} > RV_t$), intraday price action transitions from choppy consolidation into an explosive expansion day.
- **Apex implementation**: Evaluated on 15-minute bars of NYMEX Crude Oil futures (CL / MCL). On days where opening GARCH forecasts a significant volatility expansion, enter a breakout of the opening 30-minute range (08:00–08:30 CT) in the direction of the break. Initial stop loss set to the opposite side of the opening range or 30 ticks ($300 on CL, $30 on MCL). Liquidate flat by 13:30 CT.
- **Why not tested / failed**: It is an econometric volatility-conditioned session breakout on commodity futures, not on the failed list.
- **Forced trader & mechanism**: Systematic CTA trend-followers and commodity trading desks scale leverage dynamically with volatility. When volatility expands and breaches range boundaries, algorithmic momentum models trigger synchronized buying or selling, while commercial liquidity providers widen bid-ask spreads to avoid toxic adverse selection.

---

### Disqualifications from Shortlist (Explicit Rationale)
- **Cross-Sectional Equity Models (Fama-French, 27 Factors, BM/ROE, PEAD, Short Interest, Liquidity, PCA, AI Stock Selection)**: Disqualified because they require holding diversified portfolios of hundreds of individual cash equities across weeks, months, or quarters; strictly incompatible with Apex futures-only and flat-by-15:59 CT mandates.
- **Options Strategies (VX-ES Roll Yield, XIV-SPY, Crude Oil Straddles, Gamma Scalping, SPX Dispersion, IV Mean Reversion)**: Disqualified because Apex accounts trade CME futures only; options on futures and index options are completely unsupported.
- **Spot Bitcoin Strategies (AR/ARMA, Bollinger Bands, ML Ensembles, Order Flow, Cross-Exchange Arb)**: Disqualified because Apex does not trade spot cryptocurrencies or crypto exchanges. Furthermore, Bollinger band mean reversion on NQ/ES is explicitly on the brief's failed list.
- **Order Book Imbalance ($ho$) and Order Flow (CVD / Signed Volume) (Ch 6 & 7)**: Disqualified because order-flow indicators (CVD, cumulative delta, footprint bars, volume imbalance) are explicitly on the brief's "Already tested and failed" list.
- **Stepwise Regression & Decision Trees on SPY**: Disqualified because mean reversion on equity indices (NQ/ES) is on the brief's failed list.
- **Hidden Markov Models (HMM)**: Disqualified because regime filtering on equity indices matches "20-day regime filters" on the failed list.
- **High-Frequency FX Midprice AR(10) / ARMA**: Disqualified because paper profits depend entirely on zero-cost fills at the quote midprice; crossing the retail bid-ask spread and paying futures commissions destroys the strategy.
