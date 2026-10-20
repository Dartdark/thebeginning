# Systematic Strategy Building Blocks: Entries, Exits, and Architecture

A modular quantitative library of discrete entry and exit building blocks, designed to be tested in isolation, paired methodically, and tuned with optimizers and filters.

---

## 1. Architectural Philosophy: The Modular Approach

Systematic strategy engineering requires separating **Directional Edge (Entry)** from **Trade Management (Exit)**:

1. **Entries provide raw predictive edge**: An entry module must demonstrate positive statistical expectancy (MFE > MAE or raw gain over random baseline) before adding filters.
2. **Exits manage risk and harvest the distribution**: Exits must be tailored to the specific regime of the entry (e.g., trend breakouts require trailing stops and open-ended runners; mean-reversion requires limit targets or strict time-stops).
3. **Optimizers and filters eliminate low-probability regimes**: Filters should be applied only after the core entry-exit pairing demonstrates structural viability.

---

## 2. The 10 Entry Modules

### Entry 1: Three Consecutive Directional Closes (Short-Term Momentum)
* **Regime**: Short-Term Momentum Continuation
* **Concept**: Capitalizes on short-term price velocity when three consecutive bars close in the same direction.
* **Code / Logic**:
  ```easylanguage
  // Long Entry: Three consecutive up closes
  If Close[0] > Open[0] and Close[1] > Open[1] and Close[2] > Open[2] then 
      Buy next bar at market;

  // Short Entry: Three consecutive down closes
  If Close[0] < Open[0] and Close[1] < Open[1] and Close[2] < Open[2] then 
      SellShort next bar at market;
  ```
* **Best Market Fit**: Trending equity indices (NQ, ES) and momentum commodities during session runs.

---

### Entry 2: Highest/Lowest Close Breakout (Donchian Close Trend)
* **Regime**: Trend Following / Breakout
* **Concept**: Buys when price closes at the highest close of the lookback period; sells short at the lowest close.
* **Code / Logic**:
  ```easylanguage
  Inputs: Length(10);

  If Close = Highest(Close, Length) then 
      Buy next bar at market;

  If Close = Lowest(Close, Length) then 
      SellShort next bar at market;
  ```
* **Best Market Fit**: Commodities with persistent directional runs (Copper, Crude Oil, Gold).

---

### Entry 3: Price Extreme Fade (Mean Reversion)
* **Regime**: Mean Reversion / Range Trading
* **Concept**: Fades extreme high/low closes, anticipating a snap-back toward the average.
* **Correction Note**: *Original snippet contained a typo (buying highs/selling lows). Corrected below to properly execute mean reversion.*
* **Code / Logic**:
  ```easylanguage
  Inputs: Length(10);

  // Fade the high close: sell short
  If Close = Highest(Close, Length) then 
      SellShort next bar at market;

  // Fade the low close: buy
  If Close = Lowest(Close, Length) then 
      Buy next bar at market;
  ```
* **Best Market Fit**: Mean-reverting commodities (Wheat, Corn post-harvest) and fixed-income range channels.

---

### Entry 4: Low-Volume Exhaustion Reversal
* **Regime**: Volume-Filtered Mean Reversion
* **Concept**: Buys the lowest close or sells the highest close ONLY when bar volume is below its moving average, signaling lack of institutional participation and exhaustion.
* **Code / Logic**:
  ```easylanguage
  Inputs: Length(10), VolAvgLen(10);

  If Volume < Average(Volume, VolAvgLen) then begin
      If Close = Lowest(Close, Length) then 
          Buy next bar at market;
      If Close = Highest(Close, Length) then 
          SellShort next bar at market;
  end;
  ```
* **Best Market Fit**: Consolidating sessions, equities outside opening hours, agricultural trading ranges.

---

### Entry 5: Dueling Momentum (Multi-Timeframe Trend Pullback)
* **Regime**: Dual-Horizon Trend Pullback / Early Reversal
* **Concept**: Enters in the direction of short-term momentum (15-bar) while aligning with or pulling back inside a longer-term horizon (50-bar).
* **Code / Logic**:
  ```easylanguage
  Inputs: Length1(15), Length2(50);

  // Short-term positive, long-term pullback
  If Close > Close[Length1] and Close < Close[Length2] then 
      Buy next bar at market;

  // Short-term negative, long-term extension
  If Close < Close[Length1] and Close > Close[Length2] then 
      SellShort next bar at market;
  ```
* **Best Market Fit**: Multi-day swing trading across broad futures markets.

---

