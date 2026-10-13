"""MultiCharts confirmation of the Bridge's Monday Long NQ (L644NQ v2.1), 2026-10-13.

Report: 'Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx' (5-min @NQ, Bar
Magnifier 1 min, no commission / slippage in MC). Matches its trades to the Python port
(analysis/bridge_monday_long_test.py) by Monday date, then puts the MC trades (with $7.25 + 1 tick per market
fill; the target is a limit) on the funded bench next to our Monday Long.
  python3 analysis/bridge_monday_confirm.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import bridge_monday_long_test as B
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
F = "Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx"
PV, TICK, COST = 20.0, 0.25, 7.25

def load_bridge_mc(g, path=F):
    """The MC trade list as bench trades: booked on the Monday row (Sunday-evening fills and target exits too),
    entry = the Sunday 19:00 fill + 1 tick, time exits - 1 tick, the target as a limit; $7.25 is added by paths()."""
    raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
    en = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
    ex = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    et, xt = pd.to_datetime(en.Date), pd.to_datetime(ex.Date)
    kind = np.where(ex.Signal.astype(str).str.contains("Profit"), 1, 2)
    mon = (et.dt.normalize() + pd.Timedelta(days=1)).dt.strftime("%Y%m%d").astype(int).to_numpy()
    xhm = (xt.dt.hour * 100 + xt.dt.minute).to_numpy()
    j1 = np.where(kind == 1, jof(xhm), jof(1555)); j1[xhm >= 1700] = 0       # target filled on Sunday evening
    return pd.DataFrame({"day": np.searchsorted(g.dates, mon), "j0": 0, "j1": j1, "side": 1,
                         "entry": en.Price.to_numpy(float) + TICK, "exit": ex.Price.to_numpy(float) - TICK * (kind != 1),
                         "kind": kind, "slips": 0, "date": pd.to_datetime(mon.astype(str))})


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    raw = pd.read_excel(F, sheet_name="List of Trades", header=2)
    en = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
    ex = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    et, xt = pd.to_datetime(en.Date), pd.to_datetime(ex.Date)
    mc = pd.DataFrame({"date": et.dt.normalize() + pd.Timedelta(days=1),          # the Monday session (Sunday-evening target fills too)
                        "entry": en.Price.to_numpy(float), "exit": ex.Price.to_numpy(float),
                       "kind": np.where(ex.Signal.astype(str).str.contains("Profit"), 1, 2),
                       "xhm": (xt.dt.hour * 100 + xt.dt.minute).to_numpy(), "ent_ok": (et.dt.dayofweek == 6) & (et.dt.hour == 19)})
    mc["gross"] = (mc.exit - mc.entry) * PV
    mc["net"] = mc.gross - COST - TICK * PV * (1 + (mc.kind != 1))
    print(__doc__.split("\n")[0])
    print(f"MC: {len(mc)} trades {mc.date.min().date()} .. {mc.date.max().date()}; entries all Sunday 19:00: {mc.ent_ok.all()};"
          f" target exits {np.mean(mc.kind == 1):.0%}")
    py = B.bridge(g, B.bridge_adx(g)); py["date"] = pd.to_datetime(py.date)
    py = py[(py.date >= mc.date.min()) & (py.date <= mc.date.max())]
    m = mc.merge(py[["date", "entry", "exit", "kind", "net"]], on="date", how="outer", suffixes=("_mc", "_py"), indicator=True)
    print(f"Python port over the same dates: {len(py)} trades; both {np.sum(m._merge == 'both')}, MC only "
          f"{np.sum(m._merge == 'left_only')}, Python only {np.sum(m._merge == 'right_only')}")
    for side in ("left_only", "right_only"):
        q = m[m._merge == side]
        if len(q): print(f"   {side}: " + ", ".join(f"{d.date()} (${n:,.0f})" for d, n in zip(q.date, q.net_mc if side == 'left_only' else q.net_py)))
    b = m[m._merge == "both"]
    print(f"   matched: entry price diff median {np.median(np.abs(b.entry_mc - (b.entry_py - TICK))):.2f} pts, same exit type"
          f" {np.mean(b.kind_mc == b.kind_py):.0%}, P&L correlation {np.corrcoef(b.net_mc, b.net_py)[0, 1]:.3f},"
          f" mean |diff| ${np.mean(np.abs(b.net_mc - b.net_py)):.0f}")
    x = mc.net; y = mc.date.dt.year; by = x.groupby(y).sum()
    pf = x[x > 0].sum() / -x[x < 0].sum()
    print(f"\nMC trades with costs: n={len(x)} win {np.mean(x > 0):.0%} avg ${x.mean():.0f} PF {pf:.2f} t={x.mean() / x.std() * np.sqrt(len(x)):.1f}"
          f" years+ {(by > 0).sum()}/{len(by)} | 2018-22 ${x[y < 2023].mean():.0f} 2023-26 ${x[y >= 2023].mean():.0f} | worst ${x.min():,.0f}")
    print("   by year:", by.round(0).astype(int).to_dict())
    print(f"   MC gross (as in its report): ${mc.gross.sum():,.0f} total, PF {mc.gross[mc.gross > 0].sum() / -mc.gross[mc.gross < 0].sum():.2f}")

    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dly = mc.groupby("date").net.sum().reindex(days, fill_value=0.0)
    print("\nStandard metrics per NQ (long-only):")
    print(M.table({"Bridge Monday Long (MC)": (dly, mc.net), "2023+": (dly[dly.index >= "2023-01-01"], mc.net[mc.date >= "2023-01-01"])}))
    bt, pm = R.report({"MC 2023+": dly[dly.index >= "2023-01-01"]}, n=5000); print(bt); print(pm)

    t = load_bridge_mc(g)
    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    lab.add("MON_BR_MC", t, slippage=False)
    dts = pd.DatetimeIndex(g.ts[lab.tr]); C = pd.DataFrame({k: lab.daily(k) for k in ("MON_BR_MC", "MON_MC", "VB", "ONB_ML2_MC", "EOS", "LDF_MC", "NFP_MC", "VCS_MC")}, index=dts)
    print("\n   daily correlation with the plan:", C[C.index.year >= 2018].corr().round(2).loc["MON_BR_MC"].drop("MON_BR_MC").to_dict())
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "VCS_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    print("Funded bench (cushion sizing from $1,500):")
    for nm, pl in (("current plan", plan), ("+ Bridge Monday Long 1 MNQ (MC trades)", {**plan, "MON_BR_MC": 1}),
                   ("+ Bridge Monday Long 2 MNQ", {**plan, "MON_BR_MC": 2})):
        a, c = lab.score(pl, 250, **CS), lab.score(pl, 500, **CS)
        print(f"   {nm:<42} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}"
              )
    print("\nPortfolio at full size, 2018-2026 ($ per day, MNQ sizes of the plan):")
    port = {}
    for nm, pl in (("current plan (7)", plan), ("+ Bridge Monday Long 1 MNQ (8)", {**plan, "MON_BR_MC": 1})):
        names, bb = lab._base(pl)
        port[nm] = pd.Series(sum(bb[i] * lab.C[k] for i, k in enumerate(names)), index=dts)[dts.year >= 2018]
    print(M.table({k: (v, None) for k, v in port.items()}))
    bt, pm = R.report({k + " 2023+": v[v.index >= "2023-01-01"] for k, v in port.items()}, n=3000); print(bt); print(pm)
    for k, v in port.items(): print(f"   {k} by year:", v.groupby(v.index.year).sum().round(0).astype(int).to_dict())

    print("\nSpeed to $13k (analysis/speed_to_13k.py method: trading days to the 6th payout, every start day):")
    from speed_to_13k import run, fmt
    rows = {nm: run(lab, pl, fmin=0.5, fmax=1.0, ref=1500.0) for nm, pl in
            (("current plan", plan), ("+ Bridge Monday Long 1 MNQ", {**plan, "MON_BR_MC": 1}))}
    print(fmt(pd.DataFrame(rows).T))
