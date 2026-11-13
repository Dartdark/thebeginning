"""Writes the 5 sibling thresholds of the spec's 6-variant sweep (0.10 itself is trades.csv) for checker G9 (PBO)."""
import sys, numpy as np, pandas as pd
sys.argv = ["x"]; exec(open("/home/user/thebeginning/checks/candidates/s30_ibs_010/stress.py").read().split('print("threshold sweep')[0])
for th in (0.05, 0.075, 0.125, 0.15, 0.20):
    T = run((S.ibs < th).values)
    pd.DataFrame(dict(date=pd.to_datetime(g.dates[S.r.values[T.e]].astype(str)).date, side=1, net=T.net.round(2))).to_csv(
        f"/home/user/thebeginning/checks/candidates/s30_ibs_010/variants/ibs_{th}.csv", index=False)
