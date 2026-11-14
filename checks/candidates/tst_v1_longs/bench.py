"""Checker: benchmarks, neighbours, leaks for tst_v1_longs. Run from repo root."""
import sys, os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import replica as R
from scipy import stats
rng = np.random.default_rng(7)
m = R.load_1m(); b = R.bars4h(m); S = R.Sim(m, b)
sig, atr = S.signal(); T = S.run(sig, atr)
mc = S.mc; ct_end = m.ct_end.values
def tt(x): x = np.asarray(x); return x.mean() / x.std(ddof=1) * np.sqrt(len(x))
def summ(x, lab):
    x = pd.Series(x); print(f"{lab:38s} n {len(x):4d} mean {x.mean()*100:+.2f}% t {tt(x):+.2f} win {np.mean(x>0):.0%} sum {x.sum()*100:+.0f}%")
P = lambda s: print(s)
P("== base replica"); summ(T.net, "replica longs")
mk = pd.read_csv(os.path.join(HERE, "trades.csv")); summ(mk.net, "maker trades.csv")
T["bars"] = T.bx - T.j; T["days"] = (T.xi.map(lambda i: m.index[i]) - (T.t + pd.Timedelta("4h"))).dt.total_seconds() / 86400
P(f"hold days mean {T.days.mean():.1f} median {T.days.median():.1f}; in-market share of time {T.days.sum() / ((b.index[-1]-pd.Timestamp('2018-06-01')).days):.1%}; half-target hit {T.half.mean():.0%}")
P("by year:")
for y, g in T.groupby(T.t.dt.year): P(f"  {y}: n {len(g):3d} mean {g.net.mean()*100:+.2f}% sum {g.net.sum()*100:+.1f}%  t {tt(g.net) if len(g)>2 else np.nan:+.2f}")
for lab, g in (("2018-22", T[T.t.dt.year <= 2022]), ("2023+", T[T.t.dt.year >= 2023])): summ(g.net, lab)
s = T.net.sort_values(ascending=False); k5 = int(len(s)*.05)
P(f"concentration: top5 trades = {s.iloc[:5].sum()/s.sum():.0%} of total; without best 5% ({k5}): mean {s.iloc[k5:].mean()*100:+.2f}% t {tt(s.iloc[k5:]):+.2f}; without best 10: {s.iloc[10:].mean()*100:+.2f}%")
P(f"median trade {T.net.median()*100:+.2f}%")

# ---- (b) buy & hold over each trade's exact window
E = T.entry.values; xc = mc[T.xi.values]
bh = xc / E - 1 - 2 * (R.FEE + R.SLIP)
bh2 = np.where(T.half, 0.5 * (mc[T.ih.fillna(T.xi).astype(int).values] / E - 1) + 0.5 * (xc / E - 1), xc / E - 1) - 2 * (R.FEE + R.SLIP)
for lab, x in (("(b) B&H full window", bh), ("(b2) B&H exposure-matched", bh2)):
    d = T.net.values - x; summ(x, lab)
    P(f"   excess strat-B&H: mean {d.mean()*100:+.2f}% t {tt(d):+.2f} p(one-sided) {1-stats.t.cdf(tt(d), len(d)-1):.3f}; strat beats in {np.mean(d>0):.0%}")
c4 = b.close; r4 = c4.pct_change().loc["2018-06-01":]
P(f"BTC mean 4h return {r4.mean()*100:.4f}% -> drift over avg hold ({T.bars.mean():.1f} bars) ~ {r4.mean()*T.bars.mean()*100:.2f}%")

# ---- (a) random long entries, same exits, same frequency
valid = ~np.isnan(atr)
def rand_run(p, start="2018-06-01"):
    out = []; j = int(np.searchsorted(b.index.values, np.datetime64(start))); n = len(S.bc)
    while j < n:
        if valid[j] and rng.random() < p:
            r = S.trade(j, atr)
            if r is None: break
            out.append(r["net"]); j = r["bx"]; continue
        j += 1
    return np.array(out)
p = 0.02
for _ in range(3):
    cnt = np.mean([len(rand_run(p)) for _ in range(6)]); p *= len(T) / cnt
