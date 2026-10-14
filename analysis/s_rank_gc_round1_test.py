"""S-rank program, gold (GC) round 1 (S_RANK_PROGRAM.md, 2026-10-14): scheduled / forced flows native to gold.

Data: data/GC_1min_<year>.csv via cl_forced_flows_test.load("GC") (Grid24, CT, unadjusted continuous front month).
GC: $100 a point, tick 0.10 ($10); $7.25 + 1 tick a market / stop fill = $27.25 a round trip; MGC = 1/10.
Roll: the continuous series jumps by the contango (up to $6,000 per GC in 2025-26) when it rolls, at 03:32 CT (to 2024)
or the 17:00 open (2025-26) 2-4 business days before first notice day of Feb / Apr / Jun / Aug / Dec (Oct is skipped).
The roll bars are detected (largest persistent 1-minute jump in the last 12 days of Jan / Mar / May / Jul / Nov) and any
trade or return window that contains one is dropped; H3 uses a roll-adjusted series.
Trading sessions: session D runs 17:00 CT on D-1 -> 16:00 on D; trades are dated by session; daily P&L indexed by every
trading day from 2018-01-01 (0 when no trade). Engine: entry at a bar open +/- 1 tick, stop fills at the stop (worse
open on a gap) - 1 tick, time exit at a bar close - 1 tick. All Apex-legal (flat by 15:59 CT).
Design 2018-22, holdout 2023-26; every grid is picked by 2018-22 t only; advance = |t| >= 2.5 overall with the same
sign in both halves. Placebos: random side on the same entries/exits, always-long on the same windows, the same rule at
other clock times, and the clock-mismatch natural experiments.
  H1. LBMA gold price auctions, AM 10:30 and PM 15:00 London (Europe/London -> CT per date: 4:30 / 9:00 CT normally,
      5:30 / 10:00 CT in the 3-4 US/UK DST-mismatch weeks). Volatility profile aligned to the London clock vs the CT
      clock on mismatch days; drift before / during / after; follow / fade grid (signal pre-60 / pre-30 / the first 10
      auction minutes, threshold 0 / 0.1 ATR, hold 30 / 60 / 120 min, stop 0.25 / 0.5 ATR).
  H2. Shanghai Gold Exchange benchmarks 10:15 and 14:15 Beijing and the 9:00 Beijing open (Asia/Shanghai -> CT: 20:15 /
      00:15 / 19:00 CT in US winter, an hour later in US summer - China has no DST, so the US clock change is the
      natural experiment). Same battery, and whether the SGE times explain the Asian-range breakout edge
      (scratch_data/gold_filter.pkl base trades from analysis/gold_breakout_filter_test.py).
  H3. COMEX delivery cycle: business-day returns around first notice day (last business day of Jan / Mar / May / Jul /
      Sep / Nov) and gold options expiry (4th-last business day of each month), roll-adjusted, overnight (12:30 -> 7:20)
      and day (7:20 -> 12:30) separately; short / long day-session trades on the pre-specified windows.
  H4. 7:30 CT US data (event_days.release_days on GC; NFP = release Fridays on day 1-10): follow / fade the first 5 / 10
      / 15 minutes to 9:00 / 10:30 / 12:00 with 0.5 / 1.0 ATR stops; COMEX settlement 12:30 CT: follow the move into
      12:30 and follow / fade after it.
For anything that advances: Sharpe / Sortino / PF / Calmar / Ulcer whole / longs / shorts, by year, bootstrap +
permutation on 2023+, placebo, correlation with gold buy-and-hold and NQ RTH.
  python3 analysis/s_rank_gc_round1_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from cl_forced_flows_test import load
import event_days as ED
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 100.0, 0.10, 7.25
SPLIT = pd.Timestamp("2023-01-01")
RNG = np.random.default_rng(7)
NVAR = {}                                                                                  # variants tried per hypothesis


def tstat(x):
    x = np.asarray(pd.Series(x).dropna(), float); return x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pfac(x):
    x = pd.Series(x).dropna(); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(x, nm, w=64):
    x = pd.Series(x).dropna()
    if len(x) < 8: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); a, b = x[y < 2023], x[y >= 2023]
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():5.0f} PF {pfac(x):4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():5.0f} (t {tstat(a):4.1f}) 23-26 ${b.mean():5.0f} (t {tstat(b):4.1f})")


# ------------------------------------------------------------------ data
gc = load("GC")
O, H, L, C = (getattr(gc, k).ravel() for k in "ohlc")
CF = pd.Series(C).ffill().to_numpy()
TS = pd.DatetimeIndex(gc.ts)
ATR_ROW = gc.daily_atr(15)
tr = gc.trading[TS[gc.trading] >= "2018-01-01"]; idx = TS[tr]; ND = len(tr)
DAYS = idx


def find_rolls():
    """Roll bars: in the last 12 days of Jan / Mar / May / Jul / Nov (the series skips Oct), the largest positive
    (contango) bar-to-bar gap that persists (median of the next 10 closes keeps >= 70% of it), first among bars at the
    vendor's roll times (03:28-03:35 or the 17:00 open), else anywhere if it is >= 1.5 points and >= 1.4 x the next-largest persistent gap more than 30 bars away."""
    ok = np.where(~np.isnan(C))[0]; rr = TS[ok // 1440]; out = []
    for y in range(2018, 2027):
        for m in (1, 3, 5, 7, 11):
            end = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0)
            w = np.where((rr >= end - pd.Timedelta(days=12)) & (rr <= end))[0]
            if len(w) < 50: continue
            gap = O[ok[w]] - C[ok[w - 1]]
            per = np.array([np.median(C[ok[i:i + 10]]) for i in w]) - C[ok[w - 1]]
            cand = np.where((gap > 0) & (per >= 0.7 * gap))[0]
            if not len(cand): continue
            mins = ok[w[cand]] % 1440
            clock = cand[((mins >= jof(328)) & (mins <= jof(335))) | (mins == jof(1701))]      # the vendor's roll times
            if len(clock) and gap[clock].max() >= max(1.5, 0.5 * gap[cand].max()):
                i = clock[np.argmax(gap[clock])]; out.append((ok[w[i]], float(per[i]))); continue
            i = cand[np.argmax(gap[cand])]
            rest = cand[np.abs(cand - i) > 30]
            nxt = gap[rest].max() if len(rest) else 0.0
            if gap[i] >= 1.5 and gap[i] >= 1.4 * nxt:
                out.append((ok[w[i]], float(per[i])))
    return out


