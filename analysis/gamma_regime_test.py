"""0DTE NDX dealer gamma (The Bridge, exported with multi_strategy/OFB_Gamma_Exporter.txt) on NQ, 2026-10-13.

Data: GEX_1min_<year>.csv (repo root), 1-minute bars 9:30-16:15 ET = 8:30-15:15 CT, 2022-09-01 .. 2026-07-07.
Only the cumulative weighting (flip, flip_steep, maj_pos, maj_neg) is used: it is the only backtest-legal one, and
only from 2023-03-28 (the options tape starts then). Levels are NDX points; + basis = NQ level. The Bridge's NQ
closes match the NQ grid on 97.6% of minutes after ET -> CT (-1 hour), so the levels go straight onto the grid.
Regime at a minute: price above the flip ("positive gamma": dealers damp moves) or below it ("negative gamma":
dealers amplify), counted only when the steepness is > 0.02 (the manual's "worth trusting"); else "weak / none".

1. Does the regime change how NQ moves? Every 30 minutes 9:00-14:30 CT: next-30-minute size and the
   correlation of the last 30 minutes with the next 30 (momentum > 0, reversion < 0), with realized-vol control.
2. The funded set's MultiCharts trades split by the regime known at entry (each side separately), and (2b) by the
   previous session's regime.
3. Stand-alone ideas: (a) follow / fade the first hour by regime; (b) flip-cross breakouts vs fake levels;
   (c) afternoon pin toward the major positive-gamma strike vs round strikes (placebo).
Costs: $7.25 per NQ + 1 tick per market / stop fill. Design 2023-03-28..2024-12-31, holdout 2025-01-01..2026-07-07.
  python3 analysis/gamma_regime_test.py [SCRATCH_DIR]
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from funded_lab import with_slippage
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
START, END, SPLIT = pd.Timestamp("2023-03-28"), pd.Timestamp("2026-07-07"), pd.Timestamp("2025-01-01")
STEEP = 0.02
REPORTS = {
    "VB": "Backtesting Strategy Performance Report VB v1.xlsx",
    "ONB_ML2": "Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx",
    "EOS": "Backtesting Strategy Performance Report EOS v1.xlsx",
    "MON": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx",
    "LDF": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx",
    "NFP": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes NFP Fade.xlsx",
    "VCS": "Backtesting Strategy Performance Report _ @NQ - 5 Minutes Vol-Control Sell Flow.xlsx",
    "ONB_ADX30 (combine)": "Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx",
}


def load_gex(g):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("GEX_1min_*.csv"))], ignore_index=True)
    row = np.searchsorted(g.dates, d.date.values); row = np.minimum(row, g.D - 1)
    ok = (g.dates[row] == d.date.values) & (pd.to_datetime(d.date.astype(str)) >= START).to_numpy()
    d, row = d[ok], row[ok]
    col = jof(d.time.values - 100)
    A = {}
    for k in ("flip", "flip_steep", "maj_pos", "maj_neg"):
        a = np.full((g.D, 1440), np.nan); v = d[k].to_numpy(float)
        v = np.where(v == 0, np.nan, v + (d.basis.to_numpy(float) if k != "flip_steep" else 0.0))
        a[row, col] = v; A[k] = a
    a = np.full((g.D, 1440), np.nan); a[row, col] = np.where(d.spot.values != 0, d.basis.values, np.nan); A["basis"] = a
    pres = np.zeros((g.D, 1440), bool); pres[row, col] = d.spot.values != 0
    A["present"] = pres
    return A


class Regime:
    """Regime known at the close of minute (d, m): the latest Bridge minute at or before it (same minute in the
    session; before 8:31 CT the previous session's last minute, at most 4 days old)."""
    def __init__(self, g, A):
        self.g, self.A = g, A
        self.idx = np.flatnonzero(A["present"].ravel())
        self.cf = pd.Series(g.c.ravel()).ffill().to_numpy()

    def at(self, d, m):
        t = d * 1440 + m
        k = np.searchsorted(self.idx, t, side="right") - 1
        if k < 0 or t - self.idx[k] > 4 * 1440: return "n/a", np.nan
        f, s = self.A["flip"].ravel()[self.idx[k]], self.A["flip_steep"].ravel()[self.idx[k]]
        px = self.cf[t]
        if np.isnan(f) or not s > STEEP: return "weak/none", np.nan
        return ("above" if px > f else "below"), (px - f) / px


def stat(x):
    x = np.asarray(x, float)
    if len(x) < 3: return f"n={len(x):4d}"
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return f"n={len(x):4d} avg ${x.mean():5.0f} t={x.mean() / x.std() * np.sqrt(len(x)):4.1f} win {np.mean(x > 0):.0%} PF {pf:.2f}"


def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan
    return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))


