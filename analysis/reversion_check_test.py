"""ReversionCheck (user's MultiCharts code, 2026-10-15): on every bar, fade the bar's close-to-close move (up bar -> sell short
next bar at market, down bar -> buy), exit HoldBars bars later at market. The user ran it on 6E (EUR/USD futures) 10-min since
2015 and read the rising equity curve as strong mean reversion. Here, 2018-2026, 1-min data built into N-minute bars (all
hours, like a 24h chart; and the 8:30-15:00 CT day session only), fills exactly as the code: signal at bar t's close, enter at
bar t+1's open, exit at bar t+1+HoldBars' open, one trade at a time.
  A  the check as written (HoldBars 1, 10-min): gross ticks a trade vs the cost of a round trip ($7.25 + 1 tick a fill),
     on 6E, NQ, ES, YM, GC, CL, ZN; lag-1 autocorrelation of the bar returns
  B  6E: timeframe 1 / 5 / 10 / 30 / 60 min x HoldBars 1 / 3 (gross and net)
  C  6E: fade only big bars, |move| >= k x the rolling sd of the last 100 bars (k 2 / 3), 10-min, HoldBars 1 / 3; by year
  python3 analysis/reversion_check_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import load, cost, SPEC

SYMS = ["6E", "NQ", "ES", "YM", "GC", "CL", "ZN"]


def bars(g, n, day_only=False):
    """N-minute OHLC bars (only bars that traded), chronological; day id for the day-session filter."""
    o, c = g.o.ravel(), g.c.ravel()
    T = np.arange(o.size); col = T % 1440; day = T // 1440
    keep = ~np.isnan(c) & (pd.DatetimeIndex(g.ts)[day].year >= 2018)
    if day_only: keep &= (col > jof(830)) & (col <= jof(1500))       # 8:31 .. 15:00 bars
    T, col, day = T[keep], col[keep], day[keep]
    bid = (T - 1) // n                                                  # bar = minutes closing in ((k)n, (k+1)n]
    df = pd.DataFrame({"o": o[keep], "c": c[keep], "bid": bid, "day": day})
    b = df.groupby("bid").agg(o=("o", "first"), c=("c", "last"), day=("day", "first"))
    return b


def run(b, sym, hold=1, k=None, sdwin=100, same_day=False):
    """Trades of the fade rule; returns a Series of net $ per trade indexed by entry date, plus gross ticks."""
    pv, tick, _ = SPEC[sym]
    o, c, d = b.o.to_numpy(), b.c.to_numpy(), b.day.to_numpy()
    mv = np.diff(c, prepend=np.nan)
    sd = pd.Series(mv).rolling(sdwin).std().shift(1).to_numpy()
    sig = -np.sign(mv)
    if k is not None: sig = np.where(np.abs(mv) >= k * sd, sig, 0)
    out_i, out_p = [], []
    i, N = 1, len(c)
    while i < N - 1 - hold:
        if sig[i] != 0 and (not same_day or d[i + 1 + hold] == d[i]):
            out_i.append(i + 1); out_p.append(sig[i] * (o[i + 1 + hold] - o[i + 1]))
            i += 1 + hold                      # flat again at the close of the exit bar -> next signal there
        else:
            i += 1
    out_i = np.array(out_i, int); pts = np.array(out_p)
    dates = pd.DatetimeIndex(g_ts[sym])[d[out_i]]
    return pd.Series(pts * pv - cost(sym), index=dates), pts / tick


def summ(net, ticks, sym, label, w=34):
    gross_t = np.nanmean(ticks); c_t = cost(sym) / SPEC[sym][0] / SPEC[sym][1]
    y = net.index.year; per_y = len(net) / max(1, y.nunique())
    by = net.groupby(y).sum()
    return (f"   {label:<{w}} trades/yr {per_y:7.0f}  gross {gross_t:+.3f} ticks vs cost {c_t:.2f} ticks  net ${net.mean():+7.2f}/trade"
            f"  ${net.sum() / y.nunique():+10,.0f}/yr  yrs+ {(by > 0).sum()}/{len(by)} | gross 18-22 {np.nanmean(ticks[y < 2023]):+.3f} 23-26 {np.nanmean(ticks[y >= 2023]):+.3f}")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    G = {s: load(s) for s in SYMS}; g_ts = {s: G[s].ts for s in SYMS}
    print("\nA. The check as written: 10-min bars, HoldBars 1, 1 contract (gross ticks a trade; cost of a round trip in ticks)")
    for s in SYMS:
        for dayonly in (False, True):
            b = bars(G[s], 10, dayonly)
            r = np.diff(np.log(b.c.to_numpy())); ac = pd.Series(r).autocorr(1)
            net, tk = run(b, s, 1, same_day=dayonly)
            print(summ(net, tk, s, f"{s} {'day 8:30-15:00' if dayonly else 'all hours'} (lag-1 ac {ac:+.3f})"))
    print("\nB. 6E: timeframe x HoldBars, all hours")
    for n in (1, 5, 10, 30, 60):
        b = bars(G["6E"], n)
        for h in (1, 3):
            net, tk = run(b, "6E", h); print(summ(net, tk, "6E", f"6E {n}-min, hold {h}"))
    print("\nC. 6E: fade only big bars (|move| >= k x sd of the last 100 bars), 10-min")
    for dayonly in (False, True):
        b = bars(G["6E"], 10, dayonly)
        for k in (2, 3):
            for h in (1, 3):
                net, tk = run(b, "6E", h, k=k, same_day=dayonly)
                print(summ(net, tk, "6E", f"6E {'day' if dayonly else 'all'} k {k} hold {h}"))
                print("      net $ by year:", net.groupby(net.index.year).sum().round(0).astype(int).to_dict())
