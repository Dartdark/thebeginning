# Paper Digest: Beyond the Traditional VIX: A Novel Approach to Identifying Uncertainty Shocks in Financial Markets

**Authors**: Ayush Jha (Texas Tech), Abootaleb Shirvani (Kean), Svetlozar T. Rachev (Texas Tech), Frank J. Fabozzi (Johns Hopkins)  
**Publication**: Journal of Risk and Financial Management, 2025, 18(1), 11 (Published December 29, 2024)  
**DOI**: [https://doi.org/10.3390/jrfm18010011](https://doi.org/10.3390/jrfm18010011)

---

## 1. Executive Summary & Problem Formulation

In modern macro-finance (Bloom 2009, 2014), macroeconomic uncertainty shocks are traditionally quantified through the second moment (standard deviation) of S&P 500 option-implied volatility—specifically the CBOE Volatility Index (VIX).

However, this traditional framework suffers from two fundamental theoretical and econometric flaws:
1. **Thin-Tailed Gaussian Assumption**: The traditional VIX formula and standard dispersion measures implicitly assume symmetric, Gaussian returns. In reality, equity returns exhibit pronounced fat tails, skewness, and extreme jump risk (Cont 2000, Kozeniauskas et al. 2018).
2. **Short-Memory Volatility Models (GARCH)**: Standard GARCH/ARMA models enforce exponential decay in autocorrelation, severely underestimating the enduring persistence and volatility clustering of large market disruptions.

To address these limitations, the authors construct a revised volatility index—the **Volatility of VIX (VVIX)**—derived from a **double-subordinated Normal Inverse Gaussian (NDIG) Lévy process** fitted to S&P 500 daily log returns (2014–2023) and modeled via long-memory **ARFIMA-FIGARCH** time series.

---

## 2. Core Methodological Contributions

### A. Double-Subordinated Normal Inverse Gaussian (NDIG) Lévy Process
To preserve the semi-martingale structure required by the fundamental theorem of asset pricing (Delbaen & Schachermayer 1994, Duffie 2001) while incorporating stochastic volatility and heavy tails:
* Log-price process:
  $$X_t = X_0 + \mu_3 t + \gamma U(t) + \rho T(U(t)) + \sigma_3 B_{T(U(t))}$$
  where $B_t$ is standard Brownian motion, and $T(t)$ and $U(t)$ are mutually independent Inverse Gaussian (IG) Lévy subordinators:
  $$T(1) \sim IG(\lambda_T, \mu_T), \quad U(1) \sim IG(\lambda_U, \mu_U)$$
* Option pricing is performed analytically via the Fast Fourier Transform (FFT) of Carr and Madan (2001).
* **Empirical Fit**: Unlike normal and Student's $t$ distributions, the NDIG model perfectly captures both extreme tail heaviness and asymmetric skewness in S&P 500 returns across the 2018–2023 rolling windows.

### B. Long-Memory Modeling: ARFIMA-FIGARCH
Financial volatility exhibits **long-range dependence (LRD)** characterized by slow, hyperbolic decay in the autocorrelation function (ACF), rather than exponential decay:
* **Mean Equation**: $\text{ARFIMA}(1, d(m), 1)$:
  $$\phi(L)(1 - L)^{d(m)} z_t = \theta(L) \varepsilon_t, \quad d(m) = 0.268$$
* **Variance Equation**: $\text{FIGARCH}(1, d(v), 1)$:
  $$\phi(L)(1 - L)^{d(v)} \varepsilon_t^2 = \omega + [1 - \beta(L)] \nu_t, \quad d(v) = 0.01$$
* $d(m) = 0.268$ confirms significant long memory in the normalized VVIX, capturing persistent volatility clusters following major structural shocks (e.g., March 2020 COVID crash, 2022 Federal Reserve tightening).

### C. Axiomatic Performance & Risk-Reward Ratios for Tail Uncertainty
Every rigorous performance metric should satisfy four fundamental axioms (Cheridito & Kromer 2013, Artzner et al. 1999):
1. **Monotonicity (M)**: $\alpha(X) \ge \alpha(Y)$ when $X \ge Y$.
2. **Quasi-concavity (Q)**: $\alpha(\lambda X + (1-\lambda)Y) \ge \min(\alpha(X), \alpha(Y))$ (rewards diversification, penalizes risk concentration).
3. **Scale Invariance (S)**.
4. **Distribution-based (D)**.

The paper isolates uncertainty shocks through two tail-risk ratios computed over model innovations:
1. **Rachev Ratio (RR)**:
   $$RR_{(\beta, \gamma)}(X) = \frac{AVaR_\beta(-X)}{AVaR_\gamma(X)}$$
   * Compares the expected gain in the best $\beta\%$ right tail to the expected loss in the worst $\gamma\%$ left tail ($AVaR$ = Average Value-at-Risk / Expected Shortfall).
   * **Behavior**: Spikes dramatically during severe market liquidations because it isolates extreme left-tail losses. (Note: satisfies M, S, D, but fails Q due to non-concave numerator).
2. **Stable Tail Adjusted Return Ratio (STAR Ratio)**:
   $$STARR_\gamma(X) = \frac{\mathbb{E}[X]^+}{AVaR_\gamma(X)^+}$$
   * **Behavior**: Fully satisfies all four axioms (M, Q, S, D). Plummets sharply during market stress, reflecting the severe breakdown of return-to-downside-risk trade-offs.

---

## 3. Critical Findings for Quantitative Trading

### 1. Uncertainty Shocks are i.i.d. (Efficient Market Hypothesis in Volatility)
* When 10,000 NIG scenarios were simulated on ARFIMA-FIGARCH innovations, the extracted Rachev and STAR performance ratios exhibited **no discernible or systematic patterns**.
* **Microstructure Meaning**: Uncertainty shocks themselves are genuine unexpected white noise innovations. You **cannot predict the direction of a macro shock or volatility burst** once it occurs. What is persistent is the **volatility clustering (the hyperbolic memory of the regime)**, not the directional path.
* This reinforces our finding in `HYP-021`: attempting to predict or fade macroeconomic release spikes (CPI/PPI) fails because the shock innovation is directional and unforecastable.

### 2. Failure of Standard Deviation & Sharpe for Prop Account Risk
* Traditional VIX and standard deviation understate tail risk during crises (e.g., March 2020 and early 2022).
* For prop accounts (e.g., Apex $2,000 trailing drawdown), Gaussian metrics like standard Sharpe ratio are dangerously misleading because they treat upside volatility as risk and ignore tail skewness.
* **Expected Shortfall ($AVaR$) and the STARR Ratio** are mathematically superior metrics for assessing whether a strategy's loss distribution can survive a trailing drawdown limit.
