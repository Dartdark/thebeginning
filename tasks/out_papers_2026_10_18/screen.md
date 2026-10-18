# Research Paper Screen: Batch 2026_10_18

### 1. High-frequency realized stochastic volatility model (Toshiaki Watanabe, Jouchi Nakajima, 2023, no id)
- File: CV_070_hiasDP-E-127.pdf
- Has results? yes ("The model comparison exercise indicates that the daily RV improves both the in-sample fit and performance of one-day-ahead volatility forecasting." p. 25)
- Quote: "The model comparison exercise indicates that the daily RV improves both the in-sample fit and performance of one-day-ahead volatility forecasting." (p. 25)
- Market and data: E-mini S&P 500 futures, 5-minute intraday returns, January 1, 2015 to December 31, 2019 (p. 11)
- Index or single stocks? Index (E-mini S&P 500 futures)
- Forced trader: none given
- Timing: not stated
- Costs included? not stated
- Out of sample or other markets? yes, out-of-sample forecasting exercise period over 2016–2019 (4 years out-of-sample after 2015 pre-analysis, p. 11, 22)
- Size: not stated (forecast accuracy metric: RSV model achieves one-day-ahead forecast MSE 0.116 and QLIKE -2.573 vs 0.122 and -2.493 for standard SV model, Table 4 p. 22)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (0) = 3
- Apex fit: no, pure econometric volatility estimation model with no directional trade rule, execution window, or stop loss
- Already tested? no

### 2. Trading Rules Over Fundamentals: A Stock Price Formula for High Frequency Trading, Bubbles and Crashes (Godfrey Cadogan, 2012, SSRN 1977561)
- File: ssrn-1977561.pdf
- Has results? NO: framework, proposal or survey only ("This paper synthesized the continuous time asset pricing models in Cadogan (2011) (trade strategy representation theorem), and Jarrow and Protter (2010) (K-factor model for portfolio alpha), to produce a simple stock price formula that captures several empirical regularities of stock price dynamics attributable to high frequency trading–according to emergent literature." p. 41)
- Quote: "In this paper we present a simple closed form stock price formula, which captures empirical regularities of high frequency trading (HFT), based on two factors: (1) exposure to hedge factor; and (2) hedge factor volatility." (p. 1)
- Market and data: NYMEX natural gas (NG) index futures (illustrative Nanex tick charts), theoretical continuous-time framework, no data years tabulated (p. 1, 41-51)
- Index or single stocks? Index and futures
- Forced trader: none given (theoretical high frequency traders and market makers)
- Timing: not stated
- Costs included? not stated
- Out of sample or other markets? no
- Size: not stated
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (0) / out-of-sample or another market (0) / costs included (0) = 1
- Apex fit: no, theoretical mathematical formulation with no empirical trade rules, entry/exit criteria, or risk parameters
- Already tested? no

### 3. Consistent High-Precision Volatility from High-Frequency Data (Fulvio Corsi, Gilles Zumbach, Ulrich Müller, Michel Dacorogna, 2001, SSRN 261149)
- File: ssrn-261149.pdf
- Has results? yes ("With filtered prices, the daily volatility can be estimated using the information contained in high-frequency data, providing a high-precision measure of volatility at any time interval." p. 1)
- Quote: "On the basis of a simple theoretical model for foreign exchange data, the incoherent term can be filtered away from the tick-by-tick price series. With filtered prices, the daily volatility can be estimated using the information contained in high-frequency data, providing a high-precision measure of volatility at any time interval." (p. 1)
- Market and data: FX (USD/JPY, USD/CHF 1990–2001) and stock indices (S&P 500, DJIA 1996–2001), tick-by-tick to daily bars (p. 4)
- Index or single stocks? Index and FX (S&P 500, DJIA, USD/JPY, USD/CHF)
- Forced trader: none given
- Timing: not stated
- Costs included? not stated
- Out of sample or other markets? yes, tested across multiple FX pairs and stock indices (S&P 500, DJIA)
- Size: not stated (filters negative first-order return autocorrelation rho1 ~ -40% caused by market microstructure noise, p. 1)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (0) / out-of-sample or another market (1) / costs included (0) = 2
- Apex fit: no, econometric microstructure noise filter for daily volatility estimation, no trading strategy
- Already tested? no

