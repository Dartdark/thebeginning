"""Robustness (clusters, holdout, folds, sensitivity) for Overnight Drift, Expiration Open Short and Overnight
Bias ML by side, 2026-10-12 (blocks rob2_grid, rob2_an, rob2_bench). Expects scratch pickles."""

# ======================= rob2_grid
# import sys,time,pickle,warnings,itertools;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import numpy as np,pandas as pd
# from candidates24 import overnight_drift24, overnight_bias24
# from grid import execute
# from grid24 import jof
# import param_clusters as PC, calendar_flows as CF
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# g=pickle.load(open(SP+'g24.pkl','rb')); fz=pickle.load(open(SP+'frozen.pkl','rb'))
# days=pd.DatetimeIndex(g.ts[g.trading]); days=days[days.year>=2018]
# def daily(t):
#     x=PC.trade_net(t); d=pd.DatetimeIndex(t.date); return x.groupby(d).sum().reindex(days,fill_value=0.0).to_numpy(np.float32)
# mode=sys.argv[1]; P=[];DL=[]; t0=time.time()
# if mode=="ond":
#     for entry,exit_,st,down in itertools.product((0,30,100),(200,300,400,500,600),(0.2,0.3,0.4,0.6,1.0),(True,False)):
#         s,kw=overnight_drift24(g,entry=entry,exit=exit_,stop_atr=st,down_only=down)
#         t=execute(g,s,**kw); P.append(dict(entry=entry,exit=exit_,stop_atr=st,down_only=int(down))); DL.append(daily(t))
# elif mode=="eos":
#     cal=CF.calendar(g); opex=cal.index[cal.opex].to_numpy(); atr=g.daily_atr(15)
#     for start,exit_,st in itertools.product((830,845,900),(915,930,1000,1030,1100,1200,1500),(0.2,0.3,0.4,0.6,1.0)):
#         if exit_<=start: continue
#         s=pd.DataFrame(dict(day=opex,dj=jof(start),side=-1,stop=st*atr[opex],target=np.inf,exit_j=jof(exit_)))
#         t=execute(g,s,max_trades=1); P.append(dict(start=start,exit=exit_,stop_atr=st)); DL.append(daily(t))
# else:   # ONB ML: plain ONB grid + frozen ML score filter per side
#     s=fz["score"]
#     for adx_min,st,rr in itertools.product((15,20,25,30),(0.2,0.25,0.3,0.4),(2,3,4)):
#         t=overnight_bias24(g,adx_min=adx_min,stop_atr=st,rr=rr); sc=s.reindex(pd.DatetimeIndex(t.date)).to_numpy()
#         for lm,sm in itertools.product((0,0.03,0.06),(-0.03,0,0.03)):
#             keep=np.where(t.side==1,sc>=lm,sc>=sm); tt=t[keep]
#             P.append(dict(adx_min=adx_min,stop_atr=st,rr=rr,long_min=lm,short_min=sm))
#             DL.append(np.stack([daily(tt),daily(tt[tt.side==1]),daily(tt[tt.side==-1])]))
# pickle.dump((pd.DataFrame(P),np.array(DL),days),open(SP+f"rob2_{mode}.pkl","wb")); print("done",mode,len(P),round(time.time()-t0),flush=True)

