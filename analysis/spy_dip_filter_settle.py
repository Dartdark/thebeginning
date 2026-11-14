"""FIX 2026-11-14 (checker): the trailing best/peak close was keyed by id(pos), which Python reuses after a trade ends (1,072 of 1,116 ES trades started from an old best); now stored on the position.
Settle the ES dip-buy volatility filter (user 2026-11-14 'yes, settle it'). Two choices changed the result:
 1. which DAY a trade belongs to: the calendar date of the entry (the bench) or the CME session (17:00 CT start; an evening entry
    belongs to the next session, so its 'last close' is today's close, the freshest value known at 17:00, no look-ahead)
 2. WHERE the filter acts: dropping finished trades from the unfiltered list (the bench and the sweep) or blocking the SIGNAL so the
    strategy can take the next one (what live code does)
All four on ES (VIX/VIX3M rising -> skip) and NQ (VXN rising -> skip), overnight version as coded, per micro after costs. The live-
implementable one is session + signal. Then: the sweep's fair placebo on session dating (entry_date = session date) and the
personal bench with the session + signal ES series vs the bench's version.
  tools/run_stamped.sh analysis/spy_dip_filter_settle.py > analysis/outputs/spy_dip_filter_settle_output.txt
"""
import sys, subprocess, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
src = open("analysis/jesse_lib_btc_test.py", encoding="utf-8").read().split("adx_ref = P.run(P.setup())")[0]
E = {"__name__": "lib", "__doc__": "x\n"}; exec(compile(src, "jesse_lib_engine", "exec"), E)
np, pd = E["np"], E["pd"]; atr, dmi, ema, simulate, tt, htf_at = (E[k] for k in ("atr", "dmi", "ema", "simulate", "tt", "htf_at"))
print(__doc__.split("\n")[0])
import co_oc_reversal_test as CO, roll_adjust as RA
from new_data_screen import RULES, prior
from data_sweep import series
SR = series()


def supertrend(bb, period, factor):
    Hh, Ll, Cc = bb.high.to_numpy(), bb.low.to_numpy(), bb.close.to_numpy(); a = atr(bb, period); hl2 = (Hh + Ll) / 2
    ub = hl2 + factor * a; lb = hl2 - factor * a; fu = ub.copy(); fl = lb.copy(); st = np.full(len(Cc), np.nan); up = True
    for i in range(1, len(Cc)):
        if np.isnan(a[i]): continue
        if not np.isnan(fu[i - 1]):
            fu[i] = ub[i] if (ub[i] < fu[i - 1] or Cc[i - 1] > fu[i - 1]) else fu[i - 1]
            fl[i] = lb[i] if (lb[i] > fl[i - 1] or Cc[i - 1] < fl[i - 1]) else fl[i - 1]
        if up and Cc[i] < fl[i]: up = False
        elif not up and Cc[i] > fu[i]: up = True
        st[i] = fl[i] if up else fu[i]
    return st


def spy(sym):
    g = CO.load(sym); c = g.c.ravel().astype(float); o = g.o.ravel().astype(float); h = g.h.ravel().astype(float); l = g.l.ravel().astype(float)
    J = RA.roll_jumps(g, sym); adj = np.zeros(len(c))
    for jj, jump in J.items(): adj[:jj] += jump
    ok = ~np.isnan(c); ts = (pd.to_datetime(np.repeat(g.ts, 1440)) + pd.to_timedelta(np.tile(np.arange(1440), len(g.ts)), "m") - pd.Timedelta(minutes=1))[ok]
    mm = pd.DataFrame({"open": o[ok] + adj[ok], "high": h[ok] + adj[ok], "low": l[ok] + adj[ok], "close": c[ok] + adj[ok]}, index=ts); mm = mm[mm.index >= "2017-06-01"]
    E["MT"], E["MO"], E["MH"], E["ML"] = mm.index.values, mm.open.to_numpy(), mm.high.to_numpy(), mm.low.to_numpy(); E["FEE"], E["SLIP"] = 0.0, 0.0
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    b = mm.resample("1h", label="left", closed="left").agg(agg).dropna(); h4 = mm.resample("4h", label="left", closed="left").agg(agg).dropna()
    C = b.close.to_numpy(); A1 = atr(b); L4 = htf_at(b, h4, supertrend(h4, 22, 2.0)); A4 = htf_at(b, h4, atr(h4)); X4 = htf_at(b, h4, dmi(h4)[2])
    e18, e40 = ema(C, 18), ema(C, 40)
    sig = np.where((C > L4) & (C < e18), 1, np.where((C < L4) & (X4 > 22) & (C > e40), -1, 0)); sig[np.isnan(L4) | np.isnan(A4)] = 0
    bs = {}
    def mg(j, pos, event=None):
        s = pos["s"]; bb_ = pos.get("_best", pos["e"]); bb_ = max(bb_, C[j]) if s == 1 else min(bb_, C[j]); pos["_best"] = bb_
        if s == 1: pos["stop"] = max(pos["stop"], min(bb_ - 3 * A4[j], C[j] - 0.5 * A1[j]))
        else: pos["stop"] = min(pos["stop"], max(bb_ + 3 * A4[j], C[j] + 0.5 * A1[j]))
    plan = lambda i, s, e: (e - 1.5 * A4[i], None) if s == 1 else (e + 0.75 * A4[i], e - 2.5 * A4[i])
    return b, sig, plan, mg


