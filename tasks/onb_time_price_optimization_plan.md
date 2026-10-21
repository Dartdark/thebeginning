# Pre-Registered Research Plan: Overnight Bias Time & Price Optimization (HYP-026)

**Date**: 2026-10-21  
**Author**: Quantitative Strategy Team / Antigravity  
**Target Strategy**: `Overnight Bias ADX 30` (`NQOvernightBiasADX30` / Task 03)  
**Instrument**: CME E-mini Nasdaq-100 Futures (`NQ`) / Micro E-mini (`MNQ`)  
**Timeframe**: 15-Minute Bars  
**Direction**: Longs and Shorts  
**Target / Stop**: Fixed `+0.75 × ATR` target (`+3.0R`) / `-0.25 × ATR` stop loss (`-1.0R`)  
**Time Exit**: `14:30 CT` (`11:30 CT` on early close days)  

---

## 1. Problem Statement: Microstructure Failure Signatures of Overnight Bias

Historical trade audits across 673 trades (2018–2026) reveal two glaring structural flaws in Overnight Bias:

1. **The Morning 08:45–09:00 CT Stop Trap (46.8% Stop-Out Rate)**:
   - Overnight Bias forms its Opening Range (OR) on the 08:30–08:45 CT bar.
   - At **08:45 CT sharp**, it arms resting stop-buy and stop-sell orders.
   - At **09:00 CT (10:00 ET)**, high-impact US macroeconomic data is released (ISM Manufacturing/Services, Consumer Confidence, JOLTS).
   - In the 15 minutes prior to the release (08:45–09:00 CT), algorithmic market makers sweep resting liquidity above/below the 15m range by 5–10 points. This trips the resting stop order, entering the trade at the extreme wick. Two minutes later, the 09:00 CT macro data drops, whipping price into the tight 0.25 ATR stop.
   - Trades entered between 08:45 and 09:00 CT suffer a **46.8% stop-out rate**.

2. **Zero VWAP Alignment (Trading Against the Institutional Tape)**:
   - The current Overnight Bias rule has **no VWAP filter**.
   - If price opens in the upper third of the overnight range (`bias = +1`), but morning liquidation pushes price below session VWAP, the strategy still buys a breakout above the 15m high—buying directly into institutional net selling pressure.

---

## 2. Hypothesis Triplet ($h_{26}$)

- **Economic Mechanism ($m_{26}$)**: 
  1. *Time Dimension*: Delaying the entry window start to 09:00 CT allows the market to digest the 09:00 CT (10:00 ET) macroeconomic data release and clears initial opening sweeps before capital is committed.
  2. *Price Dimension*: Requiring breakout entries to align with cumulative session VWAP (`Close > VWAP` for longs, `Close < VWAP` for shorts) ensures trades only enter in the direction of institutional volume-weighted conviction.
  3. *Execution Dimension*: Requiring a 15-minute bar close confirmation (`Close > OR High`) instead of a 1-tick resting stop-order prevents buying the peak tick of intrabar false-breakout wicks.
- **Executable Expression ($e_{26}$)**: Defined across 4 pre-registered variants below.
- **Declared Return Direction ($d_{26}$)**: Directional Breakout ($+1$ for Longs, $-1$ for Shorts).

---

## 3. Pre-Registered Variants to Evaluate (In-Sample: 2018–2022)

All variants evaluated under full friction (**\$17.25 round-turn + 1 tick slippage per fill**):

| Variant | Name | Key Modification |
|---|---|---|
| **Base** | `NQONBiasADX30Base` | Original Task 03: Entry window 08:45–14:00 CT, resting stop orders, no VWAP |
| **V1** | `NQONBVWAPAlign` | **VWAP Alignment**: Longs require `Close > VWAP`; Shorts require `Close < VWAP` |
| **V2** | `NQONBDelay0900` | **09:00 CT Macro Delay**: Entry window opens at `09:00 CT` instead of `08:45 CT` |
| **V3** | `NQONBCloseConfirm` | **15m Bar Close Confirmation**: No resting stop orders; enters next bar at market only when `Close > OR High` (Long) or `Close < OR Low` (Short) |
| **V4** | `NQONBCombined` | **Combined**: 09:00 CT Delay + VWAP Alignment |

---

## 4. Evaluation Protocol

1. **In-Sample Period**: `2018-01-01` to `2022-12-31`. Strict candidate hurdle: $t \ge 2.50$, positive net profit, reduced Max Drawdown.
2. **Out-of-Sample Holdout**: `2023-01-01` to `2026-10-09`. Tested **once** for the single winner of the In-Sample evaluation.
3. **Mandatory MCP Report**: Save via `save_strategy_report` inside `strategies/NQOvernightBiasADX30/reports/`.
