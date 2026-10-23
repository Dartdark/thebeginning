"""Placebos for FC 2B (checker). Writes placebo.csv (run, net), 2018+:
  runs 0-99     random side on the real signal days (same exits)
  runs 100-299  random days (same count per year) drawn from the every-day OR-direction trades (ZMin = -inf)
  python3 checks/candidates/fc_2b/placebo_runs.py"""
import sys, numpy as np, pandas as pd
sys.argv = [sys.argv[0]]; sys.path.insert(0, "checks/candidates/fc_2b")
import replica as R
df = R.load(); rows = []
for s in range(100):
    R.RS = np.random.default_rng(s); t, _ = R.run(df); t = t[t.date >= "2018-01-01"]
    rows += [(s, v) for v in t.net]
R.RS = None; real, _ = R.run(df); real = real[real.date >= "2018-01-01"]
R.P["ZMin"] = -1e9; alld, _ = R.run(df); alld = alld[alld.date >= "2018-01-01"]
alld.to_csv("checks/candidates/fc_2b/replica_everyday_trades.csv", index=False)
rng = np.random.default_rng(7); cnt = real.groupby(real.date.dt.year).size()
for s in range(100, 300):
    pick = pd.concat([alld[alld.date.dt.year == y].sample(n, random_state=int(rng.integers(1e9))) for y, n in cnt.items()])
    rows += [(s, v) for v in pick.net]
P = pd.DataFrame(rows, columns=["run", "net"]).round(2); P.to_csv("checks/candidates/fc_2b/placebo.csv", index=False)
pm = P.groupby("run").net.mean()
print(f"real mean {real.net.mean():.1f}; random side: mean {pm[pm.index<100].mean():.1f}, 95th {pm[pm.index<100].quantile(.95):.1f}, share>=real {np.mean(pm[pm.index<100]>=real.net.mean()):.3f}")
print(f"random days: mean {pm[pm.index>=100].mean():.1f}, 95th {pm[pm.index>=100].quantile(.95):.1f}, share>=real {np.mean(pm[pm.index>=100]>=real.net.mean()):.3f}")
