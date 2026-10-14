"""S-rank program, ES round 1 (2026-10-14): five forced / scheduled-flow hypotheses on the E-mini S&P (S_RANK_PROGRAM.md).

ES: $50 a point, tick 0.25 ($12.50), $5.00 a round trip + 1 tick per market / stop fill (limit target fills: no tick).
Trade engine as in opex_morning_short_test.py / moc_london_close_test.py: entry at a bar open +/- 1 tick, stop fills at
the stop (on a gap at the bar open) - 1 tick, time exit at a bar close - 1 tick. 2018-2026; parameters picked by
design-period (2018-22) t only; holdout 2023-26 untouched. Advance = |t| >= 2.5 with the same sign in 2018-22 and 2023-26.
Daily P&L series are indexed by every ES trading day from 2018-01-01 (0 with no trade).

1. VIX expiration Wednesday. VIX settles on the special opening quotation (SOQ) of SPX options at the 8:30 CT open on the
   Wednesday 30 days before the next month's 3rd-Friday SPX expiry (that Friday a holiday -> 30 days before the Thursday,
   i.e. a Tuesday; the Wednesday an NYSE holiday -> the day before). Raw 8:30 -> 9:00 / 9:30 / 10:00 / 15:00 moves on VIX
   Wednesdays vs other Wednesdays; trade long / short at the 8:31 open, exits x stops none / 0.3 / 0.5 ATR (24 variants);
   placebos: Wednesdays one week before / after, every other Wednesday, random sets of other Wednesdays.
2. Overnight Bias (Python engine candidates24.overnight_bias24, ADX 20 / 0.30 ATR stop and ADX 30 / 0.25 ATR) on ES with
   the NQ ONB ML recipe (ml_filter_test.py ml6): ridge of the trade's R multiple on 14 price + calendar inputs known
   before the open (2-98% winsorized, lambda = n), standardized; (a) walk-forward, retrained each January from 2019;
   (b) frozen at 2022 (fit 2018-22, applied 2023-26); (c) NQ's frozen PowerLanguage weights on ES inputs (not ES-fitted,
   but NQ's fit saw 2018-26). Skip rule score < 0 (v1) and longs < 0.03 (v2). Variant: + VIX / GEX inputs.
3. SqueezeMetrics GEX regime (data/DIX.csv, prior day's value): negative GEX -> follow the 8:30 -> 10:00 move from the
   10:01 open to 15:00; positive -> fade it. Thresholds 0 / 0.25 / 0.5 ATR x stops none / 0.3 / 0.5 ATR. Controls:
   always follow / always fade (does the regime add?); GEX rank (252-day) < 0.2 as the 'low gamma' regime instead.
   Then GEX (negative / rank below 0.5) as a filter on hypotheses 1, 4, 5.
4. EOS on ES: short the 8:31 open on the monthly roll day (3rd Friday; Thursday when Friday is a holiday), out 10:00,
   stop 0.3 ATR (NQ rules, not refit). Splits (one at a time): prior VIX close above / below its 252-day median;
   GEX rank above / below 0.5. Controls: Fridays one week before / after, other Fridays, the long side.
5. MOC auction follow on ES: after a >= k ATR 14:00 -> 14:50 move, follow at the 14:51 open to the 15:00 close,
   k 0.2 / 0.3 / 0.4 / 0.5, stop none / 0.25 ATR; placebo the same rule on other 10-minute windows; early-close days.
For anything that advances: Sharpe, Sortino, PF, Calmar, Ulcer for whole / longs / shorts, by year, bootstrap +
permutation on 2023+, and the correlation of its daily P&L with ES buy-and-hold over the regular session.
  python3 analysis/s_rank_es_round1_test.py [SCRATCH_DIR]
"""
import sys, pickle, itertools, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from option_income_etf_test import roll_rows, tstat
import metrics as M, resampling as R
import gex_flows as GX

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 50.0, 0.25, 5.0
SPLIT = pd.Timestamp("2023-01-01")
SPX_CLOSED_FRI = pd.to_datetime(["2019-04-19", "2022-04-15", "2025-04-18", "2026-06-19"])   # 3rd Fridays, NYSE shut
NYSE_WED_HOL = pd.to_datetime(["2024-06-19"])                                                # a VIX Wednesday that was a holiday
NVAR = {}                                                                                    # variants tried per hypothesis


