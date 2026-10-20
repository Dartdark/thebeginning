# Research Report: Sunday Reopen Gap Push (SundayReopenGap)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Status**: **REJECTED AS CANDIDATE (Rank C / Validated WATCHLIST #22 - In-Sample $t = 1.85 \text{ to } 2.14 < 2.50$)**  
**Target Instruments**: E-mini Dow Jones (YM / MYM) & E-mini Nasdaq-100 (NQ / MNQ)  
**Execution Standard**: First print at 17:00:00 CT ($Open_{17:01}$) + adverse slippage tiers (0, 1, 2, 4 ticks); exit at 17:01:00 CT ($Close_{17:01}$) + 1 tick adverse slippage; full CME round-turn friction ($10.00 on YM, $14.50 on NQ).

---

## 1. Summary Verdict

Per the Phase 2 testing protocol established in `tasks/PERMANENT_STRATEGY_RULES.md` (*"A strategy is ONLY a candidate if $t \ge 2.5$ on 2018–22 alone under real friction and it stays positive on 2023–26. Otherwise report it as failed"*):

1. **Candidate Gate Verdict**: **Fails Candidate Gate for Immediate Portfolio Addition**.
   * On **YM** (where unadjusted 1-minute data is 100% complete across all 9 years without vendor truncation), in-sample (2018–2022) achieves **$t = 1.85$ (at 1 tick slippage) and $t = 2.14$ (at 0 ticks slippage)** across 200 reopens. Both fall below the mandatory $t \ge 2.50$ threshold.
   * On **NQ**, 2018–2022 data was truncated by the vendor (only 12 reopens contain the 17:00–17:01 bar), yielding $t = 1.98$.
2. **Replication & Watchlist Confirmation**:
   * The study **100% replicates and confirms Claude's findings in WATCHLIST #22** (`analysis/sunday_reopen_test.py`).
   * The structural edge is real: YM produces **+$15,060 net ($t = 2.66$, PF 1.63, 6/9 years positive)** over the full 2018–2026 history under 1 tick entry slippage.
   * NQ produces **+$30,702 net ($t = 2.50$, PF 2.13, 9/9 years positive)** over all available reopens ($n=173$).
3. **Execution Bottleneck (The 60-Second Window)**:
   * **Variant 5 proves that the entire edge evaporates after the first 60 seconds**: Entering at 17:01:00 and exiting at 17:02:00 loses money on both markets (YM: -$7,485, $t = -3.10$; NQ: -$6,468, $t = -1.48$).
   * Capturing the edge requires getting filled at 17:00:00 CT in a thin Globex opening order book.

---

## 2. In-Sample Results (2018-01-01 through 2022-12-31)

### E-mini Dow Jones (YM) — Complete 200-Reopen Sample
*Point Value: $5.00/pt | Tick: 1.0 pt ($5.00) | Round-turn Commission: $10.00*

| Variant | Execution Specification | Trades | Net P&L | Avg / Trade | Win Rate | Profit Factor | $t$-stat | Max Drawdown | Positive Years |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **V1** | 0 ticks entry slippage, 1 tick exit | 200 | +$7,350 | +$36.8 | 50.5% | 1.61 | **2.14** | $1,935 | 4 / 5 |
| **V2** | 1 tick entry slippage (Phase 2 Standard) | 200 | +$6,350 | +$31.8 | 50.0% | 1.51 | **1.85** | $2,235 | 4 / 5 |
| **V3** | 2 ticks entry slippage | 200 | +$5,350 | +$26.8 | 48.5% | 1.41 | **1.56** | $2,535 | 4 / 5 |
| **V4** | 4 ticks entry slippage (Stress Test) | 200 | +$3,350 | +$16.8 | 46.5% | 1.24 | **0.98** | $3,135 | 4 / 5 |
| **V5** | 1-minute late (17:01:00 to 17:02:00) | 200 | -$1,325 | -$6.6 | 39.0% | 0.85 | **-0.78** | $2,025 | 3 / 5 |

*In-Sample Year-by-Year (YM Variant 2 at 1 tick slippage)*:
* 2018: +$2,775
* 2019: +$970
* 2020: +$2,290
* 2021: -$765
* 2022: +$1,080

---

## 3. Holdout Results (2023-01-01 through 2026-10-09)

