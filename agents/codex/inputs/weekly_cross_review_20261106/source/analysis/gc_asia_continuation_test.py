"""GC USA -> Asia night continuation (user upload 2026-11-01: Gold_USA_Asia_Continuation v4/V5 PowerLanguage + MultiCharts
report; paper Wei 2026, 'Who Moves the Price? Trading-Session Return Decomposition and Cross-Session Momentum in Gold and
Silver Markets'). The user asks for ONE more discriminating variable that isolates the effect and cuts the drawdown.

Rebuild (bar by bar, as the code; 1-minute GC Grid24, CT; times in CST, +1 h in US daylight time, as enable_CST_CDT):
  USA session 08:30-18:00 CST (14:30-24:00 UTC), Asia 18:00-02:00 CST (00:00-08:00 UTC); bars belong by close time.
  Long at the open of the first Asia bar when the USA session closed up (close > open), not after a weekend (the USA session
  spans Friday -> Sunday), and the sum of the % returns of the Asia sessions ended in the last 90 calendar days is > 0
  (only once 90 days of history exist). Out at the open of the bar after 02:00 CST (03:00 CDT). No stop / target.
  Size: (a) 1 GC; (b) the code's ATR sizing: floor($6,000 / (median High-Low of the last 21 Asia sessions x $100)), 1-20.
  Costs: ours, $7.25 + 1 tick ($10) per market fill = $27.25 per GC round trip.

Candidate variables, fixed BEFORE looking at any result (2026-11-01), each with its mechanism; one is chosen on 2018-22 only:
  V1 USA close location: (USA close - USA low) / (USA high - USA low) >= 0.5. Buyers still in control at the hand-off;
     a rally that faded into the close is profit-taking, not demand that Asia will extend.
  V2 USA tail: the last hour of the USA session (17:00 -> 18:00 CST = 23:00 -> 24:00 UTC, the Globex evening reopen,
     when Asian desks come in) is up. The paper's buyer is Asian; if they are already buying, the move continues.
  V3 Gold-specific move: 6E's USA-session return <= 0 (the dollar did not fall). Gold up on a weaker dollar is a dollar
     move; gold up against a flat / stronger dollar is gold demand, the thing that should continue.
  V4 China open: skip Asia sessions on Shanghai Gold Exchange holidays (approximate calendar below: Spring Festival eve
     + 6 days, 1-7 October). If Chinese demand drives the drift, continuation should weaken when SGE is shut.
Choice rule: the variable with the best 2018-22 return / max drawdown (1 GC) wins, if it keeps >= 50% of the trades and its
removed trades average less than its kept ones; then its 2023+ result is read once. Every variable is reported in both
periods. Placebo: dropping the same share of trades at random (1,000 draws) also lowers the drawdown; a variable must beat
that, not just the unfiltered rule.
Clock: the report is closest when the inputs are read on New York time (shift -60 in CT; our MultiCharts puts COMEX on New
York time, MULTICHARTS_PITFALLS). As coded in CT (shift 0) the base rule loses in 2018-22 at 1 GC.
  python3 analysis/gc_asia_continuation_test.py [SCRATCH_DIR] [SHIFT_MIN, default -60]
"""
import sys, os, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from cl_forced_flows_test import load
import metrics as M, resampling as R, montecarlo as MC

PV, TICK, COMM = 100.0, 0.10, 7.25
COST = COMM + 2 * TICK * PV
CNY = ["2018-02-16", "2019-02-05", "2020-01-25", "2021-02-12", "2022-02-01", "2023-01-22", "2024-02-10", "2025-01-29", "2026-02-17"]


def sge_closed(d):
    d = pd.Timestamp(d)
    if d.month == 10 and d.day <= 7: return True
    for c in CNY:
        c = pd.Timestamp(c)
        if c - pd.Timedelta(days=1) <= d <= c + pd.Timedelta(days=6): return True
    return False


def is_cdt(ts):
    m, dd, w = ts.month, ts.day, (ts.dayofweek + 1) % 7
    return (3 < m < 11) or (m == 3 and dd - w >= 8) or (m == 11 and dd - w < 1)


