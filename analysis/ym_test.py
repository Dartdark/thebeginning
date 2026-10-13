"""YM (Dow futures) vs NQ (user's export, 2026-10-13): correlation, and the plan's strategies on YM.

Data: data/YM_1min_<year>.csv, full-day 1-minute bars, Central time (16:00-17:00 break), Dec 2017 - Oct 2026.
YM: $5 a point, tick 1 point; costs $5 a round trip + 1 tick per market / stop fill. The shared strategy code fills
with a 0.25-point slip, so the missing 0.75 point a fill (x 2 fills x $5 = $7.50) is added to the cost.
  1. Correlation NQ vs YM: daily (8:30 -> 15:00 and close to close), by year; 30-minute intraday; big days; days
     they move in opposite directions.
  2. The plan's strategies (Python versions) on YM vs NQ, 2018-2026 (2018-22 / 2023-26 shown): EOS, Monday Long, NFP Fade, Late-Day Flow
     (forced flows, ATR-relative stops), Overnight Bias ADX30 (ATR stop), Vault Break and the Bridge Monday Long (their
     point targets / stops scaled by the YM / NQ daily-range ratio).
  3. Daily P&L correlation of each strategy NQ vs YM, and the funded bench with YM versions added (MYM = YM / 10).
  python3 analysis/ym_test.py [SCRATCH_DIR]
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24, jof
import es_forced_flows_test as ESF
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
YPV, YCOST = 5.0, 5.0 + 7.5
START = pd.Timestamp("2018-01-02")


def rth_close(G):
    c = pd.DataFrame(G.c[:, :jof(1500) + 1]).ffill(axis=1).iloc[:, -1].to_numpy()
    o = G.o[:, jof(831)]
    ts = pd.DatetimeIndex(G.ts); keep = np.isin(np.arange(G.D), G.trading)
    return pd.DataFrame({"o": o[keep], "c": c[keep]}, index=ts[keep])


def reprice(t, pv, cost):
    t = t.copy(); t["net"] = (t.exit - t.entry) * t.side * pv - cost; t["date"] = pd.to_datetime(t.date)
    return t[t.date >= START].reset_index(drop=True)


def line(t, nm, w=30):
    if len(t) < 3: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum()
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"{nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():6.0f} PF {pf:.2f} t={x.mean() / x.std() * np.sqrt(len(x)):4.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${x[y < 2023].mean():5.0f} 23-26 ${x[y >= 2023].mean():5.0f}"
            f" | L ${x[t.side > 0].mean():5.0f} S ${x[t.side < 0].mean():5.0f}")


if __name__ == "__main__":
    pk = SP + "gy.pkl"
    if os.path.exists(pk): gy = pickle.load(open(pk, "rb"))
    else:
        gy = Grid24("data/YM_1min_20*.csv", night_pattern=""); pickle.dump(gy, open(pk, "wb"), protocol=4)
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
    print(__doc__.split("\n")[0])
    a, b = rth_close(g), rth_close(gy)
    D = a.join(b, lsuffix="_nq", rsuffix="_ym", how="inner").dropna(); D = D[D.index >= START]
    cc = D[["c_nq", "c_ym"]].pct_change().dropna(); rth = pd.DataFrame({"nq": D.c_nq / D.o_nq - 1, "ym": D.c_ym / D.o_ym - 1})
    print(f"\n1. Correlation, {len(D)} common sessions {D.index[0].date()} .. {D.index[-1].date()}")
    print("   daily close-to-close:", cc.groupby(cc.index.year).corr().xs("c_ym", level=1)["c_nq"].round(2).to_dict(), "all", round(cc.corr().iloc[0, 1], 2))
    print("   regular session 8:30 -> 15:00:", rth.groupby(rth.index.year).corr().xs("ym", level=1)["nq"].round(2).to_dict(), "all", round(rth.corr().iloc[0, 1], 2))
    for G, nm in ((g, "nq"), (gy, "ym")): pass
    b30 = {nm: G.bars(30) for G, nm in ((g, "nq"), (gy, "ym"))}
    def r30(G, bb):
        ts = pd.DatetimeIndex(G.ts); c = pd.DataFrame(bb["c"][:, jof(900) // 30:jof(1500) // 30 + 1], index=ts)
        return np.log(c).diff(axis=1)
    x, y = r30(g, b30["nq"]), r30(gy, b30["ym"]); idx = x.index.intersection(y.index); idx = idx[idx >= START]
    xv, yv = x.loc[idx].values.ravel(), y.loc[idx].values.ravel(); m = ~np.isnan(xv) & ~np.isnan(yv)
    print(f"   30-minute returns 9:00-15:00: {np.corrcoef(xv[m], yv[m])[0, 1]:.2f}")
    big = rth[rth.nq.abs() > 0.015]
    print(f"   on big NQ days (|8:30->15:00| > 1.5%, n {len(big)}): correlation {big.corr().iloc[0, 1]:.2f}; YM same direction {np.mean(np.sign(big.nq) == np.sign(big.ym)):.0%};"
          f" YM move / NQ move {np.median(big.ym / big.nq):.2f}")
    print(f"   all days: opposite direction {np.mean(np.sign(rth.nq) != np.sign(rth.ym)):.0%}; regular-session volatility YM / NQ {rth.ym.std() / rth.nq.std():.2f}")
    print(f"   down days NQ < -1%: YM down too {np.mean(rth[rth.nq < -0.01].ym < 0):.0%}, YM fell less {np.mean(rth[rth.nq < -0.01].ym > rth[rth.nq < -0.01].nq):.0%}")

    # 2. strategies
    atr_n, atr_y = g.daily_atr(15), gy.daily_atr(15)
    rows = [d for d in gy.trading if pd.Timestamp(gy.ts[d]) >= START]
    ratio = np.nanmedian(atr_y[rows]) / np.nanmedian(atr_n[[d for d in g.trading if pd.Timestamp(g.ts[d]) >= START]])
    print(f"\n2. The plan's strategies 2018-2026 (YM / NQ daily range ratio {ratio:.2f}, used to scale point targets / stops)")
    SN = ESF.strategies(g, es, "NQ"); SN = {k: reprice(v, 20.0, 7.25) for k, v in SN.items()}
    ESF.SPEC["YM"] = (YPV, YCOST)
    SY = ESF.strategies(gy, es, "YM"); SY = {k: reprice(v, YPV, YCOST) for k, v in SY.items()}
    from candidates24 import overnight_bias24
    on_n = reprice(overnight_bias24(g, adx_min=30, stop_atr=0.25), 20.0, 7.25)
    on_y = reprice(overnight_bias24(gy, adx_min=30, stop_atr=0.25), YPV, YCOST)
    import vault_break_v8_test as VB
    vb_n = reprice(VB.run(g, "v1"), 20.0, 7.25)
    vb_y = reprice(VB.run(gy, "v1", tp=40 * ratio, sl=75 * ratio), YPV, YCOST)
    import bridge_monday_long_test as BM
    bm_n = reprice(BM.bridge(g, BM.bridge_adx(g)), 20.0, 7.25)
    bm_y = reprice(BM.bridge(gy, BM.bridge_adx(gy), target=100 * ratio), YPV, YCOST)
    PAIRS = {"Vault Break": (vb_n, vb_y), "ONB ADX30": (on_n, on_y), "EOS": (SN["EOS"], SY["EOS"]), "Monday Long": (SN["MON"], SY["MON"]),
             "NFP Fade": (SN["NFP"], SY["NFP"]), "Late-Day Flow": (SN["LDF"], SY["LDF"]), "Bridge Monday": (bm_n, bm_y)}
    days = D.index
    dl = lambda t: t.groupby(t.date.dt.normalize()).net.sum().reindex(days, fill_value=0.0)
    for nm, (tn, ty) in PAIRS.items():
        print(line(tn, f"{nm} NQ")); print(line(ty, f"{nm} YM"))
        dn, dy = dl(tn), dl(ty); both = (dn != 0) & (dy != 0)
        print(f"   {'':30} daily P&L correlation NQ vs YM (days both trade): {np.corrcoef(dn[both], dy[both])[0, 1]:.2f}")
    print("\n   Standard metrics per contract (YM), 2018-2026:")
    print(M.table({f"{nm} YM": (dl(ty), ty.net) for nm, (tn, ty) in PAIRS.items()}))
    pickle.dump(dict(PAIRS=PAIRS, ratio=ratio), open(SP + "ym_pairs.pkl", "wb"))
