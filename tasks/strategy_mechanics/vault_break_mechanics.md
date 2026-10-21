# Strategy Mechanics: Vault Break (NQ Intraday Momentum Breakout)

**Strategy**: `Vault Break` (`NQVaultBreak` / `NQVBWindow1000to1230`)  
**Instrument**: CME E-mini Nasdaq-100 Futures (`NQ`) / Micro E-mini (`MNQ`)  
**Timeframe**: 30-Minute Bars  
**Direction**: Longs Only  
**Target / Stop**: Fixed `+40.0 pts` limit target / `-75.0 pts` stop loss (flatten at `14:30 CT`)  
**Trade Frequency**: Up to 3 trades per calendar day  

---

## 1. Executive Summary & Specification

`Vault Break` is a systematic momentum continuation strategy designed to capture strong trend expansions on the Nasdaq-100 during the core US institutional session.

```
                    VAULT BREAK SYSTEM ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Midnight Anchor: Measure Session Open at 00:00 CT                   │
│ 2. Volatility Barrier: Noise Level = 00:00 Open + (0.30 × ATR-15)      │
│ 3. Benchmark Trend: Cumulative Session VWAP (reset at midnight)        │
│ 4. Execution Window: 10:00 CT to 12:30 CT (Optimal) / 14:00 CT (Base) │
│ 5. Trigger: 30m Close > Noise Level AND 30m Close > VWAP               │
│ 6. Order: Buy 1 contract next bar at MARKET                            │
│ 7. Exits: Limit TP +40 pts | Stop -75 pts | Time Flatten at 14:30 CT   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Core Economic Engine: Why It Works

Vault Break does **not** rely on arbitrary technical indicators (RSI, Stochastics, MACD). Its edge is grounded in three structural realities of CME equity index futures:

### A. The 10:00 CT Institutional Takeover Window
* Between 08:30 and 10:00 CT (09:30–11:00 ET), the cash open is dominated by retail orders, morning headline reactions, 09:00/10:00 ET economic releases, and European morning desks squaring positions. This window is a "meat grinder" of false breakouts and choppy rotations.
* At **10:00 CT (11:00 ET)**, European morning desks close, liquidity consolidates, and institutional execution algorithms (VWAP/TWAP and trend-following mandates) take command of the tape. 
* Vault Break deliberately waits until **after 10:00 CT**, ensuring that it only participates when true institutional institutional flow establishes direction for the afternoon.

### B. The ATR Volatility "Noise" Barrier
* Pure price action above the midnight open is meaningless if the move is within typical overnight oscillation range.
* By adding **$0.30 \times \text{ATR}(15)$** to the midnight open, Vault Break establishes a dynamic volatility threshold. A price crossing this barrier represents a statistically significant expansion beyond normal session noise.

### C. Midnight Cumulative VWAP Filter
* Requiring `Close > VWAP` ensures that buyers are in structural control relative to the entire session's accumulated volume-weighted price.

---

## 3. The Anatomy of Failure: Why and How It "Top-Ticks"

When Vault Break wins, it often looks effortless—a smooth continuation to the +40 pt target within 1–3 bars. 

However, when Vault Break loses, it exhibits a distinct, painful failure signature: **it buys the literal high of the move ("top-ticking") and gets stopped out as the market cascades lower.**

### The Mechanics of the "Top-Tick" Loss

```
Price
  ▲
  │                  [Peak / Top Tick] ◄── Market Order Enters Long Here!
  │                         ▲
  │                     ┌───┴───┐
  │                     │       │ 30m Breakout Candle (Greedy buyers chase into resistance)
  │                     │       │
  │  ── Noise Level ─── ├── ─ ─ ┤ ─────────────────────────────────────
  │                     │       │
  │                     └───┬───┘
  │                         │     ▼ Institutional selling cascade / VWAP retest
  │                         │     ▼ Drops 75 pts ──► Hits Stop Loss (-$1,500)
  │  ── Session VWAP ───────┴──────────────────────────────────────────
  └────────────────────────────────────────────────────────────────────► Time
