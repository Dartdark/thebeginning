# Strategy Development Plan: NQ Relative Weakness Intraday Short

**Author:** Antigravity (Strategy Developer)  
**Date:** October 20, 2026  
**Target Symbol:** CME Nasdaq-100 Futures (`NQ` / `MNQ`)  
**Secondary Data:** CME E-mini S&P 500 Futures (`ES` / `MES`)  
**Role:** Strategy Builder (targeting the portfolio's severe gap in intraday short exposure)

---

## 1. Market Mechanism & Hypothesis

The current portfolio (`Vault Break`, `Monday Long`, `Relative Strength Longs`, `Overnight Bias ML`) is heavily long-biased during US Regular Trading Hours (08:30–15:00 CT). When equity indices experience sustained selling or distribution, the portfolio suffers simultaneous drawdowns.

**The Edge:**
1. **Capital Rotation:** When institutional capital rotates out of high-beta tech (growth/duration) into value, defensives, or cash, Nasdaq-100 systematically underperforms the S&P 500:
   $$\text{Spread} = \Delta \text{NQ}_{\text{RTH}} - \beta \times \Delta \text{ES}_{\text{RTH}} < 0$$
2. **Breakdown Confirmation:** When NQ displays relative weakness against ES **and** breaks down below its morning reference level (Initial Balance low or morning VWAP) while ES is not in a bull push, the downward momentum is driven by active liquidation.
3. **Addressing the 09:00 Relative Strength Weakness:**
   - The user's 09:00 CT Relative Strength shorts were weak ($t = 2.1$, dropping to $t = 1.1$ post-2023, with a massive \$28.5k max drawdown per NQ) because 09:00 CT is too early, stops were excessive (0.6x daily range = \$2,600+ per NQ), and fixed targets were too distant (1.0x range = \$4,000+), causing profits to evaporate into afternoon mean-reverting squeezes.
   - We fix this with:
     - Later confirmation window (09:30–11:30 CT, post-initial balance).
     - ES non-bullish filter (ES must be below open/flat, preventing fighting broad market rallies).
     - Asymmetric short trade management: ATR-based stop (1.0–1.25x ATR) and a breakeven profit-protection ratchet at +1.0R.
     - Mandatory flat by 15:00 CT.

---

## 2. In-Sample & Out-of-Sample Protocol

- **In-Sample Design Window:** 2018-01-01 to 2022-12-31 (5 years). All architecture and parameter selections occur exclusively here.
- **Candidate Gate:** Must achieve **$t \ge 2.50$** on in-sample data alone, with positive net profit in at least 4 of 5 years.
- **Locked Out-of-Sample Validation:** 2023-01-01 to 2026-10-09 (3.75 years). Run **ONCE** blind without code modifications. Must produce positive net profit and no structural decay.
- **Full History Target:** Combined 2018–2026 $t \ge 3.60$, bootstrap $p < 0.05$ vs random entries.
- **Apex Drawdown Constraint:** On 1 MNQ, maximum historical drawdown must be $< \$1,200$ (well within the \$2,000 trailing limit).
- **Portfolio Overlap Constraint:** Daily P&L correlation against `Vault Break` and existing strategies in `plan_daily_pnl.csv` must be $< 0.15$ (ideally negative).

---

## 3. Pre-Registered Variants (Max 5 on In-Sample 2018–2022)

All variants trade **Shorts Only**, sized at **1 full NQ contract** (\$20/pt, \$17.25 round-turn friction) / **1 MNQ** (\$2/pt, \$1.72 friction), flat by 15:00 CT:

* **Variant 1 (Baseline Relative Weakness at 09:30 CT):**
  - Measure NQ and ES return from 08:30 to 09:30 CT.
  - Signal: NQ underperforming ES by $\ge 0.30\%$ ($\Delta \text{NQ} - 1.2 \times \Delta \text{ES} \le -0.30\%$) AND `NQ Close < 09:30 Low`.
  - Exit: Stop 1.25x ATR, Target 2.0x ATR, flat 15:00 CT.

* **Variant 2 (Initial Balance Breakdown + ES Resistance):**
  - 08:30–09:30 CT Initial Balance (IB).
  - Entry Window: 09:30–11:30 CT.
  - Signal: NQ closes below IB Low AND NQ % change from open $<$ ES % change from open by $\ge 0.25\%$ AND `ES Close < ES Open`.
  - Exit: Stop 1.25x ATR, Target 2.0x ATR, flat 15:00 CT.

* **Variant 3 (Variant 2 + Breakeven Profit Protection Ratchet):**
  - Same entry as Variant 2.
  - Exit: Stop 1.25x ATR, Target 2.0x ATR. Once price moves $+1.0 \times \text{ATR}$ in profit, stop loss moves to Entry (Breakeven). Flat 15:00 CT.
  - *Mechanism:* Prevents winning short momentum moves from turning into full stop-outs during midday short squeezes.

* **Variant 4 (Midday Rotation Short, 10:00–12:30 CT):**
  - Targets the 10:00–12:30 CT European close window.
  - Signal: NQ below 200 SMA on 15m AND NQ underperforming ES by $\ge 0.40\%$ since 08:30 open.
  - Exit: Stop 1.0x ATR, Target 1.75x ATR, flat 14:30 CT.

* **Variant 5 (Dynamic Trailing Stop on IB Breakdown):**
  - Same entry as Variant 2.
  - Exit: Initial stop 1.25x ATR. Trail stop at highest high of last 3 bars (or 15m 20-bar EMA) once $+1.0 \times \text{ATR}$ profit is reached. Flat 15:00 CT.
