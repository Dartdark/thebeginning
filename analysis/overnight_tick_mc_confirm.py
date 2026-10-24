"""Overnight TickRSV / VIX: the user's MultiCharts report (5-min @NQ, VIX daily as Data2, 2026-10-24) vs the Python rebuild
(analysis/overnight_tick_test.py; order flow = The Bridge aggressor volume). Trades matched by exit date; MC P&L after our
costs ($7.25 + 1 tick per fill = $17.25 per NQ). Which nights differ, and why (down day / RSV sign / VIX regime).
  python3 analysis/overnight_tick_mc_confirm.py
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M
from co_oc_reversal_test import line

REP = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Overnight Tick VIX.xlsx"
raw = pd.read_excel(REP, sheet_name="List of Trades", header=2)
en = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True); ex = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
mc = pd.DataFrame(dict(entry_dt=pd.to_datetime(en.Date), exit_dt=pd.to_datetime(ex.Date), ep=en.Price.astype(float), xp=ex.Price.astype(float),
                       sig=ex.Signal.astype(str)))
mc["date"] = mc.exit_dt.dt.normalize(); mc["gross"] = (mc.xp - mc.ep) * 20; mc["net"] = mc.gross - 17.25
py = pd.read_csv("checks/candidates/overnight_tick/python_trades.csv", parse_dates=["date", "sess"])
N = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date", "sess"])
lo, hi = pd.Timestamp("2018-01-02"), pd.Timestamp("2026-07-08")
m, p = mc[(mc.date >= lo) & (mc.date <= hi)], py[(py.date >= lo) & (py.date <= hi)]
both = set(m.date) & set(p.date); only_mc = sorted(set(m.date) - set(p.date)); only_py = sorted(set(p.date) - set(m.date))
print(__doc__.split("\n")[0])
print(f"\nMC report: {len(mc)} trades {mc.date.min().date()} -> {mc.date.max().date()}, exits {mc.sig.value_counts().to_dict()}")
print(f"common span 2018-01-02 -> 2026-07-07: MC {len(m)}, Python {len(p)}, same nights {len(both)} "
      f"({len(both) / len(set(m.date) | set(p.date)):.0%} of all), only MC {len(only_mc)}, only Python {len(only_py)}")
j = m.set_index("date").join(p.set_index("date")[["net"]].rename(columns={"net": "py_net"}), how="inner")
print(f"same nights: P&L corr {np.corrcoef(j.net, j.py_net)[0, 1]:.3f}, mean |diff| ${np.abs(j.net - j.py_net).mean():.0f}")
s = lambda x: x.set_index("date").net
print("\nPer NQ after our costs:")
print(line(s(mc), "MC report, all (2017-07 -> 2026-10)", 40)); print(line(s(m), "MC, common span", 40)); print(line(s(p), "Python, common span", 40))
print(line(s(mc[mc.date > hi]), "MC after the order-flow data ends", 40))
print("   by year MC / Python:", {y: f"{a:,.0f} / {b:,.0f}" for y, a, b in zip(s(m).groupby(lambda d: d.year).sum().index,
                                                                           s(m).groupby(lambda d: d.year).sum(), s(p).groupby(lambda d: d.year).sum().reindex(s(m).groupby(lambda d: d.year).sum().index, fill_value=0))})
N["bar_neg"] = N.rsv_bar < 0; N["of_neg"] = N.rsv < 0
Nd = N.set_index("date")
def why(ds):
    q = Nd.reindex(ds); return dict(down=int(q.down.sum()), not_down=int((~q.down.astype(bool)).sum()),
                                    rsv_sign_differs_from_bar_proxy=int((q.bar_neg != q.of_neg).sum()), n=len(ds))
print("\nnights only in MC:", why(only_mc)); print("nights only in Python:", why(only_py))
print("   MC-only nights P&L (MC):", f"${m.set_index('date').net.reindex(only_mc).sum():,.0f}", "| Python-only nights P&L (Py):", f"${p.set_index('date').net.reindex(only_py).sum():,.0f}")
alld = pd.bdate_range(mc.date.min(), mc.date.max())
print("\nStandard metrics, MC report after our costs:")
print(M.table({"MC all": (s(mc).groupby(level=0).sum().reindex(alld, fill_value=0.0), mc.net)}))
