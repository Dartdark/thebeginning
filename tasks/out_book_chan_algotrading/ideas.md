# Testable Trading Ideas: Algorithmic Trading (Ernest P. Chan, 2013)

Book: Dr. Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their Rationale* (John Wiley & Sons, 2013, ISBN: 978-1-118-74691-2). Short name: `chan_algotrading`.

---

### 1. TU 2-Year Treasury Note Futures Time Series Momentum
- Where: Chapter 1 (Example 1.1, pp. 14-16) and Chapter 6 (Example 6.1, pp. 126-128)
- Quote: "That strategy buys (sells) the TU future if it has a positive (negative) 12-month return, and holds the position for 1 month. We pick this strategy not only because of its simplicity, but because it has a fixed holding period." (Ch 1) / "From June 1, 2004, to May 11, 2012, the Sharpe ratio is a respectable 1. The annual percentage rate (APR) of 1.7 percent may seem low, but our return is calculated based on the notional value of the contract..." (Ch 6)
- Rule as written:
  - Entry: Calculate return over the past 12 months (252 trading days). If 12-month return > 0, enter long; if 12-month return < 0, enter short.
  - Exit / Holding period: Hold for 1 month (21 trading days). In continuous form, rebalance daily by allocating 1/25th of capital each day to the new 12-month signal.
  - Stop loss: not stated.
  - Position sizing: Sized based on notional contract value (~$200,000 per TU contract) or equal risk allocation across futures; margin requirement ~$400 per contract.
  - Market: CBOT 2-Year US Treasury Note futures (TU).
  - Bar size: Daily closing prices.
