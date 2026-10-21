# Optimization Report: Monday Long Opening Regime & Timing Optimization (HYP-028)

**Date**: 2026-10-21  
**Author**: Quantitative Strategy Team / Antigravity  
**Target Strategy**: `Monday Long` (`NQMondayLong` / Task 05)  
**Instrument**: CME E-mini Nasdaq-100 Futures (`NQ`) / Micro E-mini (`MNQ`)  
**Timeframe**: 5-Minute Bars (`fast_mode = False`, full 1m intrabar execution)  
**Evaluation Window**: In-Sample Design Window `2018-01-01` to `2022-12-31`  
**Institutional Friction Applied**: Full **$17.25 round-turn commission + 1 tick ($5.00) slippage per fill ($10.00 RT) = $27.25 per trade** (1.3625 NQ points)  
**Pre-Registered Plan**: `tasks/monday_long_opening_optimization_plan.md`  

---

## 1. Executive Summary & Acceptance Gate Verdict

- **Objective**: Test whether Time (15m/30m cash open digestion) and Price (opening green bar confirmation) filters can slash `NQMondayLong`'s severe historical peak-to-valley drawdown ($22,805.00) without repeating Phase 2's failure mode (where waiting 60 minutes surrendered the 2023–2026 tech bull market opening dip-buys).
- **Candidates Evaluated**: 4 pre-registered variants (`V1` to `V4`) backtested in Jesse across 5 years of 1m intrabar data.
- **Results**:
  - **V1 (`NQMonLongWait0845`)**: Degraded Net Profit by **-$11,454.67 (-30.5%)** and worsened Max Drawdown to **$26,161.92** (+14.7% worse).
  - **V2 (`NQMonLongWait0900`)**: Degraded Net Profit by **-$15,975.84 (-42.5%)** to $21,630.33 with Max Drawdown of **$22,057.25**.
  - **V3 (`NQMonLongGreen0835`)**: Produced strong risk-adjusted improvements (Win Rate jumped from 50.4% to **58.7%**, Expectancy jumped from $162.10 to **+$292.06/trade**, Sharpe jumped from 0.66 to **0.87**, and Max Drawdown dropped by **-$5,091.50 (-22.3%)** to **$17,713.50**). However, total Net Profit was **$36,799.83** vs Base's **$37,606.17** (-$806.34 lower), and its $t$-stat of **1.60** failed the strict pre-registered gate hurdle of $t \ge 2.50$ and higher Net Profit.
  - **V4 (`NQMonLongGreen0845`)**: Collapsed to **$619.42** net profit after friction.
- **Acceptance Gate Verdict**: **REJECT ALL VARIANTS / RETAIN BASELINE (`NQMondayLong`) UNDEFEATED**.
- **Holdout Discipline**: Because no variant cleared the pre-registered In-Sample gate ($t \ge 2.50$ and higher Net Profit), the 2023–2026 Out-of-Sample Holdout window was kept **strictly untouched** to protect out-of-sample data integrity.

---

## 2. In-Sample Performance Matrix (2018–2022, 5 Years 1m Precision)

All metrics computed under full institutional friction ($27.25 per round-turn trade, 1 NQ contract = $20/pt):

| Strategy Variant | Variant Description | Trades | Win Rate | Gross Profit | Net Profit ($27.25c) | Expectancy | Max Drawdown | NP / DD | Sharpe | Sortino | $t$-stat |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Base** (`NQMondayLong`) | Baseline: Blind 08:30 CT entry | 232 | 50.4% (117W/115L) | $43,928.17 | **$37,606.17** | $162.10 | $22,805.00 | 1.65 | 0.66 | 1.07 | 1.14 |
| **V1** (`NQMonLongWait0845`) | Wait 15m (08:45 CT close) | 232 | 52.6% (122W/110L) | $32,473.50 | **$26,151.50** | $112.72 | $26,161.92 | 1.00 | 0.50 | 0.77 | 0.81 |
| **V2** (`NQMonLongWait0900`) | Wait 30m (09:00 CT close) | 234 | 53.8% (126W/108L) | $28,006.83 | **$21,630.33** | $92.44 | $22,057.25 | 0.98 | 0.45 | 0.67 | 0.69 |
| **V3** (`NQMonLongGreen0835`)| 5m Cash Open Green Confirm | 126 | **58.7%** (74W/52L) | $40,233.33 | **$36,799.83** | **$292.06** | **$17,713.50** | **2.08** | **0.87** | **1.44** | 1.60 |
| **V4** (`NQMonLongGreen0845`)| 15m Cash Open Green Confirm | 131 | 52.7% (69W/62L) | $4,189.17 | **$619.42** | $4.73 | $20,848.08 | 0.03 | 0.09 | 0.13 | 0.03 |

