"""Twin Continuation: the author's 'Build Something Of Your Own' ideas (user 2026-11-08). PRE-REGISTERED (header committed with the
variant code before the first run; 6 trials). Base = Twin cap1 (breakout stop <= 1 ATR), as in twin_cap1_150k_eval.py.
  levels  1 prevday: prior session high / low   2 prevweek: prior ISO week high / low   3 round100: next 100-point level up / down
          (each replaces the 6-hour swing levels; stop at the opposite level, capped at 1 ATR; untested-level rule kept)
  trigger 4 MO window 13:30-14:30 CT (closer to Baltussen's last half hour; exit 14:50 unchanged)
  regime  5 off when the 60-session lag-1 autocorrelation of daily RTH returns (known the day before) < 0
          6 off when the 120-session variance ratio VR(5) (known the day before) < 1
Per variant: trades, $ a trade per NQ, t, 2018-19 / 2020-22 / 2023+, and the 150K evaluation with Twin at 2 MNQ added to the set
(corrected engine), paired vs the base Twin cap1.
  tools/run_stamped.sh analysis/twin_ideas_test.py > analysis/outputs/twin_ideas_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30
from plan_150k_test import evaluation, R150
import twin_continuation_test as tc
from twin_continuation_bench import grids
from grid24 import jof

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    dts = pd.DatetimeIndex(g.ts[trr]); cl = pd.Series(g.c[trr, jof(1500)], index=dts).ffill(); r = cl.pct_change()
    ac = r.rolling(60).corr(r.shift(1)).shift(1)
    r5 = cl.pct_change(5); vr = (r5.rolling(120).var() / (5 * r.rolling(120).var())).shift(1)
    off_ac = set(int(d.strftime("%Y%m%d")) for d in dts[(ac < 0).to_numpy()]); off_vr = set(int(d.strftime("%Y%m%d")) for d in dts[(vr < 1).to_numpy()])
    print(f"   regime filters off on {len(off_ac) / D:.0%} (autocorrelation) / {len(off_vr) / D:.0%} (variance ratio) of trading days")
    P = {}
    for k, t in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
                 "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, rr = paths(g, t); P[k] = (w[trr] / 10, rr[trr] / 10)
    risk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    base = {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}
    B = tc.flatten(g); ok = yr >= 2018
    def evalpass(Wt, Rt):
        Wc = sum(P[k][0] * v for k, v in base.items()) + 2 * Wt; Rc = sum(P[k][1] * v for k, v in base.items()) + 2 * Rt
        res = [evaluation(Wc, Rc, s, D, R150) for s in range(D)]
        return np.array([x[0] if x else "" for x in res]), ok & np.array([x is not None for x in res])
    V = {"base Twin cap1": {}, "1 levels: prior day": dict(level_mode="prevday"), "2 levels: prior week": dict(level_mode="prevweek"),
         "3 levels: round 100s": dict(level_mode="round100"), "4 MO window 13:30-14:30": dict(mo_window=(1330, 1430)),
         "5 regime: autocorrelation": dict(off_dates=off_ac), "6 regime: variance ratio": dict(off_dates=off_vr)}
    o0 = None
    for nm, kw in V.items():
        T = tc.simulate(B, max_stop_mult=1.0, **kw); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
        x = T.net; tt = x.mean() / x.std(ddof=1) * np.sqrt(len(x))
        seg = lambda a, b: T[(T.date.dt.year >= a) & (T.date.dt.year <= b)].net
        Wt, Rt = grids(g, B, T); o, v = evalpass(Wt[trr] / 10, Rt[trr] / 10); ps = (o == "pass")
        if o0 is None: o0, v0 = o, v
        d = (ps.astype(float) - (o0 == "pass").astype(float))[v & v0]
        bo, mo = T[T.setup == "BO"].net, T[T.setup == "MO"].net
        print(f"\n   {nm:<28} n {len(T):5d} ${x.mean():5.0f} t {tt:5.2f} PF {x[x > 0].sum() / -x[x < 0].sum():4.2f} | 18-19 ${seg(2018, 2019).mean():5.0f} 20-22 ${seg(2020, 2022).mean():5.0f} 23+ ${seg(2023, 2026).mean():5.0f}"
              f" | BO n {len(bo)} ${bo.mean():.0f} / MO n {len(mo)} ${mo.mean():.0f}")
        print(f"      150K eval + 2 MNQ: pass {ps[v].mean():5.1%} (18-22 {ps[v & (yr < 2023)].mean():5.1%}, 23+ {ps[v & (yr >= 2023)].mean():5.1%}) | vs base {d.mean():+.1%}", flush=True)
