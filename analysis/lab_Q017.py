"""Lab Q017: trend-direction turn-of-month flow in CL, NG, GC, ZN, 6E (Van Hemert 2014 MOM-TOM), pooled in R units.
Pre-registration: checks/candidates/lab_Q017/PREREG.md. Stages 1-2 on 2018-22; stage 3 only with --holdout.
  python3 analysis/lab_Q017.py [--holdout]
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24, jof
import metrics as M

HOLD = "--holdout" in sys.argv
SPEC = {"CL": (1000.0, 0.01, 801, "cl"), "NG": (10000.0, 0.001, 801, "ng"), "GC": (100.0, 0.1, 721, "gc"),
        "ZN": (1000.0, 1 / 64, 721, "zn"), "6E": (125000.0, 0.00005, 721, "e6")}
COMM = 5.0


def load(sym):
    pk = f"scratch_data/{SPEC[sym][3]}.pkl"
    if os.path.exists(pk): return pickle.load(open(pk, "rb"))
    g = Grid24(f"data/{sym}_1min_20*.csv", night_pattern=""); pickle.dump(g, open(pk, "wb"), protocol=4); return g


def market(sym):
    """Per-session frame: row, date, tom flag, days10-12 flag, side63, side252, atr."""
    g = load(sym); rows = g.trading; idx = pd.DatetimeIndex(g.ts[rows])
    c = g.c[rows][:, :jof(1600) + 1]
    mark = pd.Series([r[np.isfinite(r)][-1] if np.isfinite(r).any() else np.nan for r in c], index=idx).ffill()
    per = idx.to_period("M"); s = pd.Series(np.arange(len(idx)), index=idx)
    rk_last = s.groupby(per).rank(ascending=False).to_numpy(); rk_first = s.groupby(per).rank().to_numpy()
    df = pd.DataFrame(dict(row=rows, tom=(rk_last == 1) | (rk_first <= 2), mid=np.isin(idx.day, [10, 11, 12]),
                           s63=np.sign(mark.shift(1) / mark.shift(64) - 1).to_numpy(),
                           s252=np.sign(mark.shift(1) / mark.shift(253) - 1).to_numpy(),
                           atr=g.daily_atr(14)[rows]), index=idx)
    return g, df


def trade(g, sym, r, s, a):
    pv, tick, j0s, _ = SPEC[sym]; j0, j1 = jof(j0s), jof(1325)
    o, h, l, c = g.o[r, j0:j1 + 1], g.h[r, j0:j1 + 1], g.l[r, j0:j1 + 1], g.c[r, j0:j1 + 1]
    if not (np.isfinite(a) and a > 0 and np.isfinite(o[0]) and s != 0 and np.isfinite(s)): return None
    ent = o[0]; stop = ent - s * 0.5 * a; px = None
    for i in range(len(o)):
        if not np.isfinite(h[i]): continue
        if s > 0 and l[i] <= stop: px = min(stop, o[i]) - tick; break
        if s < 0 and h[i] >= stop: px = max(stop, o[i]) + tick; break
    if px is None:
        last = c[np.isfinite(c)]; px = last[-1] - s * tick
    usd = s * (px - ent) * pv - COMM - tick * pv
    return usd, usd / (0.5 * a * pv)


def run(M_, syms, mask_col, side_col, lo, hi, rows_override=None):
    out = []
    for sym in syms:
        g, df = M_[sym]; d = df[(df.index.year >= lo) & (df.index.year <= hi)]
        d = d[d[mask_col]] if rows_override is None else d.loc[d.index.isin(rows_override[sym])]
        for dt, rw in d.iterrows():
            t = trade(g, sym, int(rw.row), rw[side_col], rw.atr)
            if t: out.append((dt, sym, t[0], t[1]))
    return pd.DataFrame(out, columns=["date", "sym", "usd", "R"]).set_index("date").sort_index()


def tstat(x): return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def show(T, nm):
    x = T.R; by = x.groupby(x.index.year).sum()
    print(f"  {nm:<28} n={len(x):4d} avg {x.mean():+.3f}R PF {pf(x):4.2f} t {tstat(x):5.2f} win {np.mean(x > 0):.0%} "
          f"yrs+ {(by > 0).sum()}/{len(by)}  " + " ".join(f"{y}:{v:+.1f}" for y, v in by.items()))


if __name__ == "__main__":
    MK = {s: market(s) for s in SPEC}; ALL, CN = list(SPEC), ["CL", "NG"]
    cfg = {1: (ALL, "s63"), 2: (CN, "s63"), 3: (ALL, "s252")}
    print("Stage 1 (2018-22), R = net $ / (0.5 ATR x point value)")
    T = {v: run(MK, s, "tom", c, 2018, 2022) for v, (s, c) in cfg.items()}
    for v, nm in ((1, "V1 all 5, 63-day trend"), (2, "V2 CL + NG, 63-day"), (3, "V3 all 5, 252-day trend")): show(T[v], nm)
    best = max(T, key=lambda v: tstat(T[v].R)); x = T[best]; syms, col = cfg[best]
    s1 = tstat(x.R) >= 2.0 and pf(x.R) >= 1.15 and len(x) >= 80
    print(f"  best V{best}: stage 1 {'PASS' if s1 else 'FAIL'}")
    print("  per market $ per 1 contract: " + ", ".join(f"{s} {x[x.sym == s].usd.mean():+.0f} (n {int((x.sym == s).sum())})" for s in syms))
    show(run(MK, syms, "mid", col, 2018, 2022), f"control days 10-12 V{best}")
    # random-day placebo: same count per market from non-TOM sessions
    rng = np.random.default_rng(7); pools = {}
    for s in syms:
        g, df = MK[s]; d = df[(df.index.year >= 2018) & (df.index.year <= 2022) & ~df.tom]
        P = run(MK, [s], "tom", col, 2018, 2022, rows_override={s: d.index})
        pools[s] = P.R.reindex(d.index)                      # NaN = no trade
    cnt = x.sym.value_counts()
    pm = np.array([np.nanmean(np.concatenate([pools[s].iloc[rng.choice(len(pools[s]), cnt[s], replace=False)].to_numpy()
                                              for s in syms])) for _ in range(500)])
    p = np.mean(pm >= x.R.mean()); by = x.R.groupby(x.index.year).sum(); s2 = p < 0.05 and (by > 0).sum() >= 4
    print(f"\nStage 2 placebo V{best}: random non-TOM avg {np.nanmean(pm):+.3f}R, p = {p:.3f}; stage 2 {'PASS' if s2 else 'FAIL'}")
    daily = x.R.groupby(level=0).sum().reindex(pd.date_range("2018-01-01", "2022-12-31", freq="B"), fill_value=0.0) * 500
    m = M.perf(daily, x.R * 500)
    print("  metrics V%d 2018-22 at $500 per R: Sharpe %.2f Sortino %.2f PF %.2f Calmar %.2f Ulcer %.2f" %
          (best, m["sharpe"], m["sortino"], m["profit_factor"], m["calmar"], m["ulcer"]))
    for sd, nm in ((1, "longs"), (-1, "shorts")):
        side = np.array([MK[s][1].loc[d, col] for d, s in zip(x.index, x.sym)]); show(x[side == sd], f"  V{best} {nm}")
    if HOLD and s1 and s2:
        h = run(MK, syms, "tom", col, 2023, 2026); print("\nStage 3 holdout (one look)"); show(h, f"V{best} 2023-onward")
        show(pd.concat([x, h]), f"V{best} full")
