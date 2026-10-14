"""Cross-asset overnight signals for NQ and the plan (2026-10-14; new data: GC, CL, BTC, ES, YM).

Idea: the overnight moves of gold, oil and bitcoin (and the risk-on / risk-off mix of them) are known at the 8:30 CT
open and might say something about NQ's day or about the plan's trades that NQ's own overnight move doesn't.
Features (known at 8:25 CT): each market's overnight return from the previous 15:00 CT close to 8:25 CT, as a z-score
against its own trailing 60-day overnight std:
  A gold z   B oil z   C bitcoin z (from Dec 2018)   D risk-off = gold z - oil z (gold up and oil down = risk-off)
  E risk-off with bitcoin = gold z - (oil z + bitcoin z) / 2
Targets: NQ 8:30 -> 15:00 (long, $ per NQ before costs); the plan's MultiCharts trades per day (VB, ONB ML v2,
Late-Day Flow, Monday Long), net $.
Protocol: terciles of each feature; 5 features x 5 targets = 25 splits, so a split counts only if top-minus-bottom
has |t| >= 2.5 over 2018-2026 AND the same sign in 2018-22 and 2023-26. Controls: NQ's own overnight z and the
ES / YM overnight z (to see whether a commodity signal is just the equity overnight move in disguise).
  python3 analysis/cross_asset_overnight_test.py [SCRATCH_DIR]
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24, jof
from cl_forced_flows_test import load
from time_clusters_test import trades as plan_trades

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPLIT = pd.Timestamp("2023-01-01")


def overnight(G):
    cf = pd.Series(G.c.ravel()).ffill().to_numpy(); tr = G.trading
    idx = pd.DatetimeIndex(G.ts[tr])
    c825 = pd.Series(cf[tr * 1440 + jof(825)], index=idx); c1500 = pd.Series(cf[tr * 1440 + jof(1500)], index=idx)
    r = np.log(c825 / c1500.shift(1))
    z = r / r.rolling(60, min_periods=40).std().shift(1)
    return z


def btc():
    pk = SP + "btc.pkl"
    if os.path.exists(pk): return pickle.load(open(pk, "rb"))
    G = Grid24("BTC_1min_20*.csv", night_pattern=""); pickle.dump(G, open(pk, "wb"), protocol=4); return G


def tstat_diff(a, b):
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    if len(a) < 10 or len(b) < 10: return np.nan
    return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb")); ym = pickle.load(open(SP + "gy.pkl", "rb"))
    gc, cl, bt = load("GC"), load("CL"), btc()
    Z = pd.concat({"gold": overnight(gc), "oil": overnight(cl), "btc": overnight(bt), "nq": overnight(g), "es": overnight(es), "ym": overnight(ym)}, axis=1)
    Z = Z[Z.index >= "2018-01-01"]
    F = pd.DataFrame({"A gold": Z.gold, "B oil": Z.oil, "C bitcoin": Z.btc, "D risk-off (gold - oil)": Z.gold - Z.oil,
                      "E risk-off incl. bitcoin": Z.gold - (Z.oil + Z.btc) / 2})
    CTRL = pd.DataFrame({"control: NQ overnight": Z.nq, "control: ES overnight": Z.es, "control: YM overnight": Z.ym})
    print("\nCorrelations of the overnight z-scores:")
    print(Z.corr().round(2).to_string())

    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); tr = g.trading; idx = pd.DatetimeIndex(g.ts[tr])
    rth = pd.Series((cf[tr * 1440 + jof(1500)] - g.o[tr, jof(831)]) * 20.0, index=idx)
    T = plan_trades(g)
    day = lambda t: t.groupby(t.date.dt.normalize()).net.sum()
    TGT = {"NQ 8:30-15:00 long": rth, "VB": day(T["VB"]), "ONB ML v2": day(T["ONB_ML2_MC"]), "Late-Day Flow": day(T["LDF_MC"]), "Monday Long": day(T["MON_MC"])}

    rows = []
    for fset, FF in (("feature", F), ("control", CTRL)):
        for fn in FF:
            f = FF[fn]
            for tn, y in TGT.items():
                d = pd.concat([f.rename("f"), y.rename("y")], axis=1).dropna()
                if len(d) < 60: continue
                q = d.f.expanding(120).apply(lambda v: (v[:-1] < v[-1]).mean(), raw=True)     # tercile by trailing ranks (no look-ahead)
                lo, hi = d.y[q < 1 / 3], d.y[q >= 2 / 3]; mid = d.y[(q >= 1 / 3) & (q < 2 / 3)]
                e = lambda s, a, b: s[(s.index >= a) & (s.index < b)]
                row = dict(set=fset, feature=fn, target=tn, n=len(d), low=lo.mean(), mid=mid.mean(), high=hi.mean(), t=tstat_diff(hi, lo),
                           t_18_22=tstat_diff(e(hi, "2018", SPLIT), e(lo, "2018", SPLIT)), t_23_26=tstat_diff(e(hi, SPLIT, "2027"), e(lo, SPLIT, "2027")))
                row["passes"] = abs(row["t"]) >= 2.5 and np.sign(row["t_18_22"]) == np.sign(row["t_23_26"]) and fset == "feature"
                rows.append(row)
    R = pd.DataFrame(rows)
    print("\nTercile means ($; high minus low t over 2018-26 and per period; terciles from trailing ranks):")
    print(R.to_string(index=False, float_format=lambda v: f"{v:,.1f}"))
    print(f"\nsplits passing (|t| >= 2.5 and same sign in both periods): {int(R.passes.sum())} of {int((R.set == 'feature').sum())}")
    print(R[R.passes].to_string(index=False, float_format=lambda v: f"{v:,.1f}") if R.passes.any() else "   none")
    pickle.dump(dict(Z=Z, R=R), open(SP + "cross_asset.pkl", "wb"))
