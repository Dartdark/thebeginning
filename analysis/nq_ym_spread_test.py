"""NQ vs YM relative value (user's idea, 2026-10-13): trade the days they decouple (daily correlation 0.80 vs 0.93 for ES).

Spread return from the 8:30 CT open to time T: s(T) = r_NQ(T) - beta x r_YM(T), beta = 60-day rolling regression of
NQ's regular-session returns on YM's (known before the day). z = s(T) / sigma, sigma = 60-day std of the full-day
spread return (8:30 -> 15:00). Positions per 1 NQ of exposure: long / short 1 NQ, short / long q YM, q = beta x
(NQ notional / YM notional), entered at the next minute's open, out at 14:55 CT.
  Intraday: at T = 9:00 / 9:30 / 10:30 / 12:00, if |z| > 0.5 / 1.0 / 1.5: FOLLOW the spread (rotation continues)
  or FADE it.
  Overnight gap: spread from the previous 15:00 close to the 8:30 open, |z_gap| > 0.5 / 1.0 / 1.5, follow / fade
  from 8:31 to 14:55.
Costs: NQ $7.25 + 2 ticks ($10) per round trip; YM $5 + 2 ticks ($10) per contract. Single-leg versions trade only
NQ (or only YM) in the spread trade's direction for that leg. Design 2018-22, holdout 2023-26.
  python3 analysis/nq_ym_spread_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
NQ_PV, NQ_C = 20.0, 7.25 + 2 * 0.25 * 20.0
YM_PV, YM_C = 5.0, 5.0 + 2 * 1.0 * 5.0
SPLIT = pd.Timestamp("2023-01-01")


def aligned(g, gy):
    """Per common trading date: the minute grids' rows, plus daily regular-session returns and the previous close."""
    dn = {int(g.dates[d]): d for d in g.trading}; dy = {int(gy.dates[d]): d for d in gy.trading}
    common = sorted(set(dn) & set(dy)); rows = []
    cfn = pd.Series(g.c.ravel()).ffill().to_numpy(); cfy = pd.Series(gy.c.ravel()).ffill().to_numpy()
    for dt in common:
        a, b = dn[dt], dy[dt]
        on, oy = g.o[a, jof(831)], gy.o[b, jof(831)]
        cn, cy = cfn[a * 1440 + jof(1500)], cfy[b * 1440 + jof(1500)]
        if np.isnan(on) or np.isnan(oy): continue
        rows.append(dict(date=pd.Timestamp(str(dt)), a=a, b=b, on=on, oy=oy, cn=cn, cy=cy))
    D = pd.DataFrame(rows).set_index("date")
    D["rn"], D["ry"] = D.cn / D.on - 1, D.cy / D.oy - 1
    D["pcn"], D["pcy"] = D.cn.shift(1), D.cy.shift(1)
    cov = D.rn.rolling(60).cov(D.ry); var = D.ry.rolling(60).var()
    D["beta"] = (cov / var).shift(1)
    D["sig"] = (D.rn - D.beta * D.ry).rolling(60).std().shift(1)
    gap = (D.on / D.pcn - 1) - D.beta * (D.oy / D.pcy - 1)
    D["sig_gap"] = gap.rolling(60).std().shift(1); D["gap"] = gap
    return D, cfn, cfy


def run(g, gy, D, cfn, cfy, T, zmin, mode, legs="both", rand=None):
    rng = np.random.default_rng(rand) if rand is not None else None
    out = []
    for dt, r in D.iterrows():
        if dt.year < 2018 or np.isnan(r.beta) or np.isnan(r.sig): continue
        a, b = int(r.a), int(r.b)
        if T == "gap":
            z = r.gap / r.sig_gap if r.sig_gap > 0 else np.nan; j0 = jof(831)
        else:
            jt = jof(T)
            pn, py = cfn[a * 1440 + jt], cfy[b * 1440 + jt]
            z = ((pn / r.on - 1) - r.beta * (py / r.oy - 1)) / r.sig; j0 = jt + 1
        if np.isnan(z) or abs(z) < zmin: continue
        s = int(np.sign(z)) * (1 if mode == "follow" else -1)
        if rng is not None: s = int(rng.choice([-1, 1]))
        en, ey = g.o[a, j0], gy.o[b, j0]
        xn, xy = cfn[a * 1440 + jof(1455)], cfy[b * 1440 + jof(1455)]
        if np.isnan(en) or np.isnan(ey): continue
        q = r.beta * (en * NQ_PV) / (ey * YM_PV)
        pn_ = s * (xn - en) * NQ_PV - NQ_C
        py_ = -s * (xy - ey) * YM_PV * q - YM_C * q
        net = pn_ + py_ if legs == "both" else (pn_ if legs == "nq" else (-s * (xy - ey) * YM_PV - YM_C))
        out.append(dict(date=dt, side=s, z=z, q=q, net=net, nq_leg=pn_, ym_leg=py_))
    return pd.DataFrame(out)


