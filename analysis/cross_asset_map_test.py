"""Cross-asset co-movement map: when do NQ, ES, YM, gold, oil and bitcoin move together, and do the breaks or
leads say anything about NQ? (user's idea, 2026-10-14)

Data: 1-minute bars, Central time: NQ (g24), ES, YM, GC, CL, BTC (CME futures), 2018-2026 (BTC from Dec 2018).
  A. Map. Each session's correlation of 5-minute returns with NQ, 8:30-15:00, for each market: by year, and by day
     type (FOMC decision days, 7:30 data-release days, NFP, monthly options expiry, month-end, Mondays, Fridays, VIX
     terciles from the previous close, and - descriptive only - the biggest NQ days).
  B. Lead-lag. Pooled 1- and 5-minute returns: corr(NQ now, market X k minutes earlier) for k = 1, 2, 3, 5, 10;
     NQ's own lag as the reference; 2018-22 vs 2023-26. Anything above ~0.03 at 1 minute is checked as a trade.
  C. Event reactions. On 7:30 data days and FOMC days (13:00 CT statement): does gold's / oil's / bitcoin's / ES's
     first-15-minute reaction, or its agreement with NQ's own reaction, predict NQ for the rest of the session?
  D. Decoupling. The morning (8:30-11:00) correlation of NQ with ES and with gold, known at 11:00: does a low NQ-ES
     correlation (NQ on its own story) or a high NQ-gold correlation (macro day) change what NQ does 11:00-15:00
     (follow or fade the morning move, size of the move)?
Protocol: every comparison is shown with 2018-22 and 2023-26 separately; something only counts if |t| >= 2.5 overall
and the same sign in both periods. Trades (C, D) are 1 NQ after $7.25 + 1 tick a fill ($17.25).
  python3 analysis/cross_asset_map_test.py [SCRATCH_DIR]
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from cl_forced_flows_test import load
from cross_asset_overnight_test import btc
import event_days as E

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPLIT = pd.Timestamp("2023-01-01")
COST = 7.25 + 2 * 0.25 * 20.0


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def line(x, nm, w=66):
    x = pd.Series(x).dropna()
    if len(x) < 10: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.0f} t {tstat(x):4.1f} | 18-22 ${x[y < 2023].mean():6.0f} (t {tstat(x[y < 2023]):4.1f})"
            f" 23-26 ${x[y >= 2023].mean():6.0f} (t {tstat(x[y >= 2023]):4.1f})")


def closes(G, nq_dates, j0, j1, step):
    """(sessions x bars) closes on the NQ trading dates, ffilled, from minute j0 to j1 every `step` minutes."""
    pos = pd.Series(np.arange(G.D), index=G.dates)
    rows = pos.reindex(nq_dates).to_numpy()
    cf = pd.Series(G.c.ravel()).ffill().to_numpy()
    cols = np.arange(j0, j1 + 1, step)
    out = np.full((len(nq_dates), len(cols)), np.nan)
    ok = ~np.isnan(rows)
    r = rows[ok].astype(int)
    out[ok] = cf[r[:, None] * 1440 + cols[None, :]]
    # mark sessions without real data that day
    has = np.zeros(len(nq_dates), bool); has[ok] = ~np.isnan(G.c[r, j0:j1 + 1]).all(1)
    out[~has] = np.nan
    return out


def rowcorr(a, b):
    m = ~np.isnan(a) & ~np.isnan(b)
    a = np.where(m, a, np.nan); b = np.where(m, b, np.nan)
    am = a - np.nanmean(a, 1, keepdims=True); bm = b - np.nanmean(b, 1, keepdims=True)
    num = np.nansum(am * bm, 1); den = np.sqrt(np.nansum(am ** 2, 1) * np.nansum(bm ** 2, 1))
    with np.errstate(all="ignore"): r = num / den
    r[m.sum(1) < 20] = np.nan
    return r


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    M = {"ES": pickle.load(open(SP + "ge.pkl", "rb")), "YM": pickle.load(open(SP + "gy.pkl", "rb")), "GC": load("GC"), "CL": load("CL"), "BTC": btc()}
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= pd.Timestamp("2018-01-01")]
    dates = g.dates[tr]; idx = pd.DatetimeIndex(g.ts[tr]); yr = idx.year

    # ---------- A. map ----------
    j0, j1 = jof(830), jof(1500)
    c5 = {"NQ": closes(g, dates, j0, j1, 5)}; c5.update({k: closes(G, dates, j0, j1, 5) for k, G in M.items()})
    r5 = {k: np.diff(np.log(v), axis=1) for k, v in c5.items()}
    C = pd.DataFrame({k: rowcorr(r5["NQ"], r5[k]) for k in M}, index=idx)
    print("\nA. Session correlation of 5-minute returns with NQ (8:30-15:00), mean by year")
    print(C.groupby(yr).mean().round(2).to_string())
    fomc = pd.to_datetime(E.FOMC_DATES)
    rel = pd.DatetimeIndex(g.ts[E.release_days(g)]).normalize()
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE.shift(1).reindex(idx, method="ffill")
    vq = vix.rank(pct=True)
    rth = pd.Series((c5["NQ"][:, -1] - c5["NQ"][:, 0]) * 20.0, index=idx)
    me = pd.Series(idx, index=idx).groupby(idx.to_period("M")).transform("max") == idx
    opex = (idx.dayofweek == 4) & (idx.day >= 15) & (idx.day <= 21)
    nfp = (idx.dayofweek == 4) & (idx.day <= 7) & idx.normalize().isin(rel)
    types = {"all": np.ones(len(idx), bool), "FOMC decision day": idx.normalize().isin(fomc), "7:30 data-release day": idx.normalize().isin(rel),
             "NFP Friday": nfp, "monthly opex Friday": opex, "month-end": me.to_numpy(), "Monday": idx.dayofweek == 0, "Friday": idx.dayofweek == 4,
             "VIX low third": (vq < 1 / 3).to_numpy(), "VIX high third": (vq >= 2 / 3).to_numpy(),
             "biggest NQ days (top 10% |move|, descriptive)": (rth.abs().rank(pct=True) >= 0.9).to_numpy()}
    print("\n   by day type (mean session correlation; n days)")
    T = pd.DataFrame({nm: C[m].mean() for nm, m in types.items()}).T; T["n"] = [int(m.sum()) for m in types.values()]
    print(T.round(2).to_string())

    # ---------- B. lead-lag ----------
    print("\nB. Lead-lag: corr(NQ return now, market X return k minutes earlier), pooled 8:30-15:00 sessions")
    c1 = {"NQ": closes(g, dates, j0, j1, 1)}; c1.update({k: closes(G, dates, j0, j1, 1) for k, G in M.items()})
    r1 = {k: np.diff(np.log(v), axis=1) for k, v in c1.items()}
    def lagcorr(a, b, k, mask):
        x = a[mask][:, k:].ravel(); y = b[mask][:, :-k].ravel(); m = ~np.isnan(x) & ~np.isnan(y)
        return np.corrcoef(x[m], y[m])[0, 1], m.sum()
    rows = []
    for res, R_ in (("1-min", r1), ("5-min", r5)):
        for k in (1, 2, 3, 5, 10) if res == "1-min" else (1, 2, 3):
            for X in ["NQ"] + list(M):
                d, n1 = lagcorr(R_["NQ"], R_[X], k, yr < 2023); h, n2 = lagcorr(R_["NQ"], R_[X], k, yr >= 2023)
                rows.append(dict(bars=res, lag=k, leader=X, corr_18_22=d, corr_23_26=h, n=n1 + n2))
    L = pd.DataFrame(rows)
    print(L.pivot_table(index=["bars", "lag"], columns="leader", values=["corr_18_22", "corr_23_26"]).round(3).to_string())
    se = 1 / np.sqrt(L.n.min()); print(f"   (standard error of a correlation here ~{se:.4f}; 1-minute costs need |corr| well above 0.03 to trade)")

    # ---------- C. event reactions ----------
    print("\nC. Event reactions: other markets' first 15 minutes vs NQ afterwards (1 NQ, $17.25 costs)")
    def px(G, hh):
        cc = closes(G, dates, jof(hh), jof(hh), 1); return pd.Series(cc[:, 0], index=idx)
    nq = {h: px(g, h) for h in (730, 745, 1300, 1315, 1500)}
    oth = {X: {h: px(G, h) for h in (730, 745, 1300, 1315)} for X, G in M.items()}
    ev = {"7:30 data days": (idx.normalize().isin(rel), 730, 745), "FOMC days (13:00 statement)": (idx.normalize().isin(fomc), 1300, 1315)}
    for evn, (mask, a, b) in ev.items():
        fwd = (nq[1500] - nq[b]) * 20.0
        nqr = np.sign(nq[b] - nq[a])
        print(f"   -- {evn} ({int(mask.sum())} days); NQ after the first 15 minutes, to 15:00")
        print(line((nqr * fwd - COST)[mask], "follow NQ's own first 15 minutes"))
        for X in M:
            xr = np.sign(oth[X][b] - oth[X][a])
            sgn = -1 if X == "GC" else 1        # gold up = rates / dollar down: read as equity-bullish? tested both ways below
            print(line((xr * fwd - COST)[mask], f"long NQ if {X} rose in the first 15 minutes (else short)"))
            agree = (xr == nqr)
            print(line((nqr * fwd - COST)[mask & agree], f"   follow NQ when {X} moved the same way"))
            print(line((nqr * fwd - COST)[mask & ~agree], f"   follow NQ when {X} moved the other way"))

    # ---------- D. decoupling ----------
    print("\nD. Morning decoupling (8:30-11:00 correlations, known at 11:00) and NQ 11:00 -> 15:00")
    k11 = (jof(1100) - jof(830)) // 5
    mES = rowcorr(r5["NQ"][:, :k11], r5["ES"][:, :k11]); mGC = rowcorr(r5["NQ"][:, :k11], r5["GC"][:, :k11]); mBT = rowcorr(r5["NQ"][:, :k11], r5["BTC"][:, :k11])
    am = pd.Series(np.sign(c5["NQ"][:, k11] - c5["NQ"][:, 0]), index=idx)
    pm = pd.Series((c5["NQ"][:, -1] - c5["NQ"][:, k11]) * 20.0, index=idx)
    pm_abs = pm.abs()
    rel_es = pd.Series(np.sign((c5["NQ"][:, k11] / c5["NQ"][:, 0] - 1) - (c5["ES"][:, k11] / c5["ES"][:, 0] - 1)), index=idx)
    for nm, mc in (("NQ-ES", mES), ("NQ-gold", mGC), ("NQ-bitcoin", mBT)):
        s = pd.Series(mc, index=idx); q = s.expanding(120).apply(lambda v: (v[:-1] < v[-1]).mean(), raw=True)
        for lo, hi, lab in ((0, 0.2, "bottom 20%"), (0.8, 1.01, "top 20%")):
            m = (q >= lo) & (q < hi)
            print(line((am * pm - COST)[m], f"{nm} morning corr {lab}: follow the morning move to 15:00"))
            print(line((-am * pm - COST)[m], f"{nm} morning corr {lab}: fade the morning move"))
            print(f"      {'':62} afternoon |move| ${pm_abs[m].median():,.0f} vs all ${pm_abs.median():,.0f}")
        if nm == "NQ-ES":
            m = q < 0.2
            print(line((rel_es * pm - COST)[m], "NQ-ES decoupled: trade NQ in the direction of its morning out-performance vs ES"))
            print(line((-rel_es * pm - COST)[m], "NQ-ES decoupled: trade NQ against its morning out-performance vs ES"))
    pickle.dump(dict(C=C, L=L), open(SP + "cross_asset_map.pkl", "wb"))
