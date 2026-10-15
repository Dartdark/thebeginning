"""VWAP Pullback + ADX gate with FIXED-POINT exits (community post + user's MC code VWAPADX_FIXED_POINTS, 2026-10-15): same
entries (long only, ADX(14) >= 20 and falling, 1 a day, swing levels still required for eligibility), exits replaced by a
fixed stop / target in NQ points; the author picked 120 / 80 from a 42-cell grid (SL 40-160 step 20, TP 20-120 step 20) on
2019-2026 and reports $157 a trade, PF 1.29 vs swing exits $72.
Here (our replica, NQ 2018-2026, $7.25 + 1 tick per market / stop fill, flat 15:55):
  A  the same 42-cell grid; best cell; PBO (CSCV, Bailey et al.) of picking the best cell; the 120 / 80 cell by year
  B  NQ quadrupled in price 2018 -> 2026: the same exits in ATR terms (120 / 80 points = their share of the 15-day ATR at its
     2018-26 median), by year, vs fixed points
  C  random-side placebo for 120 / 80 (same bars, mirrored distances)
  python3 analysis/vwap_adx_fixed_exits_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import vwap_orb_pullback_test as V
from candidates import adx
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); s = V.series(g)
    sh, sl = V.pivots(s["h"], s["l"], 20); th, tl = V.pivots(s["h"], s["l"], 5)
    A = adx(s["h"], s["l"], s["c"], 14); Ap = np.r_[np.nan, A[:-1]]; gate = (A >= 20) & (A <= Ap)
    run = lambda **kw: V.run(g, s, sh, sl, th, tl, apex=True, end_entry=1700, gate=gate, shorts=False, **kw)
    base = run(); print(V.line(base, "swing exits (base)"))
    grid = {}
    for SL in range(40, 161, 20):
        for TP in range(20, 121, 20):
            t = run(fsl=float(SL), ftp=float(TP)); grid[(SL, TP)] = t
    G = pd.DataFrame({k: dict(avg=v.net.mean(), t=v.net.mean() / v.net.std() * np.sqrt(len(v)), n=len(v)) for k, v in grid.items()}).T
    print("\nA. Grid, avg $ per trade (rows SL, cols TP):"); print(G.avg.unstack().round(0).to_string())
    print("   t-stat:"); print(G.t.unstack().round(2).to_string())
    best = G.t.idxmax(); print(f"   best by t: SL {best[0]} / TP {best[1]}; 120 / 80: avg ${G.loc[(120, 80), 'avg']:.0f}, t {G.loc[(120, 80), 't']:.2f}")
    days = pd.bdate_range("2018-01-01", "2026-10-09")
    Rm = pd.DataFrame({f"{k[0]}/{k[1]}": v.groupby(v.date).net.sum().reindex(days, fill_value=0.0) for k, v in grid.items()})
    pb = M.pbo(Rm, full=True); print(f"   PBO of picking the best cell: {pb['pbo']:.2f}, degradation slope {pb['degradation_slope']:+.2f}, P(loss) {pb['p_loss']:.2f}")
    t120 = grid[(120, 80)]; print(V.line(t120, "fixed 120 / 80"))
    print("   by year 120/80:", t120.groupby(t120.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   by year swing :", base.groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
    atr = g.daily_atr(15); med = np.nanmedian(atr[g.trading][pd.DatetimeIndex(g.ts[g.trading]).year >= 2018])
    ta = run(fsl=atr * 120 / med, ftp=atr * 80 / med)
    print(f"\nB. NQ median 15-day ATR {med:.0f}: 120 / 80 = {120 / med:.3f} / {80 / med:.3f} x ATR")
    print(V.line(ta, "ATR-scaled 120/80 equivalent")); print("   by year ATR:", ta.groupby(ta.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   120 points as % of the day's ATR: 2018", round(120 / np.nanmedian(atr[g.trading][pd.DatetimeIndex(g.ts[g.trading]).year == 2018]), 2),
          "2026", round(120 / np.nanmedian(atr[g.trading][pd.DatetimeIndex(g.ts[g.trading]).year == 2026]), 2))
    pl = [run(fsl=120.0, ftp=80.0, rand=r).net.mean() for r in range(20)]
    print(f"\nC. random-side placebo 120/80 (20 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs ${t120.net.mean():.0f}")
    rows = {"120/80": (t120.groupby(t120.date).net.sum().reindex(days, fill_value=0.0), t120.net),
            "swing": (base.groupby(base.date).net.sum().reindex(days, fill_value=0.0), base.net)}
    print("\nStandard metrics per NQ (long only):"); print(M.table(rows))
    b_, p_ = R.report({k: v[0][v[0].index >= "2023"] for k, v in rows.items()}, n=2000); print("2023+ bootstrap:\n" + b_)
