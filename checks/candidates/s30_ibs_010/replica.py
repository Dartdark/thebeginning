"""Checker replica of S30 IBS<0.10 from spec.md alone (NQ, 15-min, raw prices, 2018+)."""
import sys, pickle, json, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/thebeginning/analysis")
from grid24 import Grid24  # noqa (needed for unpickle)
ENTRY = float(sys.argv[1]) if len(sys.argv) > 1 else 0.10
EXIT = 0.80; BPV = 20; TICK = 0.25; COMM = 7.25
g = pickle.load(open("/home/user/thebeginning/scratch_data/g24.pkl", "rb"))
b = g.bars(15); per = b["c"].shape[1]
O, H, L, C = (b[k] for k in "ohlc")
stamps = b["j"] // 60 * 100 + b["j"] % 60
i0 = int(np.where(stamps == 845)[0][0]); i1 = int(np.where(stamps == 1500)[0][0])
fo = O.ravel(); has = ~np.isnan(fo)
pos = 0; ent = None; rows = []; fills = []; marks = []
dates = g.dates; ts = pd.DatetimeIndex(g.ts)
for r in range(g.D):
    if dates[r] < 20180101: continue
    sc = C[r, i0:i1 + 1]
    if np.isnan(sc).any(): continue          # wrong bar count -> no decision
    hi = np.nanmax(H[r, i0:i1 + 1]); lo = np.nanmin(L[r, i0:i1 + 1])
    if not hi > lo: continue
    ibs = (sc[-1] - lo) / (hi - lo)
    k = r * per + i1 + 1
    while k < len(fo) and not has[k]: k += 1
    if k >= len(fo): break
    px = fo[k]; t = ts[k // per] + pd.Timedelta(minutes=int(b["j"][k % per]))
    if pos == 0 and ibs < ENTRY:
        pos = 1; ent = (dates[r], t, px + TICK, ibs)
    elif pos == 1 and ibs > EXIT:
        xp = px - TICK
        net = (xp - ent[2]) * BPV - COMM   # repo convention: $7.25 per NQ round trip (grid.py, portfolio.py)
        rows.append(dict(date=pd.Timestamp(str(ent[0])).date(), side=1, net=round(net, 2), exit_date=pd.Timestamp(str(dates[r])).date(), entry_ibs=round(ent[3], 4)))
        fills.append(dict(entry_time=ent[1], exit_time=t, side=1, entry=ent[2] - TICK, exit=xp + TICK))
        pos = 0
T = pd.DataFrame(rows); F = pd.DataFrame(fills)
out = "/home/user/thebeginning/checks/candidates/s30_ibs_010/"
if ENTRY == 0.10:
    T.to_csv(out + "replica_trades_full.csv", index=False)
    F.to_csv(out + "fills.csv", index=False)
    if pos == 1: print("open position at end, entered", ent[0])
print(len(T), "trades, net", T.net.sum().round(2), "mean", T.net.mean().round(2))
