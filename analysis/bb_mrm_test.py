"""BB_MRM Pre-market (user's MultiCharts file BB_MRM_Pre-market.txt + 2 reports + input screen, 2026-10-24): Bollinger(50, 3)
mean reversion on NQ 1-minute bars inside an Italian-time window (Session_Open 08:05 + 1h15 = 08:05-09:20 Rome = 01:05-02:20 CT
most of the year) per its comments -- BUT the reports reproduce only on the EXCHANGE clock: 08:05-09:20 CT = the cash open
(Rome clock: 522 trades, -$7.7k in report 1's period; CT clock: 802 trades, +$59.0k, PF 1.33, win 54.5%). Default = CT. Reports: 2020-01-06 -> 2023-12-29 801 trades +$61,751 PF 1.35 win 54.6%; a later ~1 year 236 trades
+$43,870 PF 1.62 win 56.4% (per NQ).
Rebuild (IntrabarOrderGeneration false, orders for the next 1-minute bar, MultiCharts' StdDev = population):
  entry   flat, window on, band range <= 1.25 x min of the previous 3 band ranges: close crosses below the lower band ->
          buy limit 3 ticks under that close (next bar only); mirror for shorts.
  exits   hard stop 300 ticks (75 pts); target limit = SMA -/+ 10% x |entry - SMA| (moves with the SMA); breakeven stop once
          +170 ticks seen; 'soft stop' entry -/+ 2.8 x the signal-bar sd, tightened linearly to the entry from bar 2 to bar 20
          (close crossing it -> market next bar); market exit after 20 bars, when the close is through the hard / BE level,
          and when the window closes.
  fills   limits at the price (or the open if better); stops at the level or the open if gapped, 1 tick slippage; market
          orders at the next open + 1 tick; within a bar the target or the stop comes first by the bar's path (O-H-L-C
          when the open is nearer the high, else O-L-H-C), as MultiCharts assumes.
Costs $7.25 per NQ round trip + 1 tick per market / stop fill (limits none).
  python3 analysis/bb_mrm_test.py > analysis/outputs/bb_mrm_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R, montecarlo as MC

PV, TICK, COMM = 20.0, 0.25, 7.25
NTRIAL = {"n": 0}


def load():
    g = pickle.load(open("scratch_data/g24.pkl", "rb"))
    o, h, l, c = (getattr(g, k).ravel() for k in "ohlc"); ok = np.where(~np.isnan(c))[0]
    ts = pd.DatetimeIndex(g.ts[ok // 1440]) + pd.to_timedelta(ok % 1440, unit="m")       # bar close, CT
    rome = ts.tz_localize("America/Chicago", ambiguous="NaT", nonexistent="NaT").tz_convert("Europe/Rome")
    rm = np.where(rome.isna(), -1, rome.hour * 60 + rome.minute)
    ct = ts.hour * 60 + ts.minute
    return dict(o=o[ok], h=h[ok], l=l[ok], c=c[ok], ts=ts, rome=np.asarray(rm), rm=np.asarray(ct))


def run(B, bbl=50, bba=3.0, alpha=10.0, stopm=2.8, t0=2, t1=20, maxbars=20, expk=3, expa=1.25, hard=300, be=170, pb=3,
        win=(485, 560), tighten=True, longs=True, shorts=True, start="2018-01-01", count=True, rand=None, thr_e=0.0, thr_t=0.0, comm=COMM):
    if count: NTRIAL["n"] += 1
    o, h, l, c, rm = B["o"], B["h"], B["l"], B["c"], B["rm"]
    cs = pd.Series(c); ma = cs.rolling(bbl).mean().values; sd = cs.rolling(bbl).std(ddof=0).values
    up, lo = ma + bba * sd, ma - bba * sd; rng = up - lo
    mn = pd.Series(rng).shift(1).rolling(expk).min().values; bandok = rng <= mn * expa
    on = (rm >= win[0]) & (rm <= win[1])
    s0 = np.searchsorted(B["ts"], pd.Timestamp(start))
    cand = np.where(on)[0]; cand = cand[cand >= max(s0, bbl + expk + 1)]
    # visit every bar from a window's first bar until flat after the window
    trades = []; mp = 0; E = 0.0; eb = 0; ent = None; mkt = False; soft_prev = 0.0; tp = 0.0
    hs = bes = 0.0; arm = False; sig_sd = 0.0; xkind = ""
    i_list = np.unique(np.r_[cand, cand + 1, cand + 2])
    i_list = i_list[i_list < len(c)]
    prev_i = -10
    for i in i_list:
        if i != prev_i + 1 and mp == 0: ent = None                     # a gap in the visited bars: no order carries over
        prev_i = i
        # ---------------- orders working in bar i ----------------
        if mp == 0 and ent is not None:
            side, lim = ent
            if side > 0 and l[i] <= lim - thr_e: E = min(o[i], lim); mp = 1; eb = i
            elif side < 0 and h[i] >= lim + thr_e: E = max(o[i], lim); mp = -1; eb = i
            ent = None
        elif mp != 0 and i > eb:
            x = None
            if mkt: x = o[i]
            else:
                stp = max(hs, E if arm else -1e18) if mp > 0 else min(hs, E if arm else 1e18)
                if mp > 0:
                    if o[i] <= stp: x, xkind = o[i], "stop gap"
                    elif tp > 0 and o[i] >= tp: x, xkind = o[i], "target"
                    else:
                        hit_s, hit_t = l[i] <= stp, tp > 0 and h[i] >= tp + thr_t
                        high_first = (h[i] - o[i]) < (o[i] - l[i])
                        if hit_t and (not hit_s or high_first): x, xkind = tp, "target"
                        elif hit_s: x, xkind = stp, ("BE" if arm and stp == E else "hard stop")
                else:
                    if o[i] >= stp: x, xkind = o[i], "stop gap"
                    elif tp > 0 and o[i] <= tp: x, xkind = o[i], "target"
                    else:
                        hit_s, hit_t = h[i] >= stp, tp > 0 and l[i] <= tp - thr_t
                        low_first = (o[i] - l[i]) < (h[i] - o[i])
                        if hit_t and (not hit_s or low_first): x, xkind = tp, "target"
                        elif hit_s: x, xkind = stp, ("BE" if arm and stp == E else "hard stop")
            if x is not None:
                net = (x - E) * mp * PV - comm
                trades.append(dict(t=B["ts"][eb], side=mp, entry=E, exit=x, bars=i - eb, kind=xkind, net=net)); mp = 0
        mkt = False
        # ---------------- bar i close ----------------
        if mp != 0:
            if i == eb:
                hs = E - mp * hard * TICK; arm = False; ss = E - mp * stopm * sig_sd
            bse = i - eb
            tp = ma[i] - mp * alpha / 100 * abs(E - ma[i])
            if not arm and ((h[i] >= E + be * TICK) if mp > 0 else (l[i] <= E - be * TICK)): arm = True
            r = 0 if (not tighten or bse <= t0) else 1 if bse >= t1 else (bse - t0) / (t1 - t0)
            soft = ss + (E - ss) * r
            if not on[i]: mkt, xkind = True, "window close"
            elif (c[i] <= hs) if mp > 0 else (c[i] >= hs): mkt, xkind = True, "hard mkt"
            elif arm and ((c[i] <= E) if mp > 0 else (c[i] >= E)): mkt, xkind = True, "BE mkt"
            elif (c[i] < soft and c[i - 1] >= soft_prev) if mp > 0 else (c[i] > soft and c[i - 1] <= soft_prev):
                mkt, xkind = True, "soft stop"
            elif bse >= maxbars: mkt, xkind = True, "time"
            soft_prev = soft
        elif on[i] and bandok[i] and i >= s0 and rand is not None:
            if rand.random() < 0.011: sig_sd = sd[i]; sd_ = 1 if rand.random() < 0.5 else -1; ent = (sd_, c[i] - sd_ * pb * TICK)
        elif on[i] and bandok[i] and i >= s0:
            if longs and c[i] < lo[i] and c[i - 1] >= lo[i - 1]: sig_sd = sd[i]; ent = (1, c[i] - pb * TICK)
            if shorts and c[i] > up[i] and c[i - 1] <= up[i - 1]: sig_sd = sd[i]; ent = (-1, c[i] + pb * TICK)
    t = pd.DataFrame(trades)
    if len(t): t["net"] -= np.where(t.kind.isin(["target"]), 0, TICK * PV); t["date"] = t.t.dt.normalize()
    return t


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(t, nm, w=46):
    if len(t) < 5: return f"   {nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); a, b = x[y < 2024], x[y >= 2024]
    L, S = x[t.side > 0], x[t.side < 0]
    return (f"   {nm:<{w}} n={len(x):4d} ${x.mean():4.0f} PF {pf(x):4.2f} t {tst(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | <24 ${a.mean():4.0f} t {tst(a):4.1f} | 24+ n {len(b)} ${b.mean():4.0f} t {tst(b):4.1f} | L ${L.mean():4.0f} S ${S.mean():4.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    B = load(); base = run(B)
    base.to_csv("analysis/outputs/bb_mrm_trades.csv", index=False)
    print(f"\n1. The rule as in the input screen (alpha 10%, window 08:05-09:20 CT), per NQ, 2018-01 -> {base.date.max().date()}:")
    print(line(base, "rebuild"))
    w = base[(base.date >= "2020-01-06") & (base.date <= "2023-12-29")]
    print(f"   report 1 period 2020-01-06 -> 2023-12-29: {len(w)} trades (report 801), ${w.net.sum():,.0f} (report $61,751), PF {pf(w.net):.2f} (1.35), "
          f"win {np.mean(w.net > 0):.1%} (54.6%)")
    for a, b in (("2024-01-01", "2025-02-27"), ("2024-09-01", "2025-10-28"), ("2025-08-12", "2026-10-09")):
        w2 = base[(base.date >= a) & (base.date <= b)]
        print(f"   {a} -> {b}: {len(w2)} trades, ${w2.net.sum():,.0f}, PF {pf(w2.net):.2f}, win {np.mean(w2.net > 0):.1%}  (report 2: 236, $43,870, 1.62, 56.4%)")
    print("   by year $:", base.groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   by year n:", base.groupby(base.date.dt.year).size().to_dict())
    print("   exits:", base.kind.value_counts().to_dict(), "| bars held median", base.bars.median())
    rt = run(dict(B, rm=B["rome"]), count=False); wr = rt[(rt.date >= "2020-01-06") & (rt.date <= "2023-12-29")]
    print(f"   the same on the Rome clock (01:05-02:20 CT, what the comments say): {len(rt)} trades ${rt.net.mean():.0f} t {tst(rt.net):.1f}; "
          f"report 1 period {len(wr)} trades ${wr.net.sum():,.0f}")

    print("\n2. Robustness (one change at a time):")
    V = {"file default alpha 15%, window to 09:10": dict(alpha=15.0, win=(485, 550)), "alpha 0 (target = SMA)": dict(alpha=0.0),
         "alpha 30%": dict(alpha=30.0), "BB 2.5 sd": dict(bba=2.5), "BB 3.5 sd": dict(bba=3.5), "BB length 30": dict(bbl=30), "BB length 100": dict(bbl=100),
         "no band-expansion filter": dict(expa=99.0), "no stop tightening": dict(tighten=False), "no pullback (limit at the close)": dict(pb=0),
         "pullback 6 ticks": dict(pb=6), "max 10 bars": dict(maxbars=10), "max 40 bars": dict(maxbars=40),
         "window 08:30-09:45 CT (from the cash open)": dict(win=(510, 585)), "window 08:05-10:30 CT": dict(win=(485, 630)),
         "window 09:20-10:35 CT (the next 75 min)": dict(win=(560, 635)), "window 12:00-13:15 CT (midday)": dict(win=(720, 795)),
         "longs only": dict(shorts=False), "shorts only": dict(longs=False)}
    for nm, kw in V.items(): print(line(run(B, **kw), nm))

    print("   fill policy (Codex review 2026-10-25; the base accepts limit touches, as MultiCharts' default did in the user's report):")
    for nm, kw in (("entry limits 1 tick through", dict(thr_e=TICK)), ("targets 1 tick through", dict(thr_t=TICK)),
                   ("both 1 tick through", dict(thr_e=TICK, thr_t=TICK)), ("targets 1 point through (repo's strict rule)", dict(thr_t=1.0)),
                   ("both through + real micro fee ($1.04 x 10 per NQ)", dict(thr_e=TICK, thr_t=TICK, comm=10.4))):
        print(line(run(B, count=False, **kw), nm))
    rs = [run(B, rand=np.random.default_rng(k), count=False) for k in range(40)]
    m = np.array([x.net.mean() for x in rs]); n_ = np.array([len(x) for x in rs])
    print(f"   placebo: random bars in the same window (band filter on), random side, same orders and exits, 40 seeds: {n_.mean():.0f} trades, "
          f"${m.mean():.0f} a trade (95th pct ${np.percentile(m, 95):.0f}); the rule ${base.net.mean():.0f} beats {np.mean(m < base.net.mean()):.0%}")
    rev = run(B, count=False)
    pdp = pd.read_csv("agents/tasks/plan_daily_pnl.csv", index_col=0, parse_dates=True)
    x = base.groupby("date").net.sum(); x = x.reindex(pdp.index, fill_value=0.0)
    print("   daily correlation with the plan pieces (agents/tasks/plan_daily_pnl.csv):", pdp.corrwith(x).round(2).to_dict())
    import dual_thrust_test as DT
    dtd = DT.load(); dtt = DT.run(dtd, DT.setups(dtd)); dtx = dtt.set_index("date").net.groupby(level=0).sum().reindex(pdp.index, fill_value=0.0)
    print(f"   corr with Dual Thrust v4: {np.corrcoef(x, dtx)[0, 1]:+.2f}")

    print("\n3. Metrics per NQ (daily) and Monte Carlo at 1 MNQ:")
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= "2018-01-01"]
    dd = base.groupby("date").net.sum().reindex(days, fill_value=0.0)
    rows = {}
    for nm, t in (("whole", base), ("longs", base[base.side > 0]), ("shorts", base[base.side < 0])):
        x = t.groupby("date").net.sum().reindex(days, fill_value=0.0)
        for per, s in (("2018-26", "2018-01-01"), ("2023+", "2023-01-01")):
            rows[f"{nm} {per}"] = (x[x.index >= s], t[t.date >= s].set_index("date").net)
    print(M.table(rows))
    b_, p_ = R.report({"whole 2023+": dd[dd.index >= "2023-01-01"]}, limits=(5000, 10000, 20000)); print(b_); print(p_)
    print(MC.report(base.net.values, daily=dd.values, size=0.1, label="BB_MRM 1 MNQ"))
    print(f"\n   trials {NTRIAL['n']}; t threshold {M.t_threshold(NTRIAL['n']):.2f}; deflated Sharpe {M.deflated_sharpe(dd.values, NTRIAL['n']):.2f}")
