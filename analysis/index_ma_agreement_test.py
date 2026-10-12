"""Index-agreement MA rule for ES (user idea, 2026-10-12): long ES when all indices are above
yesterday's N-day moving average of 15:00 closes, short when 2+ are below. Preliminary version with
ES and NQ only (Dow / YM data not yet in data/): long when both above, short when both below, mixed =
flat ("flat"), keep position ("hold"), or decide once at 8:45 ("open"); 15-minute checks 8:45-14:45,
flat at 15:00; per ES after $5 + 1 tick per fill. Record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g=pickle.load(open(SP+"g24.pkl","rb")); ge=pickle.load(open(SP+"ge.pkl","rb"))
def daily_close(gg):
    C=pd.DataFrame(gg.c).ffill(axis=1).to_numpy(); tr=gg.trading
    return pd.Series(C[tr,jof(1500)],index=pd.DatetimeIndex(gg.ts[tr])), C
nq_cl,nqC=daily_close(g); es_cl,esC=daily_close(ge)
rowE=pd.Series(ge.trading,index=pd.DatetimeIndex(ge.ts[ge.trading])); rowN=pd.Series(g.trading,index=pd.DatetimeIndex(g.ts[g.trading]))
days=rowE.index.intersection(rowN.index); days=days[days.year>=2018]
checks=[jof(t) for t in (845,900,915,930,945,1000,1015,1030,1045,1100,1115,1130,1145,1200,1215,1230,1245,1300,1315,1330,1345,1400,1415,1430,1445)]
PV,COST,TICK=50,5.0,0.25
def run(n, mode):
    a=nq_cl.dropna(); b=es_cl.dropna(); maN=a.rolling(n).mean().shift(1).reindex(nq_cl.index).ffill(); maE=b.rolling(n).mean().shift(1).reindex(es_cl.index).ffill()   # yesterday's MA
    out=[]
    for d in days:
        if np.isnan(maN[d]) or np.isnan(maE[d]): continue
        re,rn=rowE[d],rowN[d]; pos=0; entry=0; pnl=0.0; ntr=0
        for k,j in enumerate(checks):
            pe,pn=esC[re,j],nqC[rn,j]
            if np.isnan(pe) or np.isnan(pn): continue
            above=int(pe>maE[d])+int(pn>maN[d])
            sig=1 if above==2 else (-1 if above==0 else (0 if mode=="flat" else pos))
            if mode=="open" and k>0: sig=pos            # decide once at 8:45, hold
            if sig!=pos:
                px=ge.o[re,j+1]
                if np.isnan(px): continue
                if pos!=0: pnl+=(px-entry)*pos*PV-COST-2*TICK*PV; ntr+=1
                pos=sig; entry=px
        if pos!=0:
            px=esC[re,jof(1500)]; pnl+=(px-entry)*pos*PV-COST-2*TICK*PV; ntr+=1
        out.append((d,pnl,ntr))
    r=pd.DataFrame(out,columns=["d","pnl","ntr"]).set_index("d"); return r
print("ES, signal from ES and NQ vs yesterday's N-day MA of 15:00 closes; 15-min checks 8:45-14:45; flat at 15:00; per ES after $5 + 1 tick per fill")
for n in (5,10,20,50,100,200):
    for mode in ("open","hold","flat"):
        r=run(n,mode); x=r.pnl[r.ntr>0]; by=x.groupby(x.index.year).sum()
        bh=None
        print(f"  MA{n:<3} {mode:<4}: days traded {len(x):4d} trades/day {r.ntr[r.ntr>0].mean():.1f} avg/day ${x.mean():5.0f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f} yrs+ {(by>0).sum()}/9 2023+ ${x[x.index.year>=2023].mean():5.0f}")
print("\nLong side only (no shorts) and short side only, 'flat' mode")
for n in (5,20,50,200):
    for side in (1,-1):
        old=run.__code__
        r=run(n,"flat")
        # rerun quickly with side restriction
        def run_side(n,side):
            a=nq_cl.dropna(); b=es_cl.dropna(); maN=a.rolling(n).mean().shift(1).reindex(nq_cl.index).ffill(); maE=b.rolling(n).mean().shift(1).reindex(es_cl.index).ffill()
            out=[]
            for d in days:
                if np.isnan(maN[d]) or np.isnan(maE[d]): continue
                re_,rn=rowE[d],rowN[d]; pos=0; entry=0; pnl=0.0; ntr=0
                for j in checks:
                    pe,pn=esC[re_,j],nqC[rn,j]
                    if np.isnan(pe) or np.isnan(pn): continue
                    above=int(pe>maE[d])+int(pn>maN[d])
                    sig=1 if above==2 else (-1 if above==0 else 0)
                    if sig!=side: sig=0
                    if sig!=pos:
                        px=ge.o[re_,j+1]
                        if np.isnan(px): continue
                        if pos!=0: pnl+=(px-entry)*pos*PV-COST-2*TICK*PV; ntr+=1
                        pos=sig; entry=px
                if pos!=0: px=esC[re_,jof(1500)]; pnl+=(px-entry)*pos*PV-COST-2*TICK*PV; ntr+=1
                out.append((d,pnl,ntr))
            return pd.DataFrame(out,columns=["d","pnl","ntr"]).set_index("d")
        r=run_side(n,side); x=r.pnl[r.ntr>0]; by=x.groupby(x.index.year).sum()
        print(f"  MA{n:<3} {'long ' if side>0 else 'short'}: days {len(x):4d} avg/day ${x.mean():5.0f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f} yrs+ {(by>0).sum()}/9")

