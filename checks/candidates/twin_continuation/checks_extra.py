"""Checker's extra trap checks on trades_replica.csv: gap fills, rolls, holds, concentration, per-trade placebo."""
import sys, os, pickle
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "analysis"))
import grid24  # noqa

g = pickle.load(open(os.path.join(HERE, "..", "..", "..", "scratch_data", "g24.pkl"), "rb"))
B = pd.read_csv(os.path.join(HERE, "trades_replica.csv"))
B["y"] = B.date.str[:4].astype(int); B["pct"] = B.pts / B.entry * 100
t = lambda x: x.mean() / x.std() * np.sqrt(len(x))

bo = B[B.setup == "BO"]
gapf = bo[(bo.entry - bo.level).abs() > 1e-9]
print(f"BO stop entries filled at a gapped open: {len(gapf)}/{len(bo)}, their net ${gapf.net.sum():,.0f}, mean slip vs level {((gapf.entry-gapf.level)*gapf.side).mean():.2f} pts")
on = B[B.entry_date != B.date]
print(f"trades exiting on a later calendar date: {len(on)} (BO {sum(on.setup=='BO')}), net ${on.net.sum():,.0f}")
cr = B[(pd.to_datetime(B.date) - pd.to_datetime(B.entry_date)).dt.days >= 1]
held = B[(pd.to_datetime(B.date) - pd.to_datetime(B.entry_date)).dt.days >= 1]
# positions held across a 16:00-17:00 session break
def crosses_break(r):
    d0, d1 = int(r.entry_date.replace("-", "")), int(r.date.replace("-", ""))
    if d0 == d1: return r.entry_time_ct <= 1600 < r.exit_time_ct if False else False
    return not (r.entry_time_ct > 1600)  # entered before 16:00 on an earlier date
x = B[B.apply(crosses_break, axis=1)]
print(f"trades held across a session break: {len(x)}, net ${x.net.sum():,.0f}")
print(x[["entry_date", "entry_time_ct", "date", "exit_time_ct", "setup", "side", "net"]].to_string())

