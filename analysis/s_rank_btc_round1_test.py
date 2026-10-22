"""S-rank program, Bitcoin round 1 (S_RANK_PROGRAM.md, 2026-10-14): CME Bitcoin futures, Dec 2018 - Oct 2026, CT.

Per 1 BTC (= 10 MBT, $1 a point): $25 a round trip (10 MBT x $2.50) + 1 tick (5 points = $5) per market / stop fill,
same conventions as analysis/btc_momentum_test.py. Daily P&L on every weekday trading day from 2019-01-01 (0 when
flat); a trade belongs to the session it is in (entries from 17:00 CT belong to the next weekday session).
Design 2019-22, holdout 2023-26; variants are picked by design-period t only. Every rule is compared with the same
window always-long and a random-side placebo (BTC rose ~30x, so drift matters).
  H1  CME weekend gap (Friday 16:00 -> Sunday 17:00 reopen, gap in 15-day ATR units): follow / fade from the Sunday
      open to Sunday 20:00 / Monday 2:00 / 8:30 / 15:00, ATR stops, by gap size (entry on the bar AFTER the opening
      print, since the gap is only known from it; filling at the print itself is shown as a look-ahead line, and
      entry delays of 1-59 minutes); gap-fill rate vs a matched placebo
      (Wednesday / Thursday 17:01 vs the price 49 h earlier, same 22 h horizon); the Mon-Thu 16:00-17:00
      maintenance-break gap.
  H2  Intraday seasonality: 46 tradable 30-minute windows, by year, before / since the spot ETFs (11 Jan 2024),
      Bonferroni threshold and expected false positives; the best design window traded with costs; the ETF
      benchmark (15:00 CT) dip-and-bounce seen since 2024, with the pre-ETF years as placebo.
  H3  NQ engine ports: Vault Break v1 (prices x 0.05 so one tick = 0.25; point target / stop scaled by the BTC / NQ
      ATR ratio, fixed and prior-year adaptive; long and mirrored short side), Overnight Bias (plain and ADX30,
      ATR stop, 3R), time-series momentum (prior 24 h / 5 days sign -> hold 8:31 -> 15:00).
  H4  NQ spillover: NQ 8:30 -> 10:00 move >= k ATR -> BTC follows 10:01 -> 15:00; ES / YM / BTC-own moves and random
      days as placebos.
  Candidates (|t| >= 2.5 with the same sign in 2019-22 and 2023-26): metrics.py whole / longs / shorts, by year,
  resampling.py bootstrap + permutation on 2023+, correlation with NQ 8:30 -> 15:00.
  python3 analysis/s_rank_btc_round1_test.py [SCRATCH_DIR]
"""
import sys, os, copy, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import Grid24, jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
TICK, COMM = 5.0, 25.0                      # per 1 BTC: tick 5 points = $5, commission $25 a round trip
SPLIT, START, ETF = pd.Timestamp("2023-01-01"), pd.Timestamp("2019-01-01"), pd.Timestamp("2024-01-11")
CAND = {}                                    # name -> trades (for the candidate stage)


def load_btc():
    pk = SP + "btc.pkl"
    if os.path.exists(pk): return pickle.load(open(pk, "rb"))
    G = Grid24("data/BTC_1min_20*.csv", night_pattern=""); pickle.dump(G, open(pk, "wb"), protocol=4); return G


G = load_btc()
TS = pd.DatetimeIndex(G.ts); DOW = TS.dayofweek.to_numpy()
O, H, L, C = (getattr(G, k).ravel() for k in "ohlc")
CF = pd.Series(C).ffill().to_numpy()
N = len(O)
_idx = np.where(~np.isnan(O), np.arange(N), N)
NXT = np.r_[np.minimum.accumulate(_idx[::-1])[::-1], N]          # first bar with a trade at or after i
ATR = G.daily_atr(15)
TRALL = np.asarray(G.trading)
TR = TRALL[TS[TRALL] >= START]; DAYS = TS[TR]


def session_row(i):
    """Weekday session a trade entered at flat bar i belongs to (from 17:00 CT: the next weekday)."""
    r, j = i // 1440, i % 1440
    r = np.where(j >= 1020, r + 1, r)
    k = np.minimum(np.searchsorted(TRALL, r), len(TRALL) - 1)
    return TRALL[k]


def sim(e_i, x_i, side, stop=None):
    """Market entry at the open of the first traded bar >= e_i (+1 tick), out at the close of x_i (-1 tick) or at a
    stop `stop` points away (-1 tick, gap-through at the bar open). Returns net $ per BTC (nan = no fill)."""
    e_i, x_i, side = (np.atleast_1d(np.asarray(a)) for a in (e_i, x_i, side))
    st = np.full(len(e_i), np.nan) if stop is None else np.broadcast_to(np.asarray(stop, float), e_i.shape)
    out = np.full(len(e_i), np.nan)
    for k in range(len(e_i)):
        e, x, s = int(NXT[int(e_i[k])]), int(x_i[k]), int(side[k])
        if s == 0 or e > x or e >= N: continue
        ep = O[e] + s * TICK
        px = CF[x]
        if np.isfinite(st[k]):
            sp = ep - s * st[k]
            seg = L[e:x + 1] <= sp if s > 0 else H[e:x + 1] >= sp
            if seg.any():
                j = e + int(np.argmax(seg)); oo = O[j]
                px = sp if (j == e or np.isnan(oo)) else (min(oo, sp) if s > 0 else max(oo, sp))
        out[k] = (px - s * TICK - ep) * s - COMM
    return out


