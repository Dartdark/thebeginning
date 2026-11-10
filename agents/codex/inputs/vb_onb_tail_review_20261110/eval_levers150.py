"""150K evaluation pass-rate levers (user 2026-11-09: 'how do we raise the pass rate' -> 'yes run both', plus 'a strategy with
many trades a week, at least 4-5, would offset a bad VB / ONB day: defense through offense'). PRE-REGISTERED (header committed
before the first run). Base = the current 150K evaluation set: VB 15, ONB ADX30 $2,750, Bridge Monday 5, EOS $1,250, Twin cap1 2,
Dual Thrust 2 (MNQ); corrected engine (floor keeps trailing; $9,000 target, $4,000 floor, $2,000 daily pause, 21 trading days);
every start day 2018-01 -> 2026-09; pass / fail / time-out, 2018-22 and 2023-26 starts, paired difference vs the base with a
60-day block bootstrap 5-95% band.
A. In-evaluation management (the 50K 2026-10-15 levers, $ thresholds x 3 for the 150K, whole set scaled together):
   A1 finish: x0.5 once profit >= $6,000 / A2 daily stop -$1,000 / A3 daily stop -$1,500 / A4 finish + daily stop -$1,500.
   A daily stop ends the day at that loss (the account flattens all charts when the day's open P&L touches it).
B. When to start (start-day splits of the base, not a change in trading; 2 conditions):
   B1 prior-day VIX close above vs at / below its past-252-day median; B2 the base set's P&L over the prior 10 trading days
   negative vs positive. A condition is useful only if the pass-rate gap is >= 3 points with the band excluding 0, with the
   same sign in 2018-22 and 2023-26 starts.
C. High-frequency offense (the user's idea; candidates with >= 4 trades a week, Apex-legal, not benched before): ZT continuation
   5-min EntryZ 1.0 (analysis/zt_volz_test.py: 2,573 trades = ~5.6 a week, $56 per NQ, t 2.47) at 1 and 2 MNQ as an addition,
   and 2 MNQ replacing 5 VB (VB 10). Intraday worst path per day = the day's worst trade excursion (conservative).
Adoption: a lever needs a gain whose band excludes zero and positive in both halves; post-hoc combinations are labelled.
  tools/run_stamped.sh analysis/eval_levers150.py > analysis/outputs/eval_levers150_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from donchian_lwti_test import series
from new_sources_150k import daypaths
import dual_thrust_bench as DTB
import zt_ablation as ZA
import bench150 as BB

START, TARGET, MLL, DLL, MAXD = 150_000.0, 9_000.0, 4_000.0, 2_000.0, 21


def challenge(W, R, s, D, scale_fn=lambda p, c, n: 1.0, dstop=DLL):
    bal = START; floor = START - MLL
    for n, d in enumerate(range(s, min(s + MAXD, D)), 1):
        k = scale_fn(bal - START, bal - floor, n); w, r = W[d] * k, R[d] * k
        lim = max(floor, bal - min(dstop, DLL))
        hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
        win = np.nonzero(bal + r - START >= TARGET)[0]; jp = win[0] if len(win) else len(w)
        if jp < jb: return "pass"
        if jb < len(w):
            if lim == floor: return "fail"
            bal = lim
        else: bal += r[-1]
        floor = max(floor, bal - MLL)
    return "time" if s + MAXD <= D else None


def band(x, nb=2000, L=60, seed=1):
    x = np.asarray(x, float); rng = np.random.default_rng(seed); k = int(np.ceil(len(x) / L)); st = rng.integers(0, len(x), (nb, k))
    m = x[((st[:, :, None] + np.arange(L)) % len(x)).reshape(nb, -1)[:, :len(x)]].mean(axis=1); return np.percentile(m, 5), np.percentile(m, 95)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(); g, trr, D, dts = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"]
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("DT", DTB.dt_trades(g))): w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    Wb = ctx["Wb"] - 5 * P["VB"][0] + 2 * P["DT"][0]; Rb = ctx["Rb"] - 5 * P["VB"][1] + 2 * P["DT"][1]
    S = [s for s in range(D) if dts[s] >= pd.Timestamp("2018-01-02") and dts[s] <= pd.Timestamp("2026-09-01")]; sd = dts[S]; early = sd < "2023-01-01"
    def res(W, R, **kw): return np.array([challenge(W, R, s, D, **kw) for s in S])
    o0 = res(Wb, Rb); p0 = (o0 == "pass").astype(float)
    def show(nm, o):
        p = (o == "pass").astype(float); lo, hi = band(p - p0)
        print(f"   {nm:<44} pass {p.mean():5.1%} fail {(o == 'fail').mean():5.1%} time-out {(o == 'time').mean():4.1%} | 18-22 {p[early].mean():5.1%} 23-26 {p[~early].mean():5.1%}"
              f" | vs base {p.mean() - p0.mean():+5.1%} (band {lo:+.1%} / {hi:+.1%})", flush=True)
    print(f"\n   starts {len(S)} ({sd[0].date()} -> {sd[-1].date()})")
    show("BASE (VB 15, ONB, Bridge Mon, EOS, Twin 2, DT 2)", o0)
    print("\nA. In-evaluation management:")
    for nm, kw in (("A1 finish: x0.5 once profit >= $6,000", dict(scale_fn=lambda p, c, n: 0.5 if p >= 6000 else 1.0)),
                   ("A2 daily stop -$1,000", dict(dstop=1000.0)), ("A3 daily stop -$1,500", dict(dstop=1500.0)),
                   ("A4 finish + daily stop -$1,500", dict(scale_fn=lambda p, c, n: 0.5 if p >= 6000 else 1.0, dstop=1500.0))):
        show(nm, res(Wb, Rb, **kw))
    print("\nB. When to start (base outcomes split by the start day's condition):")
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE.sort_index()
    med = vix.rolling(252, min_periods=120).median()
    hiv = np.array([bool((vix[vix.index < d] > med[med.index < d]).iloc[-1]) if (vix.index < d).any() else False for d in sd])
    cum = pd.Series(Rb[:, -1]).rolling(10).sum().shift(1).fillna(0.0).values; losing = np.array([cum[s] < 0 for s in S])
    rng = np.random.default_rng(3)
    for nm, m in (("B1 VIX above its 1-year median (vs calm)", hiv), ("B2 plan P&L last 10 days < 0 (vs > 0)", losing)):
        a, b = p0[m].mean(), p0[~m].mean(); diffs = []
        idx = np.arange(len(S)); k = int(np.ceil(len(S) / 60))
        for _ in range(2000):
            st = rng.integers(0, len(S), k); ii = ((st[:, None] + np.arange(60)) % len(S)).ravel()[:len(S)]
            mm, pp = m[ii], p0[ii]; diffs.append(pp[mm].mean() - pp[~mm].mean())
        lo, hi = np.percentile(diffs, [5, 95])
        e1, e2 = p0[m & early].mean() - p0[~m & early].mean(), p0[m & ~early].mean() - p0[~m & ~early].mean()
        print(f"   {nm:<44} share {m.mean():4.0%} | pass {a:5.1%} vs {b:5.1%}: gap {a - b:+5.1%} (band {lo:+.1%} / {hi:+.1%}) | 18-22 {e1:+.1%} 23-26 {e2:+.1%}", flush=True)
    print("\nC. High-frequency offense (ZT continuation 5-min, EntryZ 1.0):")
    s5 = series(g, 5); T = ZA.run(g, s5, ZA.zser(s5), entry=1.0); dpos = pd.Series(np.arange(D), index=dts)
    wk = len(T) / ((T.date.max() - T.date.min()).days / 7); print(f"   ZT 5-min: {len(T)} trades, {wk:.1f} a week, ${T.net.mean():.0f} per NQ; active days {T.date.nunique() / len(S):.0%}")
    Wz, Rz = daypaths(D, [(int(dpos[x]) if x in dpos.index else None, a, n_) for x, a, n_ in zip(T.date, T.adv, T.net)])
    for nm, (W, R) in (("C1 + ZT 5-min 1 MNQ", (Wb + Wz, Rb + Rz)), ("C2 + ZT 5-min 2 MNQ", (Wb + 2 * Wz, Rb + 2 * Rz)),
                       ("C3 ZT 5-min 2 MNQ for 5 VB (VB 10)", (Wb + 2 * Wz - 5 * P["VB"][0], Rb + 2 * Rz - 5 * P["VB"][1]))):
        show(nm, res(W, R))
