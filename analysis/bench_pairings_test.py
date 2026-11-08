"""Bench strategies as filters for live ones (user 2026-11-08). PRE-REGISTERED (header committed before the first run; 6 trials).
  1 VB trades kept only when a noise-area 15-min LONG (bridge_noise_15m, RTH) entered earlier the same day
  2 ONB ADX30 LONGS kept only after a green RTH day (prior session 08:30 open -> 15:00 close up); shorts unchanged, not counted
  3 VB LONGS skipped when a 60-min double top (chart_patterns_test definition) fired earlier the same day within 4 hours
  4 Late-Day Flow SHORT days kept only when Vol-Control Sell Flow also trades (sells) that day (lab daily P&L)
  5 Overnight Tick nights kept only when the prior 2 RTH sessions' 1-min closes vs time have R^2 >= 0.3 (Nocturne's rule;
    substitute for RollZone / Overnight Rebound, whose trade files are not in the repo)
  6 Twin cap1 Morning Momentum trades kept only when the opening drive agrees (08:30 open -> close of the entry minute in the trade's direction)
Score per filter: kept vs skipped $ a trade (per NQ, repo costs), Welch t of kept - skipped, 2018-22 (design) and 2023+ separately,
share of trades kept. Adoption needs t >= metrics.t_threshold(N items) and the same sign in both periods, then a plan bench.
  tools/run_stamped.sh analysis/bench_pairings_test.py > analysis/outputs/bench_pairings_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
from combine_levers_test import ONB30
from grid24 import jof
from candlestick_patterns_test import rth_bars
from chart_patterns_test import pivots_signals
import twin_continuation_test as tc


def score(nm, net, keep, dates):
    net = np.asarray(net, float); keep = np.asarray(keep, bool); d = pd.DatetimeIndex(dates); ok = d >= "2018-01-01"
    def part(m):
        a, b = net[m & keep], net[m & ~keep]
        if len(a) < 5 or len(b) < 5: return "n/a"
        t = (a.mean() - b.mean()) / np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        return f"kept ${a.mean():6.0f} (n {len(a):4d}) vs skipped ${b.mean():6.0f} (n {len(b):4d}), t {t:5.2f}"
    a, b = net[ok & keep], net[ok & ~keep]; t = (a.mean() - b.mean()) / np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    print(f"\n{nm}\n   2018-26: {part(ok)} | kept {np.mean(keep[ok]):.0%}\n   2018-22: {part(ok & (d.year < 2023))}\n   2023+  : {part(ok & (d.year >= 2023))}", flush=True)
    return t


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); T = list(g.trading); J0, J1 = jof(831), jof(1500)
    netf = lambda t: (with_slippage(t).eval("(exit - entry) * side") * 20 - 7.25).to_numpy()
    dts = lambda t: pd.DatetimeIndex(g.ts[t.day.to_numpy()])
    res = {}
    vb = load_mc(g, REPORTS["VB"][0]).reset_index(drop=True)
    nz = pd.read_csv("analysis/outputs/bridge_noise_15m_trades_rth.csv"); nz = nz[nz.side > 0]
    first = nz.groupby("row").j0.min()
    k1 = np.array([(r in first.index) and first[r] < j for r, j in zip(vb.day, vb.j0)])
    res["1 VB only after a noise-area long"] = score("1 VB only after a noise-area long entered earlier that day", netf(vb), k1, dts(vb))
    onb = load_mc(g, ONB30).reset_index(drop=True); onb = onb[onb.side > 0].reset_index(drop=True)
    op, cl = g.o[:, J0], g.c[:, J1]; pos = {r: i for i, r in enumerate(T)}
    def prev_green(r):
        i = pos.get(r, None)
        if i is None or i == 0: return False
        p = T[i - 1]; return bool(cl[p] > op[p])
    k2 = np.array([prev_green(r) for r in onb.day])
    res["2 ONB longs only after a green day"] = score("2 ONB ADX30 longs only after a green RTH day", netf(onb), k2, dts(onb))
    B = rth_bars(g, 60); S = pivots_signals(B); dt_ = B[S["DTOP"][0]][["row", "j"]]
    vbl = vb[vb.side > 0].reset_index(drop=True)
    k3 = np.array([not ((dt_.row == r) & (dt_.j < j) & (dt_.j >= j - 240)).any() for r, j in zip(vbl.day, vbl.j0)])
    res["3 VB longs skip after a 60-min double top"] = score("3 VB longs skipped after a 60-min double top (same day, 4 h)", netf(vbl), k3, dts(vbl))
    lab = pickle.load(open("scratch_data/lab.pkl", "rb")); ld = pd.DatetimeIndex(lab.g.ts[lab.tr])
    ls, vcs = lab.C["LDF_MC_S"] * 10, lab.C["VCS_MC"] * 10; m = ls != 0
    res["4 LDF shorts only with VCS"] = score("4 Late-Day Flow short days kept only when Vol-Control Sell trades", ls[m], (vcs != 0)[m], ld[m])
    ot = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date", "sess"]); _td = set(pd.read_csv("checks/candidates/overnight_tick/trades.csv").date)
    ot = ot[ot.date.dt.strftime("%Y-%m-%d").isin(_td)].reset_index(drop=True)   # trade nights only
    def r2(sess):
        i = np.searchsorted(g.dates, int(sess.strftime("%Y%m%d"))); idx = [x for x in T if x <= i][-2:]
        y = np.concatenate([g.c[x, J0:J1 + 1] for x in idx]); y = y[~np.isnan(y)]
        if len(y) < 100: return np.nan
        xx = np.arange(len(y)); return np.corrcoef(xx, y)[0, 1] ** 2
    rr = np.array([r2(s) for s in ot.sess])
    res["5 Overnight Tick only when R2 >= 0.3"] = score("5 Overnight Tick nights only when the last 2 sessions' R^2 >= 0.3", ot.net.to_numpy(), rr >= 0.3, ot.date)
    Bf = tc.flatten(g); TT = tc.simulate(Bf, max_stop_mult=1.0, v21=True); mo = TT[TT.setup == "MO"].reset_index(drop=True)
    rows, js = Bf["row"][mo.i0.to_numpy()], Bf["j"][mo.i0.to_numpy()]
    k6 = np.array([(g.c[r, j - 1] - g.o[r, J0]) * s > 0 if j - 1 >= J0 and np.isfinite(g.o[r, J0]) else False for r, j, s in zip(rows, js, mo.side)])
    res["6 Twin MO only when the opening drive agrees"] = score("6 Twin cap1 Morning Momentum only when the 08:30 -> entry move agrees", mo.net.to_numpy(), k6, mo.date)
    nt = len([1 for l_ in open("TIER_LIST.md") if l_.startswith("| ") and "---" not in l_]) + 6
    print(f"\nt needed (N = {nt}): {M.t_threshold(nt):.2f}; filters with t >= 2: {sum(v >= 2 for v in res.values())} of 6")