def frame(e_i, side, net):
    t = pd.DataFrame(dict(date=TS[session_row(np.asarray(e_i))], side=np.asarray(side), net=np.asarray(net, float),
                          e_i=np.asarray(e_i)))
    t = t[t.net.notna() & (t.date >= START)]
    return t.sort_values("date").reset_index(drop=True)


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def stats(t):
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); a, b = x[y < 2023], x[y >= 2023]
    return dict(n=len(x), avg=x.mean(), pf=pf(x), t=tstat(x), yp=int((by > 0).sum()), ny=len(by),
                ta=tstat(a), tb=tstat(b), aa=a.mean(), ab=b.mean())


def line(t, nm, w=46):
    if len(t) < 5: return f"{nm:<{w}} n={len(t)}"
    s = stats(t); Lg, Sh = t.net[t.side > 0], t.net[t.side < 0]
    return (f"{nm:<{w}} n={s['n']:4d} win {np.mean(t.net > 0):.0%} avg ${s['avg']:6.0f} PF {s['pf']:.2f} t={s['t']:5.1f}"
            f" yrs+ {s['yp']}/{s['ny']} | 19-22 ${s['aa']:5.0f} t {s['ta']:4.1f} | 23-26 ${s['ab']:5.0f} t {s['tb']:4.1f}"
            f" | L {len(Lg)} ${Lg.mean() if len(Lg) else 0:5.0f} S {len(Sh)} ${Sh.mean() if len(Sh) else 0:5.0f}")


def daily(t):
    return t.groupby(t.date.dt.normalize()).net.sum().reindex(DAYS, fill_value=0.0)


def placebo(e_i, x_i, side, stop=None, runs=20):
    """Same entries / exits / stops: always long, and random sides (mean and range of the average over `runs`)."""
    lg = sim(e_i, x_i, np.ones(len(e_i), int), stop); sh = sim(e_i, x_i, -np.ones(len(e_i), int), stop)
    rng = np.random.default_rng(7); avgs, ts_ = [], []
    for _ in range(runs):
        r = rng.choice([-1, 1], len(e_i)); x = np.where(r > 0, lg, sh); avgs.append(np.nanmean(x)); ts_.append(tstat(x))
    return (f"   placebo: always long ${np.nanmean(lg):.0f} (t {tstat(lg):.1f}); random side ${np.mean(avgs):.0f}"
            f" [{min(avgs):.0f}..{max(avgs):.0f}], t range [{min(ts_):.1f}..{max(ts_):.1f}]")


def keep(name, t, family):
    CAND[name] = (t, family)


