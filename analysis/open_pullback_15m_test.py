"""Open-breakout pullback on 15-minute bars (user's follow-up, 2026-10-13). Same as analysis/open_pullback_test.py
(entry A: a bar touching the 8:30 open and closing back on the breakout side, stop past that bar's low / high), with
15-minute signal bars: the signal bar must come after the bar holding the breakout (inside a 15-min bar the order of
breakout and touch is unknown). Breakout = any trade beyond X% ('touch', as before) or a 15-min close beyond X%.
Entry B (limit at the open) doesn't depend on the bar size: see the 5-minute test. Per NQ after $7.25 + 1 tick.
  python3 analysis/open_pullback_15m_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import open_pullback_test as T
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    print(__doc__.split("\n")[0])
    rows = []; RES = {}
    for brk, side, x, tgt in itertools.product(("touch", "close"), (1, -1), T.XS, T.TGTS):
        t = T.run(g, x, "A", tgt, sides=(side,), k=15, brk=brk, skip_break_bar=True); RES[(brk, side, x, tgt)] = t
        s = T.stats(t)
        rows.append(dict(brk=brk, side="long" if side > 0 else "short", x=x, tgt=str(tgt), **{k: s[k] for k in ("n", "avg", "pf", "t", "d", "h", "yrs")}))
    G = pd.DataFrame(rows); pd.set_option("display.width", 200)
    for brk in ("touch", "close"):
        for sd in ("long", "short"):
            q = G[(G.brk == brk) & (G.side == sd)]
            print(f"\n{sd.upper()}S, breakout = {brk}: sorted by design (2018-22) average")
            print(q.sort_values("d", ascending=False).to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
            print(f"   design avg > 0: {np.mean(q.d > 0):.0%}; of those holdout > 0: {np.mean(q[q.d > 0].h > 0):.0%}; best t {q.t.max():.1f}")
    best = G.loc[G.t.idxmax()]
    print(f"\nBest of all {len(G)} by full-period t: {best.to_dict()}")
    t = RES[(best.brk, 1 if best.side == "long" else -1, best.x, None if best.tgt == "None" else (best.tgt if best.tgt == "ext" else float(best.tgt)))]
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    d = t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print(M.table({"best 15-min": (d, t.net)}))
    print("   by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    pickle.dump(dict(G=G), open(SP + "open_pullback_15m.pkl", "wb"))

    print("\nChecks on the best 15-min long versions (0.15% touch breakout, 3R and no target):")
    from grid24 import jof
    from bridge_monday_confirm import load_bridge_mc
    ts = pd.DatetimeIndex(g.ts); atr = g.daily_atr(15)
    for tgt in (3.0, None, 2.0):
        tt = T.run(g, 0.15, "A", tgt, sides=(1,), k=15, brk="touch", skip_break_bar=True)
        print(T.line(tt, f"long 0.15% 15-min target {tgt}"))
        pl = []
        for r in tt.itertuples():                     # SHORT at the same fills, mirrored stop / target
            d = int(r.day); e = r.entry; risk = r.risk; stop = e + risk; tp = e - tgt * risk if tgt else None
            O, H, L, C = g.o[d], g.h[d], g.l[d], g.c[d]; px = None
            for j in range(int(r.j0), jof(1455) + 1):
                if np.isnan(H[j]): continue
                if H[j] >= stop: px = (max(O[j], stop) if j > r.j0 else stop) + T.TICK; break
                if tp is not None and L[j] <= tp: px = min(O[j], tp) if j > r.j0 else tp; break
            if px is None:
                cc = C[int(r.j0):jof(1455) + 1]; px = cc[~np.isnan(cc)][-1] + T.TICK
            pl.append(dict(date=r.date, side=-1, net=(e - px) * T.PV - T.COST))
        print(T.line(pd.DataFrame(pl), "   placebo: short at the same fills"))
        if tgt == 3.0: best3 = tt
    rnd = []                                          # control: long at the same time of day on random other days
    rng = np.random.default_rng(1); tr = [d for d in g.trading if ts[d].year >= 2018]
    for r in best3.itertuples():
        d = int(rng.choice(tr)); j0 = int(r.j0); o = g.o[d, j0]; c = g.c[d, jof(1455)]
        if np.isnan(o) or np.isnan(c): continue
        risk = r.risk; stop, tp = o - risk, o + 3 * risk; px = None
        for j in range(j0, jof(1455) + 1):
            if np.isnan(g.h[d, j]): continue
            if g.l[d, j] <= stop: px = stop - T.TICK; break
            if g.h[d, j] >= tp: px = tp; break
        if px is None: px = c - T.TICK
        rnd.append(dict(date=ts[d], side=1, net=(px - o - T.TICK) * T.PV - T.COST))
    print(T.line(pd.DataFrame(rnd), "control: long, same time / stop / 3R, random days"))
    d3 = best3.groupby(best3.date).net.sum().reindex(days, fill_value=0.0)
    print(M.table({"long 0.15% 15-min 3R": (d3, best3.net)}))
    bt, pm = R.report({"2023+": d3[d3.index >= "2023-01-01"]}, n=3000); print(bt); print(pm)
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    stop_pts = np.full(g.D, np.nan); stop_pts[best3.day.values] = best3.risk.values
    lab.add("OPB15", best3, stop_pts=stop_pts, slippage=False)
    dts = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts.year >= 2018
    C_ = pd.DataFrame({k_: lab.daily(k_) for k_ in ("OPB15", "VB", "ONB_ML2_MC", "MON_MC", "LDF_MC")}, index=dts)[mk]
    print("   correlation:", C_.corr().round(2).loc["OPB15"].drop("OPB15").to_dict())
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500),
            "VCS_MC": 1, "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    print("Funded bench (8-strategy plan; + this at RiskPerTrade with its own bar-low stop):")
    for nm, p in (("current plan", plan), ("+ $200", {**plan, "OPB15": ("risk", 200)}), ("+ $300", {**plan, "OPB15": ("risk", 300)})):
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<14} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
    print("Combine (VB 8 + ONB ADX30 $1,100 + Bridge Monday 2 + EOS $500 + VCS 2, + this at $X risk):")
    from portfolio import load_mc, paths, challenge
    from funded_lab import with_slippage
    from build_lab import REPORTS
    tr_ = g.trading; D = len(tr_); yr = pd.DatetimeIndex(g.ts[tr_]).year
    P = {}
    for nm, t_ in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB", with_slippage(load_mc(g, "Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx"))),
                   ("MBR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))), ("VCS", with_slippage(load_mc(g, REPORTS["VCS_MC"][0]))), ("OPB", best3)):
        w, r_ = paths(g, t_); P[nm] = (w[tr_] / 10, r_[tr_] / 10)
    rk = lambda dl_, s_: np.floor(dl_ / (np.nan_to_num(s_[tr_], nan=1e12) * 2))[:, None]
    base = [(P["VB"], 8), (P["ONB"], rk(1100, 0.25 * atr)), (P["MBR"], 2), (P["EOS"], rk(500, 0.30 * atr)), (P["VCS"], 2)]
    for nm, extra in (("current combine set", None), ("+ open pullback 15-min $500", 500), ("+ $1,000", 1000)):
        parts = base + ([(P["OPB"], rk(extra, stop_pts))] if extra else [])
        W = sum(p_[0] * q for p_, q in parts); Rr = sum(p_[1] * q for p_, q in parts)
        res = [challenge(W, Rr, np.arange(s, min(s + 21, D))) for s in range(D)]
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        print(f"   {nm:<30} pass {np.nanmean(o[yr >= 2018]):.1%} | 2023-26 {np.nanmean(o[yr >= 2023]):.1%}")
