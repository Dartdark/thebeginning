"""Relative Strength optimisation, follow-up diagnostics (2026-10-20, after relative_strength_opt_test.py; counted as trials):
  1. Is the stop-0.6 peak in the design grid also there on 2023+ (target 1.0, flat 15:00)? (diagnostic, no choice made)
  2. The base settings split by F1 (VXN above its 1-year median), and VXN SIZING instead of a filter:
     1x when VXN is above its median, 0.5x below (2 variants: 0.5x / 0x below) -- written after F1 showed kept > skipped
     in both periods but fewer trades lowered the Sharpe. Post-hoc: needs the live / forward record before use.
  python3 analysis/relative_strength_opt_followup.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import relative_strength_test as RS
from relative_strength_opt_test import sharpe, summary

if __name__ == "__main__":
    days, N, E = RS.load(); idx = pd.DatetimeIndex([pd.Timestamp(str(x)) for x in days.date]); Z = RS.signals(days, N, E)
    print("1. Stop sweep, target 1.0, flat 15:00: design / 2023+ / full daily Sharpe, $ a trade")
    for s in (0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8, 1.0):
        t = RS.trades(days, N, Z, stop_f=s)
        print(f"   stop {s:<5} design {sharpe(t, idx, hi='2023'):.2f}  2023+ {sharpe(t, idx, lo='2023'):.2f}  full {sharpe(t, idx):.2f}  ${t.pnl.mean():.0f}  stops hit {np.mean(t.kind == 'stop'):.0%}")
    T = RS.trades(days, N, Z)
    vxn = pd.read_csv("data/VXN_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE
    hi = (vxn.shift(1) > vxn.rolling(252).median().shift(1)).reindex(T.date).fillna(False).to_numpy()
    print("\n2. Base settings by VXN regime (VXN at yesterday's close vs its 1-year median)")
    for nm, m in (("VXN high", hi), ("VXN low", ~hi)):
        x = T[m]; a, b = x[x.date < "2023"], x[x.date >= "2023"]
        print(f"   {nm:<9} n {len(x):4d} ${x.pnl.mean():5.0f} (t {RS.tstat(x.pnl):.1f}) | design ${a.pnl.mean():.0f} (t {RS.tstat(a.pnl):.1f}) | 2023+ ${b.pnl.mean():.0f} (t {RS.tstat(b.pnl):.1f})")
    summary("base 1x always", T, idx)
    for lo in (0.5, 0.0):
        summary(f"1x VXN high / {lo}x VXN low", T, idx, w=np.where(hi, 1.0, lo))
    T.assign(vxn_high=hi).to_csv(RS.SP + "rs_base_vxn.csv", index=False)
