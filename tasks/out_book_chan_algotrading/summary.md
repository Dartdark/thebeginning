# Book Summary: Algorithmic Trading (Ernest P. Chan, 2013)

**Title**: *Algorithmic Trading: Winning Strategies and Their Rationale*  
**Author**: Dr. Ernest P. Chan  
**Publisher**: John Wiley & Sons, 2013 (ISBN: 978-1-118-74691-2)  
**Short Name**: `chan_algotrading`

---

## 1. What the Book Is About

Dr. Ernest P. Chan's *Algorithmic Trading* is a practitioner's guide to quantitative strategy design, statistical testing, and market mechanics. Expanding on his 2009 introductory text (*Quantitative Trading*), Chan focuses on two major classes of quantitative strategies: **mean reversion** and **momentum**, across equities, currencies, ETFs, and futures. 

The core thesis of the book is that profitable quantitative trading requires more than curve-fitting backtests: every strategy must possess a rigorous **mathematical formulation** and a clear **economic rationale** (identifying who is on the losing side of the trade and why they are forced or willing to lose). Chan pairs theoretical foundations (stochastic processes, cointegration, time series analysis, Kelly optimization) with concrete MATLAB implementations and empirical backtest evaluations.

---

## 2. Main Claims and Theoretical Foundations

1. **Standalone Price Series Are Non-Stationary**: Traded assets almost universally follow geometric random walks. Raw price mean reversion is rare and statistically weak in single stocks or unadjusted commodities.
2. **Manufacturing Stationarity via Cointegration**: While individual asset prices wander non-stationarily, linear combinations of two or more economically linked assets can form stationary, mean-reverting portfolios. Cointegration tests (CADF for pairs, Johansen eigenvector decomposition for triplets/baskets) identify optimal hedge ratios and the number of independent stationary portfolios.
3. **Half-Life Governs Strategy Parameters**: By mapping discrete mean-reverting price changes to a continuous Ornstein-Uhlenbeck process ($dy_t = (\mu + \lambda y_t)dt + d\epsilon$), the half-life of mean reversion is analytically derived as $\tau = -\ln(2)/\lambda$. This half-life establishes the natural, objective lookback window for moving averages, volatility bands, and trade holding times—eliminating arbitrary brute-force parameter optimization.
4. **Kalman Filtering Resolves Non-Stationary Drift**: Static linear regression fails when macroeconomic relationships slowly evolve. Dynamic linear regression using the Kalman filter dynamically updates hedge ratios and intercepts tick-by-tick without lookahead bias.
5. **Futures Returns Are Dominated by Roll Yield**: Unlike cash equities, futures total returns equal spot return plus roll return (contango vs. backwardation). Persistent roll yield over time drives long-horizon time series momentum and calendar spread mean reversion.
6. **Intraday Momentum Stems from Structural Inelasticity**: Intraday momentum is driven by structural and institutional forces:
   - *Cascading stop orders* triggering outside previous-day ranges at the opening bell.
   - *Leveraged ETF rebalancing*: Mandated daily constant-leverage targets force ETF managers into massive, price-insensitive market-on-close buying on up days and selling on down days.
   - *Information diffusion / PEAD*: Institutional execution constraints cause multi-hour drift following earnings announcements.

---

## 3. General Advice vs. Trading Rules

Chan carefully segregates general quantitative engineering principles from specific trading rules:

### A. Backtesting Hygiene and Statistical Rigor (Chapter 1)
- **Look-Ahead Bias**: Inadvertently using future data in calculations (e.g. calculating half-life across the entire sample, using primary exchange close prices before market open, or back-adjusting continuous contracts using future returns).
- **Data-Snooping Bias & Multiple Testing**: Backtests with high Sharpe ratios often result from testing hundreds of rules. Chan advocates walk-forward out-of-sample testing and hypothesis testing using Berntson critical values (requiring daily Sharpe $t \ge 2.33$ for $p < 0.01$, or Monte Carlo permutation testing of trade entry dates).
- **Data Integrity**: Historical stock data must be adjusted for stock splits and cash dividends; short-sale constraints and historical regulatory bans (e.g. 2008 financial short sale ban) must be incorporated.
- **Continuous Futures Contracts**: Ratio back-adjustment distorts price spread differences, creating phantom jumps; difference back-adjustment should be used when modeling price spreads.

### B. Execution Architecture & Platform Selection (Chapter 1)
- **Event-Driven vs. Bar-Driven**: Complex Event Processing (CEP) and callback-driven architectures respond to tick arrivals and news events instantaneously, whereas bar-driven polling introduces latency.
- **Latency Realities**: Retail co-location at data centers often yields negligible advantage if broker execution routing or API confirmation latency dominates the round trip.

### C. Position Sizing and Money Management (Chapter 8)
- **Kelly Formula**: For Gaussian returns, the optimal growth-maximizing leverage is $f^* = m / s^2$ (mean return divided by variance).
- **Fractional Kelly**: Because parameter estimates for $m$ and $s$ carry substantial sampling error, unconstrained Kelly betting leads to extreme drawdown volatility. Chan strongly advocates **Half-Kelly** ($f^*/2$) or **Quarter-Kelly** ($f^*/4$) to drastically cut drawdown while sacrificing only a fraction of growth.
- **Constant Proportion Portfolio Insurance (CPPI)**: To prevent an account from breaching a maximum allowable drawdown $-D$, Chan implements CPPI by allocating a fraction $D$ of equity to a trading subaccount with leverage $f$, keeping $1-D$ in risk-free cash. If equity draws down, position sizing scales down aggressively, guaranteeing that drawdown never breaches $-D$ in continuous trading.

### D. Risk Management & Stop-Losses (Chapter 8)
- **The Stop-Loss Paradox**: In a strictly stationary, mean-reverting process, a stop-loss mathematically *lowers* the backtest APR and Sharpe ratio by prematurely closing trades at maximum deviation just before they revert.
- **Regime Change Protection**: However, financial processes are non-stationary and subject to structural regime shifts. Chan concludes that a stop-loss is essential not because it improves backtest metrics in stationary periods, but as mandatory insurance against permanent regime change and tail-risk failure.
