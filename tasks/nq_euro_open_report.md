# Research Report: NQ European Open Cash Expansion (NQEuroOpenExp)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Status**: **REJECTED (Rank F - Fails Candidate Gate on 2018–2022 In-Sample)**  
**Target Instrument**: CME Nasdaq-100 Futures (NQ / MNQ)  
**Execution Standard**: Next-minute Open + 1 tick slippage (0.25 pt); chronological 1-minute stop/target evaluation (stop-loss takes precedence on tie); $17.25 RT friction per NQ contract.

---

## 1. Summary Verdict

Per the strict Phase 2 testing protocol established in `ANTIGRAVITY_BRIEF.md` ("A strategy is only a candidate if $t \ge 2.5$ on 2018–22 alone and it stays positive on 2023–26. Otherwise report it as failed"), **NQ European Open Cash Expansion is decisively rejected**.

All 5 pre-registered variants failed the in-sample candidate gate on 2018–2022 data. The holdout period (2023–2026) was **not touched**, preserving holdout integrity.

---

## 2. In-Sample Results (2018-01-01 through 2022-12-31)

| Variant | Logic | Trades | Net PnL (per NQ) | Avg / Trade | Win Rate | Profit Factor | t-stat | Max Drawdown | Positive Years |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **V1** | 15m OR Breakout (02:15–03:30 entry) | 1,108 | -$24,671 | -$22.3 | 37.5% | 0.90 | -1.37 | $25,654 | 2 / 5 |
| **V2** | 30m OR Breakout (02:30–04:00 entry) | 1,028 | -$8,656 | -$8.4 | 39.7% | 0.96 | -0.48 | $21,088 | 2 / 5 |
| **V3** | Asian Range Breakout (02:00–03:30 entry) | 993 | -$34,240 | -$34.5 | 34.6% | 0.84 | -2.07 | $38,560 | 0 / 5 |
| **V4** | 30m OR + Vol Expansion (>1.25x MA) | 952 | -$8,910 | -$9.4 | 39.6% | 0.96 | -0.52 | $18,969 | 2 / 5 |
| **V5** | 30m OR + 200 SMA Trend Filter | 635 | -$3,217 | -$5.1 | 39.5% | 0.98 | -0.23 | $18,840 | 1 / 5 |
| *Control* | Fading 30m OR (Mean Reversion) | 980 | -$16,377 | -$16.7 | 41.0% | 0.89 | -1.22 | $24,190 | 0 / 5 |

*Note: Yearly breakdown for baseline Variant 2: 2018: +$1,405; 2019: -$2,624; 2020: +$2,297; 2021: -$5,176; 2022: -$4,559.*

---

## 3. Structural Autopsy: Why It Failed

1. **Lack of Directional Persistence**:
   * The correlation between the initial 30-minute European cash open move (02:00 to 02:30 CT) and the subsequent morning drift (02:30 to 06:00 CT) across 1,287 sessions is **-0.011** (statistically identical to pure random walk).
   * Filtering for large opening expansions ($\ge 1.0$ ATR or $\ge 2.0$ ATR) yielded zero persistent follow-through ($+$1.2 pts up, $-$2.7 pts down).
2. **Thin Globex Liquidity vs. Friction Drag**:
   * European cash markets (DAX, FTSE) trade actively at 02:00 CT, but US equity index futures (NQ) trade on secondary Globex overnight volume without US primary market makers.
   * Typical 15-minute overnight ATR is only 15–25 points. Over 1,000 trades, paying $17.25 round-turn commission plus bid-ask slippage on compressed overnight ranges causes continuous negative friction decay.
3. **Fade / Mean-Reversion Also Fails**:
   * A counter-trend control fading the 30m opening range back to the midpoint also lost -$16.7/trade ($t = -1.22$, 0/5 years positive), confirming that the session is noisy chop rather than clean mean reversion.

---

## 4. Conclusion & Next Recommendation

European Open breakouts on NQ are an unviable candidate for the Apex portfolio. Per our decision rule, **Variant A is closed as Rank F**.

The real viable alpha opportunities in our data lie in **mechanisms with forced institutional rebalancing or cross-market divergence during liquid RTH hours**:
1. **Intraday Shorts via Relative Weakness Re-engineering**: Calibrating the short leg of NQ vs. ES relative divergence during RTH (09:00–11:30 CT) without lookahead fills and with wide R:R targets that survive full friction.
2. **Midday Institutional Volume Vacuum (11:30–13:30 CT)**: Fading extreme morning extensions specifically after the European cash close at 11:30 CT.
