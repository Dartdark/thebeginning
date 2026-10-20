"""NQAlignedWeaknessShort: the user's MultiCharts report (2026-10-20, '... 1 Minute Aligned Weakness Short.xlsx', costs 0,
limits need a 1-point trade-through) vs the Python rebuild (analysis/anti_nq_aligned_weakness_short_test.py).
  python3 analysis/anti_aws_mc_confirm.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import relative_strength_test as RS, metrics as M, montecarlo as MC

F = "Backtesting Strategy Performance Report _ @NQ - 1 Minute Aligned Weakness Short.xlsx"
if __name__ == "__main__":
    r = pd.read_excel(F, sheet_name="List of Trades", header=2)
    e = r[r.Type.astype(str).str.startswith("Entry")].reset_index(drop=True); x = r[r.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    mc = pd.DataFrame(dict(date=pd.to_datetime(e.Date).dt.normalize(), entry=e.Price.values, exit=x.Price.values, sig=x.Signal.values,
                           gross=e["Profit ($)"].values / e.Contracts.values))
    mc["net"] = mc.gross - 7.25 - np.where(mc.sig == "AWS.ST", 5.0, 10.0); mc = mc[mc.date >= "2018-01-01"]
    days, N, E = RS.load(); rn = N["c"][:, 30] / N["c"][:, 0] - 1; re = E[:, 30] / E[:, 0] - 1
    py = RS.trades(days, N, np.where(((rn - 1.25 * re) <= -0.002) & (re < 0), -9.0, np.nan))
    m = mc.merge(py, on="date", how="outer", indicator=True)
    both = m[m._merge == "both"]
    print(f"MultiCharts {len(mc)} trades 2018+, Python {len(py)}; same days {len(both)}; only MC {int((m._merge == 'left_only').sum())}, only Python {int((m._merge == 'right_only').sum())}")
    print(f"   same entry price {np.mean(np.isclose(both.entry_x, both.entry_y)):.0%}; same exit price {np.mean(np.isclose(both.exit_x, both.exit_y)):.0%}; P&L corr {both.net.corr(both.pnl):.3f}")
    print("   only-MC days:", m[m._merge == "left_only"].date.dt.date.tolist()[:12], "\n   only-Python days:", m[m._merge == "right_only"].date.dt.date.tolist()[:12])
    for nm, v, d in (("MultiCharts net", mc.net, mc.date), ("Python net", py.pnl, py.date)):
        s = pd.Series(v.values, index=d.values); yr = s.groupby(s.index.year).sum(); a, b = s[s.index < "2023"], s[s.index >= "2023"]
        print(f"   {nm:<16} n {len(s)} ${s.mean():.0f} t {RS.tstat(s):.2f} yrs+ {(yr > 0).sum()}/{len(yr)} | 2018-22 ${a.mean():.0f} (t {RS.tstat(a):.2f}) 2023+ ${b.mean():.0f} (t {RS.tstat(b):.2f})")
    print("   MC by year:", mc.groupby(mc.date.dt.year).net.sum().round(0).to_dict())
    idx = pd.bdate_range("2018-01-01", "2026-10-16"); dd = pd.Series(0.0, index=idx); g = mc.groupby("date").net.sum(); dd.loc[g.index] = g.values
    print("  ", M.table({"MC short": (dd, mc.net)}).replace("\n", "\n   "))
    print(MC.report(mc.net.to_numpy(), dd.to_numpy(), size=0.1, label="AWS 1 MNQ"))
