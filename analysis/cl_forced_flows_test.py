"""Crude oil (CL) 2018-2026 (user's export, 2026-10-14): correlations and CL's own forced flows.

Data: data/CL_1min_<year>.csv, Central time, unadjusted continuous front month (it rolls before expiry: low $6.90 on
2020-04-21, not the -$37 print). CL: $1,000 a point, tick 0.01 ($10); $7.25 + 1 tick a fill = $27.25 a round trip;
MCL = 1/10. Pit / settlement 13:28-13:30 CT. Pre-specified tests (each with 2018-22 vs 2023-26), 1 CL:
  1. Correlations (daily 13:30 CT closes) CL vs NQ and GC, by year.
  2. EIA weekly petroleum report, 9:30 CT Wednesday (Thursday in weeks with a Monday-Wednesday federal holiday):
     a. size of the 9:30-9:35 move vs other days; b. pre-release drift 8:00 -> 9:29;
     c. follow / fade the first 5 minutes (9:30 -> 9:35), in at 9:36, out 10:30 or 13:29; d. only big reactions.
  3. Settlement flow: follow the 8:00 -> 13:00 move into 13:29 (CL's "late-day flow"); and 13:30 -> 14:30 after it.
  4. Commodity-index roll (S&P GSCI / BCOM roll the front month on business days 5-9 of the month): short the front
     8:00 -> 13:29 on roll days; the business days just before (front-running).
  5. Expiry: CL's last trade is 3 business days before the 25th (4 if the 25th is not a business day); the front-month
     session 8:00 -> 13:29 from 5 days before to the day after.
  6. Day of week (8:00 -> 13:29 session drift).
Placebo for anything that works: the same trade on random days of the same weekday.
  python3 analysis/cl_forced_flows_test.py [SCRATCH_DIR]
"""
import sys, os, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
from grid24 import Grid24, jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 1000.0, 0.01, 7.25
COST = COMM + 2 * TICK * PV
SPLIT = pd.Timestamp("2023-01-01")


