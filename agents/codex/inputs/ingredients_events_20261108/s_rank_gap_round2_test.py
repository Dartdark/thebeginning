"""S-rank program, round 2 item 2 (2026-10-14): the weekend-gap family (S_RANK_PROGRAM.md).

Round 1: CL Sunday-open gap fade (in Sunday 17:05 against the 17:01 gap >= 0.1 ATR, out Monday 10:00) $442 / CL,
PF 2.26, t 3.2, 9/9 years, but longs weak and the 2023+ bootstrap Sharpe 5th pct < 0; BTC's CME weekend gap continues
(t 4.6 before costs) but half the move is in the first minutes and market orders at 17:02+ miss it.

Conventions (as analysis/s_rank_cl_round1_test.py): 1-minute Grid24 rows = calendar dates, CT; "in 17:05" = the open of
the bar stamped 17:05 (+/- 1 tick); exits at a bar close -/+ 1 tick; costs per round trip + 1 tick per market / stop
fill: CL $1,000/pt tick 0.01 $7.25; GC $100/pt tick 0.10 $7.25; ES $50/pt tick 0.25 $5; NQ $20/pt tick 0.25 $7.25;
YM $5/pt tick 1 $5; BTC (1 BTC = 10 MBT) $1/pt tick 5 $25. Gap = first open at / after the Sunday 17:01 bar minus the
last price before 17:00 (Friday's close), in units of the 15-day ATR. Mondays must be full sessions; Sunday 17:00 is
the start of Monday's Apex trading day, every trade is flat by 13:29 Monday (Apex: flat by 15:59 CT).
Design 2018-22 (BTC 2019-22), holdout 2023-26; every pick by design-period t only.

Roll jumps (continuous contracts are NOT back-adjusted): any trade whose window (Friday's last bar -> exit) contains a
roll bar is dropped, and the counts are printed.
  NQ / ES / YM: the vendor rolled at Friday 03:32 a week before expiry (to 2022), at the Sunday 17:01 reopen of the
     expiry week (late 2022 - 2024), at Monday / Tuesday 03:32 (2024-06, 2024-12) and at the Monday 17:01 reopen (2025+).
     Dropped: the expiry-week Sunday always (3rd Friday - 5 days), plus the largest persistent 03:28-03:35 / weekday
     17:01-17:03 jump >= 0.15 ATR in the 16 days before each quarterly 3rd Friday.
  GC: largest persistent contango jump in the last 12 days of Jan / Mar / May / Jul / Nov (as s_rank_gc_round1_test.py).
  CL: Mondays that are LTD - 2 or carry a >= $0.15 03:30 -> 03:33 jump in the 8 days before LTD (as CL round 1).
  BTC: persistent 03:28-03:35 jumps >= 0.1 ATR within 4 days of the last Friday of the month; weekends from 2026-05-29
     are dropped (CME crypto moved to 24/7 trading, there is no weekend gap any more).

Tests
 1. CL: a. walk-forward: each year re-pick side (both / shorts / longs) x threshold (0.1 / 0.25 / 0.5 ATR) x exit
       (Mon 8:00 / 10:00 / 13:29) by t on all prior years (expanding from 2018, >= 2 years), trade the next year;
       stream 2020-26. b. entry 17:05 / 17:15 / 17:30 / 18:00 (gap known at 17:01) and the first-minutes overshoot.
       c. gap-size buckets incl. >= 1 ATR (weekend-news proxy).
 2. GC / ES / NQ / YM: the CL rule as-is and a per-symbol grid (fade / follow x side x threshold x exit) picked by
    design t; entry-time and bucket checks; basket (per-Sunday sum of ATR-normalised trades: $1,000 per ATR).
 3. BTC continuation with resting stop orders placed before the reopen at Friday's close +/- k ticks (k 5..40, and
    0.1 / 0.25 / 0.5 ATR): a CME stop order that rests through the pre-open is elected by the opening trade if that
    print is at or through the trigger and then fills AT THE OPEN (not at the stop) -- modelled as max(open, stop) +
    1 tick for buys (min(...) - 1 tick for sells), with +5 / +10 tick sensitivity (thin book right after the reopen;
    CME converts stops to stop-with-protection, so a gap-through fill is capped but not guaranteed). Mode "open-only":
    the order is cancelled if the opening print does not reach it; mode "rest to 18:00": it stays until 18:00 and
    may trigger later (fill at max(bar open, stop) + 1 tick). Exits Sunday 20:00 / Monday 02:00 / Monday 8:30.
 Advancing (|t| >= 2.5 over all years, same sign in design and holdout): metrics.py whole / longs / shorts, by year,
 resampling.py bootstrap + permutation on 2023+, placebos (Mon-Thu 17:00 reopen gaps at the same threshold and at the
 same share of days, random side on the same Sundays), daily correlation with NQ RTH (8:31 -> 15:00).
  python3 analysis/s_rank_gap_round2_test.py [SCRATCH_DIR] > analysis/outputs/s_rank_gap_round2_test_output.txt
"""
import sys, os, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
if len(sys.argv) <= 1: sys.argv.append("scratch_data")         # cl_forced_flows_test reads its SP from argv
from cl_forced_flows_test import load

