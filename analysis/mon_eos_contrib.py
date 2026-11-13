"""Bridge Monday Long and EOS in the live #5 book (user 2026-11-12: 'both barely trade ... only if they actually help').
Live book = bench150.LIVE_EVAL (ONB $3,500, EOS $1,250, MON_BR 5, Twin 2, DT 2, JF 1). Per piece: trades a year, $ a trade at live size,
win rate, worst day; then the eval with vs without it: fresh pass (2018-22 / 2023-26) and from #5 now, paired band, and the passes
it creates vs the passes it costs (evaluations that flip).
  tools/run_stamped.sh analysis/mon_eos_contrib.py > analysis/outputs/mon_eos_contrib_output.txt
"""
import sys; sys.path.insert(0, "analysis"); sys.argv = ["x"]
import numpy as np, pandas as pd
src = open("analysis/eval_size_combo.py").read().split("rows = []")[0].replace("cache=True", "cache=False")
ns = {}; exec(compile(src, "eval_size_combo_head", "exec"), ns)
book, fresh, now, mult, P, dts, DES, HOL, NOWV, LIVE = (ns[k] for k in ("book", "fresh", "now", "mult", "P", "dts", "DES", "HOL", "NOWV", "LIVE"))
def band(d):
    rng = np.random.default_rng(1); n = len(d); nb_ = int(np.ceil(n / 60)); st = rng.integers(0, n, (1000, nb_))
    mm = d[((st[:, :, None] + np.arange(60)) % n).reshape(1000, -1)[:, :n]].mean(1); return np.percentile(mm, 5), np.percentile(mm, 95)
W0, R0 = book(LIVE); f0 = fresh(W0, R0); n0 = now(W0, R0)
print(f"live {LIVE}: fresh 18-22 {f0[DES].mean():.1%} 23-26 {f0[HOL].mean():.1%} | #5 now {n0[NOWV].mean():.1%}")
yrs = dts.year
for k in ("MON_BR", "EOS", "TWIN", "DT", "JF", "ONB30"):
    m = mult(k, LIVE[k]); day = (P[k][1][:, -1:] * m)[:, 0] if np.ndim(m) else P[k][1][:, -1] * m
    tr = day[(day != 0) & (yrs >= 2018)]; y = yrs[(day != 0) & (yrs >= 2018)]
    per_y = pd.Series(tr).groupby(y).size()
    W, R = book({**LIVE, k: 0}); f = fresh(W, R); n = now(W, R)
    dh = f0[HOL] - f[HOL]; dd_ = f0[DES] - f[DES]; dn = n0[NOWV] - n[NOWV]
    print(f"\n== {k} (live {LIVE[k]}): {len(tr) / len(per_y):.0f} trading days a year (2018-26: {', '.join(f'{a % 100:02d}:{b}' for a, b in per_y.items())})")
    print(f"   per trade day ${tr.mean():,.0f}, win {np.mean(tr > 0):.0%}, best ${tr.max():,.0f}, worst ${tr.min():,.0f}, total ${tr.sum():,.0f} 2018-26")
    for nm, d, a, b in (("fresh 2018-22", dd_, f0[DES], f[DES]), ("fresh 2023-26", dh, f0[HOL], f[HOL]), ("#5 from now", dn, n0[NOWV], n[NOWV])):
        bb = band(d); gain = np.sum((a == 1) & (b == 0)); loss = np.sum((a == 0) & (b == 1))
        print(f"   {nm:<14}: with {a.mean():5.1%} vs without {b.mean():5.1%} -> it adds {d.mean():+.1%} (band {bb[0]:+.1%}/{bb[1]:+.1%}); evaluations it turns into passes {gain}, passes it costs {loss}")
