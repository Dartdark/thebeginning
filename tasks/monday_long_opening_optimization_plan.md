# Pre-Registered Research Plan: Monday Long Opening Regime & Timing Optimization (HYP-028)

**Date**: 2026-10-21  
**Author**: Quantitative Strategy Team / Antigravity  
**Target Strategy**: `Monday Long` (`NQMondayLong` / Task 05)  
**Instrument**: CME E-mini Nasdaq-100 Futures (`NQ`) / Micro E-mini (`MNQ`)  
**Timeframe**: 5-Minute Bars (`fast_mode = False`, full 1m intrabar execution)  
**Direction**: Longs Only  
**Target / Stop**: Systematic Time Exit at `15:00 CT` / Dynamic Stop Loss at `Entry - 0.50 * ATR-15`  
**Holding Period**: Intraday full-day hold (~6.5 hours)  

---

## 1. Problem Statement: Microstructure Failure Signatures of Monday Long

`Monday Long` captures the systematic post-weekend equity inflow effect on the Nasdaq-100, entering long on non-holiday Mondays and holding until 15:00 CT.

However, historical trade audits reveal severe drawdowns ($22,427 peak-to-valley drawdown on 1 NQ contract):
1. **The Blind 08:30 CT Open Trap**:
   - `NQMondayLong` enters blindly at **08:30 CT**, the exact minute the New York cash equity market opens.
   - On Mondays following weekend geopolitical shock headlines (armed conflicts, bank failures, sovereign debt stress), global risk assets gap down overnight.
   - Buying blindly at 08:30 CT into an opening liquidation waterfall results in catching a falling knife, hitting the wide 0.50 ATR stop (-\$1,000 to -\$1,700 per contract) within 1 to 2 hours.
2. **Prior Phase 2 Flaw (Over-Truncation)**:
   - In Phase 2, a variant (`NQMondayLongV1`) tested requiring the entire first hour (`08:30–09:30 CT`) to close green.
   - While that worked in 2018–2022, it **failed on 2023–2026 Holdout** because waiting 60 minutes into the session surrendered the early morning dips that fueled the 2023–2026 tech bull market.
   - A surgical, shorter digestion window (15–30 minutes) or an opening bar regime filter is required to avoid falling knives without sacrificing the core morning edge.

---

## 2. Hypothesis Triplet ($h_{28}$)

- **Economic Mechanism ($m_{28}$)**: 
  1. *Time Dimension*: Allowing the cash open to digest for 15 to 30 minutes (entering at 08:45 or 09:00 CT) allows opening bid-ask spreads to normalize and clears 10:00 ET macroeconomic releases (ISM, JOLTS) before capital is committed.
  2. *Price Dimension*: Filtering by opening bar confirmation (`Close >= Open`) or requiring price to sit in the upper half of the overnight Globex range avoids stepping into broad-market risk-off liquidation waterfalls.
- **Executable Expression ($e_{28}$)**: Defined across 4 pre-registered variants below.
- **Declared Return Direction ($d_{28}$)**: Longs.

---

## 3. Pre-Registered Variants to Evaluate (In-Sample: 2018–2022)

All variants evaluated under full institutional friction (**$17.25 round-turn commission + 1 tick ($5.00) slippage per fill ($10.00 RT) = $27.25 per trade**):

| Variant | Strategy Name | Modification |
|---|---|---|
| **Base** | `NQMondayLong` | Baseline: Blind entry at `08:30 CT`, Stop at `0.50 * ATR`, exit `15:00 CT` |
| **V1** | `NQMonLongWait0845` | **15m Digestion Window**: Enters at `08:45 CT` close instead of 08:30 CT |
| **V2** | `NQMonLongWait0900` | **30m Macro Clear Window**: Enters at `09:00 CT` close to clear 10:00 ET releases |
| **V3** | `NQMonLongGreen0835`| **Opening 5m Confirmation**: At `08:35 CT`, enter ONLY if `Close >= Open` |
| **V4** | `NQMonLongGreen0845`| **Opening 15m Confirmation**: At `08:45 CT`, enter ONLY if `Close >= Open_0830` |

---

## 4. Evaluation Protocol

1. **In-Sample Period**: `2018-01-01` to `2022-12-31`. Strict candidate hurdle: $t \ge 2.50$, higher Net Profit, lower Max Drawdown, improved NP/DD ratio.
2. **Out-of-Sample Holdout**: `2023-01-01` to `2026-10-09`. Tested **once** for the single winner of the In-Sample evaluation.
3. **Mandatory MCP Report**: Save via `save_strategy_report` inside `strategies/NQMondayLong/reports/`.
