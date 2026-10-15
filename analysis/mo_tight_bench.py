"""Funded bench for Morning Momentum with a tight stop (round 2 'V3', analysis/mo_pullback_test.py): Twin's MO signal, market
entry, stop 0.10 x 15-day ATR, out at the 14:51 open; sized by fixed dollar risk (MNQ = floor(risk / (stop pts x $2))).
Added to the funded plan at $150 / $250 / $350 risk, and alone at $300 / $500 / $700. Cushion $1,500, 1 / 2 years. Also the
combine. The overnight / breakout leg is not used.
  python3 analysis/mo_tight_bench.py [SCRATCH_DIR]
"""
import sys, io, pickle, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
from mo_pullback_test import run
from portfolio import load_mc, paths, challenge
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def grid_of(g, X):
    W = np.zeros(g.o.shape); Rr = np.zeros(g.o.shape)
    for t in X.itertuples():
        seg = slice(t.ej, t.xj + 1); cost = (t.exit - t.entry) * t.side * 20 - t.net
        adv = ((g.l[t.row, seg] if t.side > 0 else g.h[t.row, seg]) - t.entry) * t.side * 20 - cost
        adv = np.nan_to_num(adv, nan=0.0); adv[-1] = t.net if t.kind == 0 else min(adv[-1], t.net)
        W[t.row, seg] += adv; W[t.row, t.xj + 1:] += t.net; Rr[t.row, t.xj:] += t.net
    return W, Rr


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; B = tc.flatten(g)
    T = tc.simulate(B, use_bo=False); T = T[T.setup == "MO"]
    sig = pd.DataFrame({"row": B["row"][T.sig_i.to_numpy()], "j": B["j"][T.sig_i.to_numpy()], "side": T.side.to_numpy(), "piv": T.piv.to_numpy()})
    sig = sig[pd.DatetimeIndex(g.ts[sig.row]) >= "2018-01-01"].reset_index(drop=True)
    X = run(g, sig, "V3"); X.to_pickle(SP + "mo_tight_trades.pkl")
    W, Rr = grid_of(g, X); lab.W["MOT"] = W[lab.tr] / 10; lab.C["MOT"] = Rr[lab.tr][:, -1] / 10
    lab.stop["MOT"] = np.nan_to_num(0.10 * g.daily_atr(15)[lab.tr], nan=1e12)
    q = lambda r: np.floor(r / (lab.stop["MOT"] * 2.0))
    print(f"trades {len(X)}; MNQ at $250 risk: 2018 median {np.median(q(250)[lab.yr == 2018]):.0f}, 2026 {np.median(q(250)[lab.yr == 2026]):.0f}")
    print("daily corr with the plan:", {k: round(float(np.corrcoef(lab.C["MOT"], lab.C[k])[0, 1]), 2) for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "MON_BR_MC")})
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    base = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
            "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    def show(nm, p):
        r = (lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0))
        print(f"   {nm:<30} ${r[0]['expected']:,.0f} / ${r[1]['expected']:,.0f}  blown {r[0]['blown']:.0%} / {r[1]['blown']:.0%}  paid {r[0]['any_payout']:.0%}"
              f"  all 6 in 2y {r[1]['all_6']:.0%}  days to 1st {r[0]['days_to_1st']:.0f} | 1y 2018-22 ${r[0]['s2018_22']:,.0f} 2023+ ${r[0]['s2023_on']:,.0f}", flush=True)
    show("plan", base)
    for r_ in (150, 250, 350): show(f"plan + MO-tight risk ${r_}", {**base, "MOT": ("risk", r_)})
    for r_ in (300, 500, 700): show(f"MO-tight alone risk ${r_}", {"MOT": ("risk", r_)})
    print("\nCombine (current set + MO-tight risk-sized):")
    atr = g.daily_atr(15); tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year; P = {}
    def add(nm, t): w, r = paths(g, t); P[nm] = (w[tr] / 10, r[tr] / 10)
    add("VB", with_slippage(load_mc(g, REPORTS["VB"][0])))
    add("ONB30", with_slippage(load_mc(g, "Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx")))
    add("MON_BR", load_bridge_mc(g)); add("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))
    P["MOT"] = (W[tr] / 10, Rr[tr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    q_onb = risk(1100, 0.25); q_eos = risk(500, REPORTS["EOS"][1])
    def score(r_mot):
        qm = risk(r_mot, 0.10) if r_mot else 0
        Wc = P["VB"][0] * 8 + P["ONB30"][0] * q_onb + P["MON_BR"][0] * 2 + P["EOS"][0] * q_eos + P["MOT"][0] * qm
        Rc = P["VB"][1] * 8 + P["ONB30"][1] * q_onb + P["MON_BR"][1] * 2 + P["EOS"][1] * q_eos + P["MOT"][1] * qm
        res = [challenge(Wc, Rc, np.arange(s, min(s + 21, D))) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018)
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        dd = np.array([np.nan if x is None or x[0] != "pass" else x[1] for x in res])
        return np.nanmean(o[ok]), np.nanmean(o[ok & (yr >= 2023)]), np.nanmedian(dd[ok])
    for r_ in (0, 200, 400, 600):
        a, b, d = score(r_); print(f"   combine + MO-tight ${r_}: pass {a:.1%} (2023-26 {b:.1%}), median days {d:.0f}")
