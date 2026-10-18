# Paul Wilmott - Paul Wilmott Introduces Quantitative Finance (2nd ed., 2007)
Short name: `wilmott_quantfin`
Book: Paul Wilmott, *Paul Wilmott Introduces Quantitative Finance*, 2nd ed., John Wiley & Sons, 2007. ISBN: 978-0-470-31958-1.

---

### 1. Delta Hedging & Dynamic Option Replication (Black-Scholes-Merton)
- Where: Chapter 6 ("The Black-Scholes Model", pp. 111-136) & Chapter 8 ("The Black-Scholes Formulae and the Greeks", pp. 147-172)
- Quote: "By choosing to hold a quantity $-\Delta$ of the underlying asset, where $\Delta = \frac{\partial V}{\partial S}$, the random movement of the asset is eliminated from the portfolio over the next time step $dt$... The portfolio becomes risk-free and must earn the risk-free rate of interest."
- Rule as written:
  - Market: Equities, equity indices, currencies, or commodities with active option chains.
  - Bar size: Continuous time (in practice, rebalanced at discrete intervals $\delta t$ such as hourly, daily, or on delta bands).
  - Portfolio construction: Form portfolio $\Pi = V - \Delta S$, where $V$ is an option contract and $S$ is the underlying asset. Calculate option delta $\Delta = \frac{\partial V}{\partial S}$ from the Black-Scholes formula: $\Delta_{\text{call}} = N(d_1)$, $\Delta_{\text{put}} = N(d_1) - 1$.
  - Execution: For each option held, sell (short) $\Delta$ shares of the underlying asset.
  - Exit / Rebalancing: Continuously recompute $\Delta_t$ as underlying price $S$ and time $t$ evolve; buy or sell underlying shares to restore delta neutrality ($\Delta_{\text{portfolio}} = 0$). Hold until option expiration $T$.
  - Stop loss: None stated (hedged portfolio is theoretically risk-free under continuous geometric Brownian motion).
  - Sizing: Determined by client trade size or market maker book inventory.
  - Holding time: Duration of the option contract (weeks to months).
