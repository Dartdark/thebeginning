# Quantitative Strategy Report: NQIntradayMR (Intraday Mean Reversion)

## 1. Executive Summary & Objective

- **Strategy Name**: `NQIntradayMR`
- **Target Symbol**: CME E-mini / Micro Nasdaq-100 Index Futures (`NQ-USD` / `MNQ`)
- **Timeframe**: `15m`
- **Evaluation Window**: **2018-04-01 through 2026-10-09** (8.5 years continuous, zero window truncation)
- **Friction Model**: Realistic CME Futures Friction (`fee = 0.00003`, \$17.25 round-turn / NQ, \$1.72 / MNQ)
- **Session Flat Mandate**: Liquidate at **15:50 CT** (Zero overnight holds)
- **Core Architecture**:
  - **Entry 4**: Low-Volume / Low-Momentum Reversal (Fade 8-bar extreme when volume < 10-bar SMA and ADX < 25)
  - **Exit 6**: Protective ATR Stop Loss (1.5 $\times$ ATR)
  - **Exit 7**: Quick Spike Limit Target (1.5 $\times$ ATR)
  - **Intraday Flat**: 15:50 CT exit

---

## 2. Iteration 0: Raw Benchmark Performance (Full History: 2018–2026)

- **Session ID**: `7de41011-3348-48cf-bba3-f542d2f1ca69`
- **Dashboard URL**: [View Dashboard](http://localhost:9000/#/backtest/7de41011-3348-48cf-bba3-f542d2f1ca69)

### Metrics Summary:
- **Total Trades**: 965 trades (~2.2 trades/week)
- **Longs / Shorts**: 302 Longs (31.3%) vs 663 Shorts (68.7%)
- **Win Rate**: **49.0%** (Longs: 51.7%, Shorts: 47.8%)
- **Win / Loss Ratio**: **1.03 : 1** (\$269.47 avg win vs \$262.83 avg loss)
- **Gross Profit**: +\$127,457.22
- **Gross Loss**: -\$129,310.73
- **Total Fees (Friction)**: \$4,343.66
- **Net Profit**: **-\$1,853.51** (-\$1.92 expectancy per trade)
- **Sharpe Ratio**: **-0.07**
- **Sortino Ratio**: **-0.10**
- **Max Drawdown**: **-1.38%** (-\$13,843 total on 5 micros / ~\$2,768 on 1 MNQ)
- **Max Consecutive Losses**: 7 trades

---

## 3. Diagnosis & Anatomical Flaws

1. **Coin-Flip Baseline**:
   - A 49.0% win rate with a 1.03:1 payoff ratio is a textbook coin flip. Without fees, it made +\$2,490 over 8.5 years. With realistic fees, it loses -\$1,853.
2. **Shorting Low-Volume Upward Grinds**:
   - 68.7% of all trades were shorts (663 shorts vs 302 longs).
   - In Nasdaq, low-volume consolidations often grind steadily upward. The strategy blindly shorted every new 8-bar high during low-volume grinds, leading to a losing 47.8% win rate on shorts.
3. **Missing Rejection Confirmation**:
   - Simply touching the 8-bar high or low is not an exhaustion signal—often momentum is just beginning. It requires price rejection (e.g. an upper shadow for shorts, a lower shadow for longs) or trend-filter alignment.
