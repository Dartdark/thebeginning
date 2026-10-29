"""Retail intensity -> overnight-minus-intraday gap, NQ / ES (paper: Ahn, Fan, Noh & Park 2026, 'Retail Ebb and Flow and the
Overnight-Intraday Return Gap', SSRN 4752520; user upload 2026-10-29). Paper (Korea 2009-23): months with above-median retail
share of volume are followed by a larger gap (4.10% vs 2.05% a month), because retail day traders buy the open and sell the
close. We have no retail flow for CME futures; pre-registered proxies from the CFTC COT report (`data/COT_index_nonrept.csv`,
legacy futures-only, CFTC public API): P1 = non-reportable (small-trader) share of E-mini open interest, (long + short) / 2 OI,
2016+; P2 = micro share of index exposure, micro OI / 10 / (E-mini OI + micro OI / 10), from 2020-08. Each minus its trailing
52-week mean (both trend). A Tuesday report is usable from the next Monday. Returns per contract: overnight 15:00 -> 08:30 CT,
intraday 08:30 -> 15:00, roll weeks (days 8-17 of Mar / Jun / Sep / Dec) out. Test: next-week and next-month mean daily gap
(overnight - intraday) when the proxy is above vs below its 52-week mean; trade = overnight long only in high-proxy weeks,
net of $7.25 NQ / $5 ES + 1 tick a side, vs every night.   python3 analysis/retail_gap_cot_test.py
"""
import glob, numpy as np, pandas as pd
cot = pd.read_csv("data/COT_index_nonrept.csv", parse_dates=["date"])
def proxies(big, micro):
    b = cot[cot.code == big].set_index("date"); m = cot[cot.code == micro].set_index("date")
    p1 = (b.nr_long + b.nr_short) / (2 * b.oi)
    p2 = (m.oi / 10 / (b.oi.reindex(m.index) + m.oi / 10)).dropna()
    out = {}
    for nm, p in (("P1 small-trader share", p1), ("P2 micro share", p2)):
        dev = (p - p.rolling(52, min_periods=26).mean()).dropna(); dev.index = dev.index + pd.Timedelta(days=6); out[nm] = dev
    return out
def tt(a, b):
    return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
for sym, pv, cost, big, micro in (("NQ", 20, 7.25 + 0.25 * 2 * 20, "209742", "209747"), ("ES", 50, 5.0 + 0.25 * 2 * 50, "13874A", "13874U")):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"data/{sym}_1min_20*.csv")) if "_ON_" not in f])
    o = d[d.time == 831].set_index("date").open; c = d[d.time == 1500].set_index("date").close
    x = pd.DataFrame(dict(o=o, c=c)).dropna(); x.index = pd.to_datetime(x.index.astype(str))
    x["on"] = (x.o - x.c.shift(1)) * pv; x["id"] = (x.c - x.o) * pv; x = x.dropna(); x = x[x.index >= "2018-01-01"]
    r = np.log(x.o / x.c.shift(1)).reindex(x.index); rw = x.index.month.isin([3, 6, 9, 12]) & (x.index.day >= 8) & (x.index.day <= 17)
    x = x[((r - r.mean()).abs() < 6 * r.std()) & ~rw]; x["gap"] = x.on - x.id
    print(f"\n{sym}: {len(x)} days 2018-26; every night overnight long net ${(x.on - cost).mean():+.0f}, gap ${x.gap.mean():+.0f}/day")
    for nm, dev in proxies(big, micro).items():
        wk = dev.reindex(x.index, method="ffill")                                  # latest usable report
        mo = dev.groupby(dev.index.to_period("M")).last().shift(1)                 # last value of the previous month
        mo = pd.Series(mo.reindex(x.index.to_period("M")).values, index=x.index)
        for h, s in (("week", wk), ("month", mo)):
            y = x[s.notna()]; hi = s[s.notna()] > 0
            on_hi, on_lo = y.on[hi] - cost, y.on[~hi] - cost
            print(f"   {nm:22s} next {h:5s}: high {hi.sum():4d} d gap ${y.gap[hi].mean():+5.0f} (on ${y.on[hi].mean():+4.0f} / id ${y.id[hi].mean():+4.0f}), "
                  f"low {(~hi).sum():4d} d gap ${y.gap[~hi].mean():+5.0f}; diff t {tt(y.gap[hi], y.gap[~hi]):+.1f};  "
                  f"overnight long high-only net ${on_hi.mean():+4.0f} t {on_hi.mean() / on_hi.std() * np.sqrt(len(on_hi)):+.1f} vs low ${on_lo.mean():+4.0f}")
        y = x[wk.notna()]; hi = wk[wk.notna()] > 0
        for per, m in (("2018-22", y.index < "2023-01-01"), ("2023+", y.index >= "2023-01-01")):
            a, b = y.gap[hi & m], y.gap[~hi & m]
            print(f"      weekly {per}: high gap ${a.mean():+5.0f} ({len(a)} d), low ${b.mean():+5.0f} ({len(b)} d), t {tt(a, b):+.1f}")
