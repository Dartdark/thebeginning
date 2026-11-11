"""5-minute jump follow: pre-registered variants (checks/candidates/jump5/PREREG.md), design + ONE holdout look, by year, longs /
shorts, placebo, the screenshot's window (2019-2026) with and without costs, MultiCharts bar-fill check, resampling, Monte Carlo.
  tools/run_stamped.sh analysis/jump_final.py > analysis/outputs/jump_final_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import jump_lib as L, jump_study as S, metrics as MT, resampling as RS, montecarlo as MC

b = L.bars(); M = S.Mkt(); yr = b.ts.dt.year.to_numpy()
sgn = np.sign(b.r).fillna(0).to_numpy(); rth = ((b.hhmm > 830) & (b.hhmm <= 1500)).to_numpy()
aJ = b.J.abs().to_numpy(); sj = b.s.to_numpy(); ALL = yr >= 2018
VAR = {"P1 J>3 RTH tgt 1R, 30 min": dict(mask=(aJ > 3) & rth, tp=1.0, hold=30),
       "P2 J>3 RTH no tgt, 30 min": dict(mask=(aJ > 3) & rth, tp=99, hold=30),
       "P3 J>3 RTH tgt 0.3R, 240 min": dict(mask=(aJ > 3) & rth, tp=0.3, hold=240),
       "P4 s>6 overnight no tgt, 30 min": dict(mask=(sj > 6) & ~rth, tp=99, hold=30)}
days = pd.DatetimeIndex(sorted(set(M.sess[(M.ts >= np.datetime64("2018-01-01"))])))


def run(v, cost=True, side=sgn, mask=None):
    return S.trades(b, M, ALL & (v["mask"] if mask is None else mask), side, "rng", 1.0, tp=v["tp"], hold=v["hold"], cost=cost)


def daily(t, d=days):
    return t.groupby(pd.DatetimeIndex(t.sess)).net.sum().reindex(d, fill_value=0.0)


def line(t, lab):
    if len(t) < 3: return f"   {lab:<28} n {len(t)}"
    x = t.net; pf = x[x > 0].sum() / -x[x < 0].sum(); tt = x.mean() / x.std() * np.sqrt(len(x))
    return f"   {lab:<28} n {len(t):5d} win {np.mean(x > 0):5.1%} net ${x.mean():7.1f} total ${x.sum():9,.0f} PF {pf:4.2f} t {tt:5.2f}"


print("== Screenshot arithmetic (pino1, NQ 5-min, 7y10m): 855 trades, 82.22% wins -> 703 wins avg $337, 152 losses avg $1,102;")
print("   win/loss size 0.306 (= the 0.3R target, so NO costs in his report); breakeven win rate at 0.3R = 76.9%; edge = +5.3 points")
print("   of win rate = +0.069R = $81 a trade; z vs breakeven 3.7 IF nothing was tuned. 0.42% of time in market = ~20 min a trade.")
print("   Max drawdown $9,963 = 2.5x the Apex 150K trailing limit ($4,000) at this size.\n")

T = {}
for nm, v in VAR.items():
    t = run(v); T[nm] = t; y = pd.DatetimeIndex(t.ts).year
    print(f"== {nm}")
    print(line(t[y <= 2022], "design 2018-22")); print(line(t[y >= 2023], "HOLDOUT 2023-26")); print(line(t, "all 2018-26"))
    print(line(t[t.side > 0], "longs all")); print(line(t[t.side < 0], "shorts all"))
    print(line(t[(t.side > 0) & (y >= 2023)], "longs holdout")); print(line(t[(t.side < 0) & (y >= 2023)], "shorts holdout"))
    print("   by year: " + "  ".join(f"{k} ${g.net.sum():,.0f} ({len(g)})" for k, g in t.groupby(y)))
    d = daily(t)
    for lab, dd, tt in (("all", d, t), ("2023+", d[d.index.year >= 2023], t[y >= 2023]), ("longs", daily(t[t.side > 0]), t[t.side > 0]), ("shorts", daily(t[t.side < 0]), t[t.side < 0])):
        p = MT.perf(dd, tt.net, capital=150_000)
        print(f"   metrics {lab:<6} Sharpe {p['sharpe']:.2f} Sortino {p['sortino']:.2f} PF {p['profit_factor']:.2f} Calmar {p['calmar']:.2f} Ulcer {p['ulcer']:.2f} maxDD ${p['max_dd']:,.0f} annual ${p['annual']:,.0f}")
    print()

print("== Screenshot window 2019-01 .. 2026-11, P3 shape (0.3R target): with our costs / without costs (his report has none)")
for lab, c in (("our costs", True), ("no costs", False)):
    t = run(VAR["P3 J>3 RTH tgt 0.3R, 240 min"], cost=c); t = t[pd.DatetimeIndex(t.ts).year >= 2019]; print(line(t, lab))
for lab, m in (("J>3 24h no costs", aJ > 3), ("J>4 24h no costs", aJ > 4), ("J>4 RTH no costs", (aJ > 4) & rth), ("J>5 24h no costs", aJ > 5), ("FADE J>3 RTH no costs", None)):
    if m is None: t = run(VAR["P3 J>3 RTH tgt 0.3R, 240 min"], cost=False, side=-sgn)
    else: t = run(dict(tp=0.3, hold=240), cost=False, mask=m)
    t = t[pd.DatetimeIndex(t.ts).year >= 2019]; print(line(t, lab))

print("\n== MultiCharts 5-minute bar fills without Bar Magnifier vs 1-minute truth (P3 shape, no costs, 2019-2026)")
o5, h5, l5, c5 = (b[k].to_numpy() for k in "ohlc"); R5 = b.rng.to_numpy(); rows = []; busy = -1
for q in np.flatnonzero(ALL & (aJ > 3) & rth & (yr >= 2019)):
    e = q + 1
    if e <= busy or e >= len(b) - 60 or R5[q] < 2: continue
    s = int(sgn[q]); px = o5[e]; st = px - s * R5[q]; tg = px + s * 0.3 * R5[q]; res = None
    for i in range(e, e + 48):
        if b.hhmm.iat[i] > 1555 and b.hhmm.iat[i] <= 1700: res = s * (c5[i] - px); break
        hit_t = (h5[i] >= tg) if s > 0 else (l5[i] <= tg); hit_s = (l5[i] <= st) if s > 0 else (h5[i] >= st)
        if hit_t and hit_s:                      # MultiCharts: the extreme nearer the open is assumed to come first
            up_first = (h5[i] - o5[i]) < (o5[i] - l5[i]); t_first = up_first if s > 0 else not up_first
            res = 0.3 * R5[q] if t_first else -R5[q]; break
        if hit_t: res = 0.3 * R5[q]; break
        if hit_s: res = -R5[q]; break
    if res is None: res = s * (c5[i] - px)
    rows.append(res * 20); busy = i
x = np.array(rows); print(f"   5-min bar fills: n {len(x)} win {np.mean(x > 0):.1%} net ${x.mean():.1f} PF {x[x > 0].sum() / -x[x < 0].sum():.2f}   (1-minute truth: the 'no costs' line above)")

print("\n== Placebo (all 2018-26): random 5-min bar of the same window on the same sessions, direction = that bar's move, same exits; 200 runs")
rng = np.random.default_rng(1)
for nm in ("P1 J>3 RTH tgt 1R, 30 min", "P2 J>3 RTH no tgt, 30 min", "P4 s>6 overnight no tgt, 30 min"):
    v = VAR[nm]; real = T[nm]; win = rth if "RTH" in nm else ~rth
    cand = np.flatnonzero(ALL & win & (sgn != 0)); ev = np.flatnonzero(ALL & v["mask"]); sess = b.sess.to_numpy()
    by = pd.Series(cand).groupby(sess[cand]).apply(lambda s: s.to_numpy()); means = []
    for _ in range(200):
        pick = np.zeros(len(b), bool)
        for sday, k in zip(*np.unique(sess[ev], return_counts=True)):
            c = by.get(sday)
            if c is not None: pick[rng.choice(c, min(k, len(c)), replace=False)] = True
        means.append(run(v, mask=pick).net.mean())
    means = np.array(means)
    print(f"   {nm:<34} real ${real.net.mean():.1f} | placebo mean ${means.mean():.1f}, p95 ${np.percentile(means, 95):.1f}, p(placebo >= real) {np.mean(means >= real.net.mean()):.3f}")

print("\n== Bootstrap + drawdown permutation on the 2023+ holdout (1 NQ, capital 150K)")
H = {nm: daily(t)[lambda d: d.index.year >= 2023] for nm, t in T.items()}
B, P = RS.report(H, n=3000, capital=150_000, limits=(2000, 4000, 6000)); print(B); print(P)
print("\n== Monte Carlo at trading size (1 NQ and 2 MNQ = x0.2; Apex 150K trailing $4,000)")
for nm, t in T.items():
    for size in (1.0, 0.2): print(MC.report(t.net, daily(t), size=size, label=nm, trail=4000.0))
N = len(MT.__dict__) and __import__("trials").parse_tier_list() if hasattr(__import__("trials"), "parse_tier_list") else None
try: n_items = len(N)
except Exception: n_items = 400
print(f"\n== Multiple-testing bar: t_threshold({n_items} ranked items) = {MT.t_threshold(n_items):.2f}; about 250 design configurations were also looked at here.")
for nm, t in T.items(): t.assign(date=pd.DatetimeIndex(t.sess).strftime("%Y-%m-%d"))[["date", "ts", "side", "R", "entry", "exit", "why", "gross", "net"]].to_csv(f"checks/candidates/jump5/trades_{nm[:2]}.csv", index=False)
