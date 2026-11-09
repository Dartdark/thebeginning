"""Checker stress tests: threshold sweep, own placebos, marked-to-market drawdown, next-day entry."""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/thebeginning/analysis"); from grid24 import Grid24  # noqa
g = pickle.load(open("/home/user/thebeginning/scratch_data/g24.pkl", "rb"))
b = g.bars(15); per = b["c"].shape[1]; O, H, L, C = (b[k] for k in "ohlc")
st = b["j"] // 60 * 100 + b["j"] % 60; i0 = int(np.where(st == 845)[0][0]); i1 = int(np.where(st == 1500)[0][0])
fo = O.ravel(); fc = C.ravel(); has = ~np.isnan(fo)
S = []  # sessions: (row, ibs, fill index, fill px)
for r in range(g.D):
    if g.dates[r] < 20180101: continue
    sc = C[r, i0:i1 + 1]
    if np.isnan(sc).any(): continue
    hi, lo = np.nanmax(H[r, i0:i1 + 1]), np.nanmin(L[r, i0:i1 + 1])
    if not hi > lo: continue
    k = r * per + i1 + 1
    while k < len(fo) and not has[k]: k += 1
    if k >= len(fo): break
    S.append((r, (sc[-1] - lo) / (hi - lo), k, fo[k]))
S = pd.DataFrame(S, columns=["r", "ibs", "k", "px"]); S["year"] = g.dates[S.r] // 10000
def run(entry_flags, exit_thr=0.80, hold=None):
    out = []; pos = False
    for i in range(len(S)):
        if not pos and entry_flags[i]: pos = True; e = i; continue
        if pos and ((hold is None and S.ibs[i] > exit_thr) or (hold is not None and i - e >= hold[e])):
            out.append((e, i, (S.px[i] - S.px[e]) * 20 - 17.25)); pos = False
    return pd.DataFrame(out, columns=["e", "x", "net"])
def tt(x): return x.mean() / x.std() * np.sqrt(len(x))
print("threshold sweep (exit 0.80):")
for th in (0.05, 0.075, 0.10, 0.125, 0.15, 0.20, 0.25, 0.30):
    T = run((S.ibs < th).values); y = S.year.values[T.e]
    print(f"  IBS<{th:<5} n {len(T):3d} mean ${T.net.mean():6.0f} t {tt(T.net):.2f} | 2023+ mean ${T.net[y>=2023].mean():6.0f} t {tt(T.net[y>=2023]):.2f} | total ${T.net.sum():,.0f}")
real = run((S.ibs < 0.10).values); ny = pd.Series(S.year.values[real.e]).value_counts()
hold = {}
for e, x in zip(real.e, real.x): hold[e] = x - e
rng = np.random.default_rng(7); P1 = []; P2 = []
holds = (real.x - real.e).values
for _ in range(300):
    f = np.zeros(len(S), bool)
    for y, n in ny.items():
        idx = np.where(S.year.values == y)[0]; f[rng.choice(idx, n, replace=False)] = True
    P1.append(run(f).net.mean())
    # duration-matched: random start days, each held a resampled actual hold length (sessions)
    hd = {i: int(rng.choice(holds)) for i in np.where(f)[0]}
    P2.append(run(f, hold=hd).net.mean())
P1, P2 = np.array(P1), np.array(P2)
print(f"real mean ${real.net.mean():.0f}; placebo A (random entry, IBS>0.8 exit): mean ${P1.mean():.0f}, p {np.mean(P1 >= real.net.mean()):.3f}")
print(f"placebo B (random entry, hold-length matched): mean ${P2.mean():.0f}, p {np.mean(P2 >= real.net.mean()):.3f}")
# sessions in market and drift
ins = sum(x - e for e, x in zip(real.e, real.x)); print(f"sessions in market {ins} of {len(S)} ({ins/len(S):.0%})")
bh = (S.px.values[1:] - S.px.values[:-1]) * 20; print(f"unconditional long per session (15:15->15:15) ${bh.mean():.0f}; x sessions held = ${bh.mean()*ins:,.0f} vs real gross ${real.net.sum()+17.25*len(real):,.0f}")
# next-day entry (enter the following session's 15:15 instead)
out = []; pos = False
for i in range(len(S) - 1):
    if not pos and S.ibs[i] < 0.10: pos = True; e = i + 1; continue
    if pos and i >= e and S.ibs[i] > 0.80: out.append((S.px[i] - S.px[e]) * 20 - 17.25); pos = False
out = pd.Series(out); print(f"entry one SESSION later: n {len(out)} mean ${out.mean():.0f} t {tt(out):.2f}")
# exit-variant: exit at next session regardless (1-day hold)
o1 = pd.Series([(S.px[i + 1] - S.px[i]) * 20 - 17.25 for i in range(len(S) - 1) if S.ibs[i] < 0.10]); print(f"every IBS<0.10 day, 1-session hold: n {len(o1)} mean ${o1.mean():.0f} t {tt(o1):.2f}")
# marked-to-market daily DD (mark at every 1-min close; worst intraday and at each 15:15)
eq_close = []; realized = 0; worst_intra = 0; peak = 0; mdd_intra = 0
for e, x, net in real.itertuples(index=False):
    ke, kx = S.k[e], S.k[x]; seg = fc[ke:kx]; seg = seg[~np.isnan(seg)]
    lows = np.nanmin(np.r_[seg, S.px[x]]); 
    path = realized + (seg - S.px[e]) * 20
    mdd_intra = max(mdd_intra, peak - path.min()) if len(path) else mdd_intra
    peak = max(peak, path.max() if len(path) else peak)
    realized += net; peak = max(peak, realized)
# exit-booked DD
cum = real.net.cumsum(); print(f"max DD exit-booked ${(cum.cummax().clip(lower=0) - cum).max():,.0f}; marked on every 1-min close ${mdd_intra:,.0f}")
# proper marked equity: 1-min closes during holds, and once per session (15:15 fill price)
eqm = []; eqd = []; realized = 0
for e, x, net in real.itertuples(index=False):
    seg = fc[S.k[e]:S.k[x] + 1]; seg = seg[~np.isnan(seg)]
    eqm.append(realized + (seg - S.px[e]) * 20)
    eqd.append(realized + (S.px.values[e:x + 1] - S.px[e]) * 20)
    realized += net; eqm.append([realized]); eqd.append([realized])
for lab, q in (("1-min marked", np.concatenate(eqm)), ("daily (15:15) marked", np.concatenate(eqd))):
    print(f"max DD {lab}: ${(np.maximum.accumulate(np.r_[0, q]) - np.r_[0, q]).max():,.0f}")
worst = [(S.r[e], (np.nanmin(fc[S.k[e]:S.k[x] + 1]) - S.px[e]) * 20) for e, x, _ in real.itertuples(index=False)]
w = sorted(worst, key=lambda z: z[1])[:5]; print("worst open-trade excursions:", [(int(g.dates[r]), round(v)) for r, v in w])
