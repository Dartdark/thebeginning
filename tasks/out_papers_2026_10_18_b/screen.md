# Research Paper Screen: Batch 2026_10_18_b

### 1. Statistical arbitrage in multi-pair trading strategy based on graph clustering algorithms in US equities market (Adam Korniejczuk, Robert Ślepaczuk, 2024, SSRN 4849095)
- File: ssrn-4849095.pdf
- Has results? yes ("All of the tested approaches outperformed appropriate benchmarks. The best combinations of the techniques and parameters demonstrated significantly better performance metrics than the relevant benchmarks. The results have been obtained under the assumption of realistic transaction costs, but are sensitive to the changes of some key parameters" p. 1)
- Quote: "All of the tested approaches outperformed appropriate benchmarks. The best combinations of the techniques and parameters demonstrated significantly better performance metrics than the relevant benchmarks. The results have been obtained under the assumption of realistic transaction costs, but are sensitive to the changes of some key parameters" (p. 1)
- Market and data: S&P 500 constituent stocks, daily bar data from January 1, 2000 to December 31, 2022 (p. 2)
- Index or single stocks? Single stocks (cross-sectional equity pairs of S&P 500 constituent stocks; nets out in index)
- Forced trader: none given
- Timing: daily frequency (holding periods multi-day)
- Costs included? yes (transaction costs modeled, p. 1, 2)
- Out of sample or other markets? yes, out-of-sample test dataset (p. 2)
- Size: not stated in abstract (outperformed buy-and-hold benchmarks on risk-adjusted metrics)
- Score (1 point each): forced trader named (0) / intraday or futures data (0) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (1) = 3
- Apex fit: no, trades portfolios of individual equities on daily bars with multi-day overnight holds; individual equities are not tradeable on Apex futures accounts, and overnight holding violates the mandatory flat by 15:59 CT rule
- Already tested? no

### 2. MaxAI: A Reinforcement Learning and Genetic Algorithm Framework for Intraday Index Futures Trading (Michael Maximilian Huber, 2025, SSRN 5761402)
- File: ssrn-5761402 (1).pdf
- Has results? yes ("The final configuration (NQ34) is validated through an additional four-year backtest, yielding $132,412 net profit across 4,014 trades from January 2018 to August 2022, with a profit factor of 1.07, Sharpe ratio of 1.04, and maximum drawdown of $41,180 after $34,530 in slippage and $8,028 in commissions." p. 1)
- Quote: "The final configuration (NQ34) is validated through an additional four-year backtest, yielding $132,412 net profit across 4,014 trades from January 2018 to August 2022, with a profit factor of 1.07, Sharpe ratio of 1.04, and maximum drawdown of $41,180 after $34,530 in slippage and $8,028 in commissions. The estimated risk of ruin was 0.38 percent." (p. 1)
- Market and data: CME E-mini Nasdaq-100 (NQ) futures, 1-minute price and volume data, January 2018 to August 2022 (plus 2025 live deployment) (p. 1)
- Index or single stocks? Index futures (CME E-mini Nasdaq-100)
- Forced trader: none given (reinforcement learning Q-agent and genetic algorithm hyperparameter optimization)
- Timing: intraday 1-minute bars
- Costs included? yes (commissions $8,028 and slippage $34,530 embedded in backtest, p. 1)
- Out of sample or other markets? yes (60% training / 40% evaluation split, 4-year validation backtest 2018–2022, and forward live deployment February–June 2025, p. 1)
- Size: net profit $132,412 across 4,014 trades, profit factor 1.07, Sharpe ratio 1.04, average trade expectancy ~$33 (p. 1)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (1) = 4
- Apex fit: no, the strategy realized a maximum drawdown of $41,180 on one NQ contract. Scaled to one Micro contract (MNQ, 1/10 size), historical max drawdown is $4,118 (with Monte Carlo 2x stress drawdown at $8,300), which exceeds the Apex 50k $2,000 trailing drawdown limit by more than 2x; no single stop-loss fits the $2,000 drawdown constraint
- Already tested? no

