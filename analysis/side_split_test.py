"""Long/short split of Overnight Bias (plain and ML), per DEVELOPMENT_PROCESS.md: per-side stats, per-side
sizing in the funded bench, and a separate walk-forward ML filter per side vs the shared one
(second block, commented). Record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g=pickle.load(open(SP+"g24.pkl","rb")); lab=pickle.load(open(SP+"lab.pkl","rb")); atr=g.daily_atr(15)
def st(x):
    by=x.groupby(x.index.year).mean()
    return f"n={len(x):4d} win {np.mean(x>0):.0%} avg ${x.mean():5.0f} PF {x[x>0].sum()/-x[x<0].sum():.2f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f} yrs+ {(by>0).sum()}/{len(by)} 2023+ ${x[x.index.year>=2023].mean():.0f}"
for name,f in (("Overnight Bias (plain)","Backtesting Strategy Performance Report ONB v2.xlsx"),("Overnight Bias ML","Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias v2.xlsx")):
    t=load_mc(g,f); t=t.set_index(pd.DatetimeIndex(t.date)); t=t[t.index.year>=2018]
    print(f"\n{name}"); print("  all    ",st(t.net))
    for s,nm in ((1,"longs "),(-1,"shorts")):
        x=t.net[t.side==s]; print(f"  {nm} ",st(x)); print("     by year:",x.groupby(x.index.year).mean().round().astype(int).to_dict())
    key="ONB" if "plain" in name else "ONB_ML_MC"
    for s,nm in ((1,"L"),(-1,"S")):
        tt=t[t.side==s].reset_index(drop=True); lab.add(f"{key}_{nm}",tt,stop_pts=0.3*atr)
print("\ncorrelation longs vs shorts (daily):"); print(lab.corr(["ONB_ML_MC_L","ONB_ML_MC_S","VB","OND_MC","EOS"]).round(2).to_string())
base={"VB":3,"OND_MC":("risk",500),"EOS":("risk",500)}
plans={"Funded set (ONB ML both sides $300)":{**base,"ONB_ML_MC":("risk",300)}}
for l,s_ in ((300,0),(0,300),(400,200),(200,400),(400,300),(500,200)):
    p=dict(base)
    if l: p["ONB_ML_MC_L"]=("risk",l)
    if s_: p["ONB_ML_MC_S"]=("risk",s_)
    plans[f"  ONB ML longs ${l} / shorts ${s_}"]=p
print(lab.table(plans)); print(lab.table(plans,horizon=500))
pickle.dump(lab,open(SP+"lab.pkl","wb"),protocol=4)

# ---------------- separate filter per side
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# from portfolio import load_mc
# SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
# g=pickle.load(open(SP+"g24.pkl","rb")); lab=pickle.load(open(SP+"lab.pkl","rb")); res,X0=pickle.load(open(SP+"ml1.pkl","rb"))
# dates=X0.index; yr=dates.year
# COLS=["ret1","ret5","ret20","rth1","atr_ratio","dist50","rv5_rv20","dow0","dow1","dow2","dow3","dow4","tdm","opex_wk"]
# X=X0[COLS]
# onb=load_mc(g,"Backtesting Strategy Performance Report ONB v2.xlsx")
# side=pd.Series(0,index=dates); side[pd.DatetimeIndex(g.ts[onb.day.values])]=onb.side.values
# y=pd.Series(lab.daily("ONB"),index=dates); R=y/pd.Series(lab.stop["ONB"]*20,index=dates); tdd=y!=0
# def wf(mask):
#     pred=pd.Series(np.nan,index=dates)
#     for Y in range(2019,2027):
#         trn=mask&(yr<Y); tst=mask&(yr==Y)
#         if trn.sum()<60 or tst.sum()==0: continue
#         mu,sd=X[trn].mean(),X[trn].std().replace(0,1)
#         A=((X[trn]-mu)/sd).to_numpy(); b=R[trn].to_numpy(); lo,hi=np.percentile(b,[2,98]); b=np.clip(b,lo,hi); b=b-b.mean()
#         w=np.linalg.solve(A.T@A+len(b)*np.eye(A.shape[1]),A.T@b); pred[tst]=((X[tst]-mu)/sd).to_numpy()@w
#     return pred
# joint=res[("ONB_frozenset_wf",100)]
# sep=pd.concat([wf(tdd&(side==1)).dropna(),wf(tdd&(side==-1)).dropna()]).reindex(dates)
# m=tdd&(yr>=2019)
# for nm,p in (("joint filter (current)",joint),("separate filter per side",sep)):
#     for s,sn in ((1,"longs"),(-1,"shorts"),(0,"both")):
#         mm=m&((side==s) if s else (side!=0)); pp=p[mm]; yy=y[mm]; k=pp>=0
#         byk=yy[k].groupby(yy[k].index.year).mean(); bys=yy[~k].groupby(yy[~k].index.year).mean()
#         print(f"  {nm:<26} {sn:<6} kept {k.mean():.0%}: kept ${yy[k].mean():5.0f} vs skipped ${yy[~k].mean():5.0f}; years kept>skipped {(byk>bys.reindex(byk.index)).sum()}/{len(byk)}")
# # bench (2019+ starts comparable): joint vs separate
# m18=yr<2019
# def mk(new,skip):
#     skip=np.asarray(skip,bool)|np.asarray(m18)
#     lab.W[new]=lab.W["ONB"].copy(); lab.C[new]=lab.C["ONB"].copy(); lab.W[new][skip]=0; lab.C[new][skip]=0; lab.stop[new]=lab.stop["ONB"]
# mk("ONB_JOINT",(joint<0)|joint.isna()); mk("ONB_SEP",(sep<0)|sep.isna())
# for k in ("VB","OND_MC","EOS"):
#     lab.W[k+"_19"]=lab.W[k].copy(); lab.C[k+"_19"]=lab.C[k].copy(); lab.W[k+"_19"][m18]=0; lab.C[k+"_19"][m18]=0
#     if k in lab.stop: lab.stop[k+"_19"]=lab.stop[k]
# base={"VB_19":3,"OND_MC_19":("risk",500),"EOS_19":("risk",500)}
# plans={"Joint ML filter (current)":{**base,"ONB_JOINT":("risk",300)},"Separate filter per side":{**base,"ONB_SEP":("risk",300)}}
# print(lab.table(plans)); print(lab.table(plans,horizon=500))
