"""Ricochet 1144 (user upload 2026-11-04; author's MultiCharts code checks/candidates/ricochet_1144/S1144_signal_multicharts.txt +
research note; Hu, Jin, Wang 2025 'after down days rebounds are more likely'). Port of the code on 1-minute NQ data:
  signal: yesterday's valid regular session (open = close of the 08:30 bar, close = close of the 15:00 bar, or 12:00 on half days;
  holidays from the code's own list) closed below its open;
  base: LONG at the close of the 17:05 bar (first 5-min bar of the CME session) unless the session is a listed holiday;
  stop 50 / target 100 pts (intrabar on the 1-minute path; a minute opening beyond a level exits at its open);
  re-entries (max 4 trades a session): after an exit, from the 2nd 5-min bar after the exit bar, LONG at the close of the first 5-min
  bar with Low <= S1 + 0.15 x ATR14(yesterday) and Close > S1 (S1 = 2P - H, P = (H+L+C)/3 of yesterday's 08:35-15:00 session);
  time exit: close of the 15:00 bar. Costs $7.25 + 1 tick per market / stop fill (target = limit). Per 1 NQ.
  Author's split: development 2017 -> 2022-10-25, out of sample 2022-10-26 ->.
  python3 analysis/ricochet_1144_test.py > analysis/outputs/ricochet_1144_test_output.txt
"""
import sys, re, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M

PV, TICK, COMM = 20.0, 0.25, 7.25
SRC = open("checks/candidates/ricochet_1144/S1144_signal_multicharts.txt", encoding="latin-1").read()
FESTE = {20000000 + int(x) - 1000000 for x in re.findall(r"Feste\[\d+\] = (\d{7})", SRC)}
SENZA = {20000000 + int(x) - 1000000 for x in re.findall(r"Senza830\[\d+\] = (\d{7})", SRC)}
g = pickle.load(open("scratch_data/g24_ext.pkl", "rb"))
O, H, L, C = g.o, g.h, g.l, g.c
SPLIT = pd.Timestamp("2022-10-26")


def bar5(r, hhmm):
    """5-min bar closing at hhmm on calendar row r: (low, close, has)."""
    j = jof(hhmm); seg = slice(max(0, j - 4), j + 1)
    if np.isnan(C[r, seg]).all(): return np.nan, np.nan, False
    c = C[r, seg]; return np.nanmin(L[r, seg]), c[~np.isnan(c)][-1], True


def regular_sessions():
    """{calendar row: (open, high, low, close)} of valid regular sessions, and ATR14 (pandas ewm adjust=False) after each."""
    out = {}; atr = None; prev_c = None; n = 0
    for r in range(g.D):
        dte = int(g.dates[r])
        if dte in FESTE or pd.Timestamp(str(dte)).dayofweek >= 5: continue
        _, c830, h830 = bar5(r, 830); _, c1200, h1200 = bar5(r, 1200); _, c1500, h1500 = bar5(r, 1500)
        if not h830 or not (h1200 or h1500): continue
        seg = slice(jof(831), jof(1500) + 1)
        if np.isnan(H[r, seg]).all(): continue
        hi, lo = np.nanmax(H[r, seg]), np.nanmin(L[r, seg]); cl = c1500 if h1500 else c1200
        n += 1
        tr = hi - lo if prev_c is None else max(hi - lo, abs(hi - prev_c), abs(lo - prev_c))
        atr = tr if atr is None else (1 - 1 / 14) * atr + (1 / 14) * tr
        out[r] = dict(o=c830, h=hi, l=lo, c=cl, atr=atr if n >= 14 else None)
        prev_c = cl
    return out