### 3. Stop Distance, Exit Methodology, and Signal Preservation in Intraday Value Area Breakouts: Evidence from E-mini S&P 500 Futures (Theo Johann Howard, 2026, SSRN 6350238)
- File: ssrn-6350238.pdf
- Has results? yes ("The unfiltered continuation signal is not economically significant: the pooled mean return is −2.20 ticks, which is not statistically significant under day-clustered standard errors (t = −1.37, p = 0.17)... price-based stop-loss rules are value-destroying at all twelve tested distances relative to the unmanaged horizon outcome;" p. 1)
- Quote: "The unfiltered continuation signal is not economically significant: the pooled mean return is −2.20 ticks, which is not statistically significant under day-clustered standard errors (t = −1.37, p = 0.17); removal of a single identifiable regime month yields a mean indistinguishable from zero (−0.19 ticks, p = 0.74). However, three structured findings emerge... price-based stop-loss rules are value-destroying at all twelve tested distances relative to the unmanaged horizon outcome;" (p. 1)
- Market and data: E-mini S&P 500 (ES) futures, 1-second trade data across 6,284 breakout events from January 2025 to January 2026 (p. 1)
- Index or single stocks? Index futures (CME E-mini S&P 500)
- Forced trader: none given (Market Profile retail concept: "Setup 2" value area breakout continuation)
- Timing: intraday regular session (first 30 minutes noted as having significantly worse outcomes) (p. 1)
- Costs included? yes (1 tick round-turn transaction cost = $12.50 per contract on ES, p. 8)
- Out of sample or other markets? no (13-month continuous sample 2025–2026)
- Size: base signal return is −2.20 ticks gross (−3.20 ticks net with transaction costs); shallow pullbacks beat deep pullbacks by +4.01 ticks (p. 1)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (0) / costs included (1) = 3
- Apex fit: no, the base signal has a negative expected return (−2.20 ticks gross, −3.20 ticks net), and the author empirically proves that price-based stop-loss rules are value-destroying at every tested distance (stop selectivity peaks at 69%, below the ~75% break-even threshold due to symmetric excursion MFE/MAE ≈ 1.0)
- Already tested? YES: matches brief's "CL / ZN opening-range breakouts" / order-flow and volume-profile filters / plain price pattern (Market Profile value area breakout continuation)

### 4. The Inherent Value of Retail Prop Firms for Fixed-Size Trading Strategies (Zachary Youngblood, 2026, SSRN 7514219)
- File: ssrn-7514219.pdf
- Has results? yes ("When the same trading paths were evaluated under the modeled Topstep $50,000 account framework, mean trader payouts were $9,368.50 against mean account costs of $7,878.30, producing mean net economic P&L of $1,490.19 per account. However, 39.70% of full-sample simulations lost money, and results varied materially between the two five-year subperiods." p. 2)
- Quote: "This article examines whether a retail proprietary or “prop” trading framework can create positive expected economic value for a trading strategy with little or no directional edge... The findings establish that retail prop firm premiums can be underpriced for certain strategies: a fixed-size strategy with no directional edge achieved positive expected economic value when the same strategy was simulated through a prop firm’s framework." (p. 2)
- Market and data: Micro E-mini Nasdaq-100 (MNQ) futures, 1-minute intraday data, 10 years (~2016–2026) across 10,000 randomized long/short paths (p. 2)
- Index or single stocks? Index futures (MNQ)
- Forced trader: none (study of prop firm evaluation payout optionality using a synthetic zero-edge strategy)
- Timing: once daily at 10:00 a.m. ET
- Costs included? yes (Topstep account combine/activation fees and commissions $0.74/round-trip per contract, p. 2, 3)
- Out of sample or other markets? yes, tested across two 5-year subperiods (p. 2)
- Size: underlying strategy produces 49.98% win rate and loses -$24,670 standalone; through prop firm option asymmetry it produces +$1,490.19 net economic P&L per account (p. 2)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (1) = 4
- Apex fit: no, models Topstep evaluation rules (not Apex trailing drawdown rules), and explicitly uses a synthetic 50/50 random coin-flip trade with zero directional market edge (standalone loss of -$24,670); provides no market trading edge
- Already tested? no

### 5. From Funded to Paid: How Big to Bet in a Funded Futures Account, When the Rules Can Take the Account Away (Kenny Tran, 2026, SSRN 7550538)
- File: ssrn-7550538.pdf
- Has results? yes ("Varying the bet does pay in the model: expected withdrawals rise 24% over the best fixed-dollar bet when the loss limit is fixed and 52% when it trails the balance, and past 100% at stronger skill levels. But it buys that with dead accounts. The best policy by expected cash loses 81% and 90% of accounts inside 250 trading days, gets paid at all in only 29% and 18% of paths, and has a median payout of zero." p. 1)
- Quote: "Varying the bet does pay in the model: expected withdrawals rise 24% over the best fixed-dollar bet when the loss limit is fixed and 52% when it trails the balance, and past 100% at stronger skill levels. But it buys that with dead accounts. The best policy by expected cash loses 81% and 90% of accounts inside 250 trading days, gets paid at all in only 29% and 18% of paths, and has a median payout of zero." (p. 1)
- Market and data: 100,000 simulated trading paths under a $2,000 loss budget, plus empirical out-of-sample tests on CME Nasdaq (NQ) and S&P (ES) futures (p. 1)
- Index or single stocks? Index futures (simulated paths + NQ and ES)
- Forced trader: none (mathematical decision framework for capital allocation and bet sizing)
- Timing: daily decision step (how much to risk each trading day)
- Costs included? yes (commissions, platform fees, withdrawal buffers, profit splits modeled, p. 1)
- Out of sample or other markets? yes, out-of-sample frozen policy test on CME futures (p. 1)
- Size: varying bet size increases expected withdrawals by 24% (fixed limit) to 52% (trailing limit), but kills 81–90% of accounts with median payout of zero (p. 1)
- Score (1 point each): forced trader named (0) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (1) = 4
- Apex fit: no, this is a bet-sizing and dynamic programming framework for retail prop accounts, not a directional trading strategy; author explicitly states: "The strategy we fix in advance loses money in both samples, so that test says nothing about whether any of this is profitable. Nothing here is advice, and none of it says a funded account can be expected to make money" (p. 1)
- Already tested? no

