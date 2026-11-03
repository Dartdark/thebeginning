"""Bridge noise-area 15-min: the user's MultiCharts reports (2026-11-03, 'default session' and '24 hr', both @NQ 15-min,
2 contracts, no commission / slippage) vs the Python port (analysis/bridge_noise_15m_test.py, 24h chart). Matches entries
by date + bar time + side, then puts MC's trades at our costs ($7.25 + 1 tick per market / stop fill, target = limit), per NQ.
  python3 analysis/bridge_noise_15m_mc_check.py > analysis/outputs/bridge_noise_15m_mc_check_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M

R = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Noise {}.xlsx"


def load(nm):
    raw = pd.read_excel(R.format(nm), sheet_name="List of Trades", header=2)
    en = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
    ex = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    side = np.where(en.Type.str.contains("Long"), 1, -1); q = en.Contracts.to_numpy(float)
    gross = (ex.Price.to_numpy(float) - en.Price.to_numpy(float)) * side * 20.0
    tgt = ex.Signal.astype(str).str.contains("Profit", case=False)
    slip = np.where(tgt, 1, 2) * 0.25 * 20.0                        # 1 tick entry + 1 tick on non-limit exits
    t = pd.DataFrame({"dt": pd.to_datetime(en.Date), "xdt": pd.to_datetime(ex.Date), "side": side, "entry": en.Price.to_numpy(float),
                      "exit": ex.Price.to_numpy(float), "signal": en.Signal, "xsignal": ex.Signal, "gross": gross,
                      "net": gross - slip - 7.25, "mc_profit": ex.index.map(lambda i: np.nan)})
    t["mc_profit_report"] = en["Profit ($)"].to_numpy(float) / q
    t["date"] = t.dt.dt.normalize(); t["hhmm"] = t.dt.dt.hour * 100 + t.dt.dt.minute
    return t


def tst(x): x = pd.Series(x); return x.mean() / x.std() * np.sqrt(len(x))


def pf(x): x = pd.Series(x); return x[x > 0].sum() / -x[x < 0].sum()


def line(t, nm):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); a, b = x[y < 2023], x[y >= 2023]
    return (f"   {nm:<34} n={len(x):5d} ${x.mean():5.1f} PF {pf(x):4.2f} t {tst(x):4.1f} yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${a.mean():5.1f} t {tst(a):4.1f}"
            f" | 23+ ${b.mean():5.1f} t {tst(b):4.1f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    A, B = load("default session"), load("24 hr")
    same = len(A) == len(B) and (A[["dt", "side", "entry", "exit"]].values == B[["dt", "side", "entry", "exit"]].values).all()
    print(f"\n1. The two reports: {len(A)} and {len(B)} trades, identical trade lists: {same}. The 'default session' is the 24-hour CME session"
          f" (trades {A.dt.min().date()} -> {A.dt.max().date()}).")
    print(f"   MC gross per NQ (2 contracts / 2): ${A.gross.sum():,.0f} over {A.date.dt.year.nunique()} years = ${A.gross.mean():.1f} a trade before costs")
    P = pd.read_csv("analysis/outputs/bridge_noise_15m_trades_24h.csv", parse_dates=["date"])
    P = P[P.date >= A.date.min()]
    P["hhmm"] = P.t0.astype(int); P["e_hhmm"] = ((P.t0 // 100) * 60 + P.t0 % 100 - 15).pipe(lambda m: (m // 60) * 100 + m % 60)
    key = lambda d, h, s: list(zip(d, h, s))
    mk = set(key(A.date, A.hhmm, A.side))
    for col, nm in (("hhmm", "bar close time"), ("e_hhmm", "bar open time")):
        pk = set(key(P.date, P[col], P.side)); m = len(mk & pk)
        print(f"   entries matched by date + {nm} + side: {m} of MC {len(mk)} / port {len(pk)} ({m / len(mk):.1%})")
    print("\n2. MC's trades at our costs ($7.25 + 1 tick per market / stop fill), per 1 NQ:")
    print(line(A, "MC 24h, both sides")); print(line(A[A.side > 0], "MC 24h, longs")); print(line(A[A.side < 0], "MC 24h, shorts"))
    print("   by year $ (both):", A.groupby(A.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   by year $ (longs):", A[A.side > 0].groupby(A.date.dt.year).net.sum().round(0).astype(int).to_dict())
    Pp = P[P.date <= A.date.max()]
    print(line(Pp.assign(date=Pp.date), "port 24h, same window (both)"))
    print(f"\n3. Scale: MC net ${A.gross.sum() * 2:,.0f} at 2 NQ and zero costs = ${A.gross.sum() * 2 / A.date.dt.year.nunique():,.0f} a year;"
          f" at our costs ${A.net.sum() * 2:,.0f} = ${A.net.sum() * 2 / A.date.dt.year.nunique():,.0f} a year at 2 NQ,"
          f" ${A.net.sum() / 10 / A.date.dt.year.nunique():,.0f} a year per MNQ (longs only ${A[A.side > 0].net.sum() / 10 / A.date.dt.year.nunique():,.0f}).")
    d = A.groupby("date").net.sum(); e = d.cumsum()
    print(f"   max closed-trade drawdown at our costs, per NQ ${-(e - e.cummax()).min():,.0f} (= ${-(e - e.cummax()).min() / 10:,.0f} per MNQ); MC's own "
          f"max strategy drawdown at 2 NQ, zero costs: $27,890")