### 4. Profitability of Trading in the Direction of Asset Price Jumps – Analysis of Multiple Assets and Frequencies (Milan Fičura, 2017, SSRN 2903629)
- File: ssrn-2903629.pdf
- Has results? yes ("The proposed system achieved promising results for the 4 currency markets, especially at the 15-minute and 30-minute frequencies at which 3 out of the 4 tested currencies turned profitable... with the profits totalling up to 30-50% p.a. in the case of a high-leverage scenario, or 15-25% in the case of a low-leverage scenario." p. 2)
- Quote: "As for the futures markets, the system achieved profits only on the Light Crude Oil market, on the frequencies of 1-hour, 4-hour and 1-day, with the profits totalling up to 20% p.a. in the case of high leverage or 10% p.a. in the case of low leverage. For USD/JPY, E-Mini S&P 500 Futures and VIX Futures the system achieved mostly a loss." (p. 2)
- Market and data: EUR/USD, GBP/USD, USD/CHF, USD/JPY (1999–2015), Light Crude Oil Futures (1987–2015), E-Mini S&P 500 Futures (1997–2015), VIX Futures (2004–2015); 1-min, 5-min, 15-min, 30-min, 1-hour, 4-hour, 1-day bars (p. 2, 40)
- Index or single stocks? Futures and FX (E-Mini S&P 500, Light Crude Oil, currencies)
- Forced trader: none given (relies on statistical price-jump detection via Lee-Mykland L-estimator)
- Timing: not stated (entries trigger whenever a jump is detected, holding 1 to 16 bars)
- Costs included? yes (1 pip for currencies, 0.05 USD for Crude Oil, 0.5 index points for E-mini S&P, p. 40)
- Out of sample or other markets? yes (out-of-sample last 50% split across 7 assets and 7 frequencies, p. 40)
- Size: E-Mini S&P lost money; Light Crude Oil achieved up to 10–20% p.a. at 1h/4h/1d holding periods (p. 2)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (0) / out-of-sample or another market (1) / costs included (1) = 3
- Apex fit: no, on E-mini S&P futures the strategy produced net losses; on Crude Oil, holding 1-hour to 4-hour bars for up to 16 periods holds positions overnight across days (violating Apex flat by 15:59 CT rule) and jumps incur severe gap risk against a $2,000 trailing drawdown
- Already tested? no

### 5. Efficient Estimation of Volatility using High Frequency Data (Gilles Zumbach, Fulvio Corsi, Adrian Trapletti, 2002, SSRN 306002)
- File: ssrn-306002.pdf
- Has results? yes ("The Monte Carlo simulations indicate that the current best available estimator is “filter + Zhou”, namely to filter the prices with an incoherent filter according to [Corsi et al., 2001], followed by a volatility estimator as given by Zhou [Zhou, 1996]." p. 21)
- Quote: "The Monte Carlo simulations indicate that the current best available estimator is “filter + Zhou”, namely to filter the prices with an incoherent filter according to [Corsi et al., 2001], followed by a volatility estimator as given by Zhou [Zhou, 1996]... The estimation error is reduced by a factor 4 when comparing RiskMetric (daily data) with the estimator ”filter + Zhou” (high frequency data)." (p. 21)
- Market and data: USD/CHF FX tick-by-tick data, January 1, 1996 to January 1, 2001, evaluated on May 2001 (p. 20, 21)
- Index or single stocks? FX (USD/CHF)
- Forced trader: none given
- Timing: not stated
- Costs included? not stated
- Out of sample or other markets? yes, Monte Carlo simulations and out-of-sample evaluation in May 2001 (p. 21)
- Size: not stated (estimation error reduced by factor of 4 vs daily RiskMetrics, p. 21)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (0) / out-of-sample or another market (1) / costs included (0) = 2
- Apex fit: no, volatility estimation and filtering algorithm with no directional trading rule or signals
- Already tested? no

### 6. Stock Index Volatility Forecasting with High Frequency Data (Eugenie Hol, Siem Jan Koopman, 2002, SSRN 318239)
- File: ssrn-318239.pdf
- Has results? yes ("We conclude that those models which include the intraday information perform better than those that are solely based on daily returns. The most accurate forecasts are then obtained with the ARFIMA-RV model..." p. 23)
- Quote: "We conclude that those models which include the intraday information perform better than those that are solely based on daily returns. The most accurate forecasts are then obtained with the ARFIMA-RV model even though the UC-RV model is only a close second." (p. 23)
- Market and data: Standard & Poor's 100 stock index (OEX), 5-minute intraday transaction prices from January 6, 1997 to December 29, 2000 (out-of-sample: March 13 to December 29, 2000) (p. 5, 21)
- Index or single stocks? Index (S&P 100)
- Forced trader: none given
- Timing: not stated
- Costs included? not stated
- Out of sample or other markets? yes, out-of-sample evaluation on March 13 to December 29, 2000 (p. 21)
- Size: not stated (forecast error metrics: ARFIMA-RV achieves HRMSE 0.5058 to 0.6401 vs GARCH 0.7999 to 1.0093 across 1-day to 5-day horizons, Table 5 p. 21)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (0) / out-of-sample or another market (1) / costs included (0) = 2
- Apex fit: no, statistical volatility forecasting model with no directional trade signals or risk controls
- Already tested? no

