# Bridge noise-area NQ 15-min (candidate, 2026-11-03)

Source: a strategy posted by The Bridge (user's paste, 2026-11-03), based on Zarattini, Aziz, Barbon (2024) intraday
momentum ("noise area"). Author's claim: net +$6,335, PF 1.30, Sharpe 3.7 (window and costs unknown).

## Claim to check
Per 1 NQ, 2018-01-01 onward, our costs ($7.25 per round trip + 1 tick slippage on every market and stop fill; the profit
target is a limit with no slippage), on an RTH 15-minute chart:
- both sides as posted: ~5,370 trades, ~$40 a trade, PF ~1.16, t ~4.9;
- **longs only (the promoted variant, `trades_longs.csv`): ~2,580 trades, ~$63 a trade, PF ~1.28, t ~5.6, 9/9 years.**
Try to break both, the longs-only claim first.

## Chart / data setup (chosen by the maker; the author did not say)
- NQ 1-minute data (raw CSVs in `data/`, or `scratch_data/g24.pkl`), aggregated to 15-minute bars stamped at their CLOSE,
  Central time. **RTH session only: bars closing 08:45 .. 15:00** on regular trading days.
- "Date <> Date[1]" = the first bar of a new trading day (the 08:45 bar), so TodayOpen = the 08:30 open and PrevClose =
  the previous day's 15:00 bar close.
- Intrabar stop / target are resolved on the 1-minute path inside each 15-min bar (stop first if both in one minute).
  Stop fills at the stop or the minute's open if it gaps through, minus 1 tick; target fills exactly at the target.
- "next bar at market" = the next 15-min bar's open, 1 tick slippage.
- The code has no exit on a day without a 14:30 bar (early closes): the maker closes such positions at that day's last bar
  close and flags them (they would be held overnight live). Treat as you see fit, but report it.
- Results per 1 contract (the file's ContractsPerTrade is 2; the stop size is per contract via SetStopContract).

## The rule (the posted PowerLanguage, verbatim logic)
```
Inputs: LookbackDays(20), VolatilityMultiplier(1.0), EMALength(20), StopLossPoints(50), ContractsPerTrade(2),
        RewardRisk(0.5), LongTrade(true), ShortTrade(true), MaxTradesPerDay(10), MaxStopsPerDay(3),
        FirstEvalTime(0900), LastEntryTime(1400), FlatSignalTime(1430);
Arrays: MoveHistory[2200](0), SlotCount[22](0);

StopDollarsPerPosition = StopLossPoints * BigPointValue * ContractsPerTrade;
SetStopContract; SetStopLoss(StopLossPoints * BigPointValue); SetProfitTarget(StopLossPoints * BigPointValue * RewardRisk);

if Date <> Date[1] then begin
    TodayOpen = Open; if CurrentBar > 1 then PrevClose = Close[1];
    TradesToday = 0; StopsToday = 0; LastTotalTrades = TotalTrades;
end;
if TotalTrades > LastTotalTrades then begin
    if PositionProfit(1) <= -StopDollarsPerPosition then StopsToday = StopsToday + 1;
    LastTotalTrades = TotalTrades;
end;
EMAValue = XAverage(Close, EMALength);          // continuous over all chart bars
CurrentMinutes = hour*60 + minute of Time; FirstMinutes = 9*60;

if Time >= 0900 and Time <= 1430 and TodayOpen > 0 and PrevClose > 0 then begin
    Slot = IntPortion((CurrentMinutes - FirstMinutes) / 15) + 1;      // 09:00 bar = 1 ... 14:15 = 22, 14:30 = 23
    if Slot >= 1 and Slot <= 22 then begin
        MoveToday = AbsValue(Close / TodayOpen - 1);
        if SlotCount[Slot] >= LookbackDays then begin
            AvgMove = mean of the slot's LookbackDays most recent stored moves (today's not yet stored);
            UpperBand = MaxList(TodayOpen, PrevClose) * (1 + AvgMove * VolatilityMultiplier);
            LowerBand = MinList(TodayOpen, PrevClose) * (1 - AvgMove * VolatilityMultiplier);
            LongTrail = MaxList(UpperBand, EMAValue); ShortTrail = MinList(LowerBand, EMAValue);
            if Time < 1430 then begin
                if MarketPosition = 0 and TradesToday < MaxTradesPerDay and StopsToday < MaxStopsPerDay
                   and Time <= LastEntryTime then begin
                    if LongTrade and Close > UpperBand and Close > Open then
                        Buy next bar at market, TradesToday += 1
                    else if ShortTrade and Close < LowerBand and Close < Open then
                        SellShort next bar at market, TradesToday += 1;
                end;
                if MarketPosition = 1 then begin
                    if Time <= LastEntryTime and ShortTrade and Close < LowerBand and Close < Open then begin
                        Sell next bar at market;
                        if TradesToday < MaxTradesPerDay and StopsToday < MaxStopsPerDay then
                            SellShort next bar at market (reversal), TradesToday += 1;
                    end else if Close < LongTrail then Sell next bar at market;
                end;
                if MarketPosition = -1 then  (mirror: reversal to long, else BuyToCover if Close > ShortTrail);
            end;
        end;
        store MoveToday as the slot's newest move (keep 100); SlotCount[Slot] += 1 (max 100);
    end;
end;
if Time = 1430 then exit any position next bar at market (the 14:45 open);
```
Notes: with LongTrade only (longs-only variant, ShortTrade = false), a long exits only on the stop, the target, the
LongTrail close exit or the 14:30 flat (no reversals). StopsToday counts a closed position that lost the full stop.
