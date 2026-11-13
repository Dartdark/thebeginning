"""IBS Globex ES v5 (analysis/ibs_globex_test.py): (1) the data-sweep leads re-checked with the regime known AT ENTRY (the sweep keys
multi-day trades on their exit date: look-ahead for a live filter), (2) the personal book bench: add at 1 / 2 MES, and replace S30-style
overlap / the most-correlated piece. MES = ES / 10 - $0.55 extra micro fee a trade. NOT Apex-legal (multi-day holds): personal only.
  tools/run_stamped.sh analysis/ibs_globex_bench.py > analysis/outputs/ibs_globex_bench_output.txt
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from data_sweep import series
from new_data_screen import RULES, prior

print(__doc__.split("\n")[0])
T = pd.read_csv("checks/candidates/ibs_globex/trades.csv", parse_dates=["entry_ts", "exit_ts", "date"])
D = pd.read_csv("checks/candidates/ibs_globex/daily.csv", index_col=0, parse_dates=True).net
T["eday"] = (T.entry_ts + pd.Timedelta(hours=7) - pd.Timedelta(minutes=1)).dt.normalize()   # entry at 15:00: the regime is the PREVIOUS close
S = series()
print("\n== Data-sweep leads, regime at ENTRY (last close before the entry session) vs at exit (as the sweep keyed them)")
e = T.eday.dt.year <= 2022
for nm in ("GEX (SqueezeMetrics)", "VVIX", "VIX", "VIX/VIX3M (term structure)"):
    for rule in ("above_median", "z_high"):
        for key, col in (("entry", "eday"), ("exit", "date")):
            v = prior(S[nm], T[col], RULES[rule]); ok = ~np.isnan(v); on = ok & (v == 1); off = ok & (v == 0)
            if on.sum() < 15 or off.sum() < 15: continue
            a, b = T.net[on], T.net[off]; t = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
            print(f"   {nm:<27}{rule:<13} at {key:<5}: on n {on.sum():3d} ${a.mean():6,.0f} | off n {off.sum():3d} ${b.mean():6,.0f} | gap t {t:5.2f} | "
                  f"2018-22 on ${T.net[on & e].mean():6,.0f} off ${T.net[off & e].mean():6,.0f} | 2023+ on ${T.net[on & ~e].mean():6,.0f} off ${T.net[off & ~e].mean():6,.0f}")

with contextlib.redirect_stdout(io.StringIO()):
    Pp = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")["P"]
Pp = Pp[[c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30")]]
base = Pp.sum(axis=1) + Pp.OvernightTick
fee = T.groupby(T.date).size().reindex(Pp.index, fill_value=0) * 0.55
mes = D.reindex(Pp.index, fill_value=0.0) / 10 - fee
vv = prior(S["VVIX"], T.eday, RULES["above_median"]); keep = T[vv == 0]
Dv = pd.Series(0.0, index=Pp.index)
for r in keep.itertuples():                                   # trade P&L on its exit day for the filtered version (approximation: not marked daily)
    if r.date in Dv.index: Dv[r.date] += r.net / 10 - 0.55
cp = {c: float(np.corrcoef(mes, Pp[c])[0, 1]) for c in Pp}; top = max(cp, key=cp.get)
print(f"\n== Personal book (every piece 1 micro, OT 2 MNQ; data to {Pp.index.max().date()})")
print("   correlation with pieces: " + ", ".join(f"{c} {v:+.2f}" for c, v in sorted(cp.items(), key=lambda x: -x[1])[:5]) + f"; most overlapped: {top}")
def mc(x):
    d = MC.daily_mc(x.values, horizon=252, n=3000, block=20, trail=1e12, seed=1); return d["pnl_p50"], d["dd_p95"], d["pnl_p50"] / d["dd_p95"]
V = {"book": base, "+ IBS 1 MES": base + mes, "+ IBS 2 MES": base + 2 * mes, f"- {top} + IBS 1 MES": base - Pp[top] + mes,
     f"- {top} (control)": base - Pp[top], "+ IBS VVIX-low 2 MES (post hoc)": base + 2 * Dv}
for per, m in (("2018-26", np.ones(len(Pp), bool)), ("2018-22", Pp.index.year <= 2022), ("2023+", Pp.index.year >= 2023)):
    r0 = mc(base[m])
    print(f"   {per}:")
    for nm, x in V.items():
        a, dd, q = mc(x[m]); print(f"      {nm:<34} median year ${a:8,.0f}  DD p95 ${dd:7,.0f}  return/DD {q:5.2f}" + ("" if nm == "book" else f" ({q - r0[2]:+.2f})"))
