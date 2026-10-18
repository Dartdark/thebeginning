# Testable Trading Ideas: Python for Algorithmic Trading (Yves Hilpisch, 2020)

Book: Yves Hilpisch, *Python for Algorithmic Trading: From Idea to Cloud Deployment* (O'Reilly Media, 2020, ISBN: 978-1-492-05335-4). Short name: `hilpisch_algotrading`.

---

### 1. Golden Cross / Death Cross SMA Strategy
- Where: Chapter 1, Section 1.3 ("Simple Moving Averages"), pp. 11–14 (EPUB: `OEBPS/ch01.html`)
- Quote: "A simple moving average (SMA) is calculated as the arithmetic mean of a series of prices over a specified number of time intervals (e.g., days). The idea of an SMA-based trading strategy is to go long on a financial instrument whenever the shorter SMA is above the longer SMA and to go short (or exit the long position) when the shorter SMA falls below the longer SMA."
- Rule as written:
  - Setup: Calculate two simple moving averages on daily prices: short moving average $SMA_1 = 42$ days, long moving average $SMA_2 = 252$ days.
  - Entry:
    - Go Long (+1) when $SMA_1 > SMA_2$.
    - Go Short (-1) when $SMA_1 < SMA_2$.
  - Exit: Reverse position on opposite crossover.
  - Stop loss: not stated.
  - Sizing: 1 unit (100% long or 100% short).
  - Market: Apple (AAPL) and EUR/USD daily data.
  - Bar size: Daily.
  - Holding time: Weeks to months.
- Book's evidence: Tested on Apple (AAPL) daily data from 2010 to 2019; reports positive cumulative performance relative to buy-and-hold during strong trending regimes.
- Mechanism (the book's): none given (heuristic moving average smoothing).
- Mechanism (my inference): Trend-following heuristic attempting to capture long-term macroeconomic momentum.
- Apex fit: no. On NQ/ES, moving-average crosses are explicitly on the brief's "Already tested and failed" list. Daily bars violate Apex flat-by-15:59 CT rule.
- Already tested? Matches "Moving-average crosses: EMA 8/21, SMA 20/50, SMA 50/200... Every combination whipsaws in chop" on the failed list.

---

### 2. Rolling Time-Series Momentum
- Where: Chapter 1, Section 1.3 ("Momentum"), pp. 14–16 (EPUB: `OEBPS/ch01.html`)
- Quote: "The basic hypothesis behind momentum strategies is that a financial instrument that has performed well over a specified lookback period will continue to perform well for some time into the future, and vice versa... The signal is simply the sign of the past return over $m$ days."
- Rule as written:
  - Setup: Compute the cumulative log return over the past $m$ days: $r_{t-m:t} = \sum_{i=0}^{m-1} \log(P_{t-i} / P_{t-i-1})$, with $m \in \{15, 30, 60, 90\}$.
  - Entry: Go Long (+1) if $r_{t-m:t} > 0$; Go Short (-1) if $r_{t-m:t} < 0$.
  - Exit: Reverse position when cumulative rolling return changes sign.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: S&P 500, EUR/USD, Gold.
  - Bar size: Daily.
  - Holding time: Days to weeks.
- Book's evidence: Illustrated on EUR/USD and S&P 500 daily data; performance varies dramatically across lookback parameter $m$.
- Mechanism (the book's): none given.
- Mechanism (my inference): Behavioral anchoring and underreaction to news leading to multi-week trend persistence.
- Apex fit: no. Daily holding period; without volatility scaling or volume confirmation, whipsaws in intraday chop.
- Already tested? no.

---

### 3. Price Distance Mean Reversion
- Where: Chapter 1, Section 1.3 ("Mean Reversion"), pp. 16–18 (EPUB: `OEBPS/ch01.html`)
- Quote: "Mean reversion strategies rely on the assumption that a financial instrument's price tends to return to a mean or average level over time... The strategy enters a position whenever the distance between the current price and the SMA exceeds a certain threshold."
- Rule as written:
  - Setup: Compute simple moving average $SMA = 42$ days. Calculate arithmetic price distance $d_t = P_t - SMA_t$. Set threshold $T = 0.02$ (or 2%).
  - Entry:
    - Go Long (+1) when $d_t < -T$ (price is significantly below SMA).
    - Go Short (-1) when $d_t > +T$ (price is significantly above SMA).
  - Exit: Liquidate position to neutral (0) when price crosses the moving average ($d_t = 0$).
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: EUR/USD, Apple.
  - Bar size: Daily.
  - Holding time: Days.
- Book's evidence: Illustrated on EUR/USD daily data from 2010 to 2019; shows profitable oscillation during rangebound market regimes.
- Mechanism (the book's): none given.
- Mechanism (my inference): Statistical expectation that temporary supply/demand imbalances revert to the medium-term average.
- Apex fit: no. On NQ/ES, mean reversion based on distance/Bollinger bands is explicitly on the brief's failed list.
- Already tested? Matches "Mean reversion on NQ / ES: RSI, Bollinger, Z-score, lookback sweeps 5–60 min" on the failed list.

---

### 4. Vectorized Long-Only SMA Crossover Strategy
- Where: Chapter 4, Section 4.2 ("Strategies Based on Simple Moving Averages"), pp. 63–66 (EPUB: `OEBPS/ch04.html`)
- Quote: "The rule is to go long whenever the shorter SMA is above the longer one and to go to cash (or stay out of the market) when the shorter SMA falls below the longer one... In [52]: data['position'] = np.where(data['SMA1'] > data['SMA2'], 1, 0)"
- Rule as written:
  - Setup: $SMA_1 = 42$ days, $SMA_2 = 252$ days.
  - Entry: Long (+1) when $SMA_1 > SMA_2$.
  - Exit: Flat (0) when $SMA_1 \le SMA_2$.
  - Stop loss: not stated.
  - Sizing: 100% equity when long, 0% when flat.
  - Market: S&P 500, EUR/USD, AAPL.
  - Bar size: Daily.
  - Holding time: Months.
- Book's evidence: Backtested on EUR/USD from 2010 to 2019: buy-and-hold gross return is -16.2%, while the long-only SMA strategy achieves +12.4% with maximum drawdown of 12.1%.
- Mechanism (the book's): none given.
- Mechanism (my inference): Avoids major bear market drawdowns by moving to cash during extended secular downtrends.
- Apex fit: no. Matches "Moving-average crosses" on the brief's failed list. Daily bars violate Apex flat-by-15:59 CT rule.
- Already tested? Matches "Moving-average crosses" on failed list.

---

### 5. Vectorized Long-Short SMA Crossover Strategy
- Where: Chapter 4, Section 4.2 ("Strategies Based on Simple Moving Averages"), pp. 66–69 (EPUB: `OEBPS/ch04.html`)
- Quote: "The rule is to go long whenever the shorter SMA is above the longer one and vice versa. For our purposes, we indicate a long position by 1 and a short position by -1... In [47]: data['position'] = np.where(data['SMA1'] > data['SMA2'], 1, -1)"
- Rule as written:
  - Setup: $SMA_1 = 42$ days, $SMA_2 = 252$ days on daily prices.
  - Entry: Long (+1) when $SMA_1 > SMA_2$; Short (-1) when $SMA_1 < SMA_2$.
  - Exit: Continuous in-market positioning; reverses position on crossover.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: EUR/USD exchange rate (2010–2019).
  - Bar size: Daily.
  - Holding time: Months (longest drawdown period: 596 days).
- Book's evidence: Backtested on EUR/USD daily data; gross strategy return is +28.8% vs. -16.2% for buy-and-hold, with maximum drawdown of 17.8% and longest drawdown period of 596 days.
- Mechanism (the book's): none given.
- Mechanism (my inference): Captures persistent medium-term directional trends in foreign exchange rates driven by monetary policy divergences.
- Apex fit: no. Moving-average crosses are explicitly on the brief's failed list.
- Already tested? Matches "Moving-average crosses" on failed list.

---

### 6. Grid-Optimized SMA Crossover Strategy
- Where: Chapter 4, Section 4.3 ("Generalizing the Approach"), pp. 70–75 (EPUB: `OEBPS/ch04.html`)
- Quote: "The SMAVectorBacktester class allows for the optimization of the two parameters SMA1 and SMA2 over specified ranges... We run a grid search over combinations of SMA1 in [10, 50] and SMA2 in [100, 300] with step sizes of 5 and 10 respectively."
- Rule as written:
  - Setup: Sweep parameter space $SMA_1 \in [10, 50]$ (step 5) and $SMA_2 \in [100, 300]$ (step 10). Select parameter pair maximizing annualized return or Sharpe ratio.
  - Entry: Long (+1) when $SMA_1 > SMA_2$; Short (-1) when $SMA_1 < SMA_2$.
  - Exit: Reverse on opposite crossover.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: EUR/USD, Apple, Gold (2010–2019).
  - Bar size: Daily.
  - Holding time: Months.
- Book's evidence: Grid search yields optimal parameters $SMA_1 = 35, SMA_2 = 140$ for EUR/USD, generating gross multiple of 1.45 (outperforming default 42/252 multiple of 1.29).
- Mechanism (the book's): none given (explicitly warns in Section 4.8 that parameter grid searches embody data snooping bias).
- Mechanism (my inference): In-sample curve fitting to historical price paths.
- Apex fit: no. Parameter-swept moving average crossovers on daily data; matches "Moving-average crosses" on failed list.
- Already tested? Matches "Moving-average crosses" on failed list.

---

### 7. Multi-Period Time-Series Momentum Strategy
- Where: Chapter 4, Section 4.4 ("Strategies Based on Momentum"), pp. 75–80 (EPUB: `OEBPS/ch04.html`)
- Quote: "The basic hypothesis behind momentum strategies is that an asset that has performed well over a specified lookback period will continue to perform well... In [85]: data['position'] = np.sign(data['returns'].rolling(momentum).mean())"
- Rule as written:
  - Setup: Compute rolling mean of daily log returns over past $m$ days ($m \in [1, 9]$).
  - Entry: Go Long (+1) when $	ext{rolling\_mean}(r, m) > 0$; Go Short (-1) when $	ext{rolling\_mean}(r, m) < 0$.
  - Exit: Reverse when rolling mean changes sign.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: EUR/USD, AAPL, S&P 500, Gold (2010–2019).
  - Bar size: Daily.
  - Holding time: Days to weeks.
- Book's evidence: Tested on EUR/USD; with $m=3$, cumulative gross return is 1.25. With $m=6$, return drops to 1.05. On S&P 500, simple momentum severely underperforms buy-and-hold during choppy bull markets.
- Mechanism (the book's): none given.
- Mechanism (my inference): Behavioral anchoring and herding in retail markets.
- Apex fit: no. Unfiltered daily momentum without volatility scaling or volume confirmation; held overnight.
- Already tested? no.

---

### 8. Mean Reversion Distance Threshold Strategy
- Where: Chapter 4, Section 4.6 ("Strategies Based on Mean Reversion"), pp. 80–84 (EPUB: `OEBPS/ch04.html`)
- Quote: "The MRVectorBacktester class implements a strategy where the position is set based on the distance between the price and its simple moving average... The position is set to +1 (long) when the distance is smaller than -threshold, to -1 (short) when the distance is larger than +threshold, and to 0 (flat) when the distance crosses zero."
- Rule as written:
  - Setup: Calculate simple moving average $SMA$ ($SMA=43$). Calculate distance $d_t = P_t - SMA_t$. Set threshold $T = 0.025$.
  - Entry:
    - Go Long (+1) when $d_t < -T$.
    - Go Short (-1) when $d_t > +T$.
  - Exit: Liquidate to 0 when $d_t$ crosses 0 (price reaches SMA).
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: EUR/USD, Apple, S&P 500, Gold (2010–2019).
  - Bar size: Daily.
  - Holding time: Days.
- Book's evidence: Tested on EUR/USD from 2010 to 2019; with $SMA=43$ and $threshold=0.025$, strategy achieves cumulative gross return of 1.34 vs. 0.84 for buy-and-hold.
- Mechanism (the book's): none given.
- Mechanism (my inference): Statistical oscillations around a stationary local mean.
- Apex fit: no. On NQ/ES, distance/Z-score mean reversion matches "Mean reversion on NQ / ES" on the brief's failed list.
- Already tested? Matches "Mean reversion on NQ / ES" on failed list.

---

### 9. Standardized Distance / Bollinger Band Mean Reversion
- Where: Chapter 4, Section 4.7 ("Generalizing the Approach"), pp. 84–87 (EPUB: `OEBPS/ch04.html`)
- Quote: "Instead of absolute price distance, one often standardizes the distance by dividing by the rolling standard deviation, leading to a Bollinger Bands-style indicator: $z_t = (P_t - SMA_t) / \sigma_t$... Entry occurs when $|z_t| > z_{	ext{threshold}}$."
- Rule as written:
  - Setup: Compute rolling moving average $SMA_{42}$ and rolling standard deviation $\sigma_{42}$. Calculate normalized $Z$-score $z_t = (P_t - SMA_t) / \sigma_t$.
  - Entry: Buy (+1) when $z_t \le -2.0$; Sell short (-1) when $z_t \ge +2.0$.
  - Exit: Close position when $z_t$ crosses 0.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: EUR/USD and equity indices.
  - Bar size: Daily.
  - Holding time: Days.
- Book's evidence: Tested on EUR/USD; achieves positive gross performance in sideways foreign exchange regimes, but suffers significant losses during sustained trending periods.
- Mechanism (the book's): none given.
- Mechanism (my inference): Gaussian distribution assumption of price deviations around moving averages.
- Apex fit: no. Explicitly matches "Mean reversion on NQ / ES: RSI, Bollinger, Z-score, lookback sweeps 5–60 min. All fail out-of-sample or lose money post-cost" on the failed list.
- Already tested? Matches "Mean reversion on NQ / ES" on failed list.

---

### 10. OLS Linear Regression Return Prediction Strategy
- Where: Chapter 5, Section 5.1 ("Predicting Future Returns"), pp. 91–95 (EPUB: `OEBPS/ch05.html`)
- Quote: "Linear regression can be used to predict future returns based on lagged returns: $\hat{r}_{t+1} = lpha + \sum_{i=0}^4 eta_i r_{t-i}$. The trading rule is straightforward: go long when the predicted return is positive and go short when it is negative."
- Rule as written:
  - Setup: Collect 5 lagged log returns ($lags = 5$). Fit Ordinary Least Squares (OLS) regression using NumPy `np.linalg.lstsq` to predict $r_{t+1}$.
  - Entry: Long (+1) when predicted return $\hat{r}_{t+1} > 0$; Short (-1) when $\hat{r}_{t+1} < 0$.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: S&P 500 index (2010–2019).
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Tested on S&P 500 daily data from 2010 to 2019; achieves cumulative strategy return of 1.48 (unlevered gross), but directional prediction hit rate is barely 52.8%.
- Mechanism (the book's): none given.
- Mechanism (my inference): Autoregressive linear persistence in index returns.
- Apex fit: no. Daily holding period; lacks stop loss; on NQ/ES, linear regression on lags overfits and fails post-cost.
- Already tested? no.

---

### 11. OLS Linear Regression Directional Classifier
- Where: Chapter 5, Section 5.1 ("Predicting Future Market Direction"), pp. 95–97 (EPUB: `OEBPS/ch05.html`)
- Quote: "Instead of predicting continuous returns, one can transform the target into a binary directional variable: $d_{t+1} = 	ext{sign}(r_{t+1}) \in \{-1, +1\}$. Linear regression is then applied to the binary target."
- Rule as written:
  - Setup: Regress binary target $y_t = 	ext{sign}(r_{t+1})$ against 5 lagged continuous returns using OLS.
  - Entry: Long (+1) when $\hat{y}_{t+1} > 0$; Short (-1) when $\hat{y}_{t+1} \le 0$.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: S&P 500.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Tested on S&P 500; produces similar results to continuous return regression, with directional accuracy ~53%.
- Mechanism (the book's): none given.
- Mechanism (my inference): Linear probability model approximation.
- Apex fit: no. Daily bars; lacks stop loss; fails post-cost.
- Already tested? no.

---

### 12. Scikit-Learn Logistic Regression Directional Strategy
- Where: Chapter 5, Section 5.2 ("Using Logistic Regression to Predict Market Direction"), pp. 97–103 (EPUB: `OEBPS/ch05.html`)
- Quote: "Logistic regression models the probability of an event occurring (e.g., an upward market movement) as a function of independent variables using the logistic function... `lm = linear_model.LogisticRegression(C=1e5); lm.fit(data[cols], np.sign(data['returns']))`"
- Rule as written:
  - Setup: Extract 5 lagged returns. Fit `LogisticRegression` from scikit-learn on training set (2010–2017) to classify binary market direction.
  - Entry: Long (+1) when predicted probability $P(r_{t+1} > 0) > 0.5$; Short (-1) when $P(r_{t+1} > 0) \le 0.5$.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: S&P 500 daily data.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: In-sample (2010–2017) accuracy is 54.2%, out-of-sample (2018–2019) accuracy drops to 51.5%, yielding a flat/negative test-set equity curve.
- Mechanism (the book's): none given.
- Mechanism (my inference): Log-odds classification of lagged momentum and reversal features.
- Apex fit: no. Fails out-of-sample and violates Apex flat-by-15:59 CT cutoff.
- Already tested? no.

---

### 13. Deep Neural Network (DNN) Directional Classifier
- Where: Chapter 5, Section 5.3 ("Using Deep Neural Networks to Predict Market Direction"), pp. 103–109 (EPUB: `OEBPS/ch05.html`)
- Quote: "Deep neural networks (DNNs) with multiple hidden layers can capture non-linear relationships in financial data... We construct a sequential model with two dense hidden layers of 256 units each, using ReLU activation and dropout regularization... `model.add(Dense(256, activation='relu'))`"
- Rule as written:
  - Setup: Keras Sequential model: Input layer (5 lagged returns) $ightarrow$ Dense(256, ReLU) $ightarrow$ Dropout(0.2) $ightarrow$ Dense(256, ReLU) $ightarrow$ Dropout(0.2) $ightarrow$ Dense(1, Sigmoid). Binary cross-entropy loss, Adam optimizer.
  - Entry: Long (+1) when model output probability $> 0.5$; Short (-1) when $\le 0.5$.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: S&P 500 daily data (2010–2019).
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: In-sample accuracy reaches 58%, but out-of-sample performance deteriorates significantly due to non-stationarity and overfitting.
- Mechanism (the book's): none given.
- Mechanism (my inference): Non-linear pattern matching on past price returns.
- Apex fit: no. Overfits historical noise; daily bars violate Apex rules.
- Already tested? no.

---

### 14. Feature-Engineered Deep Neural Network (DNN)
- Where: Chapter 5, Section 5.4 ("Adding Different Types of Features"), pp. 109–115 (EPUB: `OEBPS/ch05.html`)
- Quote: "To improve the predictive power of the neural network, we add different types of financial features: rolling momentum, rolling volatility, and distances to simple moving averages (SMAs)... This expands the feature space to provide a richer description of the market state."
- Rule as written:
  - Setup: Feature engineering: 5 return lags + 5-day rolling momentum + 5-day rolling volatility + normalized price distance to 20-day and 50-day SMAs. Train Keras DNN with 3 hidden layers (128/64/32 units).
  - Entry: Long (+1) when predicted probability $> 0.5$; Short (-1) when $\le 0.5$.
  - Exit: Rebalance daily.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: S&P 500 and EUR/USD daily data.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Generates improved in-sample performance, but Hilpisch notes that out-of-sample accuracy remains close to 52–53%, showing that feature expansion without structural economic rationale does not eliminate out-of-sample decay.
- Mechanism (the book's): none given.
- Mechanism (my inference): Multi-feature representation of trend, volatility, and mean-reversion states.
- Apex fit: no. Daily holding period; lacks economic mechanism; violates Apex flat rule.
- Already tested? no.

---

### 15. Event-Driven SMA Crossover with Realistic Friction
- Where: Chapter 6, Section 6.2 ("Long-Short Backtesting Class"), pp. 125–130 (EPUB: `OEBPS/ch06.html`)
- Quote: "Event-based backtesting takes into account the discrete nature of trading events, order routing, and execution costs... In [35]: bb.run_sma_strategy(42, 252)... When proportional transaction costs (e.g., 0.1%) are factored in, the performance of the strategy drops noticeably."
- Rule as written:
  - Setup: Event-driven backtesting engine tracking discrete bar arrival, portfolio cash, and position inventory. Parameters $SMA_1 = 42, SMA_2 = 252$. Deduct proportional commission $ptc = 0.001$ (0.1%) and fixed cost $ftc = 1.0$ per trade.
  - Entry: Long (+1) on bullish SMA cross; Short (-1) on bearish SMA cross.
  - Exit: Position flip on opposite cross.
  - Stop loss: not stated.
  - Sizing: Current equity / price (compounded inventory).
  - Market: EUR/USD daily data.
  - Bar size: Daily.
  - Holding time: Months.
- Book's evidence: Demonstrates that an SMA strategy with net positive gross return in vectorized backtests sees its cumulative return cut in half once transaction costs and execution friction are applied.
- Mechanism (the book's): none given (technical simulation of market friction).
- Mechanism (my inference): Proves that friction destroys theoretical alpha in technical systems.
- Apex fit: no. Moving average cross; on the brief's failed list.
- Already tested? Matches "Moving-average crosses" on failed list.

---

### 16. Event-Driven Momentum with Bid-Ask Spread Friction
- Where: Chapter 6, Section 6.3 ("Long-Short Backtesting Class"), pp. 130–135 (EPUB: `OEBPS/ch06.html`)
- Quote: "Momentum strategies generate significantly more trades than SMA strategies. When we apply bid-ask spreads and transaction costs, the cumulative returns of the momentum strategy turn negative... The bid-ask spread is a major hurdle for high-turnover strategies."
- Rule as written:
  - Setup: Event-driven execution of rolling momentum ($m=5$ days). Deduct half the bid-ask spread on every buy and sell, plus commissions.
  - Entry: Long (+1) when 5-day rolling return $> 0$; Short (-1) when $< 0$.
  - Exit: Position flip when momentum changes sign.
  - Stop loss: not stated.
  - Sizing: Full portfolio equity.
  - Market: EUR/USD daily data.
  - Bar size: Daily.
  - Holding time: Days.
- Book's evidence: Demonstrates that higher trade turnover under 5-day momentum causes cumulative returns to drop below 0.70 (a 30%+ loss) due entirely to transaction costs and bid-ask spread drag.
- Mechanism (the book's): none given.
- Mechanism (my inference): High turnover on small-edge technical signals transfers all expected value to brokers and market makers.
- Apex fit: no. Daily bars; confirms that unconstrained momentum fails post-cost.
- Already tested? no.

---

### 17. Event-Driven Mean Reversion with Proportional Friction
- Where: Chapter 6, Section 6.3 ("Long-Short Backtesting Class"), pp. 135–138 (EPUB: `OEBPS/ch06.html`)
- Quote: "Mean reversion strategies typically exhibit the highest number of trades among technical strategies. With $SMA=43$ and $threshold=0.025$, the strategy executes dozens of trades per year... Proportional costs quickly erode the paper profits."
- Rule as written:
  - Setup: Event-driven execution of price distance mean reversion ($SMA=43$, $threshold=0.025$). Deduct proportional transaction costs on every entry and exit.
  - Entry: Long (+1) when $d_t < -0.025$; Short (-1) when $d_t > +0.025$.
  - Exit: Close to flat (0) when distance crosses 0.
  - Stop loss: not stated.
  - Sizing: Available portfolio cash.
  - Market: EUR/USD.
  - Bar size: Daily.
  - Holding time: Days.
- Book's evidence: Proves that transaction costs reduce the cumulative performance from +34% gross to near breakeven net of costs.
- Mechanism (the book's): none given.
- Mechanism (my inference): Mean reversion profits represent narrow margins that are consumed by execution friction.
- Apex fit: no. On NQ/ES, mean reversion matches "Mean reversion on NQ / ES" on the failed list.
- Already tested? Matches "Mean reversion on NQ / ES" on failed list.

---

### 18. Real-Time Online Tick Momentum Streaming Algorithm
- Where: Chapter 7, Section 7.3 ("Signal Generation in Real Time"), pp. 147–152 (EPUB: `OEBPS/ch07.html`)
- Quote: "The online algorithm receives streaming tick data via a ZeroMQ socket and calculates the rolling momentum over the past $N$ ticks in real time... In [25]: `if momentum > 0: signal = 1; elif momentum < 0: signal = -1`"
- Rule as written:
  - Setup: Connect to streaming tick data socket. Maintain rolling window of past $N=5$ ticks. Compute tick return $r = \log(P_t / P_{t-N})$.
  - Entry: If rolling tick return $> 0$, signal = Long (+1); If $< 0$, signal = Short (-1).
  - Exit: Immediate position flip as streaming ticks update.
  - Stop loss: not stated.
  - Sizing: 1 unit.
  - Market: Simulated / streaming tick feed.
  - Bar size: Tick-by-tick.
  - Holding time: Seconds.
- Book's evidence: Illustrates real-time Python socket architecture and streaming Plotly visualization; does not report historical backtest statistics.
- Mechanism (the book's): none given.
- Mechanism (my inference): Micro-momentum chasing tick noise.
- Apex fit: no. Sub-second tick flipping that generates thousands of trades; retail commissions destroy the account within hours.
- Already tested? no.

---

### 19. Intraday 1-Minute Candle Momentum Strategy on EUR/USD (Oanda)
- Where: Chapter 8, Section 8.3 ("Backtesting a Momentum Strategy on Minute Bars"), pp. 165–170 (EPUB: `OEBPS/ch08.html`)
- Quote: "We retrieve 1-minute candle data for EUR/USD from Oanda's API and backtest a momentum strategy based on a rolling window of 15, 30, and 60 minutes... In [28]: `data['position'] = np.sign(data['returns'].rolling(momentum).mean())`"
- Rule as written:
  - Setup: Oanda 1-minute historical candles for EUR/USD. Compute rolling mean of 1-minute log returns over lookback $m \in \{15, 30, 60\}$ bars.
  - Entry: Long (+1) when rolling return $> 0$; Short (-1) when rolling return $< 0$.
  - Exit: Flip position on sign change.
  - Stop loss: not stated.
  - Sizing: Leveraged contract units via Oanda margin (e.g. 10,000 to 50,000 units, 20:1 to 30:1 leverage).
  - Market: EUR/USD CFD.
  - Bar size: 1-minute bars.
  - Holding time: 15 to 60 minutes.
- Book's evidence: Tested on several weeks of Oanda 1-minute EUR/USD data; shows positive gross performance for certain momentum windows (e.g. $m=30$), but Hilpisch notes that performance is highly sensitive to margin interest, financing costs, and spread widening.
- Mechanism (the book's): none given.
- Mechanism (my inference): Intraday trend continuation in foreign exchange during active London/New York session overlap.
- Apex fit: no. Spot FX CFD is prohibited on Apex (futures only). Unfiltered minute momentum without volatility scaling or stops whipsaws heavily.
- Already tested? no.

---

### 20. Automated Continuous FXCM Tick/Candle Execution
- Where: Chapter 9, Section 9.3 ("Working with the API"), pp. 185–190 (EPUB: `OEBPS/ch09.html`)
- Quote: "The FXCM ForexConnect API enables the retrieval of both tick and candle data and the automated placement of market orders... The automated script listens for new candles, updates the strategy signals, and sends market orders to maintain target positioning."
- Rule as written:
  - Setup: FXCM streaming API subscription to 1-minute or 5-minute candles on EUR/USD. Compute moving average cross or rolling momentum.
  - Entry: Place automated market order (`con.open_trade`) when signal flips from short to long (+1) or long to short (-1).
  - Exit: Flip position on opposite signal.
  - Stop loss: not stated.
  - Sizing: Fixed lot size (e.g., 10,000 units).
  - Market: Spot FX (EUR/USD, GBP/USD).
  - Bar size: 1-minute / 5-minute candles.
  - Holding time: Minutes to hours.
- Book's evidence: Demonstrates technical API integration and order execution workflows; no long-term out-of-sample backtest presented.
- Mechanism (the book's): none given.
- Mechanism (my inference): Programmatic automation of standard retail indicators.
- Apex fit: no. Spot FX prohibited on Apex; naive technical rules fail post-cost.
- Already tested? no.

---

### 21. End-to-End Automated Deep Learning Strategy with Kelly Sizing
- Where: Chapter 10, Section 10.2 ("ML-Based Trading Strategy"), pp. 201–210 (EPUB: `OEBPS/ch10.html`)
- Quote: "We combine machine learning with capital management by training a deep neural network on intraday features and sizing positions using the Kelly criterion... In [38]: `optimal_leverage = (mean_return - risk_free) / variance`... The strategy is deployed as an autonomous background script on a cloud instance."
- Rule as written:
  - Setup: Keras DNN trained on EUR/USD 1-minute features (5 return lags, rolling momentum, rolling volatility). Calculate expected strategy mean return $\mu$ and variance $\sigma^2$ on backtest. Determine optimal leverage via continuous Kelly formula: $f^* = \mu / \sigma^2$. Scale live trade units by fractional Kelly ($f^* / 2$).
  - Entry: Automated market buy when DNN predicts upward movement; automated market sell when DNN predicts downward movement.
  - Exit: Flip position on new candle signal; apply automated Value-at-Risk (VaR) kill-switch if portfolio equity drops below predefined risk threshold.
  - Stop loss: Daily VaR threshold limit.
  - Sizing: Fractional Kelly leverage ($f^* / 2$) applied to available equity.
  - Market: EUR/USD intraday.
  - Bar size: 1-minute bars.
  - Holding time: Minutes.
- Book's evidence: Backtested on intraday EUR/USD data; demonstrates end-to-end Python software deployment on DigitalOcean cloud server with logging, monitoring, and automated process recovery.
- Mechanism (the book's): none given (pure black-box machine learning pipeline).
- Mechanism (my inference): Statistical pattern recognition on short-term price dynamics.
- Apex fit: no. Black-box DNN without economic forced trader; EUR/USD CFD is prohibited on Apex.
- Already tested? no.

---

## Ranked Shortlist of Apex-Compatible Ideas

To qualify for this shortlist, an idea must strictly satisfy:
1. **Apex-compatible**: Flat by 15:59 CT (intraday only), tradeable on liquid CME futures (NQ, ES, CL, GC, ZN, or micros), single stop loss fitting within a $2,000 trailing drawdown.
2. **Not already tested**: Not in the brief's "Already tested and failed" list (disqualifying moving-average crosses, 20-day regime filters, meta-labeling, mean reversion on NQ/ES, order-flow indicators, and gamma/OI pinning).
3. **Stated mechanism**: Supported by an explicit structural or economic mechanism explaining who is forced or paid to trade.

### Shortlist Result: **0 Candidates Qualified**

A rigorous, objective audit of Yves Hilpisch's *Python for Algorithmic Trading* reveals that **zero ideas qualify for the Apex shortlist**. 

### Explicit Rationale for Zero Shortlist Candidates:
1. **Total Absence of Stated Economic / Forced-Trader Mechanisms**:
   Hilpisch writes from the perspective of a computational financial mathematician and Python software architect. Across all 10 chapters, the book focuses strictly on the *technical plumbing* of algorithmic trading (NumPy vectorization, pandas time-series manipulation, scikit-learn/Keras pipelines, socket streaming, Oanda/FXCM REST APIs, and Docker/DigitalOcean cloud deployment). Hilpisch provides **zero economic mechanisms** or structural forced-trader explanations for any of the trading strategies in the book. All rules are presented as pedagogical code examples of standard technical indicators or statistical learning models. Under Rule 7 and the brief's explicit requirement ("Skip rules without a stated mechanism"), ungrounded technical algorithms cannot be admitted to the shortlist.
2. **Direct Collision with "Already Tested and Failed" Rules**:
   - Every moving average strategy in the book (SMA 42/252, Long-Only SMA, Long-Short SMA, parameter grid sweeps) directly matches **"Moving-average crosses: EMA 8/21, SMA 20/50, SMA 50/200... Every combination whipsaws in chop"** on the brief's failed list.
   - Every mean-reversion strategy in the book (Price Distance from SMA, Bollinger Bands, Z-score standard deviation bands) directly matches **"Mean reversion on NQ / ES: RSI, Bollinger, Z-score, lookback sweeps 5–60 min. All fail out-of-sample or lose money post-cost"** on the brief's failed list.
3. **Incompatible Markets and Holding Periods**:
   - The momentum, machine learning (OLS, Logistic Regression, DNN), and event-driven backtesting models are evaluated either on **daily holding periods** across multi-week/multi-month horizons (violating Apex's mandatory flat-by-15:59 CT cutoff) or on **retail spot FX / CFDs** (EUR/USD on Oanda and FXCM), which are strictly prohibited on Apex futures accounts.
4. **Hilpisch's Own Findings Confirm Post-Cost Failure**:
   In Chapter 4 (Section 4.8) and Chapter 6 (Sections 6.2 & 6.3), Hilpisch explicitly demonstrates through event-based backtesting that introducing realistic bid-ask spreads and commissions destroys the paper returns of naive technical and momentum strategies, turning theoretical profits into severe losses.

---

### Disqualifications from Shortlist (Complete Itemized Inventory)
- **SMA Crossover Strategies (Ideas 1, 4, 5, 6, 15)**: Disqualified because moving-average crosses are explicitly on the brief's "Already tested and failed" list. Daily bars also violate Apex flat cutoff.
- **Mean Reversion Distance & Bollinger Bands (Ideas 3, 8, 9, 17)**: Disqualified because mean reversion on index futures (NQ/ES) via Bollinger bands, distance, and Z-scores is explicitly on the brief's "Already tested and failed" list.
- **Machine Learning & Deep Neural Networks on Lagged Returns (Ideas 10, 11, 12, 13, 14, 21)**: Disqualified because models are trained purely on historical price lags without any economic forced-trader mechanism; daily holding periods violate Apex rules; models exhibit severe out-of-sample overfitting.
- **Real-Time Streaming Tick Momentum (Idea 18)**: Disqualified because sub-second tick flipping generates excessive transaction friction that destroys retail accounts.
- **Spot FX & CFD Strategies (Ideas 19, 20)**: Disqualified because spot FX (Oanda/FXCM) is prohibited on Apex CME futures accounts, and rules lack stop losses and economic foundations.
