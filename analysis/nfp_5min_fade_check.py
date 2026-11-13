"""samuel.nys (X, 2026-11-13, user screenshot): 'Jobs report fade: opposite side of the first 5-minute move, exit 09:30 ET' — enter 08:35 ET
(07:35 CT) against the 07:30->07:35 CT move, out 08:30 CT; claims 75 releases, $304 a trade, 57% wins, 1 NQ, costs 2 pts/side + $5.
Our check: his rule exactly, on NFP days found by the same proxy as our live NFP Fade (Friday, day <= 10, 07:31-07:35 range > 3 x its
20-weekday median: the release spike), 2018-2026, per NQ: (a) our costs ($7.25 + 1 tick per side), (b) his costs ($5 + 2 pts per side);
by year / halves; vs our NFP Fade (07:30->07:45 reaction, 07:46 -> 09:00, stop 0.5 ATR); daily correlation; random-side placebo.
  tools/run_stamped.sh analysis/nfp_5min_fade_check.py > analysis/outputs/nfp_5min_fade_check_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
print(__doc__.split("\n")[0])
g = pickle.load(open("scratch_data/g24.pkl", "rb")); ts = pd.DatetimeIndex(g.ts); atr = g.daily_atr(15)
rng_ = g.h[:, jof(731):jof(735) + 1].max(1) - g.l[:, jof(731):jof(735) + 1].min(1)
wk = [r for r in range(g.D) if ts[r].dayofweek < 5 and np.isfinite(rng_[r])]; med = {}
for i, r in enumerate(wk):
    if i >= 20: med[r] = np.median([rng_[q] for q in wk[i - 20:i]])
days = [r for r in med if ts[r] >= pd.Timestamp("2018-01-01") and ts[r].dayofweek == 4 and ts[r].day <= 10 and rng_[r] > 3 * med[r]]


def trade(r, react, t1, stop_atr=None, fade=True, side=None):
    ref, rc = g.c[r, jof(730)], g.c[r, jof(react)]
    if not (np.isfinite(ref) and np.isfinite(rc)) or rc == ref: return None
    s = side if side is not None else (int(-np.sign(rc - ref)) if fade else int(np.sign(rc - ref)))
    j0 = jof(react) + 1; e = g.o[r, j0]
    if not np.isfinite(e): return None
    sp = stop_atr * atr[r] if stop_atr else None
    for j in range(j0, jof(t1) + 1):
        if not np.isfinite(g.h[r, j]): continue
        if sp and ((s > 0 and g.l[r, j] <= e - sp) or (s < 0 and g.h[r, j] >= e + sp)):
            px = (min(g.o[r, j], e - sp) if s > 0 else max(g.o[r, j], e + sp)) if j > j0 else e - s * sp
            return s, e, px, "stop"
    c = g.c[r, jof(t1)]
    return (s, e, c, "time") if np.isfinite(c) else None


def run(react, t1, stop_atr=None, cost="ours", rng=None):
    out = []
    for r in days:
        t = trade(r, react, t1, stop_atr, side=None if rng is None else int(rng.choice([-1, 1])))
        if t is None: continue
        s, e, px, why = t; gross = (px - e) * s * 20
        c = 7.25 + 2 * 5.0 if cost == "ours" else 2 * 5.0 + 2 * 2 * 20   # his: $5 + 2 pts a side
        out.append((ts[r], s, gross, gross - c, why))
    return pd.DataFrame(out, columns=["date", "side", "gross", "net", "why"])


def tt(x): return x.mean() / x.std() * np.sqrt(len(x))
def line(T, nm):
    x = T.net; y = T.date.dt.year; pf = x[x > 0].sum() / -x[x < 0].sum()
    by = " ".join(f"{k % 100:02d}:{x[y == k].sum() / 1000:+.1f}k" for k in sorted(y.unique()))
    return (f"   {nm:<44} n {len(x):3d} avg ${x.mean():5.0f} t {tt(x):4.2f} PF {pf:.2f} win {np.mean(x > 0):.0%} total ${x.sum():,.0f} worst ${x.min():,.0f} "
            f"| 2018-22 ${x[y <= 2022].mean():5.0f} 2023+ ${x[y >= 2023].mean():5.0f}\n        {by}")
H = run(735, 830); print(f"NFP days found (spike proxy): {len(days)} since 2018; traded {len(H)}")
print(line(H, "HIS RULE, our costs")); print(line(run(735, 830, cost="his"), "HIS RULE, his costs (2 pts + $5 a side)"))
H20 = H[H.date >= "2020-07-01"]; print(line(H20, "his rule, our costs, from Jul 2020 (his chart)"))
print(line(run(745, 900, 0.5), "OUR NFP Fade (07:45 reaction, 09:00, stop 0.5 ATR)"))
print(line(run(735, 830, 0.5), "his rule + our 0.5 ATR stop"))
print(line(run(745, 830), "our 07:45 reaction, exit 08:30, no stop"))
print(line(run(735, 900), "his 07:35 reaction, exit 09:00, no stop"))
rng = np.random.default_rng(1); pl = np.array([run(735, 830, rng=rng).net.mean() for _ in range(500)])
print(f"   random-side placebo (500 runs, same days and times): mean ${pl.mean():.0f}, p95 ${np.percentile(pl, 95):.0f} -> his rule p {np.mean(pl >= H.net.mean()):.3f}")
O = run(745, 900, 0.5); j = H.merge(O, on="date", suffixes=("_his", "_ours"))
print(f"   same-day P&L correlation with our NFP Fade: {np.corrcoef(j.net_his, j.net_ours)[0, 1]:+.2f} ({len(j)} days); same side {np.mean(j.side_his == j.side_ours):.0%}")

print("\n== eval book (bench150.LIVE_EVAL, #5) + his rule / our NFP Fade (resize rule: holdout and account-now bands)")
sys.argv = ["x"]; src = open("analysis/eval_size_combo.py").read().split("rows = []")[0].replace("cache=True", "cache=False")
ns = {}; exec(compile(src, "eval_size_combo_head", "exec"), ns)
book, fresh, now, LIVE, DES, HOL, NOWV, trr, D, RM = (ns[k] for k in ("book", "fresh", "now", "LIVE", "DES", "HOL", "NOWV", "trr", "D", "RM"))
from portfolio import paths, load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
rows = []
for r in days:
    t = trade(r, 735, 830)
    if t is None: continue
    s, e, px, why = t; rows.append((r, jof(735) + 1, jof(830), s, e, px, 2))
Tt = with_slippage(pd.DataFrame(rows, columns=["day", "j0", "j1", "side", "entry", "exit", "kind"]))
w, rr = paths(g, Tt); HW, HR = w[trr] / 10, rr[trr] / 10
w, rr = paths(g, with_slippage(load_mc(g, REPORTS["NFP_MC"][0]))); OW, ORr = w[trr] / 10, rr[trr] / 10
atr_t = g.daily_atr(15)[trr]; nfp_mult = lambda risk: np.floor(risk / (np.nan_to_num(REPORTS["NFP_MC"][1] * atr_t, nan=1e12) * 2))[:, None]
def band(d):
    rg = np.random.default_rng(1); n = len(d); nb_ = int(np.ceil(n / 60)); st = rg.integers(0, n, (1000, nb_))
    mm = d[((st[:, :, None] + np.arange(60)) % n).reshape(1000, -1)[:, :n]].mean(1); return np.percentile(mm, 5), np.percentile(mm, 95)
W0, R0 = book(LIVE); f0 = fresh(W0, R0); n0 = now(W0, R0)
print(f"   book: fresh 18-22 {f0[DES].mean():.1%} 23-26 {f0[HOL].mean():.1%} | #5 now {n0[NOWV].mean():.1%}")
for nm, (Wx, Rx) in [(f"+ his rule {k} MNQ", (HW * k, HR * k)) for k in (2, 4, 6)] + [(f"+ our NFP Fade ${k}", (OW * nfp_mult(k), ORr * nfp_mult(k))) for k in (500, 1000, 1500)] + \
                    [("+ his 4 MNQ + our NFP $1000", (HW * 4 + OW * nfp_mult(1000), HR * 4 + ORr * nfp_mult(1000)))]:
    f = fresh(W0 + Wx, R0 + Rx); n = now(W0 + Wx, R0 + Rx); d2 = f[HOL] - f0[HOL]; d3 = n[NOWV] - n0[NOWV]; b2 = band(d2); b3 = band(d3)
    print(f"   {nm:<30} 18-22 {(f[DES] - f0[DES]).mean():+.1%} | 23-26 {d2.mean():+.1%} [{b2[0]:+.1%},{b2[1]:+.1%}] | #5 now {d3.mean():+.1%} [{b3[0]:+.1%},{b3[1]:+.1%}]", flush=True)
