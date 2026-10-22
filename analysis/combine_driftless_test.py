"""Driftless null for the combine (after 'A confirmed beta-harvest cannot pass a prop-firm challenge without regime
foreknowledge', trading2moon working paper July 2026, user's PDF: a challenge is a first-passage race; a pass rate is only
evidence of skill above the pass rate of the same paths with the market's drift removed; their NQ + GC beta basket passes
0.76 in the 2023-26 bull but 0.04 driftless).
Here, the current combine plan (VB 8 + ONB ADX30 $1,100 + Bridge Monday 2 + EOS $500, MNQ, 2018-2026, every start day,
Apex 50K rules in portfolio.challenge): each strategy's daily P&L per MNQ is regressed on NQ's daily P&L per MNQ (15:00 ->
15:00 CT) to get its beta, then
  (1) driftless: every day, beta x quantity x NQ's average daily P&L is taken off that strategy's path (the paper's
      de-meaning, applied through each strategy's own exposure; booked at the day's first minute = conservative)
  (2) alpha only: beta x quantity x NQ's ACTUAL P&L that day is taken off (the market component removed entirely)
Pass rate, blown rate, 2018-22 / 2023-26, for the plan as is, (1) and (2).
  python3 analysis/combine_driftless_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc, paths, challenge
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
ONB30 = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx"

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15)
    trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    C = pd.DataFrame(g.c[trr]).ffill(axis=1).to_numpy(); c15 = C[:, jof(1500)]
    nq = np.r_[0.0, np.diff(c15)] * 2.0                                  # NQ daily P&L per MNQ
    nq = np.nan_to_num(nq); mu = nq[yr >= 2018].mean()
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))
    Q = {"VB": np.full(D, 8.0), "ONB30": risk(1100, 0.25), "MON_BR": np.full(D, 2.0), "EOS": risk(500, REPORTS["EOS"][1])}
    beta = {}
    m18 = yr >= 2018
    for nm in P:
        y = P[nm][1][:, -1]                                              # day's P&L per MNQ (end of the path)
        X = np.column_stack([np.ones(m18.sum()), nq[m18]]); b = np.linalg.lstsq(X, y[m18], rcond=None)[0]; beta[nm] = b[1]
    print(f"NQ average daily P&L per MNQ ${mu:.1f}; betas per MNQ: " + ", ".join(f"{k} {v:.3f}" for k, v in beta.items()))
    print("drift taken off a day at full size (avg): " + ", ".join(f"{k} ${np.nanmean(beta[k] * Q[k][m18] * mu):.1f}" for k in P))

    def run(adj):
        W = sum(P[k][0] * Q[k][:, None] for k in P) - adj[:, None]; R = sum(P[k][1] * Q[k][:, None] for k in P) - adj[:, None]
        res = [challenge(W, R, np.arange(s, min(s + 21, D))) for s in range(D)]
        ok = np.array([x is not None for x in res]) & m18
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res]); fm = np.array([np.nan if x is None else float(x[0] == "fail_mll") for x in res])
        return np.nanmean(o[ok]), np.nanmean(o[ok & (yr < 2023)]), np.nanmean(o[ok & (yr >= 2023)]), np.nanmean(fm[ok])

    zero = np.zeros(D)
    drift = sum(beta[k] * np.nan_to_num(Q[k]) * mu for k in P)
    alpha = sum(beta[k] * np.nan_to_num(Q[k]) * nq for k in P)
    for nm, adj in (("plan as is", zero), ("(1) driftless (beta x avg NQ day removed)", drift), ("(2) alpha only (beta x actual NQ day removed)", alpha)):
        a, b, c, f = run(adj)
        print(f"   {nm:<48} pass {a:.1%} (2018-22 {b:.1%}, 2023-26 {c:.1%}), blown {f:.1%}", flush=True)
