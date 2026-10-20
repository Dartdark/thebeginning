# Research Report: NQ Turnaround Tuesday Reversal (NQTurnaroundTuesday)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Status**: **REJECTED (Rank F - Fails Candidate Gate on 2018–2022 In-Sample)**  
**Target Instrument**: CME Nasdaq-100 Futures (NQ / MNQ)  
**Execution Standard**: Next-minute Open + 1 tick slippage (0.25 pt); chronological 1-minute stop/target evaluation (stop-loss takes precedence on tie); $17.25 RT friction per NQ contract.

---

## 1. Summary Verdict

Per the strict Phase 2 testing protocol established in `ANTIGRAVITY_BRIEF.md` ("A strategy is only a candidate if $t \ge 2.5$ on 2018–22 alone and it stays positive on 2023–26. Otherwise report it as failed"), **NQ Turnaround Tuesday Reversal is decisively rejected**.

All 5 pre-registered variants failed to achieve $t \ge 2.5$ on 2018–2022 in-sample data. The holdout period (2023–2026) was **not touched**, preserving holdout integrity.

---

## 2. In-Sample Results (2018-01-01 through 2022-12-31)

| Variant | Logic | Trades | Net PnL (per NQ) | Avg / Trade | Win Rate | Profit Factor | t-stat | Max Drawdown | Positive Years |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **V1** | Down Monday $\rightarrow$ Tuesday Open & Prior High Breakout | 60 | +$6,176 | +$102.9 | 53.3% | 1.14 | **0.41** | $9,868 | 3 / 5 |
| **V2** | Extreme Down Monday ($\le -1.0\%$) $\rightarrow$ Close > Open | 33 | +$921 | +$27.9 | 45.5% | 1.03 | **0.06** | $13,248 | 3 / 5 |
| **V3** | Bidirectional Monday Extension Fade (Range $> 1.0\times$ R20) | 73 | +$19,971 | +$273.6 | 47.9% | 1.44 | **1.20** | $9,550 | 4 / 5 |
| **V4** | Tuesday 30m OR Breakout in Turnaround Direction | 48 | +$5,911 | +$123.2 | 50.0% | 1.21 | **0.50** | $9,042 | 3 / 5 |
| **V5** | Tuesday Anchored VWAP Reclaim | 85 | -$1,472 | -$17.3 | 49.4% | 0.98 | **-0.07** | $20,550 | 3 / 5 |

*Note: In Variant 3 (the best of the 5 variants): 2018: +$3,796; 2019: +$3,960; 2020: +$8,665; 2021: +$9,077; 2022: -$5,527. While it is positive in 4 of 5 years, $t = 1.20$ is far below our mandatory $t \ge 2.5$ threshold.*

---

## 3. Structural Autopsy: Why It Failed

1. **Insufficient Sample Breadth / Low Trade Count**:
   * Restricting entries strictly to Tuesdays conditioned on Monday's direction yields only ~12 to 18 trades per year (33 to 85 trades across the entire 5-year in-sample period).
   * Even when average trade expectation is mildly positive ($+$100 to $+$270), the small sample size leaves the statistical significance well below our $t \ge 2.5$ candidate bar.
2. **Continuation vs. Reversal Regimes**:
   * In strong trending markets (such as 2020 and 2022), strong Monday sell-offs frequently continued cascading lower on Tuesday rather than reversing, causing severe drawdowns on long reversal attempts.
3. **Friction Drag**:
   * After paying $17.25 round-turn commission plus tick slippage on market entry, marginal edges of 5–10 points are degraded into $t \approx 0.5–1.2$.

---

## 4. Conclusion & Next Steps

Turnaround Tuesday does not provide a strong enough standalone edge to meet our candidate gate. **Variant 4 is closed as Rank F.**

From our remaining candidate list, **Candidate 1 (NQ Sunday Reopen First-Minute Gap Push, WATCHLIST #22)** has the strongest documented prior evidence in `TIER_LIST.md` (+$182/trade after costs, $t = 2.6$, 9/9 years positive, < 5% day overlap) or **Candidate 2 (COMEX Gold London PM Benchmark Fixing on GC/MGC)**.