def load(sym):
    pk = SP + f"{sym.lower()}.pkl"
    if os.path.exists(pk): return pickle.load(open(pk, "rb"))
    g = Grid24(f"data/{sym}_1min_20*.csv", night_pattern=""); pickle.dump(g, open(pk, "wb"), protocol=4); return g


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def line(x, nm, w=62):
    x = pd.Series(x).dropna()
    if len(x) < 5: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():5.0f} PF {pf:4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${x[y < 2023].mean():5.0f} 23-26 ${x[y >= 2023].mean():5.0f}")


def px(g, cf, rows, hhmm, kind="c"):
    if kind == "o":
        return pd.Series(g.o[rows, jof(hhmm)], index=pd.DatetimeIndex(g.ts[rows]))
    return pd.Series(cf[rows * 1440 + jof(hhmm)], index=pd.DatetimeIndex(g.ts[rows]))


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    cl = load("CL"); gc = load("GC"); g = pickle.load(open(SP + "g24.pkl", "rb"))
    rows = cl.trading[pd.DatetimeIndex(cl.ts[cl.trading]) >= pd.Timestamp("2018-01-01")]
    idx = pd.DatetimeIndex(cl.ts[rows]); cf = pd.Series(cl.c.ravel()).ffill().to_numpy()
    P = {h: px(cl, cf, rows, h) for h in (759, 929, 935, 1030, 1300, 1329, 1430)}
    O800 = px(cl, cf, rows, 801, "o")
    print(f"sessions {len(idx)} ({idx[0].date()} .. {idx[-1].date()}); median CL 8:00-13:30 range ${np.nanmedian(np.nanmax(cl.h[rows, jof(801):jof(1330)], 1) - np.nanmin(cl.l[rows, jof(801):jof(1330)], 1)) * PV:,.0f} per CL")

    print("\n1. Daily correlation (13:30 CT closes)")
    def closes(G):
        r = G.trading; c = pd.Series(pd.Series(G.c.ravel()).ffill().to_numpy()[r * 1440 + jof(1330)], index=pd.DatetimeIndex(G.ts[r])); return np.log(c).diff()
    J = pd.concat([closes(cl), closes(g), closes(gc)], axis=1, keys=["cl", "nq", "gc"]).dropna(); J = J[J.index >= "2018"]
    for a, b in (("cl", "nq"), ("cl", "gc"), ("gc", "nq")):
        print(f"   {a.upper()}-{b.upper()}: all {J[a].corr(J[b]):+.2f}; by year " + " ".join(f"{y}:{v:+.2f}" for y, v in J.groupby(J.index.year).apply(lambda d: d[a].corr(d[b])).items()))

    # EIA days
    hol = USFederalHolidayCalendar().holidays("2017-12-01", "2026-12-31")
    wk = idx.to_period("W")
    hol_wk = set(pd.DatetimeIndex(hol[(hol.dayofweek <= 2)]).to_period("W"))
    eia = ((idx.dayofweek == 2) & ~wk.isin(hol_wk)) | ((idx.dayofweek == 3) & wk.isin(hol_wk))
    eia = pd.Series(eia, index=idx)
    r5 = (P[935] - P[929]) * PV
    print(f"\n2. EIA report days: {eia.sum()} ({eia.mean():.0%} of sessions)")
    print(f"   |9:29 -> 9:35| ${r5.abs()[eia].median():,.0f} on EIA days vs ${r5.abs()[~eia].median():,.0f} on other days (median, per CL)")
    pre = (P[929] - O800) * PV
    print(line(pre[eia] - COST, "pre-release long 8:00 -> 9:29 (EIA days)"))
    print(line(-pre[eia] - COST, "pre-release short 8:00 -> 9:29 (EIA days)"))
    on = (O800 - P[1329].shift(1)) * PV
    print(line((np.sign(on) * pre)[eia] - COST, "pre-release: follow the overnight move, 8:00 -> 9:29"))
    s5 = np.sign(r5)
    for out, nm in ((1030, "10:30"), (1329, "13:29")):
        fw = (P[out] - P[935]) * PV
        print(line((s5 * fw)[eia] - COST, f"follow the first 5 minutes, 9:36 -> {nm}"))
        print(line((-s5 * fw)[eia] - COST, f"fade the first 5 minutes, 9:36 -> {nm}"))
        big = r5.abs() >= r5.abs()[eia].expanding(20).median().shift(1).reindex(idx).ffill()
        print(line((s5 * fw)[eia & big] - COST, f"   follow, big reactions only (above the running median), to {nm}"))
        print(line((-s5 * fw)[eia & big] - COST, f"   fade, big reactions only, to {nm}"))
        print(line((s5 * fw)[~eia] - COST, f"   control: follow 9:30-9:35 on non-EIA days, to {nm}"))

    print("\n3. Settlement flow")
    m13 = (P[1300] - O800); f13 = (P[1329] - P[1300]) * PV; a13 = (P[1430] - P[1329]) * PV
    print(line(np.sign(m13) * f13 - COST, "follow 8:00 -> 13:00 into 13:29, every day"))
    big = m13.abs() >= m13.abs().expanding(60).quantile(0.67).shift(1)
    print(line((np.sign(m13) * f13 - COST)[big], "   only when the day's move is in its top third"))
    print(line(-np.sign(m13) * f13 - COST, "fade 8:00 -> 13:00 into 13:29"))
    m_s = (P[1329] - O800)
    print(line(-np.sign(m_s) * a13 - COST, "after settlement: fade the day 13:30 -> 14:30"))
    print(line(np.sign(m_s) * a13 - COST, "after settlement: follow the day 13:30 -> 14:30"))

    print("\n4. Commodity-index roll (business days 5-9 of the month)")
    bd = CustomBusinessDay(holidays=hol)
    bdn = pd.Series(0, index=idx)
    for mth, grp in pd.Series(idx, index=idx).groupby(idx.to_period("M")):
        days_m = pd.date_range(mth.start_time, mth.end_time, freq=bd)
        pos = {d: i + 1 for i, d in enumerate(days_m)}
        for d in grp: bdn[d] = pos.get(d, 0)
    sess = (P[1329] - O800) * PV
    print(line(-sess[bdn.between(5, 9)] - COST, "short 8:00 -> 13:29 on roll days (BD 5-9)"))
    print(line(-sess[bdn.between(1, 4)] - COST, "short on BD 1-4 (front-running the roll)"))
    print(line(sess[bdn >= 10] - COST, "   reference: long on BD 10+"))
    print(line(-sess[(bdn < 5) | (bdn > 9)] - COST, "   reference: short on non-roll days"))

    print("\n5. Around CL expiry (last trade = 3 business days before the 25th)")
    exp = []
    for mth in pd.period_range("2018-01", "2026-12", freq="M"):
        d25 = pd.Timestamp(mth.year, mth.month, 25)
        base = d25 if bd.is_on_offset(d25) else d25 - bd
        exp.append(base - 3 * bd)
    exp = pd.DatetimeIndex(exp)
    rel = pd.Series(np.nan, index=idx)
    for e in exp:
        for k in range(-5, 2):
            d = e + k * bd
            if d in rel.index: rel[d] = k
    for k in range(-5, 2):
        x = sess[rel == k]
        print(f"   expiry day {k:+d}: n {len(x)} long avg ${x.mean():5.0f} t {tstat(x):4.1f} | |move| ${x.abs().median():,.0f} (all days ${sess.abs().median():,.0f})")

    print("\n6. Day of week, 8:00 -> 13:29 session, long")
    for dw, nm in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri")):
        print(line(sess[idx.dayofweek == dw] - COST, f"long {nm}"))
    pickle.dump(dict(P=P, eia=eia, bdn=bdn, rel=rel), open(SP + "cl_flows.pkl", "wb"))

    print("\n7. The best line (short on business days 1-4, front-running the index roll): metrics, longs n/a (short only), placebo")
    x = (-sess[bdn.between(1, 4)] - COST).dropna(); days = idx
    print(M.table({"short CL BD 1-4": (x.reindex(days, fill_value=0.0), x)}))
    b_, p_ = R.report({"short CL BD 1-4, 2023+": x.reindex(days, fill_value=0.0)[days >= SPLIT]}, n=3000); print(b_); print(p_)
    rng = np.random.default_rng(4); pool = (-sess - COST).dropna()
    pl = [pool.sample(len(x), random_state=int(rng.integers(1e9))).mean() for _ in range(2000)]
    print(f"   placebo (short on {len(x)} random sessions, 2,000 draws): ${np.mean(pl):.0f}, 95th percentile ${np.percentile(pl, 95):.0f}, share >= real {np.mean(np.array(pl) >= x.mean()):.1%}")
    print("   by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in x.groupby(x.index.year).sum().items()))