---

## 3. Backtest Sessions & Dashboard Verification Links

- **Baseline (`NQMondayLong`)**:
  - Session ID: `7e5d7915-f2d1-44c5-973d-178eb8a2d0f6`
  - Dashboard: http://localhost:9000/#/backtest/7e5d7915-f2d1-44c5-973d-178eb8a2d0f6
- **Variant 1 (`NQMonLongWait0845`)**:
  - Session ID: `0ff3c410-6f8c-4d6d-97d8-0e2ac1453cc3`
  - Dashboard: http://localhost:9000/#/backtest/0ff3c410-6f8c-4d6d-97d8-0e2ac1453cc3
- **Variant 2 (`NQMonLongWait0900`)**:
  - Session ID: `4f74a2be-5598-4823-94aa-bbb39fd53e69`
  - Dashboard: http://localhost:9000/#/backtest/4f74a2be-5598-4823-94aa-bbb39fd53e69
- **Variant 3 (`NQMonLongGreen0835`)**:
  - Session ID: `4d4c1532-104b-424e-8b48-113428a8d046`
  - Dashboard: http://localhost:9000/#/backtest/4d4c1532-104b-424e-8b48-113428a8d046
- **Variant 4 (`NQMonLongGreen0845`)**:
  - Session ID: `e91b4941-15d9-4051-a4fd-2b1989709eba`
  - Dashboard: http://localhost:9000/#/backtest/e91b4941-15d9-4051-a4fd-2b1989709eba

---

## 4. Microstructure Findings & Economic Mechanisms

### A. The Cost of Pure Time Delays (V1 & V2)
Delaying the cash open entry by 15 or 30 minutes (08:45 or 09:00 CT) severely impairs performance:
1. **Giving up Opening Range Displacement**: On winning Monday trend days, institutional capital immediately rushes into index futures at the 08:30 CT cash open. Entering 15 to 30 minutes later buys at substantially higher prices, surrendering 15–30 points of favorable run-up.
2. **Failure to Reduce Drawdown**: Max Drawdown did not improve (Base: $22.8k vs V1: $26.2k vs V2: $22.1k). On days that turn into liquidation waterfalls, delaying 15–30 minutes still catches the waterfall as the market continues plunging into the 10:00 ET macro window.

### B. The 5-Minute Green Confirmation Asymmetry (V3)
Variant 3 (`NQMonLongGreen0835`) filters out 106 Mondays where the first 5 minutes of cash trading closed red (`Close < Open`):
1. **Capital Efficiency & Sharpe**: In 126 trades, V3 captures **$36,799.83** net profit—virtually identical to Base's **$37,606.17** across 232 trades. It achieves this with an **80% higher trade expectancy** ($292.06 vs $162.10), a **+8.3% higher win rate** (58.7% vs 50.4%), and a **-$5,091.50 (-22.3%) reduction in Max Drawdown** ($17,713.50 vs $22,805.00).
2. **The Dip-Buying Trade-off**: The 106 filtered red-open Mondays produced a combined net profit of only **+$806.34** ($7.60/trade after $27.25 friction) over 5 years, but contributed over $5,000 to the portfolio drawdown.
3. **Why V3 Was Rejected Under Strict Institutional Protocol**:
   - The pre-registered hurdle strictly mandated **higher Net Profit** ($36,799.83 is -$806.34 lower than $37,606.17) and **$t \ge 2.50$** ($t = 1.60$).
   - Crucially, Monday Long operates as a weekly macro bias strategy (~46 trades per year). In Phase 2, requiring opening price confirmation appeared superior in 2018–2022 but drastically underperformed on 2023–2026 Holdout ($107k vs $148k) because institutional dip-buying frequently starts after an initial morning flush.
   - Preserving unconditional entry protects the strategy from regime shifts where early red dips are aggressively squeezed.

---

## 5. Final Strategic Recommendation & Portfolio Allocation

- **Final Decision**: **Retain Baseline `NQMondayLong`**.
- **Portfolio Weight**: Deployed at **1 MNQ** in the funded trading plan.
- **Holdout Status**: Untouched (`Untouched`) to maintain strict SignalLab separation and prevent holdout overfitting.
