"""Lead 1 (user, 2026-10-18): the leveraged-ETF / closing price push reverses overnight. Apex-legal version: the Apex day
starts at 17:00 CT, so a 17:00 reopen -> 8:30 open hold is inside one Apex session (flat long before 15:59).
Pre-registered before looking:
  Day move = 8:30 open -> 15:00 close of a weekday trading row (not an early-close day).
  Big day = |move| >= 0.4 x ATR15 (the LDF threshold); variant 0.8 x ATR15.
  Trade = opposite the move, entry at the open of the first bar of the 17:00 reopen that leads into the next trading row
          (first bar 17:01-17:10 stamp; some exports start at 17:01 / 17:02), exit at that next row's 8:30 open.
  Left out: roll-week nights (days 8-17 of Mar / Jun / Sep / Dec), early-close days.
  Costs per contract round trip: NQ $24.50, ES $35.
  Controls: (a) the same night on small-move days (|move| < 0.4 ATR), side = opposite the small move;
            (b) random side on the big days (1,000 draws -> p of the real mean);
            (c) the move taken only in the LETF window 14:40 -> 15:00 (the push itself) as the trigger, same size rules
                scaled 0.15 / 0.3 ATR (pre-set, smaller window).
  Overlap: the old Overnight Drift (long after a down session) = the long half of this; shorts are the new part.
  python3 analysis/letf_overnight_reversal_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M
from grid24 import jof

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MK = {"NQ": ("g24", 20.0, 24.5), "ES": ("ge", 50.0, 35.0)}
rng = np.random.default_rng(7)


def early_close(d):                                # CME early-close days, as analysis/es_euro_close_check.py
    m, dd, dow, y = d.month, d.day, d.isoweekday() % 7, d.year
    wk = 1 <= dow <= 5
    return ((m == 1 and ((dd == 1 and wk) or (dd == 2 and dow == 1)))
            or (m == 1 and dow == 1 and 15 <= dd <= 21) or (m == 2 and dow == 1 and 15 <= dd <= 21)
            or (m == 5 and dow == 1 and dd >= 25)
            or (m == 6 and y >= 2022 and ((dd == 19 and wk) or (dd == 18 and dow == 5) or (dd == 20 and dow == 1)))
            or (m == 7 and (((dd == 3 or dd == 4) and wk) or (dd == 5 and dow == 1)))
            or (m == 9 and dow == 1 and dd <= 7)
            or (m == 11 and dow == 4 and 22 <= dd <= 28) or (m == 11 and dow == 5 and 23 <= dd <= 29)
            or (m == 12 and (((dd == 24 or dd == 25) and wk) or (dd == 26 and dow == 1))))


def stats(x, dates, nm):
    x = pd.Series(np.asarray(x, float), index=pd.DatetimeIndex(dates)).dropna()
    if len(x) < 5: print(f"   {nm:<50} n={len(x)}"); return
    t = x.mean() / x.std() * np.sqrt(len(x)); yrs = x.groupby(x.index.year).sum(); gl = -x[x < 0].sum()
    a, h = x[x.index < "2023"], x[x.index >= "2023"]
    print(f"   {nm:<50} n={len(x):4d} ${x.mean():6.1f} PF {x[x > 0].sum() / gl if gl else np.inf:4.2f} t {t:4.1f} "
          f"yrs+ {(yrs > 0).sum()}/{len(yrs)} | 18-22 ${a.mean():.0f} 23+ ${h.mean():.0f}")


def nights(sym):
    g = pickle.load(open(SP + MK[sym][0] + ".pkl", "rb")); _, pv, cost = MK[sym]
    tr = g.trading; dts = pd.DatetimeIndex(g.ts[tr]); atr = g.daily_atr(15)
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    rows = []
    for i in range(len(tr) - 1):
        r, nx = tr[i], tr[i + 1]; d = dts[i]
        if d < pd.Timestamp("2018-01-01") or early_close(d.date()): continue
        if d.month in (3, 6, 9, 12) and 8 <= d.day <= 17: continue
        o830 = g.o[r, jof(831)]; c1500 = cf[r * 1440 + jof(1500)]; c1440 = cf[r * 1440 + jof(1440)]
        ev = nx - 1                                        # calendar row whose 17:00 reopen leads into the next trading row
        seg = g.o[ev, jof(1701):jof(1710) + 1]; ok = np.flatnonzero(~np.isnan(seg))
        x = g.o[nx, jof(831)]
        if not len(ok) or np.isnan(o830) or np.isnan(x) or not atr[r] > 0: continue
        e = seg[ok[0]]
        rows.append(dict(date=d, move=(c1500 - o830) / atr[r], push=(c1500 - c1440) / atr[r], night=(x - e) * pv))
    df = pd.DataFrame(rows); df["cost"] = cost
    return df


def report(df, col, k, nm):
    big = df[col].abs() >= k; side = -np.sign(df[col])
    pnl = side * df.night - df.cost
    stats(pnl[big], df.date[big], f"{nm} fade, |{col}| >= {k} ATR")
    stats(pnl[big & (side > 0)], df.date[big & (side > 0)], "   longs (after down days = Overnight Drift subset)")
    stats(pnl[big & (side < 0)], df.date[big & (side < 0)], "   shorts (after up days, the new part)")
    stats((pnl + df.cost)[big], df.date[big], "   gross, before costs")
    return pnl, big, side


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for sym in ("NQ", "ES"):
        df = nights(sym); print(f"\n{sym}: {len(df)} usable nights 2018-2026")
        pnl, big, side = report(df, "move", 0.4, sym)
        print("      by year:", pnl[big].groupby(df.date[big].dt.year).sum().round(0).to_dict())
        report(df, "move", 0.8, sym)
        sm = ~big; stats(pnl[sm], df.date[sm], "control (a): small days, same fade")
        stats((df.night - df.cost)[big], df.date[big], "control: always long on big days")
        stats(df.night - df.cost, df.date, "control: always long, every night")
        real = (side * df.night)[big].mean()
        draws = np.array([(rng.choice([-1, 1], big.sum()) * df.night[big]).mean() for _ in range(1000)])
        print(f"   control (b): random side p = {(draws >= real).mean():.3f} (gross mean ${real:.1f})")
        for k in (0.15, 0.3): report(df, "push", k, f"{sym} (c) 14:40-15:00 push")
    # Added after seeing the results above (post hoc): the one cut that worked on both NQ and ES was the LONG side of (c)
    # (down push 14:40-15:00 >= 0.15 ATR -> long 17:00 -> 8:30). Out-of-market check, rule fixed before running: YM.
    MK["YM"] = ("gy", 5.0, 20.0)
    df = nights("YM"); dn = df.push <= -0.15
    print(f"\nYM out-of-market check of the post-hoc cut ({len(df)} nights)")
    stats((df.night - df.cost)[dn], df.date[dn], "YM long after down push >= 0.15 ATR")
    stats(df.night - df.cost, df.date, "YM control: always long, every night")
    up = df.push >= 0.15; stats((-df.night - df.cost)[up], df.date[up], "YM short after up push >= 0.15 ATR")
