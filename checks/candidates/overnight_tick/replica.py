"""Checker replica of overnight_tick, built from spec.md only.
  python3 checks/candidates/overnight_tick/replica.py
Writes replica_nights.csv (every regular session with its flags) and trades_replica.csv in this folder,
and ../overnight_tick_replica/ (trades.csv + meta.json + placebo.csv) for the checker.
"""
import sys, os, glob, pickle, json, warnings; warnings.filterwarnings("ignore")
ROOT = "/home/user/thebeginning"; sys.path.insert(0, ROOT + "/analysis"); os.chdir(ROOT)
import numpy as np, pandas as pd
import grid24
from grid24 import jof
from overnight_round import roll_minutes

HERE = ROOT + "/checks/candidates/overnight_tick/"
PV, COST = 20.0, 7.25 + 2 * 5.0
VIXLEN = int(os.environ.get("VIXLEN", 25))

g = pickle.load(open("scratch_data/g24.pkl", "rb"))
O, C = g.o, g.c
roll = roll_minutes(g, "NQ")

# ---- order flow (ET, bar-close stamps) ----
of = pd.concat([pd.read_csv(f, usecols=["date", "time", "close", "upvol", "downvol"]) for f in sorted(glob.glob("data/OF_1min_*.csv"))])
of = of.drop_duplicates(["date", "time"])
w = of[(of.time >= 1516) & (of.time <= 1615)]
agg = w.groupby("date")[["upvol", "downvol"]].sum()
rsv_of = ((agg.upvol - agg.downvol) / (agg.upvol + agg.downvol)).where((agg.upvol + agg.downvol) > 0)

# ---- VIX ----
vx = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE")["CLOSE"].astype(float)
vma = vx.rolling(VIXLEN).mean()
hi = (vx > vma)

rows = []
tr = g.trading
for k, r in enumerate(tr):
    d = g.dates[r]
    if d < 20171201: continue
    rth_c = C[r, jof(831):jof(1500) + 1]; rth_o = O[r, jof(831):jof(1500) + 1]
    have = np.flatnonzero(~np.isnan(rth_c))
    if len(have) == 0: continue
    op, cl = rth_o[have[0]], rth_c[have[-1]]
    last_hhmm = 831 + 0  # placeholder
    lastj = jof(831) + have[-1]; last_hhmm = (lastj // 60) * 100 + lastj % 60
    early = last_hhmm < 1400
    down = cl < op
    # next evening session: first row from r up to (not incl.) next trading row with a 17:06 bar
    nxt = tr[k + 1] if k + 1 < len(tr) else g.D
    er = None
    for rr in range(r, nxt):
        if not np.isnan(O[rr, jof(1706)]): er = rr; break
    ent = ex = np.nan; isroll = False
    if er is not None and er + 1 < g.D:
        ent = O[er, jof(1706)]; ex = O[er + 1, jof(301)]
        a, b = er * 1440 + jof(1706), (er + 1) * 1440 + jof(301)
        isroll = bool(((roll > a) & (roll <= b)).any())
    ts = pd.Timestamp(str(d))
    rv = rsv_of.get(d, np.nan)
    vc = vx.get(ts, np.nan); vm = vma.get(ts, np.nan)
    h = bool(vc > vm) if not (np.isnan(vc) or np.isnan(vm)) else None
    # bar-direction RSV proxy from the NQ grid (14:16-15:15 CT): up-bar volume vs down-bar volume
    cc = C[r, jof(1416):jof(1515) + 1]; oo = O[r, jof(1416):jof(1515) + 1]; vv = g.v[r, jof(1416):jof(1515) + 1]
    m = ~np.isnan(cc); up = np.nansum(vv[m] * (cc[m] > oo[m])); dn = np.nansum(vv[m] * (cc[m] < oo[m]))
    rsv_bar = (up - dn) / (up + dn) if up + dn > 0 else np.nan
    exit_date = pd.Timestamp(str(g.dates[er + 1])) if er is not None and er + 1 < g.D else pd.NaT
    rows.append(dict(sess=ts, date=exit_date, down=down, early=early, roll=isroll, rsv=rv, rsv_bar=rsv_bar,
                     vix=vc, vma=vm, hi=h, ent=ent, ex=ex, net=(ex - ent) * PV - COST, entry_dow=None if er is None else pd.Timestamp(str(g.dates[er])).dayofweek,
                     vix_date_ok=not np.isnan(vc)))
N = pd.DataFrame(rows)
N["cell_ok"] = N.hi.notna() & N.rsv.notna()
N["cell"] = np.where(N.rsv < 0, np.where(N.hi == True, "neg_hi", "neg_lo"), np.where(N.hi == True, "pos_hi", "pos_lo"))
N.loc[~N.cell_ok, "cell"] = "na"
N["base"] = N.down & ~N.early & ~N.roll & N.ent.notna() & N.ex.notna() & (N.date >= "2018-01-01")
N["tk"] = N.base & N.cell.isin(["neg_hi", "pos_lo"])
N.to_csv(HERE + f"replica_nights{'' if VIXLEN == 25 else VIXLEN}.csv", index=False)
T = N[N["tk"]][["date", "net"]].assign(side=1)[["date", "side", "net"]]
T["date"] = T.date.dt.strftime("%Y-%m-%d")
if VIXLEN == 25:
    T.to_csv(HERE + "trades_replica.csv", index=False)
    od = ROOT + "/checks/candidates/overnight_tick_replica/"; os.makedirs(od, exist_ok=True)
    T.to_csv(od + "trades.csv", index=False)
    json.dump(json.load(open(HERE + "meta.json")), open(od + "meta.json", "w"))
    # placebo: VIX regime shuffled across base nights (with RSV), 20 runs
    B = N[N.base & N.cell_ok].copy(); rng = np.random.default_rng(7); P = []
    for i in range(20):
        hs = rng.permutation(B.hi.to_numpy())
        tk = ((B.rsv < 0) & hs) | ((B.rsv >= 0) & ~hs)
        P.append(pd.DataFrame(dict(run=i, net=B.net[tk.to_numpy()].to_numpy())))
    pd.concat(P).to_csv(od + "placebo.csv", index=False)
print(f"VIXLEN {VIXLEN}: trades {len(T)}, net {T.net.sum():.0f}, mean {T.net.mean():.1f}")
