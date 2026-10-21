# Quantitative Research Papers & Institutional Literature Library

This directory contains research papers, patents, and analytical digests that inform our strategy development, risk models, microstructure insights, and quantitative rules (`tasks/PERMANENT_STRATEGY_RULES.md` and `tasks/MARKET_TRUTHS_AND_MICROSTRUCTURE.md`).

---

## Paper Index

| ID | Title / Topic | Authors / Source | Key Focus | Document Link |
|---|---|---|---|---|
| **P-01** | **SignalLab: Can AI Do Financial Research?** | S. Liu et al. (Columbia / Chicago / NYU, 2026) | Observable search denominator ($N$), multiple testing penalty (Bonferroni / Harvey-Liu), untouched holdout protocol, dynamic $t$-hurdles ($t \ge 2.5 \to 3.5$). | [PDF: 2026_09_Liu_SignalLab](file:///c:/Users/dmoto/jesse-bot/tasks/papers/2026_09_Liu_SignalLab_Can_AI_Do_Financial_Research.pdf) |
| **P-02** | **CME Optimistic Messaging Protocol** | CME Group Patent (US20180183901A1, 2018) | CME Globex order matching engine, optimistic execution messaging, FIFO with LMM queue priority, order book latency and cancel protocol. | [PDF: US20180183901A1](file:///c:/Users/dmoto/jesse-bot/tasks/papers/US20180183901A1_CME_Optimistic_Messaging_Protocol.pdf) |
| **P-03** | **Can LLM-based Investing Outperform the Market in Long Run? (FINSABER)** | W. Li, H. Kim, M. Cucuringu, T. Ma (KDD 2026 / arXiv:2505.07078) | 20-year unadjusted bias-mitigated benchmark. LLMs fail to generate alpha ($p > 0.34$). Regime miscalibration (timid in bull, disaster in bear). 60-day window collapse. Low-vol anomaly and momentum skip formulas. | [Digest: FINSABER](file:///c:/Users/dmoto/jesse-bot/tasks/papers/2026_KDD_Li_FINSABER_LLM_Investors.md) |
| **P-04** | **Beyond the Traditional VIX: Uncertainty Shocks & Tail Risk** | A. Jha, A. Shirvani, S. T. Rachev, F. J. Fabozzi (J. Risk & Fin. Mgmt, 2025) | Double-subordinated NDIG Lévy process, ARFIMA-FIGARCH long memory ($d=0.268$), axiomatic risk-reward ratios (Rachev Ratio, STARR Ratio), proof that volatility shocks are i.i.d. noise while variance clusters persistently. | [Digest: Beyond VIX](file:///c:/Users/dmoto/jesse-bot/tasks/papers/2025_JRFM_Jha_Beyond_Traditional_VIX.md) |

---

## How Each Paper Maps to Our Trading Governance

### 1. Rigorous Backtest Integrity & Search Multiplicity
* **P-01 (SignalLab)** $\to$ Directly shaped **Rules 7, 8, 9, 10, 11** in `PERMANENT_STRATEGY_RULES.md` and seeded `tasks/SEARCH_DENOMINATOR_REGISTRY.csv`. Every tested variation increments $N$, elevating the required $t$-statistic hurdle.
* **P-03 (FINSABER)** $\to$ Directly justifies **Rule 1 (Zero Window Truncation)** and **Rule 7 (In-Sample / OOS Gate)**: shows that extending a test period by merely 60 days flipped published strategy Sharpe ratios from $+1.44$ to $-1.25$.

### 2. Microstructure & Order Execution Realism
* **P-02 (CME Optimistic Messaging)** $\to$ Informs our execution friction models ($17.25 round-turn + 1 tick slippage) and Globex auction queue dynamics on strategies like `SundayReopenPush` (`HYP-018`) and `Expiration Open Short` (`HYP-006`).

### 3. Risk Sizing & Tail-Drawdown Protection (Apex Survival)
* **P-04 (Beyond VIX / Rachev & Fabozzi)** $\to$ Informs our tail-risk metrics. For Apex prop accounts ($2,000 trailing limit), standard deviation and Gaussian Sharpe ratio are dangerous because they penalize upside volatility and hide fat tails. The **STARR Ratio** ($\mathbb{E}[R] / AVaR_\gamma$) directly evaluates return per unit of Expected Shortfall.
* **P-03 & P-04** $\to$ Prove that uncertainty shocks are unforecastable white noise innovations, while volatility regimes have long memory ($d = 0.268$ ARFIMA-FIGARCH). Intraday strategies must use deterministic structural rules rather than attempting to predict or fade unforecastable macro spikes.