P(f"random p per flat bar {p:.4f}")
runs = [rand_run(p) for _ in range(200)]
means = np.array([r.mean() for r in runs]); ns = np.array([len(r) for r in runs]); sums = np.array([r.sum() for r in runs])
P(f"(a) random entries 200 runs: n {ns.mean():.0f} (sd {ns.std():.0f}); mean/trade {means.mean()*100:+.2f}% (5-95% {np.percentile(means,5)*100:+.2f}..{np.percentile(means,95)*100:+.2f}); sum {sums.mean()*100:+.0f}%")
P(f"   strat mean {T.net.mean()*100:+.2f}%: excess {(T.net.mean()-means.mean())*100:+.2f}%/trade; p = share of runs >= strat {np.mean(means >= T.net.mean()):.3f}; z {(T.net.mean()-means.mean())/means.std():.2f}")
P(f"   strat sum {T.net.sum()*100:+.0f}%: p(sum) {np.mean(sums >= T.net.sum()):.3f}")
pd.DataFrame([(i, x) for i, r in enumerate(runs) for x in r], columns=["run", "net"]).to_csv(os.path.join(HERE, "placebo.csv"), index=False)
for lab, st in (("2018-22", "2018-06-01"), ("2023+", "2023-01-01")):
    rr = [rand_run(p, st) for _ in range(200)]
    if lab == "2018-22": rr = [r for r in rr]  # full; split below by real only
    mm = np.array([r.mean() for r in rr]); real = T[T.t >= st].net.mean()
    P(f"   from {st}: strat {real*100:+.2f}% vs random {mm.mean()*100:+.2f}%; p {np.mean(mm >= real):.3f}")

# ---- (c) filter removed
for lab, kw in (("(c1) ADX>25 only, no EMA stack", dict(use_ema=False)), ("(c2) EMA stack only, no ADX", dict(use_adx=False)),
                ("(c3) no filter (always long)", dict(use_ema=False, use_adx=False))):
    s2, _ = S.signal(**kw); U = S.run(s2, atr); summ(U.net, lab)
    w = stats.ttest_ind(T.net, U.net, equal_var=False)
    P(f"   excess {(T.net.mean()-U.net.mean())*100:+.2f}%/trade, Welch t {w.statistic:+.2f} p(one-sided) {w.pvalue/2 if w.statistic>0 else 1-w.pvalue/2:.3f}; sum {U.net.sum()*100:+.0f}% vs {T.net.sum()*100:+.0f}%")
    uu = U.copy(); uu["d"] = (uu.xi.map(lambda i: m.index[i]) - (uu.t + pd.Timedelta("4h"))).dt.total_seconds() / 86400
    P(f"   days in market {uu.d.sum():.0f} vs strat {T.days.sum():.0f}; return per in-market day {U.net.sum()/uu.d.sum()*100:.3f}% vs strat {T.net.sum()/T.days.sum()*100:.3f}%")

# ---- neighbours
P("== neighbours")
def nb(lab, sig_kw={}, tr_kw={}, run_kw={}):
    s2, a2 = S.signal(**sig_kw); U = S.run(s2, a2, **run_kw, **tr_kw); summ(U.net, lab); return U
for a in (20, 30): nb(f"ADX {a}", dict(adx_min=a))
for k in (1.5, 2.5): nb(f"stop {k}", tr_kw=dict(k_stop=k))
for k in (2.5, 3.5): nb(f"half {k}", tr_kw=dict(k_half=k))
for k in (1.5, 2.5): nb(f"trail {k}", tr_kw=dict(k_trail=k))
for e in ((10, 30, 60), (20, 50, 200), (9, 21, 55), (30, 60, 120)): nb(f"EMA {e}", dict(emas=e))
nb("ratcheting trail", tr_kw=dict(ratchet=True))
nb("no re-entry on the exit bar", run_kw=dict(reentry_same_bar=False))

# ---- delays
P("== delays / leaks")
def delayed(mode):
    out = []; j = int(np.searchsorted(b.index.values, np.datetime64("2018-06-01")))
    while j < len(S.bc) - 1:
        if sig[j]:
            if mode == "min": i = S.i1[j]; r = S.trade(j, atr, entry_px=S.mo[i], start_min=i + 1)
            else: r = S.trade(j + 1, atr)
            if r is None: break
            out.append(r["net"]); j = r["bx"]; continue
        j += 1
    return out
summ(delayed("min"), "entry at next 1-min open")
summ(delayed("bar"), "entry one 4h bar later")
R.FEE, R.SLIP = 0.001, 0.0004; summ(S.run(sig, atr).net, "costs x2"); R.FEE, R.SLIP = 0.0005, 0.0002

F = pd.DataFrame(dict(entry_time=ct_end[S.i1[T.j.values] - 1], exit_time=ct_end[T.xi.values], side=1, entry=T.entry.values, exit=T.exit.values))
F.to_csv(os.path.join(HERE, "fills.csv"), index=False)
lastmin = m.index[S.i1[T.j.values] - 1]; P(f"entry minute = last minute of 4h bar: {np.mean(lastmin == T.t + pd.Timedelta('239min')):.1%}; exits after entry bar: {np.mean(T.xi.values >= S.i1[T.j.values]):.0%}")
T[["date", "side", "net", "t", "tx"]].to_csv(os.path.join(HERE, "trades_replica.csv"), index=False)
