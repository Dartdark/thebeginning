"""Vault Break robustness checks prompted by an r/algotrading post ("I backtested 100+ retail trading
strategies"): (1) target exits need the price to trade 1 tick through the target, not just touch it;
(2) random-entry placebo with the same 40/75 bracket and 14:30 exit, on all days, on VB days, and at a
random time after VB's first signal (the fair version). Record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g=pickle.load(open(SP+"g24.pkl","rb"))
vb=load_mc(g,"Backtesting Strategy Performance Report VB v1.xlsx"); vb=vb[pd.DatetimeIndex(vb.date).year>=2018]
TGT,STP,PV,COST,TICK=40.0,75.0,20,7.25,0.25
def bracket(d,j0,entry,jend,through=0.0):
    """long from minute j0 (entry price given), target entry+TGT (needs high >= target+through), stop entry-STP, flat at jend close.
    Returns (net, kind)."""
    tg=entry+TGT; sp=entry-STP
    for j in range(j0,jend+1):
        h,l,o=g.h[d,j],g.l[d,j],g.o[d,j]
        if np.isnan(h): continue
        if l<=sp: px=min(o,sp) if j>j0 else sp; return (px-entry)*PV-COST-2*TICK*PV,0
        if h>=tg+through: return TGT*PV-COST-1*TICK*PV,1
    px=pd.Series(g.c[d,:jend+1]).ffill().iloc[-1]; return (px-entry)*PV-COST-2*TICK*PV,2
rows=[]
for _,t in vb.iterrows():
    d=int(t.day); j0=int(t.j0); jend=max(int(t.j1),jof(1430)) if t.kind!=2 else int(t.j1)
    a=bracket(d,j0,t.entry,jend,0.0); b=bracket(d,j0,t.entry,jend,TICK)
    rows.append((t.date,a[0],a[1],b[0],b[1],t.net))
R=pd.DataFrame(rows,columns=["date","touch","k_touch","thru","k_thru","mc"]).set_index("date")
def s(x): return f"avg ${x.mean():5.0f} win {np.mean(x>0):.0%} PF {x[x>0].sum()/-x[x<0].sum():.2f} t={x.mean()/x.std()*np.sqrt(len(x)):.1f}"
print(f"Vault Break MC trades 2018+: n={len(R)}")
print("  MC report (no slippage)      ", s(R.mc))
print("  re-sim, target fills on touch", s(R.touch))
print("  re-sim, target needs 1 tick through", s(R.thru), f"| target exits {np.mean(R.k_touch==1):.0%} -> {np.mean(R.k_thru==1):.0%}")
# random-entry placebo: same days, same bracket, random entry minute 10:00-14:00 (VB decision window), 30 seeds
rng=np.random.default_rng(7); days=vb.day.astype(int).to_numpy(); res=[]
lo,hi=jof(1000),jof(1400)
for sd in range(30):
    out=[]
    for d in days:
        j0=rng.integers(lo,hi+1); e=g.o[d,j0]
        if np.isnan(e): continue
        out.append(bracket(d,j0,e,jof(1430),0.0)[0])
    out=np.array(out); res.append((out.mean(),np.mean(out>0)))
res=np.array(res)
print(f"  RANDOM long entries, same days & bracket (30 runs): avg ${res[:,0].mean():.0f} (range {res[:,0].min():.0f} to {res[:,0].max():.0f}), win {res[:,1].mean():.0%}")
# random entries on ALL trading days (not just VB days)
alld=g.trading[pd.DatetimeIndex(g.ts[g.trading]).year>=2018]; res2=[]
for sd in range(10):
    out=[]
    for d in alld:
        j0=rng.integers(lo,hi+1); e=g.o[d,j0]
        if np.isnan(e): continue
        out.append(bracket(d,j0,e,jof(1430),0.0)[0])
    out=np.array(out); res2.append((out.mean(),np.mean(out>0)))
res2=np.array(res2); print(f"  RANDOM long entries, all days (10 runs): avg ${res2[:,0].mean():.0f}, win {res2[:,1].mean():.0%}")

# ---------------- fair placebo (random entry after VB's first signal)
# exec(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/vbcheck.py").read().split("rows=[]")[0])
# rng=np.random.default_rng(11)
# first=vb.groupby("day").j0.min()       # VB's first signal time each day
# res=[]
# for sd in range(30):
#     out=[]
#     for d,j in first.items():
#         d=int(d); j=int(j)
#         if j>=jof(1400): continue
#         j0=rng.integers(j,jof(1400)+1); e=g.o[d,j0]
#         if np.isnan(e): continue
#         out.append(bracket(d,j0,e,jof(1430),0.0)[0])
#     out=np.array(out); res.append((out.mean(),np.mean(out>0),len(out)))
# res=np.array(res)
# print(f"RANDOM entry AFTER VB's first signal (same days, same bracket, 30 runs): avg ${res[:,0].mean():.0f} (range {res[:,0].min():.0f} to {res[:,0].max():.0f}), win {res[:,1].mean():.0%}, n {res[0,2]:.0f} days")
# # VB's own first trade per day, for a like-for-like comparison
# f=vb.sort_values("j0").groupby("day").head(1)
# x=[bracket(int(t.day),int(t.j0),t.entry,jof(1430),0.0)[0] for _,t in f.iterrows()]
# x=np.array(x); print(f"VB's first trade each day (same engine): avg ${x.mean():.0f} win {np.mean(x>0):.0%} n {len(x)}")
