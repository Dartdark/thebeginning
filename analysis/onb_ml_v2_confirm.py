"""MultiCharts confirmation of Overnight Bias ML v2 (longs need score >= 0.03): funded bench and standard
metrics vs v1, whole and by side, from 2018-01 and from 2018-04. Expects the pickled funded lab."""
import sys,pickle,warnings,glob;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
import pandas as pd,numpy as np
from portfolio import load_mc
import metrics as M
SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
g=pickle.load(open(SP+'g24.pkl','rb')); lab=pickle.load(open(SP+'lab.pkl','rb'))
new=load_mc(g,glob.glob('*ML (funded) v2*.xlsx')[0]); atr=g.daily_atr(15)
lab.add("ONB_ML2_MC",new,stop_pts=0.3*atr)
for s,nm in ((1,"L"),(-1,"S")): lab.add(f"ONB_ML2_{nm}",new[new.side==s].reset_index(drop=True),stop_pts=0.3*atr)
base={"VB":3,"OND_MC":("risk",500),"EOS":("risk",500)}
plans={"Funded set with ONB ML v1 ($300)":{**base,"ONB_ML_MC":("risk",300)},"Funded set with ONB ML v2 ($300)":{**base,"ONB_ML2_MC":("risk",300)},
       "  v2 at $400":{**base,"ONB_ML2_MC":("risk",400)}}
print(lab.table(plans)); print(lab.table(plans,horizon=500))
cs=dict(fmin=0.5,fmax=1.0,ref=2000)
for lbl,k in (("v1","ONB_ML_MC"),("v2","ONB_ML2_MC")):
    p={"VB":3,k:("risk",400),"OND_MC":("risk",500),"EOS":("risk",700)}
    a=lab.score(p,250,**cs); b=lab.score(p,500,**cs)
    print(f"Recommended plan with cushion sizing, ONB ML {lbl} $400: 1y ${a['expected']:,.0f} blown {a['blown']:.0%} | 2y ${b['expected']:,.0f} blown {b['blown']:.0%}")
dates=pd.DatetimeIndex(g.ts[lab.tr]); m=dates.year>=2018
names,bb=lab._base({"ONB_ML_MC":("risk",300),"ONB_ML2_MC":("risk",300),"ONB_ML_MC_L":("risk",300),"ONB_ML2_L":("risk",300),"ONB_ML2_S":("risk",300)}); bb=np.floor(bb+1e-9)
D={k:pd.Series(lab.C[k]*bb[i],index=dates)[m] for i,k in enumerate(names)}
print(M.table({"v1 whole":(D["ONB_ML_MC"],None),"v2 whole":(D["ONB_ML2_MC"],None),"v1 longs":(D["ONB_ML_MC_L"],None),"v2 longs":(D["ONB_ML2_L"],None),"v2 shorts":(D["ONB_ML2_S"],None)}))
pickle.dump(lab,open(SP+'lab.pkl','wb'),protocol=4)

# ---- same metrics from 2018-01 and from 2018-04 (after the filter's warm-up)
# import sys,pickle,warnings;warnings.filterwarnings('ignore');sys.path.insert(0,'analysis')
# import pandas as pd,numpy as np
# import metrics as M
# SP='/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/'
# lab=pickle.load(open(SP+'lab.pkl','rb')); g=lab.g
# dates=pd.DatetimeIndex(g.ts[lab.tr])
# names,bb=lab._base({"ONB_ML_MC":("risk",300),"ONB_ML2_MC":("risk",300),"ONB_ML_MC_L":("risk",300),"ONB_ML2_L":("risk",300),"ONB_ML_MC_S":("risk",300),"ONB_ML2_S":("risk",300)}); bb=np.floor(bb+1e-9)
# for start in ("2018-01-01","2018-04-01"):
#     m=dates>=pd.Timestamp(start)
#     D={k:pd.Series(lab.C[k]*bb[i],index=dates)[m] for i,k in enumerate(names)}
#     print(f"\nfrom {start}"); print(M.table({"v1 whole":(D["ONB_ML_MC"],None),"v2 whole":(D["ONB_ML2_MC"],None),"v1 longs":(D["ONB_ML_MC_L"],None),"v2 longs":(D["ONB_ML2_L"],None),"v1 shorts":(D["ONB_ML_MC_S"],None),"v2 shorts":(D["ONB_ML2_S"],None)}))
#     x=D["ONB_ML2_L"]; eq=x.cumsum(); dd=eq-eq.cummax(); i=dd.idxmin(); pk=eq[:i].idxmax(); print("  v2 longs max DD from",pk.date(),"to",i.date())
