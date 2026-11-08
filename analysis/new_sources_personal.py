"""The 5 'new sources' on the PERSONAL book (user 2026-11-08: would the outcome differ without Apex rules?). Measure as the personal
ladder: 1-year Monte Carlo (20-day blocks, 2,000 runs) $ p50, bad year p5, DD p95, return / DD, capital = DD p95 / 0.2.
Book = the cleared personal pieces at 1 micro (personal_portfolio.py minus the forward-log pieces). Each piece added at 1 micro, per micro
(full-contract $ / 10, + $0.55 extra micro commission per trade). Personal versions where they differ from the Apex ones:
  long after a green day: the full rule (15:00 -> next 15:00, 0.5% stop; long_after_green_test.py), overnight allowed
  double top / bottom 60-min, gold Asian range (MGC), Vol-Control Sell, turn of the month (RTH days -1..+3): as in new_sources_150k.py
Scored on 2018-26, 2018-22 and 2023+ (the regime check that sank VIX sizing).
  tools/run_stamped.sh analysis/new_sources_personal.py > analysis/outputs/new_sources_personal_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from grid24 import jof
from long_after_green_test import run as lag_run, candles
import asian_breakout_test as AB
from gold_asian_breakout_gc_test import load_gc
from candlestick_patterns_test import rth_bars
from chart_patterns_test import pivots_signals
from new_sources_150k import path_exit

FWD = ["FC2B", "Kusho", "S47", "S30"]; TICK, COMM, PV, EXTRA = 0.25, 7.25, 20.0, 0.55


def mc(x):
    d = MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1); return d["pnl_p50"], d["pnl_p5"], d["dd_p95"]


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    P = pd.read_pickle("scratch_data/personal_P.pkl"); P = P[[c for c in P.columns if c not in FWD]]; idx = P.index
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = list(g.trading); dts = pd.DatetimeIndex(g.ts[trr])
    J0, J1 = jof(831), jof(1500); op, cl = g.o[trr, J0], g.c[trr, J1]
    S = {}
    def daily(dates, net): return pd.Series(np.asarray(net) / 10 - EXTRA, index=pd.DatetimeIndex(dates)).groupby(level=0).sum().reindex(idx, fill_value=0.0)
    o_, c_, ks, keep = candles(g); t = lag_run(g, PV, COMM, ks[keep & (c_ > o_)]); S["long after green (full)"] = daily(t.date, t.net)
    B = rth_bars(g, 60); Sg = pivots_signals(B); a60 = (B.h - B.l).rolling(14, min_periods=10).mean().to_numpy(); rows = []
    for nm, s in (("DTOP", -1), ("DBOT", 1)):
        for i in np.nonzero(Sg[nm][0])[0]:
            r, j = int(B.row[i]), int(B.j[i])
            if j >= jof(1430) or np.isnan(a60[i]): continue
            j0, j1 = j + 1, min(j + 240, jof(1459)); oo = g.o[r, j0:j1 + 1]; okk = ~np.isnan(oo)
            if not okk.any(): continue
            e = oo[okk][0] + s * TICK; x, _ = path_exit(g, [(r, j0, j1)], s, e, a60[i]); rows.append((pd.Timestamp(g.ts[r]), (x - s * TICK - e) * s * PV - COMM))
    d_ = pd.DataFrame(rows, columns=["d", "n"]); S["double top / bottom"] = daily(d_.d, d_.n)
    gc = load_gc(); AB.SPEC["GC"] = (100.0, 0.10, 7.25); tg = AB.run(gc, "GC", 2000, 200, 1200, 1.0, False); S["gold Asian range"] = daily(tg.date, tg.net)
    lab = pickle.load(open("scratch_data/lab.pkl", "rb")); ld = pd.DatetimeIndex(lab.g.ts[lab.tr]); v = lab.C["VCS_MC"] * 10
    S["Vol-Control Sell"] = daily(ld[v != 0], v[v != 0])
    mon = dts.month.to_numpy(); last = np.r_[mon[1:] != mon[:-1], False]; first = np.r_[False, mon[1:] != mon[:-1]]; tom = np.zeros(len(trr), bool)
    for k in range(len(trr)):
        if last[k]: tom[k] = True
        if first[k]: tom[k:k + 3] = True
    rows = []
    for k in np.nonzero(tom)[0]:
        r = trr[k]; a = atr[r - 1] if r > 0 else np.nan
        if np.isnan(op[k]) or not np.isfinite(a): continue
        e = g.o[r, J0] + TICK; x, _ = path_exit(g, [(r, J0, J1)], 1, e, 0.5 * a); rows.append((dts[k], (x - TICK - e) * PV - COMM))
    d_ = pd.DataFrame(rows, columns=["d", "n"]); S["turn of the month"] = daily(d_.d, d_.n)
    print(f"   book: {list(P.columns)}")
    for per, m in (("2018-26", np.ones(len(P), bool)), ("2018-22", idx.year <= 2022), ("2023+", idx.year >= 2023)):
        p50, p5, dd = mc(P[m].sum(axis=1))
        print(f"\n{per}: {'book as is':<28}${p50:>9,.0f} p5 ${p5:>8,.0f} DD ${dd:>7,.0f} ret/DD {p50 / dd:5.2f}")
        for nm, x in S.items():
            q50, q5, qd = mc((P.sum(axis=1) + x)[m]); c = P.sum(axis=1)[m].corr(x[m])
            print(f"         + {nm:<26}${q50:>9,.0f} p5 ${q5:>8,.0f} DD ${qd:>7,.0f} ret/DD {q50 / qd:5.2f} ({q50 / qd - p50 / dd:+.2f}) corr {c:+.2f}")
