"""Zoom-in on the two survivors of forced-flow round 4 (analysis/forced_groups_round4_test.py), 2026-10-14.

1. MOC imbalance follow: closing-auction imbalances are published from 14:50 CT and clear at the 15:00 CT cash close;
   after a 14:00 -> 14:50 move of >= 0.2 ATR, 14:50 -> 15:00 went the same way ($194 before costs, t 3.7, 8/9 years).
   Trade: follow the 14:00 -> 14:50 move at the 14:51 open, out at the 15:00 close; threshold 0.1 .. 0.5 ATR; stop none
   / 0.25 ATR. Placebos: the same rule shifted to other 10-minute windows (decide at 12:50 / 13:20 / 13:50 / 14:20
   after a 50-minute move); early-close days (cash close 12:00 CT, auction 11:50-12:00). Overlap with Late-Day Flow
   (14:00 -> 14:30 follow), and whether it is a better LDF exit.
2. European (London) close follow: at London's 16:30 close in CT (10:30, or 11:30 in the DST-mismatch weeks), follow
   the 8:30 -> close move to 15:00; threshold 0 / 0.25 / 0.5 ATR, stop 0.5 / 1.0 ATR, exit 13:00 / 14:00 / 15:00.
   Placebo: the same rule at a fixed 10:30 on the mismatch days. Overlap with Vault Break.
Pick each by 2018-22 t; holdout 2023-26; longs and shorts separately; metrics, bootstrap / permutation on 2023+; funded
bench (current plan + it).
  python3 analysis/moc_london_close_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from forced_groups_round4_test import ct_of, tstat
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25
SPLIT = pd.Timestamp("2023-01-01")


def line(x, nm, w=66):
    x = pd.Series(x).dropna()
    if len(x) < 8: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.0f} PF {pf:4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${x[y < 2023].mean():6.0f} 23-26 ${x[y >= 2023].mean():6.0f}")


def trades(g, rows, sides, j0s, j1, stop_pts):
    """Same-day trades: entry at the open of bar j0 (+/- 1 tick), out at the close of j1 or at the stop."""
    O, H, L, C = g.o, g.h, g.l, g.c; out = []
    for d, s, j0, sp_ in zip(rows, sides, j0s, stop_pts):
        if s == 0 or np.isnan(O[d, j0]): continue
        e = O[d, j0] + s * TICK; sp = e - s * sp_ if np.isfinite(sp_) else None; px = None
        if sp is not None:
            seg = L[d, j0:j1 + 1] if s > 0 else H[d, j0:j1 + 1]
            hit = np.where((seg <= sp) if s > 0 else (seg >= sp))[0]
            if len(hit):
                j = j0 + hit[0]; px = (sp if j == j0 else (min(O[d, j], sp) if s > 0 else max(O[d, j], sp))) - s * TICK; jx = j; kind = 0
        if px is None:
            cc = C[d, j0:j1 + 1]; ok = np.where(~np.isnan(cc))[0]
            if not len(ok): continue
            px = cc[ok[-1]] - s * TICK; jx = j0 + ok[-1]; kind = 2
        out.append(dict(day=d, j0=j0, j1=jx, side=s, entry=e, exit=px, kind=kind, date=pd.Timestamp(g.ts[d]), net=(px - e) * s * PV - COMM))
    if not out: return pd.DataFrame(columns=["day", "j0", "j1", "side", "entry", "exit", "kind", "date", "net"]).set_index("date", drop=False)
    return pd.DataFrame(out).set_index("date", drop=False)


def pick(res, label):
    sc = {k: tstat(v.net[v.index < SPLIT]) for k, v in res.items() if len(v) > 20}
    k = max(sc, key=sc.get); print(f"\n== {label} pick by 2018-22 t: {k} (t {sc[k]:.1f})"); return k


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr_all = g.daily_atr(15)
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2018-01-01"]; idx = pd.DatetimeIndex(g.ts[tr]); D = len(tr)
    atr = atr_all[tr]; cf = pd.Series(g.c.ravel()).ffill().to_numpy(); P = lambda t: cf[tr * 1440 + jof(t)]
    full = g.last_j[tr] >= jof(1500)                                  # full sessions (early-close days stop at 12:00)
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= "2018-01-01"]
    dl = lambda x: x.net.groupby(x.index.normalize()).sum().reindex(days, fill_value=0.0)
    from time_clusters_test import trades as plan_trades
    T = plan_trades(g)

    # ---------------- 1. MOC follow ----------------
    print("\n1. MOC imbalance follow: sign(14:00 -> 14:50) at the 14:51 open, out 15:00 close")
    mv = P(1450) - P(1400); res = {}
    for th, st in itertools.product((0.1, 0.2, 0.3, 0.4, 0.5), (None, 0.25)):
        m = full & (np.abs(mv) >= th * atr) & (mv != 0)
        res[(th, st)] = t = trades(g, tr[m], np.sign(mv[m]).astype(int), np.full(m.sum(), jof(1451)), jof(1500), (st * atr[m]) if st else np.full(m.sum(), np.inf))
        print(line(t.net, f"|14:00->14:50| >= {th} ATR, stop {st if st else 'none'}"))
    k1 = pick(res, "MOC"); t1 = res[k1]; th1 = k1[0]
    print(line(t1.net, "picked")); print(line(t1.net[t1.side > 0], "  longs")); print(line(t1.net[t1.side < 0], "  shorts"))
    print("   by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in t1.net.groupby(t1.index.year).sum().items()))
    print("   placebo: the same rule decided at other times (50-minute move, then the next 10 minutes), same threshold:")
    for dec in (1050, 1150, 1250, 1320, 1350, 1420, 1450):
        jd = jof(dec); mvp = cf[tr * 1440 + jd] - cf[tr * 1440 + jd - 50]; m = full & (np.abs(mvp) >= th1 * atr) & (mvp != 0)
        tp = trades(g, tr[m], np.sign(mvp[m]).astype(int), np.full(m.sum(), jd + 1), jd + 10, np.full(m.sum(), np.inf))
        print(line(tp.net, f"   decide {dec} (50-minute move), trade the next 10 minutes"))
    ec = ~full & (g.last_j[tr] >= jof(1159))
    mve = P(1150) - P(1100); m = ec & (mve != 0)                                     # no threshold: quiet half days
    te = trades(g, tr[m], np.sign(mve[m]).astype(int), np.full(m.sum(), jof(1151)), jof(1200), np.full(m.sum(), np.inf))
    print(f"   early-close days (last bar before 15:00, data to 11:59+): {ec.sum()} days, rule fires {len(te)}: avg ${te.net.mean() if len(te) else np.nan:.0f}, " + ", ".join(f"{d.date()} ${v:.0f}" for d, v in te.net.items()))
    ldf = T["LDF_MC"]; ldf_d = set(ldf.day); both = t1[t1.day.isin(ldf_d)]
    same = both.merge(ldf[["day", "side"]], on="day", suffixes=("", "_ldf")); same = same[same.side == same.side_ldf]
    print(f"   overlap with Late-Day Flow: {len(both)} of {len(t1)} MOC trades are on LDF days ({len(same)} the same direction); MOC on LDF days "
          f"${both.net.mean():.0f}, on other days ${t1[~t1.day.isin(ldf_d)].net.mean():.0f}")

    # ---------------- 2. London close follow ----------------
    print("\n2. London-close follow: sign(8:30 -> London close in CT), to the exit")
    lc = ct_of(idx, 16, 30, "Europe/London"); jl = jof(lc); mism = lc != 1030
    o831 = g.o[tr, jof(831)]; mvl = cf[tr * 1440 + jl] - o831; res2 = {}
    for th, st, ex in itertools.product((0.0, 0.25, 0.5), (0.5, 1.0), (1300, 1400, 1500)):
        m = full & (np.abs(mvl) >= th * atr) & (mvl != 0)
        res2[(th, st, ex)] = t = trades(g, tr[m], np.sign(mvl[m]).astype(int), jl[m] + 1, jof(ex), st * atr[m])
        print(line(t.net, f"|move| >= {th} ATR, stop {st}, out {ex}"))
    k2 = pick(res2, "London close"); t2 = res2[k2]; th2, st2, ex2 = k2
    print(line(t2.net, "picked")); print(line(t2.net[t2.side > 0], "  longs")); print(line(t2.net[t2.side < 0], "  shorts"))
    print("   by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in t2.net.groupby(t2.index.year).sum().items()))
    for nm, jj in (("London close (11:30 CT)", jl), ("fixed 10:30 CT", np.full(D, jof(1030)))):
        mvv = cf[tr * 1440 + jj] - o831; m = full & mism & (np.abs(mvv) >= th2 * atr) & (mvv != 0)
        tp = trades(g, tr[m], np.sign(mvv[m]).astype(int), jj[m] + 1, jof(ex2), st2 * atr[m])
        print(line(tp.net, f"   mismatch days only, decide at the {nm}"))
    for dec in (930, 1000, 1100, 1200):
        mvv = P(dec) - o831; m = full & ~mism & (np.abs(mvv) >= th2 * atr) & (mvv != 0)
        tp = trades(g, tr[m], np.sign(mvv[m]).astype(int), np.full(m.sum(), jof(dec) + 1), jof(ex2), st2 * atr[m])
        print(line(tp.net, f"   placebo, normal days, decide at {dec} instead of 10:30"))
    vb = T["VB"]; vbd = vb.groupby("day").net.sum()
    j = pd.DataFrame({"lc": t2.set_index("day").net}).join(vbd.rename("vb"), how="left").fillna(0)
    print(f"   overlap with Vault Break: VB trades on {np.mean(j.vb != 0):.0%} of London-close trade days; daily correlation on those days {j.corr().iloc[0, 1]:.2f}")

    # ---------------- metrics and bench ----------------
    print("\n3. Metrics")
    print(M.table({"MOC follow": (dl(t1), t1.net), "  longs": (dl(t1[t1.side > 0]), t1.net[t1.side > 0]), "  shorts": (dl(t1[t1.side < 0]), t1.net[t1.side < 0]),
                   "London-close follow": (dl(t2), t2.net), "  longs ": (dl(t2[t2.side > 0]), t2.net[t2.side > 0]), "  shorts ": (dl(t2[t2.side < 0]), t2.net[t2.side < 0])}))
    b_, p_ = R.report({"MOC follow, 2023+": dl(t1)[days >= SPLIT], "London-close follow, 2023+": dl(t2)[days >= SPLIT]}, n=3000); print(b_); print(p_)

    print("\n4. Funded bench")
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    from bridge_monday_confirm import load_bridge_mc
    lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    for nm, t, stp in (("MOC", t1, (k1[1] or 0.25) * atr_all), ("LCF", t2, st2 * atr_all)):
        tt = t.reset_index(drop=True)[["day", "j0", "j1", "side", "entry", "exit", "kind"]].copy(); tt["slips"] = 0
        lab.add(nm, tt, stop_pts=stp, slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    from speed_to_13k import run as speed, fmt
    sp = {}
    cands = [("current plan", plan)] + [(f"+ MOC {q} MNQ", {**plan, "MOC": q}) for q in (1, 2, 3)] + [(f"+ London close {q} MNQ", {**plan, "LCF": q}) for q in (1, 2)] + \
            [("+ London close risk $300", {**plan, "LCF": ("risk", 300)}), ("+ MOC 2 + London close 1", {**plan, "MOC": 2, "LCF": 1})]
    for nm, p in cands:
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<28} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        sp[nm] = speed(lab, p, **CS)
    print(fmt(pd.DataFrame(sp).T))
    for nm in ("MOC", "LCF"):
        print(f"   {nm} daily correlation with the plan:", {kk: round(float(np.corrcoef(lab.C[nm], lab.C[kk])[0, 1]), 2) for kk in ("VB", "ONB_ML2_MC", "EOS", "LDF_MC", "MON_MC")})
    pickle.dump(dict(moc=t1, lcf=t2, k1=k1, k2=k2), open(SP + "moc_london.pkl", "wb"))
