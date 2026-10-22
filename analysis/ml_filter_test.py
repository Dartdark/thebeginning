"""Kelly & Xiu (2023) "Financial Machine Learning" (SSRN 4501707) applied to the funded set:
a walk-forward ridge model (expanding window, retrained each January from 2019; standardized
inputs known at the previous 15:00 CT close; 2-98% winsorized target; heavy shrinkage) predicts
each strategy's next-day P&L, and days with a negative prediction are skipped. Then the funded
bench, including a placebo that skips the same share of Overnight Bias days at random.
Blocks: ml1 (model + skip tables), ml3 (input sets, R-multiple target), ml4/ml5 (bench, placebo).
Expects pickled grids and the funded lab from a scratch run; kept as the record of the test."""

# ======================= ml1
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
import gex_flows as GX, vix_regime as VR, calendar_flows as CF
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g=pickle.load(open(SP+"g24.pkl","rb")); lab=pickle.load(open(SP+"lab.pkl","rb"))
tr=g.trading; dates=pd.DatetimeIndex(g.ts[tr])
C=pd.DataFrame(g.c).ffill(axis=1).to_numpy()
cl=pd.Series(C[tr,jof(1500)],index=dates); op=pd.Series(g.o[tr,jof(831)],index=dates)
atr=pd.Series(g.daily_atr(15)[tr],index=dates)
V=VR.load_features(g); F=GX.features_for(g); cal=CF.calendar(g)
r1=np.log(cl).diff()
X=pd.DataFrame(index=dates)
X["vix"]=V.vix.values; X["evrp"]=V.evrp.values
X["vix_chg5"]=(V.vix-V.vix.shift(5)).values
X["gex_rank"]=F.gex_rank.reindex(tr).values; X["gex_neg"]=F.gex_neg.reindex(tr).astype(float).values; X["dix_rank"]=F.dix_rank.reindex(tr).values
X["ret1"]=r1.shift(1); X["ret5"]=np.log(cl).diff(5).shift(1); X["ret20"]=np.log(cl).diff(20).shift(1)
X["rth1"]=np.log(cl/op).shift(1)                       # yesterday's 8:30-15:00 move
X["atr_ratio"]=(atr/atr.rolling(60).mean()).values     # atr row d uses days before d
X["dist50"]=(np.log(cl/cl.rolling(50).mean())).shift(1)
X["rv5_rv20"]=(r1.rolling(5).std()/r1.rolling(20).std()).shift(1)
for k in range(5): X[f"dow{k}"]=(dates.dayofweek==k).astype(float)
X["tdm_end"]=(cal.tdm_end.reindex(tr).values<=3).astype(float); X["tdm"]=(cal.tdm.reindex(tr).values<=3).astype(float)
X["opex_wk"]=cal.opex_week.reindex(tr).astype(float).values
X=X.fillna(X.median())
yr=dates.year
def ridge_wf(name, lam_grid=(10,100,1000), q=0.0):
    y=pd.Series(lab.daily(name),index=dates); traded=y!=0
    out={}
    for lam in lam_grid:
        pred=pd.Series(np.nan,index=dates)
        for Y in range(2019,2027):
            trn=traded&(yr<Y); tst=traded&(yr==Y)
            if trn.sum()<100 or tst.sum()==0: continue
            mu,sd=X[trn].mean(),X[trn].std().replace(0,1)
            A=((X[trn]-mu)/sd).to_numpy(); b=y[trn].to_numpy(); bm=b.mean()
            # winsorize target (fat tails)
            lo,hi=np.percentile(b,[2,98]); b=np.clip(b,lo,hi)-np.clip(b,lo,hi).mean()
            w=np.linalg.solve(A.T@A+lam*len(b)/100*np.eye(A.shape[1]),A.T@b)
            pred[tst]=((X[tst]-mu)/sd).to_numpy()@w
        out[lam]=pred
    return y,traded,out
