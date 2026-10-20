# Systematic Strategy Filters & Optimizers Catalog (143 Cases)

A clean, categorized library of 143 quantitative regime filters and optimizers. These filters act as modular condition gates (`PeakFilter`) tested across optimization sweeps to eliminate low-probability market environments.

---

## 1. Architectural Role of Filters

Filters should **never** be used to create an edge out of thin air. Instead, their role is to:
1. **Regime Identification**: Gate entries so trend strategies only fire in high-ADX or expanding-volatility states, and mean-reversion strategies only fire in range-bound or low-volume exhaustion states.
2. **Execution Timing**: Restrict trade triggers to specific intraday windows (e.g., after 8:00 AM, before 12:00 PM) to avoid low-liquidity slippage.
3. **Volume & Momentum Confirmation**: Ensure institutional participation is present (expanding volume, momentum > 0).

---

## 2. Categorized Filter Families

### Family 1: Trend & Moving Average Position (Cases 1–20, 65–66, 105–106)
Gates trades based on whether price is above or below key benchmark moving averages, or whether the moving average itself is sloping upward or downward.

| Case # | EasyLanguage / PowerLanguage Code | Description | Quantitative Regime |
| :--- | :--- | :--- | :--- |
| **Case 1** | `Close < Average(Close, 5)` | Below 5-day MA | Ultra-short term downtrend |
| **Case 2** | `Close > Average(Close, 5)` | Above 5-day MA | Ultra-short term uptrend |
| **Case 3** | `Close < Average(Close, 10)` | Below 10-day MA | Short-term pullback / downtrend |
| **Case 4** | `Close > Average(Close, 10)` | Above 10-day MA | Short-term momentum |
| **Case 5** | `Close < Average(Close, 21)` | Below 21-day MA | Below 1-month trend |
| **Case 6** | `Close > Average(Close, 21)` | Above 21-day MA | Above 1-month trend |
| **Case 7** | `Close < Average(Close, 30)` | Below 30-day MA | Intermediate pullback |
| **Case 8** | `Close > Average(Close, 30)` | Above 30-day MA | Intermediate trend |
| **Case 9** | `Close < Average(Close, 40)` | Below 40-day MA | Below 8-week trend |
| **Case 10** | `Close > Average(Close, 40)` | Above 40-day MA | Above 8-week trend |
| **Case 11** | `Close < Average(Close, 50)` | Below 50-day MA | Medium-term bear regime |
| **Case 12** | `Close > Average(Close, 50)` | Above 50-day MA | Medium-term bull regime |
| **Case 13** | `Close < Average(Close, 75)` | Below 75-day MA | Below intermediate benchmark |
| **Case 14** | `Close > Average(Close, 75)` | Above 75-day MA | Above intermediate benchmark |
| **Case 15** | `Close < Average(Close, 100)` | Below 100-day MA | Long-term bear regime |
| **Case 16** | `Close > Average(Close, 100)` | Above 100-day MA | Long-term bull regime |
| **Case 19** | `Close < Average(Close, 200)` | Below 200-day MA | Institutional secular bear |
| **Case 20** | `Close > Average(Close, 200)` | Above 200-day MA | Institutional secular bull |
| **Case 65** | `Average(Close, 20) > Average(Close, 20)[1] and Average(Close, 20)[1] > Average(Close, 20)[2]` | 20-MA rising for 2 consecutive bars | Trend upward momentum |
| **Case 66** | `Average(Close, 20) < Average(Close, 20)[1] and Average(Close, 20)[1] < Average(Close, 20)[2]` | 20-MA falling for 2 consecutive bars | Trend downward momentum |
| **Case 105** | `Average(Close, 2) < Average(Close, 5)` | 2-bar MA below 5-bar MA | Short-term negative slope |
| **Case 106** | `Average(Close, 2) > Average(Close, 5)` | 2-bar MA above 5-bar MA | Short-term positive slope |

---

### Family 2: Intraday Time-of-Day Windows (Cases 21–28)
Restricts entries to specific execution windows to avoid illiquid rollover gaps or catch active cash hours.

