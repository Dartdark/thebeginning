# Book Summary: Building Winning Trading Systems with TradeStation (George Pruitt & John R. Hill, 2003)

**Title**: *Building Winning Trading Systems with TradeStation*  
**Authors**: George Pruitt and John R. Hill (Futures Truth Company)  
**Publisher**: John Wiley & Sons, Inc., 2003 (ISBN: 0-471-21569-4)  
**Short Name**: `pruitt_tradestation`

---

## 1. What the Book Is About

George Pruitt and John R. Hill’s *Building Winning Trading Systems with TradeStation* is a practitioner's masterclass in quantitative strategy design, EasyLanguage programming, backtesting integrity, and system evaluation. As the founders and operators of *Futures Truth Company*—the trading industry's foremost independent auditor of commercial trading systems—Pruitt and Hill evaluated thousands of vendor models over decades, observing firsthand why most systems collapse in real-time trading while a select few consistently generate wealth.

The book is structured into four primary sections:
1. **EasyLanguage Programming Foundations (Chapters 1–4, 7)**: Syntax, data types, modular program architecture (program headers, calculation modules, order placement modules), conditional logic, looping, custom indicators, ShowMe/PaintBar studies, custom functions (such as the Choppy Market Index), and debugging techniques utilizing TradeStation's Print Log.
2. **System Evaluation & Optimization Hygiene (Chapter 5)**: Interpreting TradeStation performance summaries (total net profit, profit factor, adjusted profit factor, outlier analysis, RINA Index), understanding favorable and adverse trade excursions, 3D parameter surface mapping (identifying broad plateaus vs. fragile peaks), and walk-forward out-of-sample verification.
3. **Turnkey Trading Strategies (Chapter 6)**: Complete, unoptimized, multi-market systems with exact EasyLanguage code, pseudocode, and 20-year performance track records: King Keltner, Bollinger Bandit, Thermostat, Dynamic Break Out II, Super Combo Day Trading, Ghost Trader, and Money Manager.
4. **Advanced Research & Developer Wisdom (Chapters 8–11)**: Researching Commitment of Traders (COT) reports, day-of-week and time-of-day execution delays, pattern recognition via finite state machines, intermarket bond-stock relationships, percent change charts, options basics, and in-depth interviews with 16 legendary system developers (including Welles Wilder, John Clayburg, Keith Fitschen, Mike Barna, John Ehlers, Chuck LeBeau, and Larry Williams).

---

## 2. Main Claims and Theoretical Foundations

1. **The Curse of Over-Optimization (Curve Fitting)**:
   The single greatest cause of trading system failure is curve fitting—customizing parameters until historical results look flawless. In their audit of commercial systems, Pruitt and Hill found that vendors routinely optimize dozens of parameters on past data, producing beautiful historical equity curves that immediately suffer catastrophic drawdowns in live execution. True system design requires simple rules, minimal parameters, and testing on raw, unadjusted out-of-sample data.
2. **3D Parameter Plateaus vs. Fragile Peaks**:
   When optimizing parameters, developers must examine the topology of the parameter space using 3D surface contour plots (with parameters on the X/Y axes and Return on Account or Profit Factor on the Z axis). Parameters that produce isolated, sharp "mountain peaks" are overfit to historical noise; the slightest shift in market behavior will cause performance to plummet into a valley. Robust parameters reside on broad, elevated "plateaus," where neighboring parameter values generate stable, consistent profits.
3. **Intraday Data Resolution & The Daily Bar Illusion**:
   Backtesting daily bars creates a dangerous chronological ambiguity: the software cannot determine whether the High or Low occurred first. Consequently, a daily backtest may erroneously record a massive winning trade when, in reality, price hit the stop-loss before reaching the profit target. Accurate backtesting requires high-resolution intraday bars (such as 5-minute bars) and TradeStation's "bouncing ticks" feature to accurately simulate real-time order fills.
4. **Trend Following Dominance and the Diversification Imperative**:
   The overwhelming majority of long-term profitable futures systems are trend-following breakout models (e.g. King Keltner, Bollinger Bandit, Donchian channels). Because trend systems typically produce low win rates (30%–40%) and extended drawdowns, survival requires trading a broadly diversified portfolio of non-correlated markets (currencies, energies, grains, metals, financials) with identical, unoptimized parameter sets.
5. **Session Order Flow Dynamics in Day Trading**:
   Stock index day trading requires respecting distinct session liquidity phases:
   - *Opening 30–60 Minutes*: Dominated by emotional retail order imbalances and news digestion; empirical testing proves that delaying entry until 10:00–10:30 CT cuts adverse excursions by over 25% and maximizes net profit.
   - *Middle of the Day*: Energy expansion following small-range compression days provides reliable breakout continuation or failed-breakout squeeze reversals.
   - *Last 30–45 Minutes (After 14:30 CT)*: Prone to institutional profit-taking and trend retracements; day trades must be protected with trailing stops and flattened at the session close (`SetExitOnClose`).

---

## 3. General Advice vs. Trading Rules

Pruitt and Hill strictly separate actionable trading strategies (detailed in `ideas.md`) from overarching system engineering, risk architecture, and operational discipline:

### A. Backtesting Hygiene and Walk-Forward Validation (Chapter 5)
- **Out-of-Sample Walk-Forward Testing**:
  Historical databases should be split in half: the first half is used for development and parameter scanning, while the second half serves as a pristine out-of-sample walk-forward test. If a strategy cannot perform on untouched out-of-sample data, it must be discarded immediately.
- **Outlier Elimination & Adjusted Profit Factor**:
  System developers must not rely on unadjusted net profit. A strategy's track record can be heavily distorted by a single massive outlier trade. TradeStation's *Adjusted Profit Factor* deflates gross profits and inflates gross losses by the square root of trades, providing a conservative, worst-case view of true expectancy.
- **Rule Symmetry**:
  Long and short rules should be as symmetric as possible (buy rules mirror short rules). Tuning different parameters for long and short trades simply fits historical market regime bias (such as multi-year equity bull runs) and guarantees failure when the regime flips.

### B. Capital Adequacy and Drawdown Reality (Chapter 5)
- **The $2\times$ to $3\times$ Drawdown Rule**:
  TradeStation reports the "Account Size Required" as equal to the historical maximum drawdown. Pruitt and Hill reject this as dangerously inadequate. The golden industry rule of thumb requires funding an account with **two to three times the historical maximum drawdown** plus exchange margin. A system tested over many years is virtually guaranteed to exceed its past maximum drawdown in future live trading.

### C. Trade Management and Execution Hygiene (Chapters 4, 6 & 7)
- **Time Stops and Stagnation Cuts**:
  Strategies should incorporate time-based liquidation rules (such as exiting after 5 unprofitable bars or 3–4 bars without momentum). Trades that fail to show immediate follow-through tie up capital and increase downside tail risk.
- **Normalized Volatility Position Sizing**:
  Position sizes should never be fixed in contracts. Sizing must be scaled inversely to rolling market volatility ($\text{StdDev}(Close, 30) \times \text{BigPointValue}$), ensuring equal risk allocation across diverse instruments.
- **Developer Consensus (Chapter 11)**:
  Interviews with 16 industry legends highlight universal tenets: trading mechanical systems removes emotional paralysis; drawdowns are an inevitable cost of doing business; and simplicity and discipline consistently outperform complex curve-fitted black boxes.
