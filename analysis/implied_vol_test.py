"""Implied volatility as the volatility unit (user's 3 resources, 2026-10-15: Cboe VIX methodology -- VIX / VXN are 30-day
annualised implied vol, daily sigma ~ VIX / sqrt(252) ~ VIX / 16; Christensen & Prabhala -- implied vol forecasts realised
vol better than history; Bekaert & Hoerova 2013 -- implied variance exceeds realised on average: the variance risk premium).
Data: data/VXN_daily.csv, data/VIX_daily.csv (Cboe, to 2026-10-14); NQ / ES 1-min, 2018-2026.
  A  forecast: today's day-session (8:30-15:00 CT) realised vol of NQ (sqrt of summed 5-min squared log returns, %) and
     range %, regressed in logs on what is known at yesterday's close: VXN/sqrt(252), the 15-day ATR as % of price, yesterday's
     realised vol, the 20-day average realised vol -- R^2 each alone and together (does implied vol subsume history?).
     Same for ES with VIX. Bias: realised close-to-close |return| and day-session vol vs implied daily sigma (the premium).
  B  Vault Break v1 exits (tp 40 / sl 75 NQ points, fixed) vs the same exits scaled per day by implied sigma in points
     (price x VXN / 100 / sqrt(252)) or by the 15-day ATR, each normalised so the 2018-26 median day keeps 40 / 75 (2
     pre-registered variants); entries unchanged; by year; standard metrics.
  python3 analysis/implied_vol_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from vault_break_v8_test import run, boundary, line
from vb_exits_maroy_test import sim
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def daily_frame(g, iv):
    r = g.trading; ts = pd.DatetimeIndex(g.ts[r]); rows = []
    J0, J1 = jof(830), jof(1500)
    for k, d in zip(r, ts):
        c = g.c[d if False else k, J0:J1 + 1]
        c = pd.Series(c).ffill().to_numpy()
        if np.isnan(c).mean() > 0.2 or np.isnan(c[0]): continue
        c5 = c[::5]; lr = np.diff(np.log(c5)); rv = np.sqrt(np.nansum(lr ** 2)) * 100
        h, l = np.nanmax(g.h[k, J0 + 1:J1 + 1]), np.nanmin(g.l[k, J0 + 1:J1 + 1])
        rows.append(dict(date=d, rv=rv, rng=(h - l) / c[0] * 100, close=c[-1]))
    D = pd.DataFrame(rows).set_index("date")
    D["cc"] = np.log(D.close).diff().abs() * 100
    atr = pd.Series(g.daily_atr(15)[r], index=ts).reindex(D.index)
    D["atrp"] = atr / D.close.shift(1) * 100
    D["iv"] = iv.reindex(D.index, method="ffill").shift(1) / np.sqrt(252)          # yesterday's close, daily sigma %
    D["rv1"] = D.rv.shift(1); D["rv20"] = D.rv.rolling(20).mean().shift(1)
    return D[D.index >= "2018-01-01"].dropna()


def r2(y, X):
    X = np.c_[np.ones(len(X)), X]; b = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ b
    return 1 - e.var() / y.var()


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    ivs = {s: pd.read_csv(f"data/{s}_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE for s in ("VXN", "VIX")}
    gs = {"NQ": pickle.load(open(SP + "g24.pkl", "rb")), "ES": pickle.load(open(SP + "ge.pkl", "rb"))}
    for sym, ivn in (("NQ", "VXN"), ("ES", "VIX")):
        D = daily_frame(gs[sym], ivs[ivn]); D = D[(D[["rv", "rng", "iv", "atrp", "rv1", "rv20"]] > 0).all(1)]; L = np.log(D[["rv", "rng", "iv", "atrp", "rv1", "rv20"]])
        print(f"\nA. {sym} with {ivn} ({len(D)} days): R^2 of log day-session realised vol / range on log predictors")
        for tgt in ("rv", "rng"):
            out = {nm: r2(L[tgt].values, L[cols].values) for nm, cols in (("implied", ["iv"]), ("ATR15", ["atrp"]), ("yesterday RV", ["rv1"]),
                   ("20-day RV", ["rv20"]), ("history (ATR+RV1+RV20)", ["atrp", "rv1", "rv20"]), ("implied + history", ["iv", "atrp", "rv1", "rv20"]))}
            print(f"   {tgt:<4} " + "  ".join(f"{k} {v:.3f}" for k, v in out.items()))
        for nm, m in (("2018-22", D.index.year < 2023), ("2023-26", D.index.year >= 2023)):
            Ls = L[m]; print(f"   {nm}: rv ~ implied {r2(Ls.rv.values, Ls[['iv']].values):.3f}, ~ history {r2(Ls.rv.values, Ls[['atrp', 'rv1', 'rv20']].values):.3f}, ~ both {r2(Ls.rv.values, Ls[['iv', 'atrp', 'rv1', 'rv20']].values):.3f}")
        print(f"   bias: mean |close-to-close| / implied sigma {(D.cc / D.iv).mean():.2f} (|N(0,1)| would be 0.80); day-session RV / implied {(D.rv / D.iv).median():.2f} (median);"
              f" implied > realised close-to-close sd: {(D.iv.mean() > D.cc.std() ) } ({D.iv.mean():.2f}% vs {np.log(D.close).diff().std() * 100:.2f}%)")
    print("\nB. Vault Break v1 exits: fixed 40 / 75 points vs scaled by implied sigma / ATR (median day keeps 40 / 75)")
    g = gs["NQ"]; ent = run(g, "v1"); Bd = boundary(g, "tr")
    px = pd.Series(pd.Series(g.c.ravel()).ffill().to_numpy().reshape(g.c.shape)[:, jof(830)], index=pd.DatetimeIndex(g.ts))
    ivd = ivs["VXN"].reindex(px.index, method="ffill").shift(1)
    sig_pts = (px.shift(1).ffill() * ivd / 100 / np.sqrt(252)).to_numpy()
    atr = g.daily_atr(15)
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]).year >= 2018]
    m_sig, m_atr = np.nanmedian(sig_pts[tr]), np.nanmedian(atr[tr])
    print(f"   median implied sigma {m_sig:.0f} pts, median ATR {m_atr:.0f} pts")
    res = {"fixed 40 / 75": sim(g, ent, Bd, dict(kind="base", sl=75.0, tp=40.0)),
           "implied-sigma scaled": sim(g, ent, Bd, dict(kind="base", sl=np.nan_to_num(75 * sig_pts / m_sig, nan=75.0), tp=np.nan_to_num(40 * sig_pts / m_sig, nan=40.0))),
           "ATR scaled": sim(g, ent, Bd, dict(kind="base", sl=np.nan_to_num(75 * atr / m_atr, nan=75.0), tp=np.nan_to_num(40 * atr / m_atr, nan=40.0)))}
    days = pd.bdate_range("2018-01-01", "2026-10-09"); rows = {}
    for nm, t in res.items():
        t = t[t.date >= "2018-01-01"]; print(line(t, nm, 30)); print("      by year:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
        rows[nm] = (t.groupby(t.date).net.sum().reindex(days, fill_value=0.0), t.net)
    print("\nStandard metrics per NQ (Vault Break is long only):"); print(M.table(rows))
    b_, p_ = R.report({k: v[0][v[0].index >= "2023"] for k, v in rows.items()}, n=2000); print("2023+ bootstrap:\n" + b_)
