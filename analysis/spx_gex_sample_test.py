"""First look at SPX / SPXW option open interest (historicaldata.net free sample, 2022-07-01 .. 2022-12-30, 127 days) as a
signal for the next ES session (user, 2026-10-17). Format check + the big known effects only; 127 days cannot prove an edge.
Per file date d (OI = prior close, gamma / underlying at d's close), features for the ES session of the NEXT trading day:
  gex      naive dealer gamma exposure: sum(gamma x OI x 100 x S^2 x 1%) with calls +, puts -   ($ per 1% move)
  flip     price where that net gamma changes sign (strike grid), distance of S from it in %
  callwall / putwall   strike with the largest call / put OI within +-10%, distance in %
  maxoi    strike with the largest total OI within +-5%
Targets (ES, 8:30 -> 15:00 CT): absolute session return and range (volatility), signed return (direction), and the
move toward each level (pinning). Data in scratch_data/options_sample (from branch antigravity/jesse, options_sample/).
  python3 analysis/spx_gex_sample_test.py
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof

COLS = ["underlying", "expiration", "type", "strike", "quote_date", "open_interest", "gamma", "underlying_close"]


def day_features(f):
    d = pd.read_csv(f, usecols=COLS)
    d = d[d.underlying.isin(["SPX", "SPXW"]) & d.open_interest.notna() & (d.open_interest > 0)]
    S = d.underlying_close.dropna().iloc[0]
    g = d[d.gamma.notna()]
    sign = np.where(g.type == "call", 1.0, -1.0)
    gex = (g.gamma * g.open_interest * 100 * S * S * 0.01 * sign).sum()
    # gamma profile across a price grid: re-centre gamma by scaling (approximation: use strikes' own gamma as of today)
    by_k = g.assign(x=g.gamma * g.open_interest * sign).groupby("strike").x.sum().sort_index()
    cum = by_k.cumsum(); flip = cum.index[np.argmin(np.abs(cum.values - cum.values[-1] / 2))] if len(cum) else np.nan
    near = d[(d.strike > S * 0.9) & (d.strike < S * 1.1)]
    cw = near[near.type == "call"].groupby("strike").open_interest.sum(); pw = near[near.type == "put"].groupby("strike").open_interest.sum()
    nn = d[(d.strike > S * 0.95) & (d.strike < S * 1.05)].groupby("strike").open_interest.sum()
    return dict(date=pd.Timestamp(d.quote_date.iloc[0]), S=S, gex=gex / 1e9, flip_pct=(S - flip) / S * 100,
                callwall_pct=(cw.idxmax() - S) / S * 100, putwall_pct=(pw.idxmax() - S) / S * 100, maxoi_pct=(nn.idxmax() - S) / S * 100,
                pcr=d[d.type == "put"].open_interest.sum() / d[d.type == "call"].open_interest.sum())


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    F = pd.DataFrame([day_features(f) for f in sorted(glob.glob("scratch_data/options_sample/options_sample/day_by_date/*_options.csv"))]).set_index("date")
    es = pickle.load(open("scratch_data/ge.pkl", "rb")); ts = pd.DatetimeIndex(es.ts)
    C = pd.DataFrame(es.c).ffill(axis=1).to_numpy()
    o = pd.Series(es.o[:, jof(831)], index=ts); c = pd.Series(C[:, jof(1500)], index=ts)
    hi = pd.Series(np.nanmax(es.h[:, jof(831):jof(1500) + 1], axis=1), index=ts); lo = pd.Series(np.nanmin(es.l[:, jof(831):jof(1500) + 1], axis=1), index=ts)
    sess = pd.DataFrame(dict(ret=(c / o - 1) * 100, rng=(hi - lo) / o * 100)).dropna()
    nxt = sess[sess.index > F.index[0]]
    # next ES session after each file date
    rows = []
    for d, r in F.iterrows():
        n = nxt.index[nxt.index > d]
        if len(n): rows.append({**r.to_dict(), "date": d, "next": n[0], **nxt.loc[n[0]].to_dict()})
    X = pd.DataFrame(rows).set_index("date"); X["absret"] = X.ret.abs()
    print(f"\n{len(X)} file days -> next ES session. SPX at the file close {X.S.min():.0f}-{X.S.max():.0f}; naive GEX ${X.gex.min():.1f}bn .. ${X.gex.max():.1f}bn per 1%, "
          f"negative on {np.mean(X.gex < 0):.0%} of days; put/call OI {X.pcr.mean():.2f}")
    def corr(a, b):
        m = X[[a, b]].dropna(); r = np.corrcoef(m[a], m[b])[0, 1]; return f"{r:+.2f} (t {r * np.sqrt(len(m) - 2) / np.sqrt(1 - r * r):+.1f})"
    print("\nVolatility (expected: negative / low GEX -> bigger next-day moves):")
    for f in ("gex", "flip_pct", "pcr"): print(f"   {f:<13} vs next range {corr(f, 'rng')} | vs next |return| {corr(f, 'absret')}")
    lo_, hi_ = X[X.gex < X.gex.median()], X[X.gex >= X.gex.median()]
    print(f"   next ES range: GEX below median {lo_.rng.mean():.2f}% vs above {hi_.rng.mean():.2f}%")
    print("\nDirection / pinning (expected per the folklore: drift toward max OI / walls):")
    for f in ("gex", "flip_pct", "pcr", "callwall_pct", "putwall_pct", "maxoi_pct"): print(f"   {f:<13} vs next return {corr(f, 'ret')}")
    for lev in ("maxoi_pct", "callwall_pct", "putwall_pct"):
        tow = np.sign(X[lev]) * X.ret; print(f"   move toward {lev:<13}: {tow.mean():+.3f}% a day (t {tow.mean() / tow.std() * np.sqrt(len(tow)):+.1f})")

    # does GEX add to what is already known: the previous ES session's range and VIX?
    vix = pd.read_csv("data/VIX_daily.csv"); vix.columns = [c.lower() for c in vix.columns]
    dc = [c for c in vix.columns if "date" in c][0]; vc = [c for c in vix.columns if "close" in c][0]
    vix = pd.Series(vix[vc].astype(float).to_numpy(), index=pd.to_datetime(vix[dc])).sort_index()
    X["prev_rng"] = sess.rng.reindex(X.index).to_numpy(); X["vix"] = vix.reindex(X.index, method="ffill").to_numpy()
    m = X[["rng", "gex", "prev_rng", "vix"]].dropna()
    A = np.column_stack([np.ones(len(m)), m.prev_rng, m.vix, m.gex]); b = m.rng.to_numpy()
    w, *_ = np.linalg.lstsq(A, b, rcond=None); res = b - A @ w; s2 = res @ res / (len(b) - A.shape[1])
    se = np.sqrt(np.diag(s2 * np.linalg.inv(A.T @ A)))
    print(f"\nNext ES range on previous range + VIX + GEX ({len(m)} days): GEX coefficient {w[3]:+.4f} per $bn (t {w[3] / se[3]:+.1f}); "
          f"previous range t {w[1] / se[1]:+.1f}, VIX t {w[2] / se[2]:+.1f}")
