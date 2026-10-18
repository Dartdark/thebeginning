# Paul Wilmott - Paul Wilmott Introduces Quantitative Finance (2nd ed., 2007)
Short name: `wilmott_quantfin`
Book: Paul Wilmott, *Paul Wilmott Introduces Quantitative Finance*, 2nd ed., John Wiley & Sons, 2007. ISBN: 978-0-470-31958-1.

---

## 1. What the Book Is About

Paul Wilmott’s *Paul Wilmott Introduces Quantitative Finance* is one of the most celebrated and accessible masterworks on mathematical finance and derivatives engineering. Written with Wilmott’s characteristic clarity, irreverent humor, and mathematical rigor, the textbook spans 30 chapters across five core domains:
- **Derivative Pricing Foundations**: Basic financial products (equities, commodities, foreign exchange, forwards, futures), no-arbitrage bounds, binomial trees, stochastic calculus (Itô’s lemma), and the partial differential equation (PDE) derivation of the Black-Scholes-Merton model.
- **The Greeks & Dynamic Hedging**: Delta, Gamma, Theta, Vega, and Rho; dynamic replication in continuous time vs. discrete rebalancing in practice; Leland’s model for transaction costs; and volatility arbitrage (trading the spread between implied volatility and realized volatility).
- **Exotic and Path-Dependent Derivatives**: American options (optimal early exercise free-boundary problems), barrier options, Asian options, lookback options, and multi-asset options.
- **Fixed Income & Term Structure Modeling**: Yield, duration, and convexity; interest rate swaps; one-factor equilibrium short-rate models (Vasicek, Cox-Ingersoll-Ross); and no-arbitrage yield curve fitting (Ho-Lee, Hull-White, Heath-Jarrow-Morton).
- **Risk Management, Gambling, & Numerical Methods**: Modern Portfolio Theory (Markowitz, CAPM); the Kelly criterion and blackjack card counting; Value at Risk (VaR), CreditMetrics, and CrashMetrics; derivatives disasters (Barings, LTCM, Orange County); finite-difference PDE methods; and Monte Carlo simulation.

---

## 2. Main Claims and Core Findings

1. **Delta Hedging Eliminates Risk in Theory, Creates Exposure in Practice**: The Black-Scholes breakthrough relies on continuous delta hedging to eliminate market risk. In practice, discrete rebalancing intervals, bid-ask spreads, commissions, and non-lognormal jumps ensure that a "delta-hedged" portfolio is never truly risk-free.
2. **Volatility Is the Only Unobservable Parameter**: In the Black-Scholes equation, asset price $S$, strike $K$, risk-free rate $r$, and time to maturity $T-t$ are known. Volatility $\sigma$ is the sole unobservable parameter. Therefore, option pricing is fundamentally volatility forecasting; trading options is trading volatility, not price direction.
3. **Implied Volatility Trades at a Structural Premium to Realized Volatility**: Historical market data shows that implied volatility (e.g. VIX) consistently trades higher on average than subsequent realized volatility (e.g. S&P 500 rolling volatility). This structural spread is driven by institutional demand for downside portfolio insurance, creating a persistent variance risk premium for systematic option sellers.
4. **Normal Distributions and VaR Are Dangerously Flawed**: Traditional risk management tools like Value at Risk (VaR) assume Gaussian returns and continuous paths. During financial panics and market crashes (1987 Black Monday, 1998 LTCM), correlations jump to 1.0, fat tails dominate, and liquidity evaporates. Wilmott argues for non-probabilistic, worst-case stress testing (**CrashMetrics**) over probabilistic VaR.
5. **Models Are Tools, Not Truth**: Quantitative models are approximations designed to assist thinking, not exact laws of physics. Blindly trusting complex models without understanding their underlying assumptions and failure modes inevitably leads to catastrophic institutional collapse.

---

## 3. General Advice vs. Trade Rules

The vast majority of Wilmott's textbook provides foundational mathematical theory, derivative pricing mechanics, and institutional risk governance rather than directional trading signals. These principles offer vital quantitative guidance:

### A. Money Management & Sizing (The Kelly Criterion)
- **Maximizing Log Wealth**: Wealth compounding is geometric. To maximize the long-term expected log of wealth ($\mathbb{E}[\log(W_T)]$), bet sizes must follow the Kelly criterion: $f^* = \frac{\text{Edge}}{\text{Odds}} = \frac{\mu - r}{\sigma^2}$.
- **The Curse of Full Kelly**: Betting full Kelly results in extreme volatility and routine peak-to-trough drawdowns of 33% to 50%. In institutional or prop trading environments with tight trailing stop-outs (e.g. Apex 50K accounts with a $2,000 maximum drawdown), full Kelly sizing guarantees account liquidation.
- **Fractional Kelly**: Betting a conservative fraction (e.g. 10% to 25% of Kelly, or risk-budgeted cushion sizing) preserves the vast majority of compound growth while compressing drawdowns to safe, survival-level bounds.

### B. Risk Decomposition (The Greeks)
- **Delta ($\Delta = \partial V / \partial S$)**: First-order directional price sensitivity. Outright futures trading is pure linear delta exposure.
- **Gamma ($\Gamma = \partial^2 V / \partial S^2$)**: Second-order curvature. Long gamma gains exponentially during large trending moves; short gamma bleeds during violent moves.
- **Theta ($\Theta = \partial V / \partial t$)**: Time decay. The cost of holding optionality.
- **Vega ($\mathcal{V} = \partial V / \partial \sigma$)**: Sensitivity to shifts in implied volatility.

### C. Risk Management Hygiene & Worst-Case Stress Testing
- **CrashMetrics vs. VaR**: Value at Risk tells an institution what it might lose on an ordinary bad day (e.g. 95% or 99% confidence level), which is useless when a systemic crisis hits. Risk managers must evaluate the entire non-linear loss envelope under catastrophic jumps ($\Delta S_{\max} = -20\%$) and structure survival floors in advance.
- **Lessons from Derivatives Disasters**: Historical blowups (Nick Leeson at Barings, Long-Term Capital Management, Metallgesellschaft) were caused by rogue unhedged directional bets, short gamma exposure in illiquid markets, and assuming historical correlations would hold during market stress.
