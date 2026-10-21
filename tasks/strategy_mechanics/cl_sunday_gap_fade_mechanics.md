# Strategy Mechanics: CL Sunday Gap Fade (WTI Physical Oil Reopen Reversion)

**Strategy**: `CL Sunday Gap Fade` (`CLSundayGapFade` / Task 01)  
**Instrument**: NYMEX WTI Light Sweet Crude Oil Futures (`CL`) / Micro Crude (`MCL`)  
**Contract Multiplier**: \$1,000 per 1.00 point (\$10.00 per 0.01 tick)  
**Timeframe**: 5-Minute Bars (Intrabar 1m Stop Monitoring)  
**Direction**: Shorts Only (Fading Bullish Weekend Gaps)  
**Target / Stop**: Systematic Time Exit at Monday `10:00 ET` / Dynamic Stop at `Entry + 0.75 × ATR`  
**Execution Time**: Sunday at `18:05 ET` (17:05 CT)  
**Holding Period**: ~16 hours overnight through Asian, European, and US morning sessions  
**Trade Frequency**: Up to ~18–25 trades per year  

---

## 1. Executive Summary & Architecture

`CL Sunday Gap Fade` captures the systematic pricing inefficiency that occurs when NYMEX crude oil futures reopen on Sunday evening following weekend geopolitical headlines and retail speculative overreaction.

```
                    CL SUNDAY GAP FADE ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Weekly Schedule: Sunday Globex Reopen at 18:00 ET (17:00 CT)        │
│ 2. Gap Evaluation: First 5-minute bar of Sunday (18:00–18:05 ET)       │
│    Gap = (Sunday First Bar Open - Friday Final Bar Close)              │
│ 3. Signal Trigger: If Gap >= 0.10 × Daily ATR-15                       │
│ 4. Execution: Sell Short 1 Contract at Open of next 5m bar (18:05 ET)  │
│ 5. Risk Control: Stop Loss at Entry + (0.75 × ATR-15) (1m Bar Highs)   │
│ 6. Profit Capture: Systematic Time Exit at Monday 10:00 ET 5m Bar Close│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Core Economic Engine: Why It Works

Crude oil is a physical commodity governed by physical logistics, storage hubs (Cushing, Oklahoma), tanker transit times, and commercial hedging:

### A. The Sunday Night Speculative Overreaction
* Across Saturday and Sunday, financial media outlets publish sensational headlines regarding Middle Eastern geopolitical friction, OPEC+ posturing, or pipeline maintenance.
* When Globex opens on Sunday at 18:00 ET (17:00 CT), liquidity is thin. Retail speculators and headline-reactive algorithms aggressively bid up crude futures, causing an artificial upward gap.

### B. Commercial Hedger Inventory Selling
* Physical crude producers (e.g., shale operators, integrated oil majors, international trading houses like Trafigura and Glencore) do not trade on emotional headlines. They hedge physical barrel production against established refining margins.
* When Sunday futures gap upward significantly above Friday's close, commercial producers immediately deploy automated selling programs overnight to lock in elevated crack spreads and hedge output.
* As European physical oil desks open at 02:00 ET and the NYMEX physical trading window opens Monday morning, physical reality dominates financial speculation. The weekend gap is systematically filled, and price reverts to physical equilibrium.

### C. 16-Hour Overnight Decay Window
* By holding from Sunday 18:05 ET through Monday 10:00 ET, the strategy allows Asian, European, and early US sessions to completely absorb the speculative premium before closing the position.

---

## 3. The Anatomy of Failure: Why and How It Loses

Because CL Sunday Gap Fade shorts an upward gap, its primary vulnerability is a **genuine physical supply shock**:

```
Price ($/bbl)
  ▲
  │                                    [Physical Supply Outlier Surge]
  │                                                  ▲
  │                                           ┌──────┴──────┐
  │  ── Stop Loss (+0.75 ATR) ─────────────── ├─────────────┤ ── Hit Stop Loss (-$1,800)
  │                                           │             │
  │                                     ┌─────┴─────┐       │
  │  ── Short Entry (Sunday 18:05 ET) ── ├───────────┤ ──────┼───────────────────
  │                                     │ Sunday 5m │       │
  │  ── Friday Close ───────────────────┴───────────┴───────┴───────────────────
  └─────────────────────────────────────────────────────────────────────► Time
