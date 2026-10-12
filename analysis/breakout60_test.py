"""60-minute NQ breakout (user idea, 2026-10-12): long when the close is above the 200-bar SMA and above
the prior 40-bar high (mirror for shorts); stop 2x ATR(14); exit on a break of the opposite 40-bar
extreme. As written (multi-day) and Apex-legal (flat 15:00 CT) versions, sensitivity, and the long-only
daytime version in the funded bench (second block, commented). Per NQ after $7.25 + 1 tick per fill."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g=pickle.load(open(SP+"g24.pkl","rb"))
b=g.bars(60); D,K=b["c"].shape
flat={k:b[k].ravel() for k in ("o","h","l","c")}; idx=np.nonzero(~np.isnan(flat["c"]))[0]
o,h,l,c=(flat[k][idx] for k in ("o","h","l","c"))
day=idx//K; hr=(b["j"][idx%K]//60)          # bar close hour (CT), 0..23 ; bar closing at hr:00
dt=pd.DatetimeIndex(g.ts[day])
sma=pd.Series(c).rolling(200).mean().to_numpy()
hh=pd.Series(h).rolling(40).max().shift(1).to_numpy(); ll=pd.Series(l).rolling(40).min().shift(1).to_numpy()
pc=np.r_[np.nan,c[:-1]]; trr=np.nanmax(np.c_[h-l,np.abs(h-pc),np.abs(l-pc)],1); atr=pd.Series(trr).rolling(14).mean().to_numpy()
PV,COST,TICK=20,7.25,0.25
def run(mode, atr_mult=2.0, n=40):
    """mode 'swing' = as written (hold across days); 'apex' = entries any hour up to 14:00 CT, flat at 15:00 CT;
       'rth' = entries only on bars closing 9:00-14:00 CT, flat at 15:00 CT"""
    HH=pd.Series(h).rolling(n).max().shift(1).to_numpy(); LL=pd.Series(l).rolling(n).min().shift(1).to_numpy()
    trades=[]; pos=0; i=200
    N=len(c)
    while i<N-1:
        if pos==0:
            okt = True
            if mode=="rth": okt = 9<=hr[i]<=14 and hr[i]!=15
            if mode=="apex": okt = not (14<hr[i]<=17)          # no entries on bars closing 15:00-17:00
            if okt and not np.isnan(sma[i]) and not np.isnan(atr[i]):
                side = 1 if (c[i]>sma[i] and c[i]>HH[i]) else (-1 if (c[i]<sma[i] and c[i]<LL[i]) else 0)
                if side:
                    e=o[i+1]; stop=e-side*atr_mult*atr[i]; pos=side; ent_i=i+1; i+=1; continue
            i+=1; continue
        # in position at bar i (entered at open of ent_i)
        trail = LL[i] if pos>0 else HH[i]                     # opposite 40-bar extreme (known at bar start)
        lvl = max(stop,trail) if pos>0 else min(stop,trail)
        if (pos>0 and l[i]<=lvl) or (pos<0 and h[i]>=lvl):
            px = min(o[i],lvl) if pos>0 else max(o[i],lvl)
            if i==ent_i: px=lvl if ((pos>0 and o[i]>lvl) or (pos<0 and o[i]<lvl)) else o[i]
            trades.append((dt[ent_i],dt[i],pos,e,px,(px-e)*pos*PV-COST-2*TICK*PV,ent_i,i)); pos=0; i+=1; continue
        if mode in ("apex","rth") and (hr[i]==15 or (i+1<N and day[i+1]!=day[i] and hr[i]>=12 and hr[i]<=15)):
            px=c[i]; trades.append((dt[ent_i],dt[i],pos,e,px,(px-e)*pos*PV-COST-2*TICK*PV,ent_i,i)); pos=0; i+=1; continue
        i+=1
    return pd.DataFrame(trades,columns=["entry_date","exit_date","side","entry","exit","net","bi0","bi1"])
def rep(t,lab):
    t=t[t.entry_date.dt.year>=2018]; x=t.net; by=x.groupby(t.entry_date.dt.year).sum()
    eq=x.cumsum(); dd=(eq-eq.cummax()).min()
    hold=(t.exit_date-t.entry_date).dt.days.mean()
    print(f"  {lab:<44} n={len(x):4d} ({len(x)/8.8:.0f}/yr) win {np.mean(x>0):.0%} avg ${x.mean():6.0f} PF {x[x>0].sum()/-x[x<0].sum():.2f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f} yrs+ {(by>0).sum()}/9 maxDD ${dd:,.0f} hold {hold:.1f}d")
    for s,nm in ((1,"longs"),(-1,"shorts")):
        y=x[t.side==s]; 
        if len(y): print(f"      {nm:<6} n={len(y)} avg ${y.mean():.0f} PF {y[y>0].sum()/max(1,-y[y<0].sum()):.2f}")
    return by
print("NQ 60-min, 40-bar breakout above/below 200 SMA, stop 2x ATR(14), exit on break of opposite 40-bar extreme; per NQ after $7.25 + 1 tick per fill, 2018-2026")
by=rep(run("swing"),"As written (holds across days)"); print("      by year:",by.round().astype(int).to_dict())
rep(run("apex"),"Apex-legal: any hour, flat at 15:00 CT")
rep(run("rth"),"Apex-legal: entries 9:00-14:00 CT, flat 15:00")
print(" sensitivity (as written):")
for n in (20,55):
    for am in (2.0,3.0):
        rep(run("swing",am,n),f"  {n}-bar breakout, {am}x ATR stop")

# ---- longs only, RTH entries, flat 15:00: by year + funded bench
from grid24 import jof
t=run("rth"); t=t[(t.side==1)&(t.entry_date.dt.year>=2018)]
x=t.net; by=x.groupby(t.entry_date.dt.year).agg(["count","mean","sum"]).round()
print("\nLONGS ONLY, entries 9:00-14:00 CT, flat 15:00:", f"n={len(x)} win {np.mean(x>0):.0%} avg ${x.mean():.0f} PF {x[x>0].sum()/-x[x<0].sum():.2f} t={x.mean()/x.std()*np.sqrt(len(x)):.1f}")
print(by.T.to_string())

# ---------------- funded bench
# exec(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/don60.py").read().split("print(\"NQ 60-min")[0])
# lab=pickle.load(open(SP+"lab.pkl","rb"))
# t=run("rth"); t=t[(t.side==1)]
# jj=b["j"]
# tt=pd.DataFrame(dict(day=(idx[t.bi0.values]//K), j0=np.maximum(jj[idx[t.bi0.values]%K]-59,0), j1=jj[idx[t.bi1.values]%K],
#     side=1, entry=t.entry.values, exit=t.exit.values, kind=0, net=t.net.values, date=t.entry_date.values, slips=2))
# tt["pnl"]=(tt.exit-tt.entry)*20
# bad=tt.j1<tt.j0; print("bad rows",bad.sum()); print(tt[bad].head()); tt=tt[~bad]; t=t[~bad.values]
# # stop distance per day for risk sizing: 2 x ATR(60m) at entry, mapped to the entry day
# stop=np.full(g.D,np.nan); stop[tt.day.values]=2*atr[t.bi0.values-1]
# stop=pd.Series(stop).ffill().bfill().to_numpy()
# lab.add("DON60L",tt,stop_pts=stop,slippage=False)
# print(lab.corr(["VB","ONB_ML_MC","OND_MC","EOS","DON60L"]).round(2).to_string())
# base={"VB":3,"ONB_ML_MC":("risk",300),"OND_MC":("risk",500),"EOS":("risk",500)}
# plans={"Funded set":base}
# for rk in (200,400): p=dict(base); p["DON60L"]=("risk",rk); plans[f"  + 60-min breakout longs ${rk}"]=p
# p=dict(base); p.pop("VB"); p["DON60L"]=("risk",400); plans["  60-min breakout longs $400 instead of VB"]=p
# print(lab.table(plans)); print(lab.table(plans,horizon=500))
