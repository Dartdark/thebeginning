"""CFTC Commitments of Traders (Traders in Financial Futures) tests, 2018-2026: next 1/4-week NQ and ES
returns by leveraged-fund / asset-manager / dealer / small-trader positioning, funded strategies by
positioning quintile, and two filters in the funded bench (second block, commented). Record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
import cot_flows as C
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g=pickle.load(open(SP+"g24.pkl","rb")); ge=pickle.load(open(SP+"ge.pkl","rb")); lab=pickle.load(open(SP+"lab.pkl","rb"))
FEATS=["lev_rank","am_rank","dealer_rank","nonrep_rank","lev_chg","am_chg","oi_chg"]
for name,gg,code,pv in (("NQ",g,C.NQ,20),("ES",ge,C.ES,50)):
    tr=gg.trading; Cc=pd.DataFrame(gg.c).ffill(axis=1).to_numpy(); cl=pd.Series(Cc[tr,jof(1500)],index=pd.DatetimeIndex(gg.ts[tr]))
    cot=C.load_cot(code)
    rows=[]
    for d,r in cot.iterrows():
        start=d+pd.Timedelta(days=3)           # Friday release; position from that Friday's 15:00 close
        c0=cl[cl.index<=start]; 
        if len(c0)==0: continue
        i0=cl.index.get_loc(c0.index[-1])
        if i0+20>=len(cl): continue
        rows.append(dict(date=d,w1=np.log(cl.iloc[i0+5]/cl.iloc[i0]),w4=np.log(cl.iloc[i0+20]/cl.iloc[i0]),**{k:r[k] for k in FEATS}))
    W=pd.DataFrame(rows).set_index("date"); W=W[W.index.year>=2018]
    print(f"\n===== {name}: next 1 week / 4 weeks return (bp) by positioning (weekly reports {len(W)})")
    for k in FEATS:
        x=W.dropna(subset=[k])
        q=pd.qcut(x[k],5,labels=False,duplicates="drop")
        m1=x.w1.groupby(q).mean()*1e4; m4=x.w4.groupby(q).mean()*1e4
        c1=np.corrcoef(x[k],x.w1)[0,1]; c4=np.corrcoef(x[k],x.w4)[0,1]
        t1=c1*np.sqrt(len(x)); 
        print(f"  {k:<12} corr w1 {c1:+.3f} (t~{t1:+.1f})  w4 {c4:+.3f} | w1 by quintile {m1.round(0).astype(int).tolist()}  w4 {m4.round(0).astype(int).tolist()}")
# strategy P&L by NQ positioning quintile (feature usable on each trading day)
F=C.features_for(g,C.NQ); dates=pd.DatetimeIndex(g.ts[g.trading])
print("\n===== funded strategies ($/NQ per traded day) by NQ positioning quintile (ranks vs previous 3 years)")
for strat in ("VB","ONB_ML_MC","OND_MC","EOS"):
    y=pd.Series(lab.daily(strat),index=g.trading); t=(y!=0)&(dates.year>=2018)
    for k in ("lev_rank","am_rank","dealer_rank"):
        x=F.loc[t,k].dropna(); yy=y[x.index]
        q=pd.cut(x,[-0.01,0.2,0.4,0.6,0.8,1.01],labels=False)
        print(f"  {strat:<10} {k:<12} " + "  ".join(f"Q{i+1} ${yy[q==i].mean():5.0f} (n{(q==i).sum()})" for i in range(5)))

# ---------------- filters in the funded bench
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# import cot_flows as C
# SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
# g=pickle.load(open(SP+"g24.pkl","rb")); lab=pickle.load(open(SP+"lab.pkl","rb"))
# F=C.features_for(g,C.NQ); idx=np.arange(lab.D)
# def filt(src,new,skip):
#     skip=np.asarray(skip,bool); lab.W[new]=lab.W[src].copy(); lab.C[new]=lab.C[src].copy(); lab.W[new][skip]=0; lab.C[new][skip]=0
#     if src in lab.stop: lab.stop[new]=lab.stop[src]
#     y=pd.Series(lab.daily(src),index=pd.DatetimeIndex(g.ts[g.trading])); s=pd.Series(skip,index=y.index); t=y!=0
#     print(f"{new}: skipped {(t&s).sum()} trades, by year skipped avg", y[t&s].groupby(y[t&s].index.year).mean().round().astype(int).to_dict())
# filt("OND_MC","OND_noLevHigh",(F.lev_rank>0.8).to_numpy())
# filt("ONB_ML_MC","ONBML_noAMlow",(F.am_rank<0.2).to_numpy())
# base={"VB":3,"ONB_ML_MC":("risk",300),"OND_MC":("risk",500),"EOS":("risk",500)}
# p1=dict(base); p1.pop("OND_MC"); p1["OND_noLevHigh"]=("risk",500)
# p2=dict(base); p2.pop("ONB_ML_MC"); p2["ONBML_noAMlow"]=("risk",300)
# print(lab.table({"Funded set":base,"  OND skips lev-fund rank>0.8":p1,"  ONB ML skips asset-mgr rank<0.2":p2}))
# print(lab.table({"Funded set":base,"  OND skips lev-fund rank>0.8":p1,"  ONB ML skips asset-mgr rank<0.2":p2},horizon=500))
