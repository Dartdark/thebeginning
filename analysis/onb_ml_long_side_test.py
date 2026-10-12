"""Improving the long side of Overnight Bias ML (2026-10-12, DEVELOPMENT_PROCESS.md): exit variants on
the long trades, entry-condition terciles (design 2018-22 vs holdout 2023-26), three long-only filters
in the funded bench, the walk-forward check of the chosen rule (longs need ML score >= 0.03), and the
standard metrics before / after. Blocks onbl1..onbl4; expects scratch pickles. Record of the test."""

# ======================= onbl1
# import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
# import numpy as np, pandas as pd
# from grid24 import jof
# from portfolio import load_mc
# SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
# g=pickle.load(open(SP+"g24.pkl","rb")); atr=g.daily_atr(15)
# PV,COST,TICK=20,7.25,0.25
# def sim(d,j0,e,stp,tgt,jend,be=None):
#     sp=e-stp; tg=e+tgt if tgt else None; moved=False
#     for j in range(j0,jend+1):
#         h,l,o=g.h[d,j],g.l[d,j],g.o[d,j]
#         if np.isnan(h): continue
#         if l<=sp: px=(min(o,sp) if j>j0 else sp); return (px-e)*PV-COST-2*TICK*PV
#         if tg is not None and h>=tg: return tgt*PV-COST-TICK*PV
#         if be is not None and not moved and h>=e+be*stp: sp=max(sp,e+0.25); moved=True
#     px=pd.Series(g.c[d,:jend+1]).ffill().iloc[-1]; return (px-e)*PV-COST-2*TICK*PV
# ml=load_mc(g,"Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias v2.xlsx")
# pl=load_mc(g,"Backtesting Strategy Performance Report ONB v2.xlsx")
# def prep(t):
#     t=t[(t.side==1)].copy(); t["dt"]=pd.DatetimeIndex(t.date); t=t[t.dt.dt.year>=2018]; return t.reset_index(drop=True)
# ML,PL=prep(ml),prep(pl)
# def evalv(T,stpm=0.3,tgtR=3.0,end=1430,be=None):
#     out=[]
#     for _,t in T.iterrows():
#         d=int(t.day); a=atr[d]; s=stpm*a
#         out.append(sim(d,int(t.j0),t.entry,s,tgtR*s if tgtR else None,jof(end) if end!=1430 else max(jof(1430),int(t.j1)) if t.kind==2 else jof(1430),be))
#     return pd.Series(out,index=T.dt.values)
# def line(x):
#     d=x[x.index.year<2023]; h=x[x.index.year>=2023]
#     pf=lambda y: y[y>0].sum()/-y[y<0].sum()
#     eq=x.cumsum(); dd=-(eq-eq.cummax()).min()
#     return f"avg ${x.mean():5.0f} PF {pf(x):.2f} win {np.mean(x>0):.0%} | 2018-22 ${d.mean():5.0f} PF {pf(d):.2f} | 2023-26 ${h.mean():5.0f} PF {pf(h):.2f} | maxDD/NQ ${dd:,.0f}"
# for nm,T in (("ONB ML longs",ML),("ONB plain longs",PL)):
#     print(f"\n===== {nm}: n={len(T)}")
#     print(f"  baseline re-sim (0.3 ATR stop, 3R, 14:30)       {line(evalv(T))}")
#     for stpm in (0.2,0.4,0.5):
#         print(f"  stop {stpm} ATR, 3R                                {line(evalv(T,stpm=stpm))}")
#     for R in (1.5,2.0,4.0,None):
#         print(f"  stop 0.3, target {str(R)+'R' if R else 'none':<5}                         {line(evalv(T,tgtR=R))}")
#     for end in (1100,1200,1300):
#         print(f"  time exit {end}                                  {line(evalv(T,end=end))}")
#     for be in (1.0,1.5):
#         print(f"  breakeven after {be}R                             {line(evalv(T,be=be))}")

