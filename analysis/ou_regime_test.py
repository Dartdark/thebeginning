"""Ornstein-Uhlenbeck mean-reversion regime (user's post, 2026-10-15: OU theta / half-life of price vs a 50-bar VWAP as a regime
filter for mean-reversion entries; cites Jashnani 2025, OU filter + Bollinger Bands on S&P 500 stocks 2010-24).

Here, NQ and ES, 2018-2026, 5-minute bars of the 8:30-15:00 CT session (78 a day), sessions chained:
  x_t   = log(close) - log(VWAP50), VWAP50 = 50-bar rolling volume-weighted typical price
  OU    = AR(1) fit x_t = a + b x_{t-1}: theta = -ln b (per bar), half-life = ln 2 / theta
  regime, known before the session: theta fitted on the PREVIOUS 20 sessions; 'MR regime' = that theta above its own 120-day
          average (the post's rolling threshold); also quintiles
  A  is it a regime at all? corr(theta prior 20 sessions, theta of the session itself)
  B  the trade it is meant to filter: z = x / sd(x, previous 20 sessions); at a 5-min close 9:00-14:30, |z| >= 2 -> fade at that
     close (+1 tick), out when z crosses 0, at |z| >= 4 (stop) or 15:00 (each at the bar close, 1 tick); one position at a time.
     Costs NQ $7.25, ES $5 + the ticks. All signals vs MR-regime vs trend-regime days; quintiles; design 2018-22 / holdout 2023-26
  C  the plan's NQ trades (MultiCharts lists) by regime: breakouts (VB, ONB ML) should do better in the trend regime
  python3 analysis/ou_regime_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"NQ": ("g24.pkl", 20.0, 0.25, 7.25), "ES": ("ge.pkl", 50.0, 0.25, 5.0)}


def bars5(g):
    j0 = jof(831); n = 78; rows, out = [], []
    for r in g.trading:
        c = g.c[r, j0:j0 + 5 * n]; h = g.h[r, j0:j0 + 5 * n]; l = g.l[r, j0:j0 + 5 * n]; v = g.v[r, j0:j0 + 5 * n]
        if np.isnan(c).mean() > 0.05 or np.isnan(c[-1]): continue
        c = pd.Series(c).ffill().bfill().to_numpy(); h = np.where(np.isnan(h), c, h); l = np.where(np.isnan(l), c, l)
        v = np.nan_to_num(v)
        C = c.reshape(n, 5)[:, -1]; H = h.reshape(n, 5).max(1); L = l.reshape(n, 5).min(1); V = v.reshape(n, 5).sum(1)
        rows.append(pd.Timestamp(g.ts[r])); out.append(np.c_[C, H, L, V])
    return pd.DatetimeIndex(rows), np.stack(out)          # days x 78 x 4


def ar1(x):
    x0, x1 = x[:-1], x[1:]; ok = ~np.isnan(x0) & ~np.isnan(x1)
    if ok.sum() < 30: return np.nan
    b = np.polyfit(x0[ok], x1[ok], 1)[0]
    return -np.log(b) if 0 < b < 1 else np.nan


def build(sym):
    g = pickle.load(open(SP + SPEC[sym][0], "rb"))
    days, B = bars5(g); keep = days >= "2017-06-01"; days, B = days[keep], B[keep]
    C, H, L, V = (B[:, :, k].ravel() for k in range(4))
    tp = (C + H + L) / 3; pv = pd.Series(tp * V).rolling(50).sum(); vv = pd.Series(V).rolling(50).sum()
    x = (np.log(C) - np.log(pv / vv)).to_numpy().reshape(len(days), 78)
    th_day = np.array([ar1(x[i]) for i in range(len(days))])
    th20 = np.full(len(days), np.nan); sd20 = np.full(len(days), np.nan)
    for i in range(20, len(days)):
        w = x[i - 20:i].ravel(); th20[i] = ar1(w); sd20[i] = np.nanstd(w)
    D = pd.DataFrame({"th_day": th_day, "th20": th20, "sd20": sd20}, index=days)
    D["th_avg"] = D.th20.rolling(120).mean(); D["mr"] = D.th20 > D.th_avg
    D["hl20"] = np.log(2) / D.th20
    return g, days, B, x, D


def mr_trades(sym, B, x, D):
    pv, tick, comm = SPEC[sym][1:]; C = B[:, :, 0]; out = []
    j_first, j_last = (900 - 830) // 5 - 1, (1430 - 830) // 5 - 1          # bar index of the 9:00 / 14:30 closes
    for i in range(len(D)):
        if np.isnan(D.sd20.iloc[i]) or np.isnan(D.th_avg.iloc[i]): continue
        z = x[i] / D.sd20.iloc[i]; pos = 0
        for j in range(77):
            if pos == 0 and j_first <= j <= j_last and abs(z[j]) >= 2:
                pos = -np.sign(z[j]); e = C[i, j] + pos * tick; j_in = j; continue
            if pos != 0 and j > j_in and (np.sign(z[j]) == pos or abs(z[j]) >= 4):
                out.append(dict(date=D.index[i], side=pos, net=(C[i, j] - pos * tick - e) * pos * pv - comm)); pos = 0
        if pos != 0: out.append(dict(date=D.index[i], side=pos, net=(C[i, 77] - pos * tick - e) * pos * pv - comm))
    return pd.DataFrame(out)


def ln(x, nm, w=34):
    x = pd.Series(x).dropna(); y = x.index.year if isinstance(x.index, pd.DatetimeIndex) else None
    t = x.mean() / x.std() * np.sqrt(len(x)); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    s = f"   {nm:<{w}} n {len(x):5d} avg ${x.mean():6.1f} PF {pf:4.2f} t {t:5.1f}"
    return s + (f" | 2018-22 ${x[y < 2023].mean():6.1f} 2023-26 ${x[y >= 2023].mean():6.1f}" if y is not None else "")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    keepD = {}
    for sym in ("NQ", "ES"):
        g, days, B, x, D = build(sym); keepD[sym] = D
        d = D[D.index >= "2018-01-01"].dropna()
        print(f"\n{sym}: {len(d)} sessions; half-life (prior 20 sessions) median {d.hl20.median():.1f} bars "
              f"(5-95%: {d.hl20.quantile(.05):.1f}-{d.hl20.quantile(.95):.1f}); MR-regime share {d.mr.mean():.0%}")
        print(f"   A. corr(theta prior 20, theta today) {d.th20.corr(d.th_day):+.3f}; rank {d.th20.rank().corr(d.th_day.rank()):+.3f}; "
              f"MR-regime days' own theta {d[d.mr].th_day.median():.4f} vs trend-regime {d[~d.mr].th_day.median():.4f}")
        T = mr_trades(sym, B, x, D); T = T[T.date >= "2018-01-01"].set_index("date")
        mr = D.mr.reindex(T.index).astype(bool)
        print("   B. VWAP50 z-score fade (|z| >= 2 -> z = 0, stop |z| 4, out 15:00)")
        print(ln(T.net, "all signals")); print(ln(T.net[mr], "MR regime (theta > 120-day avg)")); print(ln(T.net[~mr], "trend regime"))
        q = pd.qcut(D.th20.reindex(T.index), 5, labels=False)
        print("      avg $ by theta quintile (0 = slowest reversion):", T.net.groupby(q).mean().round(1).to_dict(),
              "| trades", T.net.groupby(q).size().to_dict())
        a, b = T.net[mr], T.net[~mr]
        print(f"      MR - trend: ${a.mean() - b.mean():+.1f}, t {(a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)):+.2f}")
        if sym == "ES":
            x_ = T.net[mr]; days_ = pd.Series(0.0, index=D.index[D.index >= "2018-01-01"])
            rows = {"MR regime all": (days_.add(x_.groupby(level=0).sum(), fill_value=0), x_)}
            for nm, s_ in (("longs", 1), ("shorts", -1)):
                xs = T.net[mr & (T.side == s_)]; rows[nm] = (days_.add(xs.groupby(level=0).sum(), fill_value=0), xs)
            print("\n   ES fade in the MR regime, standard metrics (per ES):"); print(M.table(rows))
            b_, p_ = R.report({k: v[0][v[0].index >= "2023"] for k, v in rows.items()}, n=2000)
            print("2023+ bootstrap:\n" + b_ + "\n2023+ drawdown permutation:\n" + p_)

    print("\nC. Plan NQ trades by NQ OU regime (known at the prior close)")
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        T = runpy.run_path("analysis/plan_agreement_test.py", run_name="__main__")["T"]
    D = keepD["NQ"]; pos = np.searchsorted(D.index, T.date); ok = pos < len(D)
    T = T[ok].copy(); T["mr"] = D.mr.to_numpy()[pos[ok]]; T["th"] = D.th20.to_numpy()[pos[ok]]; T = T.dropna(subset=["th"])
    rows = []
    for s_, x_ in T.groupby("strat"):
        a, b = x_[x_.mr == True].net, x_[x_.mr == False].net
        if len(a) < 5 or len(b) < 5: continue
        dd = lambda m: x_[m & (x_.mr == True)].net.mean() - x_[m & (x_.mr == False)].net.mean()
        rows.append(dict(strat=s_, n_mr=len(a), n_trend=len(b), mr=a.mean(), trend=b.mean(),
                         t=(a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)),
                         design=dd(x_.date.dt.year < 2023), holdout=dd(x_.date.dt.year >= 2023)))
    print(pd.DataFrame(rows).round(1).to_string(index=False))
