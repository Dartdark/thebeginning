"""Baldi-Lanfranchi, Collin-Dufresne & Daniel (2026) "Asymmetric Reversals" (NBER w35840) as a
time-series test on NQ 2018-2026: next-session returns after up / down days split by scheduled news
(8:30 ET release spike or FOMC) vs no news; NQ residual vs ES; Overnight Drift split by the
previous day; then a "long the session after a big no-news down day" trade in the funded bench
(second block, commented). Record of the test."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
import event_days as EV
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g=pickle.load(open(SP+"g24.pkl","rb")); ge=pickle.load(open(SP+"ge.pkl","rb"))
def daily(gg):
    tr=gg.trading; C=pd.DataFrame(gg.c).ffill(axis=1).to_numpy(); d=pd.DatetimeIndex(gg.ts[tr])
    return pd.DataFrame(dict(row=tr,o=gg.o[tr,jof(831)],c=C[tr,jof(1500)],c0300=C[tr,jof(300)]),index=d)
N=daily(g); E=daily(ge).reindex(N.index)
N["rth"]=np.log(N.c/N.o); E["rth"]=np.log(E.c/E.o)
N["nxt_on"]=(np.log(N.o.shift(-1)/N.c))           # 15:00 -> next 8:30
N["nxt_ond"]=np.log(N.c0300.shift(-1)/N.c)        # 15:00 -> next 3:00 (Overnight Drift window incl. evening)
N["nxt_rth"]=N.rth.shift(-1); N["nxt_cc"]=np.log(N.c.shift(-1)/N.c); N["nxt5"]=np.log(N.c.shift(-5)/N.c)
rel=set(pd.DatetimeIndex(g.ts[EV.release_days(g)])); fomc=set(pd.to_datetime(EV.FOMC_DATES))
N["news"]=[(d in rel) or (d in fomc) for d in N.index]
# NQ residual vs ES (rolling 60-day beta on RTH returns, known before the day)
b=(N.rth.rolling(60).cov(E.rth)/E.rth.rolling(60).var()).shift(1)
N["res"]=N.rth-b*E.rth; N["sys"]=b*E.rth
N["nxt_res"]=(N.nxt_rth-b.shift(-1)*E.rth.shift(-1))
N=N[N.index.year>=2018].dropna(subset=["rth"])
z=N.rth/N.rth.rolling(60).std().shift(1)
def rep(lab,m,col):
    x=N.loc[m,col].dropna()*1e4
    print(f"   {lab:<42} n={len(x):4d} mean {x.mean():6.1f} bp  t={x.mean()/x.std()*np.sqrt(len(x)):4.1f}  up {(x>0).mean():.0%}")
for col,lab in (("nxt_on","next overnight 15:00->8:30"),("nxt_ond","15:00 -> next 3:00"),("nxt_rth","next 8:30-15:00"),("nxt5","next 5 days close-close")):
    print(f"\n== {lab} (NQ, log bp), after day t:")
    rep("all days",N.index==N.index,col)
    for nl,nm in (("no-news",~N.news),("news",N.news)):
        rep(f"{nl} down day (RTH<0)",nm&(N.rth<0),col); rep(f"{nl} up day",nm&(N.rth>0),col)
        rep(f"{nl} big down (z<-1)",nm&(z<-1),col); rep(f"{nl} big up (z>1)",nm&(z>1),col)
print("\n== NQ residual vs ES (next-day NQ-minus-beta*ES RTH return, bp):")
zr=N.res/N.res.rolling(60).std().shift(1)
for lab,m in (("res < 0",N.res<0),("res > 0",N.res>0),("res z < -1",zr<-1),("res z > 1",zr>1)):
    rep(lab,m,"nxt_res")
# Overnight Drift MC trades split by news / residual of the down day
ond=load_mc(g,"mc_reports/Backtesting Strategy Performance Report OND v1.xlsx"); ond=ond[ond.j0<=jof(30)]
od=pd.DatetimeIndex(g.ts[ond.day.to_numpy()])
prev={d:N.index[N.index<d][-1] if (N.index<d).any() else None for d in od}
pv=pd.DatetimeIndex([prev[d] for d in od])
o=pd.DataFrame(dict(net=ond.net.to_numpy(),news=N.news.reindex(pv).to_numpy(),res=N.res.reindex(pv).to_numpy(),sys=N.sys.reindex(pv).to_numpy()),index=od)
print("\n== Overnight Drift (MC list, $ per NQ) by the previous (down) day:")
for lab,m in (("all",o.index==o.index),("prev day no news",o.news==False),("prev day news",o.news==True),("prev residual < 0 (NQ weaker than ES)",o.res<0),("prev residual > 0",o.res>0),("no news & residual<0",(o.news==False)&(o.res<0))):
    x=o.net[m]; by=x.groupby(x.index.year).mean()
    print(f"   {lab:<40} n={len(x):4d} avg ${x.mean():5.0f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f} yrs+ {(by>0).sum()}/{len(by)}")

# ---------------- trade + funded bench
# exec(open("/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/air1.py").read().split("def rep(")[0])
# from grid import execute
# import intraday_research as IR
# lab=pickle.load(open(SP+"lab.pkl","rb")); atr=g.daily_atr(15)
# row=pd.Series(g.trading,index=pd.DatetimeIndex(g.ts[g.trading]))
# nxt={N.index[i]:N.index[i+1] for i in range(len(N)-1)}
# def summ(t,name):
#     t2=t[pd.DatetimeIndex(t.date).year>=2018].copy(); t2["slips"]=1+(t2["kind"]!=1); t2["net"]-=t2["slips"]*5
#     s=IR.summary(t2); by=t2.groupby(pd.DatetimeIndex(t2.date).year).net.mean().round().to_dict()
#     print(f"{name:<52} n={s['trades']:4d} win {s['win']} avg ${s['avg']:5.0f} PF {s['pf']:.2f} t={s['t_stat']:4.1f} yrs+ {s['years_pos']}  {by}")
# for nm,cond in (("no-news big down",(~N.news)&(z<-1)),("any big down",z<-1),("no-news down z<-1.5",(~N.news)&(z<-1.5))):
#     days=[nxt[d] for d in N.index[cond] if d in nxt]
#     r=row.reindex(days).dropna().astype(int).to_numpy()
#     for st in (0.3,0.5):
#         s=pd.DataFrame(dict(day=r,dj=jof(830),side=1,stop=st*atr[r],target=np.inf,exit_j=jof(1500)))
#         t=execute(g,s,max_trades=1); key=f"AIR_{nm}_{st}"; summ(t,f"{nm}, long next 8:30-15:00, stop {st}"); lab.add(key,t,stop_pts=st*atr)
# base={"VB":3,"ONB_ML_MC":("risk",300),"OND_MC":("risk",500),"EOS":("risk",500)}
# plans={"Funded set (ONB ML)":base}
# for k in [k for k in lab.C if k.startswith("AIR_")]:
#     for rk in (200,400):
#         p=dict(base); p[k]=("risk",rk); plans[f"  + {k} ${rk}"]=p
# print(lab.corr(["VB","ONB_ML_MC","OND_MC","EOS","AIR_no-news big down_0.5"]).round(2).to_string())
# print(lab.table(plans)); print(lab.table(plans,horizon=500))