SPEC = {"ES": (50.0, 5.0, 12.5, "VIX/VIX3M (term structure)"), "NQ": (20.0, 7.25, 5.0, "VXN")}
OUT = {}
for sym, (pv, comm, tk, filt) in SPEC.items():
    b, sig, plan, mg = spy(sym)
    entry_t = b.index + pd.Timedelta(hours=1)                                           # entry at the 1h close
    cal = pd.DatetimeIndex(entry_t.normalize()); ses = pd.DatetimeIndex((entry_t + pd.Timedelta(hours=7)).normalize())
    rise = {"calendar": prior(SR[filt], cal, RULES["rising"]) == 1, "session": prior(SR[filt], ses, RULES["rising"]) == 1}
    run = lambda s_, seed=None: simulate(b, s_, plan, manage=mg, seed=seed)
    usd = lambda t: (t.ret * t.e * pv - comm - tk - np.where(t.why == "target", 0.0, tk)) / 10 - 0.55
    T0 = run(sig); bi = np.searchsorted(b.index.values, T0.t.values)
    print(f"\n[{sym}] filter: {filt} rising -> skip; unfiltered {len(T0)} trades, ${usd(T0).mean():.2f} per micro, t {tt(usd(T0)):.2f}")
    for day in ("calendar", "session"):
        for lvl in ("drop trades", "block signals"):
            if lvl == "drop trades": t = T0[~rise[day][bi]].reset_index(drop=True)
            else: t = run(np.where(rise[day], 0, sig))
            x = usd(t); yrs = (t.t.max() - t.t.min()).days / 365.25; e = x.groupby(t.tx.dt.normalize()).sum().cumsum()
            print(f"   {day:<9} {lvl:<14} {len(t):5d} trades, ${x.mean():6.2f} per micro, PF {x[x > 0].sum() / -x[x < 0].sum():.2f}, t {tt(x):5.2f} | 2018-22 t {tt(x[t.yr <= 2022]):5.2f} | 2023+ t {tt(x[t.yr >= 2023]):5.2f} | "
                  f"${x.sum() / yrs:,.0f} a year, max DD ${(e - e.cummax()).min():,.0f}")
            OUT[(sym, day, lvl)] = t.assign(usd=x)
    # sweep input on session dating (unfiltered trades, entry_date = session date)
    pd.DataFrame({"date": T0.tx.dt.normalize().dt.date, "entry_date": ((T0.t + pd.Timedelta(hours=8)).dt.normalize()).dt.date, "net": usd(T0)}).to_csv(f"scratch_data/sweep_inputs/spy_{sym}_session.csv", index=False)
    OUT[(sym, "session", "block signals")].to_csv(f"scratch_data/spy_dip_{sym}_session_signal.csv", index=False)
for sym in ("ES", "NQ"):
    r = subprocess.run([sys.executable, "analysis/strategy_data_sweep.py", f"scratch_data/sweep_inputs/spy_{sym}_session.csv", f"spy_{sym}_session"], capture_output=True, text=True, encoding="utf-8")
    lines = [l for l in r.stdout.splitlines() if ("VIX/VIX3M" in l or "VXN " in l or "BEST VERSION" in l or "trade days" in l)]
    print(f"\nsweep on SESSION dating, {sym}:"); print("\n".join("   " + l.strip()[:200] for l in lines[:8]))
