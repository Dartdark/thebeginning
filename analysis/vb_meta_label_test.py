"""Meta-labeling on Vault Break (user, 2026-10-17): the rule decides the entry; a model decides whether to take it.
PRE-REGISTERED (written before any result was seen):
  trades   VB's MultiCharts list (VB v1 report, 1,743 trades 2018-26), net per NQ ($7.25 + 1 tick a fill)
  inputs   known at the decision (the 30-min bar close before the entry) or at the previous 15:00 close:
           daily: ret1, ret5, ret20, rth1, atr_ratio, dist50, rv5_rv20, dow0-4, tdm3, opex_wk, single-print flag (sp)
           trade: trade_no (1-3), mins_after_10 (decision time), ext_noise ((close - noise) / ATR), ext_vwap ((close - VWAP
           from midnight) / ATR), day_move ((close - midnight open) / ATR), range_today ((high - low since midnight) / ATR),
           prev_win (result of today's previous VB trade: +1 / -1 / 0 if first)
  model    ridge on standardised inputs, target net $ winsorised 2-98% and centred, lambda = 100 (scaled as ml_filter_test),
           walk-forward: trained on all trades before year Y, applied to year Y, Y = 2019..2026
  rule     take the trade if predicted net (train mean + prediction) >= 0, else skip; secondary view: skip the bottom third
  checks   kept vs skipped by year; random skips of the same share per year (2,000 draws); funded bench with the filter
           (VB 3 / 1 flagged, 2018 trades all kept), vs the plan
  python3 analysis/vb_meta_label_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
REP = "mc_reports/Backtesting Strategy Performance Report VB v1.xlsx"
LAM = 100.0


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def tdiff(a, b):
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna(); return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))


def features(g, t):
    C = pd.DataFrame(g.c).ffill(axis=1).to_numpy(); D = g.D
    tr = g.trading; dts = pd.DatetimeIndex(g.ts)
    atr = g.daily_atr(15)
    cl15 = pd.Series(C[:, jof(1500)], index=dts); op = pd.Series(g.o[:, jof(831)], index=dts)
    td = pd.Series(False, index=dts); td.iloc[tr] = True
    clt, opt = cl15[td], op[td]; r1 = np.log(clt).diff()
    X = pd.DataFrame(index=clt.index)
    X["ret1"] = r1.shift(1); X["ret5"] = np.log(clt).diff(5).shift(1); X["ret20"] = np.log(clt).diff(20).shift(1)
    X["rth1"] = np.log(clt / opt).shift(1)
    a = pd.Series(atr, index=dts)[td]; X["atr_ratio"] = a / a.rolling(60).mean()
    X["dist50"] = np.log(clt / clt.rolling(50).mean()).shift(1)
    X["rv5_rv20"] = (r1.rolling(5).std() / r1.rolling(20).std()).shift(1)
    for k in range(5): X[f"dow{k}"] = (X.index.dayofweek == k).astype(float)
    mon = X.index.to_period("M"); X["tdm3"] = (pd.Series(1, index=X.index).groupby(mon).cumsum() <= 3).astype(float)
    fri = X.index + pd.to_timedelta(4 - X.index.dayofweek, unit="D"); X["opex_wk"] = ((fri.day >= 15) & (fri.day <= 21)).astype(float)
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); X["sp"] = S.flag.reindex(X.index).fillna(False).astype(float)
    daily = X
    # trade-level, at the decision bar close (the minute before the entry bar's first minute, on the 30-min grid)
    rows = []
    v = np.nan_to_num(g.v); tp = (np.nan_to_num(g.h) + np.nan_to_num(g.l) + np.nan_to_num(g.c)) / 3
    t = t.sort_values(["day", "j0"]).reset_index(drop=True); t["trade_no"] = t.groupby("day").cumcount() + 1
    prev = t.groupby("day").net.shift(1)
    for i, r in t.iterrows():
        d = int(r.day); jd = (int(r.j0) // 30) * 30         # decision = close of the 30-min bar ending at the entry bar's start
        cdec = C[d, jd]; o0 = g.o[d, :][~np.isnan(g.o[d, :])][0]
        hi, lo = np.nanmax(g.h[d, :jd + 1]), np.nanmin(g.l[d, :jd + 1])
        vw = (tp[d, :jd + 1] * v[d, :jd + 1]).sum() / max(1e-9, v[d, :jd + 1].sum()); A = atr[d]
        noise = o0 + 0.30 * A
        rows.append(dict(trade_no=r.trade_no, mins_after_10=jd - jof(1000), ext_noise=(cdec - noise) / A, ext_vwap=(cdec - vw) / A,
                         day_move=(cdec - o0) / A, range_today=(hi - lo) / A,
                         prev_win=0.0 if pd.isna(prev[i]) else float(np.sign(prev[i]))))
    T = pd.DataFrame(rows); dd = pd.DatetimeIndex(g.ts[t.day.to_numpy()])
    T = pd.concat([T, daily.reindex(dd).reset_index(drop=True)], axis=1)
    return t, T.fillna(T.median())


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    t = load_mc(g, REP); t, X = features(g, t)
    from funded_lab import with_slippage
    t["netx"] = with_slippage(t).pipe(lambda u: (u.exit - u.entry) * u.side * 20 - 7.25)   # net incl. 1 tick a market / stop fill
    y = t.netx; yr = pd.DatetimeIndex(t.date).year
    pred = pd.Series(np.nan, index=t.index); W = {}
    for Y in range(2019, 2027):
        trn, tst = yr < Y, yr == Y
        mu, sd = X[trn].mean(), X[trn].std().replace(0, 1)
        A = ((X[trn] - mu) / sd).to_numpy(); b = y[trn].to_numpy()
        lo, hi = np.percentile(b, [2, 98]); b = np.clip(b, lo, hi); bm = b.mean(); b = b - bm
        w = np.linalg.solve(A.T @ A + LAM * len(b) / 100 * np.eye(A.shape[1]), A.T @ b)
        pred[tst] = bm + ((X[tst] - mu) / sd).to_numpy() @ w; W[Y] = pd.Series(w, index=X.columns)
    oos = yr >= 2019; keep = pred >= 0
    k, s = y[oos & keep], y[oos & ~keep]
    print(f"\nOut of sample 2019-26: {oos.sum()} trades, kept {len(k)} ({len(k) / oos.sum():.0%}) avg ${k.mean():.0f} (t {tstat(k):.1f}) | "
          f"skipped {len(s)} avg ${s.mean():.0f} (t {tstat(s):.1f}) | kept - skipped t {tdiff(k, s):+.2f}; IC {np.corrcoef(pred[oos], y[oos])[0, 1]:+.3f}")
    by = pd.DataFrame({"kept": y[oos & keep].groupby(yr[oos & keep]).mean(), "skipped": y[oos & ~keep].groupby(yr[oos & ~keep]).mean(),
                       "n_skip": (oos & ~keep).groupby(yr).sum()[lambda z: z.index >= 2019]})
    print("   by year ($ a trade):\n" + by.round(0).to_string()); print(f"   kept beats skipped in {(by.kept > by.skipped).sum()}/{len(by)} years")
    # secondary: bottom third
    q = pred[oos].groupby(yr[oos]).transform(lambda p: p.rank(pct=True)); bot = q <= 1 / 3
    print(f"   secondary (skip the bottom third per year): kept ${y[oos][~bot].mean():.0f} vs skipped ${y[oos][bot].mean():.0f}, t {tdiff(y[oos][~bot], y[oos][bot]):+.2f}")
    # placebo: random skips, same count per year
    rng = np.random.default_rng(1); gain = y[oos & keep].sum() - y[oos].sum(); pl = []
    yo, so = y[oos].to_numpy(), (~keep[oos]).to_numpy(); yro = yr[oos]
    for _ in range(2000):
        m = np.zeros(len(yo), bool)
        for Y in np.unique(yro):
            ix = np.where(yro == Y)[0]; m[rng.choice(ix, so[yro == Y].sum(), replace=False)] = True
        pl.append(-yo[m].sum())
    pl = np.array(pl); print(f"   total P&L change from skipping: ${gain:,.0f} per NQ; random skips of the same share: p50 ${np.median(pl):,.0f}, "
                             f"p95 ${np.percentile(pl, 95):,.0f}; P(random >= filter) {np.mean(pl >= gain):.3f}")
    print("\n   latest weights (trained on 2018-25, standardised, $ per trade per 1 sd):\n   " +
          W[2026].sort_values(key=abs, ascending=False).round(1).head(10).to_string().replace("\n", "\n   "))
    # funded bench
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    kk = keep | (yr < 2019)
    for nm, tt in (("VBK", t[kk]), ("VB_ALL", t)):
        lab.add(nm, tt[["day", "j0", "j1", "side", "entry", "exit", "kind"]].reset_index(drop=True))
    for base in ("VB_ALL", "VBK"):
        lab.W[base + "_F"] = lab.W[base] * flag[:, None]; lab.C[base + "_F"] = lab.C[base] * flag
        lab.W[base + "_N"] = lab.W[base] * ~flag[:, None]; lab.C[base + "_N"] = lab.C[base] * ~flag
    rest = {"ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    print("\nFunded bench (cushion sizing, full from $1,500):")
    for nm, p in (("plan, VB as now (3 / 1 flagged)", {"VB_ALL_N": 3, "VB_ALL_F": 1, **rest}),
                  ("plan, VB meta-labelled (3 / 1)", {"VBK_N": 3, "VBK_F": 1, **rest}),
                  ("plan, VB meta-labelled 4 / 1", {"VBK_N": 4, "VBK_F": 1, **rest})):
        a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        print(f"   {nm:<36} 1y ${a['expected']:,.0f} blown {a['blown']:.0%} (2023+ starts ${a['s2023_on']:,.0f}) | 2y ${c['expected']:,.0f} blown {c['blown']:.0%}")
