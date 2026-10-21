# Market Truths & Quantitative Microstructure Knowledge Base

A cumulative, evidence-based repository of structural market mechanics, microstructure realities, and empirical findings discovered through quantitative strategy development, academic research (e.g., SignalLab / Liu et al., 2026), and historical backtesting across CME futures (NQ, ES, YM, CL, GC, ZN).

This document serves as our institutional memory. **Consult this before proposing or developing any new strategy to prevent repeating failed leads and to build exclusively upon verified market behavior.**

---

## 1. Macro Releases & Economic Shock Microstructure

### A. Inflation Data (CPI / PPI) vs. Labor Surveys (NFP)
* **CPI / PPI Prints Fundamentally Trend (Never Fade)**:
  > *“CPI prints do not mean-revert—they trigger aggressive, one-way trending liquidations or short squeezes that run right through the open. Fading CPI is stepping in front of a sovereign freight train.”*
  * **Empirical Proof (`HYP-021`)**: Testing an 07:30 CT macro release fade on midweek inflation prints (CPI/PPI/GDP) produced a deeply negative In-Sample result (**-$943.3 pts, $t = -1.57$**, PF 0.57).
  * **Microstructure Driver**: CPI directly alters Federal Reserve monetary policy, terminal interest rates, and the 10-year Treasury yield. When CPI deviates from consensus, institutional desks and multi-asset funds must mechanically recalculate the net present value (NPV) of all technology cash flows. This triggers persistent, one-way institutional re-pricing that trends directly through the cash open.
* **Labor Data (NFP) Mean-Reverts (Fading is Viable)**:
  * **Empirical Proof (`NFP Fade` — Task 08)**: Fading the 07:30 CT spike on the first Friday of the month is profitable across 2018–2026 (**+$2,326 pts / +$46,521 net, $t = 2.35$, PF 1.75**).
  * **Microstructure Driver**: Non-Farm Payrolls is backward-looking survey data. HFT keyword bots cause an initial emotional knee-jerk in a thin pre-market book, but market makers recognize employment is a lagging indicator and fade the move back toward fair value before 09:00 CT.

### B. Energy Inventory Releases (EIA Crude Oil)
* **Post-EIA Releases in Crude Oil (CL) are Dead Money**:
  * **Empirical Proof (`HYP-014`)**: Fading the Wednesday 09:30 CT EIA crude inventory spike loses **-$65/trade ($t = -2.5$)**, while following the momentum generates only **+$11/trade**—which is completely destroyed by the **$27.25 round-turn friction model** (commission + 2 ticks slippage).
  * **The True CL Edge**: The only robust edge in Crude Oil is the **CL Sunday Up-Gap Fade** (**+$410/trade, $t = 1.9$**, 2 MCL deployed in live funded plan), which exploits weekend physical commercial inventory mismatches, not intraday DOE/EIA reports.

---

## 2. Session Clocks, Order Books & Intraday Liquidity Windows

### A. The 08:30 to 10:00 CT "Morning Meat Grinder" (NQ)
* **Why Early Cash Breakouts Fail**:
  * Between 08:30 and 10:00 CT (09:30–11:00 ET), the market undergoes initial price discovery, 09:00/10:00 ET economic data releases, and European morning cash close positioning (10:30 CT). 
  * Trend breakouts attempted during this first 90 minutes suffer frequent false breakouts, violent whipsaws, and stop-runs.
* **The 10:00 CT Institutional Takeover Window (`Vault Break`)**:
  * At 10:00 CT (11:00 ET), European morning desks close, liquidity consolidates, and institutional execution algorithms take control of the tape for the afternoon trend.
  * **Empirical Proof (`Vault Break` — Task 02)**: Entering breakouts strictly between **10:00 CT and 14:30 CT** using an ATR volatility barrier ($+0.30 \times \text{ATR}$) and midnight VWAP confirmation delivers **+9,621 points, 66.0% win rate, and 9 out of 9 positive years** (Sharpe 1.76).

