"""Size UP on volatile-VIX days (user 2026-11-08; follow-up to WATCHLIST #29). Volatile = prior-day VIX above its past-only
median (vix_regime_sizing.regime). Post hoc pieces VB + LDF only (they were better on volatile days in both halves).
  funded: the 50K plan (VB 2, no CLS) WITH the cushion cap; VB + LDF x1.5 / x2 on volatile days (calm days normal);
          same 1,000 paired bootstrap histories as cushion_cap_funded.py
  evaluations: VB x1.25 / x1.5 on volatile days (50K VB 8 -> 10 / 12; 150K 20 -> 25 / 30), every start day 2018+
  tools/run_stamped.sh analysis/vix_sizeup.py > analysis/outputs/vix_sizeup_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL
from eval_sizing_bench import build
from cushion_cap_bench import run as ev_run, summary as ev_summary, R50, R150
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
    V = {"cushion cap (adopted)": (1.0, 1.0), "VB + LDF x1.5 volatile": (1.5, 1.0), "VB + LDF x2 volatile": (2.0, 1.0),
         "x1.5 volatile, x0.5 calm": (1.5, 0.5)}
    Rr = {k: np.zeros((n, 6)) for k in V}
    for h in range(n):
        ix = hist[h]; Wh = np.ascontiguousarray(W[:, ix]); Ch = np.ascontiguousarray(C[:, ix]); Sh = np.ascontiguousarray(S[:, ix])
        for nm, (up, dn) in V.items():
            mult = np.ones((len(names), len(ix))); mult[sel] = np.where(VOL[ix], up, dn)[None, :]
            Rr[nm][h] = run_cap(Wh, Ch, np.ascontiguousarray(base[:, ix] * mult), Sh, 0, H, 0.5, 1.0, 1500.0, 0.0, 1)
    b0 = Rr["cushion cap (adopted)"][:, 0]
    print("\nFunded 50K (VB 2, no CLS) with the cushion cap, 1,000 paired histories, 2 years:")
    for nm in V:
        r = Rr[nm]
        print(f"   {nm:<26} 2y ${r[:, 0].mean():7,.0f} (p5 ${np.percentile(r[:, 0], 5):6,.0f})  blown {r[:, 3].mean():5.1%}  all 6 {np.mean(r[:, 1] == 6):5.1%}"
              f"  median days to 6th {np.median(np.where(r[:, 1] == 6, r[:, 2], np.inf)):4.0f}  beats cap {np.mean(r[:, 0] > b0) + 0.5 * np.mean(r[:, 0] == b0):5.1%}"
              f"  diff ${(r[:, 0] - b0).mean():+5,.0f}")
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    ey = pd.DatetimeIndex(g.ts[trr]).year; EV = regime(g.ts[trr])
    P = build(g, with_slippage(load_mc(g, REPORTS["VB"][0])), with_slippage(load_mc(g, CL.ONB30)), load_bridge_mc(g),
              with_slippage(load_mc(g, REPORTS["EOS"][0])))
    A = np.nan_to_num(atr[trr], nan=1e12); risk = lambda dollars, m: np.floor(dollars / (m * A * 2))
    for lab_, r, q0 in (("50K", R50, {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}),
                        ("150K", R150, {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])})):
        print(f"\n{lab_} evaluation, every start day 2018+:")
        for nm, up in (("plan", 1.0), ("VB x1.25 volatile", 1.25), ("VB x1.5 volatile", 1.5)):
            q = {k: (np.floor(np.broadcast_to(v, (D,)) * np.where(EV, up, 1.0) + 1e-9) if k == "VB" else np.broadcast_to(v, (D,))) for k, v in q0.items()}
            print(ev_summary([ev_run(P, q, {}, s, D, r, "none", 0) for s in range(D)], ey, nm), flush=True)
