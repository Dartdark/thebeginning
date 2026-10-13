"""Open-breakout pullback on 1-minute bars (user's follow-up, 2026-10-13). Same as analysis/open_pullback_test.py
(entry A: a bar touching the 8:30 open and closing back on the breakout side, stop past that bar's low / high), with
1-minute signal bars: the signal bar must come after the breakout minute (stops are a single minute's range, so
very tight). Breakout = any trade beyond X% (touch) or a 1-min close beyond X%.
Entry B (limit at the open) doesn't depend on the bar size: see the 5-minute test. Per NQ after $7.25 + 1 tick.
  python3 analysis/open_pullback_1m_test.py [SCRATCH_DIR]
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
        t = T.run(g, x, "A", tgt, sides=(side,), k=1, brk=brk, skip_break_bar=True); RES[(brk, side, x, tgt)] = t
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
    print(M.table({"best 1-min": (d, t.net)}))
    print("   by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    pickle.dump(dict(G=G), open(SP + "open_pullback_1m.pkl", "wb"))

