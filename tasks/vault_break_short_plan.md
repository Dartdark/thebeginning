# Pre-Registered Research Plan: Vault Break Short (Concept 1)

**Date**: 2026-10-21  
**Author**: Antigravity (under SignalLab Institutional Standards & Rule 9)  
**Target Instrument**: CME E-mini / Micro E-mini Nasdaq-100 Futures (`NQ` / `MNQ`)  
**Cross-Asset Reference**: CME E-mini S&P 500 Futures (`ES`)  
**Data Horizon**: 2018-01-02 to 2026-10-09 (Full 1-minute unadjusted data)  
**Partitioning**: In-Sample = 2018-04-01 to 2022-12-31 | Holdout OOS = 2023-01-01 to 2026-10-09  
**Friction Model**: $17.25 per round-turn on full NQ ($1.72 per MNQ)  

---

## 1. Economic Mechanism & Hypothesis Triplet ($h_j = (m_j, e_j, d_j)$)

### Economic Mechanism ($m_j$)
`Vault Break` is our #1 performing live strategy (+$9,621 NQ pts, 9/9 positive years, Sharpe 1.76), but it is **longs only**. In equity index futures, an unconstrained short breakout is plagued by false breakdowns because retail dip-buyers and passive 401(k) / index-drift flows frequently buy intraday dips. 

However, when an intraday breakdown is confirmed by **broad-market institutional liquidation across the S&P 500 (ES)**, liquidity dries up on the bid side, systematic stop-runs trigger, and intraday downside momentum accelerates. 

We hypothesize that transferring `Vault Break`'s proven structural primitives (midnight baseline anchor, ATR volatility barrier, midnight-anchored VWAP, and post-10:00 CT institutional execution window) to the **short side** will succeed **if and only if** filtered by broad-market ES downside alignment.

### Executable Expression ($e_j$)
1. **Anchor**: Session Open at 00:00 CT (midnight).
2. **Volatility Noise Floor**: $\text{Noise Level} = \text{00:00 Open} - 0.30 \times \text{15-day ATR}$.
3. **Volume Benchmark**: Midnight-anchored VWAP (cumulative $\frac{H+L+C}{3} \times V / \sum V$ from 00:00 CT).
4. **Execution Timing**: 30-minute bar close between **10:00 CT and 14:30 CT** (Early close days: 11:00 CT).
5. **Entry Trigger**: Bar Close $< \text{Noise Level}$ AND Bar Close $< \text{Midnight VWAP}$.
6. **Cross-Asset Alignment Gates (Variants)**:
   - *Variant 1 (Unhedged)*: No cross-asset filter (pure mirror).
   - *Variant 2 (ES Session Red)*: $\text{ES Price} < \text{ES 00:00 Open}$.
   - *Variant 3 (ES VWAP Red)*: $\text{ES Price} < \text{ES Midnight VWAP}$.
   - *Variant 4 (ES Morning Drop)*: $\text{ES 09:00 Close} < \text{ES 08:30 Open}$ (the Watchlist #25 filter).
7. **Exits**:
   - Fixed Profit Target: 40.0 NQ points below entry fill.
   - Fixed Stop Loss: 75.0 NQ points above entry fill.
   - Mandatory EOD Flatten: Close of bar at or after 14:30 CT (Early close days: 11:30 CT).
   - Max trades: 3 per day.

### Declared Return Direction ($d_j$)
* $d_j = -1$ (Short). Direction is declared prior to running backtest.

---

## 2. In-Sample vs. Out-of-Sample Decision Rules (Rule 7 & 8)

1. **In-Sample Gate (2018-04-01 to 2022-12-31)**:
   - Must achieve $t \ge 2.50$ under full friction ($17.25/NQ).
   - Profit Factor $\ge 1.30$.
   - Positive net profit across at least 4 of the 5 in-sample years.
   - **Hard Stop**: If any variant fails $t < 2.50$ on 2018–2022, it is immediately rejected as Rank F without touching holdout data.

2. **Out-of-Sample Verification (2023-01-01 to 2026-10-09)**:
   - Evaluated strictly once. Must remain net positive ($t \ge 1.50$, positive net PnL).
   - Must not exhibit severe alpha decay ($t_{\text{decay}} > -1.96$).

3. **Portfolio Spanning & Funded Account Gate (Rule 10)**:
   - Does adding the short variant to `Vault Break Long` improve total portfolio Sharpe and reduce drawdown, or does it add tail risk?
