"""Gold Asian-range breakout (user's file Gold_Asian_Breakout_Strategy.txt, 2026-10-14) ported to NQ and ES.

Rules as written (New York chart): range = high / low 21:00 -> 01:00 NY (= 20:00 -> 00:00 CT all year); at 01:00 NY a
buy stop at the high and a sell stop at the low (one cancels the other); stop = StopFrac x range width (1.0); no
target; out at 11:00 NY (= 10:00 CT). As coded, the orders stay armed after a stop-out (`armed` is only cleared at the
exit time), so it can re-enter the same day; the description says one trade a day - both are tested. The author's
claim (gold): Sharpe ~0.89, PF 1.18, 34% win. No gold data here (the user's GC feed stops at Oct 4), so NQ / ES.
Fills: the first minute through a level fills at the level (or the open if it gaps through) + 1 tick; a minute touching
both sides takes the side nearer its open. Costs $7.25 (ES $5) + 1 tick per stop / market fill, 1 contract, 2018-2026.
Grid: range end 00:00 / 02:00 (all of Asia) / 07:00 (to the European open hour); stop 1.0 / 0.5 x range; exit 10:00 /
12:00 / 15:00 CT; one trade a day vs re-entry. Placebo: same entry time, random side.
  python3 analysis/asian_breakout_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"NQ": (20.0, 0.25, 7.25), "ES": (50.0, 0.25, 5.0)}
SPLIT = pd.Timestamp("2023-01-01")


def run(g, sym, r_start=2000, r_end=0, exit_t=1000, frac=1.0, reentry=False, rand=None):
    pv, tick, comm = SPEC[sym]
    O, H, L, C = (getattr(g, a).ravel() for a in "ohlc")
    ts = pd.DatetimeIndex(g.ts); rng = np.random.default_rng(rand) if rand is not None else None
    rows = []
    for d in g.trading:
        if ts[d].year < 2018 or d == 0: continue
        s = (d - 1) * 1440 + jof(r_start); e_ = d * 1440 + jof(r_end) if r_end < r_start else (d - 1) * 1440 + jof(r_end)
        seg_h, seg_l = H[s:e_], L[s:e_]
        if np.isnan(seg_h).all(): continue
        rh, rl = np.nanmax(seg_h), np.nanmin(seg_l); w = rh - rl
        if not w > 0: continue
        tx = d * 1440 + jof(exit_t)
        t = e_
        while t < tx:
            hh, ll = H[t:tx], L[t:tx]
            hit = (hh >= rh) | (ll <= rl)
            if not np.nanmax(np.where(np.isnan(hh), 0, hit)): break
            k = t + int(np.argmax(np.nan_to_num(hit, nan=0)))
            up, dn = H[k] >= rh, L[k] <= rl
            side = (1 if abs(O[k] - rh) < abs(O[k] - rl) else -1) if (up and dn) else (1 if up else -1)
            t0 = k
            lvl = rh if side > 0 else rl
            en = (max(O[t0], lvl) if side > 0 else min(O[t0], lvl)) + side * tick
            if rng is not None: side = int(rng.choice([-1, 1]))
            sp = en - side * frac * w
            seg = L[t0:tx] <= sp if side > 0 else H[t0:tx] >= sp
            kind = 0
            if seg.any():
                k = t0 + int(np.argmax(seg)); t1 = k
                px = ((min(O[k], sp) if side > 0 else max(O[k], sp)) if k > t0 else sp) - side * tick
            else:
                cc = C[t0:tx]; ok = np.where(~np.isnan(cc))[0]; t1 = t0 + ok[-1]; px = cc[ok[-1]] - side * tick; kind = 2
            rows.append(dict(day=d, t0=t0, t1=t1, side=side, entry=en, exit=px, kind=kind, width=w,
                             net=(px - en) * side * pv - comm, date=ts[d]))
            if not reentry or kind == 2: break
            t = t1 + 1
    return pd.DataFrame(rows)


def line(t, nm, w=58):
    if len(t) < 5: return f"   {nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    L_, S_ = x[t.side > 0], x[t.side < 0]
    return (f"   {nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f} t {x.mean() / x.std() * np.sqrt(len(x)):4.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${x[y < 2023].mean():5.0f} 23-26 ${x[y >= 2023].mean():5.0f} | L ${L_.mean():5.0f} S ${S_.mean():5.0f}")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    G = {"NQ": pickle.load(open(SP + "g24.pkl", "rb")), "ES": pickle.load(open(SP + "ge.pkl", "rb"))}
    out = {}
    for sym, g in G.items():
        print(f"\n=== {sym}")
        lit = run(g, sym, reentry=True); lit1 = run(g, sym, reentry=False)
        print(line(lit, "as coded (20:00-00:00 CT, stop 1.0 x range, out 10:00, re-entry)"))
        print(line(lit1, "as described (one trade a day)"))
        print(f"      trades a day as coded: {lit.groupby('day').size().mean():.2f}; median range {lit1.width.median():.1f} points;"
              f" entries by hour {(lit1.t0 % 1440 // 60).value_counts().sort_index().to_dict()}")
        pl = [run(g, sym, rand=r).net.mean() for r in range(10)]
        print(f"      placebo (one a day, random side, 10 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs ${lit1.net.mean():.0f}")
        res = {}
        for r_end, frac, ex, re in itertools.product((0, 200, 700), (1.0, 0.5), (1000, 1200, 1500), (False, True)):
            nm = f"range 20:00-{r_end:04d}, stop {frac} x, out {ex}, {'re-entry' if re else 'one a day'}"
            res[nm] = run(g, sym, 2000, r_end, ex, frac, re)
        tt = pd.Series({k: v.net.mean() / v.net.std() * np.sqrt(len(v)) for k, v in res.items()}).sort_values(ascending=False)
        print(f"   grid of {len(res)}: t > 2 in {int((tt > 2).sum())}, t > 0 in {int((tt > 0).sum())}; top 6:")
        for k in tt.index[:6]: print(line(res[k], k))
        out[sym] = (lit1, res, tt)
    # standard metrics + bench for NQ literal and NQ best
    g = G["NQ"]; lit1, res, tt = out["NQ"]; best = res[tt.index[0]]
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    tab = {}
    for nm, t in (("NQ as described", lit1), (f"NQ best: {tt.index[0]}", best)):
        tab[nm] = (dl(t), t.net); tab["  longs " + nm[:20]] = (dl(t[t.side > 0]), t.net[t.side > 0]); tab["  shorts " + nm[:20]] = (dl(t[t.side < 0]), t.net[t.side < 0])
    print("\n" + M.table(tab))
    b_, p_ = R.report({"NQ as described 2023+": dl(lit1)[days >= SPLIT], "NQ best 2023+": dl(best)[days >= SPLIT]}, n=3000); print(b_); print(p_)
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    from bridge_monday_confirm import load_bridge_mc
    lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts2.year >= 2018
    x = dl(best).reindex(dts2[mk], fill_value=0.0)
    print("   correlation of the NQ best with the plan:", {k: round(float(np.corrcoef(x, pd.Series(lab.daily(k), index=dts2)[mk])[0, 1]), 2)
                                                         for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC")})
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, t in (("AB_LIT", lit1), ("AB_BEST", best)):
        bb = t.copy(); bb["j0"] = bb.t0 - bb.day * 1440; bb["j1"] = bb.t1 - bb.day * 1440; bb["slips"] = 0
        lab.add(nm, bb[["day", "j0", "j1", "side", "entry", "exit", "kind", "slips"]], slippage=False)
    for nm, p in (("current plan", plan), ("+ as described 1 MNQ", {**plan, "AB_LIT": 1}), ("+ best 1 MNQ", {**plan, "AB_BEST": 1}), ("+ best 2 MNQ", {**plan, "AB_BEST": 2})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<24} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
