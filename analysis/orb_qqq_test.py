"""Zarattini & Aziz (2023/2025) "Can Day Trading Really Be Profitable?" (SSRN 4416622): the QQQ
5-minute ORB rules (enter at the 2nd candle open in the 1st candle direction, stop at the other side of
the 1st candle, 10R target, flat at the close) on NQ and ES 2018-2026. Record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
def orbq(g,pv,cost,rr=10.0,or_min=5,flat=1500,tick=0.25,start_year=2016):
    tr=g.trading; a0=jof(831); a1=jof(830+or_min); jf=jof(flat); rows=[]
    for d in tr:
        o=g.o[d,a0]; c=g.c[d,a1]
        if np.isnan(o) or np.isnan(c) or c==o: continue
        side=1 if c>o else -1
        hi=np.nanmax(g.h[d,a0:a1+1]); lo=np.nanmin(g.l[d,a0:a1+1])
        e=g.o[d,a1+1]
        if np.isnan(e): continue
        sp=lo if side>0 else hi; R=(e-sp)*side
        if R<=0: continue
        tg=e+side*rr*R; px=None; kind=2; je=a1+1; jx=jf
        for j in range(a1+1,jf+1):
            if np.isnan(g.c[d,j]): continue
            if (side>0 and g.l[d,j]<=sp) or (side<0 and g.h[d,j]>=sp): px=sp; kind=0; jx=j; break
            if (side>0 and g.h[d,j]>=tg) or (side<0 and g.l[d,j]<=tg): px=tg; kind=1; jx=j; break
        if px is None: px=pd.Series(g.c[d,:jf+1]).ffill().iloc[-1]
        slips=1+(kind!=1)
        net=(px-e)*side*pv-cost-slips*tick*pv
        rows.append((pd.Timestamp(g.ts[d]),d,je,jx,side,e,px,kind,net,(px-e)*side/R,R*pv))
    return pd.DataFrame(rows,columns=["date","day","je","jx","side","entry","exit","kind","net","Rmult","risk_usd"]).set_index("date")
if __name__=="__main__":
    g=pickle.load(open(SP+"g24.pkl","rb")); ge=pickle.load(open(SP+"ge.pkl","rb"))
    for name,gg,pv,cost in (("NQ",g,20,7.25),("ES",ge,50,5.0)):
        print(f"\n== {name}: paper rules (enter 2nd candle open, stop other side of first candle, target 10R, flat 15:00), per contract after costs + slippage")
        for orm,rr in ((5,10),(5,5),(5,3),(15,10),(30,10)):
            t=orbq(gg,pv,cost,rr=rr,or_min=orm); t=t[t.index.year>=2018]; x=t.net; by=x.groupby(x.index.year).mean()
            gross=(t.Rmult).mean()
            print(f"  OR {orm:2d}m target {rr:2d}R: n={len(x)} win {np.mean(x>0):.0%} avg ${x.mean():5.0f} avg R(gross) {gross:+.3f} PF {x[x>0].sum()/-x[x<0].sum():.2f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f} yrs+ {(by>0).sum()}/9 2023+ ${x[x.index.year>=2023].mean():.0f}  avg risk ${t.risk_usd.mean():.0f}")
            if name=="NQ" and orm==5 and rr==10: print("     by year:",by.round().astype(int).to_dict())
