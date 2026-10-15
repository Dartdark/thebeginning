"""Twin Continuation as its OWN funded account (2026-10-15): the plan's account is near the $13,000 payout cap, so a new
edge adds risk there; a separate Apex 50K PA running only Twin (stop capped at 1 x ATR, the code's BO_MaxStopMult) or only
Morning Momentum. Cushion sizing $1,500, 1 / 2 years.
  python3 analysis/twin_continuation_alone.py [SCRATCH_DIR]   (after twin_continuation_variants.py inputs exist)
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
    T = tc.simulate(B, max_stop_mult=1.0); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    for nm, m in (("cap1", np.ones(len(T), bool)), ("MO", (T.setup == "MO").to_numpy())):
        W, Rr = grids(g, B, T[m]); lab.W[nm] = W[lab.tr] / 10; lab.C[nm] = Rr[lab.tr][:, -1] / 10
    sc = lambda p: (lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0))
    for nm, p in (("Twin cap1 2 MNQ", {"cap1": 2}), ("Twin cap1 3 MNQ", {"cap1": 3}), ("Twin cap1 4 MNQ", {"cap1": 4}),
                  ("Twin cap1 6 MNQ", {"cap1": 6}), ("MO 3 MNQ", {"MO": 3}), ("MO 5 MNQ", {"MO": 5}), ("MO 8 MNQ", {"MO": 8})):
        r = sc(p)
        print(f"   {nm:<18} ${r[0]['expected']:,.0f} / ${r[1]['expected']:,.0f}  blown {r[0]['blown']:.0%} / {r[1]['blown']:.0%}  paid {r[0]['any_payout']:.0%}"
              f"  all 6 in 2y {r[1]['all_6']:.0%} | 1y 2018-22 ${r[0]['s2018_22']:,.0f} 2023+ ${r[0]['s2023_on']:,.0f}")
