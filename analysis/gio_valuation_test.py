"""GIO Valuation Tool 2.0 (user's TradingView code, 2026-10-15): val = normalise( ROC_n(asset) - ROC_n(reference), n ), where
normalise maps the spread onto -100..+100 by its highest / lowest of the last 10 x n bars; < -75 'undervalued' (buy),
> +75 'overvalued' (sell). Recommended: daily chart; NQ vs bonds with n = 13 (currencies vs DXY with n = 10).
Here, NQ daily closes at 15:00 CT 2018-2026 (n = 13, window 130):
  references  ZN (10-year note PRICE; the code's hidden default 'CBOT:10Y1!' is the 10-year YIELD, i.e. the opposite sign --
              shown as the flipped column), 6E (euro = inverse dollar), and NONE (NQ's own normalised ROC: does the
              reference add anything?)
  trades      mean reversion as the tool says: val < -75 -> long, > +75 -> short; (a) next day session 8:30 -> 15:00 CT
              (Apex-legal), 1 NQ, $7.25 + 1 tick a fill; (b) 5-day close-to-close forward return (information only)
  python3 analysis/gio_valuation_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import load, cost, SPEC, line
import metrics as M


def closes(sym):
    g = load(sym); r = g.trading; cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    idx = pd.DatetimeIndex(g.ts[r])
    return (pd.Series(cf[r * 1440 + jof(1500)], index=idx), pd.Series(cf[r * 1440 + jof(830)], index=idx))


def norm(x, n, mult=10):
    hi, lo = x.rolling(n * mult).max(), x.rolling(n * mult).min()
    return (200 * (x - lo) / (hi - lo) - 100).clip(-100, 100)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    nq, nq_o = closes("NQ"); zn, _ = closes("ZN"); e6, _ = closes("6E")
    df = pd.DataFrame({"nq": nq, "o": nq_o, "zn": zn, "e6": e6}).dropna()
    roc = lambda s, n: (s / s.shift(n) - 1) * 100
    day = (df.nq - df.o) * SPEC["NQ"][0]; nxt = day.shift(-1) - cost("NQ")
    fwd5 = (df.nq.shift(-5) / df.nq - 1) * 100
    V = {"vs ZN price (n 13)": norm(roc(df.nq, 13) - roc(df.zn, 13), 13),
         "vs ZN, flipped (= vs yield)": norm(roc(df.nq, 13) + roc(df.zn, 13), 13),
         "vs 6E (n 10, inverse dollar)": norm(roc(df.nq, 10) - roc(df.e6, 10), 10),
         "no reference (NQ own ROC 13)": norm(roc(df.nq, 13), 13)}
    for nm, v in V.items():
        v = v[v.index >= "2018-01-01"]
        lo, hi = v < -75, v > 75
        x = pd.concat([nxt[lo[lo].index], -(nxt[hi[hi].index] + cost("NQ")) - cost("NQ")]).sort_index()
        print(f"\n{nm}: below -75 on {lo.mean():.0%} of days, above +75 on {hi.mean():.0%}")
        print(line(nxt[lo[lo].index], "  'undervalued' -> long next session"))
        print(line(-(nxt[hi[hi].index] + cost("NQ")) - cost("NQ"), "  'overvalued' -> short next session"))
        print(line(x, "  both"))
        f = fwd5.reindex(v.index)
        print(f"   5-day forward NQ % after undervalued {f[lo].mean():+.2f}, overvalued {f[hi].mean():+.2f}, all days {f.mean():+.2f};"
              f" rank corr(val, 5-day fwd) {v.rank().corr(f.rank()):+.3f}")
