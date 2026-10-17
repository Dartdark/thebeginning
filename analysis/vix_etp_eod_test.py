"""VIX-ETP end-of-day rebalancing (Bangsgaard & Kokholm, SSRN 4470636; J. Banking & Finance 2025): VIX ETPs rebalance VIX
futures up to 16:15 ET (15:15 CT); dealers hedge by trading S&P futures in the direction of the day's move (VIX up on
down days -> ETPs buy VIX futures -> dealers short VIX futures, sell SPX futures), predicting the 16:05-16:15 ET return.
PRE-REGISTERED (2026-10-17): no intraday VIX data, so the day's index move proxies the VIX move (strongly opposite).
  A  follow: day move = 15:04 close - 8:30 open (CT); if |move| >= k x 15-day ATR (k = 0.3 / 0.5 / 1.0), trade with it at
     the 15:05 open, out at the 15:15 close, no stop; ES and NQ; one trade a day; skip early-close days (no 15:15 bar)
  B  ES MOC follow (14:51 -> 15:00, funded candidate) held to 15:15 instead of 15:00
  placebo: the same rule 15:20 -> 15:30 (rebalancing done) and 13:05 -> 13:15 (no flow)
Costs: ES $5 + 1 tick a fill ($12.50), NQ $7.25 + 1 tick a fill ($5); per contract.
  python3 analysis/vix_etp_eod_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"ES": ("ge.pkl", 50.0, 0.25, 5.0), "NQ": ("g24.pkl", 20.0, 0.25, 7.25)}


def tstat(x): x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def run(g, pv, tick, comm, k, ref0, dec, ent, ex, side_from=None):
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2018-01-01"]; atr = g.daily_atr(15)[tr]
    cf = pd.DataFrame(g.c[tr]).ffill(axis=1).to_numpy()
    full = g.last_j[tr] >= jof(ex)
    o0 = g.o[tr, jof(ref0)]; dc = cf[:, jof(dec)]; mv = dc - o0
    eo = g.o[tr, jof(ent)]; xc = cf[:, jof(ex)]
    m = full & (np.abs(mv) >= k * atr) & ~np.isnan(eo) & ~np.isnan(o0)
    s = np.sign(mv)
    net = (s * (xc - eo) - 2 * tick) * pv - comm
    t = pd.Series(net[m], index=pd.DatetimeIndex(g.ts[tr][m])); side = pd.Series(s[m], index=t.index)
    return t, side


def line(t, side, nm):
    y = t.index.year; a, b = t[y < 2023], t[y >= 2023]; by = t.groupby(y).sum()
    pf = t[t > 0].sum() / max(1e-9, -t[t < 0].sum())
    return (f"   {nm:<44} n {len(t):4d} avg ${t.mean():6.1f} PF {pf:4.2f} t {tstat(t):+4.1f} yrs+ {(by > 0).sum()}/{len(by)} | "
            f"18-22 ${a.mean():6.1f} (t {tstat(a):+4.1f}) 23+ ${b.mean():6.1f} (t {tstat(b):+4.1f}) | L ${t[side > 0].mean():6.1f} S ${t[side < 0].mean():6.1f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    res = {}
    for sym, (f, pv, tick, comm) in SPEC.items():
        g = pickle.load(open(SP + f, "rb"))
        print(f"\n{sym} (per contract, net):")
        for k in (0.3, 0.5, 1.0):
            t, s = run(g, pv, tick, comm, k, 831, 1504, 1506, 1515); res[(sym, k)] = (t, s)
            print(line(t, s, f"A follow day move >= {k} ATR, 15:05 -> 15:15"))
        for nm, (dec, ent, ex) in (("placebo 15:20 -> 15:30", (1519, 1521, 1530)), ("placebo 13:05 -> 13:15", (1304, 1306, 1315))):
            t, s = run(g, pv, tick, comm, 0.5, 831, dec, ent, ex); print(line(t, s, f"{nm} (k 0.5)"))
        if sym == "ES":
            t, s = run(g, pv, tick, comm, 0.3, 1401, 1450, 1451, 1515)
            print(line(t, s, "B MOC follow held 14:51 -> 15:15 (ref 14:00)"))
            t2, s2 = run(g, pv, tick, comm, 0.3, 1401, 1450, 1451, 1500)
            print(line(t2, s2, "  (MOC follow 14:51 -> 15:00, no stop, same calc)"))
    # standard metrics + Monte Carlo for the pre-registered middle setting on ES
    t, s = res[("ES", 0.5)]; days = pd.bdate_range("2018-01-01", t.index.max())
    dl = t.groupby(t.index.normalize()).sum().reindex(days, fill_value=0)
    print("\n" + M.table({"ES VIX-ETP follow k 0.5, per ES": (dl, t), "  longs": (t[s > 0].groupby(t[s > 0].index.normalize()).sum().reindex(days, fill_value=0), t[s > 0]),
                          "  shorts": (t[s < 0].groupby(t[s < 0].index.normalize()).sum().reindex(days, fill_value=0), t[s < 0])}))
    print(MC.report(t.to_numpy(), dl.to_numpy(), size=0.2, label="at 2 MES"))
