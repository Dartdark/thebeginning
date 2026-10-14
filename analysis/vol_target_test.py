"""Volatility targeting (Harvey, Hoyle, Korgaonkar, Rattray, Sargaison & Van Hemert 2018, SSRN 3175538) on the funded plan.

Paper: scaling exposure by 1 / recent volatility (EWMA of daily returns, 10-90 day half-life) raises the Sharpe ratio of
risk assets (equities, credit: S&P futures 0.50 -> 0.59-0.63) through the leverage effect, and for every asset class cuts
vol-of-vol, the left tail and drawdowns. Our plan: VB, Monday, LDF and the Bridge Monday are fixed MNQ counts; ONB ML,
EOS and NFP already size by risk (ATR stops).
  1. Does the plan's $ P&L per trade scale with volatility? Per strategy, average / std of net $ by the previous day's
     NQ volatility tercile (EWMA, 20-day half-life of daily close-to-close returns, known before the day).
  2. Funded bench, every start day 2018-2026 (1 and 2 years) and speed to $13k: the fixed-size strategies (or the whole
     plan) scaled by clip(target / vol, lo, hi), target = the trailing 252-day median vol (no look-ahead), half-life
     10 / 20 / 40 days, caps 0.5-1.5 / 0.67-1.33 / 0.5-1.0 (only scale down).
  python3 analysis/vol_target_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import funded_sim as F
from bridge_monday_confirm import load_bridge_mc
from time_clusters_test import trades as plan_trades
from alpha101_test import daily_bars

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
PLAN = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
FIXED = ("VB", "MON_MC", "LDF_MC", "MON_BR_MC")


def ewma_vol(r, hl):
    lam = 0.5 ** (1 / hl)
    return np.sqrt((r ** 2).ewm(alpha=1 - lam, adjust=False).mean()) * np.sqrt(252)


def run(lab, b_over, H, starts):
    names, b = lab._base(PLAN)
    for k, v in b_over.items(): b[names.index(k)] = v
    W = np.stack([lab.W[k] for k in names]); C = np.stack([lab.C[k] for k in names])
    r = F.simulate_sized(W, C, b, horizon=H, starts=starts, **CS)
    t = np.where(r["payouts"] == 6, r["days"], np.inf)
    return dict(paid=r["paid"].mean(), blown=r["blown"].mean(), all6=(r["payouts"] == 6).mean(), med6=np.median(t))


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    B = daily_bars(g); ret = np.log(B.close).diff()
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    dates = pd.DatetimeIndex(g.ts[lab.tr])
    VOL = {hl: ewma_vol(ret, hl).shift(1).reindex(dates).ffill() for hl in (10, 20, 40)}   # known before the day

    print("\n1. Net $ per trade by the previous day's NQ volatility tercile (20-day half-life EWMA), MultiCharts lists")
    T = plan_trades(g); v = VOL[20]
    q = v.rank(pct=True)
    for k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC", "MON_BR"):
        t = T[k]; vv = q.reindex(t.date.dt.normalize()).to_numpy()
        out = []
        for lo, hi, nm in ((0, 1 / 3, "low"), (1 / 3, 2 / 3, "mid"), (2 / 3, 1.01, "high")):
            x = t.net[(vv >= lo) & (vv < hi)]
            out.append(f"{nm}: n {len(x):4d} avg ${x.mean():5.0f} sd ${x.std():5.0f} avg/sd {x.mean() / x.std():5.2f}")
        print(f"   {k:<11} " + " | ".join(out))
    print(f"   NQ vol (annualized, 20-day half-life): terciles at {np.nanpercentile(v, 33):.0%} / {np.nanpercentile(v, 67):.0%}")

    rows = {}
    for H in (250, 500):
        st = np.arange(0, lab.D - H)
        res = {"current plan": run(lab, {}, H, st)}
        for hl in (10, 20, 40):
            tgt = VOL[hl].rolling(252, min_periods=120).median()
            ratio = (tgt / VOL[hl]).fillna(1.0).to_numpy()
            for lo, hi in ((0.5, 1.5), (0.67, 1.33), (0.5, 1.0)):
                s = np.clip(ratio, lo, hi)
                names, b = lab._base(PLAN)
                over = {k: b[names.index(k)] * s for k in FIXED}
                res[f"fixed-size strategies, hl {hl}, {lo:.2f}-{hi:.2f}"] = run(lab, over, H, st)
                if hl == 20:
                    over_all = {k: b[names.index(k)] * s for k in PLAN}
                    res[f"whole plan, hl {hl}, {lo:.2f}-{hi:.2f}"] = run(lab, over_all, H, st)
        df = pd.DataFrame(res).T
        print(f"\n2. Funded bench, horizon {H} trading days, every start day 2018-2026 ({len(st)} accounts)")
        print(df.to_string(formatters={"paid": "${:,.0f}".format, "blown": "{:.0%}".format, "all6": "{:.0%}".format,
                                       "med6": lambda v: f">{H}" if not np.isfinite(v) else f"{v:.0f}"}))
        rows[H] = df
    # by period for the best 1-year version
    best = rows[250].drop("current plan").paid.idxmax()
    print(f"\n   best 1-year version: {best}")
    pickle.dump(rows, open(SP + "vol_target.pkl", "wb"))
