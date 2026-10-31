"""Vault Break sized by the evaluation cushion (user, 2026-10-26, after account #1 failed on one VB stop with ~$400 cushion).
50K evaluation, combine set (VB 8 / ONB ADX30 $1,100 / Bridge Monday 2 / EOS $500), every start day 2018-26, Apex rules as in
combine_levers_test.challenge (EOD trailing $2,000, $1,000 daily stop, target $3,000). Cushion = balance - trailing floor at
the day's start. Rules fixed before running (5): VB 4 below $1,500 / below $1,200; VB skipped below $1,200; VB = whole
contracts with its 75-pt stop <= 50% of the cushion (max 8); the whole set x 0.5 below $1,000 (existing lever, reference).
  python3 analysis/vb_cushion_sizing_test.py > analysis/outputs/vb_cushion_sizing_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL

START, TARGET, MLL, DLL, LOCK, MAXD = CL.START, CL.TARGET, CL.MLL, CL.DLL, CL.LOCK, CL.MAXD


def challenge(V, O, Vr, Or, days, vb_fn, all_fn):
    bal = START; floor = START - MLL
    for n, d in enumerate(days[:MAXD], 1):
        c = bal - floor; kv = vb_fn(c); ka = all_fn(c)
        w = (V[d] * kv + O[d]) * ka; r = (Vr[d] * kv + Or[d]) * ka
        lim = max(floor, bal - DLL)
        hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
        win = np.nonzero(bal + r - START >= TARGET)[0]; jp = win[0] if len(win) else len(w)
        first = min(jb, jp)
        if first == len(w): bal = bal + r[-1]
        elif first == jp: return "pass", n
        else:
            if lim == floor: return "fail", n
            bal = lim
        floor = max(floor, min(bal - MLL, START + LOCK))
    return ("time", MAXD) if len(days) >= MAXD else None


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year; P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    V, Vr = P["VB"]; O = sum(P[k][0] * q[k] for k in q); Or = sum(P[k][1] * q[k] for k in q)
    one = lambda c: 1.0
    rules = {"plan: VB 8 always": (lambda c: 8.0, one),
             "VB 4 when cushion < $1,500": (lambda c: 4.0 if c < 1500 else 8.0, one),
             "VB 4 when cushion < $1,200": (lambda c: 4.0 if c < 1200 else 8.0, one),
             "VB off when cushion < $1,200": (lambda c: 0.0 if c < 1200 else 8.0, one),
             "VB stop <= 50% of cushion (max 8)": (lambda c: float(min(8, max(0, np.floor(0.5 * c / 150)))), one),
             "whole set x 0.5 when cushion < $1,000": (lambda c: 8.0, lambda c: 0.5 if c < 1000 else 1.0)}
    print(f"\n50K evaluation, {D} start days (2018+ counted); fee per attempt assumed $35 (Apex sale price) for cost per pass:")
    for nm, (vf, af) in rules.items():
        res = [challenge(V, O, Vr, Or, np.arange(s, min(s + MAXD, D)), vf, af) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res])
        ps, fl, tm = (o == "pass")[ok].mean(), (o == "fail")[ok].mean(), (o == "time")[ok].mean()
        nd = np.array([x[1] if x else 0 for x in res])
        print(f"   {nm:<40} pass {ps:5.1%} (18-22 {(o == 'pass')[ok & (yr < 2023)].mean():5.1%}, 23-26 {(o == 'pass')[ok & (yr >= 2023)].mean():5.1%})"
              f"  fail {fl:5.1%}  unfinished {tm:5.1%}  median days to pass {np.median(nd[ok & (o == 'pass')]):.0f}  fails per pass {fl / ps:.2f}", flush=True)