# ======================================================================================================== H1
def h1():
    print("\n" + "=" * 110 + "\nH1. CME weekend gap (Friday last price -> Sunday 17:00 reopen) and the Mon-Thu 16:00-17:00 break gap")
    sun = np.where((DOW == 6) & (TS >= pd.Timestamp("2018-12-30")))[0]; sun = sun[sun + 1 < G.D]
    rows = []
    for s in sun:
        e = NXT[s * 1440 + jof(1701)]
        if e >= (s + 1) * 1440 or e >= N: continue                       # no Sunday reopen (holiday weekend)
        if np.isnan(G.c[s + 1]).all(): continue                           # Monday closed
        prev = CF[s * 1440 + jof(1700)]; a = ATR[s + 1]
        if np.isnan(prev) or np.isnan(a): continue
        rows.append((s, e, prev, O[e], a))
    W = pd.DataFrame(rows, columns=["s", "e", "prev", "op", "atr"]); W["gap"] = (W.op - W.prev) / W.atr
    W["date"] = TS[W.s + 1]
    W["ei"] = W.e + 1          # the gap is known only from the opening print: trade from the next bar (no look-ahead)
    print(f"   {len(W)} Sunday reopens {W.date.iloc[0].date()} .. {W.date.iloc[-1].date()}; |gap| median {W.gap.abs().median():.2f} ATR,"
          f" 75% {W.gap.abs().quantile(.75):.2f}, 90% {W.gap.abs().quantile(.9):.2f}; mean signed gap {W.gap.mean():+.3f} ATR")
    EX = {"Sun 20:00": lambda s: s * 1440 + jof(2000), "Mon 02:00": lambda s: (s + 1) * 1440 + jof(200),
          "Mon 08:30": lambda s: (s + 1) * 1440 + jof(830), "Mon 15:00": lambda s: (s + 1) * 1440 + jof(1500)}
    # descriptive: signed continuation in ATR units (no costs) by gap bucket
    bk = pd.cut(W.gap.abs(), [0, .1, .25, .5, 1, 99], right=False)
    D = pd.DataFrame({"bucket": bk, "n": 1})
    for nm, f in EX.items():
        D[nm] = np.sign(W.gap) * (CF[f(W.s.values)] - W.op) / W.atr
    seg_fill = []
    for _, r in W.iterrows():
        x = int((r.s + 1) * 1440 + jof(1500)); e = int(r.e)
        seg_fill.append((np.nanmin(L[e:x + 1]) <= r.prev) if r.op > r.prev else (np.nanmax(H[e:x + 1]) >= r.prev))
    D["fill"] = np.array(seg_fill, float)
    print("   continuation in the gap's direction, mean ATR (no costs), and gap-fill rate by Monday 15:00, by |gap|:")
    g = D.groupby("bucket").agg(n=("n", "sum"), **{k: (k, "mean") for k in EX}, fill=("fill", "mean"))
    print("   " + g.round(3).to_string().replace("\n", "\n   "))
    for nm in EX:
        print(f"   t of continuation to {nm}: all {tstat(D[nm]):+.1f}; |gap| >= 0.25: {tstat(D[nm][W.gap.abs() >= .25]):+.1f}")
    # matched placebo for the fill rate: Wed / Thu 17:01, reference price 49 h earlier (2 days before, 16:00), horizon 22 h
    pr = []
    for d in np.where(np.isin(DOW, [2, 3]) & (TS >= START))[0]:
        if d + 1 >= G.D or np.isnan(ATR[d]): continue
        e = NXT[d * 1440 + jof(1701)]
        if e >= (d + 1) * 1440: continue
        ref = CF[(d - 2) * 1440 + jof(1600)]; x = (d + 1) * 1440 + jof(1500)
        if np.isnan(ref) or np.isnan(G.c[d + 1]).all(): continue
        op = O[e]; pr.append(((op - ref) / ATR[d], (np.nanmin(L[e:x + 1]) <= ref) if op > ref else (np.nanmax(H[e:x + 1]) >= ref)))
    P = pd.DataFrame(pr, columns=["gap", "fill"])
    pb = P.groupby(pd.cut(P.gap.abs(), [0, .1, .25, .5, 1, 99], right=False)).fill.agg(["count", "mean"])
    print("   'gap fill' placebo (Wed/Thu 17:01 vs the price 49 h earlier, touch by next day 15:00) by |distance|:")
    print("   " + pd.concat({"weekend n": g.n, "weekend fill": g.fill.round(2), "placebo n": pb["count"],
                             "placebo fill": pb["mean"].round(2)}, axis=1).to_string().replace("\n", "\n   "))

    # trades
    print("\n   Trades from the bar after the Sunday opening print (follow = trade in the gap's direction; fade = against it):")
    best = None
    for nm, f in EX.items():
        for gmin in (0.0, 0.25, 0.5):
            for st in (None, 0.5, 1.0):
                w = W[W.gap.abs() >= gmin]
                if len(w) < 20: continue
                stop = None if st is None else st * w.atr.values
                x_i = f(w.s.values); sg = np.sign(w.gap.values).astype(int)
                for mode, sd in (("follow", sg), ("fade", -sg)):
                    t = frame(w.ei.values, sd, sim(w.ei.values, x_i, sd, stop))
                    lab = f"{mode} -> {nm}, |gap|>={gmin}, stop {st if st else '-'}"
                    print("   " + line(t, lab))
                    s_ = stats(t)
                    if best is None or s_["ta"] > best[0]: best = (s_["ta"], lab, t, w.ei.values, x_i, sd, stop)
    print(f"\n   best design-period (2019-22) t of the 72 variants (tradable sign): {best[1]}")
    print("   " + line(best[2], best[1])); print(placebo(best[3], best[4], best[5], best[6]))
    keep("H1 weekend gap: " + best[1], best[2], "H1")
    # how robust is the continuation? gross (no costs), by period; entry delays; open-bar liquidity; matched placebo
    big = W.gap.abs() >= 0.25; y = W.date.dt.year
    for nm in ("Sun 20:00", "Mon 02:00"):
        x = D[nm]
        print(f"   gross continuation to {nm}, |gap|>=0.25 (ATR): 2019-22 {x[big & (y < 2023)].mean():+.3f} (t {tstat(x[big & (y < 2023)]):+.1f}),"
              f" 2023-26 {x[big & (y >= 2023)].mean():+.3f} (t {tstat(x[big & (y >= 2023)]):+.1f}); by year "
              f"{x[big].groupby(y[big]).mean().round(2).to_dict()}")
    fb = (G.h.ravel()[W.e.values] - G.l.ravel()[W.e.values]); vb = G.v.ravel()[W.e.values]
    vtyp = np.nanmedian(G.v[TR][:, jof(900):jof(1400)])
    print(f"   Sunday open bar: median high-low {np.nanmedian(fb):.0f} points ({np.nanmedian(fb) / TICK:.0f} ticks), median volume {np.nanmedian(vb):.0f}"
          f" contracts vs {vtyp:.0f} in a 9:00-14:00 minute -> 1 tick of slippage at the open is optimistic")
    w = W[big]; sg = np.sign(w.gap.values).astype(int); stp = 0.5 * w.atr.values
    t = frame(w.e.values, sg, sim(w.e.values, EX["Sun 20:00"](w.s.values), sg, stp))
    print("   " + line(t, "LOOK-AHEAD: filled AT the opening print -> Sun 20:00") + "  (only via the opening auction, without knowing the gap)")
    for dl in (1, 4, 14, 29, 59):
        e_d = np.maximum(w.ei.values, w.s.values * 1440 + jof(1701) + dl)
        for nm in ("Sun 20:00", "Mon 02:00"):
            t = frame(e_d, sg, sim(e_d, EX[nm](w.s.values), sg, stp))
            print("   " + line(t, f"follow |gap|>=0.25 stop 0.5, entry {(1021 + dl) // 60}:{(1021 + dl) % 60:02d} -> {nm}"))
    for a_, b_ in ((None, 1705), (1705, 2000), (1730, 2000)):
        p0 = w.op.values if a_ is None else CF[w.s.values * 1440 + jof(a_)]
        x = np.sign(w.gap.values) * (CF[w.s.values * 1440 + jof(b_)] - p0) / w.atr.values
        print(f"   gross continuation {'open' if a_ is None else a_} -> {b_}, |gap|>=0.25: {x.mean():+.3f} ATR (t {tstat(x):+.1f})")
    nadv = 0; bx = None
    for nm, f in EX.items():
        for gmin in (0.0, 0.25, 0.5):
            for st in (None, 0.5, 1.0):
                ww = W[W.gap.abs() >= gmin]; sgg = np.sign(ww.gap.values).astype(int)
                t = frame(ww.ei.values, sgg, sim(ww.ei.values, f(ww.s.values), sgg, None if st is None else st * ww.atr.values))
                s_ = stats(t); nadv += (s_["t"] >= 2.5) and s_["ta"] > 0 and s_["tb"] > 0
                if bx is None or s_["t"] > bx[0]:
                    bx = (s_["t"], f"follow -> {nm}, |gap|>={gmin}, stop {st if st else '-'}", t, ww.ei.values, f(ww.s.values), sgg,
                          None if st is None else st * ww.atr.values)
    print(f"   follow variants meeting the advance rule (t >= 2.5, both periods > 0): {nadv} of 36")
    # matched placebo: Tue-Thu 17:01, follow the move since 49 h earlier (|move| >= 0.25 ATR), stop 0.5 ATR, out 20:00
    rows = []
    for d in np.where(np.isin(DOW, [1, 2, 3]) & (TS >= START))[0]:
        if np.isnan(ATR[d]): continue
        e = NXT[d * 1440 + jof(1701)]
        if e >= d * 1440 + jof(1800): continue
        ref = CF[(d - 2) * 1440 + jof(1600)]
        if np.isnan(ref): continue
        rows.append((d, e, (O[e] - ref) / ATR[d], ATR[d]))
    Pp = pd.DataFrame(rows, columns=["d", "e", "mv", "atr"]); Pp = Pp[Pp.mv.abs() >= 0.25]
    sgp = np.sign(Pp.mv.values).astype(int)
    for nm, xf in (("20:00", lambda d: d * 1440 + jof(2000)), ("next 02:00", lambda d: (d + 1) * 1440 + jof(200))):
        t = frame(Pp.e.values + 1, sgp, sim(Pp.e.values + 1, xf(Pp.d.values), sgp, 0.5 * Pp.atr.values))
        print("   " + line(t, f"placebo Tue-Thu 17:01 follow 49h move -> {nm}"))
    # strongest variant that meets the advance rule (post hoc, for the candidate stage)
    print(f"   post hoc: best overall t of the 36 follow variants: {bx[1]}"); print(placebo(*bx[3:]))
    keep("H1 weekend gap (post hoc, best overall t): " + bx[1], bx[2], "H1x")
    # mid-week maintenance break gap
    print("\n   Mon-Thu maintenance break (16:00 -> 17:00 reopen) gap:")
    rows = []
    for d in TRALL[(DOW[TRALL] <= 3) & (TS[TRALL] >= START)]:
        if d + 1 >= G.D or np.isnan(ATR[d]): continue
        e = NXT[d * 1440 + jof(1701)]
        if e >= d * 1440 + jof(1800): continue
        prev = CF[d * 1440 + jof(1600)]
        if np.isnan(prev) or np.isnan(G.c[d + 1]).all(): continue
        rows.append((d, e, prev, O[e], ATR[d]))
    B = pd.DataFrame(rows, columns=["d", "e", "prev", "op", "atr"]); B["gap"] = (B.op - B.prev) / B.atr; B["ei"] = B.e + 1
    print(f"   {len(B)} breaks; |gap| median {B.gap.abs().median():.3f} ATR, 90% {B.gap.abs().quantile(.9):.3f}")
    EXB = {"20:00": lambda d: d * 1440 + jof(2000), "next 02:00": lambda d: (d + 1) * 1440 + jof(200),
           "next 08:30": lambda d: (d + 1) * 1440 + jof(830), "next 15:00": lambda d: (d + 1) * 1440 + jof(1500)}
    bestb = None
    for nm, f in EXB.items():
        for gmin in (0.0, 0.05, 0.1):
            w = B[B.gap.abs() >= gmin]; sg = np.sign(w.gap.values).astype(int); x_i = f(w.d.values)
            for mode, sd in (("follow", sg), ("fade", -sg)):
                t = frame(w.ei.values, sd, sim(w.ei.values, x_i, sd))
                lab = f"break {mode} -> {nm}, |gap|>={gmin}"
                print("   " + line(t, lab)); s_ = stats(t)
                if bestb is None or s_["ta"] > bestb[0]: bestb = (s_["ta"], lab, t, w.ei.values, x_i, sd)
    print(f"   best design variant of 24: {bestb[1]}"); print("   " + line(bestb[2], bestb[1])); print(placebo(*bestb[3:]))
    keep("H1 break gap: " + bestb[1], bestb[2], "H1b")


