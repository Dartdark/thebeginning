# Research Report: Midday Institutional Lull on YM / ES (MiddayYMES)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Status**: **REJECTED (Rank F - Fails Candidate Gate on 2018–2022 In-Sample)**  
**Target Instruments**: E-mini Dow Jones (YM / MYM) & E-mini S&P 500 (ES / MES)  
**Execution Standard**: Next-minute Open + 1 tick slippage; chronological 1-minute stop/target evaluation; full round-turn CME friction + slippage ($22.25 on YM, $32.25 on ES).

---

## 1. Summary Verdict

Per the strict Phase 2 testing protocol established in `ANTIGRAVITY_BRIEF.md` ("A strategy is only a candidate if $t \ge 2.5$ on 2018–22 alone and it stays positive on 2023–26. Otherwise report it as failed"), **Midday trading on YM and ES during the 11:30–13:30 CT lunch window is decisively rejected**.

All 5 pre-registered variants were significantly negative on 2018–2022 in-sample data. The holdout period (2023–2026) was **not touched**, preserving holdout integrity.

---

## 2. In-Sample Results (2018-01-01 through 2022-12-31)

| Variant | Logic | Trades | Net PnL | Avg / Trade | Win Rate | Profit Factor | t-stat | Max Drawdown | Positive Years |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **V1** | YM Lunch Range Breakout Follow | 1,147 | -$40,408 | -$35.2 | 33.7% | 0.73 | **-4.07** | $44,529 | 1 / 5 |
| **V2** | YM Lunch Range False Breakout Fade | 1,054 | -$32,084 | -$30.4 | 50.7% | 0.69 | **-4.50** | $32,307 | 0 / 5 |
| **V3** | ES AM Trend Fade at London Close (11:30) | 156 | -$25,664 | -$164.5 | 35.9% | 0.51 | **-3.38** | $26,508 | 0 / 5 |
| **V4** | ES Midday Anchored VWAP Reversion | 554 | -$58,214 | -$105.1 | 39.4% | 0.64 | **-4.01** | $59,717 | 0 / 5 |
| **V5** | YM Post-Lunch Channel Expansion | 465 | -$11,141 | -$24.0 | 35.7% | 0.79 | **-1.97** | $12,494 | 0 / 5 |

---

## 3. Structural Autopsy: Why It Failed

1. **Volume Vacuum Equals Driftless Noise**:
   * Following the European cash close at 11:30 CT (16:30 London), institutional participation drops by more than half.
   * The correlation between morning returns (08:30–11:30) and afternoon returns (12:00–13:30) is **0.0026** (pure random walk).
2. **Gross Moves Smaller than Fixed Friction**:
   * The average lunch range on YM is only 73 points. Breakouts average less than 2 points of follow-through before stalling.
   * Round-trip commission plus 2 ticks of bid-ask slippage ($22.25 on YM, $32.25 on ES) exceeds the available gross edge by 3x to 5x.
3. **Fading Fails Due to Occasional Trend Resumption**:
   * Fading false breakouts (Variant 2) has a 50.7% win rate, but when morning trends resume, losses easily overpower small mean-reversion profits (PF 0.69, $t = -4.50$).

---

## 4. Conclusion & Next Recommendation

The 11:30–13:30 CT midday window is an unviable dead zone for discretionary/intraday algorithmic setups. **Candidate 3 is closed as Rank F.**

The only remaining candidate with strong documented empirical backing in `TIER_LIST.md` and **< 5% day overlap** is:
* **Candidate 1: NQ Sunday Reopen Gap Push (17:00–17:01 CT) [WATCHLIST #22]**:
  * Documented in `TIER_LIST.md`: 173 reopens on NQ averaging **+$182 per NQ after costs ($t = 2.6$, 61% win rate, 9/9 years positive)**.
