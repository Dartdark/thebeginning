"""MultiCharts confirmation of Monday Long (report '... 5 Minutes NQ Monday Longs.xlsx'): trade-by-trade
match with the Python test, standard metrics, bootstrap, and the funded bench (cushion sizing).
Expects the pickled funded lab with MON (scratch lab_mon.pkl from monday_long_test.py)."""
import sys, pickle, warnings, glob; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
import metrics as M, resampling as R
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
lab = pickle.load(open(SP + "lab_mon.pkl", "rb")); g = lab.g
path = glob.glob("*Monday Longs*.xlsx")[0]
raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
mc = load_mc(g, path); atr = g.daily_atr(15)
print("MC rows:", len(mc), "columns:", list(mc.columns))
mc["date"] = pd.DatetimeIndex(g.ts[mc.day.values])
x = mc.copy(); x["net_mc"] = (x.exit - x.entry) * x.side * 20 - 7.25 - 2 * 5   # per NQ, $7.25 + 1 tick per fill
y = x[x.date.dt.year >= 2018]
pf = lambda s: s[s > 0].sum() / -s[s < 0].sum()
print(f"MC (per NQ, +1 tick per fill): n={len(y)} win {np.mean(y.net_mc>0):.0%} avg ${y.net_mc.mean():.0f} PF {pf(y.net_mc):.2f}"
      f" | weekdays {y.date.dt.dayofweek.value_counts().to_dict()} | first {y.date.min().date()} last {y.date.max().date()}")
print("  by year avg:", y.groupby(y.date.dt.year).net_mc.mean().round(0).astype(int).to_dict())
# Python test trades
sys.argv = ["x"]; src = open("analysis/monday_long_test.py").read(); exec(src.split("if __name__")[0])
py = trades(0.5, 900); py = py[g.last_j[py.day.values] >= 900]
mm = py.merge(y[["day", "entry", "exit", "net_mc"]], on="day", how="outer", suffixes=("_py", "_mc"), indicator=True)
print("match:", mm._merge.value_counts().to_dict())
both = mm[mm._merge == "both"]
print(f"  on common days: Python avg ${both.net.mean():.0f}, MC avg ${both.net_mc.mean():.0f}, corr {np.corrcoef(both.net, both.net_mc)[0,1]:.3f}; "
      f"|diff| > $200 on {np.mean(abs(both.net-both.net_mc)>200):.0%}")
print("  only in Python:", mm[mm._merge=="left_only"].date.dt.date.tolist()[:12])
print("  only in MC:", sorted(pd.DatetimeIndex(g.ts[mm[mm._merge=='right_only'].day.astype(int)]).date.tolist())[:12])
# funded lab with the MC trades
mcs = y.reset_index(drop=True)
stop = np.full(g.D, np.nan); stop[mcs.day.values] = 0.5 * atr[mcs.day.values]; stop = pd.Series(stop).ffill().bfill().to_numpy()
lab.add("MON_MC", mcs, stop_pts=stop)
dates = pd.DatetimeIndex(g.ts[lab.tr]); m = dates.year >= 2018
d = pd.Series(lab.daily("MON_MC"), index=dates)[m]
print("\nStandard metrics per NQ (MC trades, with slippage):")
print(M.table({"MC Monday Long 2018-26": (d, None), "MC Monday Long 2023-26": (d[d.index.year >= 2023], None),
               "Python 2018-26": (pd.Series(lab.daily("MON"), index=dates)[m], None)}))
print("corr with set:", lab.corr(["MON_MC", "VB", "ONB_ML2_MC", "OND_MC", "EOS"]).round(2).loc["MON_MC"].to_dict())
B, P = R.report({"MC 2023-26": d[d.index.year >= 2023], "MC 2018-26": d}, n=5000)
print("\nBootstrap:"); print(B)
base = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "OND_MC": ("risk", 500), "EOS": ("risk", 700)}
plans = {"Funded set": base,
         "Monday $300 replaces OND": {k: v for k, v in base.items() if k != "OND_MC"} | {"MON_MC": ("risk", 300)},
         "Monday $500 replaces OND": {k: v for k, v in base.items() if k != "OND_MC"} | {"MON_MC": ("risk", 500)},
         "+ Monday $300": {**base, "MON_MC": ("risk", 300)}}
print("\nFunded bench, cushion sizing:")
for nm, p in plans.items():
    a = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=2000.0); b = lab.score(p, 500, fmin=0.5, fmax=1.0, ref=2000.0)
    print(f"  {nm:<26} 1y ${a['expected']:,.0f} (2023+ ${a['s2023_on']:,.0f}) blown {a['blown']:.0%} | 2y ${b['expected']:,.0f} blown {b['blown']:.0%} | worst yr ${a['worst_year']:,.0f}")
pickle.dump(lab, open(SP + "lab_mon.pkl", "wb"))
