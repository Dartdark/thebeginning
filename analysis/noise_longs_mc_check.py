"""NQ Noise Longs MultiCharts report (mc_reports/NQ_Noise_Longs.xlsx, user 2026-11-12: 1 NQ, ShortTrade false, no costs) vs the Python
longs-only trades the eval bench uses (analysis/outputs/bridge_noise_15m_trades_rth_longs.csv). Matched on date + entry bar stamp.
  tools/run_stamped.sh analysis/noise_longs_mc_check.py > analysis/outputs/noise_longs_mc_check_output.txt
"""
import numpy as np, pandas as pd
print(__doc__.split("\n")[0])
d = pd.read_excel("mc_reports/NQ_Noise_Longs.xlsx", "List of Trades", header=2)
en = d[d.Type.astype(str).str.startswith("Entry")].reset_index(drop=True); ex = d[d.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
mc = pd.DataFrame(dict(ts=pd.to_datetime(en.Date), entry=en.Price.astype(float), exit=ex.Price.astype(float), why=ex.Signal.values,
                       gross=en["Profit ($)"].astype(float), qty=en.Contracts.astype(float)))
mc["key"] = mc.ts.dt.strftime("%Y%m%d") + mc.ts.dt.strftime("%H%M")
py = pd.read_csv("analysis/outputs/bridge_noise_15m_trades_rth_longs.csv", parse_dates=["date"])
py = py[(py.date >= mc.ts.min().normalize()) & (py.date <= mc.ts.max())].copy()
py["gross"] = (py.exit - py.entry) * 20; py["key"] = py.date.dt.strftime("%Y%m%d") + py.t0.astype(int).astype(str).str.zfill(4)
print(f"MC {mc.ts.min().date()}..{mc.ts.max().date()}: n {len(mc)} (qty {mc.qty.unique()}), win {np.mean(mc.gross > 0):.1%}, gross ${mc.gross.mean():.1f}, PF {mc.gross[mc.gross > 0].sum() / -mc.gross[mc.gross < 0].sum():.2f}")
print("   exits: " + ", ".join(f"{k} {v}" for k, v in mc.why.value_counts().items()))
print(f"PY same span: n {len(py)}, win {np.mean(py.gross > 0):.1%}, gross ${py.gross.mean():.1f}, PF {py.gross[py.gross > 0].sum() / -py.gross[py.gross < 0].sum():.2f}, net (our costs) ${py.net.mean():.1f}")
m = mc.merge(py, on="key", suffixes=("_mc", "_py"))
print(f"same date + entry bar: {len(m)} of MC {len(mc)} / PY {len(py)}; same entry price {np.mean(np.isclose(m.entry_mc, m.entry_py)):.1%}; "
      f"same exit price {np.mean(np.isclose(m.exit_mc, m.exit_py)):.1%}; median |gross diff| ${np.median(np.abs(m.gross_mc - m.gross_py)):.0f}; P&L corr {np.corrcoef(m.gross_mc, m.gross_py)[0, 1]:.3f}")
mo = mc[~mc.key.isin(m.key)]; po = py[~py.key.isin(m.key)]
print(f"MC only {len(mo)} (gross ${mo.gross.sum():,.0f}), PY only {len(po)} (gross ${po.gross.sum():,.0f})")
for nm, x in (("MC", mc.assign(y=mc.ts.dt.year)), ("PY", py.assign(y=py.date.dt.year))):
    print(f"   {nm} by year gross $k: " + " ".join(f"{yy % 100:02d}:{x.gross[x.y == yy].sum() / 1000:+.1f}" for yy in sorted(x.y.unique())))
print("   first MC-only:"); print(mo.head(8)[["ts", "entry", "exit", "why", "gross"]].to_string(index=False))
print("   first PY-only:"); print(po.head(8)[["date", "t0", "entry", "exit", "kind", "gross"]].to_string(index=False))
