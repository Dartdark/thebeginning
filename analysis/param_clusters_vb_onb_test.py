"""Parameter-cluster runs for Vault Break (720 combinations) and Overnight Bias (500, whole and by side),
scored on 2018-22 Calmar, top 20% clustered, medoids checked on 2023-26, then the Overnight Bias
candidates in the challenge simulator and the funded bench (blocks pc_grid, pc_clu, pc_bench).
Expects scratch pickles; kept as the record."""

# ======================= pc_grid
# import sys,time,pickle,warnings,itertools;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import numpy as np,pandas as pd
# from candidates24 import vault_break24, overnight_bias24
# from grid import execute
# import param_clusters as PC
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# g=pickle.load(open(SP+'g24.pkl','rb'))
# days=pd.DatetimeIndex(g.ts[g.trading]); A,B,E=pd.Timestamp('2018-01-01'),pd.Timestamp('2023-01-01'),pd.Timestamp('2027-01-01')
# def row(params,t,prefix=""):
#     r=dict(params)
#     for nm,lo,hi in (("des",A,B),("hold",B,E),("all",A,E)):
#         p=PC.period_metrics(t,days,lo,hi)
#         for k in ("trades","win","avg","annual","sharpe","sortino","profit_factor","calmar","ulcer","max_dd","t"):
#             r[f"{prefix}{nm}_{k}"]=p[k]
#     return r
# mode=sys.argv[1]
# t0=time.time(); rows=[]
# if mode=="vb":
#     for mult,first in itertools.product((0.2,0.25,0.3,0.35,0.4,0.5),(930,1000,1030,1100)):
#         s,kw=vault_break24(g,mult=mult,first=first)
#         for tp,sl in itertools.product((25,30,40,50,60,80),(50,60,75,90,110)):
#             s2=s.copy(); s2["stop"]=float(sl); s2["target"]=float(tp)
#             t=execute(g,s2,**kw)
#             rows.append(row(dict(mult=mult,first=first,tp=tp,sl=sl),t))
#         print(mult,first,round(time.time()-t0),flush=True)
#     pd.DataFrame(rows).to_pickle(SP+"pc_vb.pkl")
# else:
#     for frac,adx_min,stop_atr,rr in itertools.product((0.25,0.3,1/3,0.4),(0,15,20,25,30),(0.2,0.25,0.3,0.4,0.5),(1.5,2,3,4,6)):
#         t=overnight_bias24(g,frac=frac,adx_min=adx_min,stop_atr=stop_atr,rr=rr)
#         p=dict(frac=round(frac,3),adx_min=adx_min,stop_atr=stop_atr,rr=rr)
#         r=row(p,t)
#         r.update({k:v for k,v in row(p,t[t.side==1],"L_").items() if k.startswith("L_")})
#         r.update({k:v for k,v in row(p,t[t.side==-1],"S_").items() if k.startswith("S_")})
#         rows.append(r)
#         if len(rows)%25==0: print(len(rows),round(time.time()-t0),flush=True)
#     pd.DataFrame(rows).to_pickle(SP+"pc_onb.pkl")
# print("done",round(time.time()-t0))

