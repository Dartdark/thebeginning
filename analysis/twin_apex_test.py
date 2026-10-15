"""Can Twin Continuation work on Apex? (2026-10-15). Twin alone in its own 50K PA earned only $2.9k / $7.3k (1y / 2y) at
3 MNQ with the stop capped at 1 ATR, but blew only 6% / 3% -- so the binding rule is not the drawdown.
  A  diagnosis: the same account with the 50% consistency rule switched off (simulator only), sizes 2-6 MNQ
  B  pre-registered fixes for lumpy Morning Momentum wins (3 variants): MO profit target 100 / 150 / 200 points (limit),
     breakout stop capped at 1 ATR, in its own PA at 3 / 4 / 6 MNQ; then the best on top of the funded plan
Costs as always; funded bench cushion $1,500; 1 and 2 years.
  python3 analysis/twin_apex_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
from twin_continuation_bench import grids

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; B = tc.flatten(g)
    V = {"cap1": dict(max_stop_mult=1.0)}
    for T_ in (100, 150, 200): V[f"cap1_mo{T_}"] = dict(max_stop_mult=1.0, mo_target=float(T_))
    for nm, kw in V.items():
        T = tc.simulate(B, **kw); T = T[T.date >= "2018-01-01"].reset_index(drop=True); X = T.set_index("date")
        print(tc.line(X.net, nm) + f" | MO {X[X.setup == 'MO'].net.mean():.0f}, top 5% share of $ {X.net.nlargest(int(len(X) * .05)).sum() / X.net.sum():.0%}")
        W, Rr = grids(g, B, T); lab.W[nm] = W[lab.tr] / 10; lab.C[nm] = Rr[lab.tr][:, -1] / 10
    def show(nm, p, **kw):
        r = (lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0, **kw), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0, **kw))
        print(f"   {nm:<40} ${r[0]['expected']:,.0f} / ${r[1]['expected']:,.0f}  blown {r[0]['blown']:.0%} / {r[1]['blown']:.0%}  paid {r[0]['any_payout']:.0%}"
              f"  all 6 in 2y {r[1]['all_6']:.0%}  days to 1st {r[0]['days_to_1st']:.0f} | 1y 2018-22 ${r[0]['s2018_22']:,.0f} 2023+ ${r[0]['s2023_on']:,.0f}")
        return r
    print("\nA. Twin cap1 alone, consistency rule on vs off:")
    for q in (2, 3, 4, 6):
        show(f"cap1 {q} MNQ", {"cap1": q}); show(f"cap1 {q} MNQ, NO consistency rule", {"cap1": q}, consistency=False)
    print("\nB. MO profit target variants, own PA:")
    for nm in ("cap1_mo100", "cap1_mo150", "cap1_mo200"):
        for q in (3, 4, 6): show(f"{nm} {q} MNQ", {nm: q})