res={}
for name in ("VB","ONB","OND_MC"):
    y,traded,out=ridge_wf(name)
    m=traded&(yr>=2019)
    print(f"\n{name}: traded days 2019+ n={m.sum()} avg ${y[m].mean():.0f}")
    for lam,p in out.items():
        pp=p[m]; yy=y[m]
        ic=np.corrcoef(pp,yy)[0,1]
        for cut in (0.2,0.33):
            thr=pp.groupby(pp.index.year).transform(lambda s: s.quantile(cut))  # in-year quantile only for reporting
            skip=pp<0
        q=pd.qcut(pp.rank(method="first"),3,labels=False)
        by=yy.groupby(q).mean().round().to_dict()
        sk=pp<0
        print(f"  lam {lam:5d}: IC {ic:+.3f}  terciles of prediction (low->high) {by}  skip pred<0: skip {sk.mean():.0%} skipped avg ${yy[sk].mean():.0f} kept avg ${yy[~sk].mean():.0f}")
        res[(name,lam)]=p
pickle.dump((res,X),open(SP+"ml1.pkl","wb"))

# ======================= ml3
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
# lab=pickle.load(open(SP+"lab.pkl","rb")); res,X0=pickle.load(open(SP+"ml1.pkl","rb"))
# dates=X0.index; yr=dates.year
# SETS={"all":list(X0.columns),
#       "no GEX/DIX":[c for c in X0.columns if c not in ("gex_rank","gex_neg","dix_rank")],
#       "price+calendar (no VIX)":[c for c in X0.columns if c not in ("gex_rank","gex_neg","dix_rank","vix","evrp","vix_chg5")]}
# def wf(name,cols,lam=100,rank_y=False):
#     X=X0[cols]; y=pd.Series(lab.daily(name),index=dates); tdd=y!=0
#     if rank_y:   # per-risk outcome: divide by stop (R multiple) to remove the volatility scale
#         y=y/pd.Series(lab.stop[name]*20,index=dates)
#     pred=pd.Series(np.nan,index=dates); W=[]
#     for Y in range(2019,2027):
#         trn=tdd&(yr<Y); tst=tdd&(yr==Y)
#         mu,sd=X[trn].mean(),X[trn].std().replace(0,1)
#         A=((X[trn]-mu)/sd).to_numpy(); b=y[trn].to_numpy(); lo,hi=np.percentile(b,[2,98]); b=np.clip(b,lo,hi); b=b-b.mean()
#         w=np.linalg.solve(A.T@A+lam*len(b)/100*np.eye(A.shape[1]),A.T@b); W.append(w)
#         pred[tst]=((X[tst]-mu)/sd).to_numpy()@w
#     return pred,pd.Series(np.mean(W,0),index=cols)
# yd=pd.Series(lab.daily("ONB"),index=dates); m=(yd!=0)&(yr>=2019)
# for lab_,cols in SETS.items():
#     for ry in (False,True):
#         p,w=wf("ONB",cols,rank_y=ry); sk=p[m]<0; yy=yd[m]
#         byk=yy[~sk].groupby(yy[~sk].index.year).mean(); bys=yy[sk].groupby(yy[sk].index.year).mean()
#         print(f"ONB {lab_:<26} target={'R-multiple' if ry else '$/NQ':<10} skip {sk.mean():.0%}  kept ${yy[~sk].mean():.0f} skipped ${yy[sk].mean():.0f}  years kept>skipped {(byk>bys).sum()}/{len(byk)}")
#         if lab_=="all" and not ry: print("   avg weights:", w.sort_values().round(0).to_dict())
#         res[("ONB_"+lab_+("_R" if ry else ""),100)]=p
# pickle.dump((res,X0),open(SP+"ml1.pkl","wb"))

# ======================= ml4
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
# lab=pickle.load(open(SP+"lab.pkl","rb")); res,X0=pickle.load(open(SP+"ml1.pkl","rb"))
# dates=X0.index; yr=dates.year; m18=yr<2019
# def mk(src,new,skip):
#     lab.W[new]=lab.W[src].copy(); lab.C[new]=lab.C[src].copy(); lab.W[new][skip|m18]=0; lab.C[new][skip|m18]=0; (lab.stop.__setitem__(new,lab.stop[src]) if src in lab.stop else None)
# for k in ("VB","ONB","OND_MC","EOS"): mk(k,k+"_19",np.zeros(len(dates),bool))
# for key in ("ONB_all","ONB_price+calendar (no VIX)","ONB_price+calendar (no VIX)_R"):
#     p=res[(key,100)].to_numpy(); mk("ONB",key,(p<0)|np.isnan(p))
# traded=(lab.C["ONB"]!=0)&~m18
# rng=np.random.default_rng(0)
# for s in range(5):
#     sk=traded&(rng.random(len(dates))<0.55); mk("ONB","RAND%d"%s,sk)
# base={"VB_19":3,"ONB_19":("risk",300),"OND_MC_19":("risk",500),"EOS_19":("risk",500)}
# plans={"Current set (2019+)":base}
# for key in ("ONB_all","ONB_price+calendar (no VIX)","ONB_price+calendar (no VIX)_R")+tuple("RAND%d"%s for s in range(5)):
#     for rk in (300,500):
#         p=dict(base); p.pop("ONB_19"); p[key]=("risk",rk); plans[f"  ONB -> {key} ${rk}"]=p
# for h in (250,500):
#     t=lab.table(plans,horizon=h); print(t)

