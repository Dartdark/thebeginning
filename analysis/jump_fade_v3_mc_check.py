"""NQ_Jump_Fade v3 MultiCharts report (mc_reports/NQ_Jump_Fade_v3.xlsx, user 2026-11-12) vs the Python research trades with the same
volume filter (vz >= 2, jump_lib): entry minutes, sides, exits, P&L. MC report = 1 NQ, no costs; Python costs added on top.
  tools/run_stamped.sh analysis/jump_fade_v3_mc_check.py > analysis/outputs/jump_fade_v3_mc_check_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import jump_lib as L, jump_study as S
print(__doc__.split("\n")[0])
d = pd.read_excel("mc_reports/NQ_Jump_Fade_v3.xlsx", "List of Trades", header=2)
d = d[d["Trade #"].notna() | d["Type"].notna()]
en = d[d.Type.astype(str).str.startswith("Entry")].reset_index(drop=True); ex = d[d.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
mc = pd.DataFrame(dict(ts=pd.to_datetime(en.Date), side=np.where(en.Type == "EntryLong", 1, -1), entry=en.Price.astype(float),
                       exit=ex.Price.astype(float), why=ex.Signal.values, gross=en["Profit ($)"].astype(float)))
b = L.bars(); M = S.Mkt(); yr = b.ts.dt.year.to_numpy(); sgn = np.sign(b.r).fillna(0).to_numpy()
mk = (yr >= 2018) & (b.J.abs().to_numpy() > 3) & np.isin(b.ts.dt.hour.to_numpy(), [7, 8, 9]) & (b.vz.to_numpy() >= 2)
py = S.trades(b, M, mk, -sgn, "rng", 1.5, tp=0.3, hold=240)
py = py[py.ts <= mc.ts.max() + pd.Timedelta(days=1)]
print(f"MC   {mc.ts.min().date()}..{mc.ts.max().date()}: n {len(mc)}, win {np.mean(mc.gross > 0):.1%}, gross ${mc.gross.mean():.0f}, PF {mc.gross[mc.gross > 0].sum() / -mc.gross[mc.gross < 0].sum():.2f}, "
      f"L/S {np.sum(mc.side > 0)}/{np.sum(mc.side < 0)}; exits " + ", ".join(f"{k} {v}" for k, v in mc.why.value_counts().items()))
pg = py.gross
print(f"PY   {py.ts.min().date()}..{py.ts.max().date()}: n {len(py)}, win {np.mean(pg > 0):.1%}, gross ${pg.mean():.0f}, PF {pg[pg > 0].sum() / -pg[pg < 0].sum():.2f}, "
      f"L/S {np.sum(py.side > 0)}/{np.sum(py.side < 0)}; exits " + ", ".join(f"{k} {v}" for k, v in py.why.value_counts().items()))
print(S.summ(py, "PY with our costs"))
m0 = mc.merge(py, on="ts", suffixes=("_mc", "_py"))
m1 = mc.assign(ts=mc.ts - pd.Timedelta(minutes=1)).merge(py, on="ts", suffixes=("_mc", "_py"))     # MC one minute late (late-closed bucket)
print(f"same entry minute {len(m0)}; MC one minute later {len(m1)}; same side {np.mean(np.r_[m0.side_mc == m0.side_py, m1.side_mc == m1.side_py]):.1%}; "
      f"median |gross diff| ${np.median(np.abs(np.r_[m0.gross_mc - m0.gross_py, m1.gross_mc - m1.gross_py])):.0f}")
mc_only = mc[~mc.ts.isin(m0.ts) & ~(mc.ts - pd.Timedelta(minutes=1)).isin(m1.ts)]; py_only = py[~py.ts.isin(m0.ts) & ~py.ts.isin(m1.ts)]
print(f"MC only {len(mc_only)} (gross ${mc_only.gross.sum():,.0f}); PY only {len(py_only)} (gross ${py_only.gross.sum():,.0f})")
day = lambda s: set(pd.DatetimeIndex(s).normalize())
print(f"  of those, same day different minute: MC-only {len(day(mc_only.ts) & day(py_only.ts))}")
print("  MC only (first 12):"); print(mc_only.head(12).to_string(index=False))
print("  PY only (first 12):"); print(py_only[["ts", "side", "R", "entry", "exit", "why", "gross"]].head(12).to_string(index=False))
for per, a, c in (("2018-22", mc.ts.dt.year <= 2022, py.ts.dt.year <= 2022), ("2023+", mc.ts.dt.year >= 2023, py.ts.dt.year >= 2023)):
    print(f"  {per}: MC n {a.sum()} gross ${mc.gross[a].mean():.0f} | PY n {c.sum()} gross ${py.gross[c].mean():.0f}, net ${py.net[c].mean():.0f}")
