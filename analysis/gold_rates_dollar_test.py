"""Gold vs rates and the dollar (2026-10-14; new data: ZN 10-year note and 6E euro futures, 1-minute, CT).

Idea: gold is priced off real rates and the dollar. ZN up (yields down) and 6E up (dollar down) should lift gold.
If gold under- or over-reacts to what ZN and 6E imply over the last W minutes, does it catch up (fade the residual)?
Model, known before each day: a rolling 60-day regression of gold's 30-minute moves (in ATR units) on ZN's and 6E's
(7:00-13:00 CT, prior days only). Residual at decision time T = gold's W-minute move - beta . (ZN, 6E moves), in gold
ATR units.
  1. Co-movement: 30-minute return correlations by year; lead-lag (does ZN / 6E's last k minutes predict gold's next
     k minutes, beyond gold's own last k minutes?).
  2. Trades on gold (1 GC, $100/pt, tick 0.10, $7.25 + 1 tick per fill), decided at T = 8:00 .. 12:00 CT every 30 min,
     lookback W = 30 / 60 min, hold H = 30 / 60 min:
       a. fade the residual when |resid| >= k (0.15 / 0.30 ATR);
       b. catch-up: gold flat (|move| < 0.05 ATR) but the implied move |beta . f| >= k: trade gold the implied way.
     Plus the overnight version: residual 17:00 -> 7:20, trade 7:21 -> 9:00 / 12:30.
  3. Placebo for every rule: the same rule with ZN / 6E moves taken from a random other day (keeps gold's own moves).
Roll jumps (unadjusted continuous contracts; GC, ZN, 6E roll at 03:32 CT or the 17:00 reopen) are removed: any window
containing a bar-to-bar jump > 0.25 ATR is skipped. Design 2018-22, holdout 2023-26; picks by design t only; many
variants, so also report how many design-positive rules stay positive in the holdout vs the placebo.
  4. Session level: the previous session's residual (17:00 -> 15:59, 250-day betas) -> fade / follow today's session.
  python3 analysis/gold_rates_dollar_test.py [SCRATCH_DIR]
"""
import sys, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from cl_forced_flows_test import load
import metrics as M, resampling as R

PV, TICK, COMM = 100.0, 0.10, 7.25
SPLIT = pd.Timestamp("2023-01-01")


def tstat(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def line(x, nm, w=70):
    x = pd.Series(x).dropna()
    if len(x) < 8: return f"   {nm:<{w}} n={len(x)}"
    y = x.index.year; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.0f} PF {pf:4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(x.groupby(y).sum() > 0).sum()}/{len(set(y))}"
            f" | 18-22 ${x[y < 2023].mean():6.0f} (t {tstat(x[y < 2023]):4.1f}) 23-26 ${x[y >= 2023].mean():6.0f} (t {tstat(x[y >= 2023]):4.1f})")


class Aligned:
    """One symbol's minute closes on gold's trading rows (by calendar date), roll-jump flags and ATR."""
    def __init__(self, G, dates):
        r = np.searchsorted(G.dates, dates); ok = (r < G.D) & (G.dates[np.minimum(r, G.D - 1)] == dates)
        self.ok = ok; r = np.where(ok, r, 0)
        cf = pd.Series(G.c.ravel()).ffill().to_numpy(); o = G.o.ravel(); pc = pd.Series(G.c.ravel()).ffill().shift(1).to_numpy()
        atr = G.daily_atr(15)
        jump = np.abs(o - pc) > 0.25 * np.repeat(atr, 1440)
        self.c = np.where(ok[:, None], cf.reshape(G.D, 1440)[r], np.nan)
        self.prev = np.where(ok[:, None], cf.reshape(G.D, 1440)[np.maximum(r - 1, 0)], np.nan)     # previous calendar date
        self.jcum = np.where(ok[:, None], np.cumsum(jump.reshape(G.D, 1440), axis=1)[r], 0)
        self.atr = np.where(ok, atr[r], np.nan)

    def mv(self, a, b):
        """Move from the close of bar a to the close of bar b (columns), in ATR units; nan if a roll jump is inside."""
        m = (self.c[:, b] - self.c[:, a]) / self.atr
        return np.where(self.jcum[:, b] - self.jcum[:, a] > 0, np.nan, m)