# ======================= ml5
# exec(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/ml4.py").read().split("base={")[0])
# base={"VB_19":3,"ONB_19":("risk",300),"OND_MC_19":("risk",500),"EOS_19":("risk",500)}
# rows=[]
# for rk in (100,150,200):
#     p=dict(base); p["ONB_19"]=("risk",rk); rows.append(("ONB unfiltered $%d"%rk,lab.score(p,250)["expected"],lab.score(p,500)["expected"]))
# for key in ("ONB_all","ONB_price+calendar (no VIX)_R"):
#     p=dict(base); p.pop("ONB_19"); p[key]=("risk",300); rows.append((key+" $300",lab.score(p,250)["expected"],lab.score(p,500)["expected"]))
# r1=[];r2=[]
# rng=np.random.default_rng(1)
# for s in range(30):
#     sk=traded&(rng.random(len(dates))<0.55); mk("ONB","R",sk)
#     p=dict(base); p.pop("ONB_19"); p["R"]=("risk",300); r1.append(lab.score(p,250)["expected"]); r2.append(lab.score(p,500)["expected"])
# for r in rows: print(f"{r[0]:<40} 1y ${r[1]:,.0f}  2y ${r[2]:,.0f}   pct vs random: 1y {np.mean(np.array(r1)<r[1]):.0%} 2y {np.mean(np.array(r2)<r[2]):.0%}")
# print(f"random 55% skip $300 (30 draws): 1y mean ${np.mean(r1):,.0f} sd {np.std(r1):,.0f}; 2y mean ${np.mean(r2):,.0f} sd {np.std(r2):,.0f}")

