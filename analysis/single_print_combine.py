"""Combine (challenge) check for the single-print day flag (analysis/single_print_test.py): Vault Break at 8 MNQ normally and
fewer on flagged sessions, with the current combine set (VB 8 + ONB ADX30 $1,100 + Bridge Monday 2 + EOS $500).
Apex 50K challenge rules as in analysis/combine_addons_test.py (a challenge started on every trading day 2018-2026).
  python3 analysis/single_print_combine.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths, challenge
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15)
    tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year
    S = pd.read_pickle(SP + "single_print_sessions.pkl")
    flag = S.flag.reindex(pd.DatetimeIndex(g.ts[tr])).fillna(False).to_numpy().astype(bool)[:, None]
    P = {}
    def add(nm, t):
        w, r = paths(g, t); P[nm] = (w[tr] / 10, r[tr] / 10)
    add("VB", with_slippage(load_mc(g, REPORTS["VB"][0])))
    add("ONB30", with_slippage(load_mc(g, "Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx")))
    add("MON_BR", load_bridge_mc(g)); add("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    q_onb = risk(1100, 0.25); q_eos = risk(500, REPORTS["EOS"][1])

    def score(vb_n, vb_f, mask):
        q = np.where(mask, vb_f, vb_n)
        W = P["VB"][0] * q + P["ONB30"][0] * q_onb + P["MON_BR"][0] * 2 + P["EOS"][0] * q_eos
        Rr = P["VB"][1] * q + P["ONB30"][1] * q_onb + P["MON_BR"][1] * 2 + P["EOS"][1] * q_eos
        res = [challenge(W, Rr, np.arange(s, min(s + 21, D))) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018)
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        fm = np.array([np.nan if x is None else float(x[0] == "fail_mll") for x in res])
        days = np.array([np.nan if x is None or x[0] != "pass" else x[1] for x in res])
        return np.nanmean(o[ok]), np.nanmean(o[ok & (yr >= 2023)]), np.nanmedian(days[ok]), np.nanmean(fm[ok])
    print(f"{'VB size (other / flagged)':<30} pass 2018-26 | 2023-26 | median days | blown")
    for n_, f_ in ((8, 8), (8, 6), (8, 4), (8, 2), (8, 0), (10, 4)):
        a, b, d, fm = score(n_, f_, flag)
        print(f"{f'VB {n_} / {f_}':<30} {a:6.1%}      | {b:6.1%}  | {d:5.0f}       | {fm:6.1%}")
    rng = np.random.default_rng(5); pl = [score(8, 4, rng.random((D, 1)) < flag.mean())[0] for _ in range(10)]
    print(f"placebo VB 8 / 4 on random 30% days (10 draws): mean {np.mean(pl):.1%}, max {np.max(pl):.1%}")
