"""Funded bench: Twin Continuation (analysis/twin_continuation_test.py) added to the funded plan (single-print VB 3 / 1, CL fade
2 MCL, cushion $1,500), at 1 / 2 / 3 MNQ, and its two setups alone. Overnight-held breakout trades are booked on their exit
date (the Apex day they close in), with the worst open loss since entry carried into that day.
  python3 analysis/twin_continuation_bench.py [SCRATCH_DIR]   (run twin_continuation_test.py and single_print_test.py first)
"""
import sys, io, pickle, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def grids(g, B, T):
    """worst / real $ per NQ, shaped like the grid (rows x 1440)."""
    W = np.zeros(g.o.shape); Rr = np.zeros(g.o.shape)
    for t in T.itertuples():
        idx = np.arange(t.i0, t.i1 + 1); rows, js = B["row"][idx], B["j"][idx]
        cost = (t.exit - t.entry) * t.side * tc.PV - t.net                     # commission + slippage of this trade
        adv = ((B["l"][idx] if t.side > 0 else B["h"][idx]) - t.entry) * t.side * tc.PV - cost
        adv[-1] = t.net if t.kind == 0 else min(adv[-1], t.net)
        r1 = rows[-1]; m = rows == r1; a = adv[m].copy()
        if (~m).any(): a[0] = min(a[0], adv[~m].min())                       # overnight part carried into the exit day
        W[r1, js[m]] += a; W[r1, js[-1] + 1:] += t.net; Rr[r1, js[-1]:] += t.net
    return W, Rr


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; B = tc.flatten(g); T = pd.read_pickle(SP + "twin_trades.pkl")
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    for nm, m in (("TWIN", np.ones(len(T), bool)), ("TW_BO", (T.setup == "BO").to_numpy()), ("TW_MO", (T.setup == "MO").to_numpy())):
        W, Rr = grids(g, B, T[m]); lab.W[nm] = W[lab.tr] / 10; lab.C[nm] = Rr[lab.tr][:, -1] / 10
    print("daily corr of Twin with the plan:", {k: round(float(np.corrcoef(lab.C["TWIN"], lab.C[k])[0, 1]), 2)
                                                for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "MON_BR_MC", "CLS")})
    print(f"Twin $/NQ a day {lab.daily('TWIN').mean():.1f} (BO {lab.daily('TW_BO').mean():.1f}, MO {lab.daily('TW_MO').mean():.1f})")
    base = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
            "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    sc = lambda p: (lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0))
    for nm, p in (("plan", base), ("+ Twin 1 MNQ", {**base, "TWIN": 1}), ("+ Twin 2 MNQ", {**base, "TWIN": 2}),
                  ("+ Twin 3 MNQ", {**base, "TWIN": 3}), ("+ MO only 2 MNQ", {**base, "TW_MO": 2}), ("+ BO only 2 MNQ", {**base, "TW_BO": 2}),
                  ("Twin 3 MNQ alone", {"TWIN": 3}), ("Twin 5 MNQ alone", {"TWIN": 5})):
        r = sc(p)
        print(f"   {nm:<20} ${r[0]['expected']:,.0f} / ${r[1]['expected']:,.0f}  blown {r[0]['blown']:.0%} / {r[1]['blown']:.0%}  paid {r[0]['any_payout']:.0%}"
              f" | 1y 2018-22 ${r[0]['s2018_22']:,.0f} 2023+ ${r[0]['s2023_on']:,.0f}")