| Case # | EasyLanguage / PowerLanguage Code | Description | Trading Session Purpose |
| :--- | :--- | :--- | :--- |
| **Case 21** | `Time < 0400` | Before 4:00 AM | Asian session / early London only |
| **Case 22** | `Time < 0600` | Before 6:00 AM | London morning session only |
| **Case 23** | `Time < 0800` | Before 8:00 AM | Pre-US cash open only |
| **Case 24** | `Time < 1000` | Before 10:00 AM | US opening drive only |
| **Case 25** | `Time < 1200` | Before 12:00 PM (Noon) | Morning session only (skips afternoon) |
| **Case 26** | `Time > 0400` | After 4:00 AM | London open onwards |
| **Case 27** | `Time > 0600` | After 6:00 AM | Late European session onwards |
| **Case 28** | `Time > 0800` | After 8:00 AM | US pre-market / cash session onwards |

---

### Family 3: Multi-Bar Runs & Consecutive Closes (Cases 34–36, 109–110, 143)
Measures directional exhaustion or persistent momentum through consecutive directional runs.

| Case # | EasyLanguage / PowerLanguage Code | Description |
| :--- | :--- | :--- |
| **Case 34** | `Close[1] < Close[2] and Close[2] < Close[3] and Close[3] < Close[4]` | 4 consecutive down closes |
| **Case 35** | `Close[1] > Close[2] and Close[2] > Close[3] and Close[3] > Close[4] and Close[4] > Close[5]` | 5 consecutive up closes |
| **Case 36** | `Close[1] < Close[2] and Close[2] < Close[3] and Close[3] < Close[4] and Close[4] < Close[5]` | 5 consecutive down closes |
| **Case 109** | `Close[1] < Open[1] and Close[2] < Open[2]` | 2 consecutive down days (red candles) |
| **Case 110** | `Close[1] > Open[1] and Close[2] > Open[2]` | 2 consecutive up days (green candles) |
| **Case 143** | `Close[1] > Close[2]` | Yesterday's close > Prior day's close |

---

### Family 4: Intrabar Price Action, Tails, & Shadows (Cases 37–45, 111–116)
Analyzes candlestick structure (wicks vs. bodies) to identify absorption, rejection, or strong trend candles.

| Case # | EasyLanguage / PowerLanguage Code | Description | Candlestick Meaning |
| :--- | :--- | :--- | :--- |
| **Case 37** | `(High[0] - Open[0]) > ((High[1] - Open[1]) * 1.0)` | Upper range expansion 1.0x | Buyers pushing intraday extension |
| **Case 38** | `(High[0] - Open[0]) > ((High[1] - Open[1]) * 1.5)` | Upper range expansion 1.5x | Strong buyer thrust vs. prior bar |
| **Case 39** | `(Open[0] - Low[0]) > ((Open[1] - Low[1]) * 1.0)` | Lower range expansion 1.0x | Sellers pushing intraday extension |
| **Case 40** | `(Open[0] - Low[0]) > ((Open[1] - Low[1]) * 1.5)` | Lower range expansion 1.5x | Strong seller thrust vs. prior bar |
| **Case 41** | `Low[0] < Low[1]` | Trading below prior bar's low | Downside liquidity sweep |
| **Case 42** | `High[0] > High[1]` | Trading above prior bar's high | Upside liquidity sweep |
| **Case 43** | `AbsValue(Open[1] - Close[1]) < 0.5 * (High[1] - Low[1])` | Candle body < 50% of range | Doji / indecision candle |
| **Case 44/45**| `AbsValue(Open[1] - Close[1]) > 0.7 * (High[1] - Low[1])` | Candle body > 70% of range | Solid trend bar (conviction close) |
| **Case 111**| `(High[1] - MaxList(Close[1], Open[1])) < (MinList(Close[1], Open[1]) - Low[1])` | Lower shadow > Upper shadow | Buying absorption off lows |
| **Case 112**| `(High[1] - MaxList(Close[1], Open[1])) > (MinList(Close[1], Open[1]) - Low[1])` | Upper shadow > Lower shadow | Selling rejection at highs |
| **Case 113**| `(MinList(Close[1], Open[1]) - Low[1]) > AbsValue(Open[1] - Close[1])` | Lower shadow > Body size | Hammer / pin-bar off lows |
| **Case 114**| `(High[1] - MaxList(Close[1], Open[1])) < AbsValue(Open[1] - Close[1])` | Upper shadow < Body size | Strong close near high (no wick) |
| **Case 115**| `(High[1] - MaxList(Close[1], Open[1])) / (High[1] - Low[1]) * 100 < 40` | Upper shadow < 40% of range | Low upper rejection |
| **Case 116**| `(High[1] - MaxList(Close[1], Open[1])) / (High[1] - Low[1]) * 100 > 40` | Upper shadow > 40% of range | Substantial upper wick (rejection) |

