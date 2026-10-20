"""Combine: Vault Break size vs Apex's $1,000 daily loss limit (user, 2026-10-19, after VB 8 MNQ hit the limit live).
VB's stop is 75 pts = $150 per MNQ, so 8 MNQ risks $1,200 > the $1,000 daily limit (Apex cuts it at ~-$1,000 and ends the
day); 6 MNQ risks $900 (inside). Same simulator and set as analysis/combine_levers_test.py (VB + ONB ADX30 $1,100 +
Bridge Monday 2 + EOS $500, MNQ; $3,000 target, $2,000 EOD trailing floor locking at $50,100, $1,000 daily loss limit,
21 trading days, every start day 2018-2026). Only VB's size changes: 4-10 MNQ; whole numbers as they trade.
  python3 analysis/combine_vb_size_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import combine_levers_test as CL

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
yr = pd.DatetimeIndex(g.ts[trr]).year
P = {}
for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, CL.ONB30))),
              ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
    w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
one = lambda p, c, n: 1.0
print(__doc__.split("\n")[0])
print(f"\n{'VB size':<10} {'VB risk':>8} {'pass':>6} {'18-22':>6} {'23-26':>6} {'blown':>6} {'time':>5} {'med days':>8} {'changed vs 8':>12}")
base = None; out = {}
for vb in (8, 4, 5, 6, 7, 9, 10):
    q = {"VB": float(vb), "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    W = sum(P[k][0] * q[k] for k in P); R = sum(P[k][1] * q[k] for k in P)
    res = [CL.challenge(W, R, np.arange(s, min(s + CL.MAXD, D)), one) for s in range(D)]
    ok = np.array([x is not None for x in res]) & (yr >= 2018)
    o = np.array([x[0] if x is not None else "" for x in res]); ps = o == "pass"
    days = np.array([x[1] if x is not None else 0 for x in res])
    if base is None: base = o.copy()
    out[vb] = (ps[ok].mean(), ps[ok & (yr < 2023)].mean(), ps[ok & (yr >= 2023)].mean(), (o[ok] == "fail").mean(),
               (o[ok] == "time").mean(), np.median(days[ok & ps]), np.mean(o[ok] != base[ok]))
for vb in (4, 5, 6, 7, 8, 9, 10):
    a = out[vb]
    print(f"{vb:>2} MNQ    ${vb * 150:>6,} {a[0]:6.1%} {a[1]:6.1%} {a[2]:6.1%} {a[3]:6.1%} {a[4]:5.1%} {a[5]:8.0f} {a[6]:12.1%}")