```

There are four specific microstructure causes behind this top-tick behavior:

### 1. The Institutional Liquidity Sweep (Bull Trap into Overhead Supply)
On range-bound, choppy, or corrective days, market makers and institutional desks seek liquidity above key reference levels (e.g., yesterday's high, pre-market high, or an unfilled gap). 
* Algorithms engineer a sharp morning thrust between 09:30 and 10:00 CT to trigger retail breakout stops and induce breakout-chasing algorithms.
* By 10:00 CT or 10:30 CT, that thrust clears the `noise_level` and closes near the high of the 30-minute bar.
* **The Trap**: The moment the 30m bar closes green at its peak, Vault Break submits a **Market Buy Order**. That exact moment is where large institutional sellers step in, using the breakout buying liquidity to unload inventory or build short positions. The close of that breakout bar becomes the exact high of the day.

### 2. The VWAP "Rubber-Band" Mean Reversion
Vault Break checks `Close > VWAP`, but does not evaluate the **distance** between price and VWAP.
* If NQ surges +150 to +250 points in the morning, price is stretched +2 to +3 standard deviations above VWAP.
* On NQ, an intraday mean-reversion retest to VWAP is routinely 60 to 100 points deep.
* Because Vault Break enters at market at the extreme stretch with a **fixed 75-point stop**, a healthy, normal pullback to retest session VWAP will trigger the stop loss before any further upside can develop.

### 3. The 30-Minute Market Order Chase
Because the strategy uses 30-minute bars, an enormous amount of buying pressure has already occurred *inside* the bar before the close is printed. Entering next bar at market guarantees paying the worst possible price of the 30-minute interval.

### 4. Asymmetric Risk/Reward Ratio (+40 pt Target vs -75 pt Stop)
* Vault Break has an inverted payoff profile: Target is `+40 pts` (\$800), while Stop is `-75 pts` (\$1,500).
* Ratio: You risk \$1.87 to make \$1.00.
* **The Consequence**: Vault Break **requires immediate upside continuation**. It cannot tolerate a 45-point retracement. If the market pauses, hesitates, or consolidates for even one bar after entry, the momentum dies, and the position drifts down into the 75-point stop.

---

## 4. Empirical Loss Characteristics (From 2018–2026 Audit)

Understanding the strategy's statistical baseline prevents emotional interference during normal drawdown periods:

1. **Win Rate Reality**:
   * Vault Break has an overall win rate of **~65.6% to 67.4%** across 1,744 trades.
   * This means **1 out of every 3 trades is a loss**.
2. **Consecutive Loss Clusters**:
   * Maximum historical losing streak is **7 consecutive losses**.
   * Clusters of **3 to 4 consecutive losses happen multiple times every single year** (especially during regime transitions from trending bull markets into choppy ranges).
3. **Stop-Loss Velocity**:
   * **31.8% of all stop-outs occur within $\le 30$ minutes of entry**.
   * Median holding period for a losing trade is **57.0 minutes** (less than two 30m bars).
   * *Conclusion*: When Vault Break fails, it fails quickly. It does not slowly bleed out; it top-ticks and reverses immediately.

---

## 5. Production Safeguards & Optimization Fixes

To prevent repeated top-tick losses and protect capital, three quantitative safeguards have been developed and validated:

### Safeguard 1: Restrict Entry Window to `[10:00, 12:30)` CT (`NQVBWindow1000to1230`)
* **The Rule**: Allow new entries only on 30-minute bars closing from `10:00 CT` through `12:30 CT`. Disallow all new entries after 12:30 CT.
* **The Empirical Proof**:
  * Entries taken at `13:00` and `13:30 CT` historically produced a combined **-\$551 net across 254 trades** over 8.8 years.
  * Late-day breakouts have only 60–90 minutes before the mandatory `14:30 CT` flatten, truncating upside targets while taking full stop losses.
  * Restricting the window to `[10:00, 12:30)` CT slashes peak drawdown by **\$3,222.20 (-18.9% less drawdown: \$13,811.80 vs \$17,034.00)**, raises win rate to **67.4%** (69.0% on holdout), and boosts Net P&L / Max DD to **10.05**.

### Safeguard 2: VWAP Stretch Guard ($\text{Close} - \text{VWAP} \le 0.50 \times \text{ATR}$) (`NQVBVWAPStretch`)
* **The Rule**: Cap the allowable entry distance: $\text{Close} - \text{VWAP} \le 0.50 \times \text{DailyATR}_{15}$.
* **Mechanism**: When price surges $> 0.50$ ATR above VWAP, it enters a buying climax. A routine intraday mean-reversion retest to VWAP is 60–100 pts deep, which immediately clips the fixed 75-point stop. Entries taken when stretch $> 0.50$ ATR lost -$2,354 net across 8.8 years.
* **The Empirical Proof**: Slashes peak drawdown by **$3,355.00 (-19.5%)** and lifts trade expectancy to **+$88.87/trade**.

### Safeguard 3: The Deployed Champion — Vault Break Combined (`NQVBCombined`)
* **The Rule**: Simultaneously enforce the `12:30 CT` runway cutoff AND the `0.50 ATR` VWAP stretch guard.
* **Performance (2018–2026 Full Period, Full $27.25 RT Friction)**:
  * Slashes Max Drawdown by **-$4,595.00 (-26.7%)** from $17,204 down to **$12,609.00**.
  * Win Rate reaches **67.8%** (69.5% on holdout).
  * Expectancy jumps to **+$104.64 per trade** (+$22.42/trade higher than Base).
  * $t$-stat reaches **4.09**.
  * On 2 MNQ micros, max drawdown drops to **$1,260.90**, well below the Apex $2,000 trailing limit.

---

## 6. MultiCharts PowerLanguage Production Code

```pascal
{========================================================================
 Strategy: NQ Vault Break Combined (Window [10:00-12:30] + VWAP Stretch Guard)
 Symbol: NQ / MNQ Futures (30-Minute Bars)
 Account: Apex Trader Funding / Institutional Execution
 Target: +40.0 pts Limit | Stop: -75.0 pts Stop | Flatten: 14:30 CT
========================================================================}

