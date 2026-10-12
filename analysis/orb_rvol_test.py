"""Zarattini, Barbon & Aziz (2024) "A Profitable Day Trading Strategy For The U.S. Equity Market"
(SSRN 4729284): n-minute opening range breakout with a relative-volume ("in play") filter, on NQ and
ES 2018-2026, then the funded bench (second block, commented). Record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
def orb_trades(g, pv, tick, cost, stop_pct=0.10, or_min=5, rvol_min=0.0, flat=1500, atr_n=14, side_filter=0):
    tr=g.trading; atr=g.daily_atr(atr_n); a0=jof(831); a1=jof(830+or_min) if or_min<30 else jof(900)
    v=np.nan_to_num(g.v); rv=pd.Series(v[tr,a0:a1+1].sum(1),index=tr); rvavg=rv.rolling(14).mean().shift(1)
    rows=[]
    for d in tr:
        o=g.o[d,a0]; c=g.c[d,a1]
        if np.isnan(o) or np.isnan(c) or c==o or np.isnan(atr[d]) or np.isnan(rvavg[d]): continue
        rvol=rv[d]/rvavg[d]
        if rvol<rvol_min: continue
        side=1 if c>o else -1
        if side_filter and side!=side_filter: continue
        lvl=np.nanmax(g.h[d,a0:a1+1]) if side>0 else np.nanmin(g.l[d,a0:a1+1])
        st=stop_pct*atr[d]; jf=jof(flat); entry=None; px=None; kind=2
        for j in range(a1+1,jf+1):
            hi,lo,op,cl=g.h[d,j],g.l[d,j],g.o[d,j],g.c[d,j]
            if np.isnan(cl): continue
            if entry is None:
                if (side>0 and hi>=lvl) or (side<0 and lo<=lvl):
                    entry=max(lvl,op) if side>0 else min(lvl,op); sp=entry-side*st; je=j
                    if (side>0 and lo<=sp) or (side<0 and hi>=sp): px=sp; kind=0; break
                continue
            if (side>0 and lo<=sp) or (side<0 and hi>=sp): px=min(op,sp) if side>0 else max(op,sp); kind=0; break
            last=cl
        if entry is None: continue
        if px is None:
            px=pd.Series(g.c[d,:jf+1]).ffill().iloc[-1]
        net=(px-entry)*side*pv - cost - 2*tick*pv
        rows.append((pd.Timestamp(g.ts[d]),d,je,j if kind==0 else jf,side,entry,px,kind,net,rvol,(px-entry)*side/st))
    return pd.DataFrame(rows,columns=["date","day","je","jx","side","entry","exit","kind","net","rvol","R"]).set_index("date")
if __name__=="__main__":
    g=pickle.load(open(SP+"g24.pkl","rb")); ge=pickle.load(open(SP+"ge.pkl","rb"))
    for name,gg,pv,tick,cost in (("NQ",g,20,0.25,7.25),("ES",ge,50,0.25,5.0)):
        print(f"\n===== {name}: 5-min ORB (direction of first 5-min candle, stop order at its high/low, stop x ATR14, flat 15:00), net per contract")
        for orm in (5,15):
            for sp_ in (0.05,0.10,0.20):
                for rvm in (0,1.0,1.5,2.0):
                    t=orb_trades(gg,pv,tick,cost,stop_pct=sp_,or_min=orm,rvol_min=rvm); t=t[t.index.year>=2018]
                    x=t.net; by=x.groupby(x.index.year).mean()
                    if len(x)<30: continue
                    print(f"  OR {orm:2d}m stop {sp_:.2f}ATR rvol>={rvm:.1f}: n={len(x):4d} win {np.mean(x>0):.0%} avg ${x.mean():6.0f} PF {x[x>0].sum()/-x[x<0].sum():.2f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f} yrs+ {(by>0).sum()}/{len(by)} 2023+ ${x[x.index.year>=2023].mean():5.0f}")

# ---------------- funded bench
# import sys; sys.argv=["x"]
# exec(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/orb1.py").read().split('if __name__')[0])
# from grid24 import jof
# g=pickle.load(open(SP+"g24.pkl","rb")); lab=pickle.load(open(SP+"lab.pkl","rb")); atr=g.daily_atr(14)
# for rvm,key in ((1.0,"ORB15_RV1"),(0.0,"ORB15_ALL")):
#     t=orb_trades(g,20,0.25,7.25,stop_pct=0.20,or_min=15,rvol_min=rvm)
#     tt=pd.DataFrame(dict(day=t.day.values,j0=t.je.values,j1=t.jx.values,side=t.side.values,entry=t.entry.values,exit=t.exit.values,kind=t.kind.values,pnl=((t.exit-t.entry)*t.side*20).values,net=t.net.values,date=t.index,slips=0))
#     lab.add(key,tt,stop_pts=0.2*atr,slippage=False)
# onb=lab.C["ONB_ML_MC"]!=0; onbraw=lab.C["ONB"]!=0; o=lab.C["ORB15_RV1"]!=0
# print("ORB15_RV1 days",o.sum(),"| also an ONB (plain) day",(o&onbraw).sum(),"| also ONB ML day",(o&onb).sum())
# print(lab.corr(["VB","ONB","ONB_ML_MC","OND_MC","EOS","ORB15_RV1"]).round(2).to_string())
# base={"VB":3,"ONB_ML_MC":("risk",300),"OND_MC":("risk",500),"EOS":("risk",500)}
# plans={"Funded set":base}
# for k in ("ORB15_RV1","ORB15_ALL"):
#     for rk in (200,400):
#         p=dict(base); p[k]=("risk",rk); plans[f"  + {k} ${rk}"]=p
# print(lab.table(plans)); print(lab.table(plans,horizon=500))
# cs=dict(fmin=0.5,fmax=1.0,ref=2000)
# rec={"VB":3,"ONB_ML_MC":("risk",400),"OND_MC":("risk",500),"EOS":("risk",700)}
# for lbl,p in (("Recommended (cushion)",rec),("  + ORB15_RV1 $200",{**rec,"ORB15_RV1":("risk",200)}),("  + ORB15_RV1 $400",{**rec,"ORB15_RV1":("risk",400)})):
#     a=lab.score(p,250,**cs); b=lab.score(p,500,**cs)
#     print(f"{lbl:<26} 1y ${a['expected']:,.0f} blown {a['blown']:.0%} | 2y ${b['expected']:,.0f} blown {b['blown']:.0%}")
