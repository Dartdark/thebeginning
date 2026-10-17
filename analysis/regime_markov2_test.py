"""Markov regimes without the overlapping 20-day window (user, 2026-10-17: 'you don't have to use the 20-day thing').
States, each known at today's session close, scaled by the trailing 60-day st.dev. of daily returns (no look-ahead):
  1d   today's return   > +0.5 sd up / < -0.5 sd down / else flat
  5d   last 5 days      > +0.5 sd x sqrt(5) up / < -0.5 sd x sqrt(5) down / else flat
  vol  20-day realised vol vs its trailing 250-day median: > 1.25x wild / < 0.8x calm / else normal
Per symbol (NQ ES YM GC CL BTC): transition matrix vs shuffled-returns placebo, and tomorrow's return (close-to-close and
the Apex day session) by today's state and by the 9 transitions. Roll jumps removed (regime_markov_test.series).
  python3 analysis/regime_markov2_test.py
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from regime_markov_test import series, tstat

LAB = {"1d": ["down", "flat", "up"], "5d": ["down", "flat", "up"], "vol": ["calm", "normal", "wild"]}


def make(r, kind):
    sd = r.rolling(60).std().shift(1)
    if kind == "1d": x, th = r / sd, 0.5
    elif kind == "5d": x, th = r.rolling(5).sum() / (sd * np.sqrt(5)), 0.5
    else:
        rv = r.rolling(20).std(); med = rv.rolling(250, min_periods=120).median().shift(1); x = rv / med
        return pd.Series(np.where(x > 1.25, "wild", np.where(x < 0.8, "calm", "normal")), index=r.index).where(x.notna())
    return pd.Series(np.where(x > th, "up", np.where(x < -th, "down", "flat")), index=r.index).where(x.notna())


if __name__ == "__main__":
    print(__doc__.split("\n")[0]); hits = []; n = 0
    for nm in ["NQ", "ES", "YM", "GC", "CL", "BTC"]:
        df, _ = series(nm); nxt = df[["r", "sess"]].shift(-1)
        print(f"\n{'=' * 100}\n{nm}")
        for kind, labs in LAB.items():
            st = make(df.r, kind); m = pd.crosstab(st.shift(1), st, normalize="index").reindex(index=labs, columns=labs)
            rng = np.random.default_rng(1); pl = []
            for _ in range(100):
                rr = pd.Series(rng.permutation(df.r.dropna().to_numpy()), index=df.r.dropna().index); s2 = make(rr, kind)
                pl.append(pd.crosstab(s2.shift(1), s2, normalize="index").reindex(index=labs, columns=labs).to_numpy())
            pm = np.nanmean(pl, 0)
            print(f"  [{kind}] P(tomorrow | today) actual [placebo]: " + " | ".join(
                f"{a}: " + " ".join(f"{b} {m.loc[a, b]:.0%}[{pm[i, j]:.0%}]" for j, b in enumerate(labs)) for i, a in enumerate(labs)))
            prev = st.shift(1)
            cells = [(k, st == k) for k in labs] + [(f"{a}->{b}", (prev == a) & (st == b)) for a in labs for b in labs]
            for lab, msk in cells:
                x = nxt.sess[msk].dropna(); xc = nxt.r[msk].dropna(); n += 2
                if len(x) < 30: continue
                e, h = x[x.index < "2023-01-01"], x[x.index >= "2023-01-01"]
                t = tstat(x)
                flag = abs(t) >= 2.5 and np.sign(e.mean()) == np.sign(h.mean()) == np.sign(x.mean())
                if flag or abs(tstat(xc)) >= 2.5:
                    print(f"     {lab:<14} n {len(x):4d} next session {x.mean() * 1e4:+6.1f}bp t {t:+4.1f} (18-22 {e.mean() * 1e4:+6.1f} / 23+ {h.mean() * 1e4:+6.1f}) | next close-close {xc.mean() * 1e4:+6.1f}bp t {tstat(xc):+4.1f}")
                if flag: hits.append((nm, kind, lab, len(x), round(x.mean() * 1e4, 1), round(t, 2)))
    print(f"\n{n} tests (state / transition x next session / next close-to-close). Day-session cells |t| >= 2.5, same sign both periods:")
    for h in hits: print("   ", h)
    if not hits: print("    none")