# ======================================================================================================== H2
def open_mask(dow, j0):
    """CME Bitcoin open for the whole 30-min window starting at column j0 (minutes j0+1 .. j0+30)."""
    a, b = j0, j0 + 30
    if dow == 5: return False
    if dow == 6: return a >= 1020
    if dow == 4: return b <= 960
    return not (a < 1020 and b > 960)


def h2():
    print("\n" + "=" * 110 + "\nH2. Intraday seasonality: 30-minute windows (bp, log return from the first trade in the window to its last close), 2019-2026")
    rows = np.where((TS >= START) & (DOW != 5))[0]; rows = rows[rows + 1 < G.D]
    K = 48; Rm = np.full((len(rows), K), np.nan); cnt = np.zeros((len(rows), K))
    has = ~np.isnan(G.c[rows])
    for k in range(K):
        ok = np.array([open_mask(DOW[r], 30 * k) for r in rows])
        a = rows * 1440 + 30 * k; b = a + 30
        traded = has[:, 30 * k + 1:30 * k + 31].sum(1) if k < 47 else np.r_[has[:, 1411:1440].sum(1)]
        if k == 47: traded = traded + ~np.isnan(G.c[rows + 1, 0])
        e = NXT[a + 1]; e_ok = e <= b                                 # tradable: from the first trade in the window
        r = 1e4 * np.log(CF[b] / O[np.minimum(e, N - 1)])
        m = ok & (traded > 0) & e_ok & np.isfinite(r)
        Rm[m, k] = r[m]
    yr = TS[rows].year.to_numpy(); post = TS[rows] >= ETF
    allmean = np.nanmean(Rm)
    out = []
    for k in range(K):
        x = Rm[:, k]; m = ~np.isnan(x)
        if m.sum() < 100: continue
        by = pd.Series(x[m]).groupby(yr[m]).mean()
        sg = np.sign(np.nanmean(x))
        out.append(dict(win=f"{(30 * k) // 60:02d}:{(30 * k) % 60:02d}", n=int(m.sum()), bp=np.nanmean(x), t=tstat(x[m]),
                        t_ex=tstat(x[m] - allmean), yrs=int((np.sign(by) == sg).sum()), ny=len(by),
                        since21=int((np.sign(by[by.index >= 2021]) == sg).sum()),
                        t_1922=tstat(x[m & (yr < 2023)]), t_2326=tstat(x[m & (yr >= 2023)]),
                        t_pre=tstat(x[m & ~post]), t_post=tstat(x[m & post]), bp_post=np.nanmean(x[post])))
    T = pd.DataFrame(out).set_index("win")
    nw = len(T)
    from statistics import NormalDist
    nd = NormalDist(); sf = lambda z: 1 - nd.cdf(z)
    bonf = nd.inv_cdf(1 - 0.025 / nw)
    print(f"   {nw} tradable windows; all-window mean {allmean:+.2f} bp (drift); t_ex = t of (window - all-window mean)")
    print(f"   Bonferroni |t| for 5% family-wise over {nw} windows: {bonf:.2f}; expected false positives at |t|>=3: {nw * 2 * sf(3):.2f},"
          f" at |t|>=2: {nw * 2 * sf(2):.1f}")
    print("   " + T.round(2).to_string().replace("\n", "\n   "))
    for col in ("t", "t_post", "t_pre", "t_1922"):
        print(f"   windows with |{col}| >= 3: {list(T.index[T[col].abs() >= 3])}; >= Bonferroni: {list(T.index[T[col].abs() >= bonf])}")
    cons = T[(T.since21 == (T.ny - 2)) & (T.t.abs() >= 3)]
    print(f"   windows same sign every year since 2021 and |t| >= 3: {list(cons.index)}")
    # trade the best design window (largest |t_1922|), sign from design
    w = T.t_1922.abs().idxmax(); k = int(w[:2]) * 2 + int(w[3:]) // 30; sd = int(np.sign(T.loc[w, "t_1922"]))
    sel = rows[~np.isnan(Rm[:, k])]
    e_i = sel * 1440 + 30 * k + 1; x_i = sel * 1440 + 30 * k + 30; side = np.full(len(sel), sd)
    t = frame(e_i, side, sim(e_i, x_i, side))
    print(f"\n   best design window {w} ({'long' if sd > 0 else 'short'}, chosen by 2019-22 |t| among {nw}):")
    print("   " + line(t, f"30-min window {w} {'long' if sd > 0 else 'short'}")); print(placebo(e_i, x_i, side))
    keep(f"H2 window {w} {'long' if sd > 0 else 'short'}", t, "H2")
    # the post-ETF best window, honest: chosen on 2024+ itself (in-sample), shown for information
    w2 = T.t_post.abs().idxmax(); k2 = int(w2[:2]) * 2 + int(w2[3:]) // 30; sd2 = int(np.sign(T.loc[w2, "t_post"]))
    sel2 = rows[~np.isnan(Rm[:, k2]) & post]
    e2 = sel2 * 1440 + 30 * k2 + 1; x2 = sel2 * 1440 + 30 * k2 + 30; s2 = np.full(len(sel2), sd2)
    t2 = frame(e2, s2, sim(e2, x2, s2))
    print(f"   best since-ETF window {w2} (chosen in-sample on 2024+, for information): " + line(t2, "", 1))
    # named windows: US open 8:30-9:00, ETF NAV hour 14:00-15:00, Asian open 19:00-20:00 CT
    for nm, ks in (("US open 8:30-9:00", [17]), ("ETF NAV 14:00-15:00", [28, 29]), ("Asia open 19:00-20:00", [38, 39])):
        x = np.nansum(Rm[:, ks], 1); m = ~np.isnan(Rm[:, ks]).any(1)
        print(f"   {nm:<24} mean {x[m].mean():+.1f} bp t {tstat(x[m]):+.1f} | pre-ETF t {tstat(x[m & ~post]):+.1f} | since ETF {x[m & post].mean():+.1f} bp t {tstat(x[m & post]):+.1f}")
    # ETF benchmark (CF BRRNY 15:00 CT) dip-and-bounce seen since 2024 (14:30 down, 15:00 up): in-sample idea, pre-ETF = placebo
    tr = TR; a1, a2 = sim(tr * 1440 + jof(1431), tr * 1440 + jof(1500), -np.ones(len(tr), int)), sim(tr * 1440 + jof(1501), tr * 1440 + jof(1530), np.ones(len(tr), int))
    for nm, x, sd in (("short 14:31-15:00", a1, -1), ("long 15:01-15:30", a2, 1), ("both legs", np.nan_to_num(a1) + np.nan_to_num(a2), 0)):
        t = pd.DataFrame(dict(date=DAYS, side=sd if sd else 1, net=x)).dropna()
        print("   " + line(t[t.date < ETF], f"ETF fix {nm}, before ETFs") + "\n   " + line(t[t.date >= ETF], f"ETF fix {nm}, since ETFs (in-sample)"))


