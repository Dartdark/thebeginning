"""Anti-hedging lock (user's PDF 'MultiCharts Prop-Firm Anti-Hedging Lock', 2026-10-15) vs netting, on the funded plan.
Lock = one shared global slot: a strategy may only enter while NO other plan strategy holds a position (same side or opposite;
first come, first served). Opposite-only = the earlier netting script (skip only entries against an open opposite trade).
Based on analysis/plan_overlap_check.py (2026-10-14):  On one Apex account the broker nets all
NQ / MNQ positions; the script deletes any trade entered while an OPPOSITE trade from another strategy is open. Here: how
often that happens in the plan's MultiCharts trade lists (NQ strategies; the CL fade is another instrument), the P&L of the
trades the script would delete, and the funded bench with them removed vs kept.
  python3 analysis/plan_overlap_check.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
from funded_lab import with_slippage
from bridge_monday_confirm import load_bridge_mc
SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
F = {"VB": "Backtesting Strategy Performance Report VB v1.xlsx",
     "ONB_ML2_MC": "Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx",
     "MON_MC": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx",
     "EOS": "Backtesting Strategy Performance Report EOS v1.xlsx",
     "LDF_MC": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx",
     "NFP_MC": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes NFP Fade.xlsx"}
if __name__ == "__main__":
    print(__doc__.split("\n")[0]); sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")
    lab = ns["lab"]; g = lab.g; atr = g.daily_atr(15)
    raw = {k: load_mc(g, f) for k, f in F.items()}; raw["MON_BR_MC"] = load_bridge_mc(g)
    rows = []
    for k, t in raw.items():
        tt = with_slippage(t.copy()); net = (tt.exit - tt.entry) * tt.side * 20 - 7.25
        for i, r in t.reset_index(drop=True).iterrows():
            rows.append(dict(strat=k, i=i, side=r.side, a=r.day * 1440 + r.j0, b=r.day * 1440 + r.j1, net=net.iloc[i] if hasattr(net, "iloc") else net[i]))
    A = pd.DataFrame(rows).sort_values("a").reset_index(drop=True)
    print(f"NQ plan trades: {len(A)} ({A.strat.value_counts().to_dict()})")
    import os
    MODE = os.environ.get("LOCK_MODE", "any")
    longs, shorts, rej = [], [], []
    for r in A.itertuples():
        longs = [x for x in longs if x > r.a]; shorts = [x for x in shorts if x > r.a]
        blocked = (longs or shorts) if MODE == "any" else ((r.side > 0 and shorts) or (r.side < 0 and longs))
        if blocked: rej.append(r.Index); continue
        (longs if r.side > 0 else shorts).append(r.b)
    R = A.loc[rej]
    print(f"MODE {MODE}")
    print(f"trades the script would delete: {len(R)} ({len(R) / len(A):.1%}); by strategy {R.strat.value_counts().to_dict()}")
    print(f"   their P&L per NQ: total ${R.net.sum():,.0f}, avg ${R.net.mean():,.0f} (all plan trades avg ${A.net.mean():,.0f})")
    same = 0
    for r in A.itertuples():
        same += int(((A.a < r.a) & (A.b > r.a) & (A.side == r.side) & (A.strat != r.strat)).any())
    print(f"trades entered while a SAME-side plan trade is open (size stacks, nothing rejected): {same}")
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    keep = {k: set(A[(A.strat == k)].i) - set(R[R.strat == k].i) for k in raw}
    sa = {"VB": .30, "ONB_ML2_MC": .30, "MON_MC": .50, "EOS": .30, "LDF_MC": .25, "NFP_MC": .50}
    p2 = {"CLS": 2}
    for k, t in raw.items():
        t2 = t.reset_index(drop=True).loc[sorted(keep[k])].reset_index(drop=True)
        if k == "MON_BR_MC": lab.add(k + "_F", t2, slippage=False)
        else: lab.add(k + "_F", t2, stop_pts=sa[k] * atr)
        p2[k + "_F"] = plan[k]
    for nm, p in (("plan as is (trades summed)", plan), ("plan with the lock / deletions", p2)):
        a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        print(f"   {nm:<34} ${a['expected']:,.0f} / ${c['expected']:,.0f}  paid {a['any_payout']:.0%}  blown {a['blown']:.0%} / {c['blown']:.0%}")
