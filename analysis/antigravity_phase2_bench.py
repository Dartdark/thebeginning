"""Antigravity Phase 2 (2026-10-17, branch antigravity/jesse tasks/out_0N/improve_report.md): its 'funded-account option'
for Late-Day Flow (V1: move >= 0.50 ATR instead of 0.40; lower drawdown, less money in both periods) on the
bootstrapped funded bench, with the current plan (VB 2 / 1 + ES MOC 2 MES). V1 = the MultiCharts LDF trades on the days
whose 8:30 -> 14:00 move was >= 0.50 x ATR15 (our daily ATR), the rest unchanged.
Note: 0.50 is inside the threshold range already tried when LDF was built (0.3-0.5), and the variant was picked after its
holdout, so this is a sizing / risk question for the bench, not a new edge.
  python3 analysis/antigravity_phase2_bench.py [SCRATCH_DIR]
Result (2026-10-17): a wash. 2-year payouts +$67 / +$70, blown -0.5 to -0.6 pt, beats the plan in 50.4% of paired
histories (noise); at 3 MNQ +$0-31. Keep LDF as is.
"""
import sys, pickle; sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import funded_bootstrap as FB

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    lab = FB.add_moc_mes(FB.plan_lab(SP), SP)
    g = lab.g; tr = lab.tr
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    mv = cf[tr * 1440 + jof(1400)] - cf[tr * 1440 + jof(830)]
    atr = g.daily_atr(15)[tr]
    big = np.abs(mv) >= 0.50 * atr
    traded = lab.C["LDF_MC"] != 0
    print(f"LDF trade days {traded.sum()}, of which move >= 0.50 ATR: {(traded & big).sum()}")
    for nm, m in (("kept (>= 0.50)", traded & big), ("dropped (0.40-0.50)", traded & ~big)):
        print(f"   {nm:<22} n={m.sum():4d} avg {lab.C['LDF_MC'][m].mean():7.2f} per lab unit, sum {lab.C['LDF_MC'][m].sum():9.1f}")
    lab.W["LDF_V1"] = lab.W["LDF_MC"] * big[:, None]; lab.C["LDF_V1"] = lab.C["LDF_MC"] * big
    v1 = {k: v for k, v in CUR.items() if k != "LDF_MC"}
    plans = {"current (VB 2/1 + MOC 2, LDF 2)": CUR, "LDF V1 2 MNQ": {**v1, "LDF_V1": 2}, "LDF V1 3 MNQ": {**v1, "LDF_V1": 3}}
    B = FB.Boot(lab)
    for seed in (1, 2):
        df, s, _ = B.compare(plans, n=1000, L=20, seed=seed); print(f"\nseed {seed}, 1,000 paired histories, L 20:\n{s}")
