"""User's regime filter (2026-10-17): 20-trading-day change of the market > +5% = bull, -5%..+5% = sideways, < -5% = bear.
Does the state tell good from bad trades in the plan strategies?

State is known before the trade: change from the close 21 trading days before the trade date to the previous trading
day's close (last price at or before 15:00 CT; CL: last price of the weekday session). NQ for the NQ strategies, CL for
the CL fade (its Sunday trade uses Friday's close as 'previous'). Trades: each strategy's MultiCharts report, per
contract, net of $7.25 + 1 tick per market / stop fill. Pre-specified thresholds (the user's), no tuning.
Caveat: continuous data are not back-adjusted (NQ roll jumps ~1%, enough to move a few days across the 5% line).
  python3 analysis/regime20_filter_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.path.insert(0, "analysis/jesse")
import numpy as np, pandas as pd
sys.argv = sys.argv[:2]
import compare as C
from grid24 import jof
from cl_forced_flows_test import load

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
STRATS = ["VaultBreak", "ONBiasADX30", "ONBiasML", "MondayLong", "ExpOpenShort", "LateDayFlow", "NFPFade", "CLSundayFade"]


def daily_close(g, upto=1500):
    c = g.c[:, : jof(upto) + 1]
    last = pd.DataFrame(c).ffill(axis=1).iloc[:, -1].to_numpy()
    s = pd.Series(last, index=pd.DatetimeIndex(g.ts))
    s = s[s.index.dayofweek < 5].dropna()
    return s


def state_series(close):
    r = close / close.shift(20) - 1                         # change over the last 20 trading days, as of that close
    st = pd.Series(np.where(r > 0.05, "bull", np.where(r < -0.05, "bear", "side")), index=close.index).where(r.notna())
    return st, r


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def tdiff(a, b):
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    if len(a) < 5 or len(b) < 5: return np.nan
    return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); nq_st, nq_r = state_series(daily_close(g))
    cl = load("CL"); cl_c = daily_close(cl, 1600); cl_st, cl_r = state_series(cl_c)
    for nm, st in (("NQ", nq_st), ("CL", cl_st)):
        x = st[st.index >= "2018-01-01"].value_counts(normalize=True)
        print(f"{nm} days by state 2018-26: " + ", ".join(f"{k} {v:.0%}" for k, v in x.items()))
    rows = []
    for s in STRATS:
        path, pv, tick, cost = C.REPORTS[s]
        m = C.mc_trades(path); m["net"] = C.net(m, pv, tick, cost)
        d = m.entry_time.dt.normalize()
        if s == "CLSundayFade": d = d + pd.Timedelta(days=1)          # Sunday entry -> the Monday trading day
        st, r = (cl_st, cl_r) if s == "CLSundayFade" else (nq_st, nq_r)
        prev = st.shift(1); prev_r = r.shift(1)                        # previous trading day's state (known at entry)
        m["state"] = prev.reindex(d, method="ffill").to_numpy(); m["r20"] = prev_r.reindex(d, method="ffill").to_numpy()
        m = m[m.entry_time >= "2018-01-01"].dropna(subset=["state"])
        print(f"\n=== {s}  ({len(m)} trades, net $ per contract)")
        for side, x in (("all", m), ("longs", m[m.side > 0]), ("shorts", m[m.side < 0])):
            if len(x) == 0 or (side != "all" and len(x) == len(m)): continue
            parts = []
            for k in ("bull", "side", "bear"):
                y = x[x.state == k].net
                parts.append(f"{k} n {len(y):4d} ${y.mean() if len(y) else np.nan:6.0f} (t {tstat(y):4.1f})")
            # does any state differ from the rest? largest |t| of state-vs-rest
            tv = {k: tdiff(x[x.state == k].net, x[x.state != k].net) for k in ("bull", "side", "bear")}
            kb = max(tv, key=lambda k: abs(tv[k]) if pd.notna(tv[k]) else -1)
            e, h = x[x.entry_time < "2023-01-01"], x[x.entry_time >= "2023-01-01"]
            same = tdiff(e[e.state == kb].net, e[e.state != kb].net), tdiff(h[h.state == kb].net, h[h.state != kb].net)
            print(f"   {side:<6} " + " | ".join(parts) + f"   most different: {kb} vs rest t {tv[kb]:+.1f} (2018-22 {same[0]:+.1f}, 2023+ {same[1]:+.1f})")
            rows.append(dict(strategy=s, side=side, state=kb, t=tv[kb], t_1822=same[0], t_23=same[1]))
    df = pd.DataFrame(rows)
    print("\nSummary: tests run", len(df) * 3, "(strategy x side x state); |t| >= 2 in", int((df.t.abs() >= 2).sum()),
          "of", len(df), "best-state rows; same sign in both periods and |t| >= 2 overall:",
          int(((df.t.abs() >= 2) & (np.sign(df.t_1822) == np.sign(df.t_23))).sum()))
    print(df.round(2).to_string(index=False))
