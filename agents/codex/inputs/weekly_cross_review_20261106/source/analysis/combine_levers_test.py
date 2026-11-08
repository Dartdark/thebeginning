"""Combine pass-rate levers (2026-10-15, user: 'find ways to lift the combine pass rate'). The combine is a first-passage race:
+$3,000 before the $2,000 end-of-day trailing floor (locks at $50,100), $1,000 daily loss limit (pauses the day), 30
calendar days = 21 trading days. Static sizing (72 sets, analysis/pipeline_tuning_test.py) and add-ons
(analysis/combine_addons_test.py) are already exhausted; what is left is state-dependent play. Pre-specified variants
on the current set (VB 8 + ONB ADX30 $1,100 + Bridge Monday 2 + EOS $500, MNQ), every start day 2018-2026 in real day order:
  scale        the whole set x 0.75 / 1.25 / 1.5 (reference: static size)
  protect      x 0.5 while the cushion (balance - floor) is under $1,000
  press        x 1.5 while the cushion is >= $1,500 and profit < $1,500 (only early, while there is room)
  behind       from trading day 11, x 1.5 if profit < $1,000 (running out of time is the other way to fail)
  finish       x 0.5 once profit >= $2,000 (less to give back near the target)  /  finish-fast x 1.5 there
  daily stop   stop the day at -$500 / -$750 (tighter than Apex's $1,000 pause)
  profit lock  stop the day once it is up +$1,000 / +$1,500 (keep a good day)
Sizes are scaled continuously (the MNQ counts round in practice). Reported: pass, 2018-22 / 2023-26 (the selection is
judged on both halves), blown, failed on time, median days to pass; and against the plan, the share of start days whose
outcome changes (paired).
  python3 analysis/combine_levers_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
ONB30 = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx"
START, TARGET, MLL, DLL, LOCK, MAXD = 50_000.0, 3_000.0, 2_000.0, 1_000.0, 100.0, 21


def challenge(W, R, days, scale_fn, dstop=DLL, plock=None):
    bal = START; floor = START - MLL
    for n, d in enumerate(days[:MAXD], 1):
        k = scale_fn(bal - START, bal - floor, n)
        w, r = W[d] * k, R[d] * k
        lim = max(floor, bal - min(dstop, DLL))
        hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
        win = np.nonzero(bal + r - START >= TARGET)[0]; jp = win[0] if len(win) else len(w)
        jl = len(w)
        if plock is not None:
            lk = np.nonzero(r >= plock)[0]; jl = lk[0] if len(lk) else len(w)
        first = min(jb, jp, jl)
        if first == len(w): bal = bal + r[-1]
        elif first == jp: return "pass", n
        elif first == jb:
            if lim == floor: return "fail", n
            bal = lim
        else: bal = bal + r[jl]
        floor = max(floor, min(bal - MLL, START + LOCK))
    return ("time", MAXD) if len(days) >= MAXD else None


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr)
    yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    risk = lambda dollars, m: np.floor(dollars / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": risk(1100, 0.25), "MON_BR": 2.0, "EOS": risk(500, REPORTS["EOS"][1])}
    W = sum(P[k][0] * q[k] for k in P); R = sum(P[k][1] * q[k] for k in P)
    one = lambda p, c, n: 1.0
    V = {"plan (static)": (one, DLL, None),
         "scale x0.75": (lambda p, c, n: 0.75, DLL, None), "scale x1.25": (lambda p, c, n: 1.25, DLL, None), "scale x1.5": (lambda p, c, n: 1.5, DLL, None),
         "protect: x0.5 if cushion < $1,000": (lambda p, c, n: 0.5 if c < 1000 else 1.0, DLL, None),
         "press: x1.5 if cushion >= $1,500 & profit < $1,500": (lambda p, c, n: 1.5 if (c >= 1500 and p < 1500) else 1.0, DLL, None),
         "behind: x1.5 from day 11 if profit < $1,000": (lambda p, c, n: 1.5 if (n >= 11 and p < 1000) else 1.0, DLL, None),
         "finish: x0.5 once profit >= $2,000": (lambda p, c, n: 0.5 if p >= 2000 else 1.0, DLL, None),
         "finish-fast: x1.5 once profit >= $2,000": (lambda p, c, n: 1.5 if p >= 2000 else 1.0, DLL, None),
         "daily stop -$500": (one, 500.0, None), "daily stop -$750": (one, 750.0, None),
         "profit lock +$1,000": (one, DLL, 1000.0), "profit lock +$1,500": (one, DLL, 1500.0)}
    base = None
    print(f"\n{'variant':<52} {'pass':>6} {'18-22':>6} {'23-26':>6} {'blown':>6} {'time':>5} {'med days':>8} {'changed':>8}")
    for nm, (fn, ds, pl) in V.items():
        res = [challenge(W, R, np.arange(s, min(s + MAXD, D)), fn, ds, pl) for s in range(D)]
        ok = np.array([x is not None for x in res]) & (yr >= 2018)
        o = np.array([x[0] if x is not None else "" for x in res])
        ps = (o == "pass"); days = np.array([x[1] if x is not None else 0 for x in res])
        if base is None: base = o.copy()
        ch = np.mean(o[ok] != base[ok])
        print(f"{nm:<52} {ps[ok].mean():6.1%} {ps[ok & (yr < 2023)].mean():6.1%} {ps[ok & (yr >= 2023)].mean():6.1%} "
              f"{(o[ok] == 'fail').mean():6.1%} {(o[ok] == 'time').mean():5.1%} {np.median(days[ok & ps]):8.0f} {ch:8.1%}", flush=True)

    # the two small positives together (post-hoc: judged on both halves only)
    fin = lambda p, c, n: 0.5 if p >= 2000 else 1.0
    res = [challenge(W, R, np.arange(s, min(s + MAXD, D)), fin, 750.0, None) for s in range(D)]
    ok = np.array([x is not None for x in res]) & (yr >= 2018); o = np.array([x[0] if x is not None else "" for x in res]); ps = o == "pass"
    print(f"{'finish x0.5 + daily stop -$750 (post-hoc combo)':<52} {ps[ok].mean():6.1%} {ps[ok & (yr < 2023)].mean():6.1%} {ps[ok & (yr >= 2023)].mean():6.1%} {(o[ok] == 'fail').mean():6.1%}")

    # pipeline: combines on a copier get identical trades, so accounts started on the same day share one outcome.
    # How much does starting k trading days apart decorrelate them? P(both pass), P(both blow) vs independence.
    res0 = [challenge(W, R, np.arange(s, min(s + MAXD, D)), one) for s in range(D)]
    o0 = np.array([x[0] if x is not None else "" for x in res0]); ok0 = np.array([x is not None for x in res0]) & (yr >= 2018)
    p = (o0[ok0] == "pass").mean(); b = (o0[ok0] == "fail").mean()
    print(f"\nTwo combine accounts on the same copier, started k trading days apart (independent would be both pass {p * p:.1%}, both blow {b * b:.1%}):")
    for k in (0, 1, 2, 3, 5, 10, 21):
        i = np.arange(D - k); m = ok0[i] & ok0[i + k]
        a1, a2 = o0[i][m], o0[i + k][m]
        bp, bb = np.mean((a1 == "pass") & (a2 == "pass")), np.mean((a1 == "fail") & (a2 == "fail"))
        at_least_one = np.mean((a1 == "pass") | (a2 == "pass"))
        print(f"   k {k:2d}: both pass {bp:5.1%}, both blow {bb:5.1%}, at least one pass {at_least_one:5.1%}, outcome correlation {np.corrcoef(a1 == 'pass', a2 == 'pass')[0, 1]:+.2f}")
