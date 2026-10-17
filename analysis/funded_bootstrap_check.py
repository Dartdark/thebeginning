"""Check that analysis/funded_bootstrap.py reproduces the single-history funded bench when fed the real consecutive windows (2026-10-17)."""
import sys; sys.path.insert(0, "analysis"); import numpy as np
import funded_bootstrap as FB
lab = FB.plan_lab(); B = FB.Boot(lab)
# replace the resampler with the real consecutive windows (every 5th start day) -> must match lab.score
H = 500; D = len(B.days); starts = np.arange(0, D - H, 5)
B._histories = lambda n, H, L, seed: np.stack([B.days[s:s + H] for s in starts])
res, y1, nmin = B.run({"plan": FB.PLAN}, n=len(starts), H=H)
print("real windows via the bootstrap code: 1y", round(y1["plan"].mean()), "2y", round(res["plan"][:, 0].mean()), "blown", res["plan"][:, 3].mean())
st = B.days[starts] - B.days[0]
import funded_sim as F
names, b = lab._base(FB.PLAN); W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names])
r = F.simulate_sized(W, C, b, horizon=H, starts=B.days[starts], fmin=0.5, fmax=1.0, ref=1500.0)
print("same windows via the original bench:  2y", round(r["paid"].mean()), "blown", r["blown"].mean())
