"""Abnormal trading volume (Bajo 2010, "The Information Content of Abnormal Trading Volume", SSRN 675587) on NQ.

Paper (Milan stocks 1997-2003): normalized abnormal volume NAV = (ln(1 + volume) - its 66-day mean) / 66-day std;
events NAV > 2.33 with no event in the previous 30 days. Day 0 earns +2.5%, day +1 another +1.0% (no reversal over 30
days). Trading it next day (open -> close, long if the event-day excess return was > +1/3/5%, short if below): longs
+0.32-0.39% a day after spreads, shorts lose.
NQ version (regular session 8:30-15:00 volume, 1 NQ, $7.25 + 1 tick a fill):
  1. Next day 8:31 -> 14:59 after an abnormal-volume day, direction = sign of the event day's move (and |move| >
     0.5 / 1 / 1.5 x ATR thresholds); NAV > 1.64 / 2.33 / 3.09; with and without the 30-day "fresh event" rule;
     longs and shorts separately; control = the same next-day trade after equally big moves on normal volume.
  2. Same day, intraday: at 12:00 CT, if volume so far is abnormal versus the same window of the last 66 days, follow the
     8:30 -> 12:00 move to 14:59.
  python3 analysis/abnormal_volume_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from alpha101_test import daily_bars
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25
COST = COMM + 2 * TICK * PV
SPLIT = pd.Timestamp("2023-01-01")


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def line(x, nm, w=64):
    x = pd.Series(x).dropna()
    if len(x) < 5: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum()
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():5.0f} PF {pf:4.2f} t {tstat(x):4.1f} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${x[x.index < SPLIT].mean():5.0f} 23-26 ${x[x.index >= SPLIT].mean():5.0f}")


def nav(series, n=66, log=False):
    """The paper's NAV uses ln(1 + volume); on NQ the log version almost never exceeds 2.33, so the raw-volume z-score
    (same 66-day window, known before the day) is the default here."""
    lv = np.log1p(series) if log else series
    mu = lv.rolling(n).mean().shift(1); sd = lv.rolling(n).std().shift(1)
    return (lv - mu) / sd


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    B = daily_bars(g)
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    B["x"] = cf[B.row.values * 1440 + jof(1459)]
    B["move"] = B.close - B.open                                   # event-day 8:30 -> 15:00 move, points
    tr = np.maximum(B.high - B.low, np.maximum(abs(B.high - B.close.shift()), abs(B.low - B.close.shift())))
    B["atr"] = tr.rolling(14).mean().shift(1)
    B["nav"] = nav(B.volume); B["nav_log"] = nav(B.volume, log=True)
    B["ratio"] = B.volume / B.volume.rolling(66).median().shift(1)
    B["next"] = ((B.x - B.open) * PV).shift(-1)                     # next day's long $ 8:30 -> 14:59 (gross)
    B = B[B.index >= pd.Timestamp("2018-01-01")]
    print(f"sessions {len(B)}; NAV > 1.64 on {np.mean(B.nav > 1.64):.1%} of days, > 2.33 {np.mean(B.nav > 2.33):.1%}, > 3.09 {np.mean(B.nav > 3.09):.1%}")
    print(f"   paper's log NAV: > 1.64 on {np.mean(B.nav_log > 1.64):.1%}, > 2.33 {np.mean(B.nav_log > 2.33):.1%} -> raw-volume z used below;"
          f" volume / 66-day median >= 1.5 on {np.mean(B.ratio >= 1.5):.1%}, >= 2 on {np.mean(B.ratio >= 2):.1%}")
    print(f"   event-day |move| / ATR: NAV > 2.33 {np.nanmedian((B.move.abs() / B.atr)[B.nav > 2.33]):.2f} vs other days {np.nanmedian((B.move.abs() / B.atr)[B.nav <= 2.33]):.2f}")

    print("\n1. Next day 8:31 -> 14:59 after abnormal volume, side = sign of the event day's move")
    net = lambda s: s * B.next - COST
    sd = np.sign(B.move)
    print(line(net(pd.Series(1.0, index=B.index)), "always long (benchmark)"))
    for cut in (1.64, 2.33, 3.09):
        ev = B.nav > cut
        fresh = ev & ~(ev.shift(1).rolling(30, min_periods=1).max().fillna(0) > 0)
        for nm, m in ((f"NAV > {cut}", ev), (f"NAV > {cut}, fresh (no event in prior 30 days)", fresh)):
            print(line(net(sd)[m], f"{nm}: follow"))
            print(line(net(sd)[m & (sd > 0)], f"   longs (event day up)"))
            print(line(net(sd)[m & (sd < 0)], f"   shorts (event day down)"))
    for r_ in (1.5, 2.0):
        m = B.ratio >= r_
        print(line(net(sd)[m], f"volume >= {r_} x 66-day median: follow"))
        print(line(net(sd)[m & (sd > 0)], "   longs")); print(line(net(sd)[m & (sd < 0)], "   shorts"))
        print(line(net(-sd)[m], "   fade instead"))
    print("   with a minimum event-day move (NAV > 2.33):")
    for k in (0.5, 1.0, 1.5):
        big = (B.move.abs() >= k * B.atr)
        m = (B.nav > 2.33) & big
        print(line(net(sd)[m], f"   |move| >= {k} ATR, follow"))
        print(line(net(sd)[m & (sd > 0)], f"      longs"))
        print(line(net(sd)[m & (sd < 0)], f"      shorts"))
        print(line(net(sd)[(B.nav <= 0.5) & big], f"      control: same move on normal volume (NAV <= 0.5)"))
        print(line(net(-sd)[m], f"      fade instead"))

    print("\n2. Same day: at 12:00 CT, abnormal volume so far (vs the same window of the last 66 days), follow 8:30 -> 12:00 to 14:59")
    rows = g.trading; j0, j1 = jof(831), jof(1200)
    vol_am = pd.Series(np.nansum(np.nan_to_num(g.v[rows, j0:j1 + 1]), 1), index=pd.DatetimeIndex(g.ts[rows]))
    n_am = nav(vol_am)
    p12 = pd.Series(cf[rows * 1440 + j1], index=vol_am.index); o = pd.Series(g.o[rows, j0], index=vol_am.index)
    x = pd.Series(cf[rows * 1440 + jof(1459)], index=vol_am.index)
    s = np.sign(p12 - o); intr = s * (x - p12) * PV - COST
    intr = intr[intr.index >= pd.Timestamp("2018-01-01")]; n_am = n_am.reindex(intr.index); s = s.reindex(intr.index)
    print(line(intr, "follow 8:30 -> 12:00, every day"))
    for cut in (1.0, 1.64, 2.33):
        print(line(intr[n_am > cut], f"   morning NAV > {cut}"))
        print(line(intr[(n_am > cut) & (s > 0)], f"      longs"))
        print(line(intr[(n_am > cut) & (s < 0)], f"      shorts"))
    print(line(intr[n_am < 0], "   morning NAV < 0 (quiet)"))

    # metrics for the paper's main rule (NAV > 2.33, follow, next day), whole / longs / shorts
    m = B.nav > 2.33; t = net(sd)[m].dropna()
    days = B.index
    dl = t.reindex(days, fill_value=0.0); side = sd[m].reindex(t.index)
    rows_ = {"NAV > 2.33 follow next day": (dl, t), "  longs": (t[side > 0].reindex(days, fill_value=0.0), t[side > 0]),
             "  shorts": (t[side < 0].reindex(days, fill_value=0.0), t[side < 0])}
    print("\n" + M.table(rows_))
    b_, p_ = R.report({"NAV > 2.33 follow, 2023+": dl[dl.index >= SPLIT]}, n=3000); print(b_); print(p_)
