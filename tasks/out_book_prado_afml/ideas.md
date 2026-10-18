# Testable Trading Ideas: Advances in Financial Machine Learning (Marcos López de Prado, 2018)

Book: Marcos López de Prado, *Advances in Financial Machine Learning* (John Wiley & Sons, 2018, ISBN: 978-1-119-48208-6). Short name: `prado_afml`.

---

### 1. Treasury Auction Liquidity Concession / Pre-Auction Rebalancing Effect
- Where: Chapter 13, Section 13.2 ("Trading Rules"), p. 180 (EPUB: `OPS/c13.xhtml`)
- Quote: "For instance, suppose that financial intermediaries tend to sell off-the-run bonds two days before U.S. Treasury auctions, in order to raise the cash needed for buying the new 'paper.' One could monetize on that knowledge by selling off-the-run bonds three days before auctions. But how? Each investment strategy requires an implementation tactic, often referred to as 'trading rules.'"
- Rule as written:
  - Entry: Sell off-the-run U.S. Treasury bonds 3 days prior to scheduled U.S. Treasury auctions.
  - Exit: Buy back / cover after auction conclusion (exact holding period or intraday exit hour: not stated).
  - Stop loss: not stated.
  - Position sizing: not stated.
  - Market: U.S. Treasury bonds (off-the-run Treasury securities).
  - Bar size: Daily.
  - Holding time: ~3 trading days.
