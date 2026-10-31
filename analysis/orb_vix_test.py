"""YZ_ORB_Volatility_Filtered (user's MultiCharts .NET files + ES / GC reports, 2026-10-25; checks/candidates/orb_vix/).
Rebuild of the C# signal on our 1-minute grids, aggregated to 5-minute bars stamped at their CLOSE (Central time; the
author's anchors are ET = CT + 1 h):
  OR = high / low of the bars closing 08:35-08:45 CT (09:30-09:45 ET). Day gate at 09:45 ET: VixMin <= VIX <= VixMax
  (15-30). We have daily VIX only: the VIX OPEN (09:30 ET print, known before 09:45) stands in for the 09:45 5-min bar.
  Candidate: a bar closing 08:50-10:55 CT whose close crosses the OR high (prior close <= OR high) -> buy at the next bar's
  open (longs only, as the reports; shorts as a test). Size = floor(RiskDollars / ((close - (OR low - 0.25 ATR14)) x pv)),
  capped at MaxContracts; size 0 skips the candidate without using up the day.
  Frozen stop = OR low - 0.25 x ATR14 (5-min simple-average true range at the ENTRY bar). Exits work from the bar after
  the entry bar (entry bar unprotected, as the C#): stop (frozen -> entry once the high reached entry + 1R -> ATR trail
  once scaled), T1 limit at entry + 1.0 x OR for ceil(q/2). After T1 the runner trails: max(trail, high - 4 x ATR14),
  seeded at the entry. Not scaled: flat at the 11:00 CT close (12:00 ET); scaled: flat at the 15:30 CT close (16:30 ET).
  Inside a bar: a stop or limit the bar opens beyond fills at the open; otherwise MultiCharts' path rule (the open nearer the
  high -> O-H-L-C, else O-L-H-C) decides whether T1 or the stop comes first. One trade a day.
Costs: ours ($5 per ES / $7.25 per GC round trip + 1 tick per market or stop fill; the T1 limit pays no slippage), the
reviewer's ($4 + 1 tick), and $0 (the reports). Sizes: the reports' $5,000 risk / 50 cap on $100k, a fixed 2 contracts
(the scale needs 2) reported per contract, and the Apex size (micros, below).
  python3 analysis/orb_vix_test.py [SCRATCH_DIR] > analysis/outputs/orb_vix_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
sys.argv = [sys.argv[0], SP]
import s_rank_gap_round2_test as SG

NTRIAL = {"n": 0}
VIX = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE")
UP = "/root/.claude/uploads/7d3d05ee-c7fa-5007-8486-392889736cec/"
REPORT = {"ES": "mc_reports/ORB_Volatility_Filtered_ES_gross.xlsx", "GC": "mc_reports/ORB_Volatility_Filtered_GC_gross.xlsx"}


class Days5:
    """5-minute bars per trading day, from 06:05 to 15:35 CT (bar k closes at 06:05 + 5k minutes)."""
    T0 = jof(605)

    def __init__(self, name):
        S = SG.Sym(name); g = S.g; self.S, self.name = S, name
        self.tick, self.pv, self.comm = S.tick, S.pv, S.comm
        cols = np.arange(self.T0 - 4, jof(1535) + 1); n = len(cols) // 5
        self.t = np.array([(self.T0 + 5 * k) // 60 * 100 + (self.T0 + 5 * k) % 60 for k in range(n)])
        D = {}
        for r in g.trading:
            o, h, l, c = (getattr(g, a)[r, cols].reshape(n, 5) for a in "ohlc")
            with np.errstate(all="ignore"):
                hh, ll = np.nanmax(h, 1), np.nanmin(l, 1)
            ok = ~np.isnan(c).all(1)
            if ok.sum() < 60: continue
            oo = np.array([x[~np.isnan(x)][0] if m else np.nan for x, m in zip(o, ok)])
            cc = np.array([x[~np.isnan(x)][-1] if m else np.nan for x, m in zip(c, ok)])
            D[pd.Timestamp(g.ts[r])] = (oo, hh, ll, cc)
        self.D = D

    def atr(self, h, l, c, n=14):
        """Simple-average true range of the last n bars (bars with data only), per bar index."""
        pc = pd.Series(c).ffill().shift(1).to_numpy()
        tr = np.where(np.isnan(h), np.nan, np.nanmax(np.c_[h - l, np.abs(h - pc), np.abs(l - pc)], axis=1))
        return pd.Series(tr).rolling(n, min_periods=n).mean().to_numpy()      # NaN bars break the window (rare)


def run(X, vix_lo=15.0, vix_hi=30.0, use_vix=True, vix_col="OPEN", risk=5000.0, cap=50, fixed=None, longs=True, shorts=False,
        comm=None, slip_ticks=1, t1_mult=1.0, be_r=1.0, trail_mult=4.0, buf_mult=0.25, noon=1100, close_t=1530, count=True,
        start="2018-01-01", end="2026-12-31"):
    if count: NTRIAL["n"] += 1
    t = X.t; tick, pv = X.tick, X.pv; comm = X.comm if comm is None else comm; slip = slip_ticks * tick
    rt = lambda x: np.round(x / tick) * tick
    i_or = np.where((t >= 835) & (t <= 845))[0]; rows = []
    for d, (O, H, L, C) in X.D.items():
        if d < pd.Timestamp(start) or d > pd.Timestamp(end): continue
        if np.isnan(H[i_or]).all(): continue
        orh, orl = np.nanmax(H[i_or]), np.nanmin(L[i_or]); osz = orh - orl
        if use_vix:
            if d not in VIX.index: continue
            v = VIX.loc[d, vix_col]
            if not (vix_lo <= v <= vix_hi): continue
        A = X.atr(H, L, C)
        traded = False; i = i_or[-1] + 1
        while not traded and i < len(t) - 1 and t[i] <= 1055:
            if np.isnan(C[i]) or np.isnan(C[i - 1]): i += 1; continue
            side = 1 if (longs and C[i] > orh and C[i - 1] <= orh) else -1 if (shorts and C[i] < orl and C[i - 1] >= orl) else 0
            if side == 0 or np.isnan(A[i]): i += 1; continue
            lvl = orl - buf_mult * A[i] if side > 0 else orh + buf_mult * A[i]
            q = fixed if fixed else int(min(np.floor(risk / (abs(C[i] - lvl) * pv)), cap))
            if q < 1: i += 1; continue                                     # size skip: the day stays open
            k = i + 1
            while k < len(t) and np.isnan(O[k]): k += 1
            if k >= len(t): break
            e = O[k]; traded = True
            sp0 = rt(orl - buf_mult * A[k]) if side > 0 else rt(orh + buf_mult * A[k]); Rr = abs(e - sp0)
            q1 = (q + 1) // 2; t1 = rt(e + side * t1_mult * osz)
            pos = q; be = False; scaled = False; trail = 0.0; legs = []      # legs: (qty, exit price, kind)
            be = be_r > 0 and Rr > 0 and ((H[k] >= e + be_r * Rr) if side > 0 else (L[k] <= e - be_r * Rr))
            mae = (L[k] - e) * side if side > 0 else (e - H[k]); mfe = 0.0
            done_t = None; j = k
            if t[k] >= noon: legs.append((pos, C[k], "noon")); pos = 0; done_t = t[k]
            j = k + 1
            while pos > 0 and j < len(t):
                if np.isnan(O[j]): j += 1; continue
                sp = trail if scaled else (rt(e) if be else sp0)
                o, h, l, c = O[j], H[j], L[j], C[j]
                fav, adv = (h, l) if side > 0 else (-l, -h)
                so, sp_, t1_ = (o, sp, t1) if side > 0 else (-o, -sp, -t1)
                hit_t1 = False
                if so <= sp_:
                    legs.append((pos, o, "stop")); pos = 0
                else:
                    if not scaled and so >= t1_:
                        legs.append((q1 if q1 < pos else pos, o, "t1")); pos -= min(q1, pos); hit_t1 = True
                    high_first = (h - o) <= (o - l) if side > 0 else (o - l) <= (h - o)
                    if pos > 0 and not scaled and not hit_t1 and high_first and fav >= t1_:
                        legs.append((min(q1, pos), t1, "t1")); pos -= min(q1, pos); hit_t1 = True
                    if pos > 0 and adv <= sp_:
                        legs.append((pos, sp, "stop")); pos = 0
                    if pos > 0 and not scaled and not hit_t1 and fav >= t1_:
                        legs.append((min(q1, pos), t1, "t1")); pos -= min(q1, pos); hit_t1 = True
                mae = min(mae, (l - e) if side > 0 else (e - h)); mfe = max(mfe, (h - e) if side > 0 else (e - l))
                if pos > 0:
                    if not be and be_r > 0 and Rr > 0 and ((h >= e + be_r * Rr) if side > 0 else (l <= e - be_r * Rr)): be = True
                    if hit_t1 and not scaled: scaled = True; trail = rt(e)
                    if scaled and not np.isnan(A[j]):
                        cnd = rt(h - trail_mult * A[j]) if side > 0 else rt(l + trail_mult * A[j])
                        trail = max(trail, cnd) if side > 0 else min(trail, cnd)
                    if (not scaled and t[j] >= noon) or (scaled and t[j] >= close_t):
                        legs.append((pos, c, "noon" if not scaled else "close")); pos = 0
                if pos == 0: done_t = t[j]
                j += 1
            if pos > 0: legs.append((pos, C[~np.isnan(C)][-1], "close")); pos = 0
            gross = sum(qq * (px - e) * side * pv for qq, px, _ in legs)
            cost = q * comm + slip * pv * (q + sum(qq for qq, _, kd in legs if kd != "t1"))
            rows.append(dict(date=d, side=side, q=q, entry=e, stop=sp0, R=Rr, osz=osz, sig=t[i], fill=t[k], out=done_t,
                             kinds="+".join(kd for _, _, kd in legs), gross=gross, net=gross - cost, risk_d=Rr * q * pv,
                             r_net=(gross - cost) / (Rr * q * pv) if Rr > 0 else np.nan, mae=mae * q * pv, mfe=mfe * q * pv))
    x = pd.DataFrame(rows)
    return x.set_index("date") if len(x) else x


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(t, nm, w=46, col="net"):
    if len(t) < 5: return f"   {nm:<{w}} n={len(t)}"
    x = t[col]; y = x.index.year; by = x.groupby(y).sum(); a, b = x[y < 2023], x[y >= 2023]
    return (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.0f} R {t.r_net.mean():+.3f} PF {pf(x):4.2f} t {tst(x):4.1f} win {np.mean(x > 0):.0%} "
            f"yrs+ {(by > 0).sum()}/{len(by)} | 18-22 t {tst(a):4.1f} | 23+ ${b.mean():6.0f} t {tst(b):4.1f}")


def report_trades(path):
    d = pd.read_excel(path, sheet_name="List of Trades", header=2)
    e = d[d.Type.astype(str).str.startswith("Entry")].reset_index(drop=True); x = d[d.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    e["day"] = pd.to_datetime(e.Date).dt.normalize(); e["pnl"] = e["Profit ($)"].astype(float); e["sig"] = x.Signal.values
    return e


def flat_periods(dates, all_days):
    """Longest run of trading days with no trade."""
    s = pd.Series(0, index=all_days); s[s.index.isin(dates)] = 1
    gaps = (s == 0).astype(int).groupby((s != 0).cumsum()).sum(); return int(gaps.max())


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    X = {nm: Days5(nm) for nm in ("ES", "GC")}
    print("\n1. The reports' settings ($5,000 risk, cap 50, longs only, $0 costs), 2020-01 -> 2026-03, vs the MultiCharts reports:")
    for nm in ("ES", "GC"):
        z = run(X[nm], comm=0, slip_ticks=0, start="2020-01-06", end="2026-03-31"); e = report_trades(REPORT[nm])
        days_mc = set(e.day.dt.date); days_py = set(z.index.date)
        rep_net = e.pnl.sum(); by_mc = e.groupby(e.day.dt.year).pnl.sum(); by_py = z.net.groupby(z.index.year).sum()
        print(f"   {nm}: report {len(days_mc)} trade days, net ${rep_net:,.0f}, PF {pf(e.groupby('day').pnl.sum()):.2f}, contracts avg {e.Contracts.mean():.1f} "
              f"| rebuild {len(days_py)} days, net ${z.net.sum():,.0f}, PF {pf(z.net):.2f}, contracts avg {z.q.mean():.1f}; same days "
              f"{len(days_mc & days_py)} ({len(days_mc & days_py) / len(days_mc):.0%} of the report's)")
        print(f"      by year report: {by_mc.round(0).astype(int).to_dict()}\n      by year rebuild: {by_py.round(0).astype(int).to_dict()}")
        both = sorted(days_mc & days_py)
        if both:
            m = e.groupby("day").pnl.sum(); m.index = m.index.date; zz = z.net.copy(); zz.index = zz.index.date
            print(f"      on the shared days: report ${m.loc[both].sum():,.0f}, rebuild ${zz.loc[both].groupby(level=0).sum().sum():,.0f}, "
                  f"daily P&L corr {np.corrcoef(m.loc[both], zz.loc[both].groupby(level=0).sum())[0, 1]:+.2f}")
        exs = e.sig.value_counts(normalize=True).round(2).to_dict()
        print(f"      exit mix report {exs}; rebuild {z.kinds.value_counts(normalize=True).round(2).head(6).to_dict()}")

    for nm in ("ES", "GC"):
        Xn = X[nm]; print(f"\n2. {nm}, 2018-2026 (2018-19 = before the reports' window):")
        fx = run(Xn, fixed=2); fx["net"] /= 2; fx["gross"] /= 2; fx["mae"] /= 2; fx["mfe"] /= 2
        print(line(run(Xn, fixed=2, comm=0, slip_ticks=0).assign(net=lambda d: d.net / 2), "per contract, $0 costs (the reports)"))
        print(line(run(Xn, fixed=2, comm=4.0).assign(net=lambda d: d.net / 2), "per contract, reviewer $4 + 1 tick"))
        print(line(fx, f"per contract, ours ${Xn.comm:.2f} + 1 tick"))
        print("   per contract by year, ours:", fx.net.groupby(fx.index.year).sum().round(0).astype(int).to_dict())
        print(f"   cost share: gross ${fx.gross.mean():.0f} a contract -> net ${fx.net.mean():.0f}")
        rs = run(Xn); print(line(rs, "risk-sized $5,000 / cap 50, ours"))
        print(f"      risk-sized: max contracts {rs.q.max()}, median {rs.q.median():.0f}; margin at the max (~$15k ES / ~$12k GC per contract): "
              f"${rs.q.max() * (15000 if nm == 'ES' else 12000):,.0f}")
        print(line(run(Xn, use_vix=False, fixed=2).assign(net=lambda d: d.net / 2), "no VIX filter"))
        for lo, hi in ((0, 15), (15, 20), (20, 25), (25, 30), (30, 99), (16, 25), (12, 35)):
            print(line(run(Xn, vix_lo=lo, vix_hi=hi, fixed=2).assign(net=lambda d: d.net / 2), f"VIX {lo}-{hi}"))
        print(line(run(Xn, fixed=2, longs=False, shorts=True).assign(net=lambda d: d.net / 2), "shorts only"))
        print(line(run(Xn, fixed=2, shorts=True).assign(net=lambda d: d.net / 2), "longs + shorts"))
        print(line(run(Xn, fixed=2, shorts=True, use_vix=False).assign(net=lambda d: d.net / 2), "longs + shorts, no VIX filter"))
        for tm in (2.0, 3.0, 6.0): print(line(run(Xn, fixed=2, trail_mult=tm).assign(net=lambda d: d.net / 2), f"trail {tm} ATR"))
        print(line(run(Xn, fixed=2, be_r=0).assign(net=lambda d: d.net / 2), "no break-even"))
        print(line(run(Xn, fixed=2, t1_mult=99).assign(net=lambda d: d.net / 2), "no T1 scale (all to noon / stop)"))
        print(line(run(Xn, fixed=2, noon=1530).assign(net=lambda d: d.net / 2), "no noon exit (hold to 15:30 CT)"))
        dys = pd.DatetimeIndex(sorted(Xn.D)); w20 = dys[(dys >= "2020-01-06") & (dys <= "2026-03-31")]; w18 = dys[dys >= "2018-01-01"]
        nv = run(Xn, use_vix=False, fixed=2, count=False)
        print(f"   longest stretch without a trade (trading days): VIX 15-30 {flat_periods(fx.index, w18)} (2018-26), "
              f"{flat_periods(fx.index, w20)} (the reports' window); no VIX filter {flat_periods(nv.index, w18)}; "
              f"trade days a year {len(fx) / (len(w18) / 252):.0f} of 252")
        eq = fx.net.groupby(fx.index).sum().reindex(w18, fill_value=0).cumsum(); hi = eq.cummax()
        under = (eq < hi).astype(int); runs = under.groupby((under == 0).cumsum()).sum()
        print(f"   longest time below a previous equity high (per contract, 2018-26): {runs.max()} trading days")
        vix_d = VIX.OPEN.reindex(pd.DatetimeIndex(sorted(Xn.D))); allv = run(Xn, use_vix=False, fixed=2, count=False); allv["net"] /= 2
        inside = allv[(vix_d.reindex(allv.index) >= 15) & (vix_d.reindex(allv.index) <= 30)]
        ms = np.array([allv.net.sample(len(inside), random_state=s).mean() for s in range(500)])
        print(f"   VIX gate vs random days: band days ${inside.net.mean():.0f} a contract; random same-size subsets ${ms.mean():.0f} "
              f"(95th pct ${np.percentile(ms, 95):.0f}); share >= band {np.mean(ms >= inside.net.mean()):.1%}")
        globals()[f"FX_{nm}"] = fx

    print("\n3. Metrics, per 1 contract (ours, fixed 2 / 2), daily:")
    for nm in ("ES", "GC"):
        fx = globals()[f"FX_{nm}"]; days = pd.DatetimeIndex(sorted(X[nm].D)); days = days[days >= "2018-01-01"]
        dd = fx.net.groupby(fx.index).sum().reindex(days, fill_value=0.0)
        print(M.table({f"{nm} 2018-26": (dd, fx.net), f"{nm} 2023+": (dd[dd.index >= "2023-01-01"], fx.net[fx.index >= "2023-01-01"])}))
        b_, p_ = R.report({f"{nm} 2023+": dd[dd.index >= "2023-01-01"]}, limits=(2000, 5000, 10000)); print(b_); print(p_)
        mic = 10.0
        print(MC.report(fx.net.values, daily=dd.values, size=1 / mic, label=f"{nm} ORB 1 micro"))
        globals()[f"DD_{nm}"] = dd
    a, b = DD_ES.align(DD_GC, join="inner", fill_value=0)
    print(f"\n   ES / GC daily corr {np.corrcoef(a, b)[0, 1]:+.2f}")
    print("\n4. Our personal-portfolio pieces (1 micro each) on the days the VIX gate blocks vs passes (VIX open):")
    import io, contextlib, runpy
    with contextlib.redirect_stdout(io.StringIO()):
        gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
    P = gg["P"]; v = VIX.OPEN.reindex(P.index); band = pd.cut(v, [0, 15, 30, 999], labels=["VIX<15", "VIX 15-30", "VIX>30"])
    tab = P.groupby(band).mean().T.round(1); tab["n<15"] = int((band == "VIX<15").sum()); tab["n15-30"] = int((band == "VIX 15-30").sum())
    print("   average $ a day per piece:"); print(tab.to_string())
    o = DD_ES.reindex(P.index, fill_value=0) / 10
    print(f"   ES ORB (1 MES) daily corr with the 17-piece book {np.corrcoef(o, P.sum(axis=1))[0, 1]:+.2f}; "
          f"book $ a day on VIX<15 days {P.sum(axis=1)[band == 'VIX<15'].mean():.0f}, on 15-30 days {P.sum(axis=1)[band == 'VIX 15-30'].mean():.0f}")
    print(f"\n   trials counted here: {NTRIAL['n']}; t threshold {M.t_threshold(NTRIAL['n']):.2f}")
