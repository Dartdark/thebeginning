"""CME MBO order flow from The Bridge (exported with multi_strategy/OFB_OrderFlow_Exporter.txt) on NQ, 2026-10-13.

Data: OF_1min_<year>_<part>.csv (repo root), 1-minute RTH bars 9:30-16:15 ET = 8:30-15:15 CT, 2018-01-02 ..
2026-07-07 (2,197 sessions). The Bridge's closes match the NQ grid on 96.8% of minutes (ET -> CT = -1 hour).
Column notes found by checking: MultiCharts' Volume returned the BUY volume (volume = upvol = aggressive buys),
downvol = aggressive sells, buys + sells = the grid's volume (97% within 5%); d(cum_delta) = buys - sells
(corr 0.995) but cum_delta does not reset at the RTH open, so RTH delta is rebuilt here. Slots: s48/49, s50/51,
s52/53 = bid/ask size over 10/20/50 levels; s54-57 = bid walls 1-2 (price, size), s58-61 = ask walls 1-2.

1. Do order-flow numbers predict the next 5 / 15 / 30 minutes? Correlation of each feature with the next move
   (non-overlapping samples 9:00-14:30 CT), by year, design 2018-2022 vs holdout 2023-2026.
2. Opening flow: does the 8:30-9:00 / 8:30-9:30 CT delta predict the rest of the day beyond the price move?
3. Big prints (|largest trade| >= 99.5th percentile of the prior 20 sessions): follow for 15 / 30 / 60 minutes.
4. The plan's MultiCharts trades split by whether order flow agrees with the trade at entry (each side).
5. Trades for anything that clears the design period, tested on the holdout, with placebo and metrics.
Costs: $7.25 per NQ + 1 tick per market fill (entry next bar open, exit at a bar close).
  python3 analysis/orderflow_test.py [SCRATCH_DIR]
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from funded_lab import with_slippage
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
SPLIT = pd.Timestamp("2023-01-01")
REPORTS = {
    "VB": "mc_reports/Backtesting Strategy Performance Report VB v1.xlsx",
    "ONB_ML2": "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx",
    "EOS": "mc_reports/Backtesting Strategy Performance Report EOS v1.xlsx",
    "MON": "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx",
    "LDF": "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx",
    "NFP": "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes NFP Fade.xlsx",
    "VCS": "mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Vol-Control Sell Flow.xlsx",
    "ONB_ADX30 (combine)": "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx",
}
COLS = {"buy": "volume", "sell": "downvol", "simb": "size_imb", "cimb": "count_imb", "qdb": "qdepl_bid",
        "qda": "qdepl_ask", "plb": "pulled_bid", "pla": "pulled_ask", "icb": "ice_bid", "ica": "ice_ask",
        "big": "big_trade", "b10": "s48", "a10": "s49", "b50": "s52", "a50": "s53", "wbs": "s55", "was": "s59",
        "wbp": "s54", "wap": "s58", "vwap": "vwap"}


def load_of(g):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/OF_1min_*.csv"))], ignore_index=True)
    row = np.minimum(np.searchsorted(g.dates, d.date.values), g.D - 1)
    ok = g.dates[row] == d.date.values
    d, row = d[ok], row[ok]
    col = jof(d.time.values - 100)
    A = {}
    for k, c in COLS.items():
        a = np.full((g.D, 1440), np.nan); a[row, col] = d[c].to_numpy(float); A[k] = a
    A["delta"] = A["buy"] - A["sell"]; A["tot"] = A["buy"] + A["sell"]
    A["has"] = ~np.isnan(A["buy"])
    return A


def wsum(a, d, j0, j1):
    return np.nansum(a[d, j0:j1 + 1])


def last_c(g, d, j):
    r = g.c[d, :j + 1]; ok = np.flatnonzero(~np.isnan(r))
    return r[ok[-1]] if len(ok) else np.nan


def trade(g, d, j_in, side, j_out, stop=None):
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


def stat(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if len(x) < 3: return f"n={len(x):5d}"
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return f"n={len(x):5d} avg ${x.mean():5.0f} t={x.mean() / x.std() * np.sqrt(len(x)):4.1f} win {np.mean(x > 0):.0%} PF {pf:.2f}"


def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan
    return (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))


def ratio(a, b):
    with np.errstate(all="ignore"):
        return np.where((a + b) > 0, (a - b) / (a + b), np.nan)


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    A = load_of(g); ts = pd.DatetimeIndex(g.ts)
    days = [d for d in g.trading if A["has"][d, jof(831):jof(1500)].sum() > 300]
    yr = {d: ts[d].year for d in days}
    print(__doc__.split("\n")[0]); print(f"sessions: {len(days)} ({ts[days[0]].date()} .. {ts[days[-1]].date()})")
    atr = g.daily_atr(15)

    # ---------------- 1. predictive correlations ----------------
    print("\n1. Correlation of each feature with the next H minutes (points), non-overlapping samples 9:00-14:30 CT.")
    print("   'same' = correlation with the move over the same window (how much the feature describes, not predicts).")
    FEAT = ["delta_5", "delta_15", "delta_30", "rth_delta", "size_imb", "count_imb", "depth10", "depth50",
            "pulled", "qdepl", "iceberg", "big_15", "wall_sz"]
    res = []
    for H in (5, 15, 30):
        rows = []
        for d in days:
            for j in range(jof(900), jof(1430) + 1, H):
                c0, cf = last_c(g, d, j), last_c(g, d, j + H)
                if np.isnan(c0) or np.isnan(cf) or not A["has"][d, j]: continue
                f = {}
                for n in (5, 15, 30):
                    f[f"delta_{n}"] = wsum(A["delta"], d, j - n + 1, j) / max(1, wsum(A["tot"], d, j - n + 1, j))
                f["rth_delta"] = wsum(A["delta"], d, jof(831), j) / max(1, wsum(A["tot"], d, jof(831), j))
                f["size_imb"], f["count_imb"] = A["simb"][d, j], A["cimb"][d, j]
                f["depth10"] = ratio(A["b10"][d, j], A["a10"][d, j]); f["depth50"] = ratio(A["b50"][d, j], A["a50"][d, j])
                # pulled / depleted bids are bearish: sign so that + = bullish
                f["pulled"] = -ratio(np.nanmean(A["plb"][d, j - 4:j + 1]), np.nanmean(A["pla"][d, j - 4:j + 1]))
                f["qdepl"] = -ratio(np.nanmean(A["qdb"][d, j - 4:j + 1]), np.nanmean(A["qda"][d, j - 4:j + 1]))
                f["iceberg"] = ratio(wsum(A["icb"], d, j - 14, j), wsum(A["ica"], d, j - 14, j))
                f["big_15"] = np.nansum(np.sign(A["big"][d, j - 14:j + 1]) * np.abs(A["big"][d, j - 14:j + 1]))
                f["wall_sz"] = ratio(A["wbs"][d, j], A["was"][d, j])
                cp = last_c(g, d, j - H)
                rows.append(dict(d=d, j=j, y=yr[d], fwd=cf - c0, past=c0 - cp if not np.isnan(cp) else np.nan,
                                 **{k: float(v) for k, v in f.items()}))
        S = pd.DataFrame(rows)
        for k in FEAT:
            q = S[[k, "fwd", "past", "y"]].replace([np.inf, -np.inf], np.nan).dropna()
            ic = lambda z: np.corrcoef(z[k], z["fwd"])[0, 1]
            byy = q.groupby("y").apply(ic)
            dsg, hol = q[q.y < 2023], q[q.y >= 2023]
            res.append(dict(H=H, feat=k, ic=ic(q), t=ic(q) * np.sqrt(len(q)), design=ic(dsg), holdout=ic(hol),
                            same=np.corrcoef(q[k], q["past"])[0, 1] if H <= 30 else np.nan,
                            yrs_pos=int((byy > 0).sum()), n=len(q)))
        if H == 15: S15 = S
    IC = pd.DataFrame(res)
    print(IC.to_string(index=False, float_format=lambda v: f"{v:+.3f}"))
    print("   (|corr| 0.02 on 15 minutes ~ 0.3 points of edge a trade vs ~0.9 points of costs; t uses n non-overlapping samples)")

    # ---------------- 2. opening flow ----------------
    print("\n2. Opening flow: at 9:01 / 9:31 CT trade the sign of the RTH delta (or of the price move), out 14:55 CT, stop 0.5 ATR:")
    rows = []
    for d in days:
        if np.isnan(atr[d]): continue
        o = g.o[d, jof(831)]
        for end in (900, 930):
            c0 = last_c(g, d, jof(end)); dl = wsum(A["delta"], d, jof(831), jof(end)); tv = wsum(A["tot"], d, jof(831), jof(end))
            if np.isnan(o) or np.isnan(c0) or tv == 0: continue
            pm, dm = int(np.sign(c0 - o)), int(np.sign(dl))
            for nm, side in (("delta", dm), ("price", pm)):
                if side == 0: continue
                x = trade(g, d, jof(end) + 1, side, jof(1455), c0 - side * 0.5 * atr[d])
                if x is not None: rows.append(dict(date=ts[d], end=end, sig=nm, side=side, agree=pm == dm, dn=dl / tv, net=x))
    OP = pd.DataFrame(rows)
    for end in (900, 930):
        for nm in ("delta", "price"):
            q = OP[(OP.end == end) & (OP.sig == nm)]
            print(f"   {end} {nm:<5} all {stat(q.net)} | 18-22 ${q[q.date < SPLIT].net.mean():5.0f} 23-26 ${q[q.date >= SPLIT].net.mean():5.0f}")
        q = OP[(OP.end == end) & (OP.sig == "delta")]
        print(f"        delta and price agree {stat(q[q.agree].net)} | disagree (delta's side) {stat(q[~q.agree].net)}")
    OP["date"] = pd.to_datetime(OP.date)

    # ---------------- 3. big prints ----------------
    print("\n3. Big prints: |largest trade in the minute| >= 99.5th percentile of the prior 20 sessions, 9:00-14:00 CT;"
          " follow its side from the next bar (first one per hour per day):")
    thr = {}
    hist = []
    for d in days:
        if len(hist) >= 20: thr[d] = np.nanpercentile(np.concatenate(hist[-20:]), 99.5)
        hist.append(np.abs(A["big"][d, jof(831):jof(1500) + 1]))
    rows = []
    for d in days:
        if d not in thr: continue
        last_h = -1
        for j in range(jof(900), jof(1400) + 1):
            b = A["big"][d, j]
            if np.isnan(b) or abs(b) < thr[d] or j // 60 == last_h: continue
            last_h = j // 60; side = int(np.sign(b))
            for H in (15, 30, 60):
                x = trade(g, d, j + 1, side, j + H)
                if x is not None: rows.append(dict(date=ts[d], H=H, side=side, net=x, size=abs(b)))
    BP = pd.DataFrame(rows)
    for H in (15, 30, 60):
        q = BP[BP.H == H]
        print(f"   follow {H:2d} min: {stat(q.net)} | 18-22 ${q[q.date < SPLIT].net.mean():5.0f} 23-26 ${q[q.date >= SPLIT].net.mean():5.0f}"
              f" | buys ${q[q.side > 0].net.mean():4.0f} sells ${q[q.side < 0].net.mean():4.0f}")

    # ---------------- 4. plan trades vs order flow at entry ----------------
    print("\n4. The plan's MultiCharts trades: does order flow agree with the trade at entry? (per NQ, +1 tick slippage)")
    print("   agree = sign of the RTH delta so far (entries after 8:45 CT) or of the previous session's RTH delta (earlier entries)"
          " equals the trade side; last30 = the last 30 minutes' delta instead")
    for nm, f in REPORTS.items():
        t = with_slippage(load_mc(g, f)); t["net"] = (t.exit - t.entry) * t.side * PV - COST
        t = t[t.date >= "2018-01-02"].reset_index(drop=True)
        ag, ag30 = [], []
        for r in t.itertuples():
            d, j = int(r.day), int(r.j0) - 1
            if jof(845) <= j <= jof(1515) and A["has"][d].any():
                dl = wsum(A["delta"], d, jof(831), j); d30 = wsum(A["delta"], d, j - 29, j)
            else:
                k = np.searchsorted(g.trading, d) - (0 if j > jof(1515) else 1); p = g.trading[k]
                dl = wsum(A["delta"], p, jof(831), jof(1515)); d30 = wsum(A["delta"], p, jof(1446), jof(1515))
            ag.append(np.nan if dl == 0 else float(np.sign(dl) == r.side)); ag30.append(np.nan if d30 == 0 else float(np.sign(d30) == r.side))
        t["agree"], t["agree30"] = ag, ag30
        print(f"   {nm}:")
        for sd, snm in ((0, "both"), (1, "longs"), (-1, "shorts")):
            q = t if sd == 0 else t[t.side == sd]
            if len(q) < 20 or (sd != 0 and len(q) == len(t)): continue
            for col in ("agree", "agree30"):
                a, b = q[q[col] == 1].net, q[q[col] == 0].net
                per = " ".join(f"{p_} ${q[(q[col] == 1) & m].net.mean():5.0f} / ${q[(q[col] == 0) & m].net.mean():5.0f}"
                               for p_, m in (("18-22", q.date < SPLIT), ("23-26", q.date >= SPLIT)))
                print(f"     {snm:<6} {col:<7} agree {stat(a)} | disagree {stat(b)} | t {welch(a, b):+.1f} | {per}")

    # ---------------- 5. the best design-period predictor as a trade ----------------
    print("\n5. The feature with the best design-period correlation at 15 minutes, as a trade (top / bottom 10% by design thresholds):")
    dI = IC[IC.H == 15].assign(a=lambda z: z.design.abs()).sort_values("a", ascending=False)
    best = dI.iloc[0]; k = best.feat; sgn = np.sign(best.design)
    print(f"   chosen on 2018-22: {k} (design corr {best.design:+.3f}, holdout {best.holdout:+.3f})")
    q = S15.replace([np.inf, -np.inf], np.nan).dropna(subset=[k])
    lo, hi = np.nanpercentile(q[q.y < 2023][k], [10, 90])
    tr = []
    for r in q[(q[k] <= lo) | (q[k] >= hi)].itertuples():
        side = int(sgn * (1 if getattr(r, k) >= hi else -1))
        x = trade(g, int(r.d), int(r.j) + 1, side, int(r.j) + 15)
        if x is not None: tr.append(dict(date=ts[int(r.d)], side=side, net=x))
    T5 = pd.DataFrame(tr)
    for nm, m in (("design 2018-22", T5.date < SPLIT), ("holdout 2023-26", T5.date >= SPLIT)):
        z = T5[m]; print(f"   {nm}: {stat(z.net)} | longs ${z[z.side > 0].net.mean():4.0f} shorts ${z[z.side < 0].net.mean():4.0f}")
    print("   by year:", T5.groupby(T5.date.dt.year).net.sum().round(0).astype(int).to_dict())

    Dall = pd.DatetimeIndex([ts[d] for d in days]); Dh = Dall[Dall >= SPLIT]
    dly = lambda t, D=Dall: t.groupby(pd.to_datetime(t.date)).net.sum().reindex(D, fill_value=0.0)
    print("\n6. Standard metrics per NQ (2018-2026, and the 2023-26 holdout):")
    od = OP[(OP.end == 930) & (OP.sig == "delta")]
    rows = {f"5. {k} 15-min trade": (dly(T5), T5.net), f"5. {k} longs": (dly(T5[T5.side > 0]), T5.net[T5.side > 0]),
            f"5. {k} shorts": (dly(T5[T5.side < 0]), T5.net[T5.side < 0]),
            "2. opening delta 9:31": (dly(od), od.net), "3. big print follow 30": (dly(BP[BP.H == 30]), BP[BP.H == 30].net)}
    print(M.table(rows))
    hold = {nm: v[0].reindex(Dh, fill_value=0.0) for nm, v in rows.items()}
    b, p = R.report({f"{nm} (2023-26)": v for nm, v in hold.items()}, n=2000)
    print(b); print(p)
    pickle.dump(dict(IC=IC, OP=OP, BP=BP, T5=T5), open(SP + "orderflow_test.pkl", "wb"))
