"""S-rank program, YM round 1 (2026-10-14): is there a Dow-specific edge? (S_RANK_PROGRAM.md, YM hypotheses 1-4.)

YM: $5 a point, tick 1 point ($5); costs $5 a round trip + 1 tick per market / stop fill (target limits: no slip).
ES ($50, 0.25, $5) and NQ ($20, 0.25, $7.25) only as comparisons. Design 2018-22, holdout 2023-26, every pick by the
2018-22 t only. Daily P&L indexed by every YM session from 2018-01-01 (0 on days without a trade).
  1. Overnight Bias on YM + the NQ ML v2 recipe refit on YM: base ONB (ADX 20 / 0.30 ATR = the ML base, ADX 30 / 0.25
     = the challenge version, plus a 24-cell design-period refit of ADX / stop / reward:risk); ridge filter (R-multiple
     target, 2-98% winsorized, standardized, shrinkage = n) on the NQ input set computed from YM, and the same set plus
     cross-index inputs (YM - ES and YM - NQ relative returns); walk-forward (expanding, retrained each January 2019+)
     and frozen-at-2022 weights for 2023-26; skip days with a negative score. Placebo: random skips at the same rate.
  2. MOC auction follow on YM: sign(14:00 -> 14:50) at the 14:51 open, out at the 15:00 close, |move| >= 0.1 .. 0.5 ATR,
     stop none / 0.25 ATR; placebo: the same rule at other 10-minute windows; the picked rule on ES and NQ.
  3. YM - ES rotation as a YM-only signal: beta-adjusted residual of YM vs ES (60-day rolling beta / sd, known in
     advance), (a) prior day 15:00 -> 15:00 -> trade YM 8:31 -> 15:00 next day, (b) 8:30 -> 10:00 / 11:00 / 12:00 ->
     trade YM to 15:00; revert or continue, k = 1 / 1.5 / 2 sd, stop none / 0.5 ATR. Placebo: the same rule on YM's own
     move (no ES) and random sides.
  4. Forced-flow battery on YM vs ES vs NQ (same rule, $ per contract and gross move in ATR): monthly-expiry 8:30 open
     short (EOS-like), Monday long, month-end / quarter-end last hour (long and follow), Dow component changes
     (descriptive; dates typed in, n tiny), 15:00 -> 15:15 post-settlement reversal. YM-specific only if YM is clearly
     stronger than both.
Anything with |t| >= 2.5 overall and the same sign in 2018-22 and 2023-26 gets full metrics (whole / longs / shorts),
by-year, bootstrap + permutation on 2023+, and correlation with NQ's regular session.
  python3 analysis/s_rank_ym_round1_test.py [SCRATCH_DIR]
"""
import sys, os, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPEC = {"YM": (5.0, 1.0, 5.0), "ES": (50.0, 0.25, 5.0), "NQ": (20.0, 0.25, 7.25)}      # point value, tick, commission
SPLIT = pd.Timestamp("2023-01-01"); START = pd.Timestamp("2018-01-01")
CLOSED_FRI = pd.to_datetime(["2019-04-19", "2022-04-15", "2025-04-18", "2026-06-19"])
SUMMARY = []                                   # (hypothesis, name, trades) for the advance check
pd.set_option("display.width", 230)


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x):
    x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(x, nm, w=60):
    x = pd.Series(x).dropna()
    if len(x) < 8: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); a, b = x[y < 2023], x[y >= 2023]
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.0f} PF {pf(x):4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():5.0f} (t {tstat(a):4.1f}) 23-26 ${b.mean():5.0f} (t {tstat(b):4.1f})")


