# Pre-Registered Research Plan: COMEX Gold Asian-Range Breakout (GoldAsianBreakout)

**Date**: 2026-10-20  
**Author**: Antigravity (Strategy Builder)  
**Target Instrument**: CME Micro Gold Futures (`MGC` — $10 / pt, tick $0.10 = $1.00; GC benchmark = $100 / pt)  
**Classification Target**: Standalone Diversifier / Funded Portfolio Addition (Watchlist #6)  
**Objective**: Transform the verified raw Asian-range breakout edge on COMEX Gold into an institutional, risk-managed strategy capable of passing the Apex 50K trailing drawdown threshold ($2,000 cushion).

---

## 1. Structural Market Mechanism & Why It Works

1. **The Institutional Order Flow Mechanics**:
   * **Asian Base Building (20:00–00:00 CT)**: During Tokyo/Hong Kong/Shanghai trading, physical bullion liquidity forms a well-defined, consolidated price bracket.
   * **European / London Pre-Open Thrust (00:00–02:00 CT)**: London physical bullion fixing desks, European central bank reserves, and Swiss refiners begin positioning ahead of the European cash open.
   * **Breakout Realization**: Clean breakouts of the Asian high/low during the 00:00–02:00 CT window capture persistent institutional trend continuation that extends through the European morning (exiting at 12:00 CT).
2. **True Asset Class Diversification**:
   * Correlation with NQ equity index strategies (`Vault Break`, `Relative Strength`, `Late-Day Flow`): **$r \le 0.02$ (Zero correlation)**.
   * Bullion moves on real interest rate expectations, sovereign central bank accumulation, and currency debasement—completely orthogonal to US tech equities.

---

## 2. Solving the Historical Flaw (Why It Was Previously Parked in Tier C)

* **The Problem Identified in Prior Audits**:
  * The raw Asian breakout had a verified positive edge ($+0.078\text{ R}$ to $+0.106\text{ R}$, $t = 2.0$, 7/9 positive years, $113–$140/GC).
  * However, with an open-ended hold to 12:00 CT and a full $1.0\times$ range stop, the win rate was low (~38%), producing extended losing streaks of 13–19 trades ($-\$3,100$ to $-\$4,200$ per MGC), which breached the Apex $\$2,000$ trailing threshold.
* **The Structural Solutions to Test**:
  1. **Filter B (Pre-London Execution Only)**: Unfilled orders cancelled at 02:00 CT (eliminates low-expectancy late European fills).
  2. **Filter D (Daily Counter-Trend Alignment)**: Trade breakouts strictly *opposite* to yesterday's daily candle direction (exploits multi-day inventory exhaustion; in Claude's filter test, this slashed max DD by 36% to $2,187/MGC and lifted average trade to $140/GC).
  3. **ATR Risk-Managed Bracket (Target + Stop)**: Cap downside risk at $0.5\times \text{ATR}_{14}$ or $1.0\times$ range, with defined profit targets at $1.0\times$ and $1.5\times$ range to harvest gains and reduce adverse excursion.

---

## 3. Protocol & Execution Standards

* **In-Sample Design Window**: **2018-01-01 through 2022-12-31** (5 calendar years).
* **Locked Out-of-Sample Holdout**: **2023-01-01 through 2026-10-09** (tested ONCE only if an in-sample variant passes).
* **Candidate Gate (Rule 7)**:
  * In-Sample $t \ge 2.00$ on 2018–2022 under full CME commissions and 1 tick adverse slippage.
  * Profit Factor $\ge 1.25$.
  * Max drawdown $\le \$2,000$ on 1 MGC.
  * Standalone $t \ge 1.0$ and positive P&L on the 2023–2026 holdout.
* **Friction & Contract Specs**:
  * Micro Gold (`MGC`): Point Value = $\$10.00$. Minimum Tick = $0.10$ ($\$1.00$).
  * Slippage: 1 tick adverse on entry ($0.10\text{ pt} = \$1.00$), 1 tick adverse on stop/target exit.
  * Commission: $\$3.00$ round-turn per MGC (Apex / CME rate). Total friction = $\$5.00$ per round-turn.

---

## 4. Pre-Registered Variants (Max 4 Variants)

All variants calculate the Asian Range as High and Low between **20:00 CT and 00:00 CT**:

| Variant | Entry Orders Placed | Cancel Time | Filter D (Yesterday) | Stop Loss | Profit Target | Time Exit |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **V1 (Benchmark B)** | 00:00 CT Stop Orders | 02:00 CT | None (Both Sides) | $1.0\times$ Range | None | 12:00 CT |
| **V2 (B + D Counter)** | 00:00 CT Stop Orders | 02:00 CT | Opp. Yesterday | $1.0\times$ Range | None | 12:00 CT |
| **V3 (B + Target 1.5R)** | 00:00 CT Stop Orders | 02:00 CT | None (Both Sides) | $1.0\times$ Range | $1.5\times$ Range | 12:00 CT |
| **V4 (B + D + Target 1.5R)** | 00:00 CT Stop Orders | 02:00 CT | Opp. Yesterday | $1.0\times$ Range | $1.5\times$ Range | 12:00 CT |

---

## 5. Strict Code & Trades Alignment Guarantee

The strategy Python class `GoldAsianBreakout` and its companion replication script will execute the exact identical order logic, bar-by-bar traversal, tick friction, and time windows.
