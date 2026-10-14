"""'Beta from A to Z' (Oct 2026 textbook, user's upload 2026-10-14): its pairs-trading tools on NQ vs ES and NQ vs YM.

The book proves the estimators and gives no trading results. Its pairs recipe (ch. 16, 21-23): a Kalman-filter hedge ratio
(the innovation / sqrt(F) is a ready z-score), cointegration for the long-run equilibrium, and the short-run vs long-run
beta (ch. 13 / 22: if one leg over-reacts, the 1-period beta exceeds the long-run one and the spread reverts).
  1. Facts: NQ's beta on ES / YM at 1, 5, 15, 30, 60 minutes, the regular session, daily, 5 and 20 days; overnight vs
     regular-session beta (ch. 13.9); the Engle-Granger cointegration test and spread half-life (ch. 22).
  2. Kalman beta (daily regular-session returns, q chosen by maximum likelihood on 2018-22 only) for the intraday
     spread: z at 9:00 / 10:30 / 12:00 = (r_NQ - beta r_X) / sqrt(F), follow or fade to 14:55, both legs.
  3. Multi-day reversion (Apex-legal, flat every day): rolling 250-day cointegration residual of the 15:00 log prices,
     z at yesterday's close; |z| > 1 / 1.5 / 2: fade the spread today 8:31 -> 14:55, both legs or the NQ leg alone.
Costs per round trip: NQ $7.25 + 2 ticks ($17.25), ES $5 + 2 ticks ($30), YM $5 + 2 ticks ($15). Per 1 NQ of exposure; the
hedge leg holds beta x notional ratio contracts (fractional = micros). Design 2018-22, holdout 2023-26.
  python3 analysis/beta_pairs_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from nq_ym_spread_test import aligned
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
NQ_PV, NQ_C = 20.0, 7.25 + 2 * 0.25 * 20.0
SPEC = {"ES": (50.0, 5.0 + 2 * 0.25 * 50.0), "YM": (5.0, 5.0 + 2 * 1.0 * 5.0)}
SPLIT = pd.Timestamp("2023-01-01")


def horizon_betas(g, gx, D):
    """NQ on X: beta = cov / var at several sampling intervals (regular session 8:30-15:00 for intraday)."""
    out = {}
    rows_n, rows_x = D.a.values.astype(int), D.b.values.astype(int)
    for k in (1, 5, 15, 30, 60):
        j = np.arange(jof(830), jof(1500) + 1, k)
        cn = pd.DataFrame(g.c[rows_n][:, j]).ffill(axis=1).to_numpy(); cx = pd.DataFrame(gx.c[rows_x][:, j]).ffill(axis=1).to_numpy()
        y, x = np.diff(np.log(cn), axis=1).ravel(), np.diff(np.log(cx), axis=1).ravel()
        m = np.isfinite(y) & np.isfinite(x); out[f"{k}m"] = np.cov(y[m], x[m])[0, 1] / np.var(x[m], ddof=1)
    out["RTH day"] = D.rn.cov(D.ry) / D.ry.var()
    lc_n, lc_x = np.log(D.cn), np.log(D.cx)
    for h in (1, 5, 20):
        y, x = lc_n.diff(h).iloc[::h].dropna(), lc_x.diff(h).iloc[::h].dropna()
        out[f"{h}d close"] = y.cov(x) / x.var()
    on_n, on_x = np.log(D.on / D.pcn), np.log(D.ox / D.pcx)
    out["overnight"] = on_n.cov(on_x) / on_x.var()
    out["corr RTH"] = D.rn.corr(D.ry); out["corr overnight"] = on_n.corr(on_x)
    return out


def kalman(y, x, q, r=None):
    """beta_t random walk + alpha random walk (q x R each), y = a + b x + e. Returns predicted a, b, F (known before t)."""
    n = len(y); R_ = np.nanvar(y) * 0.2 if r is None else r
    b = np.array([0.0, 1.0]); P = np.eye(2) * 1.0; Q = np.diag([q * R_ * 1e-2, q * R_ / max(np.nanvar(x), 1e-12)])
    A, B, F, ll = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan), 0.0
    for t in range(n):
        P = P + Q
        h = np.array([1.0, x[t]])
        A[t], B[t] = b; F[t] = h @ P @ h + R_
        if np.isfinite(y[t]) and np.isfinite(x[t]):
            v = y[t] - h @ b; K = P @ h / F[t]
            b = b + K * v; P = P - np.outer(K, h) @ P
            if t > 20: ll += -0.5 * (np.log(2 * np.pi * F[t]) + v * v / F[t])
    return A, B, F, ll


def fit_kalman(D, design):
    y, x = D.rn.to_numpy(), D.ry.to_numpy()
    nd = int(design.sum()); best = None
    for q in (1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2):
        for rf in (0.05, 0.1, 0.2, 0.4):
            r_ = np.nanvar(y[:nd]) * rf
            ll = kalman(y[:nd], x[:nd], q, r_)[3]
            if best is None or ll > best[0]: best = (ll, q, r_)
    A, B, F, _ = kalman(y, x, best[1], best[2])
    return A, B, F, best


def pair_trade(g, gx, D, i_dates, side, jin, pv, cost, beta, legs="both"):
    """side +1 = long NQ / short beta x X, from minute jin to 14:55."""
    cfn = pd.Series(g.c.ravel()).ffill().to_numpy(); cfx = pd.Series(gx.c.ravel()).ffill().to_numpy()
    out = []
    for dt, s, bt in zip(i_dates, side, beta):
        r = D.loc[dt]; a, b = int(r.a), int(r.b)
        en, ex = g.o[a, jin], gx.o[b, jin]
        xn, xx = cfn[a * 1440 + jof(1455)], cfx[b * 1440 + jof(1455)]
        if np.isnan(en) or np.isnan(ex): continue
        q = bt * (en * NQ_PV) / (ex * pv)
        nq = s * (xn - en) * NQ_PV - NQ_C
        hx = -s * (xx - ex) * pv * q - cost * abs(q)
        out.append(dict(date=dt, side=s, net=nq + hx if legs == "both" else nq, nq=nq, hx=hx, q=q))
    return pd.DataFrame(out)


def stats(t):
    if len(t) < 15: return dict(n=len(t), avg=np.nan, pf=np.nan, t=np.nan, d=np.nan, h=np.nan, yrs="")
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    return dict(n=len(x), avg=x.mean(), pf=x[x > 0].sum() / max(1e-9, -x[x < 0].sum()), t=x.mean() / x.std() * np.sqrt(len(x)),
                d=x[y < 2023].mean(), h=x[y >= 2023].mean(), yrs=f"{(by > 0).sum()}/{len(by)}")


def adf_t(s):
    """Engle-Granger step 2: t of phi in d s = phi s(-1) + c d s(-1)."""
    s = pd.Series(s).dropna(); ds = s.diff(); X = pd.concat([s.shift(1), ds.shift(1)], axis=1).dropna(); yv = ds.loc[X.index]
    Xv = np.c_[np.ones(len(X)), X.values]; bh, *_ = np.linalg.lstsq(Xv, yv.values, rcond=None)
    e = yv.values - Xv @ bh; s2 = e @ e / (len(e) - 3); cov = s2 * np.linalg.inv(Xv.T @ Xv)
    return bh[1] / np.sqrt(cov[1, 1]), bh[1]


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    print(__doc__.split("\n")[0])
    ALL = {}
    for X in ("ES", "YM"):
        gx = pickle.load(open(SP + ("ge.pkl" if X == "ES" else "gy.pkl"), "rb")); pv, cost = SPEC[X]
        D, cfn, cfy = aligned(g, gx); D = D[D.index >= pd.Timestamp("2018-01-01")]
        D = D.rename(columns={"oy": "ox", "cy": "cx", "pcy": "pcx"})
        print(f"\n================ NQ vs {X} ({len(D)} sessions)")
        hb = horizon_betas(g, gx, D)
        print("1. beta of NQ on", X, "by sampling interval:", {k: round(v, 2) for k, v in hb.items()})
        lp_n, lp_x = np.log(D.cn), np.log(D.cx)
        Xv = np.c_[np.ones(len(D)), lp_x]; gam = np.linalg.lstsq(Xv, lp_n.values, rcond=None)[0]
        res = lp_n - Xv @ gam; tt, phi = adf_t(res)
        hl = np.log(0.5) / np.log(1 + phi) if phi < 0 else np.inf
        print(f"   cointegration 2018-26 (whole sample, descriptive): gamma {gam[1]:.2f}, ADF t {tt:.2f} (5% critical ~ -3.34), half-life {hl:.0f} sessions")
        for y0, y1 in ((2018, 2020), (2021, 2023), (2024, 2026)):
            m = (D.index.year >= y0) & (D.index.year <= y1)
            Xm = np.c_[np.ones(m.sum()), lp_x[m]]; gm = np.linalg.lstsq(Xm, lp_n[m].values, rcond=None)[0]
            tm, pm = adf_t(lp_n[m] - Xm @ gm)
            print(f"      {y0}-{y1}: gamma {gm[1]:.2f}, ADF t {tm:.2f}, half-life {np.log(0.5) / np.log(1 + pm) if pm < 0 else np.inf:.0f}")

        # 2. Kalman beta, intraday spread
        design = D.index < SPLIT
        A, B, F, best = fit_kalman(D, design)
        print(f"\n2. Kalman (ML on 2018-22): q {best[1]:g}, R = {best[2]:.2e}; beta median {np.nanmedian(B):.2f} (10-90% {np.nanpercentile(B[60:], 10):.2f}-{np.nanpercentile(B[60:], 90):.2f})")
        rows = []; T_ = {}
        for T, zmin, mode in itertools.product((900, 1030, 1200), (0.25, 0.5, 1.0), ("follow", "fade")):
            jt = jof(T); dates, sides, betas = [], [], []
            for i, (dt, r) in enumerate(D.iterrows()):
                if i < 60: continue
                a, b = int(r.a), int(r.b)
                pn, px = cfn[a * 1440 + jt], cfy[b * 1440 + jt]
                s = (pn / r.on - 1) - A[i] - B[i] * (px / r.ox - 1)
                z = s / np.sqrt(F[i])
                if not np.isfinite(z) or abs(z) < zmin: continue
                dates.append(dt); sides.append(int(np.sign(z)) * (1 if mode == "follow" else -1)); betas.append(B[i])
            t = pair_trade(g, gx, D, dates, sides, jt + 1, pv, cost, betas); T_[(T, zmin, mode)] = t
            rows.append(dict(T=T, z=zmin, mode=mode, **stats(t)))
        G = pd.DataFrame(rows)
        print("   intraday spread with the Kalman hedge (both legs), sorted by 2018-22 average:")
        print(G.sort_values("d", ascending=False).to_string(index=False, float_format=lambda v: f"{v:,.2f}"))

        # 3. multi-day cointegration reversion
        print("\n3. Multi-day reversion: rolling 250-day cointegration residual at yesterday's 15:00 close, fade today 8:31 -> 14:55")
        W = 250; zs = np.full(len(D), np.nan); gs = np.full(len(D), np.nan); hls = []
        ln, lx = lp_n.values, lp_x.values
        for i in range(W + 1, len(D)):
            sl = slice(i - 1 - W, i - 1 + 1)       # window ends at yesterday (i-1)
            Xw = np.c_[np.ones(W + 1), lx[sl]]; gw = np.linalg.lstsq(Xw, ln[sl], rcond=None)[0]
            e = ln[sl] - Xw @ gw
            zs[i] = e[-1] / e.std(); gs[i] = gw[1]
        D["zc"] = zs; D["gam"] = gs
        rows = []; T3 = {}
        for zmin, legs in itertools.product((1.0, 1.5, 2.0), ("both", "nq")):
            m = D.zc.abs() >= zmin
            t = pair_trade(g, gx, D, D.index[m], (-np.sign(D.zc[m])).astype(int).tolist(), jof(831), pv, cost, D.gam[m].tolist(), legs=legs)
            T3[(zmin, legs)] = t; rows.append(dict(z=zmin, legs=legs, **stats(t)))
            # follow (placebo-ish opposite)
            t2 = pair_trade(g, gx, D, D.index[m], np.sign(D.zc[m]).astype(int).tolist(), jof(831), pv, cost, D.gam[m].tolist(), legs=legs)
            rows.append(dict(z=zmin, legs=legs + " (follow)", **stats(t2)))
        print(pd.DataFrame(rows).to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
        ac = D.zc.dropna(); print(f"   residual z: {np.mean(ac.abs() >= 1):.0%} of days |z| >= 1, {np.mean(ac.abs() >= 2):.0%} >= 2; day-to-day autocorrelation {ac.autocorr():.3f}")
        # does the spread revert over the next day / 5 / 20 days from |z| >= 2?
        for h in (1, 5, 20):
            fwd = (lp_n.shift(-h) - lp_n) - D.gam * (lp_x.shift(-h) - lp_x)     # today's hedge ratio held h sessions
            m = D.zc.abs() >= 2
            print(f"   from |z| >= 2: spread change over the next {h:2d} sessions in the fade direction {(-np.sign(D.zc[m]) * fwd[m]).mean() * 1e4:6.1f} bp (all days {(-np.sign(D.zc) * fwd).mean() * 1e4:5.1f} bp)")
        ALL[X] = dict(G=G, T_=T_, T3=T3, hb=hb, D=D)

    # metrics for the best of each family (by design average), both pairs
    print("\n=== Standard metrics (per 1 NQ of exposure): best design version of each family")
    rows = {}; hold = {}
    for X, r in ALL.items():
        G = r["G"]; k = G.sort_values("d", ascending=False).iloc[0]; t = r["T_"][(k["T"], k["z"], k["mode"])]
        D = r["D"]; days = D.index
        dl = lambda t_: t_.groupby(t_.date).net.sum().reindex(days, fill_value=0.0)
        nm = f"{X} Kalman intraday {k['T']} z{k['z']} {k['mode']}"
        rows[nm] = (dl(t), t.net); rows[nm + " long NQ"] = (dl(t[t.side > 0]), t[t.side > 0].net); rows[nm + " short NQ"] = (dl(t[t.side < 0]), t[t.side < 0].net)
        hold[nm] = dl(t)[days >= SPLIT]
        best3 = max(((kk, stats(v)) for kk, v in r["T3"].items()), key=lambda z: z[1]["d"] if np.isfinite(z[1]["d"]) else -1e9)
        t = r["T3"][best3[0]]; nm = f"{X} multi-day fade z{best3[0][0]} {best3[0][1]}"
        rows[nm] = (dl(t), t.net); rows[nm + " long NQ"] = (dl(t[t.side > 0]), t[t.side > 0].net); rows[nm + " short NQ"] = (dl(t[t.side < 0]), t[t.side < 0].net)
        hold[nm] = dl(t)[days >= SPLIT]
    print(M.table(rows))
    b_, p_ = R.report(hold, n=3000); print(b_); print(p_)
    pickle.dump({X: dict(G=r["G"], hb=r["hb"]) for X, r in ALL.items()}, open(SP + "beta_pairs.pkl", "wb"))