SPLIT = pd.Timestamp("2023-01-01")
NVAR = {"n": 0}
ADV = []                                     # (name, trades df, symbol) of advancing lines
SPEC = dict(CL=("cl", 1000.0, 0.01, 7.25), GC=("gc", 100.0, 0.10, 7.25), ES=("ge", 50.0, 0.25, 5.0),
            NQ=("g24", 20.0, 0.25, 7.25), YM=("gy", 5.0, 1.0, 5.0), BTC=("btc", 1.0, 5.0, 25.0))


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def summ(t):
    x = t.net; y = x.index.year; a, b = x[y < 2023], x[y >= 2023]; by = x.groupby(y).sum()
    return dict(n=len(x), avg=x.mean(), pf=pf(x), t=tstat(x), yp=int((by > 0).sum()), ny=len(by), aa=a.mean(), ta=tstat(a),
                ab=b.mean(), tb=tstat(b))


def line(t, nm, w=60, count=True, adv=None):
    if count: NVAR["n"] += 1
    if len(t) < 8: return f"   {nm:<{w}} n={len(t)}"
    s = summ(t); Lg, Sh = t.net[t.side > 0], t.net[t.side < 0]
    ok = abs(s["t"]) >= 2.5 and np.sign(s["aa"]) == np.sign(s["ab"]) == np.sign(s["t"]) and len(t) >= 20
    if ok and adv is not None and nm not in [a[0] for a in ADV]: ADV.append((nm, t, adv))
    return (f"   {nm:<{w}} n={s['n']:4d} avg ${s['avg']:6.0f} PF {s['pf']:4.2f} t {s['t']:4.1f} win {np.mean(t.net > 0):.0%} yrs+ {s['yp']}/{s['ny']}"
            f" | des ${s['aa']:5.0f} t {s['ta']:4.1f} | hold ${s['ab']:5.0f} t {s['tb']:4.1f} | L {len(Lg)} ${Lg.mean() if len(Lg) else 0:5.0f}"
            f" S {len(Sh)} ${Sh.mean() if len(Sh) else 0:5.0f}{'  <-- advances' if ok and adv is not None else ('  (|t|>=2.5, same sign)' if ok else '')}")


class Sym:
    def __init__(self, name, g=None):
        self.name = name; f, self.pv, self.tick, self.comm = SPEC[name]
        if g is None:
            g = load(name) if name in ("CL", "GC") else pickle.load(open(SP + f + ".pkl", "rb"))
        self.g = g
        self.O, self.H, self.L, self.C = (getattr(g, k).ravel() for k in "ohlc")
        self.CF = pd.Series(self.C).ffill().to_numpy(); self.N = len(self.O)
        v = ~np.isnan(self.C); self.valid = v
        self.prevv = np.maximum.accumulate(np.where(v, np.arange(self.N), -1))
        self.TS = pd.DatetimeIndex(g.ts); self.atr = g.daily_atr(15)
        start = "2019-01-01" if name == "BTC" else "2018-01-01"
        self.tr = g.trading[self.TS[g.trading] >= start]; self.days = self.TS[self.tr]
        self.full = g.last_j >= (jof(830) if name == "BTC" else jof(1500))
        self.rollbars = np.array([], int)

    def set_rolls(self, bars):
        self.rollbars = np.unique(np.asarray(bars, int))
        cum = np.zeros(self.N + 1); cum[self.rollbars + 1] = 1; self.rcum = np.cumsum(cum)

    def has_roll(self, a, b):
        a, b = np.asarray(a, int), np.asarray(b, int); return self.rcum[np.clip(b, 0, self.N - 1) + 1] - self.rcum[np.clip(a, 0, self.N - 1)] > 0

    def first_open(self, e, k=10):
        e = np.asarray(e, int); out = np.full(len(e), -1)
        for s in range(k):
            ee = np.clip(e + s, 0, self.N - 1); okk = (out < 0) & ~np.isnan(self.O[ee]); out[okk] = ee[okk]
        return out

    def jumps(self):
        """bar-to-bar jump (open minus the previous valid close) and its persistence (median of the next 10 closes)."""
        ok = np.where(self.valid)[0]; j = np.full(self.N, np.nan); p = np.full(self.N, np.nan)
        j[ok[1:]] = self.O[ok[1:]] - self.C[ok[:-1]]
        Cv = self.C[ok]; win = np.lib.stride_tricks.sliding_window_view(np.r_[Cv, np.full(9, np.nan)], 10)
        p[ok[1:]] = np.nanmedian(win[1:], axis=1) - Cv[:-1]
        return j, p, ok

    def daily(self, t):
        x = t.net.groupby(t.index.normalize()).sum(); return x.reindex(self.days, fill_value=0.0)


