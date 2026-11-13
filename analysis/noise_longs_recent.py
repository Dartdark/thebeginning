"""Noise Longs: last 2 months vs its history (user 2026-11-12). MC report (1 NQ, gross) minus our costs ($7.25 + 1 tick a market / stop fill).
  tools/run_stamped.sh analysis/noise_longs_recent.py > analysis/outputs/noise_longs_recent_output.txt
"""
import numpy as np, pandas as pd
print(__doc__.split("\n")[0])
d = pd.read_excel("mc_reports/NQ_Noise_Longs.xlsx", "List of Trades", header=2)
en = d[d.Type.astype(str).str.startswith("Entry")].reset_index(drop=True); ex = d[d.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
t = pd.DataFrame(dict(ts=pd.to_datetime(en.Date), why=ex.Signal.values, gross=en["Profit ($)"].astype(float)))
t["net"] = t.gross - 7.25 - np.where(t.why == "Profit Target", 5.0, 10.0)
last = t.ts.max(); cut = last - pd.Timedelta(days=61); r = t[t.ts > cut]; h = t[t.ts <= cut]
print(f"last 2 months ({cut.date()}..{last.date()}): n {len(r)}, win {np.mean(r.net > 0):.0%}, avg ${r.net.mean():.0f}, sum ${r.net.sum():,.0f} per NQ "
      f"(${r.net.sum() * 0.3:,.0f} at 3 MNQ); exits " + ", ".join(f"{k} {v}" for k, v in r.why.value_counts().items()))
print(f"history 2018 -> {cut.date()}: n {len(h)}, win {np.mean(h.net > 0):.0%}, avg ${h.net.mean():.0f}")
m = t.set_index("ts").net.resample("ME").sum(); print("monthly net per NQ, last 8: " + " ".join(f"{i:%y-%m}:{v:+,.0f}" for i, v in m.tail(8).items()))
# every rolling 61-day window since 2018: where does the latest one rank?
days = pd.date_range(t.ts.min().normalize() + pd.Timedelta(days=61), last.normalize(), freq="7D")
w = np.array([t.net[(t.ts > d0 - pd.Timedelta(days=61)) & (t.ts <= d0)].sum() for d0 in days])
cur = r.net.sum(); print(f"rolling 2-month windows since 2018 (weekly): latest ${cur:,.0f}; {np.mean(w <= cur):.0%} of windows were this bad or worse; "
      f"median ${np.median(w):,.0f}, 10th pct ${np.percentile(w, 10):,.0f}, worst ${w.min():,.0f}")
eq = t.net.cumsum(); dd = (eq - eq.cummax()); print(f"drawdown now ${dd.iloc[-1]:,.0f} per NQ; worst ever ${dd.min():,.0f} ({t.ts[dd.idxmin()].date()})")
y = t.assign(y=t.ts.dt.year).groupby("y").net.agg(["count", "mean", "sum"]); print(y.round(0).to_string())
