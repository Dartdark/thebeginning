"""Forced-flow round 4 (2026-10-13, from multi_strategy/FORCED_FLOWS.md): weekly options expiry Fridays,
MSCI quarterly review days, JPMorgan Hedged Equity collar reset.

W. Weekly (PM-settled) index options expire at Friday's close. Non-monthly Fridays vs the monthly 3rd
   Friday and other weekdays (SPX dailies since 2022, so split 2018-21 / 2022+).
   W1 afternoon size: |13:00 -> 15:00| / ATR (pinning = smaller)
   W2 follow / fade the 8:30 -> 13:00 move from 13:01 to 15:00
   W3 strike magnet: at 13:00, within 25 NQ points of a multiple of 100 (ES: 6 points of a 25) ->
      trade toward it, target the level, stop 0.15 ATR, out 15:00
   W4 Monday after: follow / fade Friday's 13:00 -> 15:00 move over Monday 8:30 -> 15:00
M. MSCI reviews take effect at the close of the last business day of Feb / May / Aug / Nov.
   M1 size of the last hour and the last 10 minutes vs other month-ends and normal days
   M2 follow the 8:30 -> 14:00 move into 15:00 (Late-Day Flow logic) on MSCI days vs other days
   M3 follow / fade the 8:30 -> 14:50 move over 14:51 -> 15:00
J. JPMorgan Hedged Equity (JHEQX) resets its SPX collar at the close of the last business day of each
   quarter (sells ~3-5% OTM calls). Estimated call strike = ES close at the previous reset x 1.04.
   J1 realized range in days -5..-1 vs +1..+5 vs normal
   J2 ES / NQ moves: day -5 close -> reset close, reset close -> day +3 close
   J3 pin: days -5..-1 with ES within 2% below the estimated strike -> short NQ 8:30 -> 15:00
   J4 release: long NQ days +1..+3 8:30 -> 15:00
Per NQ after $7.25 + 1 tick on entry and exit (raw windows) unless a stop / target is used.
  python3 analysis/forced_flows4_test.py [SCRATCH_DIR]
"""
import sys, warnings, pickle; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from news_meanrev_test import row, summ
from cta_volcontrol_test import rep, NT, PV

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def third_fri(ts):
    return (ts.dayofweek == 4) & (ts.day >= 15) & (ts.day <= 21)