- Book's evidence: Foundation of the 1973 Black-Scholes-Merton options pricing model and Nobel prize-winning framework. Validated by trillions of dollars in daily OTC and exchange-traded derivative transactions.
- Mechanism (the book's): No-arbitrage replication. Because delta eliminates first-order price risk over $dt$, the portfolio has zero variance and must yield the risk-free rate $r$. If an option deviates from Black-Scholes fair value, an arbitrageur buys the cheap instrument and replicates the synthetic short, locking in a riskless spread.
- Mechanism (my inference): None needed; book provides complete PDE derivation and economic rationale.
- Apex fit: No. Requires trading options (Apex trades only outright futures), continuous multi-day dynamic hedging, and holding positions overnight across expiration cycles. Violates flat by 15:59 CT daily closeout.
- Already tested? No.

---

### 2. Volatility Arbitrage via Delta-Neutral Portfolios (Actual vs. Implied Volatility)
- Where: Chapter 9 ("Overview of Volatility Modeling", pp. 173-186) & Chapter 10 ("How to Delta Hedge", pp. 187-210)
- Quote: "Buy the option today, hedge using the implied delta, and put any cash in the bank earning $r$. The mark-to-market profit from today to tomorrow is $\frac{1}{2} (\sigma^2 - \tilde{\sigma}^2) S^2 \frac{\partial^2 V}{\partial S^2} dt$... This is a far nicer way to make money. Observe how the daily profit is deterministic... all we need to know is that actual is always going to be greater than implied (if we are buying) or always less (if we are selling)."
- Rule as written:
  - Market: Equity index options (e.g. S&P 500 / SPX / VIX) or individual liquid equity options.
  - Bar size: Daily rebalancing.
  - Signal: Compare market implied volatility $\tilde{\sigma}$ against proprietary forecast of realized volatility $\sigma$.
  - Entry:
    - If forecast realized volatility exceeds implied volatility ($\sigma > \tilde{\sigma}$): Buy the option (long gamma $\Gamma > 0$) and delta hedge using the implied delta $\Delta = \frac{\partial V}{\partial S}(\tilde{\sigma})$.
    - If forecast realized volatility is less than implied volatility ($\sigma < \tilde{\sigma}$): Sell the option (short gamma $\Gamma < 0$) and delta hedge using the implied delta.
  - Exit: Rebalance delta hedge daily at market close until option expiration or until implied volatility converges to realized volatility.
  - Stop loss: None stated.
  - Sizing: Scaled by available portfolio vega/gamma risk limits.
  - Holding time: Multi-week to multi-month expiration cycle.
- Book's evidence: Wilmott presents historical distributions of VIX implied volatility vs. realized SPX rolling volatility (Figure 10.1). Shows that VIX trades at a persistent structural premium (mean ~20%) over realized SPX volatility (mean ~15%), creating systematic profit opportunities for volatility sellers, while long gamma positions profit during large market shocks.
- Mechanism (the book's): Variance risk premium and institutional hedging demand. Institutional asset managers buy out-of-the-money put options as catastrophic insurance against market crashes. This persistent demand bids implied volatility above expected realized volatility, allowing delta-hedged market makers and volatility arbitrageurs to harvest the variance premium.
- Mechanism (my inference): None needed; book details implied vs. actual volatility spread dynamics.
- Apex fit: No. Requires trading options contracts and delta hedging underlying shares/futures overnight over weeks/months. Prohibited on Apex (outright futures only, flat daily by 15:59 CT).
- Already tested? No.

---

### 3. Discrete Delta Hedging with Transaction Costs (Leland's Model)
- Where: Chapter 10 ("How to Delta Hedge - Hedging in practice & Transaction costs", pp. 200-210)
- Quote: "In reality you cannot hedge continuously, and hedging costs money because of the bid-ask spread and broker commissions... Leland (1985) showed that discrete delta hedging with transaction costs can be modeled by modifying the volatility in the Black-Scholes equation by adding or subtracting an amount proportional to the transaction cost and inversely proportional to the square root of the hedging interval."
- Rule as written:
  - Market: Exchange-traded options and underlying stocks/futures.
  - Bar size: Fixed discrete rebalancing interval $\delta t$ (e.g. daily, hourly, or every 15 minutes).
  - Transaction cost: Round-trip cost per share traded equal to $k$ (half the bid-ask spread plus commissions).
  - Adjusted Volatility (Leland formula):
    $$\sigma_{\text{eff}}^2 = \sigma^2 \left(1 + \text{Le} \cdot \text{sgn}\left(\frac{\partial^2 V}{\partial S^2}\right)\right)$$
    where the Leland number is $\text{Le} = \sqrt{\frac{2}{\pi}} \frac{k}{\sigma \sqrt{\delta t}}$.
  - Execution: If short gamma ($\Gamma < 0$), price option with increased volatility $\sigma_{\text{eff}} > \sigma$; rebalance delta hedge strictly every $\delta t$. If long gamma ($\Gamma > 0$), price option with reduced volatility $\sigma_{\text{eff}} < \sigma$.
  - Exit: Option expiration.
  - Stop loss: None stated.
  - Sizing: Book inventory limit.
  - Holding time: Duration of the option contract.
- Book's evidence: Mathematical derivation replicating Leland (1985) and Hoggard, Whalley, and Wilmott (1994). Simulation shows that without volatility adjustment, transaction costs from rebalancing wipe out all theoretical option trading edge.
- Mechanism (the book's): Friction-adjusted replication. Buying high and selling low when rebalancing a short gamma position incurs unavoidable bid-ask crossing costs; Leland's formula charges buyers the exact expected value of the rebalancing friction.
- Mechanism (my inference): None needed; book details transaction cost math.
- Apex fit: No. Requires option contracts and multi-day dynamic hedging. Off-limits on Apex.
- Already tested? No.

---

### 4. Duration Matching & Convexity Hedging for Fixed Income
- Where: Chapter 14 ("Fixed-Income Products and Analysis: Yield, Duration and Convexity", pp. 245-266)
- Quote: "Duration measures the sensitivity of a bond's price to changes in yield... By matching duration while maximizing convexity, an investor creates a portfolio that gains more when interest rates change significantly in either direction than a duration-matched benchmark."
- Rule as written:
  - Market: US Treasury bonds, notes, bills, or interest rate futures (e.g. 10-Year Note - ZN).
  - Bar size: Daily yield curve data.
  - Formulae: Modified Duration $D_{\text{mod}} = -\frac{1}{P} \frac{dP}{dy} = \frac{D_{\text{Mac}}}{1 + y/m}$; Convexity $C = \frac{1}{P} \frac{d^2P}{dy^2}$. Price change approximation: $\frac{\Delta P}{P} \approx -D_{\text{mod}} \Delta y + \frac{1}{2} C (\Delta y)^2$.
  - Strategy Rules:
    - *Immunization*: Construct bond portfolio such that aggregate modified duration matches liability target: $\sum w_i D_{\text{mod}, i} = D_{\text{target}}$.
    - *Convexity Barbell vs. Bullet*: Construct a zero-duration, zero-net-cost portfolio consisting of a "barbell" (long short-maturity bonds and long long-maturity bonds) financed by a short "bullet" (short intermediate-maturity bonds) with equal total duration ($D_{\text{barbell}} = D_{\text{bullet}}$). Because the barbell has higher convexity ($C_{\text{barbell}} > C_{\text{bullet}}$), the portfolio gains during large parallel yield shifts in either direction.
  - Exit: Rebalance monthly or when yield curve shifts alter duration balance.
  - Stop loss: None stated.
  - Sizing: Capital allocated to achieve target duration weighting.
  - Holding time: Months to years.
- Book's evidence: Standard institutional fixed-income portfolio management across US Treasury and corporate bond markets.
- Mechanism (the book's): Bond price curvature (convexity). A bond's price-yield function is convex to the origin; price gains from falling yields are larger than price losses from rising yields of the same magnitude. Barbell portfolios capture second-order curvature while neutralizing first-order duration risk.
- Mechanism (my inference): None needed; book provides classical bond math.
- Apex fit: No. While Treasury futures (ZN) are traded on Apex, barbell/bullet convexity trades require holding multi-instrument yield curve positions across weeks/months. Cannot be traded intraday and violates flat by 15:59 CT daily closeout.
- Already tested? No.

---

### 5. Mean-Reverting Short Rate Models & Yield Curve Arbitrage (Vasicek / CIR)
- Where: Chapter 16 ("One-Factor Interest Rate Modeling", pp. 283-306) & Chapter 17 ("Yield Curve Fitting", pp. 307-320)
- Quote: "The Vasicek model introduces mean reversion to interest rates, reflecting the economic reality that interest rates do not wander off to infinity but are pulled back toward a long-term economic average by central bank policy and macroeconomic forces."
- Rule as written:
  - Market: Short-term interest rates, Treasury bonds, and interest rate swaps.
  - Bar size: Daily interest rates / yield curve data.
  - Model: Vasicek stochastic process: $dr = \gamma (\bar{r} - r) dt + \sigma dW$, where $\bar{r}$ is the long-term mean rate and $\gamma$ is the speed of mean reversion; or Cox-Ingersoll-Ross (CIR): $dr = \gamma (\bar{r} - r) dt + \sigma \sqrt{r} dW$.
  - Pricing & Arbitrage: Derive theoretical zero-coupon bond prices $P(t, T) = A(t, T) e^{-B(t, T) r_t}$. Fit model parameters $(\gamma, \bar{r}, \sigma, \lambda)$ to market yield curve.
  - Trading Rule: If market bond yields or swap spreads diverge significantly from theoretical zero-coupon curve $P(t, T)$:
    - Buy undervalued maturity bond / swap, sell overvalued maturity bond / swap.
    - If short rate $r_t$ is significantly above $\bar{r}$, take long fixed-rate duration position anticipating rate decline.
  - Exit: Rebalance as market rates revert to theoretical model equilibrium.
  - Stop loss: None stated.
  - Sizing: Scaled by interest rate duration (DV01) exposure.
  - Holding time: Multi-week to multi-year macroeconomic cycle.
- Book's evidence: Calibrated to historical US Treasury and money market yield curves. Yield curve shapes (normal upward-sloping, inverted, humped) derived analytically from model parameters.
- Mechanism (the book's): Central bank monetary policy feedback. Central banks tighten monetary policy (raise rates) when economic growth and inflation overheat, and ease policy (cut rates) during recessions, creating fundamental economic mean reversion toward neutral interest rates ($r^*$).
- Mechanism (my inference): None needed; book outlines macroeconomic monetary mechanics.
- Apex fit: No. Macroeconomic interest rate convergence strategy holding cash bonds and interest rate derivatives across months/years. Not an intraday directional trading rule; violates flat by 15:59 CT daily closeout.
- Already tested? No.

---

### 6. Kelly Criterion Advantage Play & Bet Sizing
- Where: Chapter 20 ("Investment Lessons from Blackjack and Gambling", pp. 359-382)
- Quote: "The Kelly criterion tells you how much to bet on each turn of a favorable game to maximize the long-term compound growth rate of your capital... If you bet more than the Kelly fraction, your expected return actually decreases while your risk of ruin skyrockets."
- Rule as written:
  - Market: Any investment, trading strategy, or gambling game with a positive expected edge ($\mu > 0$).
  - Discrete Formula: Optimal bet fraction $f^* = \frac{p(b+1) - 1}{b} = \frac{p b - q}{b} = \frac{\text{Edge}}{\text{Odds}}$, where $p$ is probability of winning, $q = 1-p$, and $b$ is net payoff ratio (win amount / loss amount).
  - Continuous Formula: For asset with expected drift $\mu$, risk-free rate $r$, and volatility $\sigma$: $f^* = \frac{\mu - r}{\sigma^2}$.
  - Execution Rule:
    - Bet or allocate strictly fraction $f^*$ of current total capital $W_t$ on each trade: $\text{Bet Size}_t = f^* \cdot W_t$.
    - If edge is zero or negative ($p b \le q$), bet zero ($f^* = 0$).
    - Fractional Kelly: To mitigate estimation error and curtail drawdowns, use fractional Kelly $f = c \cdot f^*$ where $c \in [0.2, 0.5]$ (half-Kelly or quarter-Kelly).
  - Exit: Bet settles at trade outcome.
  - Stop loss: Implicit in bet size (loss per trade bounded by $f^* W_t$).
  - Holding time: Duration of single bet or trade.
- Book's evidence: Ed Thorp's historical blackjack card counting results and Princeton Newport Partners market-neutral hedge fund track record (1969-1988). Mathematical proof showing that Kelly betting outperforms any other betting strategy in the long run with probability 1.
- Mechanism (the book's): Maximization of expected logarithmic wealth: $\max \mathbb{E}[\log(W_T)]$. Because investment compounding is multiplicative, geometric mean return governs terminal wealth; arithmetic mean return is illusory due to volatility drag (a 50% loss requires a 100% gain to break even).
- Mechanism (my inference): None needed; book provides full mathematical and information-theoretic proof.
- Apex fit: Position sizing algorithm only (not a directional entry signal). In the context of Apex 50K combines ($2,000 trailing drawdown limit on $50,000 account = 4.0% maximum permissible drawdown), standard full Kelly sizing guarantees account failure because full Kelly routinely incurs 33% to 50% peak-to-trough drawdowns. Only a heavily scaled fractional Kelly ($f^*/10$ or risk-budgeted cushion sizing) is viable.
- Already tested? Mentioned in brief as the foundation of the funded cushion sizing rule.

---

### 7. Modern Portfolio Theory (Markowitz Mean-Variance Optimization) & CAPM
- Where: Chapter 21 ("Portfolio Management", pp. 383-406)
- Quote: "Modern Portfolio Theory shows that by combining assets that are not perfectly correlated, an investor can reduce total portfolio risk without sacrificing expected return... The efficient frontier represents the set of optimal portfolios that offer the highest expected return for a given level of risk."
- Rule as written:
  - Market: Universe of risky assets (stocks, bonds, commodities).
  - Bar size: Daily or monthly historical returns.
  - Formulae: Expected return $\mu_p = w^T \mu$; Portfolio variance $\sigma_p^2 = w^T \Sigma w$.
  - Optimization Problem: Minimize $w^T \Sigma w$ subject to $w^T \mu = \mu_{\text{target}}$ and $\sum w_i = 1$. The tangency portfolio maximizes the Sharpe ratio: $\max_w \frac{w^T \mu - r_f}{\sqrt{w^T \Sigma w}}$.
  - Capital Asset Pricing Model (CAPM): Asset expected return $\mathbb{E}[R_i] = r_f + \beta_i (\mathbb{E}[R_m] - r_f)$ where $\beta_i = \frac{\text{Cov}(R_i, R_m)}{\text{Var}(R_m)}$.
  - Execution: Rebalance asset weights $w_i$ periodically (monthly/quarterly) to remain on the efficient frontier.
  - Stop loss: None stated.
  - Sizing: Determined by weights $w$.
  - Holding time: Multi-month / multi-year continuous allocation.
- Book's evidence: Harry Markowitz (1952) Nobel Prize paper and William Sharpe (1964) CAPM framework. Evaluated on US blue-chip equities (e.g. Disney, Microsoft).
- Mechanism (the book's): Diversification effect. Idiosyncratic risk is uncorrelated across firms and cancels out in an aggregated portfolio, leaving only systematic market covariance risk.
- Mechanism (my inference): None needed; book provides standard portfolio theory derivation.
- Apex fit: No. Multi-asset portfolio allocation across equities and bonds held over long horizons. Not an intraday single-instrument directional trading rule. Apex trades 1 intraday futures contract with a strict trailing stop.
- Already tested? No.

---

### 8. CrashMetrics: Worst-Case Scenario Hedging & Stress Testing
- Where: Chapter 25 ("CrashMetrics", pp. 445-462)
- Quote: "Value at Risk tells you what you might lose on a normal bad day, but it is completely useless during a crash... CrashMetrics takes a worst-case approach: assume the worst happens, compute your portfolio's nonlinear response across the entire crash envelope, and optimize your portfolio to survive."
- Rule as written:
  - Market: Complex institutional derivative portfolios (options, swaps, futures, underlying stocks).
  - Framework: Assume asset prices experience an instantaneous non-probabilistic market crash of magnitude $\Delta S \in [-\Delta S_{\max}, +\Delta S_{\max}]$ (e.g. up to a 20% drop).
  - Optimization: Compute portfolio nonlinear change $\Delta \Pi(\Delta S) \approx \Delta \cdot \Delta S + \frac{1}{2} \Gamma (\Delta S)^2$. Formulate hedging problem: Find hedge weights $w_{\text{hedge}}$ in liquid hedging instruments (puts, futures) to minimize worst-case portfolio loss:
    $$\max_{w} \min_{\Delta S} \Delta \Pi(\Delta S; w)$$
    subject to cash constraints and maximum acceptable crash drawdown.
  - Execution: Buy out-of-the-money puts or futures hedges to eliminate downside convex crash exposure ("Platinum Hedging").
  - Exit: Dynamic adjustment as market price levels and portfolio positions shift.
  - Stop loss: Implicit in worst-case optimization envelope.
  - Sizing: Derived from mathematical programming solution.
  - Holding time: Continuous structural book overlay.
- Book's evidence: Case studies analyzing the 1987 Black Monday crash (-23% in one day) and the 1998 Long-Term Capital Management (LTCM) collapse. Demonstrates that standard VaR (assuming normal distributions) underestimated true tail losses by an order of magnitude, whereas CrashMetrics correctly identifies nonlinear catastrophic exposures.
- Mechanism (the book's): Market crash physics and illiquidity. During a panic, normal statistical correlations break down to 1.0, liquidity evaporates, and stop-loss orders suffer massive slippage; portfolios must be structurally immunized in advance against jump discontinuities.
- Mechanism (my inference): None needed; book details institutional stress-testing physics.
- Apex fit: No. Risk management and hedging methodology for institutional multi-asset option portfolios, not an intraday directional trading strategy.
- Already tested? No.

---

### 9. Cost-of-Carry Futures / Cash-and-Carry Arbitrage
- Where: Chapter 1 ("Products and Markets: Equities, Commodities, Exchange Rates, Forwards and Futures", pp. 1-32)
- Quote: "Arbitrage guarantees that the futures price must equal the spot price compounded at the cost of carry... If the futures price diverges from this fair value, a riskless profit can be locked in by simultaneously buying the cheap asset and selling the expensive one until delivery."
- Rule as written:
  - Market: Commodities (crude oil, gold, grains) and stock index futures (S&P 500, Nasdaq-100).
  - Bar size: Real-time tick / daily close.
  - Pricing Equation: Fair futures price $F_0 = S_0 e^{(r + u - y) T}$, where $S_0$ is spot price, $r$ is risk-free financing rate, $u$ is physical storage and insurance cost, $y$ is convenience yield or dividend yield, and $T$ is time to maturity.
  - Cash-and-Carry Arbitrage:
    - If market futures price $F_{\text{market}} > S_0 e^{(r + u - y) T} + \text{Transaction Costs}$: Borrow cash at rate $r$, buy physical spot asset $S$, pay storage $u$, and sell (short) futures contract $F$. Deliver physical asset at maturity $T$, locking in riskless profit $F - S_0 e^{(r+u-y)T}$.
    - Reverse Cash-and-Carry: If $F_{\text{market}} < S_0 e^{(r + u - y) T} - \text{Transaction Costs}$: Short spot asset $S$, invest proceeds at $r$, and buy futures $F$.
  - Exit: Hold positions until futures contract expiration and delivery.
  - Stop loss: None (pure arbitrage).
  - Sizing: Limited by financing line and physical warehouse capacity.
  - Holding time: Weeks to months until contract expiration.
- Book's evidence: Empirical pricing of financial and commodity forward/futures contracts. Derives theoretical no-arbitrage bounds enforced by index arbitrage desks and physical commodity merchants.
- Mechanism (the book's): Physical no-arbitrage boundary. Spot and futures represent the identical underlying asset separated only by time and carrying costs; divergence creates riskless cash flow arbitrage that market makers exploit until prices align.
- Mechanism (my inference): None needed; book details classical forward pricing.
- Apex fit: No. Requires simultaneous positions in physical cash/spot assets and futures contracts held until delivery over months. In an Apex futures account, traders cannot trade physical spot, cannot take delivery, and must be strictly flat daily by 15:59 CT.
- Already tested? No.

---

## Ranked Short List

Under the strict criteria of `tasks/TASK_BOOK_READING.md` and `tasks/ANTIGRAVITY_BRIEF.md`, candidate rules must be:
1. **Apex-compatible**: Trade outright futures (NQ/ES/CL/GC/ZN), strictly flat by 15:59 CT daily, and use a single stop loss that respects a $2,000 trailing drawdown limit.
2. **Not already tested and failed**: Must not violate the brief's failure list (mean reversion on NQ/ES, order-flow indicator filters, moving average cross, gamma/open-interest pinning).
3. **Have a stated economic mechanism**: Identify who is forced or paid to trade and why they accept losing.

### Result: 0 Directional Candidate Strategies Qualify

Every single trading strategy and quantitative model in Paul Wilmott’s textbook fails Apex qualification for distinct structural reasons:

1. **Option Derivatives Strategies (Rules 1, 2, 3)**:
   - Black-Scholes Delta Hedging, Volatility Arbitrage (Implied vs. Realized Vol), and Leland's Discrete Hedging all require trading option contracts and dynamically hedging the underlying asset continuously across expiration cycles. **Options are strictly prohibited on Apex prop accounts** (which permit only outright futures contracts), and holding positions overnight violates the mandatory **flat by 15:59 CT daily closeout**.
2. **Fixed Income Term Structure & Duration Models (Rules 4 & 5)**:
   - Duration Matching, Convexity Barbell/Bullet Hedging, and Vasicek/CIR Yield Curve Arbitrage operate across multi-maturity cash bond baskets or interest rate swaps over multi-week macroeconomic cycles. They cannot be executed as intraday single-instrument directional trades and violate flat by 15:59 CT.
3. **Cash-and-Carry Futures Arbitrage (Rule 9)**:
   - Requires simultaneous long/short positions across physical spot cash assets and futures contracts held until expiration/delivery. Apex traders have no access to physical spot markets, cannot take delivery, and cannot carry overnight positions.
4. **Portfolio Allocation & Stress Testing Frameworks (Rules 7 & 8)**:
   - Modern Portfolio Theory (Markowitz) and CrashMetrics are multi-asset portfolio balancing and stress-testing algorithms, not directional trade entry rules.

### Quantitative Risk Insights for Apex Execution

While 0 directional entry rules qualify, Paul Wilmott’s mathematical derivations provide profound foundational insights that directly validate the user’s current prop trading architecture:

1. **Mathematical Justification for Cushion Sizing (Rule 6 - Kelly Criterion)**:
   - Wilmott proves that while full Kelly betting maximizes long-term compound growth, it inherently subjects the account to severe drawdowns of 33% to 50%. On an Apex 50K account, the trailing drawdown limit is $2,000 (a 4.0% loss threshold). Full Kelly sizing guarantees account termination. Wilmott demonstrates that fractional Kelly (e.g. 10% Kelly) retains ~75% of the growth rate while slashing drawdown risk by an order of magnitude, mathematically validating the user's cushion rule ($1,500+ above drawdown = full size; below = half size).
2. **First-Order Delta vs. Second-Order Gamma Risk (Rules 1 & 8)**:
   - Wilmott emphasizes that directional trading is pure linear delta risk, whereas holding derivatives exposes traders to non-linear gamma, theta decay, and vega shocks. By trading outright intraday futures (flat by 15:59 CT), the user eliminates overnight gap risk, theta decay, and financing drag, isolating pure intraday momentum.
