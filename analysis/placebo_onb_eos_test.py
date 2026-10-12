"""Random-entry placebos for Overnight Bias ML and Expiration Open Short (2026-10-12), following the
r/algotrading post: same stop/target/exit rules, with the entry time, direction or day randomized;
each strategy's own MultiCharts trades re-simulated with the same engine. Record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
import calendar_flows as CF
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g=pickle.load(open(SP+"g24.pkl","rb")); atr=g.daily_atr(15)
PV,COST,TICK=20,7.25,0.25
def br(d,j0,side,stp,tgt,jend,entry=None):
    e=g.o[d,j0] if entry is None else entry
    if np.isnan(e): return None
    sp=e-side*stp; tg=e+side*tgt if tgt else None
    for j in range(j0,jend+1):
        h,l,o=g.h[d,j],g.l[d,j],g.o[d,j]
        if np.isnan(h): continue
        if (side>0 and l<=sp) or (side<0 and h>=sp):
            px=(min(o,sp) if side>0 else max(o,sp)) if j>j0 else sp; return (px-e)*side*PV-COST-2*TICK*PV
        if tg is not None and ((side>0 and h>=tg) or (side<0 and l<=tg)): return tgt*PV-COST-TICK*PV
    px=pd.Series(g.c[d,:jend+1]).ffill().iloc[-1]; return (px-e)*side*PV-COST-2*TICK*PV
def st(x):
    x=np.array([v for v in x if v is not None]); return x.mean(),np.mean(x>0),len(x)
def runs(fn,n,seed):
    rng=np.random.default_rng(seed); r=np.array([st(fn(rng))[:2] for _ in range(n)]); return r
yrs=lambda t: pd.DatetimeIndex(t.date).year>=2018
# ---------------- Overnight Bias ML
o=load_mc(g,"Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias v2.xlsx"); o=o[yrs(o)]
jx=jof(1430)
own=[br(int(t.day),int(t.j0),int(t.side),0.3*atr[int(t.day)],0.9*atr[int(t.day)],jx,entry=t.entry) for _,t in o.iterrows()]
a=st(own); print(f"\nOVERNIGHT BIAS ML ({a[2]} trades): own trades re-simulated  avg ${a[0]:.0f} win {a[1]:.0%}  (MC report avg ${o.net.mean():.0f})")
tests={
 "same days & direction, random time after its entry": lambda rng: [br(int(t.day),int(rng.integers(int(t.j0),max(int(t.j0),jof(1400))+1)),int(t.side),0.3*atr[int(t.day)],0.9*atr[int(t.day)],jx) for _,t in o.iterrows()],
 "same days & entry time, RANDOM direction": lambda rng: [br(int(t.day),int(t.j0),int(rng.choice([-1,1])),0.3*atr[int(t.day)],0.9*atr[int(t.day)],jx,entry=t.entry) for _,t in o.iterrows()],
 "same days & entry time, OPPOSITE direction": lambda rng: [br(int(t.day),int(t.j0),-int(t.side),0.3*atr[int(t.day)],0.9*atr[int(t.day)],jx,entry=t.entry) for _,t in o.iterrows()],
 "random days, random time 8:45-14:00, random direction": lambda rng: [br(int(d),int(rng.integers(jof(846),jof(1400)+1)),int(rng.choice([-1,1])),0.3*atr[int(d)],0.9*atr[int(d)],jx) for d in rng.choice(g.trading[pd.DatetimeIndex(g.ts[g.trading]).year>=2018],len(o))],
}
for k,fn in tests.items():
    r=runs(fn,1 if "OPPOSITE" in k else 20,1)
    beat=np.mean(r[:,0]<a[0])
    print(f"  {k:<55} avg ${r[:,0].mean():5.0f} (range {r[:,0].min():.0f} to {r[:,0].max():.0f}) win {r[:,1].mean():.0%} | own beats {beat:.0%} of runs")
# ---------------- Expiration Open Short
e=load_mc(g,"Backtesting Strategy Performance Report EOS v1.xlsx"); e=e[yrs(e)]
cal=CF.calendar(g); opex=cal.index[cal.opex].to_numpy(); opex=opex[pd.DatetimeIndex(g.ts[opex]).year>=2018]
j830=jof(831); j10=jof(1000)
own=[br(int(t.day),int(t.j0),-1,0.3*atr[int(t.day)],None,j10,entry=t.entry) for _,t in e.iterrows()]
a=st(own); print(f"\nEXPIRATION OPEN SHORT ({a[2]} trades): own re-simulated avg ${a[0]:.0f} win {a[1]:.0%} (MC report avg ${e.net.mean():.0f})")
alld=g.trading[pd.DatetimeIndex(g.ts[g.trading]).year>=2018]
fri=alld[(pd.DatetimeIndex(g.ts[alld]).dayofweek==4)&~np.isin(alld,opex)]
tests={
 "short 8:30-10:00 on RANDOM days": lambda rng: [br(int(d),j830,-1,0.3*atr[int(d)],None,j10) for d in rng.choice(alld,len(e))],
 "short 8:30-10:00 on random NON-expiration Fridays": lambda rng: [br(int(d),j830,-1,0.3*atr[int(d)],None,j10) for d in rng.choice(fri,len(e))],
 "expiration days, short a RANDOM 90 min (10:00-15:00 start)": lambda rng: [br(int(d),int(s),-1,0.3*atr[int(d)],None,int(s)+90) for d in opex for s in [rng.integers(jof(1000),jof(1330)+1)]],
 "expiration days 8:30-10:00, RANDOM direction": lambda rng: [br(int(d),j830,int(rng.choice([-1,1])),0.3*atr[int(d)],None,j10) for d in opex],
}
for k,fn in tests.items():
    r=runs(fn,30,2); beat=np.mean(r[:,0]<a[0])
    print(f"  {k:<58} avg ${r[:,0].mean():5.0f} (range {r[:,0].min():.0f} to {r[:,0].max():.0f}) win {r[:,1].mean():.0%} | own beats {beat:.0%} of runs")