def last_bday_flags(dts, months):
    s = pd.Series(np.arange(len(dts)), index=dts)
    last = s.groupby([dts.year, dts.month]).transform("max").to_numpy() == np.arange(len(dts))
    return last & np.isin(dts.month, months)


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); es = pickle.load(open(SP + "ge.pkl", "rb"))
    atr = g.daily_atr(15); tr = g.trading; dts = pd.DatetimeIndex(g.ts[tr]); A = atr[tr]
    c = lambda t: g.c[tr, jof(t)]; o = lambda t: g.o[tr, jof(t)]
    o830 = g.o[tr, 511]
    ei = pd.Series(np.arange(len(es.dates)), index=es.dates).reindex(g.dates[tr]).to_numpy()
    okk = ~np.isnan(ei); ei = np.where(okk, ei, 0).astype(int)
    ec = lambda t: np.where(okk, es.c[ei, jof(t)], np.nan)
    print(__doc__.split("\n")[0])

    # ------------------------------------------------------------------ W. weekly expiry Fridays
    fri = dts.dayofweek == 4; mfri = third_fri(dts); wfri = fri & ~mfri; other = dts.dayofweek < 4
    era = {"2018-21": dts.year <= 2021, "2022+": dts.year >= 2022}
    aft = (c(1500) - c(1300)) / A
    print("\nW1. |13:00 -> 15:00| / ATR (smaller = pinned):")
    for nm, m in (("weekly-expiry Fridays", wfri), ("monthly 3rd Fridays", mfri), ("Mon-Thu", other)):
        print("   " + nm.ljust(24) + " ".join(f"{e}: {np.nanmean(np.abs(aft[m & em])):.3f} (n={int((m & em).sum())})" for e, em in era.items()))
    mv = np.sign(c(1300) - o830); last2 = (c(1500) - o(1301)) * PV
    print("\nW2. 8:30 -> 13:00 direction, then 13:01 -> 15:00:")
    for nm, m in (("weekly Fridays", wfri), ("monthly Fridays", mfri), ("Mon-Thu", other)):
        for e, em in era.items():
            rep(f"{nm} {e}: follow", mv * last2, dts, m & em)
            rep(f"{nm} {e}: fade", -mv * last2, dts, m & em)
    print("\nW3. Strike magnet at 13:00 (NQ: within 25 points of a 100; target the level, stop 0.15 ATR, out 15:00):")
    for nm, m in (("weekly Fridays", wfri), ("monthly Fridays", mfri), ("Mon-Thu", other)):
        rows = []
        for k in np.where(m & (dts.year >= 2018))[0]:
            d = tr[k]; p = g.c[d, jof(1300)]
            if np.isnan(p) or np.isnan(atr[d]): continue
            lvl = round(p / 100) * 100; dist = lvl - p
            if abs(dist) > 25 or abs(dist) < 2: continue
            sd = int(np.sign(dist)); e = g.o[d, jof(1301)]
            if np.isnan(e) or (lvl - e) * sd <= 0: continue
            r = row(g, d, jof(1301), sd, jof(1500), e - sd * 0.15 * atr[d], lvl)
            if r: rows.append(r)
        t = pd.DataFrame(rows)
        print("   " + summ(t, nm, 30))
    fri_aft = np.sign(c(1500) - c(1300))
    mon = np.asarray(dts.dayofweek == 0)
    prev_fri = np.r_[False, wfri[:-1]]; prev_mfri = np.r_[False, mfri[:-1]]
    sig = np.r_[np.nan, fri_aft[:-1]]
    monday = (c(1500) - o830) * PV
    print("\nW4. Monday 8:30 -> 15:00 after an expiry Friday, vs Friday's 13:00 -> 15:00 direction:")
    for nm, m in (("after weekly expiry", mon & prev_fri), ("after monthly expiry", mon & prev_mfri)):
        rep(f"{nm}: follow Friday afternoon", sig * monday, dts, m)
        rep(f"{nm}: fade Friday afternoon", -sig * monday, dts, m)

    # ------------------------------------------------------------------ M. MSCI review days
    msci = last_bday_flags(dts, [2, 5, 8, 11]); mend = last_bday_flags(dts, [1, 3, 4, 6, 7, 9, 10, 12])
    print(f"\nM1. Size of the close (|move| / ATR); MSCI days n={int((msci & (dts.year >= 2018)).sum())}:")
    for nm, m in (("MSCI review days", msci), ("other month-ends", mend), ("all other days", ~msci & ~mend)):
        m = m & (dts.year >= 2018)
        print(f"   {nm:<20} 14:00->15:00 {np.nanmean(np.abs(c(1500) - c(1400))[m] / A[m]):.3f}"
              f" | 14:50->15:00 {np.nanmean(np.abs(c(1500) - c(1450))[m] / A[m]):.3f}")
    big = np.abs(c(1400) - o830) >= 0.4 * A; d14 = np.sign(c(1400) - o830)
    lh = (c(1500) - o(1401)) * PV
    print("\nM2. Late-Day Flow logic (|8:30->14:00| >= 0.4 ATR, follow to 15:00):")
    rep("MSCI days", d14 * lh, dts, msci & big); rep("other month-ends", d14 * lh, dts, mend & big)
    rep("all other days", d14 * lh, dts, ~msci & ~mend & big)
    d1450 = np.sign(c(1450) - o830); l10 = (c(1500) - o(1451)) * PV
    print("\nM3. Last 10 minutes (14:51 -> 15:00) vs the 8:30 -> 14:50 direction:")
    for nm, m in (("MSCI days", msci), ("other month-ends", mend)):
        rep(f"{nm}: follow", d1450 * l10, dts, m); rep(f"{nm}: fade", -d1450 * l10, dts, m)

    # ------------------------------------------------------------------ J. JPM collar reset
    qend = last_bday_flags(dts, [3, 6, 9, 12]); qi = np.where(qend)[0]
    e15 = pd.Series(ec(1500)).ffill().to_numpy(); n15 = pd.Series(c(1500)).ffill().to_numpy()
    rng_ = (np.nanmax(g.h[tr, 511:901], 1) - np.nanmin(g.l[tr, 511:901], 1)) / A
    print(f"\nJ. JPMorgan collar resets (quarter-ends) since 2018: {int((qend & (dts.year >= 2018)).sum())}")
    before = np.zeros(len(dts), bool); after = np.zeros(len(dts), bool); rel = np.full(len(dts), np.nan)
    strike = np.full(len(dts), np.nan)
    for a_, b_ in zip(qi[:-1], qi[1:]):
        k = e15[a_] * 1.04
        strike[a_ + 1:b_ + 1] = k
        before[max(a_ + 1, b_ - 5):b_] = True; after[b_ + 1:b_ + 6] = True
    yr = dts.year >= 2018
    print(f"   J1 day range / ATR: days -5..-1 {np.nanmean(rng_[before & yr]):.3f}, days +1..+5 {np.nanmean(rng_[after & yr]):.3f},"
          f" all days {np.nanmean(rng_[yr]):.3f}")
    rows = []
    for k_ in qi:
        if dts[k_].year < 2018 or k_ < 5 or k_ + 3 >= len(dts): continue
        rows.append(dict(date=dts[k_], es_pre=e15[k_] / e15[k_ - 5] - 1, es_post=e15[k_ + 3] / e15[k_] - 1,
                         nq_pre=(n15[k_] - n15[k_ - 5]) * PV, nq_post=(n15[k_ + 3] - n15[k_]) * PV,
                         dist=e15[k_] / strike[k_] - 1 if not np.isnan(strike[k_]) else np.nan))
    J = pd.DataFrame(rows)
    print(f"   J2 ES day -5 -> reset: mean {J.es_pre.mean():+.2%} (up {np.mean(J.es_pre > 0):.0%});"
          f" reset -> day +3: mean {J.es_post.mean():+.2%} (up {np.mean(J.es_post > 0):.0%}); n={len(J)}")
    print(f"      ES close at reset vs estimated call strike: median {J.dist.median():+.1%}; within 1% below: {np.mean((J.dist < 0) & (J.dist > -0.01)):.0%}")
    near = (e15 / strike - 1 > -0.02) & (e15 / strike - 1 < 0)
    near_prev = np.r_[False, near[:-1]]
    rth = (c(1500) - o830) * PV
    rep("J3 days -5..-1, ES within 2% below the est. strike (prev close): short NQ", -rth, dts, before & near_prev)
    rep("J3 control: days -5..-1, not near the strike: short NQ", -rth, dts, before & ~near_prev)
    rep("J4 days +1..+3 after the reset: long NQ", rth, dts, np.isin(np.arange(len(dts)), np.r_[[np.arange(i + 1, i + 4) for i in qi if i + 4 < len(dts)]].ravel()))
    print(f"\ncomparisons (rep): {NT[0]}; with this many, |t| >= 3 is the bar")

    # ------------------------------------------------------------------ follow-up: month-end close momentum
    print("\nF. Follow-up: month-end close momentum (all month-ends, MSCI included), robustness")
    allme = msci | mend
    for a_, b_ in ((1440, 1450), (1445, 1445), (1450, 1450), (1455, 1455)):
        sgn = np.sign(c(a_) - o830); pnl = (c(1500) - o(b_ + 1)) * PV
        rep(f"month-end: 8:30->{a_} direction, {b_ + 1}->15:00", sgn * pnl, dts, allme)
        rep(f"  control, other days: same window", sgn * pnl, dts, ~allme)
    # ES version
    e830 = np.where(okk, es.o[ei, 511], np.nan); e1450 = ec(1450); e1500 = ec(1500); e1451 = np.where(okk, es.o[ei, jof(1451)], np.nan)
    x = np.sign(e1450 - e830) * (e1500 - e1451) * 50 + 17.25 - (5 + 2 * 12.5)     # ES: $5 + 1 tick ($12.50) per fill
    rep("ES month-end: follow 8:30->14:50, 14:51->15:00 ($50/pt)", x, dts, allme)
    # day before / after month-end
    prev = np.r_[allme[1:], False]; nxt = np.r_[False, allme[:-1]]
    sgn = np.sign(c(1450) - o830); pnl = (c(1500) - o(1451)) * PV
    rep("day before month-end, same rule", sgn * pnl, dts, prev); rep("first day of the month, same rule", sgn * pnl, dts, nxt)
    print(f"comparisons (rep): {NT[0]}")