### Entry 6: Fixed Calendar Date Seasonality
* **Regime**: Calendar / Seasonal Structural Flow
* **Concept**: Enters on a specific calendar date (e.g., September 1st) to exploit institutional rebalancing, crop delivery dates, or fiscal year transitions.
* **Code / Logic**:
  ```easylanguage
  // Example: Buy on September 1st across years
  If Date crosses over 1220901 then Buy this bar at close;
  If Date crosses over 1210901 then Buy this bar at close;
  If Date crosses over 1200901 then Buy this bar at close;
  ```
* **Best Market Fit**: Softs (Cocoa harvest Oct 1, Coffee pre-frost June 1) and energy seasonal transitions.

---

### Entry 7: Day of Week Liquidity Anomaly
* **Regime**: Weekly Structural Flow
* **Concept**: Enters on a specific day of the week (e.g., Tuesday) and exits the following day (Wednesday) to capture structural weekly positioning shifts.
* **Code / Logic**:
  ```easylanguage
  // Buy on Tuesday (Day 2), exit on Wednesday close (Day 3)
  If DayOfWeek(Date) = 2 then 
      Buy next bar at market;

  If DayOfWeek(Date) = 3 then 
      SetExitOnClose;
  ```
* **Best Market Fit**: Turnaround Tuesday in equities; Wednesday pre-EIA inventory in energies.

---

### Entry 8: Quantamental / External Positioning Extreme
* **Regime**: Macro / COT Sentiment Reversal
* **Concept**: Enters when large institutional non-commercial traders (hedge funds) reach crowded net-long or net-short extremes, triggering on a local stop break.
* **Code / Logic**:
  ```easylanguage
  Inputs: COTThreshold(-20000);

  // Sell breakdown when speculative positioning is crowded
  If HedgeFundNetLongPosition > COTThreshold then 
      SellShort next bar at Lowest(Low, 2) stop;
  ```
* **Best Market Fit**: Multi-week commodity swing trades (Gold, Crude Oil, Grains).

---

### Entry 9: Dual Moving Average Crossover
* **Regime**: Classical Trend Following
* **Concept**: Enters when a fast moving average crosses a slow moving average, establishing a directional regime shift.
* **Code / Logic**:
  ```easylanguage
  Inputs: Length1(10), Length2(50);
  Variables: MAS(0), MAL(0);

  MAS = AverageFC(Close, Length1);
  MAL = AverageFC(Close, Length2);

  If MAS crosses over MAL then 
      Buy next bar at market;

  If MAS crosses under MAL then 
      SellShort next bar at market;
  ```
* **Best Market Fit**: Trending commodities (Copper, Crude Oil, Platinum).

---

### Entry 10: Resting Intrabar Stop Breakout (Donchian / Turtle)
* **Regime**: Intrabar Volatility Expansion
* **Concept**: Places resting stop orders at the highest high or lowest low of the last X bars, entering immediately upon price penetration.
* **Code / Logic**:
  ```easylanguage
  Inputs: Length(10);

  Buy next bar at Highest(High, Length) stop;
  SellShort next bar at Lowest(Low, Length) stop;
  ```
* **Best Market Fit**: Volatile breakout markets (NQ, Crude Oil, Lean Hogs).

---

## 3. The 10 Exit Modules

### Exit 1: Entry as Exit (Always-in-the-Market Reversal)
* **Category**: Position Reversal
* **Logic**: Reverses position immediately upon generating the opposite entry signal.
* **Code**:
  ```easylanguage
  Inputs: RevLength(6);
  If Close = Highest(Close, RevLength) then Buy next bar at market;
  If Close = Lowest(Close, RevLength) then SellShort next bar at market;
  ```

---

### Exit 2: Simple Static Profit Target
* **Category**: Hard Dollar Profit Target
* **Logic**: Enforces a rigid profit ceiling using broker/platform target execution.
* **Code**:
  ```easylanguage
  SetProfitTarget(10000); // Fixed dollar target
  ```

---

### Exit 3: Delayed Profit Target Next Bar at Market
* **Category**: Bar-Close Profit Target
* **Logic**: Waits until bar close confirms that maximum profit exceeded target, then executes at market on the next open.
* **Code**:
  ```easylanguage
  If MaxPositionProfit > ProfitTarget then begin
      Sell next bar at market;
      BuyToCover next bar at market;
  end;
  ```

---

### Exit 4: Trailing Dollar Giveback Stop
* **Category**: Trailing High-Water Mark Profit Lock
* **Logic**: Tracks the trade's highest open profit (`MaxPositionProfit`) and exits if open profit gives back more than a specified dollar threshold ($2,000).
* **Code**:
  ```easylanguage
  If (MaxPositionProfit - OpenPositionProfit) > 2000 then begin
      Sell ("Trailing Sell") next bar at market;
      BuyToCover ("Trailing Buy") next bar at market;
  end;
  ```

