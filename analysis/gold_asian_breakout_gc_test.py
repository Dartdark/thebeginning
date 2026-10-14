"""Gold Asian-range breakout (user's file Gold_Asian_Breakout_Strategy.txt) on gold itself: GC 2018-2026 (user's export).

Same rules and engine as analysis/asian_breakout_test.py (range 20:00 -> 00:00 CT = 21:00 -> 01:00 NY, OCO stops at the
edges, stop 1.0 x range, no target, out 10:00 CT = 11:00 NY). GC: $100 a point, tick 0.10; $7.25 + 1 tick ($10) per fill,
1 GC (= 10 MGC). Author's claim: Sharpe ~0.89, PF 1.18, ~34% win, out-of-sample.
  1. As coded (re-entry after a stop) and as described (one trade a day); placebo (random side); by year; longs / shorts.
  2. Grid of 36 (range end 00:00 / 02:00 / 07:00, stop 1.0 / 0.5 x, out 10:00 / 12:00 / 15:00, one a day / re-entry),
     design 2018-22 vs holdout 2023-26.
  3. Standard metrics + bootstrap / permutation on 2023+; correlation with the plan; funded bench with MGC added
     (gold's own intraday adverse path).
  python3 analysis/gold_asian_breakout_gc_test.py [SCRATCH_DIR]
"""
import sys, os, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24
import asian_breakout_test as AB
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPLIT = pd.Timestamp("2023-01-01")
AB.SPEC["GC"] = (100.0, 0.10, 7.25)


def load_gc():
    pk = SP + "gc.pkl"
    if os.path.exists(pk):
        g = pickle.load(open(pk, "rb"))
        if pd.Timestamp(g.ts[g.trading[-1]]) >= pd.Timestamp("2026-10-01"): return g
    g = Grid24("data/GC_1min_20*.csv", night_pattern=""); pickle.dump(g, open(pk, "wb"), protocol=4); return g


