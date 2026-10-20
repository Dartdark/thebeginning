# NQ Breakout ATR Building Blocks Optimization Report

## 1. Executive Summary & Objective

- **Objective**: Construct, backtest, and optimize a modular trading system from discrete building blocks on CME Nasdaq-100 index futures (`NQ-USD`).
- **Core Architecture**:
  - **Entry Module**: Entry 10 (Resting Stop Breakout — 10-bar Highest High / Lowest Low breakout).
  - **Hard Risk Exit**: Exit 8 (Dynamic ATR Volatility Stop Loss — 2x ATR(14)).
  - **Profit Protection Exit**: Exit 4 (Trailing Giveback Lock from Peak — 40 NQ points).
  - **Regime Filter**: Modular switch slot testing filters from `tasks/STRATEGY_FILTERS_CATALOG.md`.
- **Market & Data**: `NQ-USD` on `Custom Data`, 15-minute timeframe.
- **In-Sample Period**: `2021-01-01` to `2022-12-31` (2 full calendar years).

---

## 2. Iteration Log & Performance Evolution

### Iteration 0: Raw Naked Baseline (filter_case = 0)
- **Session ID**: `87458b6a-c916-41e1-bf85-59f35ca9bb50`
- **Dashboard URL**: http://localhost:9000/#/backtest/87458b6a-c916-41e1-bf85-59f35ca9bb50
- **Configuration**: Entry 10 (10-bar Donchian breakout) + Exit 8 (2.0x ATR Stop) + Exit 4 (40-pt Trailing Giveback). No regime filters.
- **Key Metrics**:
  - Total Trades: 2,289 (1,140 Longs / 1,149 Shorts)
  - Win Rate: 34.3% (Longs 34.0% / Shorts 34.6%)
  - **Ratio Avg Win / Loss**: **2.01** ($379.83 avg win vs. $188.74 avg loss)
  - Net Profit: **+$13,919.83**
  - Expectancy: $6.09 per trade
  - Sharpe Ratio: **0.59**
  - Sortino Ratio: **0.88**
  - Calmar Ratio: **0.80**
  - Max Drawdown: **−0.87%** (~$8,738)
  - Max Losing Streak: 18 trades
  - Largest Losing Trade: −$2,140.00
  - Largest Winning Trade: +$2,686.25
- **Conclusion**: The raw building blocks possess a genuine positive expectancy right out of the box (2.01:1 win/loss ratio, positive net profit across both long and short sides). However, executing 2,289 trades (~3.15 trades/day) causes heavy over-trading and whipsaws during low-volatility/chop regimes, resulting in an 18-trade losing streak and large single-trade drawdown hits.

---

### Iteration 1: Trend Strength Regime Filter (filter_case = 91, ADX > 30)
- **Session ID**: `60632385-6903-4840-bbfe-f9fca9912dd7`
- **Dashboard URL**: http://localhost:9000/#/backtest/60632385-6903-4840-bbfe-f9fca9912dd7
- **What Changed**: Activated **Filter Case 91** from `tasks/STRATEGY_FILTERS_CATALOG.md` (`ADX(15) > 30`). Entries are strictly blocked during dead or choppy conditions and only allowed when trend strength is high.
- **Key Metrics**:
  - Total Trades: **881** (410 Longs / 471 Shorts) — *61% reduction in over-trading*
  - Win Rate: **34.9%** (Longs 33.8% / Shorts 35.7%)
  - **Ratio Avg Win / Loss**: **2.09** ($384.04 avg win vs. $184.04 avg loss)
  - Net Profit: **+$12,242.60**
  - Expectancy: **$13.94 per trade** — *more than doubled (+129%)*
  - Sharpe Ratio: **0.88** — *jumped from 0.59 (+49%)*
  - Sortino Ratio: **1.60** — *nearly doubled from 0.88 (+82%)*
  - Calmar Ratio: **1.02** — *rose from 0.80 (+28%)*
  - Max Drawdown: **−0.60%** — *reduced by 31%*
  - Max Losing Streak: **11 trades** — *down from 18 trades*
  - Largest Losing Trade: **−$651.05** — *slashed by 70% from −$2,140*
  - Largest Winning Trade: +$2,152.50
- **Conclusion**: Exceptional improvement across all risk-adjusted dimensions. By filtering out low-ADX chop, the strategy eliminated 1,408 junk trades, more than doubled average trade expectancy ($6.09 $\rightarrow$ $13.94), reduced drawdowns by nearly a third, and capped the worst-case single-trade loss at −$651.

---

## 3. Comparison Matrix

| Metric | Iteration 0 (Naked Baseline) | Iteration 1 (ADX > 30 Filter) | Delta / Improvement |
| :--- | :--- | :--- | :--- |
| **Session ID** | `87458b6a-c916...` | `60632385-6903...` | — |
| **Dashboard** | [View Iteration 0](http://localhost:9000/#/backtest/87458b6a-c916-41e1-bf85-59f35ca9bb50) | [View Iteration 1](http://localhost:9000/#/backtest/60632385-6903-4840-bbfe-f9fca9912dd7) | — |
| **Total Trades** | 2,289 | 881 | −61.5% (Eliminated 1,408 chop trades) |
| **Win Rate** | 34.3% | 34.9% | +0.6% |
| **Avg Win / Avg Loss**| 2.01 ($380 / $189) | 2.09 ($384 / $184) | +4.0% |
| **Expectancy / Trade**| $6.09 | $13.94 | **+128.9% (More than doubled)** |
| **Sharpe Ratio** | 0.59 | **0.88** | **+49.2%** |
| **Sortino Ratio** | 0.88 | **1.60** | **+81.8%** |
| **Calmar Ratio** | 0.80 | **1.02** | **+27.5%** |
| **Max Drawdown** | −0.87% | **−0.60%** | **−31.0% (Risk reduced)** |
| **Max Losing Streak**| 18 | **11** | **−38.9% (Faster recovery)** |
| **Worst Single Loss** | −$2,140.00 | **−$651.05** | **−69.6% (Tail risk controlled)** |

---

## 4. Final Selected Variant & Next Steps

- **Selected Foundation**: `NQBreakoutATR` with **Filter Case 91 (ADX > 30)**.
- **Next Candidate Optimization Iterations**:
  1. **Time Window Filter**: Test Case 28 (Trade only during US Cash session $> 08:00$ CT) combined with ADX.
  2. **Trailing Giveback Sweep**: Sweep `giveback_points` between 30 and 60 NQ points.
  3. **Multi-Year Holdout Validation**: Extend backtest across full 2018–2026 data.
