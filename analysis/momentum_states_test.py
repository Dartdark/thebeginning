"""Goulding, Harvey & Mazzoleni "Momentum Turning Points" (SSRN 3489539): Bull / Correction / Bear /
Rebound states from slow (12-month) and fast (1-month) NQ momentum, known at the previous close;
next-month NQ returns and the funded strategies by state, 2018-2026. Record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g=pickle.load(open(SP+"g24.pkl","rb")); lab=pickle.load(open(SP+"lab.pkl","rb"))
tr=g.trading; dates=pd.DatetimeIndex(g.ts[tr]); C=pd.DataFrame(g.c).ffill(axis=1).to_numpy()
cl=pd.Series(C[tr,jof(1500)],index=dates)
def states(slow=252,fast=21):
    s=(cl/cl.shift(slow)-1).shift(1); f=(cl/cl.shift(fast)-1).shift(1)   # known at the previous close
    st=np.select([(s>=0)&(f>=0),(s>=0)&(f<0),(s<0)&(f<0),(s<0)&(f>=0)],["Bull","Correction","Bear","Rebound"],"na")
    return pd.Series(st,index=dates)
nxt=np.log(cl.shift(-21)/cl)
for slow,fast in ((252,21),(126,10)):
    st=states(slow,fast); m=(dates.year>=2018)&(st!="na")
    print(f"\n== states from {slow}-day and {fast}-day NQ returns (2018-2026): share of days, next-21-day NQ return (bp)")
    for k in ("Bull","Correction","Bear","Rebound"):
        mm=m&(st==k); print(f"   {k:<11} {mm.mean()/m.mean():5.0%}  next month {nxt[mm].mean()*1e4:6.0f} bp")
    print("   funded strategies, $ per NQ per traded day:")
    for s_ in ("VB","ONB_ML_MC","OND_MC","EOS"):
        y=pd.Series(lab.daily(s_),index=dates); t=(y!=0)&m
        row=[]
        for k in ("Bull","Correction","Bear","Rebound"):
            x=y[t&(st==k)]; row.append(f"{k} ${x.mean():5.0f} (n{len(x)}, t {x.mean()/x.std()*np.sqrt(len(x)):.1f})")
        print(f"     {s_:<10} "+"  ".join(row))
pickle.dump(states(252,21),open(SP+"mtp_states.pkl","wb"))
