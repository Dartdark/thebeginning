"""Zoom-in from the cross-asset map: fade NQ's first-15-minute reaction to 7:30 CT data (2026-10-14).

Map finding (analysis/cross_asset_map_test.py, section C): on 7:30 data-release days, following NQ's 7:30 -> 7:45 move
to 15:00 lost $588 a trade (t -2.4; 2018-22 -$412, 2023-26 -$733), and lost $1,283 (t -2.7, both periods) when oil moved
the other way in those 15 minutes. So: fade the reaction. The plan already has NFP Fade (NFP Fridays, 7:30 -> 9:00
CT fade, stop 0.5 ATR), so NFP days are reported separately and the candidate is the non-NFP days.
Trade: at 7:45 CT, against the 7:30 -> 7:45 move, entry 7:46 open + 1 tick; exit 9:00 / 10:30 / 12:00 / 15:00;
stop none / 0.5 / 1.0 x 15-day ATR; 1 NQ, $7.25 + 1 tick a fill. Split: all release days / NFP / non-NFP; oil
disagreeing with NQ's reaction (CL 7:30 -> 7:45 the other way) or agreeing. Placebo: the same fade at 7:45 on
ordinary days (no release). Design 2018-22, holdout 2023-26; funded bench for a survivor.
  python3 analysis/release_reaction_fade_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from cl_forced_flows_test import load
import event_days as E
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25
SPLIT = pd.Timestamp("2023-01-01")


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def line(x, nm, w=60):
    x = pd.Series(x).dropna()
    if len(x) < 8: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.0f} PF {pf:4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${x[y < 2023].mean():6.0f} 23-26 ${x[y >= 2023].mean():6.0f}")


def fade_trades(g, rows, side, exit_t, stop_atr, atr):
    """side per row (+1 long / -1 short), entry 7:46 open, stop k x ATR (None = no stop), out at exit_t close."""
    O, H, L, C = g.o, g.h, g.l, g.c
    out = []
    for d, s in zip(rows, side):
        if s == 0 or np.isnan(O[d, jof(746)]): continue
        e = O[d, jof(746)] + s * TICK; sp = e - s * stop_atr * atr[d] if stop_atr else None
        px = None; j1 = jof(exit_t); jx = j1
        for j in range(jof(746), j1 + 1):
            if np.isnan(H[d, j]): continue
            if sp is not None and ((L[d, j] <= sp) if s > 0 else (H[d, j] >= sp)):
                px = ((min(O[d, j], sp) if s > 0 else max(O[d, j], sp)) if j > jof(746) else sp) - s * TICK; jx = j; kind = 0; break
        if px is None:
            cc = C[d, jof(746):j1 + 1]; ok = np.where(~np.isnan(cc))[0]
            if not len(ok): continue
            px = cc[ok[-1]] - s * TICK; jx = jof(746) + ok[-1]; kind = 2
        out.append(dict(day=d, j0=jof(746), j1=jx, side=s, entry=e, exit=px, kind=kind, date=pd.Timestamp(g.ts[d]),
                        net=(px - e) * s * PV - COMM))
    return pd.DataFrame(out).set_index("date", drop=False)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); cl = load("CL")
    atr = g.daily_atr(15)
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= pd.Timestamp("2018-01-01")]
    idx = pd.DatetimeIndex(g.ts[tr])
    rel = set(E.release_days(g))
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    nq_r = np.sign(cf[tr * 1440 + jof(745)] - cf[tr * 1440 + jof(730)])
    pos = pd.Series(np.arange(cl.D), index=cl.dates); cr = pos.reindex(g.dates[tr]).to_numpy()
    ccf = pd.Series(cl.c.ravel()).ffill().to_numpy(); okc = ~np.isnan(cr); cl_r = np.full(len(tr), np.nan)
    cr_i = cr[okc].astype(int); cl_r[okc] = np.sign(ccf[cr_i * 1440 + jof(745)] - ccf[cr_i * 1440 + jof(730)])
    is_rel = np.array([d in rel for d in tr]); nfp = is_rel & (idx.dayofweek == 4) & (idx.day <= 7)
    oil_dis = (cl_r == -nq_r) & (nq_r != 0)
    side = -nq_r
    groups = {"all release days": is_rel, "NFP Fridays": nfp, "non-NFP release days": is_rel & ~nfp,
              "non-NFP, oil disagreed": is_rel & ~nfp & oil_dis, "non-NFP, oil agreed": is_rel & ~nfp & ~oil_dis,
              "placebo: ordinary days (no release), same fade": ~is_rel}
    print(f"release days {is_rel.sum()} (NFP {nfp.sum()}, other {(is_rel & ~nfp).sum()}); oil disagreed on {np.mean(oil_dis[is_rel & ~nfp]):.0%} of the non-NFP ones")
    res = {}
    for ex, st in itertools.product((900, 1030, 1200, 1500), (None, 0.5, 1.0)):
        print(f"\n-- fade, out {ex}, stop {st if st else 'none'}{' x ATR' if st else ''}")
        for gn, m in groups.items():
            t = fade_trades(g, tr[m], side[m], ex, st, atr); res[(ex, st, gn)] = t
            print(line(t.net, gn))
    # design pick on non-NFP release days, by 2018-22 t
    cand = {k: v for k, v in res.items() if k[2] == "non-NFP release days"}
    sc = {k: tstat(v.net[v.index < SPLIT]) for k, v in cand.items()}
    pick = max(sc, key=sc.get); t = cand[pick]
    print(f"\n== Pick by 2018-22 t (non-NFP release days): out {pick[0]}, stop {pick[1]}")
    print(line(t.net, "picked rule, all years"))
    print("   by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in t.net.groupby(t.index.year).sum().items()))
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= "2018-01-01"]
    dl = lambda x: x.net.groupby(x.index.normalize()).sum().reindex(days, fill_value=0.0)
    print(M.table({"picked": (dl(t), t.net), "  longs (faded a drop)": (dl(t[t.side > 0]), t.net[t.side > 0]),
                   "  shorts (faded a rise)": (dl(t[t.side < 0]), t.net[t.side < 0])}))
    b_, p_ = R.report({"picked, 2023+": dl(t)[days >= SPLIT]}, n=3000); print(b_); print(p_)
    pl = res[(pick[0], pick[1], "placebo: ordinary days (no release), same fade")]
    print(line(pl.net, "placebo at the same settings: ordinary days"))
    # funded bench: add to the plan (NFP Fade already trades NFP days)
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    from bridge_monday_confirm import load_bridge_mc
    lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    tt = t.reset_index(drop=True)[["day", "j0", "j1", "side", "entry", "exit", "kind"]].copy(); tt["slips"] = 0
    lab.add("RRF", tt, stop_pts=(pick[1] or 1.0) * atr, slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    from speed_to_13k import run as speed, fmt
    sp = {}
    for nm, p in (("current plan", plan), ("+ release fade 1 MNQ", {**plan, "RRF": 1}), ("+ release fade 2 MNQ", {**plan, "RRF": 2}),
                  ("+ release fade risk $300", {**plan, "RRF": ("risk", 300)}), ("+ release fade risk $500", {**plan, "RRF": ("risk", 500)})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<28} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        sp[nm] = speed(lab, p, **CS)
    print(fmt(pd.DataFrame(sp).T))
    print("   daily correlation with the plan:", {k: round(float(np.corrcoef(lab.C["RRF"], lab.C[k])[0, 1]), 2) for k in ("VB", "ONB_ML2_MC", "NFP_MC", "EOS", "LDF_MC")})

    print("\n== NFP Fade with a longer hold (zoom-in result): replace the plan's NFP Fade (7:30-7:45 fade, out 9:00, stop 0.5 ATR, risk $500)")
    nfp_rows = tr[nfp]; nfp_side = side[nfp]
    V = {"9:00, stop 0.5 (as now, Python)": (900, 0.5), "12:00, stop 0.5": (1200, 0.5), "12:00, stop 1.0": (1200, 1.0),
         "15:00, stop 0.5": (1500, 0.5), "15:00, stop 1.0": (1500, 1.0)}
    cands = {"current plan": plan}
    for nm, (ex, st) in V.items():
        t2 = fade_trades(g, nfp_rows, nfp_side, ex, st, atr)
        print(line(t2.net, f"NFP fade out {nm}"))
        lb = f"NFP_{ex}_{st}"; tt = t2.reset_index(drop=True)[["day", "j0", "j1", "side", "entry", "exit", "kind"]].copy(); tt["slips"] = 0
        lab.add(lb, tt, stop_pts=st * atr, slippage=False)
        p = {k: v for k, v in plan.items() if k != "NFP_MC"}; p[lb] = ("risk", 500); cands[f"NFP {nm}, risk $500"] = p
        if st == 1.0: p2 = dict(p); p2[lb] = ("risk", 1000); cands[f"NFP {nm}, risk $1,000 (same size as now)"] = p2
    sp = {}
    for nm, p in cands.items():
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<50} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        sp[nm] = speed(lab, p, **CS)
    print(fmt(pd.DataFrame(sp).T))
    t2 = fade_trades(g, nfp_rows, nfp_side, 1200, 1.0, atr)
    print(M.table({"NFP out 12:00 stop 1.0": (dl(t2), t2.net), "  longs": (dl(t2[t2.side > 0]), t2.net[t2.side > 0]), "  shorts": (dl(t2[t2.side < 0]), t2.net[t2.side < 0])}))
    b_, p_ = R.report({"NFP out 12:00 stop 1.0, 2023+": dl(t2)[days >= SPLIT]}, n=3000); print(b_); print(p_)
    print("   by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in t2.net.groupby(t2.index.year).sum().items()))
