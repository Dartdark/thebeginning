"""MultiCharts confirmation of three watched pieces (user's reports 2026-11-09, in mc_reports/): S30 IBS < 0.10 (WATCHLIST #34; 15-min,
no Bar Magnifier), ZT continuation EntryZ 1.25 (#36; 15-min, Bar Magnifier 1 min) and Ricochet 1144 target 80 (#35; 5-min, Bar
Magnifier 1 min). Each MultiCharts list (no commission / slippage in the reports) is matched trade by trade to the Python rebuild from
2018: count, share matched (same entry day + side, in order), P&L in points (MC) vs the rebuild's gross points, correlation, totals;
then the MC trades after our costs ($7.25 + 1 tick per market fill; Ricochet stop fills also 1 tick, target limits none) by period.
  tools/run_stamped.sh analysis/mc_confirm_3.py > analysis/outputs/mc_confirm_3_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from donchian_lwti_test import series
from overnight_round import roll_minutes
from grid24 import jof
import s30_ibs_test as S3
import zt_ablation as A

R = "mc_reports/Backtesting Strategy Performance Report _ @NQ - "
PV, TICK, COMM = 20.0, 0.25, 7.25


def mc_list(path):
    raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
    en = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True); ex = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    n = min(len(en), len(ex)); en, ex = en.iloc[:n], ex.iloc[:n]
    t = pd.DataFrame({"et": pd.to_datetime(en.Date), "xt": pd.to_datetime(ex.Date), "side": np.where(en.Type.str.contains("Long"), 1, -1),
                      "e": en.Price.astype(float).values, "x": ex.Price.astype(float).values, "sig": ex.Signal.astype(str).values,
                      "usd": en["Profit ($)"].astype(float).values / en.Contracts.astype(float).values})
    t["pts"] = (t.x - t.e) * t.side
    return t[ex.Signal.astype(str).str.lower().values != "open"]


def report(nm, mc, py, key_mc, key_py, cost_mc):
    mc = mc.copy(); py = py.copy(); mc["k"] = key_mc(mc); py["k"] = key_py(py)
    mc["o"] = mc.groupby(["k", "side"]).cumcount(); py["o"] = py.groupby(["k", "side"]).cumcount()
    j = mc.merge(py, on=["k", "side", "o"], suffixes=("_mc", "_py"))
    um = mc.merge(py[["k", "side", "o"]], on=["k", "side", "o"], how="left", indicator=True); um = um[um._merge == "left_only"]
    up = py.merge(mc[["k", "side", "o"]], on=["k", "side", "o"], how="left", indicator=True); up = up[up._merge == "left_only"]
    if len(um) <= 12: print("   MC-only trades:", [(str(r.et), round(r.pts, 2)) for r in um.itertuples()])
    if len(up) <= 12: print("   Python-only trades:", [(str(r.k.date()), round(r.pts, 2)) for r in up.itertuples()])
    if "sig" in j: d_ = (j.pts_mc - j.pts_py).abs() > 0.25; print("   differing matched trades by MC exit:", j[d_].sig.value_counts().to_dict(), "| MC - Python points on them:", round((j.pts_mc - j.pts_py)[d_].sum(), 1))
    yr = pd.DatetimeIndex(mc.k)
    print(f"\n {nm}: MultiCharts {len(mc)} trades from 2018, Python {len(py)}; matched (same day, side, order) {len(j)} = {len(j) / len(mc):.1%} of MC / {len(j) / len(py):.1%} of Python")
    print(f"   matched P&L points: corr {np.corrcoef(j.pts_mc, j.pts_py)[0, 1]:.3f}; identical (|diff| <= 0.25) {np.mean(np.abs(j.pts_mc - j.pts_py) <= 0.25):.1%}; "
          f"sum MC {j.pts_mc.sum():,.0f} vs Python {j.pts_py.sum():,.0f} points")
    net = mc.pts * PV - cost_mc(mc); a, b = net[yr < "2023"], net[yr >= "2023"]
    tt = lambda v: v.mean() / v.std() * np.sqrt(len(v))
    print(f"   MC trades after our costs: ${net.mean():.0f} a trade (t {tt(net):.2f}), total ${net.sum():,.0f} | 2018-22 ${a.mean():.0f} (t {tt(a):.1f}) | 2023+ ${b.mean():.0f} (t {tt(b):.1f})")
    print(f"   MC by year $: {net.groupby(yr.year).sum().round(0).astype(int).to_dict()}")
    print(f"   Python after costs: ${py.net.mean():.0f} a trade, total ${py.net.sum():,.0f}")
    return j


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb"))
    # ---------- S30 IBS < 0.10 (decision at the 15:00 close, fill at the 15:15-stamped bar's open)
    S = S3.sessions(g, "NQ"); S = S[S.date >= "2017-12-01"].reset_index(drop=True); rolls = np.sort(roll_minutes(g, "NQ")); rows = []; pos = 0
    for i, x in S.iterrows():
        if not x.full or not np.isfinite(x.ibs) or not np.isfinite(x.nxt) or x.hi <= x.lo: continue
        if pos == 0 and x.ibs < 0.10: pos = 1; e_i = i
        elif pos and x.ibs > 0.80:
            rows.append((S.date[e_i], x.date, 1, x.nxt - S.nxt[e_i])); pos = 0
    py = pd.DataFrame(rows, columns=["date", "xdate", "side", "pts"]); py["net"] = (py.pts - 2 * TICK) * PV - COMM; py = py[py.date >= "2018-01-01"]
    mc = mc_list(R + "15 Minutes S30 IBS 010.xlsx"); mc = mc[mc.et >= "2018-01-01"]
    j = report("S30 IBS < 0.10 (raw prices on both sides: roll gaps inside a hold are in both)", mc, py, lambda t: t.et.dt.normalize(), lambda t: t.date,
               lambda t: 2 * TICK * PV + COMM)
    print(f"   same exit day on matched: {np.mean(j.xt.dt.normalize().values == j.xdate.values):.1%}")
    # ---------- ZT continuation EntryZ 1.25
    s = series(g, 15); T = A.run(g, s, A.zser(s), entry=1.25); T["pts"] = (T.net + COMM) / PV + 2 * TICK
    mc = mc_list(R + "15 Minutes ZT Continuation.xlsx"); mc = mc[mc.et >= "2018-01-01"]
    report("ZT continuation EntryZ 1.25", mc, T, lambda t: t.et.dt.normalize(), lambda t: t.date, lambda t: 2 * TICK * PV + COMM)
    # ---------- Ricochet 1144 target 80
    rp = pd.read_csv("checks/candidates/ricochet_1144/python_trades_t80.csv", parse_dates=["date"]); rp["side"] = 1
    rp["pts"] = rp.exit - rp.entry; rp = rp[rp.date >= "2018-01-01"]
    mc = mc_list(R + "5 Minutes Ricochet 80.xlsx")
    sess = lambda t: (t.et - pd.Timedelta(hours=0)).dt.normalize().where(t.et.dt.hour < 17, (t.et + pd.Timedelta(days=1)).dt.normalize())
    mc = mc[sess(mc) >= "2018-01-01"]
    print(f"\n   Ricochet: Python session stamp check: first rows {rp[['session', 'date', 'entry']].head(2).values.tolist()}")
    for lab, kf in (("session = next day for 17:00+ entries", sess),):
        try: report(f"Ricochet target 80 ({lab})", mc, rp, kf, lambda t: t.date, lambda t: np.where(t.sig.str.contains("TP"), TICK * PV, 2 * TICK * PV) + COMM)
        except Exception as e: print(f"   {lab}: {e.__class__.__name__} {e}")
    print("   Ricochet exit signals in MC:", mc.sig.value_counts().to_dict())
