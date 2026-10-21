# Paper Digest: Can LLM-based Financial Investing Strategies Outperform the Market in Long Run? (FINSABER)

**Authors**: Weixian Waylon Li, Hyeonjun Kim, Mihai Cucuringu, Tiejun Ma  
**Publication**: Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD ’26), August 2026  
**arXiv Reference**: [arXiv:2505.07078v6 [q-fin.TR]](https://arxiv.org/abs/2505.07078)  
**Code & Data**: [https://github.com/waylonli/FINSABER](https://github.com/waylonli/FINSABER)

---

## 1. Executive Summary & Problem Formulation

Recent financial literature has proposed LLM-driven autonomous trading agents (e.g., FinMem, FinAgent, FinRobot, TradExpert, FinCon, TradingAgents, MarketSenseAI 2.0). These studies routinely report extraordinary performance metrics (Sharpe ratios > 2.0, annualized returns > 60%). 

However, this paper demonstrates that almost all prior claims are **methodological artifacts driven by three severe biases**:
1. **Survivorship & Pre-inclusion Bias**: Evaluations were conducted solely on recent mega-cap tech winners (TSLA, AMZN, NFLX, MSFT) that rode an historic 15-year secular bull market, omitting delisted or bankrupt assets (Garcia & Gould 1993, Elton et al. 1996).
2. **Look-Ahead Bias**: Parameters, features, and symbols were hand-picked based on full-period performance.
3. **Data-Snooping / Multiple-Testing Bias**: Evaluations used short horizons (< 1 year, often 3–8 months) without adjusting for multiple hypothesis testing (Bailey, Borwein, López de Prado, Zhu 2015).

To resolve this, the authors built **FINSABER**, a bias-mitigated backtesting framework evaluating strategies over **20 years (2000–2024 / 2004–2024)** across **7,000+ US equities** and all historical S&P 500 constituents including delisted symbols.

---

## 2. Core Empirical Findings

### A. The 60-Day Evaluation Collapse
* When evaluated on the original cherry-picked period (Oct 2022 to Apr 2023), LLMs appeared profitable on TSLA.
* **Marginal Extension Disaster**: Extending the evaluation window by just **2 months** (to June 2023) completely destroyed published results:
  * **MSFT**: Cumulative return crashed from **+23.3% down to -22.0%**, and Sharpe ratio flipped from **+1.44 to -1.25**.
  * **NFLX**: Sharpe ratio collapsed from **+2.02 to -0.48**.
* Extending to the full 2004–2024 period, simple Buy-and-Hold and traditional rule-based strategies outperformed LLM investors across virtually all symbols.

### B. Composite Bias-Mitigated Benchmarking (Table 4 & 5)
Under rolling-window evaluations on historical constituent lists (including delisted assets) across Random, Momentum, and Volatility selections:
* **Market Baseline Outperformance**: Passive Buy-and-Hold statistically significantly outperforms both FinMem and FinAgent across all setups ($p = 3.0 \times 10^{-6}$ to $4.0 \times 10^{-5}$).
* **Zero Statistically Significant Alpha**: In CAPM factor regressions ($\alpha$ and $\beta$), neither FinMem nor FinAgent generated statistically significant alpha (**all $\alpha$ $p$-values $> 0.34$**). FinMem generated persistent negative alpha ($-1.04\%$ to $-1.34\%$).
* **Friction & Overtrading**: FinMem exhibited a pathological trading profile with commission ratios 5x to 9x higher than FinAgent, destroying capital through transaction churn.

### C. The Regime Miscalibration Axiom (Section 7 & Figure 2)
Decomposing performance across Bull ($\ge +20\%$), Bear ($\le -20\%$), and Sideways markets revealed that unconstrained AI agents are **inversely calibrated to market regimes**:
* **Bull Markets (Timid)**: Agents take low market beta ($\beta \approx 0.20 - 0.50$), sit in cash, or exit prematurely. FinAgent achieved Sharpe 0.12 and FinMem -0.19, failing to capture passive equity beta (B&H Sharpe 0.61).
* **Bear Markets (Pro-Cyclical Catastrophe)**: Agents fail to hedge and make aggressive, pro-cyclical decisions that amplify liquidations. In 2008, FinMem suffered a **-75% drawdown on John Deere (DE)** vs -50% for SPX, recording a bear Sharpe of **-0.97** (FinAgent -0.38).
* **Sideways Markets**: Overtrading destroys equity. Classical models (ARIMA Sharpe 0.34, ATR Band Sharpe 0.16) outperform LLMs.

### D. Model Scaling Law Failure in Finance
* NLP scaling laws (Kaplan et al. 2020) do not translate to financial markets due to low signal-to-noise ratio.
* Frontier models (GPT-4o) do not reliably beat smaller models (GPT-4o-mini), and both are consistently beaten by simpler classical models (ARIMA, ATR Band, Trend Following). Without explicit financial logic, architectural complexity simply fits noise.

---

## 3. Actionable Quantitative Formulas

The paper validates three robust selection and risk filtering mechanics:

### 1. Momentum Factor with 1-Month Skip Window (Carhart 1997 / Jegadeesh & Titman 1993)
$$\text{Momentum Score}_t = \frac{\text{Price}_{t - 21}}{\text{Price}_{t - 100}} - 1$$
* **Mechanism**: Skipping the immediate 21 trading days (1 month) removes the contaminating 1-month short-term reversal anomaly. Pure intermediate momentum resides in the $t-100 \to t-21$ interval.

### 2. Low-Volatility Anomaly via Weekly Log Return Smoothing (Blitz & Vliet 2007)
$$\sigma = \text{std}\left(\ln\left(\frac{P_t}{P_{t-5}}\right)\right) \quad \text{over 21 trading days}$$
* **Mechanism**: Using weekly log returns rather than daily returns filters microstructure bounce and bid-ask spread noise. Selecting low-volatility assets cut maximum drawdown by more than half (**-14.1% vs -35.1%**) and doubled baseline Sharpe (**0.703 vs 0.315**).

### 3. Correlation-Discounted Portfolio Construction (FinCon Metric)
$$\text{Selection Score}_i = \text{Sharpe}_i \times (1 - \bar{\rho}_i)$$
where $\bar{\rho}_i$ is candidate $i$'s average pairwise correlation to the active universe.
* **Diversification Gate**: If internal correlation of the candidate portfolio exceeds $0.70$, discard the initial set and apply a greedy correlation-minimizing fallback.

---

## 4. Application to our Futures Strategy Portfolio

1. **Vindication of Rule 1 & Rule 7**: Validates our mandatory 2018–2026 zero-truncation rule and chronological In-Sample vs Out-of-Sample split. Strategies that look great over 6 months collapse when tested over years.
2. **Explicit Structural Rules over Black-Box ML**: Explains why unconstrained LLM/ML models fail in prop environments—they are timid in bull moves and blow up in bear liquidations. Intraday strategies must use explicit structural triggers (`Vault Break` VWAP/ATR barrier, `Overnight Bias` range positioning, `Monday Long` weekly flow).
3. **Friction-Adjusted Hurdle**: Confirms that high turnover without strict edge leads to capital destruction via commissions.
