"""Ingredient ablation of the LETF-flow fade (user 2026-11-08: 'what is spoiling its performance?'). Information only: post hoc on a post hoc
lead (WATCHLIST #31), no promotion; any change found here needs its own forward / pre-registered test. Base = analysis/letf_fade_test.py:
Z = yesterday's Nasdaq exposure flow (TQQQ +3, SQQQ -3, QLD +2, QID -2 x fund dollar flow) / past-60-day sd; |Z| >= 1 -> fade at 14:31,
stop 0.25 ATR, out 15:00. One part changed at a time, per NQ after costs, 2018-26 and both periods:
  funds: 3x only (TQQQ / SQQQ) / 2x only (QLD / QID) / bull funds only (TQQQ + QLD) / bear funds only (SQQQ + QID)
  weighting: no leverage weight (plain dollar flow, bear funds negative)
  scale: raw dollars (threshold = the base's share of days, full-sample quantile) / 20-day and 120-day sd
  threshold: every day (any Z) / |Z| >= 0.5 / |Z| >= 1.5
  timing: flow from 2 days ago / window 14:00-14:30 / 14:45-15:00 / no stop
  regime (information): yesterday's VIX above / below its 25-day SMA; NQ up / down yesterday
  tools/run_stamped.sh analysis/letf_ablation.py > analysis/outputs/letf_ablation_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import letf_flow_test as LF
from grid24 import jof


def fund_flows():
    out = {}
    for f in LF.FUNDS:
        d = pd.read_csv(f"data/letf/{f}.csv"); d["Date"] = pd.to_datetime(d.Date, format="%m/%d/%Y"); d = d.sort_values("Date").set_index("Date")
        aum, nav = d["Assets Under Management"].astype(float), d.NAV.astype(float); out[f] = aum - aum.shift(1) * nav / nav.shift(1)
    return pd.DataFrame(out).dropna()


def signal(X, days, sdw=60, zmin=1.0, lag=1, raw_share=None):
    if raw_share is not None:
        q = np.quantile(np.abs(X[X.index >= "2018"]), 1 - raw_share); Zf = X / q          # |Z| >= 1 <=> |X| >= q
    else:
        Zf = X / X.rolling(sdw).std().shift(1)
    Zf = Zf.dropna(); out = {}
    for d, z in Zf.items():
        later = days[days > d]
        if len(later) >= lag and abs(z) >= zmin: out.setdefault(later[lag - 1], z)
    return pd.Series(out).sort_index()


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); days = pd.DatetimeIndex(g.ts[g.trading]); Fd = fund_flows()
    L = pd.Series(LF.FUNDS); X0 = (Fd * L).sum(axis=1)
    fade = lambda d, z: -int(np.sign(z))
    def run(nm, sig, **kw):
        T = LF.trades(g, sig, fade, **kw); print(LF.line(T.net, T.date, nm), flush=True); return T
    base = run("as is (fade, |Z| >= 1, 60-day sd)", signal(X0, days))
    share = len(signal(X0, days)) / len(days[days >= "2018"])
    print("\n   funds / weighting:")
    for nm, cols in (("3x only (TQQQ / SQQQ)", ["TQQQ", "SQQQ"]), ("2x only (QLD / QID)", ["QLD", "QID"]), ("bull funds only (TQQQ + QLD)", ["TQQQ", "QLD"]),
                     ("bear funds only (SQQQ + QID)", ["SQQQ", "QID"])):
        run(nm, signal((Fd[cols] * L[cols]).sum(axis=1), days))
    run("no leverage weight (+-1 per fund)", signal((Fd * np.sign(L)).sum(axis=1), days))
    print("\n   scale / threshold:")
    run("raw dollars (count-matched; full sample)", signal(X0, days, raw_share=share))
    run("20-day sd", signal(X0, days, sdw=20)); run("120-day sd", signal(X0, days, sdw=120))
    run("every day (any Z)", signal(X0, days, zmin=0.0)); run("|Z| >= 0.5", signal(X0, days, zmin=0.5)); run("|Z| >= 1.5", signal(X0, days, zmin=1.5))
    print("\n   timing / exits:")
    S0 = signal(X0, days)
    run("flow from 2 days ago", signal(X0, days, lag=2)); run("window 14:00-14:30", S0, t0=1400, t1=1430); run("window 14:45-15:00", S0, t0=1445, t1=1500)
    run("no stop", S0, stop=100.0)
    print("\n   regime split of the base trades (information):")
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE.sort_index(); hi = vix > vix.rolling(25).mean()
    hv = base.date.map(lambda d: hi[hi.index < d].iloc[-1] if (hi.index < d).any() else np.nan)
    rth = pd.Series(g.c[g.trading, jof(1500)] - g.o[g.trading, jof(831)], index=days).shift(1)
    up = base.date.map(rth) > 0
    for nm, m in (("VIX above its SMA25 yesterday", hv == True), ("VIX at / below", hv == False), ("NQ up yesterday", up), ("NQ down yesterday", ~up),
                  ("fade = short after bullish flow, NQ up yesterday", (base.side < 0) & up), ("fade = long after bearish flow, NQ down yesterday", (base.side > 0) & ~up)):
        x = base[m.fillna(False).to_numpy()]; print(LF.line(x.net, x.date, nm))
