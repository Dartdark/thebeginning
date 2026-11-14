"""KAMA_TrendFollowing on BTC spot, 15 min, WITHOUT the 10-bar cooldown (user 2026-11-14). POST HOC: chosen after kama_trend_test showed
15-min BTC 2018-22 +$42 (t 2.3) and the 1h ingredient breakdown showed the cooldown hurting. Same harness; random-side placebo (100 runs);
plus the with-cooldown line on the same footing for comparison.
  tools/run_stamped.sh analysis/kama_btc15_nocool.py > analysis/outputs/kama_btc15_nocool_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
src = open("analysis/kama_trend_test.py").read().rsplit("\nRES = {}", 1)[0]; exec(compile(src, "kama_head", "exec"))
print(__doc__.split("\n")[0])
A = ksim(BTC, "15min", btc_cost).pipe(lambda T: T[T.ts >= "2018-01-01"])
B = ksim(BTC, "15min", btc_cost, drop="cooldown").pipe(lambda T: T[T.ts >= "2018-01-01"])
print(line(A, "15 min, as coded (cooldown)")); print(by_year(A))
print(line(B, "15 min, NO cooldown")); print(by_year(B))
print(f"   no cooldown: exits " + ", ".join(f"{k} {v}" for k, v in B.why.value_counts().items()) + f"; {len(B) / 8.85:.0f} trades a year; median hold {B.mins.median():.0f} min; worst ${B.net.min():,.0f} per BTC")
for nm, m in (("2018-2020", B.ts.dt.year <= 2020), ("2021-2022", B.ts.dt.year.between(2021, 2022)), ("2023-2024", B.ts.dt.year.between(2023, 2024)), ("2025-2026", B.ts.dt.year >= 2025)):
    print(f"   {nm}: n {m.sum()} avg ${B.net[m].mean():.1f} t {tt(B.net[m]):.2f}")
eq = B.net.cumsum(); print(f"   max drawdown ${(eq - eq.cummax()).min():,.0f} per BTC; total ${B.net.sum():,.0f}")
rng = np.random.default_rng(1); pl = np.array([ksim(BTC, "15min", btc_cost, drop="cooldown", rng=rng).pipe(lambda P: P[P.ts >= "2018-01-01"].net.mean()) for _ in range(100)])
print(f"   random side, same entries (100 runs): mean ${pl.mean():.1f}, p95 ${np.percentile(pl, 95):.1f} -> real ${B.net.mean():.1f}: p {np.mean(pl >= B.net.mean()):.3f}")
bf = B.assign(net=B.net + 0.0006 * (B.entry + B.exit) - (0.0004 * (B.entry + B.exit)))   # cheaper fees: 0.04% a side all-in (maker-ish)
print(line(bf, "no cooldown, fees 0.04% a side all-in"))
