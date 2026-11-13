"""Finish mode under the Rithmic copier (user 2026-11-09: built-in Rithmic copier, one leader for evaluations and one for funded;
followers copy the leader's orders 1x, so every evaluation in the group trades the SAME size). PRE-REGISTERED (header committed
before the first run). Information for the group rule of finish mode (analysis/eval_levers150.py: per account, half size once the
account is up $6,000: +1.7 points).
Cohort model: 20 evaluations bought one a trading day (cohort start every 10th trading day 2018-01 -> 2026-07); each trades the
current 150K evaluation set (VB 15, ONB $2,750, Bridge Monday 5, EOS $1,250, Twin 2, DT 2) from its own start with its own
balance / trailing floor / 21-day clock (corrected engine). Each day ONE size factor applies to every active account (the
copier), decided by the group rule from the active accounts' profit at the day's start:
  NONE (always full) / OWN (each account its own rule: not possible with a copier; the reference) / ANY (half if any active
  account is up >= $6,000) / MEDIAN (half if the median active account is up >= $6,000) / MEAN (same, mean) / LEADER (half if
  the oldest active account, the copier leader, is up >= $6,000).
Reported: pass rate over all accounts, paired difference vs NONE and vs OWN with a block bootstrap over cohorts (5-95%).
Adoption: the best implementable rule if its gain vs NONE has a band above zero; else no group finish mode.
  tools/run_stamped.sh analysis/copier_finish_bench.py > analysis/outputs/copier_finish_bench_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
import dual_thrust_bench as DTB
import bench150 as BB

START, TARGET, MLL, DLL, MAXD, N, TH = 150_000.0, 9_000.0, 4_000.0, 2_000.0, 21, 20, 6000.0


def cohort(W, R, c0, rule):
    bal = np.full(N, START); floor = bal - MLL; st = np.zeros(N, int); used = np.zeros(N, int)   # 0 waiting, 1 active, 2 pass, 3 fail, 4 time
    for d in range(c0, c0 + N + MAXD + 1):
        if d >= len(W): break
        i = d - c0
        if i < N: st[i] = 1
        act = np.flatnonzero(st == 1)
        if not len(act): continue
        prof = bal[act] - START
        if rule == "NONE": k = np.ones(len(act))
        elif rule == "OWN": k = np.where(prof >= TH, 0.5, 1.0)
        else:
            g = {"ANY": prof.max(), "MEDIAN": np.median(prof), "MEAN": prof.mean(), "LEADER": prof[0]}[rule]
            k = np.full(len(act), 0.5 if g >= TH else 1.0)
        w0, r0 = W[d], R[d]
        for a, kk in zip(act, k):
            w, r = w0 * kk, r0 * kk; lim = max(floor[a], bal[a] - DLL)
            hit = np.nonzero(bal[a] + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
            win = np.nonzero(bal[a] + r - START >= TARGET)[0]; jp = win[0] if len(win) else len(w)
            used[a] += 1
            if jp < jb: st[a] = 2; continue
            if jb < len(w):
                if lim == floor[a]: st[a] = 3; continue
                bal[a] = lim
            else: bal[a] += r[-1]
            floor[a] = max(floor[a], bal[a] - MLL)
            if used[a] >= MAXD: st[a] = 4
    return st


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(base="legacy"); g, trr, D, dts = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"]; P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("DT", DTB.dt_trades(g))): w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    W = ctx["Wb"] - 5 * P["VB"][0] + 2 * P["DT"][0]; R = ctx["Rb"] - 5 * P["VB"][1] + 2 * P["DT"][1]
    c_lo, c_hi = int(np.argmax(dts >= "2018-01-02")), int(np.argmax(dts >= "2026-07-01"))
    C = list(range(c_lo, c_hi, 10)); print(f"   cohorts {len(C)} x {N} evaluations")
    res = {}
    for rule in ("NONE", "OWN", "ANY", "MEDIAN", "MEAN", "LEADER"):
        S = np.array([cohort(W, R, c0, rule) for c0 in C]); res[rule] = S
        print(f"   {rule:<7} pass {(S == 2).mean():5.1%} fail {(S == 3).mean():5.1%} time-out {(S == 4).mean():4.1%}", flush=True)
    def band(x, nb=2000, L=6, seed=1):
        rng = np.random.default_rng(seed); k = int(np.ceil(len(x) / L)); st = rng.integers(0, len(x), (nb, k))
        m = x[((st[:, :, None] + np.arange(L)) % len(x)).reshape(nb, -1)[:, :len(x)]].mean(axis=1); return np.percentile(m, 5), np.percentile(m, 95)
    early = np.array([dts[c] < pd.Timestamp("2023-01-01") for c in C])
    print("\n   paired vs NONE / vs OWN (per cohort pass share; band = 5-95% block bootstrap over cohorts):")
    pn = (res["NONE"] == 2).mean(axis=1); po = (res["OWN"] == 2).mean(axis=1)
    for rule in ("OWN", "ANY", "MEDIAN", "MEAN", "LEADER"):
        p = (res[rule] == 2).mean(axis=1); a = band(p - pn); b = band(p - po)
        print(f"   {rule:<7} vs NONE {np.mean(p - pn):+5.1%} ({a[0]:+.1%} / {a[1]:+.1%}; 18-22 {np.mean((p - pn)[early]):+.1%}, 23+ {np.mean((p - pn)[~early]):+.1%})"
              f" | vs OWN {np.mean(p - po):+5.1%} ({b[0]:+.1%} / {b[1]:+.1%})")
