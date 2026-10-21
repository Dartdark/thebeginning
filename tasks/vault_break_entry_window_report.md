# Research & Optimization Report: Vault Break Entry Window Optimization

**Strategy**: `Vault Break` (`NQVaultBreak` / `NQVBWindow1000to1230`)  
**Symbol / Route**: `NQ-USD` on `Custom Data`, `30m` timeframe  
**Date**: 2026-10-21  
**Author**: Antigravity (Quantitative Strategy Engineer)  
**Framework**: SignalLab Quantitative Standards & `ANTIGRAVITY_BRIEF.md` Phase 2  
**Friction Model**: $17.25 round-turn commission + 1 tick ($5.00) slippage per market/stop fill ($22.25 on limit target fills, $27.25 on stop/time exits)  

---

## 1. Executive Summary & Verdict

We evaluated optimizing the execution entry window for `Vault Break` on CME E-mini Nasdaq-100 futures (`NQ`), testing two primary microstructure mechanisms:
1. **Pruitt Execution Delay Hypothesis** (*TradeStation as a Research Tool*, pp. 183–187): Delaying entry from 10:00 CT to 10:30 CT to bypass post-open retail chop and European morning close settlement.
2. **Late-Day Time-Truncation Hypothesis**: Cutting off new entries after 12:30 CT because positions entered at 13:00–14:00 CT have insufficient runway before the mandatory 14:30 CT flatten.

### Empirical Verdict
* **Delaying Start to 10:30 CT FAILS**: Delaying entry to 10:30 CT flunked the Holdout gate ($t = 1.39$ on 2023–2026). In the 2023–2026 regime, the initial 10:00 CT breakout bar generated **+$39,745 net**; skipping it forfeited the strongest momentum impulse of the session.
* **Restricting Window to `[10:00, 12:30)` CT (`NQVBWindow1000to1230` — V2) PASSES WITH HIGH VALUE**:
  * **In-Sample (2018–2022)**: Achieved the highest $t$-statistic ($t = 2.93$ vs 2.84 Base), highest win rate (65.7% vs 63.8%), and higher profit factor (1.29 vs 1.25), retaining 95.6% of net dollars while slashing 179 trades of friction.
  * **Holdout (2023–2026)**: Slashes Max Drawdown by **$3,222.20 (-18.9% less drawdown: $13,811.80 vs $17,034.00)**, boosts win rate to **69.0%** (vs 67.4% Base), and elevates capital efficiency (NP/DD 5.27 vs 4.63).
  * **Full Period (2018–2026)**: Win rate increases to **67.4%**, Profit Factor to **1.27**, Max Drawdown drops to **$13,811.80**, and NP/DD expands to **10.05** (vs 8.68 Base).

---

## 2. In-Sample Design Window Results (`2018-01-02` to `2022-12-31`)

All 5 pre-registered variants were tested under identical friction:

