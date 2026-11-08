"""Two 'Setup Generator' stock setups (user screenshot 2026-10-30: the two best setups by profit on 10/23, 13 and 6 trades,
stocks) moved to NQ. Rules fixed before running (2 trials); stock-only filters replaced as noted. 5-minute NQ bars (CT),
1 unit = 0.25 x 14-day ATR, first signal per day, entry at the next bar's open, out 14:55 CT (= 3:55 PM ET).
  S1 Early momentum pop: signal bars closing 08:50-10:00 CT (9:50-11:00 ET); breadth proxy = NQ and ES both above their
     session VWAP (from 08:30); RSI(14) of 5-min closes up >= 19 points vs 3 bars ago; the bar's lower wick >= 1/3 of its range.
     (Stock filters 'range >= 4.4%' and '$50M a day' dropped.) Stop 1 unit below entry, no target.
  S2 Midday failed-breakdown reclaim: signal bars 10:30-13:00 CT (11:30-14:00 ET); ES up > 0.25% since its 08:30 open (SPY
     proxy); NQ traded below its 08:30-09:00 opening-range low earlier today and this bar closes back above it; >= 4 closes
     crossing VWAP since 08:50; close >= 0.31% below its 20-bar SMA. Stop 1 unit below; once +1 unit, a 1-unit trailing stop.
Costs $7.25 per NQ + 1 tick per market / stop fill. Design 2018-22, holdout 2023+ (opened only for a design pass:
t >= 2, PF >= 1.2, >= 4/5 years positive, >= 100 trades).
  python3 analysis/setup_generator_nq_test.py SCRATCH_DIR [holdout]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
HOLD = len(sys.argv) > 2 and sys.argv[2] == "holdout"
PV, TICK, COMM = 20.0, 0.25, 7.25


def five(g, row):
    """5-minute bars 08:35..15:00 CT of one calendar row: o, h, l, c, v and the end column of each bar."""
    ends = np.arange(jof(835), jof(1500) + 1, 5)
    o = np.array([g.o[row, e - 4] for e in ends]); c = np.array([g.c[row, e] for e in ends])
    h = np.array([np.nanmax(g.h[row, e - 4:e + 1]) for e in ends]); l = np.array([np.nanmin(g.l[row, e - 4:e + 1]) for e in ends])
    v = np.array([np.nansum(g.v[row, e - 4:e + 1]) for e in ends])
    return ends, o, h, l, c, v


def vwap(h, l, c, v):
    tp = (h + l + c) / 3; return np.cumsum(tp * v) / np.maximum(np.cumsum(v), 1e-9)


def rsi(c, n=14):
    d = np.diff(c, prepend=c[0]); up = pd.Series(np.maximum(d, 0)).ewm(alpha=1 / n, adjust=False).mean()
    dn = pd.Series(np.maximum(-d, 0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn.replace(0, np.nan))).to_numpy()


def exit_walk(g, row, j0, ep, unit, trail):
    """From the open of minute column j0 to the open of 14:55: stop ep - unit; trailing 1 unit once +1 unit (S2)."""
    stop = ep - unit; armed = False
    for j in range(j0, jof(1455)):
        o, h, l = g.o[row, j], g.h[row, j], g.l[row, j]
        if not np.isfinite(o): continue
        if j > j0 and o <= stop: return o, 0
        if l <= stop: return stop, 0
        if trail:
            if not armed and h >= ep + unit: armed = True
            if armed: stop = max(stop, h - unit)
    x = g.o[row, jof(1455)]
    return (x if np.isfinite(x) else g.c[row, jof(1454)]), 2


def run(g, ge):
    atr = g.daily_atr(14); rows = []
    for k, row in enumerate(g.trading):
        y = int(str(g.dates[row])[:4])
        if y < 2018 or (y >= 2023 and not HOLD) or not np.isfinite(g.c[row, jof(1500)]): continue
        unit = 0.25 * atr[k] if k < len(atr) and np.isfinite(atr[k]) else np.nan
        if not np.isfinite(unit): continue
        try:
            e, o, h, l, c, v = five(g, row); _, eo, eh, el, ec, ev = five(ge, row)
        except Exception: continue
        if np.isnan(c).sum() > 3 or np.isnan(ec).sum() > 3: continue
        vw, evw = vwap(h, l, c, v), vwap(eh, el, ec, ev); r = rsi(c)
        hm = (e // 60) * 100 + e % 60
        orl = np.nanmin(l[hm <= 900]); broke = np.cumsum(l < orl) > 0
        side_vw = np.sign(c - vw); cross = np.cumsum(np.r_[0, (np.diff(side_vw) != 0) & (hm[1:] > 850)])
        sma20 = pd.Series(c).rolling(20, min_periods=20).mean().to_numpy(); eopen = eo[0]
        for name, lo, hi in (("S1", 850, 1000), ("S2", 1030, 1300)):
            for i in range(3, len(e) - 1):
                if not (lo <= hm[i] <= hi): continue
                rng = h[i] - l[i]
                if name == "S1":
                    ok = (c[i] > vw[i] and ec[i] > evw[i] and r[i] - r[i - 3] >= 19 and rng > 0 and (min(o[i], c[i]) - l[i]) >= rng / 3)
                else:
                    ok = (ec[i] / eopen - 1 > 0.0025 and broke[i - 1] and c[i - 1] <= orl < c[i] and cross[i] >= 4
                          and np.isfinite(sma20[i]) and c[i] <= sma20[i] * (1 - 0.0031))
                if ok:
                    j0 = e[i] + 1; ep = g.o[row, j0]
                    if not np.isfinite(ep): break
                    px, kind = exit_walk(g, row, j0, ep, unit, name == "S2")
                    net = (px - ep - TICK * 2) * PV - COMM
                    rows.append(dict(setup=name, date=pd.Timestamp(g.ts[row]), year=y, net=net, R=(px - ep) / unit, kind=kind))
                    break
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); ge = pickle.load(open(SP + "ge.pkl", "rb"))
    T = run(g, ge)
    for s in ("S1", "S2"):
        for lab, a, b in (("2018-22", 2018, 2022),) + ((("2023+", 2023, 2026),) if HOLD else ()):
            x = T[(T.setup == s) & (T.year >= a) & (T.year <= b)]
            if len(x) < 3: print(f"{s} {lab}: {len(x)} trades"); continue
            t = x.net.mean() / x.net.std() * np.sqrt(len(x)); pf = x.net[x.net > 0].sum() / -x.net[x.net < 0].sum()
            days = pd.DatetimeIndex(g.ts[g.trading]); days = days[(days.year >= a) & (days.year <= b)]
            p = M.perf(x.set_index("date").net.reindex(days, fill_value=0).values, x.net.values)
            yrs = x.groupby("year").net.sum()
            print(f"{s} {lab}: {len(x)} trades, win {(x.net > 0).mean():.0%}, avg ${x.net.mean():.0f} per NQ ({x.R.mean():+.2f}R), t {t:.2f}, "
                  f"PF {pf:.2f}, Sharpe {p['sharpe']:.2f}, Sortino {p['sortino']:.2f}, Calmar {p['calmar']:.2f}, Ulcer {p['ulcer']:.2f}, "
                  f"max DD ${p['max_dd']:,.0f}, years+ {(yrs > 0).sum()}/{len(yrs)} {dict((int(k), round(v)) for k, v in yrs.items())}")