def trade(g, d, j_in, side, j_out, stop=None):
    """Market entry at the open of j_in, out at the close of j_out (or the stop): net $ per NQ."""
    o, h, l, c = g.o[d], g.h[d], g.l[d], g.c[d]
    while j_in <= j_out and np.isnan(o[j_in]): j_in += 1
    if j_in > j_out: return None
    e = o[j_in] + side * TICK
    for j in range(j_in, j_out + 1):
        if np.isnan(h[j]): continue
        if stop is not None and ((l[j] <= stop) if side > 0 else (h[j] >= stop)):
            px = ((min(o[j], stop) if side > 0 else max(o[j], stop)) if j > j_in else stop) - side * TICK
            return (px - e) * side * PV - COST
    cc = c[j_in:j_out + 1]; ok = np.flatnonzero(~np.isnan(cc))
    return (cc[ok[-1]] - side * TICK - e) * side * PV - COST


def last_c(g, d, j):
    r = g.c[d, :j + 1]; ok = np.flatnonzero(~np.isnan(r))
    return r[ok[-1]] if len(ok) else np.nan


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    A = load_gex(g); RG = Regime(g, A)
    ts = pd.DatetimeIndex(g.ts)
    days = [d for d in g.trading if START <= ts[d] <= END and A["present"][d].any()]
    print(__doc__.split("\n")[0]); print(f"sessions with gamma data: {len(days)} ({ts[days[0]].date()} .. {ts[days[-1]].date()})")
    reg_day = pd.Series([RG.at(d, jof(900))[0] for d in days])
    print("regime at 9:00 CT (10:00 ET):", reg_day.value_counts(normalize=True).round(2).to_dict())

    # ---------------- 1. regime and price behaviour ----------------
    print("\n1. Next 30 minutes by regime (samples every 30 minutes 9:00-14:30 CT):")
    rows = []
    for d in days:
        for hm in (900, 930, 1000, 1030, 1100, 1130, 1200, 1230, 1300, 1330, 1400, 1430):
            j = jof(hm)
            c0, cp, cf = last_c(g, d, j), last_c(g, d, j - 30), last_c(g, d, j + 30)
            seg = g.c[d, j - 60:j + 1]; seg = seg[~np.isnan(seg)]
            if np.isnan(c0) or np.isnan(cp) or np.isnan(cf) or len(seg) < 30: continue
            rv = np.std(np.diff(np.log(seg))) * 1e4
            r, dist = RG.at(d, j)
            rows.append(dict(d=d, date=ts[d], hm=hm, reg=r, dist=dist, past=np.log(c0 / cp) * 1e4,
                             fwd=np.log(cf / c0) * 1e4, rv=rv))
    S = pd.DataFrame(rows); S["absf"] = S.fwd.abs()
    for nm, q in (("all", S), ("design 2023-24", S[S.date < SPLIT]), ("holdout 2025-26", S[S.date >= SPLIT])):
        out = []
        for r in ("above", "below", "weak/none"):
            x = q[q.reg == r]
            if len(x) < 30: continue
            out.append(f"{r}: n={len(x)} |next 30m| {x.absf.mean():.1f} bp, corr(last, next) {np.corrcoef(x.past, x.fwd)[0, 1]:+.3f}")
        print(f"   {nm:<16} " + " | ".join(out))
    S["rvq"] = pd.qcut(S.rv, 5, labels=False)
    print("   same, within realized-vol quintiles (last 60 minutes): |next 30m| bp above / below, corr above / below")
    for k, q in S.groupby("rvq"):
        a, b = q[q.reg == "above"], q[q.reg == "below"]
        if len(a) < 30 or len(b) < 30: continue
        print(f"     rv q{k + 1} ({q.rv.min():.1f}-{q.rv.max():.1f} bp/min): {a.absf.mean():5.1f} / {b.absf.mean():5.1f}"
              f" (ratio {b.absf.mean() / a.absf.mean():.2f}, n {len(a)} / {len(b)}) | corr {np.corrcoef(a.past, a.fwd)[0, 1]:+.3f} / {np.corrcoef(b.past, b.fwd)[0, 1]:+.3f}")
    # day-level: regime at 9:00 CT and the rest of the day's range
    dl = []
    for d in days:
        r, _ = RG.at(d, jof(900))
        hi, lo = np.nanmax(g.h[d, jof(901):jof(1500) + 1]), np.nanmin(g.l[d, jof(901):jof(1500) + 1])
        c0 = last_c(g, d, jof(900)); o = g.o[d, jof(831)]
        fr = (np.nanmax(g.h[d, jof(831):jof(900) + 1]) - np.nanmin(g.l[d, jof(831):jof(900) + 1])) / c0 * 1e4
        dl.append(dict(date=ts[d], reg=r, rng=(hi - lo) / c0 * 1e4, fr=fr))
    DL = pd.DataFrame(dl); DL["frq"] = pd.qcut(DL.fr, 3, labels=["low", "mid", "high"])
    print("   rest-of-day range (9:01-15:00 CT, bp) by regime at 9:00, within first-30-minute range terciles:")
    print("    ", DL.pivot_table(index="frq", columns="reg", values="rng", aggfunc="mean").round(0).to_dict("index"))
    print("     days:", DL.pivot_table(index="frq", columns="reg", values="rng", aggfunc="count").to_dict("index"))

    # ---------------- 2. funded set split by regime at entry ----------------
    print("\n2. MultiCharts trades split by the regime known at entry (2023-03-28 .. 2026-07-07, per NQ, +1 tick slippage):")
    split_rows = {}
    for nm, f in REPORTS.items():
        try: t = with_slippage(load_mc(g, f))
        except Exception as e: print(f"   {nm}: {e}"); continue
        t["net"] = (t.exit - t.entry) * t.side * PV - COST
        t = t[(t.date >= START) & (t.date <= END)].reset_index(drop=True)
        rg = [RG.at(int(r.day), int(r.j0) - 1) for r in t.itertuples()]
        t["reg"] = [x[0] for x in rg]
        print(f"   {nm}: entry times (CT) {pd.Series(t.j0 // 60 * 100 + t.j0 % 60).quantile([0, .5, 1]).astype(int).tolist()}")
        for sd, snm in ((0, "both"), (1, "longs"), (-1, "shorts")):
            q = t if sd == 0 else t[t.side == sd]
            if len(q) < 10: continue
            a, b = q[q.reg == "above"].net, q[q.reg == "below"].net
            print(f"     {snm:<6} all {stat(q.net)}")
            print(f"            above {stat(a)} | below {stat(b)} | weak/none {stat(q[q.reg == 'weak/none'].net)} | diff t {welch(a, b):+.1f}")
            if sd != 0:
                for per, m in (("design", q.date < SPLIT), ("holdout", q.date >= SPLIT)):
                    qq = q[m]
                    print(f"            {per:<7} above ${qq[qq.reg == 'above'].net.mean():5.0f} (n {np.sum(qq.reg == 'above'):3d})"
                          f" below ${qq[qq.reg == 'below'].net.mean():5.0f} (n {np.sum(qq.reg == 'below'):3d})")
        split_rows[nm] = t

    print("\n2b. Same trades split by the PREVIOUS session's regime (read at several times, CT), all trades / both sides:")
    for hm in (1300, 1400, 1430, 1455, 1515):
        print(f"   previous session at {hm}:")
        for nm, t in split_rows.items():
            pv = [RG.at(g.trading[np.searchsorted(g.trading, int(x.day)) - 1], jof(hm))[0] for x in t.itertuples()]
            pv = np.array(pv); a, b = t.net[pv == "above"], t.net[pv == "below"]
            per = " ".join(f"{p_}: ${t.net[(pv == 'above') & m].mean():5.0f} / ${t.net[(pv == 'below') & m].mean():5.0f}"
                           for p_, m in (("23-24", (t.date < SPLIT).to_numpy()), ("25-26", (t.date >= SPLIT).to_numpy())))
            print(f"     {nm:<20} above ${a.mean():5.0f} (n {len(a):3d}) below ${b.mean():5.0f} (n {len(b):3d}) diff t {welch(a, b):+.1f} | {per}")

    # ---------------- 3. stand-alone ideas ----------------
    atr = g.daily_atr(15)
    print("\n3a. First hour (8:30 -> 9:30 CT move), at 9:31 CT follow it or fade it, out 14:55 CT, stop 0.5 ATR:")
    rows = []
    for d in days:
        o, c0 = g.o[d, jof(831)], last_c(g, d, jof(930))
        if np.isnan(o) or np.isnan(c0) or c0 == o or np.isnan(atr[d]): continue
        r, _ = RG.at(d, jof(930)); mv = int(np.sign(c0 - o))
        for mode, side in (("follow", mv), ("fade", -mv)):
            x = trade(g, d, jof(931), side, jof(1455), c0 - side * 0.5 * atr[d])
            if x is not None: rows.append(dict(date=ts[d], reg=r, mode=mode, side=side, net=x))
    F = pd.DataFrame(rows)
    for mode in ("follow", "fade"):
        for r in ("above", "below", "weak/none"):
            q = F[(F["mode"] == mode) & (F.reg == r)]
            print(f"   {mode:<6} {r:<9} {stat(q.net)} | design ${q[q.date < SPLIT].net.mean():5.0f} holdout ${q[q.date >= SPLIT].net.mean():5.0f}")
    rule = pd.concat([F[(F["mode"] == "follow") & (F.reg == "below")], F[(F["mode"] == "fade") & (F.reg == "above")]])
    print(f"   regime rule (follow below, fade above) {stat(rule.net)} | design ${rule[rule.date < SPLIT].net.mean():.0f} holdout ${rule[rule.date >= SPLIT].net.mean():.0f}")

    print("\n3b. Flip cross (steepness > 0.02): first close through the flip 9:00-13:30 CT, trade in the cross direction,"
          " out 14:55 CT, stop 0.3 ATR; placebo = same rule on fake levels (flip +/- 0.5% and +/- 1%):")
    def cross_test(shift, rev=False):
        out = []
        for d in days:
            F_, St = A["flip"][d], A["flip_steep"][d]
            if np.isnan(atr[d]): continue
            prev = None
            for j in range(jof(900), jof(1330) + 1):
                c = g.c[d, j]; f = F_[j]
                if np.isnan(c) or np.isnan(f) or not St[j] > STEEP: prev = None; continue
                lv = f * (1 + shift); s = int(np.sign(c - lv))
                if prev is not None and s != 0 and s != prev:
                    side = -s if rev else s
                    x = trade(g, d, j + 1, side, jof(1455), c - side * 0.3 * atr[d])
                    if x is not None: out.append(dict(date=ts[d], side=side, net=x))
                    break
                if s != 0: prev = s
        return pd.DataFrame(out)
    XC = {}
    for sh in (0.0, -0.01, -0.005, 0.005, 0.01):
        XC[sh] = cross_test(sh)
        q = XC[sh]
        if len(q) < 5: print(f"   level flip{sh:+.1%}: n={len(q)}"); continue
        print(f"   level flip{sh:+.1%}: {stat(q.net)} | L ${q[q.side > 0].net.mean():5.0f} S ${q[q.side < 0].net.mean():5.0f}"
              f" | design ${q[q.date < SPLIT].net.mean():5.0f} holdout ${q[q.date >= SPLIT].net.mean():5.0f}")
    q = cross_test(0.0, rev=True); print(f"   flip, fade the cross instead: {stat(q.net)}")

    print("\n3c. Pin: at 13:30 CT above the flip (steep > 0.02), trade toward the major positive-gamma strike when it is"
          " 0.15-1.0% away, out 14:55 CT, stop 0.3 ATR; placebo = toward the nearest other 100-point NDX strike:")
    pin, plc = [], []
    for d in days:
        j = jof(1330); c = last_c(g, d, j); r, _ = RG.at(d, j)
        mp = A["maj_pos"][d, j]
        if r != "above" or np.isnan(mp) or np.isnan(atr[d]): continue
        dist = (mp - c) / c
        x0 = (last_c(g, d, jof(1455)) - c) / c
        rec = dict(date=ts[d], dist=dist, move=x0)
        if 0.0015 <= abs(dist) <= 0.01:
            side = int(np.sign(dist)); rec["net"] = trade(g, d, j + 1, side, jof(1455), c - side * 0.3 * atr[d]); pin.append(rec)
        # placebo: another 100-point NDX strike (+ basis) 0.15-1% away that is not the major strike
        bs = A["basis"][d, j]
        if np.isnan(bs): continue
        k0 = np.round((c - bs) / 100) * 100
        cand = [k0 + k * 100 + bs for k in range(-3, 4)]
        cand = [x for x in cand if 0.0015 <= abs(x - c) / c <= 0.01 and abs(x - mp) > 50]
        if cand:
            lv = cand[d % len(cand)]
            side = int(np.sign(lv - c)); plc.append(dict(date=ts[d], net=trade(g, d, j + 1, side, jof(1455), c - side * 0.3 * atr[d])))
    P_, Q_ = pd.DataFrame(pin).dropna(), pd.DataFrame(plc).dropna()
    print(f"   toward major +gamma strike: {stat(P_.net)} | design ${P_[P_.date < SPLIT].net.mean():5.0f} holdout ${P_[P_.date >= SPLIT].net.mean():5.0f}")
    print(f"   toward another level (placebo): {stat(Q_.net)}")
    allp = pd.DataFrame([dict(dist=r_["dist"], move=r_["move"]) for r_ in pin])
    if len(allp): print(f"   share of days the 13:30->14:55 move goes toward the strike: {np.mean(np.sign(allp.move) == np.sign(allp.dist)):.0%}")

    # ---------------- metrics for anything that looks real ----------------
    D2 = pd.DatetimeIndex([ts[d] for d in days])
    dly = lambda t: t.groupby(t.date).net.sum().reindex(D2, fill_value=0.0)
    print("\n4. Standard metrics per NQ (2023-03-28 .. 2026-07-07):")
    rows = {"3a regime rule": (dly(rule), rule.net), "3b flip cross": (dly(XC[0.0]), XC[0.0].net),
            "3b flip cross longs": (dly(XC[0.0][XC[0.0].side > 0]), XC[0.0].net[XC[0.0].side > 0]),
            "3b flip cross shorts": (dly(XC[0.0][XC[0.0].side < 0]), XC[0.0].net[XC[0.0].side < 0]),
            "3c pin": (dly(P_), P_.net)}
    print(M.table(rows))
    b, p = R.report({k: v[0] for k, v in rows.items()}, n=2000)
    print(b); print(p)
    pickle.dump(dict(split=split_rows, S=S, F=F, XC=XC, pin=P_), open(SP + "gamma_test.pkl", "wb"))