def add_to_lab(lab, name, t, gc):
    """Inject a GC trade list into the funded lab: rows = $ per GC on the plan's trading days, worst intraday path from
    gold's own highs / lows; lab units are 1/10 (MGC like MNQ)."""
    pv, tick, comm = AB.SPEC["GC"]
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); W = np.zeros(len(dates)); C = np.zeros(len(dates))
    pos = pd.Series(np.arange(len(dates)), index=dates)
    H, L = gc.h.ravel(), gc.l.ravel()
    for r in t.itertuples():
        if r.date not in pos.index: continue
        i = pos[r.date]
        adv = (np.nanmin(L[r.t0:r.t1 + 1]) - r.entry) if r.side > 0 else (r.entry - np.nanmax(H[r.t0:r.t1 + 1]))
        W[i] = min(W[i], C[i] + min(adv * pv - comm, r.net))     # worst point of the day so far (conservative: applied all day)
        C[i] += r.net
    lab.W[name] = np.minimum(W, C)[:, None] / 10 * np.ones((1, lab.W["VB"].shape[1]))
    lab.C[name] = C / 10


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    gc = load_gc()
    print(f"GC sessions {len(gc.trading)} ({pd.Timestamp(gc.ts[gc.trading[0]]).date()} .. {pd.Timestamp(gc.ts[gc.trading[-1]]).date()})")
    lit = AB.run(gc, "GC", reentry=True); one = AB.run(gc, "GC")
    print("\n1. Rules as given")
    print(AB.line(lit, "as coded (re-entry after a stop)")); print(AB.line(one, "as described (one trade a day)"))
    print(f"      trades a day as coded {lit.groupby('day').size().mean():.2f}; median range {one.width.median():.1f} points (${one.width.median() * 100:,.0f} per GC)")
    pl = [AB.run(gc, "GC", rand=r).net.mean() for r in range(20)]
    print(f"      placebo (random side, 20 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs ${one.net.mean():.0f}")
    print("      by year (one a day): " + " | ".join(f"{y} ${v:,.0f}" for y, v in one.groupby(one.date.dt.year).net.sum().items()))
    res = {}
    for r_end, frac, ex, re in itertools.product((0, 200, 700), (1.0, 0.5), (1000, 1200, 1500), (False, True)):
        nm = f"range 20:00-{r_end:04d}, stop {frac} x, out {ex}, {'re-entry' if re else 'one a day'}"
        res[nm] = AB.run(gc, "GC", 2000, r_end, ex, frac, re)
    st = pd.DataFrame({k: dict(t=v.net.mean() / v.net.std() * np.sqrt(len(v)), d=v.net[v.date < SPLIT].mean(), h=v.net[v.date >= SPLIT].mean())
                       for k, v in res.items()}).T
    print(f"\n2. Grid of {len(res)}: t > 2 in {int((st.t > 2).sum())}, t > 0 in {int((st.t > 0).sum())};"
          f" design (2018-22) > 0 in {int((st.d > 0).sum())}, of which holdout > 0: {int(((st.d > 0) & (st.h > 0)).sum())}")
    for k in st.sort_values("d", ascending=False).index[:6]: print(AB.line(res[k], k))
    bestd = st.sort_values("d", ascending=False).index[0]; best = res[bestd]

    days = pd.DatetimeIndex(gc.ts[gc.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    tab = {}
    for nm, t in (("as described", one), ("best by 2018-22", best)):
        tab[nm] = (dl(t), t.net); tab[nm + " longs"] = (dl(t[t.side > 0]), t.net[t.side > 0]); tab[nm + " shorts"] = (dl(t[t.side < 0]), t.net[t.side < 0])
    print("\n3. Standard metrics per GC (best = " + bestd + ")\n" + M.table(tab))
    b_, p_ = R.report({"as described 2023+": dl(one)[days >= SPLIT], "best by 2018-22, 2023+": dl(best)[days >= SPLIT]}, n=3000); print(b_); print(p_)

    g = pickle.load(open(SP + "g24.pkl", "rb"))
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    from bridge_monday_confirm import load_bridge_mc
    lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts2.year >= 2018
    x = dl(one).reindex(dts2[mk], fill_value=0.0)
    print("   correlation (as described) with the plan:", {k: round(float(np.corrcoef(x, pd.Series(lab.daily(k), index=dts2)[mk])[0, 1]), 2)
                                                         for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC")})
    add_to_lab(lab, "GAB", one, gc); add_to_lab(lab, "GAB_BEST", best, gc)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    for nm, p in (("current plan", plan), ("+ gold breakout 1 MGC", {**plan, "GAB": 1}), ("+ gold breakout 2 MGC", {**plan, "GAB": 2}),
                  ("+ best-by-design 1 MGC", {**plan, "GAB_BEST": 1}), ("+ best-by-design 2 MGC", {**plan, "GAB_BEST": 2})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<26} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")

    print("\n4. In risk units (R = net / (range width x $100), removes gold's price level) and risk-sized in the funded bench")
    for nm, t in (("as described", one), ("best by 2018-22", best)):
        Rr = t.net / (t.width * 100.0); y = t.date.dt.year
        print(f"   {nm}: avg {Rr.mean():+.3f} R, t {Rr.mean() / Rr.std() * np.sqrt(len(Rr)):.1f}; by year " +
              " | ".join(f"{yy} {v:+.3f}" for yy, v in Rr.groupby(y).mean().items()) + f"; 2018-22 {Rr[y < 2023].mean():+.3f}, 2023-26 {Rr[y >= 2023].mean():+.3f}")
    # risk sizing: lab b = risk / (stop_pts x 2) for $2 / point / unit; MGC = $10 / point, so pass stop = width x 5
    st_arr = np.full(lab.D, 1e12); dpos = pd.Series(np.arange(lab.D), index=dts2)
    for r in one.itertuples():
        if r.date in dpos.index: st_arr[dpos[r.date]] = r.width * 5.0
    lab.stop["GAB"] = st_arr
    for risk in (100, 150, 250):
        p = {**plan, "GAB": ("risk", risk)}
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   + gold breakout risk ${risk} a trade (MGC count = risk / range $)  1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
    from speed_to_13k import run as speed, fmt
    print(fmt(pd.DataFrame({"current plan": speed(lab, plan, **CS), "+ gold risk $150": speed(lab, {**plan, "GAB": ("risk", 150)}, **CS),
                            "+ gold risk $250": speed(lab, {**plan, "GAB": ("risk", 250)}, **CS)}).T))
