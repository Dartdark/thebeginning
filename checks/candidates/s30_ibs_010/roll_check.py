"""Checker: P&L booked from contract-roll gaps on the raw continuous chart (rolls detected as the one-minute
jump in each roll window; 2020-01..2022-06 rolls are near-zero carry and not detected -> left in)."""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/thebeginning/analysis"); from grid24 import Grid24  # noqa
g = pickle.load(open("/home/user/thebeginning/scratch_data/g24.pkl", "rb"))
ROLLS = ["2018-03-09 03:33","2018-06-08 03:32","2018-09-14 03:32","2018-12-14 03:33","2019-03-08 03:33","2019-06-14 03:32",
 "2019-09-13 03:32","2019-12-13 03:32","2022-09-11 17:01","2022-12-11 17:01","2023-03-12 17:01","2023-06-11 17:01",
 "2023-09-10 17:01","2023-12-10 17:01","2024-03-10 17:01","2024-06-18 03:32","2024-09-15 17:01","2024-12-16 03:32",
 "2025-03-17 17:01","2025-06-16 17:01","2025-09-15 17:01","2025-12-15 17:01","2026-03-16 17:01","2026-06-15 17:01","2026-09-14 17:01"]
c = g.c.ravel(); o = g.o.ravel(); ts0 = pd.Timestamp(g.ts[0])
def at(t):
    k = int((t - ts0) / pd.Timedelta(minutes=1)); j = k - 1
    while np.isnan(c[j]): j -= 1
    while np.isnan(o[k]): k += 1
    return o[k] - c[j]
R = pd.DataFrame(dict(t=pd.to_datetime(ROLLS))); R["gap"] = [at(t) for t in R.t]
F = pd.read_csv("/home/user/thebeginning/checks/candidates/s30_ibs_010/fills.csv", parse_dates=["entry_time", "exit_time"])
T = pd.read_csv("/home/user/thebeginning/checks/candidates/s30_ibs_010/replica_trades_full.csv")
adj = np.zeros(len(F)); hit = []
for i, f in F.iterrows():
    for r in R.itertuples():
        if f.entry_time < r.t <= f.exit_time: adj[i] += r.gap * 20; hit.append((T.date[i], r.t.date(), r.gap))
print(R.to_string()); print("trades spanning a detected roll:", len(hit)); [print("  ", h) for h in hit]
T["net_rolladj"] = T.net - adj
T[["date", "side", "net_rolladj"]].rename(columns={"net_rolladj": "net"}).to_csv(
    "/home/user/thebeginning/checks/candidates/s30_ibs_010_replica/trades_rolladj.csv", index=False)
for lab, s in (("raw", T.net), ("roll-adj", T.net_rolladj)):
    for per, m in (("all", T.date >= "2018"), ("2023+", T.date >= "2023")):
        x = s[m]; print(f"{lab:9s} {per:6s} n {len(x)} total ${x.sum():,.0f} mean ${x.mean():,.0f} t {x.mean()/x.std()*np.sqrt(len(x)):.2f}")