# roll windows: weekday 17:0x gaps >= 0.7% in roll months (unadjusted continuous) + intraday splices
c = g.c.ravel(); o = g.o.ravel(); idx = np.where(np.isfinite(c))[0]
rel = (o[idx[1:]] - c[idx[:-1]]) / c[idx[:-1]]
dd = g.dates[idx[1:] // 1440]; mm = dd // 100 % 100
roll = sorted(set(dd[(np.abs(rel) > 0.007) & np.isin(mm, [3, 6, 9, 12]) & (dd % 100 >= 7) & (dd % 100 <= 20)]))
roll_ts = pd.to_datetime(pd.Series(roll).astype(str))
ed = pd.to_datetime(B.entry_date)
near = ed.apply(lambda d: ((d - roll_ts).dt.days.between(0, 4)).any())
print(f"roll-like gap dates found: {len(roll)}; trades entered within 4 days after: {near.sum()}, "
      f"mean ${B[near].net.mean():.0f} vs other ${B[~near].net.mean():.0f}")
for d in (20240618, 20241216):
    print(d, B[B.entry_date == pd.to_datetime(str(d)).strftime('%Y-%m-%d')][["entry_time_ct", "exit_time_ct", "setup", "net"]].values.tolist())

# concentration
s = B.net.sort_values(ascending=False)
print(f"top 1% trades = {s[:len(s)//100].sum()/s.sum():.0%} of $; top 5% = {s[:len(s)//20].sum()/s.sum():.0%}")
print(B.sort_values("net", ascending=False).head(8)[["entry_date", "setup", "side", "net", "pct"]].to_string())
sp = B.pct.sort_values(ascending=False)
print(f"% of price: total {sp.sum():.1f}%, without best 5% {sp[len(sp)//20:].sum():.1f}%, t {t(B.pct):.2f}")
print("by year, % of price summed:", B.groupby("y").pct.sum().round(1).to_dict())
for s_ in ("BO", "MO"):
    for sd in (1, -1):
        z = B[(B.setup == s_) & (B.side == sd)]
        print(f"{s_} {sd:+d}: n {len(z)}, win {np.mean(z.net>0):.0%}, %/trade {z.pct.mean():.3f} (t {t(z.pct):.2f}), "
              f"18-22 {z[z.y<2023].pct.mean():.3f}, 23+ {z[z.y>=2023].pct.mean():.3f}")

# per-trade random-side placebo (same entry bar; MO: 75-pt stop + 14:51 exit; BO: mirrored stop & target, 15:45 exit)
H = g.h.ravel(); L = g.l.ravel(); O = o; C = c
row = {d: i for i, d in enumerate(g.dates)}
def flat_i(dstr, hhmm): return row[int(dstr.replace("-", ""))] * 1440 + (hhmm // 100) * 60 + hhmm % 100
def sim(r, side):
    i0 = flat_i(r.entry_date, int(r.entry_time_ct)); ep = r.entry
    sd = abs(r.entry - r.stop); stop = ep - side * sd
    tgt = ep + side * abs(r.tgt - r.entry) if r.setup == "BO" else None
    k = i0 + 1
    while True:
        if not np.isfinite(C[k]): k += 1; continue
        hh = (k % 1440) // 60 * 100 + (k % 1440) % 60
        if r.setup == "MO" and hh == 1451: return (O[k] - ep) * side * 20 - 17.25
        if side == 1:
            if tgt is not None and O[k] >= tgt: return (O[k] - ep) * 20 - 7.25 - 5
            if O[k] <= stop: return (O[k] - ep) * 20 - 17.25
            if L[k] <= stop: return (stop - ep) * 20 - 17.25
            if tgt is not None and H[k] >= tgt: return (tgt - ep) * 20 - 12.25
        else:
            if tgt is not None and O[k] <= tgt: return (ep - O[k]) * 20 - 12.25
            if O[k] >= stop: return (ep - O[k]) * 20 - 17.25
            if H[k] >= stop: return (ep - stop) * 20 - 17.25
            if tgt is not None and L[k] <= tgt: return (ep - tgt) * 20 - 12.25
        if r.setup == "BO" and 1545 <= hh <= 1600: return (C[k] - ep) * side * 20 - 17.25
        k += 1
B["net_same"] = [sim(r, r.side) for r in B.itertuples()]
print(f"per-trade re-sim with own side: corr with replica {np.corrcoef(B.net, B.net_same)[0,1]:.4f}, mean ${B.net_same.mean():.1f} vs ${B.net.mean():.1f}")
rng = np.random.default_rng(7); runs = []
flip = {}
for rr in B.itertuples():
    flip[rr.Index] = (sim(rr, 1), sim(rr, -1))
P = []
for k in range(200):
    sides = rng.choice([1, -1], len(B))
    v = np.array([flip[i][0] if s == 1 else flip[i][1] for i, s in zip(B.index, sides)])
    runs.append(v.mean())
    if k < 10: P += [(k, x) for x in v]
runs = np.array(runs)
print(f"random-side placebo (200 runs): mean ${runs.mean():.1f}, p95 ${np.percentile(runs,95):.1f}, max ${runs.max():.1f}; real ${B.net.mean():.1f}; share>=real {np.mean(runs>=B.net.mean()):.3f}")
for s_ in ("BO", "MO"):
    m = (B.setup == s_).to_numpy()
    rs = [np.mean([flip[i][0] if s == 1 else flip[i][1] for i, s in zip(B.index[m], rng.choice([1, -1], m.sum()))]) for _ in range(200)]
    print(f"  {s_}: placebo mean ${np.mean(rs):.1f}, p95 ${np.percentile(rs,95):.1f}; real ${B.net[m].mean():.1f}")
# always-long / always-short at the same entries (direction value of the signal)
for s_ in ("BO", "MO"):
    m = B.setup == s_
    al = np.mean([flip[i][0] for i in B.index[m]]); as_ = np.mean([flip[i][1] for i in B.index[m]])
    print(f"  {s_}: same entries always long ${al:.1f}, always short ${as_:.1f}")
os.makedirs(os.path.join(HERE, "..", "twin_continuation_replica"), exist_ok=True)
pd.DataFrame(P, columns=["run", "net"]).to_csv(os.path.join(HERE, "..", "twin_continuation_replica", "placebo.csv"), index=False)
