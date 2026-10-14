"""Market Intraday Momentum (Gao, Han, Li & Zhou 2018 JFE, SSRN 2440866; user's upload 2026-10-14) on NQ and ES.

Paper (SPY 1993-2013): r1 = previous 16:00 ET close -> 10:00 ET predicts r13 = 15:30 -> 16:00 ET (R2 1.6%, t 4.1),
r12 = 15:00 -> 15:30 adds to it; timing (long / short the last half-hour by the sign of r1) 6.7% a year, Sharpe 1.08;
stronger on volatile days, high volume, recessions, news days (FOMC minutes R2 11%).
In CT: r1 = previous 15:00 close -> 9:00, r12 = 14:00 -> 14:30, r13 = 14:30 -> 15:00. Our Late-Day Flow already trades
14:00 -> 14:30 after a big 8:30 -> 14:00 move, so the overlap matters.
  1. Regressions r13 on r1, r12, both (and r1 regular-session only 8:30 -> 9:00), by period; recursive out-of-sample R2.
  2. Timing trades 14:30 -> 15:00 CT, 1 NQ, $7.25 + 1 tick per fill: sign(r1); r1 & r12 agree; |r1| filters; first
     half-hour volatility terciles (known at 9:00); news days (FOMC decision days; the paper used FOMC minutes); random-side placebo; ES too.
  3. Overlap with Late-Day Flow; funded bench and speed to $13k with it added.
  python3 analysis/gao_intraday_momentum_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPLIT = pd.Timestamp("2023-01-01")
SPEC = {"NQ": (20.0, 0.25, 7.25), "ES": (50.0, 0.25, 5.0)}


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def table(g):
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    rows = g.trading; out = []
    prev = None
    for d in rows:
        b = d * 1440
        p = {k: cf[b + jof(k)] for k in (900, 1400, 1430, 1500)}
        o = g.o[d, jof(831)]
        last = g.last_j[d]
        if prev is not None and np.isfinite(o) and last >= jof(1500):
            r1m = np.diff(np.log(pd.Series(g.c[d, jof(831):jof(900) + 1]).ffill().to_numpy()))
            out.append(dict(date=pd.Timestamp(g.ts[d]), day=d, r1=p[900] / prev - 1, r1rth=p[900] / o - 1, r12=p[1430] / p[1400] - 1,
                            r13=p[1500] / p[1430] - 1, e=p[1430], x=p[1500], vol1=np.nanstd(r1m) * np.sqrt(len(r1m))))
        prev = cf[b + jof(1500)] if last >= jof(1500) else prev
    return pd.DataFrame(out).set_index("date")


def ols(y, X):
    X = np.c_[np.ones(len(X)), X]; b, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ b
    # White standard errors
    XtXi = np.linalg.inv(X.T @ X); S = X.T @ (X * (e ** 2)[:, None]); V = XtXi @ S @ XtXi
    r2 = 1 - e.var() / y.var()
    return b, b / np.sqrt(np.diag(V)), r2


def oos_r2(y, X, start):
    yh, ym = [], []
    for t in range(start, len(y)):
        Xi = np.c_[np.ones(t), X[:t]]; b, *_ = np.linalg.lstsq(Xi, y[:t], rcond=None)
        yh.append(np.r_[1, X[t]] @ b); ym.append(y[:t].mean())
    yh, ym, yt = np.array(yh), np.array(ym), y[start:]
    return 1 - ((yt - yh) ** 2).sum() / ((yt - ym) ** 2).sum()


def trades(T, side, pv, tick, comm):
    m = side != 0
    x = T[m]; s = side[m]
    net = ((x.x - x.e) * s - 2 * tick) * pv - comm
    return pd.DataFrame(dict(date=x.index, day=x.day.values, side=s.values, entry=x.e.values, exit=x.x.values, net=net.values))


def st(t):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    return dict(n=len(x), win=np.mean(x > 0), avg=x.mean(), pf=x[x > 0].sum() / max(1e-9, -x[x < 0].sum()), t=tstat(x),
                yrs=f"{(by > 0).sum()}/{len(by)}", d=x[y < 2023].mean(), h=x[y >= 2023].mean(),
                L=x[t.side > 0].mean(), S=x[t.side < 0].mean())


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); ge = pickle.load(open(SP + "ge.pkl", "rb"))
    from event_days import FOMC_DATES
    RES = {}
    for G, sym in ((g, "NQ"), (ge, "ES")):
        pv, tick, comm = SPEC[sym]
        T = table(G); T = T[T.index >= pd.Timestamp("2018-01-01")]
        print(f"\n================ {sym}: {len(T)} sessions {T.index[0].date()} .. {T.index[-1].date()}")
        print("1. Regressions of r13 (14:30 -> 15:00 CT) x 100, White t:")
        for nm, cols in (("r1", ["r1"]), ("r1 RTH only (8:30 -> 9:00)", ["r1rth"]), ("r12", ["r12"]), ("r1 + r12", ["r1", "r12"])):
            for per, m in (("2018-26", T.index >= "2018"), ("2018-22", T.index < SPLIT), ("2023-26", T.index >= SPLIT)):
                b, tt, r2 = ols(T.r13[m].values * 100, T[cols][m].values * 100)
                print(f"   {nm:<28} {per}: slopes {np.round(b[1:], 3)} t {np.round(tt[1:], 2)} R2 {r2:.2%}")
        n0 = int((T.index < pd.Timestamp("2020-01-01")).sum())
        print(f"   recursive out-of-sample R2 from 2020 (expanding window): r1 {oos_r2(T.r13.values, T[['r1']].values, n0):.2%},"
              f" r1 + r12 {oos_r2(T.r13.values, T[['r1', 'r12']].values, n0):.2%}")

        print("\n2. Timing trades 14:30 -> 15:00 CT, 1 contract after costs")
        s1 = np.sign(T.r1); s12 = np.sign(T.r12); agree = s1.where(s1 == s12, 0)
        q = T.vol1.rank(pct=True)          # terciles on the whole sample are only descriptive; also an expanding version
        qx = T.vol1.expanding(60).apply(lambda v: (v[:-1] < v[-1]).mean(), raw=True)
        big = T.r1.abs() >= T.r1.abs().expanding(60).median().shift(1)
        rng = np.random.default_rng(1)
        V = {"sign(r1) (paper)": s1, "sign(r12)": s12, "r1 and r12 agree (paper)": agree, "sign(r1 RTH 8:30-9:00)": np.sign(T.r1rth),
             "always long": pd.Series(1.0, index=T.index),
             "sign(r1), |r1| above its running median": s1.where(big, 0),
             "sign(r1), first half-hour vol top third (running)": s1.where(qx >= 2 / 3, 0),
             "sign(r1), first half-hour vol bottom third (running)": s1.where(qx < 1 / 3, 0),
             "agree, vol top third (running)": agree.where(qx >= 2 / 3, 0)}
        fomc = pd.to_datetime(FOMC_DATES)
        V["sign(r1), FOMC decision days"] = s1.where(T.index.isin(fomc), 0); V["sign(r1), other days"] = s1.where(~T.index.isin(fomc), 0)
        TT = {k: trades(T, v.fillna(0), pv, tick, comm) for k, v in V.items()}
        pl = [trades(T, pd.Series(rng.choice([-1.0, 1.0], len(T)), index=T.index), pv, tick, comm).net.mean() for _ in range(50)]
        rows = {k: st(t) for k, t in TT.items()}
        print(pd.DataFrame(rows).T.to_string(float_format=lambda v: f"{v:,.2f}"))
        print(f"   random side placebo (50 runs): ${np.mean(pl):.1f} ({np.percentile(pl, 5):.1f} .. {np.percentile(pl, 95):.1f}) a trade")
        y = TT["sign(r1) (paper)"]; print("   sign(r1) by year: " + " | ".join(f"{yy} ${v:.0f}" for yy, v in y.groupby(y.date.dt.year).net.mean().items()))
        RES[sym] = dict(T=T, TT=TT)

    # 3. overlap with Late-Day Flow, metrics, funded bench
    T, TT = RES["NQ"]["T"], RES["NQ"]["TT"]
    from time_clusters_test import trades as plan_trades
    P = plan_trades(g); ldf = P["LDF_MC"]
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= pd.Timestamp("2018-01-01")]
    dl = lambda t: t.groupby(pd.to_datetime(t.date).dt.normalize()).net.sum().reindex(days, fill_value=0.0)
    im = TT["sign(r1) (paper)"]
    ld = ldf.set_index(ldf.date.dt.normalize())
    both = im[im.date.isin(ld.index)]
    agree_ldf = both[both.side.values == ld.loc[both.date].side.values]
    print("\n3. Overlap with Late-Day Flow (LDF trades 14:00 -> 14:30 after a big 8:30 -> 14:00 move)")
    print(f"   daily P&L correlation sign(r1) vs LDF: {np.corrcoef(dl(im), dl(ldf))[0, 1]:.2f}; LDF days {len(both)} of {len(im)};"
          f" same side {len(agree_ldf) / max(1, len(both)):.0%}")
    print(f"   sign(r1) on LDF days ${both.net.mean():.0f} (same side ${agree_ldf.net.mean():.0f}), on other days ${im[~im.date.isin(ld.index)].net.mean():.0f}")
    # LDF extended: hold LDF to 15:00 when r1 agrees (the 14:30 -> 15:00 leg only)
    ext = both[both.side.values == ld.loc[both.date].side.values]
    print(f"   = holding LDF to 15:00 when r1 agrees: +${ext.net.mean():.0f} a trade on {len(ext)} trades (t {tstat(ext.net):.1f})")

    rows = {}
    for k in ("sign(r1) (paper)", "r1 and r12 agree (paper)", "sign(r1), first half-hour vol top third (running)"):
        t = TT[k]; rows[k] = (dl(t), t.net); rows[k + " longs"] = (dl(t[t.side > 0]), t[t.side > 0].net); rows[k + " shorts"] = (dl(t[t.side < 0]), t[t.side < 0].net)
    print(M.table(rows))
    b_, p_ = R.report({k: dl(TT[k])[days >= SPLIT] for k in ("sign(r1) (paper)", "r1 and r12 agree (paper)")}, n=3000); print(b_); print(p_)

    print("\n   Funded bench (7-strategy plan) + intraday momentum:")
    from bridge_monday_confirm import load_bridge_mc
    from speed_to_13k import run as speed, fmt
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    for k, nm in (("sign(r1) (paper)", "IMOM"), ("r1 and r12 agree (paper)", "IMOM_AG"), ("sign(r1), first half-hour vol top third (running)", "IMOM_HV")):
        t = TT[k].copy(); t["j0"] = jof(1431); t["j1"] = jof(1500); t["kind"] = 2; t["slips"] = 2
        lab.add(nm, t[["day", "j0", "j1", "side", "entry", "exit", "kind", "slips"]], slippage=True)
    plan = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}
    CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
    cands = {"current plan": plan, "+ IMOM 1 MNQ": {**plan, "IMOM": 1}, "+ IMOM 2 MNQ": {**plan, "IMOM": 2},
             "+ IMOM agree 2 MNQ": {**plan, "IMOM_AG": 2}, "+ IMOM high-vol 2 MNQ": {**plan, "IMOM_HV": 2}}
    sp = {}
    for nm, p in cands.items():
        a, c = lab.score(p, 250, **CS), lab.score(p, 500, **CS)
        print(f"   {nm:<26} 1y ${a['expected']:,.0f} 2y ${c['expected']:,.0f} blown {a['blown']:.0%} / {c['blown']:.0%}")
        sp[nm] = speed(lab, p, **CS)
    print(fmt(pd.DataFrame(sp).T))
    pickle.dump(RES, open(SP + "intraday_momentum.pkl", "wb"))