# ======================= ml6 (frozen input set + final fit) and mlchk (replay of the PowerLanguage score)
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
# lab=pickle.load(open(SP+"lab.pkl","rb")); res,X0=pickle.load(open(SP+"ml1.pkl","rb"))
# dates=X0.index; yr=dates.year
# COLS=["ret1","ret5","ret20","rth1","atr_ratio","dist50","rv5_rv20","dow0","dow1","dow2","dow3","dow4","tdm","opex_wk"]
# y=pd.Series(lab.daily("ONB"),index=dates); tdd=y!=0
# R=y/pd.Series(lab.stop["ONB"]*20,index=dates)
# def fit(trn,X):
#     mu,sd=X[trn].mean(),X[trn].std().replace(0,1)
#     A=((X[trn]-mu)/sd).to_numpy(); b=R[trn].to_numpy(); lo,hi=np.percentile(b,[2,98]); b=np.clip(b,lo,hi); b=b-b.mean()
#     w=np.linalg.solve(A.T@A+len(b)*np.eye(A.shape[1]),A.T@b)
#     return mu,sd,w
# X=X0[COLS]
# pred=pd.Series(np.nan,index=dates)
# for Y in range(2019,2027):
#     trn=tdd&(yr<Y); tst=tdd&(yr==Y); mu,sd,w=fit(trn,X); pred[tst]=((X[tst]-mu)/sd).to_numpy()@w
# m=tdd&(yr>=2019); sk=pred[m]<0; yy=y[m]
# byk=yy[~sk].groupby(yy[~sk].index.year).mean(); bys=yy[sk].groupby(yy[sk].index.year).mean()
# print(f"walk-forward, frozen input set: skip {sk.mean():.0%} kept ${yy[~sk].mean():.0f} skipped ${yy[sk].mean():.0f} years kept>skipped {(byk>bys).sum()}/8")
# print(" kept",byk.round().to_dict()); print(" skipped",bys.round().to_dict())
# res[("ONB_frozenset_wf",100)]=pred
# # final frozen fit on all ONB trades 2018-2026
# mu,sd,w=fit(tdd,X)
# a=w/sd.to_numpy(); c0=-(w*mu.to_numpy()/sd.to_numpy()).sum()
# coef=pd.DataFrame(dict(mean=mu,sd=sd,w_std=w,coef_raw=a))
# print(coef.to_string()); print("const",c0)
# full=c0+X.to_numpy()@a
# fs=pd.Series(full,index=dates)
# print(f"in-sample (all years): skip {(fs[tdd]<0).mean():.0%} kept ${y[tdd&(fs>=0)].mean():.0f} skipped ${y[tdd&(fs<0)].mean():.0f}")
# pickle.dump((res,X0),open(SP+"ml1.pkl","wb")); pickle.dump(dict(mu=mu,sd=sd,w=w,a=a,c0=c0,cols=COLS,score=fs),open(SP+"frozen.pkl","wb"))
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# from grid24 import jof
# SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
# g=pickle.load(open(SP+"g24.pkl","rb")); fz=pickle.load(open(SP+"frozen.pkl","rb"))
# tr=g.trading; C=pd.DataFrame(g.c).ffill(axis=1).to_numpy(); atr=g.daily_atr(15)
# CH=[];OH=[];AH=[]; last_month=0; mc=0; out={}
# ts=pd.DatetimeIndex(g.ts)
# for d in tr:   # MC loop: at the start of trading date d, history holds earlier trading days
#     dt=ts[d]
#     if len(CH)>=59:
#         x={}
#         x["ret1"]=np.log(CH[0]/CH[1]); x["ret5"]=np.log(CH[0]/CH[5]); x["ret20"]=np.log(CH[0]/CH[20]); x["rth1"]=np.log(CH[0]/OH[0])
#         x["atr_ratio"]=atr[d]/((atr[d]+sum(AH[:59]))/60); x["dist50"]=np.log(CH[0]/np.mean(CH[:50]))
#         r=[np.log(CH[k]/CH[k+1]) for k in range(20)]; x["rv5_rv20"]=np.std(r[:5],ddof=1)/np.std(r,ddof=1)
#         dow=dt.dayofweek+1
#         for k in range(5): x[f"dow{k}"]=1.0 if dow==k+1 else 0.0
#         tdm=1 if dt.month!=last_month else mc+1; x["tdm"]=1.0 if tdm<=3 else 0.0
#         fri=dt.day+(5-dow); x["opex_wk"]=1.0 if 15<=fri<=21 else 0.0
#         out[dt]=fz["c0"]+sum(a*x[c] for c,a in zip(fz["cols"],fz["a"]))
#     CH.insert(0,C[d,jof(1500)]); OH.insert(0,g.o[d,jof(831)]); AH.insert(0,atr[d])
#     mc=1 if dt.month!=last_month else mc+1; last_month=dt.month
# mcs=pd.Series(out); py=fz["score"].reindex(mcs.index)
# d=(mcs-py).abs()
# print("days compared",len(d),"max abs diff",d.max(),"sign disagreements",(np.sign(mcs)!=np.sign(py)).sum())
# print(d.sort_values().tail(5))

