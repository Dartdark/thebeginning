"""Evaluation sizing bench (user, 2026-11-04, after #2 and #4 failed on the same day): does smaller sizing fail less, and at what
cost in pass rate / speed? Combine set = VB 8 MNQ, ONB ADX30 risk $1,100, Bridge Monday 2, EOS risk $500 (50K); x 2.5 on 150K.
  A. 50K evaluation (combine_levers_test.challenge: +$3,000, $2,000 EOD trail touched intraday, $1,000 daily pause, 21 days),
     every start day 2018+, MultiCharts trade lists + 1 tick, sized in MNQ: VB 8/6/5/4, ONB $1,100/$800/$550, and a VB daily
     loss cap (no new VB trade after the day's first VB loss).
  B. 150K evaluation (plan_150k_test.evaluation, +$9,000, $4,000 trail): VB 20/15/12/10, ONB $2,750/$2,000/$1,400, VB loss cap.
  C. The live stretch: Python ports on the data extended with the VPS bar feed, start 10/20 (#2, 50K) and 11/02 (#4, 150K).
  Fee per funded account = fee / pass rate (150K No-Activation $249).
  python3 analysis/eval_sizing_bench.py > analysis/outputs/eval_sizing_bench_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from candidates24 import vault_break24, overnight_bias24
from grid import execute
import combine_levers_test as CL, plan_150k_test as P150

FEE = 249.0


def loss_cap(t):
    """Drop VB trades taken after the day's first losing VB trade."""
    keep = []
    for d, x in t.sort_values(["day", "j0"]).groupby("day"):
        lost = False
        for i, r in x.iterrows():
            if not lost: keep.append(i)
            if r.exit < r.entry if r.side > 0 else r.exit > r.entry: lost = True
    return t.loc[keep]


def build(g, vb, onb, mon=None, eos=None):
    trr = g.trading; P = {}
    items = [("VB", vb), ("VBC", loss_cap(vb)), ("ONB30", onb)] + ([("MON_BR", mon)] if mon is not None else []) + \
            ([("EOS", eos)] if eos is not None else [])
    for nm, t in items:
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    return P


def sized(P, q):
    Ws = sum(P[x][0] * q[x] for x in q); Rs = sum(P[x][1] * q[x] for x in q); return Ws, Rs


def summary(res, yr, nm, ok_mask=None):
    ok = np.array([x is not None for x in res]) & (yr >= 2018)
    o = np.array([x[0] if x else "" for x in res]); n = np.array([x[1] if x else 0 for x in res])
    ps, fl, tm = (o == "pass")[ok], (o == "fail")[ok], (o == "time")[ok]
    med = np.median(n[ok & (o == "pass")]) if ps.any() else np.nan
    r23 = (o == "pass")[ok & (yr >= 2023)].mean()
    return (f"   {nm:<34} pass {ps.mean():5.1%}  fail {fl.mean():5.1%}  time-out {tm.mean():5.1%}  | 2023+ pass {r23:5.1%}"
            f" | median days to pass {med:4.0f} | fee per funded ${FEE / max(ps.mean(), 1e-9):,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    P = build(g, with_slippage(load_mc(g, REPORTS["VB"][0])), with_slippage(load_mc(g, CL.ONB30)), load_bridge_mc(g),
              with_slippage(load_mc(g, REPORTS["EOS"][0])))
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    one = lambda p, c, n: 1.0
    print("\nA. 50K evaluation, every start day 2018+:")
    for nm, vbk, vbq, onb in (("plan: VB 8, ONB $1,100", "VB", 8, 1100), ("VB 6", "VB", 6, 1100), ("VB 5", "VB", 5, 1100), ("VB 4", "VB", 4, 1100),
                              ("ONB $800", "VB", 8, 800), ("ONB $550", "VB", 8, 550), ("VB 6, ONB $800", "VB", 6, 800),
                              ("VB 4, ONB $550 (half size)", "VB", 4, 550), ("VB 8 + VB loss cap", "VBC", 8, 1100),
                              ("VB 6 + VB loss cap", "VBC", 6, 1100), ("VB 6 + loss cap, ONB $800", "VBC", 6, 800)):
        q = {vbk: float(vbq), "ONB30": risk(onb, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
        Ws, Rs = sized(P, q)
        print(summary([CL.challenge(Ws, Rs, np.arange(s0, min(s0 + CL.MAXD, D)), one) for s0 in range(D)], yr, nm), flush=True)
    print("\nB. 150K evaluation (x 2.5 set), every start day 2018+:")
    for nm, vbk, vbq, onb in (("plan: VB 20, ONB $2,750", "VB", 20, 2750), ("VB 15", "VB", 15, 2750), ("VB 12", "VB", 12, 2750),
                              ("VB 10", "VB", 10, 2750), ("ONB $2,000", "VB", 20, 2000), ("ONB $1,400", "VB", 20, 1400),
                              ("VB 15, ONB $2,000", "VB", 15, 2000), ("VB 10, ONB $1,400 (half size)", "VB", 10, 1400),
                              ("VB 20 + VB loss cap", "VBC", 20, 2750), ("VB 15 + loss cap, ONB $2,000", "VBC", 15, 2000)):
        q = {vbk: float(vbq), "ONB30": risk(onb, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}
        Ws, Rs = sized(P, q)
        print(summary([P150.evaluation(Ws, Rs, s0, D, P150.R150) for s0 in range(D)], yr, nm), flush=True)

    print("\nC. The live stretch (Python ports on the extended data; Bridge / EOS had no trades in it):")
    ge = pickle.load(open("scratch_data/g24_ext.pkl", "rb")); atre = ge.daily_atr(15); tre = ge.trading
    s, kw = vault_break24(ge); vbp = execute(ge, s, **kw); onbp = overnight_bias24(ge, adx_min=30, stop_atr=0.25)
    Pe = build(ge, vbp, onbp)
    riske = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atre[tre], nan=1e12) * 2))[:, None]
    dts = pd.DatetimeIndex(ge.ts[tre])
    for start, which, sets in (("2026-10-20", 50, (("plan VB 8, ONB $1,100", "VB", 8, 1100), ("VB 6, ONB $800", "VB", 6, 800),
                                                   ("VB 4, ONB $550", "VB", 4, 550), ("VB 6 + loss cap, ONB $800", "VBC", 6, 800))),
                               ("2026-11-02", 150, (("plan VB 20, ONB $2,750", "VB", 20, 2750), ("VB 15, ONB $2,000", "VB", 15, 2000),
                                                    ("VB 10, ONB $1,400", "VB", 10, 1400), ("VB 15 + loss cap, ONB $2,000", "VBC", 15, 2000)))):
        s0 = int(dts.searchsorted(pd.Timestamp(start))); De = int(dts.searchsorted(pd.Timestamp("2026-11-05")))
        for nm, vbk, vbq, onb in sets:
            q = {vbk: float(vbq), "ONB30": riske(onb, 0.25)}
            Ws, Rs = sized(Pe, q)
            if which == 50: res = CL.challenge(Ws, Rs, np.arange(s0, De), one)
            else: res = P150.evaluation(Ws, Rs, s0, De, P150.R150)
            day_pnl = Rs[s0:De, -1]
            print(f"   {which}K from {start}  {nm:<30} -> {res if res else 'still open on 11/04'}; P&L to 11/04 ${day_pnl.sum():+,.0f}, "
                  f"worst day ${day_pnl.min():+,.0f}")