ROLLS = find_rolls()
ROLL_I = np.array([k for k, _ in ROLLS])
ADJ = CF.copy()                                                                            # back-adjusted closes (additive)
for k, jmp in ROLLS:
    ADJ[:k] += jmp
ROLL_CUM = np.zeros(len(C) + 1); ROLL_CUM[ROLL_I + 1] = 1; ROLL_CUM = np.cumsum(ROLL_CUM)


def has_roll(a, b):
    """True if a roll bar lies in flat bars a..b (inclusive)."""
    a, b = np.minimum(a, b), np.maximum(a, b); return ROLL_CUM[b + 1] - ROLL_CUM[a] > 0


def flat_local(hh, mm, tz, day_offset=0):
    """Flat index (row * 1440 + minute) of local hh:mm in tz on each session date (+ day_offset), in CT."""
    loc = pd.DatetimeIndex(idx + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hh, minutes=mm)).tz_localize(tz)
    c = loc.tz_convert("America/Chicago").tz_localize(None)
    row = np.searchsorted(gc.dates, c.strftime("%Y%m%d").astype(int).to_numpy())
    return row * 1440 + c.hour.to_numpy() * 60 + c.minute.to_numpy()


def flat_ct(hhmm, day_offset=0):
    return (tr + day_offset) * 1440 + jof(hhmm)


def run(e, x, side, stop, date=None):
    """Vectorized trades: entry at the open of flat bar e (+/- 1 tick), out at the close of flat bar x (- 1 tick) or
    at the stop (stop points from entry; fill at the stop, or the worse open on a gap, - 1 tick). Returns DataFrame."""
    e = np.asarray(e); x = np.asarray(x); side = np.asarray(side).astype(int); stop = np.broadcast_to(np.asarray(stop, float), e.shape)
    date = idx if date is None else date
    ok = (side != 0) & ~np.isnan(O[e]) & (x > e) & ~has_roll(e - 1, x)
    e, x, side, stop, date = e[ok], x[ok], side[ok], stop[ok], date[ok]
    if not len(e): return pd.DataFrame(columns=["side", "net", "e", "x"])
    Lm = int((x - e).max()) + 1; J = np.arange(Lm)
    ii = e[:, None] + J[None, :]; valid = J[None, :] <= (x - e)[:, None]
    en = O[e] + side * TICK; sp = en - side * stop
    hit = np.where(side[:, None] > 0, L[ii] <= sp[:, None], H[ii] >= sp[:, None]) & valid & np.isfinite(sp)[:, None]
    any_ = hit.any(1); first = np.argmax(hit, 1)
    oo = O[e + first]
    gapfill = np.where(side > 0, np.fmin(oo, sp), np.fmax(oo, sp))
    spfill = np.where((first == 0) | np.isnan(oo), sp, gapfill) - side * TICK
    px = np.where(any_, spfill, CF[x] - side * TICK)
    net = (px - en) * side * PV - COMM
    return pd.DataFrame(dict(side=side, net=net, e=e, x=np.where(any_, e + first, x)), index=pd.DatetimeIndex(date))


def daily(t):
    return t.net.groupby(t.index.normalize()).sum().reindex(DAYS, fill_value=0.0) if len(t) else pd.Series(0.0, index=DAYS)


def placebo(e, x, stop, date, n=30):
    """Random side (n runs) and always-long on the same entries, exits and stops."""
    rs = [run(e, x, RNG.choice([-1, 1], len(e)), stop, date).net.mean() for _ in range(n)]
    lg = run(e, x, np.ones(len(e)), stop, date).net
    return f"random side ${np.mean(rs):.0f} ({np.percentile(rs, 5):.0f}..{np.percentile(rs, 95):.0f}), always long ${lg.mean():.0f} (t {tstat(lg):.1f})"