### 6. Noise-Band Intraday Momentum in Nasdaq-100 Futures (Justin Chuk, 2026, SSRN 7609644)
- File: ssrn-7609644.pdf
- Has results? yes ("On one-minute data from 2020 to July 2026 the executable rule earns +$10.26 per trading day net of costs (day-block bootstrap 95% interval [+$3.27, +$17.25]), with a daily Sharpe ratio of 1.14 and positive results in each of seven calendar years, two of them only marginally." p. 1)
- Quote: "This paper adapts the intraday momentum strategy of Zarattini et al. (2024), which trades breaks from a “noise area” around the open on the SPY ETF, to Nasdaq-100 futures (NQ) at a fixed size of one micro contract and under constraints that permit unattended webhook execution. On one-minute data from 2020 to July 2026 the executable rule earns +$10.26 per trading day net of costs (day-block bootstrap 95% interval [+$3.27, +$17.25]), with a daily Sharpe ratio of 1.14 and positive results in each of seven calendar years, two of them only marginally." (p. 1)
- Market and data: CME Nasdaq-100 (NQ / MNQ) futures, Databento 1-minute and 5-minute OHLCV data from 2020 to July 2026 (checked 2014–2019 and found flat) (p. 1, 2)
- Index or single stocks? Index futures (CME Nasdaq-100 / MNQ)
- Forced trader: Institutional investors executing large orders across the day via TWAP/VWAP algorithms (Gao et al. 2018) and option market makers dynamically delta-hedging short gamma by buying into rises and selling into falls (Baltussen et al. 2021) (p. 1)
- Timing: Entries checked at :00 and :30 from 10:00 to 15:30 ET (9:00 to 14:30 CT); exit at 15:55 ET (14:55 CT) bar or on trailing stop (p. 2, 3)
- Costs included? yes ($2 round trip commission per contract + detailed execution stress testing with 1 point stop slippage and 1-bar update latency, p. 3, 4)
- Out of sample or other markets? yes, adapted from SPY ETF (Zarattini et al. 2024) to NQ futures; 144 pre-registered test registry; forward paper test logged since September 2026 (p. 1, 5)
- Size: +$10.26 per day net on 1 MNQ contract ($16,582 total net profit over 2,184 trades), daily Sharpe ratio 1.14 (p. 3)
- Score (1 point each): forced trader named (1) / intraday or futures data (1) / data runs to 2018 or later (1) / out-of-sample or another market (1) / costs included (1) = 5
- Apex fit: yes, trades 1 MNQ contract with intraday entries between 9:00 and 14:30 CT and full flat exit by 14:55 CT (well ahead of the 15:59 CT cutoff). The trailing stop (closer of band or VWAP, updated every 5 min) provides tight intraday loss containment (typically 15–40 NQ points = $30–$80 risk per trade on MNQ). Note: Historical max drawdown is $2,458 on 1 MNQ ($3,406 at 95th pct bootstrap), so on a 50K account ($2,000 trailing limit) it requires either a capital cushion rule or deployment on the planned 150K accounts ($4,500 drawdown limit).
- Already tested? no (Note: The user's active combine plan runs "Vault Break" [Task 02] which is a 30-min long-only fixed bracket breakout; Chuk's paper tests the 5-min bidirectional version with VWAP/noise-band trailing stops, short signals, and webhook execution audit).

