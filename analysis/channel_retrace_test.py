"""Rogul (SSRN 6469419, 2026) 'Hybrid systematic-discretionary channel breakout' made mechanical,
NQ 1-minute, 2018-2026. The paper withholds its lookbacks and uses a discretionary bias, so the
parameters here are mine (stated below) and the bias is replaced by price rules (plus a
perfect-hindsight bias as the paper's own 'upper bound').

Engine (paper section 3.2-3.3, 4):
  breakout   1-min close above the highest high (below the lowest low) of the previous N bars
  retrace    within R bars after the breakout, a bar's low (high) touches the M-bar SMA
  confirm    a bar closing in the bias direction, above (below) the SMA, volume > mean of previous P bars
  entry      at that bar's close, entries 8:45-10:00 CT (9:45-11:00 ET)
  stop       'swing': beyond the extreme since the breakout (1 tick); 'vol': 2 x ATR(14, 1-min) x
             sqrt(breakout volume / mean volume) clipped to 1-3 (the paper's volume-adaptive stop)
  exit       'trail': tiers 2R -> breakeven, 3R -> +1R, 5R -> +3R, 10R -> +8R; 'tp2': fixed 2R target;
             flat 15:00 CT either way
  one-loss   no more trades that day after a loss
Costs $7.25 + 1 tick per market/stop fill, per NQ ($20/pt). Stop before target inside one bar.
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g = pickle.load(open(SP + "g24.pkl", "rb")); lab = pickle.load(open(SP + "lab.pkl", "rb"))
PV, COST, TICK = 20.0, 7.25, 0.25
J0, JE0, JE1, JX = 510, 525, 600, 900          # 8:30 start, entries 8:45-10:00, flat 15:00 CT

# continuous EMAs of 1-min closes for the bias rules (spans in minutes ~ 20 bars of 15/30/60/240 min)
fc = g.c.ravel(); ok = ~np.isnan(fc)
ema = {}
for span in (300, 600, 1200, 4800):
    e = np.full(fc.shape, np.nan); e[ok] = pd.Series(fc[ok]).ewm(span=span).mean().to_numpy()
    ema[span] = pd.Series(e).ffill().to_numpy().reshape(g.c.shape)
onb_dir = np.zeros(g.D); onb_dir[lab.tr] = np.sign(lab.C["ONB_L"]) * 0 + (lab.C["ONB_L"] != 0) - (lab.C["ONB_S"] != 0)
day_dir = np.sign(g.c[:, JX] - g.c[:, J0])     # hindsight: the RTH direction of the day


def bias_ok(mode, d, j, side):
    c = g.c[d, j]
    if mode == "none": return True
    if mode == "mtf": return side * (c - ema[300][d, j]) > 0 and side * (c - ema[600][d, j]) > 0
    if mode == "htf": return all(side * (c - ema[s][d, j]) > 0 for s in (300, 600, 1200, 4800))
    if mode == "onb": return onb_dir[d] == side
    if mode == "hindsight": return day_dir[d] == side


def run(N=20, M_=20, P=20, R=30, stop="swing", exit="trail", bias="none"):
    out = []
    for d in g.trading:
        o, h, l, c, v = (getattr(g, k)[d, :JX + 1] for k in ("o", "h", "l", "c", "v"))
        if np.isnan(c[J0:JX + 1]).mean() > 0.2 or np.isnan(c[JX]): continue
        idx = np.nonzero(~np.isnan(c))[0]
        oo, hh, ll, cc, vv = o[idx], h[idx], l[idx], c[idx], v[idx]
        hi = pd.Series(hh).rolling(N).max().shift(1).to_numpy(); lo = pd.Series(ll).rolling(N).min().shift(1).to_numpy()
        ma = pd.Series(cc).rolling(M_).mean().to_numpy(); va = pd.Series(vv).rolling(P).mean().shift(1).to_numpy()
        pc = np.r_[np.nan, cc[:-1]]
        atr = pd.Series(np.nanmax(np.c_[hh - ll, abs(hh - pc), abs(ll - pc)], 1)).rolling(14).mean().to_numpy()
        setup = 0; pos = 0; done = False
        for i in np.nonzero(idx >= J0)[0]:
            j = idx[i]
            if pos:                                            # manage the open trade
                hit = (ll[i] <= sl) if pos > 0 else (hh[i] >= sl)
                if hit:
                    px = (min(oo[i], sl) if pos > 0 else max(oo[i], sl)) - pos * TICK; kind = 0
                elif tp is not None and ((hh[i] >= tp) if pos > 0 else (ll[i] <= tp)):
                    px = tp; kind = 1
                elif j >= JX:
                    px = cc[i] - pos * TICK; kind = 0
                else:
                    if exit == "trail":
                        fav = ((hh[i] - e) if pos > 0 else (e - ll[i])) / rk
                        for at, lock in ((10, 8), (5, 3), (3, 1), (2, 0)):
                            if fav >= at:
                                new = e + pos * lock * rk
                                sl = max(sl, new) if pos > 0 else min(sl, new); break
                    continue
                net = (px - e) * pos * PV - COST
                out.append((g.ts[d], d, j0, j, pos, e, px, kind, net, rk))
                pos = 0; done = done or net < 0
                continue
            if done or j > JE1: continue
            if np.isnan(hi[i]) or np.isnan(ma[i]) or np.isnan(va[i]): continue
            if cc[i] > hi[i]: setup, bi, ret, ext = 1, i, False, ll[i]
            elif cc[i] < lo[i]: setup, bi, ret, ext = -1, i, False, hh[i]
            if setup and i - bi > R: setup = 0
            if not setup: continue
            ext = min(ext, ll[i]) if setup > 0 else max(ext, hh[i])
            if not ret and ((ll[i] <= ma[i]) if setup > 0 else (hh[i] >= ma[i])): ret = True
            if ret and j >= JE0 and setup * (cc[i] - oo[i]) > 0 and setup * (cc[i] - ma[i]) > 0 \
                    and vv[i] > va[i] and bias_ok(bias, d, j, setup):
                e = cc[i] + setup * TICK; pos = setup; j0 = j
                if stop == "swing":
                    sl = ext - setup * TICK
                else:
                    k = np.clip(np.sqrt(vv[bi] / va[bi]) if va[bi] > 0 else 1, 1, 3)
                    sl = e - setup * 2 * atr[i] * k
                rk = max(abs(e - sl), 2.0); sl = e - setup * rk
                tp = e + setup * 2 * rk if exit == "tp2" else None
                setup = 0
    return pd.DataFrame(out, columns=["date", "day", "j0", "j1", "side", "entry", "exit", "kind", "net", "risk"])


def line(t, name):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); h = x[y >= 2023]
    pf = lambda s: s[s > 0].sum() / max(1e-9, -s[s < 0].sum())
    return (f"{name:<38} n={len(x):5d} win {np.mean(x>0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f} "
            f"t={x.mean()/x.std()*np.sqrt(len(x)):4.1f} yrs+ {(by>0).sum()}/{len(by)} | 2023+ n={len(h)} avg ${h.mean():4.0f} PF {pf(h):.2f}"
            f" | L ${x[t.side>0].mean():4.0f} S ${x[t.side<0].mean():4.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    res = {}
    tried = 0
    for bias in ("none", "mtf", "htf", "onb", "hindsight"):
        for stop in ("swing", "vol"):
            for ex in ("trail", "tp2"):
                for N in (20, 60):
                    t = run(N=N, stop=stop, exit=ex, bias=bias); tried += 1
                    res[(bias, stop, ex, N)] = t
                    print(line(t, f"{bias:9s} {stop:5s} {ex:5s} N={N}"), flush=True)
    print(f"variants tried: {tried}")
    pickle.dump(res, open(SP + "chret.pkl", "wb"))


# ---------------- record of the follow-up checks (2026-10-12)
# Placebo (scratch chret2.py): on the 664 days the ONB-bias version traded, a random entry minute
# 8:45-10:00 in the ONB direction with the same risk distance and exit averaged $356 (30 runs,
# $254-420) vs $284 for the engine's entry: the engine beat only 3% of runs, so the channel /
# retracement / volume entry adds nothing; the edge is the Overnight Bias direction.
# Correlation of daily P&L: ONB 0.52, ONB ML v2 0.40, VB 0.15, OND -0.01, EOS 0.00.
# On ONB ML v2 days $553 a trade (229), on the days ML skips $142 (435).
def metrics_by_side(t, name):
    dates = pd.DatetimeIndex(g.ts[lab.tr]); rows = {}
    for s, nm in ((0, "all"), (1, "longs"), (-1, "shorts")):
        x = t if s == 0 else t[t.side == s]
        d = pd.Series(0.0, index=dates); a = x.groupby("date").net.sum(); d.loc[a.index] += a.values
        rows[f"{name} {nm}"] = (d[d.index.year >= 2018], x.net.values)
    return rows
