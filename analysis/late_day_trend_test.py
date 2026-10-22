"""Intraday trend seasonality (Concretum Research, 'The Intraday Seasonality of Market Trends', Aug 2026, user's PDF): on SPY,
an ensemble of 6 intraday trend models earned ~60% of its P&L in the last hour 2007-26, but since 2023 trends REVERSE in the
last 15 minutes (15:45-16:00 ET = 14:45-15:00 CT), giving back ~30% of the day's trend P&L; they suggest cutting part of the
trend exposure 15 minutes before the close (0DTE dealer hedges unwinding is their hypothesis).
Here, NQ 1-min 2018-2026 (CT):
  A  two of their trend models, minute by minute, 8:31-15:00 CT, gross bp per 15-min bucket, 2018-22 vs 2023-26:
     VWAP model (#6): long above the session VWAP (from 8:30), short below; 'from-open' model: long above the 8:30 open, short below
  B  the plan's strategies that hold into the last 15 minutes: Monday Long (exit 15:00 CT) and the Bridge Monday Long
     (exit 15:55 CT or 100-pt target): P&L of the open trades from 14:45 to the exit, per NQ, by period; and Monday Long
     with the exit moved to 14:45 (gross, same trades)
  python3 analysis/late_day_trend_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    r = g.trading[pd.DatetimeIndex(g.ts[g.trading]).year >= 2018]; yrs = pd.DatetimeIndex(g.ts[r]).year
    J0, J1 = jof(830), jof(1500)
    C = pd.DataFrame(g.c[r, J0:J1 + 1]).ffill(axis=1).to_numpy(); H, L, V = g.h[r, J0:J1 + 1], g.l[r, J0:J1 + 1], np.nan_to_num(g.v[r, J0:J1 + 1])
    tp = (np.nan_to_num(H) + np.nan_to_num(L) + np.nan_to_num(C)) / 3
    vw = np.cumsum(tp[:, 1:] * V[:, 1:], 1) / np.maximum(np.cumsum(V[:, 1:], 1), 1)     # VWAP through each bar from 8:31
    ret = np.diff(np.log(C), axis=1) * 1e4                                               # bp, bar 8:31 .. 15:00
    sig_vw = np.sign(C[:, 1:-1] - vw[:, :-1]); sig_op = np.sign(C[:, 1:-1] - C[:, :1])   # known at bar t, applied to bar t+1
    P = {"VWAP model": sig_vw * ret[:, 1:], "from-open model": sig_op * ret[:, 1:]}
    mins = np.arange(J0 + 2, J1 + 1); bucket = ((mins - 1) // 15) * 15                  # bucket by bar-close minute
    lab_ = [f"{b // 60:02d}:{b % 60:02d}" for b in sorted(set(bucket))]
    print("\nA. Average gross bp per day in each 15-min bucket (bucket start, CT), and the share of the day's total:")
    for nm, pm in P.items():
        rows = {}
        for per, m in (("2018-22", yrs < 2023), ("2023-26", yrs >= 2023)):
            x = pd.DataFrame(np.nan_to_num(pm[m]), columns=mins).T.groupby(bucket).sum().T.mean()
            rows[per] = x.values
        T = pd.DataFrame(rows, index=lab_)
        print(f"\n   {nm}:"); print(T.round(2).T.to_string())
        for per in T: print(f"      {per}: day total {T[per].sum():+.1f} bp; last hour {T[per].iloc[-4:].sum():+.1f}; last 15 min (14:45-15:00) {T[per].iloc[-1]:+.2f}")
        last = pd.Series(np.nansum(pm[:, -15:], 1), index=pd.DatetimeIndex(g.ts[r]))
        print("      last-15-min bp by year:", last.groupby(last.index.year).mean().round(2).to_dict())
    print("\nB. Plan trades open at 14:45 CT: P&L from 14:45 to the exit (per NQ, gross)")
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    for nm, t in (("Monday Long", load_mc(g, "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx")),
                  ("Bridge Monday Long", load_bridge_mc(g))):
        t = t.reset_index(drop=True); m = (t.j1 > jof(1445)) & (t.j0 < jof(1445))
        tt = t[m]; p1445 = cf[tt.day.to_numpy() * 1440 + jof(1445)]
        seg = (tt.exit.to_numpy() - p1445) * tt.side.to_numpy() * 20.0
        whole = (tt.exit - tt.entry).to_numpy() * tt.side.to_numpy() * 20.0
        dt = pd.DatetimeIndex(g.ts[tt.day.to_numpy()]); s = pd.Series(seg, index=dt)
        print(f"   {nm}: {m.sum()} of {len(t)} trades open at 14:45; last segment avg ${s.mean():+.0f} (t {s.mean() / s.std() * np.sqrt(len(s)):+.2f});"
              f" 2018-22 ${s[s.index.year < 2023].mean():+.0f}, 2023-26 ${s[s.index.year >= 2023].mean():+.0f}; whole-trade avg ${whole.mean():+.0f}")
        print("      by year:", s.groupby(s.index.year).mean().round(0).astype(int).to_dict())
