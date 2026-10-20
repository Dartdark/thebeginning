"""Relative Strength 'aligned' (longs + shorts only when ES is down 8:30-9:00; Antigravity's NQRelativeStrength, 2026-10-20,
= WATCHLIST #25) vs the plan's RS longs only, on the bootstrapped 50K funded bench and the 150K funded single history.
The filter was found on the full 2018-26 sample (post hoc), so its own split is shown first.
  python3 analysis/relative_strength_aligned_bench.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import relative_strength_test as RS, funded_bootstrap as FB, funded_sim150 as F150

if __name__ == "__main__":
    days, N, E = RS.load(); T = RS.trades(days, N, RS.signals(days, N, E))
    re = pd.Series(E[:, 30] / E[:, 0] - 1, index=pd.DatetimeIndex([pd.Timestamp(str(x)) for x in days.date]))
    T["es_down"] = re.reindex(T.date).to_numpy() < 0
    AL = T[(T.side > 0) | T.es_down].reset_index(drop=True)
    for nm, t in (("RS both", T), ("RS longs", T[T.side > 0]), ("RS aligned", AL), ("  aligned shorts only", AL[AL.side < 0]),
                  ("  dropped shorts (ES up)", T[(T.side < 0) & ~T.es_down])): RS.line(nm, t)
    lab = FB.plan_lab(RS.SP); FB.add_moc_mes(lab, RS.SP); K = {"stop": 0, "target": 1, "flat": 2}
    for nm, t in (("RS", T), ("RS_L", T[T.side > 0]), ("RS_AL", AL)):
        t = t.reset_index(drop=True).copy(); t["kind"] = t.kind.map(K); lab.add(nm, t)
    CUR = {**FB.PLAN, "VB_N": 2, "MOC_MES": 2}
    plans = {"plan + RS longs 1 (now)": {**CUR, "RS_L": 1}, "plan + RS aligned 1": {**CUR, "RS_AL": 1},
             "plan + RS both 1": {**CUR, "RS": 1}, "plan without RS": CUR}
    print("\n50K funded, bootstrapped (1,000 paired histories):")
    df, s, _ = FB.Boot(lab).compare(plans, n=1000, L=20); print(s)
    sc = lambda plan, k: {n: (("risk", v[1] * k) if isinstance(v, tuple) else v * k) for n, v in plan.items()}
    print("\n150K funded (plan x 1.5, full from $3,000; single history):")
    for nm, add in (("+ RS both 1 (now)", {"RS": 1}), ("+ RS aligned 1", {"RS_AL": 1}), ("+ RS aligned 2", {"RS_AL": 2})):
        names, b = lab._base({**sc(CUR, 1.5), **add}); W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names]); o = []
        for h in (250, 500):
            r = F150.simulate_sized(W, C, b, horizon=h, starts=np.arange(0, lab.D - h), fmin=0.5, fmax=1.0, ref=3000.0)
            o.append((r["paid"].mean(), r["blown"].mean(), np.mean(r["payouts"] == 6)))
        print(f"   {nm:<22} 1y ${o[0][0]:,.0f} blown {o[0][1]:.0%} | 2y ${o[1][0]:,.0f} blown {o[1][1]:.0%} all 6 {o[1][2]:.0%}")
