"""Funded plan: does anything else from 2026-10-13 help? (after adding the Bridge Monday Long)

Bench: funded_lab (Apex 50K PA rules, cushion sizing f = cushion / $1,500 in 0.5-1), every start day 2018-2026;
speed = analysis/speed_to_13k.py (median trading days to the 6th payout). Candidates from today's tests that were
within noise or not yet combined: DriftPullback shorts 1 MNQ (Python replica), Vol-Control Sell at 2 MNQ, Late-Day
Flow longs filtered by the last-30-minute order-flow delta, Overnight Bias ML with the Bridge's OR-size band.
  python3 analysis/funded_today_check.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from bridge_monday_confirm import load_bridge_mc
from speed_to_13k import run as speed, fmt

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); lab = pickle.load(open(SP + "lab.pkl", "rb"))
    lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    dp = pickle.load(open(SP + "drift_pullback.pkl", "rb"))["base"]
    lab.add("DPB_S", dp[dp.side < 0].reset_index(drop=True), slippage=False)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500),
            "VCS_MC": 1, "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    cands = {"current plan (8 strategies)": plan,
             "+ DriftPullback shorts 1 MNQ": {**plan, "DPB_S": 1},
             "VCS 2 MNQ instead of 1": {**plan, "VCS_MC": 2},
             "Bridge Monday 2 MNQ instead of 1": {**plan, "MON_BR_MC": 2},
             "EOS $500 instead of $700": {**plan, "EOS": ("risk", 500)},
             "without our Monday Long (Bridge's only)": {k: v for k, v in plan.items() if k != "MON_MC"}}
    print(__doc__.split("\n")[0])
    rows = {}
    for nm, p in cands.items():
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<42} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        rows[nm] = speed(lab, p, fmin=0.5, fmax=1.0, ref=1500.0)
    print("\nSpeed to $13k:")
    print(fmt(pd.DataFrame(rows).T))