# ======================================================================================================== H3
def scaled(G0, k, neg=False):
    Hh = copy.copy(G0)
    if neg:
        Hh.o, Hh.c, Hh.h, Hh.l = -G0.o * k, -G0.c * k, -G0.l * k, -G0.h * k
    else:
        for a in "ohlc": setattr(Hh, a, getattr(G0, a) * k)
    return Hh


def engine_frame(t, pv, side_sign, slip_kinds=False):
    """Engine trades on the scaled grid -> $ per BTC. pv = $ per scaled point (20). slip_kinds: add 1 tick for the stop
    entry and 1 for a stop / time exit (overnight_bias24 has no slippage built in)."""
    if not len(t): return pd.DataFrame(columns=["date", "side", "net", "e_i"])
    net = (t.exit - t.entry) * t.side * pv - COMM
    if slip_kinds: net = net - TICK * (1 + (t.kind != 1).astype(int))
    e_i = t.day.values * 1440 + t.j0.values
    f = pd.DataFrame(dict(date=pd.DatetimeIndex(TS[t.day.values]), side=t.side.values * side_sign, net=net.values, e_i=e_i,
                          x_i=t.day.values * 1440 + t.j1.values))
    return f[f.date >= START].reset_index(drop=True)


def h3(g):
    print("\n" + "=" * 110 + "\nH3. NQ engine ports (prices x 0.05: one BTC tick = 0.25 scaled; $20 a scaled point per BTC)")
    import vault_break_v8_test as VB
    from candidates24 import overnight_bias24
    k = 0.05; Gs = scaled(G, k); Gn = scaled(G, k, neg=True)
    atr_s = Gs.daily_atr(15); atr_n = g.daily_atr(15)
    nq_tr = np.asarray(g.trading)[pd.DatetimeIndex(g.ts[g.trading]) >= START]
    med_n = np.nanmedian(atr_n[nq_tr]); ratio = np.nanmedian(atr_s[TR]) / med_n
    print(f"   BTC / NQ ATR ratio (scaled points per NQ point, 2019-26 medians): {ratio:.2f}; by year:",
          {y: round(float(np.nanmedian(atr_s[TR][DAYS.year == y]) / med_n), 2) for y in range(2019, 2027)})
    VB.TICK = 0.25
    res = {}
    for side_nm, GG, sgn in (("long", Gs, 1), ("short (mirrored)", Gn, -1)):
        t = engine_frame(VB.run(GG, "v1", tp=40 * ratio, sl=75 * ratio, years=(2019, 2026)), 20.0, sgn)
        res[f"VB {side_nm}, fixed tp/sl"] = t
        parts = []
        for y in range(2019, 2027):                                       # prior-year ATR ratio (no look-ahead)
            prev = TR[DAYS.year == y - 1] if y > 2019 else TRALL[TS[TRALL].year == 2018]
            ry = np.nanmedian(atr_s[prev]) / med_n
            parts.append(VB.run(GG, "v1", tp=40 * ry, sl=75 * ry, years=(y, y)))
        res[f"VB {side_nm}, prior-year ratio"] = engine_frame(pd.concat(parts, ignore_index=True), 20.0, sgn)
    for nm, t in res.items(): print("   " + line(t, "Vault Break " + nm[3:]))
    vb_both = pd.concat([res["VB long, prior-year ratio"], res["VB short (mirrored), prior-year ratio"]]).sort_values("date")
    print("   " + line(vb_both, "Vault Break both sides, prior-year ratio"))
    print(placebo(vb_both.e_i.values, vb_both.x_i.values, vb_both.side.values))
    best = max(list(res.items()) + [("VB both, prior-year ratio", vb_both)], key=lambda kv: stats(kv[1])["ta"])
    keep("H3 " + best[0], best[1], "H3vb")
    # Overnight Bias
    ob = {}
    for adx_min in (-1, 20, 30):
        for st in (0.25, 0.30, 0.50):
            t = overnight_bias24(Gs, adx_min=adx_min, stop_atr=st)
            t = t[pd.DatetimeIndex(t.date) >= START] if len(t) else t
            # engine has no slippage: + 1 tick on the stop entry and on stop / time exits
            ob[f"ONB ADX>{adx_min} stop {st} ATR"] = engine_frame(t, 20.0, 1, slip_kinds=True)
    for nm, t in ob.items(): print("   " + line(t, nm))
    bo = max(ob.items(), key=lambda kv: stats(kv[1])["ta"])
    print(f"   best ONB by design t (of 9): {bo[0]}"); print(placebo(bo[1].e_i.values, bo[1].x_i.values, bo[1].side.values))
    keep("H3 " + bo[0], bo[1], "H3onb")
    # time-series momentum
    tm = {}
    for nm, lag in (("prior 24 h", 1), ("prior 5 days", 5)):
        for st in (None, 1.0):
            rows = TR[1 + 5:]; ip = np.searchsorted(TRALL, rows)
            now = CF[rows * 1440 + jof(830)]; then = CF[TRALL[ip - lag] * 1440 + jof(830)]
            sd = np.sign(now - then).astype(int); e_i = rows * 1440 + jof(831); x_i = rows * 1440 + jof(1500)
            stop = None if st is None else st * ATR[rows]
            t = frame(e_i, sd, sim(e_i, x_i, sd, stop)); tm[f"TSMOM {nm}, stop {st or '-'}"] = (t, e_i, x_i, sd, stop)
            print("   " + line(t, f"TSMOM {nm} -> 8:31-15:00, stop {st or '-'} ATR"))
    bt = max(tm.items(), key=lambda kv: stats(kv[1][0])["ta"])
    print(f"   best TSMOM by design t (of 4): {bt[0]}"); print(placebo(*bt[1][1:]))
    keep("H3 " + bt[0], bt[1][0], "H3ts")


