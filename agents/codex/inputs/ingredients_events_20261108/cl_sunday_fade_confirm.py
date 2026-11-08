"""MultiCharts check of the CL Sunday up-gap fade (2026-10-14).

Report: `mc_reports/Backtesting Strategy Performance Report _ CL - 5 Minutes CL Sunday Gap.xlsx` (5-minute @CL, Bar Magnifier 1 min,
GapAtrPct 0.10, StopAtrPct 0.75, ExitTime 1000, no commission / slippage). The chart ran on Eastern time (NYMEX
exchange time): entries are stamped 18:10 ET (= the 17:05 CT open) and ExitTime 1000 meant 10:00 ET = 9:00 CT, one hour
earlier than the Python test. So the Python rule is re-run with the 9:00 CT exit (and the 17:05 CT 5-minute bar open)
and matched trade by trade; MultiCharts P&L gets the test's costs ($7.25 + 1 tick a fill = $27.25 a trade).
  python3 analysis/cl_sunday_fade_confirm.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from cl_forced_flows_test import load
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
REPORT = "mc_reports/Backtesting Strategy Performance Report _ CL - 5 Minutes CL Sunday Gap.xlsx"
PV, TICK, COMM = 1000.0, 0.01, 7.25
COST = COMM + 2 * TICK * PV


def python_trades(cl, fr, exit_ct, entry_j, roll_skip):
    O, H = cl.o.ravel(), cl.h.ravel(); C = pd.Series(cl.c.ravel()).ffill().to_numpy(); out = []
    for r in fr.itertuples():
        if not r.ok or (roll_skip and r.roll) or not (r.gA >= 0.1): continue
        e_i = int(r.sun) * 1440 + entry_j; x_i = int(r.mon) * 1440 + jof(exit_ct)
        if np.isnan(O[e_i]): continue
        e = O[e_i] - TICK; px = C[x_i] + TICK; sp = e + 0.75 * r.atr; kind = "time"
        hit = np.where(H[e_i:x_i + 1] >= sp)[0]
        if len(hit): j = e_i + hit[0]; px = (sp if j == e_i or np.isnan(O[j]) else max(O[j], sp)) + TICK; kind = "stop"
        out.append(dict(date=pd.Timestamp(cl.ts[int(r.mon)]).normalize(), py_entry=O[e_i], py_net=(e - px) * PV - COMM, py_kind=kind))
    return pd.DataFrame(out).set_index("date")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    raw = pd.read_excel(REPORT, sheet_name="List of Trades", header=2)
    ent = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
    ex = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    mc = pd.DataFrame({"date": (pd.to_datetime(ent.Date) + pd.Timedelta(days=1)).dt.normalize(),       # Sunday entry -> Monday trading day
                       "mc_entry": ent.Price.values, "mc_exit": ex.Price.values, "mc_sig": ex.Signal.values,
                       "mc_gross": ent["Profit ($)"].values}).set_index("date")
    mc["mc_net"] = mc.mc_gross - COST
    print(f"MultiCharts: {len(mc)} trades, gross ${mc.mc_gross.sum():,.0f}, net of $27.25 ${mc.mc_net.sum():,.0f} (avg ${mc.mc_net.mean():.0f}); "
          f"stops {int((mc.mc_sig == 'Stop Loss').sum())}")
    cl = load("CL"); fr = pickle.load(open(SP + "s_rank_gap2.pkl", "rb"))["frames"]["CL"]
    for nm, ext, ej, rs in (("Python as tested (17:04 open, out 10:00 CT, roll weekends skipped)", 1000, jof(1705), True),
                            ("Python like the MC run (17:05 open, out 9:00 CT, no roll skip)", 900, jof(1706), False)):
        py = python_trades(cl, fr, ext, ej, rs)
        py = py[py.index >= mc.index.min()]
        j = mc.join(py, how="outer")
        both = j.dropna(subset=["mc_net", "py_net"])
        print(f"\n== {nm}: {len(py)} trades from {mc.index.min().date()}")
        print(f"   matched days {len(both)}; only MC {int(j.py_net.isna().sum())}; only Python {int(j.mc_net.isna().sum())}")
        print(f"   matched: MC net ${both.mc_net.mean():.0f} vs Python ${both.py_net.mean():.0f} a trade; entry price equal on {np.mean(np.isclose(both.mc_entry, both.py_entry, atol=0.005)):.0%}, "
              f"|P&L diff| <= $30 on {np.mean(np.abs(both.mc_net - both.py_net) <= 30):.0%}; P&L correlation {np.corrcoef(both.mc_net, both.py_net)[0, 1]:.3f}")
        print("   MC-only days: " + ", ".join(f"{d.date()} ${v:.0f}" for d, v in j[j.py_net.isna()].mc_net.items()))
        print("   Python-only days: " + ", ".join(f"{d.date()} ${v:.0f}" for d, v in j[j.mc_net.isna()].py_net.items()))
        big = both[np.abs(both.mc_net - both.py_net) > 200]
        if len(big): print("   largest differences:\n" + big.assign(diff=big.mc_net - big.py_net).sort_values("diff").round(2).to_string())
    x = mc.mc_net; y = x.index.year
    print(f"\nMultiCharts trades (net of costs): avg ${x.mean():.0f}, PF {x[x > 0].sum() / -x[x < 0].sum():.2f}, t {x.mean() / x.std() * np.sqrt(len(x)):.1f}, "
          f"win {np.mean(x > 0):.0%}, years + {(x.groupby(y).sum() > 0).sum()}/{len(x.groupby(y))}; 2018-22 ${x[y < 2023].mean():.0f}, 2023-26 ${x[y >= 2023].mean():.0f}")
    print("   by year: " + " | ".join(f"{a} ${b:,.0f}" for a, b in x.groupby(y).sum().items()))
    days = pd.DatetimeIndex(cl.ts[cl.trading]); days = days[days >= mc.index.min()]
    dl = x.groupby(x.index).sum().reindex(days, fill_value=0.0)
    print(M.table({"CL Sunday fade (MultiCharts, out 9:00 CT)": (dl, x)}))