# --------------------------------------------------------------------------------------------- roll detection
def rolls_index(S):
    j, p, ok = S.jumps(); rr = S.TS[ok // 1440]; mins = ok % 1440; dw = rr.dayofweek; out, info = [], []
    for y in range(2017, 2027):
        for m in (3, 6, 9, 12):
            F = pd.date_range(pd.Timestamp(y, m, 1), periods=21, freq="D"); F = F[F.dayofweek == 4][2]
            sunr = S.TS.searchsorted(F - pd.Timedelta(days=5))
            e = S.first_open([sunr * 1440 + jof(1701)])[0]
            if e >= 0 and e // 1440 == sunr: out.append(e); info.append(f"{S.TS[sunr].date()}S")
            w = np.where((rr >= F - pd.Timedelta(days=16)) & (rr <= F))[0]
            if not len(w): continue
            clk = ((mins[w] >= jof(328)) & (mins[w] <= jof(335))) | ((mins[w] >= jof(1701)) & (mins[w] <= jof(1703)) & (dw[w] <= 3))
            a = S.atr[ok[w] // 1440]; jj, pp = j[ok[w]], p[ok[w]]
            cand = clk & (np.abs(jj) >= 0.15 * a) & (np.sign(pp) == np.sign(jj)) & (np.abs(pp) >= 0.7 * np.abs(jj))
            if cand.any():
                i = np.where(cand)[0][np.argmax(np.abs(jj[cand]))]; out.append(ok[w[i]])
                info.append(f"{rr[w[i]].date()} {mins[w[i]] // 60:02d}:{mins[w[i]] % 60:02d} {jj[i]:+.0f}")
    return out, info


def rolls_gc(S):
    j, p, ok = S.jumps(); rr = S.TS[ok // 1440]; out, info = [], []
    for y in range(2018, 2027):
        for m in (1, 3, 5, 7, 11):
            end = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0)
            w = np.where((rr >= end - pd.Timedelta(days=12)) & (rr <= end))[0]
            if len(w) < 50: continue
            gap, per = j[ok[w]], p[ok[w]]
            cand = np.where((gap > 0) & (per >= 0.7 * gap))[0]
            if not len(cand): continue
            mins = ok[w[cand]] % 1440
            clock = cand[((mins >= jof(328)) & (mins <= jof(335))) | (mins == jof(1701))]
            if len(clock) and gap[clock].max() >= max(1.5, 0.5 * gap[cand].max()): i = clock[np.argmax(gap[clock])]
            else:
                i = cand[np.argmax(gap[cand])]; rest = cand[np.abs(cand - i) > 30]
                if not (gap[i] >= 1.5 and gap[i] >= 1.4 * (gap[rest].max() if len(rest) else 0)): continue
            out.append(ok[w[i]]); info.append(f"{rr[w[i]].date()} {ok[w[i]] % 1440 // 60:02d}:{ok[w[i]] % 60:02d} {gap[i]:+.1f}")
    return out, info


def rolls_cl(S):
    """Roll bars = the 03:33 bar on LTD - 2 and on every day with a >= $0.15 03:30 -> 03:33 jump in the 8 days before LTD."""
    g = S.g; bdays = S.TS[g.trading[g.last_j[g.trading] >= jof(1329)]]
    allb = pd.DatetimeIndex(sorted(set(bdays) | set(pd.bdate_range("2026-10-14", "2027-01-31"))))
    rows = np.arange(g.D); j330 = pd.Series(S.CF[rows * 1440 + jof(333)] - S.CF[rows * 1440 + jof(330)], index=S.TS).fillna(0)
    days = set()
    for mth in pd.period_range("2017-12", "2026-11", freq="M"):
        i = allb.searchsorted(pd.Timestamp(mth.year, mth.month, 25), side="right") - 1; L = allb[i - 3]
        days.add(allb[allb.searchsorted(L) - 2])
        w = j330[(j330.index >= L - pd.Timedelta(days=8)) & (j330.index <= L)]
        if len(w) and w.abs().max() >= 0.15: days.add(w.abs().idxmax())
    rws = S.TS.searchsorted(pd.DatetimeIndex(sorted(days)))
    rws = rws[rws < g.D]
    return list(rws * 1440 + jof(333)), [str(S.TS[r].date()) for r in rws]


def rolls_btc(S):
    j, p, ok = S.jumps(); rr = S.TS[ok // 1440]; mins = ok % 1440; out, info = [], []
    for mth in pd.period_range("2018-12", "2026-10", freq="M"):
        e = pd.Timestamp(mth.year, mth.month, 1) + pd.offsets.MonthEnd(0); lf = e - pd.Timedelta(days=(e.dayofweek - 4) % 7)
        w = np.where((rr >= lf - pd.Timedelta(days=4)) & (rr <= lf + pd.Timedelta(days=4)) & (mins >= jof(328)) & (mins <= jof(335)))[0]
        if not len(w): continue
        a = S.atr[ok[w] // 1440]; jj, pp = j[ok[w]], p[ok[w]]
        cand = (np.abs(jj) >= 0.1 * a) & (np.sign(pp) == np.sign(jj)) & (np.abs(pp) >= 0.7 * np.abs(jj))
        if cand.any():
            i = np.where(cand)[0][np.argmax(np.abs(jj[cand]))]; out.append(ok[w[i]])
            info.append(f"{rr[w[i]].date()} {mins[w[i]] // 60:02d}:{mins[w[i]] % 60:02d} {jj[i]:+.0f}")
    return out, info


# --------------------------------------------------------------------------------------------- Sunday frames
def sunday_frame(S):
    dow = S.TS[S.tr].dayofweek
    mon = S.tr[(dow == 0) & S.full[S.tr]]; sun = mon - 1
    keep = S.TS[sun].dayofweek == 6; mon, sun = mon[keep], sun[keep]
    if S.name == "BTC":                                                      # 24/7 from 2026-05-29: no weekend gap
        sat_has = S.valid.reshape(S.g.D, 1440)[sun - 1].any(1) | S.valid.reshape(S.g.D, 1440)[sun, :jof(1600)].any(1)
        mon, sun = mon[~sat_has], sun[~sat_has]
    o_i = S.first_open(sun * 1440 + jof(1701)); ok = (o_i >= 0) & (o_i // 1440 == sun)
    ref_i = S.prevv[sun * 1440 + jof(1700)]
    ref = S.CF[sun * 1440 + jof(1700)]
    gap = np.where(ok, S.O[np.clip(o_i, 0, None)] - ref, np.nan)
    a = S.atr[mon]
    F = pd.DataFrame(dict(sun=sun, mon=mon, o_i=o_i, ref=ref, ref_i=ref_i, gap=gap, atr=a, gA=gap / a, ok=ok & np.isfinite(gap / a) & (gap != 0)),
                     index=S.TS[mon])
    F["roll"] = S.has_roll(ref_i + 1, mon * 1440 + jof(1329))
    return F


def flat_x(F, out, rowcol="mon"):
    """Exit flat index: hhmm >= 1700 means the Sunday evening, else Monday."""
    return np.where(out >= 1700, F.sun.values * 1440 + jof(out), F[rowcol].values * 1440 + jof(out))


CACHE = {}


def legs(S, F, ein, out):
    """net $ per contract for a long and a short on every Sunday of F: in at the open of the ein bar, out at the close of out."""
    k = (S.name, id(F), ein, out)
    if k in CACHE: return CACHE[k]
    e = S.first_open(F.sun.values * 1440 + jof(ein)); x = flat_x(F, out)
    okk = (e >= 0) & (x > e) & (e // 1440 == F.sun.values)
    res = {}
    for s in (1, -1):
        ent = S.O[np.clip(e, 0, None)] + s * S.tick; px = S.CF[x] - s * S.tick
        res[s] = np.where(okk, (px - ent) * s * S.pv - S.comm, np.nan)
    CACHE[k] = res; return res


def sun_trades(S, F, ein=1705, out=1000, th=0.1, mode="fade", sides="both", lo=None, hi=None, gA=None, rand=None):
    gA = F.gA.values if gA is None else gA
    sg = np.sign(gA) * (-1 if mode == "fade" else 1) if rand is None else rand
    m = F.ok.values & ~F.roll.values & (np.abs(gA) >= th)
    if hi is not None: m &= np.abs(gA) < hi
    if sides == "short": m &= sg < 0
    if sides == "long": m &= sg > 0
    L = legs(S, F, ein, out); net = np.where(sg > 0, L[1], L[-1])
    m &= np.isfinite(net)
    return pd.DataFrame(dict(net=net[m], side=sg[m], gA=gA[m]), index=F.index[m])


def weekday_frame(S):
    """Mon-Thu 17:00 reopen after the 16:00 break; trade exits the next calendar day (a full session)."""
    dow = S.TS[S.tr].dayofweek
    nxt = np.r_[S.tr[1:], -1]
    m = (dow <= 3) & S.full[S.tr] & (nxt - S.tr == 1) & S.full[np.clip(nxt, 0, None)]
    r, n_ = S.tr[m], nxt[m]
    o_i = S.first_open(r * 1440 + jof(1701)); ok = (o_i >= 0) & (o_i // 1440 == r)
    ref_i = S.prevv[r * 1440 + jof(1700)]; ref = S.CF[r * 1440 + jof(1700)]
    gap = np.where(ok, S.O[np.clip(o_i, 0, None)] - ref, np.nan); a = S.atr[n_]
    F = pd.DataFrame(dict(sun=r, mon=n_, o_i=o_i, ref=ref, ref_i=ref_i, gap=gap, atr=a, gA=gap / a, ok=ok & np.isfinite(gap / a) & (gap != 0)), index=S.TS[n_])
    F["roll"] = S.has_roll(ref_i + 1, n_ * 1440 + jof(1329))
    return F


def placebos(S, F, W, k, base):
    """k = (mode, ein, out, th, sides). Weekday reopen gaps at the same threshold and at the same share of days; random side."""
    mode, ein, out, th, sides = k
    o = []
    o.append(line(sun_trades(S, W, ein, out, th, mode, sides), f"placebo Mon-Thu 17:00 reopen, same rule (>= {th} ATR)", count=False))
    el = (F.ok & ~F.roll).values; share = np.mean(np.abs(F.gA.values[el]) >= th)
    gw = np.abs(W.gA.values[(W.ok & ~W.roll).values]); q = np.nanquantile(gw, 1 - share)
    o.append(line(sun_trades(S, W, ein, out, q, mode, sides), f"placebo Mon-Thu reopen, same share of days (>= {q:.3f} ATR)", count=False))
    rng = np.random.default_rng(11); L = legs(S, F, ein, out); m = F.ok.values & ~F.roll.values & (np.abs(F.gA.values) >= th)
    if sides != "both":
        sg = np.sign(F.gA.values) * (-1 if mode == "fade" else 1); m &= (sg < 0) if sides == "short" else (sg > 0)
    lg, sh = L[1][m], L[-1][m]; ok_ = np.isfinite(lg) & np.isfinite(sh); lg, sh = lg[ok_], sh[ok_]
    av = np.array([np.where(rng.random(len(lg)) < 0.5, lg, sh).mean() for _ in range(2000)])
    o.append(f"   placebo random side on the same Sundays (2,000 draws): mean ${av.mean():.0f}, 95th pct ${np.percentile(av, 95):.0f}, share >= real ${base.net.mean():.0f}: {np.mean(av >= base.net.mean()):.2%}")
    return "\n".join(o)


def grid_pick(S, F, label, modes=("fade", "follow"), ins=(1705,), outs=(800, 1000, 1329), ths=(0.1, 0.25, 0.5), quiet=False):
    res = {}
    for mode, ein, out, th, sides in itertools.product(modes, ins, outs, ths, ("both", "short", "long")):
        t = sun_trades(S, F, ein, out, th, mode, sides); res[(mode, ein, out, th, sides)] = t; NVAR["n"] += 1
    sc = {k: tstat(v.net[v.index < SPLIT]) for k, v in res.items() if (v.index < SPLIT).sum() >= 20}
    k = max(sc, key=lambda q: sc[q] if np.isfinite(sc[q]) else -99)
    print(f"   -> {label}: pick by design t over {len(res)} variants = {k} (design t {sc[k]:.1f})")
    print(line(res[k], f"{label} pick {k}", count=False, adv=S.name))
    return k, res


def full_report(S, nm, t, nq):
    print(f"\n== {nm}")
    rows = {"whole": (S.daily(t), t.net)}
    for lab, sel in (("  longs", t.side > 0), ("  shorts", t.side < 0)):
        if (t.index[sel] >= SPLIT).sum() >= 5 and (~sel).any(): rows[lab] = (S.daily(t[sel]), t.net[sel])
    print(M.table(rows))
    print("   by year: " + " | ".join(f"{y} ${v:,.0f} ({n})" for (y, v), n in zip(t.net.groupby(t.index.year).sum().items(), t.net.groupby(t.index.year).size())))
    dd = S.days >= SPLIT
    print("   2023+ only:"); print(M.table({k: (v[0][dd], v[1][v[1].index >= SPLIT]) for k, v in rows.items()}))
    b_, p_ = R.report({k.strip() + " 2023+": v[0][dd] for k, v in rows.items()}, n=2000)
    print(b_); print(p_)
    x = t.net.groupby(t.index.normalize()).sum()
    print(f"   daily correlation with NQ RTH (8:31 -> 15:00) on trade days: {pd.concat([x, nq], axis=1, join='inner').corr().iloc[0, 1]:+.2f}; "
          f"worst ${t.net.min():,.0f}, best ${t.net.max():,.0f}; per year per contract ${t.net.sum() / (len(S.days) / 252):,.0f}")


def overshoot(S, F, th=0.1):
    m = F.ok & ~F.roll & (F.gA.abs() >= th); f = F[m]; s = np.sign(f.gap.values); o0 = S.O[f.o_i.values]
    out = []
    for hm in (1705, 1715, 1730, 1800, 2000):
        c = (S.CF[f.sun.values * 1440 + jof(hm)] - o0) * s / f.atr.values
        out.append(f"{hm}: {np.nanmean(c):+.3f} ({tstat(c):+.1f})")
    for hm in (800, 1000):
        c = (S.CF[f.mon.values * 1440 + jof(hm)] - o0) * s / f.atr.values
        out.append(f"Mon {hm}: {np.nanmean(c):+.3f} ({tstat(c):+.1f})")
    return f"   continuation from the 17:01 open in the gap's direction, ATR (t), |gap| >= {th}: " + "  ".join(out)


def buckets(S, F, ein=1705, out=1000, mode="fade"):
    for lo_, hi_ in ((0.1, 0.25), (0.25, 0.5), (0.5, 1.0), (1.0, None)):
        print(line(sun_trades(S, F, ein, out, lo_, mode, hi=hi_), f"{mode} |gap| in [{lo_}, {hi_ or 'inf'}) ATR, 17:05 -> Mon {out}"))


# ============================================================================================================== main
if __name__ == "__main__":
    pd.set_option("display.width", 240)
    print(__doc__.split("\n")[0])
    g24 = pickle.load(open(SP + "g24.pkl", "rb")); gt = pd.DatetimeIndex(g24.ts[g24.trading]); gcf = pd.Series(g24.c.ravel()).ffill().to_numpy()
    NQRTH = pd.Series((gcf[g24.trading * 1440 + jof(1500)] - g24.o[g24.trading, jof(831)]) * 20.0, index=gt)
    SYMS, FR, WF, PICK = {}, {}, {}, {}
    for nm in ("CL", "GC", "ES", "NQ", "YM"):
        S = Sym(nm, g24 if nm == "NQ" else None)
        bars, info = {"CL": rolls_cl, "GC": rolls_gc}.get(nm, rolls_index)(S); S.set_rolls(bars)
        F = sunday_frame(S); W = weekday_frame(S)
        SYMS[nm], FR[nm], WF[nm] = S, F, W
        print(f"\n[{nm}] roll bars {len(bars)}: " + ", ".join(info))
        print(f"[{nm}] Sundays (full Mondays, 2018+) {len(F)}, with a gap {F.ok.sum()}; dropped as roll weekends {int((F.ok & F.roll).sum())}"
              f" (of which |gap| >= 0.1 ATR: {int((F.ok & F.roll & (F.gA.abs() >= 0.1)).sum())}); weekday reopens {len(W)}, roll-dropped {int((W.ok & W.roll).sum())};"
              f" median |gap| {F.gA.abs()[F.ok].median():.3f} ATR, >= 0.1 ATR {np.mean(F.gA.abs()[F.ok] >= 0.1):.0%}, >= 1 ATR {int((F.gA.abs()[F.ok & ~F.roll] >= 1).sum())}")

    # ======================================================= 1. CL
    S, F, W = SYMS["CL"], FR["CL"], WF["CL"]
    print("\n" + "=" * 110 + "\n1. CL Sunday-gap fade")
    base = sun_trades(S, F, 1705, 1000, 0.1, "fade")
    print(line(base, "round-1 rule: fade >= 0.1 ATR, 17:05 -> Mon 10:00", adv="CL"))
    print(line(base[base.side > 0], "   longs (fading down-gaps)", count=False)); print(line(base[base.side < 0], "   shorts (fading up-gaps)", count=False))
    print("\n1a. walk-forward (expanding from 2018, >= 2 training years): side x threshold x exit picked by training t, traded next year")
    V = {(sd, th, out): sun_trades(S, F, 1705, out, th, "fade", sd) for sd in ("both", "short", "long") for th in (0.1, 0.25, 0.5) for out in (800, 1000, 1329)}
    NVAR["n"] += len(V); wf = []
    for Y in range(2020, 2027):
        sc = {k: tstat(v.net[v.index.year < Y]) for k, v in V.items() if (v.index.year < Y).sum() >= 15}
        k = max(sc, key=lambda q: sc[q] if np.isfinite(sc[q]) else -99); x = V[k][V[k].index.year == Y]; wf.append(x)
        print(f"   {Y}: pick {k} (train t {sc[k]:.1f}) -> {len(x)} trades ${x.net.sum():,.0f} (avg ${x.net.mean() if len(x) else 0:.0f})")
    WFS = pd.concat(wf).sort_index()
    print(line(WFS, "walk-forward stream 2020-26", count=False, adv="CL"))
    s19 = base[base.index.year >= 2020]; print(line(s19, "   same years, fixed round-1 rule (for comparison)", count=False))
    print("\n1b. entry time (gap known at the 17:01 open), fade >= 0.1 ATR, out Mon 10:00")
    print(overshoot(S, F, 0.1)); print(overshoot(S, F, 0.5))
    for ein in (1705, 1715, 1730, 1800):
        t = sun_trades(S, F, ein, 1000, 0.1, "fade"); print(line(t, f"fade in {ein}") + f"  | shorts ${t.net[t.side < 0].mean():.0f} (t {tstat(t.net[t.side < 0]):.1f}) longs ${t.net[t.side > 0].mean():.0f} (t {tstat(t.net[t.side > 0]):.1f})")
    print("\n1c. gap size buckets (very large gaps = weekend-news proxy)")
    buckets(S, F)
    big = sun_trades(S, F, 1705, 1000, 1.0, "fade"); print("   >= 1 ATR Sundays: " + ", ".join(f"{d.date()} {g:+.2f} ${v:,.0f}" for d, g, v in zip(big.index, big.gA, big.net)))
    print("   shorts-only by bucket: " + " | ".join(f"[{a},{b}) n {len(t)} ${t.net.mean():.0f} t {tstat(t.net):.1f}" for a, b in ((0.1, 0.25), (0.25, 0.5), (0.5, 1.0), (1.0, None)) for t in [sun_trades(S, F, 1705, 1000, a, 'fade', 'short', hi=b)]))
    print("\n1d. CL design-period grid pick (for the record)")
    PICK["CL"] = grid_pick(S, F, "CL")
    print(placebos(S, F, W, ("fade", 1705, 1000, 0.1, "both"), base))
    print(placebos(S, F, W, ("fade", 1705, 1000, 0.1, "short"), base[base.side < 0]))

    # ======================================================= 2. other markets
    print("\n" + "=" * 110 + "\n2. The same Sunday-gap rule on GC / ES / NQ / YM (placebo for the crude mechanism, and basket)")
    for nm in ("GC", "ES", "NQ", "YM"):
        S, F, W = SYMS[nm], FR[nm], WF[nm]
        print(f"\n-- {nm} (pv ${S.pv:.0f}, tick {S.tick}, ${S.comm})")
        for mode in ("fade", "follow"):
            t = sun_trades(S, F, 1705, 1000, 0.1, mode); print(line(t, f"{mode} >= 0.1 ATR, 17:05 -> Mon 10:00 (CL rule)", adv=nm))
            print(line(t[t.side > 0], "   longs", count=False)); print(line(t[t.side < 0], "   shorts", count=False))
        print(overshoot(S, F, 0.1))
        for ein in (1715, 1800):
            print(line(sun_trades(S, F, ein, 1000, 0.1, "fade"), f"fade in {ein} -> Mon 10:00"))
        buckets(S, F)
        PICK[nm] = grid_pick(S, F, nm)
        k = PICK[nm][0]; print(placebos(S, F, W, k, PICK[nm][1][k]))
    # basket: per-Sunday sum of ATR-normalised trades ($1,000 per 1 ATR move)
    print("\n-- basket, fade >= 0.1 ATR, 17:05 -> Mon 10:00, each trade scaled to $1,000 per ATR (R units x 1,000)")
    norm = {}
    for nm in ("CL", "GC", "ES", "NQ", "YM"):
        S, F = SYMS[nm], FR[nm]; t = sun_trades(S, F, 1705, 1000, 0.1, "fade")
        norm[nm] = t.net / (F.atr.reindex(t.index).values * S.pv) * 1000
    Nn = pd.DataFrame(norm)
    print("   correlation of the per-Sunday normalised fade P&L:\n" + Nn.corr().round(2).to_string())
    for cols, lab in ((["CL", "GC", "ES", "NQ", "YM"], "all five"), (["CL", "GC", "NQ"], "CL + GC + NQ"), (["ES", "NQ", "YM"], "equity indices")):
        b = Nn[cols].sum(axis=1, min_count=1).dropna(); bt = pd.DataFrame(dict(net=b, side=0.0), index=b.index)
        print(line(bt, f"basket {lab} (per Sunday)", adv="BASKET"))

    # ======================================================= 3. BTC
    print("\n" + "=" * 110 + "\n3. BTC weekend-gap continuation with resting stop orders at Friday's close +/- k ticks")
    B = Sym("BTC"); bars, info = rolls_btc(B); B.set_rolls(bars); FB = sunday_frame(B)
    print(f"[BTC] roll bars {len(bars)}; Sundays 2019+ {len(FB)} (24/7 weekends from 2026-05-29 excluded), with a gap {FB.ok.sum()}, roll-dropped {int((FB.ok & FB.roll).sum())}; "
          f"median |gap| {FB.gA.abs()[FB.ok].median():.2f} ATR, {np.nanmedian(np.abs(FB.gap[FB.ok])):.0f} points")
    WB = weekday_frame(B)

    def btc_stop(F, k_pts, out, mode="open", extra=0, frame_side=None):
        """k_pts: array of trigger distances (points) per Sunday. Returns trades df (side +1 = buy stop above)."""
        nets, sides, dts = [], [], []
        x_all = flat_x(F, out)
        for i in range(len(F)):
            r = F.iloc[i]
            if not r.ok or r.roll: continue
            up, dn = r.ref + k_pts[i], r.ref - k_pts[i]
            e = int(r.o_i); op = B.O[e]; s = 0; fill = np.nan
            if op >= up: s, fill = 1, op
            elif op <= dn: s, fill = -1, op
            elif mode == "rest":
                end = int(r.sun) * 1440 + jof(1800)
                Hs, Ls = B.H[e + 1:end + 1], B.L[e + 1:end + 1]
                hu, hd = np.where(Hs >= up)[0], np.where(Ls <= dn)[0]
                ju = hu[0] if len(hu) else 10 ** 9; jd = hd[0] if len(hd) else 10 ** 9
                if ju == jd == 10 ** 9 or ju == jd: continue
                if ju < jd: j = e + 1 + ju; s = 1; fill = max(B.O[j], up) if not np.isnan(B.O[j]) else up
                else: j = e + 1 + jd; s = -1; fill = min(B.O[j], dn) if not np.isnan(B.O[j]) else dn
                e = j
            if s == 0: continue
            if frame_side is not None and s != frame_side: continue
            x = x_all[i]
            if x <= e: continue
            ent = fill + s * B.tick * (1 + extra); px = B.CF[x] - s * B.tick
            nets.append((px - ent) * s - B.comm); sides.append(s); dts.append(F.index[i])
        return pd.DataFrame(dict(net=nets, side=sides), index=pd.DatetimeIndex(dts))

    resB = {}
    outsB = {"Sun 20:00": 2000, "Mon 02:00": 200, "Mon 8:30": 830}
    for mode in ("open", "rest"):
        print(f"\n   mode: {'open-only (cancel if the opening print misses the stop)' if mode == 'open' else 'resting until Sunday 18:00'}")
        for kk in (5, 10, 15, 20, 25, 30, 40):
            for on, out in outsB.items():
                t = btc_stop(FB, np.full(len(FB), kk * B.tick), out, mode); resB[(mode, f"{kk} ticks", on)] = t
                print(line(t, f"{mode}: stops +/- {kk} ticks ({kk * 5} pts), out {on}", adv="BTC"))
        for ka in (0.1, 0.25, 0.5):
            for on, out in outsB.items():
                kp = np.round(FB.atr.values * ka / B.tick) * B.tick
                t = btc_stop(FB, kp, out, mode); resB[(mode, f"{ka} ATR", on)] = t
                print(line(t, f"{mode}: stops +/- {ka} ATR, out {on}", adv="BTC"))
    sc = {k: tstat(v.net[v.index < SPLIT]) for k, v in resB.items() if k[0] == "open" and (v.index < SPLIT).sum() >= 20}
    kB = max(sc, key=lambda q: sc[q] if np.isfinite(sc[q]) else -99)
    print(f"\n   -> BTC pick by 2019-22 t (open-only family, {len(sc)} variants): {kB} (design t {sc[kB]:.1f})")
    tB = resB[kB]; print(line(tB, f"BTC pick {kB}", count=False, adv="BTC"))
    print(line(tB[tB.side > 0], "   longs (up-gaps, buy stop)", count=False)); print(line(tB[tB.side < 0], "   shorts (down-gaps, sell stop)", count=False))
    kp_fn = (lambda F_: np.full(len(F_), int(kB[1].split()[0]) * B.tick)) if "ticks" in kB[1] else (lambda F_: np.round(F_.atr.values * float(kB[1].split()[0]) / B.tick) * B.tick)
    for ex in (5, 10):
        print(line(btc_stop(FB, kp_fn(FB), outsB[kB[2]], "open", extra=ex), f"   same with +{ex} ticks extra slippage at the open fill", count=False))
    print(line(btc_stop(WB, kp_fn(WB), outsB[kB[2]] if outsB[kB[2]] < 1700 else 830, "open"), "   placebo: Mon-Thu 17:00 reopen gap through the same stops (out next day; 20:00 -> 8:30)", count=False))
    # random side on the same Sundays (the gap-through Sundays, random direction)
    Ls_ = btc_stop(FB, kp_fn(FB), outsB[kB[2]], "open"); rng = np.random.default_rng(5)
    flip = Ls_.net.values  # P&L of the opposite side = -(gross) - 2 costs
    gross = flip + B.comm + 2 * B.tick; opp = -gross - B.comm - 2 * B.tick
    av = np.array([np.where(rng.random(len(flip)) < 0.5, flip, opp).mean() for _ in range(2000)])
    print(f"   placebo random side on the same gap-through Sundays: mean ${av.mean():.0f}, 95th pct ${np.percentile(av, 95):.0f}, share >= real: {np.mean(av >= flip.mean()):.2%}")

    # ======================================================= advancing lines: full metrics
    print("\n" + "=" * 110 + f"\nAdvancing lines (|t| >= 2.5, same sign in design and holdout, n >= 20): {len(ADV)}")
    for nm, t, sym in ADV: print(f"   [{sym}] {nm}")
    best = {}
    for nm, t, sym in ADV:
        if sym == "BASKET" or t.net.mean() <= 0: continue
        dt = tstat(t.net[t.index < SPLIT])
        if sym not in best or dt > best[sym][2]: best[sym] = (nm, t, dt)
    for sym, (nm, t, dt) in best.items():
        S = B if sym == "BTC" else SYMS[sym]
        full_report(S, f"[{sym}] {nm} (best design t among this symbol's advancing lines: {dt:.1f})", t, NQRTH)
        if sym == "BTC":
            m_ = FB.ok & ~FB.roll; lg = legs(B, FB, 1702, 2000)[1][m_.values]
            print(f"   BTC drift check: always long Sunday 17:02 -> 20:00 on every Sunday ${np.nanmean(lg):.0f} (t {tstat(lg):.1f})")
    S = SYMS["CL"]; cs = sun_trades(S, FR["CL"], 1705, 1000, 0.1, "fade", "short")
    full_report(S, "[CL] shorts only: fade up-gaps >= 0.1 ATR, 17:05 -> Mon 10:00 (side split of the round-1 rule)", cs, NQRTH)
    print(placebos(S, FR["CL"], WF["CL"], ("fade", 1705, 1000, 0.1, "short"), cs).split("\n")[-1])
    for nm, t, sym in ADV:
        if sym == "BASKET":
            print(f"\n== [basket] {nm} (R x 1,000 per Sunday, CL trading-day calendar)")
            S = SYMS["CL"]; d = t.net.groupby(t.index.normalize()).sum().reindex(S.days, fill_value=0.0)
            print(M.table({"basket": (d, t.net), "basket 2023+": (d[S.days >= SPLIT], t.net[t.index >= SPLIT])}))
            b_, p_ = R.report({"basket 2023+": d[S.days >= SPLIT]}, n=2000); print(b_); print(p_); break
    if "walk-forward stream 2020-26" not in [a[0] for a in ADV]:
        print("\n== CL walk-forward stream (not advancing, metrics for the record)")
        S = SYMS["CL"]; print(M.table({"WF": (S.daily(WFS)[S.days >= "2020-01-01"], WFS.net)}))

    print(f"\nVariants tried (lines / grid cells evaluated, excluding placebos): {NVAR['n']}")
    print("\nSummary of picks:")
    for nm in PICK:
        k, res = PICK[nm]; s = summ(res[k]); print(f"   {nm:<4} {str(k):<40} n {s['n']:4d} avg ${s['avg']:6.0f} PF {s['pf']:.2f} t {s['t']:4.1f} yrs+ {s['yp']}/{s['ny']} | des t {s['ta']:4.1f} hold ${s['ab']:5.0f} t {s['tb']:4.1f}")
    s = summ(tB); print(f"   BTC  {str(kB):<40} n {s['n']:4d} avg ${s['avg']:6.0f} PF {s['pf']:.2f} t {s['t']:4.1f} yrs+ {s['yp']}/{s['ny']} | des t {s['ta']:4.1f} hold ${s['ab']:5.0f} t {s['tb']:4.1f}")
    s = summ(WFS); print(f"   CL walk-forward 2020-26                       n {s['n']:4d} avg ${s['avg']:6.0f} PF {s['pf']:.2f} t {s['t']:4.1f} yrs+ {s['yp']}/{s['ny']} | hold ${s['ab']:5.0f} t {s['tb']:4.1f}")
    pickle.dump(dict(picks={k: (v[0], v[1][v[0]]) for k, v in PICK.items()}, wf=WFS, btc=resB, btc_pick=kB, adv=[(a, b, c) for a, b, c in ADV],
                     frames={k: v for k, v in FR.items()}), open(SP + "s_rank_gap2.pkl", "wb"))
