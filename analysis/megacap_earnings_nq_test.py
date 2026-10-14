"""NQ after mega-cap earnings (index-level PEAD, from the Fink 2021 / Sojka 2018 reviews), 2018-2026.

Data: data/ndx_megacap_earnings.csv (Alpha Vantage EARNINGS: report date, pre- / post-market, EPS estimate / actual, surprise %)
for NVDA, MSFT, AAPL, AMZN, META, AVGO, GOOGL, TSLA, AMD, PLTR (NFLX, COST missing: rate limit). Approximate Nasdaq-100 weights
(%): NVDA 9, MSFT 8, AAPL 8, AMZN 6, GOOGL 5, META 4, AVGO 5, TSLA 3, AMD 1, PLTR 1.
Event session T: the next trading day after a post-market report, the same day for a pre-market report. Reaction R = NQ
15:00 CT (day before T) -> 8:30 CT on T, which spans the report. Pre-specified trades on T, 1 NQ, $7.25 + 1 tick a fill:
  1 follow R, 8:30 -> 15:00 (placebo: the same on every other day)   2 fade R
  3 follow the weighted surprise sign S = sum(weight x sign(surprise %))
  4 variants: only the six largest names (weight >= 4), only |R| >= 0.5 sd of R, entry at 9:00
  python3 analysis/megacap_earnings_nq_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import line
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, COST = 20.0, 7.25 + 2 * 0.25 * 20
WT = {"NVDA": 9, "MSFT": 8, "AAPL": 8, "AMZN": 6, "GOOGL": 5, "AVGO": 5, "META": 4, "TSLA": 3, "AMD": 1, "PLTR": 1}

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    tr = g.trading; days = pd.DatetimeIndex(g.ts[tr])
    px = lambda rows, hh: cf[rows * 1440 + jof(hh)]
    P = pd.DataFrame({"prev1500": np.r_[np.nan, px(tr[:-1], 1500)], "o830": px(tr, 830), "o900": px(tr, 900),
                      "c1500": px(tr, 1500)}, index=days)
    P = P[P.index >= "2018-01-01"]
    P["R"] = np.log(P.o830 / P.prev1500)
    P["day830"] = (P.c1500 - P.o830) * PV; P["day900"] = (P.c1500 - P.o900) * PV
    E = pd.read_csv("data/ndx_megacap_earnings.csv")
    E["d"] = pd.to_datetime(E.reportedDate); E = E[(E.d >= "2017-12-15") & E.ticker.isin(WT)]
    E["sp"] = pd.to_numeric(E.surprisePercentage, errors="coerce")
    idx = P.index
    def session(r):
        if r.reportTime == "pre-market": k = idx.searchsorted(r.d)
        else: k = idx.searchsorted(r.d, side="right")
        return idx[k] if k < len(idx) else pd.NaT
    E["T"] = E.apply(session, axis=1); E = E.dropna(subset=["T"])
    E["w"] = E.ticker.map(WT); E["ws"] = E.w * np.sign(E.sp.fillna(0))
    agg = E.groupby("T").agg(S=("ws", "sum"), W=("w", "sum"), big=("w", "max"), names=("ticker", lambda x: ",".join(x)))
    P = P.join(agg); ev = P.S.notna()
    print(f"event sessions {ev.sum()} ({ev.sum() / len(P) * 252:.0f} a year); names per session {E.groupby('T').size().mean():.1f}")
    sdR = P.R.rolling(60).std().shift(1)
    print(f"|overnight move| on event nights {P.R[ev].abs().mean() * 1e4:.0f} bp vs other nights {P.R[~ev].abs().mean() * 1e4:.0f} bp")
    print(f"corr(R, next session 8:30-15:00): event {P.R[ev].corr(P.day830[ev]):+.3f}, other {P.R[~ev].corr(P.day830[~ev]):+.3f}")
    print(f"corr(surprise sign S, R) {P.S[ev].corr(P.R[ev]):+.3f}; corr(S, session) {P.S[ev].corr(P.day830[ev]):+.3f}")
    rows = {}
    for nm, sig, m, col in (
            ("1 follow R (event)", np.sign(P.R), ev, "day830"), ("1 follow R (placebo, other days)", np.sign(P.R), ~ev, "day830"),
            ("2 fade R (event)", -np.sign(P.R), ev, "day830"), ("2 fade R (placebo)", -np.sign(P.R), ~ev, "day830"),
            ("3 follow surprise sign S", np.sign(P.S), ev & (P.S != 0), "day830"),
            ("4a follow R, six largest names", np.sign(P.R), ev & (P.big >= 4), "day830"),
            ("4a fade R, six largest names", -np.sign(P.R), ev & (P.big >= 4), "day830"),
            ("4b follow R, |R| >= 0.5 sd", np.sign(P.R), ev & (P.R.abs() >= 0.5 * sdR), "day830"),
            ("4b fade R, |R| >= 0.5 sd", -np.sign(P.R), ev & (P.R.abs() >= 0.5 * sdR), "day830"),
            ("4c follow R, 9:00 entry", np.sign(P.R), ev, "day900"), ("4c fade R, 9:00 entry", -np.sign(P.R), ev, "day900"),
            ("   long every event day (drift)", pd.Series(1.0, index=P.index), ev, "day830"),
            ("   long every other day (drift)", pd.Series(1.0, index=P.index), ~ev, "day830")):
        x = (sig * P[col])[m].dropna() - COST
        print(line(x, nm, 36)); rows[nm] = x
    best = max([k for k in rows if "placebo" not in k and "drift" not in k], key=lambda k: rows[k].mean())
    x = rows[best]; d = x.reindex(P.index).fillna(0)
    print(f"\nbest pre-specified cell: {best}"); print(M.table({best: (d, x)}))
    b, p = R.report({best: d[d.index >= "2023"]}, n=2000); print("2023+ bootstrap:\n" + b)
