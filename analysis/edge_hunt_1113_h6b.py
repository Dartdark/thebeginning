"""Edge hunt Amendment 1 (checks/candidates/edge_hunt_1113/PREREG.md): H6b Friday afternoon long 13:01 -> 14:55 CT, stop 0.3 ATR.
Design 2018-22 first; the holdout is printed only if G1 passes (avg > 0, t >= 2.0, Fridays beat Mon-Thu).
  tools/run_stamped.sh analysis/edge_hunt_1113_h6b.py > analysis/outputs/edge_hunt_1113_h6b_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
src = open("analysis/edge_hunt_1113.py").read().split("# ---------------- setups")[0]; exec(compile(src, "hunt_head", "exec"))
def setups(dow):
    return [(d, F(d, 1300) + 1, 1, rt(0.3 * atr[d]), None, F(d, 1455)) for d in TR if ts[d].dayofweek in dow and np.isfinite(C[F(d, 1300)])]
Tf = run(setups([4])); Tf = Tf[Tf.date >= "2018-01-01"]; To = run(setups([0, 1, 2, 3])); To = To[To.date >= "2018-01-01"]
de, do = Tf[Tf.date.dt.year <= 2022], To[To.date.dt.year <= 2022]
by = " ".join(f"{k % 100:02d}:{v / 1000:+.1f}k" for k, v in de.net.groupby(de.date.dt.year).sum().items())
print(f"DESIGN 2018-22: Fridays {stat(de.net, '')} | Mon-Thu {stat(do.net, '')}\n   Fridays by year: {by}")
print("   by weekday (design): " + " | ".join(f"{'MTWTF'[k]} ${v.mean():.0f} (t {tt(v):.1f})" for k, v in pd.concat([de, do]).groupby(pd.concat([de, do]).date.dt.dayofweek).net))
diff = de.net.mean() - do.net.mean(); se = np.sqrt(de.net.var() / len(de) + do.net.var() / len(do))
g1 = de.net.mean() > 0 and tt(de.net) >= 2.0 and diff > 0
print(f"   Friday minus Mon-Thu ${diff:.0f} (t {diff / se:.2f}); G1: {'PASS' if g1 else 'FAIL -> holdout not opened'}")
if g1:
    ho = Tf[Tf.date.dt.year >= 2023]; hoo = To[To.date.dt.year >= 2023]
    by = " ".join(f"{k % 100:02d}:{v / 1000:+.1f}k" for k, v in ho.net.groupby(ho.date.dt.year).sum().items())
    print(f"HOLDOUT 2023-26: Fridays {stat(ho.net, '')} | Mon-Thu {stat(hoo.net, '')}\n   by year: {by}\n   whole sample Fridays: {stat(Tf.net, '')}")
    allT = pd.concat([Tf, To]); rng = np.random.default_rng(1); pl = np.array([allT.net.sample(len(Tf), random_state=int(rng.integers(1e9))).mean() for _ in range(2000)])
    print(f"   G2: {'PASS' if ho.net.mean() > 0 and tt(ho.net) >= 1.5 and tt(Tf.net) >= 2.5 else 'FAIL'} | G3 placebo (random weekdays, 2000 draws): mean ${pl.mean():.0f}, p95 ${np.percentile(pl, 95):.0f}, p {np.mean(pl >= Tf.net.mean()):.3f}")
Tf.to_csv("checks/candidates/edge_hunt_1113/trades_H6b.csv", index=False)