def pf(x):
    return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(x, nm, w=62):
    x = pd.Series(x).dropna()
    if len(x) < 6: return f"   {nm:<{w}} n={len(x)}" + (f" avg ${x.mean():.0f}" if len(x) else "")
    y = x.index.year; by = x.groupby(y).sum()
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():5.0f} PF {pf(x):4.2f} t {tstat(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${x[y < 2023].mean():5.0f} (t {tstat(x[y < 2023]):4.1f}) 23-26 ${x[y >= 2023].mean():5.0f} (t {tstat(x[y >= 2023]):4.1f})")


def advances(x):
    x = pd.Series(x).dropna(); a, b = x[x.index < SPLIT].mean(), x[x.index >= SPLIT].mean()
    return len(x) > 10 and abs(tstat(x)) >= 2.5 and np.sign(a) == np.sign(b) == np.sign(x.mean())


def trades(g, rows, sides, j0s, j1, stop_pts):
    """Same-day trades: entry at the open of bar j0 (+/- 1 tick), out at the close of j1 (or the last bar before) or at the stop."""
    O, H, L, C = g.o, g.h, g.l, g.c; out = []
    sides = np.broadcast_to(np.asarray(sides), (len(rows),)); j0s = np.broadcast_to(np.asarray(j0s), (len(rows),))
    stop_pts = np.broadcast_to(np.asarray(stop_pts, float), (len(rows),))
    for d, s, j0, sp_ in zip(rows, sides, j0s, stop_pts):
        if s == 0 or np.isnan(O[d, j0]): continue
        e = O[d, j0] + s * TICK; sp = e - s * sp_ if np.isfinite(sp_) else None; px = None
        if sp is not None:
            seg = L[d, j0:j1 + 1] if s > 0 else H[d, j0:j1 + 1]
            hit = np.where((seg <= sp) if s > 0 else (seg >= sp))[0]
            if len(hit):
                j = j0 + hit[0]; px = (sp if j == j0 else (min(O[d, j], sp) if s > 0 else max(O[d, j], sp))) - s * TICK; jx = j; kind = 0
        if px is None:
            cc = C[d, j0:j1 + 1]; ok = np.where(~np.isnan(cc))[0]
            if not len(ok): continue
            px = cc[ok[-1]] - s * TICK; jx = j0 + ok[-1]; kind = 2
        out.append(dict(day=d, j0=j0, j1=jx, side=s, entry=e, exit=px, kind=kind, date=pd.Timestamp(g.ts[d]), net=(px - e) * s * PV - COMM))
    if not out: return pd.DataFrame(columns=["day", "j0", "j1", "side", "entry", "exit", "kind", "date", "net"]).set_index("date", drop=False)
    return pd.DataFrame(out).set_index("date", drop=False)


def pick(res, label, minn=20):
    sc = {k: tstat(v.net[v.index < SPLIT]) for k, v in res.items() if len(v) > minn}
    k = max(sc, key=sc.get); print(f"\n   == {label}: pick by 2018-22 t -> {k} (design t {sc[k]:.1f}; {len(res)} variants)"); return k


def byyear(x):
    return "   by year: " + " | ".join(f"{y} ${v:,.0f}" for y, v in x.groupby(x.index.year).sum().items())


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "ge.pkl", "rb")); atr_all = g.daily_atr(15)
    tr = g.trading[pd.DatetimeIndex(g.ts[g.trading]) >= "2018-01-01"]; idx = pd.DatetimeIndex(g.ts[tr]); D = len(tr)
    atr = atr_all[tr]; cf = pd.Series(g.c.ravel()).ffill().to_numpy(); P = lambda t: cf[tr * 1440 + jof(t)]
    o831 = g.o[tr, jof(831)]
    full = g.last_j[tr] >= jof(1500)
    days = idx
    dl = lambda x: x.net.groupby(pd.DatetimeIndex(x.date).normalize()).sum().reindex(days, fill_value=0.0)
    bh = pd.Series((P(1500) - o831) * PV, index=idx).fillna(0.0)          # ES buy-and-hold, regular session, per contract
    pos_of = pd.Series(np.arange(D), index=idx)
    # GEX / VIX known before the open
    F = GX.features_for(g).reindex(tr); gex = F.gex.to_numpy(); grank = F.gex_rank.to_numpy()
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE")["CLOSE"]
    vix_prev = vix.shift(1).reindex(idx, method="ffill"); vix_hi = (vix_prev > vix_prev.rolling(252, min_periods=120).median()).to_numpy()
    print(f"ES trading days {idx[0].date()} .. {idx[-1].date()}: {D}; median ATR {np.nanmedian(atr):.1f} pts; negative GEX on {np.mean(gex < 0):.0%} of days")
    CAND = {}                                                               # name -> (trades, placebo note)

    def split_pick(t, label, masks=None):
        """One split at a time (prior-day values); the best half is picked by 2018-22 t and kept only if it advances."""
        if len(t) < 10: return
        k = pos_of.reindex(pd.DatetimeIndex(t.date).normalize()).to_numpy()
        masks = masks or {"GEX negative": gex[k] < 0, "GEX positive": gex[k] >= 0, "GEX rank < 0.5": grank[k] < 0.5, "GEX rank >= 0.5": grank[k] >= 0.5}
        sc = {}
        for nm, m in masks.items():
            print(line(t.net[m], f"{label}: {nm}"))
            x = t.net[m]; xd = x[x.index < SPLIT]
            if len(xd) >= 10: sc[nm] = tstat(xd)
        if sc:
            b = max(sc, key=sc.get); x = t[masks[b]]
            print(f"      -> design-t pick: {b} (t {sc[b]:.1f}); {'ADVANCES' if advances(x.net) else 'does not advance'}")
            if advances(x.net): CAND[f"{label} | {b}"] = x

    # =================================================== 1. VIX expiration Wednesday
    print("\n" + "=" * 100 + "\n1. VIX expiration Wednesday (SOQ at the 8:30 CT open)")
    tset = set(idx)
    vx = []
    for y, m in itertools.product(range(2018, 2027), range(1, 13)):
        y2, m2 = (y, m + 1) if m < 12 else (y + 1, 1)
        fr = pd.date_range(pd.Timestamp(y2, m2, 1), periods=31, freq="D"); fr = fr[(fr.month == m2) & (fr.dayofweek == 4)]; f3 = fr[2]
        if f3 in SPX_CLOSED_FRI: f3 = f3 - pd.Timedelta(days=1)
        v = f3 - pd.Timedelta(days=30)
        while v in NYSE_WED_HOL or (v not in tset and v <= idx[-1] and v >= idx[0]): v = v - pd.Timedelta(days=1)
        if idx[0] <= v <= idx[-1]: vx.append(v)
    vx = pd.DatetimeIndex(vx); kv = pos_of.reindex(vx).dropna().astype(int).to_numpy()
    print(f"   VIX expiry days: {len(kv)} ({(vx.dayofweek != 2).sum()} not Wednesdays: {', '.join(str(d.date()) for d in vx[vx.dayofweek != 2])})")
    wed = np.where(idx.dayofweek == 2)[0]; other_wed = np.setdiff1d(wed, kv)
    shift = lambda k, w: pos_of.reindex(idx[k] + pd.Timedelta(days=7 * w)).dropna().astype(int).to_numpy()
    print("   raw moves from the 8:30 open, $ per ES before costs (avg, t) and |move| / ATR:")
    for nm, k in (("VIX expiry", kv), ("week before", shift(kv, -1)), ("week after", shift(kv, 1)), ("other Wednesdays", other_wed)):
        s = []
        for T_ in (900, 930, 1000, 1500):
            x = pd.Series((P(T_)[k] - o831[k]) * PV, index=idx[k]).dropna(); s.append(f"{T_}: ${x.mean():5.0f} (t {tstat(x):4.1f}; |.|/ATR {np.nanmean(np.abs(P(T_)[k] - o831[k]) / atr[k]):.2f})")
        print(f"   {nm:<18} n={len(k):4d}  " + "  ".join(s))
    for nm, k in (("VIX expiry", kv), ("other Wednesdays", other_wed)):
        x = pd.Series((P(1000)[k] - o831[k]) * PV, index=idx[k]).dropna()
        print(f"   8:30->10:00 {nm:<17} 18-22 ${x[x.index < SPLIT].mean():5.0f} (t {tstat(x[x.index < SPLIT]):4.1f}) | 23-26 ${x[x.index >= SPLIT].mean():5.0f} (t {tstat(x[x.index >= SPLIT]):4.1f})")
    res1 = {}
    for s, ex, st in itertools.product((1, -1), (900, 930, 1000, 1500), (None, 0.3, 0.5)):
        res1[(s, ex, st)] = trades(g, tr[kv], s, jof(831), jof(ex), st * atr[kv] if st else np.inf)
    for kk, t in res1.items(): print(line(t.net, f"{'long ' if kk[0] > 0 else 'short'} 8:31, out {kk[1]}, stop {kk[2] if kk[2] else 'none'}"))
    NVAR["1 VIX Wednesday"] = len(res1)
    k1 = pick(res1, "VIX Wednesday"); s1, ex1, st1 = k1; t1 = res1[k1]
    print(line(t1.net, "picked")); print(byyear(t1.net))
    stp = lambda k: st1 * atr[k] if st1 else np.inf
    print("   controls at the pick:")
    for nm, k in (("Wednesday one week BEFORE", shift(kv, -1)), ("Wednesday one week AFTER", shift(kv, 1)), ("every other Wednesday", other_wed),
                  ("Tuesday before VIX expiry", np.clip(kv - 1, 0, None)), ("Thursday after VIX expiry", np.clip(kv + 1, 0, D - 1))):
        print(line(trades(g, tr[k], s1, jof(831), jof(ex1), stp(k)).net, nm))
    print(line(trades(g, tr[kv], -s1, jof(831), jof(ex1), stp(kv)).net, "opposite side, VIX expiry"))
    raw = (P(ex1) - o831) * s1 * PV - COMM - 2 * TICK * PV; rnd = np.random.default_rng(1)
    pm = np.array([np.nanmean(raw[rnd.choice(other_wed, len(kv), replace=False)]) for _ in range(3000)])
    print(f"   random sets of {len(kv)} other Wednesdays (no stop, same side / exit): avg ${pm.mean():.0f}, 95th pct ${np.percentile(pm, 95):.0f}; "
          f"VIX days no stop ${np.nanmean(raw[kv]):.0f}; share >= it {np.mean(pm >= np.nanmean(raw[kv])):.3f}")
    if advances(t1.net): CAND["VIX Wednesday"] = t1

    # =================================================== 2. Overnight Bias with an ES-trained ML filter
    print("\n" + "=" * 100 + "\n2. Overnight Bias on ES with an ES-trained ridge filter (NQ ONB ML recipe)")
    from candidates24 import overnight_bias24
    cl = pd.Series(P(1500), index=idx); op = pd.Series(o831, index=idx); r1 = np.log(cl).diff()
    atr_s = pd.Series(atr, index=idx)
    X = pd.DataFrame(index=idx)
    X["ret1"] = r1.shift(1); X["ret5"] = np.log(cl).diff(5).shift(1); X["ret20"] = np.log(cl).diff(20).shift(1)
    X["rth1"] = np.log(cl / op).shift(1); X["atr_ratio"] = atr_s / atr_s.rolling(60).mean()
    X["dist50"] = np.log(cl / cl.rolling(50).mean()).shift(1); X["rv5_rv20"] = (r1.rolling(5).std() / r1.rolling(20).std()).shift(1)
    for k in range(5): X[f"dow{k}"] = (idx.dayofweek == k).astype(float)
    X["tdm"] = (pd.Series(1, index=idx).groupby(idx.year * 100 + idx.month).cumcount() + 1 <= 3).astype(float)
    fri_dom = idx.day + (4 - idx.dayofweek); X["opex_wk"] = ((fri_dom >= 15) & (fri_dom <= 21)).astype(float)
    COLS = list(X.columns)
    X["vix"] = vix_prev.to_numpy(); X["gex_rank"] = grank
    X = X.fillna(X.median())
    NQW = dict(ret1=2.550842376, ret5=0.05697325462, ret20=-0.08269967616, rth1=1.729498386, atr_ratio=-0.03608247696, dist50=-0.3355796551,
               rv5_rv20=-0.03976333906, dow0=0.07809504609, dow1=-0.008560935801, dow2=-0.02267574106, dow3=-0.03459885088, dow4=-0.005544247888,
               tdm=0.1654566373, opex_wk=-0.003794081905)
    nq_score = pd.Series(0.05535517974 + X[COLS].to_numpy() @ np.array([NQW[c] for c in COLS]), index=idx)

    def onb(adx_min, stop_atr):
        t = overnight_bias24(g, adx_min=adx_min, stop_atr=stop_atr).copy()
        t["date"] = pd.to_datetime(t.date); t = t[t.date >= "2018-01-01"]
        t["net"] = (t.exit - t.entry) * t.side * PV - COMM - TICK * PV * (1 + (t.kind != 1))   # stop entry 1 tick; stop / time exit 1 tick
        t["R"] = t.net / (stop_atr * atr_all[t.day.to_numpy()] * PV)
        return t.set_index("date", drop=False)

    def ridge(Xt, b):
        mu, sd = Xt.mean(), Xt.std().replace(0, 1); A = ((Xt - mu) / sd).to_numpy(); b = b.to_numpy()
        lo, hi = np.percentile(b, [2, 98]); b = np.clip(b, lo, hi); b = b - b.mean()
        w = np.linalg.solve(A.T @ A + len(b) * np.eye(A.shape[1]), A.T @ b)
        return lambda Z: ((Z - mu) / sd).to_numpy() @ w

    res2 = {}
    for (adx_min, stop_atr) in ((20, 0.30), (30, 0.25)):
        t = onb(adx_min, stop_atr); nm0 = f"ONB ADX{adx_min}"; Xt = X.reindex(t.index); yr = t.index.year
        print(f"\n   {nm0} (stop {stop_atr} ATR, 3R target, out 14:30)")
        print(line(t.net, f"{nm0} plain")); print(line(t.net[t.side > 0], "  longs")); print(line(t.net[t.side < 0], "  shorts"))
        res2[(nm0, "plain")] = t
        for cols_nm, cols in (("price+calendar", COLS), ("+VIX/GEX", COLS + ["vix", "gex_rank"])):
            wf = pd.Series(np.nan, index=t.index)
            for Y in range(2019, 2027):
                trn, tst = yr < Y, yr == Y
                if tst.sum(): wf[tst] = ridge(Xt.loc[trn, cols], t.R[trn])(Xt.loc[tst, cols])
            fz = pd.Series(np.nan, index=t.index); fz[yr >= 2023] = ridge(Xt.loc[yr < 2023, cols], t.R[yr < 2023])(Xt.loc[yr >= 2023, cols])
            sc_list = [("walk-forward", wf), ("frozen at 2022", fz)] + ([("NQ frozen weights", nq_score.reindex(t.index))] if cols_nm == "price+calendar" else [])
            for sc_nm, sc in sc_list:
                for thr_nm, lthr in (("v1 >= 0", 0.0), ("v2 longs >= 0.03", 0.03)):
                    ok = sc.notna(); keep = ok & (sc >= np.where(t.side > 0, lthr, 0.0)); skip = ok & ~keep
                    kk = t[keep]; res2[(nm0, cols_nm, sc_nm, thr_nm)] = kk
                    yk, ys = t.net[keep].groupby(yr[keep]).mean(), t.net[skip].groupby(yr[skip]).mean()
                    better = (yk > ys.reindex(yk.index)).sum()
                    print(line(kk.net, f"{cols_nm:<14} {sc_nm:<17} {thr_nm:<16} kept") +
                          f" | skipped n={skip.sum()} ${t.net[skip].mean():.0f}; yrs kept>skipped {better}/{len(yk)}")
    NVAR["2 ONB ML"] = len(res2)
    # pick by design-period t of the kept trades among the ES-fitted walk-forward filters (2019-22 is out of sample for each year)
    sc2 = {k: tstat(v.net[v.index < SPLIT]) for k, v in res2.items() if len(k) == 4 and k[2] == "walk-forward"}
    k2 = max(sc2, key=sc2.get); t2 = res2[k2]
    print(f"\n   == ONB ML on ES: pick by 2019-22 walk-forward t -> {k2} (t {sc2[k2]:.1f})")
    print(line(t2.net, "picked")); print(line(t2.net[t2.side > 0], "  longs")); print(line(t2.net[t2.side < 0], "  shorts")); print(byyear(t2.net))
    base2 = res2[(k2[0], "plain")]; b19 = base2[base2.index.year >= 2019]
    rnd = np.random.default_rng(2); keep_share = len(t2) / len(b19)
    pr = np.array([b19.net[rnd.random(len(b19)) < keep_share].mean() for _ in range(3000)])
    print(f"   placebo: keep {keep_share:.0%} of the 2019+ plain trades at random: avg ${pr.mean():.0f}, 95th pct ${np.percentile(pr, 95):.0f}; filter ${t2.net.mean():.0f}; share >= {np.mean(pr >= t2.net.mean()):.3f}")
    for k_ in (("ONB ADX20", "plain"), ("ONB ADX30", "plain"), k2):
        if advances(res2[k_].net): CAND[" / ".join(k_)] = res2[k_]

    # =================================================== 3. GEX regime: follow / fade the morning
    print("\n" + "=" * 100 + "\n3. GEX regime (prior day): negative -> follow 8:30->10:00 from 10:01 to 15:00; positive -> fade")
    mv = P(1000) - o831; ok = full & (mv != 0) & ~np.isnan(gex) & ~np.isnan(mv)
    res3 = {}
    for reg, th, st in itertools.product(("GEX<0", "rank<0.2"), (0.0, 0.25, 0.5), (None, 0.3, 0.5)):
        low = (gex < 0) if reg == "GEX<0" else (grank < 0.2)
        m = ok & (np.abs(mv) >= th * atr); sd = (np.sign(mv) * np.where(low, 1, -1)).astype(int)
        t = trades(g, tr[m], sd[m], jof(1001), jof(1500), st * atr[m] if st else np.inf)
        k_ = pos_of.reindex(pd.DatetimeIndex(t.date).normalize()).to_numpy(); t["low"] = low[k_]
        res3[(reg, th, st)] = t
        print(line(t.net, f"{reg:<8} |move| >= {th} ATR, stop {st if st else 'none'}: both") + f"\n{line(t.net[t.low], '     low-gamma follow')}\n{line(t.net[~t.low], '     high-gamma fade')}")
    NVAR["3 GEX regime"] = len(res3) * 3
    k3 = pick(res3, "GEX regime (combined)"); t3 = res3[k3]
    print(line(t3.net, "picked")); print(line(t3.net[t3.low], "  low-gamma follow part")); print(line(t3.net[~t3.low], "  high-gamma fade part")); print(byyear(t3.net))
    reg, th3, st3 = k3; m = ok & (np.abs(mv) >= th3 * atr)
    for nm, sd in (("control: always follow", np.sign(mv)), ("control: always fade", -np.sign(mv))):
        print(line(trades(g, tr[m], sd[m].astype(int), jof(1001), jof(1500), st3 * atr[m] if st3 else np.inf).net, nm))
    k3l = max(((a, b, c) for a, b, c in res3), key=lambda k_: tstat(res3[k_].net[res3[k_].low & (res3[k_].index < SPLIT)]))
    k3h = max(((a, b, c) for a, b, c in res3), key=lambda k_: tstat(res3[k_].net[~res3[k_].low & (res3[k_].index < SPLIT)]))
    print(f"   best low-gamma follow by design t {k3l}:"); print(line(res3[k3l].net[res3[k3l].low], "  low-gamma follow"))
    print(f"   best high-gamma fade by design t {k3h}:"); print(line(res3[k3h].net[~res3[k3h].low], "  high-gamma fade"))
    if advances(t3.net): CAND["GEX regime"] = t3
    if advances(res3[k3l].net[res3[k3l].low]): CAND["GEX low-gamma follow"] = res3[k3l][res3[k3l].low]
    if advances(res3[k3h].net[~res3[k3h].low]): CAND["GEX high-gamma fade"] = res3[k3h][~res3[k3h].low]

    # =================================================== 4. EOS on ES
    print("\n" + "=" * 100 + "\n4. EOS on ES: short the 8:31 open on the monthly roll day, out 10:00, stop 0.3 ATR (NQ rules)")
    kr = roll_rows(g, tr); fri = np.where(idx.dayofweek == 4)[0]; other_fri = np.setdiff1d(fri, kr)
    eos = lambda k, s=-1, ex=1000, st=0.3: trades(g, tr[k], s, jof(831), jof(ex), st * atr[k] if st else np.inf)
    t4 = eos(kr); print(line(t4.net, "EOS ES (short 8:31 -> 10:00, stop 0.3 ATR)")); print(byyear(t4.net))
    for ex, st in ((1000, None), (1000, 0.5), (1030, 0.3), (1100, 0.3)): print(line(eos(kr, ex=ex, st=st).net, f"  sensitivity: out {ex}, stop {st if st else 'none'}"))
    print("   controls:")
    for nm, k in (("Friday one week BEFORE", shift(kr, -1)), ("Friday one week AFTER", shift(kr, 1)), ("every other Friday", other_fri)):
        print(line(eos(k).net, nm))
    print(line(eos(kr, s=1).net, "long side, same day / exit / stop"))
    raw4 = (P(1000) - o831) * -PV - COMM - 2 * TICK * PV; rnd = np.random.default_rng(4)
    pm4 = np.array([np.nanmean(raw4[rnd.choice(other_fri, len(kr), replace=False)]) for _ in range(3000)])
    print(f"   random sets of {len(kr)} other Fridays (no stop): avg ${pm4.mean():.0f}, 95th ${np.percentile(pm4, 95):.0f}; roll days no stop ${np.nanmean(raw4[kr]):.0f}; share >= {np.mean(pm4 >= np.nanmean(raw4[kr])):.3f}")
    print("   splits (one at a time; prior-day values):")
    k4 = pos_of.reindex(pd.DatetimeIndex(t4.date).normalize()).to_numpy()
    split_pick(t4, "4 EOS ES", {"VIX above its 252-day median": vix_hi[k4], "VIX below its 252-day median": ~vix_hi[k4], "GEX rank >= 0.5": grank[k4] >= 0.5,
                                "GEX rank < 0.5": grank[k4] < 0.5, "GEX negative": gex[k4] < 0, "GEX positive": gex[k4] >= 0})
    NVAR["4 EOS"] = 1 + 4 + 6
    if advances(t4.net): CAND["EOS ES"] = t4

    # =================================================== 5. MOC auction follow on ES
    print("\n" + "=" * 100 + "\n5. MOC auction follow on ES: sign(14:00 -> 14:50) at the 14:51 open, out at the 15:00 close")
    mv5 = P(1450) - P(1400); res5 = {}
    for th, st in itertools.product((0.2, 0.3, 0.4, 0.5), (None, 0.25)):
        m = full & (np.abs(mv5) >= th * atr) & (mv5 != 0)
        res5[(th, st)] = t = trades(g, tr[m], np.sign(mv5[m]).astype(int), jof(1451), jof(1500), st * atr[m] if st else np.inf)
        print(line(t.net, f"|14:00->14:50| >= {th} ATR, stop {st if st else 'none'}"))
    NVAR["5 MOC"] = len(res5)
    k5 = pick(res5, "MOC"); t5 = res5[k5]; th5, st5 = k5
    print(line(t5.net, "picked")); print(line(t5.net[t5.side > 0], "  longs")); print(line(t5.net[t5.side < 0], "  shorts")); print(byyear(t5.net))
    raw5 = pd.Series(np.where(np.abs(mv5) >= th5 * atr, np.sign(mv5) * (P(1500) - P(1450)) * PV, np.nan), index=idx)
    print(f"   before costs (14:50 close -> 15:00 close): ${raw5.mean():.1f}, t {tstat(raw5):.1f}")
    print("   placebo: the same rule decided at other times (50-minute move, then the next 10 minutes):")
    for dec in (1050, 1150, 1250, 1320, 1350, 1420, 1450):
        jd = jof(dec); mvp = cf[tr * 1440 + jd] - cf[tr * 1440 + jd - 50]; m = full & (np.abs(mvp) >= th5 * atr) & (mvp != 0)
        tp = trades(g, tr[m], np.sign(mvp[m]).astype(int), jd + 1, jd + 10, st5 * atr[m] if st5 else np.inf)
        print(line(tp.net, f"   decide {dec}"))
    x5 = t5.net; print(line(x5[x5.index.year != 2020], "picked without 2020")); print(line(x5.sort_values().iloc[:-5].sort_index(), "picked without its best 5 trades"))
    k5d = pos_of.reindex(pd.DatetimeIndex(t5.date).normalize()).to_numpy(); raw5t = (P(1500)[k5d] - P(1450)[k5d]) * PV; rnd = np.random.default_rng(5)
    pm5 = np.array([np.mean(raw5t * rnd.choice((-1, 1), len(k5d))) for _ in range(3000)])
    print(f"   random direction on the same {len(k5d)} days (14:50 -> 15:00, before costs): 95th pct ${np.percentile(pm5, 95):.0f}, 99th ${np.percentile(pm5, 99):.0f}; "
          f"rule ${np.mean(raw5t * t5.side.to_numpy()):.0f}; share >= {np.mean(pm5 >= np.mean(raw5t * t5.side.to_numpy())):.4f}")
    for ent in (1446, 1451, 1452, 1453):
        dec = ent - 1; jd = jof(dec); mvp = cf[tr * 1440 + jd] - P(1400); m = full & (np.abs(mvp) >= th5 * atr) & (mvp != 0)
        print(line(trades(g, tr[m], np.sign(mvp[m]).astype(int), jof(ent), jof(1500), st5 * atr[m] if st5 else np.inf).net, f"   entry timing: decide at {dec}, enter {ent} open"))
    ec = ~full & (g.last_j[tr] >= jof(1159)); mve = P(1150) - P(1100); m = ec & (mve != 0)
    te = trades(g, tr[m], np.sign(mve[m]).astype(int), jof(1151), jof(1200), np.inf)
    print(f"   early-close days (auction 11:50-12:00 CT): {len(te)} trades avg ${te.net.mean() if len(te) else np.nan:.0f}")
    if advances(t5.net): CAND["MOC follow ES"] = t5

    # =================================================== GEX as a filter on 1 / 4 / 5
    print("\n" + "=" * 100 + "\nGEX (prior day) as a filter on hypotheses 1, 4, 5 (at their picked / fixed settings)")
    split_pick(t1, "1 VIX Wed"); split_pick(t5, "5 MOC ES"); print("   (4 EOS: GEX / VIX splits in section 4)")
    NVAR["GEX filters"] = 8

    # =================================================== candidates
    print("\n" + "=" * 100 + f"\nVariants tried: {NVAR} (total {sum(NVAR.values())})")
    print("Advancing (|t| >= 2.5, same sign 2018-22 and 2023-26): " + (", ".join(CAND) if CAND else "none"))
    for nm, t in CAND.items():
        print(f"\n--- {nm}")
        print(line(t.net, "all")); print(line(t.net[t.side > 0], "longs")); print(line(t.net[t.side < 0], "shorts")); print(byyear(t.net))
        rows = {nm: (dl(t), t.net), "  longs": (dl(t[t.side > 0]), t.net[t.side > 0]), "  shorts": (dl(t[t.side < 0]), t.net[t.side < 0])}
        rows = {k_: v for k_, v in rows.items() if len(v[1])}
        rows["  2023+"] = (dl(t)[days >= SPLIT], t.net[t.index >= SPLIT])
        print(M.table(rows))
        rr = {f"{nm}, 2023+": dl(t)[days >= SPLIT]}
        for sn, s in (("longs", 1), ("shorts", -1)):
            if (t.side == s).sum() > 20: rr[f"  {sn}, 2023+"] = dl(t[t.side == s])[days >= SPLIT]
        b_, p_ = R.report(rr, n=3000); print(b_); print(p_)
        d_ = dl(t); print(f"   daily P&L correlation with ES buy-and-hold 8:30-15:00: all days {np.corrcoef(d_, bh)[0, 1]:.2f}; "
                          f"trade days {np.corrcoef(d_[d_ != 0], bh[d_ != 0])[0, 1]:.2f}")
        per_year = t.net.groupby(t.index.year).sum(); px = pd.Series(P(1500), index=idx).groupby(idx.year).mean() * PV
        print(f"   profit a year per ES ${t.net.sum() / (len(days) / 252):,.0f} vs ~5% of notional ${0.05 * px.mean():,.0f}")
    pickle.dump(dict(vix_wed=res1, pick1=k1, onb=res2, pick2=k2, gex=res3, pick3=k3, eos=t4, moc=res5, pick5=k5, cand=CAND),
                open(SP + "s_rank_es.pkl", "wb"))