### 7. Hedging Option Greeks: Risk Management Tool for Portfolio of Futures & Options. (Ms. Dikshita, Dr. Harjit Singh, 2019, SSRN 3479421)
- File: ssrn-3479421.pdf
- Has results? NO: framework, proposal or survey only ("This study is focussed at providing the knowledge of the Greeks and their implementation as risk management tools so as to enhance gains or avoid losses." p. 1; descriptive textbook walkthrough of Delta, Gamma, Vega, Theta with hypothetical strike numbers, no empirical data or test results)
- Quote: "This study is focussed at providing the knowledge of the Greeks and their implementation as risk management tools so as to enhance gains or avoid losses. Delta, Vega and Theta of the options as well as the other position Greeks are associated with the any option strategy and they equally impact the portfolio." (p. 1)
- Market and data: none (textbook formulas and toy arithmetic examples, no empirical data or years)
- Index or single stocks? Options in general
- Forced trader: none given
- Timing: not stated
- Costs included? not stated
- Out of sample or other markets? no
- Size: not stated
- Score (1 point each): forced trader named (0) / intraday or futures data (0) / data runs to 2018 or later (0) / out-of-sample or another market (0) / costs included (0) = 0
- Apex fit: no, introductory primer on option Greeks; options trading is prohibited on Apex prop accounts
- Already tested? no

### 8. Hedging Pressure and Commodity Option Prices (Ing-Haw Cheng, Jiarui Feng, Ke Tang, Lei Yan, 2025, SSRN 3933070)
- File: ssrn-3933070.pdf
- Has results? yes ("A strategy that provides liquidity to hedgers earns an average excess return of 6.8% per month before transaction costs and consideration of margin requirements. Overall, our results confirm the existence of hedging premiums, demand effects, and limits to arbitrage in commodity option markets." p. 1)
- Quote: "A new measure of hedging pressure in commodity options markets—commercial hedgers’ net short option exposure—predicts option returns and changes in the slope of implied volatility curves. Puts are more expensive, and calls are cheaper, when values of option hedging pressure are greater." (p. 1)
- Market and data: 24 commodity futures options on CBOT, CME, ICE, NYMEX, weekly CFTC COT reports and daily option prices, March 21, 1995 to December 24, 2018 (p. 6)
- Index or single stocks? Commodities cross-section (24 commodity option markets)
- Forced trader: Commercial hedgers (producers hedging downside via put buying/call selling, and processors hedging upside via call buying/put selling) who create non-discretionary hedging pressure (p. 1, 3)
- Timing: Weekly rebalancing based on Tuesday CFTC COT reports, held across weeks/months (p. 3, 6)
- Costs included? no ("before transaction costs and consideration of margin requirements", p. 1)
- Out of sample or other markets? yes, tested across 24 distinct commodity markets and subperiod splits (first vs second half of sample, DCOT post-2006, p. 21-23)
- Size: average excess return of 6.8% per month (t = 3.42) before transaction costs and margin (p. 1, 16)
- Score (1 point each): forced trader named (1) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (0) = 4
- Apex fit: no, requires trading portfolios of commodity options (selling puts and buying calls held across weeks), which is prohibited on Apex futures accounts
- Already tested? no

### 9. Liquidity Premium Around FOMC Announcements (Tommaso Baglioni, Alessandro Giannozzi, Ruy M. Ribeiro, Oliviero Roggi, 2026, SSRN 4304807)
- File: ssrn-4304807.pdf
- Has results? yes ("Measured over the full announcement day, from the close of FOMCt-1 to the close of the FOMC day, meetings preceded by low liquidity deliver 32 to 39 basis points, whereas meetings preceded by high liquidity deliver returns that are generally indistinguishable from zero: high ex-ante liquidity signals that the announcement premium has already been delivered before the release." p. 20)
- Quote: "Interpreting low pre-announcement liquidity as a manifestation of a “calm-before-the-storm” environment, characterized by reduced trading activity and the temporary withdrawal of liquidity provision, we find that calmer pre-announcement periods are followed by larger post-announcement increases in liquidity and higher post-announcement returns." (p. 20)
- Market and data: E-mini S&P 500 futures (ES) and SPY, tick/1-minute intraday order book depth, volume, and spreads across 215 scheduled FOMC announcements, 1997 to 2024 (p. 5, 7)
- Index or single stocks? Index and futures (E-mini S&P 500 futures)
- Forced trader: Liquidity providers / market makers temporarily withdrawing liquidity before scheduled macro event risk ("calm before the storm"), demanding an illiquidity premium that gets earned as institutions trade post-announcement (p. 1, 20)
- Timing: Scheduled FOMC announcement days (Wednesdays). Post-announcement trading window from statement release (14:00 ET / 13:00 CT) to market close (16:00 ET / 15:00 CT), conditioned on pre-announcement (day t-1) liquidity (p. 7, 20)
- Costs included? no
- Out of sample or other markets? yes, verified across ES futures and SPY ETF, across multiple liquidity measures (depth, dollar volume, Amihud, spread), and across pre- vs post-2011 subperiods (p. 7, 20, 43)
- Size: meetings preceded by low liquidity deliver +32 to +39 basis points (t = 3.5 to 5.7, p < 0.001) over the announcement day, while high liquidity meetings deliver ~0 bp (p. 20, Table A.11)
- Score (1 point each): forced trader named (1) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (0) = 4
- Apex fit: yes, tradeable on E-mini S&P 500 (ES) or Micro E-mini (MES) on FOMC Wednesdays; entry at 13:00 CT post-announcement when pre-FOMC liquidity was low, exit at 15:00 CT, completely flat before the 15:59 CT cutoff; defined stop easily fits $2,000 trailing drawdown
- Already tested? no