# ======================= rob2_an
# import sys,pickle,warnings;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import numpy as np,pandas as pd
# import robustness as R, param_clusters as PC
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# pd.set_option("display.width",250)
# folds=[(y,y+2) for y in range(2018,2025)]
# def clusters(P,DL,days,params,chosen,label):
#     des=(days.year<=2022); hol=(days.year>=2023); full=np.ones(len(days),bool)
#     df=P.copy(); df["des"]=R.calmar_rows(DL,des); df["hold"]=R.calmar_rows(DL,hol); df["full"]=R.calmar_rows(DL,full)
#     df["des_sh"]=R.sharpe_rows(DL,des); df["hold_sh"]=R.sharpe_rows(DL,hol)
#     summ,_=PC.cluster_top(df,params,"des",top=0.2,k=min(5,max(2,len(df)//25)))
#     print(f"-- clusters of the top 20% by 2018-22 Calmar ({len(df)} combinations):")
#     hs=df.hold
#     for _,c in summ.iterrows():
#         m=df.loc[c.medoid_index]
#         print(f"   size {int(c['size']):3d}  medoid {dict((p,m[p]) for p in params)}  2018-22 Calmar {m.des:.2f} | 2023-26 Calmar {m.hold:.2f} (better than {np.mean(hs<m.hold):.0%}) | full {m.full:.2f}")
#     b=df.sort_values("des",ascending=False).iloc[0]
#     print(f"   single best by 2018-22: {dict((p,b[p]) for p in params)} 2023-26 Calmar {b.hold:.2f} (better than {np.mean(hs<b.hold):.0%})")
#     for nm,ctr in chosen.items():
#         i=R.find(P,ctr); print(f"   {nm}: 2018-22 {df.des[i]:.2f} (rank {np.mean(df.des<df.des[i]):.0%}) | 2023-26 {df.hold[i]:.2f} (better than {np.mean(hs<df.hold[i]):.0%}) | full {df.full[i]:.2f}")
# def report(title,P,DL,days,params,chosen):
#     print(f"\n================ {title}")
#     clusters(P,DL,days,params,chosen,title)
#     ft=R.fold_table(P,DL,days,folds,params,chosen); print("-- folds:"); print(ft.round(2).to_string(index=False))
#     for nm,ctr in chosen.items():
#         print(f" -- sensitivity around {nm} {ctr} (2018-2026; Calmar | Sharpe):")
#         for p,d in R.sensitivity(P,DL,days,ctr,params).items():
#             arr=d.calmar.to_numpy(); i=int(np.argmin(np.abs(d[p].to_numpy(float)-ctr[p]))); nb=[arr[j] for j in (i-1,i+1) if 0<=j<len(arr)]
#             print(f"   {p:<10} "+" ".join(f"{v:g}:{c:.2f}|{s:.2f}" for v,c,s in zip(d[p],d.calmar,d.sharpe))+(f"   | worst neighbour drop {(arr[i]-min(nb))/arr[i]:.0%}" if nb else ""))
# P,DL,days=pickle.load(open(SP+"rob2_ond.pkl","rb"))
# report("OVERNIGHT DRIFT (long only)",P,DL,days,["entry","exit","stop_atr","down_only"],{"current":dict(entry=0,exit=300,stop_atr=0.3,down_only=1)})
# P,DL,days=pickle.load(open(SP+"rob2_eos.pkl","rb"))
# report("EXPIRATION OPEN SHORT (short only)",P,DL,days,["start","exit","stop_atr"],{"current":dict(start=830,exit=1000,stop_atr=0.3)})
# P,DL,days=pickle.load(open(SP+"rob2_onbml.pkl","rb"))
# prm=["adx_min","stop_atr","rr","long_min","short_min"]; ch={"current v2":dict(adx_min=20,stop_atr=0.3,rr=3,long_min=0.03,short_min=0)}
# report("OVERNIGHT BIAS ML (both sides)",P,DL[:,0,:],days,prm,ch)
# report("OVERNIGHT BIAS ML LONGS",P,DL[:,1,:],days,prm,ch)
# report("OVERNIGHT BIAS ML SHORTS",P,DL[:,2,:],days,prm,ch)

# ======================= rob2_bench
# import sys,pickle,warnings;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import numpy as np,pandas as pd
# import robustness as R
# from candidates24 import overnight_bias24
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# P,DL,days=pickle.load(open(SP+"rob2_onbml.pkl","rb"))
# folds=[(y,y+2) for y in range(2018,2025)]
# ch={"v2 (stop 0.30)":dict(adx_min=20,stop_atr=0.3,rr=3,long_min=0.03,short_min=0),"v2 stop 0.25":dict(adx_min=20,stop_atr=0.25,rr=3,long_min=0.03,short_min=0)}
# print(R.fold_table(P,DL[:,0,:],days,folds,["adx_min","stop_atr","rr","long_min","short_min"],ch)[["fold","v2 (stop 0.30) calmar","v2 (stop 0.30) pct","v2 stop 0.25 calmar","v2 stop 0.25 pct"]].round(2).to_string(index=False))
# for nm,c in ch.items():
#     i=R.find(P,c)
#     for lab_,m in (("2018-22",days.year<=2022),("2023-26",days.year>=2023)):
#         print(f"  {nm} {lab_}: Calmar {R.calmar_rows(DL[i:i+1,0,:],m)[0]:.2f} Sharpe {R.sharpe_rows(DL[i:i+1,0,:],m)[0]:.2f}")
# lab=pickle.load(open(SP+'lab.pkl','rb')); g=lab.g; fz=pickle.load(open(SP+'frozen.pkl','rb')); atr=g.daily_atr(15)
# for st in (0.3,0.25):
#     t=overnight_bias24(g,stop_atr=st); sc=fz["score"].reindex(pd.DatetimeIndex(t.date)).to_numpy()
#     keep=np.where(t.side==1,sc>=0.03,sc>=0); lab.add(f"ONBML_st{st}",t[keep].reset_index(drop=True),stop_pts=st*atr)
# base={"VB":3,"OND_MC":("risk",500),"EOS":("risk",500)}
# plans={f"ONB ML v2, stop {st}":{**base,f"ONBML_st{st}":("risk",300)} for st in (0.3,0.25)}
# print(lab.table(plans)); print(lab.table(plans,horizon=500))
# cs=dict(fmin=0.5,fmax=1.0,ref=2000)
# for st in (0.3,0.25):
#     p={"VB":3,f"ONBML_st{st}":("risk",400),"OND_MC":("risk",500),"EOS":("risk",700)}
#     a=lab.score(p,250,**cs); b=lab.score(p,500,**cs); print(f"  cushion plan, stop {st}: 1y ${a['expected']:,.0f} blown {a['blown']:.0%} | 2y ${b['expected']:,.0f} blown {b['blown']:.0%}")
