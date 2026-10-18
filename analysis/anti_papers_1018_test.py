"""Antigravity's paper screen, batch 2026_10_18 (TASK_PAPER_SCREEN): its 'Send to Claude' list, tested as Antigravity wrote
the trades (SSRN pages return 403 here, so its quotes are NOT verified against the papers). Pre-registered before looking.
  1. Fleming, Liu & Nguyen (2026), Treasury auction price pressure: ALREADY TESTED (TIER_LIST, analysis/treasury_auction_test.py:
     pre-auction leg real but 1/3 of the cost, post-auction rebound absent). Not rerun.
  2. Baglioni, Giannozzi, Ribeiro & Roggi, 'Liquidity Premium Around FOMC Announcements' (SSRN 4304807): long at the 13:00 CT
     statement, out 15:00 CT, on FOMC days when the PRIOR day's liquidity was below median. Proxies (no book depth before
     2018 in our data): prior-day RTH volume (8:30-15:00) below its 20-day median; prior-day Amihud |ret| / volume above its
     20-day median. All FOMC days too; with and without a 15-point ES stop (NQ: 60 points). ES and NQ.
     Placebo: the same window on every other Wednesday.
  3. Ladia, 'Opening-Range Reversal in Dow Jones Futures' (SSRN 7124578): YM, if 8:30 open -> 8:45 close >= +0.1 ATR15 (an
     upward opening push), short at 8:45, out 9:30 CT; variant 1:1 bracket 50 YM points. Also the mirror (down push -> long),
     the gap-up version (8:30 open above the prior 15:00 close), and the same rule on ES / NQ as a control.
Costs per contract round trip: ES $35, NQ $24.50, YM $20. Stops on 1-minute bars, stop first if both in one minute.
  python3 analysis/anti_papers_1018_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from event_days import FOMC_DATES

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MK = {"ES": ("ge", 50.0, 35.0, 0.25), "NQ": ("g24", 20.0, 24.5, 0.25), "YM": ("gy", 5.0, 20.0, 1.0)}
FOMC = set(pd.to_datetime(FOMC_DATES))


def stats(x, dates, nm):
    x = pd.Series(np.asarray(x, float), index=pd.DatetimeIndex(dates)).dropna()
    if len(x) < 5: print(f"   {nm:<48} n={len(x)}"); return
    t = x.mean() / x.std() * np.sqrt(len(x)); yrs = x.groupby(x.index.year).sum(); gl = -x[x < 0].sum()
    a, h = x[x.index < "2023"], x[x.index >= "2023"]
    print(f"   {nm:<48} n={len(x):4d} ${x.mean():7.1f} PF {x[x > 0].sum() / gl if gl else np.inf:4.2f} t {t:4.1f} "
          f"yrs+ {(yrs > 0).sum()}/{len(yrs)} | 18-22 ${a.mean():.0f} 23+ ${h.mean():.0f}")


def trade(g, r, j0, j1, side, e, stop=None, tgt=None, tick=0.25):
    """Exit at the close of minute j1 (or stop / target in between); returns points net of 1 tick per market/stop fill."""
    x, slip = None, 2 * tick
    for j in range(j0 + 1, j1 + 1):
        lo, hi = g.l[r, j], g.h[r, j]
        if np.isnan(lo): continue
        if stop is not None and ((side > 0 and lo <= e - side * stop) or (side < 0 and hi >= e - side * stop)):
            x = e - side * stop; break
        if tgt is not None and ((side > 0 and hi >= e + side * tgt) or (side < 0 and lo <= e + side * tgt)):
            x, slip = e + side * tgt, tick; break
    if x is None:
        x = pd.Series(g.c[r, :j1 + 1]).ffill().iloc[-1]
    return side * (x - e) - slip


def daily(sym):
    g = pickle.load(open(SP + MK[sym][0] + ".pkl", "rb")); tr = g.trading
    dts = pd.DatetimeIndex(g.ts[tr]).normalize(); atr = g.daily_atr(15)
    cf = lambda r, hm: pd.Series(g.c[r, :jof(hm) + 1]).ffill().iloc[-1]
    vol = np.nansum(g.v[tr][:, jof(831):jof(1500) + 1], axis=1)
    ret = np.array([abs(cf(r, 1500) / g.o[r, jof(831)] - 1) if not np.isnan(g.o[r, jof(831)]) else np.nan for r in tr])
    d = pd.DataFrame(dict(r=tr, vol=vol, amihud=ret / np.where(vol > 0, vol, np.nan), atr=atr[tr]), index=dts)
    d["lowvol"] = (d.vol < d.vol.rolling(20).median()).shift(1)
    d["illiq"] = (d.amihud > d.amihud.rolling(20).median()).shift(1)
    return g, d[d.index >= "2018-01-01"], cf


def fomc_test(sym):
    g, d, cf = daily(sym); pv, cost, tick = MK[sym][1], MK[sym][2], MK[sym][3]; stop = 15.0 if sym == "ES" else 60.0
    rows = []
    for dt, x in d.iterrows():
        if dt.dayofweek != 2: continue
        r = int(x.r); e = cf(r, 1300)
        if np.isnan(e): continue
        rows.append(dict(date=dt, fomc=dt in FOMC, lowvol=bool(x.lowvol), illiq=bool(x.illiq),
                         plain=trade(g, r, jof(1300), jof(1500), 1, e, tick=tick) * pv - cost,
                         stop=trade(g, r, jof(1300), jof(1500), 1, e, stop=stop, tick=tick) * pv - cost))
    df = pd.DataFrame(rows); f = df[df.fomc]; o = df[~df.fomc]
    print(f"\n2. FOMC liquidity premium, {sym}: long 13:00 -> 15:00 CT ({len(f)} FOMC days)")
    stats(f.plain, f.date, "all FOMC days")
    stats(f.plain[f.lowvol], f.date[f.lowvol], "prior-day volume below 20-day median")
    stats(f.plain[~f.lowvol], f.date[~f.lowvol], "   (prior-day volume above)")
    stats(f.plain[f.illiq], f.date[f.illiq], "prior-day Amihud illiquidity above median")
    stats(f.stop[f.lowvol], f.date[f.lowvol], f"low volume, {'15' if sym == 'ES' else '60'}-pt stop")
    stats(o.plain, o.date, "placebo: other Wednesdays")
    stats(o.plain[o.lowvol], o.date[o.lowvol], "placebo: other Wednesdays, low volume")


def ym_open(sym):
    g, d, cf = daily(sym); pv, cost, tick = MK[sym][1], MK[sym][2], MK[sym][3]
    br = {"YM": 50.0, "ES": 50.0 / 40000 * 5000, "NQ": 50.0 / 40000 * 18000}[sym]   # 50 YM points, scaled by index level
    rows = []
    prev15 = np.nan
    for dt, x in d.iterrows():
        r = int(x.r); o = g.o[r, jof(831)]; e = cf(r, 845)
        if np.isnan(o) or np.isnan(e) or not x.atr > 0: prev15 = cf(r, 1500); continue
        push = (e - o) / x.atr; side = -1 if push >= 0.1 else (1 if push <= -0.1 else 0)
        rows.append(dict(date=dt, push=push, gapup=o > prev15, side=side,
                         plain=trade(g, r, jof(845), jof(930), side or -1, e, tick=tick) * pv - cost,
                         brk=trade(g, r, jof(845), jof(930), side or -1, e, stop=br, tgt=br, tick=tick) * pv - cost))
        prev15 = cf(r, 1500)
    df = pd.DataFrame(rows); up = df.side == -1; dn = df.side == 1
    print(f"\n3. Opening-range reversal, {sym}: push 8:30 -> 8:45 >= 0.1 ATR, fade 8:45 -> 9:30 CT")
    stats(df.plain[up], df.date[up], "SHORT after an up push (the paper's side)")
    stats(df.brk[up], df.date[up], f"   with a 1:1 bracket ({br:.0f} pts)")
    stats(df.plain[dn], df.date[dn], "long after a down push (mirror)")
    gu = df.gapup & (df.push > 0)
    stats(df.plain[gu], df.date[gu], "short on gap-up days with an up push (any size)")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for s in ("ES", "NQ"): fomc_test(s)
    for s in ("YM", "ES", "NQ"): ym_open(s)
