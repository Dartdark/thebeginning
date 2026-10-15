"""Twin-like round 2 (2026-10-15): keep Morning Momentum's DIRECTION, enter on a pullback with a tight stop, so the loss per
trade fits a $2,000 trailing drawdown. Pre-registered before looking (3 variants, counted in TRIALS.csv):
  signal  Twin's MO signal (10-min oscillator cross +/-100, bucket ending 8:40-9:30 CT, first per date, not on half days),
          run with the breakout leg OFF so no signal is blocked
  V0      baseline: market entry next bar, stop 0.292 x 15-day ATR (= 75 pts at NQ's median ATR), out at the 14:51 open
  V1      VWAP pullback: limit at the session VWAP (from the 8:31 bar) as it stands each minute after the signal, until 11:00
          CT (fill needs a 1-tick trade-through), stop 0.10 x ATR, out at the 14:51 open
  V2      pivot pullback: limit at the oscillator's EMA21 pivot at the signal (fixed level), until 11:00, stop 0.10 x ATR, 14:51
  V3      market entry next bar, stop 0.10 x ATR, 14:51
Costs $7.25 + 1 tick a market / stop fill (limit entries: no slip). Per NQ; whole / longs / shorts; 2018-22 vs 2023-26;
standard metrics + 2023+ bootstrap / permutation; random-side placebo (same fills, opposite side at random, 200 draws);
then the funded bench, risk-sized (MNQ = risk / stop), added to the plan and alone.
  python3 analysis/mo_pullback_test.py [SCRATCH_DIR]
"""
import sys, io, pickle, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import twin_continuation_test as tc
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25


def run(g, sig, variant, side_override=None):
    atr = g.daily_atr(15); out = []
    J0, JX, JL = jof(831), jof(1451), jof(1100)
    for k, s_ in enumerate(sig.itertuples()):
        r, js = s_.row, s_.j                      # signal bar (close minute)
        side = s_.side if side_override is None else side_override[k]
        a = atr[r]
        if not np.isfinite(a): continue
        h, l, o, c, v = g.h[r], g.l[r], g.o[r], g.c[r], np.nan_to_num(g.v[r])
        if variant in ("V0", "V3"):
            j_in = js + 1
            if np.isnan(o[j_in]): continue
            ent = o[j_in]; slip_in = 1
        else:
            if variant == "V1":
                tp = (h + l + c) / 3; cum = np.nancumsum(np.where(np.arange(1440) >= J0, np.nan_to_num(tp) * v, 0))
                cv = np.cumsum(np.where(np.arange(1440) >= J0, v, 0)); vw = cum / np.maximum(cv, 1)
            j_in = None
            for j in range(js + 1, JL + 1):
                if np.isnan(c[j]): continue
                L = vw[j - 1] if variant == "V1" else s_.piv          # limit known at the previous bar's close
                if (side > 0 and l[j] <= L - TICK) or (side < 0 and h[j] >= L + TICK):
                    j_in = j; ent = min(o[j], L) if side > 0 else max(o[j], L); break
            if j_in is None: continue
            slip_in = 0
        stopd = (0.292 if variant == "V0" else 0.10) * a; st = ent - side * stopd; px = None
        for j in range(j_in + 1, JX + 1):
            if np.isnan(c[j]): continue
            if j == JX: px, kind = o[j], 2; break
            if (side > 0 and l[j] <= st) or (side < 0 and h[j] >= st):
                px, kind = (min(o[j], st) if side > 0 else max(o[j], st)), 0; break
        if px is None:
            last = np.where(~np.isnan(c[:JX]))[0][-1]; px, kind = c[last], 2
        net = (px - ent) * side * PV - COMM - (slip_in + 1) * TICK * PV
        out.append(dict(date=pd.Timestamp(g.ts[r]), side=side, entry=ent, exit=px, kind=kind, net=net, stop_pts=stopd,
                        ej=j_in, row=r))
    return pd.DataFrame(out)


def line(x, nm, w=30):
    x = x.dropna(); y = x.index.year; by = x.groupby(y).sum(); t = x.mean() / x.std() * np.sqrt(len(x))
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n {len(x):4d} avg ${x.mean():6.1f} PF {pf:4.2f} t {t:5.2f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 2018-22 ${x[y < 2023].mean():6.1f} 2023-26 ${x[y >= 2023].mean():6.1f}"), t


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); B = tc.flatten(g)
    T = tc.simulate(B, use_bo=False); T = T[T.setup == "MO"]
    sig = pd.DataFrame({"row": B["row"][T.sig_i.to_numpy()], "j": B["j"][T.sig_i.to_numpy()], "side": T.side.to_numpy(), "piv": T.piv.to_numpy()})
    sig = sig[pd.DatetimeIndex(g.ts[sig.row]) >= "2018-01-01"].reset_index(drop=True)
    print(f"\n{len(sig)} MO signals 2018-26 (breakout leg off)")
    res = {}
    for v in ("V0", "V1", "V2", "V3"):
        X = run(g, sig, v).set_index("date"); res[v] = X
        s, t = line(X.net, f"{v}"); print(s + f" | fills {len(X) / len(sig):.0%}, median stop ${X.stop_pts.median() * 2:.0f} per MNQ (2026 ${X[X.index.year == 2026].stop_pts.median() * 2:.0f})")
        for sd, sn in ((1, "longs"), (-1, "shorts")): print(line(X[X.side == sd].net, f"   {v} {sn}")[0])
    rng = np.random.default_rng(7)
    print("\nRandom-side placebo (same signals and fills, side at random, 200 draws):")
    for v in ("V1", "V2", "V3"):
        real = res[v].net.mean(); sims = []
        for _ in range(200):
            so = rng.choice([-1, 1], len(sig)); sims.append(run(g, sig, v, side_override=so).net.mean())
        sims = np.array(sims); print(f"   {v}: real ${real:.1f}; placebo mean ${sims.mean():.1f}, p95 ${np.percentile(sims, 95):.1f}; share >= real {np.mean(sims >= real):.3f}")
    for v in ("V1", "V2", "V3"): res[v].to_pickle(SP + f"mo_pullback_{v}.pkl")
    best = max(("V1", "V2", "V3"), key=lambda v: line(res[v].net, v)[1]); X = res[best]
    days = pd.bdate_range("2018-01-01", X.index.max()); rows = {}
    for nm, x in ((f"{best} all", X.net), ("longs", X[X.side == 1].net), ("shorts", X[X.side == -1].net)):
        rows[nm] = (x.groupby(level=0).sum().reindex(days, fill_value=0.0), x)
    print(f"\nStandard metrics, best by t ({best}), per NQ:"); print(M.table(rows))
    b_, p_ = R.report({k: v[0][v[0].index >= "2023"] for k, v in rows.items()}, n=2000); print("2023+ bootstrap:\n" + b_ + "\n2023+ drawdown permutation:\n" + p_)