---

### Family 5: Volatility Expansion, Contraction & Range (Cases 67–68, 71–72, 99–100, 137–142)
Detects structural regime transitions between quiet consolidation (compression) and explosive trending (expansion).

| Case # | EasyLanguage / PowerLanguage Code | Description | Regime Transition |
| :--- | :--- | :--- | :--- |
| **Case 67** | `(High - Low)[1] > (High - Low)[2] and (High - Low)[0] < (High - Low)[1]` | Expansion followed by contraction | Volatility exhaustion / rest |
| **Case 68** | `(High - Low)[1] < (High - Low)[2] and (High - Low)[0] > (High - Low)[1]` | Contraction followed by expansion | Volatility breakout / ignition |
| **Case 71** | `Highest(High, 3) - Lowest(High, 3) <= 0.20 * (Highest(High, 3) - Lowest(Low, 3))` | Art Collins: Highs clustered in top 20% | Resistance ceiling formation |
| **Case 72** | `Highest(Low, 3) - Lowest(Low, 3) <= 0.20 * (Highest(High, 3) - Lowest(Low, 3))` | Art Collins: Lows clustered in bottom 20%| Support floor formation |
| **Case 99** | `Average(High - Low, 5) > Average(High - Low, 20)` | 5-bar range > 20-bar range | Expanding volatility regime |
| **Case 100**| `Average(High - Low, 5) < Average(High - Low, 20)` | 5-bar range < 20-bar range | Compressing volatility regime |
| **Case 137**| `(High[1] - Low[1]) < AvgTrueRange(10) * 2.5` | Prior range < 2.5x ATR | Normal volatility bounds |
| **Case 138**| `(High[1] - Low[1]) > AvgTrueRange(10) * 2.5` | Prior range > 2.5x ATR | Outlier / shock range expansion |
| **Case 139**| `StandardDev(Close, 5, 1) > Average(StandardDev(Close, 5, 1), 10)` | 5-bar StdDev > 10-bar average | Rising standard deviation |
| **Case 140**| `StandardDev(Close, 5, 1) < Average(StandardDev(Close, 5, 1), 10)` | 5-bar StdDev < 10-bar average | Falling standard deviation |
| **Case 141**| `High[1] > High[2] and Low[1] > Low[2]` | Higher High and Higher Low | Ascending channel range |
| **Case 142**| `High[1] < High[2] and Low[1] < Low[2]` | Lower High and Lower Low | Descending channel range |

---

### Family 6: Donchian & Multi-Bar High/Low Levels (Cases 55–64, 69–70, 101–104, 107–108)
Tracks relative position of recent highs and lows, swing points, and Donchian channel tests.