def stats(t):
    if len(t) < 10: return dict(n=len(t), avg=np.nan, pf=np.nan, t=np.nan, d=np.nan, h=np.nan, yrs="")
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    return dict(n=len(x), avg=x.mean(), pf=x[x > 0].sum() / max(1e-9, -x[x < 0].sum()), t=x.mean() / x.std() * np.sqrt(len(x)),
                d=x[y < 2023].mean(), h=x[y >= 2023].mean(), yrs=f"{(by > 0).sum()}/{len(by)}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); gy = pickle.load(open(SP + "gy.pkl", "rb"))
    D, cfn, cfy = aligned(g, gy)
    print(__doc__.split("\n")[0])
    print(f"common sessions {len(D)}; beta median {D.beta.median():.2f} (10-90%: {D.beta.quantile(.1):.2f}-{D.beta.quantile(.9):.2f});"
          f" YM contracts per NQ median {((D.on * NQ_PV) / (D.oy * YM_PV) * D.beta).median():.2f}")
    sp = (D.rn - D.beta * D.ry).dropna()
    print(f"daily spread (8:30->15:00) autocorrelation day to day {sp.autocorr():+.3f}; std {sp.std() * 100:.2f}%")
    rows = []; T_ = {}
    for T, zmin, mode in itertools.product((900, 930, 1030, 1200, "gap"), (0.5, 1.0, 1.5), ("follow", "fade")):
        t = run(g, gy, D, cfn, cfy, T, zmin, mode); T_[(T, zmin, mode)] = t
        rows.append(dict(T=T, z=zmin, mode=mode, **stats(t)))
    G = pd.DataFrame(rows); pd.set_option("display.width", 200)
    print("\n1. Spread trades (both legs, per 1 NQ of exposure), all 30 versions sorted by design (2018-22) average:")
    print(G.sort_values("d", ascending=False).to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
    print(f"   design avg > 0: {np.mean(G.d > 0):.0%}; of those holdout > 0: {np.mean(G[G.d > 0].h > 0):.0%}; best t {G.t.max():.1f}")
    best = G.sort_values("d", ascending=False).iloc[0]
    key = (best["T"], best["z"], best["mode"]); bt = T_[key]
    print(f"\n2. Best design version {key}: legs and checks")
    print(f"   NQ leg ${bt.nq_leg.mean():.0f}, YM leg ${bt.ym_leg.mean():.0f} a trade (YM contracts per NQ {bt.q.median():.2f})")
    for legs in ("nq", "ym"):
        s_ = stats(run(g, gy, D, cfn, cfy, key[0], key[1], key[2], legs=legs))
        print(f"   single leg {legs.upper()}: n {s_['n']} avg ${s_['avg']:.0f} PF {s_['pf']:.2f} t {s_['t']:.1f} | 18-22 ${s_['d']:.0f} 23-26 ${s_['h']:.0f} yrs {s_['yrs']}")
    pl = [run(g, gy, D, cfn, cfy, key[0], key[1], key[2], rand=r).net.mean() for r in range(20)]
    print(f"   placebo (same days, random direction, 20 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs ${bt.net.mean():.0f}")
    days = D.index[D.index.year >= 2018]
    dl = lambda t: t.groupby(t.date).net.sum().reindex(days, fill_value=0.0)
    print(M.table({f"best spread {key}": (dl(bt), bt.net)}))
    b_, p_ = R.report({"2023+": dl(bt)[dl(bt).index >= SPLIT]}, n=3000); print(b_); print(p_)
    pickle.dump(dict(G=G), open(SP + "nq_ym_spread.pkl", "wb"))

    print("\n3. Is the NQ-only leg just NQ's own early momentum? (9:00, follow, out 14:55, NQ only)")
    days_sig = set(bt.date)
    rows = []
    for dt, r in D.iterrows():
        if dt.year < 2018 or np.isnan(r.beta) or np.isnan(r.sig): continue
        a, b = int(r.a), int(r.b); jt = jof(900)
        pn, py = cfn[a * 1440 + jt], cfy[b * 1440 + jt]
        rn_, ry_ = pn / r.on - 1, py / r.oy - 1
        en = g.o[a, jt + 1]; xn = cfn[a * 1440 + jof(1455)]
        if np.isnan(en): continue
        rows.append(dict(date=dt, rn=rn_, ry=ry_, z=(rn_ - r.beta * ry_) / r.sig, nq_fwd=(xn - en) * NQ_PV, sig=r.sig))
    Q = pd.DataFrame(rows)
    def res(mask, side, nm):
        x = side[mask] * Q.nq_fwd[mask] - NQ_C; y = Q.date[mask].dt.year
        print(f"   {nm:<62} n {mask.sum():4d} avg ${x.mean():5.0f} t {x.mean() / x.std() * np.sqrt(len(x)):4.1f} | 18-22 ${x[y < 2023].mean():5.0f} 23-26 ${x[y >= 2023].mean():5.0f}")
    big = Q.z.abs() >= 1.0
    res(big, np.sign(Q.z), "spread days (|z| >= 1), NQ in the spread's direction")
    res(big, np.sign(Q.rn), "same days, NQ in its OWN 8:30->9:00 direction")
    agree = np.sign(Q.z) == np.sign(Q.rn)
    print(f"   on those days the spread and NQ's own move point the same way {np.mean(agree[big]):.0%} of the time")
    res(big & ~agree, np.sign(Q.z), "  days they disagree: NQ in the spread's direction")
    q_ = Q.rn.abs().rank(pct=True) >= 1 - big.mean()
    res(q_, np.sign(Q.rn), f"control: the {big.mean():.0%} biggest NQ 8:30->9:00 moves, follow NQ")
    zr = Q.z.abs() >= 1.0
    for lo, hi in ((0.5, 1.0), (1.0, 1.5), (1.5, 9)):
        m_ = (Q.z.abs() >= lo) & (Q.z.abs() < hi)
        res(m_, np.sign(Q.z), f"   |z| {lo}-{hi}: NQ in the spread's direction")
