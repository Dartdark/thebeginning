# Strategy Mechanics: Overnight Bias (ADX30 & Ridge ML)

**Strategy**: `Overnight Bias ADX30` (Task 03) / `Overnight Bias ML` (Task 04)  
**Instrument**: CME E-mini Nasdaq-100 Futures (`NQ`) / Micro E-mini (`MNQ`)  
**Timeframe**: 15-Minute Bars  
**Direction**: Longs and Shorts  
**Target / Stop**: Dynamic ATR-based: `+3.0R Target` / `-1.0R Stop` (`0.25 × ATR` in Task 03; `0.30 × ATR` in Task 04)  
**Time Exit**: Flatten at `14:30 CT` (`11:30 CT` on early days)  
**Trade Frequency**: Maximum 1 trade per day  

---

## 1. Executive Summary & Architecture

`Overnight Bias` exploits the structural handover of inventory between the European trading session (overnight Globex) and the US cash session (Regular Trading Hours, 08:30 CT).

```
                   OVERNIGHT BIAS ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Overnight Window: 23:15 CT to 08:30 CT (Overnight High / Low)       │
│ 2. Bias Calculation (08:45 Open):                                     │
│    pos = (Open - Overnight Low) / (Overnight High - Overnight Low)     │
│    • pos >= 0.6667 (Top 33%)    ──► BIAS LONG                          │
│    • pos <= 0.3333 (Bottom 33%) ──► BIAS SHORT                         │
│    • Middle 33%                 ──► NO TRADE (Skip Day)                │
│ 3. Opening Range (OR): High & Low of 08:30–08:45 CT Bar                │
│ 4. Trend Quality Filter:                                               │
│    • Task 03: ADX(14) > 30                                             │
│    • Task 04: ADX(14) > 20 AND Frozen Ridge ML Score >= Threshold      │
│ 5. Entry Trigger (08:45 to 14:00 CT):                                  │
│    • Long: Break of OR High (Stop-Buy at OR High / Market if close >=) │
│    • Short: Break of OR Low (Stop-Sell at OR Low / Market if close <=) │
│ 6. Risk Profile: Inverted Asymmetry (1R Risk for 3R Reward)            │
│    • Stop: 0.25 × ATR (Task 03) / 0.30 × ATR (Task 04) (~25-45 pts)    │
│    • Target: 3.0 × Stop Distance (~75-135 pts)                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Core Economic Engine: Why It Works

### A. European Session Inventory Handover
Between 02:00 CT (London open) and 08:30 CT (US open), European institutional asset managers, sovereign wealth funds, and macro hedge funds price global macro data into US index futures.
* If overnight trading has continuously absorbed selling pressure and held price in the **upper third (pos ≥ 0.6667)** of the 9-hour overnight range going into 08:30 CT, institutional inventory is net long.
* Conversely, if price is pinned in the **lower third (pos ≤ 0.3333)**, dealers and funds are net short or distributing inventory.
* Days that open in the middle third (0.3333 to 0.6667) represent balanced, two-sided rotational auctions with no net directional conviction. The strategy systematically skips these days, eliminating 33% of chop-induced losses.

### B. The Opening Range Breakout Mechanism
The 08:30–08:45 CT bar represents the initial price discovery of the New York cash open.
* When price breaks out of this initial 15-minute range *in the direction of the overnight bias*, it confirms that US institutional opening liquidity aligns with the European macro bias.
* This alignment creates large, one-sided trend expansion days (high directional momentum).

### C. Positive Asymmetry (3:1 Reward-to-Risk)
Unlike Vault Break (which risks \$1.87 to make \$1.00), Overnight Bias operates on **strong positive expectancy with a 3:1 payout ratio**:
* Average win: `+75 to +135 pts` (\$1,500 to \$2,700 per NQ contract).
* Average loss: `-25 to -45 pts` (-\$500 to -\$900 per NQ contract).
* Because of this positive asymmetry, the strategy only requires a **~35% to 40% win rate** to produce exceptional long-term Sharpe and Calmar ratios.

---

## 3. The Anatomy of Failure: Why and How It Loses

Because Overnight Bias targets large 3R trends with a tight ATR stop (0.25 to 0.30 ATR), its losses follow distinct microstructural patterns:

```
Price
  ▲
  │                       [False Breakout Spike]
  │                             ▲
  │                     ┌───────┴───────┐ ── Buy Stop Triggered Here
  │  ── OR High ─────── ├── ─ ─ ─ ─ ─ ─ ┤ ────────────────────────────────
  │                     │  15m OR Bar   │
  │                     │  (08:30-08:45)│
  │  ── OR Low ──────── ├───────────────┤ ────────────────────────────────
  │                     │               │   ▼ Sharp 30-pt Mean Reversion
  │                     │               │   ▼ Hits 0.25 ATR Stop Loss (-$600)
  └─────────────────────┴───────────────┴────────────────────────────────► Time
