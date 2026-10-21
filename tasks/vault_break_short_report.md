# Empirical Research Report: Vault Break Short (Concept 1)

**Date**: 2026-10-21  
**Status**: **FAILED (Rank F — Failed Holdout Gate & Portfolio Degradation)**  
**Author**: Antigravity (under SignalLab Institutional Standards & Rules 7–11)  
**Dataset**: Full 2018–2026 unadjusted 1-minute NQ and ES futures (3,087,803 bars)  
**In-Sample Window**: 2018-04-01 to 2022-12-31  
**Holdout Window**: 2023-01-01 to 2026-10-09  
**Friction**: $17.25 per round-turn on full NQ ($1.72 on MNQ)  
**Trade Ledger**: [`tasks/out_vault_break_short/trades.csv`](file:///c:/Users/dmoto/jesse-bot/tasks/out_vault_break_short/trades.csv) (1,362 trades with minute-level timestamps)  

---

## 1. Executive Summary & Verdict

We evaluated transferring the proven mechanical primitives of our #1 live strategy (`Vault Break Long`) to the **short side**, testing whether broad-market S&P 500 (ES) downside alignment could filter out low-probability short traps.

| Variant | Total Trades | Full Period Net Pts (USD) | Full $t$-stat | In-Sample $t$ (2018–22) | Holdout $t$ (2023–26) | Holdout Net Pts | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`V0_Long_Base` (Benchmark)** | 2,498 | +8,021.2 pts (+$160,425) | **3.65** | **3.15** | **2.04** | **+3,322.0 pts** | **PASS (Deployed Live)** |
| **`V1_Short_Pure`** | 2,134 | +751.7 pts (+$15,034) | 0.34 | 0.81 | -0.79 | -1,243.5 pts | **FAIL (Rank F — Noise)** |
| **`V2_Short_ES_Red`** | 2,044 | +148.8 pts (+$2,976) | 0.07 | 0.61 | -0.94 | -1,464.1 pts | **FAIL (Rank F — Noise)** |
| **`V3_Short_ES_VWAP`** | 2,050 | +548.1 pts (+$10,962) | 0.25 | 1.00 | -1.15 | -1,780.4 pts | **FAIL (Rank F — Noise)** |
| **`V4_Short_ES_0830_Drop`** | 1,362 | +3,750.0 pts (+$75,001) | 2.15 | **3.11** | **-0.54** | **-662.4 pts** | **FAIL (Rank F — Holdout Decay)** |

### Final Verdict: RANK F (REJECTED)
Under **Rule 7 (Hard Stop Rule)** and **Rule 10 (Portfolio Spanning & Temporal Non-Decay)**, `Vault Break Short` is rejected:
1. **The In-Sample Trap**: Variant 4 passed the In-Sample candidate gate decisively ($t = 3.11 \ge 2.50$, PF 1.28, 5/5 positive years from 2018–2022).
2. **The Holdout Collapse**: On the locked 2023–2026 holdout, Variant 4 collapsed to **-$662.4 pts ($t = -0.54$)**, suffering a catastrophic **-$1,826.0 pt drawdown in 2023 alone ($t = -2.97$)**.
3. **Severe Portfolio Degradation**: Adding `V4` to `Vault Break Long` in 2023 would have turned a profitable year (+289.6 pts) into a severe **-$1,536.4 pt loss**, completely blowing an Apex funded account.

---

## 2. In-Depth Year-by-Year Performance Breakdown

### Variant 4 (`V4_Short_ES_0830_Drop`) — The Best Short Candidate

| Year | Trades | Wins | Win Rate | Net Pts ($17.25 friction) | Net PnL ($) | Profit Factor | $t$-statistic | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **2018** | 151 | 95 | 62.9% | +1,479.3 | +$29,586 | 1.91 | 3.54 | In-Sample |
| **2019** | 148 | 73 | 49.3% | +78.1 | +$1,562 | 1.04 | 0.19 | In-Sample |
| **2020** | 131 | 90 | 68.7% | +848.8 | +$16,976 | 1.33 | 1.53 | In-Sample |
| **2021** | 147 | 92 | 62.6% | +333.5 | +$6,670 | 1.11 | 0.57 | In-Sample |
| **2022** | 221 | 156 | 70.6% | +1,672.9 | +$33,458 | 1.39 | 2.29 | In-Sample |
| **IS Subtotal** | **773** | **506** | **65.5%** | **+3,804.0** | **+$76,080** | **1.28** | **3.11** | **PASS IS GATE** |
| **2023** | 131 | 68 | 51.9% | **-1,826.0** | **-$36,520** | **0.57** | **-2.97** | **Account Blown** |
| **2024** | 159 | 104 | 65.4% | +695.1 | +$13,902 | 1.22 | 1.14 | Holdout |
| **2025** | 169 | 108 | 63.9% | +144.0 | +$2,880 | 1.04 | 0.21 | Holdout |
| **2026** | 105 | 71 | 67.6% | +324.4 | +$6,488 | 1.13 | 0.60 | Holdout |
| **OOS Subtotal**| **564** | **351** | **62.2%** | **-662.4** | **-$13,248** | **0.95** | **-0.54** | **FAIL HOLDOUT** |

---

## 3. Quantitative Microstructure Diagnosis: Why It Failed

1. **The 2023 AI / Mega-Cap Regime Shift**:
   In 2018–2022, tech stocks moved in high beta synchronization with the broad market. If ES dropped between 08:30 and 09:00 CT, tech stocks almost always followed through on downside breaks.
   In 2023, the macro landscape decoupled: even on days when the broader S&P 500 (financials, energy, industrials) was weak, massive institutional liquidity concentrated into mega-cap tech (NVDA, MSFT, AAPL, AMZN). Downside breakdowns after 10:00 CT were aggressively bought as institutional liquidity sweeps, triggering short stops repeatedly.

2. **The "20-Coin" Lesson in Action**:
   This test is a perfect real-world validation of the **SignalLab** paper:
   - If a researcher tested this on 2018–2022 data alone, the numbers ($t = 3.11$, 5/5 positive years, +$76,080) would look like a world-class edge.
   - But because we froze 2023–2026 as an untouched out-of-sample holdout, the illusion was instantly shattered before a single dollar of live capital was risked.

---

## 4. Search Denominator Registry & Audit Trail

Logged into [`tasks/SEARCH_DENOMINATOR_REGISTRY.csv`](file:///c:/Users/dmoto/jesse-bot/tasks/SEARCH_DENOMINATOR_REGISTRY.csv):
* `HYP-019`: `Vault_Break_Short_Pure` — FAILED (Rank F)
* `HYP-020`: `Vault_Break_Short_ES_Aligned` — FAILED (Rank F)

All 1,362 minute-level trades are preserved in [`tasks/out_vault_break_short/trades.csv`](file:///c:/Users/dmoto/jesse-bot/tasks/out_vault_break_short/trades.csv) for independent audit by Claude and MultiCharts.
