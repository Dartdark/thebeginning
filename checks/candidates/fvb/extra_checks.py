"""Checker extras for FVB: stop gap-through, slippage sensitivity, cap at 3R, random-time placebos, roll-day count.
  python3 checks/candidates/fvb/extra_checks.py
"""
import sys, os, pickle
sys.path.insert(0, "/home/user/thebeginning/analysis"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from replica import walk, rt, RTH0, RTH1, PM0, PM1, ENTRY_END, PV, COST, TICK

os.chdir("/home/user/thebeginning")
HERE = "checks/candidates/fvb"
T = pd.read_csv(f"{HERE}/trades_replica.csv")
g = pickle.load(open("scratch_data/g24.pkl", "rb"))
O, H, L, C = g.o, g.h, g.l, g.c


def tstat(x): x = np.asarray(x); return x.mean() / x.std(ddof=1) * np.sqrt(len(x))


# 1. stop gap-through: bar opening beyond the stop
st = T[T.kind == "stop"]
op = O[st.row.values, st.j1.values]
gt = np.where(st.side == 1, op < st.stop, op > st.stop)
fill = np.where(gt, op, st.stop)
extra = np.where(gt, (fill - st.stop) * st.side, 0) * PV
print(f"stops {len(st)}, gap-through {gt.sum()} ({gt.mean():.1%}), extra cost total ${extra.sum():,.0f} (avg ${extra[gt].mean() if gt.any() else 0:.0f} on those)")
print(f"stops on the entry bar: {(st.j0 == st.j1).mean():.1%}")
net2 = T.net.copy(); net2[T.kind == "stop"] += extra
print(f"net with gap-through fills ${net2.sum():,.0f} mean ${net2.mean():.1f} t {tstat(net2):.2f}")
for k in (2, 3, 4):
    n3 = T.net - (k - 1) * 5 * 2
    print(f"slippage {k} ticks per fill: mean ${n3.mean():.1f} t {tstat(n3):.2f}")
# 2. cap winners at 3R / 5R
for cap in (3, 5, 10):
    capped = np.minimum(T.pts, cap * T.sd) * PV - COST
    print(f"cap at {cap}R: mean ${capped.mean():.1f} total ${capped.sum():,.0f}")
r = T.pts / T.sd; s = np.sort(T.net.values)[::-1]
print(f"top 1% trades ${s[:len(s)//100].sum():,.0f}, top 5% ${s[:len(s)//20].sum():,.0f}, total ${s.sum():,.0f}; win {np.mean(T.net>0):.1%}; max R {r.max():.1f}")
print("R per trade (net/(sd*PV)) mean", (T.net / (T.sd * PV)).mean().round(3))
# by year, sides
T["y"] = T.date.str[:4]
print(T.groupby(["y"]).net.agg(["count", "mean", "sum"]).round(0).T.to_string())
print(T.groupby(["side"]).net.agg(["count", "mean", "sum"]).round(0).to_string())
print(T.groupby(["level"]).net.agg(["count", "mean", "sum"]).round(0).to_string())
print(T.groupby(["n"]).net.agg(["count", "mean", "sum"]).round(0).to_string())
# stop size in $
T["risk"] = T.sd * PV
print("stop $ by year (median):", T.groupby("y").risk.median().round(0).to_dict())

# 3. random-time placebo: same days, same number of trades per day, entry after a random bar in the 08:31-10:30 window,
#    side = random or the real side; same stop width and exit rule (one trade per slot, no re-entry logic)
rng = np.random.default_rng(11)
first = T.drop_duplicates("row")
days = []
for _, t in first.iterrows():
    r = int(t.row); js = np.where(~np.isnan(C[r, RTH0:RTH1 + 1]))[0] + RTH0
    days.append((r, js, O[r, js], H[r, js], L[r, js], C[r, js], t.sd, int(t.side)))
res_rand, res_real = [], []
for run in range(200):
    a, b = [], []
    for r, js, o, h, l, c, sd, side in days:
        cand = np.where(js < ENTRY_END)[0]; cand = cand[cand < len(js) - 1]
        i = rng.choice(cand)
        for dd, lst in ((rng.choice([-1, 1]), a), (side, b)):
            ep, xp, sp, kind, xi = walk(o, h, l, c, js, i, dd, sd); lst.append((xp - ep) * dd * PV - COST)
    res_rand.append(np.mean(a)); res_real.append(np.mean(b))
real_first = first.net.mean()
print(f"first-trade-of-day real mean ${real_first:.1f} (n {len(first)})")
print(f"random time + random side: mean ${np.mean(res_rand):.1f}, p95 ${np.percentile(res_rand,95):.1f}, share >= real {np.mean(np.array(res_rand)>=real_first):.3f}")
print(f"random time + real side:   mean ${np.mean(res_real):.1f}, p95 ${np.percentile(res_real,95):.1f}, share >= real {np.mean(np.array(res_real)>=real_first):.3f}")
pd.DataFrame(dict(run=np.repeat(np.arange(200), 1), net=res_rand)).to_csv(f"{HERE}/placebo_randomtime_means.csv", index=False)
