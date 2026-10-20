# Pre-Registered Research Plan: Sunday Reopen Gap Push (SundayReopenGap)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Objective**: Evaluate whether the Globex Sunday 17:00 CT reopen creates a tradable directional momentum burst in the direction of the weekend gap on E-mini Dow Jones (YM / MYM) and E-mini Nasdaq-100 (NQ / MNQ), under strict Phase 2 candidate gates and adverse slippage tiers.

---

## 1. Market Mechanism & Portfolio Gap

1. **The Catalyst & Structural Flow**:
   * The CME Globex futures market reopens every Sunday at **17:00 CT** (18:00 ET / 23:00 UTC), following a 48-hour cash and futures market closure from Friday afternoon.
   * Over the weekend, geopolitical headlines, macroeconomic developments, and commercial order flow accumulate.
   * At 17:00:00 CT, institutional crossing algorithms and market participants execute accumulated weekend orders simultaneously in a thin opening order book.
   * The weekend gap direction ($Open_{17:00} - Close_{\text{Friday}}$) exhibits immediate directional follow-through as orders clear the book during the first 60 seconds.

2. **Portfolio Fit & Day Overlap**:
   * Operates strictly on **Sunday evening from 17:00:00 to 17:01:00 CT** (a 60-second trade duration).
   * **Zero time overlap** with all weekday RTH strategies in `plan_daily_pnl.csv` (Vault Break, Relative Strength, Late-Day Flow, Monday Long).
   * **Zero asset overlap** with the only active Sunday strategy (CL Sunday Gap Fade on Crude Oil).
   * **Trade Day Overlap**: **< 5%** against the active portfolio.

---

## 2. Rigorous Protocol & Execution Standards

* **In-Sample Design Window**: **2018-01-01 through 2022-12-31** (5 full calendar years).
* **Locked Out-of-Sample Holdout**: **2023-01-01 through 2026-10-09** (tested once without parameter alterations).
* **Candidate Gate (Rule 7)**:
  * In-Sample $t \ge 2.50$ on 2018–2022 data under full CME commissions and slippage.
  * Profit Factor $\ge 1.30$.
  * Positive net P&L across a majority of years ($\ge 4/5$ in-sample years).
  * Out-of-sample holdout must remain net positive.
* **Execution & Friction Standards**:
  * Baseline CME round-turn commissions: $\$10.00$ on YM, $\$14.50$ on NQ.
  * Contract Point Value: YM = $\$5.00/\text{pt}$ (tick = $1.0\text{ pt} = \$5.00$); NQ = $\$20.00/\text{pt}$ (tick = $0.25\text{ pt} = \$5.00$).
  * Adverse exit slippage: 1 tick on all exits.
  * Entry execution: Evaluated across 4 adverse slippage tiers ($0, 1, 2, 4\text{ ticks}$).
* **Roll Filtering**: Skip roll weekends (4th through 20th of March, June, September, December) to prevent false gaps caused by contract expirations.

---

## 3. Pre-Registered Variants (Max 5)

All variants trade in the direction of the weekend gap:
$$\text{Direction} = \text{sign}\left(Open_{17:00} - Close_{\text{Friday}}\right)$$

* **Variant 1 (Baseline / 0 Ticks Entry Slippage)**:
  * Entry: Enter at 17:00:00 first print ($Open_{17:01}$).
  * Exit: Flat at 17:01:00 ($Close_{17:01}$) with 1 tick adverse slippage.
  * Total friction: Commission + 1 tick slippage ($15.00 on YM, $19.50 on NQ).

* **Variant 2 (1 Tick Adverse Entry Slippage — Phase 2 Standard)**:
  * Entry: Enter at $Open_{17:01} + 1\text{ tick}$ adverse slippage.
  * Exit: Flat at 17:01:00 ($Close_{17:01}$) with 1 tick adverse slippage.
  * Total friction: Commission + 2 ticks slippage ($20.00 on YM, $24.50 on NQ).

* **Variant 3 (2 Ticks Adverse Entry Slippage)**:
  * Entry: Enter at $Open_{17:01} + 2\text{ ticks}$ adverse slippage.
  * Exit: Flat at 17:01:00 ($Close_{17:01}$) with 1 tick adverse slippage.
  * Total friction: Commission + 3 ticks slippage ($25.00 on YM, $29.50 on NQ).

* **Variant 4 (4 Ticks Adverse Entry Slippage — Execution Stress Test)**:
  * Entry: Enter at $Open_{17:01} + 4\text{ ticks}$ adverse slippage.
  * Exit: Flat at 17:01:00 ($Close_{17:01}$) with 1 tick adverse slippage.
  * Total friction: Commission + 5 ticks slippage ($35.00 on YM, $39.50 on NQ).

* **Variant 5 (One Minute Late / 17:01:00 to 17:02:00 CT)**:
  * Entry: Enter at $Close_{17:01}$ (after first 60 seconds have passed).
  * Exit: Flat at $Close_{17:02}$ with 1 tick adverse slippage.
  * Total friction: Commission + 2 ticks slippage ($20.00 on YM, $24.50 on NQ).
  * Tests whether directional momentum persists or if edge is exclusively captured within the opening 60 seconds.