def run(max_trades=4, stop=50.0, target=100.0, marg=0.15, pause=1, reentry=True, signal="red"):
    REG = regular_sessions(); regs = sorted(REG)
    rows = []
    for d in range(1, g.D):
        sess = int(g.dates[d])
        if sess in FESTE or sess in SENZA or pd.Timestamp(str(sess)).dayofweek >= 5: continue
        # the session runs 17:00 on the previous calendar row -> 16:00 on row d; Monday's starts on Sunday's row
        p = d - 1
        prior = [r for r in regs if r < d]
        if not prior: continue
        y = REG[prior[-1]]
        red = y["c"] < y["o"]
        take = red if signal == "red" else (not red if signal == "green" else True)
        if not take: continue
        _, c1705, has = bar5(p, 1705)
        if not has: continue
        S1 = 2 * (y["h"] + y["l"] + y["c"]) / 3 - y["h"]; mg = marg * y["atr"] if y["atr"] else 0.0
        # minute sequence of the session: (row, col)
        mins = [(p, j) for j in range(jof(1706), 1440)] + [(d, j) for j in range(0, jof(1500) + 1)]
        bars_end = {(p, j) for j in range(jof(1705), 1440, 5)} | {(d, j) for j in range(0, jof(1500) + 1, 5)}
        pos = True; e = c1705 + TICK; n_tr = 1; exit_bar = None; bar_i = 0
        for (r, j) in mins:
            if (r, j) in bars_end: bar_i += 1
            if pos:
                o_, h_, l_ = O[r, j], H[r, j], L[r, j]
                if not np.isnan(o_):
                    sp, tp = e - stop, e + target
                    if l_ <= sp:
                        x = min(o_, sp) - TICK; rows.append((sess, n_tr, e, x, "stop")); pos = False; exit_bar = bar_i
                    elif h_ >= tp:
                        x = max(o_, tp); rows.append((sess, n_tr, e, x, "target")); pos = False; exit_bar = bar_i
            if (r, j) in bars_end:
                if r == d and j == jof(1500):
                    if pos: rows.append((sess, n_tr, e, C[r, j] - TICK if not np.isnan(C[r, j]) else e, "time")); pos = False
                    break
                if not pos and reentry and exit_bar is not None and n_tr < max_trades and bar_i >= exit_bar + 1 + pause:
                    lo5, c5, ok = bar5(r, int(j // 60 * 100 + j % 60))
                    if ok and lo5 <= S1 + mg and c5 > S1:
                        n_tr += 1; e = c5 + TICK; pos = True; exit_bar = None
        if pos:
            cc = C[d, :jof(1500) + 1]; cc = cc[~np.isnan(cc)]
            rows.append((sess, n_tr, e, (cc[-1] if len(cc) else e) - TICK, "time (no 15:00 bar)"))
    t = pd.DataFrame(rows, columns=["session", "n", "entry", "exit", "kind"])
    t["date"] = pd.to_datetime(t.session.astype(str)); t["net"] = (t.exit - t.entry) * PV - COMM
    return t


def rows_open(rows, sess):
    return any(r[0] == sess for r in rows)


def tst(x): x = pd.Series(x); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def line(t, nm):
    s = t.groupby("date").net.sum(); a, b = t[t.date < SPLIT], t[t.date >= SPLIT]
    sa, sb = a.groupby("date").net.sum(), b.groupby("date").net.sum()
    pf = t.net[t.net > 0].sum() / -t.net[t.net < 0].sum()
    by = t.groupby(t.date.dt.year).net.sum()
    return (f"   {nm:<38} n={len(t):5d} ${t.net.mean():6.1f} PF {pf:4.2f} t(sessions) {tst(s):4.2f} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | dev ${a.net.mean():6.1f} t {tst(sa):4.2f} | OOS ${b.net.mean():6.1f} t {tst(sb):4.2f} n {len(b)}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    T = run(); T.to_csv("checks/candidates/ricochet_1144/python_trades.csv", index=False)
    T = T[T.date >= "2017-06-01"]
    print(f"\nHolidays parsed from the code: {len(FESTE)}; excluded 2020 sessions: {len(SENZA)}; data to {T.date.max().date()}")
    print("\n1. As coded vs the author's note (note: 2,238 trades, $105.54, dev $130.00 t 3.73 / OOS $78.85 t 1.95, 1,070 OOS trades):")
    print(line(T, "as coded (ours)"))
    print("   exits:", T.kind.value_counts().to_dict())
    print("   by year $:", T.groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("   by trade number (dev $ / OOS $):", {n: (int(T[(T.n == n) & (T.date < SPLIT)].net.sum()), int(T[(T.n == n) & (T.date >= SPLIT)].net.sum())) for n in (1, 2, 3, 4)})
    print("\n2. Controls:")
    for nm, kw in (("base trade only (no re-entries)", dict(reentry=False)), ("max 2 trades", dict(max_trades=2)),
                   ("after an UP day instead (placebo)", dict(signal="green")), ("every session (no signal)", dict(signal="all"))):
        print(line(run(**kw).query("date >= '2017-06-01'"), nm))
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[(days >= "2018-01-01") & (days <= T.date.max())]
    x = T.groupby("date").net.sum().reindex(days, fill_value=0.0)
    rows = {"2018-26": (x, T[T.date >= "2018"].set_index("date").net), "OOS 2022-10-26+": (x[x.index >= SPLIT], T[T.date >= SPLIT].set_index("date").net)}
    print("\n3. Metrics per NQ (daily, 2018+):"); print(M.table(rows))
    pickle.dump(x, open("scratch_data/ricochet_daily.pkl", "wb"))

    # 4. Personal book (user's pre-screen guide + bench), 1 MNQ
    import io, runpy, contextlib, montecarlo as MC, bridge_noise_15m_mc_check as K
    with contextlib.redirect_stdout(io.StringIO()):
        gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
    P, pdays, ft = gg["P"].copy(), gg["days"], gg["from_trades"]
    A = K.load("RTH Anchor"); P["NoiseLongs"], _ = ft(None, "NBL", A[A.side > 0][["date", "net"]])
    o, _ = ft(None, "RICO", T[["date", "net"]]); tot = P.sum(axis=1); yrs = len(pdays) / 252
    sh = lambda v: v.mean() / v.std() * np.sqrt(252)
    print(f"\n4. Personal book ({P.shape[1]} pieces at 1 micro): Ricochet 1 MNQ ${o.sum() / yrs:,.0f} a year, Sharpe {sh(o):.2f}, "
          f"corr with the book {np.corrcoef(o, tot)[0, 1]:+.2f}; guide hurdle {sh(tot):.2f} x corr = {sh(tot) * np.corrcoef(o, tot)[0, 1]:.2f}")
    print("   corr with pieces >= 0.15:", {c: round(float(np.corrcoef(o, P[c])[0, 1]), 2) for c in P if abs(np.corrcoef(o, P[c])[0, 1]) >= 0.15})
    for nm, xx in (("current book", tot), ("+ Ricochet 1", tot + o), ("Overnight Tick -> Ricochet 1", tot - P["OvernightTick"] + o)):
        dd = MC.daily_mc(xx.values, horizon=252, n=5000, block=20, trail=1e12); e = xx.cumsum()
        print(f"   {nm:<30} ${xx.sum() / yrs:>7,.0f} a year, Sharpe {sh(xx):.2f}, max DD ${-(e - e.cummax()).min():>6,.0f}, "
              f"MC p50 ${dd['pnl_p50']:>7,.0f}, DD p95 ${dd['dd_p95']:>6,.0f}, return/DD {dd['ret_dd']:.1f}")