### 10. Trading Theta: A Strategy Exploiting Time Decay (Yunpeng Lu, 2024, SSRN 4792284)
- File: ssrn-4792284.pdf
- Has results? yes ("The result shows the trading setting with main contracts of SPX Put and hedge contracts of SPY Put has the highest performance... Figure shows: main contract: SPX Put, hedge: SPY Put, ignore Friday and day before holiday; annual Pnl is 20.04%." p. 1, 22)
- Quote: "Overall, this strategy has tiny negative annualized PnL, which is in line with the fact that in the BSM world, PnL should be the same as risk free rate. With the position adjust cost eroding the return, the total PnL should be around zero, considering the annual position adjust cost is below 10%." (p. 22)
- Market and data: SPX options, SPY options, and E-mini S&P 500 futures hedge, daily data, 2010 till 2022 (p. 1, 17)
- Index or single stocks? Index options (SPX, SPY, E-mini)
- Forced trader: none given (exploits theoretical time decay of option theta)
- Timing: Daily rebalancing / multi-day holding periods
- Costs included? yes (position adjustment costs / bid-ask spread modeled, p. 17-21)
- Out of sample or other markets? no (64 parameter variations evaluated on single in-sample dataset)
- Size: single isolated setting (#32) shows 20.04% annual PnL, but overall across all settings the strategy produces negative annualized net PnL after position adjust costs (p. 22)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (0) / costs included (1) = 3
- Apex fit: no, requires shorting SPX/SPY options and holding multi-leg options portfolios across days, which is prohibited on Apex prop accounts
- Already tested? no

### 11. High-frequency estimation of Itô semimartingale baseline for Hawkes processes (Yoann Potiron, Olivier Scaillet, Vladimir Volkov, Seunghyeon Yu, 2026, SSRN 5108542)
- File: ssrn-5108542.pdf
- Has results? yes ("The empirical application shows that the absence of a Hawkes component and a constant baseline is always rejected, highlighting the presence of U-shaped and J-shaped patterns of trading." p. 31)
- Quote: "The empirical application shows that the absence of a Hawkes component and a constant baseline is always rejected, highlighting the presence of U-shaped and J-shaped patterns of trading." (p. 31)
- Market and data: S&P 500 E-mini futures, tick-level quote timestamps, January 2020 to December 2021 (p. 26)
- Index or single stocks? Index futures (S&P 500 E-mini)
- Forced trader: none given (econometric point-process paper)
- Timing: not stated
- Costs included? not stated
- Out of sample or other markets? no
- Size: not stated (hypothesis test p-values rejecting no-Hawkes and constant-baseline at 1% and 5% level, p. 28, 31)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (0) / costs included (0) = 2
- Apex fit: no, econometric point process estimation of quote arrival intensity with no directional trading rule
- Already tested? no

### 12. Intraday Price Pressure and Order Flow Around U.S. Treasury Auctions (Michael Fleming, Weiling Liu, Giang Nguyen, 2026, SSRN 6447502)
- File: ssrn-6447502 (1).pdf
- Has results? yes ("Table 2 provides strong evidence of economically and statistically significant yield pressure around Treasury auctions. Panel A indicates that, over the full 1991–2024 sample, temporary yield deviations in the six-hour window around auctions range from about 0.7 to 1.2 bps across maturities, all statistically significant at the 1% level." p. 19)
- Quote: "Using 33 years of intraday Treasury data, we provide the first high-frequency evidence on auction-day price pressure: yields rise in the hours before auction and reverse afterward. This pressure strengthens when dealers face tighter risk-bearing constraints and weakens when investor demand is stronger or more elastic." (p. 2)
- Market and data: On-the-run U.S. Treasury securities (2-, 3-, 5-, 7-, 10-, and 30-year), tick and 1-minute intraday secondary market data (GovPX and BrokerTec), June 25, 1991 to July 25, 2024 (p. 2, 15)
- Index or single stocks? Rates and futures (U.S. Treasury benchmarks; directly tradeable via CBOT Treasury futures: ZN, ZF, ZB)
- Forced trader: Primary dealers bidding at Treasury auctions face strict balance sheet inventory limits; to absorb multi-billion dollar auction supply shocks, dealers hedge and short in the interdealer secondary market before the 13:00 ET auction close, driving yields up (prices down), and buy back/rebalance post-auction once supply is allocated (p. 2, 7, 42)
- Timing: Monthly Treasury auction days. Pre-auction yield run-up: 10:00 to 13:00 ET (9:00 to 12:00 CT); post-auction yield reversal (price rally): 13:01 to 16:00 ET (12:01 to 15:00 CT) following the 13:00/13:01 ET result release (p. 18, 19)
- Costs included? not stated (measured in interdealer yield deviations; interdealer bid-ask spreads are tight, ~1/4 to 1/2 tick, p. 12, 19)
- Out of sample or other markets? yes, tested across 6 maturities (2Y, 3Y, 5Y, 7Y, 10Y, 30Y) and 3 distinct historical eras (1991–2006, 2007–2014, 2015–2024), plus comparison against non-auction days and FOMC/NFP days (p. 18, 41)
- Size: 0.7 to 1.2 bps total yield pressure (t-stats > 4); post-auction yield reversal is -0.32 to -0.75 bps across maturities (p < 0.01). On 10-year Treasury note (ZN), 1 bp yield move corresponds to ~8 ticks ($250 per contract) (p. 19)
- Score (1 point each): forced trader named (1) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (0) = 4
- Apex fit: yes, fully tradeable on 10-Year Treasury Note futures (ZN) or 5-Year (ZF); buy ZN post-auction at 12:01 CT and hold until 15:00 CT, completely flat before the 15:59 CT cutoff; fixed 4–6 tick stop ($62.50/tick) fits well inside the $2,000 trailing drawdown
- Already tested? no (the brief lists "CL / ZN opening-range breakouts"; this is an auction-concession post-announcement reversal, not an opening-range breakout)

### 13. From Pinning to Amplification: Evidence of a Regime Shift in S&P 500 Options Expiration Dynamics, 2016–2025 (Nathan Elms, 2026, SSRN 6564078)
- File: ssrn-6564078.pdf
- Has results? yes ("We find no evidence of options pinning in S&P 500 expiration dynamics across five tests on 2,294 trading days (2016–2025). The significant finding (p < 0.001) shows the opposite: high near-expiry ATM open interest is associated with wider, not narrower, daily ranges." p. 5)
- Quote: "Five tests find no evidence of pinning in this modern sample. The single statistically significant result (p < 0.001) shows that days with the highest ATM open interest exhibit 16% wider daily ranges than days with the lowest—consistent with the gamma amplification mechanism described by Barbon & Buraschi (2021) rather than the pinning documented in earlier periods." (p. 1)
- Market and data: SPY near-expiry options matched with E-mini S&P 500 futures, 1-minute intraday, 2,294 trading days from 2016 to 2025 (p. 1)
- Index or single stocks? Index (S&P 500)
- Forced trader: Options dealers delta hedging (net short gamma amplifying intraday moves) (p. 1, 5)
- Timing: Expiration days, 9:30 to 16:00 ET
- Costs included? not stated
- Out of sample or other markets? no
- Size: 16% wider daily ranges on high ATM open-interest days (p < 0.001); pinning effect is 0 (p. 1)
- Score (1 point each): forced trader named (1) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (0) / costs included (0) = 3
- Apex fit: no, empirical confirmation of non-pinning and range widening with no actionable trading strategy or stops
- Already tested? YES: gamma / open-interest pinning (also 0DTE gamma flip / strike pinning)

### 14. Regime-Conditioned Directional Prediction of the S&P 500 Index: A Walk-Forward Validation Study Using Dealer Greek Exposure (Narayanan Doraiswamy, 2026, SSRN 6741978)
- File: ssrn-6741978.pdf
- Has results? yes ("Over a 15-month walk-forward out-of-sample period (January 2025 through March 2026), the framework produces 321 trades across six directional sleeves with a 77% win rate (z = 9.54, p = 1.1 × 10−22 ) and +3,063 realized S&P 500 points." p. 2)
- Quote: "Over a 15-month walk-forward out-of-sample period (January 2025 through March 2026), the framework produces 321 trades across six directional sleeves with a 77% win rate (z = 9.54, p = 1.1 × 10−22 ) and +3,063 realized S&P 500 points." (p. 2)
- Market and data: S&P 500 index options and E-mini S&P 500 futures, 15-minute intraday bars, January 2025 to March 2026 (p. 2, 25)
- Index or single stocks? Index (S&P 500)
- Forced trader: Dealer gamma exposure / market makers delta hedging (p. 1)
- Timing: Intraday 15-minute bars, exits 30–60 minutes before close (p. 24)
- Costs included? not stated
- Out of sample or other markets? yes, 15-month walk-forward out-of-sample period (p. 2)
- Size: 77% win rate, +3,063 S&P points over 321 trades (p. 2)
- Score (1 point each): forced trader named (1) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (0) = 4
- Apex fit: tradeable on ES/MES intraday, BUT carries extreme warning signs
- Warning signs: one unaffiliated author with huge returns (77% win rate, z=9.54, p=1.1e-22); "machine learning predicts" (3-state Hidden Markov Model + regime-adaptive XGBoost models with 71 features)
- Already tested? YES: 20-day bull / bear regime filters and Markov state transitions, gamma / open-interest pinning, 0DTE gamma flip / strike pinning

### 15. Day Trading: Adapting to Change (Asher Levine, 2026, SSRN 6833239)
- File: ssrn-6833239.pdf
- Has results? yes ("Results showed an overall profitable performance with a 53% win rate, while the ORB strategy achieved a statistically significantly higher success rate of 75% compared to the other momentum continuation models." p. 1)
- Quote: "Results showed an overall profitable performance with a 53% win rate, while the ORB strategy achieved a statistically significantly higher success rate of 75% compared to the other momentum continuation models. A two-proportion z-test indicated that the difference in the strategies was statistically significant, as I achieved a z = 1.68 and p = 0.047." (p. 1)
- Market and data: E-mini S&P 500 futures (ES), simulated paper trading on TradingView, 3 months from October to December 2025 (p. 1, 7)
- Index or single stocks? Index futures (ES)
- Forced trader: none given (retail ICT concepts, "order blocks", "NDOG EH indicator", p. 6)
- Timing: 8:00 to 8:15 am ORB (opening range breakout) (p. 7)
- Costs included? no (paper trading simulated fills recorded in a personal Google Sheet, p. 8)
- Out of sample or other markets? no
- Size: 53% overall win rate; 75% win rate on 8:00-8:15 am ORB (p. 1, 7)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (0) / costs included (0) = 2
- Apex fit: tradeable on ES, but highly questionable validity
- Warning signs: one unaffiliated student author paper trading on TradingView for 3 months with discretionary trade logs in Google Sheets; reliance on retail YouTube concepts ("ICT", "order blocks")
- Already tested? YES: CL / ZN opening-range breakouts, order-flow indicator filters

### 16. Gamma Exposure (GEX) Without the Paywall: A Fully Disclosed Dealer-Gamma Engine for Gold and S&P 500 Futures at US$42.80 a Month (Naresh Sen, 2026, SSRN 7098358)
- File: ssrn-7098358.pdf
- Has results? NO: framework, proposal or survey only ("No backtested P&L claim is made. This paper documents a measurement methodology and its cost, not a trading strategy with audited returns." p. 12)
- Quote: "No backtested P&L claim is made. This paper documents a measurement methodology and its cost, not a trading strategy with audited returns. The regime-and-location framework is a structured way to read the map; its profitability depends on execution, costs, and discipline." (p. 12)
- Market and data: CME S&P 500 futures options and COMEX gold futures options, intraday and daily options chains, 2026 (p. 1)
- Index or single stocks? Index and commodity futures options (S&P 500 and Gold)
- Forced trader: Options dealers delta hedging (p. 2)
- Timing: not stated
- Costs included? not stated
- Out of sample or other markets? no
- Size: not stated
- Score (1 point each): forced trader named (1) / intraday or futures data (1) / data runs to 2018 or later (0) [no historical sample] / out-of-sample or another market (0) / costs included (0) = 2
- Apex fit: no, measurement methodology and engineering blueprint only, no backtested trading system
- Already tested? YES: gamma / open-interest pinning

### 17. Opening-Range Reversal in Dow Jones Futures: Evidence Consistent with 0DTE Hedging Pressure (Lance Ladia, 2026, SSRN 7124578)
- File: ssrn-7124578.pdf
- Has results? yes ("This paper documents a short-side opening reversal pattern in E-mini Dow futures over 194 trades from January 2023–March 2026. Under a symmetric 1:1 payoff structure, the strategy produced a 59.79% win rate and gross expectancy of 0.196R per trade." p. 1)
- Quote: "This paper documents a short-side opening reversal pattern in E-mini Dow futures over 194 trades from January 2023–March 2026. Under a symmetric 1:1 payoff structure, the strategy produced a 59.79% win rate and gross expectancy of 0.196R per trade. Performance was concentrated in the earliest entry windows: trades in the first three timing buckets won 65.56% of the time, compared with 39.53% of the time in the final two." (p. 1)
- Market and data: E-mini Dow Jones futures (YM), 5-minute intraday bars, 194 trades from January 2023 to March 2026 (exploratory historical sample 2021–2022) (p. 1)
- Index or single stocks? Index futures (E-mini Dow Jones YM)
- Forced trader: Options market makers hedging 0DTE positions during the opening minutes of cash equity trading (p. 1, 2)
- Timing: Opening 45 minutes of equity cash session (9:30 to 10:15 ET / 8:30 to 9:15 CT); performance concentrated in the earliest entry windows (p. 1, 11)
- Costs included? no ("results are reported gross of estimated execution costs", p. 11)
- Out of sample or other markets? no (historical 2021-2022 reconstruction showed 45.22% win rate; single instrument YM, p. 1, 11)
- Size: 59.79% win rate across 194 trades, +0.196R gross expectancy under symmetric 1:1 payoff; trades in first three windows won 65.56% (p. 1)
- Score (1 point each): forced trader named (1) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (0) / costs included (0) = 3
- Apex fit: yes, tradeable on E-mini Dow (YM) or Micro Dow (MYM); short-side opening fade between 8:30 and 9:15 CT, flat well before 15:59 CT; symmetric 1:1 stop fits $2,000 trailing drawdown
- Warning signs: one unaffiliated author trading personal capital with direct financial interest; exact trade parameters withheld preventing independent replication; results reported gross of execution costs
- Already tested? no (the brief lists "CL / ZN opening-range breakouts" [breakout, not reversal; different symbols], "mean reversion on NQ / ES" [different symbols], and "the plan's strategies ported to ES / YM / GC / CL" [the plan's strategies do not include opening-range reversals])

### 18. Stock Price Movement and Its Relationship with Options Delta and Gamma on Expiration Dates (Vishal Chopra, 2026, SSRN 7222220)
- File: ssrn-7222220 (1).pdf
- Has results? NO: framework, proposal or survey only ("A structured empirical methodology is proposed for testing the relationship between estimated dealer gamma exposure and intraday stock behavior." p. 2; marked "Draft for SSRN Submission", contains research proposal and bibliography notes without empirical data or results)
- Quote: "A structured empirical methodology is proposed for testing the relationship between estimated dealer gamma exposure and intraday stock behavior. The framework combines option-chain data, strike-level open interest, implied volatility, estimated Greeks, intraday equity prices, trading volume, realized volatility, and liquidity measures." (p. 2)
- Market and data: none (proposal framework only, no dataset or years)
- Index or single stocks? Index and single stocks proposed
- Forced trader: Options market makers delta hedging on expiration dates (p. 1)
- Timing: not stated
- Costs included? not stated
- Out of sample or other markets? no
- Size: not stated
- Score (1 point each): forced trader named (1) / intraday or futures data (0) / data runs to 2018 or later (0) / out-of-sample or another market (0) / costs included (0) = 1
- Apex fit: no, uncompleted draft proposal with no data or results
- Already tested? no (draft proposal)

### 19. Volatility Prediction of Oil and Gold Prices Using GARCH Model (Piyush Kumar, Divyansh Sagar, Lakhwinder Kaur Dhillon, 2024, SSRN 7323778)
- File: ssrn-7323778.pdf
- Has results? yes ("For gold prices, Micro Gold Futures (MGC=F) GARCH (1,0) was applicable, for E-Mini Gold Futures (QO=F) GARCH (1,2) was applicable and for ZKB Gold ETF (ZGLD.SW) GARCH (1,1) was applicable and predicted accurate results with fewer errors." p. 8)
- Quote: "The objective of the paper is to create a GARCH/ARCH model to predict future volatility on a rolling basis and based on it suggest recommendations related to the use of the model for risk management." (p. 1)
- Market and data: Brent Oil Futures, WTI ETF, E-Mini Oil futures, ZKB gold ETF, Micro gold futures, E-mini gold futures (Yahoo Finance daily bars), August 2014 to February 2022 (p. 1)
- Index or single stocks? Commodities (Crude Oil and Gold futures/ETFs)
- Forced trader: none given (statistical volatility estimation)
- Timing: not stated (daily rolling 1-day ahead forecasts)
- Costs included? not stated
- Out of sample or other markets? yes, evaluated across both crude oil and gold commodities, 70/30 train/test split (p. 1, 8)
- Size: not stated (statistical volatility error metrics: AIC, BIC, RMSE, p. 5-8)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (0) = 3
- Apex fit: no, daily rolling GARCH volatility prediction for risk management; no directional trading rule, signals, or stops
- Already tested? no

### 20. Do Gamma-Exposure Walls Show Strike-Local Effects on NDX? A Pre-Registered, Placebo-Controlled Test (Reza Cenobar, Katie Fazeli, 2026, SSRN 7592005)
- File: ssrn-7592005.pdf
- Has results? yes ("A pre-registered fade trade at the wall shows no evidence of profit: its mean net result is −4.0 (call walls) and −2.3 (put walls) NQ points per trade, with wide intervals spanning zero. The pre-registered verdict is no large edge." p. 1)
- Quote: "Walls constructed as platforms define them do not behave as reliable intraday barriers on NDX. Relative to levels at the same distance from spot, they are breached a little less often, price may linger a little longer near them, and the registered fade rule does not pay." (p. 11)
- Market and data: Nasdaq-100 index options (NDX and NDXP) and E-mini Nasdaq-100 futures (NQ), 1-minute intraday, 124 trading sessions from January 12 to July 10, 2026 (p. 1)
- Index or single stocks? Index (NDX / NQ)
- Forced trader: Options dealers delta hedging (tested whether dealer gamma walls act as mechanical barriers)
- Timing: Intraday cash session, 9:30 to 16:00 ET
- Costs included? yes (two ticks of slippage and exchange fees deducted per round turn, p. 9)
- Out of sample or other markets? yes, pre-registered OSF trial with distance-matched placebo levels (p. 1)
- Size: net loss of −4.0 NQ points per trade on call walls, −2.3 NQ points on put walls (p. 1)
- Score (1 point each): forced trader named (1) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (1) = 5
- Apex fit: tradeable on NQ futures intraday, but edge is negative
- Already tested? YES: gamma / open-interest pinning (also 0DTE gamma flip / strike pinning; the paper's findings directly confirm the brief's listing)

---

## Send to Claude

1. **Intraday Price Pressure and Order Flow Around U.S. Treasury Auctions** (Michael Fleming, Weiling Liu, Giang Nguyen, 2026, SSRN 6447502 / FRBNY Staff Report No. 1188)
   - Score: 4/5 | Market: 10-Year U.S. Treasury Note Futures (ZN) | Apex fit: Yes
   - Forced trader: Primary dealers bidding at scheduled Treasury auctions face balance sheet inventory limits; they hedge supply shocks by selling in the secondary market ahead of the 13:00 ET cut-off, causing yield concessions that reverse post-auction.
   - My inference trade line: **Market: ZN (10-Year Treasury Note futures); Entry: 12:01 CT (13:01 ET, immediately following auction result release on monthly 10Y/30Y auction days); Exit: 15:00 CT (16:00 ET) or 15:50 CT market close; Direction: Long ZN (buying the post-auction price rebound / yield decline), fixed stop 5 ticks ($156.25).**

2. **Liquidity Premium Around FOMC Announcements** (Tommaso Baglioni, Alessandro Giannozzi, Ruy M. Ribeiro, Oliviero Roggi, 2026, SSRN 4304807)
   - Score: 4/5 | Market: E-mini S&P 500 Futures (ES) / Micro E-mini (MES) | Apex fit: Yes
   - Forced trader: Liquidity providers temporarily withdraw liquidity ahead of scheduled FOMC interest rate announcements ("calm-before-the-storm"), demanding an illiquidity premium that gets paid as institutional capital re-enters post-announcement.
   - My inference trade line: **Market: ES / MES; Entry: 13:00 CT (14:00 ET, at scheduled FOMC announcement on Wednesdays when prior-day order book liquidity/depth was below median); Exit: 15:00 CT (16:00 ET cash close); Direction: Long ES (capturing the +32 to +39 bp post-announcement liquidity replenishment drift), fixed stop 15 index points ($750 on ES / $75 on MES).**

3. **Opening-Range Reversal in Dow Jones Futures: Evidence Consistent with 0DTE Hedging Pressure** (Lance Ladia, 2026, SSRN 7124578)
   - Score: 3/5 | Market: E-mini Dow Futures (YM) / Micro Dow (MYM) | Apex fit: Yes
   - Forced trader: Options dealers hedging retail 0DTE call/put demand during the opening 15–30 minutes of the New York cash open create short-lived upside overextensions that quickly exhaust.
   - My inference trade line: **Market: YM / MYM; Entry: 8:35 to 8:45 CT (9:35 to 9:45 ET, within the first 15 minutes after cash open on sessions opening with an upward push/gap); Exit: 9:30 CT (10:30 ET) or at a 1:1 symmetric target/stop; Direction: Short YM (fading the opening 0DTE hedging overextension), fixed stop 50 points ($250 on YM / $25 on MYM).**

---

## Skip

- **CV_070_hiasDP-E-127.pdf**: not Apex (econometric realized stochastic volatility forecasting model; no directional trading rule or stops).
- **ssrn-1977561.pdf**: no results (purely theoretical mathematical framework and formula; no empirical backtest or results).
- **ssrn-261149.pdf**: not Apex (microstructure noise filter for daily volatility estimation; no trading strategy).
- **ssrn-2903629.pdf**: not Apex (produced net losses on E-mini S&P futures; crude oil momentum requires 1h–4h holding periods held across days, violating Apex flat by 15:59 CT rule).
- **ssrn-306002.pdf**: not Apex (high-frequency volatility estimator and noise filter; no trading rule).
- **ssrn-318239.pdf**: not Apex (S&P 100 econometric volatility forecasting comparison; no trading rule).
- **ssrn-3479421.pdf**: no results (introductory descriptive primer on option Greeks; options trading prohibited on Apex).
- **ssrn-3933070.pdf**: not Apex (requires trading multi-week commodity options portfolios; options prohibited on Apex).
- **ssrn-4792284.pdf**: not Apex (requires multi-leg SPX/SPY option spread portfolios held overnight; options prohibited on Apex).
- **ssrn-5108542.pdf**: not Apex (econometric Hawkes point-process model of quote arrivals; no trading rule).
- **ssrn-6564078.pdf**: tested (matches brief's "gamma / open-interest pinning"; paper finds zero pinning effect on S&P 500).
- **ssrn-6741978.pdf**: tested (matches brief's "20-day bull / bear regime filters and Markov state transitions" and "gamma / open-interest pinning"; extreme warning signs: one unaffiliated author claiming 77% win rate with 71-feature XGBoost HMM).
- **ssrn-6833239.pdf**: tested (matches brief's "CL / ZN opening-range breakouts" and order-flow filters; 3-month paper trading log using retail "ICT" order blocks).
- **ssrn-7098358.pdf**: no results (methodology and architecture blueprint for a dealer-gamma engine; author explicitly states no backtested P&L claim is made; also tested gamma pinning).
- **ssrn-7222220 (1).pdf**: no results (uncompleted draft proposal for SSRN submission with no dataset, testing, or results).
- **ssrn-7323778.pdf**: not Apex (daily rolling GARCH volatility prediction for commodity risk management; no directional trading rule).
- **ssrn-7592005.pdf**: tested (matches brief's "gamma / open-interest pinning" and "0DTE gamma flip / strike pinning"; pre-registered study confirms fade trade loses −4.0 NQ points per trade).
