"""GC_COMBO v2 from the user's MultiCharts report (2026-10-24, ETminusChart 0: the chart runs on New York time; parity with the
note: 1,204 trades 2017-09-18 -> 2026-08-07, every year's count and bp identical). Our costs per GC: $7.25 + 1 tick ($10) per
market / stop fill (entries, time exits, stops); targets none. Contracts as traded (1, 2 at |score| >= 3). Also writes the
trades in the bench format (CT grid row, entry / exit minute) for analysis/gc_combo_bench.py.
  python3 analysis/gc_combo_mc_eval.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from gc_combo_mc_check import load
from co_oc_reversal_test import line
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 100.0, 0.10, 7.25


def bench_trades(g):
    T = load(); T = T[T.t0 >= "2018-01-01"].reset_index(drop=True)
    t0, t1 = T.t0 - pd.Timedelta(hours=1), T.t1 - pd.Timedelta(hours=1)          # New York chart -> CT grid
    row = pd.Series(np.arange(g.D), index=pd.DatetimeIndex(g.ts))
    T["row"] = row.reindex(t0.dt.normalize()).values; T["date"] = t0.dt.normalize()
    T["j0"] = (t0.dt.hour * 60 + t0.dt.minute).values; T["j1"] = (t1.dt.hour * 60 + t1.dt.minute).values
    T["same_day"] = (t0.dt.normalize() == t1.dt.normalize()).values
    T["kind"] = np.where(T.xsig == "Profit Target", 1, np.where(T.xsig == "Stop Loss", 0, 2))
    T["sleeve"] = np.where(T.sig == "ST_S", "stretch", "blend")
    slips = 1 + (T.kind != 1)                                                      # entry always, exit unless target
    T["net"] = (T.x - T.e) * T.side * PV * T.q - (COMM + slips * TICK * PV) * T.q
    T["net1"] = T.net / T.q
    return T


def stats(x, nm, dd):
    p = M.perf(x.groupby(x.index).sum().reindex(dd, fill_value=0.0), x.values)
    return (f"   {nm:<24} Sharpe {p['sharpe']:5.2f} Sortino {p['sortino']:5.2f} PF {p['profit_factor']:4.2f} "
            f"Calmar {p['calmar']:5.2f} Ulcer {p['ulcer']:5.2f} maxDD ${p['max_dd']:,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "gc.pkl", "rb")); T = bench_trades(g)
    print(f"trades 2018 -> {T.date.max().date()}: {len(T)}, all intraday: {T.same_day.all()}; contracts {T.q.sum()}")
    s = lambda m=None, col="net": (T[col] if m is None else T[col][m]).set_axis(pd.DatetimeIndex(T.date if m is None else T.date[m]))
    IS, OOS = T.date < "2025-01-01", T.date >= "2025-01-01"; B, St = T.sleeve == "blend", T.sleeve == "stretch"
    print("\nper GC contract (net1), our costs:")
    for nm, m in (("COMBO", None), ("  IS 2018-24", IS), ("  OOS 2025-26", OOS), ("blend", B), ("  blend IS", B & IS), ("  blend OOS", B & OOS),
                  ("  blend longs", B & (T.side > 0)), ("  blend shorts", B & (T.side < 0)), ("  blend score 2 (1 lot)", B & (T.q == 1)),
                  ("  blend score >= 3 (2 lots)", B & (T.q == 2)), ("stretch short", St), ("  stretch IS", St & IS), ("  stretch OOS", St & OOS),
                  ("after the GCCOMBO file ends", T.date > "2026-09-25")):
        print(line(s(m, "net1"), nm, 30))
    print("\nby year, $ as traded:", s().groupby(lambda d: d.year).sum().round(0).to_dict())
    dd = pd.DatetimeIndex(pd.Series(pd.DatetimeIndex(g.ts[g.trading]))[lambda x: x >= "2018-01-01"])
    print("\nmetrics (daily, contracts as traded):")
    for nm, m in (("COMBO", None), ("blend", B), ("stretch", St), ("longs", T.side > 0), ("shorts", T.side < 0)):
        print(stats(s(m), nm, dd))
    d23 = dd[dd >= "2023-01-01"]; x = s(T.date >= "2023-01-01")
    print("\nresampling 2023+:"); print("\n".join(R.report({"COMBO": x.groupby(x.index).sum().reindex(d23, fill_value=0.0)})))
    y = s(); dy = y.groupby(y.index).sum().reindex(dd, fill_value=0.0)
    print(MC.report(y.values, dy, size=0.1, label="COMBO at 1-2 MGC"))
    y1 = s(None, "net1")
    print(f"      t per contract {y1.mean() / y1.std() * np.sqrt(len(y1)):.2f}; DSR at 296 items {M.deflated_sharpe(dy, 296):.2f}, "
          f"at the author's 10,831 {M.deflated_sharpe(dy, 10831):.2f}; bar t {M.t_threshold(296):.2f}")
    out = T[["date", "same_day", "sleeve", "side", "q", "e", "x", "kind", "row", "j0", "j1", "net", "bp"]].rename(columns={"q": "qty", "row": "day"})
    out.to_csv(SP + "gc_combo_trades_mc.csv", index=False); out.to_csv("checks/candidates/gc_combo/mc_trades.csv", index=False)