def hm(x):
    return (x // 100) * 60 + x % 100


def sessions(g, s_usa=830, e_usa=1800, s_asia=1800, e_asia=200, regime_days=90, atr_len=21, after_weekend=False, shift=0, dst=True, every_night=False):
    """Bar-by-bar replica. Returns one row per USA-up signal with its features, entry / exit and the regime state."""
    TS = pd.DatetimeIndex(g.ts)
    O, H, L, C = (getattr(g, k).ravel() for k in "ohlc")
    idx = np.where(~np.isnan(C))[0]
    row = idx // 1440; tod = idx % 1440
    cdt = np.array([is_cdt(TS[r]) for r in range(g.D)])[row]
    off = np.where(cdt & dst, 60, 0) + shift
    sU, eU, sA, eA = ((hm(s_usa) + off) % 1440, (hm(e_usa) + off) % 1440, (hm(s_asia) + off) % 1440, (hm(e_asia) + off) % 1440)
    t = tod                                               # minute of the day of the bar's close (00:00 bar = 0, as MC's Time 0)
    inU = np.where(sU < eU, (t > sU) & (t <= eU), (t > sU) | (t <= eU))
    inA = np.where(sA < eA, (t > sA) & (t <= eA), (t > sA) | (t <= eA))
    rows = []
    asia_buf = []; rng_buf = []; first_j = None
    usa_open = usa_close = usa_hi = usa_lo = 0.0; usa_valid = False; usa_gap = False; usa_start = 0
    a_open = a_close = a_hi = a_lo = 0.0; a_active = False
    pend = None; atr = 0.0
    pos = None
    jul = row                                            # calendar row = day number
    n = len(idx)
    for k in range(n):
        i = idx[k]; prevU = inU[k - 1] if k else False; prevA = inA[k - 1] if k else False
        # fills at this bar's open (orders from bar k-1)
        if pos is not None and pos.get("exit_pending"):
            pos["exit"] = O[i]; pos["x"] = i; rows.append(pos); pos = None
        if pend is not None and pend.get("go"):
            pos = dict(pend); pos["entry"] = O[i]; pos["e"] = i; pend = None
        # USA tracking
        if inU[k] and not prevU:
            usa_open = O[i]; usa_hi = H[i]; usa_lo = L[i]; usa_valid = k > 0; usa_gap = False; usa_start = i; pend = None
        if prevU and k > 0 and jul[k] - jul[k - 1] >= 2: usa_gap = True
        if inU[k]:
            usa_close = C[i]; usa_hi = max(usa_hi, H[i]); usa_lo = min(usa_lo, L[i])
        if prevA and not inA[k]: pend = None
        # Asia tracking (regime + ATR)
        if inA[k] and not prevA:
            a_open, a_hi, a_lo, a_active = O[i], H[i], L[i], k > 0
        if inA[k]:
            a_close = C[i]; a_hi = max(a_hi, H[i]); a_lo = min(a_lo, L[i])
        a_end = a_active and ((inA[k] and t[k] == eA[k]) or (not inA[k] and prevA))
        if a_end:
            a_active = False
            asia_buf.append((jul[k], 100 * (a_close - a_open) / a_open))
            if first_j is None: first_j = jul[k]
            rng_buf.append(a_hi - a_lo)
            atr = float(np.median(rng_buf[-atr_len:])) if len(rng_buf) >= atr_len else 0.0
        # USA end -> signal
        u_end = usa_valid and ((inU[k] and t[k] == eU[k]) or (not inU[k] and prevU))
        if u_end:
            usa_valid = False; pend = None
            mv = 100 * (usa_close - usa_open) / usa_open if usa_open > 0 else 0.0
            if (after_weekend or not usa_gap) and (mv > 0 or every_night):
                cur = jul[k]
                win = [r for j_, r in asia_buf if j_ > cur - regime_days]
                ready = first_j is not None and cur - first_j >= regime_days and len(win) > 0
                regime = sum(win) if ready else np.nan
                if ready and atr > 0:
                    lk = k if inU[k] else k - 1                  # last USA bar (k is the fallback bar outside the session)
                    tail = C[idx[lk]] - C[idx[lk - 60]] if lk >= 60 else np.nan   # last 60 traded minutes of the USA session
                    pend = dict(date=TS[row[k]], usa_ret=mv, usa_open=usa_open, usa_close=usa_close, usa_hi=usa_hi, usa_lo=usa_lo,
                                usa_start=usa_start, usa_end=i, regime=regime, atr=atr, usa_tail=tail, go=False)
        if pend is not None and not pend["go"]:
            if t[k] == sA[k] or (inA[k] and t[k] != eA[k]):
                pend["go"] = True                          # buy next bar at market
        if pos is not None and (t[k] == eA[k] or not inA[k]) and k > 0 and pos["e"] < i:
            pos["exit_pending"] = True
    out = pd.DataFrame(rows)
    out["pts"] = out.exit - out.entry
    out["clv"] = (out.usa_close - out.usa_lo) / (out.usa_hi - out.usa_lo)
    out["asia_date"] = pd.DatetimeIndex(TS[out.x // 1440])
    out["qty_atr"] = np.clip(np.floor(6000.0 / (out.atr * PV)), 1, 20)
    return out


def fx_usa_ret(trades, fx):
    """6E return over the same USA window (open of the first bar after the start -> last close at the end)."""
    O, C = fx.o.ravel(), pd.Series(fx.c.ravel()).ffill().to_numpy()
    Ov = pd.Series(O).bfill().to_numpy()
    base = int((pd.Timestamp(fx.ts[0]) - pd.Timestamp(trades_grid_start[0])).days) * 1440
    a = trades.usa_start.to_numpy() - base; b = trades.usa_end.to_numpy() - base
    ok = (a >= 0) & (b < len(C))
    r = np.full(len(trades), np.nan)
    r[ok] = C[b[ok]] / Ov[a[ok]] - 1
    return r


def stats(x, label):
    x = pd.Series(x, dtype=float)
    e = x.cumsum(); dd = -(e - e.cummax()).min()
    gp, gl = x[x > 0].sum(), -x[x < 0].sum()
    t = x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
    return dict(set=label, n=len(x), net=x.sum(), avg=x.mean(), pf=gp / gl if gl else np.inf, t=t, maxdd=dd,
                ret_dd=x.sum() / dd if dd else np.inf, win=(x > 0).mean())


trades_grid_start = [None]

if __name__ == "__main__":
    pd.set_option("display.width", 250)
    SHIFT = int(sys.argv[2]) if len(sys.argv) > 2 else -60
    g = load("GC"); fx = load("6E"); trades_grid_start[0] = g.ts[0]
    print(f"Clock: shift {SHIFT:+d} min vs the code read in CT (-60 = the user's chart on New York time: closest to the report)")
    s = sessions(g, shift=SHIFT)
    s["net1"] = s.pts * PV - COST
    s["netA"] = s.net1 * s.qty_atr
    s["fx"] = fx_usa_ret(s, fx)
    s["china_closed"] = s.asia_date.map(sge_closed)
    s["regime_ok"] = s.regime > 0
    T = s[s.regime_ok & (s.date >= "2018-01-01")].copy()
    T["period"] = np.where(T.date < "2023-01-01", "2018-22", "2023+")
    print(f"USA-up signals 2018+: {int((s.date >= '2018-01-01').sum())}; after the 90-day regime filter: {len(T)} trades "
          f"({T.date.min().date()} .. {T.date.max().date()}); GC data to {pd.Timestamp(g.ts[-1]).date()}")
    print("\n== Base rule as uploaded (regime on), user's report: 2018-22 254 trades PF 1.64, 2023-26 245 trades PF 1.31 (ATR sizing, their costs)")
    rows = []
    for p in ("2018-22", "2023+"):
        u = T[T.period == p]
        rows += [stats(u.net1, f"{p} 1 GC"), stats(u.netA, f"{p} ATR-sized")]
    print(pd.DataFrame(rows).round(2).to_string(index=False))
    print("\nby year (1 GC):", T.groupby(T.date.dt.year).net1.agg(["size", "sum", "mean"]).round(0).T.to_string())
    # benchmark: every Asia session long (same weekend / regime / data), to see what the USA-up condition adds
    b = sessions(g, shift=SHIFT, every_night=True); b["net1"] = b.pts * PV - COST
    Bt = b[(b.regime > 0) & (b.date >= "2018-01-01")]
    print("\n== Benchmark: long EVERY Asia session (same regime / weekend rules), 1 GC; and USA-down nights only")
    rows = []
    for p, m in (("2018-22", Bt.date < "2023-01-01"), ("2023+", Bt.date >= "2023-01-01")):
        u = Bt[m]; rows += [stats(u.net1, f"{p} every night"), stats(u.net1[u.usa_ret > 0], f"{p} USA up (the rule)"),
                            stats(u.net1[u.usa_ret <= 0], f"{p} USA down")]
    print(pd.DataFrame(rows).round(2).to_string(index=False))
    print("\nWorst 8 nights 2023+ (1 GC):", T[T.period == "2023+"].nsmallest(8, "net1")[["asia_date", "net1", "usa_ret"]].round(2).to_string(index=False))
    # candidates
    V = {"V1 close location >= 0.5": T.clv >= 0.5, "V2 last USA hour up": T.usa_tail > 0, "V3 6E USA return <= 0": T.fx <= 0,
         "V4 SGE open (skip China holidays)": ~T.china_closed}
    print("\n== Candidates (1 GC). kept / removed; return/DD vs the base; placebo = random removal of the same share (1,000 draws)")
    rng = np.random.default_rng(1); res = []
    for name, m in V.items():
        m = m.fillna(False)
        for p in ("2018-22", "2023+"):
            u = T[T.period == p]; mk = m[T.period == p].to_numpy()
            base = stats(u.net1, "base"); kept = stats(u.net1[mk], "kept"); rem = stats(u.net1[~mk], "removed")
            sh = mk.mean(); x = u.net1.to_numpy()
            pl = []
            for _ in range(1000):
                keep = rng.random(len(x)) < sh; pl.append(stats(x[keep], "p")["ret_dd"])
            res.append(dict(variable=name, period=p, keep=f"{sh:.0%}", kept_n=kept["n"], kept_avg=kept["avg"], removed_avg=rem["avg"],
                            kept_pf=kept["pf"], kept_t=kept["t"], base_ret_dd=base["ret_dd"], kept_ret_dd=kept["ret_dd"],
                            base_dd=base["maxdd"], kept_dd=kept["maxdd"],
                            placebo_ret_dd_p50=np.median(pl), beats_placebo=f"{(np.array(pl) < kept['ret_dd']).mean():.0%}"))
    Rz = pd.DataFrame(res)
    print(Rz.round(2).to_string(index=False))
    d = Rz[Rz.period == "2018-22"]
    elig = d[(d.kept_n >= 0.5 * len(T[T.period == '2018-22'])) & (d.removed_avg < d.kept_avg)]
    pick = elig.sort_values("kept_ret_dd", ascending=False).variable.iloc[0] if len(elig) else None
    print(f"\nChosen on 2018-22 only: {pick}")
    if pick:
        print(Rz[Rz.variable == pick].round(2).to_string(index=False))
        m = V[pick].fillna(False); K = T[m]
        print("\nChosen variable, ATR-sized (the user's sizing), both periods:")
        print(pd.DataFrame([stats(T[T.period == p].netA, f"{p} base") for p in ("2018-22", "2023+")] +
                           [stats(K[K.period == p].netA, f"{p} + {pick}") for p in ("2018-22", "2023+")]).round(2).to_string(index=False))
        print("by year kept (1 GC):", K.groupby(K.date.dt.year).net1.sum().round(0).to_dict())
    T.to_csv(f"checks/candidates/gc_asia_continuation/python_trades_shift{SHIFT}.csv", index=False)
    # standard metrics, 1 MGC (= GC / 10), daily on trade dates
    for nm, X in (("base", T), (f"+ {pick}", T[V[pick].fillna(False)] if pick else T)):
        days = pd.bdate_range("2018-01-01", T.date.max())
        dly = X.groupby(X.asia_date).net1.sum().reindex(days, fill_value=0.0)
        print(f"\n== {nm}: metrics per GC (daily, calendar of business days)")
        print(M.table({"whole": (dly, X.net1), "2018-22": (dly[dly.index < "2023-01-01"], X[X.period == "2018-22"].net1),
                       "2023+": (dly[dly.index >= "2023-01-01"], X[X.period == "2023+"].net1)}, capital=50_000.0))
        b_, p_ = R.report({f"{nm} 2023+": dly[dly.index >= "2023-01-01"]}); print(b_); print(p_)
        print(MC.report(X.net1.values, daily=dly.values, size=0.1, label=f"{nm} 1 MGC"))
