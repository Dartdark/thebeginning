"""Cushion cap bench (user 2026-11-08, after Codex's 11/04 loss audit: on #2, #3, #4 one full ONB stop was larger than the room
left above the floor). Rule: at the start of each day, cushion = balance - floor; each piece trades
min(planned, floor((cushion - buffer) / stop per contract)) contracts (0 = skip). Pieces with a stop: VB (75 pts),
ONB ADX30 (0.25 ATR), EOS (0.30 ATR); Bridge Monday Long has no stop (exempt).
  per-piece   each stop alone fits the cushion (the audit's defect)
  combined    the day's stops together fit (ONB first, then VB, then EOS)
Same data / sizing / rules as analysis/eval_sizing_bench.py (MC trade lists + 1 tick, MNQ, every start day 2018+).
  tools/run_stamped.sh analysis/cushion_cap_bench.py > analysis/outputs/cushion_cap_bench_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL
from eval_sizing_bench import build, FEE

R50 = dict(st=50_000.0, dd=2_000.0, dll=1_000.0, lock=50_100.0, tgt=3_000.0)
R150 = dict(st=150_000.0, dd=4_000.0, dll=2_000.0, lock=150_100.0, tgt=9_000.0)
ORDER = ("ONB30", "VB", "EOS")


def run(P, q, stop, s, D, r, mode, buf, evalrule=False):
    # evalrule (Codex weekly review 2026-11-06 #1 / eval audit 2026-11-04): evaluation floor keeps trailing (no PA lock at
    # start + $100) and a same-minute target / floor tie counts as a FAIL (conservative). Default False = the old engine.
    bal = r["st"]; floor = r["st"] - r["dd"]; capped = skipped = 0
    for n, d in enumerate(range(s, min(s + 21, D)), 1):
        room = bal - floor - buf; qq = {}
        for x in q:
            qd = float(q[x][d]) if np.ndim(q[x]) else float(q[x])
            if mode != "none" and x in stop and qd > 0:
                fit = max(0.0, np.floor(room / stop[x][d])) if stop[x][d] > 0 else qd
                if fit < qd: capped += 1; skipped += fit == 0
                qd = min(qd, fit)
                if mode == "combined": room -= qd * stop[x][d]
            qq[x] = qd
        w = sum(P[x][0][d] * qq[x] for x in qq); rr = sum(P[x][1][d] * qq[x] for x in qq)
        lim = max(floor, bal - r["dll"])
        hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
        win = np.nonzero(bal + rr - r["st"] >= r["tgt"])[0]; jp = win[0] if len(win) else len(w)
        if jp < jb: return "pass", n, capped, skipped   # a same-minute tie already falls to the floor branch (FAIL)
        if jb < len(w):
            if lim == floor: return "fail", n, capped, skipped
            bal = lim
        else: bal += rr[-1]
        floor = max(floor, bal - r["dd"]) if evalrule else max(floor, min(bal - r["dd"], r["lock"]))
    return ("time", 21, capped, skipped) if s + 21 <= D else None


def summary(res, yr, nm):
    ok = np.array([x is not None for x in res]) & (yr >= 2018)
    o = np.array([x[0] if x else "" for x in res]); n = np.array([x[1] if x else 0 for x in res])
    cp = np.array([x[2] if x else 0 for x in res]); ps = o == "pass"
    return (f"   {nm:<40} pass {ps[ok].mean():5.1%}  fail {(o == 'fail')[ok].mean():5.1%}  time-out {(o == 'time')[ok].mean():5.1%}"
            f" | 2018-22 pass {ps[ok & (yr < 2023)].mean():5.1%} / 2023+ {ps[ok & (yr >= 2023)].mean():5.1%}"
            f" | median days {np.median(n[ok & ps]):3.0f} | fee/funded ${FEE / max(ps[ok].mean(), 1e-9):,.0f} | capped trades/acct {cp[ok].mean():.1f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    P = build(g, with_slippage(load_mc(g, CL.REPORTS["VB"][0] if hasattr(CL, "REPORTS") else REPORTS["VB"][0])), with_slippage(load_mc(g, CL.ONB30)),
              load_bridge_mc(g), with_slippage(load_mc(g, REPORTS["EOS"][0])))
    A = np.nan_to_num(atr[trr], nan=1e12)
    risk = lambda dollars, m: np.floor(dollars / (m * A * 2))
    stop = {"VB": np.full(D, 75 * 2.0), "ONB30": 0.25 * A * 2, "EOS": REPORTS["EOS"][1] * A * 2}
    for lab, r, q in (("50K (VB 8, ONB $1,100, Bridge 2, EOS $500)", R50,
                       {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}),
                      ("150K (VB 20, ONB $2,750, Bridge 5, EOS $1,250)", R150,
                       {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])})):
        print(f"\n{lab}, every start day 2018+:")
        for nm, mode, buf in (("plan (no cap)", "none", 0), ("per-piece cap, buffer $0", "piece", 0), ("per-piece cap, buffer $200", "piece", 200),
                              ("combined cap, buffer $0", "combined", 0), ("combined cap, buffer $200", "combined", 200)):
            print(summary([run(P, q, stop, s, D, r, mode, buf) for s in range(D)], yr, nm), flush=True)