### B. The Sunday Reopen 60-Second Liquidity Vacuum (`SundayReopenPush`)
* **The 60-Second Reopen Window**:
  * **Empirical Proof (`HYP-018` / Watchlist #22)**: CME Globex reopens Sunday at 17:00 CT (18:00 ET) after 48 hours of accumulated weekend headlines. Entering in the gap direction at 17:00:00 CT and exiting at 17:01:00 CT delivers **+$29,839 net (PF 2.12, $t = 2.44, 4/4 positive holdout years)** on NQ, and **+$15,060 net ($t = 2.66$)** on YM.
  * **Slippage Resilience**: Highly robust—even under **4 ticks of adverse entry slippage** ($39.50 round-turn cost), it retains +$27,334 net and PF 1.99.
* **The Latency Trap (The 1-Minute Rule)**:
  * Entering just 1 minute late (17:01:00 to 17:02:00 CT) turns net negative (**-$2,260 net, $t = -0.52$**). The entire edge exists in the initial clearing burst of the accumulated order backlog through a thin book.

### C. The "Overnight Mirage" and Mandatory Intraday Flattening (15:55 CT)
* **Unhedged Overnight Drift is NOT Alpha**:
  * **Empirical Proof (`NQBreakoutATR` Audit — Rule 3)**: A strategy that appears profitable on paper but keeps positions overnight is almost always riding passive overnight equity appreciation. When flattened by 15:55 CT, the "edge" collapses into losses.
  * **Mandate**: An intraday strategy must prove positive expectancy on **same-day cash trades alone**.
  * **The 14:30 / 15:00 CT Cutoff**: Flattening before 15:00 CT avoids the chaotic 15:00–16:00 CT settlement auctions, MOC imbalances, and zero-day options (0DTE) gamma storms.

---

## 3. Shorting Equity Indices & Regime Decoupling

### A. The Structural Upward Drift & Unhedged Short Trap
* **The Asymmetry of Index Futures**:
  * The Nasdaq-100 and S&P 500 have an intrinsic upward drift driven by corporate share repurchases, dividend reinvestment, and passive 401(k) inflows.
  * Mirroring a successful long strategy into an unhedged short strategy **always fails**. Unhedged downside breakouts (`Vault Break Short Pure` — `HYP-019`) produced $t = 0.34$ and -$1,243 points in holdout. Dip-buyers consistently absorb intraday breakdowns.

### B. The 2023 Mega-Cap AI Decoupling Regime
* **Broad Market (ES) Downside Alignment Does NOT Protect NQ Shorts**:
  * **Empirical Proof (`Vault Break Short Aligned` — `HYP-020`)**: In 2018–2022, tech moved with broad-market S&P 500 sentiment ($t = 3.11$, +$76,080). But on the 2023–2026 holdout, it suffered a catastrophic **-$1,826.0 point loss (-$36,520, $t = -2.97$) in 2023 alone**.
  * **Microstructure Driver**: In 2023, mega-cap tech (NVDA, MSFT, AAPL, AMZN) decoupled from the broader economy. Institutional algorithms used morning weakness in ES as liquidity pools to aggressively buy NQ dips, turning downside breakouts into devastating short-squeeze traps.

---

## 4. Institutional Calendar & Flow Anomalies

### A. Monthly OPEX Dealer Unwind (`Expiration Open Short` — EOS)
* **Monthly 3rd Friday Delta-Hedging Unwind**:
  * **Empirical Proof (`EOS` — Task 06)**: Shorting the 08:30 CT open on monthly options-expiration Fridays (out at 10:00 CT) achieves **$t = 3.10$ In-Sample and $t = 2.70$ Holdout**.
  * **Microstructure Driver**: Options market makers unwinding long delta hedges against expiring call open interest create persistent, predictable selling pressure during the first 90 minutes of trading.

### B. Weekly Institutional Positioning (`Monday Long`)
* **Post-Weekend Capital Deployment**:
  * **Empirical Proof (`Monday Long` — Task 05)**: Buying at the 08:30 CT cash open on regular Mondays (0.50x ATR stop, 15:00 CT exit) is profitable across both bull and bear regimes (**2018–2022 $t = 2.80$, 2023–2026 $t = 2.50$**).
  * **Microstructure Driver**: Systematic re-allocation and risk-on capital deployment following the clearance of weekend geopolitical uncertainty.

### C. Turn-of-Month (TOM) — The "Bull Market Beta Mirage"
* **Turn-of-Month Inflows are NOT All-Weather Alpha**:
  * **Empirical Proof (`TurnOfMonthLong` — `HYP-022`)**: Buying the 08:30 CT open on Trading Days 1–3 exploded in the 2023–2026 bull market (+45.66 pts/trade, +$120k net), but made **zero money in 2018–2022 ($t = 0.23$, PF 1.05)**.
  * **Microstructure Driver**: Turn-of-month cash deployment only works when the broader market is already in a raging secular bull market. In chop, corrections, or bear regimes, blind monthly buying is pure random noise. It is an unhedged beta trade, not a market anomaly.

---

## 5. Cross-Asset & Spread Inefficiencies

### A. Gold Asian Breakouts (`GoldAsianBreakout`)
* **Session Breakouts on COMEX Gold Fail In-Sample**:
  * **Empirical Proof (`HYP-015`)**: A breakout of the Asian session high/low into London on Gold (GC) failed the in-sample gate (**$t = 0.74$, PF 1.09, 3 out of 5 years negative**).
  * **Microstructure Driver**: Gold is driven by real interest rates, dollar debasement, and central bank reserve purchases. Its recent full-period profitability was an artifact of the 2024–2026 macroeconomic bull market ($1,800 to $4,100), not an intraday Asian range breakout.

### B. Cross-Index Spread Lead-Lag (`NQESCrossFlow`)
* **Cross-Index Momentum Decays Rapidly**:
  * **Empirical Proof (`HYP-016`)**: Trading NQ/ES relative momentum lead-lag decayed from $t = 1.90$ down to **$t = 0.20$ on holdout**, degrading total portfolio Sharpe from 1.37 to 1.22 and adding $16,000 in drawdown.
  * **Microstructure Driver**: Modern HFT co-located cross-arbitrage algorithms have eliminated mechanical lead-lag latency between CME equity index futures.

---

## 6. The Quantitative Research Method (SignalLab Standards)

### A. The 20-Coin Lottery Trap (The Search Denominator)
* **The Multiplicity Problem**: If a researcher tests 20 variations before finding one that hits $t = 2.0$, that result has a **~64% probability of being pure random noise**.
* **Dynamic Significance Hurdles**:
  * $N = 1$ (Pre-registered single test): $t \ge 2.50$ ($p \le 0.01$).
  * $N \ge 10$ (Variant sweeps): $t \ge 3.00$ (Harvey Minimum Bayes Factor).
  * $N \ge 100$ (Data mining): $t \ge 3.50$ (Harvey–Liu Bootstrap / Bonferroni).

### B. The Untouched Holdout Reset ($N = 1$)
* An in-sample $t$-statistic measures how well you mined historical noise.
* Freezing a completely untouched out-of-sample period (2023–2026) resets $N = 1$. If performance decays, turns negative, or blows an account during holdout, the idea is immediately classified as **Rank F**.

### C. Portfolio Spanning & Funded Account Realism
* A new strategy is **never evaluated in isolation**. It must undergo a portfolio spanning test against our active live strategies (`Vault Break`, `Overnight Bias`, `Relative Strength`, `Late-Day Flow`, `EOS`, `Monday Long`, `CL Gap Fade`).
* If adding the strategy increases peak-to-valley drawdown on the 1,000-iteration bootstrapped funded simulator without accelerating payouts, it is shelved on the Watchlist.

### D. Minute-Level Trade Auditability by Default
* All strategy backtests and evaluations must output `trades.csv` with exact minute-level timestamps (`entry_time`, `exit_time`), fill prices, and net P&L. Claims must be verifiable by independent models and auditors (Claude / MultiCharts) in minutes.