# ======================= onbl2
# exec(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/onbl1.py").read().split("def evalv")[0])
# import gex_flows as GX, vix_regime as VR
# res,X0=pickle.load(open(SP+"ml1.pkl","rb")); fz=pickle.load(open(SP+"frozen.pkl","rb"))
# C=pd.DataFrame(g.c).ffill(axis=1).to_numpy(); tr=g.trading; dates=pd.DatetimeIndex(g.ts[tr])
# row_of=pd.Series(tr,index=dates)
# prevc=pd.Series(np.r_[np.nan,C[tr[:-1],jof(1500)]],index=dates)
# V=VR.load_features(g); F=GX.features_for(g)
# def feats(T):
#     f=pd.DataFrame(index=T.index)
#     d=T.day.astype(int).values; dt=pd.DatetimeIndex(T.date)
#     o=g.o[d,jof(831)]; a=atr[d]
#     orh=np.array([np.nanmax(g.h[x,jof(831):jof(845)+1]) for x in d]); orl=np.array([np.nanmin(g.l[x,jof(831):jof(845)+1]) for x in d])
#     onh=np.array([np.nanmax(np.r_[g.h[x-1,jof(2301):],g.h[x,:jof(830)+1]]) for x in d]); onl=np.array([np.nanmin(np.r_[g.l[x-1,jof(2301):],g.l[x,:jof(830)+1]]) for x in d])
#     f["or_width"]=(orh-orl)/a; f["gap"]=(o-prevc.reindex(dt).values)/a
#     f["pos_in_on"]=(o-onl)/(onh-onl); f["on_range"]=(onh-onl)/a
#     f["entry_hour"]=T.j0.values/60.0
#     f["ext_above_on_high"]=(o-onh)/a
#     for k in ("ret1","rth1","dist50","atr_ratio","ret5","ret20"): f[k]=X0[k].reindex(dt).values
#     f["vix"]=V.vix.reindex(dt).values if hasattr(V.vix,"reindex") else np.nan
#     f["gex_rank"]=F.gex_rank.reindex(d).values
#     f["ml_score"]=fz["score"].reindex(dt).values
#     return f
# for nm,T in (("ONB ML longs",ML),("ONB plain longs",PL)):
#     f=feats(T); y=pd.Series(T.net.values,index=T.index); yr=pd.DatetimeIndex(T.date).year.values
#     print(f"\n===== {nm} (n={len(T)}): avg $ per trade by tercile of each feature; design 2018-22 | holdout 2023-26")
#     for k in f.columns:
#         x=f[k]
#         if x.notna().sum()<60: continue
#         q=pd.qcut(x.rank(method="first"),3,labels=False)
#         des=[y[(q==i)&(yr<2023)].mean() for i in range(3)]; hol=[y[(q==i)&(yr>=2023)].mean() for i in range(3)]
#         same = np.sign(des[2]-des[0])==np.sign(hol[2]-hol[0])
#         cuts=x.quantile([1/3,2/3]).round(2).tolist()
#         print(f"  {k:<18} cuts {str(cuts):<18} design {[int(v) for v in des]}  holdout {[int(v) for v in hol]}  {'SAME direction' if same else ''}")