---

### Exit 5: Profit Retracement Ratio Ratchet
* **Category**: Proportional Profit Protection
* **Logic**: Once a substantial gain is achieved ($\ge \$5,000$), protects the win by exiting if current profit drops below 50% of the maximum unrealized peak.
* **Code**:
  ```easylanguage
  If MaxPositionProfit >= 5000 then begin
      If MarketPosition > 0 and (OpenPositionProfit / MaxPositionProfit) < 0.5 then 
          Sell ("Protect Sell") next bar on Open;
      If MarketPosition < 0 and (OpenPositionProfit / MaxPositionProfit) < 0.5 then 
          BuyToCover ("Protect Buy") next bar on Open;
  end;
  ```

---

### Exit 6: Simple Hard Stop Loss
* **Category**: Catastrophic Risk Limit
* **Logic**: Fixed dollar safety stop.
* **Code**:
  ```easylanguage
  SetStopLoss(5000); // Fixed dollar risk per contract
  ```

---

### Exit 7: Quick Spike Limit Target (Percentage Extension)
* **Category**: Overextension / Mean Reversion Exit
* **Logic**: Places resting limit orders at entry price + 3% to capture immediate liquidity spikes.
* **Code**:
  ```easylanguage
  If MarketPosition > 0 then 
      Sell ("Spike Long Exit") next bar at Close + (Close * 0.03) limit;
  If MarketPosition < 0 then 
      BuyToCover ("Spike Short Exit") next bar at Close - (Close * 0.03) limit;
  ```

---

### Exit 8: Dynamic ATR Volatility Stop
* **Category**: Adaptive Risk Containment
* **Logic**: Places a stop loss dynamically scaled to 2x the 10-bar historical ATR(2), expanding stops in volatile markets and tightening in calm regimes.
* **Code**:
  ```easylanguage
  If MarketPosition > 0 then 
      Sell ("ATR Long Stop") next bar at EntryPrice - (AvgTrueRange(2)[10] * 2) stop;
  If MarketPosition < 0 then 
      BuyToCover ("ATR Short Stop") next bar at EntryPrice + (AvgTrueRange(2)[10] * 2) stop;
  ```

---

### Exit 9: Time-Based Position Reversal
* **Category**: Time-Delayed Directional Flip
* **Logic**: If an active position has not succeeded or terminated after 10 bars, automatically flips to the opposite side.
* **Code**:
  ```easylanguage
  If BarsSinceEntry > 10 then begin
      If MarketPosition > 0 then 
          SellShort ("Reverse Sell") next bar on Open;
      If MarketPosition < 0 then 
          Buy ("Reverse Buy") next bar on Open;
  end;
  ```

---

### Exit 10: Fixed Time Horizon Exit
* **Category**: Capital Recycling / Dead-Time Timeout
* **Logic**: Unconditionally closes the trade after 20 bars, eliminating dead capital and reducing exposure to tail events.
* **Code**:
  ```easylanguage
  If BarsSinceEntry >= 20 then begin
      Sell next bar at market;
      BuyToCover next bar at market;
  end;
  ```

---

## 4. Regime Pairing Architecture

| Strategy Archetype | Compatible Entry Modules | Compatible Exit Modules | Primary Markets |
| :--- | :--- | :--- | :--- |
| **Trend Runner** | Entry 2 (Close Breakout), Entry 9 (MA Cross), Entry 10 (Stop Breakout) | Exit 8 (ATR Stop) + Exit 4 (Trailing Giveback) or Exit 5 (Profit Ratchet) | `NQ`, `HG` (Copper), `CL` (Crude) |
| **Mean Reversion / Exhaustion** | Entry 3 (Extreme Fade), Entry 4 (Low-Vol Reversal), Entry 5 (Dueling Momentum) | Exit 6 (Stop Loss) + Exit 7 (Spike Limit) + Exit 10 (Time Horizon) | `ZW` (Wheat), `ZC` (Corn), Consolidating FX |
| **Calendar & Event Flow** | Entry 6 (Date Seasonal), Entry 7 (Day of Week), Entry 8 (COT Crowding) | Exit 2 / 3 (Fixed Profit Target) + Exit 8 (ATR Stop) + Exit 10 (Time Stop) | `KC` (Coffee), `CC` (Cocoa), `HE` (Hogs), `NG` (Gas) |
