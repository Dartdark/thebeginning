# Institutional Optimization & Failure Mode Report: Overnight Bias Time & Price Optimization (HYP-026)

**Strategy Name**: `NQOvernightBiasADX30`  
**Instrument**: CME E-mini Nasdaq-100 Futures (`NQ-USD` / `MNQ`)  
**Timeframe**: 15-Minute Strategy Bars (`fast_mode = False`, 1-minute intrabar execution)  
**Exchange**: `Custom Data`  
**Execution Friction Model**: Strict Institutional Friction — **$17.25 round-turn commission + 1 tick ($5.00) slippage per fill ($10.00 RT)** = **$27.25 per trade** (1.3625 NQ points).  
**Evaluation Standard**: Strict SignalLab split — In-Sample (`2018-01-01` to `2022-12-31`), Candidate Gate $t \ge 2.50$, lower Max DD, higher Net Profit; Holdout (`2023-01-01` to `2026-10-09`) tested once only for an In-Sample winner.  

---

## 1. Executive Summary & Verdict

- **Core Question**: Can Overnight Bias be improved in the same way as Vault Break by targeting its empirical failure mode (a 46.8% stop-out rate between 08:45 and 09:00 CT) across orthogonal **Time** (macro-release delay) and **Price** (VWAP alignment) dimensions?
- **Empirical Verdict**: **UNANIMOUS REJECTION OF ALL CANDIDATE MODIFICATIONS**.  
  Every single tested variant (**V1 VWAP Alignment**, **V2 09:00 CT Delay**, **V3 Bar Close Confirmation**, and **V4 Combined**) degraded net performance, reduced trade expectancy, and increased Max Drawdown relative to the original baseline:
  - **Base In-Sample**: **$122,452.33 Net Profit**, **$6,917.00 Max Drawdown**, **NP/DD 17.70**, **$t = 4.00**, **$339.20/trade**.
  - **V1 (VWAP Align)**: $119,110.50 Net (-$3.3k), $9,804.92 Max DD (+41.7% worse DD), NP/DD 12.15, $t = 3.91.
  - **V2 (09:00 Delay)**: $111,397.25 Net (-$11.1k), $8,927.42 Max DD (+29.1% worse DD), NP/DD 12.48, $t = 3.75.
  - **V3 (Close Confirm)**: $95,647.83 Net (-$26.8k), $8,047.00 Max DD (+16.3% worse DD), NP/DD 11.89, $t = 3.45.
  - **V4 (Combined)**: $110,537.25 Net (-$11.9k), $8,927.42 Max DD (+29.1% worse DD), NP/DD 12.38, $t = 3.72.
- **Why Did This Happen? (Microstructure Insight)**:
  - Vault Break is a **1:1 to 1.5:1 reward-to-risk mean-reverting breakout** where capping runaway stretch and cutting off late-day entries cuts churn.
  - Overnight Bias is fundamentally different: it is an **asymmetric 3:1 trend-runner model** (`TP = 0.75 * ATR`, `SL = 0.25 * ATR`).
  - The trades entered immediately at 08:45 CT suffer a 46.8% stop rate, but the 53.2% that survive catch the **entire multi-hundred point trend day from the very bottom tick** (averaging **+$426.73 net per trade** and generating **+$56,328.33 in net profit**). Delaying entry to 09:00 CT completely misses these trend days or forces entries after price has already moved 50-100 points.
  - Session VWAP at 08:45 CT is calculated over only 1 or 2 bars, making it extremely noisy and unanchored; filtering by it erroneously disqualified massive +$2,000+ winning trend shorts.
- **Protocol Action**: Under SignalLab rules, when zero variants beat the in-sample baseline, no holdout degrees of freedom are burned. The baseline **`NQOvernightBiasADX30` remains undefeated and deployed**.

---

## 2. In-Sample Results Matrix (2018–2022, 5.0 Years)

All figures include full institutional friction ($17.25 RT + 1 tick slip per fill = $27.25 / trade):

