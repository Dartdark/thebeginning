"""Price gaps (Caporale & Plastun 2016, 'Price Gaps: Another Market Anomaly?', SSRN 2850057; user's PDF and rule 2026-10-15).
Paper (daily 2000-15): gaps don't predict direction (H1-H4 rejected), up to 80% aren't filled within 5 days (H5), but in
EUR/USD and GBP/USD the session after a POSITIVE gap drifts down (H6); robot 'sell after a positive gap, close at the end of
the day': EUR/USD gap 0.10% 148 trades, 63.5% win, 13/16 years up; GBP/USD 0.05% 221 trades, 60%. 96% of FX gaps are on
Mondays (the weekend is FX's only real break).
User's rule, futures: at the session open, if the open is >= threshold above the prior settlement, short 1 contract; cover
at that session's settlement; positive gaps only; no stop / target; costs; tag every trade by weekday. 6E 0.10% (6B 0.05%:
no 6B data here). Then the same rule on our other futures.
Here: session open = 17:00 CT (Sunday 17:00 for Monday); prior settlement = last trade at the settlement minute (6E / ZN
14:00, NQ / ES / YM 15:00, CL 13:30, GC 12:30 CT); exit = last trade at that minute on the session's trading day (Monday for
the Sunday open). Entry fills: (E0) the 17:00 open itself, (E5) the 17:05 open (the CL Sunday fade's MultiCharts-confirmed
fill); 1 tick slippage on entry and exit, $7.25 (ES $5) a round trip, 1 contract, 2018-2026.
Two gap definitions: (S) the user's, open vs prior SETTLEMENT (includes the 14:00-16:00 trading after the settle), and (T) the
paper's true gap, open vs the last trade before the break (16:00 CT, Friday's last for Sunday). Also shown: negative gaps faded (long; the paper says no effect), and every session's open -> settle short as the baseline.
  python3 analysis/fx_gap_fade_test.py [SCRATCH_DIR]
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import load, SPEC

SETTLE = {"6E": 1400, "ZN": 1400, "NQ": 1500, "ES": 1500, "YM": 1500, "CL": 1330, "GC": 1230}
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def sessions(sym):
    g = load(sym); pv, tick, comm = SPEC[sym]
    O = g.o.ravel(); cf = pd.Series(g.c.ravel()).ffill().to_numpy(); ts = pd.DatetimeIndex(g.ts)
    js = jof(SETTLE[sym]); has_s = ~np.isnan(g.c[:, js - 5:js + 1]).all(1)
    rows = []
    for d in range(1, g.D - 3):
        o0 = g.o[d, jof(1701)]
        if np.isnan(o0): continue
        prev = [r for r in range(d, max(d - 4, -1), -1) if has_s[r] and (r < d or True)]
        if not prev: continue
        r0 = prev[0]; settle0 = cf[r0 * 1440 + js]
        nxt = [r for r in range(d + 1, d + 4) if has_s[r]]
        if not nxt: continue
        r1 = nxt[0]; x = cf[r1 * 1440 + js]
        o5 = g.o[d, jof(1706)]
        last = cf[d * 1440 + jof(1659)]                                  # last trade before the 16:00-17:00 break (Friday's for Sunday)
        rows.append(dict(date=ts[r1], dow=DOW[ts[r1].dayofweek], gap=o0 / settle0 - 1, tgap=o0 / last - 1, o0=o0, o5=o5, x=x))
    df = pd.DataFrame(rows); df = df[df.date >= "2018-01-01"].reset_index(drop=True)
    for e in ("o0", "o5"):
        df[f"short_{e}"] = ((df[e] - df.x) - 2 * tick) * pv - comm      # short at entry, cover at settle
        df[f"long_{e}"] = ((df.x - df[e]) - 2 * tick) * pv - comm
    return df


def line(x, nm, w=40):
    x = x.dropna()
    if len(x) < 3: return f"   {nm:<{w}} n={len(x)}"
    y = pd.DatetimeIndex(x.index).year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():6.0f} PF {pf:4.2f} t {x.mean() / x.std() * np.sqrt(len(x)):+4.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${x[y < 2023].mean():6.0f} 23-26 ${x[y >= 2023].mean():6.0f}")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    for sym, ths in (("6E", (0.0005, 0.0010, 0.0015, 0.0020)), ("NQ", (0.0010, 0.0025)), ("ES", (0.0010, 0.0025)), ("YM", (0.0010, 0.0025)),
                     ("GC", (0.0010, 0.0025)), ("CL", (0.0010, 0.0025)), ("ZN", (0.0005, 0.0010))):
        df = sessions(sym).set_index("date")
        print(f"\n== {sym}: {len(df)} sessions; |gap| >= 0.10% on {np.mean(df.gap.abs() >= 0.001):.0%}; share of those on Monday "
              f"{np.mean(df[df.gap.abs() >= 0.001].dow == 'Mon'):.0%}")
        print(line(df.short_o5, "baseline: short every session (17:05)"))
        print(f"   true gap (T): |gap| >= 0.10% on {np.mean(df.tgap.abs() >= 0.001):.0%}; share on Monday {np.mean(df[df.tgap.abs() >= 0.001].dow == 'Mon'):.0%}")
        for (gcol, th) in [(c, t) for c in ("gap", "tgap") for t in ths]:
            up, dn = df[df[gcol] >= th], df[df[gcol] <= -th]
            print(f"  {'S (vs settlement)' if gcol == 'gap' else 'T (true gap)'} threshold {th:.2%}:")
            print(line(up.short_o0, "  up-gap short, fill 17:00 open"))
            print(line(up.short_o5, "  up-gap short, fill 17:05"))
            print("      by weekday (17:05): " + " | ".join(f"{k} n{len(v)} ${v.mean():+.0f}" for k, v in up.short_o5.groupby(up.dow)))
            print(line(dn.long_o5, "  down-gap long (fade), 17:05"))
