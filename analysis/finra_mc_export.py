"""Writes the MultiCharts research file for the FINRA short-volume longs (WATCHLIST #32) with its signal dates embedded
(MultiCharts can't fetch FINRA data). Rule = analysis/finra_longs_test.py: Nasdaq short-volume ratio Z >= 1 (QQQ + 10 mega-caps,
past-60-day mean / sd) -> long NQ the NEXT trading day at the 08:31 open, stop 0.5 x daily ATR15, out at the 14:55 close; CME
early-close days skipped (the list already excludes them). Rerun after appending new FINRA days to refresh the dates:
  python3 analysis/finra_mc_export.py   -> checks/candidates/finra_longs/NQ_FINRA_Short_Volume_Longs.txt (+ python_trades.csv)
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import letf_flow_test as LF
from finra_short_test import SYMS

F = pd.read_csv("data/finra/short_volume.csv", sep="|", parse_dates=["Date"]); F = F[F.Symbol.isin(SYMS) & (F.TotalVolume > 0)]
F["r"] = F.ShortVolume / F.TotalVolume; R = F.pivot_table(index="Date", columns="Symbol", values="r").mean(axis=1)
Z = (R - R.rolling(60).mean().shift(1)) / R.rolling(60).std().shift(1)
g = pickle.load(open("scratch_data/g24.pkl", "rb")); days = pd.DatetimeIndex(g.ts[g.trading]); sig = {}
for d, z in Z.dropna().items():
    later = days[days > d]
    if len(later) and z >= 1.0: sig.setdefault(later[0], z)
    elif len(later) == 0 and z >= 1.0: sig.setdefault(pd.Timestamp("2099-01-01"), z)   # signal for the next (not yet loaded) day
sig = pd.Series(sig).sort_index()
T = LF.trades(g, sig, lambda d, z: 1, t0=830, t1=1455, stop=0.5)
T.to_csv("checks/candidates/finra_longs/python_trades.csv", index=False)
from replica import is_early_close
dates = [d for d in sig.index if d.year < 2099 and not is_early_close(d)]
nxt_note = "none" if sig.index[-1].year < 2099 else "the next trading day after " + R.index[-1].strftime("%Y-%m-%d")
mc = lambda d: (d.year - 1900) * 10000 + d.month * 100 + d.day
fill = "\n".join(f"\tSigDate[{i}] = {mc(d)};" for i, d in enumerate(dates))
code = f"""{{ NQ FINRA Short-Volume Longs - RESEARCH / BACKTEST file (personal-account candidate, WATCHLIST #32; NOT for Apex).
  Generated {pd.Timestamp.today().date()} by analysis/finra_mc_export.py from data/finra/short_volume.csv (FINRA data to {R.index[-1].date()}).

  Rule: when the equal-weight FINRA off-exchange short-volume ratio of QQQ + AAPL MSFT NVDA AMZN META GOOGL AVGO TSLA COST NFLX
  is >= 1 sd above its past-60-day mean, buy NQ at the 08:31 CT open the NEXT trading day; stop 0.5 x the daily ATR(15)
  (weekday calendar dates, as Late-Day Flow / Overnight Bias); exit at the 14:55 CT bar close. One trade a day. The signal
  dates are embedded below ({len(dates)} dates, 2018-08 -> {dates[-1].date()}); pending signal: {nxt_note}.
  Python research (analysis/finra_longs_test.py, per NQ after $7.25 + 1 tick per fill, 2018-08 -> 2026-11-06): 374 trades,
  $661 a trade, t 3.51, PF 1.78, max DD $23.9k; random-day longs $138 (p 0.000). Post hoc long-only split: forward log first.
  Chart: @NQ (or MNQ) 1 minute, Exchange time (Central), CME 24-hour session, IOG off. Backtest: Qty 1 on NQ, commission
  $7.25 per round trip (or $3.63 per side) + 1 tick slippage per side. Expected python trade list:
  checks/candidates/finra_longs/python_trades.csv (date, net per NQ after costs). Send the MultiCharts report for a trade-by-trade match. }}

DefineDLLFunc: "kernel32.dll", int, "GetFileAttributesA", lpstr;

{{ LIVE (2026-11-09, user: no manual daily steps): set UseFlagFiles true. The VPS task 'FinraDaily' (live/vps/finra_daily.ps1)
  downloads FINRA's file each weekday evening, computes the same Z and, when Z >= 1, writes C:\TradingLogs\finra\SIG_<FINRA date>.
  At the 08:30 bar the strategy looks for the flag of the previous weekday (= the next trading day of the backtest) instead of
  the embedded dates below, so the file never needs regenerating. CME early-close days are skipped (as the backtest list), and
  a position is never held past its entry day. UseFlagFiles false = the embedded dates (backtests, MultiCharts checks). }}

Inputs:
	EntryTime(830),         {{ bar closing 08:30 -> buy at the next bar's open (08:31) }}
	ExitTime(1455),         {{ exit at the close of this bar }}
	StopAtr(0.5),
	AtrDays(15),
	Qty(1),
	UseFlagFiles(false),    {{ LIVE: true = read the VPS flag files; false = the embedded dates }}
	FlagFolder("C:\TradingLogs\finra\");

Variables:
	DayHi(0), DayLo(0), DayClose(0), PrevDayClose(0),
	TR(0), TrCount(0), TrIdx(0), TrSum(0), Ti(0), ATRv(0),
	StopPts(0), IsSignal(false), Si(0), DayStartTrades(0), TradedToday(false), NSig({len(dates)}),
	PrevWkDay(0), CalMonth(0), CalDay(0), CalDow(0), CalYear(0), IsWeekday(false), IsEarlyClose(false);

Arrays:
	TrHist[100](0), SigDate[{max(len(dates), 1) + 10}](0);

once begin
{fill}
end;

{{ ---------- Daily ATR (weekday calendar dates; same code as NQ_Late_Day_Flow, MultiCharts-confirmed) ---------- }}
if Date <> Date[1] then begin
	if DayClose > 0 then begin
		if DayOfWeek(Date[1]) >= 1 and DayOfWeek(Date[1]) <= 5 then begin
			if PrevDayClose > 0 then
				TR = MaxList(DayHi, PrevDayClose) - MinList(DayLo, PrevDayClose)
			else
				TR = DayHi - DayLo;
			TrHist[TrIdx] = TR;
			TrIdx = Mod(TrIdx + 1, AtrDays);
			if TrCount < AtrDays then TrCount = TrCount + 1;
		end;
		PrevDayClose = DayClose;
	end;
	DayHi = High;
	DayLo = Low;
	DayStartTrades = TotalTrades;
	if DayOfWeek(Date[1]) >= 1 and DayOfWeek(Date[1]) <= 5 then PrevWkDay = Date[1];   {{ the last weekday before today }}
	{{ is today a signal date? }}
	IsSignal = false;
	for Si = 0 to NSig - 1 begin
		if SigDate[Si] = Date then IsSignal = true;
	end;
end
else begin
	DayHi = MaxList(DayHi, High);
	DayLo = MinList(DayLo, Low);
end;
DayClose = Close;

ATRv = 0;
if TrCount >= AtrDays then begin
	TrSum = 0;
	for Ti = 0 to AtrDays - 1 begin
		TrSum = TrSum + TrHist[Ti];
	end;
	ATRv = TrSum / AtrDays;
end;

{{ ---------- CME holiday half-days (same rule as the plan's files): no entry, as the backtest list ---------- }}
CalMonth = Month(Date); CalDay = DayOfMonth(Date); CalDow = DayOfWeek(Date); CalYear = Year(Date) + 1900;
IsWeekday = CalDow >= 1 and CalDow <= 5;
IsEarlyClose = (CalMonth = 1 and ((CalDay = 1 and IsWeekday) or (CalDay = 2 and CalDow = 1)))
	or (CalMonth = 1 and CalDow = 1 and CalDay >= 15 and CalDay <= 21)
	or (CalMonth = 2 and CalDow = 1 and CalDay >= 15 and CalDay <= 21)
	or (CalMonth = 5 and CalDow = 1 and CalDay >= 25)
	or (CalMonth = 6 and CalYear >= 2022 and ((CalDay = 19 and IsWeekday) or (CalDay = 18 and CalDow = 5) or (CalDay = 20 and CalDow = 1)))
	or (CalMonth = 7 and (((CalDay = 3 or CalDay = 4) and IsWeekday) or (CalDay = 5 and CalDow = 1)))
	or (CalMonth = 9 and CalDow = 1 and CalDay <= 7)
	or (CalMonth = 11 and CalDow = 4 and CalDay >= 22 and CalDay <= 28)
	or (CalMonth = 11 and CalDow = 5 and CalDay >= 23 and CalDay <= 29)
	or (CalMonth = 12 and (((CalDay = 24 or CalDay = 25) and IsWeekday) or (CalDay = 26 and CalDow = 1)));

{{ live: the flag of the previous weekday decides (checked at the entry bar, so a chart loaded during the day still sees it) }}
if UseFlagFiles and Time = EntryTime then
	IsSignal = PrevWkDay > 0 and IsEarlyClose = false
		and GetFileAttributesA(FlagFolder + "SIG_" + NumToStr(PrevWkDay + 19000000, 0)) <> -1;

{{ ---------- Entry at the 08:31 open on signal dates; the stop also protects the entry bar ---------- }}
TradedToday = MarketPosition <> 0 or TotalTrades > DayStartTrades;
if Time = EntryTime and IsSignal and ATRv > 0 and MarketPosition = 0 and TradedToday = false then begin
	StopPts = StopAtr * ATRv;
	Buy ("FSV_L") Qty contracts next bar at market;
	Sell ("FSV_SL0") next bar at Close - StopPts stop;      {{ entry-bar protection (fill not known yet) }}
end;

{{ ---------- Stop and time exit ---------- }}
if MarketPosition > 0 then begin
	Sell ("FSV_SL") next bar at EntryPrice - StopPts stop;
	if Time = ExitTime then Sell ("FSV_X") this bar at close;
	if Date <> EntryDate then Sell ("FSV_DX") next bar at market;   {{ safety: never held past the entry day }}
end;
"""
open("checks/candidates/finra_longs/NQ_FINRA_Short_Volume_Longs.txt", "w").write(code)
print(f"wrote {len(dates)} signal dates; python trades {len(T)} (2018+ {int((T.date >= '2018').sum())}); last data {R.index[-1].date()}; pending: {nxt_note}")