| Variant | Strategy Name | Session ID & Dashboard URL | Trades | Win Rate | Gross Profit | Net Profit ($) | Net / Trade | Max DD ($) | NP / DD | $t$-stat | In-Sample Gate |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Base** | `NQONBiasADX30Base` | [32bfbf06-67e8-41a1-848d-961b6bfbe908](http://localhost:9000/#/backtest/32bfbf06-67e8-41a1-848d-961b6bfbe908)<br>Dashboard: http://localhost:9000/#/backtest/32bfbf06-67e8-41a1-848d-961b6bfbe908 | **361** | 50.7% | **$132,289.58** | **$122,452.33** | **$339.20** | **$6,917.00** | **17.70** | **4.00** | **UNDFEATED BASELINE** |
| **V1** | `NQONBVWAPAlign` | [5d4ec2b8-60b7-4217-b985-fb614fbef8fa](http://localhost:9000/#/backtest/5d4ec2b8-60b7-4217-b985-fb614fbef8fa)<br>Dashboard: http://localhost:9000/#/backtest/5d4ec2b8-60b7-4217-b985-fb614fbef8fa | 359 | 50.7% | $128,893.25 | $119,110.50 | $331.78 | $9,804.92 | 12.15 | 3.91 | FAILED (+41.7% DD, -$3.3k Net) |
| **V2** | `NQONBDelay0900` | [d700e8fa-854a-49c8-a8d5-7783101cf651](http://localhost:9000/#/backtest/d700e8fa-854a-49c8-a8d5-7783101cf651)<br>Dashboard: http://localhost:9000/#/backtest/d700e8fa-854a-49c8-a8d5-7783101cf651 | 348 | 51.4% | $120,880.25 | $111,397.25 | $320.11 | $8,927.42 | 12.48 | 3.75 | FAILED (+29.1% DD, -$11.1k Net) |
| **V3** | `NQONBCloseConfirm` | [aaba312d-130c-4e58-8160-c12e7378204b](http://localhost:9000/#/backtest/aaba312d-130c-4e58-8160-c12e7378204b)<br>Dashboard: http://localhost:9000/#/backtest/aaba312d-130c-4e58-8160-c12e7378204b | 322 | 52.5% | $104,422.33 | $95,647.83 | $297.04 | $8,047.00 | 11.89 | 3.45 | FAILED (+16.3% DD, -$26.8k Net) |
| **V4** | `NQONBCombined` | [c98dff93-6a9d-4fff-b890-d2d02ee615e4](http://localhost:9000/#/backtest/c98dff93-6a9d-4fff-b890-d2d02ee615e4)<br>Dashboard: http://localhost:9000/#/backtest/c98dff93-6a9d-4fff-b890-d2d02ee615e4 | 348 | 51.4% | $120,020.25 | $110,537.25 | $317.64 | $8,927.42 | 12.38 | 3.72 | FAILED (+29.1% DD, -$11.9k Net) |

---

## 3. Deep-Dive Iteration Logs & Trade Dissection

### Iteration 1: VWAP Alignment (`NQONBVWAPAlign`, `HYP-026 V1`)
- **Session ID**: `5d4ec2b8-60b7-4217-b985-fb614fbef8fa`
- **Dashboard**: [View on dashboard](http://localhost:9000/#/backtest/5d4ec2b8-60b7-4217-b985-fb614fbef8fa)
- **Mechanism**: Enforce directional consistency with session VWAP (`Close > VWAP` for longs, `Close < VWAP` for shorts).
- **Outcome**: Net profit fell by -$3,341.83; Max Drawdown surged from $6,917.00 to $9,804.92 (+41.7%).
- **Why It Failed**: Session VWAP resets at 08:30 CT. At 08:45 CT, only one 15m candle exists. Cumulative VWAP on 1 bar is simply the typical price of that single bar. Requiring price to be on one side of this single-bar noisy average filtered out 11 trades, including massive multi-thousand dollar trend-day winners (+2,062.75 on 2021-02-23, +$1,732.75 on 2021-04-19, +$2,355.00 on 2021-08-16, +$1,662.75 on 2022-12-08). Removing these recovery windfalls caused equity drawdowns to widen significantly.

### Iteration 2: 09:00 CT Macro Release Delay (`NQONBDelay0900`, `HYP-026 V2`)
- **Session ID**: `d700e8fa-854a-49c8-a8d5-7783101cf651`
- **Dashboard**: [View on dashboard](http://localhost:9000/#/backtest/d700e8fa-854a-49c8-a8d5-7783101cf651)
- **Mechanism**: Delay entry window start from 08:45 CT to 09:00 CT to clear 10:00 ET US macro releases (ISM, JOLTS, Consumer Confidence).
- **Outcome**: Net profit collapsed by -$11,055.08; Max Drawdown increased by +$2,010.42 (+29.1%).
- **Why It Failed**: Detailed trade auditing shows that the trades taken during the 08:45–09:00 CT window generated **+$56,328.33 of net profit** with an average expectancy of **+$426.73 per trade**. The highest-conviction trend breakouts occur immediately at the cash open. By 09:00 CT, the trend has already moved 50–100 points, leaving late entries to either be skipped entirely or buy the top/sell the bottom.

### Iteration 3: 15-Minute Bar Close Confirmation (`NQONBCloseConfirm`, `HYP-026 V3`)
- **Session ID**: `aaba312d-130c-4e58-8160-c12e7378204b`
- **Dashboard**: [View on dashboard](http://localhost:9000/#/backtest/aaba312d-130c-4e58-8160-c12e7378204b)
- **Mechanism**: Replace resting stop orders with bar close confirmation (`Close > OR High`) to prevent false-breakout wick entries.
- **Outcome**: Net profit plunged by -$26,804.50; Max Drawdown worsened by +16.3% to $8,047.00.
- **Why It Failed**: Adverse selection and lag. Waiting for a 15-minute candle to fully close above the opening range meant entering 15 to 40 points higher than the breakout level. This severely degraded the reward-to-risk ratio (average trade expectancy collapsed from $339.20 to $297.04).

### Iteration 4: Combined 09:00 Delay + VWAP Alignment (`NQONBCombined`, `HYP-026 V4`)
- **Session ID**: `c98dff93-6a9d-4fff-b890-d2d02ee615e4`
- **Dashboard**: [View on dashboard](http://localhost:9000/#/backtest/c98dff93-6a9d-4fff-b890-d2d02ee615e4)
- **Outcome**: Net profit fell by -$11,915.08; Max Drawdown matched V2 at $8,927.42.
- **Verdict**: Compounding two flawed filters produced no synergy; Base strictly dominates.

---

## 4. Final Verdict & Deployment Recommendation

1. **Undefeated Baseline**: The original `NQOvernightBiasADX30` configuration remains strictly superior across every performance, risk, and stability metric.
2. **Holdout Status**: Retained from verified session `5cc12f34-5f0e-4c5b-95f5-3a1d4d1f2852`:
   - Out-of-Sample Holdout (2023–2026): **$127,746.25 Net Profit**, **$13,608.50 Max Drawdown**, **Sharpe 1.85**, **$t = 2.90**.
   - Full 9-Year Record (2018–2026): **673 trades, 9/9 positive years, +$250,198.58 Net Profit, Sharpe 1.86**.
3. **Registry Update**: `HYP-026` logged in `tasks/SEARCH_DENOMINATOR_REGISTRY.csv` as `FAILED_IN_SAMPLE_BASE_RETAINED`.
