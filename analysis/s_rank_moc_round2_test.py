"""S-rank program, round 2 item 1 (2026-10-14): the closing-auction (MOC) follow on NQ + ES + YM, pooled.

Round 1 rule (per index): after a >= 0.3 ATR 14:00 -> 14:50 CT move, enter at the 14:51 bar open (the bar that opens at
14:50:00, when the NYSE / Nasdaq closing-imbalance messages start) in that direction, out at the 15:00 close (the cash
close), stop 0.25 x 15-day ATR. Engine as in moc_london_close_test.py / s_rank_*_round1_test.py (entry at a bar open +/-
1 tick, stop at the stop (gap: worse of open and stop) - 1 tick, time exit at a bar close - 1 tick), vectorized here.
Costs per contract: NQ $7.25, ES $5, YM $5 + 1 tick per market / stop fill. Sessions 2018-01 .. 2026-10, full sessions
only (early-close days excluded). Grids: scratch_data/g24.pkl (NQ), ge.pkl (ES), gy.pkl (YM).

Pooled stream: each leg sized to 1 NQ-equivalent ATR risk (leg contracts = NQ ATR$ / leg ATR$, same day), summed per
day ("NQ-eq $"). The honest t for the pool is the t of the DAILY pooled P&L (the legs are ~0.9 correlated on 10 minutes).
Selection: every variant is scored by the 2018-22 t of the pooled daily stream only; 2023-26 is never used to pick. Only
variants with the 0.25 ATR stop are selectable (Apex needs a bounded loss per trade; no-stop variants listed for reference);
entry / exit timing (section 4) is then picked the same way on the selected signal.

1. Agreement: own-index signal vs (a) own signal + all three 14:00 -> 14:50 signs agree, (b) all three |move| >= th and
   the same sign, (c) disagreement days (control); legs and pool.
2. Signal strength: the cross-index average move in ATR units (composite, one threshold, all three legs trade its sign);
   the 14:30 -> 14:50 (last 20 minutes) vs 14:00 -> 14:30 split; the whole session 8:31 open -> 14:50 (the leveraged-ETF
   rebalancing hypothesis: LETF MOC orders scale with the day's move).
3. Day types (pre-registered, descriptive, 4 splits = 8 cells): month-end (last session of the month), Fridays,
   monthly options expiry (3rd Friday), prior-day VIX close above / below its trailing 252-day median.
4. Entry / exit timing on the pick: entry 14:51 / 14:52 / 14:53 open (decision still at 14:50, and decision at entry - 1),
   exit 15:00 close vs 14:59 close.
Best version: full metrics (Sharpe, Sortino, PF, Calmar, Ulcer) pool / longs / shorts and per index, by year, bootstrap +
permutation on 2023+ (resampling.R.report), placebos (other decision times, random sides on the same days), correlation
with the NQ funded plan's daily P&L (time_clusters_test.trades).
  python3 analysis/s_rank_moc_round2_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R
from s_rank_ym_round1_test import Sym, tstat, pf

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPLIT = pd.Timestamp("2023-01-01")
SYMS = ("NQ", "ES", "YM")
NVAR = {}                                   # family -> variants tried
pd.set_option("display.width", 230)


# ------------------------------------------------------------------ engine (vectorized; same fills as round 1)
def sim(S, sig, j0, j1, stop_atr):
    """sig: signed signal on S.idx (NaN / 0 = no trade); trade sign(sig) at the j0 open, out at the j1 close or the stop."""
    G = S.G; tk = S.tick
    s = np.sign(np.nan_to_num(np.asarray(sig, float)))
    m = S.full & (s != 0) & ~np.isnan(S.atr)
    rows = S.tr[m]; s = s[m]; atr = S.atr[m]
    O0 = G.o[rows, j0]; ok = ~np.isnan(O0); rows, s, atr, O0 = rows[ok], s[ok], atr[ok], O0[ok]
    e = O0 + s * tk
    spx = e - s * (stop_atr * atr if stop_atr else np.inf)
    W = slice(j0, j1 + 1)
    Lw, Hw, Ow, Cw = G.l[rows, W], G.h[rows, W], G.o[rows, W], G.c[rows, W]
    with np.errstate(invalid="ignore"):
        hit = np.where(s[:, None] > 0, Lw <= spx[:, None], Hw >= spx[:, None])
    anyh = hit.any(1); first = hit.argmax(1); r = np.arange(len(rows))
    of = Ow[r, first]; of = np.where(np.isnan(of), spx, of)
    pxs = np.where(first == 0, spx, np.where(s > 0, np.minimum(of, spx), np.maximum(of, spx))) - s * tk
    hc = ~np.isnan(Cw); lastk = Cw.shape[1] - 1 - hc[:, ::-1].argmax(1)
    pxc = Cw[r, lastk] - s * tk
    px = np.where(anyh, pxs, pxc); keep = anyh | hc.any(1)
    d = pd.DatetimeIndex(G.ts[rows])
    t = pd.DataFrame(dict(day=rows, side=s.astype(int), entry=e, exit=px, kind=np.where(anyh, 0, 2), atr=atr,
                          pts=(px - e) * s, net=(px - e) * s * S.pv - S.comm), index=d)[keep]
    return t


# ------------------------------------------------------------------ reporting helpers
def line(x, nm, w=58):
    x = pd.Series(x).dropna(); x = x[x != 0] if nm.startswith("POOL") else x
    if len(x) < 8: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; by = x.groupby(y).sum(); a, b = x[y < 2023], x[y >= 2023]
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():5.0f} PF {pf(x):4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} "
            f"yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${a.mean():5.0f} (t {tstat(a):4.1f}) 23-26 ${b.mean():5.0f} (t {tstat(b):4.1f})")


def byyear(x):
    return "   by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in pd.Series(x).groupby(pd.Series(x).index.year).sum().items())


class World:
    def __init__(self):
        files = {"NQ": "g24.pkl", "ES": "ge.pkl", "YM": "gy.pkl"}
        self.S = {k: Sym(pickle.load(open(SP + f, "rb")), k) for k, f in files.items()}
        self.days = self.S["NQ"].idx.union(self.S["ES"].idx).union(self.S["YM"].idx)
        nq = self.S["NQ"]; self.nq_atr_usd = pd.Series(nq.atr * nq.pv, index=nq.idx).reindex(self.days).ffill()
        F = {}
        for k, S in self.S.items():
            a = S.atr; o831 = S.G.o[S.tr, jof(831)]
            F[k] = pd.DataFrame({"m": (S.P(1450) - S.P(1400)) / a, "ma": (S.P(1430) - S.P(1400)) / a,
                                 "mb": (S.P(1450) - S.P(1430)) / a, "ms": (S.P(1450) - o831) / a,
                                 "full": S.full}, index=S.idx)
        self.F = F
        self.both = F["NQ"].index.intersection(F["ES"].index).intersection(F["YM"].index)
        X = lambda c: pd.DataFrame({k: F[k][c].reindex(self.days).where(F[k]["full"].reindex(self.days).fillna(False).astype(bool)) for k in SYMS})
        self.X = {c: X(c) for c in ("m", "ma", "mb", "ms")}

    def own(self, k, ser):                      # date-indexed series -> array on S.idx
        return ser.reindex(self.S[k].idx).to_numpy(float)

    def legs(self, sigs, j0=jof(1451), j1=jof(1500), stop=0.25):
        """sigs: {sym: date-indexed signal} -> {sym: trades} with NQ-eq weight column."""
        out = {}
        for k, sg in sigs.items():
            S = self.S[k]; t = sim(S, self.own(k, sg), j0, j1, stop)
            t["w"] = self.nq_atr_usd.reindex(t.index).to_numpy() / (t.atr * S.pv); t["nqeq"] = t.net * t.w
            out[k] = t
        return out

    def pool(self, L):
        return sum(t.nqeq.groupby(t.index).sum().reindex(self.days, fill_value=0.0) for t in L.values())


def report(W, L, nm, legs=True):
    P = W.pool(L); s = [line(P, f"POOL {nm}"[:58])]
    if legs:
        for k, t in L.items(): s.append(line(t.net, f"   {k} $/contract"))
    return P, s


def tpool18(P):
    x = P[(P != 0) & (P.index < SPLIT)]; return tstat(x)


# ======================================================================================================================
if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    W = World(); X = W.X; sgn = np.sign
    print(f"sessions: NQ {len(W.S['NQ'].idx)}, ES {len(W.S['ES'].idx)}, YM {len(W.S['YM'].idx)}; all three {len(W.both)}")
    c = X["m"]; print("correlation of the 14:00 -> 14:50 moves (ATR units):\n" + c.corr().round(3).to_string())
    r10 = pd.DataFrame({k: pd.Series((W.S[k].P(1500) - W.S[k].P(1450)) / W.S[k].atr, index=W.S[k].idx) for k in SYMS})
    print("correlation of the 14:50 -> 15:00 moves:\n" + r10.corr().round(3).to_string())
    VAR = {}                                                         # name -> (legs, pooled daily, family)

    def add(fam, nm, sigs, **kw):
        L = W.legs(sigs, **kw); P, s = report(W, L, nm); VAR[nm] = (L, P, fam); NVAR[fam] = NVAR.get(fam, 0) + 1
        print("\n".join(s)); return L, P

    # ------------------------------------------------------------------ 0. baseline (round 1 rule) per index
    print("\n" + "=" * 118 + "\n0. Round-1 rule per index: own |14:00->14:50| >= th ATR, 14:51 open -> 15:00 close, stop 0.25 ATR")
    for th, st in itertools.product((0.2, 0.3, 0.4), (None, 0.25)):
        add("0 own", f"own >= {th} stop {st}", {k: c[k].where(c[k].abs() >= th) for k in SYMS}, stop=st)

    # ------------------------------------------------------------------ 1. agreement
    print("\n" + "=" * 118 + "\n1. Agreement across NQ / ES / YM (14:00 -> 14:50 signs)")
    agree = (sgn(c).nunique(axis=1) == 1) & c.notna().all(1) & (c != 0).all(1)
    print(f"   all-three sessions with an agreeing sign: {agree.sum()} of {c.notna().all(1).sum()} ({agree.mean():.0%} of days)")
    for th, st in itertools.product((0.2, 0.3, 0.4), (None, 0.25)):
        add("1 agree", f"own >= {th} & signs agree, stop {st}", {k: c[k].where((c[k].abs() >= th) & agree) for k in SYMS}, stop=st)
    for th, st in itertools.product((0.2, 0.3, 0.4), (None, 0.25)):
        allx = (c.abs() >= th).all(1) & agree
        add("1 agree", f"all three >= {th} same sign, stop {st}", {k: c[k].where(allx) for k in SYMS}, stop=st)
    print("   control (not selectable): own >= 0.3 but signs disagree, stop 0.25")
    Ld = W.legs({k: c[k].where((c[k].abs() >= 0.3) & ~agree & c.notna().all(1)) for k in SYMS})
    print("\n".join(report(W, Ld, "disagree (control)")[1]))
    # within-leg: the leg's own signal on disagreement days (is the leg that disagrees right or wrong?)
    for k in SYMS:
        oth = [o for o in SYMS if o != k]; other_mean = c[oth].mean(1)
        m_dis = (c[k].abs() >= 0.3) & c.notna().all(1) & (sgn(c[k]) != sgn(other_mean))
        tt = sim(W.S[k], W.own(k, c[k].where(m_dis)), jof(1451), jof(1500), 0.25)
        tf = sim(W.S[k], W.own(k, (-c[k]).where(m_dis)), jof(1451), jof(1500), 0.25)
        print(line(tt.net, f"   {k} own >= 0.3 against the other two: follow own") + "\n" + line(tf.net, f"   {k}   ... follow the other two instead"))

    # ------------------------------------------------------------------ 2. signal strength
    print("\n" + "=" * 118 + "\n2a. Composite = mean of the three 14:00 -> 14:50 moves in ATR; all legs trade its sign")
    comp = c.mean(1).where(c.notna().all(1))
    for th, st in itertools.product((0.1, 0.2, 0.3, 0.4, 0.5), (None, 0.25)):
        add("2 composite", f"composite >= {th}, stop {st}", {k: comp.where(comp.abs() >= th) for k in SYMS}, stop=st)
    print("\n2b. Which part of the hour: 14:30 -> 14:50 (last 20 min) vs 14:00 -> 14:30, composite, stop 0.25")
    mb, ma = X["mb"].mean(1).where(X["mb"].notna().all(1)), X["ma"].mean(1).where(X["ma"].notna().all(1))
    for th in (0.1, 0.15, 0.2, 0.3):
        add("2 split", f"composite 14:30->14:50 >= {th}", {k: mb.where(mb.abs() >= th) for k in SYMS})
    for th in (0.1, 0.2, 0.3):
        add("2 split", f"composite 14:00->14:30 >= {th}", {k: ma.where(ma.abs() >= th) for k in SYMS})
    for th in (0.2, 0.3):
        add("2 split", f"composite >= {th} & last 20 min same sign", {k: comp.where((comp.abs() >= th) & (sgn(mb) == sgn(comp))) for k in SYMS})
        add("2 split", f"composite >= {th} & last 20 min opposite", {k: comp.where((comp.abs() >= th) & (sgn(mb) == -sgn(comp))) for k in SYMS})
    print("\n2c. Whole-session move (8:31 open -> 14:50, the leveraged-ETF rebalancing hypothesis), composite, stop 0.25")
    ms = X["ms"].mean(1).where(X["ms"].notna().all(1))
    for th in (0.25, 0.5, 0.75, 1.0):
        add("2 session", f"composite 8:31->14:50 >= {th}", {k: ms.where(ms.abs() >= th) for k in SYMS})
    for th in (0.5, 1.0):
        add("2 session", f"composite >= 0.3 & session move >= {th} same sign", {k: comp.where((comp.abs() >= 0.3) & (ms.abs() >= th) & (sgn(ms) == sgn(comp))) for k in SYMS})
    # regression: which window predicts 14:50 -> 15:00 (composite, gross, ATR units)?
    y = r10.mean(1).where(r10.notna().all(1)); D = pd.concat([y.rename("y"), ma.rename("ma"), mb.rename("mb"), (ms - comp).rename("pre14")], axis=1).dropna()
    for per, msk in (("2018-22", D.index < SPLIT), ("2023-26", D.index >= SPLIT)):
        d_ = D[msk]; Z = np.c_[np.ones(len(d_)), d_[["ma", "mb", "pre14"]].to_numpy()]
        b, *_ = np.linalg.lstsq(Z, d_.y.to_numpy(), rcond=None); res = d_.y.to_numpy() - Z @ b
        se = np.sqrt(np.diag(np.linalg.inv(Z.T @ Z)) * res.var(ddof=4))
        print(f"   OLS {per}: y(14:50->15:00) on 14:00->14:30 {b[1]:+.4f} (t {b[1] / se[1]:.1f}), 14:30->14:50 {b[2]:+.4f} (t {b[2] / se[2]:.1f}), "
              f"8:31->14:00 {b[3]:+.4f} (t {b[3] / se[3]:.1f})  n={len(d_)}")

    # ------------------------------------------------------------------ pick (2018-22 pooled daily t only)
    print("\n" + "=" * 118 + "\nPick: every selectable variant ranked by the 2018-22 t of the pooled daily stream (holdout not used)")
    sc = sorted(((tpool18(P), nm) for nm, (L, P, f) in VAR.items()), reverse=True)
    for s_, nm in sc[:12]: print(line(VAR[nm][1], f"POOL {nm}"[:58]) + f"  [18-22 t {s_:.2f}]")
    # Apex tradability is part of the S bar: a fixed stop is required, so only stop-0.25 variants are selectable
    sel = [(s_, nm) for s_, nm in sc if not nm.endswith("None")]
    best = sel[0][1]
    print(f"\n   picked among the stop-0.25 variants (no-stop variants are listed for reference; Apex needs a stop): {best} [18-22 t {sel[0][0]:.2f}]")
    import re
    th_b = float(re.search(r">= ([0-9.]+)", best).group(1)); ST = 0.25
    KIND = ("agree" if "signs agree" in best else "own" if best.startswith("own") else "all" if best.startswith("all three")
            else "comp20" if "last 20 min same sign" in best else "comp" if best.startswith("composite >=") and "&" not in best else None)
    assert KIND, best

    def rule(dec, look):
        """The picked rule decided at `dec` on the move from `dec - look` minutes (signals on W.days)."""
        jd = jof(dec)
        def mv(ln):
            return pd.DataFrame({k: pd.Series((W.S[k].cf[W.S[k].tr * 1440 + jd] - W.S[k].cf[W.S[k].tr * 1440 + jd - ln]) / W.S[k].atr,
                                              index=W.S[k].idx).reindex(W.days).where(W.F[k]["full"].reindex(W.days).fillna(False).astype(bool))
                                 for k in SYMS})
        mm = mv(look); ag = (sgn(mm).nunique(axis=1) == 1) & mm.notna().all(1) & (mm != 0).all(1); cc = mm.mean(1).where(mm.notna().all(1))
        if KIND == "own": return {k: mm[k].where(mm[k].abs() >= th_b) for k in SYMS}
        if KIND == "agree": return {k: mm[k].where((mm[k].abs() >= th_b) & ag) for k in SYMS}
        if KIND == "all": return {k: mm[k].where((mm.abs() >= th_b).all(1) & ag) for k in SYMS}
        if KIND == "comp": return {k: cc.where(cc.abs() >= th_b) for k in SYMS}
        m20 = mv(20).mean(1); return {k: cc.where((cc.abs() >= th_b) & (sgn(m20) == sgn(cc))) for k in SYMS}

    # ------------------------------------------------------------------ 4. entry / exit timing on the pick
    print("\n" + "=" * 118 + f"\n4. Entry / exit timing for the pick ({best}); the 14:51 bar opens at 14:50:00 = the first imbalance message")
    TIM = {}
    for dec, ent, ex in [(1450, e, x) for e in (1451, 1452, 1453) for x in (1500, 1459)] + [(1451, 1452, 1500), (1452, 1453, 1500)]:
        sg = rule(dec, jof(dec) - jof(1400)); L = W.legs(sg, j0=jof(ent), j1=jof(ex), stop=ST); P = W.pool(L); TIM[(dec, ent, ex)] = (L, P, sg)
        print(line(P, f"POOL decide {dec} (move from 14:00), enter {ent} open, exit {ex} close") + f"  [18-22 t {tpool18(P):.2f}]")
    NVAR["4 timing"] = len(TIM) - 1
    DEC, ENT, EXT = max(TIM, key=lambda k: tpool18(TIM[k][1])); Lb, Pb, SIG = TIM[(DEC, ENT, EXT)]
    best = f"{best}, decide {DEC}, enter {ENT} open, exit {EXT} close"
    print(f"   final pick (2018-22 t): {best}")

    # ------------------------------------------------------------------ 3. day types (pre-registered)
    print("\n" + "=" * 118 + f"\n3. Day types for the pick (pre-registered: 4 splits, 8 cells; descriptive unless a cell beats the rest in both periods)")
    days = W.days; ser = pd.Series(days, index=days)
    month_end = ser.groupby([days.year, days.month]).transform("max") == ser
    fri = pd.Series(days.dayofweek == 4, index=days)
    third_fri = fri & pd.Series((days.day >= 15) & (days.day <= 21), index=days)
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE
    vmed = vix.rolling(252, min_periods=126).median(); hiv = (vix > vmed).shift(1)               # prior day's close vs its median
    hiv = hiv.reindex(days, method="ffill").fillna(False).astype(bool)
    SPLITS = {"month-end": month_end, "Friday": fri, "3rd Friday (opex)": third_fri, "prior VIX > 252d median": hiv}
    for nm, msk in SPLITS.items():
        for lab, mm in ((nm, msk), ("not " + nm, ~msk)):
            print(line(Pb.where(mm.to_numpy(), 0.0), f"POOL {lab}"))
    NVAR["3 day types"] = 2 * len(SPLITS)

    # ------------------------------------------------------------------ full report for the pick
    print("\n" + "=" * 118 + f"\nFull report: {best} (pooled NQ-eq $ = each leg sized to NQ's ATR risk)")
    for k, t in Lb.items():
        print(line(t.net, f"{k} $/contract whole") + "\n" + line(t.net[t.side > 0], f"{k}   longs") + "\n" + line(t.net[t.side < 0], f"{k}   shorts"))
        print(byyear(t.net))
    Pl = W.pool({k: t[t.side > 0] for k, t in Lb.items()}); Ps = W.pool({k: t[t.side < 0] for k, t in Lb.items()})
    print(line(Pb, "POOL whole (per active day)") + "\n" + line(Pl, "POOL longs") + "\n" + line(Ps, "POOL shorts")); print(byyear(Pb))
    rows = {"pool": (Pb, Pb[Pb != 0]), "pool longs": (Pl, Pl[Pl != 0]), "pool shorts": (Ps, Ps[Ps != 0])}
    for k, t in Lb.items():
        S = W.S[k]; rows[f"{k} /contract"] = (S.daily(t), t.net)
    print("   metrics 2018-2026 (daily $, $50k):\n" + M.table(rows))
    h = W.days >= SPLIT
    rows23 = {k: (v[0][v[0].index >= SPLIT], v[1][v[1].index >= SPLIT]) for k, v in rows.items()}
    print("   metrics 2023-2026:\n" + M.table(rows23))
    b, p = R.report({"pool 2023+": Pb[h], "pool longs 2023+": Pl[h], "pool shorts 2023+": Ps[h],
                     **{f"{k} 2023+": W.S[k].daily(t)[W.S[k].idx >= SPLIT] for k, t in Lb.items()}}, n=3000)
    print("   bootstrap (10-day blocks, 3,000 runs), 2023+:\n" + b); print("   permutation, 2023+:\n" + p)

    # ------------------------------------------------------------------ placebos
    print(f"\n   placebo 1: the same rule decided at other times ({jof(DEC) - jof(1400)}-minute move, enter {jof(ENT) - jof(DEC)} min later, out {jof(EXT) - jof(DEC)} min after the decision)")
    PLAC = {}
    for dec in (1051, 1151, 1251, 1321, 1351, 1421, DEC) if DEC == 1451 else (1050, 1150, 1250, 1320, 1350, 1420, DEC):
        jd = jof(dec); P = W.pool(W.legs(rule(dec, jof(DEC) - jof(1400)), j0=jd + jof(ENT) - jof(DEC), j1=jd + jof(EXT) - jof(DEC), stop=ST)); PLAC[dec] = P
        print(line(P, f"POOL decide {dec}"))
    print("   placebo 2: random sides on the same days (one coin per day for all legs; full re-simulation with the stop), 500 draws")
    rnd = np.random.default_rng(7); act = Pb != 0; real = Pb[act].mean(); draws = []
    if True:
        for _ in range(500):
            flip = pd.Series(rnd.choice((-1.0, 1.0), len(W.days)), index=W.days)
            P = W.pool(W.legs({k: SIG[k] * flip for k in SYMS}, j0=jof(ENT), j1=jof(EXT), stop=ST)); draws.append(P[P != 0].mean())
        draws = np.array(draws)
        print(f"   rule ${real:.0f} per active day; random sides: mean ${draws.mean():.0f}, 95th ${np.percentile(draws, 95):.0f}, 99th "
              f"${np.percentile(draws, 99):.0f}, max ${draws.max():.0f}; share >= rule {np.mean(draws >= real):.4f}")

    # ------------------------------------------------------------------ correlation with the NQ funded plan
    try:
        from time_clusters_test import trades as plan_trades
        T = plan_trades(W.S["NQ"].G)
        plan = sum(t.net.groupby(pd.DatetimeIndex(t.date).normalize()).sum().reindex(W.days, fill_value=0.0)
                   for k, t in T.items() if k in ("VB", "ONB_ML2_MC", "MON_MC", "EOS", "LDF_MC", "NFP_MC"))
        j = pd.concat([Pb.rename("moc"), plan.rename("plan")], axis=1)
        both = (j.moc != 0) & (j.plan != 0)
        print(f"\n   correlation with the NQ plan's daily net (VB, ONB ML2, MON, EOS, LDF, NFP; per NQ): all days {j.corr().iloc[0, 1]:.3f}, "
              f"days both trade {j[both].corr().iloc[0, 1]:.3f} (n={both.sum()})")
        ldf = T["LDF_MC"]; ldd = set(pd.DatetimeIndex(ldf.date).normalize())
        on = Pb[act].index.isin(list(ldd))
        print(f"   pick on Late-Day Flow days: {on.sum()} of {act.sum()}, avg ${Pb[act][on].mean():.0f}; other days ${Pb[act][~on].mean():.0f}")
    except Exception as ex:
        print(f"\n   plan correlation skipped: {ex!r}")

    # ------------------------------------------------------------------ sizing hint and variant count
    nq = W.S["NQ"]; at = pd.Series(nq.atr, index=nq.idx)
    print(f"\n   NQ 15-day ATR median 2023+: {at[at.index >= SPLIT].median():.0f} pts -> 0.25 ATR stop = ${0.25 * at[at.index >= SPLIT].median() * 20:,.0f} per NQ "
          f"(${0.25 * at[at.index >= SPLIT].median() * 2:,.0f} per MNQ)")
    for k in ("ES", "YM"):
        tt = Lb[k]; print(f"   {k} leg weight (contracts per NQ-eq), median 2023+: {tt.w[tt.index >= SPLIT].median():.2f}")
    dl = pd.DataFrame({k: W.S[k].daily(t).reindex(W.days, fill_value=0.0) for k, t in Lb.items()}); on_ = (dl != 0).any(axis=1)
    print("   daily P&L correlation between the legs on trade days:\n" + dl[on_].corr().round(3).to_string())
    MIC = {"NQ": 0.1, "ES": 0.2, "YM": 0.3}                             # 1 MNQ + 2 MES + 3 MYM (full-contract equivalents)
    mic = sum(dl[k] * v for k, v in MIC.items()); nq1 = dl["NQ"] * 0.1
    print("   fixed micro size (net scaled from the full contracts; micro commissions differ slightly):\n" + M.table({
        "1 MNQ + 2 MES + 3 MYM": (mic, mic[mic != 0]), "1 MNQ + 2 MES + 3 MYM, 2023+": (mic[mic.index >= SPLIT], mic[(mic != 0) & (mic.index >= SPLIT)]),
        "1 MNQ only": (nq1, nq1[nq1 != 0]), "1 MNQ only, 2023+": (nq1[nq1.index >= SPLIT], nq1[(nq1 != 0) & (nq1.index >= SPLIT)])}))
    print("\n   variants tried: " + ", ".join(f"{k} {v}" for k, v in NVAR.items()) + f"; total {sum(NVAR.values())}")
    pickle.dump(dict(best=best, legs=Lb, pool=Pb, timing=TIM, placebo=PLAC, nvar=NVAR,
                     variants={nm: P for nm, (L, P, f) in VAR.items()}), open(SP + "s_rank_moc2.pkl", "wb"))
