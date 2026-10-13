"""MultiCharts confirmation of NFP Fade and Vol-Control Sell Flow (2026-10-13): trade-by-trade match with
the Python tests, standard metrics (whole / longs / shorts), bootstrap + permutation on 2023+, funded
bench and speed-to-$13k with the MultiCharts trade lists.
  python3 analysis/nfp_vcs_confirm.py [SCRATCH_DIR]
"""
import sys, pickle, warnings, glob; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
import metrics as M, resampling as R
import addon_combo_test as A
from news_meanrev_test import reaction_trades
import event_days as E
from speed_to_13k import run, fmt, PLAN

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
pf = lambda s: s[s > 0].sum() / max(1e-9, -s[s < 0].sum())


def mc_list(g, pat):
    t = load_mc(g, glob.glob(pat)[0])
    t["date"] = pd.DatetimeIndex(g.ts[t.day.values])
    t["net"] = (t.exit - t.entry) * t.side * 20 - 7.25 - 2 * 5          # +1 tick per market/stop fill
    return t


def compare(nm, mc, py):
    x = mc.net; yr = mc.date.dt.year
    print(f"\n{nm}: MultiCharts n={len(mc)} win {np.mean(x > 0):.0%} avg ${x.mean():.0f} PF {pf(x):.2f}"
          f" t={x.mean() / x.std() * np.sqrt(len(x)):.1f} | longs n={(mc.side > 0).sum()} ${x[mc.side > 0].mean():.0f}"
          f" | shorts n={(mc.side < 0).sum()} ${x[mc.side < 0].mean():.0f}")
    print("  by year:", x.groupby(yr).sum().round(0).astype(int).to_dict())
    print(f"  Python   n={len(py)} avg ${py.net.mean():.0f} PF {pf(py.net):.2f}")
    mm = py[["day", "side", "entry", "exit", "net"]].merge(mc[["day", "side", "entry", "exit", "net"]], on="day",
                                                           how="outer", suffixes=("_py", "_mc"), indicator=True)
    b = mm[mm._merge == "both"]
    print(f"  match: {mm._merge.value_counts().to_dict()}; common days same side {np.mean(b.side_py == b.side_mc):.0%},"
          f" entry within 1 tick {np.mean(abs(b.entry_py - b.entry_mc - b.side_mc * 0.25) <= 0.26):.0%},"
          f" P&L corr {np.corrcoef(b.net_py, b.net_mc)[0, 1]:.3f}, Python ${b.net_py.mean():.0f} vs MC ${b.net_mc.mean():.0f}")
    for lab_, side in (("only in Python", "left_only"), ("only in MultiCharts", "right_only")):
        r = mm[mm._merge == side]
        if len(r):
            print(f"  {lab_} ({len(r)}):", ", ".join(f"{pd.Timestamp(g.ts[int(d)]).date()} ${v:.0f}"
                  for d, v in zip(r.day, r.net_py if side == "left_only" else r.net_mc)))
    return mm


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
    atr = g.daily_atr(15)
    nfp_mc = mc_list(g, "*5 Minutes NFP Fade*.xlsx"); vcs_mc = mc_list(g, "*Vol-Control Sell Flow*.xlsx")
    rel = E.release_days(g); ts = pd.DatetimeIndex(g.ts[rel])
    nfp_py = reaction_trades(g, rel[(ts.dayofweek == 4) & (ts.day <= 10)], 730, 745, 900, "fade", stop_k=0.5, atr=atr)
    vcs_py = A.vcs_trades(g, es, atr)
    print(__doc__.split("\n")[0])
    compare("NFP Fade", nfp_mc, nfp_py)
    compare("Vol-Control Sell Flow", vcs_mc, vcs_py)

    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]; D2 = days[days.year >= 2023]
    dl = lambda t, ix: t.groupby(t.date).net.sum().reindex(ix, fill_value=0.0)
    rows = {}
    for nm, t in (("NFP", nfp_mc), ("VCS", vcs_mc)):
        rows[f"{nm} 2018-26"] = (dl(t, days), t.net)
        rows[f"{nm} 2023-26"] = (dl(t[t.date.dt.year >= 2023], D2), t.net[t.date.dt.year >= 2023])
    for s_, nm in ((1, "longs"), (-1, "shorts")):
        t = nfp_mc[nfp_mc.side == s_]
        rows[f"NFP {nm} 2018-26"] = (dl(t, days), t.net)
    both = pd.concat([nfp_mc, vcs_mc]); rows["NFP + VCS 2018-26"] = (dl(both, days), both.net)
    print("\nStandard metrics per NQ (MultiCharts trades, +1 tick per fill):"); print(M.table(rows))
    B, P = R.report({"NFP 2023-26": dl(nfp_mc[nfp_mc.date.dt.year >= 2023], D2),
                     "VCS 2023-26": dl(vcs_mc[vcs_mc.date.dt.year >= 2023], D2),
                     "NFP + VCS 2023-26": dl(both[both.date.dt.year >= 2023], D2)}, n=5000)
    print("\nBootstrap 2023-26:"); print(B); print("\nPermutation 2023-26:"); print(P)

    lab = pickle.load(open(SP + "lab.pkl", "rb"))
    stop_n = np.full(g.D, np.nan); stop_n[:] = 0.5 * atr
    lab.add("NFP_MC", nfp_mc, stop_pts=0.5 * atr)           # slippage added by the lab (1 tick per market/stop fill)
    lab.add("VCS_MC", vcs_mc, stop_pts=0.25 * atr)
    dts2 = pd.DatetimeIndex(g.ts[lab.tr]); mk = dts2.year >= 2018
    Pd = {k: pd.Series(lab.daily(k), index=dts2)[mk] for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "VCS_MC")}
    print("\nCorrelation with the plan:"); print(pd.DataFrame(Pd).corr().round(2).loc[["NFP_MC", "VCS_MC"]].to_string())
    CS = dict(fmin=0.5, fmax=1.0, ref=2000.0)
    print("\nFunded bench (cushion sizing), MultiCharts lists:")
    plans = {"current plan": PLAN, "+ NFP $500": {**PLAN, "NFP_MC": ("risk", 500)}, "+ VCS 1 MNQ": {**PLAN, "VCS_MC": 1},
             "+ NFP $500 + VCS 1": {**PLAN, "NFP_MC": ("risk", 500), "VCS_MC": 1},
             "+ NFP $500 + VCS 2": {**PLAN, "NFP_MC": ("risk", 500), "VCS_MC": 2}}
    for nm, p in plans.items():
        a = lab.score(p, 250, **CS); b = lab.score(p, 500, **CS)
        print(f"  {nm:<22} 1y ${a['expected']:,.0f} (2023+ ${a['s2023_on']:,.0f}) 2y ${b['expected']:,.0f} blown {a['blown']:.0%} / {b['blown']:.0%}"
              f" | 1st payout {a['days_to_1st']:.0f}d")
    print("\nSpeed to $13k (3-year horizon), MultiCharts lists:")
    rows = {"current plan, ref $2,000": run(lab, PLAN), "current plan, ref $1,500": run(lab, PLAN, ref=1500.0)}
    for nm, p in (("+ NFP $500 + VCS 1", plans["+ NFP $500 + VCS 1"]), ("+ NFP $500 + VCS 2", plans["+ NFP $500 + VCS 2"])):
        rows[f"{nm}, ref $2,000"] = run(lab, p); rows[f"{nm}, ref $1,500"] = run(lab, p, ref=1500.0)
    print(fmt(pd.DataFrame(rows).T.drop(columns=["max_mnq"]).assign(paid1y=np.nan)))