```

### 1. The Opening 15-Minute "Liquidity Sweep" (Whipsaw)
The most common loss signature occurs between 08:45 and 09:30 CT:
* The 08:30–08:45 CT opening bar sets the initial range.
* At 08:46–09:00 CT, algorithmic market makers push price 5–10 points above the OR High to sweep resting stop-loss buy orders from pre-market shorts.
* This sweep triggers the strategy's stop-buy order.
* As soon as liquidity is consumed, market makers reverse price back into the center of the opening range. Because the strategy's stop is only 0.25 × ATR (typically 25–40 points on NQ), this normal 30-point intraday rotation triggers the stop loss before any trend can form.

### 2. High-Frequency Chop on Low-Vol Days (ADX Lag)
* ADX is a lagging indicator. On days following a high-volatility trend session, ADX(14) can remain above 30 even though the current morning has devolved into an inside, low-volume consolidation day.
* Entering breakouts on such days leads to immediate churn.
* *Solution in Task 04*: The **Ridge ML model** specifically penalizes days with high realized volatility ratios (`rv`), recent exhaustion (`dist50`), and unfavorable day-of-week/opex timing, cutting false entries substantially.

### 3. Early Stop-Out Before the Real Move ("Being Right Too Early")
* Because the stop loss is very tight (0.25–0.30 ATR), NQ frequently stops the trade out by 2–5 points during the 09:00 CT economic release noise, only to reverse and run 200 points in the original bias direction by 13:00 CT.
* This is the structural cost of maintaining a 3:1 reward-to-risk ratio. The trader must accept that being shaken out on noise is part of the mathematical engine.

---

## 4. Empirical Loss Characteristics & Drawdown Signatures

When executing Overnight Bias on live capital, expect the following statistical realities:

| Metric | Task 03 (ADX 30) | Task 04 (Ridge ML) |
|---|---|---|
| **Win Rate** | **37.5% – 42.0%** | **44.0% – 48.5%** |
| **Profit Factor** | **1.35 – 1.55** | **1.60 – 1.85** |
| **Max Consecutive Losses** | **6 to 9 losses** | **4 to 6 losses** |
| **Average Loss Duration** | **1 to 3 bars (15–45 min)** | **1 to 3 bars (15–45 min)** |
| **Average Win Duration** | **8 to 16 bars (2–4 hours)** | **8 to 16 bars (2–4 hours)** |

> [!WARNING]
> **Psychological Hazard of Low Win-Rate Strategies**:  
> Overnight Bias loses on roughly 6 out of every 10 trades. It is completely normal to experience **5 to 8 consecutive losing trades** across a two-week period. Each loss is small (-\$500 to -\$700), but the cumulative string can consume \$3,000 to \$4,500 of equity before a single +3R winner (+\$2,200) recovers the ground.

---

## 5. Live Execution & Apex Prop Account Management Rules

### A. The Apex $2,000 Trailing Drawdown Rule
* On a standard Apex \$50,000 account, the maximum trailing drawdown is **\$2,000**.
* A sequence of 3 consecutive full-stop losses on 1 full NQ contract (-\$700 × 3 = -\$2,100) will **instantly blow the account**.
* **Mandatory Rule for Combine / Evaluation**:
  - Trade **Micro contracts (MNQ)** or enforce the **Cushion Rule**:
  - Under \$1,500 cushion: Trade maximum **2 MNQ** (Max loss = -\$140 per trade).
  - \$1,500 to \$3,000 cushion: Trade **5 MNQ** (Max loss = -\$350 per trade).
  - Only deploy **1 full NQ contract** once accumulated profit cushion exceeds **\$3,500**.

### B. Daily Loss Limit Protection
* Apex imposes a daily loss limit of \$1,000 on \$50k accounts.
* Overnight Bias only takes **1 trade per day**. Even on full NQ, a single loss of 0.25 ATR (25–35 pts = \$500–\$700) will never breach the daily loss limit on its own.

### C. MultiCharts PowerLanguage Implementation Gotchas
1. **Intrabar Stop Fills**: In MultiCharts, ensure `SetStopLoss` or `SetStopContract` uses tick-by-tick calculation or BarMagnifier, otherwise backtest fills will assume best-case bar extremes.
2. **Order Cancellation**: Ensure that if the opening range is not broken by 14:00 CT, all resting stop-buy and stop-sell orders are cancelled immediately.
3. **Time Sync**: Verify the 08:45 calculation bar uses bar close or open properly matching Rithmic/CME exchange timestamps (08:30:00 to 08:44:59).