| Case # | EasyLanguage / PowerLanguage Code | Description |
| :--- | :--- | :--- |
| **Case 55** | `CountIf(High > Highest(High, 30)[1], 5) >= 1` | New 30-bar high printed in last 5 bars |
| **Case 56** | `CountIf(Low < Lowest(Low, 30)[1], 5) >= 1` | New 30-bar low printed in last 5 bars |
| **Case 57** | `HighestBar(Close, 10) < LowestBar(Close, 10)` | Highest close occurred more recently than lowest close |
| **Case 58** | `HighestBar(Close, 10) > LowestBar(Close, 10)` | Lowest close occurred more recently than highest close |
| **Case 59** | `High == Highest(High, 5)` | Current bar is 5-bar highest high |
| **Case 60** | `Low == Lowest(Low, 5)` | Current bar is 5-bar lowest low |
| **Case 61** | `HighestBar(High, 10) < LowestBar(High, 10)` | Highest high printed after lowest high |
| **Case 62** | `HighestBar(High, 10) > LowestBar(High, 10)` | Highest high printed before lowest high |
| **Case 63** | `HighestBar(Low, 10) < LowestBar(Low, 10)` | Highest low printed after lowest low |
| **Case 64** | `HighestBar(Low, 10) > LowestBar(Low, 10)` | Highest low printed before lowest low |
| **Case 69** | `Close == Highest(Close, 5)` | Current close is 5-bar highest close |
| **Case 70** | `Close == Lowest(Close, 5)` | Current close is 5-bar lowest close |
| **Case 101**| `High[1] > High[2] and High[1] > High[3] and High[1] > High[4]` | Prior high is a 3-bar swing high |
| **Case 102**| `High[1] < High[2] and High[1] < High[3] and High[1] < High[4]` | Prior high is lower than last 3 highs |
| **Case 103**| `Low[1] < Low[2] and Low[1] < Low[3] and Low[1] < Low[4]` | Prior low is a 3-bar swing low |
| **Case 104**| `Low[1] > Low[2] and Low[1] > Low[3] and Low[1] > Low[4]` | Prior low is higher than last 3 lows |

---

### Family 7: Technical Oscillators & Momentum (Cases 75–98)
Standard momentum filters across RSI, Williams %R, Rate of Change, ADX, and MACD.

| Case # | EasyLanguage / PowerLanguage Code | Description | Indicator State |
| :--- | :--- | :--- | :--- |
| **Case 75** | `CountIf(RSI(Close, 14) > 50, 5) == 5` | RSI > 50 for 5 consecutive bars | Bullish momentum persistence |
| **Case 76** | `CountIf(RSI(Close, 14) < 50, 5) == 5` | RSI < 50 for 5 consecutive bars | Bearish momentum persistence |
| **Case 77** | `PercentR(7) > 75` | Williams %R > 75 | Overbought momentum |
| **Case 78** | `PercentR(7) <= 25` | Williams %R <= 25 | Oversold momentum |
| **Case 79** | `RSI(Close, 14) >= 75` | 14-period RSI >= 75 | Classic overbought |
| **Case 80** | `RSI(Close, 14) <= 75 and RSI(Close, 14)[1] > 75` | RSI crossing back below 75 | Overbought reversal |
| **Case 81** | `RSI(Close, 14) >= 25 and RSI(Close, 14)[1] < 25` | RSI crossing back above 25 | Oversold reversal |
| **Case 82** | `RSI(Close, 14) <= 25` | 14-period RSI <= 25 | Classic oversold |
| **Case 83** | `RSI(Close, 3) > 75` | Fast 3-period RSI > 75 | Ultra-short overbought |
| **Case 84** | `RSI(Close, 3) < 75` | Fast 3-period RSI < 75 | Ultra-short overbought reverse |
| **Case 85** | `RSI(Close, 3) > 25` | Fast 3-period RSI > 25 | Ultra-short oversold reverse |
| **Case 86** | `RSI(Close, 3) < 25` | Fast 3-period RSI < 25 | Ultra-short oversold |
| **Case 87** | `RateOfChange(Close, 10) < -5` | 10-bar ROC < -5% | Deep downward price velocity |
| **Case 88** | `RateOfChange(Close, 10) > 5` | 10-bar ROC > +5% | Strong upward price velocity |
| **Case 89** | `Momentum(Close[1], 10) < 0` | 10-bar Momentum < 0 | Negative momentum |
| **Case 90** | `Momentum(Close[1], 10) > 0` | 10-bar Momentum > 0 | Positive momentum |
| **Case 91** | `ADX(15) > 30` | ADX > 30 | Strong trending regime |
| **Case 92** | `ADX(15) < 30` | ADX < 30 | Non-trending / range regime |
| **Case 93** | `ADX(15) > 10` | ADX > 10 | Non-flatline market |
| **Case 94** | `ADX(15) < 10` | ADX < 10 | Dead market / zero trend |
| **Case 95** | `MACD(Close, 10, 30) < XAverage(MACD(Close, 10, 30), 10)` | MACD below Signal Line | Bearish momentum cross |
| **Case 96** | `MACD(Close, 10, 30) > XAverage(MACD(Close, 10, 30), 10)` | MACD above Signal Line | Bullish momentum cross |
| **Case 97** | `Close[1] < Average(Close, 5) and Close[1] > Average(Close, 20)` | Pullback below 5-MA in 20-MA uptrend | Dueling momentum dip |
| **Case 98** | `Close[1] > Average(Close, 5) and Close[1] < Average(Close, 20)` | Rally above 5-MA in 20-MA downtrend | Dueling momentum rally |

