"""Lahanis, Liu & Zhou, 'Online Quantitative Trading Strategies' (NYU Stern Glucksman Fellowship; user upload 2026-11-12;
papers/lahanis_liu_zhou_online_portfolio.pdf): online portfolio selection (Li & Hoi 2013 survey) on NASDAQ-100 stocks 1998-2010, no costs.
PRE-REGISTERED: the paper's two headline mean-reversion rules + the classic benchmark, on our 9 futures (daily 08:31-09:30 CT VWAP,
ratio roll-adjusted, panel from analysis/ml_futures_xs_test.py), 2018-2026, long-only simplex weights as in the paper:
  CRP  equal weight, rebalanced daily (benchmark)
  PAMR Li et al. 2012, PAMR-0, the paper's eps 0.9 (also the literature default eps 0.5)
  OLMAR Li & Hoi 2012, the paper's window 2 / eps 0.8 (also the literature default window 5 / eps 10)
Costs: daily turnover x each market's round-trip cost / 2 (our standard: commission + 1 tick a side, as bp of notional).
Report: annualised return, Sharpe, max DD, gross and net, 2018-22 vs 2023+, and vs CRP. Not Apex-legal (overnight): personal only.
  tools/run_stamped.sh analysis/ops_futures_test.py > analysis/outputs/ops_futures_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
print(__doc__.split("\n")[0])
VE, VR = pickle.load(open("scratch_data/ml_fut_vwap_ratio.pkl", "rb")); VE = pd.DataFrame(VE)
VE = VE[(VE.index.dayofweek < 5) & (VE.index >= "2017-12-01")]; VE = VE[VE.notna().sum(1) >= 7].ffill()
X = (VE / VE.shift(1)).iloc[1:]; X = X.where((X - 1).abs() <= 0.25, 1.0).fillna(1.0); X = X[X.index >= "2018-01-01"]
SPEC = {"6E": (125000, 0.00005), "BTC": (5, 5), "CL": (1000, 0.01), "ES": (50, 0.25), "GC": (100, 0.1), "NG": (10000, 0.001),
        "NQ": (20, 0.25), "YM": (5, 1), "ZN": (1000, 1 / 64)}
C = pd.DataFrame({s: (7.25 if s == "NQ" else 5.0) + 2 * SPEC[s][0] * SPEC[s][1] for s in X.columns}, index=X.index) / (VE.loc[X.index] * pd.Series({s: SPEC[s][0] for s in X.columns}))
X = X.values; C = C.values / 2; n, m = X.shape


def simplex(v):
    u = np.sort(v)[::-1]; css = np.cumsum(u); r = np.nonzero(u * np.arange(1, len(v) + 1) > (css - 1))[0][-1]
    return np.maximum(v - (css[r] - 1) / (r + 1), 0)


def run(kind, **p):
    b = np.ones(m) / m; R = np.zeros(n); T = np.zeros(n); hist = []
    for t in range(n):
        x = X[t]; R[t] = b @ x - 1; bnext_raw = b * x / (b @ x)        # drifted weights after the day
        hist.append(x)
        if kind == "CRP": nb = np.ones(m) / m
        elif kind == "PAMR":
            loss = max(0.0, b @ x - p["eps"]); d = x - x.mean(); den = d @ d
            nb = simplex(b - (loss / den if den > 0 else 0) * d)
        elif kind == "OLMAR":
            w = p["w"]; H = np.array(hist[-w:]); P = np.cumprod(H[::-1], axis=0)       # price ratios back from today
            xp = (1.0 / P).mean(axis=0) * 1.0 if len(H) >= 1 else x                    # MA(w) / p_t
            xb = xp.mean(); d = xp - xb; den = d @ d; lam = max(0.0, (p["eps"] - b @ xp) / den) if den > 0 else 0
            nb = simplex(b + lam * d)
        T[t] = np.abs(nb - bnext_raw) @ C[min(t + 1, n - 1)] if t + 1 < n else 0     # cost of rebalancing into tomorrow
        b = nb
    return pd.Series(R, index=pd.DatetimeIndex(VE.index[-n:])), pd.Series(T, index=pd.DatetimeIndex(VE.index[-n:]))


def st(r):
    eq = (1 + r).cumprod(); dd = (eq / eq.cummax() - 1).min()
    return f"ann {((eq.iloc[-1]) ** (252 / len(r)) - 1):+6.1%} Sharpe {r.mean() / r.std() * np.sqrt(252):5.2f} maxDD {dd:6.1%}"


print(f"   {n} days {VE.index[-n].date()}..{VE.index[-1].date()}, {m} futures")
base = None
for nm, kind, p in (("CRP (equal weight)", "CRP", {}), ("PAMR eps 0.9 (paper)", "PAMR", {"eps": 0.9}), ("PAMR eps 0.5 (default)", "PAMR", {"eps": 0.5}),
                    ("OLMAR w2 eps 0.8 (paper)", "OLMAR", {"w": 2, "eps": 0.8}), ("OLMAR w5 eps 10 (default)", "OLMAR", {"w": 5, "eps": 10})):
    g, c = run(kind, **p); net = g - c; y = net.index.year
    if base is None: base = net
    print(f"   {nm:<27} gross {st(g)} | net {st(net)} | cost {c.mean() * 1e4:5.1f} bp/day | 18-22 net Sharpe {net[y <= 2022].mean() / net[y <= 2022].std() * 15.87:5.2f}, "
          f"23+ {net[y >= 2023].mean() / net[y >= 2023].std() * 15.87:5.2f} | minus CRP: {(net - base).mean() * 1e4:+5.1f} bp/day t {(net - base).mean() / (net - base).std() * np.sqrt(len(net)):4.1f}")