class Sym:
    """Per-instrument helpers on the YM-style 24-hour grid."""
    def __init__(self, G, sym):
        self.G, self.sym = G, sym; self.pv, self.tick, self.comm = SPEC[sym]
        early = np.array([_early(pd.Timestamp(t)) for t in G.ts])
        tr = G.trading[pd.DatetimeIndex(G.ts[G.trading]) >= START]
        has15 = ~np.isnan(G.c[tr, jof(1500)])
        tr = tr[has15 | (early[tr] & ~np.isnan(G.c[tr, jof(1159)]))]       # regular or half sessions (no holiday rows)
        self.tr = tr; self.idx = pd.DatetimeIndex(G.ts[tr]); self.early = early
        self.full = ~np.isnan(G.c[tr, jof(1500)]) & ~early[tr]
        self.atr_all = G.daily_atr(15); self.atr = self.atr_all[tr]
        self.cf = pd.Series(G.c.ravel()).ffill().to_numpy()

    def P(self, t, rows=None):
        rows = self.tr if rows is None else rows
        return self.cf[rows * 1440 + jof(t)]

    def trades(self, rows, sides, j0s, j1s, stop_pts):
        """Entry at the open of j0 (+/- 1 tick), out at the close of j1 (-/+ 1 tick) or at the stop (gap: worse of open
        and stop, - 1 tick). stop_pts may be inf."""
        G = self.G; O, H, L, C = G.o, G.h, G.l, G.c; tk = self.tick; out = []
        j0s = np.broadcast_to(j0s, len(rows)); j1s = np.broadcast_to(j1s, len(rows)); stop_pts = np.broadcast_to(stop_pts, len(rows))
        for d, s, j0, j1, sp_ in zip(rows, sides, j0s, j1s, stop_pts):
            if s == 0 or np.isnan(O[d, j0]): continue
            e = O[d, j0] + s * tk; px = None
            if np.isfinite(sp_):
                sp = e - s * sp_; seg = L[d, j0:j1 + 1] if s > 0 else H[d, j0:j1 + 1]
                hit = np.where((seg <= sp) if s > 0 else (seg >= sp))[0]
                if len(hit):
                    j = j0 + hit[0]; o = O[d, j]
                    px = (sp if j == j0 else (min(o, sp) if s > 0 else max(o, sp))) - s * tk; jx = j; kind = 0
            if px is None:
                cc = C[d, j0:j1 + 1]; ok = np.where(~np.isnan(cc))[0]
                if not len(ok): continue
                px = cc[ok[-1]] - s * tk; jx = j0 + ok[-1]; kind = 2
            out.append(dict(day=d, j0=j0, j1=jx, side=int(s), entry=e, exit=px, kind=kind, date=pd.Timestamp(G.ts[d]),
                            pts=(px - e) * s, atr=self.atr_all[d], net=(px - e) * s * self.pv - self.comm))
        cols = ["day", "j0", "j1", "side", "entry", "exit", "kind", "date", "pts", "atr", "net"]
        return (pd.DataFrame(out) if out else pd.DataFrame(columns=cols)).set_index("date", drop=False)

    def daily(self, t, days=None):
        days = self.idx if days is None else days
        return t.net.groupby(t.index.normalize()).sum().reindex(days, fill_value=0.0)


def _early(ts):
    from replica import is_early_close
    return is_early_close(ts)