# ======================================================================================================== H4
def h4(g, es, ym):
    print("\n" + "=" * 110 + "\nH4. NQ spillover: big NQ 8:30 -> 10:00 move -> BTC 10:01 -> 15:00 in the same direction")
    def move(GG):
        cf = pd.Series(GG.c.ravel()).ffill().to_numpy(); a = GG.daily_atr(15)
        rr = np.searchsorted(GG.dates, G.dates[TR]); ok = (rr < GG.D) & (GG.dates[np.minimum(rr, GG.D - 1)] == G.dates[TR])
        rr = np.minimum(rr, GG.D - 1)
        m = (cf[rr * 1440 + jof(1000)] - cf[rr * 1440 + jof(830)]) / a[rr]
        has = ~np.isnan(GG.c[rr, jof(831):jof(1001)]).all(1)
        return np.where(ok & has, m, np.nan)
    MV = {"NQ": move(g), "ES": move(es), "YM": move(ym), "BTC own": move(G)}
    e_i = TR * 1440 + jof(1001); x_i = TR * 1440 + jof(1500)
    btc_r = (CF[x_i] - CF[TR * 1440 + jof(1000)]) / ATR[TR]
    yr = DAYS.year
    for nm, m in MV.items():
        ok = ~np.isnan(m) & ~np.isnan(btc_r)
        cc = pd.Series([np.corrcoef(m[ok & (yr == y)], btc_r[ok & (yr == y)])[0, 1] for y in range(2019, 2027)], index=range(2019, 2027))
        print(f"   corr({nm} 8:30->10:00, BTC 10:00->15:00): all {np.corrcoef(m[ok], btc_r[ok])[0, 1]:+.3f}; by year {cc.round(2).to_dict()}")
    nq_rt = np.searchsorted(g.dates, G.dates[TR])
    best = None
    for nm, m in MV.items():
        for thr in (0.3, 0.5, 0.75):
            sel = np.where(np.abs(m) >= thr)[0]; sd = np.sign(m[sel]).astype(int)
            for st in (None, 0.5):
                stop = None if st is None else st * ATR[TR[sel]]
                t = frame(e_i[sel], sd, sim(e_i[sel], x_i[sel], sd, stop))
                lab = f"{nm} |move|>={thr} ATR, follow, stop {st or '-'}"
                print("   " + line(t, lab))
                if nm == "NQ":
                    s_ = stats(t)
                    if best is None or s_["ta"] > best[0]: best = (s_["ta"], lab, t, e_i[sel], x_i[sel], sd, stop)
    print(f"   best NQ variant by design t (of 6): {best[1]}"); print(placebo(*best[3:]))
    rng = np.random.default_rng(3); n = len(best[2]); av = []
    for _ in range(50):
        sel = rng.choice(len(TR), n, replace=False); sd = rng.choice([-1, 1], n)
        av.append(np.nanmean(sim(e_i[sel], x_i[sel], sd)))
    print(f"   random days, random side (50 x {n} days): avg ${np.mean(av):.0f} [{np.percentile(av, 5):.0f}..{np.percentile(av, 95):.0f}]")
    keep("H4 " + best[1], best[2], "H4")


