# Pre-Registered Research Plan: Optimizing Vault Break Entry Windows

**Strategy**: `Vault Break` (`NQVaultBreak`, CME E-mini Nasdaq-100 Futures, `NQ-USD` 30m bars)  
**Author**: Antigravity (Quantitative Strategy Engineer)  
**Date**: 2026-10-21  
**Framework**: SignalLab Quantitative Standards (`PERMANENT_STRATEGY_RULES.md` & `ANTIGRAVITY_BRIEF.md` Phase 2)  
**Transaction Friction Model**:
* Commission: $17.25 per round-turn ($0.8625 pts on NQ)
* Slippage: 1 tick ($5.00 / 0.25 pts) per market/stop fill ($0 on limit target fills)
* Total friction: $22.25 on limit target exits, $27.25 on stop/time exits

---

## 1. Economic Mechanism & Literature Grounding

### A. The Pruitt Execution Delay Finding
In *TradeStation as a Research Tool* (Pruitt & Hill, Chapter 8, pp. 183–187), empirical testing on S&P 500 index futures demonstrated:
* Entering at the 08:30 CT cash open resulted in severe maximum adverse excursion (MAE -$2,477).
* Introducing execution delays progressively improved outcomes:
  * 60-min delay (09:30 CT): MAE -$2,161
  * 105-min delay (10:15 CT): MAE -$1,905
  * **120-min delay (10:30 CT)**: Net profit peaked at $39,075 (highest profit) and MAE dropped to a minimum of -$1,851 (lowest drawdown).
* **Driver**: The first 60–90 minutes of the cash session are dominated by opening retail imbalance digestion, 09:00/10:00 ET economic releases, and European morning cash close positioning. By 10:00–10:30 CT, true institutional order flow takes control.

### B. The Late-Day Time-Decay Truncation Trap
In our empirical trade ledger audit of Vault Break (1,755 trades across 2018–2026):
* Entries taken at `13:00` and `13:30 CT` had a combined net performance of **-$551 across 254 trades** (mean +0.04 pts at 13:00; -0.28 pts at 13:30).
* **Driver**: Because all intraday positions are forcibly flattened at `14:30 CT` (or 15:55 CT per Rule 3), entries taken after 12:30 CT have only 60–90 minutes of trading runway. If market momentum slows into the midday lunch lull, the position cannot reach the +40 pt target before time liquidation, while remaining fully exposed to full -75 pt stop-outs.

---

## 2. Pre-Registered Variants (Max 5 Variants)

All variants maintain the identical core Vault Break mechanics:
* 30-minute NQ bars
* Session open from 00:00 CT
* Cumulative session VWAP from midnight
* Volatility noise barrier: `session_open + 0.30 * ATR(15)`
* Brackets: +40 pts take-profit limit, -75 pts stop-loss, 14:30 CT time flatten
* Max 3 trades per calendar day

| Variant | Strategy Name | Allowed Entry Bars (CT) | Market Mechanism |
| :--- | :--- | :---: | :--- |
| **`Base`** | `NQVaultBreakBase` | `10:00 <= t < 14:30` (10:00 to 14:00 bars) | Baseline specification (9 bars). |
| **`V1`** | `NQVB_Window_1030_1430` | `10:30 <= t < 14:30` (10:30 to 14:00 bars) | **Pruitt 120-min Delay**: Drops 10:00 CT bar to avoid post-cash-open false breakouts. |
| **`V2`** | `NQVB_Window_1000_1230` | `10:00 <= t < 13:00` (10:00 to 12:30 bars) | **Morning Execution Only**: Eliminates 13:00-14:00 bars so every trade has $\ge 2$ hrs runway before 14:30 flatten. |
| **`V3`** | `NQVB_Window_1030_1300` | `10:30 <= t < 13:00` (10:30 to 12:30 bars) | **Sweet-Spot Window**: Combines Pruitt delay with early afternoon cutoff (10:30–12:30 bars). |
| **`V4`** | `NQVB_Window_1000_1330` | `10:00 <= t < 14:00` (10:00 to 13:00 bars) | **Extended Midday Window**: Drops only late-day 13:30 & 14:00 bars, preserving 12:30 entries. |
| **`V5`** | `NQVB_Window_1030_1330` | `10:30 <= t < 14:00` (10:30 to 13:00 bars) | **Balanced Trend Window**: Starts after 10:00 noise, ends before 13:30 decay. |

---

## 3. Two-Period Decision Protocol (Rule 7 & Brief Phase 2)

1. **In-Sample Design Window (`2018-01-02` to `2022-12-31`)**:
   * All 5 variants evaluated strictly on In-Sample data.
   * Hurdle: Must achieve $t \ge 2.50$ under full friction.
   * Selection: Variant with highest Sharpe, highest Net $, and lowest Max DD chosen as candidate winner.
2. **Holdout Validation Window (`2023-01-01` to `2026-10-09`)**:
   * Selected design winner(s) tested **ONCE** on holdout.
   * Promotion Gate: To beat baseline, must beat `Base` in **BOTH** Design (2018–2022) and Holdout (2023–2026) on **BOTH** Net $ per contract AND Max Drawdown, with flat by 15:59 CT.