def rule(sig_a, sig_b, e, hold, mode, thr, stopm, atr, mask=None, date=None):
    """sign(close[sig_b] - close[sig_a]) followed (+1) or faded (-1), entry at open of flat bar e, out at e + hold - 1."""
    mv = CF[sig_b] - CF[sig_a]
    m = (np.abs(mv) >= thr * atr) & (mv != 0) & np.isfinite(atr) & ~has_roll(sig_a, sig_b)
    if mask is not None: m &= mask
    s = (np.sign(mv) * mode).astype(int)
    d = idx if date is None else date; hold = np.broadcast_to(hold, e.shape)
    return run(e[m], e[m] + hold[m] - 1, s[m], stopm * atr[m], d[m])


def grid_event(A, atr, name, mask=None, holds=(30, 60, 120), verbose=True):
    """Follow / fade grid around event flat index A; returns {key: trades} and prints the design pick."""
    res = {}
    sigs = {"pre60": (A - 60, A - 1, A), "pre30": (A - 30, A - 1, A), "win10": (A - 1, A + 9, A + 10)}
    for (sn, (a, b, e)), mode, thr, hold, st in itertools.product(sigs.items(), (1, -1), (0.0, 0.1), holds, (0.25, 0.5)):
        res[(sn, "follow" if mode > 0 else "fade", thr, hold, st)] = rule(a, b, e, hold, mode, thr, st, atr, mask)
    NVAR[name] = NVAR.get(name, 0) + len(res)
    sc = {k: tstat(v.net[v.index < SPLIT]) for k, v in res.items() if (v.index < SPLIT).sum() >= 40}
    top = sorted(sc, key=sc.get, reverse=True)
    if verbose:
        allt = pd.Series({k: tstat(v.net) for k, v in res.items()})
        print(f"   {name}: {len(res)} variants; overall t range {allt.min():.1f} .. {allt.max():.1f}; |t| >= 2.5 overall: {(allt.abs() >= 2.5).sum()}")
        for k in top[:3]:
            print(line(res[k].net, f"design #{top.index(k) + 1}: {k}"))
    return res, top[0]


def vol_profile(A, mask, lo=-60, hi=60, step=5):
    """Mean |5-minute move| ($ per GC) in buckets around flat index A, rows where mask."""
    out = {}
    for k in range(lo, hi, step):
        a, b = A[mask] + k - 1, A[mask] + k + step - 1
        ok = ~has_roll(a, b)
        out[k] = np.nanmean(np.abs(CF[b[ok]] - CF[a[ok]])) * PV
    return pd.Series(out)


def drift_table(A, mask, label):
    rows = []
    for nm, a, b in (("-60 -> -30", -60, -30), ("-30 -> 0", -30, 0), ("0 -> +10", 0, 10), ("+10 -> +30", 10, 30),
                     ("+30 -> +60", 30, 60), ("+60 -> +120", 60, 120)):
        aa, bb = A[mask] + a - 1, A[mask] + b - 1; ok = ~has_roll(aa, bb)
        r = pd.Series((CF[bb] - CF[aa]) * PV, index=idx[mask])[ok].dropna()
        y = r.index.year
        rows.append(f"      {nm:<12} mean ${r.mean():6.1f} t {tstat(r):5.1f} | 18-22 ${r[y < 2023].mean():6.1f} 23-26 ${r[y >= 2023].mean():6.1f}")
    print(f"   {label} (gross $ per GC, long):"); print("\n".join(rows))


