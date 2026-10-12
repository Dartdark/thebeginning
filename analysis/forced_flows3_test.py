"""Forced-flow round 3 (2026-10-12): flows from players who must trade regardless of price.
Raw windows per NQ after $7.25 + 2 ticks (one round trip with a market entry and exit), 2018-2026,
with the 2023-2026 holdout. Count of comparisons is printed; Bonferroni-style bar is |t| >= 3.

 A. Leveraged-ETF rebalancing: TQQQ/SQQQ/QLD/SSO... must buy (sell) about L(L-1) x AUM x day return
    near the cash close. Follow the 8:30 -> T move (T = 14:00, 14:30) into 15:00 on big-move days.
 B. Futures settlement (14:59:30-15:00 CT) and MOC: does 15:00 -> 15:15 reverse the day / last hour?
 C. Volatility-target / risk-parity funds: de-lever after realized vol jumps, re-lever after it falls.
    Signal: change in 5-day realized vol vs 20-day; next day 8:30-15:00 and close-to-close.
 D. Weekday x time-of-day (Friday pre-weekend de-risking, Monday found earlier): 5 x 4 windows.
 E. Quarter-end pension rebalancing: fade the quarter-to-date move over the last 3 trading days.
 F. European cash close (10:30 CT): follow the 8:30 -> 10:30 move to 15:00 (morning momentum).
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
SP = "/tmp/claude-0/-home-user-thebeginning/7f50794d-c1bb-567e-997c-15fdea9b8719/scratchpad/"
g = pickle.load(open(SP + "g24.pkl", "rb"))
PV, RT = 20.0, 7.25 + 2 * 0.25 * 20
tr = g.trading; dts = pd.DatetimeIndex(g.ts[tr]); keep = dts.year >= 2018
o830 = g.o[tr, 511]
def px(j): return g.c[tr, j]
nt = [0]


def rep(name, pnl, mask=None):
    """pnl: $ per NQ per day (already signed, before costs), mask: days traded."""
    x = pd.Series(pnl, index=dts)
    m = keep & ~np.isnan(x.values) & (mask if mask is not None else True)
    x = x[m] - RT
    if len(x) < 20: return
    nt[0] += 1
    y = x.groupby(x.index.year).sum(); h = x[x.index.year >= 2023]; d = x[x.index.year <= 2022]
    t = x.mean() / x.std() * np.sqrt(len(x))
    flag = " <==" if abs(t) >= 3 else (" <" if abs(t) >= 2 else "")
    print(f"  {name:<58} n={len(x):4d} avg ${x.mean():5.0f} t={t:5.1f} yrs+ {(y>0).sum()}/{len(y)} | 18-22 ${d.mean():5.0f} | 23+ ${h.mean():5.0f}{flag}")


print(__doc__.split("\n")[0])
c900 = px(900); c915 = g.c[tr, 915]; c840 = px(840); c870 = px(870)
print("\nA. Leveraged-ETF rebalancing: follow the day's move into 15:00")
for T, cT, nm in ((840, c840, "14:00"), (870, c870, "14:30")):
    r = (cT - o830) / o830 * 100; s = np.sign(r)
    for th in (0, 1.0, 1.5, 2.0):
        rep(f"|8:30->{nm}| >= {th}%: follow {nm}->15:00", s * (c900 - g.o[tr, T + 1]) * PV, np.abs(r) >= th)
print("\nB. After settlement: 15:00 -> 15:15 vs the day's / last hour's direction")
rd = np.sign(c900 - o830); rl = np.sign(c900 - c840)
rep("follow the day (8:30->15:00)", rd * (c915 - c900) * PV)
rep("follow the last hour (14:00->15:00)", rl * (c915 - c900) * PV)
big = np.abs((c900 - o830) / o830) >= 0.015
rep("follow the day, |day| >= 1.5%", rd * (c915 - c900) * PV, big)
print("\nC. Vol-target de/re-levering (realized vol of RTH closes)")
cl = pd.Series(c900, index=dts); ret = cl.pct_change()
rv5 = ret.rolling(5).std(); rv20 = ret.rolling(20).std()
sig = np.sign(-(rv5 / rv20 - 1)).shift(1).to_numpy()      # vol up -> short next day; vol down -> long
nxt_rth = (c900 - o830) * PV
cc = (cl - cl.shift(1)).to_numpy() * PV
rep("rv5/rv20 falling(<1) long, rising(>1) short: 8:30->15:00", sig * nxt_rth)
chg = (rv5 / rv5.shift(1) - 1).shift(1).to_numpy()
rep("rv5 jumped >25% yesterday -> short 8:30->15:00", -nxt_rth, chg > 0.25)
rep("rv5 fell >15% yesterday -> long 8:30->15:00", nxt_rth, chg < -0.15)
print("\nD. Weekday x time of day (long)")
W = {"8:30-10:00": (511, 600), "10:00-12:00": (601, 720), "12:00-15:00": (721, 900)}
for k, nm in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri"]):
    for wn, (a, b) in W.items():
        rep(f"{nm} {wn}", (g.c[tr, b] - g.o[tr, a]) * PV, dts.dayofweek == k)
# overnight into each weekday: previous 15:00 close -> 8:30 open
prevc = np.r_[np.nan, c900[:-1]]
for k, nm in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri"]):
    rep(f"{nm} overnight (prev 15:00 -> 8:30)", (o830 - prevc) * PV, dts.dayofweek == k)
print("\nE. Quarter-end: fade the quarter-to-date move over the last 3 trading days")
q = dts.to_period("Q"); qd = pd.Series(range(len(dts)), index=dts).groupby(q).transform(lambda s: s.max() - s)
qstart = cl.groupby(q).transform("first"); qtd = np.sign((cl.shift(1) - qstart)).to_numpy()
rep("last 3 days of quarter: fade QTD, 8:30->15:00", -qtd * nxt_rth, (qd <= 2).to_numpy())
rep("last day of quarter: fade QTD, 8:30->15:00", -qtd * nxt_rth, (qd == 0).to_numpy())
print("\nF. European close / morning momentum")
for T, nm in ((600, "10:00"), (630, "10:30"), (660, "11:00")):
    s = np.sign(g.c[tr, T] - o830)
    rep(f"follow 8:30->{nm} to 15:00", s * (c900 - g.o[tr, T + 1]) * PV)
    r = np.abs(g.c[tr, T] - o830) / o830 * 100
    rep(f"follow 8:30->{nm} to 15:00, |move| >= 0.5%", s * (c900 - g.o[tr, T + 1]) * PV, r >= 0.5)
print(f"\ncomparisons: {nt[0]}")
