"""FC 2B: MultiCharts report (user's export 2026-10-23, @NQ 1-minute, Bar Magnifier off) vs the Python rebuild
(analysis/fc_2b_test.py), trade by trade, plus the MC trades' metrics under our costs.
  python3 analysis/fc_2b_mc_confirm.py
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import fc_2b_test as F, metrics as M

REP = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute FC 2B.xlsx"


def load_report():
    raw = pd.read_excel(REP, sheet_name="List of Trades", header=2)
    en = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
    ex = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    side = np.where(en.Type.str.contains("Long"), 1, -1)
    t = pd.DataFrame(dict(date=pd.to_datetime(en.Date).dt.normalize(), side=side, entry=en.Price.astype(float),
                          exit=ex.Price.astype(float), xtime=pd.to_datetime(ex.Time).dt.strftime("%H%M"), sig=ex.Signal))
    t["gross"] = (t.exit - t.entry) * t.side * F.PV
    t["net"] = t.gross - F.COST - 2 * F.TICK * F.PV
    return t


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    mc = load_report()
    days = F.load(); sig = F.signals(days)
    rows = []
    for _, s in sig[sig.side != 0].iterrows():
        r = F.trade(days[int(s.date.strftime("%Y%m%d"))], s.side, s.sig_close)
        if r: rows.append(dict(date=s.date, side=s.side, **r))
    py = pd.DataFrame(rows)
    m = mc.merge(py, on="date", how="outer", suffixes=("_mc", "_py"), indicator=True)
    both = m[m._merge == "both"]
    print(f"\nMC trades {len(mc)} ({mc.date.min().date()} -> {mc.date.max().date()}), Python {len(py)}; same day {len(both)}, "
          f"MC only {(m._merge == 'left_only').sum()}, Python only {(m._merge == 'right_only').sum()}")
    same_side = (both.side_mc == both.side_py)
    print(f"same side {same_side.mean():.1%}; entry price equal {np.isclose(both.entry_mc, both.entry_py).mean():.1%}; "
          f"exit price equal {np.isclose(both.exit_mc, both.exit_py).mean():.1%}; gross within $20 "
          f"{(abs(both.gross_mc - both.gross_py) <= 20).mean():.1%}; gross corr {np.corrcoef(both.gross_mc, both.gross_py)[0, 1]:.4f}")
    print(f"total gross MC ${mc.gross.sum():,.0f} vs Python ${py.gross.sum():,.0f} (per NQ, all dates)")
    diff = both[~np.isclose(both.exit_mc, both.exit_py)]
    print("\nlargest exit differences:")
    print(diff.assign(d=(diff.gross_mc - diff.gross_py)).sort_values("d", key=abs, ascending=False)
          [["date", "side_mc", "entry_mc", "exit_mc", "exit_py", "xtime", "sig", "kind", "d"]].head(8).to_string(index=False))
    print("\nMC-only days:", m[m._merge == "left_only"].date.dt.date.tolist()[:20])
    print("Python-only days:", m[m._merge == "right_only"].date.dt.date.tolist()[:20])
    t = mc[mc.date >= "2018-01-01"]
    print("\nMC trades 2018-26 under our costs ($7.25 + 1 tick per fill):")
    print(F.line(t, "all")); print(F.line(t[t.side > 0], "longs")); print(F.line(t[t.side < 0], "shorts"))
    print("   by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
    alld = pd.bdate_range("2018-01-01", t.date.max())
    dl = lambda q: q.groupby(q.date).net.sum().reindex(alld, fill_value=0.0)
    print(M.table({"MC FC 2B": (dl(t), t.net), "longs": (dl(t[t.side > 0]), t.net[t.side > 0]), "shorts": (dl(t[t.side < 0]), t.net[t.side < 0])}))
    x = t.net; print(f"   t {x.mean() / x.std() * np.sqrt(len(x)):.2f}; DSR at N=282: {M.deflated_sharpe(x.values, 282) if hasattr(M, 'deflated_sharpe') else 'n/a'}")
