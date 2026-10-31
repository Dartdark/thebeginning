"""Price jumps -> next overnight / intraday return, NQ / ES (paper: Liu, Hou, Zhu & Chen, 'The Asymmetric Effect of Information
Shock on Overnight and Intraday Expected Returns: Evidence from Chinese A-share Stock Market', SSRN 4435622; user upload
2026-10-29). Paper (A-shares 2010-17, monthly cross-section): stocks with high jump returns earn higher next overnight returns
and lower intraday returns, driven by positive jumps (investors buy winners). Time-series version fixed before looking:
day-session jump test of Barndorff-Nielsen & Shephard / Huang & Tauchen on 5-min returns 08:30-15:00 CT (78 bars),
ratio z with tripower quarticity, jump day if z > 3.09 (alpha 0.999); sign = sign of the 08:30 -> 15:00 return. Outcomes:
next overnight (15:00 -> next 08:30) and next intraday (08:30 -> 15:00) per contract; monthly version: sum of the month's
jump returns vs next month. Roll weeks (days 8-17 of Mar / Jun / Sep / Dec) out. Costs $7.25 NQ / $5 ES + 1 tick a side.
python3 analysis/jump_overnight_test.py
"""
import glob, numpy as np, pandas as pd
Z999 = 3.0902  # standard normal 0.999 quantile
mu1 = np.sqrt(2 / np.pi)
from math import gamma, pi
mu43 = 2 ** (2 / 3) * gamma(7 / 6) / gamma(1 / 2)
def jump_z(r):
    M = len(r); a = np.abs(r)
    rv = (r ** 2).sum(); bv = mu1 ** -2 * M / (M - 1) * (a[1:] * a[:-1]).sum()
    tp = M * mu43 ** -3 * M / (M - 2) * ((a[2:] * a[1:-1] * a[:-2]) ** (4 / 3)).sum()
    z = ((rv - bv) / rv) / np.sqrt(((pi / 2) ** 2 + pi - 5) / M * max(1, tp / bv ** 2))
    return z
for sym, pv, cost in (("NQ", 20, 7.25 + 2 * 0.25 * 20), ("ES", 50, 5.0 + 2 * 0.25 * 50)):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"data/{sym}_1min_20*.csv")) if "_ON_" not in f])
    d = d[(d.time > 830) & (d.time <= 1500)]
    rows = []
    for dt, g in d.groupby("date"):
        if len(g) < 380: continue
        c = g.set_index("time").close; px = np.r_[g.open.iloc[0], c[c.index % 5 == 0].values]
        r = np.diff(np.log(px))
        if len(r) < 70: continue
        rows.append((dt, g.open.iloc[0], g.close.iloc[-1], jump_z(r)))
    x = pd.DataFrame(rows, columns=["date", "o", "c", "z"]); x.index = pd.to_datetime(x.date.astype(str)); x = x[x.index >= "2018-01-01"]
    x["ret"] = np.log(x.c / x.o); x["jump"] = x.z > Z999
    x["next_on"] = (x.o.shift(-1) - x.c) * pv; x["next_id"] = (x.c.shift(-1) - x.o.shift(-1)) * pv
    rw = x.index.month.isin([3, 6, 9, 12]) & (x.index.day >= 7) & (x.index.day <= 17)
    lr = np.log(x.o.shift(-1) / x.c); x = x[~rw & ((lr - lr.mean()).abs() < 6 * lr.std())].dropna()
    pj, nj, no = x.jump & (x.ret > 0), x.jump & (x.ret < 0), ~x.jump
    print(f"\n{sym}: {len(x)} days, jump days {x.jump.sum()} ({x.jump.mean():.0%}): up {pj.sum()}, down {nj.sum()}")
    for nm, m in (("after up-jump day", pj), ("after down-jump day", nj), ("after no-jump day", no)):
        a, b = x.next_on[m], x.next_id[m]
        print(f"   {nm:20s} next overnight ${a.mean():+5.0f} (t {a.mean() / a.std() * np.sqrt(len(a)):+.1f}), next intraday ${b.mean():+5.0f} (t {b.mean() / b.std() * np.sqrt(len(b)):+.1f})")
    for per, m in (("2018-22", x.index < "2023-01-01"), ("2023+", x.index >= "2023-01-01")):
        a = x.next_on[pj & m] - cost; b = x.next_on[no & m] - cost
        print(f"   {per}: overnight long after up-jump days {len(a)} nights ${a.mean():+5.0f} t {a.mean() / a.std() * np.sqrt(len(a)):+.1f}; after no-jump ${b.mean():+4.0f}")
    x["jr"] = np.where(x.jump, x.ret, 0); m = x.groupby(x.index.to_period("M")).agg(jr=("jr", "sum"), on=("next_on", "sum"), id=("next_id", "sum"))
    m["on1"] = m.on.shift(-1); m["id1"] = m.id.shift(-1); m = m.dropna(); hi = m.jr > 0
    print(f"   monthly: months with net positive jump return {hi.sum()} -> next month overnight ${m.on1[hi].mean():+.0f} / intraday ${m.id1[hi].mean():+.0f}; "
          f"other {(~hi).sum()} -> ${m.on1[~hi].mean():+.0f} / ${m.id1[~hi].mean():+.0f}")
