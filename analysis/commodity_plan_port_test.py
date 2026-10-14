"""The plan's strategies on crude oil (CL) and gold (GC), 2018-2026 (user's request 2026-10-14; YM version: analysis/ym_test.py).

The shared strategy code fills with a 0.25-point slip (one NQ tick), so prices are rescaled to make one tick = 0.25:
CL x 25 (0.01 -> 0.25, $40 a scaled point), GC x 2.5 (0.10 -> 0.25, $40 a scaled point). ATR-relative stops are
unchanged by the scaling; point targets / stops (Vault Break, Bridge Monday) are scaled by the CL / GC vs NQ daily-range
ratio. Costs $7.25 + 1 tick per fill, 1 contract (MCL / MGC = 1/10).
Strategies (Python versions, as on YM): Vault Break, Overnight Bias ADX30 (ATR stop), EOS (equity expiry Fridays),
Monday Long, NFP Fade, Late-Day Flow (14:00 -> 14:30 after a big 8:30 -> 14:00 move), Bridge Monday Long.
Note the equity-session timing (8:30 open, 14:00) doesn't match CL's 8:00-13:30 pit hours; NFP (7:30 CT) applies to all.
  python3 analysis/commodity_plan_port_test.py [SCRATCH_DIR]
"""
import sys, copy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import es_forced_flows_test as ESF
import metrics as M
from ym_test import reprice, line
from cl_forced_flows_test import load

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SCALE = {"CL": (25.0, 1000.0 / 25.0), "GC": (2.5, 100.0 / 2.5)}
START = pd.Timestamp("2018-01-02")


def scaled(G, k):
    H = copy.copy(G)
    for a in ("o", "h", "l", "c"): setattr(H, a, getattr(G, a) * k)
    return H


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
    atr_n = g.daily_atr(15); rows_n = [d for d in g.trading if pd.Timestamp(g.ts[d]) >= START]
    SN = {k: reprice(v, 20.0, 7.25) for k, v in ESF.strategies(g, es, "NQ").items()}
    from candidates24 import overnight_bias24
    import vault_break_v8_test as VB, bridge_monday_long_test as BM
    base = {"Vault Break": reprice(VB.run(g, "v1"), 20.0, 7.25), "ONB ADX30": reprice(overnight_bias24(g, adx_min=30, stop_atr=0.25), 20.0, 7.25),
            "EOS": SN["EOS"], "Monday Long": SN["MON"], "NFP Fade": SN["NFP"], "Late-Day Flow": SN["LDF"],
            "Bridge Monday": reprice(BM.bridge(g, BM.bridge_adx(g)), 20.0, 7.25)}
    ALL = {}
    for sym in ("CL", "GC"):
        k, pv = SCALE[sym]
        G = scaled(load(sym), k)
        atr = G.daily_atr(15); rows = [d for d in G.trading if pd.Timestamp(G.ts[d]) >= START]
        ratio = np.nanmedian(atr[rows]) / np.nanmedian(atr_n[rows_n])
        ESF.SPEC[sym] = (pv, 7.25)
        S = {kk: reprice(v, pv, 7.25) for kk, v in ESF.strategies(G, es, sym).items()}
        T = {"Vault Break": reprice(VB.run(G, "v1", tp=40 * ratio, sl=75 * ratio), pv, 7.25),
             "ONB ADX30": reprice(overnight_bias24(G, adx_min=30, stop_atr=0.25), pv, 7.25),
             "EOS": S["EOS"], "Monday Long": S["MON"], "NFP Fade": S["NFP"], "Late-Day Flow": S["LDF"],
             "Bridge Monday": reprice(BM.bridge(G, BM.bridge_adx(G), target=100 * ratio), pv, 7.25)}
        print(f"\n=== {sym} (daily range vs NQ: {ratio:.2f} scaled points per NQ point; 1 {sym} = ${pv:.0f} a scaled point)")
        for nm in T:
            print(line(base[nm], f"{nm} NQ")); print(line(T[nm], f"{nm} {sym}"))
        days = pd.DatetimeIndex(G.ts[rows])
        dl = lambda t: t.groupby(pd.to_datetime(t.date).dt.normalize()).net.sum().reindex(days, fill_value=0.0)
        tab = {}
        for nm, t in T.items():
            if len(t) < 10: continue
            tab[f"{nm} {sym}"] = (dl(t), t.net)
            tab[f"  longs"] = (dl(t[t.side > 0]), t.net[t.side > 0]); tab[f"  shorts"] = (dl(t[t.side < 0]), t.net[t.side < 0])
            print(M.table({f"{nm} {sym}": tab[f"{nm} {sym}"], "  longs": tab["  longs"], "  shorts": tab["  shorts"]}).split("\n", 1)[1])
        ALL[sym] = T
    pickle.dump(ALL, open(SP + "commodity_port.pkl", "wb"))
