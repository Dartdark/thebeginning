"""Bridge 'noise area' NQ 15-min (Zarattini / Aziz / Barbon intraday momentum; user's upload 2026-11-03, the Bridge's code).
Bar-by-bar port of the posted PowerLanguage, per NQ (ContractsPerTrade 2 = 2 NQ in the file; results here per 1 NQ):
  TodayOpen = Open of the first bar of the DATE, PrevClose = Close of the bar before it (Date <> Date[1]);
  slot k = 15-min bar closing 09:00 + 15(k-1) (k 1..22 = 09:00 .. 14:15; the 14:30 bar is slot 23 and is skipped by
  'Slot <= 22'); move = |Close / TodayOpen - 1|; band = mean of that slot's previous 20 moves (needs 20 stored);
  UB = max(TodayOpen, PrevClose) x (1 + avg), LB = min(...) x (1 - avg); EMA 20 of 15-min closes (continuous);
  flat & Time <= 14:00: close > UB and close > open -> buy next bar open; close < LB and close < open -> short;
  long: (Time <= 14:00, short signal) -> reverse (if the day caps allow, else just exit); else close < max(UB, EMA) -> exit;
  stop 50 / target 25 pts per contract (intrabar, 1-minute path); max 10 entries, max 3 stops a day; 14:30 bar -> exit
  next bar open (14:45). Costs $7.25 + 1 tick per market / stop fill (target = limit, no slip).
Two chart sessions, since the code's 'day open' depends on it: RTH (08:30-15:00 bars; open = 08:30, prev close = 15:00)
and 24h CME (first bar of the date closes 00:00; open ~ 23:45 of the previous date). A day with no 14:30 bar (early
close) has no flat signal in the code: such positions are reported, and closed at the day's last bar here.
  python3 analysis/bridge_noise_15m_test.py > analysis/outputs/bridge_noise_15m_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R, montecarlo as MC

PV, TICK, COMM = 20.0, 0.25, 7.25
NTRIAL = {"n": 0}
g = pickle.load(open("scratch_data/g24.pkl", "rb"))
B = g.bars(15)
TR = set(g.trading.tolist())


def series(session):
    """Continuous 15-min bars of the chart: rows (row, hhmm, o, h, l, c, j_close)."""
    out = []
    for r in range(g.D):
        if session == "rth" and r not in TR: continue
        for i in range(96):
            c = B["c"][r, i]
            if np.isnan(c): continue
            hhmm = (i * 15 // 60) * 100 + (i * 15) % 60
            if session == "rth" and not (845 <= hhmm <= 1500): continue
            if session == "24h" and i == 0 and r - 1 < 0: continue
            out.append((r, hhmm, B["o"][r, i], B["h"][r, i], B["l"][r, i], c, i * 15))
    return pd.DataFrame(out, columns=["row", "t", "o", "h", "l", "c", "j"])


def ema(x, n):
    a = 2.0 / (n + 1); y = np.empty(len(x)); y[0] = x[0]
    for i in range(1, len(x)): y[i] = y[i - 1] + a * (x[i] - y[i - 1])
    return y


def run(S, look=20, vm=1.0, emalen=20, sl=50.0, rr=0.5, maxtr=10, maxstops=3, longs=True, shorts=True, last_entry=1400,
        count=True, through=0.0, anchor=None):
    if count: NTRIAL["n"] += 1
    tp = sl * rr
    row, t, O, H, L, C, J = (S[k].to_numpy() for k in ("row", "t", "o", "h", "l", "c", "j"))
    E = ema(C, emalen)
    hist = [[] for _ in range(23)]
    rows = []; pos = 0; e = 0.0; t_in = None; j_in = 0; pend = None
    today_open = prev_close = 0.0; trades = stops = 0; flagged = 0
    last_rth_close = 0.0
    n = len(S)

    def close_trade(px, kind, k, jx):
        nonlocal pos, stops
        pts = (px - e) * pos
        if pts <= -sl: stops += 1
        rows.append((g.ts[row[k]], pos, e, px, kind, t_in, t[k], row[k], j_in, jx))
        pos = 0

    for k in range(n):
        newday = k == 0 or row[k] != row[k - 1]
        if newday:
            if pos != 0:                                             # no 14:30 bar yesterday: the code would hold it
                flagged += 1; close_trade(C[k - 1] - pos * TICK, "held past session (closed at last bar)", k - 1, J[k - 1])
            pend = None
            today_open = O[k]; prev_close = C[k - 1] if k > 0 else 0.0; trades = stops = 0
        if anchor is not None and t[k] == anchor[0]:                 # RTH anchor on a 24h chart: open of the 08:30 bar
            today_open = O[k]; prev_close = last_rth_close
        if anchor is not None and t[k] == anchor[1]: last_rth_close = C[k]
        # ---- bar k opens: the pending market order fills at its open ----
        if pend is not None:
            if pend[0] in ("out", "rev") and pos != 0:
                close_trade(O[k] - pos * TICK, pend[2], k, J[k] - 14)
            if pend[0] in ("in", "rev") and pend[1] != 0:
                pos = pend[1]; e = O[k] + pos * TICK; t_in = t[k]; j_in = J[k] - 14
            pend = None
        # ---- stop / target inside bar k, 1-minute path ----
        if pos != 0:
            r = row[k]; j1 = J[k]
            for m in range(max(0, j1 - 14), j1 + 1):
                if np.isnan(g.c[r, m]): continue
                stp, tgt = e - pos * sl, e + pos * tp
                if (g.l[r, m] <= stp) if pos > 0 else (g.h[r, m] >= stp):
                    close_trade((min(g.o[r, m], stp) if pos > 0 else max(g.o[r, m], stp)) - pos * TICK, "stop", k, m); break
                if (g.h[r, m] >= tgt + through) if pos > 0 else (g.l[r, m] <= tgt - through):
                    close_trade(tgt, "target", k, m); break
        # ---- bar k closes: the signal code ----
        tt = t[k]
        if 900 <= tt <= 1430 and today_open > 0 and prev_close > 0:
            slot = (tt // 100 * 60 + tt % 100 - 540) // 15 + 1
            if 1 <= slot <= 22:
                mv = abs(C[k] / today_open - 1)
                hs = hist[slot]
                if len(hs) >= look:
                    avg = np.mean(hs[-look:]) * vm
                    ub = max(today_open, prev_close) * (1 + avg); lb = min(today_open, prev_close) * (1 - avg)
                    ltr, strl = max(ub, E[k]), min(lb, E[k])
                    can = trades < maxtr and stops < maxstops
                    lsig = longs and C[k] > ub and C[k] > O[k]; ssig = shorts and C[k] < lb and C[k] < O[k]
                    if tt < 1430:
                        if pos == 0 and can and tt <= last_entry:
                            if lsig: pend = ("in", 1); trades += 1
                            elif ssig: pend = ("in", -1); trades += 1
                        elif pos == 1:
                            if tt <= last_entry and ssig:
                                if can: pend = ("rev", -1, "reverse"); trades += 1
                                else: pend = ("out", 0, "reverse exit")
                            elif C[k] < ltr: pend = ("out", 0, "band/EMA exit")
                        elif pos == -1:
                            if tt <= last_entry and lsig:
                                if can: pend = ("rev", 1, "reverse"); trades += 1
                                else: pend = ("out", 0, "reverse exit")
                            elif C[k] > strl: pend = ("out", 0, "band/EMA exit")
                hs.append(mv)
                if len(hs) > 100: hs.pop(0)
        if tt == 1430 and pos != 0:
            pend = ("out", 0, "flat 14:30")
    T = pd.DataFrame(rows, columns=["date", "side", "entry", "exit", "kind", "t0", "t1", "row", "j0", "j1"])
    T["date"] = pd.to_datetime(T.date)
    T["net"] = (T.exit - T.entry) * T.side * PV - COMM
    T.attrs["flagged"] = flagged
    return T


def tst(x):
    x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan


def pf(x): x = pd.Series(x); return x[x > 0].sum() / max(1e-9, -x[x < 0].sum())


def line(t, nm, w=46):
    t = t[t.date >= "2018-01-01"]
    if len(t) < 5: return f"   {nm:<{w}} n={len(t)}"
    x = t.net; y = t.date.dt.year; by = x.groupby(y).sum(); a, b = x[y < 2023], x[y >= 2023]
    return (f"   {nm:<{w}} n={len(x):4d} ${x.mean():4.0f} PF {pf(x):4.2f} t {tst(x):4.1f} win {np.mean(x > 0):.0%} yrs+ {(by > 0).sum()}/{len(by)}"
            f" | 18-22 ${a.mean():4.0f} t {tst(a):4.1f} | 23+ ${b.mean():4.0f} t {tst(b):4.1f} | L ${x[t.side > 0].mean():4.0f} S ${x[t.side < 0].mean():4.0f}")


DAYS = pd.DatetimeIndex(g.ts[g.trading]); DAYS = DAYS[DAYS >= "2018-01-01"]


def daily(t): return t.groupby("date").net.sum().reindex(DAYS, fill_value=0.0)


def placebo(T, S, n=200, seed=7):
    """Same number of trades a day, random side, entry at a random 15-min open 09:15-14:15, same 50 / 25 bracket, out 14:45."""
    rng = np.random.default_rng(seed); res = []
    by = T.groupby("date").size()
    rows = {pd.Timestamp(g.ts[r]): r for r in g.trading}
    for _ in range(n):
        tot = []
        for d, cnt in by.items():
            r = rows.get(d)
            if r is None: continue
            for _ in range(cnt):
                j0 = int(rng.integers(555, 856)); side = rng.choice([-1, 1])
                if np.isnan(g.o[r, j0]): continue
                e = g.o[r, j0] + side * TICK; x = None
                for m in range(j0, 885):
                    if np.isnan(g.c[r, m]): continue
                    if (g.l[r, m] <= e - 50) if side > 0 else (g.h[r, m] >= e + 50):
                        x = (e - side * 50) - side * TICK; break
                    if (g.h[r, m] >= e + 25) if side > 0 else (g.l[r, m] <= e - 25):
                        x = e + side * 25; break
                if x is None:
                    c = g.c[r, 885] if not np.isnan(g.c[r, 885]) else g.c[r, :886][~np.isnan(g.c[r, :886])][-1]
                    x = c - side * TICK
                tot.append((x - e) * side * PV - COMM)
        res.append(np.mean(tot))
    return np.array(res)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    S = {s: series(s) for s in ("rth", "24h")}
    base = {}
    print(f"\n1. As posted (20 days, 50 / 25 pts, both sides), per NQ, 2018-01 -> {DAYS[-1].date()}:")
    for s in ("rth", "24h"):
        T = base[s] = run(S[s]); T.to_csv(f"analysis/outputs/bridge_noise_15m_trades_{s}.csv", index=False)
        print(line(T, f"as posted, {s.upper()} chart"))
        print("      exits:", T.kind.value_counts().to_dict(), "| early-close days the code would hold:", T.attrs["flagged"])
        print("      by year $:", T[T.date >= "2018"].groupby(T.date.dt.year).net.sum().round(0).astype(int).to_dict())
    print("\n2. Variants (same family checks as the 30-min test), RTH chart:")
    V = {"no target (stop 50 only)": dict(rr=100.0), "target 50 / stop 50": dict(rr=1.0), "target 100 / stop 50": dict(rr=2.0),
         "no stop, no target (paper exits)": dict(sl=1e6, rr=1.0), "longs only": dict(shorts=False), "shorts only": dict(longs=False),
         "lookback 14 (paper)": dict(look=14), "1 entry a day": dict(maxtr=1),
         "target fills only 1 tick THROUGH (no touch fills)": dict(through=TICK), "target 1 tick through, longs only": dict(through=TICK, shorts=False)}
    for nm, kw in V.items(): print(line(run(S["rth"], **kw), nm))
    for s_ in ("rth",):
        for th, nm in ((0.0, "touch"), (TICK, "1 tick through")):
            T2 = run(S[s_], through=th).copy(); T2["net"] -= np.where(T2.kind == "target", 1, 2) * TICK * PV
            print(line(T2, f"+1 more tick per market/stop fill, target {nm}"))
    for s in ("rth", "24h"):
        pl = placebo(base[s], None)
        x = base[s][base[s].date >= "2018"].net
        print(f"\n3. Random-entry placebo ({s.upper()}; same trades a day, random side and 15-min open 09:15-14:15, same bracket, 200 runs):"
              f" real ${x.mean():.0f} vs placebo mean ${pl.mean():.0f} (95th pct ${np.percentile(pl, 95):.0f}); p = {np.mean(pl >= x.mean()):.3f}")
    print("\n4. Metrics per NQ (daily):")
    rows = {}
    for s in ("rth", "24h"):
        t = base[s]; x = daily(t)
        for per, st in (("2018-26", "2018-01-01"), ("2023+", "2023-01-01")):
            rows[f"{s} {per}"] = (x[x.index >= st], t[t.date >= st].set_index("date").net)
        for sd, nn in ((1, "longs"), (-1, "shorts")):
            rows[f"{s} {nn}"] = (daily(t[t.side == sd]), t[(t.side == sd) & (t.date >= "2018")].set_index("date").net)
    print(M.table(rows))
    x = daily(base["rth"])
    b_, p_ = R.report({"RTH as posted 2023+": x[x.index >= "2023-01-01"]}, limits=(5000, 10000, 20000)); print(b_); print(p_)
    print(MC.report(base["rth"][base["rth"].date >= "2018"].net.values, daily=x.values, size=0.1, label="RTH as posted, 1 MNQ"))
    print(MC.report(base["rth"][base["rth"].date >= "2018"].net.values, daily=x.values, size=0.2, label="RTH as posted, 2 MNQ"))
    pdp = pd.read_csv("agents/tasks/plan_daily_pnl.csv", index_col=0, parse_dates=True)
    print("   daily corr with the plan pieces (RTH):", pdp.corrwith(x.reindex(pdp.index, fill_value=0.0)).round(2).to_dict())
    nt = NTRIAL["n"]
    print(f"\n   trials here {nt}; deflated Sharpe (RTH as posted, N = {nt}) {M.deflated_sharpe(x.values, nt):.2f}")
