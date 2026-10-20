# Quantitative Strategy Report: NQIntradayMR (Intraday Mean Reversion)

## 1. Executive Summary & Objective

- **Strategy Name**: `NQIntradayMR`
- **Target Symbol**: CME E-mini / Micro Nasdaq-100 Index Futures (`NQ-USD` / `MNQ`)
- **Timeframe**: `15m`
- **Evaluation Window**: **2018-04-01 through 2026-10-09** (8.5 years continuous, zero window truncation)
- **Friction Model**: Realistic CME Futures Friction (`fee = 0.00003`, \$17.25 round-turn / NQ, \$1.72 / MNQ)
- **Session Flat Mandate**: Liquidate at **15:50 CT** (Zero overnight holds)
- **Core Architecture**:
  - **Entry 4**: Low-Volume / Low-Momentum Reversal (Fade extreme when volume < 10-bar SMA and ADX < 25)
  - **Regime Filter (Iteration 1)**: 200 SMA Macro Trend Alignment (Only buy dips above 200 SMA; only sell rallies below 200 SMA)
  - **Exit 6**: Protective ATR Stop Loss (1.5 $\times$ ATR)
  - **Exit 7**: Quick Spike Limit Target (1.5 $\times$ ATR)
  - **Intraday Flat**: 15:50 CT mandatory liquidation

---

## 2. Iteration History & Comparative Metrics

| Metric | Iteration 0 (Raw Baseline) | Iteration 1 (Trend-Aligned 200 SMA) | Delta / Impact |
| :--- | :--- | :--- | :--- |
| **Session ID** | `7de41011-3348-48cf-bba3-f542d2f1ca69` | `68f404e7-c3f4-47bd-a691-4bfd83fd4c8f` | - |
| **Dashboard URL** | [View Baseline](http://localhost:9000/#/backtest/7de41011-3348-48cf-bba3-f542d2f1ca69) | [View Iteration 1](http://localhost:9000/#/backtest/68f404e7-c3f4-47bd-a691-4bfd83fd4c8f) | - |
| **Total Trades** | 965 | 259 | -706 trades (-73.2% noise eliminated) |
| **Longs / Shorts** | 302 / 663 (68.7% short) | 100 / 159 (61.4% short) | Shifted towards balanced exposure |
| **Win Rate (Total)** | 49.0% | **49.42%** | +0.42% |
| **Win Rate (Longs)** | 51.7% | **52.0%** | +0.30% |
| **Win Rate (Shorts)** | 47.8% | **47.8%** | Unchanged (still lagging) |
| **Win / Loss Ratio** | 1.03 : 1 | **1.086 : 1** | +5.4% improvement |
| **Average Win** | \$269.47 | **\$292.45** | +\$22.98 |
| **Average Loss** | \$262.83 | **\$269.17** | -\$6.34 |
| **Gross Profit** | +\$127,457.22 | +\$37,433.34 | Concentrated quality |
| **Gross Loss** | -\$129,310.73 | -\$35,261.35 | Reduced total loss exposure |
| **Fees Paid (Friction)** | \$4,343.66 | **\$1,169.43** | -\$3,174.23 fees saved |
| **Net Profit** | **-\$1,853.51** | **+\$2,171.99** | **+\$4,025.50 turnaround (profitable)** |
| **Expectancy / Trade** | -\$1.92 | **+\$8.39** | Positive statistical expectation |
| **Sharpe Ratio** | -0.07 | **0.17** | Positive risk-adjusted return |
| **Sortino Ratio** | -0.10 | **0.24** | Improved downside deviation |
| **Max Drawdown** | **-1.38%** (~\$2,768 on 1 MNQ) | **-0.31%** (~\$620 on 1 MNQ) | **-77.5% drawdown reduction** |
| **Largest Losing Trade** | -\$1,385.25 | **-\$907.63** | Reduced tail risk |

---

## 3. Account Phase Assessment

| Phase | Evaluation Rule | Iteration 0 Result | Iteration 1 Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1: Prop Evaluation (Apex)** | Max DD $\le \$2,000$ per contract, strict 15:55 CT flat | **FAILED** (Max DD \$2,768 on 1 MNQ breaches \$2k limit) | **PASSED** (Max DD is \$620 on 1 MNQ, well within \$2,000 trailing limit) | **Viable Candidate** |
| **Phase 2: Funded / PA Account** | Payout preservation, consistent edge, low volatility | **FAILED** (Negative expectancy) | **MARGINAL** (Positive expectancy +\$8.39/trade, low trade frequency ~30 trades/yr) | **Needs Edge Enhancement** |
| **Phase 3: Personal Capital** | High Sharpe, compounding, flexible drawdown tolerance | **FAILED** (Negative Sharpe) | **ACCEPTABLE SEED** (Positive Sharpe 0.17, clean risk bounds) | **Building Block Validated** |

---

## 4. Key Diagnostic Insights from Iteration 1

1. **Macro Trend Alignment is Mandatory for Mean Reversion**:
   - The baseline strategy suffered from shorting low-volume upward grinds during bull markets. In Nasdaq, low volume during an uptrend is typically institutional accumulation, not a reversal.
   - Enforcing `Close > 200 SMA` for Longs and `Close < 200 SMA` for Shorts eliminated 706 unpromising trades and turned a -\$1,853 loss into a +\$2,172 net profit after full futures fees.
2. **Drawdown Compression**:
   - Max drawdown dropped from \$2,768 down to \$620 on 1 MNQ (a 77.5% drop), transforming the strategy from an automatic Apex fail into a strategy that satisfies the \$2,000 trailing drawdown constraint.
3. **The Persistent Short Disadvantage**:
   - While Longs won 52.0%, Shorts still lagged at 47.8%. Touching the 8-bar high in a downtrend is not sufficient by itself—it requires price rejection confirmation.

---

## 5. Next Controlled Hypotheses

- **Iteration 2A: Rejection Wick Confirmation (Intrabar Absorption)**:
  - Require a lower rejection wick for Longs (`lower_wick >= 1.0 * body`) confirming buyers defended the low.
  - Require an upper rejection wick for Shorts (`upper_wick >= 1.0 * body`) confirming sellers defended the high.
- **Iteration 2B: Asymmetric Risk / Reward**:
  - Test expanding target from 1.5 $\times$ ATR to 2.0 $\times$ ATR while keeping stop at 1.5 $\times$ ATR (1.33:1 reward-to-risk ratio) to improve average win and boost expectancy.
