"""Overnight range and the RTH open vs the overnight midpoint (user's post, 2026-10-15: NQ 2015-25, 2,827 days; open above the
ON midpoint -> ON high broken first 76.2%, below -> ON low first 75.6%; 94.2% of days break at least one ON level; median
first break 11 min after the open; larger gaps -> fewer opposite-side sweeps).

Here: NQ 1-min 2018-2026, CT. ON session 17:00 CT (18:00 ET) -> 8:30 CT (9:30 ET): ONH, ONL, mid. RTH = 8:31 .. 15:00 CT
bars, RTH open = the 8:31 bar's open. First break = first RTH bar trading above ONH / below ONL (a bar doing both = 'both
same bar', dropped from first-side stats).
  A  replication: any-break rate, first side by open vs mid, timing, gap sizes, opposite-side sweep after the first break
  B  NULL: a driftless random walk starting at the open hits ONH before ONL with p = (open - ONL) / (ONH - ONL). Actual
     high-first rate vs that geometric expectation, overall and by open position (deciles); if they match, the 76% is
     geometry, not information
  C  trades (1 NQ, $7.25 + 1 tick a fill): toward the nearer level from the 8:31 open, target that level, stop the far
     level (or out 15:00) -- under the null its expected gross P&L is 0; also break-and-continue: after the first break,
     follow it for 1 x / 0.5 x the ON range target, stop back at the midpoint, out 15:00
  python3 analysis/overnight_midpoint_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25 + 2 * 0.25 * 20.0


def frame(g):
    rows = []
    J0, J1 = jof(831), jof(1500)
    for r in g.trading:
        if r == 0: continue
        on_h = np.r_[g.h[r - 1, jof(1701):], g.h[r, :jof(830) + 1]]; on_l = np.r_[g.l[r - 1, jof(1701):], g.l[r, :jof(830) + 1]]
        if np.isnan(on_h).mean() > 0.3 or np.isnan(g.o[r, J0]): continue
        H, L = np.nanmax(on_h), np.nanmin(on_l)
        if not H > L: continue
        o = g.o[r, J0]; h, l, c = g.h[r, J0:J1 + 1], g.l[r, J0:J1 + 1], g.c[r, J0:J1 + 1]
        if np.isnan(c).mean() > 0.1: continue
        prevc = g.c[r - 1, jof(1500)] if not np.isnan(g.c[r - 1, jof(1500)]) else np.nan
        uh = np.where(h > H)[0]; ul = np.where(l < L)[0]
        fh = uh[0] if len(uh) else 9999; fl = ul[0] if len(ul) else 9999
        rows.append(dict(date=pd.Timestamp(g.ts[r]), r=r, H=H, L=L, o=o, prevc=prevc, fh=fh, fl=fl, close=c[~np.isnan(c)][-1]))
    D = pd.DataFrame(rows).set_index("date")
    D = D[D.index >= "2018-01-01"]
    D["pos"] = (D.o - D.L) / (D.H - D.L)                      # 0 = at ONL, 1 = at ONH (can be outside)
    D["first"] = np.where((D.fh == 9999) & (D.fl == 9999), "none", np.where(D.fh < D.fl, "H", np.where(D.fl < D.fh, "L", "same")))
    D["gap"] = D.o - D.prevc
    return D


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); D = frame(g)
    inside = D[(D.pos > 0) & (D.pos < 1)]
    print(f"\n{len(D)} sessions 2018-2026; open inside the ON range {len(inside) / len(D):.0%} (outside = already broken at the open)")
    print("\nA. Replication")
    hb, lb = D.fh < 9999, D.fl < 9999
    print(f"   any ON level broken in RTH {np.mean(hb | lb):.1%} (post 94.2%); only high {np.mean(hb & ~lb):.1%}, only low {np.mean(lb & ~hb):.1%},"
          f" both {np.mean(hb & lb):.1%}, neither {np.mean(~hb & ~lb):.1%}")
    X = inside[inside["first"].isin(["H", "L"])]
    up = X.pos > 0.5
    print(f"   open inside range, above mid: high first {np.mean(X[up]['first'] == 'H'):.1%} (post 76.2%); below mid: low first {np.mean(X[~up]['first'] == 'L'):.1%} (post 75.6%); n {len(X)}")
    t = np.minimum(X.fh, X.fl) + 1
    print(f"   minutes to first break: median {t.median():.0f}; within 5 / 15 / 30 / 60 / 120: " +
          " / ".join(f"{np.mean(t <= m):.0%}" for m in (5, 15, 30, 60, 120)))
    print("\nB. Null: random-walk P(high first) = position of the open in the ON range")
    X = X.assign(null=X.pos.clip(0, 1), hit=(X["first"] == "H").astype(float))
    print(f"   all: actual high-first {X.hit.mean():.1%} vs geometric {X.null.mean():.1%}")
    for nm, m in (("above mid", up), ("below mid", ~up)):
        print(f"   {nm}: actual high-first {X[m].hit.mean():.1%} vs geometric {X[m].null.mean():.1%}  (n {m.sum()})")
    X["dec"] = pd.cut(X.pos, np.linspace(0, 1, 11))
    tab = X.groupby("dec").agg(n=("hit", "size"), actual=("hit", "mean"), geometric=("null", "mean"))
    print((tab * [1, 100, 100]).round(1).to_string())
    resid = X.hit - X.null; se = resid.std() / np.sqrt(len(resid))
    print(f"   actual - geometric = {resid.mean() * 100:+.1f} pts (t {resid.mean() / se:.2f}); above mid {resid[up].mean() * 100:+.1f}, below mid {resid[~up].mean() * 100:+.1f}")
    print("\nC. Trades (net per NQ)")
    out = []
    for d, s in X.iterrows():
        side = 1 if s.pos > 0.5 else -1; tgt, stp = (s.H, s.L) if side > 0 else (s.L, s.H)
        hit_t = s.fh if side > 0 else s.fl; hit_s = s.fl if side > 0 else s.fh
        if hit_t < hit_s: px = tgt
        elif hit_s < hit_t: px = stp
        else: px = s.close
        out.append(dict(date=d, side=side, net=(px - s.o) * side * PV - COST, pos=s.pos))
    T = pd.DataFrame(out).set_index("date"); x = T.net; y = x.index.year
    print(f"   toward the nearer level (target it, stop the far one): n {len(x)} avg ${x.mean():.1f} t {x.mean() / x.std() * np.sqrt(len(x)):.2f}"
          f" win {np.mean(x > 0):.0%} | 2018-22 ${x[y < 2023].mean():.1f} 2023-26 ${x[y >= 2023].mean():.1f}")
    # break and continue
    for mult in (1.0, 0.5):
        res = []
        for d, s in D.iterrows():
            if s["first"] not in ("H", "L"): continue
            r = int(s.r); side = 1 if s["first"] == "H" else -1; lvl = s.H if side > 0 else s.L; j0 = jof(831) + int(min(s.fh, s.fl))
            ent = lvl + side * TICK; rng_ = s.H - s.L; tgt = ent + side * mult * rng_; stp = (s.H + s.L) / 2; px = None
            for j in range(j0 + 1, jof(1500) + 1):
                if np.isnan(g.c[r, j]): continue
                if (side > 0 and g.l[r, j] <= stp) or (side < 0 and g.h[r, j] >= stp): px = stp - side * TICK; break
                if (side > 0 and g.h[r, j] >= tgt) or (side < 0 and g.l[r, j] <= tgt): px = tgt; break
            if px is None: px = g.c[r, jof(1500)]
            res.append(dict(date=d, net=(px - ent) * side * PV - COST))
        z = pd.DataFrame(res).set_index("date").net; yy = z.index.year
        print(f"   break-and-continue, target {mult:g} x ON range, stop at mid: n {len(z)} avg ${z.mean():.1f} t {z.mean() / z.std() * np.sqrt(len(z)):.2f}"
              f" win {np.mean(z > 0):.0%} | 2018-22 ${z[yy < 2023].mean():.1f} 2023-26 ${z[yy >= 2023].mean():.1f}")
    D["gq"] = pd.qcut((D.gap.abs() / (D.H - D.L)).replace([np.inf], np.nan), 4, labels=["tiny", "small", "medium", "large"])
    both = (D.fh < 9999) & (D.fl < 9999)
    print("\n   opposite-side sweep after the first break, by gap size (quartiles of |gap| / ON range):",
          both.groupby(D.gq).mean().round(3).to_dict(), "| ON range / ATR does the same job? corr(|gap|/range, range) =",
          round(float((D.gap.abs() / (D.H - D.L)).corr(D.H - D.L)), 2))
