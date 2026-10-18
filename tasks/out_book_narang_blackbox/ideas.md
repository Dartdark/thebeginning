# Concrete Trading Rules and Market Effects: Inside the Black Box (Rishi K. Narang, 2nd ed. 2013)

**Book**: *Inside the Black Box: A Simple Guide to Quantitative and High-Frequency Trading* (2nd Edition)  
**Author**: Rishi K. Narang  
**Publisher**: John Wiley & Sons, Inc., 2013 (ISBN: 978-1-118-36241-9)  
**Short Name**: `narang_blackbox`  

---

### 1. Moving Average Crossover Trend-Following Model
- Where: Chapter 3: Alpha Models, pp. 30–31; Exhibit 3.2
- Quote: "One way to define a trend for trading purposes, known as a moving average crossover indicator, is to compare the average price of the index over a shorter time period (e.g., 60 days) to that of a longer time period (e.g., 200 days). When the shorter-term average price is below the longer-term average price, the index is said to be in a negative trend, and when the shorter-term average price is above the longer-term average, the index is in a positive trend."
- Rule as written:
  - Entry: Buy long when the 60-day moving average crosses above the 200-day moving average. Sell short when the 60-day moving average crosses below the 200-day moving average.
  - Exit: Reverse position on an opposing crossover (or exit when the trend condition ends).
  - Stop Loss / Sizing: Not stated.
  - Markets: S&P 500 equity index, futures, and diversified commodities (CTAs).
  - Bar size: Daily bars (60 days vs. 200 days).
  - Holding time: Multi-month to multi-year (e.g., held short continuously throughout 2008).