# ======================= onbl3
# exec(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/onbl2.py").read().split("for nm,T in")[0])
# import metrics as M
# lab=pickle.load(open(SP+"lab.pkl","rb"))
# f=feats(ML); y=pd.Series(ML.net.values,index=pd.DatetimeIndex(ML.date)); yr=y.index.year
# rules={"L1: ret20 > 0":f.ret20.values>0,
#        "L2: ML score >= 0.03":f.ml_score.values>=0.03,
#        "L3: open <= 0.88 of overnight range":f.pos_in_on.values<=0.88,
#        "L1 + L2":(f.ret20.values>0)&(f.ml_score.values>=0.03),
#        "L1 + L3":(f.ret20.values>0)&(f.pos_in_on.values<=0.88),
#        "L1 + L2 + L3":(f.ret20.values>0)&(f.ml_score.values>=0.03)&(f.pos_in_on.values<=0.88)}
# print(f"ONB ML longs, all: n={len(y)} avg ${y.mean():.0f}")
# for k,keep in rules.items():
#     kk=pd.Series(keep,index=y.index)
#     a=y[kk]; s=y[~kk]
#     byk=a.groupby(a.index.year).mean(); bys=s.groupby(s.index.year).mean()
#     pf=lambda z: z[z>0].sum()/-z[z<0].sum()
#     print(f"  {k:<36} keep {kk.mean():.0%}: kept ${a.mean():5.0f} PF {pf(a):.2f} | skipped ${s.mean():5.0f} | design kept ${a[a.index.year<2023].mean():.0f} vs skip ${s[s.index.year<2023].mean():.0f} | holdout kept ${a[a.index.year>=2023].mean():.0f} vs skip ${s[s.index.year>=2023].mean():.0f} | yrs kept>skip {(byk>bys.reindex(byk.index)).sum()}/{len(byk)}")
# # funded bench: drop skipped LONG days from ONB ML (shorts untouched)
# dates=pd.DatetimeIndex(g.ts[lab.tr]); pos=pd.Series(np.arange(len(dates)),index=dates)
# base={"VB":3,"OND_MC":("risk",500),"EOS":("risk",500)}
# plans={"Current: ONB ML both sides $300":{**base,"ONB_ML_MC":("risk",300)}}
# rowsM={}
# for k,keep in rules.items():
#     skipd=y.index[~keep]; ii=pos.reindex(skipd).dropna().astype(int).values
#     nm="ONBML_"+k.split(":")[0].replace(" ","").replace("+","")
#     lab.W[nm]=lab.W["ONB_ML_MC"].copy(); lab.C[nm]=lab.C["ONB_ML_MC"].copy(); lab.W[nm][ii]=0; lab.C[nm][ii]=0; lab.stop[nm]=lab.stop["ONB_ML_MC"]
#     for rk in (300,400):
#         plans[f"  {k} (longs filtered), ONB ${rk}"]={**base,nm:("risk",rk)}
# print(lab.table(plans)); print(lab.table(plans,horizon=500))
# pickle.dump(lab,open(SP+"lab.pkl","wb"),protocol=4)

# ======================= onbl4
# exec(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/onbl2.py").read().split("for nm,T in")[0])
# import metrics as M
# lab=pickle.load(open(SP+"lab.pkl","rb"))
# wf=res[("ONB_frozenset_wf",100)]
# # walk-forward check on plain ONB longs (the ML model never saw the test year)
# P=PL.copy(); P["dt"]=pd.DatetimeIndex(P.date); P=P[P.dt.dt.year>=2019]; P["wf"]=wf.reindex(P.dt).values
# y=pd.Series(P.net.values,index=P.dt)
# print("Plain ONB longs 2019+, walk-forward ML score (model never saw the test year):")
# for lo,hi in ((-9,0),(0,0.03),(0.03,9)):
#     m=(P.wf>=lo)&(P.wf<hi); x=y[m.values]
#     print(f"  score in [{lo},{hi}): n={len(x)} avg ${x.mean():.0f}  design(2019-22) ${x[x.index.year<2023].mean():.0f}  holdout ${x[x.index.year>=2023].mean():.0f}")
# for thr in (0.0,0.02,0.03,0.05):
#     k=P.wf>=thr; a=y[k.values]; s=y[(~k).values & (P.wf>=0).values]
#     print(f"  long threshold {thr:.2f}: kept n={len(a)} ${a.mean():.0f} | skipped among score>=0: n={len(s)} ${s.mean() if len(s) else float('nan'):.0f}")
# # standard metrics for ONB ML long side before / after L2, $300 risk, and the whole strategy
# dates=pd.DatetimeIndex(g.ts[lab.tr]); m=dates.year>=2018
# names,b=lab._base({"ONB_ML_MC_L":("risk",300),"ONB_ML_MC_S":("risk",300),"ONBML_L2":("risk",300),"ONB_ML_MC":("risk",300)}); b=np.floor(b+1e-9)
# S_={k:pd.Series(lab.C[k]*b[i],index=dates)[m] for i,k in enumerate(names)}
# f=feats(ML); skipL=pd.DatetimeIndex(ML.date)[f.ml_score.values<0.03]
# L2long=S_["ONB_ML_MC_L"].copy(); L2long[L2long.index.isin(skipL)]=0
# print(M.table({"ONB ML longs (current)":(S_["ONB_ML_MC_L"],None),"ONB ML longs, score>=0.03":(L2long,None),"ONB ML shorts":(S_["ONB_ML_MC_S"],None),
#                "ONB ML both (current)":(S_["ONB_ML_MC"],None),"ONB ML both, longs score>=0.03":(S_["ONBML_L2"],None)}))
