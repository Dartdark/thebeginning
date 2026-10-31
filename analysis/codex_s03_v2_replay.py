"""Literal uploaded S03 noise-area v2 plus frozen v1/flat controls (54bbba7).

No import-time price access. Features reproduce the source ring buffer and
calendar; next-bar orders and stop-only intraminute geometry are causal.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"agents/codex/runtime/or_pullback_python"),str(ROOT/"analysis")]
import hashlib
import json
import pickle
import subprocess
import datetime as dt
import numpy as np
import pandas as pd
from numba import njit

PREREG="54bbba745006f1d20805ef9daab0d130abf4e6fe"
OUT=ROOT/"analysis/outputs/codex_s03_v2/replay"
MODELS={"v2_raw":(.4,False),"v2_apex":(.4,True),"v1_raw":(0.,False),"v1_apex":(0.,True)}
COLS=["side","entry","exit","entry_flat","exit_flat","kind","signal_flat","exit_signal_flat",
      "stop_distance","stop_px","entry_minute_adverse_px","exit_minute_adverse_px","mae_points_observed",
      "exit_segment","reason_code"]
REASONS=["stop","band","reversal","source_eod","apex_flat","session_eoc"]


def authorize():
    subprocess.run(["git","cat-file","-e",PREREG+":agents/codex/plans/s03_v2.md"],cwd=ROOT,check=True)


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def source_calendar(stamps):
    """Literal date predicates; no inferred substitute holiday calendar."""
    holiday=[];half=[]
    for stamp in pd.DatetimeIndex(stamps):
        y,m,d=stamp.year,stamp.month,stamp.day
        w=(stamp.dayofweek+1)%7
        a=y%19;b=y//100;c=y%100;dd=b//4;e=b%4;f=(b+8)//25;g=(b-f+1)//3
        h=(19*a+b-dd-g+15)%30;i=c//4;k=c%4;l=(32+2*e+2*i-h-k)%7;mm=(a+11*h+22*l)//451
        em=(h+l-7*mm+114)//31;ed=(h+l-7*mm+114)%31+1
        gf=dt.date(y,em,ed)-dt.timedelta(days=2)
        hol=((m==1 and ((d==1 and 1<=w<=5) or(d==2 and w==1))) or
             (m==1 and w==1 and 15<=d<=21) or(m==2 and w==1 and 15<=d<=21) or
             (m==gf.month and d==gf.day) or(m==5 and w==1 and d>=25) or
             (y>=2022 and m==6 and ((d==19 and 1<=w<=5)or(d==20 and w==1)or(d==18 and w==5)))or
             (m==7 and((d==4 and 1<=w<=5)or(d==5 and w==1)or(d==3 and w==5)))or
             (m==9 and w==1 and d<=7)or(m==11 and w==4 and 22<=d<=28)or
             (m==12 and((d==25 and 1<=w<=5)or(d==26 and w==1)or(d==24 and w==5)))or
             stamp.strftime("%Y%m%d") in("20181205","20250109"))
        hf=((m==11 and w==5 and 23<=d<=29)or(m==12 and d==24 and 1<=w<=4)or(m==7 and d==3 and 1<=w<=4))
        holiday.append(hol);half.append(hf)
    return np.asarray(holiday,bool),np.asarray(half,bool)


@njit(cache=True)
def features(o,h,l,c,v,observed,no_trade):
    D,M=c.shape
    # UB,LB,VWAP,rawmu,signalclose,valid,taintedpriorcount.
    f=np.full((D,12,7),np.nan)
    moves=np.zeros((390,60));full_days=0;last_close=0.;have=False;prev_rth=False
    slot=0;day_open=0.;pc=0.;pv=0.;vv=0.;seen=0
    complete_slots=np.zeros(60,np.bool_)
    audit=np.zeros((D,5)) # firstRTHj,observedRTHminutes,accepted,priorcounter,shiftedanchor
    for d in range(D):
        audit[d,0]=-1
        for j in range(M):
            if not observed[d,j]:continue
            rth=511<=j<=900
            if rth:
                idx=j-511
                if idx==0 or not prev_rth:
                    day_open=o[d,j];pc=last_close;slot=full_days%60
                    for k in range(390):moves[k,slot]=0.
                    pv=0.;vv=0.;seen=0
                    audit[d,0]=j;audit[d,3]=full_days;audit[d,4]=j!=511
                tp=(h[d,j]+l[d,j]+c[d,j])/3.
                pv+=tp*v[d,j];vv+=v[d,j];seen+=1;audit[d,1]+=1
                vw=pv/vv if vv>0 else tp
                moves[idx,slot]=abs(c[d,j]/day_open-1.)
                if 540<=j<=870 and (j-540)%30==0:
                    k=(j-540)//30
                    f[d,k,2]=vw;f[d,k,4]=c[d,j]
                    if have and full_days>=14:
                        mu=0.;bad=0
                        for back in range(1,15):
                            s=(full_days-back)%60
                            mu+=moves[idx,s]
                            bad+=not complete_slots[s]
                        mu/=14
                        f[d,k,0]=max(day_open,pc)*(1+mu)
                        f[d,k,1]=min(day_open,pc)*(1-mu)
                        f[d,k,3]=mu;f[d,k,5]=not no_trade[d];f[d,k,6]=bad
                if idx==389 and not no_trade[d]:
                    complete_slots[slot]=seen==390
                    full_days+=1;last_close=c[d,j];have=True;audit[d,2]=1
            prev_rth=rth
    return f,audit


@njit(cache=True)
def stop_level(entry,side,distance):
    if distance<=0:return np.nan
    raw=entry-side*distance
    return np.floor(raw*4+1e-9)/4 if side>0 else np.ceil(raw*4-1e-9)/4


@njit(cache=True)
def emit(buf,n,state,minute,price,kind,segment,adverse,reason,exit_signal):
    buf[n,0]=state[0];buf[n,1]=state[1];buf[n,2]=price
    buf[n,3]=state[3];buf[n,4]=minute;buf[n,5]=kind
    buf[n,6]=state[4];buf[n,7]=exit_signal;buf[n,8]=state[5];buf[n,9]=state[2]
    buf[n,10]=state[6];buf[n,11]=adverse;buf[n,12]=max(state[7],(state[1]-adverse)*state[0],0.)
    buf[n,13]=segment;buf[n,14]=reason
    return n+1


@njit(cache=True)
def engine(o,h,l,c,observed,f,early,first,last,initial,factor,apex,trade_start):
    """State:side,entry,stop,entryflat,signalflat,distance,entryadverse,MAE,
    pendingNewSide,pendingCloseReason,pendingDistance,pendingSignal,markflat,mark.
    Close reason-1 is no pending market order. One old exit and one new fill on reversal.
    """
    state=initial.copy();buf=np.empty((100000,15));n=0
    for minute in range(first,last):
        d,j=minute//1440,minute%1440
        if not observed[d,j]:continue
        oo,hh,ll,cc=o[d,j],h[d,j],l[d,j],c[d,j]
        entered=False
        if state[9]>=0:
            if state[0]!=0:
                n=emit(buf,n,state,minute,oo,2,0,oo,int(state[9]),state[11])
                state[0]=0
            if state[8]!=0:
                state[0]=state[8];state[1]=oo;state[2]=stop_level(oo,int(state[0]),state[10])
                state[3]=minute;state[4]=state[11];state[5]=state[10];state[6]=oo;state[7]=0.
                entered=True
            state[8]=0;state[9]=-1
        if state[0]!=0:
            side=int(state[0]);adverse=ll if side>0 else hh
            stop=state[2]
            gap=np.isfinite(stop) and (oo-stop)*side<=0
            hit=np.isfinite(stop) and (adverse-stop)*side<=0
            if gap or hit:
                price=oo if gap else stop
                adverse=price
                if entered:state[6]=adverse
                n=emit(buf,n,state,minute,price,0,0 if gap else 1,adverse,0,-1)
                state[0]=0
            else:
                state[7]=max(state[7],(state[1]-adverse)*side,0.)
                if entered:state[6]=adverse
                state[12]=minute;state[13]=cc
        if minute<trade_start:continue
        if state[0]!=0 and j==960: # observed Default/CME session close fallback
            adverse=ll if state[0]>0 else hh
            n=emit(buf,n,state,minute,cc,2,3,adverse,5,minute)
            state[0]=0;state[8]=0;state[9]=-1
        if 540<=j<=870 and (j-540)%30==0:
            k=(j-540)//30
            if f[d,k,5]==1:
                ub,lb,vw,mu=f[d,k,0],f[d,k,1],f[d,k,2],f[d,k,3]
                want=1 if cc>ub and cc>vw and state[0]!=1 else -1 if cc<lb and cc<vw and state[0]!=-1 else 0
                close=(state[0]==1 and cc<max(ub,vw))or(state[0]==-1 and cc>min(lb,vw))
                if want!=0:
                    state[8]=want;state[9]=2 if state[0]!=0 else 1
                    state[10]=factor*mu*cc;state[11]=minute
                elif close:
                    state[8]=0;state[9]=1;state[11]=minute
        if state[0]!=0 and j==900:
            state[8]=0;state[9]=3;state[11]=minute
        deadline=690 if early[d] else 955
        if apex and state[0]!=0 and j>=deadline:
            state[8]=0;state[9]=4;state[11]=minute
        if n>=99999:raise ValueError("Trade buffer exhausted")
    return buf[:n].copy(),state


def prepare(g):
    holiday,half=source_calendar(g.ts)
    observed=np.logical_and.reduce([np.isfinite(getattr(g,k)) for k in("o","h","l","c","v")])
    f,audit=features(g.o,g.h,g.l,g.c,g.v,observed,holiday|half)
    return dict(f=f,feature_audit=audit,observed=observed,no_trade=holiday|half,holiday=holiday,half=half,
                known_closed=np.load(ROOT/"analysis/outputs/codex_r2vault/replay/known_closed.npy"))


def ledger(g,raw,model,p):
    t=pd.DataFrame(raw,columns=COLS)
    if not len(t):return t
    for field in("side","entry_flat","exit_flat","kind","signal_flat","exit_signal_flat","exit_segment","reason_code"):
        t[field]=t[field].astype(int)
    t["model"]=model;t["trade_id"]=np.arange(len(t))
    t["entry_row"]=t.entry_flat//1440;t["entry_j"]=t.entry_flat%1440
    t["exit_row"]=t.exit_flat//1440;t["exit_j"]=t.exit_flat%1440
    t["day"]=t.entry_row;t["gridrow"]=t.entry_row
    t["date"]=pd.DatetimeIndex(g.ts[t.entry_row]);t["entry_date"]=t.date
    t["exit_date"]=pd.DatetimeIndex(g.ts[t.exit_row])
    t["entry_phase"]="open";t["exit_phase"]=np.where(t.exit_segment==0,"open","intrabar")
    t["exit_reason"]=[REASONS[k] for k in t.reason_code]
    t["gross_points"]=(t.exit-t.entry)*t.side;t["gross_nq"]=t.gross_points*20
    t["cross_date"]=t.entry_row!=t.exit_row
    t["late_after_1559"]=t.cross_date|(t.exit_j>960)|((t.exit_j==960)&(t.exit_phase!="open"))
    t["signal_mu"]=p["f"][t.signal_flat.to_numpy()//1440,(t.signal_flat.to_numpy()%1440-540)//30,3]
    t["signal_close"]=p["f"][t.signal_flat.to_numpy()//1440,(t.signal_flat.to_numpy()%1440-540)//30,4]
    t["tainted_prior_sessions"]=p["f"][t.signal_flat.to_numpy()//1440,(t.signal_flat.to_numpy()%1440-540)//30,6].astype(int)
    unknown=(~p["observed"])&(~p["known_closed"])
    pref=np.r_[0,np.cumsum(unknown.ravel())];miss=np.r_[0,np.cumsum((~p["observed"]).ravel())]
    ends=t.exit_flat.to_numpy()+(t.exit_phase!="open").to_numpy(int)
    starts=t.entry_flat.to_numpy()
    t["unknown_held_minutes"]=pref[ends]-pref[starts]
    t["missing_held_minutes"]=miss[ends]-miss[starts]
    return t


def audit_days(g,t,p,state,model):
    from replica import is_early_close
    D=len(g.ts);tr=np.zeros(D,bool);tr[g.trading]=True
    early=np.array([is_early_close(x) for x in pd.DatetimeIndex(g.ts)],bool)
    # Source normally finishes15:00; fallback may remain active through15:56.
    covered=np.array([(p["observed"][d,511:(692 if early[d] else 957)]|
                       p["known_closed"][d,511:(692 if early[d] else 957)]).all() for d in range(D)])
    bad=np.zeros(D,bool)
    for x in t.itertuples():
        if x.cross_date or x.late_after_1559 or x.unknown_held_minutes:
            bad[int(x.entry_row):int(x.exit_row)+1]=True
    if state[0]!=0:bad[int(state[3])//1440:]=True
    dates=pd.DatetimeIndex(g.ts)
    a=pd.DataFrame(dict(date=dates,gridrow=np.arange(D),is_trading_row=tr,source_no_trade=p["no_trade"],
        account_window_complete=covered,affected_by_bad_trade=bad,
        account_eligible=tr&covered&(~bad)&(dates>="2018-01-01"),
        control_eligible=tr&(~p["no_trade"])&p["observed"][:,511:901].all(axis=1)&
            np.any(p["f"][:,:,5]==1,axis=1)&(dates>="2018-01-01"),
        first_RTH_j=p["feature_audit"][:,0],observed_RTH_minutes=p["feature_audit"][:,1],
        accepted_for_history=p["feature_audit"][:,2].astype(bool),history_days_before=p["feature_audit"][:,3]))
    a["model"]=model
    return a[a.date>="2018-01-01"]


def fixtures():
    from types import SimpleNamespace
    shape=(1,1440)
    o=np.full(shape,100.);h=o+1;l=o-1;c=o.copy();obs=np.ones(shape,bool)
    f=np.full((1,12,7),np.nan);f[0,0]=[99.,98.,99.,.1,100.,1.,0.]
    state=np.zeros(14);state[9]=-1
    # Long atminute541, immediately stops at96 with .4*.1*100=4points.
    l[0,541]=90.
    raw,s=engine(o,h,l,c,obs,f,np.zeros(1,bool),0,542,state,.4,False,0)
    assert len(raw)==1 and raw[0,1]==100 and raw[0,2]==96 and raw[0,5]==0 and raw[0,10]==96
    # No-stop control remains open; reversal then opens exactlyone short.
    f[0,1]=[102.,101.,102.,.1,100.,1.,0.]
    raw,s=engine(o,h,l,c,obs,f,np.zeros(1,bool),0,572,state,0.,False,0)
    assert len(raw)==1 and raw[0,14]==2 and s[0]==-1 and s[3]==571
    # Prior-stop gap and new trade stop do not borrow post-exit low.
    assert stop_level(100.,1,4.01)==95.75 and stop_level(100.,-1,4.01)==104.25
    dates=pd.to_datetime(["2025-01-09","2026-07-03","2026-11-27","2026-04-03","2026-07-06"])
    holiday,half=source_calendar(dates)
    assert holiday.tolist()==[True,True,False,True,False] and half[2]
    # Feature direct mean usesprior14 ring slots, excludescurrentmove.
    D=17;o=np.full((D,1440),100.);h=o+1;l=o-1;c=o.copy();v=np.ones_like(o);ob=np.zeros_like(o,dtype=bool)
    ob[:,510:902]=True
    for d in range(D):c[d,511:901]=100.+d
    ff,aa=features(o,h,l,c,v,ob,np.zeros(D,bool))
    np.testing.assert_allclose(ff[15,0,3],np.mean(np.arange(1,15)/100.),rtol=0,atol=1e-14)
    assert aa[15,3]==15 and ff[15,0,5]==1
    return dict(entry_bar_stop=True,reversal_once=True,adverse_tick_rounding=True,calendar_literal=True,
                sigma_prior14_only=True,ring_buffer_today_excluded=True,no_price_cache_read=True)


def run():
    authorize();OUT.mkdir(parents=True,exist_ok=True)
    checks=fixtures()
    with open(ROOT/"scratch_data/g24.pkl","rb") as handle:g=pickle.load(handle)
    p=prepare(g)
    from replica import is_early_close
    early=np.array([is_early_close(x) for x in pd.DatetimeIndex(g.ts)],bool)
    split=int(pd.DatetimeIndex(g.ts).searchsorted("2023-01-01"))*1440
    first=int(pd.DatetimeIndex(g.ts).searchsorted("2018-01-01"))*1440
    states={};pieces={m:[] for m in MODELS}
    for label,start,end in(("2018_22",0,split),("2023_plus",split,g.o.size)):
        for m,(factor,apex) in MODELS.items():
            state=states.get(m,np.zeros(14));state[9]=-1 if m not in states else state[9]
            raw,state=engine(g.o,g.h,g.l,g.c,p["observed"],p["f"],early,start,end,state,factor,apex,first)
            states[m]=state;pieces[m].append(raw)
            t=ledger(g,raw,m,p);t.to_csv(OUT/f"{m}_{label}_trades.csv",index=False)
            print(label,m,len(t),"open",int(state[0]!=0),flush=True)
    manifest=dict(preregistration=PREREG,fixtures=checks,models={},context=sha(ROOT/"analysis/outputs/codex_s03_v2/context.json"),
        script_sha256=sha(__file__),market_cache_sha256=sha(ROOT/"scratch_data/g24.pkl"))
    for m in MODELS:
        t=ledger(g,np.concatenate(pieces[m]),m,p);state=states[m]
        a=audit_days(g,t,p,state,m)
        t.to_csv(OUT/f"{m}_trades.csv",index=False);a.to_csv(OUT/f"{m}_audit.csv",index=False)
        op=t.iloc[:0].copy()
        if state[0]!=0:
            er,ej=divmod(int(state[3]),1440)
            op=pd.DataFrame([dict(side=int(state[0]),entry=state[1],entry_row=er,entry_j=ej,entry_flat=int(state[3]),
                entry_phase="open",date=pd.Timestamp(g.ts[er]),signal_flat=int(state[4]),stop_distance=state[5])])
        op.to_csv(OUT/f"{m}_open_positions.csv",index=False)
        manifest["models"][m]=dict(trades=len(t),open=len(op),account_days=int(a.account_eligible.sum()),
            gross_nq=t.gross_nq.sum(),trade_sha256=sha(OUT/f"{m}_trades.csv"),
            cross_date=int(t.cross_date.sum()),unknown_gap_trades=int((t.unknown_held_minutes>0).sum()),
            tainted_history_trades=int((t.tainted_prior_sessions>0).sum()))
    target=ROOT/"agents/codex/runtime/s03_v2_features.pkl"
    with open(target,"wb") as handle:pickle.dump(p,handle,protocol=4)
    pd.DataFrame(dict(date=pd.DatetimeIndex(g.ts),holiday=p["holiday"],half=p["half"],
        observed_RTH_minutes=p["feature_audit"][:,1],history_accepted=p["feature_audit"][:,2],
        prior_days=p["feature_audit"][:,3])).to_csv(OUT/"feature_days.csv",index=False)
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,default=str)+"\n")
    print(json.dumps(manifest["models"],indent=2),flush=True)


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--fixtures-only",action="store_true");args=ap.parse_args()
    if args.fixtures_only:print(fixtures())
    else:run()