| Variant | Strategy Name | Entry Window (CT) | Session ID | Dashboard URL | Trades | Win % | PF | Net USD | Max DD $ | NP/DD | $t$-stat |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Base`** | `NQVaultBreakBase` | `[10:00, 14:30)` | `450bb03c-d960-4650-9486-c514f3887120` | [View Dashboard](http://localhost:9000/#/backtest/450bb03c-d960-4650-9486-c514f3887120) | 864 | 63.8% | 1.25 | $68,966.0 | $9,289.2 | 7.42 | 2.84 |
| **`V1`** | `NQVBWindow1030to1430` | `[10:30, 14:30)` | `5959bba9-1818-4297-ad78-61aef7c6d99b` | [View Dashboard](http://localhost:9000/#/backtest/5959bba9-1818-4297-ad78-61aef7c6d99b) | 794 | 62.8% | 1.26 | $61,303.5 | $9,121.8 | 6.72 | 2.70 |
| **`V2`** | `NQVBWindow1000to1230` | `[10:00, 12:30)` | `87cf8813-1298-42cd-ade5-bfd807ca4c9d` | [View Dashboard](http://localhost:9000/#/backtest/87cf8813-1298-42cd-ade5-bfd807ca4c9d) | 685 | **65.7%** | **1.29** | $65,938.8 | $9,261.0 | 7.12 | **2.93** |
| **`V3`** | `NQVBWindow1030to1230` | `[10:30, 12:30)` | `97e2e145-f6e5-474a-9b32-163cf9bff638` | [View Dashboard](http://localhost:9000/#/backtest/97e2e145-f6e5-474a-9b32-163cf9bff638) | 609 | 64.9% | **1.30** | $57,804.8 | **$8,268.2** | 6.99 | 2.80 |
| **`V4`** | `NQVBWindow1000to1330` | `[10:00, 13:30)` | `15d86c30-4a67-4206-91b6-f8c114c65723` | [View Dashboard](http://localhost:9000/#/backtest/15d86c30-4a67-4206-91b6-f8c114c65723) | 808 | 64.2% | 1.25 | $64,987.0 | $10,788.2 | 6.02 | 2.72 |
| **`V5`** | `NQVBWindow1030to1330` | `[10:30, 13:30)` | `faa6dce4-c9b5-48a8-8e67-a992fce7e051` | [View Dashboard](http://localhost:9000/#/backtest/faa6dce4-c9b5-48a8-8e67-a992fce7e051) | 732 | 63.1% | 1.25 | $56,338.0 | $9,345.8 | 6.03 | 2.53 |

---

## 3. Out-of-Sample Holdout Validation (`2023-01-01` to `2026-10-09`)

| Variant | Strategy Name | Entry Window (CT) | Session ID | Dashboard URL | Trades | Win % | PF | Net USD | Max DD $ | NP/DD | $t$-stat |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Base`** | `NQVaultBreakBase` | `[10:00, 14:30)` | `28ebc7d5-1c86-4dcd-9bc8-2cb16f755edf` | [View Dashboard](http://localhost:9000/#/backtest/28ebc7d5-1c86-4dcd-9bc8-2cb16f755edf) | 880 | 67.4% | 1.23 | $78,920.0 | $17,034.0 | 4.63 | 2.76 |
| **`V1`** | `NQVBWindow1030to1430` | `[10:30, 14:30)` | `c2fe18c9-14bb-469b-a4f5-e98f184946e6` | [View Dashboard](http://localhost:9000/#/backtest/c2fe18c9-14bb-469b-a4f5-e98f184946e6) | 826 | 65.4% | 1.11 | $38,336.5 | $15,007.0 | 2.55 | 1.39 (Fail) |
| **`V2`** | `NQVBWindow1000to1230` | `[10:00, 12:30)` | `cdd232e5-7e60-49e9-ab2d-8991805638b8` | [View Dashboard](http://localhost:9000/#/backtest/cdd232e5-7e60-49e9-ab2d-8991805638b8) | 707 | **69.0%** | **1.25** | $72,839.2 | **$13,811.8** | **5.27** | **2.75** |
| **`V3`** | `NQVBWindow1030to1230` | `[10:30, 12:30)` | `4a445bd1-1a3d-4485-82d4-e39274038b04` | [View Dashboard](http://localhost:9000/#/backtest/4a445bd1-1a3d-4485-82d4-e39274038b04) | 619 | 66.9% | 1.14 | $37,322.2 | **$11,702.8** | 3.19 | 1.50 (Fail) |

---

## 4. Full Combined Performance Summary (`2018-01-02` to `2026-10-09`)

| Variant | Window | Trades | Win Rate | Profit Factor | Net USD | Max Drawdown | Net P&L / Max DD | Trades Avoided |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Base`** | `[10:00, 14:30)` | 1,744 | 65.6% | 1.24 | **$147,886.0** | $17,034.0 | 8.68 | Baseline |
| **`V2`** | `[10:00, 12:30)` | **1,392** | **67.4%** | **1.27** | $138,778.0 | **$13,811.8** | **10.05** | **+352 trades avoided** |

---

## 5. Microstructure Diagnosis & Practical Implementation

### Why `[10:00, 12:30)` is the Optimal Production Window
1. **The 13:00–14:00 Friction Drain**:
   Across 8.8 years, trades entered at 13:00 and 13:30 generated a combined **-$551 net** while incurring 254 round-trip commissions and slippage. Eliminating these low-expectancy late entries saves capital and mental capital.
2. **Drawdown Protection for Apex Prop Accounts**:
   Cutting off entries at 12:30 CT reduces peak-to-valley drawdown from **$17,034 down to $13,811 (a savings of $3,222 per contract)**. For accounts governed by a $2,000 trailing drawdown limit, this lower drawdown tail materially increases survival probability on funded combines.
3. **Runway Preservation**:
   Every trade entered before 12:30 CT has at least 2.0 full hours of active cash session trading before the mandatory 14:30 CT flatten, ensuring sufficient runway to hit the +40 pt target without being prematurely liquidated at time.

### Recommendation
* **Combine & Prop Trading (Apex $2,000 Trailing Limit)**: Deploy **`NQVBWindow1000to1230` (V2)** for its lower drawdown ($13.8k vs $17.0k) and higher win rate (67.4%).
* **Unconstrained Personal Capital**: Retain `Base` if maximizing gross points takes absolute priority over drawdown sizing.
