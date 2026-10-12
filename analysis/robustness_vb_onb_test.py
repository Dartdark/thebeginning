"""Fold stability and one-at-a-time sensitivity for Vault Break and Overnight Bias (2026-10-12), plus a fine
grid around Vault Break target / first entry (blocks fold_grid, fold_an, vbfine). Expects scratch pickles."""

# ======================= fold_grid
# import sys,time,pickle,warnings,itertools;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import numpy as np,pandas as pd
# from candidates24 import vault_break24, overnight_bias24
# from grid import execute
# import param_clusters as PC
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# g=pickle.load(open(SP+'g24.pkl','rb'))
# days=pd.DatetimeIndex(g.ts[g.trading]); days=days[days.year>=2018]
# def daily(t):
#     x=PC.trade_net(t); d=pd.DatetimeIndex(t.date); return x.groupby(d).sum().reindex(days,fill_value=0.0).to_numpy(np.float32)
# mode=sys.argv[1]; P=[]; DL=[]; t0=time.time()
# if mode=="vb":
#     for mult,first in itertools.product((0.2,0.25,0.3,0.35,0.4,0.5),(930,1000,1030,1100)):
#         s,kw=vault_break24(g,mult=mult,first=first)
#         for tp,sl in itertools.product((25,30,40,50,60,80),(50,60,75,90,110)):
#             s2=s.copy(); s2["stop"]=float(sl); s2["target"]=float(tp); t=execute(g,s2,**kw)
#             P.append(dict(mult=mult,first=first,tp=tp,sl=sl)); DL.append(daily(t))
#     pickle.dump((pd.DataFrame(P),np.array(DL),days),open(SP+"fold_vb.pkl","wb"))
# else:
#     for frac,adx_min,stop_atr,rr in itertools.product((0.25,0.3,1/3,0.4),(0,15,20,25,30),(0.2,0.25,0.3,0.4,0.5),(1.5,2,3,4,6)):
#         t=overnight_bias24(g,frac=frac,adx_min=adx_min,stop_atr=stop_atr,rr=rr)
#         P.append(dict(frac=round(frac,3),adx_min=adx_min,stop_atr=stop_atr,rr=rr)); DL.append(np.stack([daily(t),daily(t[t.side==1]),daily(t[t.side==-1])]))
#     pickle.dump((pd.DataFrame(P),np.array(DL),days),open(SP+"fold_onb.pkl","wb"))
# print("done",round(time.time()-t0),flush=True)

# ======================= fold_an
# import sys,pickle,warnings;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import numpy as np,pandas as pd
# import robustness as R
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# pd.set_option("display.width",250)
# folds=[(y,y+2) for y in range(2018,2025)]
# def report(title,P,DL,days,params,chosen):
#     print(f"\n================ {title}")
#     ft=R.fold_table(P,DL,days,folds,params,chosen); print(ft.round(2).to_string(index=False))
#     for p in params: print(f"   best {p} across folds: {ft[f'best {p}'].tolist()}")
#     for name,ctr in chosen.items():
#         print(f"\n -- sensitivity around {name} {ctr} (2018-2026; Calmar | Sharpe):")
#         for p,df in R.sensitivity(P,DL,days,ctr,params).items():
#             cells=" ".join(f"{v:g}:{c:.2f}|{s:.2f}" for v,c,s in zip(df[p],df.calmar,df.sharpe))
#             arr=df.calmar.to_numpy(); i=int(np.argmin(np.abs(df[p].to_numpy(float)-ctr[p])))
#             nb=[arr[j] for j in (i-1,i+1) if 0<=j<len(arr)]
#             drop=(arr[i]-min(nb))/arr[i] if nb else np.nan
#             print(f"   {p:<9} {cells}   | worst neighbour drop {drop:.0%}")
# P,DL,days=pickle.load(open(SP+"fold_vb.pkl","rb"))
# report("VAULT BREAK",P,DL,days,["mult","first","tp","sl"],{"current":dict(mult=0.3,first=1000,tp=40,sl=75)})
# P,DL,days=pickle.load(open(SP+"fold_onb.pkl","rb"))
# prm=["frac","adx_min","stop_atr","rr"]; ch={"current":dict(frac=0.333,adx_min=20,stop_atr=0.3,rr=3),"ADX30":dict(frac=0.333,adx_min=30,stop_atr=0.25,rr=3)}
# report("OVERNIGHT BIAS (both sides)",P,DL[:,0,:],days,prm,ch)
# report("OVERNIGHT BIAS LONGS",P,DL[:,1,:],days,prm,ch)
# report("OVERNIGHT BIAS SHORTS",P,DL[:,2,:],days,prm,ch)

# ======================= vbfine
# import sys,pickle,warnings,itertools;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import numpy as np,pandas as pd
# from candidates24 import vault_break24
# from grid import execute
# import param_clusters as PC, robustness as R
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# g=pickle.load(open(SP+'g24.pkl','rb'))
# days=pd.DatetimeIndex(g.ts[g.trading]); days=days[days.year>=2018]
# def daily(t):
#     x=PC.trade_net(t); d=pd.DatetimeIndex(t.date); return x.groupby(d).sum().reindex(days,fill_value=0.0).to_numpy(float)
# P=[];DL=[]
# for first in (930,945,1000,1015,1030):
#     s,kw=vault_break24(g,mult=0.3,first=first)
#     for tp in (30,33,35,38,40,42,45,48,50):
#         s2=s.copy(); s2["stop"]=75.0; s2["target"]=float(tp); t=execute(g,s2,**kw); P.append(dict(first=first,tp=tp)); DL.append(daily(t))
# P=pd.DataFrame(P); DL=np.array(DL)
# for nm,(a,b) in (("2018-2026",(2018,2026)),("2018-2022",(2018,2022)),("2023-2026",(2023,2026))):
#     m=(days.year>=a)&(days.year<=b); c=R.calmar_rows(DL,m)
#     tab=pd.DataFrame(c.reshape(5,9),index=[930,945,1000,1015,1030],columns=[30,33,35,38,40,42,45,48,50])
#     print(f"\nVault Break Calmar, {nm} (rows = first entry time, columns = target pts; stop 75, noise 0.3)"); print(tab.round(2).to_string())
