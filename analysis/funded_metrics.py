"""Standard metrics (analysis/metrics.py) for the funded set at funded sizes, by side for Overnight Bias ML, and per 1 NQ.
Expects the pickled funded lab from a scratch run; kept as the record."""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"analysis")
import numpy as np, pandas as pd
import metrics as M
SP="/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
lab=pickle.load(open(SP+"lab.pkl","rb")); g=lab.g
dates=pd.DatetimeIndex(g.ts[lab.tr]); m=dates.year>=2018
def sized(plan):
    names,b=lab._base(plan); b=np.floor(b+1e-9)
    return {k: pd.Series(lab.C[k]*b[i],index=dates)[m] for i,k in enumerate(names)}
for title,plan in (("Funded set, current sizes (VB 3, ONB ML $300, OND $500, EOS $500)",{"VB":3,"ONB_ML_MC":("risk",300),"OND_MC":("risk",500),"EOS":("risk",500)}),
                   ("Recommended sizes (ONB ML $400, EOS $700)",{"VB":3,"ONB_ML_MC":("risk",400),"OND_MC":("risk",500),"EOS":("risk",700)})):
    P=sized(plan); rows={k:(v,None) for k,v in P.items()}; rows["PORTFOLIO"]=(sum(P.values()),None)
    print(f"\n{title}, 2018-2026, $ per day at funded size (MNQ), with slippage; drawdown % vs $50,000")
    print(M.table(rows))
# long/short split of ONB ML at $300
P=sized({"ONB_ML_MC_L":("risk",300),"ONB_ML_MC_S":("risk",300)})
print("\nOvernight Bias ML by side ($300 risk)"); print(M.table({"longs":(P["ONB_ML_MC_L"],None),"shorts":(P["ONB_ML_MC_S"],None),"both":(P["ONB_ML_MC_L"]+P["ONB_ML_MC_S"],None)}))
# per NQ, 1 contract (strategy quality, no sizing)
rows={k:(pd.Series(lab.daily(k),index=dates)[m],None) for k in ("VB","ONB_ML_MC","OND_MC","EOS")}
print("\nPer 1 NQ contract (no sizing), drawdown % vs $50,000"); print(M.table(rows))
