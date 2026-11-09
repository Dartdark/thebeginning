"""Vault Break vs Dual Thrust in the 150K evaluation, with recent conditions in focus (user 2026-11-09: 'VB isn't doing well in current
market conditions even though the pass rate doesn't say so; might be worth switching to DT'). PRE-REGISTERED (header committed before the
run; 4 swap variants). Part A: trades per year and $ a trade by year, VB (MultiCharts VB v1) vs Dual Thrust v4 (rebuild = MultiCharts list).
Part B: 150K evaluation pass rate (set + Twin 2 MNQ; VB 20 now) by start year, for VB 20 / VB 15 + DT 2 / VB 10 + DT 4 / VB 5 + DT 6 /
VB 0 + DT 8 (DT sizes keep roughly the same total risk); the recent window 2025-01 -> 2026-09 shown on its own with a paired band.
  tools/run_stamped.sh analysis/vb_vs_dt_eval.py > analysis/outputs/vb_vs_dt_eval_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from plan_150k_test import evaluation, R150
import dual_thrust_bench as DTB
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(); g, trr, D, dts, yr = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"], ctx["yr"]; ts = pd.DatetimeIndex(g.ts)
    vb = with_slippage(load_mc(g, REPORTS["VB"][0])); dt = DTB.dt_trades(g)
    print("\nA. Trades per year and $ a trade per NQ:")
    for nm, t in (("Vault Break", vb), ("Dual Thrust", dt)):
        t = t.assign(date=ts[t.day.values], net=(t.exit - t.entry) * t.side * 20 - 7.25); t = t[t.date >= "2018-01-01"]; y = t.groupby(t.date.dt.year)
        print(f"   {nm:<12} trades/yr {dict(y.size())} | $/trade {dict(y.net.mean().round(0).astype(int))}")
    P = {}
    for nm, t in (("VB", vb), ("DT", dt)): w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    V = {"VB 20 (now)": (0, 0), "VB 15 + DT 2": (-5, 2), "VB 10 + DT 4": (-10, 4), "VB 5 + DT 6": (-15, 6), "VB 0 + DT 8": (-20, 8)}
    ok = (yr >= 2018) & (dts <= pd.Timestamp("2026-09-01")); res = {}
    for nm, (dv, dd) in V.items():
        W = ctx["Wb"] + dv * P["VB"][0] + dd * P["DT"][0]; R = ctx["Rb"] + dv * P["VB"][1] + dd * P["DT"][1]
        o = np.array([(lambda z: z[0] if z else "")(evaluation(W, R, s, D, R150)) for s in range(D)]); res[nm] = o
    print("\nB. 150K evaluation pass rate by start year (set + Twin 2):")
    for nm, o in res.items():
        print(f"   {nm:<14} all {(o == 'pass')[ok & (o != '')].mean():5.1%} | " + " ".join(f"{y}: {(o == 'pass')[ok & (yr == y) & (o != '')].mean():4.0%}" for y in range(2018, 2027)), flush=True)
    rec = ok & (dts >= pd.Timestamp("2025-01-01"))
    for nm, o in res.items():
        if nm.startswith("VB 20"): continue
        d = ((o == "pass").astype(float) - (res["VB 20 (now)"] == "pass").astype(float))[rec & (o != "")]
        rng = np.random.default_rng(1); nb = int(np.ceil(len(d) / 60)); st = rng.integers(0, len(d), (2000, nb)); mm = d[((st[:, :, None] + np.arange(60)) % len(d)).reshape(2000, -1)[:, :len(d)]].mean(axis=1)
        print(f"   2025-26 starts: {nm:<14} vs VB 20: {d.mean():+.1%} (band {np.percentile(mm, 5):+.1%} / {np.percentile(mm, 95):+.1%}, {len(d)} starts)")