# ======================= pc_clu
# import sys,pickle,warnings;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import numpy as np,pandas as pd
# import param_clusters as PC
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# pd.set_option("display.width",250); pd.set_option("display.max_columns",40)
# def show(df,params,prefix,label,current,min_tr):
#     sc=f"{prefix}des_calmar"
#     print(f"\n================ {label}: {len(df)} combinations; score = design (2018-22) Calmar; top 20% clustered")
#     best=df.replace([np.inf,-np.inf],np.nan).dropna(subset=[sc]); best=best[best[f"{prefix}des_trades"]>=min_tr].sort_values(sc,ascending=False)
#     cols=params+[f"{prefix}{p}_{k}" for p in ("des","hold") for k in ("trades","avg","profit_factor","sharpe","calmar","ulcer")]
#     print("-- single best (by design score):"); print(best[cols].head(3).round(2).to_string(index=False))
#     cur=df
#     for k,v in current.items(): cur=cur[np.isclose(cur[k],v)]
#     print("-- current settings:"); print(cur[cols].round(2).to_string(index=False))
#     summ,sel=PC.cluster_top(df,params,sc,top=0.2,k=5,min_trades=min_tr,trades_col=f"{prefix}des_trades")
#     rows=[]
#     for _,c in summ.iterrows():
#         med=df.loc[c.medoid_index]
#         rows.append({**{"cluster":int(c.cluster),"size":int(c["size"]),"des_score_mean":round(c.score_mean,2),"des_score_sd":round(c.score_sd,2)},
#                      **{f"{p} range":c[f"{p}_range"] for p in params},**{f"med {p}":med[p] for p in params},
#                      **{f"med {k}":round(med[f"{prefix}{k}"],2) for k in ("des_avg","des_calmar","hold_trades","hold_avg","hold_profit_factor","hold_sharpe","hold_calmar","hold_ulcer")}})
#     out=pd.DataFrame(rows); print("-- clusters (largest first) and their medoids:"); print(out.to_string(index=False))
#     # holdout rank of medoids vs the whole grid
#     hs=df[f"{prefix}hold_calmar"].replace([np.inf,-np.inf],np.nan)
#     for _,c in summ.iterrows():
#         v=df.loc[c.medoid_index,f"{prefix}hold_calmar"]; print(f"   cluster {int(c.cluster)} medoid holdout Calmar {v:.2f} = better than {np.mean(hs<v):.0%} of all combinations")
#     bv=best.iloc[0][f"{prefix}hold_calmar"]; print(f"   single best combination holdout Calmar {bv:.2f} = better than {np.mean(hs<bv):.0%}")
#     return summ
# vb=pd.read_pickle(SP+"pc_vb.pkl")
# s_vb=show(vb,["mult","first","tp","sl"],"","VAULT BREAK (long only)",dict(mult=0.3,first=1000,tp=40,sl=75),300)
# onb=pd.read_pickle(SP+"pc_onb.pkl")
# P=["frac","adx_min","stop_atr","rr"]; cur=dict(frac=0.333,adx_min=20,stop_atr=0.3,rr=3)
# s_on=show(onb,P,"","OVERNIGHT BIAS (both sides)",cur,300)
# s_L=show(onb,P,"L_","OVERNIGHT BIAS LONGS",cur,120)
# s_S=show(onb,P,"S_","OVERNIGHT BIAS SHORTS",cur,120)
# pickle.dump(dict(vb=s_vb,onb=s_on,L=s_L,S=s_S),open(SP+"pc_summ.pkl","wb"))

