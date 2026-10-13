"""The plan's forced-flow strategies on ES (2026-10-13): does the same edge exist in the S&P future?

Python versions of Expiration Open Short (EOS), Monday Long (MON), NFP Fade (NFP), Late-Day Flow (LDF)
and Vol-Control Sell Flow (VCS), run identically on NQ and ES 1-minute data. ES: $50 a point, $5
costs, 1 tick (0.25 pt) per market/stop fill; NQ: $20 a point, $7.25, 1 tick. 2018-2026.
Then: daily correlation NQ vs ES per strategy, and whether splitting each strategy between NQ and ES
(half NQ + the same dollar notional in ES) improves the risk-adjusted result vs NQ alone.
  python3 analysis/es_forced_flows_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from news_meanrev_test import row, reaction_trades
import event_days as E, metrics as M
import addon_combo_test as A

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
CLOSED_FRI = pd.to_datetime(["2019-04-19", "2022-04-15", "2025-04-18", "2026-06-19"])
SPEC = {"NQ": (20.0, 7.25), "ES": (50.0, 5.0)}


def reprice(t, pv, cost):
    if len(t) == 0: return t
    t = t.copy(); t["net"] = (t.exit - t.entry) * t.side * pv - cost
    return t


def simple(G, days, side, j0, j1, stop_atr, atr):
    rows = []; ts = pd.DatetimeIndex(G.ts)
    for d in days:
        if ts[d].year < 2018 or np.isnan(atr[d]) or np.isnan(G.o[d, j0]): continue
        e = G.o[d, j0] + side * 0.25
        r = row(G, d, j0, side, j1, e - side * stop_atr * atr[d], None)
        if r: rows.append(r)
    return pd.DataFrame(rows)


def strategies(G, es, name):
    atr = G.daily_atr(15); tr = G.trading; ts = pd.DatetimeIndex(G.ts[tr])
    pv, cost = SPEC[name]
    # EOS: third Friday (Thursday before a closed Friday), short 8:30 -> 10:00, stop 0.3 ATR
    thu_before = ts.dayofweek == 3
    thu_before &= np.isin((ts + pd.Timedelta(days=1)).normalize(), CLOSED_FRI)
    exp = ((ts.dayofweek == 4) & (ts.day >= 15) & (ts.day <= 21) & ~np.isin(ts.normalize(), CLOSED_FRI)) | thu_before
    out = {"EOS": simple(G, tr[exp], -1, 511, jof(1000), 0.30, atr),
           "MON": simple(G, tr[ts.dayofweek == 0], 1, 511, jof(1500), 0.50, atr)}
    rel = E.release_days(G); tsr = pd.DatetimeIndex(G.ts[rel])
    out["NFP"] = reaction_trades(G, rel[(tsr.dayofweek == 4) & (tsr.day <= 10)], 730, 745, 900, "fade", stop_k=0.5, atr=atr)
    rows = []
    for d in tr:
        if pd.Timestamp(G.ts[d]).year < 2018 or np.isnan(atr[d]): continue
        o0, c14 = G.o[d, 511], G.c[d, jof(1400)]
        if np.isnan(o0) or np.isnan(c14) or np.isnan(G.c[d, jof(1430)]): continue
        if abs(c14 - o0) < 0.4 * atr[d]: continue
        sd = int(np.sign(c14 - o0)); e = G.o[d, jof(1401)]
        if np.isnan(e): continue
        r = row(G, d, jof(1401), sd, jof(1430), e + sd * 0.25 - sd * 0.25 * atr[d], None)
        if r: rows.append(r)
    out["LDF"] = pd.DataFrame(rows)
    out["VCS"] = A.vcs_trades(G, es, atr)
    return {k: reprice(v, pv, cost) for k, v in out.items()}


def line(t, nm, w=10):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); h = x[y >= 2023]
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    return (f"{nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():5.0f} PF {pf(x):.2f}"
            f" t={x.mean() / x.std() * np.sqrt(len(x)):4.1f} yrs+ {(by > 0).sum()}/{len(by)} | 23+ ${h.mean():5.0f} PF {pf(h):.2f}")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
    print(__doc__.split("\n")[0])
    S = {"NQ": strategies(g, es, "NQ"), "ES": strategies(es, es, "ES")}
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(t.date.dt.normalize()).net.sum().reindex(days, fill_value=0.0)
    # dollar notional of 1 NQ / 1 ES per day (15:00 close of the previous day)
    def px(G):
        p = pd.Series(G.c[G.trading, 900], index=pd.DatetimeIndex(G.ts[G.trading])).ffill()
        return p.shift(1).reindex(days).ffill()
    ratio = (px(g) * 20) / (px(es) * 50)                        # ES contracts per NQ of notional
    print(f"\nES contracts with the notional of 1 NQ: median {ratio.median():.2f}")
    print("\n1. Per contract, Python versions (NQ and ES):")
    rows_m = {}
    for k in ("EOS", "MON", "NFP", "LDF", "VCS"):
        print(line(S["NQ"][k], f"{k} NQ")); print(line(S["ES"][k], f"{k} ES"))
        dn, de = dl(S["NQ"][k]), dl(S["ES"][k])
        both = (dn != 0) & (de != 0)
        print(f"           daily P&L correlation NQ vs ES on days both trade: {np.corrcoef(dn[both], de[both])[0, 1]:.2f}")
        rows_m[f"{k}: 1 NQ"] = (dn, None)
        rows_m[f"{k}: ES, same notional"] = (de * ratio, None)
        rows_m[f"{k}: half NQ + half ES"] = (0.5 * dn + 0.5 * de * ratio, None)
    print("\n2. NQ alone vs ES alone vs split (same total notional), daily P&L 2018-26:")
    print(M.table(rows_m))
    pn = sum(dl(S["NQ"][k]) for k in S["NQ"]); pe = sum(dl(S["ES"][k]) * ratio for k in S["ES"])
    print("\n3. All five together (1 NQ each vs ES of the same notional vs half / half):")
    print(M.table({"five on NQ": (pn, None), "five on ES": (pe, None), "five, half NQ + half ES": (0.5 * pn + 0.5 * pe, None)}))
    for nm, x in (("NQ", pn), ("ES", pe)):
        print(f"   {nm} by year:", x.groupby(x.index.year).sum().round(0).astype(int).to_dict())
