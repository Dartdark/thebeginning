"""ZT continuation ingredient ablation (user 2026-11-09: 'take apart the ZT continuation ingredients ... for the best version of it').
PRE-REGISTERED (header committed before the first run). Information first. Base = the best ZT item (analysis/zt_volz_test.py, post hoc):
15-min NQ bars, ZT = (C - EMA32) / (C x sd(returns, 32, population) x sqrt 32), flat and ZT >= +1 -> long next bar at market (<= -1 ->
short), exit next bar at market when |ZT| <= 0.25 / ZT past -/+4 / 8 bars held / a bar closes after 14:45; entries on bars closing
08:35-14:45 CT. Per NQ after $7.25 + 1 tick per fill. ONE part changed at a time:
  signal measure: SMA instead of EMA / mean 16 / mean 64 / vol window 16 / vol window 64 / ATR(32) denominator / no vol scaling
    (points from the EMA) -- the last two with the threshold set so the same share of 2018-22 bars qualifies as the base /
    EntryZ 0.75 / 1.25
  exits: no |ZT| <= 0.25 exit / exit at |ZT| <= 0.5 / no +-4 stop / hold 4 / hold 16 / no bar limit (to 14:45)
  entries: fresh cross only (ZT crossed the threshold on this bar; no instant re-entry) / one trade a day / longs only / shorts only
  time: entries 08:35-11:00 only / entries 11:00-14:45 only
  Twin overlap (info): base trades split by Twin-active vs Twin-flat days.
Two-bar rule: a variant whose t and both periods' $ a trade beat the base is benched (150K evaluation + 2 MNQ, funded + 2 MNQ,
personal + 1 MNQ) next to the base.
  tools/run_stamped.sh analysis/zt_ablation.py > analysis/outputs/zt_ablation_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from donchian_lwti_test import series
from ingredient_ablation3 import line

PV, TICK, COST = 20.0, 0.25, 7.25


def zser(s, mean="ema", mean_len=32, vol_len=32, denom="ret"):
    C = pd.Series(s["c"]); H, L = pd.Series(s["h"]), pd.Series(s["l"])
    m = C.ewm(alpha=2 / (mean_len + 1), adjust=False).mean() if mean == "ema" else C.rolling(mean_len).mean()
    if denom == "ret": dv = C * (C / C.shift(1) - 1).rolling(vol_len).std(ddof=0) * np.sqrt(mean_len)
    elif denom == "atr":
        tr = pd.concat([H - L, (H - C.shift()).abs(), (L - C.shift()).abs()], axis=1).max(axis=1); dv = tr.rolling(vol_len).mean() * np.sqrt(mean_len)
    else: dv = pd.Series(1.0, index=C.index)
    return ((C - m) / dv).where(dv > 0, 0.0).to_numpy()


def run(g, s, z, entry=1.0, exit_=0.25, stop=4.0, hold=8, win=(835, 1445), ent=None, fresh=False, one_day=False, side_only=0):
    O, H, L, C, row, hm = s["o"], s["h"], s["l"], s["c"], s["row"], s["hhmm"]
    ts = pd.DatetimeIndex(g.ts); y0 = np.searchsorted(row, np.flatnonzero(ts >= "2018-01-01")[0])
    n = len(C); out = []; pos = 0; pend = 0; xp = False; e = 0.0; i0 = 0; adv = 0.0; last_day = -1
    inwin = (hm >= win[0]) & (hm <= win[1]); inent = inwin if ent is None else (hm >= ent[0]) & (hm <= ent[1])
    for i in range(max(y0, 70), n):
        if pend: pos = pend; e = O[i] + pos * TICK; i0 = i; adv = 0.0; pend = 0
        elif xp:
            px = O[i] - pos * TICK; out.append((ts[row[i0]], pos, (px - e) * pos * PV - COST, min(adv, (px - e) * pos) * PV - COST)); pos = 0; xp = False
        if pos:
            adv = min(adv, ((L[i] if pos > 0 else H[i]) - e) * pos)
            if (exit_ is not None and abs(z[i]) <= exit_) or (stop is not None and z[i] * pos <= -stop) or (hold is not None and i - i0 >= hold) or not inwin[i]: xp = True
            continue
        if not inent[i] or (one_day and row[i] == last_day): continue
        sig = 1 if z[i] >= entry else (-1 if z[i] <= -entry else 0)
        if sig and fresh and abs(z[i - 1]) >= entry and np.sign(z[i - 1]) == sig: sig = 0
        if sig and side_only and sig != side_only: sig = 0
        if sig: pend = sig; last_day = row[i]
    return pd.DataFrame(out, columns=["date", "side", "net", "adv"])


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); s = series(g, 15); ts = pd.DatetimeIndex(g.ts)
    design = (ts[s["row"]] >= "2018-01-01") & (ts[s["row"]] < "2023-01-01") & (s["hhmm"] >= 835) & (s["hhmm"] <= 1445)
    z0 = zser(s); share = np.mean(np.abs(z0[design]) >= 1.0); print(f"   base: share of 2018-22 window bars with |ZT| >= 1: {share:.2%}")
    sh = lambda nm, T: (print(line(T.net, T.date, nm), flush=True), T)[1]
    T0 = sh("BASE (15-min, EntryZ 1, continuation)", run(g, s, z0)); res = {"base": T0}
    tt = lambda T: T.net.mean() / T.net.std() * np.sqrt(len(T))
    print("\n1. Signal measure:")
    for nm, kw in (("SMA instead of EMA", dict(mean="sma")), ("mean 16", dict(mean_len=16)), ("mean 64", dict(mean_len=64)),
                   ("vol window 16", dict(vol_len=16)), ("vol window 64", dict(vol_len=64))):
        res[nm] = sh(nm, run(g, s, zser(s, **kw)))
    for nm, dn in (("ATR(32) denominator (same bar share)", "atr"), ("no vol scaling: points from EMA (same share)", "pts")):
        z = zser(s, denom=dn); thr = np.quantile(np.abs(z[design]), 1 - share); print(f"      threshold {thr:.3f}")
        res[nm] = sh(nm, run(g, s, z, entry=thr, exit_=0.25 * thr, stop=4 * thr))
    for ez in (0.75, 1.25): res[f"EntryZ {ez}"] = sh(f"EntryZ {ez}", run(g, s, z0, entry=ez))
    print("\n2. Exits:")
    for nm, kw in (("no |ZT| <= 0.25 exit", dict(exit_=None)), ("exit at |ZT| <= 0.5", dict(exit_=0.5)), ("no +-4 stop", dict(stop=None)),
                   ("hold 4 bars", dict(hold=4)), ("hold 16 bars", dict(hold=16)), ("no bar limit (to 14:45)", dict(hold=None))):
        res[nm] = sh(nm, run(g, s, z0, **kw))
    print("\n3. Entries:")
    for nm, kw in (("fresh cross only", dict(fresh=True)), ("one trade a day", dict(one_day=True)), ("longs only", dict(side_only=1)), ("shorts only", dict(side_only=-1))):
        res[nm] = sh(nm, run(g, s, z0, **kw))
    print("\n4. Time:")
    for nm, kw in (("entries 08:35-11:00 only", dict(ent=(835, 1100))), ("entries 11:00-14:45 only", dict(ent=(1100, 1445)))):
        res[nm] = sh(nm, run(g, s, z0, **kw))
    print("\n5. Twin overlap (base trades):")
    P = pd.read_pickle("scratch_data/personal_P.pkl"); tw = set(P.index[P.TwinContinuation != 0])
    m = T0.date.isin(tw); sh("on Twin-active days", T0[m]); sh("on Twin-flat days", T0[~m])
    per = T0.groupby(T0.date).size(); print(f"   trades a day when active: mean {per.mean():.1f}, max {per.max()}; worst day ${T0.groupby(T0.date).net.sum().min():,.0f} per NQ")
    a0, b0 = T0[T0.date < "2023"].net.mean(), T0[T0.date >= "2023"].net.mean()
    win_ = [k for k, T in res.items() if k != "base" and len(T) > 30 and tt(T) > tt(T0) and T[T.date < "2023"].net.mean() > a0 and T[T.date >= "2023"].net.mean() > b0]
    print(f"\n   Variants beating the base on t and both periods: {win_ or 'none'}")
    if not win_: sys.exit()
    import bench150 as BB
    from new_sources_150k import daypaths
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts); E, F, Pm = {}, {}, {}; ext = {}
    for k in ["base"] + win_:
        T = res[k]; W1, R1 = daypaths(D, [(int(dpos[x]) if x in dpos.index else None, a, n_) for x, a, n_ in zip(T.date, T.adv, T.net)])
        E[f"+ {k} 2 MNQ"] = (2 * W1, 2 * R1); key = "ZT_" + str(len(ext)); ext[key] = (W1, R1[:, -1]); F[f"+ {k} 2 MNQ"] = {**BB.BASE_FUNDED, key: 2}
        Pm[f"+ {k} 1 MNQ"] = (T.net / 10 - 0.55).groupby(T.date).sum()
    print(); BB.eval_bench(ctx, E); print(); BB.funded_bench(ctx, F, extra=ext); print(); BB.personal(Pm)
