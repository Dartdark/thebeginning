"""Swing Target v3 with 2x size on the shorts (user 2026-11-08: 'what about just adding more size to the shorts'). PRE-REGISTERED (header
committed before the run; 1 variant, post hoc in origin from ingredient_ablation5's shorts $486 vs longs $168). Every trade kept: short
breaks 2 MNQ, long breaks 1 MNQ, vs both sides 1 MNQ and vs 2 MNQ on both sides (the 'more size of everything' control). Personal book
(SwingTarget column replaced by the rebuild), 1-year MC return / DD p95 by period, plus the median year, DD and capital at the 20% rule.
  tools/run_stamped.sh analysis/st_short_size_test.py > analysis/outputs/st_short_size_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from ingredient_ablation5 import swing
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); S = swing(g)
    dm = lambda w: ((S.net / 10 - 0.55) * w).groupby(S.date).sum()
    V = {"ST 1 / 1 (rebuild)": dm(np.ones(len(S))), "ST shorts 2 / longs 1": dm(np.where(S.side < 0, 2.0, 1.0)), "ST 2 / 2 (control)": dm(np.full(len(S), 2.0))}
    BB.personal(V, drop=("SwingTarget",))
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); Pp = Pp[[c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30")]]
    base = Pp.drop(columns="SwingTarget").sum(axis=1) + Pp.OvernightTick          # current plan: OT 2 MNQ
    print("\n   Current plan (OT 2 MNQ), 1-year MC:")
    for nm, s in V.items():
        x = base + s.reindex(Pp.index, fill_value=0.0); d = MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1)
        print(f"      {nm:<24} median year ${d['pnl_p50']:,.0f}  p5 ${d['pnl_p5']:,.0f}  DD p95 ${d['dd_p95']:,.0f}  ret/DD {d['pnl_p50'] / d['dd_p95']:.2f}  capital ${d['dd_p95'] / 0.2 / 1000:.1f}k")