if __name__ == "__main__":
    pd.set_option("display.width", 240)
    print(__doc__.split("\n")[0])
    gc, zn, e6 = load("GC"), load("ZN"), load("6E")
    tr = gc.trading[pd.DatetimeIndex(gc.ts[gc.trading]) >= "2018-01-01"]; idx = pd.DatetimeIndex(gc.ts[tr]); D = len(tr)
    dates = gc.dates[tr]
    G, Z, E = Aligned(gc, dates), Aligned(zn, dates), Aligned(e6, dates)
    both = Z.ok & E.ok
    print(f"gold days {D}; with ZN and 6E data {both.sum()}")

    # ---- rolling betas from 30-minute moves 7:00-13:00 CT on prior days ----
    halves = [(jof(t0), jof(t0) + 30) for t0 in (700, 730, 800, 830, 900, 930, 1000, 1030, 1100, 1130, 1200, 1230)]
    Yg = np.stack([G.mv(a, b) for a, b in halves], 1); Xz = np.stack([Z.mv(a, b) for a, b in halves], 1); Xe = np.stack([E.mv(a, b) for a, b in halves], 1)
    ok = np.isfinite(Yg) & np.isfinite(Xz) & np.isfinite(Xe)
    f = lambda a: np.where(ok, a, 0.0)
    S = {k: pd.Series(v.sum(1)).rolling(60, min_periods=40).sum().shift(1).to_numpy() for k, v in
         (("zz", f(Xz * Xz)), ("ee", f(Xe * Xe)), ("ze", f(Xz * Xe)), ("zy", f(Xz * Yg)), ("ey", f(Xe * Yg)))}
    det = S["zz"] * S["ee"] - S["ze"] ** 2
    bz = (S["ee"] * S["zy"] - S["ze"] * S["ey"]) / det; be = (S["zz"] * S["ey"] - S["ze"] * S["zy"]) / det
    print(f"rolling betas (gold ATR per ATR): ZN median {np.nanmedian(bz):.2f} (by year {pd.Series(bz, index=idx).groupby(idx.year).median().round(2).to_dict()})")
    print(f"                                  6E median {np.nanmedian(be):.2f} (by year {pd.Series(be, index=idx).groupby(idx.year).median().round(2).to_dict()})")

    print("\n1. Co-movement and lead-lag")
    flat = lambda a: a[ok]
    yr = np.repeat(idx.year.to_numpy()[:, None], len(halves), 1)[ok]
    cz = pd.Series(flat(Yg)).groupby(yr).corr(pd.Series(flat(Xz))); ce = pd.Series(flat(Yg)).groupby(yr).corr(pd.Series(flat(Xe)))
    print("   30-min correlation gold-ZN by year: " + " ".join(f"{a} {b:.2f}" for a, b in cz.items()))
    print("   30-min correlation gold-6E by year: " + " ".join(f"{a} {b:.2f}" for a, b in ce.items()))
    for k in (1, 5, 15, 30):
        rows = []
        for t0 in range(jof(800), jof(1200), 30):
            g_next = G.mv(t0, t0 + k); g_past = G.mv(t0 - k, t0); z_past = Z.mv(t0 - k, t0); e_past = E.mv(t0 - k, t0)
            rows.append(np.c_[g_next, g_past, z_past, e_past])
        A = np.vstack(rows); A = A[np.isfinite(A).all(1)]
        X = np.c_[np.ones(len(A)), A[:, 1:]]; coef, *_ = np.linalg.lstsq(X, A[:, 0], rcond=None)
        res = A[:, 0] - X @ coef; se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * res.var())
        print(f"   k={k:2d} min: gold next on [gold past, ZN past, 6E past]: coef {coef[1]:+.3f} / {coef[2]:+.3f} / {coef[3]:+.3f}, t {coef[1] / se[1]:+.1f} / {coef[2] / se[2]:+.1f} / {coef[3] / se[3]:+.1f}  (n {len(A)})")

    # ---- trades ----
    O = gc.o; Cg = pd.Series(gc.c.ravel()).ffill().to_numpy().reshape(gc.D, 1440)
    rng = np.random.default_rng(7); perm = rng.permutation(D)
    def trade(side, e_j, x_j):
        """Gold market entry at the open of column e_j, out at the close of x_j (arrays per day); net $ per GC."""
        e_j = np.broadcast_to(e_j, D); x_j = np.broadcast_to(x_j, D)
        ent = O[tr, e_j] + side * TICK; ex = Cg[tr, x_j] - side * TICK
        jump = G.jcum[np.arange(D), x_j] - G.jcum[np.arange(D), np.maximum(e_j - 1, 0)] > 0
        net = (ex - ent) * side * PV - COMM
        return pd.Series(np.where((side != 0) & np.isfinite(net) & ~jump, net, np.nan), index=idx).dropna()
    res = {}
    for T, W, H, k, rule in itertools.product(range(jof(800), jof(1200) + 1, 30), (30, 60), (30, 60), (0.15, 0.30), ("fade", "catch")):
        for pl in (False, True):
            gm = G.mv(T - W, T); zm = Z.mv(T - W, T); em = E.mv(T - W, T)
            if pl: zm, em = zm[perm], em[perm]
            imp = bz * zm + be * em; resid = gm - imp
            if rule == "fade": side = np.where(np.abs(resid) >= k, -np.sign(resid), 0)
            else: side = np.where((np.abs(gm) < 0.05) & (np.abs(imp) >= k), np.sign(imp), 0)
            side = np.nan_to_num(side).astype(int)
            res[(T, W, H, k, rule, pl)] = trade(side, T + 1, T + H)
    # overnight residual -> day
    for out_t, k, rule in itertools.product((900, 1230), (0.15, 0.30), ("fade", "catch")):
        for pl in (False, True):
            def on(A):
                m = (A.c[:, jof(720)] - A.prev[:, jof(1700)]) / A.atr
                return m
            gm, zm, em = on(G), on(Z), on(E)
            if pl: zm, em = zm[perm], em[perm]
            imp = bz * zm + be * em; resid = gm - imp
            side = np.where(np.abs(resid) >= k, -np.sign(resid), 0) if rule == "fade" else np.where((np.abs(gm) < 0.1) & (np.abs(imp) >= k), np.sign(imp), 0)
            res[("ON", out_t, k, rule, pl)] = trade(np.nan_to_num(side).astype(int), jof(721), jof(out_t))

    real = {k: v for k, v in res.items() if not k[-1]}; plac = {k: v for k, v in res.items() if k[-1]}
    def summary(D_):
        rows = []
        for k_, v in D_.items():
            y = v.index.year
            rows.append(dict(key=k_[:-1], n=len(v), avg=v.mean(), t=tstat(v), t_d=tstat(v[y < 2023]), avg_d=v[y < 2023].mean(), avg_h=v[y >= 2023].mean(), t_h=tstat(v[y >= 2023])))
        return pd.DataFrame(rows)
    Sr, Sp = summary(real), summary(plac)
    print(f"\n2. Trades: {len(real)} rules (plus the same number of placebos)")
    for nm, Sx in (("real", Sr), ("placebo", Sp)):
        dp = Sx[Sx.t_d > 0]
        print(f"   {nm:<8}: design-positive {len(dp)} of {len(Sx)}; of those, holdout-positive {np.mean(dp.avg_h > 0):.0%}; design t >= 2: {int((Sx.t_d >= 2).sum())}, "
              f"of those holdout t >= 1: {int(((Sx.t_d >= 2) & (Sx.t_h >= 1)).sum())}; mean holdout $ of the top-10 design rules: ${Sx.sort_values('t_d', ascending=False).head(10).avg_h.mean():.0f}")
    top = Sr.sort_values("t_d", ascending=False).head(12)
    print("\n   top 12 rules by design t (key = T, W, H, k, rule  or  ON, exit, k, rule):")
    print(top.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
    best = top.iloc[0].key; x = real[best + (False,)]
    print(f"\n== best design rule {best}")
    print(line(x, "picked")); print(line(plac[best + (True,)], "   its placebo (ZN / 6E from random days)"))
    days = pd.DatetimeIndex(gc.ts[gc.trading]); days = days[days >= "2018-01-01"]
    dl = lambda s: s.groupby(s.index.normalize()).sum().reindex(days, fill_value=0.0)
    print(M.table({"picked": (dl(x), x)}))
    b_, p_ = R.report({"picked, 2023+": dl(x)[days >= SPLIT]}, n=3000); print(b_); print(p_)

    # ---- 3. session level: yesterday's residual -> today's gold session (17:01 -> 15:58, the Apex trading day) ----
    print("\n3. Session level: residual of gold's previous session (17:00 -> 15:59) vs ZN / 6E -> trade today's session")
    def sess(A):
        m = (A.c[:, jof(1559)] - A.prev[:, jof(1700)]) / A.atr          # previous evening 17:00 -> today 15:59
        return m
    gS, zS, eS = sess(G), sess(Z), sess(E)
    okS = np.isfinite(gS) & np.isfinite(zS) & np.isfinite(eS)
    jumpday = (G.jcum[:, jof(1559)] > 0) | (Z.jcum[:, jof(1559)] > 0) | (E.jcum[:, jof(1559)] > 0)
    okS &= ~jumpday
    Xs = pd.DataFrame({"z": np.where(okS, zS, np.nan), "e": np.where(okS, eS, np.nan), "g": np.where(okS, gS, np.nan)})
    roll = lambda a: a.rolling(250, min_periods=120).sum().shift(1)
    zz, ee, ze = roll(Xs.z ** 2), roll(Xs.e ** 2), roll(Xs.z * Xs.e); zy, ey = roll(Xs.z * Xs.g), roll(Xs.e * Xs.g)
    dt = zz * ee - ze ** 2; bzS = ((ee * zy - ze * ey) / dt).to_numpy(); beS = ((zz * ey - ze * zy) / dt).to_numpy()
    resid = gS - (bzS * zS + beS * eS)
    print(f"   session betas (250-day): ZN median {np.nanmedian(bzS):.2f}, 6E median {np.nanmedian(beS):.2f}; residual sd {np.nanstd(resid):.2f} ATR")
    nxt_side = lambda s: np.r_[s[:-1], 0]          # placeholder (side decided on day i, traded on day i+1)
    for k in (0.0, 0.5, 1.0):
        for nm, sgn in (("fade", -1), ("follow", 1)):
            side = np.where(np.abs(resid) >= k, sgn * np.sign(resid), 0); side = np.nan_to_num(side).astype(int)
            out = {}
            for i in range(D - 1):
                s = side[i]
                if s == 0 or not okS[i]: continue
                d1 = tr[i + 1]; e_i = (d1 - 1) * 1440 + jof(1701); x_i = d1 * 1440 + jof(1558)        # next session: prev evening 17:01 -> 15:58
                o_ = gc.o.ravel()[e_i]; c_ = pd.Series(gc.c.ravel()).iloc[x_i - 5:x_i + 1].ffill().iloc[-1]
                if np.isnan(o_) or np.isnan(c_) or G.jcum[i + 1, jof(1559)] > 0: continue
                out[idx[i + 1]] = ((c_ - s * TICK) - (o_ + s * TICK)) * s * PV - COMM
            print(line(pd.Series(out), f"{nm} the previous session's residual, |resid| >= {k} ATR"))
