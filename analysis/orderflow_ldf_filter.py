"""Late-Day Flow filtered by the last 30 minutes of order-flow delta (The Bridge), on the funded bench, 2026-10-13.

The one order-flow split in analysis/orderflow_test.py that held in both periods: LDF longs make $138 when the
last 30 minutes of delta agree vs -$4 when not (2018-22 and 2023-26 alike). Here: drop the disagreeing longs
(or all disagreeing trades), standard metrics, 2023+ bootstrap / permutation, funded bench vs the current plan.
  python3 analysis/orderflow_ldf_filter.py
"""
import sys,pickle,warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,'analysis')
import numpy as np,pandas as pd
from grid24 import jof
from portfolio import load_mc
import orderflow_test as T, metrics as M, resampling as R
g=pickle.load(open('scratch_data/g24.pkl','rb')); A=T.load_of(g); lab=pickle.load(open('scratch_data/lab.pkl','rb'))
atr=g.daily_atr(15)
t=load_mc(g,T.REPORTS["LDF"])
ag=[]
for r in t.itertuples():
    d,j=int(r.day),int(r.j0)-1
    d30=T.wsum(A["delta"],d,j-29,j) if A["has"][d].any() else np.nan
    ag.append(np.nan if (np.isnan(d30) or d30==0) else float(np.sign(d30)==r.side))
t["agree30"]=ag
cov=t.date>="2018-01-02"
print("LDF trades",len(t),"with order flow",int(np.sum(~np.isnan(t.agree30))))
for nm,keep in (("longs only when delta agrees", ~((t.side>0)&(t.agree30==0))), ("both sides only when delta agrees", ~(t.agree30==0))):
    f=t[keep].reset_index(drop=True)
    lab.add("LDF_F",f,stop_pts=0.25*atr)
    plan={"VB":3,"ONB_ML2_MC":("risk",400),"MON_MC":1,"EOS":("risk",700),"LDF_MC":2,"NFP_MC":("risk",500),"VCS_MC":1}
    CS=dict(fmin=0.5,fmax=1.0,ref=1500.0)
    for pn,p in (("current plan",plan),(f"LDF filtered ({nm}) 2 MNQ",{**{k:v for k,v in plan.items() if k!="LDF_MC"},"LDF_F":2}),(f"LDF filtered ({nm}) 3 MNQ",{**{k:v for k,v in plan.items() if k!="LDF_MC"},"LDF_F":3})):
        a,c=lab.score(p,250,**CS),lab.score(p,500,**CS)
        print(f"   {pn:<62} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
    dts=pd.DatetimeIndex(g.ts[lab.tr]); mk=dts.year>=2018
    rows={"LDF":(pd.Series(lab.daily("LDF_MC"),index=dts)[mk],None),f"LDF {nm}":(pd.Series(lab.daily("LDF_F"),index=dts)[mk],None)}
    print(M.table(rows))
    h={k+" 2023+":v[0][v[0].index>="2023-01-01"] for k,v in rows.items()}
    b,pp=R.report(h,n=2000); print(b); print(pp)
    print("   filtered by year:", f.groupby(f.date.dt.year).net.sum().round(0).astype(int).to_dict())
