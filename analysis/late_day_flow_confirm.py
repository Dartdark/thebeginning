"""MultiCharts confirmation of Late-Day Flow (report '... 5 Minutes Late Day Flow.xlsx'): trade-by-trade
match with the Python test, standard metrics whole / longs / shorts, bootstrap + permutation on 2023+,
and the funded bench (cushion sizing). Expects the funded lab with MON_MC (scratch lab_mon.pkl)."""
import sys, pickle, warnings, glob; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
import metrics as M, resampling as R
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
lab = pickle.load(open(SP + "lab_mon.pkl", "rb")); g = lab.g
path = glob.glob("*Late Day Flow*.xlsx")[0]
mc = load_mc(g, path); atr = g.daily_atr(15)
mc["date"] = pd.DatetimeIndex(g.ts[mc.day.values])
mc["net_mc"] = (mc.exit - mc.entry) * mc.side * 20 - 7.25 - 2 * 5          # +1 tick per market/stop fill
y = mc[mc.date.dt.year >= 2018].reset_index(drop=True)
pf = lambda s: s[s > 0].sum() / -s[s < 0].sum()
x = y.net_mc; yr = y.date.dt.year
print(f"MC per NQ (+1 tick per fill): n={len(y)} win {np.mean(x>0):.0%} avg ${x.mean():.0f} PF {pf(x):.2f} "
      f"t={x.mean()/x.std()*np.sqrt(len(x)):.1f} | longs n={(y.side>0).sum()} ${x[y.side>0].mean():.0f} PF {pf(x[y.side>0]):.2f}"
      f" | shorts n={(y.side<0).sum()} ${x[y.side<0].mean():.0f} PF {pf(x[y.side<0]):.2f}")
print("  by year avg:", x.groupby(yr).mean().round(0).astype(int).to_dict(), "| 2018-22", round(x[yr<=2022].mean()), "2023+", round(x[yr>=2023].mean()))
sys.argv = ["x"]; src = open("analysis/letf_rebalance_test.py").read(); exec(src.split("if __name__")[0])
py = trades(g, 0.4, 0.25, j_exit=870)
mm = py.merge(y[["day", "side", "entry", "exit", "net_mc"]], on="day", how="outer", suffixes=("_py", "_mc"), indicator=True)
print("match:", mm._merge.value_counts().to_dict())
b = mm[mm._merge == "both"]
print(f"  common days: same side {np.mean(b.side_py==b.side_mc):.1%}, entry within 1 tick {np.mean(abs(b.entry_py-b.entry_mc)<=0.26):.1%}, "
      f"Python avg ${b.net.mean():.0f} vs MC ${b.net_mc.mean():.0f}, corr {np.corrcoef(b.net,b.net_mc)[0,1]:.3f}")
lo = pd.DatetimeIndex(g.ts[mm[mm._merge=='left_only'].day.astype(int)]); ro = pd.DatetimeIndex(g.ts[mm[mm._merge=='right_only'].day.astype(int)])
print("  only in Python:", len(lo), [d.date() for d in lo[:8]]); print("  only in MC:", len(ro), [d.date() for d in ro[:8]])
stop = np.full(g.D, np.nan); stop[y.day.values] = 0.25 * atr[y.day.values]; stop = pd.Series(stop).ffill().bfill().to_numpy()
lab.add("LDF_MC", y, stop_pts=stop)
lab.add("LDF_MC_L", y[y.side > 0].reset_index(drop=True), stop_pts=stop)
lab.add("LDF_MC_S", y[y.side < 0].reset_index(drop=True), stop_pts=stop)
dates = pd.DatetimeIndex(g.ts[lab.tr]); m = dates.year >= 2018
D = {k: pd.Series(lab.daily(k), index=dates)[m] for k in ("LDF_MC", "LDF_MC_L", "LDF_MC_S")}
rows = {}
for k, nm in (("LDF_MC", "all"), ("LDF_MC_L", "longs"), ("LDF_MC_S", "shorts")):
    rows[f"{nm} 2018-26"] = (D[k], None); rows[f"{nm} 2023-26"] = (D[k][D[k].index.year >= 2023], None)
print("\nStandard metrics per NQ (MC trades, with slippage):"); print(M.table(rows))
print("corr with set:", lab.corr(["LDF_MC", "VB", "ONB_ML2_MC", "MON_MC", "EOS"]).round(2).loc["LDF_MC"].to_dict())
B, P = R.report({k + " 2023-26": v[v.index.year >= 2023] for k, v in (("all", D["LDF_MC"]), ("longs", D["LDF_MC_L"]), ("shorts", D["LDF_MC_S"]))}, n=5000)
print("\nBootstrap, 2023-26:"); print(B); print("\nPermutation, 2023-26:"); print(P)
base = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700)}
print("\nFunded bench, cushion sizing:")
for nm, p in (("current plan", base), ("+ Late-Day Flow 1 MNQ", {**base, "LDF_MC": 1}), ("+ Late-Day Flow 2 MNQ", {**base, "LDF_MC": 2}),
              ("+ Late-Day Flow 3 MNQ", {**base, "LDF_MC": 3})):
    a = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=2000.0); bb = lab.score(p, 500, fmin=0.5, fmax=1.0, ref=2000.0)
    print(f"  {nm:<24} 1y ${a['expected']:,.0f} (2018-22 ${a['s2018_22']:,.0f}, 2023+ ${a['s2023_on']:,.0f}) blown {a['blown']:.0%} | 2y ${bb['expected']:,.0f} blown {bb['blown']:.0%} | 1st payout {a['days_to_1st']:.0f}d")
pickle.dump(lab, open(SP + "lab_mon.pkl", "wb"))
