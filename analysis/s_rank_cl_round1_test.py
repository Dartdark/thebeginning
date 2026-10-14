"""S-rank program, CL round 1 (2026-10-14): crude oil's scheduled flows from S_RANK_PROGRAM.md, looking for an S strategy.

Data: data/CL_1min_<year>.csv (Grid24, CT, full 24-hour days; rows = calendar dates, so Sunday-evening bars sit on the
Sunday row). The export is an unadjusted continuous front month that switches contract at ~03:32 CT two business days
before the front's last trade (detected below from the 03:30 -> 03:33 jumps); nothing here holds through that minute.
CL: $1,000 a point, tick 0.01 ($10); $7.25 + 1 tick per market / stop fill (limit targets: no tick); MCL = 1/10.
Entries at a bar open +/- 1 tick, stops fill at the stop or the worse bar open - 1 tick, time exits at a bar close -
1 tick. Apex: flat by 15:59 CT; an overnight trade enters after the 17:00 reopen and counts for the next trading day.
Sizes and thresholds are in units of the 15-day ATR. Design 2018-22, holdout 2023-26; picks by 2018-22 t only.
"x-Apr20" = average without April 2020 (negative-price month; the front had already rolled, low $6.90).
  1. API weekly inventory report, Tuesday 15:30 CT (Wednesday if Monday / Tuesday is a federal holiday):
     a. size of the 15:30 -> 15:35 move vs other days; b. follow / fade the first 5 / 10 / 15 minutes to 15:58;
     c. follow / fade the 15:30 -> 15:58 reaction overnight: in at the 17:01 reopen, out Wednesday 8:00 / 9:00 / 9:29
        (before EIA at 9:30); d. pre-API drift Tuesday 13:30 -> 15:29, and the overnight drift into EIA (17:01 -> 9:29).
     Controls: the same rules on the other weekdays.
  2. Commodity-index roll refined (S&P GSCI rolls business days 5-9, BCOM 6-10; the index funds sell the front):
     short by business-day group (1-4, 5-9, 6-10, 11+, each day 1-12) in four windows: night 17:01 -> 8:00,
     day 8:01 -> 13:29, roll hour 12:31 -> 13:29 (the roll trades at the 13:28-13:30 settlement), after 13:31 -> 15:58.
  3. Sunday-open gap (Sunday 17:00 open vs Friday's last price): fade / follow, in at 17:01 or 17:05, out Monday 8:00 /
     10:00 / 13:29, |gap| >= 0 / 0.1 / 0.25 ATR, stop none / 0.5 / 1 ATR. Placebo: the weekday 17:00 reopen gaps.
  3b. Robustness of the pick: entry 17:01..21:00 x exit 8:00..13:29, gap measured at 17:01 vs at the entry bar,
     threshold 0..0.5 ATR, longs (fading down-gaps) / shorts (fading up-gaps), concentration (best 5 trades), placebos:
     random side on the same Sundays, the Mon-Thu 17:00 reopen gap (same share of days), fading Friday's 8:00-15:58 move.
     Then full metrics, bootstrap / permutation on 2023+ for whole / longs / shorts.
  4. a. Baker Hughes rig count Friday 12:00 CT: move size, follow / fade the first 5 / 10 / 15 minutes to 13:29 /
        15:58, pre-release drift 11:00 -> 11:59 (control: Thursday).
     b. WTI (LO) options expiry, tested on two dates (CME's rule changed over the years): futures last trade (LTD) - 3
        and LTD - 1 business days. 12:00 -> 13:29 long / short / follow the morning; settlement pinning (distance of
        the 13:29 price to the nearest $0.50 strike, 12:00-13:30 range) and "go toward the nearest strike" vs other days.
        Note LTD - 1 is after the export's roll, so there the series is the second month, not the expiring one.
     c. Overnight Bias for CL: position of the 8:00 price in the overnight range (from 17:00 or 23:00), top / bottom
        third -> long / short; entry at the 8:01 open or on a stop at the 8:00-8:15 range; ADX(14, 15-min) none / > 20 /
        > 30; stop 0.25 / 0.5 ATR, target 3R, out 13:29.
Promotion: t >= 2.5 over 2018-26 (after costs) and positive in both 2018-22 and 2023-26 -> full metrics (whole / longs / shorts),
by year, bootstrap + permutation on 2023+, placebo, correlation with NQ RTH.
  python3 analysis/s_rank_cl_round1_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from grid24 import jof
from cl_forced_flows_test import load
from candidates import adx as adx_fn
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 1000.0, 0.01, 7.25
SPLIT = pd.Timestamp("2023-01-01")
SURV, PICKS = [], []


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def tdiff(a, b):
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)) if min(len(a), len(b)) > 5 else np.nan


def line(x, nm, w=66, test=True):
    x = pd.Series(x).dropna()
    if len(x) < 8: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    a, b = x[y < 2023], x[y >= 2023]; t = tstat(x)
    xa = x[~((x.index.year == 2020) & (x.index.month == 4))]
    ok = test and t >= 2.5 and a.mean() > 0 and b.mean() > 0          # after costs only positive lines can be traded
    if ok and nm not in [q[0] for q in SURV]: SURV.append((nm, x))
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():5.0f} PF {pf:4.2f} t {t:4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():5.0f} (t {tstat(a):4.1f}) 23-26 ${b.mean():5.0f} (t {tstat(b):4.1f}) | x-Apr20 ${xa.mean():5.0f}{'  <-- passes' if ok else ''}")


def pick(res, label):
    """res: {key: trade series}; pick by 2018-22 t, report the holdout."""
    sc = {k: tstat(v[v.index < SPLIT]) for k, v in res.items() if len(v.dropna()) > 20}
    k = max(sc, key=lambda q: sc[q] if np.isfinite(sc[q]) else -9); x = res[k].dropna()
    print(f"   -> {label}: pick by 2018-22 t = {k} (design t {sc[k]:.1f}, {len(sc)} variants)")
    print(line(x, f"{label} pick {k}")); PICKS.append((label, k, x)); return k


class Eng:
    """Flat minute arrays (row * 1440 + j): trades may cross midnight."""
    def __init__(self, g):
        self.o, self.h, self.l, self.c = (getattr(g, k).ravel() for k in "ohlc")
        self.cf = pd.Series(self.c).ffill().to_numpy()
        self.N = len(self.o)

    def first_open(self, e, k=5):
        """First bar with an open at or after flat index e (within k bars), else -1."""
        e = np.asarray(e, int); out = np.full(len(e), -1)
        for s in range(k):
            ee = np.clip(e + s, 0, self.N - 1); okk = (out < 0) & ~np.isnan(self.o[ee]); out[okk] = ee[okk]
        return out

    def run(self, e_i, x_i, side, dates, stop=None, tgt=None):
        """Market entry at the open of e_i (+/- 1 tick), exit at the close of x_i - 1 tick, or the stop / target (points).
        Returns (net Series by date, side Series)."""
        e_i = self.first_open(e_i); x_i = np.asarray(x_i, int); side = np.asarray(side, float)
        ok = (e_i >= 0) & (side != 0) & np.isfinite(side) & (x_i > e_i)
        net = np.full(len(e_i), np.nan)
        ent = self.o[np.where(ok, e_i, 0)] + side * TICK
        px = self.cf[x_i] - side * TICK
        net[ok] = ((px - ent) * side * PV - COMM)[ok]
        if stop is not None or tgt is not None:
            stop = np.broadcast_to(np.inf if stop is None else stop, len(e_i)); tgt = np.broadcast_to(np.inf if tgt is None else tgt, len(e_i))
            for i in np.where(ok & (np.isfinite(stop) | np.isfinite(tgt)))[0]:
                s, e, a, b = side[i], ent[i], e_i[i], x_i[i]
                sp, tp = e - s * stop[i], e + s * tgt[i]
                L, H, O = self.l[a:b + 1], self.h[a:b + 1], self.o[a:b + 1]
                hs = (L <= sp) if s > 0 else (H >= sp); ht = (H >= tp) if s > 0 else (L <= tp)
                js = np.argmax(hs) if hs.any() else 10 ** 9; jt = np.argmax(ht) if ht.any() else 10 ** 9
                if js == 10 ** 9 and jt == 10 ** 9: continue
                if js <= jt:                                                     # stop first (same bar: stop, conservative)
                    oo = O[js]; p = sp if js == 0 or np.isnan(oo) else (min(oo, sp) if s > 0 else max(oo, sp)); p -= s * TICK
                else:
                    oo = O[jt]; p = tp if jt == 0 or np.isnan(oo) else (max(oo, tp) if s > 0 else min(oo, tp))
                net[i] = (p - e) * s * PV - COMM
        idx = pd.DatetimeIndex(dates)
        return pd.Series(net, index=idx).dropna(), pd.Series(side, index=idx)[~np.isnan(net)]


if __name__ == "__main__":
    pd.set_option("display.width", 240)
    print(__doc__.split("\n")[0])
    cl = load("CL"); E = Eng(cl); atr_all = cl.daily_atr(15); ts = pd.DatetimeIndex(cl.ts)
    tr = cl.trading[ts[cl.trading] >= "2018-01-01"]; idx = ts[tr]; D = len(tr); atr = atr_all[tr]; base = tr * 1440
    days = idx
    full = cl.last_j[tr] >= jof(1500)                                           # full sessions (not holiday half days)
    bdays = idx[cl.last_j[tr] >= jof(1329)]                                      # business days (settlement held)
    cf = E.cf
    Pc = lambda rows, t: cf[rows * 1440 + jof(t)]
    mv = lambda a, b, rows=tr: Pc(rows, b) - Pc(rows, a)
    dl = lambda x: x.groupby(x.index.normalize()).sum().reindex(days, fill_value=0.0)
    print(f"trading days {D} ({idx[0].date()} .. {idx[-1].date()}), full sessions {full.sum()}, median ATR {np.nanmedian(atr):.2f} pts (${np.nanmedian(atr) * PV:,.0f})")

    # ---- the export's roll: largest 03:30 -> 03:33 jump each month vs LTD ----
    allb = pd.DatetimeIndex(sorted(set(bdays) | set(pd.bdate_range("2026-10-14", "2027-01-31"))))
    def bshift(d, k):
        i = allb.searchsorted(d); return allb[i + k] if 0 <= i + k < len(allb) else pd.NaT
    ltd = []
    for m in pd.period_range("2018-01", "2026-11", freq="M"):
        d25 = pd.Timestamp(m.year, m.month, 25); i = allb.searchsorted(d25, side="right") - 1        # 25th or the business day before
        ltd.append(allb[i - 3])
    ltd = pd.DatetimeIndex(ltd)
    rowsall = np.arange(cl.D); j330 = pd.Series(cf[rowsall * 1440 + jof(333)] - cf[rowsall * 1440 + jof(330)], index=ts).fillna(0)
    roll = []
    for L in ltd:
        w = j330[(j330.index >= L - pd.Timedelta(days=8)) & (j330.index <= L)]
        if len(w): roll.append((L, w.abs().idxmax(), w.abs().max()))
    rr = pd.DataFrame(roll, columns=["ltd", "roll", "jump"])
    rr["k"] = [len(allb[(allb > a) & (allb <= b)]) for a, b in zip(rr.roll, rr.ltd)]
    big = rr[rr.jump >= 0.15]
    print(f"export roll check: months with a >= $0.15 03:30-03:33 jump in the 8 days before LTD: {len(big)} of {len(rr)}; business days before LTD: {big.k.value_counts().to_dict()}")
    roll_days = set(pd.DatetimeIndex([bshift(L, -2) for L in ltd]).normalize()) | set(pd.DatetimeIndex(big.roll).normalize())
    print(f"   overnight trades skip {len(roll_days)} possible roll days (LTD - 2 and every detected jump day)")   # never hold through 03:32 on these

    hol = USFederalHolidayCalendar().holidays("2017-12-01", "2026-12-31")
    wk = idx.to_period("W"); hol_wk = set(pd.DatetimeIndex(hol[hol.dayofweek <= 1]).to_period("W"))
    dow = idx.dayofweek

    # =================== 1. API ===================
    print("\n1. API weekly inventory report, 15:30 CT Tuesday (Wednesday in Monday / Tuesday-holiday weeks)")
    api = ((dow == 1) & ~wk.isin(hol_wk)) | ((dow == 2) & wk.isin(hol_wk))
    api &= full
    r5 = mv(1530, 1535)
    print(f"   API days {api.sum()}; median |15:30 -> 15:35| ${np.nanmedian(np.abs(r5[api])) * PV:,.0f} vs ${np.nanmedian(np.abs(r5[~api & full])) * PV:,.0f} other days;"
          f" |15:30 -> 15:58| ${np.nanmedian(np.abs(mv(1530, 1558)[api])) * PV:,.0f} vs ${np.nanmedian(np.abs(mv(1530, 1558)[~api & full])) * PV:,.0f}")
    print("   by year, median |15:30 -> 15:35| API / other: " + " ".join(f"{y}:{np.nanmedian(np.abs(r5[api & (idx.year == y)])) * PV:.0f}/{np.nanmedian(np.abs(r5[~api & full & (idx.year == y)])) * PV:.0f}" for y in range(2018, 2027)))
    res1 = {}
    for k_, mode in itertools.product((5, 10, 15), ("follow", "fade")):
        s = np.sign(mv(1530, 1530 + k_)) * (1 if mode == "follow" else -1)
        net, _ = E.run(base + jof(1531 + k_), base + jof(1558), np.where(api, s, 0), idx)
        res1[("intraday", k_, mode, "15:58")] = net
        print(line(net, f"API {mode} the first {k_} min, in {15}:{31 + k_}, out 15:58"))
        netc, _ = E.run(base + jof(1531 + k_), base + jof(1558), np.where(~api & full & (dow <= 3), s, 0), idx)
        print(line(netc, f"   control: same on non-API Mon-Thu", test=False))
    # overnight: decide on 15:30 -> 15:58, in at 17:01 the same evening, out the next trading day
    nxt = np.r_[tr[1:], -1]; nxt_ok = (nxt > 0) & (nxt - tr <= 1)                    # next trading day is the next calendar date
    nxt_dates = pd.DatetimeIndex(np.where(nxt_ok, cl.ts[np.clip(nxt, 0, None)], np.datetime64("NaT")))
    no_roll_next = ~pd.Series(nxt_dates.normalize()).isin(roll_days).to_numpy()
    for src, mode in itertools.product((1545, 1558), ("follow", "fade")):
        s = np.sign(mv(1530, src)) * (1 if mode == "follow" else -1)
        for out in (800, 900, 929):
            for nm, mask in (("API", api), ("control non-API Mon-Thu", ~api & full & (dow <= 3))):
                m = mask & nxt_ok & no_roll_next
                net, _ = E.run(base + jof(1701), np.clip(nxt, 0, None) * 1440 + jof(out), np.where(m, s, 0), nxt_dates.fillna(pd.Timestamp("2000-01-01")))
                if nm == "API": res1[("overnight", src, mode, out)] = net
                print(line(net, f"{'   ' if nm != 'API' else ''}{nm}: {mode} 15:30->{src}, in 17:01, out next day {out}", test=(nm == "API")))
    print("   pre-API / pre-EIA drift")
    for mode in ("long", "short", "follow 8:00->13:29"):
        s = np.ones(D) if mode == "long" else (-np.ones(D) if mode == "short" else np.sign(mv(800, 1329)))
        net, _ = E.run(base + jof(1331), base + jof(1529), np.where(api, s, 0), idx); res1[("pre-API", mode)] = net
        print(line(net, f"API day {mode} 13:31 -> 15:29"))
        net, _ = E.run(base + jof(1331), base + jof(1529), np.where(~api & full & (dow <= 3), s, 0), idx)
        print(line(net, f"   control non-API Mon-Thu {mode} 13:31 -> 15:29", test=False))
    for mode in ("long", "short"):
        s = 1.0 if mode == "long" else -1.0
        m = api & nxt_ok & no_roll_next
        net, _ = E.run(base + jof(1701), np.clip(nxt, 0, None) * 1440 + jof(929), np.where(m, s, 0), nxt_dates.fillna(pd.Timestamp("2000-01-01")))
        res1[("into EIA", mode)] = net
        print(line(net, f"overnight into EIA: {mode} 17:01 (API evening) -> 9:29"))
    pick(res1, "API")

    # =================== 2. index roll ===================
    print("\n2. Commodity-index roll: short the front by business day of the month (business days = sessions with a settlement)")
    bpos = pd.Series(0, index=idx)
    bs = pd.Series(bdays, index=bdays); pos = bs.groupby(bs.index.to_period("M")).cumcount() + 1
    bpos.loc[pos.index] = pos.values; bn = bpos.to_numpy()
    prev_ok = np.r_[False, (tr[1:] - tr[:-1]) <= 3]                               # previous evening exists (Mon: Sunday evening)
    ev = tr - 1                                                                  # calendar row of the evening before
    W = {"night 17:01->8:00": (ev * 1440 + jof(1701), base + jof(800)), "day 8:01->13:29": (base + jof(801), base + jof(1329)),
         "roll hour 12:31->13:29": (base + jof(1231), base + jof(1329)), "after 13:31->15:58": (base + jof(1331), base + jof(1558))}
    notroll = ~idx.normalize().isin(roll_days)
    tabs, res2 = {}, {}
    for wn, (e_, x_) in W.items():
        m0 = full & (prev_ok if wn.startswith("night") else True) & (notroll if wn.startswith("night") else True)
        net, _ = E.run(e_, x_, np.where(m0, -1.0, 0), idx); net = net.reindex(idx)
        tabs[wn] = net
        for nm, sel in (("BD 1-4", (bn >= 1) & (bn <= 4)), ("BD 5-9 (GSCI)", (bn >= 5) & (bn <= 9)), ("BD 6-10 (BCOM)", (bn >= 6) & (bn <= 10)), ("BD 11+", bn >= 11)):
            res2[(wn, nm)] = net[sel].dropna()
            print(line(net[sel], f"short {wn}, {nm}", test=not nm.startswith("BD 11")))
        print(f"      roll days (5-10) minus other days: t {tdiff(net[(bn >= 5) & (bn <= 10)], net[(bn < 5) | (bn > 10)]):.1f}; BD 1-4 minus BD 11+: t {tdiff(net[(bn >= 1) & (bn <= 4)], net[bn >= 11]):.1f}")
    print("   short $ per CL by business day (n ~ 105 each); t in brackets")
    for wn, net in tabs.items():
        print(f"   {wn:<24} " + " ".join(f"{k}:{net[bn == k].mean():4.0f}({tstat(net[bn == k]):+.1f})" for k in range(1, 13)))
    pick({k: v for k, v in res2.items() if not k[1].startswith("BD 11")}, "index roll")

    # =================== 3. Sunday gap ===================
    print("\n3. Sunday-open gap (Sunday 17:01 open vs the last price before it)")
    mon = np.where((dow == 0) & full)[0]                                         # Mondays (trading rows)
    sun = tr[mon] - 1; assert (ts[sun].dayofweek == 6).all()
    sun_o_i = E.first_open(sun * 1440 + jof(1701), 10)
    okg = sun_o_i >= 0
    fri_c = cf[sun * 1440 + jof(1700)]                                           # last close before Sunday 17:00 (ffilled)
    gap = np.where(okg, E.o[np.clip(sun_o_i, 0, None)] - fri_c, np.nan)
    gA = gap / atr[mon]
    print(f"   Sundays {len(mon)}, median |gap| {np.nanmedian(np.abs(gA)):.2f} ATR (${np.nanmedian(np.abs(gap)) * PV:,.0f}); |gap| >= 0.25 ATR on {np.mean(np.abs(gA) >= 0.25):.0%}")
    mdates = idx[mon]; mroll = mdates.normalize().isin(roll_days)
    res3, sd3 = {}, {}
    for ein, out, th, st, mode in itertools.product((1701, 1705), (800, 1000, 1329), (0.0, 0.1, 0.25), (None, 0.5, 1.0), ("fade", "follow")):
        s = np.sign(gap) * (-1 if mode == "fade" else 1); m = okg & (np.abs(gA) >= th) & ~mroll
        net, sd = E.run(sun * 1440 + jof(ein), tr[mon] * 1440 + jof(out), np.where(m, s, 0), mdates, stop=(st * atr[mon]) if st else None)
        res3[(mode, ein, out, th, st)] = net; sd3[(mode, ein, out, th, st)] = sd
    for mode in ("fade", "follow"):
        for out in (800, 1000, 1329):
            for th in (0.0, 0.1, 0.25):
                print(line(res3[(mode, 1701, out, th, None)], f"{mode} the Sunday gap, in 17:01, out Mon {out}, |gap| >= {th} ATR, no stop"))
    print("   with stops (in 17:01):")
    for mode, out, st in itertools.product(("fade", "follow"), (800, 1329), (0.5, 1.0)):
        print(line(res3[(mode, 1701, out, 0.1, st)], f"{mode}, out {out}, |gap| >= 0.1 ATR, stop {st} ATR"))
    k3 = pick(res3, "Sunday gap")
    # placebo: weekday 17:00 reopen gaps (16:00 maintenance break), same rule
    wd = np.where(full & (dow <= 3) & nxt_ok & no_roll_next)[0]
    g_o = E.first_open(tr[wd] * 1440 + jof(1701), 10); okw = g_o >= 0
    gapw = np.where(okw, E.o[np.clip(g_o, 0, None)] - cf[tr[wd] * 1440 + jof(1700)], np.nan); gwA = gapw / atr[wd]
    mode, ein, out, th, st = k3
    s = np.sign(gapw) * (-1 if mode == "fade" else 1)
    netp, _ = E.run(tr[wd] * 1440 + jof(ein), nxt[wd] * 1440 + jof(out), np.where(okw & (np.abs(gwA) >= th), s, 0), nxt_dates[wd], stop=(st * atr[wd]) if st else None)
    print(f"   weekday 17:00 reopen gaps: median |gap| {np.nanmedian(np.abs(gwA)):.2f} ATR")
    print(line(netp, f"   placebo: picked rule on the weekday 17:00 reopen gaps", test=False))

    # ---- Sunday gap: robustness of the pick ----
    print("\n3b. Sunday-gap fade, robustness (fade = trade against the 17:01 gap; no stop)")
    def sunfade(ein, out, th, at_entry=False, side_mult=-1.0, rand=None):
        e_ = E.first_open(sun * 1440 + jof(ein), 10)
        gg = (np.where(e_ >= 0, E.o[np.clip(e_, 0, None)], np.nan) - fri_c) if at_entry else gap
        s = np.sign(gg) * side_mult if rand is None else rand
        m = okg & (np.abs(gg / atr[mon]) >= th) & ~mroll
        return E.run(sun * 1440 + jof(ein), tr[mon] * 1440 + jof(out), np.where(m, s, 0), mdates)
    ins, outs = (1701, 1705, 1710, 1715, 1730, 1800, 1900, 2100), (800, 900, 1000, 1100, 1329)
    for at_e in (False, True):
        print(f"   avg $ (t) by entry time x Monday exit, |gap| >= 0.1 ATR, gap measured {'at the entry bar' if at_e else 'at 17:01'}:")
        print("      entry  " + "".join(f"{o:>16}" for o in outs))
        for ein in ins:
            print(f"      {ein:5d}  " + "".join(f"{sunfade(ein, o, 0.1, at_e)[0].mean():>9.0f} ({tstat(sunfade(ein, o, 0.1, at_e)[0]):4.1f})" for o in outs))
    print("   threshold sensitivity, in 17:05, out 10:00 (gap at 17:01): " + " | ".join(f">= {th}: n {len(sunfade(1705, 1000, th)[0])} ${sunfade(1705, 1000, th)[0].mean():.0f} t {tstat(sunfade(1705, 1000, th)[0]):.1f}" for th in (0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5)))
    c15 = (cf[sun * 1440 + jof(1705)] - np.where(okg, E.o[np.clip(sun_o_i, 0, None)], np.nan)) * np.sign(gap)
    big_ = okg & (np.abs(gA) >= 0.1)
    print(f"   first minutes: the 17:01 open -> 17:05 close moves further with the gap by {np.nanmean(c15[big_]) / np.nanmedian(atr[mon]):.3f} ATR (${np.nanmean(c15[big_]) * PV:.0f}) on |gap| >= 0.1 ATR Sundays")
    t3, s3 = sunfade(1705, 1000, 0.1)
    print(line(t3[s3 > 0], "   longs (fading down-gaps)", test=False)); print(line(t3[s3 < 0], "   shorts (fading up-gaps)", test=False))
    rng = np.random.default_rng(3); pl = []
    for _ in range(2000):
        pl.append(sunfade(1705, 1000, 0.1, rand=rng.choice([-1.0, 1.0], len(mon)))[0].mean())
    print(f"   placebo 1, random side on the same Sundays (2,000 draws): mean ${np.mean(pl):.0f}, 95th pct ${np.percentile(pl, 95):.0f}, share >= real {np.mean(np.array(pl) >= t3.mean()):.2%}")
    wo = E.first_open(tr * 1440 + jof(1701), 10)                                 # Mon-Thu evening reopen after the 16:00-17:00 break (same row)
    wmv = np.where(wo >= 0, E.o[np.clip(wo, 0, None)], np.nan) - cf[tr * 1440 + jof(1700)]
    wsel = full & (dow <= 3) & nxt_ok & no_roll_next
    q = np.nanquantile(np.abs(wmv[wsel] / atr[wsel]), 1 - len(t3) / okg.sum())
    m = wsel & (np.abs(wmv / atr) >= q) & (wmv != 0)
    netw, _ = E.run(tr * 1440 + jof(1705), np.clip(nxt, 0, None) * 1440 + jof(1000), np.where(m, -np.sign(wmv), 0), nxt_dates.fillna(pd.Timestamp("2000-01-01")))
    print(line(netw, f"   placebo 2, Mon-Thu 17:00 reopen gap, top {len(t3) / okg.sum():.0%} (>= {q:.3f} ATR): fade in 17:05, out next day 10:00", test=False))
    srt = t3.sort_values()
    print(f"   concentration: median trade ${t3.median():.0f}; without the best 5 trades ${srt.iloc[:-5].mean():.0f} (t {tstat(srt.iloc[:-5]):.1f}); best 5: " + ", ".join(f"{d_.date()} ${v_:,.0f}" for d_, v_ in srt.iloc[-5:].items()))
    t3s = t3[s3 < 0].sort_values(); print(f"   shorts without their best 5 trades ${t3s.iloc[:-5].mean():.0f} (t {tstat(t3s.iloc[:-5]):.1f})")
    fmv = cf[sun * 1440 - 1440 * 2 + jof(1558)] - cf[sun * 1440 - 1440 * 2 + jof(800)]      # Friday 8:00 -> 15:58
    m = okg & (np.abs(gA) >= 0.1) & ~mroll
    netf, _ = E.run(sun * 1440 + jof(1705), tr[mon] * 1440 + jof(1000), np.where(m, -np.sign(fmv), 0), mdates)
    print(line(netf, "   placebo 3, same Sundays, fade Friday's 8:00 -> 15:58 move instead of the gap", test=False))
    for nm, mk in (("ex-2020", t3.index.year != 2020), ("2026 only", t3.index.year == 2026)):
        print(line(t3[mk], f"   {nm}", test=False))
    SUN = dict(net=t3, side=s3)

    # =================== 4a. Baker Hughes ===================
    print("\n4a. Baker Hughes rig count, Friday 12:00 CT (control: Thursday)")
    bh = (dow == 4) & full; th_ = (dow == 3) & full
    r5 = mv(1200, 1205)
    print(f"   Fridays {bh.sum()}; median |12:00 -> 12:05| ${np.nanmedian(np.abs(r5[bh])) * PV:,.0f} vs Thursday ${np.nanmedian(np.abs(r5[th_])) * PV:,.0f}, all other days ${np.nanmedian(np.abs(r5[~bh & full])) * PV:,.0f}")
    res4 = {}
    for k_, mode, out in itertools.product((5, 10, 15), ("follow", "fade"), (1329, 1558)):
        s = np.sign(mv(1200, 1200 + k_)) * (1 if mode == "follow" else -1)
        net, _ = E.run(base + jof(1201 + k_), base + jof(out), np.where(bh, s, 0), idx); res4[(k_, mode, out)] = net
        print(line(net, f"rig count: {mode} the first {k_} min, out {out}"))
        net, _ = E.run(base + jof(1201 + k_), base + jof(out), np.where(th_, s, 0), idx)
        print(line(net, f"   control Thursday", test=False))
    for mode in ("long", "short"):
        net, _ = E.run(base + jof(1101), base + jof(1159), np.where(bh, 1.0 if mode == "long" else -1.0, 0), idx); res4[("pre", mode)] = net
        print(line(net, f"rig count pre-drift {mode} 11:01 -> 11:59"))
    pick(res4, "Baker Hughes")

    # =================== 4b. options expiry ===================
    print("\n4b. WTI options expiry (LTD - 3 and LTD - 1 business days)")
    res5 = {}
    near = lambda p: np.round(p * 2) / 2
    p1200, p1329 = Pc(tr, 1200), Pc(tr, 1329)
    dist = np.abs(p1329 - near(p1329)); rng_ = (np.nanmax(cl.h[tr, jof(1201):jof(1330)], 1) - np.nanmin(cl.l[tr, jof(1201):jof(1330)], 1)) / atr
    for lag in (3, 1):
        oe = pd.DatetimeIndex([bshift(L, -lag) for L in ltd]); m = idx.isin(oe) & full
        oth = ~idx.isin(oe) & full & ~idx.isin(pd.DatetimeIndex([bshift(L, -k) for L in ltd for k in (0, 1, 2, 3, 4)]))
        print(f"   LTD-{lag}: {m.sum()} days; 13:29 distance to nearest $0.50 strike mean {dist[m].mean():.3f} vs {dist[oth].mean():.3f} other days (uniform = 0.125), t {tdiff(pd.Series(dist[m]), pd.Series(dist[oth])):.1f};"
              f" 12:00-13:30 range {np.nanmean(rng_[m]):.2f} vs {np.nanmean(rng_[oth]):.2f} ATR")
        for mode in ("long", "short", "follow 8:00->12:00", "fade 8:00->12:00", "toward strike"):
            if mode == "long": s = np.ones(D)
            elif mode == "short": s = -np.ones(D)
            elif mode.startswith("follow"): s = np.sign(mv(800, 1200))
            elif mode.startswith("fade"): s = -np.sign(mv(800, 1200))
            else:
                d_ = near(p1200) - p1200; s = np.where(np.abs(d_) >= 0.10, np.sign(d_), 0)
            net, _ = E.run(base + jof(1201), base + jof(1329), np.where(m, s, 0), idx); res5[(lag, mode)] = net
            print(line(net, f"LTD-{lag} {mode}, 12:01 -> 13:29"))
            if mode in ("toward strike", "follow 8:00->12:00"):
                netc, _ = E.run(base + jof(1201), base + jof(1329), np.where(oth, s, 0), idx)
                print(line(netc, f"   control: other days", test=False))
    pick(res5, "options expiry")

    # =================== 4c. Overnight Bias CL ===================
    print("\n4c. Overnight Bias for CL (8:00 price in the overnight range)")
    b15 = cl.bars(15); okb = ~np.isnan(b15["c"]); A = np.full(b15["c"].shape, np.nan)
    A[okb] = adx_fn(b15["h"][okb], b15["l"][okb], b15["c"][okb], 14)
    Af = pd.Series(A.ravel()).ffill().to_numpy()                                 # ADX of the last closed 15-min bar
    J15 = b15["j"]
    p800 = Pc(tr, 800)
    onr = {}
    for st_ in (1700, 2300):
        hi = np.full(D, np.nan); lo = np.full(D, np.nan)
        for i in range(D):
            if not prev_ok[i]: continue
            a = ev[i] * 1440 + jof(st_) + 1; b = base[i] + jof(800) + 1
            with np.errstate(all="ignore"):
                hi[i] = np.nanmax(E.h[a:b]); lo[i] = np.nanmin(E.l[a:b])
        onr[st_] = (hi, lo)
    orh = np.nanmax(cl.h[tr, jof(801):jof(815) + 1], 1); orl = np.nanmin(cl.l[tr, jof(801):jof(815) + 1], 1)
    res6, sides6 = {}, {}
    for st_, ent, amin, stp in itertools.product((1700, 2300), ("market 8:01", "stop at 8:15 range"), (0, 20, 30), (0.25, 0.5)):
        hi, lo = onr[st_]; posr = (p800 - lo) / (hi - lo)
        side = np.where(posr >= 2 / 3, 1, np.where(posr <= 1 / 3, -1, 0)) * ((hi > lo) & full & prev_ok)
        nets, sds, dts = [], [], []
        for i in np.where(side != 0)[0]:
            s = side[i]
            if ent == "market 8:01":
                if amin and not (Af[tr[i] * 96 + jof(800) // 15] > amin): continue
                e_i = base[i] + jof(801)
            else:
                lvl = orh[i] if s > 0 else orl[i]; e_i = -1
                for j in range(jof(816), jof(1200)):
                    if amin and not (Af[tr[i] * 96 + (j - 1) // 15] > amin): continue
                    k = base[i] + j
                    if np.isnan(E.o[k]): continue
                    if (s > 0 and E.h[k] >= lvl) or (s < 0 and E.l[k] <= lvl):
                        e_i = k; break
                if e_i < 0: continue
                # stop-order fill: level or worse open, + 1 tick
                fill = (max(E.o[e_i], lvl) if s > 0 else min(E.o[e_i], lvl)) + s * TICK
            if ent == "market 8:01": fill = E.o[e_i] + s * TICK
            if np.isnan(fill): continue
            sp_, tp_ = fill - s * stp * atr[i], fill + s * 3 * stp * atr[i]
            a, b = e_i, base[i] + jof(1329)
            L, H, O = E.l[a:b + 1], E.h[a:b + 1], E.o[a:b + 1]
            hs = (L <= sp_) if s > 0 else (H >= sp_); ht = (H >= tp_) if s > 0 else (L <= tp_)
            js = np.argmax(hs) if hs.any() else 10 ** 9; jt = np.argmax(ht) if ht.any() else 10 ** 9
            if js == 10 ** 9 and jt == 10 ** 9: p = E.cf[b] - s * TICK
            elif js <= jt:
                oo = O[js]; p = (sp_ if js == 0 or np.isnan(oo) else (min(oo, sp_) if s > 0 else max(oo, sp_))) - s * TICK
            else:
                oo = O[jt]; p = tp_ if jt == 0 or np.isnan(oo) else (max(oo, tp_) if s > 0 else min(oo, tp_))
            nets.append((p - fill) * s * PV - COMM); sds.append(s); dts.append(idx[i])
        res6[(st_, ent, amin, stp)] = pd.Series(nets, index=pd.DatetimeIndex(dts)); sides6[(st_, ent, amin, stp)] = pd.Series(sds, index=pd.DatetimeIndex(dts))
        x = res6[(st_, ent, amin, stp)]; sd = sides6[(st_, ent, amin, stp)]
        print(line(x, f"ONB-CL range from {st_}, {ent}, ADX>{amin}, stop {stp} ATR, 3R, out 13:29") +
              f"\n      longs ${x[sd > 0].mean():5.0f} (t {tstat(x[sd > 0]):4.1f}) shorts ${x[sd < 0].mean():5.0f} (t {tstat(x[sd < 0]):4.1f})")
    k6 = pick(res6, "ONB-CL")
    hi, lo = onr[k6[0]]; posr = (p800 - lo) / (hi - lo)
    mid = (posr > 1 / 3) & (posr < 2 / 3) & full & prev_ok
    rs = np.random.default_rng(6).choice([-1.0, 1.0], D)
    netp, _ = E.run(base + jof(801), base + jof(1329), np.where(mid, rs, 0), idx, stop=k6[3] * atr, tgt=3 * k6[3] * atr)
    print(line(netp, "   placebo: middle-third days, random side, market 8:01, same stop / target", test=False))

    print("\n== Candidate: Sunday-gap fade (in 17:05 Sunday, out Monday 10:00, |gap| >= 0.1 ATR, no stop): metrics whole / longs / shorts")
    t3, s3 = SUN["net"], SUN["side"]
    rowsm = {"Sunday fade": (dl(t3), t3), "  longs": (dl(t3[s3 > 0]), t3[s3 > 0]), "  shorts": (dl(t3[s3 < 0]), t3[s3 < 0])}
    print(M.table(rowsm))
    print("   by year: " + " | ".join(f"{y} ${v:,.0f} ({n})" for (y, v), n in zip(t3.groupby(t3.index.year).sum().items(), t3.groupby(t3.index.year).size())))
    print("   2023+ only:"); print(M.table({k: (v[0][days >= SPLIT], v[1][v[1].index >= SPLIT]) for k, v in rowsm.items()}))
    b_, p_ = R.report({"Sunday fade, 2023+": dl(t3)[days >= SPLIT], "  longs, 2023+": dl(t3[s3 > 0])[days >= SPLIT], "  shorts, 2023+": dl(t3[s3 < 0])[days >= SPLIT]}, n=3000); print(b_); print(p_)
    print(f"   per year per CL ${t3.sum() / (len(days) / 252):,.0f}; average CL price ${np.nanmean(cf[base + jof(1329)]):.0f} (notional ${np.nanmean(cf[base + jof(1329)]) * PV:,.0f}); worst trade ${t3.min():,.0f}, best ${t3.max():,.0f}")

    # =================== survivors ===================
    print(f"\nSurvivors (t >= 2.5, positive in 2018-22 and in 2023-26) out of all tested lines: {len(SURV)}")
    for nm, _ in SURV: print(f"   {nm}")
    g = pickle.load(open(SP + "g24.pkl", "rb")); gt = pd.DatetimeIndex(g.ts[g.trading]); gcf = pd.Series(g.c.ravel()).ffill().to_numpy()
    nq = pd.Series((gcf[g.trading * 1440 + jof(1500)] - g.o[g.trading, jof(831)]) * 20.0, index=gt)
    for nm, x in SURV:
        print(f"\n== {nm}")
        x = x.sort_index(); d = dl(x)
        rows = {nm[:44]: (d, x)}
        print(M.table(rows))
        print("   by year: " + " | ".join(f"{y} ${v:,.0f} ({n})" for (y, v), n in zip(x.groupby(x.index.year).sum().items(), x.groupby(x.index.year).size())))
        xa = x[~((x.index.year == 2020) & (x.index.month == 4))]; print(line(xa, "   without April 2020", test=False))
        b_, p_ = R.report({nm[:40] + ", 2023+": d[days >= SPLIT]}, n=3000); print(b_); print(p_)
        print(f"   daily correlation with NQ RTH (8:30 -> 15:00) on trade days: {pd.concat([x.groupby(x.index.normalize()).sum(), nq], axis=1, join='inner').corr().iloc[0, 1]:+.2f}")

    print("\nPicks by design-period t (one per hypothesis):")
    for lab_, k, x in PICKS:
        y = x.index.year
        print(f"   {lab_:<16} {str(k):<58} n {len(x):4d} avg ${x.mean():5.0f} PF {x[x > 0].sum() / max(1e-9, -x[x < 0].sum()):.2f} t {tstat(x):4.1f} yrs+ {(x.groupby(y).sum() > 0).sum()}/{y.nunique()} | 18-22 t {tstat(x[y < 2023]):4.1f} 23-26 ${x[y >= 2023].mean():5.0f} t {tstat(x[y >= 2023]):4.1f}")
    pickle.dump(dict(res1=res1, res2=res2, res3=res3, res4=res4, res5=res5, res6=res6, surv=SURV, picks=PICKS), open(SP + "s_rank_cl.pkl", "wb"))