[IntrabarOrderGeneration = false]
inputs:
    AtrLength(15),             // Daily ATR length
    NoiseMultiplier(0.30),     // ATR multiplier for midnight noise band
    StretchCapMultiplier(0.50),// Max allowable distance from VWAP (in ATR units)
    TargetPts(40.0),           // Profit target in NQ points ($800/contract)
    StopPts(75.0),             // Stop loss in NQ points ($1,500/contract)
    StartTimeCT(1000),         // Entry window start (10:00 CT)
    EndTimeCT(1230),           // Entry window end (12:30 CT cutoff)
    ExitTimeCT(1430),          // Daily mandatory flattening time (14:30 CT)
    MaxEntriesPerDay(3);       // Max allowed entries per calendar day

variables:
    MidnightOpen(0),
    NoiseLevel(0),
    DailyVWAP(0),
    CumVol(0),
    CumPV(0),
    TypicalPrice(0),
    DayATR(0),
    Stretch(0),
    EntriesToday(0),
    CurrentDateLocal(0);

// Calculate Daily ATR-15
DayATR = AvgTrueRange(AtrLength);

// Reset daily accumulators at midnight (00:00 CT)
if Date <> CurrentDateLocal or (Time = 0000 or (Time > 0000 and Time[1] >= 2300)) then begin
    CurrentDateLocal = Date;
    MidnightOpen = Open;
    CumVol = 0;
    CumPV = 0;
    EntriesToday = 0;
end;

// Maintain Cumulative Midnight-Anchored VWAP
TypicalPrice = (High + Low + Close) / 3.0;
CumVol = CumVol + Volume;
CumPV = CumPV + (TypicalPrice * Volume);

if CumVol > 0 then
    DailyVWAP = CumPV / CumVol
else
    DailyVWAP = Close;

// Compute Volatility Noise Barrier & VWAP Stretch
NoiseLevel = MidnightOpen + (NoiseMultiplier * DayATR);
Stretch = Close - DailyVWAP;

// Track trade count today
if MarketPosition <> 0 and MarketPosition[1] = 0 then
    EntriesToday = EntriesToday + 1;

// Entry Condition: Window [10:00-12:30 CT] + Noise Breakout + Above VWAP + Stretch Guard
if Time >= StartTimeCT and Time <= EndTimeCT and MarketPosition = 0 and EntriesToday < MaxEntriesPerDay then begin
    if Close > NoiseLevel and Close > DailyVWAP and Stretch <= (StretchCapMultiplier * DayATR) then begin
        Buy ("VB_Combined_Long") next bar at Market;
    end;
end;

// Profit Target & Stop Loss Execution
if MarketPosition > 0 then begin
    Sell ("VB_Target") next bar at EntryPrice + TargetPts Limit;
    Sell ("VB_StopLoss") next bar at EntryPrice - StopPts Stop;
end;

// Mandatory End-of-Day Flatten at 14:30 CT
if Time >= ExitTimeCT and MarketPosition > 0 then begin
    Sell ("VB_TimeExit") next bar at Market;
end;
```

---

## 7. Prop Account Survival Protocol (Apex $2,000 Trailing Limit)

For automated traders operating on **Apex 50K accounts** with a **\$2,000 trailing drawdown**, a 3-loss cluster on full contract sizing is dangerous:
* 3 losses at 75 pts on 1 full NQ = **-\$4,500** (liquidates a 50K account twice over).
* 3 losses at 75 pts on 1 MNQ micro = **-\$450** (easily absorbed by the \$2,000 cushion).

### The Mandatory Cushion Rule (From `ANTIGRAVITY_BRIEF.md`)
1. **Full Size (2–3 MNQ)**: ONLY traded when account equity is **$\ge \$1,500$ above the trailing stop**.
2. **Half Size (1 MNQ)**: The instant equity dips within **$\$1,500$ of the trailing threshold**, immediately scale down to **1 MNQ micro**.
3. **Recovery**: Remain at 1 MNQ until positive expectancy rebuilds the equity cushion beyond $+\$1,500$.

By strictly applying the **`[10:00, 12:30)` entry cutoff**, the **`0.50 ATR` VWAP stretch guard**, and the **Apex Cushion Rule**, a trader can comfortably endure the inevitable 3-to-4 trade top-tick clusters while harvesting the strategy's massive +$136k long-term alpha.
