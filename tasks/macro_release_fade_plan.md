# Pre-Registered Research Plan: Universal 07:30 Macro Release Fade (MacroReleaseFade)

**Date**: 2026-10-21  
**Author**: Antigravity (under SignalLab Institutional Standards & Rule 9)  
**Target Instrument**: CME E-mini / Micro E-mini Nasdaq-100 Futures (`NQ` / `MNQ`)  
**Data Horizon**: 2018-01-02 to 2026-10-09 (Full 1-minute unadjusted data aggregated to 5-minute bars)  
**In-Sample Window**: 2018-04-01 to 2022-12-31  
**Holdout Window**: 2023-01-01 to 2026-10-09  
**Friction Model**: $17.25 per round-turn on full NQ ($1.72 on MNQ) + 1 tick adverse slippage  

---

## 1. Economic Mechanism & Hypothesis Triplet ($h_j = (m_j, e_j, d_j)$)

### Economic Mechanism ($m_j$)
In our live funded portfolio, `NFP Fade` (Task 08) is one of our cleanest event strategies ($t = 2.6$). It exploits the mechanical overshoot that occurs at 07:30 CT (08:30 ET) on Non-Farm Payroll Fridays. 

However, NFP only occurs once a month. The US Bureau of Labor Statistics (BLS) and Bureau of Economic Analysis (BEA) release other massive market-moving inflation and growth data at the exact same **07:30 CT window**:
- **CPI (Consumer Price Index)**: Monthly (typically 2nd Tuesday or Wednesday)
- **PPI (Producer Price Index)**: Monthly (typically day after CPI)
- **GDP (Advance / Second / Final prints)**: Monthly (last Thursday)
- **Retail Sales**: Monthly (mid-month)

Because pre-market Globex book depth at 07:30 CT is only ~15–25% of regular cash hours, automated headline-reading algorithms cause extreme initial liquidity vacuums, overshooting fair value. By 07:45 CT (15 minutes post-release), institutional market makers absorb the panic, fading the initial displacement before the 08:30 CT equity cash open.

We hypothesize that **any high-volatility 07:30 CT macro release shock** creates a statistically significant mean-reverting fade opportunity, expanding our macro alpha from 1 trade/month to 3–5 trades/month.

### Executable Expression ($e_j$)
1. **Reference Price**: Close of 5-minute bar stamped **07:30 CT**.
2. **Spike Detection**:
   - On Monday–Friday, compute $\text{Range}_{0735} = \text{High}_{0735} - \text{Low}_{0735}$.
   - Maintain a rolling 20-day history of weekday 07:35 ranges.
   - A **Macro Spike** occurs when $\text{Range}_{0735} \ge k \times \text{median}(\text{past 20 } 0735 \text{ ranges})$.
3. **Entry Signal (at close of 07:45 CT bar)**:
   - Compute reaction displacement: $\Delta = \text{Close}_{0745} - \text{Close}_{0730}$.
   - If $\Delta > 0$ (upside knee-jerk spike): **SELL SHORT** next bar at market (fade the rally).
   - If $\Delta < 0$ (downside knee-jerk spike): **BUY LONG** next bar at market (fade the selloff).
4. **Exits**:
   - Fixed Stop: $0.50 \times \text{15-day ATR}$ from entry fill.
   - Mandatory Time Exit: Flat at close of **09:00 CT** bar (30 minutes after cash open; out before regular morning trends develop).
   - No overnight hold; max 1 trade per day.

---

## 2. Pre-Registered Variants to Test

* **Variant 1 (All Weekday 07:30 Spikes — $k = 3.0$)**: Fading any 07:30 release spike Monday through Friday.
* **Variant 2 (Midweek Inflation & Growth Spikes — Tue/Wed/Thu only)**: Strictly isolates CPI, PPI, Retail Sales, and GDP from Friday NFP.
* **Variant 3 (Spike Threshold Sensitivity — $k = 2.5$)**: Looser spike threshold to test sample size expansion.
* **Variant 4 (Spike Threshold Sensitivity — $k = 3.5$)**: Tighter spike threshold (only extreme macro surprises).
* **Variant 5 (Extended Hold to 09:30 or 10:00 CT)**: Evaluating whether the fade continues into the cash open.

---

## 3. In-Sample vs. Holdout Candidate Gates

* **In-Sample Gate (2018-04-01 to 2022-12-31)**:
  - Must achieve $t \ge 2.50$ under full $\$17.25$ friction per NQ.
  - Profit Factor $\ge 1.30$.
* **Holdout Validation (2023-01-01 to 2026-10-09)**:
  - Must remain net positive ($t \ge 1.50$, positive net PnL).
  - Rolling performance slope must not decay ($t_{\text{decay}} > -1.96$).
* **Portfolio Spanning**: Must have zero trade clash with `Vault Break` (which only enters after 10:00 CT) and `Late-Day Flow` (15:00 CT).
