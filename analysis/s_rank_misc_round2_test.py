"""S-rank program, round 2 items 3-5 (S_RANK_PROGRAM.md, 2026-10-14): three independent pre-registered tests.

Costs: NQ $20/pt, tick 0.25, $7.25; ES $50/pt, tick 0.25, $5; YM $5/pt, tick 1, $5; GC $100/pt, tick 0.10, $7.25;
+ 1 tick per market / stop fill, no tick on limit fills. Design 2018-22, holdout 2023-26, picks by design t only.
Advance = |t| >= 2.5 overall with the same sign in 2018-22 and 2023-26 -> full metrics (metrics.py / resampling.py).

A. ES Overnight Bias through NQ's model, cleanly out of sample. The NQ ONB ML v2 ridge (ml_filter_test.py ml6: R
   multiple of each ONB ADX20 / 0.30 ATR trade on 14 price + calendar inputs known before the open, 2-98% winsorized,
   lambda = n, standardized) is refit on NQ ONB trades of 2018-22 ONLY (Python engine candidates24.overnight_bias24 on
   both markets), frozen, and applied to (i) NQ 2023-26 (reference) and (ii) ES ONB candidate trades 2023-26 (ES inputs
   computed the same way). Pre-registered rule: v2 (keep shorts with score >= 0, longs with score >= 0.03), NQ's
   standardization (the raw NQ coefficients on ES inputs, as in round 1); also v1 (score >= 0) and ES's own 2018-22
   input scaling (no ES labels used). Kept vs skipped; random-keep placebo at the same keep rate (5,000 draws).
   ES 2018-22 under the same frozen model is shown too (cross-market, but the same years as the fit).
B. EOS low-VIX split. EOS = short the 8:31 open on the monthly 3rd Friday, out 10:00, stop 0.3 ATR. NQ uses the
   MultiCharts trade list (time_clusters_test.trades(g)["EOS"]); YM (independent check) and ES (replication of round
   1) use the Python engine with the same rules. One split: the prior VIX close (data/VIX_daily.csv, last close before
   the trade date) below / above its own trailing 252-day median; sanity: prior VIX below / above 20.
C. Gold. (1) Options-expiry pinning as a short-vol fade: on COMEX options-expiry days (4th-last business day of the
   month, round-1 code), the first 1-minute close between 7:21 and 11:30 CT that is >= k ATR (k 0.25 / 0.4 / 0.6) from
   the 7:20 open (open of the 7:20-7:21 bar) -> fade at the next bar's open (1 tick), target = the 7:20 open (limit,
   must trade through by 1 tick, no slip), stop 0.5 / 1.0 ATR beyond entry (1 tick), else out at the 12:30 close
   (1 tick); stop assumed first when target and stop share a bar. Placebo: the same rule on non-expiry days, on the
   day before and after expiry, and random sets of non-expiry days. (2) LBMA auction short with resting limits: short
   limit at the close 1 minute before the auction (AM 10:30 / PM 15:00 London, moving with the London clock) + k ticks
   (k 1 / 2 / 3), working from that minute until the exit, filled only if the high trades >= 1 tick through it, no
   slippage, $7.25; out at market (1 tick) at the close 10 / 20 / 30 minutes after the auction start. Placebo: the
   same limit rule 60 / 120 minutes before / after (London clock) and the mirror (buy limit k ticks below, long).
   Windows containing a roll bar (round-1 detection) are dropped.
  python3 analysis/s_rank_misc_round2_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
SPLIT = pd.Timestamp("2023-01-01")
SPEC = {"NQ": (20.0, 0.25, 7.25), "ES": (50.0, 0.25, 5.0), "YM": (5.0, 1.0, 5.0), "GC": (100.0, 0.10, 7.25)}
NVAR = {}
RES = {}


def tstat(x):
    x = np.asarray(pd.Series(x).dropna(), float); return x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pfac(x):
    x = pd.Series(x).dropna(); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(x, nm, w=60):
    x = pd.Series(x).dropna()
    if len(x) < 6: return f"   {nm:<{w}} n={len(x)}" + (f" avg ${x.mean():.0f}" if len(x) else "")
    y = x.index.year; by = x.groupby(y).sum(); a, b = x[y < 2023], x[y >= 2023]
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():5.0f} PF {pfac(x):4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():5.0f} (t {tstat(a):4.1f}) 23-26 ${b.mean():5.0f} (t {tstat(b):4.1f})")


def advances(x):
    x = pd.Series(x).dropna(); a, b = x[x.index < SPLIT].mean(), x[x.index >= SPLIT].mean()
    return len(x) > 10 and abs(tstat(x)) >= 2.5 and np.sign(a) == np.sign(b) == np.sign(x.mean())


def byyear(x):
    return "   by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in x.groupby(x.index.year).sum().items())


def full_metrics(name, t, days, nq_rth):
    """Full metrics for an advancing candidate: t has a DatetimeIndex, columns net and side."""
    dl = lambda q: q.net.groupby(q.index.normalize()).sum().reindex(days, fill_value=0.0)
    lg, sh = t[t.side > 0], t[t.side < 0]
    print(f"\n   == full metrics: {name}")
    print(line(t.net, "all")); print(line(lg.net, "longs")); print(line(sh.net, "shorts")); print(byyear(t.net))
    rows = {"all": (dl(t), t.net)}
    if len(lg): rows["longs"] = (dl(lg), lg.net)
    if len(sh): rows["shorts"] = (dl(sh), sh.net)
    rows["all 2023+"] = (dl(t)[days >= SPLIT], t.net[t.index >= SPLIT])
    print(M.table(rows))
    rr = {f"{name[:26]} 2023+": dl(t)[days >= SPLIT]}
    for nm, q in (("longs", lg), ("shorts", sh)):
        if (q.index >= SPLIT).sum() > 15: rr[f"  {nm} 2023+"] = dl(q)[days >= SPLIT]
    b_, p_ = R.report(rr, n=3000); print(b_); print(p_)
    d = dl(t); nr = nq_rth.reindex(days).fillna(0.0)
    print(f"   daily correlation with NQ RTH 8:30->15:00: all days {np.corrcoef(d, nr)[0, 1]:+.2f}; trade days {np.corrcoef(d[d != 0], nr[d != 0])[0, 1]:+.2f}")


def same_day(g, sym, rows, sides, j0, j1, stop_pts):
    """Same-day trades (round-1 engine): entry at the open of bar j0 +/- 1 tick, stop at stop (worse open on a gap) - 1 tick,
    else out at the close of bar j1 (or the last bar before) - 1 tick."""
    PV, TICK, COMM = SPEC[sym]; O, H, L, C = g.o, g.h, g.l, g.c; out = []
    for d, s, sp_ in zip(rows, np.broadcast_to(sides, (len(rows),)), np.broadcast_to(np.asarray(stop_pts, float), (len(rows),))):
        if np.isnan(O[d, j0]) or not np.isfinite(sp_): continue
        e = O[d, j0] + s * TICK; sp = e - s * sp_; px = None
        seg = L[d, j0:j1 + 1] if s > 0 else H[d, j0:j1 + 1]
        hit = np.where((seg <= sp) if s > 0 else (seg >= sp))[0]
        if len(hit):
            j = j0 + hit[0]; px = (sp if j == j0 else (min(O[d, j], sp) if s > 0 else max(O[d, j], sp))) - s * TICK
        if px is None:
            cc = C[d, j0:j1 + 1]; ok = np.where(~np.isnan(cc))[0]
            if not len(ok): continue
            px = cc[ok[-1]] - s * TICK
        out.append(dict(date=pd.Timestamp(g.ts[d]), side=s, net=(px - e) * s * PV - COMM))
    return pd.DataFrame(out).set_index("date") if out else pd.DataFrame(columns=["side", "net"])


def rth_series(g, pv):
    cf = pd.Series(g.c.ravel()).ffill().to_numpy(); r = g.trading
    return pd.Series((cf[r * 1440 + jof(1500)] - g.o[r, jof(831)]) * pv, index=pd.DatetimeIndex(g.ts[r]))


def trading_days(g):
    d = pd.DatetimeIndex(g.ts[g.trading]); return d[d >= "2018-01-01"]


# =========================================================================================== A
def onb_features(g):
    """The 14 NQ ONB ML v2 inputs (ml_filter_test.py), known before the 8:30 open, on every trading row of g."""
    tr = g.trading; idx = pd.DatetimeIndex(g.ts[tr]); cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    cl = pd.Series(cf[tr * 1440 + jof(1500)], index=idx); op = pd.Series(g.o[tr, jof(831)], index=idx)
    atr = pd.Series(g.daily_atr(15)[tr], index=idx); r1 = np.log(cl).diff()
    X = pd.DataFrame(index=idx)
    X["ret1"] = r1.shift(1); X["ret5"] = np.log(cl).diff(5).shift(1); X["ret20"] = np.log(cl).diff(20).shift(1)
    X["rth1"] = np.log(cl / op).shift(1); X["atr_ratio"] = atr / atr.rolling(60).mean()
    X["dist50"] = np.log(cl / cl.rolling(50).mean()).shift(1); X["rv5_rv20"] = (r1.rolling(5).std() / r1.rolling(20).std()).shift(1)
    for k in range(5): X[f"dow{k}"] = (idx.dayofweek == k).astype(float)
    X["tdm"] = (pd.Series(1, index=idx).groupby(idx.year * 100 + idx.month).cumcount() + 1 <= 3).astype(float)
    fri_dom = idx.day + (4 - idx.dayofweek); X["opex_wk"] = ((fri_dom >= 15) & (fri_dom <= 21)).astype(float)
    return X.fillna(X.median())


def onb_trades(g, sym, adx_min=20, stop_atr=0.30):
    from candidates24 import overnight_bias24
    PV, TICK, COMM = SPEC[sym]
    t = overnight_bias24(g, adx_min=adx_min, stop_atr=stop_atr).copy()
    t["date"] = pd.to_datetime(t.date); t = t[t.date >= "2018-01-01"]
    t["net"] = (t.exit - t.entry) * t.side * PV - COMM - TICK * PV * (1 + (t.kind != 1))   # stop entry 1 tick; stop / time exit 1 tick
    t["R"] = t.net / (stop_atr * g.daily_atr(15)[t.day.to_numpy()] * PV)
    return t.set_index("date", drop=False)


def ridge_fit(Xt, b):
    mu, sd = Xt.mean(), Xt.std().replace(0, 1); A = ((Xt - mu) / sd).to_numpy(); b = b.to_numpy()
    lo, hi = np.percentile(b, [2, 98]); b = np.clip(b, lo, hi); b = b - b.mean()
    return mu, sd, np.linalg.solve(A.T @ A + len(b) * np.eye(A.shape[1]), A.T @ b)


def keep_report(t, score, label, lthr, rng):
    ok = score.notna(); keep = ok & (score >= np.where(t.side > 0, lthr, 0.0)); skip = ok & ~keep
    k, s = t.net[keep], t.net[skip]; share = keep.sum() / ok.sum()
    pr = np.array([t.net[ok][rng.random(ok.sum()) < share].mean() for _ in range(5000)])
    td = (k.mean() - s.mean()) / np.sqrt(k.var() / len(k) + s.var() / len(s)) if len(k) > 2 and len(s) > 2 else np.nan
    yk, ys = k.groupby(k.index.year).mean(), s.groupby(s.index.year).mean()
    print(line(k, f"{label}: kept ({share:.0%})"))
    print(f"      skipped n={len(s)} avg ${s.mean():.0f} (t {tstat(s):.1f}); kept - skipped t {td:+.1f}; years kept > skipped {(yk > ys.reindex(yk.index)).sum()}/{len(yk)}; "
          f"random keep {share:.0%}: avg ${pr.mean():.0f}, 95th ${np.percentile(pr, 95):.0f}, share >= kept {np.mean(pr >= k.mean()):.3f}")
    print(f"      kept longs n={(t.side[keep] > 0).sum()} ${t.net[keep & (t.side > 0)].mean():.0f} | kept shorts n={(t.side[keep] < 0).sum()} ${t.net[keep & (t.side < 0)].mean():.0f}")
    return t[keep]


def test_A(gn, ge, nq_rth):
    print("\n" + "=" * 110 + "\nA. ES Overnight Bias through NQ's ridge, refit on NQ 2018-22 only (ONB ADX20, stop 0.30 ATR, 3R, out 14:30)")
    tn, te = onb_trades(gn, "NQ"), onb_trades(ge, "ES")
    Xn, Xe = onb_features(gn), onb_features(ge); COLS = list(Xn.columns)
    Xtn, Xte = Xn.reindex(tn.index), Xe.reindex(te.index)
    print(line(tn.net, "NQ ONB plain")); print(line(te.net, "ES ONB plain")); print(line(te.net[te.side > 0], "  ES longs")); print(line(te.net[te.side < 0], "  ES shorts"))
    dn = tn.index < SPLIT
    mu, sd, w = ridge_fit(Xtn.loc[dn, COLS], tn.R[dn])
    print("   NQ 2018-22 ridge (standardized weights): " + ", ".join(f"{c} {v:+.3f}" for c, v in zip(COLS, w)))
    de = te.index < SPLIT; mu_e, sd_e = Xte.loc[de, COLS].mean(), Xte.loc[de, COLS].std().replace(0, 1)
    sc_n = pd.Series(((Xtn[COLS] - mu) / sd).to_numpy() @ w, index=tn.index)
    sc_eN = pd.Series(((Xte[COLS] - mu) / sd).to_numpy() @ w, index=te.index)
    sc_eE = pd.Series(((Xte[COLS] - mu_e) / sd_e).to_numpy() @ w, index=te.index)
    print(f"   score correlation on ES trades, NQ vs ES scaling: {np.corrcoef(sc_eN, sc_eE)[0, 1]:.2f}; ES score >= 0 share {np.mean(sc_eN >= 0):.0%} (NQ scaling)")
    rng = np.random.default_rng(11); out = {}
    hn, he = tn.index >= SPLIT, te.index >= SPLIT
    print("\n   NQ reference: NQ-trained (2018-22) -> NQ 2023-26 (pure out of sample)")
    print(line(tn.net[hn], "NQ 2023-26 plain"))
    for rn, lt in (("v2 longs >= 0.03", 0.03), ("v1 >= 0", 0.0)):
        out[("NQ", rn)] = keep_report(tn[hn], sc_n[hn], f"NQ 23-26 {rn}", lt, rng)
    print("\n   ES: NQ-trained (2018-22) -> ES 2023-26 (pure out of sample, cross-market); ES 2018-22 shown for the same years as the fit")
    print(line(te.net[he], "ES 2023-26 plain"))
    for (sn, sc), (rn, lt) in itertools.product((("NQ scaling", sc_eN), ("ES 18-22 scaling", sc_eE)), (("v2 longs >= 0.03", 0.03), ("v1 >= 0", 0.0))):
        pre = " [PRE-REGISTERED]" if (sn == "NQ scaling" and lt == 0.03) else ""
        print(f"   -- {sn}, {rn}{pre}")
        out[("ES", sn, rn, "23-26")] = keep_report(te[he], sc[he], "ES 23-26", lt, rng)
        out[("ES", sn, rn, "18-22")] = keep_report(te[~he], sc[~he], "ES 18-22 (same years as fit)", lt, rng)
        kk = pd.concat([out[("ES", sn, rn, "18-22")], out[("ES", sn, rn, "23-26")]]).sort_index()
        print(line(kk.net, "ES kept, 2018-26 combined"))
        out[("ES", sn, rn, "all")] = kk
    NVAR["A ES via NQ ridge"] = 4; NVAR["A NQ reference"] = 2
    pre = out[("ES", "NQ scaling", "v2 longs >= 0.03", "all")]
    print(f"\n   pre-registered ES kept set (2018-22 kept is cross-market in-period, 2023-26 pure OOS): {'ADVANCES' if advances(pre.net) else 'does not advance'}")
    if advances(pre.net): full_metrics("ES ONB kept (NQ 18-22 ridge)", pre, trading_days(ge), nq_rth)
    RES["A"] = dict(weights=(mu, sd, w), scores=dict(nq=sc_n, es_nq=sc_eN, es_es=sc_eE), kept=out, nq_plain=tn, es_plain=te)


# =========================================================================================== B
def vix_flags(dates):
    v = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE")["CLOSE"].sort_index()
    med = v.rolling(252, min_periods=200).median()
    pos = v.index.searchsorted(pd.DatetimeIndex(dates).normalize(), side="left") - 1     # last VIX close before the date
    vp, mp = v.to_numpy()[pos], med.to_numpy()[pos]
    return vp, mp


def eos_split(t, label, days, nq_rth, adv):
    vp, mp = vix_flags(t.index)
    lo, hi = vp < mp, vp >= mp
    print(line(t.net, f"{label} EOS plain")); print(byyear(t.net))
    print(line(t.net[lo], f"{label}: prior VIX < its 252-day median")); print(line(t.net[hi], f"{label}: prior VIX >= its 252-day median"))
    ta, tb = t.net[lo], t.net[hi]
    print(f"      low - high difference ${ta.mean() - tb.mean():.0f} (t {(ta.mean() - tb.mean()) / np.sqrt(ta.var() / len(ta) + tb.var() / len(tb)):+.1f})")
    print(line(t.net[vp < 20], f"{label}: prior VIX < 20 (sanity)")); print(line(t.net[vp >= 20], f"{label}: prior VIX >= 20 (sanity)"))
    rng = np.random.default_rng(5); n = lo.sum()
    pr = np.array([t.net.to_numpy()[rng.choice(len(t), n, replace=False)].mean() for _ in range(5000)])
    print(f"      placebo: random {n} of the {len(t)} EOS days: 95th pct ${np.percentile(pr, 95):.0f}; low-VIX ${ta.mean():.0f}; share >= {np.mean(pr >= ta.mean()):.3f}")
    if advances(ta): adv[f"{label} EOS low VIX"] = (t[lo], days)
    return t[lo]


def test_B(gn, ge, gy, nq_rth):
    print("\n" + "=" * 110 + "\nB. EOS (short 8:31 open on the monthly 3rd Friday, out 10:00, stop 0.3 ATR) split by prior VIX vs its 252-day median")
    from time_clusters_test import trades
    from option_income_etf_test import roll_rows
    T = trades(gn)["EOS"]; tn = T.set_index(pd.DatetimeIndex(T.date))[["side", "net"]]
    adv, out = {}, {}
    print("\n   NQ (MultiCharts-confirmed trade list)")
    out["NQ"] = (tn, eos_split(tn, "NQ", trading_days(gn), nq_rth, adv))
    for sym, g in (("YM", gy), ("ES", ge)):
        tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2018-01-01"]; kr = roll_rows(g, tr); atr = g.daily_atr(15)
        t = same_day(g, sym, tr[kr], -1, jof(831), jof(1000), 0.3 * atr[tr[kr]])
        print(f"\n   {sym} (Python engine, same rules{'; independent check' if sym == 'YM' else '; replication of round 1'})")
        out[sym] = (t, eos_split(t, sym, trading_days(g), nq_rth, adv))
    NVAR["B EOS VIX split"] = 3 * 2
    print("\n   advancing (|t| >= 2.5, same sign both periods): " + (", ".join(adv) if adv else "none"))
    for nm, (t, days) in adv.items(): full_metrics(nm, t, days, nq_rth)
    RES["B"] = out


# =========================================================================================== C
def test_C():
    print("\n" + "=" * 110 + "\nC. Gold: options-expiry pinning fade, LBMA auction limit short")
    import s_rank_gc_round1_test as G
    PV, TICK, COMM = SPEC["GC"]; O, H, L, CF, gc, tr, idx, ND = G.O, G.H, G.L, G.CF, G.gc, G.tr, G.idx, G.ND
    atr = G.ATR_ROW[tr]
    # ---------------------------------------------------------------- expiry days (round-1 code)
    ym = idx.to_period("M"); s = pd.Series(np.arange(ND), index=idx)
    rank_from_end = s.groupby(ym).transform("max").to_numpy() - np.arange(ND)
    complete = ym != ym[-1]                                                                # last month in the data is partial
    OE = np.where((rank_from_end == 3) & complete)[0]
    print(f"   options-expiry days: {len(OE)} ({idx[OE[0]].date()} .. {idx[OE[-1]].date()}); median ATR ${np.nanmedian(atr) * PV:,.0f} per GC")

    def fade_all(k, stm):
        """Expiry-pinning fade on every session; returns DataFrame indexed by position."""
        j_o, j_a, j_b, j_x = jof(721), jof(721), jof(1130), jof(1230); rows = []
        for p in range(ND):
            b = tr[p] * 1440; a_ = atr[p]
            if not np.isfinite(a_) or np.isnan(O[b + j_o]) or G.has_roll(b + j_o - 1, b + j_x): continue
            o0 = O[b + j_o]; cc = CF[b + j_a: b + j_b + 1]
            hit = np.where(np.abs(cc - o0) >= k * a_)[0]
            if not len(hit): continue
            j0 = j_a + hit[0] + 1; s_ = -int(np.sign(cc[hit[0]] - o0))
            if np.isnan(O[b + j0]): continue
            e = O[b + j0] + s_ * TICK; sp = e - s_ * stm * a_; tg = o0
            hh, ll, oo = H[b + j0: b + j_x + 1], L[b + j0: b + j_x + 1], O[b + j0: b + j_x + 1]
            st_hit = (ll <= sp) if s_ > 0 else (hh >= sp)
            tg_hit = (hh >= tg + TICK) if s_ > 0 else (ll <= tg - TICK)
            i_s = np.argmax(st_hit) if st_hit.any() else 10 ** 6; i_t = np.argmax(tg_hit) if tg_hit.any() else 10 ** 6
            if i_s <= i_t and i_s < 10 ** 6:
                o_ = oo[i_s]; px = (sp if (i_s == 0 or np.isnan(o_)) else (min(o_, sp) if s_ > 0 else max(o_, sp))) - s_ * TICK; kd = "stop"
            elif i_t < 10 ** 6:
                o_ = oo[i_t]; px = tg if (i_t == 0 or np.isnan(o_)) else (max(o_, tg) if s_ > 0 else min(o_, tg)); kd = "target"
            else:
                px = CF[b + j_x] - s_ * TICK; kd = "time"
            rows.append(dict(pos=p, date=idx[p], side=s_, net=(px - e) * s_ * PV - COMM, kind=kd, entry_j=j0))
        return pd.DataFrame(rows).set_index("pos")

    print("\n   1. Expiry-pinning fade (enter on the first close >= k ATR from the 7:20 open, 7:21-11:30; target the open; out 12:30)")
    oe_set = set(OE); before, after = set(OE - 1), set(np.minimum(OE + 1, ND - 1))
    other = np.array([p for p in range(ND) if p not in oe_set])
    resF, allF = {}, {}
    for k, stm in itertools.product((0.25, 0.4, 0.6), (0.5, 1.0)):
        A = fade_all(k, stm); allF[(k, stm)] = A
        t = A[A.index.isin(OE)].set_index("date"); resF[(k, stm)] = t
        print(line(t.net, f"expiry day, k {k} ATR, stop {stm} ATR") + f"  [targets {np.mean(A.loc[A.index.isin(OE), 'kind'] == 'target'):.0%}]")
    NVAR["C1 expiry fade"] = len(resF)
    sc = {kk: tstat(v.net[v.index < SPLIT]) for kk, v in resF.items() if (v.index < SPLIT).sum() >= 15}
    kp = max(sc, key=sc.get); A = allF[kp]; tp = resF[kp]
    print(f"   == pick by 2018-22 t -> k {kp[0]}, stop {kp[1]} (design t {sc[kp]:.1f})")
    print(line(tp.net, "picked")); print(line(tp.net[tp.side > 0], "  longs (fade a fall)")); print(line(tp.net[tp.side < 0], "  shorts (fade a rise)")); print(byyear(tp.net))
    print("   placebo at the pick:")
    for nm, pset in (("non-expiry days", set(other)), ("day before expiry", before - oe_set), ("day after expiry", after - oe_set)):
        print(line(A[A.index.isin(list(pset))].set_index("date").net, nm))
    oth = A[~A.index.isin(OE)]; rng = np.random.default_rng(3)
    pm = np.array([oth.net.to_numpy()[rng.choice(len(oth), len(tp), replace=False)].mean() for _ in range(5000)])
    print(f"   random sets of {len(tp)} non-expiry trades: avg ${pm.mean():.0f}, 95th ${np.percentile(pm, 95):.0f}; expiry ${tp.net.mean():.0f}; share >= {np.mean(pm >= tp.net.mean()):.3f}")
    print("   all six cells, expiry minus non-expiry avg $: " + ", ".join(f"k{kk[0]}/s{kk[1]} {resF[kk].net.mean() - allF[kk][~allF[kk].index.isin(OE)].net.mean():+.0f}" for kk in resF))
    adv = {}
    if advances(tp.net): adv["GC expiry-pinning fade"] = tp

    # ---------------------------------------------------------------- LBMA limit short
    print("\n   2. LBMA auction short with a resting limit (ref = close 1 minute before the auction; filled if high >= limit + 1 tick)")
    AM = G.flat_local(10, 30, "Europe/London"); PM = G.flat_local(15, 0, "Europe/London")

    def limit_trades(Aa, k, h, side=-1):
        ref = CF[Aa - 1]; lim = ref - side * k * TICK                        # short: ref + k ticks; long mirror: ref - k ticks
        J = np.arange(h); ii = Aa[:, None] + J[None, :]
        fill = (H[ii] >= lim[:, None] + TICK) if side < 0 else (L[ii] <= lim[:, None] - TICK)
        ok = fill.any(1) & np.isfinite(ref) & ~G.has_roll(Aa - 1, Aa + h) & np.isfinite(CF[Aa + h])
        ex = CF[Aa + h] - side * TICK
        net = (ex - lim) * side * PV - COMM
        tt = pd.DataFrame(dict(side=side, net=net[ok]), index=idx[ok])
        return tt, ok.sum() / np.isfinite(ref).sum()

    resL = {}
    for (an, Aa), k, h in itertools.product((("AM", AM), ("PM", PM)), (1, 2, 3), (10, 20, 30)):
        t, fr = limit_trades(Aa, k, h); resL[(an, k, h)] = t
        print(line(t.net, f"{an} short limit ref+{k} ticks, out +{h} min") + f"  [fill {fr:.0%}]")
    NVAR["C2 LBMA limit short"] = len(resL)
    sc = {kk: tstat(v.net[v.index < SPLIT]) for kk, v in resL.items()}
    kl = max(sc, key=sc.get); tl = resL[kl]; an, k, h = kl; Aa = AM if an == "AM" else PM
    print(f"   == pick by 2018-22 t -> {kl} (design t {sc[kl]:.1f})")
    print(line(tl.net, "picked")); print(byyear(tl.net))
    gross = pd.Series((CF[Aa + h] - CF[Aa - 1]) * -PV, index=idx)
    print(f"   gross short ref -> +{h} min, every day: ${gross.mean():.1f} (t {tstat(gross):.1f}); filled days only (gross from the limit): ${(tl.net + COMM + TICK * PV).mean():.1f}")
    print("   placebo at the pick:")
    for sh in (-120, -60, 60, 120):
        print(line(limit_trades(Aa + sh, k, h)[0].net, f"same rule {sh:+d} min from the auction"))
    print(line(limit_trades(Aa, k, h, side=1)[0].net, "mirror: buy limit ref - k ticks, long"))
    mism = (Aa % 1440) != (jof(430) if an == "AM" else jof(900))
    print(line(tl.net[tl.index.isin(idx[mism])], "DST-mismatch days only (London clock)"))
    tm, _ = limit_trades(Aa - 60, k, h)
    print(line(tm.net[tm.index.isin(idx[mism])], "DST-mismatch days at the usual CT time (placebo)"))
    if advances(tl.net): adv["GC LBMA limit short"] = tl
    print("\n   advancing (|t| >= 2.5, same sign both periods): " + (", ".join(adv) if adv else "none"))
    nq_rth_gc = pd.Series(G.NQ_RTH, index=G.DAYS)
    for nm, t in adv.items(): full_metrics(nm, t, G.DAYS, nq_rth_gc)
    RES["C"] = dict(fade=resF, fade_pick=kp, lbma=resL, lbma_pick=kl, oe=idx[OE])


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    print(__doc__.split("\n")[0])
    gn = pickle.load(open(SP + "g24.pkl", "rb")); ge = pickle.load(open(SP + "ge.pkl", "rb")); gy = pickle.load(open(SP + "gy.pkl", "rb"))
    nq_rth = rth_series(gn, 20.0)
    test_A(gn, ge, nq_rth)
    test_B(gn, ge, gy, nq_rth)
    del ge, gy
    test_C()
    print("\n" + "=" * 110 + f"\nVariants tried: {NVAR} (total {sum(NVAR.values())})")
    pickle.dump(RES, open(SP + "s_rank_misc2.pkl", "wb"))
