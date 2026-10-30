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
    """P: per-contract (worst path, running path) for VB / ONB and REST at its whole-contract size for this account;
    rule(cushion) -> (VB contracts, ONB risk dollars). ONB contracts = floor(risk dollars / its stop in $ per MNQ), whole
    contracts as the PowerLanguage code sizes them (Codex cross-review 2026-10-30: no fractional 50K quantities x 2.5)."""
    bal = a["st"]; floor = a["st"] - a["dd"]
    for n, d in enumerate(days[:a["maxd"]], 1):
        kv, dollars = rule(bal - floor); ko = np.floor(dollars / P["ONB_STOP"][d]) if P["ONB_STOP"][d] > 0 else 0.0
        w = P["VB"][0][d] * kv + P["ONB"][0][d] * ko + P["REST"][0][d]
        r = P["VB"][1][d] * kv + P["ONB"][1][d] * ko + P["REST"][1][d]
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
    for name, a in ACC.items():
        k = a["k"]; onb, vb, nvb = 1100 * k, 1200 * k, round(8 * k)
        qe = risk(500 * k, REPORTS["EOS"][1]); nbr = round(2 * k)
        P = {"VB": raw["VB"], "ONB": raw["ONB30"], "ONB_STOP": np.nan_to_num(0.25 * atr[trr] * 2, nan=1e12),
             "REST": (raw["MON_BR"][0] * nbr + raw["EOS"][0] * qe, raw["MON_BR"][1] * nbr + raw["EOS"][1] * qe)}
        rules = {"plan (everything always)": lambda c, x=onb, n=nvb: (n, x),
                 f"ONB off when cushion < ${onb:,.0f}": lambda c, x=onb, n=nvb: (n, 0.0 if c < x else x),
                 f"ONB off when cushion < ${1.5 * onb:,.0f}": lambda c, x=onb, n=nvb: (n, 0.0 if c < 1.5 * x else x),
                 "ONB risk <= 50% of cushion": lambda c, x=onb, n=nvb: (n, min(x, 0.5 * c)),
                 f"ONB + VB off when cushion < ${vb:,.0f}": lambda c, x=onb, y=vb, n=nvb: (0, 0.0) if c < y else (n, x)}
        print(f"\n{name} evaluation (x{k}), every start day 2018-26:")
        for nm, rule in rules.items():
            res = [challenge(P, np.arange(s, min(s + a["maxd"], D)), a, rule) for s in range(D)]
            ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x else "" for x in res])
            ps, fl, tm = (o == "pass")[ok].mean(), (o == "fail")[ok].mean(), (o == "time")[ok].mean()
            print(f"   {nm:<34} pass {ps:5.1%} (18-22 {(o == 'pass')[ok & (yr < 2023)].mean():5.1%}, 23-26 "
                  f"{(o == 'pass')[ok & (yr >= 2023)].mean():5.1%})  fail {fl:5.1%}  unfinished {tm:5.1%}  fails per pass {fl / ps:.2f}", flush=True)