# ======================= chal_ml (50K challenge: plain ONB vs ONB ML)
# exec(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/chal4.py").read().split("plans = {")[0].replace('"EOS": load_mc(g, "mc_reports/Backtesting Strategy Performance Report EOS v1.xlsx")}',
#  '"EOS": load_mc(g, "mc_reports/Backtesting Strategy Performance Report EOS v1.xlsx"), "ONBML": load_mc(g, "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias v2.xlsx")}'))
# res,X0=pickle.load(open(SP_:="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/ml1.pkl","rb"))
# wf=res[("ONB_frozenset_wf",100)]
# t=T["ONB"]; dt=pd.DatetimeIndex(g.ts[t.day.to_numpy()]); keep=wf.reindex(dt).to_numpy()>=0
# w_, r_ = paths(g, t[keep]); P[("ONBWF",False)]=(w_[tr]/10, r_[tr]/10)
# plans={"Current: VB 8 + ONB $1,100": {"VB":8,"ONB":("risk",1100)}}
# for rk in (1100,1500,2000):
#     plans[f"VB 8 + ONB ML (MC list) ${rk:,}"]={"VB":8,"ONBML":("risk",rk)}
# for rk in (1100,1500,2000):
#     plans[f"VB 8 + ONB ML walk-forward ${rk:,} (2019+)"]={"VB":8,"ONBWF":("risk",rk)}
# m19=yr>=2019
# for name,p in plans.items():
#     o,dd=run(p,False)
#     print(f"{name:<44} pass {np.nanmean(o):.1%}  2019+ {np.nanmean(o[m19]):.1%}  2018-22 {np.nanmean(o[yr<2023]):.1%}  2023-26 {np.nanmean(o[yr>=2023]):.1%}  worst yr {pd.Series(o).groupby(yr).mean().min():.0%}  median days {np.nanmedian(dd):.0f}",flush=True)

# ======================= logit1 (yes/no logistic target instead of ridge, after Vilkov 2026 '0DTE Trading Rules')
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
# lab=pickle.load(open(SP+"lab.pkl","rb")); res,X0=pickle.load(open(SP+"ml1.pkl","rb"))
# dates=X0.index; yr=dates.year
# COLS=["ret1","ret5","ret20","rth1","atr_ratio","dist50","rv5_rv20","dow0","dow1","dow2","dow3","dow4","tdm","opex_wk"]
# X=X0[COLS]; y=pd.Series(lab.daily("ONB"),index=dates); tdd=y!=0
# def logit(A,b,lam):
#     w=np.zeros(A.shape[1]); c=np.log(b.mean()/(1-b.mean()))
#     for _ in range(50):   # Newton / IRLS with L2 on w
#         p=1/(1+np.exp(-(c+A@w))); Wt=p*(1-p)
#         g=np.r_[np.sum(p-b), A.T@(p-b)+lam*w]
#         Aa=np.c_[np.ones(len(b)),A]; H=Aa.T@(Aa*Wt[:,None]); H[1:,1:]+=lam*np.eye(A.shape[1])
#         step=np.linalg.solve(H,g); c-=step[0]; w-=step[1:]
#         if np.abs(step).max()<1e-8: break
#     return c,w
# out={}
# for lam in (10,100,1000):
#     pr=pd.Series(np.nan,index=dates)
#     for Y in range(2019,2027):
#         trn=tdd&(yr<Y); tst=tdd&(yr==Y)
#         mu,sd=X[trn].mean(),X[trn].std().replace(0,1)
#         c,w=logit(((X[trn]-mu)/sd).to_numpy(),(y[trn]>0).astype(float).to_numpy(),lam)
#         pr[tst]=1/(1+np.exp(-(c+((X[tst]-mu)/sd).to_numpy()@w)))
#     out[lam]=pr
#     m=tdd&(yr>=2019); pp=pr[m]; yy=y[m]
#     for thr_name,thr in (("p<0.5",0.5),("p<median of training-period p",None)):
#         if thr is None:
#             sk=pd.Series(False,index=pp.index)
#             for Y in range(2019,2027):
#                 s=pp[pp.index.year==Y]; sk[s.index]=s<pp[pp.index.year<Y].median() if (pp.index.year<Y).any() else s<0.5
#         else: sk=pp<thr
#         byk=yy[~sk].groupby(yy[~sk].index.year).mean(); bys=yy[sk].groupby(yy[sk].index.year).mean()
#         print(f"logit lam {lam:4d} skip {thr_name:<30}: skip {sk.mean():.0%} kept ${yy[~sk].mean():.0f} (win {np.mean(yy[~sk]>0):.0%}) skipped ${yy[sk].mean():.0f} years kept>skipped {(byk>bys.reindex(byk.index)).sum()}/8")
# r=res[("ONB_frozenset_wf",100)]; m=tdd&(yr>=2019); sk=r[m]<0; yy=y[m]
# print(f"ridge (current)                                 : skip {sk.mean():.0%} kept ${yy[~sk].mean():.0f} (win {np.mean(yy[~sk]>0):.0%}) skipped ${yy[sk].mean():.0f}")
# pickle.dump(out,open(SP+"logit_wf.pkl","wb"))
