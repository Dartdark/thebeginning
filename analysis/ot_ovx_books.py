"""Overnight Tick sized by oil volatility, in the current books (user 2026-11-10: 'test it against the current books'). POST HOC
(Overnight Tick was the best of 19 in analysis/ovx_screen.py, t 2.55 < the 2.79 bar): information only; the honest test is the
2009-2017 NQ export in TODO. High-OVX night = the entry session's OVX close above the median of its past 252 closes (known at the
17:05 entry; OVX closes 15:15 CT).
  Personal book (Overnight Tick at 2 MNQ now): high 3 / low 2, high 4 / low 2, high 3 / low 1 (about the same average size).
  Funded 150K (plan x 1.5 + Twin 2, with Overnight Tick 2 MNQ as in FUNDED_PLAN): 2 every night vs 3 / 2 and 3 / 1.
  tools/run_stamped.sh analysis/ot_ovx_books.py > analysis/outputs/ot_ovx_books_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC, bench150 as BB
from new_sources_150k import daypaths
from new_data_filters_test import prior

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ovx = pd.read_csv("data/codex_20261108/OVX.csv", parse_dates=["date"]).set_index("date").close_index_points.astype(float)
    hi_fn = lambda s: float(s.iloc[-1] > s.iloc[-252:].median()) if len(s) >= 120 else np.nan
    P = pd.read_pickle("scratch_data/personal_P.pkl"); ot = P.OvernightTick; on = ot[ot != 0]
    hi = pd.Series(prior(ovx, on.index, hi_fn) == 1, index=on.index)
    print(f"   personal: OT nights {len(on)}, high-OVX {hi.mean():.0%}; $ a night per MNQ high ${on[hi].mean():.0f} / low ${on[~hi].mean():.0f}")
    f = lambda x: (lambda r: (r["pnl_p50"], r["dd_p95"], r["pnl_p50"] / r["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    for lab, cols in (("full", list(P.columns)), ("core", [c for c in P.columns if c not in ("FC2B", "Kusho", "S47", "S30")])):
        base = P[cols].sum(axis=1) + ot                                   # OT at 2 MNQ (the plan)
        print(f"\n   {lab} book (OT 2 MNQ every night):")
        for nm, h, l in (("high 3 / low 2", 3, 2), ("high 4 / low 2", 4, 2), ("high 3 / low 1", 3, 1)):
            m = pd.Series(2.0, index=P.index); m[on.index[hi.values]] = h; m[on.index[~hi.values]] = l
            alt = base - 2 * ot + ot * m; parts = []
            for per, mm in (("2018-26", np.ones(len(P), bool)), ("2018-22", P.index.year <= 2022), ("2023+", P.index.year >= 2023)):
                x, y = f(base[mm]), f(alt[mm]); parts.append(f"{per} {x[2]:.2f} -> {y[2]:.2f} ({y[2] - x[2]:+.2f}; median ${y[0] - x[0]:+,.0f}, DD ${y[1] - x[1]:+,.0f})")
            print(f"      {nm}: " + " | ".join(parts), flush=True)
    print("\n   Funded 150K:")
    ctx = BB.setup(); D, dts = ctx["D"], ctx["dts"]; dp = pd.Series(np.arange(D), index=dts)
    N = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date", "sess"]); N = N[N.down & ~N.half & N.rsv.notna() & N.hi25.notna()]
    N = N[((N.rsv < 0) & N.hi25.astype(bool)) | ((N.rsv >= 0) & ~N.hi25.astype(bool))]
    W, R = daypaths(D, [(int(dp[d]) if d in dp.index else None, a, n) for d, a, n in zip(N.date, N.adv, N.net)])
    hN = prior(ovx, pd.DatetimeIndex(N.date), hi_fn) == 1; hd = set(pd.DatetimeIndex(N.date)[hN])
    ext = {"OT": (W, R[:, -1])}; var = {"+ OT 2 every night": {**BB.BASE_FUNDED, "OT": 2}}
    for nm, h, l in (("3 / 2", 3, 2), ("3 / 1", 3, 1)):
        m = np.array([h if d in hd else l for d in dts], float); key = f"OT_{h}{l}"
        ext[key] = (W * m[:, None], R[:, -1] * m); var[f"+ OT high {nm}"] = {**BB.BASE_FUNDED, key: 1}
    BB.funded_bench(ctx, var, extra=ext)
