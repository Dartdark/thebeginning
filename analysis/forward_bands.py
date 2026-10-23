"""Frozen forward-log bands (2026-10-23, before any forward observation; after Codex's fc2b_bench_forward_review.md).
For each forward-logged rule: the backtest ledger (per full contract, after the repo's costs), and at each checkpoint n the
10th / 90th percentile of the MEAN of n trades drawn with replacement from that ledger (a predictive band for future
results under 'the backtest is the truth'; 20,000 draws, seed 20261023, iid trades). Also the joint false-rejection
rate of the two-checkpoint rule when the backtest is the truth (sequential simulation), so the stopping rule's error is known.
Decision rule (exhaustive), applied at checkpoint 1 then 2:
  REJECT   mean < p10, or (checkpoint 1) mean <= 0 with t <= -1;
  CONTINUE p10 <= mean <= p90 (checkpoint 1 -> go on to checkpoint 2; checkpoint 2 -> 'passed': eligible for the user's decision);
  CHECK    mean > p90: continue as above AND audit data / fills before believing it.
  python3 analysis/forward_bands.py
"""
import numpy as np, pandas as pd

LEDGERS = {"FC 2B v2 (MC v2 report)": ("checks/candidates/fc_2b/trades.csv", None, (40, 80)),
           "S47 v2": ("checks/candidates/s47_v2/python_trades_v2.csv", None, (40, 80)),
           "Kusho v9 (21:00)": ("checks/candidates/kusho/python_trades_v9.csv", None, (100, 200)),
           "Kusho v9 flat 15:45": ("checks/candidates/kusho/python_trades_v9_RTH.csv", None, (100, 200)),
           "S30 NQ": ("checks/candidates/s30_ibs/python_trades_NQ.csv", None, (20, 40)),
           "S30 ES": ("checks/candidates/s30_ibs/python_trades_ES.csv", None, (20, 40))}

if __name__ == "__main__":
    print(__doc__.split("\n")[0]); rng = np.random.default_rng(20261023)
    for nm, (path, _, (n1, n2)) in LEDGERS.items():
        x = pd.read_csv(path).net.to_numpy(float)
        m1 = rng.choice(x, (20000, n1)).mean(1); m2 = rng.choice(x, (20000, n2)).mean(1)
        b1 = np.percentile(m1, [10, 90]); b2 = np.percentile(m2, [10, 90])
        # joint false rejection: draw n2 trades, check checkpoint 1 on the first n1, checkpoint 2 on all
        d = rng.choice(x, (20000, n2)); a = d[:, :n1]; ma = a.mean(1); ta = ma / (a.std(1, ddof=1) / np.sqrt(n1))
        rej1 = (ma < b1[0]) | ((ma <= 0) & (ta <= -1)); rej2 = ~rej1 & (d.mean(1) < b2[0])
        print(f"   {nm:<24} backtest {len(x)} trades, mean ${x.mean():,.0f} | checkpoint {n1}: p10 ${b1[0]:,.0f} / p90 ${b1[1]:,.0f} | "
              f"checkpoint {n2}: p10 ${b2[0]:,.0f} / p90 ${b2[1]:,.0f} | false rejection if the backtest is true: "
              f"{rej1.mean():.1%} at {n1}, {(rej1 | rej2).mean():.1%} by {n2}")
