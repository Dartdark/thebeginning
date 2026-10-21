# Pre-Registered Research Plan: Vault Break VWAP Stretch Filter (HYP-024)

**Date**: 2026-10-21  
**Author**: Quantitative Strategy Team / Antigravity  
**Target Strategy**: `Vault Break` (`NQVaultBreak`)  
**Instrument**: CME E-mini Nasdaq-100 Futures (`NQ`) / Micro E-mini (`MNQ`)  
**Timeframe**: 30-Minute Bars  
**Direction**: Longs Only  
**Target / Stop**: Fixed `+40.0 pts` limit target / `-75.0 pts` stop loss  

---

## 1. Problem Statement: The Microstructure of the "Top-Tick" Loss

In live execution on Apex Trader Funding accounts, Vault Break's most damaging failure mode is entering at the literal top tick of a 30-minute breakout candle right before an institutional selling cascade or mean-reversion retest to VWAP.

### The Physics of the Failure:
1. When a 30-minute bar surges strongly above the midnight open + 0.30 ATR noise band, price often ends up stretched **+1.0 to +2.5 standard deviations above the session VWAP**.
2. On NQ, a normal intraday pullback to test session VWAP is routinely 60 to 100 points deep.
3. Because Vault Break enters at market at the extreme stretch with a **fixed 75-point stop**, a healthy, normal pullback to retest session VWAP will trigger the stop loss before any further upside can develop.
4. Furthermore, buying at extreme distance from VWAP pays peak liquidity prices right where institutional desks are offloading inventory into retail breakout buyers.

---

## 2. Hypothesis Triplet ($h_{24}$)

* **Economic Mechanism ($m_{24}$)**: Capping the allowable distance between the trigger candle's close and the session cumulative VWAP prevents buying into overextended exhaustion tops (buying climaxes). It forces the strategy to only enter breakouts that originate relatively close to the institutional volume-weighted average price, leaving ample headroom before the 75-point stop is threatened.
* **Executable Expression ($e_{24}$)**:
  $$\text{Stretch} = \text{Close} - \text{VWAP}$$
  $$\text{Entry Condition}: \text{Close} > \text{Noise Level} \quad \text{AND} \quad \text{Close} > \text{VWAP} \quad \text{AND} \quad \text{Stretch} \le k \times \text{DailyATR}_{15}$$
* **Declared Return Direction ($d_{24}$)**: Long ($+1$).

---

## 3. Pre-Registered Variants to Evaluate

We pre-register exactly 3 variants evaluated against Base on the **In-Sample Period (2018-04-01 to 2022-12-31)**:

| Variant | Formulation | Description |
|---|---|---|
| **Base** | $\text{Stretch} < \infty$ | Original Vault Break (no stretch cap) |
| **V1** | $\text{Stretch} \le 0.50 \times \text{DailyATR}$ | Conservative Cap: Only enters when price is within 0.50 ATR of VWAP (~60-120 pts) |
| **V2** | $\text{Stretch} \le 0.75 \times \text{DailyATR}$ | Moderate Cap: Enters within 0.75 ATR of VWAP (~90-180 pts) |
| **V3** | $\text{Stretch} \le 1.00 \times \text{DailyATR}$ | Loose Cap: Rejects only extreme parabolic outliers > 1.0 ATR above VWAP |

---

## 4. Testing Protocol & Success Gates

1. **Chronological In-Sample Split**:
   - In-Sample (IS): **2018-04-01 through 2022-12-31**.
   - Hurdle Gate: $t \ge 2.50$, positive profit across sub-periods, and reduction in Max Drawdown.
2. **Locked Out-of-Sample (OOS) Holdout**:
   - Holdout: **2023-01-01 through 2026-10-09**.
   - Tested **only once** for the single winner of the In-Sample gate.
3. **Friction Model**:
   - Standard NQ friction: **\$17.25 per round-turn** + 1 tick slippage per fill.
4. **Mandatory MCP Report**:
   - Save via `save_strategy_report` inside `strategies/NQVaultBreak/reports/`.
