"""Markov regime transitions (user, 2026-10-17; 'Quant ... with Fable 5' video): states from the 20-trading-day change
(> +5% bull, -5..+5% sideways, < -5% bear); count today -> tomorrow transitions (9 combinations) per symbol; then the
question that matters for trading: does today's state, or the transition into it, predict TOMORROW's return?

  A  transition matrix per symbol (NQ, ES, YM, GC, CL, BTC), against a placebo: the same daily returns shuffled
     (no memory at all) give the matrix a 20-day window produces mechanically (19 of 20 days shared day to day)
  B  next day's return by today's state and by the 9 transitions (yesterday's state -> today's): close-to-close and the
     Apex-tradable day session (index 8:30 -> 15:00 CT, CL 8:00 -> 13:30, GC 7:20 -> 12:30, BTC 8:30 -> 15:00),
     mean, t, 2018-22 vs 2023+; vs the unconditional mean
  C  the best cells as a long / short day-session strategy, per contract, $ costs + 1 tick a fill
Daily closes at the session end; roll jumps removed (roll bars from s_rank_gap_round2_test). Pre-specified thresholds.
  python3 analysis/regime_markov_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import s_rank_gap_round2_test as SR
from grid24 import jof

SESS = {"NQ": (830, 1500), "ES": (830, 1500), "YM": (830, 1500), "GC": (720, 1230), "CL": (800, 1330), "BTC": (830, 1500)}
ROLLS = {"NQ": SR.rolls_index, "ES": SR.rolls_index, "YM": SR.rolls_index, "GC": SR.rolls_gc, "CL": SR.rolls_cl, "BTC": SR.rolls_btc}
ST = ["bear", "side", "bull"]


def series(nm):
    S = SR.Sym(nm); bars, _ = ROLLS[nm](S); S.set_rolls(bars)
    a, b = SESS[nm]; rows = S.tr; N = S.N
    ic = rows * 1440 + jof(b); io = rows * 1440 + jof(a)            # session-end bar and session-open bar (closing a)
    ic = S.prevv[np.clip(ic, 0, N - 1)]
    cl = S.CF[ic]
    # roll jump between consecutive closes: sum of the open-minus-previous-close jump at roll bars in between
    j, _, _ = S.jumps(); jr = np.zeros(N); jr[S.rollbars] = np.nan_to_num(j[S.rollbars]); cj = np.cumsum(jr)
    adj = np.r_[np.nan, cj[ic[1:]] - cj[ic[:-1]]]
    r = np.log(cl / np.r_[np.nan, cl[:-1]]) - np.r_[np.nan, adj[1:]] / cl
    # day session: first open after a, last close at or before b (no roll inside)
    oi = S.first_open(io + 1)
    sess = pd.Series(np.where(oi >= 0, S.CF[ic] / np.where(oi >= 0, S.O[np.clip(oi, 0, N - 1)], np.nan) - 1, np.nan))
    df = pd.DataFrame(dict(r=r, sess=sess.to_numpy(), open=np.where(oi >= 0, S.O[np.clip(oi, 0, N - 1)], np.nan), close=cl),
                      index=S.TS[rows])
    df = df[df.index >= ("2019-01-01" if nm == "BTC" else "2018-01-01")]
    return df, S


def states(r):
    c20 = np.exp(r.rolling(20).sum()) - 1
    return pd.Series(np.where(c20 > 0.05, "bull", np.where(c20 < -0.05, "bear", "side")), index=r.index).where(c20.notna())


def matrix(st):
    t = pd.crosstab(st.shift(1), st, normalize="index").reindex(index=ST, columns=ST)
    return t


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(__doc__.split("\n")[0])
    found = []; ntests = 0
    for nm in ["NQ", "ES", "YM", "GC", "CL", "BTC"]:
        df, S = series(nm); st = states(df.r)
        print(f"\n{'=' * 100}\n{nm}: {len(df)} days; days by state " + ", ".join(f"{k} {v:.0%}" for k, v in st.value_counts(normalize=True).items()))
        m = matrix(st)
        rng = np.random.default_rng(1); pl = []
        for _ in range(200):
            rr = pd.Series(rng.permutation(df.r.dropna().to_numpy()), index=df.r.dropna().index); pl.append(matrix(states(rr)).to_numpy())
        pm = np.nanmean(pl, 0)
        print("   A. P(tomorrow | today), actual  [shuffled-returns placebo]:")
        for i, k in enumerate(ST):
            print(f"      {k:<5} -> " + "  ".join(f"{c} {m.loc[k, c]:5.0%} [{pm[i, jx]:4.0%}]" for jx, c in enumerate(ST)))
        # B: next day's returns by today's state and by transition
        nxt = df[["r", "sess"]].shift(-1); prev = st.shift(1)
        base = {c: nxt[c].mean() for c in ("r", "sess")}
        print(f"   B. next day's return (bp) by today's state / transition; unconditional: close-to-close {base['r'] * 1e4:+.1f}, day session {base['sess'] * 1e4:+.1f}")
        cells = [(k, st == k) for k in ST] + [(f"{a}->{b}", (prev == a) & (st == b)) for a in ST for b in ST if a != b]
        for lab, msk in cells:
            out = []
            for c in ("r", "sess"):
                x = nxt[c][msk]; o = nxt[c][~msk & st.notna()]
                td = (x.mean() - o.mean()) / np.sqrt(x.var() / len(x) + o.var() / len(o)) if len(x) > 5 else np.nan
                e, h = x[x.index < "2023-01-01"], x[x.index >= "2023-01-01"]
                out.append(f"{x.mean() * 1e4:+6.1f} (t {tstat(x):+4.1f}, vs rest {td:+4.1f}; 18-22 {e.mean() * 1e4:+6.1f} / 23+ {h.mean() * 1e4:+6.1f})")
                ntests += 1
                if c == "sess" and len(x) >= 20 and abs(tstat(x)) >= 2.5 and np.sign(e.mean()) == np.sign(h.mean()) == np.sign(x.mean()):
                    found.append((nm, lab, len(x), x.mean() * 1e4, tstat(x)))
            print(f"      {lab:<11} n {int(msk.sum()):4d} | next close-to-close {out[0]} | next day session {out[1]}")
    print(f"\n{ntests} tests. Day-session cells with |t| >= 2.5, n >= 20, same sign in both periods:")
    for f in found: print("   ", f)
    if not found: print("    none")