# ======================= pc_bench
# import sys,pickle,warnings;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import numpy as np,pandas as pd
# from candidates24 import overnight_bias24
# from portfolio import load_mc, paths, challenge
# from funded_lab import with_slippage
# import metrics as M
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# g=pickle.load(open(SP+'g24.pkl','rb')); lab=pickle.load(open(SP+'lab.pkl','rb')); fz=pickle.load(open(SP+'frozen.pkl','rb'))
# vb=pd.read_pickle(SP+"pc_vb.pkl")
# cur=vb[(vb['mult']==0.3)&(vb['first']==1000)&(vb.tp==40)&(vb.sl==75)].iloc[0]
# print(f"VB current holdout Calmar {cur.hold_calmar:.2f} = better than {np.mean(vb.hold_calmar<cur.hold_calmar):.0%} of all 720 combinations; design Calmar rank {np.mean(vb.des_calmar<cur.des_calmar):.0%}")
# tr=g.trading; D=len(tr); yr=pd.DatetimeIndex(g.ts[tr]).year; atr=g.daily_atr(15)
# stop_mnq=lambda pct: pct*np.nan_to_num(atr[tr],nan=1e12)*2
# VB=load_mc(g,"mc_reports/Backtesting Strategy Performance Report VB v1.xlsx")
# w,r=paths(g,with_slippage(VB)); VBw,VBc=w[tr]/10,r[tr]/10
# variants={"current (1/3, ADX 20, 0.30 ATR, 3R)":dict(frac=1/3,adx_min=20,stop_atr=0.30,rr=3.0),
#           "cluster medoid (1/3, ADX 30, 0.25 ATR, 3R)":dict(frac=1/3,adx_min=30,stop_atr=0.25,rr=3.0),
#           "ADX 30 only (1/3, ADX 30, 0.30 ATR, 3R)":dict(frac=1/3,adx_min=30,stop_atr=0.30,rr=3.0),
#           "ADX 25 (1/3, ADX 25, 0.25 ATR, 3R)":dict(frac=1/3,adx_min=25,stop_atr=0.25,rr=3.0)}
# T={}
# for nm,p in variants.items():
#     t=overnight_bias24(g,**p); T[nm]=(t,p)
#     x=(t.net-(1+(t.kind!=1))*5); x.index=pd.DatetimeIndex(t.date); x=x[x.index.year>=2018]
#     daily=x.groupby(x.index).sum()
#     m=M.perf(daily.reindex(pd.DatetimeIndex(g.ts[tr])[yr>=2018],fill_value=0),trades=x)
#     print(f"  {nm:<44} n={m['trades']} avg ${m['avg']:.0f} PF {m['profit_factor']:.2f} Sharpe {m['sharpe']:.2f} Sortino {m['sortino']:.2f} Calmar {m['calmar']:.2f} Ulcer {m['ulcer']:.2f}")
# print("\nCHALLENGE (VB 8 MNQ + plain ONB at $1,100 risk), pass rate within 21 days, with slippage:")
# for nm,(t,p) in T.items():
#     w,r=paths(g,with_slippage(t)); Ow,Oc=w[tr]/10,r[tr]/10
#     q=np.floor(1100/stop_mnq(p["stop_atr"]))[:,None]
#     W=VBw*8+Ow*q; R=VBc*8+Oc*q
#     res=[challenge(W,R,np.arange(s,min(s+21,D))) for s in range(D)]
#     o=np.array([np.nan if x is None else float(x[0]=="pass") for x in res]); dd=np.array([np.nan if x is None or x[0]!="pass" else x[1] for x in res])
#     print(f"  {nm:<44} pass {np.nanmean(o):.1%}  2018-22 {np.nanmean(o[yr<2023]):.1%}  2023-26 {np.nanmean(o[yr>=2023]):.1%}  median days {np.nanmedian(dd):.0f}",flush=True)
# print("\nFUNDED (ML filter applied on top: frozen score, longs >= 0.03, shorts >= 0):")
# s=fz["score"]
# for nm,(t,p) in T.items():
#     dt=pd.DatetimeIndex(t.date); sc=s.reindex(dt).to_numpy()
#     keep=np.where(t.side==1,sc>=0.03,sc>=0)
#     key="ONBX_"+nm.split(" (")[0].replace(" ","_")
#     lab.add(key,t[keep].reset_index(drop=True),stop_pts=p["stop_atr"]*atr)
# plans={nm:{"VB":3,"ONBX_"+nm.split(" (")[0].replace(" ","_"):("risk",300),"OND_MC":("risk",500),"EOS":("risk",500)} for nm in T}
# print(lab.table(plans)); print(lab.table(plans,horizon=500))
# cs=dict(fmin=0.5,fmax=1.0,ref=2000)
# for nm in T:
#     p={"VB":3,"ONBX_"+nm.split(" (")[0].replace(" ","_"):("risk",400),"OND_MC":("risk",500),"EOS":("risk",700)}
#     a=lab.score(p,250,**cs); b=lab.score(p,500,**cs); print(f"  cushion plan, {nm:<44} 1y ${a['expected']:,.0f} blown {a['blown']:.0%} | 2y ${b['expected']:,.0f} blown {b['blown']:.0%}")
# pickle.dump(lab,open(SP+'lab.pkl','wb'),protocol=4)
