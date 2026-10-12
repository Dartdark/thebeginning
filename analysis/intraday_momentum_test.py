"""Baltussen, Da, Lammers & Martens (2021) "Hedging demand and market intraday momentum"
(SSRN 3760365) on NQ/ES 2018-2026: the rest-of-day return (previous 15:00 CT close to 14:30)
predicting the last 30 minutes, with size and prior-day GEX conditioning. Record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
import gex_flows as GX
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
for name,f,pv,tick in (("NQ","g24.pkl",20,5),("ES","ge.pkl",50,12.5)):
    cost={"NQ":7.25,"ES":5}[name]+2*tick
    g=pickle.load(open(SP+f,"rb")); tr=g.trading
    C=pd.DataFrame(g.c).ffill(axis=1).to_numpy()
    prev=np.r_[np.nan,C[tr[:-1],jof(1500)]]
    c1430=C[tr,jof(1430)]; c1500=C[tr,jof(1500)]; o=g.o[tr,jof(831)]; c900=C[tr,jof(900)]
    df=pd.DataFrame(dict(rod=c1430/prev-1, onfh=c900/prev-1, rm=c1430/c900-1, lh=(c1500-c1430)*pv,
        nxt=np.r_[(C[tr[1:],jof(1500)]-c1500[:-1])*pv,np.nan]),index=pd.DatetimeIndex(g.ts[tr]))
    F=GX.features_for(g); df["gneg"]=F.gex_neg.reindex(tr).to_numpy(); df["grank"]=F.gex_rank.reindex(tr).to_numpy()
    df=df[(df.index.year>=2018)].dropna(subset=["rod","lh"])
    sd=df.rod.rolling(60).std().shift(1); df["z"]=df.rod/sd
    print(f"\n==== {name}: trade sign(signal) over 14:30-15:00, $ per contract, cost ${cost:.0f} ====")
    for sig in ("rod","onfh","rm"):
        x=df[sig].to_numpy(); y=df.lh.to_numpy(); xc=x-x.mean(); b=(xc*y).sum()/(xc**2).sum(); e=y-y.mean()-b*xc
        se=np.sqrt(((xc**2)*(e**2)).sum())/(xc**2).sum(); print(f"  regress LH on {sig}: t={b/se:.2f} (robust)")
    def rep(lab,m,sig="rod"):
        x=(np.sign(df[sig])*df.lh)[m].dropna()-cost
        by=x.groupby(x.index.year).mean()
        print(f"  {lab:<44} n={len(x):4d} net ${x.mean():5.0f} gross ${x.mean()+cost:5.0f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f} win {(x>0).mean():.0%} yrs+ {(by>0).sum()}/{len(by)} {by.round().astype(int).to_dict()}")
    rep("all days (ROD sign)", df.index==df.index)
    rep("all days (ONFH sign, Gao et al.)", df.index==df.index,"onfh")
    for k in (0.5,1,1.5,2): rep(f"|ROD| > {k} sd", df.z.abs()>k)
    rep("prev-day GEX < 0", df.gneg==True); rep("prev-day GEX < 0 and |ROD|>1sd", (df.gneg==True)&(df.z.abs()>1))
    rep("prev-day GEX rank < 0.2", df.grank<0.2); rep("prev-day GEX rank > 0.5", df.grank>0.5)
    # reversal next day
    x=(-np.sign(df.rod)*df.nxt)[df.z.abs()>1].dropna()
    print(f"  next-day reversal after |ROD|>1sd (close-to-close, gross) n={len(x)} ${x.mean():.0f} t={x.mean()/x.std()*np.sqrt(len(x)):.1f}")