# ======================================================================================================== candidates
def nq_rth(g):
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); tr = np.asarray(g.trading)
    s = pd.Series((cf[tr * 1440 + jof(1500)] - cf[tr * 1440 + jof(830)]) * 20.0, index=pd.DatetimeIndex(g.ts[tr]))
    return s


def candidates(g):
    print("\n" + "=" * 110 + "\nCandidates: the best design-period variant of each family; advance = t >= 2.5 after costs, positive in 2019-22 and 2023-26")
    nq = nq_rth(g); adv = []
    for nm, (t, fam) in CAND.items():
        s = stats(t); ok = s["t"] >= 2.5 and s["ta"] > 0 and s["tb"] > 0              # a tradable (positive) edge only
        print(f"   {'ADVANCES' if ok else 'stops   '} " + line(t, nm, 70))
        if ok: adv.append(nm)
    if not adv:
        print("   nothing advances; full metrics shown for the best overall t anyway (for the record)")
        adv = [max(CAND, key=lambda k: stats(CAND[k][0])["t"])]
    for nm in adv:
        t = CAND[nm][0]; lg, sh = t[t.side > 0], t[t.side < 0]
        print(f"\n   --- {nm}")
        rows = {"whole": (daily(t), t.net)}
        if len(lg) > 5: rows["longs"] = (daily(lg), lg.net)
        if len(sh) > 5: rows["shorts"] = (daily(sh), sh.net)
        print("   " + M.table(rows).replace("\n", "\n   "))
        print("   by year $:", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
        d = daily(t); c = pd.concat([d, nq], axis=1, join="inner").corr().iloc[0, 1]
        print(f"   daily correlation with NQ 8:30->15:00 (1 NQ): {c:+.2f}")
        hold = {k: v[0][v[0].index >= SPLIT] for k, v in rows.items()}
        b, p = R.report(hold, n=3000)
        print("   bootstrap 2023+:\n   " + b.replace("\n", "\n   ")); print("   permutation 2023+:\n   " + p.replace("\n", "\n   "))


if __name__ == "__main__":
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(__doc__.split("\n")[0])
    print(f"BTC grid {G.dates[0]} .. {G.dates[-1]}; {len(TR)} weekday sessions from 2019; per 1 BTC after $25 + 1 tick per market/stop fill")
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    h1(); h2(); h3(g)
    es = pickle.load(open(SP + "ge.pkl", "rb")); ym = pickle.load(open(SP + "gy.pkl", "rb"))
    h4(g, es, ym); del es, ym
    candidates(g)
    pickle.dump({k: v[0] for k, v in CAND.items()}, open(SP + "s_rank_btc.pkl", "wb"))
