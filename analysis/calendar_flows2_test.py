"""Structural calendar flows round 2 (2026-10-12): index rebalance / reconstitution days,
quarterly roll week, buyback blackout windows, VIX expiration Wednesdays (raw windows on NQ and
ES, FOMC overlap check), then the two survivors in the funded bench (commented block).
Expects pickled grids and the funded lab from a scratch run; kept as the record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
import calendar_flows as CF
from grid24 import jof
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
def third_fri(y,m):
    d1=pd.Timestamp(y,m,1); return d1+pd.Timedelta(days=(4-d1.dayofweek)%7+14)
def vix_exp(y,m):
    # Wednesday 30 days before the third Friday of the NEXT month
    ny,nm=(y+1,1) if m==12 else (y,m+1)
    return third_fri(ny,nm)-pd.Timedelta(days=30)
for name,f,pv,cost in (("NQ","g24.pkl",20,7.25+2*5),("ES","ge.pkl",50,5+2*12.5)):
    g=pickle.load(open(SP+f,"rb")); cal=CF.calendar(g); tr=g.trading
    C=pd.DataFrame(g.c).ffill(axis=1).to_numpy()
    dates=pd.DatetimeIndex(g.ts[tr]); dset=pd.Series(tr,index=dates)
    o=g.o[tr,jof(831)]
    W={"open 8:30-10:00":C[tr,jof(1000)]-o,"RTH 8:30-15:00":C[tr,jof(1500)]-o,
       "last hour 14:00-15:00":C[tr,jof(1500)]-C[tr,jof(1400)],"last 30m":C[tr,jof(1500)]-C[tr,jof(1430)],
       "next open 15:00->8:30":np.r_[g.o[tr[1:],jof(831)]-C[tr[:-1],jof(1500)],np.nan]}
    df=pd.DataFrame({k:v*pv for k,v in W.items()},index=dates)
    df=df[df.index.year>=2018]; yr=df.index.year
    ev={}
    def mark(ds):
        ds=pd.DatetimeIndex(ds); out=[]
        for d in ds:   # last trading day on or before d
            c=df.index[df.index<=d]
            if len(c) and (d-c[-1]).days<4: out.append(c[-1])
        return pd.DatetimeIndex(sorted(set(out)))
    Y=range(2018,2027)
    q=[third_fri(y,m) for y in Y for m in (3,6,9,12)]
    ev["S&P quarterly rebalance (triple witching)"]=mark(q)
    ev["Nasdaq-100 reconstitution (Dec 3rd Fri)"]=mark([third_fri(y,12) for y in Y])
    def last_fri_june(y):
        d=pd.Timestamp(y,6,30); return d-pd.Timedelta(days=(d.dayofweek-4)%7)
    ev["Russell reconstitution (last Fri June)"]=mark([last_fri_june(y) for y in Y])
    ev["VIX expiration Wednesday"]=mark([vix_exp(y,m) for y in Y for m in range(1,13)])
    # roll: Thursday 8 days before quarterly expiry; roll week = Mon-Fri containing it
    roll=[third_fri(y,m)-pd.Timedelta(days=8) for y in Y for m in (3,6,9,12)]
    rw=[d for r in roll for d in pd.date_range(r-pd.Timedelta(days=3),r+pd.Timedelta(days=1))]
    ev["roll week (week before triple witching)"]=pd.DatetimeIndex([d for d in rw if d in df.index])
    ev["roll Thursday"]=mark(roll)
    # buyback blackout approx: from the 15th of the quarter's last month to the 25th of the next month
    bb=[]
    for d in df.index:
        m=d.month
        if (m in (3,6,9,12) and d.day>=15) or (m in (1,4,7,10) and d.day<=25): bb.append(d)
    ev["buyback blackout (approx.)"]=pd.DatetimeIndex(bb)
    ev["buyback open window"]=df.index.difference(pd.DatetimeIndex(bb))
    ev["day after triple witching"]=pd.DatetimeIndex([df.index[df.index.get_loc(d)+1] for d in ev["S&P quarterly rebalance (triple witching)"] if df.index.get_loc(d)+1<len(df)])
    print(f"\n===== {name} (long $ per contract, net of ${cost:.0f} round trip) =====")
    for col in df.columns:
        x=df[col].dropna(); print(f"  baseline {col:<24} n={len(x)} mean ${x.mean():6.0f}")
    for lab,ds in ev.items():
        print(f" {lab}")
        sub=df.loc[df.index.intersection(ds)]
        for col in df.columns:
            x=sub[col].dropna()
            if len(x)<8: continue
            base=df[col].dropna().mean()
            by=(x).groupby(x.index.year).mean()
            t=(x.mean()-base)/x.std()*np.sqrt(len(x))
            print(f"   {col:<24} n={len(x):4d} mean ${x.mean():6.0f} (vs all {base:5.0f}) t_diff={t:4.1f} up {(x>0).mean():.0%} yrs+ {(by>0).sum()}/{len(by)}")
    from event_days import FOMC_DATES
    fomc=pd.DatetimeIndex(pd.to_datetime(FOMC_DATES))
    print(" --- FOMC overlap check ---")
    for lab in ("VIX expiration Wednesday","roll week (week before triple witching)","S&P quarterly rebalance (triple witching)","day after triple witching"):
        ds=df.index.intersection(ev[lab]); nf=ds.difference(fomc)
        for col in ("RTH 8:30-15:00","last hour 14:00-15:00"):
            x=df.loc[nf,col].dropna(); base=df[col].mean()
            print(f"   {lab:<42} {col:<22} FOMC days in set {len(ds)-len(nf):3d}; without them n={len(x)} mean ${x.mean():5.0f} t_diff={(x.mean()-base)/x.std()*np.sqrt(len(x)):4.1f}")

# ---------------- funded bench (separate run)
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# from grid import execute
# from grid24 import jof
# from portfolio import load_mc
# import intraday_research as IR
# SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
# g=pickle.load(open(SP+"g24.pkl","rb")); lab=pickle.load(open(SP+"lab.pkl","rb"))
# atr=g.daily_atr(15); tr=g.trading; dates=pd.DatetimeIndex(g.ts[tr]); row=pd.Series(tr,index=dates)
# def third_fri(y,m):
#     d1=pd.Timestamp(y,m,1); return d1+pd.Timedelta(days=(4-d1.dayofweek)%7+14)
# Y=range(2017,2027)
# roll=[third_fri(y,m)-pd.Timedelta(days=8) for y in Y for m in (3,6,9,12)]
# rw=pd.DatetimeIndex([d for r in roll for d in pd.date_range(r-pd.Timedelta(days=3),r+pd.Timedelta(days=1))])
# tw=[third_fri(y,m) for y in Y for m in (3,6,9,12)]
# after_tw=[]
# for d in tw:
#     nxt=dates[dates>d]
#     if len(nxt) and (nxt[0]-d).days<=4: after_tw.append(nxt[0])
# def summ(t,name):
#     t2=t[pd.DatetimeIndex(t.date).year>=2018].copy(); t2["slips"]=1+(t2["kind"]!=1); t2["net"]-=t2["slips"]*5
#     s=IR.summary(t2); by=t2.groupby(pd.DatetimeIndex(t2.date).year).net.mean().round().to_dict()
#     print(f"{name:<44} n={s['trades']:4d} win {s['win']} avg ${s['avg']:5.0f} PF {s['pf']:.2f} t={s['t_stat']:4.1f} yrs+ {s['years_pos']}  {by}")
# def sig(days,side,st,ex=1500):
#     d=row.reindex(days).dropna().astype(int).to_numpy()
#     return pd.DataFrame(dict(day=d,dj=jof(830),side=side,stop=st*atr[d],target=np.inf,exit_j=jof(ex)))
# for st in (0.3,0.5):
#     t=execute(g,sig(rw,-1,st),max_trades=1); summ(t,f"roll week short 8:30-15:00 stop {st}"); lab.add(f"RWS{int(st*10)}",t,stop_pts=st*atr)
#     for dow in range(5):
#         tt=t[pd.DatetimeIndex(t.date).dayofweek==dow]; summ(tt,f"   weekday {dow}")
# t=execute(g,sig(after_tw,1,0.3),max_trades=1); summ(t,"day after triple witching long, stop 0.3"); lab.add("ATW",t,stop_pts=0.3*atr)
# base={"VB":3,"ONB":("risk",300),"OND_MC":("risk",500),"EOS":("risk",500)}
# plans={"Current funded set":base}
# for k in ("RWS3","RWS5","ATW"):
#     for rk in (200,400):
#         p=dict(base); p[k]=("risk",rk); plans[f"  + {k} ${rk}"]=p
# print(lab.corr(["VB","ONB","OND_MC","EOS","RWS3","ATW"]).round(2).to_string())
# print(lab.table(plans)); print(lab.table(plans,horizon=500))
