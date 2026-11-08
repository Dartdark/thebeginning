"""WATCHLIST #29 with the cushion cap (user 2026-11-08): VB + LDF half size on calm-VIX days, on top of the funded plan with the
per-strategy cushion cap (FUNDED_PLAN 'Cushion cap'). Same 1,000 paired bootstrap histories (seed 1, L 20, 2 years) as
cushion_cap_funded.py / vix_regime_sizing_followup.py. Post hoc piece choice (see #29).
  tools/run_stamped.sh analysis/vix_cap_combo.py > analysis/outputs/vix_cap_combo_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from cushion_cap_funded import run_cap
from funded_bootstrap import PLAN
from vix_regime_sizing import regime

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    lab = pickle.load(open("scratch_data/lab.pkl", "rb")); dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); VOL = regime(dates)
    S_ = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = S_.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    plan = {k: v for k, v in PLAN.items() if k != "CLS"}
    order = ["ONB_ML2_MC", "VB_N", "VB_F", "EOS", "NFP_MC", "LDF_MC", "MON_MC", "MON_BR_MC"]
    names, b = lab._base(plan); ix0 = [names.index(k) for k in order]; names = [names[i] for i in ix0]; base = b[ix0]
    W = np.ascontiguousarray(np.stack([lab.W[k] for k in names])); C = np.ascontiguousarray(np.stack([lab.C[k] for k in names]))
    S = np.zeros_like(base)
    for i, k in enumerate(names):
        if k in ("VB_N", "VB_F"): S[i] = 150.0
        elif k in lab.stop: S[i] = lab.stop[k] * 2.0
    sel = np.array([k in ("VB_N", "VB_F", "LDF_MC") for k in names])
    days = np.where(dates >= "2018-01-01")[0]; rng = np.random.default_rng(1); n, H, L = 1000, 500, 20
    stb = rng.integers(0, len(days), (n, H // L)); hist = days[((stb[:, :, None] + np.arange(L)) % len(days)).reshape(n, -1)]
    V = {"plan (no cap)": (1.0, 0), "cushion cap": (1.0, 1), "VB + LDF calm x0.5": (0.5, 0), "cap + VB + LDF calm x0.5": (0.5, 1)}
    Rr = {k: np.zeros((n, 6)) for k in V}
    for h in range(n):
        ix = hist[h]; Wh = np.ascontiguousarray(W[:, ix]); Ch = np.ascontiguousarray(C[:, ix]); Sh = np.ascontiguousarray(S[:, ix])
        for nm, (f, mode) in V.items():
            mult = np.ones((len(names), len(ix))); mult[sel] = np.where(VOL[ix], 1.0, f)[None, :]
            Rr[nm][h] = run_cap(Wh, Ch, np.ascontiguousarray(base[:, ix] * mult), Sh, 0, H, 0.5, 1.0, 1500.0, 0.0, mode)
    for ref in ("plan (no cap)", "cushion cap"):
        b0 = Rr[ref][:, 0]; print(f"\nFunded 50K plan (VB 2, no CLS), 1,000 paired histories, 2 years; compared with '{ref}':")
        for nm in V:
            r = Rr[nm]
            print(f"   {nm:<26} 2y payouts ${r[:, 0].mean():7,.0f} (p5 ${np.percentile(r[:, 0], 5):6,.0f})  blown {r[:, 3].mean():5.1%}"
                  f"  all 6 {np.mean(r[:, 1] == 6):5.1%}  median days to 6th {np.median(np.where(r[:, 1] == 6, r[:, 2], np.inf)):4.0f}"
                  f"  beats {np.mean(r[:, 0] > b0) + 0.5 * np.mean(r[:, 0] == b0):5.1%}  diff ${(r[:, 0] - b0).mean():+5,.0f}")
