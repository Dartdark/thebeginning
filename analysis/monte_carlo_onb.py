"""Monte Carlo analysis of Overnight Bias (MultiCharts trade list).

  1. Edge: bootstrap of the trades -> 95% range of the average trade and the
     profit factor, and the chance the true average is <= 0.
  2. A year of trading at $RISK a trade (sized in whole MNQ by the stop):
     trades resampled in random order -> year P&L, max drawdown, losing streaks.
  3. Apex 50K challenge, the notebook's method: whole real days drawn at random
     (with replacement), checked minute by minute -> pass rate with a 95%
     range, failure reasons, days to pass; and the same trades with no edge.
  4. Stress: extra slippage per trade and a share of winners turned into
     average losers -> average trade and Apex pass rate.

Usage (from the repo root): python3 analysis/monte_carlo_onb.py   (about 2 minutes)
"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "analysis")
from grid24 import Grid24
from portfolio import load_mc, paths, challenge, summarize
from prop_sim import ci
from multi_strategy import zero_edge
from multi_strategy24 import risk_sized, ONB_REPORT

RISK = 1100
N_BOOT = 10_000
N_CHAL = 10_000
SEED = 7


def random_day_challenges(g, t, n, rng):
    w, r = paths(g, t)
    w, r = w[g.trading], r[g.trading]
    res = [challenge(w, r, rng.integers(0, len(w), 21)) for _ in range(n)]
    return summarize(res), res


def pct(x):
    return f"{x:.0%}"


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    g = Grid24()
    t1 = load_mc(g, ONB_REPORT)                      # per NQ
    print(f"Overnight Bias, {ONB_REPORT}: {len(t1)} trades, "
          f"{t1.date.min():%Y-%m-%d} to {t1.date.max():%Y-%m-%d}")

    # ---------- 1. edge ----------
    x = t1["net"].to_numpy()
    idx = rng.integers(0, len(x), (N_BOOT, len(x)))
    s = x[idx]
    means = s.mean(1)
    pf = np.where(s > 0, s, 0).sum(1) / -np.where(s < 0, s, 0).sum(1)
    print("\n1. Edge (per NQ, after costs; 10,000 resamples of the 997 trades)")
    print(f"   average trade ${x.mean():.0f}  95% range ${np.percentile(means, 2.5):.0f} to ${np.percentile(means, 97.5):.0f}")
    print(f"   profit factor {np.where(x > 0, x, 0).sum() / -np.where(x < 0, x, 0).sum():.2f}  95% range "
          f"{np.percentile(pf, 2.5):.2f} to {np.percentile(pf, 97.5):.2f}")
    print(f"   chance the true average trade is <= $0: {(means <= 0).mean():.2%}")
    half = t1.date.dt.year < 2023
    for lab, m in (("2018-22", half), ("2023-26", ~half)):
        xx = x[m.to_numpy()]
        mm = xx[rng.integers(0, len(xx), (N_BOOT, len(xx)))].mean(1)
        print(f"   {lab}: average ${xx.mean():.0f}, 95% range ${np.percentile(mm, 2.5):.0f} to ${np.percentile(mm, 97.5):.0f}")

    # ---------- 2. a year at $RISK a trade ----------
    tr = risk_sized(g, t1, RISK)
    y = tr["net"].to_numpy()                          # $ per trade at the risk size
    per_year = int(round(len(tr) / (len(g.trading) / 252)))
    seq = y[rng.integers(0, len(y), (N_BOOT, per_year))]
    eq = seq.cumsum(1)
    dd = (np.maximum.accumulate(np.c_[np.zeros(N_BOOT), eq], 1)[:, 1:] - eq).max(1)
    def longest(row):
        best = cur = 0
        for v in row:
            cur = cur + 1 if v < 0 else 0
            best = max(best, cur)
        return best
    streak = np.array([longest(r) for r in seq])
    print(f"\n2. One year of trading at ${RISK:,} risk a trade (about {per_year} trades; "
          f"{tr.qty.mul(10).median():.0f} MNQ typical size)")
    print(f"   average trade ${y.mean():.0f}; largest loss ${y.min():,.0f}")
    q = lambda a, p: np.percentile(a, p)
    print(f"   year P&L: median ${q(eq[:, -1], 50):,.0f}; 1 in 10 years below ${q(eq[:, -1], 10):,.0f}; "
          f"losing year {(eq[:, -1] < 0).mean():.0%}")
    print(f"   max drawdown in the year: median ${q(dd, 50):,.0f}; 1 in 10 above ${q(dd, 90):,.0f}; "
          f"1 in 100 above ${q(dd, 99):,.0f}")
    print(f"   longest losing streak: median {q(streak, 50):.0f}; 1 in 10 years {q(streak, 90):.0f}+; "
          f"1 in 100 {q(streak, 99):.0f}+")
    print(f"   chance a drawdown reaches $2,000 within the year: {(dd >= 2000).mean():.0%}")

    # ---------- 3. Apex challenges on random days ----------
    print("\n3. Apex 50K challenges, 10,000 each, whole real days drawn at random")
    print(f"   {'risk a trade':>12} {'pass':>6} {'95% range':>13} {'drawdown fail':>14} {'out of time':>12} "
          f"{'median days':>12} {'no edge':>8}")
    for risk in (700, 900, 1100, 1300, 1500):
        t = risk_sized(g, t1, risk)
        r, res = random_day_challenges(g, t, N_CHAL, rng)
        z, _ = random_day_challenges(g, zero_edge(t), N_CHAL, rng)
        lo, hi = ci(r["p"], r["n"])
        print(f"   ${risk:>11,} {pct(r['p']):>6} {pct(lo) + '-' + pct(hi):>13} {pct(r['mll']):>14} "
              f"{pct(r['time']):>12} {r['med_days']:>12.0f} {pct(z['p']):>8}")
        if risk == RISK:
            days = pd.Series([d for o, d in res if o == "pass"])
    print(f"   at ${RISK:,}: passes by day 5 {(days <= 5).sum() / N_CHAL:.0%}, by day 10 "
          f"{(days <= 10).sum() / N_CHAL:.0%}, by day 21 {len(days) / N_CHAL:.0%}")

    # ---------- 4. stress ----------
    print(f"\n4. Stress at ${RISK:,} a trade (Apex random-day pass rate, 5,000 challenges each)")
    base = risk_sized(g, t1, RISK)
    loss_pts = -base.loc[base.pnl < 0, "pnl"].mean() / 20.0     # average loss, points per NQ
    print(f"   {'extra slippage':>15} {'winners lost':>13} {'avg trade per NQ':>17} {'pass':>6}")
    for slip_pts, flip in ((0, 0), (1, 0), (2, 0), (4, 0), (0, 0.05), (0, 0.10), (2, 0.05), (2, 0.10)):
        t = base.copy()
        t["exit"] = t["exit"] - t["side"] * slip_pts
        if flip:
            win = np.nonzero((t.pnl > 0).to_numpy())[0]
            pick = rng.choice(win, int(round(flip * len(win))), replace=False)
            t.loc[pick, "exit"] = t.loc[pick, "entry"] - t.loc[pick, "side"] * loss_pts
        t["pnl"] = (t["exit"] - t["entry"]) * t["side"] * 20.0
        r, _ = random_day_challenges(g, t, 5000, rng)
        print(f"   {f'{slip_pts} pts (${slip_pts * 20})':>15} {pct(flip):>13} {f'${(t.pnl - 7.25).mean():.0f}':>17} {pct(r['p']):>6}")
