"""Meta-labeling on Late-Day Flow (user, 2026-10-17), same method as analysis/vb_meta_label_test.py.
PRE-REGISTERED (written before any result was seen):
  trades   LDF's MultiCharts list (Late Day Flow report), one a day at 14:00 -> 14:30 CT, net per NQ ($7.25 + 1 tick a fill)
  inputs   daily (previous 15:00 close): ret1, ret5, ret20, rth1, atr_ratio, dist50, rv5_rv20, dow0-4, tdm3, opex_wk
           signal (14:00 bar close): side (+1 long / -1 short), move_atr (|14:00 close - 8:30 open| / ATR), last_hour
           ((14:00 close - 13:00 close) / ATR x side: the move still running into 14:00), vwap_dist ((14:00 close - VWAP
           since 8:30) / ATR x side), range_atr ((high - low 8:30-14:00) / ATR), gap_atr ((8:30 open - previous 15:00
           close) / ATR x side), afternoon_share (|14:00 close - 11:00 close| / |move|)
  model    ridge, standardised inputs, target net $ winsorised 2-98% and centred, lambda 100, walk-forward by year 2019-26
  rule     take if predicted net >= 0; secondary: skip the bottom third
  checks   kept vs skipped by year, longs / shorts, random skips (2,000), funded bench (LDF 2 MNQ) vs the plan
  python3 analysis/ldf_meta_label_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from vb_meta_label_test import features as vb_features, tstat, tdiff, LAM

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
REP = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx"


def signal_features(g, t):
    C = pd.DataFrame(g.c).ffill(axis=1).to_numpy(); atr = g.daily_atr(15)
    v = np.nan_to_num(g.v); tp = (np.nan_to_num(g.h) + np.nan_to_num(g.l) + np.nan_to_num(g.c)) / 3
    rows = []
    for r in t.itertuples():
        d = int(r.day); A = atr[d]; s = r.side; a, b = jof(831), jof(1400)
        o830 = g.o[d, a]; c14 = C[d, b]; mv = c14 - o830
        prevc = C[d - 1, jof(1500)] if d > 0 else np.nan
        k = d - 1
        while k > 0 and np.isnan(g.c[k, jof(1500)]): k -= 1
        prevc = C[k, jof(1500)]
        vw = (tp[d, a:b + 1] * v[d, a:b + 1]).sum() / max(1e-9, v[d, a:b + 1].sum())
        rows.append(dict(side=float(s), move_atr=abs(mv) / A, last_hour=(c14 - C[d, jof(1300)]) / A * s,
                         vwap_dist=(c14 - vw) / A * s, range_atr=(np.nanmax(g.h[d, a:b + 1]) - np.nanmin(g.l[d, a:b + 1])) / A,
                         gap_atr=(o830 - prevc) / A * s, afternoon_share=abs(c14 - C[d, jof(1100)]) / max(1e-9, abs(mv))))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    t = load_mc(g, REP).sort_values(["day", "j0"]).reset_index(drop=True)
    _, Xd = vb_features(g, t.copy())                    # daily block (+ VB columns we drop)
    Xd = Xd[["ret1", "ret5", "ret20", "rth1", "atr_ratio", "dist50", "rv5_rv20", "dow0", "dow1", "dow2", "dow3", "dow4", "tdm3", "opex_wk"]]
    X = pd.concat([Xd.reset_index(drop=True), signal_features(g, t)], axis=1); X = X.fillna(X.median())
    from funded_lab import with_slippage
    y = with_slippage(t).pipe(lambda u: (u.exit - u.entry) * u.side * 20 - 7.25); yr = pd.DatetimeIndex(t.date).year
    pred = pd.Series(np.nan, index=t.index); W = {}
    for Y in range(2019, 2027):
        trn, tst = yr < Y, yr == Y
        mu, sd = X[trn].mean(), X[trn].std().replace(0, 1)
        A = ((X[trn] - mu) / sd).to_numpy(); b = y[trn].to_numpy(); lo, hi = np.percentile(b, [2, 98]); b = np.clip(b, lo, hi); bm = b.mean(); b = b - bm
        w = np.linalg.solve(A.T @ A + LAM * len(b) / 100 * np.eye(A.shape[1]), A.T @ b)
        pred[tst] = bm + ((X[tst] - mu) / sd).to_numpy() @ w; W[Y] = pd.Series(w, index=X.columns)
    oos = yr >= 2019; keep = pred >= 0
    k, s = y[oos & keep], y[oos & ~keep]
    print(f"\nOut of sample 2019-26: {oos.sum()} trades, kept {len(k)} ({len(k) / oos.sum():.0%}) avg ${k.mean():.0f} (t {tstat(k):.1f}) | "
          f"skipped {len(s)} avg ${s.mean():.0f} (t {tstat(s):.1f}) | kept - skipped t {tdiff(k, s):+.2f}; IC {np.corrcoef(pred[oos], y[oos])[0, 1]:+.3f}")
    for sd_, nm in ((1, "longs"), (-1, "shorts")):
        mk = oos & (t.side == sd_)
        print(f"   {nm}: kept ${y[mk & keep].mean():.0f} (n {int((mk & keep).sum())}) vs skipped ${y[mk & ~keep].mean():.0f} (n {int((mk & ~keep).sum())}), t {tdiff(y[mk & keep], y[mk & ~keep]):+.2f}")
    by = pd.DataFrame({"kept": y[oos & keep].groupby(yr[oos & keep]).mean(), "skipped": y[oos & ~keep].groupby(yr[oos & ~keep]).mean(),
                       "n_skip": (oos & ~keep).groupby(yr).sum()[lambda z: z.index >= 2019]})
    print("   by year ($ a trade):\n" + by.round(0).to_string()); print(f"   kept beats skipped in {(by.kept > by.skipped).sum()}/{len(by)} years")
    q = pred[oos].groupby(yr[oos]).transform(lambda p: p.rank(pct=True)); bot = q <= 1 / 3
    print(f"   secondary (skip the bottom third per year): kept ${y[oos][~bot].mean():.0f} vs skipped ${y[oos][bot].mean():.0f}, t {tdiff(y[oos][~bot], y[oos][bot]):+.2f}")
    rng = np.random.default_rng(1); gain = y[oos & keep].sum() - y[oos].sum(); pl = []
    yo, so = y[oos].to_numpy(), (~keep[oos]).to_numpy(); yro = yr[oos]
    for _ in range(2000):
        m = np.zeros(len(yo), bool)
        for Y in np.unique(yro):
            ix = np.where(yro == Y)[0]; m[rng.choice(ix, so[yro == Y].sum(), replace=False)] = True
        pl.append(-yo[m].sum())
    pl = np.array(pl); print(f"   P&L change from skipping: ${gain:,.0f} per NQ; random skips p50 ${np.median(pl):,.0f}, p95 ${np.percentile(pl, 95):,.0f}; P(random >= filter) {np.mean(pl >= gain):.3f}")
    print("\n   latest weights ($ per trade per 1 sd):\n   " + W[2026].sort_values(key=abs, ascending=False).round(1).head(10).to_string().replace("\n", "\n   "))
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    dates = pd.DatetimeIndex(g.ts[lab.tr]); S = pd.read_pickle(SP + "single_print_sessions.pkl")
    flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag; lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    cols = ["day", "j0", "j1", "side", "entry", "exit", "kind"]
    lab.add("LDF_K", t[keep | (yr < 2019)][cols].reset_index(drop=True)); lab.add("LDF_A", t[cols])
    rest = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    print("\nFunded bench (cushion sizing, full from $1,500):")
    for nm, p in (("plan, LDF as now (2 MNQ)", {**rest, "LDF_A": 2}), ("plan, LDF meta-labelled (2)", {**rest, "LDF_K": 2}),
                  ("plan, LDF meta-labelled 3", {**rest, "LDF_K": 3})):
        a, c = lab.score(p, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(p, 500, fmin=0.5, fmax=1.0, ref=1500.0)
        print(f"   {nm:<32} 1y ${a['expected']:,.0f} blown {a['blown']:.0%} | 2y ${c['expected']:,.0f} blown {c['blown']:.0%}")