---

### Family 8: Volume Moving Averages & Trajectory (Cases 117–136)
Measures institutional flow, volume expansion, and volume dry-up.

| Case # | EasyLanguage / PowerLanguage Code | Description | Volume State |
| :--- | :--- | :--- | :--- |
| **Case 117**| `Volume < Average(Volume, 3)` | Volume below 3-bar average | Very short-term volume lull |
| **Case 118**| `Volume > Average(Volume, 3)` | Volume above 3-bar average | Short-term volume surge |
| **Case 119**| `Volume < Average(Volume, 5)` | Volume below 5-bar average | Low 5-bar volume |
| **Case 120**| `Volume > Average(Volume, 5)` | Volume above 5-bar average | High 5-bar volume |
| **Case 121**| `Volume < Average(Volume, 10)` | Volume below 10-bar average | Low 10-bar volume |
| **Case 122**| `Volume > Average(Volume, 10)` | Volume above 10-bar average | High 10-bar volume |
| **Case 123**| `Volume < Average(Volume, 20)` | Volume below 20-bar average | Low 20-bar volume |
| **Case 124**| `Volume > Average(Volume, 20)` | Volume above 20-bar average | High 20-bar volume |
| **Case 125**| `Volume < Average(Volume, 50)` | Volume below 50-bar average | Low 50-bar volume |
| **Case 126**| `Volume > Average(Volume, 50)` | Volume above 50-bar average | High 50-bar volume |
| **Case 127**| `Volume < Average(Volume, 100)` | Volume below 100-bar average | Long-term quiet volume |
| **Case 128**| `Volume < Volume[1] * 0.5` | Volume dropped by > 50% vs prior bar | Sudden volume dry-up |
| **Case 129**| `Volume > Volume[1] * 2.0` | Volume doubled vs prior bar | Sudden volume explosion |
| **Case 130**| `Volume > Volume[1]` | Volume rising (1 bar) | Expanding participation |
| **Case 131**| `Volume < Volume[1]` | Volume falling (1 bar) | Contracting participation |
| **Case 132**| `Volume > Volume[1] and Volume[1] > Volume[2]` | Volume rising 2 consecutive bars | Accelerating volume |
| **Case 133**| `Volume < Volume[1] and Volume[1] < Volume[2]` | Volume falling 2 consecutive bars | Declining volume |
| **Case 134**| `Volume > Volume[1] and Volume[1] > Volume[2] and Volume[2] > Volume[3]` | Volume rising 3 consecutive bars | Sustained volume expansion |
| **Case 135**| `Volume < Volume[1] and Volume[1] < Volume[2] and Volume[2] < Volume[3]` | Volume falling 3 consecutive bars | Sustained volume dry-up |
| **Case 136**| `Volume < Average(Volume, 100)` | Volume below 100-bar average | Repeat of low 100-bar volume |