def full_report(label, S, t, placebo_lines=(), nq_rth=None):
    """Full metrics for a candidate that advanced."""
    print(f"\n   ---- full report: {label} ----")
    L, Sh = t[t.side > 0], t[t.side < 0]
    rows = {"whole": (S.daily(t), t.net)}
    if len(L): rows["longs"] = (S.daily(L), L.net)
    if len(Sh): rows["shorts"] = (S.daily(Sh), Sh.net)
    print(M.table(rows))
    for nm, x in (("whole", t), ("longs", L), ("shorts", Sh)):
        if len(x): print(line(x.net, nm))
    print("   by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in t.net.groupby(t.index.year).sum().items()))
    b, p = R.report({f"{label} 2023+": S.daily(t)[S.idx >= SPLIT], **({f"longs 2023+": S.daily(L)[S.idx >= SPLIT]} if len(L) else {}),
                     **({f"shorts 2023+": S.daily(Sh)[S.idx >= SPLIT]} if len(Sh) else {})}, n=3000)
    print(b); print(p)
    for pl in placebo_lines: print(pl)
    if nq_rth is not None:
        d = S.daily(t); j = pd.concat([d, nq_rth], axis=1, join="inner").dropna(); tdd = j.iloc[:, 0] != 0
        print(f"   correlation with NQ 8:30 -> 15:00 (1 NQ $): all days {j.corr().iloc[0, 1]:.2f}, traded days {j[tdd].corr().iloc[0, 1]:.2f}")


# =====================================================================================================================
def onb_ym(S, adx_min, stop_atr, rr):
    """Overnight Bias (candidates24.overnight_bias24 signals) repriced for YM with explicit fills: stop-order entry
    + 1 tick, stop and time exits - 1 tick, target limit at the price; $5 commission."""
    from candidates24 import overnight_bias24
    t = overnight_bias24(S.G, adx_min=adx_min, stop_atr=stop_atr, rr=rr)
    t = t[np.isin(t.day, S.tr)].copy()
    e = t.entry + t.side * S.tick; x = t.exit - np.where(t.kind == 1, 0.0, t.side * S.tick)
    t["entry"], t["exit"] = e, x
    t["net"] = (x - e) * t.side * S.pv - S.comm; t["pts"] = (x - e) * t.side; t["atr"] = S.atr_all[t.day]
    t["R"] = t.net / (stop_atr * t.atr * S.pv); t["date"] = pd.to_datetime(t.date)
    return t.set_index("date", drop=False)


def features(S, ES, NQ):
    """Inputs known at the previous 15:00 CT close (NQ ML v2 set) from YM's own prices, plus cross-index ones."""
    idx = S.idx; cl = pd.Series(S.P(1500), index=idx); op = pd.Series(S.G.o[S.tr, jof(831)], index=idx)
    atr = pd.Series(S.atr, index=idx); r1 = np.log(cl).diff()
    X = pd.DataFrame(index=idx)
    X["ret1"] = r1.shift(1); X["ret5"] = np.log(cl).diff(5).shift(1); X["ret20"] = np.log(cl).diff(20).shift(1)
    X["rth1"] = np.log(cl / op).shift(1); X["atr_ratio"] = atr / atr.rolling(60).mean()
    X["dist50"] = np.log(cl / cl.rolling(50).mean()).shift(1); X["rv5_rv20"] = (r1.rolling(5).std() / r1.rolling(20).std()).shift(1)
    for k in range(5): X[f"dow{k}"] = (idx.dayofweek == k).astype(float)
    mon = pd.Series(idx.to_period("M"), index=idx); tdm = mon.groupby(mon).cumcount() + 1
    X["tdm"] = (tdm <= 3).astype(float)
    fri = idx + pd.to_timedelta(4 - idx.dayofweek, "D"); X["opex_wk"] = ((fri.day >= 15) & (fri.day <= 21)).astype(float)
    base = list(X.columns)
    for O, nm in ((ES, "es"), (NQ, "nq")):
        oc = pd.Series(O.P(1500), index=O.idx).reindex(idx).ffill(); orr = np.log(oc).diff()
        X[f"rel_{nm}1"] = (r1 - orr).shift(1); X[f"rel_{nm}5"] = (np.log(cl).diff(5) - np.log(oc).diff(5)).shift(1)
    X = X.fillna(X.median())
    return X, base, list(X.columns)


def ridge_fit(X, y, trn):
    mu, sd = X[trn].mean(), X[trn].std().replace(0, 1)
    A = ((X[trn] - mu) / sd).to_numpy(); b = y[trn].to_numpy(); lo, hi = np.percentile(b, [2, 98]); b = np.clip(b, lo, hi); b = b - b.mean()
    w = np.linalg.solve(A.T @ A + len(b) * np.eye(A.shape[1]), A.T @ b)
    return lambda Z: ((Z - mu) / sd).to_numpy() @ w, pd.Series(w, index=X.columns)


def h1(S, ES, NQ, nq_rth):
    print("\n" + "=" * 118 + "\n1. Overnight Bias on YM + ML (ridge) filter refit on YM")
    bases = {}
    for a, s, r in ((20, 0.30, 3.0), (30, 0.25, 3.0)):
        bases[(a, s, r)] = t = onb_ym(S, a, s, r)
        print(line(t.net, f"ONB ADX {a} / stop {s} ATR / {r:.0f}R"))
    print("   design-period refit, 24 cells (ADX 20/25/30 x stop 0.20/0.25/0.30/0.40 ATR x 2R/3R):")
    grid = {}
    for a, s, r in itertools.product((20, 25, 30), (0.20, 0.25, 0.30, 0.40), (2.0, 3.0)):
        grid[(a, s, r)] = t = bases.get((a, s, r)) if (a, s, r) in bases else onb_ym(S, a, s, r)
    sc = {k: tstat(v.net[v.index < SPLIT]) for k, v in grid.items()}
    for k in sorted(sc, key=sc.get, reverse=True)[:6]: print(line(grid[k].net, f"  ADX {k[0]} stop {k[1]} {k[2]:.0f}R (design t {sc[k]:.1f})"))
    print(f"   cells with design t > 0: {sum(v > 0 for v in sc.values())}/24; median design t {np.median(list(sc.values())):.2f}")
    kbest = max(sc, key=sc.get); bases[kbest] = grid[kbest]
    X, base_cols, all_cols = features(S, ES, NQ)
    yr = X.index.year; rng = np.random.default_rng(7); res = {}
    print("\n   ML filter (skip score < 0). WF = walk-forward 2019-26 (expanding, retrained each January); FZ = frozen at 2022, 2023-26")
    for bk, t in bases.items():
        tt = t.groupby(t.index.normalize()).first()          # one ONB trade a day
        Rm = tt.R.reindex(X.index); tdd = Rm.notna(); net = tt.net.reindex(X.index)
        for setnm, cols in (("NQ input set", base_cols), ("+ cross-index (YM-ES, YM-NQ)", all_cols)):
            Xs = X[cols]; wf = pd.Series(np.nan, index=X.index)
            for Y in range(2019, 2027):
                trn = tdd & (yr < Y); tst = tdd & (yr == Y)
                if tst.sum() == 0: continue
                f, _ = ridge_fit(Xs, Rm, trn); wf[tst] = f(Xs[tst])
            f22, w22 = ridge_fit(Xs, Rm, tdd & (yr < 2023)); fz = pd.Series(np.nan, index=X.index); m23 = tdd & (yr >= 2023); fz[m23] = f22(Xs[m23])
            m = tdd & (yr >= 2019); keep = wf[m] >= 0; y_ = net[m]
            byk = y_[keep].groupby(y_[keep].index.year).mean(); bys = y_[~keep].groupby(y_[~keep].index.year).mean()
            # placebo: random skips with the same per-year rate
            share = (~keep).groupby(keep.index.year).mean(); pl = []
            for _ in range(2000):
                u = rng.random(len(y_)); thr = share.reindex(y_.index.year).to_numpy(); pl.append(y_[u >= thr].mean())
            pct = np.mean(np.array(pl) < y_[keep].mean())
            kz = fz[m23] >= 0
            print(f"   base ADX {bk[0]} / {bk[1]} / {bk[2]:.0f}R, {setnm:<30}: WF skip {(~keep).mean():.0%}, kept ${y_[keep].mean():.0f} vs skipped ${y_[~keep].mean():.0f},"
                  f" years kept > skipped {(byk > bys.reindex(byk.index)).sum()}/{len(byk)}, vs random skips pct {pct:.0%};"
                  f" FZ 2023-26 kept ${net[m23][kz].mean():.0f} (n {kz.sum()}) vs skipped ${net[m23][~kz].mean():.0f}")
            kept_days = y_[keep].index
            tk = t[t.index.normalize().isin(kept_days)]
            res[(bk, setnm)] = dict(t=tk, wf=wf, fz=fz, w22=w22)
            print(line(tk.net, f"     kept trades (WF), 2019-26"))
            tz = t[t.index.normalize().isin(net[m23][kz].index)]
            print(line(tz.net, f"     kept trades 2023-26 with frozen-2022 weights"))
    k0 = ((20, 0.30, 3.0), "NQ input set")
    print("   frozen-2022 weights (standardized), NQ recipe on YM base ADX 20:", res[k0]["w22"].round(3).to_dict())
    for (bk, setnm), v in res.items():
        SUMMARY.append(("1 ONB ML", f"ADX {bk[0]}/{bk[1]}/{bk[2]:.0f}R, {setnm}, WF kept", v["t"]))
    for bk, t in bases.items(): SUMMARY.append(("1 ONB", f"base ADX {bk[0]}/{bk[1]}/{bk[2]:.0f}R", t))
    return res, bases


# =====================================================================================================================
def moc_rule(S, th, st, dec=1450, win=10, look=50):
    jd = jof(dec); rows = S.tr
    mv = S.cf[rows * 1440 + jd] - S.cf[rows * 1440 + jd - look]
    m = S.full & (np.abs(mv) >= th * S.atr) & (mv != 0) & ~np.isnan(S.atr)
    return S.trades(rows[m], np.sign(mv[m]).astype(int), jd + 1, jd + win, (st * S.atr[m]) if st else np.full(m.sum(), np.inf))


def h2(S, ES, NQ):
    print("\n" + "=" * 118 + "\n2. MOC auction follow on YM: sign(14:00 -> 14:50) at the 14:51 open, out at the 15:00 close")
    res = {}
    for th, st in itertools.product((0.1, 0.2, 0.3, 0.4, 0.5), (None, 0.25)):
        res[(th, st)] = t = moc_rule(S, th, st)
        print(line(t.net, f"|14:00->14:50| >= {th} ATR, stop {st if st else 'none'}"))
    sc = {k: tstat(v.net[v.index < SPLIT]) for k, v in res.items()}; k = max(sc, key=sc.get); t = res[k]
    print(f"   pick by 2018-22 t: {k} (t {sc[k]:.1f})")
    print(line(t.net[t.side > 0], "  longs")); print(line(t.net[t.side < 0], "  shorts"))
    print("   gross move in ATR, YM / ES / NQ, same rule (MOC follow is a cash-close flow, so it should show on all three):")
    for O in (S, ES, NQ):
        tt = moc_rule(O, *k); g = tt.pts / tt.atr
        print(line(tt.net, f"  {O.sym}: $ per contract") + f" | gross {g.mean():+.4f} ATR (t {tstat(g):.1f})")
    print("   placebo: the same rule at other times (50-minute move, then the next 10 minutes), YM:")
    for dec in (1050, 1150, 1250, 1320, 1350, 1420, 1450):
        print(line(moc_rule(S, k[0], k[1], dec).net, f"  decide {dec}"))
    for kk, v in res.items(): SUMMARY.append(("2 MOC", f"th {kk[0]} stop {kk[1]}", v))
    return res, k


# =====================================================================================================================
def h3(S, ES, nq_rth):
    print("\n" + "=" * 118 + "\n3. YM - ES rotation (beta-adjusted residual), trade YM only")
    idx = S.idx; esS = lambda t: pd.Series(ES.P(t), index=ES.idx).reindex(idx)
    ym = lambda t: pd.Series(S.P(t), index=idx)
    out = {}
    # (a) prior day residual 15:00 -> 15:00
    ry = np.log(ym(1500)).diff(); re = np.log(esS(1500)).diff()
    ok = ry.notna() & re.notna() & S.full
    cov = (ry * re).rolling(60, min_periods=40).mean() - ry.rolling(60, min_periods=40).mean() * re.rolling(60, min_periods=40).mean()
    beta = (cov / re.rolling(60, min_periods=40).var()).shift(1)
    resid = ry - beta * re; z = resid / resid.rolling(60, min_periods=40).std().shift(1)
    zprev = z.shift(1); zown = (ry / ry.rolling(60, min_periods=40).std().shift(1)).shift(1)
    print(f"   rolling beta YM on ES: median {beta.median():.2f}; residual sd median {resid.rolling(60).std().median() * 1e4:.0f} bp")
    print("   (a) prior-day residual z -> YM 8:31 open to 15:00 close next day")
    for k, mode, st in itertools.product((1.0, 1.5, 2.0), ("revert", "continue"), (None, 0.5)):
        zz = zprev.to_numpy(); m = S.full & (np.abs(zz) >= k) & ~np.isnan(S.atr)
        sd = np.sign(zz[m]) * (-1 if mode == "revert" else 1)
        out[("prior day", k, mode, st)] = t = S.trades(S.tr[m], sd.astype(int), jof(831), jof(1500), (st * S.atr[m]) if st else np.full(m.sum(), np.inf))
        print(line(t.net, f"  |z| >= {k}, {mode}, stop {st if st else 'none'}"))
    # (b) morning residual 8:30 -> decision time
    print("   (b) morning residual (8:31 open -> decision), z vs its own 60-day sd -> YM from the next bar to 15:00")
    o_y = pd.Series(S.G.o[S.tr, jof(831)], index=idx); o_e = pd.Series(ES.G.o[ES.tr, jof(831)], index=ES.idx).reindex(idx)
    zm = {}
    for dec in (1000, 1100, 1200):
        a = np.log(ym(dec) / o_y); b = np.log(esS(dec) / o_e)
        cv = (a * b).rolling(60, min_periods=40).mean() - a.rolling(60, min_periods=40).mean() * b.rolling(60, min_periods=40).mean()
        bt = (cv / b.rolling(60, min_periods=40).var()).shift(1); rs = a - bt * b
        zm[dec] = (rs / rs.rolling(60, min_periods=40).std().shift(1), a / a.rolling(60, min_periods=40).std().shift(1))
        for k, mode, st in itertools.product((1.0, 1.5, 2.0), ("revert", "continue"), (None, 0.5)):
            zz = zm[dec][0].to_numpy(); m = S.full & (np.abs(zz) >= k) & ~np.isnan(S.atr)
            sd = np.sign(zz[m]) * (-1 if mode == "revert" else 1)
            out[(dec, k, mode, st)] = t = S.trades(S.tr[m], sd.astype(int), jof(dec) + 1, jof(1500), (st * S.atr[m]) if st else np.full(m.sum(), np.inf))
            print(line(t.net, f"  decide {dec}, |z| >= {k}, {mode}, stop {st if st else 'none'}"))
    sc = {k: tstat(v.net[v.index < SPLIT]) for k, v in out.items() if len(v) > 30}; kb = max(sc, key=sc.get); t = out[kb]
    print(f"   pick by 2018-22 t (of {len(sc)} cells): {kb} (t {sc[kb]:.1f})")
    print(line(t.net[t.side > 0], "  longs")); print(line(t.net[t.side < 0], "  shorts"))
    # placebo 1: same rule with YM's own move instead of the residual; placebo 2: random sides on the same days
    zsrc = zown if kb[0] == "prior day" else zm[kb[0]][1]
    zz = zsrc.to_numpy(); m = S.full & (np.abs(zz) >= kb[1]) & ~np.isnan(S.atr); sd = np.sign(zz[m]) * (-1 if kb[2] == "revert" else 1)
    j0 = jof(831) if kb[0] == "prior day" else jof(kb[0]) + 1
    tp = S.trades(S.tr[m], sd.astype(int), j0, jof(1500), (kb[3] * S.atr[m]) if kb[3] else np.full(m.sum(), np.inf))
    print(line(tp.net, "  placebo: same rule on YM's own move (no ES)"))
    rng = np.random.default_rng(3); rr = []
    rows = t.day.to_numpy()
    for _ in range(200):
        sdr = rng.choice([-1, 1], len(rows)); st = (kb[3] * S.atr_all[rows]) if kb[3] else np.full(len(rows), np.inf)
        rr.append(S.trades(rows, sdr, j0, jof(1500), st).net.mean())
    print(f"   placebo: random sides on the same days (200 draws): mean ${np.mean(rr):.0f}, 95th pct ${np.percentile(rr, 95):.0f}; picked ${t.net.mean():.0f}")
    for kk, v in out.items(): SUMMARY.append(("3 YM-ES", str(kk), v))
    return out, kb


# =====================================================================================================================
def battery(O):
    """Same forced-flow rules on any instrument -> {name: trades}."""
    idx, tr, full, atr = O.idx, O.tr, O.full, O.atr; out = {}
    ok = ~np.isnan(atr)
    thu = (idx.dayofweek == 3) & np.isin((idx + pd.Timedelta(days=1)).normalize(), CLOSED_FRI)
    exp = (((idx.dayofweek == 4) & (idx.day >= 15) & (idx.day <= 21) & ~np.isin(idx.normalize(), CLOSED_FRI)) | thu) & ok
    out["Expiry 8:30 open short (8:31 -> 10:00, stop 0.3 ATR)"] = O.trades(tr[exp], -np.ones(exp.sum(), int), jof(831), jof(1000), 0.3 * atr[exp])
    q = exp & np.isin(idx.month, (3, 6, 9, 12))
    out["  quarterly expiries only"] = O.trades(tr[q], -np.ones(q.sum(), int), jof(831), jof(1000), 0.3 * atr[q])
    mon = (idx.dayofweek == 0) & ok
    out["Monday long (8:31 -> 15:00, stop 0.5 ATR)"] = O.trades(tr[mon], np.ones(mon.sum(), int), jof(831), jof(1500), 0.5 * atr[mon])
    me = np.r_[idx.month[1:] != idx.month[:-1], False] & full & ok        # last session of each month
    qe = me & np.isin(idx.month, (3, 6, 9, 12))
    mv = O.P(1400) - O.G.o[tr, jof(831)]
    for nm, m in (("Month-end", me), ("Quarter-end", qe)):
        out[f"{nm} last hour long (14:01 -> 15:00)"] = O.trades(tr[m], np.ones(m.sum(), int), jof(1401), jof(1500), np.full(m.sum(), np.inf))
        mm = m & (mv != 0)
        out[f"{nm} last hour follow 8:30->14:00 (14:01 -> 15:00)"] = O.trades(tr[mm], np.sign(mv[mm]).astype(int), jof(1401), jof(1500), np.full(mm.sum(), np.inf))
    # post-settlement reversal 15:01 -> 15:15
    for look, nm in ((jof(1400), "14:00->15:00"), (jof(1450), "14:50->15:00"), (jof(831), "8:31->15:00")):
        mvp = O.P(1500) - (O.G.o[tr, jof(831)] if look == jof(831) else O.cf[tr * 1440 + look])
        th = 0.2 if look != jof(1450) else 0.05
        m = full & ok & (np.abs(mvp) >= th * atr) & (mvp != 0)
        out[f"Post-settlement fade of {nm} (|move| >= {th} ATR), 15:01 -> 15:15"] = O.trades(tr[m], -np.sign(mvp[m]).astype(int), jof(1501), jof(1515), np.full(m.sum(), np.inf))
    return out


DOW_CHANGES = pd.to_datetime(["2018-06-26", "2019-04-02", "2020-04-06", "2020-08-31", "2024-02-26", "2024-11-08"])


def h4(SY, ES, NQ):
    print("\n" + "=" * 118 + "\n4. Forced-flow battery, YM vs ES vs NQ (same rules; $ per contract; gross move in ATR units)")
    B = {O.sym: battery(O) for O in (SY, ES, NQ)}
    verdict = {}
    for nm in B["YM"]:
        print(f"   {nm}")
        g = {}
        for s in ("YM", "ES", "NQ"):
            t = B[s][nm]; x = t.pts / t.atr; g[s] = (tstat(x), x.mean())
            print(line(t.net, f"  {s}", 6) + f" | gross {x.mean():+.4f} ATR (t {tstat(x):4.1f})")
        ty = g["YM"][0]; verdict[nm] = ty >= 2.5 and g["YM"][1] > 1.5 * max(g["ES"][1], g["NQ"][1], 0) or (ty <= -2.5 and g["YM"][1] < 1.5 * min(g["ES"][1], g["NQ"][1], 0))
        SUMMARY.append(("4 battery", nm, B["YM"][nm]))
    print("   YM-specific (YM |t| >= 2.5 and its ATR-scaled move > 1.5x both ES and NQ):", [k for k, v in verdict.items() if v] or "none")
    # Dow component changes (descriptive): effective-day YM - ES regular-session move, and the day after
    print("   Dow component changes (effective dates typed in, list may be incomplete; n = 6 -> descriptive only):")
    ym8 = pd.Series((SY.P(1500) - SY.G.o[SY.tr, jof(831)]) / SY.atr, index=SY.idx)
    es8 = pd.Series((ES.P(1500) - ES.G.o[ES.tr, jof(831)]) / ES.atr, index=ES.idx)
    for d in DOW_CHANGES:
        i = SY.idx.searchsorted(d)
        if i + 1 >= len(SY.idx): continue
        a, b = SY.idx[i], SY.idx[i + 1]
        print(f"     {d.date()}: effective day YM {ym8.get(a, np.nan):+.2f} ATR vs ES {es8.get(a, np.nan):+.2f}; next day YM {ym8.get(b, np.nan):+.2f} vs ES {es8.get(b, np.nan):+.2f}")
    return B


def h4b(SY, ES, NQ):
    """Post-settlement fade (the only battery rule where YM stands apart): sensitivity and placebos."""
    print("\n   4b. Post-settlement fade of 14:00 -> 15:00 on YM: sensitivity and placebos")
    def fade(O, dec, th, x1, look=60):
        jd = jof(dec); mv = O.cf[O.tr * 1440 + jd] - O.cf[O.tr * 1440 + jd - look]
        m = O.full & ~np.isnan(O.atr) & (np.abs(mv) >= th * O.atr) & (mv != 0)
        return O.trades(O.tr[m], -np.sign(mv[m]).astype(int), jd + 1, jof(x1), np.full(m.sum(), np.inf))
    for th in (0.1, 0.2, 0.3, 0.4):
        for x1 in (1505, 1510, 1515, 1530):
            print(line(fade(SY, 1500, th, x1).net, f"  |14:00->15:00| >= {th} ATR, out {x1}"))
    t0 = fade(SY, 1500, 0.2, 1515)
    print(line(t0.net - 5.0 * 2, "  picked rule with 2 ticks per fill instead of 1"))
    print("   placebo, other times (fade the prior 60-minute move >= 0.2 ATR, hold 14 minutes):")
    for dec in (1000, 1100, 1200, 1300, 1400, 1430):
        print(line(fade(SY, dec, 0.2, (dec // 100) * 100 + (dec % 100) + 15 if dec % 100 < 45 else dec + 55).net, f"  decide {dec}"))
    rng = np.random.default_rng(5); rows = t0.day.to_numpy(); rr = []
    for _ in range(300):
        rr.append(SY.trades(rows, rng.choice([-1, 1], len(rows)), jof(1501), jof(1515), np.full(len(rows), np.inf)).net.mean())
    print(f"   placebo: random sides on the same days (300 draws): mean ${np.mean(rr):.0f}, 95th pct ${np.percentile(rr, 95):.0f}; rule ${t0.net.mean():.0f}")
    yrs = t0.index.year
    print(f"   regime: 2018-20 ${t0.net[yrs <= 2020].mean():.0f} (n {np.sum(yrs <= 2020)}), 2021-26 ${t0.net[yrs >= 2021].mean():.0f} (n {np.sum(yrs >= 2021)})")
    return t0


# =====================================================================================================================
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    SY = Sym(pickle.load(open(SP + "gy.pkl", "rb")), "YM")
    ES = Sym(pickle.load(open(SP + "ge.pkl", "rb")), "ES")
    NQ = Sym(pickle.load(open(SP + "g24.pkl", "rb")), "NQ")
    print(f"YM sessions {SY.idx[0].date()} .. {SY.idx[-1].date()}: {len(SY.idx)} ({SY.full.sum()} full); median ATR(15) {np.nanmedian(SY.atr):.0f} pts = ${np.nanmedian(SY.atr) * 5:,.0f}")
    nq_rth = pd.Series((NQ.P(1500) - NQ.G.o[NQ.tr, jof(831)]) * 20, index=NQ.idx)
    r1, bases = h1(SY, ES, NQ, nq_rth)
    r2, k2 = h2(SY, ES, NQ)
    r3, k3 = h3(SY, ES, nq_rth)
    B = h4(SY, ES, NQ)
    t4b = h4b(SY, ES, NQ)

    print("\n" + "=" * 118 + "\n5. Advance check (|t| >= 2.5 overall and the same sign in 2018-22 and 2023-26), all YM variants tested")
    adv = []; n_tested = 0
    for hyp, nm, t in SUMMARY:
        if len(t) < 20: continue
        n_tested += 1; x = t.net; a, b = x[x.index < SPLIT], x[x.index >= SPLIT]; tt = tstat(x)
        if abs(tt) >= 2.5 and np.sign(a.mean()) == np.sign(b.mean()) == np.sign(tt): adv.append((hyp, nm, t, tt))
    print(f"   {n_tested} YM variants tested; advancing: {len(adv)}")
    best_abs = sorted(SUMMARY, key=lambda r: -abs(tstat(r[2].net)) if len(r[2]) >= 20 else 0)[:8]
    print("   largest |t| among all YM variants (for reference):")
    for hyp, nm, t in best_abs: print(line(t.net, f"  [{hyp}] {nm}"[:60]))
    for hyp, nm, t, tt in adv:
        full_report(f"[{hyp}] {nm}", SY, t, nq_rth=nq_rth)
    pickle.dump(dict(summary=[(h, n, t) for h, n, t in SUMMARY], k2=k2, k3=k3), open(SP + "s_rank_ym.pkl", "wb"))
