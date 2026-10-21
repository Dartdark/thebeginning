# Institutional Optimization & Failure Mode Report: Late-Day Flow VWAP Climax & Stretch Guard (HYP-027)

**Strategy Name**: `NQLateDayFlow`  
**Instrument**: CME E-mini Nasdaq-100 Futures (`NQ-USD` / `MNQ`)  
**Timeframe**: 5-Minute Strategy Bars (`fast_mode = False`, full 1-minute intrabar execution)  
**Exchange**: `Custom Data`  
**Execution Friction Model**: Strict Institutional Friction — **$17.25 round-turn commission + 1 tick ($5.00) slippage per fill ($10.00 RT)** = **$27.25 per trade** (1.3625 NQ points).  
**Evaluation Standard**: Strict SignalLab split — In-Sample (`2018-01-01` to `2022-12-31`), Candidate Gate $t \ge 2.50$, lower Max DD, higher Net Profit; Holdout (`2023-01-01` to `2026-10-09`) tested once only for an In-Sample winner.  

---

## 1. Executive Summary & Microstructure Verdict

- **Core Question**: Can Late-Day Flow be improved by applying a VWAP Climax & Stretch Guard (capping distance from session VWAP at 14:00 CT) to prevent buying into end-of-day profit-taking exhaustion—the exact price-dimension guard that succeeded on Vault Break?
- **Empirical Verdict**: **UNANIMOUS REJECTION OF VWAP STRETCH RESTRICTIONS**.  
  Every tested variant (**V1 Stretch <= 1.00 ATR**, **V2 Stretch <= 0.75 ATR**, **V3 Stretch <= 0.50 ATR**, and **V4 Pullback to VWAP**) degraded net profit and trade expectancy relative to the baseline:
  - **Base In-Sample**: **$32,917.67 Net Profit**, **$67.73 / trade**, **$16,541.00 Max Drawdown**, **$t = 2.37** across 486 trades.
  - **V1 (Stretch <= 1.00 ATR)**: $31,852.17 Net, $65.81 / trade, $16,541.00 Max DD, $t = 2.30.
  - **V2 (Stretch <= 0.75 ATR)**: $28,050.25 Net (-$4.8k), $59.30 / trade, $15,899.25 Max DD, $t = 2.10.
  - **V3 (Stretch <= 0.50 ATR)**: $13,155.17 Net (-$19.8k), $32.64 / trade, $14,798.42 Max DD, $t = 1.11.
  - **V4 (Pullback to VWAP)**: -$2,882.50 Net (Unviable / Negative Expectancy), $t = -0.32.
- **Why Did This Fail? (The Economics of Leveraged ETF Rebalancing)**:
  - **Vault Break vs Late-Day Flow**: Vault Break is a morning breakout above an overnight noise band where overextension signifies retail buying climax. Late-Day Flow is fundamentally driven by **mathematically mandated Leveraged ETF asset rebalancing** (e.g. ProShares UltraPro QQQ `TQQQ` 3x Long, `SQQQ` 3x Short) and institutional Market-on-Close (MOC) flows.
  - Multi-billion dollar leveraged ETFs must rebalance their exposure at the 15:00 CT equity close to maintain their stated 3x leverage multiple. The compounding mathematics dictate that **the greater the daily displacement from the mean (session VWAP), the LARGER the required rebalancing volume**!
  - Auditing the 83 trades filtered out by `Stretch <= 0.50 ATR` reveals that they were the **highest-performing trades in the strategy**, generating **+$19,762.50 in net profit** with an extraordinary expectancy of **+$238.10 per trade** (3.5x higher than the strategy average!).
  - Capping VWAP stretch filters out the massive trend days with the largest rebalancing flows, leaving only low-conviction, choppy sessions where price is oscillating near VWAP.
  - Requiring a pullback to VWAP (V4) turns a momentum rebalancing cascade into an unviable counter-trend trade (-$2,882.50 net loss).
- **Protocol Action**: Zero variants beat the in-sample baseline. Under SignalLab rules, no holdout degrees of freedom are burned. The baseline **`NQLateDayFlow` remains the undefeated production model**.

---

## 2. In-Sample Results Matrix (2018–2022, 5.0 Years)

All figures include full institutional friction ($17.25 RT + 1 tick slip per fill = $27.25 / trade):

