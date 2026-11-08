"""VIX-regime sizing (user 2026-11-08, after checker G13 flagged regime-dependent pieces). PRE-REGISTERED before running:
  regime: prior-day VIX close above its expanding median (past-only, >= 250 days) = 'volatile', else 'calm'.
  rule A: calm days trade x0.5 (contracts floored); rule B: calm days trade 0 (off). Applied to every piece alike.
  1. per piece: $ a trade on volatile vs calm days, 2018-22 and 2023+ (MC trade lists, lab costs)
  2. evaluation benches (50K / 150K, as cushion_cap_bench.py): pass / fail / time-out / fee per funded
  3. funded bench (funded_bootstrap.PLAN without CLS, VB 2): 1,000 paired bootstrap histories, 2 years
  tools/run_stamped.sh analysis/vix_regime_sizing.py > analysis/outputs/vix_regime_sizing_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL
from eval_sizing_bench import build, FEE
from cushion_cap_bench import run as ev_run, summary as ev_summary, R50, R150
from cushion_cap_funded import run_cap
from funded_bootstrap import PLAN


def regime(dates):
    v = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE.sort_index()
    hi = (v.shift(1) > v.expanding(250).median().shift(1))
    return hi.reindex(pd.DatetimeIndex(dates), method="ffill").fillna(True).to_numpy(bool)   # unknown -> full size


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    lab = pickle.load(open("scratch_data/lab.pkl", "rb")); dates = pd.DatetimeIndex(lab.g.ts[lab.tr]); yr = lab.yr
    VOL = regime(dates)
    print(f"\n1. Per piece, $ per NQ-equivalent day with a trade (lab, 2018+); volatile share of days {VOL[yr >= 2018].mean():.0%}:")
    for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "MON_BR_MC", "VCS_MC", "OND_MC"):
        c = lab.C[k] * 10; m = (c != 0) & (yr >= 2018)
        def s(mask):
            x = c[m & mask]; return f"${x.mean():6.0f} (n {len(x):4d}, t {x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan:4.1f})"
        print(f"   {k:<11} volatile {s(VOL)} calm {s(~VOL)} | 2018-22 vol/calm {c[m & VOL & (yr < 2023)].mean():5.0f}/{c[m & ~VOL & (yr < 2023)].mean():5.0f}"
              f" | 2023+ {c[m & VOL & (yr >= 2023)].mean():5.0f}/{c[m & ~VOL & (yr >= 2023)].mean():5.0f}")
    # ---- 2. evaluation benches
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    ey = pd.DatetimeIndex(g.ts[trr]).year; EV = regime(g.ts[trr])
    P = build(g, with_slippage(load_mc(g, REPORTS["VB"][0])), with_slippage(load_mc(g, CL.ONB30)), load_bridge_mc(g),
              with_slippage(load_mc(g, REPORTS["EOS"][0])))
    A = np.nan_to_num(atr[trr], nan=1e12); risk = lambda dollars, m: np.floor(dollars / (m * A * 2))
    for lab_, r, q0 in (("50K", R50, {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}),
                        ("150K", R150, {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])})):
        print(f"\n2. {lab_} evaluation, every start day 2018+:")
        for nm, f in (("plan", 1.0), ("A: calm days x0.5", 0.5), ("B: calm days off", 0.0)):
            q = {k: np.floor((np.broadcast_to(v, (D,)) * np.where(EV, 1.0, f)) + 1e-9) for k, v in q0.items()}
            print(ev_summary([ev_run(P, q, {}, s, D, r, "none", 0) for s in range(D)], ey, nm), flush=True)
    # ---- 3. funded bootstrap
    S_ = pd.read_pickle("scratch_data/single_print_sessions.pkl"); flag = S_.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    plan = {k: v for k, v in PLAN.items() if k != "CLS"}; names, base = lab._base(plan)
    W = np.ascontiguousarray(np.stack([lab.W[k] for k in names])); C = np.ascontiguousarray(np.stack([lab.C[k] for k in names]))
    S0 = np.zeros_like(base); days = np.where(dates >= "2018-01-01")[0]; rng = np.random.default_rng(1); n, H, L = 1000, 500, 20
    stb = rng.integers(0, len(days), (n, H // L)); hist = days[((stb[:, :, None] + np.arange(L)) % len(days)).reshape(n, -1)]
    V = {"plan": 1.0, "A: calm days x0.5": 0.5, "B: calm days off": 0.0}; Rr = {k: np.zeros((n, 6)) for k in V}
    for h in range(n):
        ix = hist[h]; Wh = np.ascontiguousarray(W[:, ix]); Ch = np.ascontiguousarray(C[:, ix]); Sh = np.ascontiguousarray(S0[:, ix])
        for nm, f in V.items():
            bh = np.ascontiguousarray(base[:, ix] * np.where(VOL[ix], 1.0, f)[None, :])
            Rr[nm][h] = run_cap(Wh, Ch, bh, Sh, 0, H, 0.5, 1.0, 1500.0, 0.0, 0)
    b0 = Rr["plan"][:, 0]; print("\n3. Funded 50K plan (VB 2, no CLS), 1,000 paired bootstrap histories, 2 years (regime label travels with each day):")
    for nm in V:
        r = Rr[nm]
        print(f"   {nm:<22} 2y payouts ${r[:, 0].mean():7,.0f}  blown {r[:, 3].mean():5.1%}  all 6 {np.mean(r[:, 1] == 6):5.1%}"
              f"  beats plan {np.mean(r[:, 0] > b0) + 0.5 * np.mean(r[:, 0] == b0):5.1%}  diff ${(r[:, 0] - b0).mean():+6,.0f}")
