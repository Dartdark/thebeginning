"""Personal-account portfolio from everything tested so far (user, 2026-10-23: 'what would my personal portfolio look
like, with plan numbers'). No Apex rules: overnight holds allowed, no trailing limit, no payout cap.
Pieces (daily $ per 1 micro, 2018-01 -> 2026-10, after costs):
  - the 10 funded-plan strategies (agents/tasks/plan_daily_pnl.csv; RS both sides; CL fade per MCL, ES MOC per MES)
  - FC 2B v2 (checks/candidates/fc_2b/trades.csv = MultiCharts v2 trades after $7.25 + 1 tick, per NQ / 10)
  - Twin Continuation v2.1 (checks/candidates/twin_continuation/trades.csv, per NQ / 10; holds overnight, uncapped stop)
  - Kusho v9 21:00 (roll-adjusted, checks/candidates/kusho/python_trades_v9_rolladj.csv, booked on the exit day) and S47 v2
    (checks/candidates/s47_v2/python_trades_v2.csv), per NQ / 10; added 2026-10-24 (user), still forward-logged
  - Dual Thrust v4 (checks/candidates/dual_thrust/trades.csv = rebuild analysis/dual_thrust_test.py, per NQ / 10; added
    2026-10-24, user)
  - Overnight TickRSV / VIX (checks/candidates/overnight_tick/trades.csv, per NQ / 10; replaced Overnight Anomaly 2026-10-24, user)
  - (until 2026-10-24) OvernightAnomaly v4.1 = Block B of the user's merged file (checks/candidates/overnight_anomaly/trades.csv, rebuild
    analysis/overnight_anomaly_test.py, per NQ / 10; long 17:30 -> 02:30 CT after a down RTH day; added 2026-10-24, user)
Micro costs: the repo's per-NQ costs / 10 give $0.725 commission per round trip; real micro commissions are ~$1.25, so
$0.55 more is charged per micro trade (plan pieces: per day with a trade, a slight underestimate for VB's re-entries).
Portfolio = every piece at 1 micro. Sizing: Davey (size for half the drawdown you think you can take) and Radge
(max DD ~ 1.7-2 x annual volatility): capital so the 1-year Monte Carlo p95 drawdown is <= 20% of it.
  python3 analysis/personal_portfolio.py
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, montecarlo as MC

EXTRA = 0.55


def twin_marked(days, path="checks/candidates/twin_continuation/trades.csv", sp="scratch_data/"):
    """Twin v1 ledger with open overnight positions marked at each session's 16:00 CT close (2026-10-24, cross-review
    2026-10-23 open item). A trade's session = its date, or the next date when it is after 16:00 CT. Each mark books the
    price change since the last mark; costs and slippage (net - gross) go on the exit day, so the sum equals the ledger."""
    import pickle
    from grid24 import jof
    g = pickle.load(open(sp + "g24.pkl", "rb")); cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    row = pd.Series(np.arange(len(g.ts)), index=pd.DatetimeIndex(g.ts))
    has = ~np.isnan(g.c[:, jof(1530):jof(1600) + 1]).all(axis=1)          # a session with an afternoon close
    t = pd.read_csv(path, parse_dates=["date", "entry_date"]); t = t[t.date <= days[-1]]
    sess = lambda d, hm: d + pd.to_timedelta((hm > 1600).astype(int), unit="D")
    s0, s1 = sess(t.entry_date, t.entry_time_ct), sess(t.date, t.exit_time_ct)
    book = []
    for r, a, b in zip(t.itertuples(), s0, s1):
        last, gross = r.entry, 0.0
        for d in pd.date_range(a, b - pd.Timedelta(days=1)):
            i = row.get(d)
            if i is None or not has[i]: continue
            m = cf[i * 1440 + jof(1600)]; x = (m - last) * r.side * 20 / 10; book.append((d, x)); gross += x; last = m
        book.append((b, r.net / 10 - gross - EXTRA))
    k = days.searchsorted(pd.DatetimeIndex([d for d, _ in book])); k = np.minimum(k, len(days) - 1)
    out = pd.Series([x for _, x in book], index=days[k]).groupby(level=0).sum().reindex(days, fill_value=0.0)
    assert abs(out.sum() - (t.net / 10 - EXTRA).sum()) < 1e-6
    return out.rename("TwinContinuation")

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    p = pd.read_csv("agents/tasks/plan_daily_pnl.csv", parse_dates=["date"]).set_index("date")
    p = p - EXTRA * (p != 0)
    days = p.index
    def to_trading_day(d):
        # book each exit on the next plan trading day on or after its calendar date (Sunday-evening exits -> Monday,
        # market-closed weekdays -> the next session); fix 2026-10-23 after Codex's cross-review (9 Twin exits were dropped)
        k = days.searchsorted(pd.DatetimeIndex(d)); k = np.minimum(k, len(days) - 1); return days[k]
    def from_trades(path, nm, df=None):
        t = df if df is not None else pd.read_csv(path, parse_dates=["date"]); t = t[pd.DatetimeIndex(t.date) <= days[-1]]
        x = (t.net / 10 - EXTRA).to_numpy()
        out = pd.Series(x, index=to_trading_day(t.date)).groupby(level=0).sum().reindex(days, fill_value=0.0).rename(nm)
        assert abs(out.sum() - x.sum()) < 1e-6, nm      # every trade booked, none dropped
        return out, len(t)
    fc, nfc = from_trades("checks/candidates/fc_2b/trades.csv", "FC2B")
    # Twin: no v2.1 ledger exists. Main = the Python port v1 (checker ledger, 1,074 trades; has 4 holiday carries v2.1 removes);
    # sensitivity = the MultiCharts v2 report (MC-confirmed; v2.1 differs by its evening SetExitOnClose and holiday fixes).
    tw, ntw = from_trades("checks/candidates/twin_continuation/trades.csv", "TwinContinuation")
    raw = pd.read_excel("mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Twin Continuation v2.xlsx", sheet_name="List of Trades", header=2)
    en = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True); ex = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    sd = np.where(en.Type.str.contains("Long"), 1, -1)
    tmc = pd.DataFrame(dict(date=pd.to_datetime(ex.Date).dt.normalize(), net=(ex.Price.astype(float) - en.Price.astype(float)) * sd * 20 - 7.25 - 2 * 0.25 * 20))
    tmc = tmc[tmc.date >= "2018-01-01"]
    tw_mc, _ = from_trades(None, "TwinContinuation", tmc)
    tw_exit = tw.copy()
    tw = twin_marked(days)          # main since 2026-10-24: overnight holds marked at each 16:00 CT close (was booked at exit)
    oa, noa = from_trades("checks/candidates/overnight_anomaly/trades.csv", "OvernightAnomaly")
    dth, ndt = from_trades("checks/candidates/dual_thrust/trades.csv", "DualThrust")    # added 2026-10-24 (user)
    # Kusho v9 (21:00 exit, weekend holds; roll-adjusted rule, booked on its exit day) and S47 v2: added 2026-10-24 (user),
    # both still on the forward log (agents/codex/FORWARD_LOG.md)
    k21 = pd.read_csv("checks/candidates/kusho/python_trades_v9_rolladj.csv", parse_dates=["date", "exit_date"])
    ku, nku = from_trades(None, "Kusho", k21.assign(date=k21.exit_date))
    s47, ns47 = from_trades("checks/candidates/s47_v2/python_trades_v2.csv", "S47")
    # S30 IBS reversal (NQ + ES long, holds days, daily marked): added 2026-10-24 (user), still on the forward log
    s30 = pd.read_csv("checks/candidates/s30_ibs/daily_nq_es_per_micro.csv", index_col=0, parse_dates=True).iloc[:, 0].reindex(days, fill_value=0.0).rename("S30")
    # Overnight TickRSV / VIX replaced Overnight Anomaly 2026-10-24 (user; MultiCharts-confirmed; checks/candidates/overnight_tick/).
    # Its order-flow input ends 2026-07-07, so no trades after that in this backtest.
    otv, notv = from_trades("checks/candidates/overnight_tick/trades.csv", "OvernightTick")
    P = pd.concat([p, fc, tw, otv, dth, ku, s47, s30], axis=1)
    names = {"VaultBreak": "Vault Break", "OvernightBiasML": "ONB ML", "MondayLong": "Monday Long", "ExpirationOpenShort": "EOS",
             "LateDayFlow": "Late-Day Flow", "NFPFade": "NFP Fade", "BridgeMondayLong": "Bridge Monday", "CLSundayFade_perMCL": "CL Sunday (MCL)",
             "ESMOCFollow_perMES": "ES MOC (MES)", "RelativeStrength": "Relative Strength", "FC2B": "FC 2B", "TwinContinuation": "Twin Continuation",
             "OvernightTick": "Overnight Tick / VIX", "DualThrust": "Dual Thrust",
             "Kusho": "Kusho v9", "S47": "S47 v2", "S30": "S30 IBS (NQ + ES)"}
    yrs = len(P) / 252
    print(f"\n1. Pieces at 1 micro each, {days.min().date()} -> {days.max().date()} ({yrs:.1f} years), after micro costs:")
    rows = []
    for c in P:
        x = P[c]; e = x.cumsum(); a = x[x.index.year >= 2023]
        rows.append(dict(piece=names[c], per_year=x.sum() / yrs, y2023=a.sum() / (len(a) / 252), max_dd=-(e - e.cummax()).min(),
                         sharpe=x.mean() / x.std() * np.sqrt(252), days=int((x != 0).sum())))
    t = pd.DataFrame(rows).set_index("piece")
    print(t.to_string(formatters={"per_year": "${:,.0f}".format, "y2023": "${:,.0f}".format, "max_dd": "${:,.0f}".format, "sharpe": "{:.2f}".format}))

    tot = P.sum(axis=1)
    print("\n2. Whole portfolio, every piece at 1 micro:")
    e = tot.cumsum(); dd = (e - e.cummax()).min(); m = tot.resample("ME").sum(); yv = tot.std() * np.sqrt(252)
    print(f"   ${tot.sum() / yrs:,.0f} a year | max DD ${-dd:,.0f} | worst month ${m.min():,.0f} | losing months {np.mean(m < 0):.0%} | "
          f"annual volatility ${yv:,.0f}")
    print("   by year:", {k: f"${v:,.0f}" for k, v in tot.groupby(tot.index.year).sum().items()})
    print(M.table({"portfolio": (tot, tot[tot != 0]), "  2023+": (tot[tot.index >= "2023-01-01"], tot[(tot != 0) & (tot.index >= "2023-01-01")])}))
    dm = MC.daily_mc(tot.values, horizon=252, n=5000, block=20, trail=1e12)
    print(f"   Monte Carlo, 1 year (20-day blocks): P&L p5 ${dm['pnl_p5']:,.0f} / p50 ${dm['pnl_p50']:,.0f} / p95 ${dm['pnl_p95']:,.0f}, "
          f"P(losing year) {dm['p_loss']:.1%}, max DD p50 ${dm['dd_p50']:,.0f} / p95 ${dm['dd_p95']:,.0f}, return/DD {dm['ret_dd']:.1f}")
    print("\n   Correlation of daily P&L (pieces with the rest of the portfolio):")
    print("   " + ", ".join(f"{names[c]} {np.corrcoef(P[c], tot - P[c])[0, 1]:+.2f}" for c in P))

    print("\n3. Sizing (capital so the 1-year MC p95 drawdown <= 20%; historical max DD shown as % of it):")
    for cap in (10000, 15000, 20000, 25000, 50000):
        k = max(1, int(np.floor(0.20 * cap / dm["dd_p95"] + 1e-9)))
        print(f"   ${cap:>6,}: {k} x the 1-micro portfolio -> ${k * dm['pnl_p50']:,.0f} a year (p50, {k * dm['pnl_p50'] / cap:.0%}), "
              f"p5 ${k * dm['pnl_p5']:,.0f}, DD p95 ${k * dm['dd_p95']:,.0f} ({k * dm['dd_p95'] / cap:.0%}), worst historical DD {k * -dd / cap:.0%}")
    need = dm["dd_p95"] / 0.20
    print(f"   capital for 1x at the 20% rule: ${need:,.0f}")

    t16 = tot - P["S30"]; d16 = MC.daily_mc(t16.values, horizon=252, n=5000, block=20, trail=1e12); e16 = t16.cumsum()
    print(f"   before S30 (16 pieces): ${t16.sum() / yrs:,.0f} a year, Sharpe {t16.mean() / t16.std() * np.sqrt(252):.2f}, "
          f"max DD ${-(e16 - e16.cummax()).min():,.0f}, MC p50 ${d16['pnl_p50']:,.0f}, DD p95 ${d16['dd_p95']:,.0f}, return/DD {d16['ret_dd']:.1f}, "
          f"capital at the 20% rule ${d16['dd_p95'] / 0.20:,.0f}")
    t14 = t16 - P["Kusho"] - P["S47"]; d14 = MC.daily_mc(t14.values, horizon=252, n=5000, block=20, trail=1e12); e14 = t14.cumsum()
    print(f"   before Kusho + S47 (14 pieces): ${t14.sum() / yrs:,.0f} a year, Sharpe {t14.mean() / t14.std() * np.sqrt(252):.2f}, "
          f"max DD ${-(e14 - e14.cummax()).min():,.0f}, MC p50 ${d14['pnl_p50']:,.0f}, DD p95 ${d14['dd_p95']:,.0f}, return/DD {d14['ret_dd']:.1f}, "
          f"capital at the 20% rule ${d14['dd_p95'] / 0.20:,.0f}")
    t13 = t14 - P["DualThrust"]; d13 = MC.daily_mc(t13.values, horizon=252, n=5000, block=20, trail=1e12); e13 = t13.cumsum()
    print(f"   before Dual Thrust (13 pieces): ${t13.sum() / yrs:,.0f} a year, Sharpe {t13.mean() / t13.std() * np.sqrt(252):.2f}, "
          f"max DD ${-(e13 - e13.cummax()).min():,.0f}, MC p50 ${d13['pnl_p50']:,.0f}, DD p95 ${d13['dd_p95']:,.0f}, return/DD {d13['ret_dd']:.1f}, "
          f"capital at the 20% rule ${d13['dd_p95'] / 0.20:,.0f}")
    alt = tot - P["OvernightTick"] + oa; da = MC.daily_mc(alt.values, horizon=252, n=5000, block=20, trail=1e12); ea = alt.cumsum()
    print(f"   with Overnight Anomaly instead (before 2026-10-24): ${alt.sum() / yrs:,.0f} a year, Sharpe {alt.mean() / alt.std() * np.sqrt(252):.2f}, "
          f"max DD ${-(ea - ea.cummax()).min():,.0f}, DD p95 ${da['dd_p95']:,.0f}, return/DD {da['ret_dd']:.1f}, capital ${da['dd_p95'] / 0.20:,.0f}")
    t12 = t13 - P["OvernightTick"]; d12 = MC.daily_mc(t12.values, horizon=252, n=5000, block=20, trail=1e12); e12 = t12.cumsum()
    print(f"   without the overnight-anomaly piece (12 pieces): ${t12.sum() / yrs:,.0f} a year, Sharpe {t12.mean() / t12.std() * np.sqrt(252):.2f}, "
          f"max DD ${-(e12 - e12.cummax()).min():,.0f}, MC p50 ${d12['pnl_p50']:,.0f}, DD p95 ${d12['dd_p95']:,.0f}, return/DD {d12['ret_dd']:.1f}, "
          f"capital at the 20% rule ${d12['dd_p95'] / 0.20:,.0f}")

    print("\n4. Without Twin Continuation (its uncapped swing stop is the biggest single-trade risk):")
    t2 = tot - P["TwinContinuation"]; d2 = MC.daily_mc(t2.values, horizon=252, n=5000, block=20, trail=1e12); e2 = t2.cumsum()
    print(f"   ${t2.sum() / yrs:,.0f} a year, max DD ${-(e2 - e2.cummax()).min():,.0f}, MC p50 ${d2['pnl_p50']:,.0f}, DD p95 ${d2['dd_p95']:,.0f}, "
          f"return/DD {d2['ret_dd']:.1f}, capital at the 20% rule ${d2['dd_p95'] / 0.20:,.0f}")
    for nm_, twx in (("Twin = MultiCharts v2 report", tw_mc), ("Twin booked at exit (before 2026-10-24)", tw_exit)):
        alt = tot - P["TwinContinuation"] + twx; da = MC.daily_mc(alt.values, horizon=252, n=5000, block=20, trail=1e12); ea = alt.cumsum()
        print(f"   full 16 with {nm_}: ${alt.sum() / yrs:,.0f} a year, max DD ${-(ea - ea.cummax()).min():,.0f}, MC p50 ${da['pnl_p50']:,.0f}, "
              f"DD p95 ${da['dd_p95']:,.0f}, capital at the 20% rule ${da['dd_p95'] / 0.20:,.0f} (Twin alone ${twx.sum() / yrs:,.0f} a year vs port ${P['TwinContinuation'].sum() / yrs:,.0f})")
    print(f"   worst single Twin trade per MNQ ${pd.read_csv('checks/candidates/twin_continuation/trades.csv').net.min() / 10:,.0f}; "
          f"worst portfolio day ${tot.min():,.0f}")

    print("\n5. Starter sets for a smaller account (1 micro each; capital at the 20% rule), then add pieces as it grows:")
    sets = {"A. 5 pieces: Twin, ONB ML, Bridge, CL Sunday, NFP": ["TwinContinuation", "OvernightBiasML", "BridgeMondayLong", "CLSundayFade_perMCL", "NFPFade"],
            "B. 6 pieces: A + EOS": ["TwinContinuation", "OvernightBiasML", "BridgeMondayLong", "CLSundayFade_perMCL", "NFPFade", "ExpirationOpenShort"],
            "C. 7 pieces: B + Vault Break": ["TwinContinuation", "OvernightBiasML", "BridgeMondayLong", "CLSundayFade_perMCL", "NFPFade", "ExpirationOpenShort", "VaultBreak"],
            "D. 9 pieces: C + RS + ES MOC": ["TwinContinuation", "OvernightBiasML", "BridgeMondayLong", "CLSundayFade_perMCL", "NFPFade", "ExpirationOpenShort", "VaultBreak", "RelativeStrength", "ESMOCFollow_perMES"]}
    for nm, ks in sets.items():
        x = P[ks].sum(axis=1); d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
        print(f"   {nm:<52} ${x.sum() / yrs:,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():,.0f}, "
              f"MC p5 / p50 ${d['pnl_p5']:,.0f} / ${d['pnl_p50']:,.0f}, DD p95 ${d['dd_p95']:,.0f} -> capital ${d['dd_p95'] / 0.20:,.0f}")

    print("\n6. S30 IBS reversal (NQ + ES, 1 micro each; daily marked; in the plan since 2026-10-24): with and without it")
    for nm, base in (("full 16 (no S30)", tot - s30), ("set D (9)", P[["TwinContinuation", "OvernightBiasML", "BridgeMondayLong", "CLSundayFade_perMCL", "NFPFade",
                                                         "ExpirationOpenShort", "VaultBreak", "RelativeStrength", "ESMOCFollow_perMES"]].sum(axis=1))):
        for lab_, x in ((nm, base), (nm + " + S30", base + s30)):
            d = MC.daily_mc(x.values, horizon=252, n=5000, block=20, trail=1e12); e = x.cumsum()
            print(f"   {lab_:<18} ${x.sum() / yrs:,.0f} a year, Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}, max DD ${-(e - e.cummax()).min():,.0f}, "
                  f"MC p50 ${d['pnl_p50']:,.0f}, DD p95 ${d['dd_p95']:,.0f}, return/DD {d['ret_dd']:.1f}, capital at the 20% rule ${d['dd_p95'] / 0.20:,.0f}")
    print(f"   S30 corr with the rest of the portfolio: {np.corrcoef(s30, tot - s30)[0, 1]:+.2f}")
