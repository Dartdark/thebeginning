# Book Summary: Systematic Trading (Robert Carver, 2015)

**Title**: *Systematic Trading: A unique new method for designing trading and investing systems*  
**Author**: Robert Carver (Former Head of Fixed Income, AHL / Man Group)  
**Publisher**: Harriman House, 2015 (ISBN: 978-0-85719-445-9)  
**Short Name**: `carver_systematic`

---

## 1. What the Book Is About

Robert Carver’s *Systematic Trading* provides a comprehensive, practitioner-grade architecture for designing, constructing, and managing automated trading and investment systems. Drawing upon his experience as Head of Fixed Income at AHL (one of the world's largest quantitative managed futures / CTA hedge funds at Man Group), Carver demystifies quantitative institutional trading into an accessible, modular, and mathematically sound engineering framework.

The book is structured around three distinct archetypes of systematic investors:
1. **The Asset Allocating Investor**: A long-term passive investor who allocates systematically across uncorrelated global asset classes (equities, bonds, commodities) using dynamic volatility weighting without market-timing forecasts.
2. **The Semi-Automatic Trader**: An investor who generates directional trade ideas or forecasts discretionarily (fundamental, macro, or qualitative) but submits them to a rigid systematic sizing, volatility-targeting, and execution engine.
3. **The Staunch System Trader**: A fully quantitative, automated trader who operates multiple systematic trading rules (trend following, carry, value) across dozens of liquid futures and FX markets with continuous risk budgeting and automated order execution.

Carver's primary contribution is not a collection of secret predictive indicators, but rather a unified **system framework** that standardizes trading rules, forecasts, volatility targeting, instrument diversification, and order execution buffers into a cohesive mathematical machine.

---

## 2. Main Claims and Theoretical Foundations

1. **Humans Are Fundamentally Flawed Traders**:
   Cognitive psychology demonstrates that human traders are subject to deep behavioral biases: loss aversion (holding losers too long in hopes of breaking even), the disposition effect (cutting winners prematurely to lock in a psychological gain), overconfidence, recency bias, and emotional fatigue during drawdowns. A systematic trading framework removes human discretion from risk allocation and trade execution, enforcing statistical discipline.
2. **Positive vs. Negative Skewness (The Two Ways to Make Money)**:
   Carver categorizes all trading strategies by their return distribution skewness:
   - *Positive Skew (Trend Following / Momentum)*: Features a low win rate (often 30–45%), frequent small losses, and occasional massive, open-ended windfall gains ("fat right tail"). Positive skew strategies suffer long, grinding drawdowns but survive extreme market crises and provide crisis alpha.
   - *Negative Skew (Carry / Mean Reversion / Arbitrage / Premium Selling)*: Features a high win rate (often 65–85%), steady and predictable small daily gains, but occasional catastrophic drawdowns ("fat left tail"). Investors routinely mistake high Sharpe ratios in negative skew strategies for superior skill, failing to recognize that they are simply picking up nickels in front of a steamroller. Carver emphasizes combining positive skew (trend) and negative skew (carry) strategies in balanced proportions (e.g., 60/40) to diversify distributional risk.
3. **Forecast Standardization on a [-20, +20] Continuum**:
   Rather than using binary (all-in / all-out) signals, Carver introduces a standardized dimensionless trading forecast scale. Regardless of the underlying mechanism (fast trend, slow trend, carry, overnight drift), raw indicator values are scaled so that the historical absolute average forecast equals **+10**, capped strictly at **+20** (maximum long) and **-20** (maximum short). A forecast of 0 indicates complete neutrality (zero position). This allows heterogeneous models and timeframes to be combined linearly with clear, interpretable weights.
4. **The Forecast Diversification Multiplier (FDM)**:
   When multiple uncorrelated trading rules are combined for a single asset, or multiple uncorrelated assets are combined in a portfolio, diversification reduces aggregate portfolio volatility. To prevent the combined strategy from trading too small and falling below the investor’s target risk, Carver derives the Forecast Diversification Multiplier ($FDM = 1 / \sqrt{w^T \Sigma w}$), which systematically scales combined forecasts back up to maintain the target risk level.
5. **Continuous Volatility Targeting ($w_t \propto 1/\sigma_t$)**:
   Carver rejects fixed-share or fixed-dollar position sizing. Position sizes are dynamically re-benchmarked every day using exponential moving standard deviations of daily price changes. As market volatility expands, position size contracts automatically; as volatility contracts, position size expands. This ensures that every trade contributes an equal unit of risk to the portfolio, insulating the trader from regime shifts and tail-risk blowups.
6. **Execution Buffer Zones (Friction Management)**:
   Continuous systematic models produce small, daily changes in target position sizes. Directly executing every micro-adjustment burns massive amounts of capital through transaction costs, broker commissions, and the bid-ask spread. Carver mathematically proves that implementing a **$\pm 10\%$ position buffer zone** around optimal target holdings cuts portfolio trading turnover by **30% to 40%** while introducing negligible tracking error against target risk.

---

## 3. General Advice vs. Trading Rules

Carver explicitly separates overarching system design, risk management, and operational hygiene from specific trade-generating rules:

### A. Backtesting Hygiene and the "Handcrafting" Philosophy (Chapters 6 & 8)
- **The Curse of Optimization / Data-Fitting**:
  Carver delivers an uncompromising critique of parameter optimization in backtesting. He demonstrates that searching for the "optimal" moving average lookback (e.g., testing every parameter from 5 to 200 to find the best Sharpe ratio) is an exercise in data fitting that guarantees out-of-sample failure.
- **Handcrafted Robust Systems**:
  Instead of optimizing, Carver advocates "handcrafting": selecting a broad, geometrically spaced set of intuitive, permanent parameter variations (e.g., EWMAC lookback pairs 2:8, 4:16, 8:32, 16:64, 32:128, 64:256) and allocating capital equally across them. Because no single parameter can be known to be best in advance, pooling multiple speeds captures trends across all market horizons without curve-fitting.
- **Cost Drag and Speed Penalties**:
  Fast trading rules generate high gross Sharpe ratios on paper, but after realistic commissions and half-spread costs, their net Sharpe ratios collapse. Slow rules trade infrequently, incurring minimal transaction drag. Carver establishes that typical retail and small-scale traders cannot afford to trade fast trend rules (e.g., 2:8 or 4:16) due to transaction cost friction, and should instead focus on medium to slow horizons (16:64, 32:128, 64:256).

### B. Risk Control, Leverage, and Capital Adequacy (Chapters 4, 9 & 10)
- **Cash Volatility vs. Target Volatility**:
  The user must establish an explicit annual portfolio risk target (typically 10% to 25% annualized standard deviation). A 25% annualized risk target implies an expected 1-in-100-year drawdown of approximately 50–60%. Carver stresses that if an investor cannot tolerate a 50% drawdown, they must lower their annual volatility target to 10–12%.
- **Futures Lumpiness and Capital Minimums**:
  Futures contracts represent large, discrete nominal exposures (e.g., one standard crude oil contract controls 1,000 barrels). Carver mathematically shows that trading full-sized futures contracts with proper risk targeting and diversification requires significant capital (often $100,000 to $500,000+). Undercapitalized accounts trading full-size contracts are forced to over-concentrate risk, leading to almost certain ruin. (Micro contracts and mini futures mitigate this constraint for smaller systematic accounts).
- **The Fallacy of Arbitrary Stop Losses in Trend Following**:
  Carver provides rigorous empirical and theoretical arguments against tight, hard stop losses in systematic trend following. Arbitrary stop losses truncate the natural variance of trend systems, frequently stopping out positions during routine market noise right before major trending moves occur. In Carver's architecture, risk is controlled by **sizing small initially**; the systematic forecast itself contracts smoothly towards zero as price reverses, providing an organic, volatility-adjusted exit.

### C. Execution and Portfolio Construction (Chapters 11 & 12)
- **Equal Weighting vs. Mean-Variance Optimization**:
  Carver warns against Markowitz mean-variance optimization for instrument and rule weighting. Covariance matrices and expected return estimates are notoriously unstable. Instead, he demonstrates that simple equal weighting (or inverse-volatility weighting) with an analytical Forecast Diversification Multiplier produces vastly more robust out-of-sample portfolio Sharpe ratios than quadratic optimizers.
- **Buffer Zone Execution Discipline**:
  Traders must never chase infinitesimal changes in continuous target positions. Carver prescribes strict algorithmic execution thresholds: calculate target contracts, establish a $\pm 10\%$ upper and lower contract buffer, and only execute trades when current holdings breach the outer buffer boundary, trading strictly back to the buffer edge or target.