### 7. Stop-Loss Orders and Price Cascades in Currency Markets (Carol L. Osler, 2002, SSRN 920687)
- File: ssrn-920687.pdf
- Has results? yes ("My analysis of high-frequency exchange rates offers three main results that provide empirical support for the hypothesis that stop-loss orders contribute to price cascades: (1) Exchange rate trends are unusually rapid when rates reach exchange rate levels at which stop-loss orders have been documented to cluster. (2) The response to stop-loss orders is larger than the response to take-profit orders, which generate negative-feedback trading and are therefore unlikely to contribute to price cascades. (3) The response to stop-loss orders lasts longer than the response to take-profit orders." p. 1)
- Quote: "My analysis of high-frequency exchange rates offers three main results that provide empirical support for the hypothesis that stop-loss orders contribute to price cascades: (1) Exchange rate trends are unusually rapid when rates reach exchange rate levels at which stop-loss orders have been documented to cluster. (2) The response to stop-loss orders is larger than the response to take-profit orders, which generate negative-feedback trading and are therefore unlikely to contribute to price cascades. (3) The response to stop-loss orders lasts longer than the response to take-profit orders." (p. 1)
- Market and data: Spot foreign exchange (USD/DEM, USD/JPY, GBP/USD), minute-by-minute quotes during NY hours (9 a.m. to 4 p.m.) from January 1996 through April 1998; customer order book of 9,655 stop-loss and take-profit orders ($55 billion) from August 1999 to April 2000 (p. 3, 29, 31)
- Index or single stocks? Currencies (spot foreign exchange)
- Forced trader: Leveraged currency market participants whose stop-loss orders are triggered sequentially beyond round numbers, generating positive-feedback order flow and price cascades (p. 1-3)
- Timing: 15 minutes to 2 hours following round-number crosses (p. 1, 22)
- Costs included? no (not stated; purely econometric microstructure study)
- Out of sample or other markets? yes, tested across three currency pairs (USD/DEM, USD/JPY, GBP/USD) and split morning/afternoon subsamples (p. 3, 22)
- Size: exchange rates trend 50–100% faster for at least two hours following round-number crosses (p. 1, 22); excess kurtosis / fat tails
- Score (1 point each): forced trader named (1) / intraday or futures data (1) / data runs to 2018 or later (0, data ends in 2000) / out-of-sample or another market (1) / costs included (0) = 3
- Apex fit: no, empirical microstructure study on spot FX (not CME futures traded on Apex); data is from 1996–2000 (more than two decades old); paper provides no concrete trading rules, entry triggers, stop-loss distance, or risk management sizing for a $2,000 trailing drawdown
- Already tested? no

---

## Send to Claude

1. **Noise-Band Intraday Momentum in Nasdaq-100 Futures** (Justin Chuk, 2026, SSRN 7609644)
   - Score: 5/5 | Market: CME Micro E-mini Nasdaq-100 (MNQ) / NQ futures | Apex fit: Yes (requires capital cushion on 50K or deployment on 150K accounts)
   - Forced trader: Institutional investors executing large orders across the day via TWAP/VWAP algorithms (Gao et al. 2018) and option market makers dynamically delta-hedging short gamma into price moves (Baltussen et al. 2021).
   - My inference trade line: **Market: MNQ (Micro E-mini Nasdaq-100 futures); Entry: 9:00 to 14:30 CT (10:00 to 15:30 ET) checked at :00 and :30; Exit: 14:55 CT (15:55 ET bar) or on trailing stop; Direction: Long if 5-minute bar close is above the upper noise band and above VWAP; Short if 5-minute bar close is below the lower noise band and below VWAP; Stop: trailing stop at the closer of the noise band or VWAP, recomputed every 5 minutes at bar close.**

---

## Skip

- **ssrn-4849095.pdf**: single stocks (statistical arbitrage cross-sectional equity pairs on S&P 500 constituent stocks; requires multi-day overnight holding; individual equities prohibited on Apex).
- **ssrn-5761402 (1).pdf**: not Apex (realized maximum drawdown of $41,180 on NQ / $4,118 on MNQ exceeds the Apex $2,000 trailing drawdown limit by more than 2x; black-box reinforcement learning with no forced-trader mechanism).
- **ssrn-6350238.pdf**: tested (Market Profile "Setup 2" value area breakout continuation; base signal has negative expected return of −2.20 ticks, and price-based stop-loss rules destroy value at all tested distances; matches brief's order-flow and price-pattern breakout failures).
- **ssrn-7514219.pdf**: not Apex (study of retail prop firm evaluation payout asymmetry using a synthetic zero-edge 50/50 coin-flip strategy; provides no directional trading rule or market edge).
- **ssrn-7550538.pdf**: not Apex (capital allocation and dynamic bet-sizing framework under trailing drawdowns; underlying strategy loses money in both samples; provides no market trading edge).
- **ssrn-920687.pdf**: not Apex (econometric microstructure study of spot foreign exchange stop cascades from 1996–2000; provides no executable trading rules, stop levels, or risk management).
