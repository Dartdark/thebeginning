# Test 02: review a MultiCharts signal before it goes live

Work on branch `codex/tests` only. Don't fetch or read other branches. Read `MULTICHARTS_PITFALLS.md` and
`apex_strategies/NQ_Vault_Break.txt` (the live version) first.

## The situation

Another research agent wrote the PowerLanguage signal below and called it "clean, production-ready" for 30-minute NQ /
MNQ charts on Apex accounts. It is meant to implement exactly this rule, which it tested in Python:

- Data: 30-minute NQ bars, Exchange time zone (Central), 24-hour CME session; bars stamped at their close.
- Noise level = midnight open (first bar of the calendar date) + 0.30 x **15-day daily ATR** (true range per calendar
  date, previous 15 completed weekdays).
- VWAP = (H+L+C)/3 x volume, cumulative from midnight.
- Long only: a decision bar closing 10:00-12:30 CT with close > noise level, close > VWAP, and
  close − VWAP <= 0.50 x daily ATR → buy next bar at market.
- Target +40 points, stop −75 points, both active from the fill; flat at 14:30 CT; max 3 trades a day; one position.
- Apex: must never carry a position past 15:59 CT, including on early-close holidays (12:00 CT halts).

## Your task

Review the code line by line against the rule and against how MultiCharts actually executes. For each problem give:
the line, what happens in MultiCharts (backtest and live, with Rithmic), severity (CRITICAL = changes the strategy or
creates live risk / MAJOR / MINOR / harmless), and the fix. Also state clearly whether the code has intrabar
look-ahead bias, with your reasoning. Don't report problems you can't explain. Then write a corrected version.

Output: `agents/codex/results/TEST_02.md` (findings table + verdict: SAFE TO PASTE / NOT SAFE) and the corrected code
`agents/codex/results/TEST_02_corrected.txt`. Commit and push to `codex/tests`.

## The code

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

// Calculate Daily ATR-15 (using daily true range approximation)
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
