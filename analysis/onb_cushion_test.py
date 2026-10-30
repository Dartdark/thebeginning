"""Overnight Bias (and VB) gated by the evaluation cushion (user, 2026-10-30, after #3 failed: ~$1,823 room, ONB short
liquidated on an intraday touch of the floor; #1 failed 10/26 on one VB stop with ~$400 room). Combine set VB 8 / ONB ADX30
$1,100 / Bridge Monday 2 / EOS $500 (150K: x 2.5, $4,000 trailing, $2,000 daily pause, +$9,000), every start day 2018-26.
Cushion = balance - trailing floor at the day's start. Rules fixed before running (5, per account size, k = 1 for 50K,
2.5 for 150K): ONB off when cushion < its risk ($1,100k); ONB off < 1.5 x its risk; ONB risk = min($1,100k, 50% of cushion);
ONB AND VB off when cushion < one VB stop ($1,200k); reference = plan. Same engine as vb_cushion_sizing_test.challenge.
  python3 analysis/onb_cushion_test.py > analysis/outputs/onb_cushion_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL

ACC = {"50K": dict(st=50_000.0, dd=2_000.0, dll=1_000.0, lock=50_100.0, tgt=3_000.0, k=1.0, maxd=21),
       "150K": dict(st=150_000.0, dd=4_000.0, dll=2_000.0, lock=150_100.0, tgt=9_000.0, k=2.5, maxd=21)}


def challenge(P, days, a, rule):
    """P: dict of (worst path, running path) per piece at its base size; rule(cushion) -> (vb_mult, onb_mult)."""
    bal = a["st"]; floor = a["st"] - a["dd"]
    for n, d in enumerate(days[:a["maxd"]], 1):
        kv, ko = rule(bal - floor)
        w = (P["VB"][0][d] * kv + P["ONB"][0][d] * ko + P["REST"][0][d]) * a["k"]
        r = (P["VB"][1][d] * kv + P["ONB"][1][d] * ko + P["REST"][1][d]) * a["k"]
        lim = max(floor, bal - a["dll"])
        hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
        win = np.nonzero(bal + r - a["st"] >= a["tgt"])[0]; jp = win[0] if len(win) else len(w)
        first = min(jb, jp)
        if first == len(w): bal = bal + r[-1]
        elif first == jp: return "pass", n
        else:
            if lim == floor: return "fail", n
            bal = lim
        floor = max(floor, min(bal - a["dd"], a["lock"]))
    return ("time", a["maxd"]) if len(days) >= a["maxd"] else None


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year; raw = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r = paths(g, t); raw[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    qo = risk(1100, 0.25); qe = risk(500, REPORTS["EOS"][1])
    P = {"VB": (raw["VB"][0] * 8, raw["VB"][1] * 8), "ONB": (raw["ONB30"][0] * qo, raw["ONB30"][1] * qo),
         "REST": (raw["MON_BR"][0] * 2 + raw["EOS"][0] * qe, raw["MON_BR"][1] * 2 + raw["EOS"][1] * qe)}
    for name, a in ACC.items():
        k = a["k"]; onb, vb = 1100 * k, 1200 * k
        rules = {"plan (everything always)": lambda c: (1.0, 1.0),
                 f"ONB off when cushion < ${onb:,.0f}": lambda c, x=onb: (1.0, 0.0 if c < x else 1.0),
                 f"ONB off when cushion < ${1.5 * onb:,.0f}": lambda c, x=1.5 * onb: (1.0, 0.0 if c < x else 1.0),
                 "ONB risk <= 50% of cushion": lambda c, x=onb: (1.0, min(1.0, 0.5 * c / x)),
                 f"ONB + VB off when cushion < ${vb:,.0f}": lambda c, x=vb: (0.0, 0.0) if c < x else (1.0, 1.0)}
        print(f"\n{name} evaluation (x{k}), every start day 2018-26:")
        for nm, rule in rules.items():
            res = [challenge(P, np.arange(s, min(s + a["maxd"], D)), a, rule) for s in range(D)]
            ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res])
            ps, fl, tm = (o == "pass")[ok].mean(), (o == "fail")[ok].mean(), (o == "time")[ok].mean()
            print(f"   {nm:<34} pass {ps:5.1%} (18-22 {(o == 'pass')[ok & (yr < 2023)].mean():5.1%}, 23-26 "
                  f"{(o == 'pass')[ok & (yr >= 2023)].mean():5.1%})  fail {fl:5.1%}  unfinished {tm:5.1%}  fails per pass {fl / ps:.2f}", flush=True)