- Book's evidence: Tested on TU futures from 2004-06-01 to 2012-05-11: Unlevered APR = 1.7%, Sharpe ratio = 1.0, Maximum Drawdown = 2.5%. Also summarized in Table 6.2 for other futures contracts.
- Mechanism (the book's): Total futures return equals spot return plus roll return. Futures contracts often stay in persistent contango or backwardation for extended multi-month periods. The sign of the roll return does not fluctuate frequently, creating persistent multi-month serial correlation (momentum) in total returns.
- Mechanism (my inference): none needed.
- Apex fit: no. Holding period is 1 month (requires holding positions overnight across weeks); Apex strictly requires all positions closed by 15:59 CT.
- Already tested? no.

---

### 2. USD.CAD Linear Mean Reversion Model
- Where: Chapter 2, Section "A Linear Mean-Reverting Trading Strategy", Example 2.5 (pp. 36-39)
- Quote: "In this simple strategy, we seek to own a number of units of USD.CAD equal to the negative normalized deviation from its moving average. The market value (in USD) of one unit of a currency pair USD.X is nothing but the quote USD.X, so in this case the linear mean reversion is equivalent to setting the market value of the portfolio to be the negative of the Z-Score of USD.CAD."
- Rule as written:
  - Model: Estimate half-life of mean reversion $\tau = -\ln(2)/\lambda$ by fitting Ornstein-Uhlenbeck regression $\Delta y_t = \mu + \lambda y_{t-1} + \epsilon_t$.
  - Lookback: Set moving average and standard deviation lookback equal to half-life $\tau$ (calculated as 115 trading days for USD.CAD).
  - Entry / Sizing: Target position units $N_t = - \frac{Price_t - MA(Price, \tau)}{StdDev(Price, \tau)} = - Z_t$.
  - Exit: Dynamic continuous rebalancing; position scales down as $Z_t$ approaches 0.
  - Stop loss: not stated (explicitly omitted).
  - Market: USD.CAD spot currency pair (sampled at 17:00 ET).
  - Bar size: Daily closes (17:00 ET).
  - Holding time: Variable, based on half-life (approx. 115 trading days).
- Book's evidence: Tested on USD.CAD over 2007–2012: positive cumulative P&L, but suffered a very large drawdown; transaction costs omitted; Chan notes in-sample lookahead bias in finding half-life and notes infinite capital required if unconstrained, presenting it as an educational baseline rather than a live strategy.
- Mechanism (the book's): none given (purely statistical Ornstein-Uhlenbeck property).
- Mechanism (my inference): Macroeconomic purchasing power parity and central bank policy rate bounds keep major currency pairs within broad equilibrium trading bands.
- Apex fit: no. Requires multi-month overnight spot FX holding; Apex requires intraday futures flat by 15:59 CT.
- Already tested? no.

---

### 3. EWA-EWC-IGE Cointegration Triplet Portfolio Mean Reversion
- Where: Chapter 2, Section "Cointegration", Examples 2.7 & 2.8 (pp. 43-48)
- Quote: "Both Trace statistic and Eigen statistic tests conclude that we should have three cointegrating relations with 95 percent certainty... Here, we also accumulate units of the portfolio proportional to the negative Z-Score of the 'unit' portfolio's price. A unit portfolio is one with shares determined by the Johansen eigenvector."
- Rule as written:
  - Formation: Apply Johansen cointegration test to daily prices of EWA, EWC, and IGE. Take the primary eigenvector $[w_1, w_2, w_3]$ corresponding to the largest eigenvalue to define unit portfolio price $y_{port} = w_1 P_{EWA} + w_2 P_{EWC} + w_3 P_{IGE}$.
  - Lookback: Calculate half-life of $y_{port}$ via Ornstein-Uhlenbeck regression ($\tau = 23$ trading days). Set moving average and moving standard deviation lookback to 23 days.
  - Sizing / Entry: Hold units of the unit portfolio proportional to $-Z_{port} = - \frac{y_{port} - MA(y_{port}, 23)}{StdDev(y_{port}, 23)}$.
  - Exit: Rebalance daily as $Z_{port}$ reverts towards zero.
  - Stop loss: not stated.
  - Market: EWA (Australia ETF), EWC (Canada ETF), IGE (Natural Resources ETF).
  - Bar size: Daily closes.
  - Holding time: ~23 days (half-life).
- Book's evidence: Johansen test confirms cointegration at 95% confidence; half-life = 23 trading days; positive equity curve over 2006–2012 without transaction costs.
- Mechanism (the book's): Australia and Canada are resource-based economies whose national terms of trade, currencies, and corporate cash flows are fundamentally tied to the global commodities and natural resources sector (IGE), creating a cointegrated macroeconomic equilibrium.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires holding a 3-ETF equity portfolio overnight across weeks; Apex requires flat by 15:59 CT on futures.
- Already tested? no.

---

### 4. GLD-USO Bollinger Band Spread Mean Reversion
- Where: Chapter 3, Section "Implementing Mean Reversion Strategies", Examples 3.1 & 3.2 (pp. 53-57)
- Quote: "Here, we simply switch to a Bollinger band strategy, using the entryZscore = 1 and exitZscore = 0, with the first part of the program identical to PriceSpread.m... The Bollinger band strategy has an APR = 17.8 percent, and Sharpe ratio of 0.96, quite an improvement from the linear mean reversal strategy!"
- Rule as written:
  - Spread definition: $Spread = P_{USO} - \beta \cdot P_{GLD}$, where hedge ratio $\beta$ is estimated via linear regression.
  - Lookback: Half-life calculated as 18–20 days; moving average and standard deviation lookback set to 20 days.
  - Entry: Long spread (Buy 1 unit USO, Short $\beta$ units GLD) when $Z < -1.0$. Short spread (Sell 1 unit USO, Long $\beta$ units GLD) when $Z > +1.0$.
  - Exit: Liquidate entire position when $Z$ crosses 0.0.
  - Stop loss: not stated (Chan explicitly demonstrates that adding stop-losses reduces Sharpe ratio in stationary backtests).
  - Sizing: Fixed 1 unit of spread (non-scaling).
  - Market: GLD (Gold ETF) and USO (Crude Oil ETF).
  - Bar size: Daily closes.
  - Holding time: ~20 trading days (half-life).
- Book's evidence: Backtested 2006-05-24 to 2012-04-09: APR = 17.8%, Sharpe ratio = 0.96 (compared to APR = 1.9% for linear scaling model).
- Mechanism (the book's): Gold and crude oil are key dollar-denominated physical commodities sensitive to global inflation expectations, monetary policy, and currency debasement, maintaining an equilibrium exchange ratio.
- Mechanism (my inference): none needed.
- Apex fit: no. Overnight multi-week holding of ETF pairs; Apex requires flat by 15:59 CT on futures.
- Already tested? no.

---

### 5. EWA-EWC Dynamic Linear Regression via Kalman Filter
- Where: Chapter 3, Section "Dynamic Linear Regression", Example 3.3 (pp. 60-65)
- Quote: "The measurement prediction error e(t)... is none other than the deviation of the spread EWC-EWA from its predicted mean value, and we will buy this spread when the deviation is very negative, and vice versa if it is very positive."
- Rule as written:
  - Model: Kalman filter updating state vector $[\beta_t, \alpha_t]^T$ where $y_t = \beta_t x_t + \alpha_t + \epsilon_t$. Transition covariance parameter $\delta = 0.0001$, observation variance $V_e = 0.001$.
  - Signal: Measurement prediction error $e_t = y_t - \hat{y}_t$ normalized by its predicted standard deviation $\sqrt{Q_t}$.
  - Entry / Sizing: Position size in spread proportional to $-e_t / \sqrt{Q_t}$ (linear model) or Bollinger threshold entry ($|e_t / \sqrt{Q_t}| > 1.0$).
  - Exit: When prediction error reverts to 0.
  - Stop loss: not stated.
  - Market: EWA and EWC ETFs.
  - Bar size: Daily closes.
  - Holding time: Multi-day.
- Book's evidence: 2006 to 2012 backtest demonstrates that Kalman filtering dynamically tracks slope and intercept without lookahead bias or arbitrary rolling window choices.
- Mechanism (the book's): Economic relationships between correlated assets undergo slow structural drift over time; the Kalman filter separates slow structural trend changes from transient mean-reverting deviations.
- Mechanism (my inference): none needed.
- Apex fit: no. Overnight ETF pair trading; Apex requires flat by 15:59 CT on futures.
- Already tested? no.

---

### 6. Intraday Buy-on-Gap Model on S&P 500 Stocks
- Where: Chapter 4, Section 4.3, Example 4.1 (pp. 75-79)
- Quote: "1. Select all stocks near the market open whose returns from their previous day's lows to today's opens are lower than one standard deviation. The standard deviation is computed using the daily close-to-close returns of the last 90 days... 2. Narrow down this list of stocks by requiring their open prices to be higher than the 20-day moving average of the closing prices. 3. Buy the 10 stocks within this list that have the lowest returns from their previous day's lows... 4. Liquidate all positions at the market close."
- Rule as written:
  - Universe: S&P 500 individual stocks.
  - Entry Condition 1: Gap down from prior low: $\frac{Open_t - Low_{t-1}}{Low_{t-1}} < -1.0 \times \sigma_{90}$, where $\sigma_{90}$ is the 90-day moving standard deviation of close-to-close returns.
  - Entry Condition 2 (Trend filter): $Open_t > MA(Close, 20)$.
  - Ranking & Sizing: Select up to 10 stocks with the lowest return from prior low (buy all if fewer than 10 qualify). Equal dollar allocation across selected stocks. Enter at market open (09:30 ET).
  - Exit: Liquidate all positions at market close (16:00 ET).
  - Stop loss: not stated.
  - Market: S&P 500 individual stocks.
  - Bar size: Daily Open, Low, Close (intraday execution).
  - Holding time: Intraday (from 09:30 ET open to 16:00 ET close; flat overnight).
- Book's evidence: Tested on S&P 500 stocks from 2006-05-11 to 2012-04-24: APR = 8.7%, Sharpe ratio = 1.5. (Chan notes survivorship bias in SPX data, and notes without Rule 2 the strategy suffered diminishing returns after 2008).
- Mechanism (the book's): Pre-market drops in equity index futures trigger emotional panic-selling and retail market orders at the open. Once the opening liquidity imbalance is absorbed, market makers and institutional buyers step in, causing price to mean-revert intraday. Rule 2 filters out genuine fundamental negative news (e.g. disastrous earnings).
- Mechanism (my inference): none needed.
- Apex fit: no. Operates on individual equities (unavailable on Apex accounts), and "mean reversion on NQ / ES" and "20-day regime filters" are in the brief's failed list.
- Already tested? Matches "mean reversion on NQ / ES" and "20-day bull / bear regime filters" on the brief's failed list.

---

### 7. SPY vs Component Stocks Cointegration Arbitrage
- Where: Chapter 4, Section 4.2, Example 4.2 (pp. 70-74)
- Quote: "The impatient reader can look ahead to Example 4.2, which shows a linear mean-reverting strategy between an exchange-traded fund (ETF) and its component stocks..."
- Rule as written:
  - Universe: SPY ETF and its top market-cap component stocks.
  - Model: Johansen cointegration test finds stationary linear combination between SPY and individual stocks.
  - Entry / Sizing: Trade unit portfolio proportional to negative Z-score of spread.
  - Exit: Rebalance as spread reverts to mean.
  - Stop loss: not stated.
  - Market: SPY ETF vs component equities.
  - Bar size: Daily closes.
  - Holding time: Multi-day.
- Book's evidence: Cointegration confirmed at 95% confidence level; backtest demonstrates index arbitrage.
- Mechanism (the book's): Authorized participants (APs) enforce parity between an ETF and its underlying basket through physical creation and redemption; temporary tracking dislocations are arbitraged away.
- Mechanism (my inference): none needed.
- Apex fit: no. Cash equity stock basket trading with overnight hold; Apex requires intraday futures.
- Already tested? no.

---

### 8. Cross-Sectional Contrarian Equity Rebalancing (Khandani & Lo 2007)
- Where: Chapter 4, Section 4.4, Examples 4.3 & 4.4 (pp. 81-86)
- Quote: "The implementation of Equation 4.1 in MATLAB is very compact... It has an APR of 13.7 percent and Sharpe ratio of 1.3 from January 2, 2007, to December 30, 2011, even if we backtest on the SPX."
- Rule as written:
  - Universe: S&P 500 stocks (or broader equity universe).
  - Sizing / Portfolio weights: $w_i(t) = - \frac{R_i(t-1) - R_m(t-1)}{\sum_k |R_k(t-1) - R_m(t-1)|}$, where $R_i$ is stock return and $R_m$ is universe mean return. Dollar-neutral long/short portfolio.
  - Entry: Daily rebalancing at market close (or intraday variant in Example 4.4 entering at market open based on overnight close-to-open return $R_{i,co}$).
  - Exit: Liquidate at next close.
  - Stop loss: not stated.
  - Market: S&P 500 equities.
  - Bar size: Daily.
  - Holding time: 1 day (or intraday open to close).
- Book's evidence: Tested on S&P 500 from 2007-01-02 to 2011-12-30: APR = 13.7%, Sharpe ratio = 1.3 (achieved 30% APR in 2008).
- Mechanism (the book's): Short-term reversals in individual stocks driven by institutional order flow execution, liquidity shocks, and bid-ask bounce; liquidity providers earn a return premium for absorbing temporary imbalances.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires trading 500 individual stocks simultaneously long/short; Apex only trades index/commodity futures.
- Already tested? no.

---

### 9. AUD.USD vs CAD.USD Currency Pair Trading with Rollover Carry
- Where: Chapter 5, Section 5.1, Examples 5.1 & 5.2 (pp. 91-96)
- Quote: "In this strategy we use the Johansen test to find out the best hedge ratio of capital, or capital weights, between AUD.USD versus CAD.USD... using CAD.USD in our backtest program doesn't make live trading any more difficult: Whenever the program sends an order to 'Buy 1 unit of CAD.USD,' we should just 'Sell 1/y of USD.CAD'..."
- Rule as written:
  - Pair: AUD.USD and CAD.USD (both quoted in USD).
  - Model: Johansen cointegration test determines capital weights $[w_1, w_2]$.
  - Entry / Sizing: Bollinger band ($Z = \pm 1$) or linear mean reversion on spread Z-score. Long currency with higher interest rate earns daily carry while waiting for mean reversion.
  - Exit: Liquidate when spread reverts to mean ($Z = 0$).
  - Stop loss: not stated.
  - Market: Spot FX (AUD/USD and USD/CAD).
  - Bar size: Daily closes (17:00 ET).
  - Holding time: Multi-day / multi-week.
- Book's evidence: 2007 to 2012: positive performance; Chan shows rollover interest adds substantial yield when aligned with trade direction.
- Mechanism (the book's): Australia and Canada share commodity-exporting macroeconomic linkages, but differing central bank policy interest rates provide a structural carry yield that pays the trader during the mean-reversion holding period.
- Mechanism (my inference): none needed.
- Apex fit: no. Multi-day spot FX trading with overnight rollover; Apex requires intraday futures flat by 15:59 CT.
- Already tested? no.

---

### 10. Crude Oil (CL) 12-Month Calendar Spread Mean Reversion
- Where: Chapter 5, Section 5.2, Examples 5.3 & 5.4 (pp. 102-107)
- Quote: "1. The holding period for a pair of contracts is 3 months (61 trading days). 2. We roll forward to the next pair of contracts 10 days before the current near contract's expiration. 3. The expiration dates of the near and far contracts are 1 year apart... This results in an attractive unlevered APR of 8.3 percent and a Sharpe ratio of 1.3 from January 2, 2008, to August 13, 2012."
- Rule as written:
  - Spread selection: 1-year expiration gap between far contract ($T_2$) and near contract ($T_1$).
  - Roll schedule: Roll forward to the next contract pair 10 days before the near contract's expiration.
  - Signal: Linear mean reversion on forward curve slope parameter $\gamma$ (half-life = 36 trading days). Position proportional to negative Z-score of $\gamma$ (36-day lookback).
  - Holding period: 3 months (61 trading days).
  - Stop loss: not stated.
  - Sizing: Long 1 far contract, Short 1 near contract (unlevered daily P&L divided by 2).
  - Market: NYMEX Light Sweet Crude Oil futures (CL).
  - Bar size: Daily settlement prices.
  - Holding time: 61 trading days (~3 months).
- Book's evidence: Backtested 2008-01-02 to 2012-08-13: Unlevered APR = 8.3%, Sharpe ratio = 1.3.
- Mechanism (the book's): Convenience yield and physical storage costs govern the term structure of storable commodities (theory of storage). Transitory localized supply disruptions affect the front contract disproportionately, creating temporary curve kinks that revert over seasonal storage cycles.
- Mechanism (my inference): none needed.
- Apex fit: no. Holding period is 61 trading days (requires holding positions overnight across months); Apex requires flat by 15:59 CT.
- Already tested? no.

---

### 11. VX Volatility Futures Calendar Spread Mean Reversion
- Where: Chapter 5, Section 5.3 (pp. 107-109)
- Quote: "If we apply our usual linear mean-reverting strategy using ratio as the signal (and with a 15-day look-back for the moving average and standard deviations), VX yields an APR of 17.7 percent and a Sharpe ratio of 1.5 from October 27, 2008, to April 23, 2012... though it performed much more poorly prior to October 2008."
- Rule as written:
  - Signal: Ratio of back-month to front-month VX futures prices: $Ratio = P_{back} / P_{front}$.
  - Model: Linear mean reversion with 15-day lookback for moving average and standard deviation.
  - Entry / Sizing: Position in calendar spread proportional to negative Z-score of ratio.
  - Exit: As ratio mean-reverts.
  - Stop loss: not stated.
  - Market: CBOE VIX futures (VX front and back contracts).
  - Bar size: Daily settlement prices.
  - Holding time: Multi-day.
- Book's evidence: Backtested 2008-10-27 to 2012-04-23: APR = 17.7%, Sharpe ratio = 1.5. Performed poorly prior to Oct 2008 due to a structural regime shift.
- Mechanism (the book's): The term structure of implied volatility is anchored by long-term mean reversion of variance, while front-month contracts reflect immediate event risk, creating mean-reverting term structure fluctuations.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires trading VX futures (unsupported on Apex) and holding positions overnight; Apex requires flat by 15:59 CT.
- Already tested? no.

---

### 12. ES vs VX Intermarket Volatility Spread Mean Reversion
- Where: Chapter 5, Section 5.4, Eq 5.11 (pp. 110-113)
- Quote: "This means that a portfolio that is long 0.3906 contracts of VX and long one contract of ES should be stationary... We can construct a Bollinger band–like mean-reverting strategy by shorting this portfolio whenever its value deviates from one standard deviation of the residuals determined in the training set. The APR on the test set July 29, 2010, to May 8, 2012, is 12.3 percent, with a Sharpe ratio of 1.4."
- Rule as written:
  - Unit portfolio: Long 0.3906 front VX contracts + Long 1 front ES contract (dollar-weighted: $1,000 \times VX + 50 \times ES$).
  - Residual standard deviation: $\sigma = \$2,047$ from linear regression fit on 500-day training set post-August 2008.
  - Entry: Short portfolio when portfolio value deviates $> +1.0 \times \sigma$ ($2,047); Long portfolio when portfolio value deviates $< -1.0 \times \sigma$.
  - Exit: Liquidate when value reverts to regression line (mean).
  - Stop loss: not stated.
  - Market: CBOE VX futures and CME ES futures.
  - Bar size: Daily settlement prices.
  - Holding time: Multi-day / multi-week.
- Book's evidence: Out-of-sample test 2010-07-29 to 2012-05-08: APR = 12.3%, Sharpe ratio = 1.4.
- Mechanism (the book's): Equity index levels and volatility index futures have strong negative correlation; temporary divergences between equity prices and option implied volatility represent pricing inefficiencies that revert to equilibrium.
- Mechanism (my inference): none needed.
- Apex fit: no. VX futures are not available on Apex prop accounts, and strategy holds overnight across multiple weeks.
- Already tested? Matches "mean reversion on NQ / ES" on the brief's failed list.

---

### 13. VX vs ES Roll-Return Momentum / Contango Trading (Simon & Campasano 2012)
- Where: Chapter 6, Section 6.2 (pp. 129-132)
- Quote: "1. If the price of the front contract of VX is higher than that of VIX by 0.1 point (contango) times the number of trading days untill settlement, short 0.3906 front contracts of VX and short 1 front contract of ES. Hold for one day. 2. If the price of the front contract of VX is lower than that of VIX by 0.1 point (backwardation) times the number of trading days untill settlement, buy 0.3906 front contracts of VX and buy 1 front contract of ES. Hold for one day."
- Rule as written:
  - Contango condition: $(Price(VX_{front}) - VIX) > 0.10 \times Days\_to\_settlement$. Action: Short 0.3906 front VX contracts and Short 1 front ES contract.
  - Backwardation condition: $(Price(VX_{front}) - VIX) < -0.10 \times Days\_to\_settlement$. Action: Buy 0.3906 front VX contracts and Buy 1 front ES contract.
  - Holding period: Exactly 1 day (rebalanced daily).
  - Settlement: Day after contracts expire.
  - Stop loss: not stated.
  - Market: CBOE VX futures, CME ES futures, CBOE VIX index.
  - Bar size: Daily settlement/close.
- Book's evidence: Backtested 2010-07-29 to 2012-05-07: APR = 6.9%, Sharpe ratio = 1.0.
- Mechanism (the book's): In contango, front VX decays toward spot VIX as expiration approaches, delivering a severe negative roll yield (~-50% annualized). Shorting VX captures this roll yield, while shorting ES hedges the residual equity market exposure due to the -75% anti-correlation between VX and ES.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires trading VX futures (unsupported on Apex) and holds positions overnight (1-day hold); Apex requires flat by 15:59 CT.
- Already tested? no.

---

### 14. Cross-Sectional Stock Momentum (Jegadeesh & Titman 1993, Daniel & Moskowitz 2011)
- Where: Chapter 6, Section 6.3 (pp. 133-137)
- Quote: "Jegadeesh and Titman (1993) first discovered that stocks that outperformed their peers in the past 3 to 12 months continue to outperform them in the next 3 to 12 months... Daniel and Moskowitz (2011) extended the backtest... to 1927 to 2009."
- Rule as written:
  - Ranking period: 12 months, skipping the most recent month (i.e. returns from month $t-12$ to month $t-2$) to avoid short-term bid-ask bounce.
  - Selection: Long top decile (winners), Short bottom decile (losers).
  - Rebalance / Holding period: Rebalance monthly; hold for 1 month.
  - Sizing: Equal dollar weighting within deciles; dollar neutral long/short.
  - Stop loss: not stated.
  - Market: Broad US equities (CRSP universe).
  - Bar size: Monthly closes.
- Book's evidence: 1927 to 2009 in Daniel & Moskowitz: strong positive returns historically, but subject to severe "momentum crashes" (e.g. 1932 and 2009) when panic selling abruptly rebounds.
- Mechanism (the book's): Underreaction by investors due to behavioral biases (anchoring, conservatism bias, slow institutional diffusion of information), followed by late-stage herding.
- Mechanism (my inference): none needed.
- Apex fit: no. Monthly equity stock basket held overnight; Apex requires intraday futures.
- Already tested? no.

---

### 15. News Sentiment Factor Momentum (RavenPack / Hafez & Xie 2012)
- Where: Chapter 6, Section 6.4 (pp. 138-141)
- Quote: "Hafez and Xie (2012) tested a strategy based on RavenPack news sentiment scores... buy the stock at open if sentiment is positive, short if negative, holding from 1 to 5 days."
- Rule as written:
  - Signal: RavenPack news sentiment score (> 50 = positive news, < 50 = negative news).
  - Entry: Enter at market open following news release.
  - Exit / Holding period: Hold for 1 to 5 days (1-day hold gave highest Sharpe).
  - Stop loss: not stated.
  - Sizing: Equal weighting across news-triggered stocks.
  - Market: US equities (Russell 3000 universe).
  - Bar size: Daily open and close.
- Book's evidence: Hafez & Xie (2012) reported annualized return around 18–20% with Sharpe > 2.0 before transaction costs.
- Mechanism (the book's): Slow information diffusion and institutional execution constraints prevent stock prices from adjusting instantaneously to news events, resulting in multi-day drift.
- Mechanism (my inference): none needed.
- Apex fit: no. Single-stock universe, requires paid external news feed, holds overnight; Apex is intraday futures without external APIs.
- Already tested? no.

---

### 16. Mutual Fund Forced Fire Sales and Forced Purchases (Coval & Stafford 2007)
- Where: Chapter 6, Section 6.5 (pp. 141-144)
- Quote: "Researchers Coval and Stafford (2007) found that mutual funds experiencing large redemptions are likely to reduce or eliminate their existing stock positions... Stocks disproportionately held by poorly performing mutual funds facing redemptions therefore experience negative returns... Hence, momentum in both directions for the commonly held stocks can be ignited."
- Rule as written:
  - Signal: Measure capital flow pressure $PRESSURE_i$ on stock $i$ based on the net percentage of funds holding it that experience extreme outflows (bottom 10%) vs inflows (top 10%).
  - Action: Short stocks experiencing extreme fire sales and long stocks experiencing extreme inflows during the quarter of forced pressure (momentum); or buy fire-sale stocks after the pressure abates (mean-reversion rebound).
  - Holding time: 1 quarter to 1 year.
  - Stop loss: not stated.
  - Market: US equities held by mutual funds.
  - Bar size: Quarterly / daily.
- Book's evidence: Coval & Stafford (2007) demonstrated significant price distortion of several percentage points during pressure quarters, followed by multi-quarter mean reversion.
- Mechanism (the book's): Mutual funds maintain minimal cash buffers and are legally compelled to liquidate holdings to meet investor redemption requests regardless of valuation. This forced selling depresses prices, suppressing returns of other funds holding the same stocks and triggering further contagious redemptions.
- Mechanism (my inference): none needed.
- Apex fit: no. Multi-month/quarterly holding of individual stocks; Apex is intraday futures only.
- Already tested? no.

---

### 17. Opening Gap Momentum on Index Futures (FSTX & GBPUSD)
- Where: Chapter 7, Section 7.1, Example 7.1 (pp. 149-152)
- Quote: "In Chapter 4, we discussed a mean-reverting buy-on-gap strategy for stocks. The opposite momentum strategy will sometimes work on futures and currencies: buying when the instrument gaps up, and shorting when it gaps down. After being tested on a number of futures, this strategy proved to work best on the Dow Jones STOXX 50 index futures (FSTX) trading on Eurex, which generates an annual percentage rate (APR) of 13 percent and a Sharpe ratio of 1.4 from July 16, 2004, to May 17, 2012."
- Rule as written:
  - Entry: At market open, compare open to previous day's trading range:
    - If $Open > High_{t-1}$, BUY at market open.
    - If $Open < Low_{t-1}$, SELL SHORT at market open.
    - (Alternative variant tested in code: open outside previous close or range by moving standard deviation threshold).
  - Exit: Liquidate at the same day's market close.
  - Stop loss: not stated.
  - Sizing: 1 contract (fixed size).
  - Market: Eurex Dow Jones STOXX 50 index futures (FSTX); also tested on GBPUSD (with 05:00 ET London open and 17:00 ET close).
  - Bar size: Daily Open, High, Low, Close (executed at open and close).
  - Holding time: Intraday (open to close; flat by end of day).
- Book's evidence: FSTX backtest 2004-07-16 to 2012-05-17: APR = 13%, Sharpe ratio = 1.4. GBPUSD 2007-07-23 to 2012-02-20: APR = 7.2%, Sharpe ratio = 1.3.
- Mechanism (the book's): Overnight news and accumulated non-trading orders cause the open to gap outside the previous day's price range. Stop-loss orders clustered at previous day highs or lows are triggered all at once at the open, creating a cascading liquidation effect that drives continued directional price momentum throughout the trading session.
- Mechanism (my inference): none needed (book explicitly provides stop cascading and overnight news explanation).
- Apex fit: YES.
  - Flat by 15:59 CT? Yes (enters at open, liquidates at close; flat by 15:00/15:15 CT).
  - Markets: Equity index futures (NQ, ES, or micros MNQ, MES; equivalent to FSTX tested in book).
  - Single stop loss fitting $2,000 trailing drawdown? Yes, when traded on micros (MNQ/MES) with an intraday catastrophic stop loss.
- Already tested? no. (Brief noted "mean reversion on NQ / ES" failed; this is opening gap *momentum*, not mean reversion. Overnight Bias in combine set uses 15m range break with ADX, but Chan's pure daily open gap momentum rule is not on the failed list).

---

### 18. Intraday Post-Earnings Announcement Drift (PEAD)
- Where: Chapter 7, Section 7.2, Example 7.2 (pp. 153-157)
- Quote: "What I will show in this section is that as recently as 2011 this strategy is still profitable if we enter at the market open after the earnings announcement was made after the previous close, buying the stock if the return is very positive and shorting if the return is very negative, and liquidate the position at the same day's close... For a universe of S&P 500 stocks, the APR from January 3, 2011, to April 24, 2012, is 6.7 percent, while the Sharpe ratio is a very respectable 1.5."
- Rule as written:
  - Universe: S&P 500 stocks with earnings announced between previous trading day 16:00 ET close and today's 09:30 ET open.
  - Signal: Return from previous close to today's open: $R_{gap} = (Open_t - Close_{t-1}) / Close_{t-1}$.
  - Entry:
    - If $R_{gap} > +1.0 \times \sigma_{90}$, BUY at market open (09:30 ET).
    - If $R_{gap} < -1.0 \times \sigma_{90}$, SELL SHORT at market open (09:30 ET).
    - ($\sigma_{90}$ is 90-day moving standard deviation of close-to-open returns).
  - Exit: Liquidate at the same day's market close (16:00 ET).
  - Stop loss: not stated.
  - Sizing: Capital divided equally across active positions (denominated by max expected positions, e.g. 30).
  - Market: S&P 500 individual stocks.
  - Bar size: Daily Open and Close.
  - Holding time: Intraday (09:30 ET to 16:00 ET; flat overnight).
- Book's evidence: Tested on S&P 500 from 2011-01-03 to 2012-04-24: APR = 6.7%, Sharpe ratio = 1.5. Max 30 simultaneous positions.
- Mechanism (the book's): Earnings announcements create massive informational shocks. Institutional investors cannot complete large block reallocations immediately due to market impact constraints, so their execution orders drift into the market throughout the trading day in the direction of the earnings surprise.
- Mechanism (my inference): none needed.
- Apex fit: no. Applied strictly to single stocks (not tradeable on Apex prop accounts).
- Already tested? no.

---

### 19. Leveraged ETF End-of-Day Momentum (Cheng & Madhavan 2009)
- Where: Chapter 7, Section 7.3 (pp. 158-161)
- Quote: "We can test this hypothesis by constructing a very simple momentum strategy: buy DRN if the return from previous day's close to 15 minutes before market close is greater than 2 percent, and sell if the return is smaller than −2 percent. Exit the position at the market close. Note that this momentum strategy is based on the momentum of the underlying stocks, so it should be affecting the near-market-close returns of the unlevered ETFs such as SPY as well... The APR of trading DRN is 15 percent with a Sharpe ratio of 1.8 from October 12, 2011, to October 25, 2012."
- Rule as written:
  - Time of evaluation: 15 minutes before market close (15:45 ET / 14:45 CT).
  - Return calculation: Return from previous day's close to 15:45 ET today: $R = \frac{Price(15:45) - Close_{t-1}}{Close_{t-1}}$.
  - Entry:
    - If $R > +2.0\%$, BUY at 15:45 ET (14:45 CT).
    - If $R < -2.0\%$, SELL SHORT at 15:45 ET (14:45 CT).
  - Exit: Liquidate at market close (16:00 ET / 15:00 CT).
  - Holding time: Exactly 15 minutes.
  - Stop loss: not stated.
  - Sizing: 1 unit / fixed allocation.
  - Market: Leveraged ETFs (DRN tested; also FAS, FAZ, TNA, TQQQ) or underlying index instruments (SPY, ES, NQ futures).
  - Bar size: 15-minute / intraday minute bars.
- Book's evidence: DRN backtest 2011-10-12 to 2012-10-25: APR = 15%, Sharpe ratio = 1.8. Cites Cheng & Madhavan (2009) showing a 1% move in SPX necessitates buying/selling ~17% of market-on-close volume across $19 billion in leveraged ETF AUM.
- Mechanism (the book's): Leveraged ETFs (2x, 3x, and inverse) must maintain constant leverage by regulatory prospectus mandate at daily close. When the market has moved substantially (+2% or -2%), compounding changes their debt-to-equity ratio, legally obligating ETF fund sponsors to rebalance in the final 15-30 minutes of the day by aggressively buying more assets on up days and dumping assets on down days. They are 100% price-insensitive forced buyers/sellers executing into the market-on-close.
- Mechanism (my inference): none needed (book provides full structural mathematical derivation of the forced rebalancing flow).
- Apex fit: YES.
  - Flat by 15:59 CT? Yes (enters 14:45 CT, exits 15:00 CT; flat 59 minutes before Apex 15:59 CT cutoff).
  - Markets: NQ, ES, or micros MNQ, MES (where leveraged ETFs TQQQ/SQQQ and UPRO/SPXU create identical closing rebalancing flows).
  - Single stop loss fitting $2,000 trailing drawdown? Yes, 15-minute holding period with a defined stop on micro contracts has minimal adverse excursion.
- Already tested? no. (User has "Late-Day Flow" as Task 07 in funded plan, but this specific Chan rule with a +2%/-2% return threshold and 15-minute holding window is distinct and not on the failed list).

---

### 20. High-Frequency Order Book Imbalance / Ratio Trading / Ticking
- Where: Chapter 7, Section 7.4 (pp. 161-168)
- Quote: "Most high-frequency momentum strategies involve extracting information from the order book, and the basic idea is simple: If the bid size is much bigger than the ask size, expect the price to tick up and vice versa... In markets that fill orders on a pro-rata basis such as the Eurodollar futures trading on CME, the simplest way to benefit from this expectation is just to 'join the bid' immediately... In markets where the bid-ask spread is bigger than two ticks... place the buy order at the best bid plus one tick... called ticking or quote matching."
- Rule as written:
  - Signal: Imbalance $I = (BidSize - AskSize) / (BidSize + AskSize)$ or bid size >> ask size.
  - Entry: Join bid immediately (pro-rata markets) or submit limit buy at best bid + 1 tick (price-time priority markets with spread > 2 ticks).
  - Exit: Sell limit at best ask - 1 tick (or at bid + 1 tick profit), or scratch at original bid if unfilled.
  - Stop loss: Sell at best bid (loss of commissions + 1 tick).
  - Sizing: Ratio of own order to aggregate depth.
  - Market: CME Eurodollar futures, equities, FX.
  - Bar size: Tick-by-tick order book data (Level 2/3).
  - Holding time: Milliseconds to seconds.
- Book's evidence: Cites Maslov & Mills (2001) linear relationship between order book imbalance and short-term price moves on Nasdaq; Hellström & Simonsen (2006). No standalone quantitative backtest table given by Chan.
- Mechanism (the book's): Immediate order queue priority front-runs informed market orders; large institutional orders arriving as market orders consume opposing book liquidity, creating short-term price drift.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires sub-millisecond execution, queue position tracking, and direct market access (DMA); retail Rithmic API / MultiCharts bar architecture cannot support HFT queue matching, and "order-flow indicator filters" is on the brief's failed list.
- Already tested? Matches "order-flow indicator filters" on the brief's failed list.

---

## Ranked Shortlist of Apex-Compatible Ideas

Of the 20 ideas identified in the book, only 2 strictly meet all three criteria:
1. **Apex-compatible**: Flat by 15:59 CT (no overnight hold), tradeable on index/commodity futures (NQ / ES / CL / GC / ZN or micros), with risk that fits a $2,000 trailing drawdown.
2. **Not already tested**: Not in the brief's "Already tested and failed" list.
3. **Stated mechanism**: Have an explicit economic or structural mechanism explaining who is forced or paid to trade.

Ranked by the clarity of the forced trader:

### 1. Leveraged ETF End-of-Day Momentum (Idea 19)
- **Rank**: 1
- **Where**: Chapter 7, Section 7.3 (pp. 158-161)
- **Why #1**: The forced trader is crystal clear and legally mandated. Leveraged ETF sponsors (e.g. ProShares, Direxion managing TQQQ, SQQQ, UPRO, SPXU) must maintain constant daily leverage by prospectus rule at the market close. On large trend days ($|Return| \ge 2\%$), their compounding math forces them to execute massive market-on-close orders in the same direction as the day's trend during the final 15 minutes (15:45–16:00 ET / 14:45–15:00 CT). They are completely price-insensitive forced buyers or sellers.
- **Apex implementation**: Evaluated at 14:45 CT on NQ/ES (or MNQ/MES). If return from prior close $> +2\%$, buy; if $< -2\%$, short. Liquidate at 15:00 CT. Flat 59 minutes before the 15:59 CT cutoff. 15-minute holding time fits well within the $2,000 trailing drawdown.

### 2. Opening Gap Momentum on Index Futures (Idea 17)
- **Rank**: 2
- **Where**: Chapter 7, Section 7.1, Example 7.1 (pp. 149-152)
- **Why #2**: The forced traders are overnight inventory holders and breakout stop-loss orders. When the open gaps outside the previous day's entire range ($Open > High_{t-1}$ or $Open < Low_{t-1}$), accumulated resting stop orders clustered above yesterday's high or below yesterday's low are triggered simultaneously at the opening bell, forcing automatic market orders that fuel an intraday momentum trend.
- **Apex implementation**: Evaluated at the regular session open on NQ/ES (or MNQ/MES). If $Open > High_{t-1}$, buy; if $Open < Low_{t-1}$, short. Exit at the market close (15:00/15:15 CT, well before 15:59 CT). Sized on micros (MNQ/MES) with an intraday catastrophic stop loss to fit the $2,000 trailing drawdown.
