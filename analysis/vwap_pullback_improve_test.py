"""Can the VWAP pullback be made useful? (2026-10-13) Use it as an ENTRY for a direction that has a proven
edge instead of the opening-range break: (1) the Overnight Bias rule (8:30 open in the top / bottom third of
the 23:00-8:30 range), (2) only the days Overnight Bias ML (MultiCharts) trades, same side. Apex version
(entries 9:01-15:00, flat 15:55), swing stop / target as in the file, and a 14:30 time exit variant.
Design 2018-22 vs holdout 2023-26, random-side placebo, funded bench.
  python3 analysis/vwap_pullback_improve_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
import vwap_orb_pullback_test as V
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def line(t, nm, w=58):
    if len(t) < 3: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    a, b = x[y <= 2022], x[y >= 2023]
    return (f"{nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f} t={x.mean()/x.std()*np.sqrt(len(x)):4.1f}"
            f" yrs+ {(x.groupby(y).sum() > 0).sum()}/{y.nunique()} | 18-22 ${a.mean():5.0f} PF {pf(a):.2f} | 23+ ${b.mean():5.0f} PF {pf(b):.2f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); s = V.series(g)
    sh, sl = V.pivots(s["h"], s["l"], 20); th, tl = V.pivots(s["h"], s["l"], 5)
    print(__doc__.split("\n")[0])
    # Overnight Bias direction per day
    onb = {}
    for d in g.trading:
        if d == 0: continue
        h = np.r_[g.h[d - 1, jof(2300) + 1:], g.h[d, :jof(830) + 1]]; l = np.r_[g.l[d - 1, jof(2300) + 1:], g.l[d, :jof(830) + 1]]
        if np.isnan(h).all(): continue
        hi, lo, op = np.nanmax(h), np.nanmin(l), g.o[d, 511]
        if np.isnan(op) or hi <= lo: continue
        p = (op - lo) / (hi - lo)
        onb[int(d)] = 1 if p >= 2 / 3 else (-1 if p <= 1 / 3 else 0)
    ml = load_mc(g, "Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx")
    mlb = {int(d): int(sd) for d, sd in zip(ml.day, ml.side)}
    res = {}
    res["original (ORB break bias)"] = V.run(g, s, sh, sl, th, tl, apex=True)
    res["Overnight Bias direction"] = V.run(g, s, sh, sl, th, tl, apex=True, bias=onb)
    res["Overnight Bias direction, out 14:30"] = V.run(g, s, sh, sl, th, tl, apex=True, bias=onb, exit_t=1430)
    res["ONB ML trade days, same side"] = V.run(g, s, sh, sl, th, tl, apex=True, bias=mlb)
    res["ONB ML trade days, same side, out 14:30"] = V.run(g, s, sh, sl, th, tl, apex=True, bias=mlb, exit_t=1430)
    for k, t in res.items(): print(line(t, k))
    for k in ("Overnight Bias direction", "ONB ML trade days, same side"):
        pl = [V.run(g, s, sh, sl, th, tl, apex=True, bias=(onb if "Overnight" in k else mlb), rand=r).net.mean() for r in range(10)]
        print(f"   placebo for '{k}' (random side on the same entry bars): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f})")
    # same days: ONB ML's own trades vs the VWAP-pullback entry on those days
    t = res["ONB ML trade days, same side"]
    mlx = ml.copy(); mlx["net"] = (mlx.exit - mlx.entry) * mlx.side * 20 - 7.25 - 5 * (1 + (mlx.kind != 1))
    both = set(t.day) & set(mlx.day)
    a = mlx[mlx.day.isin(both)].net.mean(); b = t[t.day.isin(both)].net.mean()
    print(f"\n   on the {len(both)} days both trade: ONB ML's own entry ${a:.0f} vs VWAP-pullback entry ${b:.0f}")
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "VCS_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    print("\n   Funded bench:")
    a0, c0 = lab.score(plan, 250, **CS), lab.score(plan, 500, **CS)
    print(f"   current plan                      1y ${a0['expected']:,.0f} 2y ${c0['expected']:,.0f}")
    for k in ("Overnight Bias direction", "ONB ML trade days, same side"):
        tt = res[k]; tt = tt[tt.t1 // 1440 == tt.t0 // 1440].copy()
        lab.add("VWPX", tt, slippage=False)
        a, c = lab.score({**plan, "VWPX": 1}, 250, **CS), lab.score({**plan, "VWPX": 1}, 500, **CS)
        print(f"   + '{k}' 1 MNQ   1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