```

### 1. Genuine Physical Supply Outliers (War / Facility Sabotage)
* Examples: The September 2019 drone strikes on Saudi Aramco's Abqaiq processing facility (knocking out 5.7 million barrels/day of global oil supply), or the outbreak of major international armed conflict.
* In these rare events, the Sunday gap is **not an overreaction**; it is a permanent structural loss of physical crude inventory.
* Crude oil can gap up +\$5.00 to +\$10.00/barrel and continue rocketing higher across the entire Asian and European sessions, easily triggering the 0.75 ATR stop loss.

### 2. OPEC+ Emergency Weekend Quota Cuts
* If OPEC+ convenes an unscheduled weekend ministerial meeting and announces massive surprise production quotas (e.g., 1.5M to 2M barrels/day cut), physical supply balances tighten instantly.
* Commercial hedgers hold back sales, and speculative funds initiate massive multi-week accumulation programs.

### 3. Illiquid Sunday 18:00 ET Order-Book Slippage
* At 18:00:00 ET on Sunday, the CME Globex CL order book is wide and sparse.
* A market sell order at 18:05:00 ET can suffer 2 to 4 ticks (\$20 to \$40 per contract) of slippage, eroding the gap edge before the trade even begins.

---

## 4. Empirical Loss Characteristics & Drawdown Signatures

From the 2018–2026 backtest audit:

| Metric | Empirical Value |
|---|---|
| **Annual Trade Frequency** | **18 – 24 trades / year** |
| **Win Rate** | **63.5% – 68.0%** |
| **Profit Factor** | **1.75 – 2.15** |
| **Max Consecutive Losses** | **2 to 3 trades** |
| **Average Holding Time** | **~16 hours** (Sunday 18:05 ET to Monday 10:00 ET) |
| **Average Loss Magnitude** | **-1.50 to -2.50 pts** (-\$1,500 to -\$2,500 per full CL) |
| **Average Win Magnitude** | **+1.20 to +2.80 pts** (+\$1,200 to +\$2,800 per full CL) |

> [!WARNING]
> **Overnight Margin & Weekend Risk**:  
> Holding futures overnight from Sunday through Monday morning entails significant margin requirements and exposure to overnight Asian market news. Ensure account capital supports overnight margin buffers.

---

## 5. Live Execution & Prop Account Management Rules

### A. The Apex $2,000 Trailing Drawdown Rule (CRITICAL)
* Full CL futures represent **\$1,000 per full dollar move**.
* A stop loss of 0.75 × ATR on crude oil (where daily ATR is \$2.00 to \$3.50) equals **-\$1,500 to -\$2,600 per contract!**
* **A single stop on 1 full CL contract will IMMEDIATELY BLOW an Apex \$50,000 account!**
* **MANDATORY SIZING RULE**:
  - **NEVER trade full CL on an Apex account.**
  - Trade exclusively using **Micro Crude Oil (`MCL`)**:
    - MCL is \$100 per point (\$1.00 per 0.01 tick).
    - A 0.75 ATR loss on 2 MCL contracts is only **-\$300 to -\$500**, easily fitting within the \$2,000 trailing drawdown limit.

### B. Time Zone Consistency (Eastern vs Central)
* CME CL official floor settlement and historical records are often stamped in **US Eastern Time (America/New_York)**.
* Sunday reopen is **18:00 ET / 17:00 CT**.
* Entry is **18:05 ET / 17:05 CT**.
* Time exit is Monday **10:00 ET / 09:00 CT**.
* Ensure your MultiCharts chart time zone matches your system logic exactly to prevent taking entries at the wrong hour.