- Book's evidence: Exhibit 3.2 illustrating the S&P 500 entering short at year-end 2007 and remaining short across 2008. Historical references to Ed Seykota (turning $5,000 into $15,000,000 over 12 years; ~60% annualized), Larry Hite's Mint Investments (>30% annualized net over 13 years; +60% in 1987), and Renaissance Technologies / Axcom (+55% net in 1989).
- Mechanism (the book's): Consensus building and the greater fools theory: information diffuses gradually among market participants, and herd behavior perpetuates trends as institutional allocators adjust macro exposure.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: No. Multi-month holding period held overnight; violates the mandatory Apex requirement to be flat by 15:59 CT daily.
- Already tested? **Yes**. The brief explicitly states: *"Already tested and failed: moving-average crosses (your Golden Cross: -$824 a trade as written, -$250 flat-by-close)"*.

---

### 2. Equity Statistical Arbitrage Pairs Trading (Spread Divergence & Reversion)
- Where: Chapter 3: Alpha Models, pp. 31–33; Exhibit 3.3
- Quote: "Exhibit 3.3 shows a simplified example of the mean-reverting behavior evident between similar instruments, in this case Merrill Lynch (MER) and Charles Schwab (SCHW). As you can see, the spread between these two companies oscillates rather consistently in a reasonably narrow range for long periods. This effect allows a trader to wait for significant divergences and then bet on a reversion back to the equilibrium level."
- Rule as written:
  - Universe: Structurally similar pairs of stocks within the same sector (e.g., broker-dealers MER and SCHW).
  - Spread calculation: Measure the historical relative price spread between the two assets.
  - Entry: When the spread experiences a "significant divergence" beyond its historical equilibrium range, buy the relatively undervalued/depressed stock and sell short the relatively overvalued/elevated stock. Threshold: not stated.
  - Exit: Liquidate both legs when the spread reverts back to the equilibrium level.
  - Stop Loss / Sizing: Not stated.
  - Bar size: Daily bars.
  - Holding time: Days to weeks.
- Book's evidence: Exhibit 3.3 charting the spread between MER and SCHW oscillating within a narrow horizontal band from 2004 to 2006.
- Mechanism (the book's): Liquidity imbalances and supply-demand shocks: "Mean reversion strategies... are frequently being paid for providing liquidity to someone whose desire to trade is far more pressing than his price sensitivity."
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Stock pair held overnight; violates the mandatory Apex requirement to be flat by 15:59 CT daily.
- Already tested? **Yes**. The brief explicitly states: *"Already tested and failed: mean reversion on NQ / ES"*.

---

### 3. Dual-Horizon Trend vs. Mean Reversion Regime Model
- Where: Chapter 3: Alpha Models, pp. 32–33; Exhibit 3.4
- Quote: "Trends tend to occur over longer time horizons, whereas reversions tend to happen over shorter-term time horizons. Exhibit 3.4 shows this effect in action. You can see that there are indeed longer-term trends and shorter-term mean reversions that take place. In fact, you can also see that the strategies are likely to work well in different regimes... in some cases, mean reversion strategies can work as the longer-term indicator, while momentum can be used as a faster indicator."
- Rule as written:
  - Architecture: Run two distinct models simultaneously across different time horizons.
  - Long-term horizon: Trend-following momentum model captures multi-month macro moves (e.g., 2000–2002 bear market, 2008 crash).
  - Short-term horizon: Mean reversion model trades counter-trend oscillations within multi-month consolidations (e.g., 2003–2007 bull market).
  - Horizon parameters / Triggers / Stops: Not stated.
  - Bar size: Multiple timeframes (daily/weekly for trend; intraday/daily for reversion).
  - Markets: Equities and futures.
- Book's evidence: Exhibit 3.4 showing S&P 500 from 2000 to 2008 illustrating trend regime dominance in 2000–2002 and 2008, versus mean-reverting regime dominance in 2003–2007.
- Mechanism (the book's): Heterogeneous market participants: short-term liquidity shocks cause temporary overreactions that revert quickly, while macroeconomic consensus shifts take months to fully reflect in prices.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Multi-day/multi-week positions held overnight; violates flat by 15:59 CT.
- Already tested? **Yes**. Combines both trend and mean reversion failed items in the brief.

---

### 4. Options Put/Call Volume Ratio Sentiment Model
- Where: Chapter 3: Alpha Models, p. 34
- Quote: "One is to look at the volume of puts and calls, and to use this as an indicator of sentiment. If puts have higher volumes relative to calls than they normally do, it might be an indicator that investors are worried about a downturn. If puts have lower volumes versus calls than normal, it might be a bullish sentiment indicator."
- Rule as written:
  - Metric: Ratio of put option trading volume to call option trading volume ($\text{Put Volume} / \text{Call Volume}$) on the underlying asset relative to its historical baseline.
  - Bullish Signal: Put/call volume ratio significantly below normal (excess call buying indicates bullish sentiment).
  - Bearish Signal: Put/call volume ratio significantly above normal (excess put buying indicates bearish sentiment).
  - Thresholds / Exit / Stop / Sizing: Not stated.
  - Markets: Underlying equities and equity indexes.
  - Bar size: Daily bars.
- Book's evidence: None given.
- Mechanism (the book's): Informed speculation and institutional hedging: options order flow reveals directional positioning and downside tail-risk hedging by market participants prior to price discovery in cash markets.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Daily sentiment metric without intraday timing; violates flat by 15:59 CT.
- Already tested? No.

---

### 5. Options Implied Volatility Skew Sentiment Model
- Where: Chapter 3: Alpha Models, pp. 34–35
- Quote: "A second example of options-based sentiment in equities utilizes the implied volatilities of puts versus calls... If one analyzes the historical ratio of put volatility and call volatility, there will likely be some natural ratio (greater than one, due to the phenomenon just described about upside and downside volatility), and divergences from this natural level might be treated as indicative of sentiment."
- Rule as written:
  - Metric: Ratio of put implied volatility to call implied volatility ($IV_{\text{put}} / IV_{\text{call}}$) relative to its historical baseline mean ($> 1.0$).
  - Signal: Significant divergence from the historical mean ratio indicates abnormal market fear (overpriced downside insurance) or extreme complacency.
  - Thresholds / Triggers / Stops: Not stated.
  - Markets: Equities and equity index options.
- Book's evidence: None given.
- Mechanism (the book's): Crashophobia and asymmetric demand for downside puts: sellers demand higher implied volatility for downside protection due to stocks' tendency to fall faster than they rise.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Options IV metric without intraday liquidation rules.
- Already tested? No.

---

### 6. Limit Order Book Shape & Depth Imbalance Indicator
- Where: Chapter 3: Alpha Models, p. 35; Chapter 14, pp. 200–205; Chapter 15, pp. 222–225
- Quote: "At the shortest timeframes, some higher-frequency traders evaluate the shape of the limit order book to determine near-term sentiment. The shape of the order book includes factors such as the size of bids or offers away from the mid-market relative to the size at the best bid/offer, or the aggregate size of bids versus offers."
- Rule as written:
  - Metric: Order book depth imbalance and queue shape:
    $$\text{Imbalance} = \frac{\text{Bid Depth} - \text{Ask Depth}}{\text{Bid Depth} + \text{Ask Depth}}$$
    measured at the inside quotes and across levels away from mid-market.
  - Long Signal: Significant aggregate bid depth exceeding ask depth indicates buying support; buy ahead of price tick up.
  - Short Signal: Significant aggregate ask depth exceeding bid depth indicates selling pressure; sell ahead of price tick down.
  - Thresholds / Exit / Stop: Not stated.
  - Market: Electronic futures and equities with high-resolution L2/L3 order book data.
  - Bar size: Tick / millisecond timescale.
  - Holding time: Seconds to minutes.
- Book's evidence: Detailed mockups of order book changes in Exhibits 14.1–14.10 and Exhibits 15.1–15.2.
- Mechanism (the book's): Short-term liquidity exhaustion: large passive queues provide a buffer against adverse moves, while sparse queues on the opposite side allow aggressive market orders to quickly sweep through depth, pushing the mid-price in the direction of the imbalance.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: No. The brief explicitly lists: *"Already tested and failed: order-flow indicator filters"*.
- Already tested? **Yes**. Matches "order-flow indicator filters".

---

### 7. Trading Volume Turnover Contrarian Model
- Where: Chapter 3: Alpha Models, p. 35
- Quote: "For slightly longer-term strategies, analyses of volume can include looking at the trading volume, the turnover (trading versus float), open interest, or other similar measures of trading activity... It can be used as a contrarian indicator (i.e., high-volume or high-turnover stocks are expected to underperform, while low volume or low turnover stocks are expected to outperform)... Most of the research I have reviewed, however, focuses on the contrarian approach."
- Rule as written:
  - Metric: Volume turnover ratio ($\text{Volume} / \text{Float}$).
  - Long Entry: Buy stocks with abnormally low volume or low turnover.
  - Short Entry: Sell short stocks with abnormally high volume or high turnover.
  - Thresholds / Holding time / Stops: Not stated.
  - Markets: Equities.
  - Bar size: Daily/weekly bars.
- Book's evidence: Reference to academic literature reviewed by the author; no specific table provided.
- Mechanism (the book's): Attention-driven overreaction: retail and speculative capital rushes into high-turnover stocks during media hype cycles, temporarily inflating prices above fundamental value, while neglected low-turnover stocks are underpriced.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Stock turnover model holding multi-week positions overnight; violates flat by 15:59 CT.
- Already tested? No.

---

### 8. Earnings Yield (E/P Inversion) Value Model
- Where: Chapter 3: Alpha Models, pp. 36–37; Exhibit 3.5
- Quote: "Quants tend to invert such ratios, keeping prices in the denominator. An inverted P/E ratio, or an E/P ratio, is also known as earnings yield... The basic concept of value strategies is that the higher the yield, the cheaper the instrument... E/P ratio is well behaved for any level of earnings per share for a hypothetical stock with a price greater than $1... By contrast, the P/E ratio is rather poorly behaved and does not lend itself well to analysis and is not even properly defined when earnings per share are zero."
- Rule as written:
  - Metric: Earnings Yield $E/P = \text{Earnings Per Share} / \text{Price}$.
  - Ranking: Rank universe by $E/P$ yield.
  - Long Entry: Buy high-yielding stocks (top fractile).
  - Short Entry: Sell short low-yielding or negative-yielding stocks (bottom fractile).
  - Rebalance / Holding time: Quarterly / annual (e.g. 12-month return forecasts).
  - Thresholds / Stops: Not stated.
  - Markets: Equities.
- Book's evidence: Exhibit 3.5 plotting P/E vs. E/P across negative and positive EPS.
- Mechanism (the book's): Mean reversion to intrinsic fundamental earnings power: investors overreact to short-term cyclical earnings dips, allowing value investors to purchase claims on future cash flows at a discount.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Fundamental equity ranking model holding multi-month positions overnight; violates flat by 15:59 CT.
- Already tested? No.

---

### 9. Currency Carry Trade Model
- Where: Chapter 3: Alpha Models, p. 38
- Quote: "Carry trading is an enormously popular kind of strategy for quants (and discretionary traders) in currencies, where the currency of a country with higher short-term yields is purchased against a short position in the currency of a country with relatively low short-term yields. For example, if the European Central Bank's target interest rate is set at 4.25 percent, whereas the U.S. Federal Reserve has set the Fed Funds rate at 2 percent, a carry trade would be to buy euros against the U.S. dollar. This is a classic value trade because the net yield is 2.25 percent... and this provides a margin of safety."
- Rule as written:
  - Metric: Short-term central bank target interest rate differential between currency pairs.
  - Long Entry: Buy the currency with higher short-term policy yield (e.g. EUR at 4.25%).
  - Short Entry: Sell short the currency with lower short-term policy yield (e.g. USD at 2.00%).
  - Holding time: Multi-month to multi-year carry harvesting.
  - Stop loss / Sizing: Not stated.
  - Market: Foreign exchange (FX) currency pairs.
- Book's evidence: Historical ECB vs. Fed interest rate spread example yielding 2.25% net carry; reference to Long-Term Capital Management (LTCM).
- Mechanism (the book's): Compensation for crash risk: high-yielding currencies expose investors to tail-risk devaluations during liquidity crises; investors demand a structural interest rate premium to hold them.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: No. FX carry trade holding positions overnight for months; violates flat by 15:59 CT.
- Already tested? No.

---

### 10. Commodity Futures Roll Yield / Term Structure Model
- Where: Chapter 3: Alpha Models, p. 38
- Quote: "Roll yield is the spread between the price of a futures contract with some expiry date in the future, versus that of the spot (or that of the contract with a shorter-dated expiry). In backwardated markets, spot prices are higher than futures contracts as they extend out into the calendar. Because there is a convergence of futures contracts up to the spot price, futures in this situation are considered to have positive roll yield. In contango markets, spot prices are lower than futures, and so the yield is considered negative."
- Rule as written:
  - Metric: Term structure slope / Roll Yield:
    $$\text{Roll Yield} = \frac{Price_{\text{near}} - Price_{\text{far}}}{Price_{\text{near}}}$$
  - Long Signal: Buy commodities trading in backwardation (spot / near contract > deferred contract), capturing positive roll yield as the contract converges up to spot price at expiration.
  - Short Signal: Sell short commodities trading in contango (spot / near contract < deferred contract), capturing negative roll yield decay.
  - Expiry / Roll schedule / Stops: Not stated.
  - Markets: Commodity futures.
  - Holding time: Multi-week to multi-month holding until contract roll.
- Book's evidence: None given.
- Mechanism (the book's): Keynesian theory of normal backwardation: commercial producers pay a convenience premium or insurance fee to financial speculators to hedge physical inventory, creating structural roll yield.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Multi-week commodity futures contract holding held overnight; violates flat by 15:59 CT.
- Already tested? No.

---

### 11. Sell-Side Analyst Earnings Estimate Revisions Model
- Where: Chapter 3: Alpha Models, pp. 39–40
- Quote: "Note that an important variant of growth trading utilized by a wide variety of quants and discretionary equity traders focuses on analysts' earnings estimate revisions (or other aspects of analyst sentiment, including price targets and recommendation levels)... The thesis is identical to any other growth strategy, but the idea is to try to get an early glimpse of a company's growth by using the analysts' expectations rather than simply waiting for the company itself to report its official earnings results."
- Rule as written:
  - Metric: Net change in consensus sell-side analyst EPS estimates over a rolling window (e.g., 1 month or 3 months).
  - Long Signal: Buy stocks experiencing upward revisions in consensus EPS forecasts and price targets.
  - Short Signal: Sell short stocks experiencing downward revisions in consensus EPS forecasts.
  - Rebalance / Thresholds / Stops: Not stated.
  - Markets: Equities.
  - Holding time: Weeks to quarters.
- Book's evidence: Discussed as standard operating procedure across quantitative long/short (QLS) funds.
- Mechanism (the book's): Post-earnings-announcement drift (PEAD) and analyst herding: sell-side analysts revise estimates conservatively and incrementally; prices drift over several quarters as institutional models re-anchor to new earnings trajectories.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Multi-week equity swing trade held overnight; violates flat by 15:59 CT.
- Already tested? No.

---

### 12. Discretionary Accruals / Earnings Quality Model
- Where: Chapter 3: Alpha Models, pp. 41–42
- Quote: "A third type of quality signal is management quality... there are measures found, for example, in companies' financial statements, including changes in discretionary accruals (the idea being, the greater the increase in discretionary accruals, the more likely there are problems with the management's stewardship of the company)... A fourth type of quality strategy is fraud risk... attempts to measure how close are a company's true economic earnings (as measured by, say, the free cash flow) to the reported earnings-per-share numbers."
- Rule as written:
  - Metric: Discretionary Accruals = $\text{Reported Net Income} - \text{Operating Cash Flow}$.
  - Long Signal: Buy companies with low or negative discretionary accruals (high cash flow relative to accounting earnings; high earnings quality).
  - Short Signal: Sell short companies with high or rising discretionary accruals (reported earnings significantly higher than operating cash flow; potential accounting manipulation).
  - Thresholds / Stops: Not stated.
  - Markets: Equities.
  - Holding time: Multi-quarter holding period.
- Book's evidence: Historical performance during 2001–2002 corporate accounting scandals (Enron, WorldCom) and 2008 banking credit crisis.
- Mechanism (the book's): Accounting manipulation reversal: companies that rely on discretionary accruals to inflate earnings eventually suffer restatements, write-downs, or insolvency when cash flows fail to materialize.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Multi-month fundamental equity holding held overnight; violates flat by 15:59 CT.
- Already tested? No.

---

### 13. Multiple Regression Linear Composite Alpha Blending Model
- Where: Chapter 3: Alpha Models, pp. 45–47
- Quote: "The first step in using a linear model in this way is to assign a weight to each alpha factor... This is typically done using a technique known as multiple regression, which is aimed at finding the combination of alpha factors that explains the maximum amount of the historical behavior of the instruments being traded... By summing the products of the weights of each factor and the outputs of each factor, we arrive at a composite forecast or score."
- Rule as written:
  - Formula:
    $$\text{Composite Forecast} = \sum_{j=1}^{k} w_j \cdot f_j(x)$$
  - Example given in text: Two factors for XOM: Yield factor forecast = $+20\%$, Trend factor forecast = $-10\%$. Weights determined by historical multiple regression: $70\%$ Yield, $30\%$ Trend.
  - Calculation: $(0.70 \times +20\%) + (0.30 \times -10\%) = +14\% - 3\% = +11\%$ expected return over 12 months.
  - Target action: Rank assets by composite expected return to allocate long/short capital.
  - Parameters / Thresholds: Not stated.
  - Markets: Equities and cross-asset portfolios.
- Book's evidence: Numerical worked example in text computing XOM composite return of +11%.
- Mechanism (the book's): Alpha diversification: individual alpha signals have low signal-to-noise ratios, but combining uncorrelated factors approximately doubles forecasting accuracy (Exhibit 3.8).
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: Yes as an analytical framework for combining signals; not an independent directional trading rule.
- Already tested? No.

---

### 14. Conditional Non-Linear Alpha Blending Model (Trend-Gated Value/Yield)
- Where: Chapter 3: Alpha Models, pp. 47–48
- Quote: "Using the same two factors as earlier, a conditional model might indicate that E/P yields should drive forecasts, but only when the price trends are in agreement with the E/P yields. In other words, the highest-yielding stocks would be candidates to be bought only if the price trends of these stocks were also positive. The lowest-yielding stocks would be candidates to be sold short, but only if the price trends of these stocks were also negative. When the agreement condition is met, the yield factor entirely drives the forecast. But if the price trend doesn't confirm the E/P yield signal, the yield signal is ignored entirely."
- Rule as written:
  - Setup: Two signals: Fundamental Yield (E/P) and Price Trend.
  - Long Condition: Buy only if $\text{Yield Forecast} > 0$ AND $\text{Price Trend} > 0$. If both positive, allocation is driven entirely by Yield forecast ($+20\%$).
  - Short Condition: Sell short only if $\text{Yield Forecast} < 0$ AND $\text{Price Trend} < 0$.
  - Filter: If Trend and Yield disagree (e.g., Yield $+20\%$, Trend $-10\%$), output is $0$ (no position taken).
  - Stop / Sizing / Exit: Not stated.
  - Markets: Equities.
- Book's evidence: XOM example where conflicting signals result in zero position.
- Mechanism (the book's): Avoiding "value traps": cheap stocks often continue falling due to structural deterioration; requiring price trend confirmation filters out declining assets before purchasing.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Equity value model holding multi-month positions overnight; violates flat by 15:59 CT.
- Already tested? No.

---

### 15. Constant-Risk Dynamic Volatility Position Sizing Model
- Where: Chapter 4: Risk Models, pp. 58–60
- Quote: "Another aspect of limiting risk relates to managing the risk of a portfolio through time... By adjusting the size of the portfolio dynamically as volatility changes, the quant aims to keep the portfolio's risk level constant... If volatility doubles, the size of the position or portfolio is cut in half, thereby maintaining the same risk budget."
- Rule as written:
  - Sizing rule: Position Size is scaled inversely to estimated volatility:
    $$\text{Position Size}_t \propto \frac{\text{Target Risk}}{\sigma_t}$$
  - Action: When rolling volatility $\sigma_t$ increases, reduce position size proportionately; when volatility decreases, increase position size proportionately.
  - Rebalance frequency / Lookback: Not stated.
  - Markets: Cross-asset (futures, equities, currencies).
- Book's evidence: Described as a universal risk management practice among quantitative CTA and hedge fund managers.
- Mechanism (the book's): Volatility clustering: market volatility is time-varying and highly clustered; holding static capital exposure causes portfolio risk to surge during volatile panics. Scaling size dynamically stabilizes portfolio drawdown variance.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: Yes as a position sizing engine (can scale micro contracts inversely to intraday ATR); not an independent directional trading rule.
- Already tested? No.

---

### 16. Equal Risk-Weighted Portfolio Construction (Risk Parity)
- Where: Chapter 6: Portfolio Construction Models, pp. 83–85; Exhibit 6.1
- Quote: "Equal risk weighting adjusts position sizes inversely to their volatilities (or whatever other measure of risk, such as drawdown, is preferred). More volatile positions are given smaller allocations, and less volatile positions are given larger allocations. In this way, each position is equalized in the portfolio, not by the size of the allocation but rather by the amount of risk that the allocation contributes to the portfolio."
- Rule as written:
  - Formula: Weight allocated to instrument $i$ is:
    $$w_i = \frac{1 / \sigma_i}{\sum_{j=1}^{N} (1 / \sigma_j)}$$
  - Example given in text: Two-stock portfolio with GOOG (higher volatility) and XOM (lower volatility). GOOG receives a smaller capital allocation, while XOM receives a larger allocation, equalizing risk contribution (Exhibit 6.1).
  - Lookback / Risk metric: Historical volatility (or maximum drawdown).
  - Stop / Target: Not stated.
  - Markets: Equities, futures, multi-asset portfolios.
- Book's evidence: Exhibit 6.1 illustrating inverse-volatility allocation on GOOG vs. XOM.
- Mechanism (the book's): Eliminating inadvertent concentration risk: in equal-dollar portfolios, high-volatility assets dominate portfolio variance. Equal risk weighting ensures every asset contributes equally to total portfolio return.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: Yes as a portfolio weighting algorithm across instruments; not a directional day-trading rule.
- Already tested? No.

---

### 17. Black-Litterman Portfolio Optimization Framework
- Where: Chapter 6: Portfolio Construction Models, pp. 93–94
- Quote: "Fischer Black, of Black-Scholes fame, and Bob Litterman, of Goldman Sachs, in 1990 produced a new optimization method... Their Black-Litterman optimizer addresses some of the problems associated with errors in the measurement of inputs to an optimizer. Most important, they proposed a method of blending an investor's expectations with a degree of confidence about those expectations, and these with the historical precedent evident in the data."
- Rule as written:
  - Inputs: (1) Market equilibrium implied returns (reverse-engineered from CAPM market capitalization weights); (2) Quantitative alpha model views/forecasts; (3) Uncertainty/confidence matrix for each view.
  - Output: Posterior distribution of expected returns and adjusted covariance matrix fed into a mean-variance optimizer.
  - Parameters / Confidence matrix: Not stated.
  - Markets: Multi-asset and equity portfolios.
- Book's evidence: References 1990 Goldman Sachs internal memo and 1992 *Financial Analysts Journal* publication; CVX vs. XOM correlation adjustment example.
- Mechanism (the book's): Bayesian shrinkage against estimation error: pure Markowitz optimizers act as "error-maximizers" on noisy historical returns; anchoring views to market equilibrium priors prevents corner solutions and wild turnover.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: No. Portfolio construction optimizer for institutional allocators; not a directional day-trading rule.
- Already tested? No.

---

### 18. Order Chunking & Child Order Execution Model
- Where: Chapter 7: Execution, pp. 104–105
- Quote: "As such, a common technique for automated execution involves taking a large transaction for, say, 100,000 shares of a stock, breaking it into 1,000 orders of 100 shares each, and spreading the orders out over a window of time... Generally, however, it is agreed that spreading out trades is a useful way to reduce the cost of transacting, and this is an extremely common feature in execution algorithms."
- Rule as written:
  - Setup: Parent order of size $Q$ (e.g., 100,000 shares).
  - Action: Split parent order into $N$ small child orders of size $q$ (e.g., 1,000 orders of 100 shares).
  - Dispatch: Release child orders spaced across a time window or upon liquidity appearance at the inside quote.
  - Sizing rule: Child order size calibrated to available book liquidity to avoid eating into deeper, more expensive order book tiers.
  - Stop / Target: Not stated.
  - Markets: Electronic equities and futures.
- Book's evidence: Numerical example of 100,000 shares sliced into 1,000 child orders of 100 shares.
- Mechanism (the book's): Minimizing market impact: large orders leave a prominent footprint, causing other market participants to pull liquidity and front-run the trade. Slicing orders allows natural counterparties to replenish the inside quote.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: Yes as an execution algorithm for managing order size; not an independent directional trading setup.
- Already tested? No.

---

### 19. Iceberg Order Execution Technique
- Where: Chapter 7: Execution, p. 102
- Quote: "One algorithmic trading technique that utilizes hidden orders is known as iceberging, which takes a single large order and breaks it up into multiple smaller pieces, but displays only one piece at a time to the marketplace... Once the visible piece is executed, another piece of the order is revealed, until the entire order has been filled."
- Rule as written:
  - Setup: Large order submitted with a visible display quantity $Q_{\text{vis}}$ (the "tip of the iceberg") and a total hidden quantity $Q_{\text{tot}}$.
  - Action: Only $Q_{\text{vis}}$ is broadcast to the public limit order book. When $Q_{\text{vis}}$ is executed, the exchange automatically refreshes the display size with another $Q_{\text{vis}}$ chunk from the hidden reserve until $Q_{\text{tot}}$ is satisfied.
  - Markets: Electronic exchanges supporting native iceberg or hidden order flags.
- Book's evidence: Standard order type on modern electronic equity and futures exchanges.
- Mechanism (the book's): Concealing institutional footprint: displaying a 50,000-share bid signals aggressive buying, causing sellers to cancel offers and raise prices. Concealing the full size behind a 500-share display prevents adverse order book repricing.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: Yes as an execution order type; not a directional trade setup.
- Already tested? No.

---

### 20. Noncontractual High-Frequency Market Making (NCMM)
- Where: Chapter 15: High-Frequency Trading, pp. 217–220
- Quote: "Noncontractual market making (NCMM) also involves taking the other side of active orders. NCMMs provide bids and offers that rest in the order books of various exchanges, particularly lit exchanges... In general, an NCMM acquires positions by placing passive orders, waiting for someone to lift his bid or offer. Once acquired, the NCMM may exit passively or actively, depending on liquidity provision rebates and the market's movements... A key challenge for NCMMs is how to manage and dispose of the inventory they acquire... another approach to dealing with inventory risk is to take opposing positions in instruments that closely correlate."
- Rule as written:
  - Entry: Post passive limit orders concurrently at both the best bid and best offer on electronic lit exchanges.
  - Inventory Management: When one side is filled (e.g., passive bid is hit, making the NCMM long), immediately post passive offers to exit at the spread, or hedge inventory by shorting a closely correlated peer instrument (e.g., short UVW when long XYZ).
  - Adverse Selection Protection: Sub-millisecond order cancellation when cross-market signals (e.g., S&P futures) indicate a directional impulse.
  - Holding time: Milliseconds to seconds.
  - Markets: High-liquidity equities, futures, and currency pairs.
- Book's evidence: Detailed discussion of lit exchange market-making economics and liquidity provision rebates.
- Mechanism (the book's): Earning the bid-ask spread and exchange liquidity rebates from active traders who require immediate execution.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Requires co-located sub-millisecond execution hardware, direct exchange feeds, and maker-taker rebate schedules; completely incompatible with retail MultiCharts / Rithmic infrastructure.
- Already tested? No.

---

### 21. Cross-Market / Index Arbitrage (ETF vs. Futures)
- Where: Chapter 15: High-Frequency Trading, pp. 220–222
- Quote: "Arbitrage opportunities exist when instruments that are structurally correlated behave differently... If the S&P 500 futures contract (ES) is up 1 percent for today, while the SPY ETF (which tracks the S&P 500 also) is up only 0.6 percent, a riskless profit opportunity exists, to go short the futures and go long the ETF. In this way, the trader has virtually guaranteed himself a 0.4 percent profit... The arbitrageur sells the relatively overpriced one and buys the relatively underpriced one, so that when they converge, he reaps the profit."
- Rule as written:
  - Universe: Structurally correlated instruments tracking the identical underlying basket (e.g., ES futures vs. SPY ETF, or cash index constituents).
  - Trigger: When a sudden market order moves one instrument (e.g., ES rallies +1.0%) while the other lags (e.g., SPY up only +0.6%), buy the lagging instrument and sell short the leading instrument.
  - Exit: Liquidate both positions when prices converge to parity.
  - Latency Requirement: Sub-millisecond execution to beat competing arbitrageurs and avoid "legging risk".
  - Markets: Index futures (ES) vs. ETFs (SPY).
  - Holding time: Milliseconds to seconds.
- Book's evidence: Numerical ES vs. SPY example showing 0.4% arbitrage spread.
- Mechanism (the book's): Price discovery latency and order fragmentation: large orders temporarily displace price on one venue before passive quotes on the secondary venue update.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Requires microsecond multi-venue execution; retail latency on Rithmic (~15–50ms) guarantees adverse selection and execution slippage.
- Already tested? No.

---

### 22. Fast Alpha / Cross-Asset Lead-Lag Momentum Model
- Where: Chapter 15: High-Frequency Trading, pp. 222–225
- Quote: "For example, if some stock index's futures contract is rallying sharply, there is a very strong probability that a wide variety of stocks will also rally sharply in the immediate future... A fast trend-following strategy will naturally want to get short that instrument (or instruments that closely correlate to it)... Fast alpha strategies mainly use price-based signals, such as momentum, mean reversion, and technical sentiment."
- Rule as written:
  - Setup: Monitor a highly liquid macro bellwether instrument (e.g., S&P or Nasdaq futures) for sudden sharp momentum spikes.
  - Signal: When the leading contract rallies sharply, immediately buy lagging constituent equities or correlated instruments before their quotes adjust upward.
  - Execution: Aggressive market or marketable limit orders.
  - Exit: Scalp exit within seconds as lagging instruments catch up to the macro impulse.
  - Stop: Immediate exit if correlation breaks or lead contract stalls.
  - Timescale: Milliseconds to seconds.
  - Markets: Index futures and constituent equities.
- Book's evidence: Discussed as the primary mode of fast alpha intraday execution by HFT firms.
- Mechanism (the book's): Information transmission friction across fragmented markets: price discovery occurs first in the most liquid derivative (index futures) and transmits with a microsecond-to-millisecond delay to individual equities.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Requires sub-millisecond low-latency infrastructure; cannot be traded over standard retail broker connections.
- Already tested? No.

---

## Ranked Shortlist (Apex-Compatible Candidates)

### Qualifying Candidates: 0 directional trade setups qualify.

Under the strict requirements of `tasks/TASK_BOOK_READING.md` and `tasks/ANTIGRAVITY_BRIEF.md` (mandatory flat by 15:59 CT daily, $2,000 trailing drawdown limit, traded on NQ/MNQ, and a stated market mechanism):

1. **Explicitly Disqualified by Brief's "Already Tested and Failed" List**:
   - **Moving Average Crossover (Rule 1)**: The brief explicitly states: *"Already tested and failed: moving-average crosses (your Golden Cross: -$824 a trade as written, -$250 flat-by-close)"*.
   - **Equity Pairs Trading / Mean Reversion (Rule 2 & Rule 3)**: The brief explicitly states: *"Already tested and failed: mean reversion on NQ / ES"*.
   - **Limit Order Book Depth / Shape Imbalance (Rule 6)**: The brief explicitly states: *"Already tested and failed: order-flow indicator filters"*.

2. **Incompatible Holding Horizon (Overnight Holding Violations)**:
   - Rules 4, 5, 7, 8, 9, 10, 11, 12, and 14 are medium-to-long-term institutional alpha factors (options sentiment, volume turnover, earnings yield E/P, currency carry, commodity roll yield, analyst estimate revisions, discretionary accruals, trend-gated value).
   - All require holding positions overnight across weeks, quarters, or years to harvest risk premia or fundamental drift, completely violating Apex's strict requirement to be flat by 15:59 CT daily.

3. **Incompatible Infrastructure (Sub-Millisecond HFT Requirements)**:
   - Rules 20, 21, and 22 (noncontractual market making, cross-venue index arbitrage, fast alpha lead-lag) require co-located servers, direct exchange fiber feeds, and sub-millisecond execution. Traded over retail Rithmic infrastructure (15–50 ms latency), traders suffer immediate adverse selection and execution slippage.

4. **Sizing and Execution Architectural Value for Apex Accounts**:
   - While 0 directional entry rules qualify for Apex intraday trading, Narang's **risk, portfolio construction, and execution models** provide valuable institutional engineering principles:
     - **Constant-Risk Dynamic Volatility Sizing (Rule 15)**: Scaling position size inversely to estimated volatility ($\text{Size} \propto 1/\sigma$) directly stabilizes dollar risk on intraday MNQ trades across varying volatility regimes.
     - **Equal Risk Weighting (Rule 16)**: Allocating risk inversely to rolling ATR ensures balanced exposure when trading multiple micro contracts.
     - **Child Order Chunking & Iceberg Execution (Rules 18 & 19)**: Breaking larger orders into child tranches reduces slippage and market impact when scaling funded accounts toward maximum contract limits.
