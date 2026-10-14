"""Gold Asian-range breakout: exit management (user's request 2026-10-14, "there must be a way to optimize it").

Base: filter B version (analysis/gold_breakout_filter_test.py): range 20:00 -> 00:00 CT, OCO stops at the edges, fills
before 02:00 CT only, stop 1.0 x range width (= 1R), one a day, 1 GC, $7.25 + 1 tick a fill.
Pre-registered grid (32 versions), chosen on 2018-22 only, then run once on 2023-26:
  time exit  05:00 (end of early London) / 07:25 (before the 7:30 CT US data) / 10:00 (as written) / 12:00
  breakeven  off / stop to entry + 1 tick once the trade has been +1R (from the next minute)
  target     none / 1.5R / 2R / 3R (limit, no slippage)
Fills: 1-minute bars; a minute that touches both stop and target counts as the stop (conservative).
  python3 analysis/gold_breakout_exit_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import asian_breakout_test as AB
import gold_asian_breakout_gc_test as GT
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPLIT = pd.Timestamp("2023-01-01")
PV, TICK, COMM = 100.0, 0.10, 7.25


def manage(gc, base, exit_t, be, tgt):
    O, H, L, C = (getattr(gc, a).ravel() for a in "ohlc")
    out = []
    for r in base.itertuples():
        s, en, risk = r.side, r.entry, r.width
        sp = en - s * risk; tp = en + s * tgt * risk if tgt else None
        tx = r.day * 1440 + jof(exit_t)
        if r.t0 >= tx: continue
        px = None; kind = 2; armed_be = False
        for k in range(r.t0, tx):
            if np.isnan(H[k]): continue
            hit_sp = (L[k] <= sp) if s > 0 else (H[k] >= sp)
            hit_tp = tp is not None and ((H[k] >= tp) if s > 0 else (L[k] <= tp))
            if hit_sp:
                px = ((min(O[k], sp) if s > 0 else max(O[k], sp)) if k > r.t0 else sp) - s * TICK; kind = 0; t1 = k; break
            if hit_tp:
                px = tp; kind = 1; t1 = k; break
            if be and not armed_be and ((H[k] - en) * s >= risk if s > 0 else (en - L[k]) >= risk):
                armed_be = True; sp = en + s * TICK
        if px is None:
            cc = C[r.t0:tx]; ok = np.where(~np.isnan(cc))[0]; t1 = r.t0 + ok[-1]; px = cc[ok[-1]] - s * TICK
        net = (px - en) * s * PV - COMM
        out.append(dict(day=r.day, t0=r.t0, t1=t1, side=s, entry=en, exit=px, kind=kind, width=r.width, net=net,
                        Rr=net / (risk * PV), date=r.date))
    return pd.DataFrame(out)


def streaks(x):
    s = "".join("L" if v < 0 else "W" for v in x)
    return max(len(z) for z in s.split("W")), x.rolling(20).sum().min()


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    print(__doc__.split("\n")[0])
    gc = GT.load_gc()
    base = AB.run(gc, "GC", exit_t=1200); base = base[(base.date >= pd.Timestamp("2018-01-01")) & ((base.t0 % 1440) // 60 < 2)].reset_index(drop=True)
    res = {}
    for ex, be, tg in itertools.product((500, 725, 1000, 1200), (False, True), (None, 1.5, 2.0, 3.0)):
        nm = f"out {ex:04d}, BE {'on ' if be else 'off'}, target {tg if tg else 'none'}"
        res[nm] = manage(gc, base, ex, be, tg)
    rows = []
    for nm, t in res.items():
        y = t.date.dt.year; d, h = t.Rr[y < 2023], t.Rr[y >= 2023]; ls, w20 = streaks(t.Rr)
        rows.append(dict(version=nm, n=len(t), win=np.mean(t.net > 0), R=t.Rr.mean(), t=t.Rr.mean() / t.Rr.std() * np.sqrt(len(t)),
                         R_18_22=d.mean(), t_18_22=d.mean() / d.std() * np.sqrt(len(d)), R_23_26=h.mean(), yrs=f"{(t.Rr.groupby(y).sum() > 0).sum()}/{y.nunique()}",
                         streak=ls, worst20R=w20))
    T = pd.DataFrame(rows).set_index("version").sort_values("t_18_22", ascending=False)
    print("\n1. All 32 versions, sorted by 2018-22 t (R per trade = net / range $)")
    print(T.to_string(float_format=lambda v: f"{v:,.3f}"))
    print(f"   versions positive in 2018-22: {int((T.R_18_22 > 0).sum())}/32, of those positive in 2023-26: {int(((T.R_18_22 > 0) & (T.R_23_26 > 0)).sum())};"
          f" Spearman 2018-22 vs 2023-26 R across versions {T.R_18_22.rank().corr(T.R_23_26.rank()):+.2f}")
    pick = T.index[0]; ref = "out 1000, BE off, target none"
    print(f"\n2. Pick by 2018-22: {pick} (reference = filter B as before: {ref})")
    days = pd.DatetimeIndex(gc.ts[gc.trading]); days = days[days.year >= 2018]
    dl = lambda x: x.groupby(x.date).net.sum().reindex(days, fill_value=0.0)
    for nm in (ref, pick):
        t = res[nm]
        print(M.table({nm: (dl(t), t.net), "  longs": (dl(t[t.side > 0]), t.net[t.side > 0]), "  shorts": (dl(t[t.side < 0]), t.net[t.side < 0])}))
        print("      R by year: " + " | ".join(f"{yy} {v:+.3f}" for yy, v in t.Rr.groupby(t.date.dt.year).mean().items()))
    b_, p_ = R.report({f"{ref} 2023+": dl(res[ref])[days >= SPLIT], f"{pick} 2023+": dl(res[pick])[days >= SPLIT]}, n=3000); print(b_); print(p_)
    rng = np.random.default_rng(3); tp_ = res[pick]
    pl = []
    for _ in range(10):
        b2 = base.copy(); b2["side"] = rng.choice([-1, 1], len(b2))
        ex, be, tg = pick.split(", ")
        pl.append(manage(gc, b2, int(ex.split()[1]), "on" in be, None if tg.endswith("none") else float(tg.split()[1])).Rr.mean())
    print(f"   placebo (same fills, random side, 10 runs): {np.mean(pl):+.3f} R ({min(pl):+.3f}..{max(pl):+.3f}) vs {tp_.Rr.mean():+.3f}")

    print("\n3. Funded bench (plan + gold on MGC)")
    g = pickle.load(open(SP + "g24.pkl", "rb")); lab = pickle.load(open(SP + "lab.pkl", "rb"))
    from bridge_monday_confirm import load_bridge_mc
    lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); dpos = pd.Series(np.arange(lab.D), index=dts2)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    from speed_to_13k import run as speed, fmt
    cands = {"current plan": plan}
    top3 = list(T.index[:3]); top3 = top3 if ref in top3 else top3 + [ref]
    for i, nm in enumerate(top3):
        t = res[nm]; key = f"GX{i}"; GT.add_to_lab(lab, key, t, gc)
        st_arr = np.full(lab.D, 1e12)
        for r in t.itertuples():
            if r.date in dpos.index: st_arr[dpos[r.date]] = r.width * 5.0
        lab.stop[key] = st_arr
        for q in (1, 2): cands[f"+ {nm}, {q} MGC"] = {**plan, key: q}
        cands[f"+ {nm}, risk $75"] = {**plan, key: ("risk", 75)}
    sp = {}
    for nm, p in cands.items():
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<56} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        sp[nm] = speed(lab, p, **CS)
    print(fmt(pd.DataFrame(sp).T))
