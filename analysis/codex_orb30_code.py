"""Generate the research-only PowerLanguage reconstruction and calendar.
No prices, returns, external messages or live files are accessed.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scratch_data/codex_deps'),str(ROOT/'analysis')]
import pandas as pd
from codex_s03_calendar import calendar_status

HEAD='''{ ORB30 EMA — RESEARCH PROTOTYPE; NOT COMPILED OR MC-CONFIRMED.
  NQ/MNQ, ONE-MINUTE chart, full Globex session, Exchange time CENTRAL.
  Enable Intrabar Order Generation and use one-minute/tick Bar Magnifier.
  Native tick fills can differ from Python minute nearer-extreme paths.
  EMA mode1 = all complete M30 bars; mode2 = cash M30 bars only.
  RR0 disables target. Default1.85 retains the stated rule;4 is an experiment.
  No short entries. No re-entry. Calendar blocks at actual OR date.
  Calendar dates supported2018-2027; extend/review before later use.
  Default UsePercentRisk=true enables INTEGER futures1%; false uses FixedContracts1.
  InitialBalance+NetProfit is THIS STRATEGY'S backtest balance, not a broker
  or shared account balance. Margin and portfolio netting are not modeled.
  Pending quantity uses planned high-low risk; gap fills can exceed budget.
  Author timer flatten is approximated by a15:55 CT completed-minute decision
  and next-tick market exit; no SetExitOnClose/session rollover dependence.
  Built-in stop/target are active on entry bar; actual fill reanchors the stop
  amount on first observed fill tick. Broker acknowledgment is unverified.
  Commission/slippage set in research chart settings, not subtracted twice.
}
[IntrabarOrderGeneration = true]
Inputs: EMAMode(1), EMALength(20), RR(1.85), FlatTime(1555),
        UsePercentRisk(true), RiskPct(1), InitialBalance(100000),
        FixedContracts(1), MaxContracts(100);
Vars: IntrabarPersist StateDate(0), IntrabarPersist ORHigh(0),
      IntrabarPersist ORLow(0), IntrabarPersist ORCount(0),
      IntrabarPersist EMAValue(0), IntrabarPersist EMACount(0),
      IntrabarPersist M30Count(0), IntrabarPersist LastMinute(-1),
      IntrabarPersist LastMinuteDate(0), IntrabarPersist LastBar(-1),
      IntrabarPersist PreviousDate(0), IntrabarPersist DecisionClock(0),
      IntrabarPersist Armed(false), IntrabarPersist Attempted(false),
      IntrabarPersist CarryPosition(false),
      IntrabarPersist TTStart(0), IntrabarPersist DayQty(0),
      IntrabarPersist Blocked(false), IntrabarPersist SignalRisk(0),
      mins(0), prevmins(0), alpha(0), balance(0), ticksize(0),
      stopdistance(0), targetprice(0), targetdistance(0);

if Date <> StateDate then begin
    StateDate=Date; ORCount=0;
    CarryPosition=(MarketPosition<>0);
    { Preserve protective anchors if a missing-bar outage carried a trade. }
    if not CarryPosition then begin ORHigh=0;ORLow=0;end;
    Armed=false; Attempted=false; TTStart=TotalTrades; DayQty=0;
    DecisionClock=0;
    Blocked=(CarryPosition or DayOfWeek(Date)=0 or DayOfWeek(Date)=6
             or Date<1180101 or Date>1271231);
'''
TAIL='''end;

if MarketPosition<>0 or TotalTrades>TTStart then Attempted=true;

if BarStatus(1)=2 and CurrentBar<>LastBar then begin
    LastBar=CurrentBar;
    DecisionClock=Time;
    mins=IntPortion(Time/100)*60+Mod(Time,100);
    { Require successive native minute labels within each M30 bucket. }
    if LastMinuteDate=0 then M30Count=0
    else if not ((LastMinuteDate=Date and mins=LastMinute+1) or
            (DateToJulian(Date)=DateToJulian(LastMinuteDate)+1 and
             LastMinute=1439 and mins=0)) then M30Count=0;
    if Mod(mins,30)=1 then M30Count=0;
    M30Count=M30Count+1;
    if Mod(mins,30)=0 then begin
        if M30Count=30 and
           (EMAMode=1 or (Time>=900 and Time<=1500)) then begin
            if EMACount=0 then EMAValue=Close
            else begin
                alpha=2.0/(EMALength+1);
                EMAValue=alpha*Close+(1-alpha)*EMAValue;
            end;
            EMACount=EMACount+1;
        end;
        M30Count=0;
    end;
    LastMinute=mins;LastMinuteDate=Date;

    if Time>830 and Time<=900 and not CarryPosition then begin
        if ORCount=0 then begin ORHigh=High;ORLow=Low;end
        else begin ORHigh=MaxList(ORHigh,High);ORLow=MinList(ORLow,Low);end;
        ORCount=ORCount+1;
    end;
    if Time=900 and not Blocked and ORCount=30
       and EMACount>=EMALength and Close>EMAValue and ORHigh>ORLow then begin
        SignalRisk=ORHigh-ORLow;
        if UsePercentRisk then begin
            balance=InitialBalance+NetProfit;
            DayQty=IntPortion(MaxList(0,balance)*RiskPct/100/
                            (SignalRisk*BigPointValue));
        end else DayQty=FixedContracts;
        DayQty=MinList(MaxContracts,MaxList(0,DayQty));
        Armed=(DayQty>=1);
    end;
end;

ticksize=MinMove/PriceScale;
if Armed or MarketPosition=1 then begin
    SetStopContract;
    stopdistance=SignalRisk;
    if MarketPosition=1 then stopdistance=EntryPrice-ORLow;
    if stopdistance>0 then begin
        SetStopLoss(stopdistance*BigPointValue);
        if RR>0 then begin
            targetprice=ORHigh+RR*SignalRisk;
            if MarketPosition=1 then targetprice=EntryPrice+RR*stopdistance;
            targetprice=-IntPortion(-targetprice/ticksize)*ticksize;
            { IntPortion truncates toward zero: explicitly round UP. }
            if targetprice < (ORHigh+RR*SignalRisk) and MarketPosition=0
                then targetprice=targetprice+ticksize;
            if MarketPosition=1 and targetprice<EntryPrice+RR*stopdistance
                then targetprice=targetprice+ticksize;
            targetdistance=targetprice-ORHigh;
            if MarketPosition=1 then targetdistance=targetprice-EntryPrice;
            SetProfitTarget(targetdistance*BigPointValue);
        end;
    end;
end;

if Armed and not Attempted and MarketPosition=0
   and DecisionClock>=900 and DecisionClock<FlatTime then
    Buy ("ORB30L") DayQty contracts next bar at ORHigh stop;

if DecisionClock>=FlatTime then begin
    Armed=false;
    if MarketPosition=1 then Sell ("ORB30Time") next bar at market;
end;
if CarryPosition and MarketPosition=1 then
    Sell ("ORB30Carry") next bar at market;
'''

def main():
    dest=ROOT/'agents/codex/code';dest.mkdir(parents=True,exist_ok=True)
    excluded=[]
    for d in pd.date_range('2018-01-01','2027-12-31'):
        z=calendar_status(d)
        if d.weekday()<5 and z['kind']!='normal':excluded.append(dict(date=d.strftime('%Y-%m-%d'),pl_date=(d.year-1900)*10000+d.month*100+d.day,reason=z['reason']))
    lines=['    if Date='+str(q['pl_date'])+' then Blocked=true; { '+q['date']+' '+q['reason']+' }' for q in excluded]
    (dest/'ORB30_EMA_Research.txt').write_text(HEAD+'\n'.join(lines)+'\n'+TAIL,encoding='utf-8')
    pd.DataFrame(excluded).to_csv(ROOT/'analysis/outputs/codex_orb30_ema/code_calendar.csv',index=False)
    print('Generated research prototype; no platform compilation or broker connection.')

if __name__=='__main__':main()