- Book's evidence: none given (cited as an illustrative industry example of a structural market inefficiency).
- Mechanism (the book's): Primary dealers and financial intermediaries who bid at U.S. Treasury auctions are structurally constrained by balance sheet limits and capital requirements. They must liquidate existing off-the-run bond inventories 2 days prior to the auction to raise cash to fund purchases of newly issued on-the-run debt, creating predictable, price-insensitive downward pressure.
- Mechanism (my inference): none needed.
- Apex fit: no. Requires holding bond positions overnight across 3 days; Apex strictly mandates all positions flat by 15:59 CT.
- Already tested? no.

---

### 2. Information-Driven Tick Imbalance Bars (TIB)
- Where: Chapter 2, Section 2.3.2.1 ("Tick Imbalance Bars"), pp. 29–31 (EPUB: `OPS/c02.xhtml`)
- Quote: "The idea behind tick imbalance bars (TIBs) is to sample bars whenever tick imbalances exceed our expectations... When $\theta_T$ is more imbalanced than expected, a low $T$ will satisfy these conditions. Accordingly, TIBs are produced more frequently under the presence of informed trading (asymmetric information that triggers one-side trading). In fact, we can understand TIBs as buckets of trades containing equal amounts of information..."
- Rule as written:
  - Signal / Sampling: Label tick aggressor sign $b_t \in \{-1, +1\}$ via the tick rule ($b_t = b_{t-1}$ if $\Delta p_t = 0$; $\Delta p_t / |\Delta p_t|$ otherwise). Form a bar when absolute cumulative tick imbalance $|\theta_T| = |\sum_{t=1}^T b_t| \ge E_0[T] |2 P[b_t = 1] - 1|$, where $E_0[T]$ and $P[b_t = 1]$ are estimated via exponentially weighted moving averages from prior bars.
  - Action / Entry: Enter directional trade when asymmetric tick imbalance triggers accelerated bar sampling ahead of price reaching new equilibrium.
  - Exit: not stated.
  - Stop loss: not stated.
  - Sizing: not stated.
  - Market: Any tick-level liquid asset (futures, equities).
  - Bar size: Information-driven (variable tick count).
  - Holding time: not stated.
- Book's evidence: Demonstrates that information-driven sampling synchronizes data frequency with informed trader arrival and partially restores IID Gaussian properties.
- Mechanism (the book's): Informed traders possess asymmetric private information and execute aggressively on one side of the market. Monitoring the cumulative tick imbalance detects informed trading before market makers adjust quotes to the new equilibrium price.
- Mechanism (my inference): none needed.
- Apex fit: no. Relies on order-flow / tick classification; matches "order-flow indicator filters" on the brief's failed list.
- Already tested? Matches "order-flow indicator filters" on the brief's failed list.

---

### 3. Information-Driven Volume & Dollar Imbalance Bars (VIB & DIB)
- Where: Chapter 2, Section 2.3.2.2 ("Volume/Dollar Imbalance Bars"), pp. 31–33 (EPUB: `OPS/c02.xhtml`)
- Quote: "The idea behind volume imbalance bars (VIBs) and dollar imbalance bars (DIBs) is to extend the concept of tick imbalance bars (TIBs). We would like to sample bars when volume or dollar imbalances diverge from our expectations... When $\theta_T$ is more imbalanced than expected, a low $T$ will satisfy these conditions."
- Rule as written:
  - Signal / Sampling: Define signed volume/dollar imbalance $\theta_T = \sum_{t=1}^T b_t v_t$, where $v_t$ is volume (VIB) or dollar amount (DIB). Sample bar at $T^*$ where $|\theta_T| \ge E_0[T] |2 v^+ - E_0[v_t]|$, where $v^+$ and $E_0[v_t]$ are estimated via exponential moving averages from prior bars.
  - Action / Entry: Trade in the direction of the outsized volume/dollar imbalance surge.
  - Exit: not stated.
  - Stop loss: not stated.
  - Sizing: not stated.
  - Market: Futures (e.g. E-mini S&P 500) and equities.
  - Bar size: Information-driven volume/dollar bars.
  - Holding time: not stated.
- Book's evidence: Addresses tick fragmentation and corporate actions, regularizing heteroscedasticity compared to time bars.
- Mechanism (the book's): Large institutional traders execute informed parent orders using volume-weighted execution algorithms, leaving persistent signed volume imbalances in the transaction stream.
- Mechanism (my inference): none needed.
- Apex fit: no. Order-flow / volume-signing filter; matches "order-flow indicator filters" on the brief's failed list.
- Already tested? Matches "order-flow indicator filters" on the brief's failed list.

---

### 4. Information-Driven Tick & Volume Runs Bars (TRB & VRB)
- Where: Chapter 2, Section 2.3.2.3 & 2.3.2.4 ("Tick Runs Bars", "Volume/Dollar Runs Bars"), pp. 33–35 (EPUB: `OPS/c02.xhtml`)
- Quote: "Large traders will sweep the order book, use iceberg orders, or slice a parent order into multiple children, all of which leave a trace of runs in the $\{b_t\}_{t=1,\dots,T}$ sequence. For this reason, it can be useful to monitor the sequence of buys in the overall volume, and take samples when that sequence diverges from our expectations."
- Rule as written:
  - Metric: Define run length as $\theta_T = \max(\sum_{t|b_t=1}^T b_t v_t, -\sum_{t|b_t=-1}^T b_t v_t)$ (measuring buy volume or sell volume unilaterally without offsetting). Sample bar when $\theta_T \ge E_0[T] \max(P[b_t=1] E_0[v_t|b_t=1], (1-P[b_t=1]) E_0[v_t|b_t=-1])$.
  - Action / Entry: Follow order book sweeps and institutional iceberg child-order runs.
  - Exit: not stated.
  - Stop loss: not stated.
  - Sizing: not stated.
  - Market: Electronic futures and equity markets.
  - Bar size: Run-driven bar.
  - Holding time: not stated.
- Book's evidence: Detects institutional execution algorithms without requiring order book Level 3 data.
- Mechanism (the book's): Institutional execution algorithms slicing large parent orders or sweeping price levels generate unbroken sequences of aggressive trades that temporarily exhaust one side of the order book.
- Mechanism (my inference): none needed.
- Apex fit: no. Matches "order-flow indicator filters" on the brief's failed list.
- Already tested? Matches "order-flow indicator filters" on the brief's failed list.

---

### 5. Symmetric CUSUM Filter as an Event-Driven Trading Trigger
- Where: Chapter 2, Section 2.5.2.1 ("The CUSUM Filter"), pp. 38–40 (EPUB: `OPS/c02.xhtml`)
- Quote: "The CUSUM filter is a quality-control method, designed to detect a shift in the mean value of a measured quantity away from a target value... Lam and Yam [1997] propose an investment strategy whereby alternating buy-sell signals are generated when an absolute return $h$ is observed relative to a prior high or low. Those authors demonstrate that such strategy is equivalent to the so-called 'filter trading strategy' studied by Fama and Blume [1966]... One practical aspect that makes CUSUM filters appealing is that multiple events are not triggered by gRaw hovering around a threshold level, which is a flaw suffered by popular market signals such as Bollinger bands."
- Rule as written:
  - Signal: Maintain two running cumulative sums from raw price/return series $y_t$:
    $$S_t^+ = \max(0, S_{t-1}^+ + y_t - E_{t-1}[y_t]), \quad S_0^+ = 0$$
    $$S_t^- = \min(0, S_{t-1}^- + y_t - E_{t-1}[y_t]), \quad S_0^- = 0$$
    with $E_{t-1}[y_t] = y_{t-1}$.
  - Entry: When $S_t^+ \ge h$, signal an upward mean-shift event (Buy); when $S_t^- \le -h$, signal a downward mean-shift event (Sell short). Reset $S_t = 0$ upon activation.
  - Parameter $h$: Set dynamically to daily/hourly rolling volatility $\sigma_t$ (e.g. estimated from daily returns or high-low Parkinson volatility).
  - Exit: Alternating buy-sell signals (reverse position), or exit via triple-barrier (horizontal profit/stop or vertical end-of-session limit).
  - Stop loss: Fixed at threshold $h$ or dynamic volatility stop.
  - Sizing: not stated.
  - Market: Tested conceptually on broad asset series; applicable to futures (ES, NQ).
  - Bar size: Minute bars or tick/volume bars.
  - Holding time: Intraday (from trigger until reverse signal or session close).
- Book's evidence: Cites Lam & Yam (1997) and Fama & Blume (1966); illustrates CUSUM sampling on E-mini S&P 500 futures in Figure 2.3.
- Mechanism (the book's): Prices undergo structural mean shifts when new macroeconomic or fundamental information enters the market. Unlike fixed-threshold bands that generate multiple whipsaw signals when price oscillates near a line, CUSUM filters require a full continuous run of size $h$ to trigger, filtering out zero-mean noise while capturing genuine momentum shifts.
- Mechanism (my inference): none needed.
- Apex fit: YES.
  - Flat by 15:59 CT? Yes (intraday run filter; positions entered upon event and closed by 15:00/15:15 CT).
  - Markets: NQ, ES, or micros MNQ, MES.
  - Single stop loss fitting $2,000 trailing drawdown? Yes, when threshold $h$ is calibrated to an intraday volatility fraction on micros (e.g. $0.5\sigma$ to $1.0\sigma$).
- Already tested? no. (Brief noted "20-day bull/bear regime filters" and "moving average crosses" failed, but an intraday CUSUM quality-control run filter is distinct and not on the failed list).

---

### 6. Triple-Barrier Method with Dynamic Volatility Corridors
- Where: Chapter 3, Section 3.4 ("The Triple-Barrier Method"), pp. 45–47 (EPUB: `OPS/c03.xhtml`)
- Quote: "I call it the triple-barrier method because it labels an observation according to the first barrier touched out of three barriers. First, we set two horizontal barriers and one vertical barrier. The two horizontal barriers are defined by profit-taking and stop-loss limits, which are a dynamic function of estimated volatility (whether realized or implied). The third barrier is defined in terms of number of bars elapsed since the position was taken (an expiration limit)."
- Rule as written:
  - Dynamic horizontal barriers: Upper barrier $= P_0 + L_1 \cdot \sigma_t$; Lower barrier $= P_0 - L_2 \cdot \sigma_t$, where $\sigma_t$ is the exponentially weighted rolling standard deviation of returns (Snippet 3.1) and $L_1, L_2$ are non-negative multipliers.
  - Vertical barrier: Maximum holding time limit $t_0 + \Delta t$ (e.g. fixed number of bars or hard end-of-day timestamp).
  - Exit rule: Liquidate position immediately upon the first barrier touched:
    - If upper barrier touched first $\rightarrow$ profit-taking exit.
    - If lower barrier touched first $\rightarrow$ stop-loss exit.
    - If vertical barrier touched first $\rightarrow$ time-expiration market exit.
  - Entry: Triggered by primary strategy signal.
  - Stop loss: Dynamically enforced by the lower horizontal barrier ($L_2 \cdot \sigma_t$).
  - Sizing: Determined by bet sizing or volatility targeting.
  - Market: Applicable across all financial markets (demonstrated on E-mini futures).
  - Bar size: Daily, intraday minute, or volume bars.
  - Holding time: Bounded by vertical barrier $\Delta t$.
- Book's evidence: Demonstrated via Python snippets (Snippets 3.1–3.4) on financial time series, proving path-dependent labeling matches trader reality.
- Mechanism (the book's): Traditional fixed-time horizon exit models fail because price paths are path-dependent. Dynamic volatility scaling aligns risk corridors with market expansion/contraction, while the vertical barrier prevents dead capital allocation in stagnant volatility regimes.
- Mechanism (my inference): none needed.
- Apex fit: YES.
  - Flat by 15:59 CT? Yes (strictly enforced by setting vertical barrier $\le 15:00$ CT).
  - Markets: NQ, ES, CL, GC, ZN, micros.
  - Single stop loss fitting $2,000 trailing drawdown? Yes, stop loss is explicitly defined by horizontal volatility barrier $L_2 \sigma_t$.
- Already tested? no. (This is an execution/risk corridor framework; not on the failed list).

---

### 7. Meta-Labeling for Position Sizing and Trade Filtering
- Where: Chapter 3, Section 3.6 ("Meta-Labeling"), pp. 50–55 (EPUB: `OPS/c03.xhtml`)
- Quote: "Suppose that you have a model for setting the side of the bet (long or short). You just need to learn the size of that bet, which includes the possibility of no bet at all (zero size)... I call this problem meta-labeling because we want to build a secondary ML model that learns how to use a primary exogenous model."
- Rule as written:
  - Primary model: A heuristic, econometric, or technical rule that sets the side: $side \in \{-1, +1\}$ (e.g. moving average cross, Bollinger breakout, fundamental indicator).
  - Secondary model: A binary ML classifier (e.g. Random Forest) trained on meta-labels: $Y \in \{0, 1\}$, where $Y=1$ if the primary trade hits the profit-taking horizontal barrier before the stop-loss barrier, and $Y=0$ otherwise.
  - Filter / Sizing Rule: When primary signal fires, evaluate ML predicted probability $p$. If $p < threshold$ (e.g. 0.5), filter out trade (size $= 0$). If $p \ge threshold$, execute trade with size proportional to probability.
  - Exit: Governed by triple-barrier logic.
  - Stop loss: Governed by lower barrier.
  - Market: General financial assets.
  - Bar size: Any.
  - Holding time: Bounded by vertical barrier.
- Book's evidence: Demonstrates higher precision, higher F1-score, and reduced drawdown on backtested models by separating the decision of side from size.
- Mechanism (the book's): Decoupling side from size allows the primary model to maximize recall (catching opportunities) while the secondary ML model maximizes precision (filtering false positives).
- Mechanism (my inference): none needed.
- Apex fit: no. Explicitly tested and failed on the user's NQ strategy suite.
- Already tested? YES. Matches "**meta-labeling Vault Break**" on the brief's "Already tested and failed" list.

---

### 8. Probability-Derived Sigmoid Bet Sizing
- Where: Chapter 10, Section 10.3 ("Bet Sizing from Predicted Probabilities"), pp. 142–144 (EPUB: `OPS/c10.xhtml`)
- Quote: "Assuming that the Sharpe ratio of opportunities follows a standard Gaussian distribution, we may derive the bet size as $m = 2 Z[z] - 1$, where $m \in [-1, 1]$ and $Z[.]$ is the CDF of the standard Gaussian... We compute the statistic $z = \frac{\tilde{p} - \frac{1}{\|X\|}}{\sqrt{\tilde{p}(1-\tilde{p})}} \sim Z$..."
- Rule as written:
  - Given ML predicted probability $p$ of a successful trade outcome:
    - Compute test statistic: $z = \frac{p - 0.5}{\sqrt{p(1-p)}}$.
    - Derive bet size: $m = 2 Z[z] - 1$, where $Z[\cdot]$ is the standard Gaussian cumulative distribution function.
    - Sizing: Scaled continuously between 0 (when $p = 0.5$) and 1.0 (as $p \to 1.0$).
  - Discretization (Section 10.5): Discretize bet size to a step grid $d$ (e.g. $d = 0.2$ or 1 micro contract) to avoid excessive order adjustments from insignificant probability fluctuations.
  - Stop loss / Exit: Defined by underlying trading rule.
  - Market: General futures / equities.
  - Bar size: Any.
  - Holding time: Governed by active bet duration.
- Book's evidence: Mathematical proof connecting predicted probability to the expected Sharpe ratio and normal CDF (Snippet 10.1).
- Mechanism (the book's): Translates probabilistic classifier confidence directly into capital allocation, scaling risk up when predictive edge is statistically significant and reducing risk to near-zero when confidence is marginal.
- Mechanism (my inference): none needed.
- Apex fit: YES.
  - Flat by 15:59 CT? Yes (applies to sizing intraday trades).
  - Markets: NQ/ES micros (MNQ/MES) where integer discretization maps cleanly to 1 to 5 micro contracts.
  - Single stop loss fitting $2,000 trailing drawdown? Yes, dynamic sizing scales down position size when confidence drops.
- Already tested? no. (This is a quantitative sizing formula, not an indicator filter; not on the failed list).

---

### 9. Dynamic Bet Sizing and Divergence Limit Pricing
- Where: Chapter 10, Section 10.6 ("Dynamic Bet Sizes and Limit Prices"), pp. 146–149 (EPUB: `OPS/c10.xhtml`)
- Quote: "In this section we will introduce an approach to adjust bet sizes as market price $p_t$ and forecast price $f_i$ fluctuate. In the process, we will derive the order's limit price. Let $q_t$ be the current position, $Q$ the maximum absolute position size, and $\hat{q}_{i,t}$ the target position size... $\hat{q}_{i,t} = \text{int}[m[\omega, f_i - p_t] Q]$, where $m[\omega, x] = \frac{x}{\sqrt{\omega + x^2}}$..."
- Rule as written:
  - Divergence: Let $x = f_i - p_t$ be the difference between forecasted target price $f_i$ and current market price $p_t$.
  - Target position size: $\hat{q}_{i,t} = \text{int}\left[ \frac{f_i - p_t}{\sqrt{\omega + (f_i - p_t)^2}} \cdot Q \right]$, where $Q$ is max position size and $\omega$ regulates the sigmoid function's width.
  - Limit order price derivation: The limit price at which the trader is indifferent to adding 1 additional unit is derived by solving for the price $p^*$ where target position equals $q_t + 1$:
    $$p^* = f_i - \sqrt{\frac{\omega (q_t + 1)^2}{Q^2 - (q_t + 1)^2}}$$
  - Action: Place passive limit order at $p^*$, dynamically updating as market price moves.
  - Exit / Stop: Exited when price reaches forecast $f_i$ or stop boundary.
  - Market: Electronic futures and equities with central limit order books.
  - Bar size: Intraday minute bars.
  - Holding time: Duration of the forecast horizon.
- Book's evidence: Mathematical derivation in Snippets 10.4 and 10.5; plots limit price schedules as a function of inventory.
- Mechanism (the book's): As market price fluctuates toward or away from the forecast, the marginal risk/reward of the opportunity changes. Dynamic sizing automatically buys more when price dips below forecast (if within bounds) and places passive limit orders that capture the bid-ask spread rather than paying market spread fees.
- Mechanism (my inference): none needed.
- Apex fit: YES.
  - Flat by 15:59 CT? Yes (intraday execution).
  - Markets: NQ/ES (or MNQ/MES).
  - Single stop loss fitting $2,000 trailing drawdown? Yes, bounded by max size $Q$ and explicit limit prices.
- Already tested? no.

---

### 10. Optimal Trading Rules (OTR) under Ornstein-Uhlenbeck Process
- Where: Chapter 13, Sections 13.4–13.6 ("Numerical Determination of Optimal Trading Rules"), pp. 182–192 (EPUB: `OPS/c13.xhtml`)
- Quote: "Until now we have not characterized the stochastic process from which observations $\pi_{i,t}$ are drawn. We are interested in finding an optimal trading rule (OTR) for those scenarios where overfitting would be most damaging, such as when $\pi_{i,t}$ exhibits serial correlation. In particular, suppose a discrete Ornstein-Uhlenbeck (O-U) process on prices... Using the entire historical sample, we will characterize the stochastic process that generates the observed stream of returns, and derive the optimal values for the trading rule's parameters without requiring a historical simulation."
- Rule as written:
  - Model fitting: Fit discrete Ornstein-Uhlenbeck process on prices $P_{i,t} = E_0[P_{i,T}] + \phi (P_{i,t-1} - E_0[P_{i,T}]) + \xi_t$ to estimate speed parameter $\phi$ and residual variance $\sigma^2$. Half-life $\tau = -\ln(2)/\ln(\phi)$.
  - Calibration without historical backtesting: Generate 100,000 synthetic Monte Carlo paths under estimated $\{\phi, \sigma\}$ with initial condition $P_{i,0}$ and target $E_0[P_{i,T}]$, imposing a vertical holding period barrier ($maxHP = 100$ bars).
  - Mesh evaluation: Evaluate a 20x20 Cartesian mesh of stop-loss and profit-taking thresholds $(\pi_-, \pi_+)$ to find the node that maximizes the Sharpe ratio:
    - *For market makers* ($E_0[P] = 0$, short half-life $\tau \le 5$): Optimal rule is asymmetric: small profit-taking combined with wide stop-losses (e.g. 5x to 7x wider stop).
    - *For position takers* ($E_0[P] > 0$, positive expected drift): Optimal rule is rectangular/square: profit-taking centered on the expected target with tight stop-losses.
  - Entry: Enter upon price divergence.
  - Exit: First barrier touched out of $(\pi_-, \pi_+)$ or vertical expiration $maxHP$.
  - Market: Liquid futures contracts (specifically cites E-mini S&P 500 futures, 10-Year Treasury Note futures, WTI Crude Oil futures in exercises 13.2–13.3).
  - Bar size: Dollar bars or minute bars.
  - Holding time: Up to $maxHP$ (e.g. 100 bars; flat intraday).
- Book's evidence: Extensive experimental heat-maps (Figures 13.1–13.25) across 25 parameter configurations covering zero, positive, and negative expected drifts, demonstrating maximum Sharpe ratios of 3.2 to 12.0.
- Mechanism (the book's): Calibrating stop-loss and profit-taking parameters via brute-force historical backtesting guarantees backtest overfitting (PBO) because parameters overfit random noise in a single observed historical path. Deriving exit corridors numerically from the underlying stochastic process guarantees out-of-sample robustness.
- Mechanism (my inference): none needed.
- Apex fit: YES.
  - Flat by 15:59 CT? Yes (strictly bounded by vertical barrier $maxHP \le 100$ bars, ensuring all trades close within the session).
  - Markets: NQ, ES, CL, GC, ZN, micros.
  - Single stop loss fitting $2,000 trailing drawdown? Yes, stop loss is explicitly derived and capped.
- Already tested? no. (Brief failed list ruled out "mean reversion on NQ / ES", but OTR applies to directional position-takers with positive expected target $E_0[P] > 0$).

---

### 11. Hierarchical Risk Parity (HRP) Asset Allocation
- Where: Chapter 16, Sections 16.4–16.6 ("Machine Learning Asset Allocation"), pp. 226–236 (EPUB: `OPS/c16.xhtml`)
- Quote: "One reason for the instability of quadratic optimizers is that the vector space is modelled as a complete (fully connected) graph, where every node is a potential candidate to substitute another... Markowitz's curse: The higher the correlation between investments, the larger the need for diversification, and the more unstable the inverse covariance matrix is."
- Rule as written:
  - Step 1 (Tree Clustering): Convert correlation matrix $\rho$ to distance matrix $D_{i,j} = \sqrt{\frac{1}{2}(1 - \rho_{i,j})}$. Apply single-linkage hierarchical clustering to build a dendrogram.
  - Step 2 (Quasi-Diagonalization): Reorder rows and columns of covariance matrix to place correlated assets adjacent along the diagonal.
  - Step 3 (Recursive Bisection): Recursively bisect the tree hierarchy, allocating portfolio weight between left and right clusters inversely proportional to each cluster's aggregate variance:
    $$\alpha_1 = 1 - \frac{V_1}{V_1 + V_2}, \quad w_1 = \alpha_1 \cdot W, \quad w_2 = (1 - \alpha_1) \cdot W$$
  - Sizing: Allocates portfolio capital across $N$ assets without requiring matrix inversion.
  - Rebalance: Monthly or quarterly.
  - Stop loss: not stated.
  - Market: Multi-asset universes (stocks, bond futures, commodity futures).
  - Bar size: Daily returns.
  - Holding time: Multi-day / multi-month.
- Book's evidence: Out-of-sample Monte Carlo simulations (Section 16.6) demonstrate HRP delivers higher Sharpe ratio, lower variance, and lower maximum drawdown than Markowitz Minimum Variance and Traditional Risk Parity across 10,000 runs.
- Mechanism (the book's): Quadratic optimizers treat the investment universe as a fully connected graph, causing catastrophic inversion errors when assets are collinear. HRP models investments as a hierarchical tree graph, allocating risk across top-level economic clusters before allocating within clusters.
- Mechanism (my inference): none needed.
- Apex fit: no. HRP is a multi-asset portfolio weighting algorithm requiring holding multiple assets across days/weeks; Apex user trades single-instrument intraday futures.
- Already tested? no.

---

### 12. Chu-Stinchcombe-White CUSUM Structural Break Test on Levels
- Where: Chapter 17, Section 17.3.2 ("Chu-Stinchcombe-White CUSUM Test on Levels"), pp. 253–254 (EPUB: `OPS/c17.xhtml`)
- Quote: "This test follows Homm and Breitung [2012]... We compute the standardized departure of log-price $y_t$ relative to the log-price at $y_n$, $t > n$, as $S_{n,t} = (y_t - y_n) (\hat{\sigma}_t \sqrt{t-n})^{-1}$... These authors derived via Monte Carlo that $b_{0.05} = 4.6$."
- Rule as written:
  - Test Statistic: For log-price series $y_t$, compute standardized departure from baseline $y_n$:
    $$S_{n,t} = \frac{y_t - y_n}{\hat{\sigma}_t \sqrt{t-n}}, \quad \text{where } \hat{\sigma}_t^2 = \frac{1}{t-1} \sum_{i=2}^t (\Delta y_i)^2$$
  - Critical Value: Time-dependent boundary $c_\alpha[n, t] = 4.6 + \log[\sqrt{t-n}]$ at the 5% significance level.
  - Action / Entry: When $S_{n,t} \ge c_\alpha[n, t]$, reject the null hypothesis of a zero-drift random walk; signal a structural upward regime shift and enter long. When $S_{n,t} \le -c_\alpha[n, t]$, signal a structural downward regime shift and enter short.
  - Window: Evaluated across backward-shifting windows $n \in [1, t]$ taking the supremum $S_t = \sup_n S_{n,t}$.
  - Exit: When $S_{n,t}$ returns inside the boundary or at session close.
  - Stop loss: Fixed at entry boundary or trailing volatility stop.
  - Market: Liquid futures (e.g. E-mini S&P 500 futures).
  - Bar size: Dollar bars or minute bars.
  - Holding time: Intraday.
- Book's evidence: Derived via Monte Carlo in Homm & Breitung (2012); applied to E-mini S&P 500 futures in Exercise 17.1.
- Mechanism (the book's): In transitioning from a random walk into a persistent regime trend, price movements accumulate beyond Brownian diffusion limits. The test detects when accumulated price displacement is statistically impossible under random walk diffusion.
- Mechanism (my inference): none needed.
- Apex fit: YES.
  - Flat by 15:59 CT? Yes (evaluated intraday, flat at session close).
  - Markets: NQ, ES, or micros MNQ, MES.
  - Single stop loss fitting $2,000 trailing drawdown? Yes, stop loss placed at regime invalidation level on micros.
- Already tested? no. (Brief failed list includes 20-day Markov regime filters, but this is an intraday continuous-level CUSUM boundary test).

---

### 13. Supremum Augmented Dickey-Fuller (SADF) Explosiveness Bubble/Crash Detector
- Where: Chapter 17, Section 17.4.2 ("Supremum Augmented Dickey-Fuller"), pp. 254–260 (EPUB: `OPS/c17.xhtml`)
- Quote: "In the words of Phillips, Wu and Yu [2011], 'standard unit root and cointegration tests are inappropriate tools for detecting bubble behavior because they cannot effectively distinguish between a stationary process and a periodically collapsing bubble model...' Phillips and Yu [2011] and Phillips, Wu and Yu [2011] proposed the Supremum Augmented Dickey-Fuller test (SADF)... The SADF line spikes when prices exhibit a bubble-like behavior, and returns to low levels when the bubble bursts."
- Rule as written:
  - Regression: Fit backwards-expanding ADF specification on log prices at each bar $t$:
    $$\Delta y_t = \alpha + \beta y_{t-1} + \sum_{l=1}^L \gamma_l \Delta y_{t-l} + \epsilon_t$$
  - Statistic: $SADF_t = \sup_{t_0 \in [1, t-\tau]} \left\{ \frac{\hat{\beta}_{t_0,t}}{\hat{\sigma}_{\beta, t_0, t}} \right\}$, testing $H_0: \beta \le 0$ (steady/unit-root) against right-tail alternative $H_1: \beta > 0$ (explosive process).
  - Action / Entry: When $SADF_t$ breaches critical right-tail threshold, an explosive regime is active.
    - If $\log(y_0) > -\alpha/\beta$, price is in an explosive upward rally $\rightarrow$ ride momentum with trailing stop or fade when SADF turns down.
    - If $\log(y_0) < -\alpha/\beta$, price is in an explosive downward crash $\rightarrow$ short momentum or hedge longs.
  - Exit: When $SADF_t$ rolls over and drops below threshold, or at market close.
  - Stop loss: Trailing stop or dynamic volatility threshold.
  - Market: E-mini S&P 500 futures (Figure 17.1), equity indices.
  - Bar size: Dollar bars or minute bars.
  - Holding time: Duration of the explosive spike (intraday).
- Book's evidence: Empirical plot on E-mini S&P 500 futures continuous price series (Figure 17.1) demonstrating extreme spikes during the 2000 dot-com bubble, 2007–2008 subprime run-up, and 2008 crash.
- Mechanism (the book's): In transitioning into an explosive regime, market participants on the losing side are caught off-guard. Before accepting losses, they act irrationally, holding and desperate averaging down into losing positions. Once margin calls and stop-loss limits are breached, forced liquidations cascade, fueling an explosive non-linear run until liquidity completely exhausts.
- Mechanism (my inference): none needed.
- Apex fit: YES.
  - Flat by 15:59 CT? Yes (can be run on intraday 1-min/5-min bars on NQ/ES, flat at 15:00 CT).
  - Markets: NQ, ES, or micros MNQ, MES.
  - Single stop loss fitting $2,000 trailing drawdown? Yes, sized on micros with a trailing stop.
- Already tested? no. (Not on the brief's failed list).

---

### 14. Sub- and Super-Martingale Explosiveness Tests (SMT)
- Where: Chapter 17, Section 17.4.3 ("Sub- and Super-Martingale Tests"), pp. 260–261 (EPUB: `OPS/c17.xhtml`)
- Quote: "Consider a process that is either a sub- or super-martingale. Given some observations $\{y_t\}$, we would like to test for the existence of an explosive time trend, $H_0: \beta = 0, H_1: \beta \ne 0$, under alternative specifications: Polynomial trend... Exponential trend... Power trend... Similar to SADF, we fit any of these specifications to each end point $t = \tau,\dots,T$, with backwards expanding start points, then compute $SMT_t = \sup_{t_0} \frac{|\hat{\beta}_{t_0,t}|}{\hat{\sigma}_{\beta, t_0, t} (t - t_0)^\phi}$..."
- Rule as written:
  - Specification: Fit exponential trend $\log[y_t] = \log[\alpha] + \beta t + \xi_t$ or power trend $\log[y_t] = \log[\alpha] + \beta \log[t] + \xi_t$ on backwards-expanding windows.
  - Penalty parameter $\phi \in [0, 1]$: Penalizes sample length to balance detection between long-run and short-run bubbles (e.g. $\phi = 0.5$).
  - Entry: Enter in direction of $\beta$ when $SMT_t$ exceeds critical threshold.
  - Exit: When $SMT_t$ decays or at session close.
  - Stop loss: not stated.
  - Market: Equity index futures.
  - Bar size: Dollar bars or minute bars.
  - Holding time: Intraday.
- Book's evidence: Demonstrates parameterization across polynomial, exponential, and power trends in Exercise 17.4.
- Mechanism (the book's): Direct parametric measurement of super-exponential price paths driven by feedback loops and forced participant capitulation.
- Mechanism (my inference): none needed.
- Apex fit: YES.
  - Flat by 15:59 CT? Yes (intraday holding).
  - Markets: NQ, ES, micros.
  - Single stop loss fitting $2,000 trailing drawdown? Yes, on micros with stop loss.
- Already tested? no.

---

### 15. Market Entropy / Lempel-Ziv Compression Inefficiency Metric
- Where: Chapter 18, Section 18.8.1 & 18.8.4 ("Market Efficiency", "Market Microstructure"), pp. 273–276 (EPUB: `OPS/c18.xhtml`)
- Quote: "When arbitrage mechanisms exploit the complete set of opportunities, prices instantaneously reflect the full amount of available information, becoming unpredictable (i.e., a martingale), with no discernable patterns. Conversely, when arbitrage is not perfect, prices contain incomplete amounts of information, which gives rise to predictable patterns. Patterns occur when a string contains redundant information, which enables its compression... Bubbles are formed in compressed (low entropy) markets."
- Rule as written:
  - Metric: Discretize return stream or signed order flow $v_t^B$ into binary or quantile alphabet. Estimate entropy rate $H[X]$ using Kontoyiannis' Lempel-Ziv estimator (Snippet 18.4).
  - Trading Signal:
    - When entropy rate $H[X]$ is abnormally low (high compression rate / high redundancy): Market is inefficient and predictable patterns dominate. Enter trend-following or breakout strategies.
    - When entropy rate $H[X]$ is near maximum theoretical entropy: Market is highly efficient and unpredictable. Suspend trend-following; switch to market making or stand aside.
  - Exit: When entropy normalizes or at session close.
  - Stop loss: not stated.
  - Market: E-mini S&P 500 futures (Exercise 18.1).
  - Bar size: Dollar bars or volume bars.
  - Holding time: Intraday.
- Book's evidence: Derived from information theory (Shannon 1948, Lempel & Ziv 1978, Kontoyiannis 1998); demonstrated on simulated Gaussian processes and S&P 500 futures.
- Mechanism (the book's): Efficient markets produce incompressible, high-entropy white noise. Inefficient or bubble regimes produce repetitive, low-entropy sequential patterns because algorithmic herding and constrained arbitrageurs create redundant order sequences.
- Mechanism (my inference): none needed.
- Apex fit: YES.
  - Flat by 15:59 CT? Yes (intraday regime filter).
  - Markets: NQ/ES futures or micros.
  - Single stop loss fitting $2,000 trailing drawdown? Yes, on micros.
- Already tested? no.

---

### 16. Volume-Synchronized Probability of Informed Trading (VPIN) Toxicity Detector
- Where: Chapter 19, Section 19.5.2 ("Volume-Synchronized Probability of Informed Trading"), pp. 290–292 (EPUB: `OPS/c19.xhtml`)
- Quote: "Easley et al. [2011] proposed a high-frequency estimate of PIN, which they named volume-synchronized probability of informed trading (VPIN). This procedure adopts a volume clock, which synchronizes the data sampling with market activity, as captured by volume... $VPIN_\tau = \frac{\sum_{\tau=1}^n |V_\tau^B - V_\tau^S|}{n V}$... a number of studies have found that VPIN indeed has predictive power: Abad and Yague [2012], Bethel et al. [2012], Cheung et al. [2015]..."
- Rule as written:
  - Metric: Under a volume clock where each bar contains constant volume $V$, classify trade volume into buy volume $V_\tau^B$ and sell volume $V_\tau^S$ via the tick rule. Compute VPIN over a rolling window of $n$ volume bars:
    $$VPIN_\tau = \frac{\sum_{i=1}^n |V_i^B - V_i^S|}{n \cdot V}$$
  - Signal / Action: When VPIN exceeds its 99th percentile historical threshold:
    - For market makers: Immediately withdraw passive bids/offers to avoid toxic adverse selection.
    - For directional traders: Trade in the direction of the dominant signed order flow $(V_\tau^B - V_\tau^S)$, anticipating liquidity dry-up and severe directional volatility cascades.
  - Exit: Liquidate when VPIN drops back below normal historical median (e.g. 50th percentile) or at session close.
  - Stop loss: Dynamic volatility stop.
  - Market: E-mini S&P 500 futures, WTI Crude Oil, major futures.
  - Bar size: Volume bars (constant $V$).
  - Holding time: Intraday (from toxicity spike until order flow rebalances).
- Book's evidence: Cites Easley, López de Prado, and O'Hara (2011, 2012a, 2012b) showing VPIN reached record historical extremes prior to the May 6, 2010 Flash Crash.
- Mechanism (the book's): Market makers act as sellers of an option to be adversely selected. When informed traders aggressively buy or sell, order flow toxicity surges. Market makers cannot discern individual trader motives, but observe sustained order flow imbalances; to avoid catastrophic losses, they simultaneously pull passive limit orders from the book, causing liquidity to evaporate and triggering sharp price cascades.
- Mechanism (my inference): none needed.
- Apex fit: no. Relies on order-flow classification and imbalance metrics; matches "order-flow indicator filters" on the brief's failed list.
- Already tested? Matches "order-flow indicator filters" on the brief's failed list.

---

### 17. Roll (1984) Effective Bid-Ask Spread & Serial Covariance Model
- Where: Chapter 19, Section 19.3.2 ("The Roll Model"), pp. 282–284 (EPUB: `OPS/c19.xhtml`)
- Quote: "Roll [1984] was one of the first models to propose an explanation for the effective bid-ask spread at which a security trades... $\sigma[\Delta p_t, \Delta p_{t-1}] = -c^2$, resulting in $c = \max\{0, -\sigma[\Delta p_t, \Delta p_{t-1}]\}$ and $\sigma_u^2 = \sigma^2[\Delta p_t] + 2 \sigma[\Delta p_t, \Delta p_{t-1}]$. In conclusion, the bid-ask spread is a function of the serial covariance of price changes..."
- Rule as written:
  - Metric: Estimate effective spread half-width $c = \sqrt{-\text{Cov}(\Delta p_t, \Delta p_{t-1})}$ when first-order autocovariance is negative.
  - Application: Detects the presence of bid-ask bounce noise. When autocovariance is strongly negative, price changes reflect microstructure bouncing between bid and ask rather than true fundamental price movement.
  - Action: Filter out false momentum breakouts occurring within the effective spread $2c$; provide passive liquidity inside wide estimated spreads.
  - Exit / Stop: not stated.
  - Market: Infrequently traded securities, corporate bonds, futures.
  - Bar size: Tick or trade bars.
  - Holding time: Microstructure horizon (seconds to minutes).
- Book's evidence: Theoretical derivation from Roll (1984) under geometric random walk assumptions.
- Mechanism (the book's): Sequential trade execution against passive bid and ask quotes introduces artificial negative serial correlation (bid-ask bounce) in transaction prices, masking true price innovation variance.
- Mechanism (my inference): none needed.
- Apex fit: no. Microstructure noise estimation; trades mean reversion inside the spread, which on NQ/ES fails after transaction costs ($7.25 per side + 1 tick slippage).
- Already tested? Matches "mean reversion on NQ / ES" on the brief's failed list.

---

### 18. Corwin and Schultz (2012) High-Low Bid-Ask Spread Estimator
- Where: Chapter 19, Section 19.3.4 ("Corwin and Schultz"), pp. 284–286 (EPUB: `OPS/c19.xhtml`)
- Quote: "Corwin and Schultz [2012] introduce a bid-ask spread estimator from high and low prices. The estimator is based on two principles: First, high prices are almost always matched against the offer, and low prices are almost always matched against the bid. The ratio of high-to-low prices reflects fundamental volatility as well as the bid-ask spread. Second, the component of the high-to-low price ratio that is due to volatility increases proportionately with the time elapsed between two observations."
- Rule as written:
  - Formula: Compute 2-bar high/low ratios $\beta_t = \sum_{j=0}^1 [\log(H_{t-j}/L_{t-j})]^2$ and $\gamma_t = [\log(H_{t-1,t}/L_{t-1,t})]^2$. Spread is estimated as:
    $$S_t = \frac{2(e^{\alpha_t} - 1)}{1 + e^{\alpha_t}}, \quad \text{where } \alpha_t = \frac{\sqrt{2\beta_t} - \sqrt{\beta_t}}{3 - 2\sqrt{2}} - \sqrt{\frac{\gamma_t}{3 - 2\sqrt{2}}}$$
  - Application: Tracks effective transaction costs and liquidity dry-ups from simple OHLC bars without requiring Level 2 tick quotes.
  - Action: Avoid trading or widen breakout bands when estimated spread $S_t$ spikes.
  - Exit / Stop / Sizing: not stated.
  - Market: Corporate bonds, equities, futures.
  - Bar size: Daily or hourly bars.
  - Holding time: not stated.
- Book's evidence: Python implementation in Snippets 19.1 and 19.2; validated against TAQ datasets in Corwin & Schultz (2012).
- Mechanism (the book's): High prices in any bar are buyer-initiated at the ask, while low prices are seller-initiated at the bid. Combining 1-bar and 2-bar high-low variances separates true volatility from the constant bid-ask spread component.
- Mechanism (my inference): none needed.
- Apex fit: no. Liquidity filter rather than a standalone directional trading rule.
- Already tested? no.

---

### 19. Kyle's Lambda ($\lambda$) and Amihud's Price Impact Illiquidity Trading
- Where: Chapter 19, Section 19.4.1 & 19.4.2 ("Kyle's Lambda", "Amihud's Lambda"), pp. 286–289 (EPUB: `OPS/c19.xhtml`)
- Quote: "In Kyle's model, the variable $\lambda$ captures price impact. Illiquidity increases with uncertainty about $v$ and decreases with the amount of noise. As a feature, it can be estimated by fitting the regression $\Delta p_t = \lambda b_t V_t + \epsilon_t$... Amihud [2002] studies the positive relationship between absolute returns and illiquidity... $\Delta \log \tilde{p}_\tau = \lambda \sum_{t \in B_\tau} p_t V_t + \epsilon_\tau$..."
- Rule as written:
  - Kyle's $\lambda$: Regress price changes against signed volume: $\Delta p_t = \lambda (b_t V_t) + \epsilon_t$.
  - Amihud's $\lambda$: Regress absolute returns against dollar volume: $|\Delta \log \tilde{p}_\tau| = \lambda \cdot DollarVolume_\tau + \epsilon_\tau$.
  - Application: When $\lambda$ or Amihud illiquidity is high, price impact per contract is severe.
  - Trading Signal: Follow institutional order flow when $\lambda$ is rising (anticipating persistent drift); fade order flow when $\lambda$ collapses (reversion to liquidity).
  - Exit / Stop / Sizing: not stated.
  - Market: E-mini S&P 500 futures (Figures 19.1 & 19.2).
  - Bar size: 5-minute bars or volume bars.
  - Holding time: not stated.
- Book's evidence: Empirical histograms of Kyle's and Amihud's lambdas computed on E-mini S&P 500 futures (Figures 19.1–19.2).
- Mechanism (the book's): Informed traders submit market orders to monetize mispricing, while noise traders provide camouflage. Market makers set price impact $\lambda$ to balance inventory risk against adverse selection. In thin liquidity regimes, even moderate order flow drives outsized price displacement.
- Mechanism (my inference): none needed.
- Apex fit: no. Order-flow price impact filter; matches "order-flow indicator filters" on the brief's failed list.
- Already tested? Matches "order-flow indicator filters" on the brief's failed list.

---

## Ranked Shortlist of Apex-Compatible Ideas

Of the 19 ideas cataloged from the book, only **3 ideas** strictly satisfy all three criteria:
1. **Apex-compatible**: Flat by 15:59 CT (intraday only), tradeable on equity index futures (NQ/ES/MNQ/MES), with a defined stop loss fitting a $2,000 trailing drawdown.
2. **Not already tested**: Not in the brief's "Already tested and failed" list (disqualifying meta-labeling, order-flow indicators, 20-day regime filters, and mean reversion on NQ/ES).
3. **Stated mechanism**: Supported by an explicit structural or economic mechanism explaining who is forced or paid to trade.

Ranked by the clarity of the forced trader:

### 1. Supremum Augmented Dickey-Fuller (SADF) Explosive Regime Breakout (Idea 13)
- **Rank**: 1
- **Where**: Chapter 17, Section 17.4.2 (pp. 254–260)
- **Why #1**: The forced trader mechanism is exceptionally clear. In a transitioning regime where prices switch from stationary/random walk to an explosive unit-root process ($\beta > 0$), participants positioned against the move (mean-reverters and short-sellers) are caught off-guard. Behavioral biases lead them to hold and average down into losing positions. Once cumulative losses breach margin maintenance thresholds, brokers execute mandatory, price-insensitive stop-out liquidations, fueling an explosive runaway trend until liquidity collapses.
- **Apex implementation**: Evaluated on 1-minute or 5-minute intraday bars of NQ/ES (or MNQ/MES). When $SADF_t$ breaches its right-tail critical threshold, enter momentum in the direction of the explosive run. Enforce an intraday trailing volatility stop. Liquidate flat by 15:00 CT (59 minutes before the 15:59 CT cutoff). Fits within a $2,000 trailing drawdown when sized on micro contracts.

### 2. Symmetric CUSUM Volatility Run-Breakout (Idea 5)
- **Rank**: 2
- **Where**: Chapter 2, Section 2.5.2.1 (pp. 38–40)
- **Why #2**: The mechanism is rooted in quality-control engineering (Lam & Yam 1997 / Fama & Blume 1966). Unlike standard indicators (e.g. Bollinger bands) that generate chronic false whipsaws when prices oscillate around a static line, the CUSUM filter requires an unbroken run of accumulated price displacement equal to dynamic volatility $h = \sigma_t$. This detects when price has experienced a true structural mean shift driven by aggressive institutional order arrival, filtering out noise.
- **Apex implementation**: Run on intraday minute bars on NQ/ES (MNQ/MES). Enter long when $S_t^+ \ge h$ and short when $S_t^- \le -h$, where $h$ is anchored to intraday Parkinson/Garman-Klass volatility. Exit upon reverse threshold trigger or flat at 15:00 CT. A catastrophic stop placed at $h$ protects against sudden adverse reversals, fitting comfortably within the $2,000 trailing drawdown.

### 3. Optimal Trading Rules (OTR) under Ornstein-Uhlenbeck Process with Vertical Barrier (Idea 10)
- **Rank**: 3
- **Where**: Chapter 13, Sections 13.4–13.6 (pp. 182–192)
- **Why #3**: Eliminates backtest overfitting (PBO) by deriving the exit corridor directly from the underlying stochastic process parameters (speed of convergence $\phi$ and volatility $\sigma$) on synthetic paths, rather than in-sample curve fitting. For directional position-takers with an expected target ($E_0[P] > 0$), the mathematically optimal exit is a profit target centered on the expected move with a tight stop loss, bounded by a strict vertical holding-period barrier.
- **Apex implementation**: Evaluated on NQ/ES opportunities where an exogenous catalytic signal forecasts an intraday move. Calculate $\{\phi, \sigma\}$ on a rolling window; set stop-loss $\pi_-$ and profit target $\pi_+$ from the pre-computed OTR mesh; enforce a vertical barrier ($maxHP \le 60$ minutes, exiting flat by 15:00 CT). Tight, mathematically derived stop losses ensure compliance with the $2,000 trailing drawdown.