def full_metrics(name, t, extra_place=None):
    d = daily(t); lg, sh = t[t.side > 0], t[t.side < 0]
    print(f"\n   == full metrics: {name}")
    print(line(t.net, "all")); print(line(lg.net, "longs")); print(line(sh.net, "shorts"))
    print("   by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in t.net.groupby(t.index.year).sum().items()))
    print(M.table({"all": (d, t.net), "longs": (daily(lg), lg.net), "shorts": (daily(sh), sh.net),
                   "all 2023+": (d[DAYS >= SPLIT], t.net[t.index >= SPLIT])}))
    b_, p_ = R.report({f"{name[:28]} 2023+": d[DAYS >= SPLIT], "longs 2023+": daily(lg)[DAYS >= SPLIT],
                       "shorts 2023+": daily(sh)[DAYS >= SPLIT]}, n=3000)
    print(b_); print(p_)
    print(f"   daily correlation with gold buy-and-hold: {np.corrcoef(d, GOLD_BH)[0, 1]:+.2f}; with NQ RTH 8:30->15:00: {np.corrcoef(d, NQ_RTH)[0, 1]:+.2f}")


# ---------------------------------------------------------------- benchmarks for correlations
def _bh():
    s = pd.Series(ADJ[flat_ct(1230)], index=DAYS); return (s.diff() * PV).fillna(0.0)


GOLD_BH = _bh().to_numpy()
_g = pickle.load(open(SP + "g24.pkl", "rb"))
_cfn = pd.Series(_g.c.ravel()).ffill().to_numpy()
_nr = _g.trading; _nq = pd.Series((_cfn[_nr * 1440 + jof(1500)] - _g.o[_nr, jof(831)]) * 20.0, index=pd.DatetimeIndex(_g.ts[_nr]))
NQ_RTH = _nq.reindex(DAYS).fillna(0.0).to_numpy(); del _g, _cfn

if __name__ == "__main__":
    pd.set_option("display.width", 240)
    print(__doc__.split("\n")[0])
    print(f"sessions {ND} ({idx[0].date()} .. {idx[-1].date()}); median 15-day ATR ${np.nanmedian(ATR_ROW[tr]) * PV:,.0f} per GC; "
          f"cost ${COMM + 2 * TICK * PV:.2f} a round trip")
    print(f"roll bars detected: {len(ROLLS)}: " + ", ".join(f"{TS[k // 1440].date()} {(k % 1440) // 60:02d}:{k % 60:02d} {j:+.1f}" for k, j in ROLLS))
    atr_d = ATR_ROW[tr]; atr_on = ATR_ROW[tr - 1]                                          # overnight events: yesterday's ATR
    atr_on = np.where(np.isfinite(atr_on), atr_on, atr_d)

    print("\n0. Context: average 60-minute move by CT hour (gross $ per GC, long), 2018-22 vs 2023-26 - gold's drift map")
    hrs = []
    for hh in list(range(17, 24)) + list(range(0, 16)):
        off = -1 if hh >= 17 else 0
        a, b = flat_ct(hh * 100, off) - 1, flat_ct(hh * 100 + 59, off)
        ok = ~has_roll(a, b); r = pd.Series((CF[b] - CF[a]) * PV, index=idx)[ok].dropna(); y = r.index.year
        hrs.append(f"{hh:02d}h {r[y < 2023].mean():+5.0f}/{r[y >= 2023].mean():+5.0f} (t {tstat(r):+.1f})")
    for i in range(0, len(hrs), 6): print("   " + " | ".join(hrs[i:i + 6]))
    print("   night vs day as trades (1 GC, costs; exploratory, not a round-1 hypothesis):")
    for nm, a, b, sd in (("long 17:00 -> 7:20 (Globex night)", flat_ct(1701, -1), flat_ct(720), 1), ("short 7:20 -> 12:30 (COMEX day)", flat_ct(721), flat_ct(1230), -1)):
        t = run(a, b, np.full(ND, sd), np.inf); print(line(t.net, nm))
        print("      by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in t.net.groupby(t.index.year).sum().items()))

    # ================================================================ H1 LBMA
    print("\n" + "=" * 100 + "\nH1. LBMA gold price auctions (AM 10:30, PM 15:00 London)")
    AM = flat_local(10, 30, "Europe/London"); PM = flat_local(15, 0, "Europe/London")
    pm_ct = (PM % 1440); mism = pm_ct != jof(900)
    print(f"   PM auction at 9:00 CT on {np.sum(~mism)} sessions, at {sorted(set((pm_ct[mism] // 60 * 100 + pm_ct[mism] % 60).tolist()))} CT on {mism.sum()} (DST mismatch)")
    print("   a. volatility (mean |5-min move| $ per GC) around the PM auction, mismatch days: aligned to London (10:00 CT) vs to 9:00 CT")
    vL = vol_profile(PM, mism, -75, 75); vC = vol_profile(PM - 60, mism, -75, 75); vN = vol_profile(PM, ~mism, -75, 75)
    print("      minutes from    " + " ".join(f"{k:5d}" for k in vL.index))
    print("      normal (9:00)   " + " ".join(f"{v:5.0f}" for v in vN))
    print("      mismatch 10:00  " + " ".join(f"{v:5.0f}" for v in vL))
    print("      mismatch 9:00   " + " ".join(f"{v:5.0f}" for v in vC))
    print("   (9:00 CT = 10:00 ET, when ISM / JOLTS / new home sales etc. are released, so on normal days the PM auction and US"
          " 10:00 ET data coincide; on mismatch days a spike that stays at 9:00 CT is US data, one that moves to 10:00 is LBMA)")
    print("   AM auction volatility, normal (4:30 CT) vs mismatch (5:30 CT) aligned to London:")
    am_m = (AM % 1440) != jof(430)
    vA = vol_profile(AM, ~am_m, -45, 45); vAm = vol_profile(AM, am_m, -45, 45); vAc = vol_profile(AM - 60, am_m, -45, 45)
    print("      minutes from    " + " ".join(f"{k:5d}" for k in vA.index))
    print("      normal (4:30)   " + " ".join(f"{v:5.0f}" for v in vA))
    print("      mismatch 5:30   " + " ".join(f"{v:5.0f}" for v in vAm))
    print("      mismatch 4:30   " + " ".join(f"{v:5.0f}" for v in vAc))
    print("   b. drift around the auctions")
    drift_table(AM, np.ones(ND, bool), "AM auction, all days"); drift_table(PM, np.ones(ND, bool), "PM auction, all days")
    drift_table(PM, mism, "PM auction, mismatch days only (10:00 CT)")
    print("   b2. the auction window falls (0 -> +10 above): short at the auction start, out after 10 / 15 minutes, no stop, every day")
    am_mm = (AM % 1440) != jof(430)
    for nm, A, mm_ in (("AM", AM, am_mm), ("PM", PM, mism)):
        for ho in (10, 15):
            NVAR["LBMA window short"] = NVAR.get("LBMA window short", 0) + 1
            print(line(run(A, A + ho - 1, -np.ones(ND), np.inf).net, f"{nm} short {ho} min, all days"))
            print(line(run(A[~mm_], A[~mm_] + ho - 1, -np.ones((~mm_).sum()), np.inf, idx[~mm_]).net, f"   normal days"))
            print(line(run(A[mm_], A[mm_] + ho - 1, -np.ones(mm_.sum()), np.inf, idx[mm_]).net, f"   mismatch days at the London time"))
            print(line(run(A[mm_] - 60, A[mm_] - 60 + ho - 1, -np.ones(mm_.sum()), np.inf, idx[mm_]).net, f"   mismatch days at the usual CT time (placebo)"))
        g10 = pd.Series((CF[A + 9] - CF[A - 1]) * PV, index=idx)
        gm = pd.Series((CF[A - 60 + 9] - CF[A - 60 - 1]) * PV, index=idx)
        print(f"      {nm} gross 10-minute move (natural experiment): normal days ${g10[~mm_].mean():.1f} (t {tstat(g10[~mm_]):.1f}); mismatch days at the"
              f" London time ${g10[mm_].mean():.1f} (t {tstat(g10[mm_]):.1f}), at the usual CT time ${gm[mm_].mean():.1f} (t {tstat(gm[mm_]):.1f})")
        pl = {sh: ((CF[A + sh + 9] - CF[A + sh - 1]) * PV).mean() for sh in (-120, -90, -60, -30, 30, 60, 90, 120)}
        print(f"      {nm} gross 10-minute move at the auction ${g10.mean():.1f}; same 10 minutes shifted: " + ", ".join(f"{k:+d} ${v:.1f}" for k, v in pl.items()))
    tmm = pd.concat([run(AM[am_mm], AM[am_mm] + 9, -np.ones(am_mm.sum()), np.inf, idx[am_mm]), run(PM[mism], PM[mism] + 9, -np.ones(mism.sum()), np.inf, idx[mism])])
    NVAR["LBMA window short"] += 1
    print(line(tmm.net, "post-hoc: short AM + PM auction 10 min, mismatch weeks only"))
    print("      by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in tmm.net.groupby(tmm.index.year).sum().items()))
    print("   c. follow / fade grid (entry at the bar after the signal, ATR stop, time exit)")
    rAM, kAM = grid_event(AM, atr_d, "LBMA AM")
    rPM, kPM = grid_event(PM, atr_d, "LBMA PM")
    H1 = {}
    for nm, res, k, A in (("LBMA AM", rAM, kAM, AM), ("LBMA PM", rPM, kPM, PM)):
        t = res[k]; H1[nm] = (k, t)
        print(f"   {nm} pick {k}:")
        print(line(t.net, "picked")); print(line(t.net[t.side > 0], "  longs")); print(line(t.net[t.side < 0], "  shorts"))
        print("     placebo: " + placebo(t.e.to_numpy(), t.x.to_numpy() * 0 + t.e.to_numpy() + k[3] - 1, k[4] * atr_d[np.searchsorted(tr, t.e.to_numpy() // 1440)], t.index))
        sn, mo, th, ho, st = k; mode = 1 if mo == "follow" else -1
        offs = {"pre60": (-60, -1, 0), "pre30": (-30, -1, 0), "win10": (-1, 9, 10)}[sn]
        for sh in (-180, -120, -60, 60, 120, 180):
            B = A + sh; tp = rule(B + offs[0], B + offs[1], B + offs[2], ho, mode, th, st, atr_d)
            print(line(tp.net, f"     same rule {sh:+d} min from the auction"))
        if nm == "LBMA PM":
            for lab_, BB, mm in (("mismatch days, at the London time (10:00 CT)", A, mism), ("mismatch days, at fixed 9:00 CT", A - 60, mism),
                                  ("normal days only", A, ~mism)):
                tp = rule(BB + offs[0], BB + offs[1], BB + offs[2], ho, mode, th, st, atr_d, mm)
                print(line(tp.net, f"     {lab_}"))

    # ================================================================ H2 SGE
    print("\n" + "=" * 100 + "\nH2. Shanghai Gold Exchange: benchmark 10:15 / 14:15 Beijing, open 9:00 Beijing (Beijing date = session date)")
    SAM = flat_local(10, 15, "Asia/Shanghai"); SPMa = flat_local(14, 15, "Asia/Shanghai"); SOP = flat_local(9, 0, "Asia/Shanghai")
    summer = (SAM % 1440) == jof(2115)
    print(f"   SGE AM at 20:15 CT (US winter) on {np.sum(~summer)} sessions, 21:15 CT (US summer) on {summer.sum()}")
    for nm, A in (("SGE open 9:00", SOP), ("SGE AM 10:15", SAM), ("SGE PM 14:15", SPMa)):
        vw = vol_profile(A, ~summer, -30, 45); vs = vol_profile(A, summer, -30, 45); vsc = vol_profile(A - 60, summer, -30, 45)
        print(f"   {nm} volatility (mean |5-min move| $ per GC), minutes from the Beijing time:")
        print("      minutes from       " + " ".join(f"{k:5d}" for k in vw.index))
        print("      US winter          " + " ".join(f"{v:5.0f}" for v in vw))
        print("      US summer (Beijing)" + " ".join(f"{v:5.0f}" for v in vs))
        print("      US summer, -1h CT  " + " ".join(f"{v:5.0f}" for v in vsc))
        drift_table(A, np.ones(ND, bool), f"{nm} drift, all days")
    rSO, kSO = grid_event(SOP, atr_on, "SGE open", holds=(30, 60, 120))
    rSA, kSA = grid_event(SAM, atr_on, "SGE AM", holds=(30, 60, 120))
    rSP, kSP = grid_event(SPMa, atr_on, "SGE PM", holds=(30, 60, 120))
    H2 = {}
    for nm, res, k, A in (("SGE open", rSO, kSO, SOP), ("SGE AM", rSA, kSA, SAM), ("SGE PM", rSP, kSP, SPMa)):
        t = res[k]; H2[nm] = (k, t)
        print(f"   {nm} pick {k}:")
        print(line(t.net, "picked")); print(line(t.net[t.side > 0], "  longs")); print(line(t.net[t.side < 0], "  shorts"))
        sn, mo, th, ho, st = k; mode = 1 if mo == "follow" else -1
        offs = {"pre60": (-60, -1, 0), "pre30": (-30, -1, 0), "win10": (-1, 9, 10)}[sn]
        print("     placebo: " + placebo(t.e.to_numpy(), t.e.to_numpy() + ho - 1, st * atr_on[np.searchsorted(DAYS, t.index)], t.index))
        for lab_, BB, mm in (("US summer, at the Beijing time", A, summer), ("US summer, 1h earlier in CT (winter clock)", A - 60, summer),
                              ("US winter, at the Beijing time", A, ~summer), ("US winter, 1h later in CT (summer clock)", A + 60, ~summer)):
            tp = rule(BB + offs[0], BB + offs[1], BB + offs[2], ho, mode, th, st, atr_on, mm)
            print(line(tp.net, f"     {lab_}"))

    print("\n   Does the SGE timing explain the Asian-range breakout? (base trades, range 20:00 -> 00:00, out 10:00; R = net / range)")
    gf = pickle.load(open(SP + "gold_filter.pkl", "rb")); bt = gf["t"].copy(); bt["R"] = bt.net / (bt.width * PV)
    bt = bt[bt.date >= "2018-01-01"]
    pos = np.searchsorted(tr, bt.day.to_numpy()); okp = (pos < ND) & (tr[np.minimum(pos, ND - 1)] == bt.day.to_numpy())
    bt = bt[okp]; pos = pos[okp]
    rel = bt.t0.to_numpy() - SPMa[pos]                                                    # minutes from the SGE PM benchmark
    bt["summer"] = summer[pos]
    bt["bucket"] = pd.cut(rel, [-10000, -60, -15, 30, 90, 10000], labels=["< PM-60", "PM-60..-15", "PM-15..+30", "PM+30..+90", "> PM+90"])
    print("      fill time vs SGE PM (14:15 Beijing)   " + " | ".join(f"{b}" for b in bt.bucket.cat.categories))
    for nm, sub in (("US winter (PM 00:15 CT)", bt[~bt.summer]), ("US summer (PM 01:15 CT)", bt[bt.summer])):
        g_ = sub.groupby("bucket", observed=False).R; sz, mu = g_.size(), g_.mean()
        print(f"      {nm:<28} " + " | ".join(f"n {sz.get(b, 0):3d} {mu.get(b, np.nan):+.3f}R" for b in bt.bucket.cat.categories))
    bt["clk"] = pd.cut((bt.t0 % 1440).to_numpy(), [-1, 59, 119, 359, 1439], labels=["00h", "01h", "02-05h", "later"])
    for nm, sub in (("US winter", bt[~bt.summer]), ("US summer", bt[bt.summer])):
        g_ = sub.groupby("clk", observed=False).R; sz, mu = g_.size(), g_.mean()
        print(f"      fill CT hour, {nm:<14} " + " | ".join(f"{b} n {sz.get(b, 0):3d} {mu.get(b, np.nan):+.3f}R" for b in bt.clk.cat.categories))
    print("      (if Chinese PM-benchmark demand drove the edge, the good fills should move from 00h to 01h CT in US summer)")

    # ================================================================ H3 delivery cycle
    print("\n" + "=" * 100 + "\nH3. COMEX delivery cycle (roll-adjusted series)")
    ym = idx.to_period("M"); s = pd.Series(np.arange(ND), index=idx)
    last_bd = s.groupby(ym).transform("max").to_numpy()                                   # position of the month's last business day
    rank_from_end = last_bd - np.arange(ND)                                                # 0 = last business day
    FND = np.where((rank_from_end == 0) & np.isin(idx.month, (1, 3, 5, 7, 9, 11)))[0]
    OE = np.where(rank_from_end == 3)[0]; OE_act = OE[np.isin(idx.month[OE], (1, 3, 5, 7, 9, 11))]
    DY = pd.Series((ADJ[flat_ct(1230)] - ADJ[flat_ct(720)]) * PV, index=idx)              # 7:20 -> 12:30 (COMEX day)
    # the previous calendar row is not always the previous trading day: use the previous trading row's 12:30
    prev_rows = np.r_[tr[0] - 1, tr[:-1]]
    ON = pd.Series((ADJ[tr * 1440 + jof(720)] - ADJ[prev_rows * 1440 + jof(1230)]) * PV, index=idx)   # 12:30 prev -> 7:20
    TOT = ON + DY
    def offsets(ev, label, ks):
        print(f"   {label}: n {len(ev)} events; gross $ per GC (long); all other days: overnight ${ON.mean():.0f}, day ${DY.mean():.0f}, total ${TOT.mean():.0f}")
        for k in ks:
            p = ev + k; p = p[(p >= 0) & (p < ND)]
            out = []
            for nm, ser in (("overnight", ON), ("day", DY), ("total", TOT)):
                x = ser.iloc[p]; y = x.index.year; rest = ser.drop(x.index)
                tdiff = (x.mean() - rest.mean()) / np.sqrt(x.var() / len(x) + rest.var() / len(rest))
                out.append(f"{nm} ${x.mean():5.0f} (diff t {tdiff:+.1f}; 18-22 ${x[y < 2023].mean():5.0f} 23-26 ${x[y >= 2023].mean():5.0f})")
            print(f"      day {k:+d}: " + " | ".join(out))
    offsets(FND, "first notice day (day 0 = FND, last business day of Jan/Mar/May/Jul/Sep/Nov)", range(-6, 3))
    offsets(OE, "options expiry, every month (day 0 = 4th-last business day)", range(-3, 3))
    print("   range on options-expiry day vs other days (pinning would shrink it): ", end="")
    rng_day = pd.Series((np.nanmax(gc.h[tr, jof(721):jof(1231)], 1) - np.nanmin(gc.l[tr, jof(721):jof(1231)], 1)) / atr_d, index=idx)
    ro, rr_ = rng_day.iloc[OE].dropna(), rng_day.drop(idx[OE]).dropna(); tt = (ro.mean() - rr_.mean()) / np.sqrt(ro.var() / len(ro) + rr_.var() / len(rr_))
    print(f"OE day {ro.mean():.2f} ATR (diff t {tt:+.1f}; 18-22 {ro[ro.index.year < 2023].mean():.2f}, 23-26 {ro[ro.index.year >= 2023].mean():.2f}),"
          f" OE+1 {rng_day.iloc[np.minimum(OE + 1, ND - 1)].mean():.2f}, other days {rr_.mean():.2f} (18-22 {rr_[rr_.index.year < 2023].mean():.2f}, 23-26 {rr_[rr_.index.year >= 2023].mean():.2f})")
    print("   trades (day session 7:20 -> 12:30 CT, entry 7:20 open, out 12:30 close, stop 0.5 ATR or none):")
    H3 = {}
    e0, x0 = flat_ct(721), flat_ct(1230)
    for nm, pos_, side in (("short FND-3..FND-1 (pre-FND liquidation)", np.concatenate([FND - 3, FND - 2, FND - 1]), -1),
                           ("short FND-5..FND-1", np.concatenate([FND - k for k in range(1, 6)]), -1),
                           ("long FND+1 (after liquidation)", FND + 1, 1),
                           ("short options expiry day (active months)", OE_act, -1),
                           ("short options expiry day (all months)", OE, -1),
                           ("long OE-1 .. OE (all months)", np.concatenate([OE - 1, OE]), 1)):
        pos_ = np.unique(pos_[(pos_ >= 0) & (pos_ < ND)])
        for st in (np.inf, 0.5):
            t = run(e0[pos_], x0[pos_], np.full(len(pos_), side), st * atr_d[pos_], idx[pos_]); NVAR["COMEX cycle"] = NVAR.get("COMEX cycle", 0) + 1
            print(line(t.net, f"{nm}, stop {st}")); H3[(nm, st)] = t
        print("        placebo, same side on all other days: " + line(run(e0, x0, np.full(ND, side), np.full(ND, np.inf)).drop(idx[pos_], errors="ignore").net, "", 0).strip())

    # ================================================================ H4 US data, settlement
    print("\n" + "=" * 100 + "\nH4. 7:30 CT US data and the 12:30 CT COMEX settlement")
    rel_rows = ED.release_days(gc); isrel = np.isin(tr, rel_rows)
    nfp = isrel & (idx.dayofweek == 4) & (idx.day <= 10)
    print(f"   release days (7:30-7:35 range > 3 x 20-day median): {isrel.sum()} ({isrel.mean():.0%}); NFP (release Fridays day 1-10): {nfp.sum()}")
    H4 = {}
    for grp, mm in (("NFP", nfp), ("non-NFP release", isrel & ~nfp), ("all release", isrel)):
        res = {}
        for k, mode, ex, st in itertools.product((5, 10, 15), (1, -1), (900, 1030, 1200), (0.5, 1.0)):
            a = flat_ct(729); b = flat_ct(729 + k); e = b + 1; hold = (flat_ct(ex) - e + 1)
            mv = CF[b] - CF[a]; m = mm & (mv != 0) & ~has_roll(a, flat_ct(ex))
            res[(k, "follow" if mode > 0 else "fade", ex, st)] = run(e[m], flat_ct(ex)[m], (np.sign(mv[m]) * mode).astype(int), st * atr_d[m], idx[m])
        NVAR["7:30 data"] = NVAR.get("7:30 data", 0) + len(res)
        sc = {k: tstat(v.net[v.index < SPLIT]) for k, v in res.items() if (v.index < SPLIT).sum() >= 15}
        top = sorted(sc, key=sc.get, reverse=True); k = top[0]; t = res[k]; H4[grp] = (k, t)
        allt = pd.Series({kk: tstat(v.net) for kk, v in res.items()})
        print(f"   {grp}: {len(res)} variants, overall t {allt.min():.1f} .. {allt.max():.1f}; design pick {k}")
        print(line(t.net, "picked")); print(line(t.net[t.side > 0], "  longs")); print(line(t.net[t.side < 0], "  shorts"))
        a = flat_ct(729); b = flat_ct(729 + k[0]); mv = CF[b] - CF[a]; mode = 1 if k[1] == "follow" else -1
        m = ~isrel & (mv != 0)
        tp = run((b + 1)[m], flat_ct(k[2])[m], (np.sign(mv[m]) * mode).astype(int), k[3] * atr_d[m], idx[m])
        print(line(tp.net, "     placebo: same rule on non-release days"))
        print("     placebo: " + placebo(t.e.to_numpy(), flat_ct(k[2])[np.searchsorted(tr, t.e.to_numpy() // 1440)], k[3] * atr_d[np.searchsorted(tr, t.e.to_numpy() // 1440)], t.index))
    print("   COMEX settlement 12:30 CT (12:28-12:30 window)")
    res = {}
    for (sa, sb), mode, thr, st in itertools.product(((1130, 1215), (721, 1215), (1000, 1215)), (1, -1), (0.0, 0.15), (0.25, np.inf)):
        a, b = flat_ct(sa) - 1, flat_ct(sb)
        res[("into", sa, sb, "follow" if mode > 0 else "fade", thr, st)] = rule(a, b, b + 1, flat_ct(1230) - b, mode, thr, st, atr_d)
    for (sa, sb), mode, ex, st in itertools.product(((1200, 1230), (721, 1230)), (1, -1), (1330, 1500, 1555), (0.25, 0.5)):
        a, b = flat_ct(sa) - 1, flat_ct(sb)
        res[("after", sa, sb, "follow" if mode > 0 else "fade", ex, st)] = rule(a, b, b + 1, flat_ct(ex) - b, mode, 0.0, st, atr_d)
    NVAR["settlement"] = len(res)
    sc = {k: tstat(v.net[v.index < SPLIT]) for k, v in res.items()}
    top = sorted(sc, key=sc.get, reverse=True)
    allt = pd.Series({kk: tstat(v.net) for kk, v in res.items()})
    print(f"   settlement: {len(res)} variants, overall t {allt.min():.1f} .. {allt.max():.1f}")
    for k in top[:3]: print(line(res[k].net, f"design #{top.index(k) + 1}: {k}"))
    kS = top[0]; tS = res[kS]; H4["settlement"] = (kS, tS)
    print(line(tS.net[tS.side > 0], "  longs")); print(line(tS.net[tS.side < 0], "  shorts"))
    # placebo: same rule shifted by -3h, -2h, -1h, +1h (into windows; after windows earlier)
    mode = 1 if kS[3] == "follow" else -1
    for sh in (-180, -120, -60, 60):
        a, b = flat_ct(kS[1]) - 1 + sh, flat_ct(kS[2]) + sh
        if kS[0] == "into":
            tp = rule(a, b, b + 1, flat_ct(1230) - flat_ct(kS[2]), mode, kS[4], kS[5], atr_d)
        else:
            tp = rule(a, b, b + 1, min(flat_ct(kS[4])[0] - flat_ct(kS[2])[0], flat_ct(1555)[0] - flat_ct(kS[2])[0] - sh), mode, 0.0, kS[5], atr_d)
        print(line(tp.net, f"     placebo: same rule {sh:+d} min"))

    # ================================================================ summary + advancing candidates
    print("\n" + "=" * 100 + "\nSummary of design picks (advance = |t| >= 2.5 overall and the same sign in 2018-22 and 2023-26)")
    picks = {**{f"H1 {k}": v for k, v in H1.items()}, **{f"H2 {k}": v for k, v in H2.items()},
             **{f"H3 {k[0]} stop {k[1]}": (k, v) for k, v in H3.items()}, **{f"H4 {k}": v for k, v in H4.items()}}
    adv = {}
    for nm, (k, t) in picks.items():
        y = t.index.year; a, b = t.net[y < 2023], t.net[y >= 2023]
        ok = abs(tstat(t.net)) >= 2.5 and np.sign(a.mean()) == np.sign(b.mean())
        print(line(t.net, f"{nm[:52]}{' ADV' if ok else ''}", 58))
        if ok: adv[nm] = (k, t)
    print("   variants tried: " + ", ".join(f"{k} {v}" for k, v in NVAR.items()) + f"; total {sum(NVAR.values())}")
    for nm, (k, t) in adv.items():
        full_metrics(f"{nm} {k}", t)
    pickle.dump(dict(picks={k: (v[0], v[1]) for k, v in picks.items()}, advanced=list(adv), rolls=ROLLS), open(SP + "s_rank_gc.pkl", "wb"))