| Variant | Strategy Name | Session ID & Dashboard URL | Trades | Win Rate | Gross Profit | Net Profit ($) | Net / Trade | Max DD ($) | NP / DD | $t$-stat | In-Sample Gate |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Base** | `NQLateDayFlow` | [2ee6e880-fb4e-4934-a9b7-d14d24cd629a](http://localhost:9000/#/backtest/2ee6e880-fb4e-4934-a9b7-d14d24cd629a)<br>Dashboard: http://localhost:9000/#/backtest/2ee6e880-fb4e-4934-a9b7-d14d24cd629a | **486** | **52.5%** | **$46,161.17** | **$32,917.67** | **$67.73** | **$16,541.00** | **1.99** | **2.37** | **UNDFEATED BASELINE** |
| **V1** | `NQLDFStretch100` | [c948f300-6d05-40a4-8f0e-8910d267ebfc](http://localhost:9000/#/backtest/c948f300-6d05-40a4-8f0e-8910d267ebfc)<br>Dashboard: http://localhost:9000/#/backtest/c948f300-6d05-40a4-8f0e-8910d267ebfc | 484 | 52.5% | $45,041.17 | $31,852.17 | $65.81 | $16,541.00 | 1.93 | 2.30 | FAILED (Filters 2 trades, lower Net $) |
| **V2** | `NQLDFStretch075` | [0b316e79-1211-4d07-9f50-f601601fd1dc](http://localhost:9000/#/backtest/0b316e79-1211-4d07-9f50-f601601fd1dc)<br>Dashboard: http://localhost:9000/#/backtest/0b316e79-1211-4d07-9f50-f601601fd1dc | 473 | 52.6% | $40,939.50 | $28,050.25 | $59.30 | $15,899.25 | 1.76 | 2.10 | FAILED (-$4.8k Net for only -$641 DD) |
| **V3** | `NQLDFStretch050` | [b236ad9b-dc00-4866-9a06-24dcc54b58a8](http://localhost:9000/#/backtest/b236ad9b-dc00-4866-9a06-24dcc54b58a8)<br>Dashboard: http://localhost:9000/#/backtest/b236ad9b-dc00-4866-9a06-24dcc54b58a8 | 403 | 52.4% | $24,136.92 | $13,155.17 | $32.64 | $14,798.42 | 0.89 | 1.11 | FAILED (-$19.8k Net / cuts 83 best trades) |
| **V4** | `NQLDFPullbackVWAP`| [a866f795-1647-45f1-9630-63c481604974](http://localhost:9000/#/backtest/a866f795-1647-45f1-9630-63c481604974)<br>Dashboard: http://localhost:9000/#/backtest/a866f795-1647-45f1-9630-63c481604974 | 245 | 49.4% | $3,793.75 | -$2,882.50 | -$11.77 | $13,729.25 | -0.21 | -0.32 | FAILED (Unviable / Negative Expectancy) |

---

## 3. Deep-Dive Iteration Logs & Trade Dissection

### Iteration 1: Liberal Stretch Ceiling (`NQLDFStretch100`, `HYP-027 V1`)
- **Session ID**: `c948f300-6d05-40a4-8f0e-8910d267ebfc`
- **Dashboard**: [View on dashboard](http://localhost:9000/#/backtest/c948f300-6d05-40a4-8f0e-8910d267ebfc)
- **Mechanism**: Cap entry distance from session VWAP to $\le 1.00 \times \text{ATR}$.
- **Outcome**: Filtered only 2 trades out of 486. Both were positive winners. Net profit fell slightly to $31,852.17.
- **Conclusion**: Capping at 1.00 ATR is too loose to alter drawdown structure but still chips away at edge.

### Iteration 2: Moderate Stretch Ceiling (`NQLDFStretch075`, `HYP-027 V2`)
- **Session ID**: `0b316e79-1211-4d07-9f50-f601601fd1dc`
- **Dashboard**: [View on dashboard](http://localhost:9000/#/backtest/0b316e79-1211-4d07-9f50-f601601fd1dc)
- **Mechanism**: Cap entry distance from session VWAP to $\le 0.75 \times \text{ATR}$.
- **Outcome**: Trades dropped from 486 to 473. Max Drawdown declined slightly from $16,541.00 to $15,899.25 (-$641.75 / -3.9%), but Net Profit collapsed by **-$4,867.42** (-14.8%). NP/DD degraded from 1.99 to 1.76.
- **Conclusion**: Unfavorable tradeoff: sacrificing $7.58 of profit for every $1.00 of drawdown reduction.

### Iteration 3: Tight Stretch Ceiling (`NQLDFStretch050`, `HYP-027 V3`)
- **Session ID**: `b236ad9b-dc00-4866-9a06-24dcc54b58a8`
- **Dashboard**: [View on dashboard](http://localhost:9000/#/backtest/b236ad9b-dc00-4866-9a06-24dcc54b58a8)
- **Mechanism**: Cap entry distance from session VWAP to $\le 0.50 \times \text{ATR}$ (the optimal Vault Break threshold).
- **Outcome**: Net profit was destroyed, falling from $32,917.67 to $13,155.17 (-$19,762.50 / -60.0%). Expectancy collapsed from $67.73 to $32.64 / trade.
- **Why It Failed**: Detailed auditing of the 83 filtered trades revealed an average net profit of **+$238.10 per trade** with a 53.0% win rate. When price is $> 0.50 \times \text{ATR}$ away from VWAP at 14:00 CT, institutional Leveraged ETF compounding imbalances are at their maximum. Filtering these days out deprives the strategy of its primary profit engine.

### Iteration 4: Pullback to VWAP Gate (`NQLDFPullbackVWAP`, `HYP-027 V4`)
- **Session ID**: `a866f795-1647-45f1-9630-63c481604974`
- **Dashboard**: [View on dashboard](http://localhost:9000/#/backtest/a866f795-1647-45f1-9630-63c481604974)
- **Mechanism**: Require a pullback toward VWAP during the 14:00 bar before entering at 14:05 CT.
- **Outcome**: Total Net Profit turned negative (-$2,882.50). Expectancy fell to -$11.77 / trade.
- **Conclusion**: Pulling back to VWAP at 14:00 CT indicates that the daily trend is losing momentum and mean-reverting. Entering in the direction of the morning move after a deep pullback is the worst possible execution signature.

---

## 4. Final Verdict & Deployment Recommendation

1. **Undefeated Baseline**: The original `NQLateDayFlow` (`Base`) configuration remains strictly superior to all VWAP-stretch filtered variations.
2. **Key Takeaway**: Indicators that eliminate climax exhaustion on mean-reverting or morning range breakouts (like Vault Break) act as **performance poisons** when applied to late-day rebalancing momentum cascades (where overextension is a direct proxy for required institutional flow volume).
3. **Registry Update**: `HYP-027` logged in `tasks/SEARCH_DENOMINATOR_REGISTRY.csv` as `FAILED_IN_SAMPLE_BASE_RETAINED`.
