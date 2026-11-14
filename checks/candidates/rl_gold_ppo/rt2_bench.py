"""Benchmarks on the SAME sliding test windows, same env and costs: always-long, always-short, random direction (20 seeds, random brackets),
their trend_hold baseline (defaults 0.7 / sl 2.0 ATR / tp 3R). Per-trade R; long / short split."""
import sys, os
os.chdir(sys.argv[1]); sys.path.insert(0, sys.argv[1])
from pathlib import Path
import numpy as np, pandas as pd
import config
config.CFG.csv_path = Path("data/GC_1min_adj.csv"); config.CFG.spread_price = 0.0; config.CFG.slippage_price = 0.4625; config.CFG.commission_per_trade = 0.0
import train_ppo as T, baselines as B
from data_loader import make_sliding_folds
CFG = config.CFG
m1, feat, fc = T._load_decision_features()
folds = make_sliding_folds(feat, train_years=CFG.sliding_train_years, val_months=CFG.sliding_val_months, test_months=CFG.sliding_test_months,
                           step_months=CFG.sliding_step_months, embargo_bars=CFG.split_embargo_bars)
def run(te, pol):
    env = T.build_env(te, T._slice_m1_for_decision_window(m1, te), fc).unwrapped
    _, tr = B.run_policy(env, pol); return tr
def stats(nm, trs):
    t = pd.concat(trs, ignore_index=True) if trs else pd.DataFrame()
    if t.empty: print(f"{nm}: no trades"); return
    r = t.r_mult; tt = r.mean() / r.std(ddof=1) * np.sqrt(len(r))
    print(f"{nm:<34} n {len(r):5d}  sum {r.sum():+8.1f}R  mean {r.mean():+.3f}R  t {tt:+.2f}  win {np.mean(r>0):.0%} | longs n {(t.direction==1).sum()} {r[t.direction==1].sum():+.1f}R | shorts n {(t.direction==-1).sum()} {r[t.direction==-1].sum():+.1f}R")
print("test windows:", [(te.index.min().date(), te.index.max().date()) for _, _, te in folds])
const = lambda d, s, p: (lambda env: np.array([d, s, p]))
stats("always long (sl 1.5 ATR, tp 2R)", [run(te, const(1, 1, 2)) for _, _, te in folds])
stats("always long (sl 2 ATR, tp 3R)", [run(te, const(1, 2, 3)) for _, _, te in folds])
stats("always short (sl 1.5 ATR, tp 2R)", [run(te, const(2, 1, 2)) for _, _, te in folds])
stats("trend_hold baseline (0.7, 2, 3)", [run(te, lambda env: B.trend_hold_policy(env)) for _, _, te in folds])
sums = []
for sd in range(20):
    rng = np.random.default_rng(sd)
    pol = lambda env: np.array([rng.integers(0, 3), rng.integers(0, 3), rng.integers(0, 4)])
    t = pd.concat([run(te, pol) for _, _, te in folds], ignore_index=True); sums.append(t.r_mult.sum())
print(f"random actions (20 seeds): sum R mean {np.mean(sums):+.1f}, p5 {np.percentile(sums,5):+.1f}, p95 {np.percentile(sums,95):+.1f}")
