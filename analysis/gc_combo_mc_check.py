"""GC_COMBO v2: the user's MultiCharts report (2026-10-24, @GC 1-min + @CL + GCCOMBO, no costs) vs the author's note and our
rebuild: trade counts by year and sleeve, which clock the chart ran on (entry prices vs our CT grid), day / side matches.
  python3 analysis/gc_combo_mc_check.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
REP = "mc_reports/Backtesting Strategy Performance Report _ @GC - 1 Minute GC COMBO v2.xlsx"


def load(path=REP):
    t = pd.read_excel(path, sheet_name="List of Trades", header=2)
    en = t[t.Type.astype(str).str.startswith("Entry")].reset_index(drop=True); ex = t[t.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    T = pd.DataFrame(dict(sig=en.Signal.values, xsig=ex.Signal.values, t0=pd.to_datetime(en.Date).values, t1=pd.to_datetime(ex.Date).values,
                          e=en.Price.astype(float).values, x=ex.Price.astype(float).values, q=en.Contracts.values.astype(int),
                          pnl=en["Profit ($)"].values.astype(float)))
    T["side"] = np.where(T.sig == "BL_L", 1, -1); T["day"] = T.t0.dt.normalize()
    T["bp"] = (T.x - T.e) / T.e * 1e4 * T.side
    return T


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    T = load(); g = pickle.load(open(SP + "gc.pkl", "rb")); row = pd.Series(np.arange(g.D), index=pd.DatetimeIndex(g.ts))
    w = T[(T.t0 >= "2017-09-18") & (T.t0 <= "2026-08-07")]
    print(f"trades {len(T)} ({T.t0.min().date()} -> {T.t0.max().date()}); author window 2017-09-18 -> 2026-08-07: {len(w)} trades "
          f"(note ~1,204), net before costs ${w.pnl.sum():,.0f}, {w.q.sum()} contracts")
    print("   signals:", T.sig.value_counts().to_dict(), "| exits:", T.xsig.value_counts().to_dict())
    note = {2018: 122, 2019: 136, 2020: 123, 2021: 133, 2022: 156, 2023: 119, 2024: 156, 2025: 157}
    by = T.groupby(T.t0.dt.year).agg(n=("bp", "size"), bp=("bp", "mean")); by["note_n"] = pd.Series(note)
    by["note_bp"] = pd.Series({2018: 3.5, 2019: 5.9, 2020: 15.7, 2021: 4.1, 2022: 6.3, 2023: 5.9, 2024: 8.8, 2025: 1.6})
    print(by.round(1).to_string())
    B = T[T.sig.str.startswith("BL") & (T.t0 >= "2018-01-01")]
    for lag in (801, 901, 1001):
        m = [abs(g.o[row[d], jof(lag)] - e) <= 0.2 for d, e in zip(B.day, B.e) if d in row.index and np.isfinite(g.o[row[d], jof(lag)])]
        print(f"   blend entry price = our open at {lag} CT on {np.mean(m):.0%} of trades")
    P = pd.read_csv("checks/candidates/gc_combo/python_trades_proxyB.csv", parse_dates=["date"])
    Pb = P[P.sleeve == "blend"].drop(columns=["day"]).rename(columns={"date": "day"}); j = B.merge(Pb, on="day", how="outer", suffixes=("_mc", "_py"), indicator=True)
    both = j[j._merge == "both"]
    print(f"   blend days: MC only {(j._merge == 'left_only').sum()}, Python only {(j._merge == 'right_only').sum()}, both {len(both)}, "
          f"same side {np.mean(both.side_mc == both.side_py):.0%} (vote B differs by construction)")
    Ms = T[(T.sig == "ST_S") & (T.t0 >= "2018-01-01")]; Ps = P[P.sleeve == "stretch"]
    print(f"   stretch: MC {len(Ms)}, Python {len(Ps)}, same days {len(set(Ms.day) & set(Ps.date))}")
