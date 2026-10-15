"""Funded bench + combine for the round-3 survivor (analysis/high_winrate_test.py): Twin's Morning Momentum signal, market
entry, target 0.10 x 15-day ATR, stop 0.20 x ATR, out at the 14:51 open; 75% winners. Risk-sized (MNQ = risk / (stop x $2)),
added to the funded plan at $150 / $250 / $350, alone at $300 / $500, longs-only variant at $250 (shorts are weak: Sharpe
0.57); combine + $200 / $400. Cushion $1,500, 1 / 2 years.
  python3 analysis/high_winrate_bench.py [SCRATCH_DIR]
"""
import sys, io, pickle, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import twin_continuation_test as tc
from high_winrate_test import exits
from mo_tight_bench import grid_of
from portfolio import load_mc, paths, challenge
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; B = tc.flatten(g)
    T = tc.simulate(B, use_bo=False); T = T[T.setup == "MO"]
    sig = pd.DataFrame({"row": B["row"][T.sig_i.to_numpy()], "j": B["j"][T.sig_i.to_numpy()], "side": T.side.to_numpy()})
    sig = sig[pd.DatetimeIndex(g.ts[sig.row]) >= "2018-01-01"].reset_index(drop=True)
    e1 = sig.assign(ej=sig.j + 1); e1["entry"] = g.o[e1.row, e1.ej]; e1 = e1.dropna(subset=["entry"]).assign(jx=jof(1451), xmode="open", slip_in=1)
    X = exits(g, e1.reset_index(drop=True), 0.10, 0.20).reset_index(); X.to_pickle(SP + "hw_trades.pkl")
    for nm, m in (("HW", np.ones(len(X), bool)), ("HWL", (X.side == 1).to_numpy())):
        W, Rr = grid_of(g, X[m]); lab.W[nm] = W[lab.tr] / 10; lab.C[nm] = Rr[lab.tr][:, -1] / 10
        lab.stop[nm] = np.nan_to_num(0.20 * g.daily_atr(15)[lab.tr], nan=1e12)
    print("daily corr with the plan:", {k: round(float(np.corrcoef(lab.C["HW"], lab.C[k])[0, 1]), 2) for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "MON_BR_MC")})
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    base = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
            "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    def show(nm, p):
        r = (lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0))
        print(f"   {nm:<28} ${r[0]['expected']:,.0f} / ${r[1]['expected']:,.0f}  blown {r[0]['blown']:.0%} / {r[1]['blown']:.0%}  paid {r[0]['any_payout']:.0%}"
              f"  all 6 in 2y {r[1]['all_6']:.0%}  days to 1st {r[0]['days_to_1st']:.0f} | 1y 2018-22 ${r[0]['s2018_22']:,.0f} 2023+ ${r[0]['s2023_on']:,.0f}", flush=True)
    show("plan", base)
    for r_ in (150, 250, 350): show(f"plan + HW risk ${r_}", {**base, "HW": ("risk", r_)})
    show("plan + HW longs risk $250", {**base, "HWL": ("risk", 250)})
    for r_ in (300, 500): show(f"HW alone risk ${r_}", {"HW": ("risk", r_)})
    print("\nCombine (current set + HW risk-sized):")
    atr = g.daily_atr(15); tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year; P = {}
    def add(nm, t): w, r = paths(g, t); P[nm] = (w[tr] / 10, r[tr] / 10)
    add("VB", with_slippage(load_mc(g, REPORTS["VB"][0])))
    add("ONB30", with_slippage(load_mc(g, "Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx")))
    add("MON_BR", load_bridge_mc(g)); add("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))
    W, Rr = grid_of(g, X); P["HW"] = (W[tr] / 10, Rr[tr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    q_onb = risk(1100, 0.25); q_eos = risk(500, REPORTS["EOS"][1])
    def score(r_):
        qh = risk(r_, 0.20) if r_ else 0
        Wc = P["VB"][0] * 8 + P["ONB30"][0] * q_onb + P["MON_BR"][0] * 2 + P["EOS"][0] * q_eos + P["HW"][0] * qh
        Rc = P["VB"][1] * 8 + P["ONB30"][1] * q_onb + P["MON_BR"][1] * 2 + P["EOS"][1] * q_eos + P["HW"][1] * qh
        res = [challenge(Wc, Rc, np.arange(s, min(s + 21, D))) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018)
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        dd = np.array([np.nan if x is None or x[0] != "pass" else x[1] for x in res])
        return np.nanmean(o[ok]), np.nanmean(o[ok & (yr >= 2023)]), np.nanmedian(dd[ok])
    for r_ in (0, 200, 400):
        a, b, d = score(r_); print(f"   combine + HW ${r_}: pass {a:.1%} (2023-26 {b:.1%}), median days {d:.0f}")
