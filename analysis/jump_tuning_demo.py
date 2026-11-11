"""How much win rate / profit factor does TUNING alone buy on a 0.3R-target jump rule? (demo, not a candidate; user upload 2026-11-11)
Grid on the screenshot's window (2019-01 .. 2026-11), NO costs (as in the screenshot): |J| threshold x follow / fade x stop size
(k x jump-bar range) x entry window (start hour, length). Trades are independent events (no one-at-a-time rule).
Then the honest check: pick the best on the first half (2019-2022), read the same rule on the second half (2023-2026).
  tools/run_stamped.sh analysis/jump_tuning_demo.py > analysis/outputs/jump_tuning_demo_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd, jump_lib as L, jump_study as S
b = L.bars(); M = S.Mkt(); yr = b.ts.dt.year.to_numpy(); sgn = np.sign(b.r).fillna(0).to_numpy(); aJ = b.J.abs().to_numpy()
base = (yr >= 2019) & (aJ > 2.5); rows = []; E = {}
for d, sd in (("follow", sgn), ("fade", -sgn)):
    for k in (0.5, 1.0, 1.5, 2.0):
        t = S.trades(b, M, base, sd, "rng", k, tp=0.3, hold=240, cost=False, one=False)
        t["aJ"] = aJ[t.q]; t["hr"] = pd.DatetimeIndex(t.ts).hour; t["y"] = pd.DatetimeIndex(t.ts).year; E[d, k] = t
def st(x):
    g = x.gross; return len(x), np.mean(g > 0), g[g > 0].sum() / max(1.0, -g[g < 0].sum()), g.mean()
for (d, k), t in E.items():
    for thr in (2.5, 3, 3.5, 4, 5):
        for h0 in range(0, 24):
            for ln in (2, 3, 4, 6, 8, 12, 24):
                hrs = [(h0 + i) % 24 for i in range(ln)]
                if ln == 24 and h0: continue
                x = t[(t.aJ > thr) & t.hr.isin(hrs)]
                if len(x) < 400: continue
                a, c = x[x.y <= 2022], x[x.y >= 2023]
                if len(a) < 150 or len(c) < 150: continue
                rows.append((d, k, thr, h0, ln) + st(x) + st(a) + st(c))
R = pd.DataFrame(rows, columns="dir k thr h0 len n win pf avg n1 win1 pf1 avg1 n2 win2 pf2 avg2".split())
print(f"{len(R)} rule versions with >= 400 trades (>= 150 in each half). Breakeven win rate at 0.3R = 76.9%, PF 1.00. Screenshot: 855 trades, 82.2%, PF 1.41.")
print(f"whole window: median PF {R.pf.median():.2f}, best PF {R.pf.max():.2f}; versions with PF >= 1.41: {(R.pf >= 1.41).sum()}, PF >= 1.25: {(R.pf >= 1.25).sum()}, win >= 82%: {(R.win >= .82).sum()}")
print("\nTop 8 by whole-window PF (what a tuner would show):")
print(R.sort_values("pf", ascending=False).head(8)[["dir", "k", "thr", "h0", "len", "n", "win", "pf", "avg", "pf1", "pf2"]].round(3).to_string(index=False))
top = R.sort_values("pf1", ascending=False).head(20)
print(f"\nPick the 20 best on 2019-22 only: first-half PF {top.pf1.mean():.2f} (win {top.win1.mean():.1%}) -> same rules on 2023-26: PF {top.pf2.mean():.2f} (win {top.win2.mean():.1%}); {(top.pf2 > 1).sum()} of 20 still above 1.00")
print(f"rank correlation of first-half PF with second-half PF across all versions: {R.pf1.rank().corr(R.pf2.rank()):.2f}")
