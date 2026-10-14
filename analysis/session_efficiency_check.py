"""Session Efficiency Forecast (user's MultiCharts indicator README, 2026-10-14) vs the plan's strategies.
ER = |last close - first close| / sum |close-to-close| on 5-min bars, 8:30-15:00 CT, NQ. The indicator's logistic model
(15 features, fitted on NQ 2010-18) correlates ~0.10 with the actual ER out of sample (its own README).
  1. ceiling (look-ahead, NOT tradable): each strategy's P&L by tercile of the day's ACTUAL ER
  2. pre-day inputs of the model (yesterday's ER, the ER two days ago, the 20-day average ER): correlation with today's ER,
     and as filters through analysis/bridge_filter_scan.scan (design 2018-22, holdout 2023-26, shuffled-P&L null)
  python3 analysis/session_efficiency_check.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import bridge_filter_scan as B1

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    print(__doc__.split("\n")[0]); sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/plan_agreement_test.py", run_name="__main__")
    T = ns["T"]; T = T[T.strat.isin(["VB", "ONB_ML", "MON", "EOS", "LDF", "NFP", "BRIDGE"])].reset_index(drop=True)
    g = pickle.load(open(SP + "g24.pkl", "rb")); tr = g.trading; idx = pd.DatetimeIndex(g.ts[tr])
    c5 = pd.DataFrame(g.c[tr, jof(835):jof(1500) + 1:5]).ffill(axis=1).to_numpy()
    ok = np.isfinite(c5).all(1)
    er = np.where(ok, np.abs(c5[:, -1] - c5[:, 0]) / np.nansum(np.abs(np.diff(c5, axis=1)), 1), np.nan)
    ER = pd.Series(er, index=idx)
    pre = pd.DataFrame({"er1": ER.shift(1), "er2": ER.shift(2), "er20": ER.rolling(20).mean().shift(1)})
    print(f"NQ 5-min ER: median {ER.median():.3f}; corr with today's ER: yesterday {ER.corr(pre.er1):+.3f}, two days ago {ER.corr(pre.er2):+.3f}, 20-day avg {ER.corr(pre.er20):+.3f}")
    T["ER"] = T.date.map(ER); T = T.join(T.date.map(pre.er1).rename("er1")).join(T.date.map(pre.er2).rename("er2")).join(T.date.map(pre.er20).rename("er20"))
    print("\n1. CEILING (hindsight): average $ per trade by tercile of the day's actual ER")
    q = ER.quantile([1 / 3, 2 / 3]).values
    for s in T.strat.unique():
        x = T[T.strat == s]; b = np.digitize(x.ER, q)
        print(f"   {s:<7} choppy ${x.net[b == 0].mean():6.0f} | middle ${x.net[b == 1].mean():6.0f} | trending ${x.net[b == 2].mean():6.0f}  (n {len(x)})")
    F = T[["er1", "er2", "er20"]].copy(); B1.FEATS, B1.UNSIGNED = ["er1", "er2", "er20"], {"er1", "er2", "er20"}
    R = B1.scan(T, F, T.net.to_numpy()); pd.set_option("display.width", 200)
    print(f"\n2. pre-day ER inputs as filters: {len(R)} tests, PASS {int(R.PASS.sum())}")
    print(R.sort_values("t_design", key=abs, ascending=False).head(8).round(2).to_string(index=False))
    rng = np.random.default_rng(1); null = []
    for _ in range(200):
        y = T.net.to_numpy().copy()
        for s in T.strat.unique():
            m = (T.strat == s).to_numpy(); y[m] = rng.permutation(y[m])
        null.append(int(B1.scan(T, F, y).PASS.sum()))
    print(f"   null: passes mean {np.mean(null):.2f}, P(>= real) {np.mean(np.array(null) >= R.PASS.sum()):.2f}")