### E-mini Dow Jones (YM) — 161 Reopens
| Variant | Execution Specification | Trades | Net P&L | Avg / Trade | Win Rate | Profit Factor | $t$-stat | Max Drawdown | Positive Years |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **V1** | 0 ticks entry slippage | 161 | +$9,515 | +$59.1 | 49.7% | 1.85 | **2.12** | $2,205 | 2 / 4 |
| **V2** | 1 tick entry slippage | 161 | +$8,710 | +$54.1 | 1.75 | **1.94** | $2,565 | 2 / 4 |
| **V3** | 2 ticks entry slippage | 161 | +$7,905 | +$49.1 | 45.3% | 1.66 | **1.76** | $2,925 | 2 / 4 |
| **V4** | 4 ticks entry slippage | 161 | +$6,295 | +$39.1 | 44.7% | 1.49 | **1.40** | $3,645 | 2 / 4 |
| **V5** | 1-minute late (17:01:00 to 17:02:00) | 161 | -$6,160 | -$38.3 | 33.5% | 0.35 | **-3.63** | $6,160 | 0 / 4 |

### E-mini Nasdaq-100 (NQ) — 161 Reopens
*Point Value: $20.00/pt | Tick: 0.25 pt ($5.00) | Round-turn Commission: $14.50*

| Variant | Execution Specification | Trades | Net P&L | Avg / Trade | Win Rate | Profit Factor | $t$-stat | Max Drawdown | Positive Years |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **V1** | 0 ticks entry slippage | 161 | +$28,196 | +$175.1 | 59.6% | 2.08 | **2.32** | $3,835 | 4 / 4 |
| **V2** | 1 tick entry slippage | 161 | +$27,390 | +$170.1 | 59.6% | 2.03 | **2.25** | $3,935 | 4 / 4 |
| **V3** | 2 ticks entry slippage | 161 | +$26,586 | +$165.1 | 59.6% | 1.99 | **2.19** | $4,035 | 4 / 4 |
| **V4** | 4 ticks entry slippage | 161 | +$24,976 | +$155.1 | 58.4% | 1.91 | **2.06** | $4,235 | 4 / 4 |
| **V5** | 1-minute late (17:01:00 to 17:02:00) | 161 | -$7,904 | -$49.1 | 41.6% | 0.64 | **-1.87** | $8,434 | 0 / 4 |

---

## 4. Full History Summary (2018–2026)

| Asset | Variant | Trades | Net P&L | Avg / Trade | Win Rate | Profit Factor | $t$-stat | Max Drawdown | Positive Years |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YM** | V1 (0 ticks) | 361 | +$16,865 | +$46.7 | 50.1% | 1.73 | **2.98** | $2,205 | 6 / 9 |
| **YM** | V2 (1 tick) | 361 | +$15,060 | +$41.7 | 48.8% | 1.63 | **2.66** | $2,850 | 6 / 9 |
| **YM** | V4 (4 ticks) | 361 | +$9,645 | +$26.7 | 45.7% | 1.36 | **1.71** | $5,490 | 6 / 9 |
| **YM** | V5 (1-min late) | 361 | -$7,485 | -$20.7 | 36.6% | 0.59 | **-3.10** | $7,720 | 3 / 9 |
| **NQ** | V1 (0 ticks) | 173 | +$31,566 | +$182.5 | 60.7% | 2.18 | **2.58** | $3,835 | 9 / 9 |
| **NQ** | V2 (1 tick) | 173 | +$30,702 | +$177.5 | 60.7% | 2.13 | **2.50** | $3,935 | 9 / 9 |
| **NQ** | V4 (4 ticks) | 173 | +$28,106 | +$162.5 | 59.0% | 2.00 | **2.29** | $4,235 | 9 / 9 |
| **NQ** | V5 (1-min late) | 173 | -$6,468 | -$37.4 | 42.8% | 0.71 | **-1.48** | $8,434 | 4 / 9 |

---

## 5. Structural Findings & Strategic Classification

1. **The Edge is Fast, Concentrated, and Real**:
   * On both YM and NQ, following the direction of the weekend gap at the 17:00:00 reopen produces a statistically robust 5.5 bp expansion during the first 60 seconds.
   * On NQ, it achieves a 60.7% win rate, PF 2.13, and is positive in 9 of 9 years.
2. **Why It Cannot Be Promoted to the Funded Plan Today**:
   * **In-Sample Gate**: On YM (complete data), in-sample $t = 1.85 \text{ to } 2.14$, which fails the strict $t \ge 2.50$ candidate gate.
   * **Execution Bottleneck**: If an automated execution engine misses the opening second or experiences a 60-second delay (Variant 5), the entire edge vanishes and turns into a consistent loser ($t = -3.10$ on YM).
   * **Classification**: Retained as **Rank C / Confirmed WATCHLIST #22**. Recommended for forward paper-trade fill logging on the live VPS before considering real capital allocation.
