"""GC_COMBO v2 (user's upload 2026-10-24: community PowerLanguage file + GCCOMBO.txt daily file + research note;
checks/candidates/gc_combo/). Rebuild of the defaults on our GC / CL 1-min grids (CT), 2018-01 -> 2026-10:
  BLEND at the 09:00 CT bar (10:00 ET): score = A sign(close 09:00 - close 07:20) + B -sign(morning taker flow 07:21-09:00)
    + C GLD vote (GCCOMBO close - 10) + D crude vote (yesterday's CL 16:00 CT -> 16:00 CT return >= 1.5 x the mean |return|
    of the prior 20) + E A again on 'dollar-decoupled' days (GCCOMBO open - 10 = 1). |score| >= 2 -> 1 GC (2 at >= 3),
    market at the next bar's open, out at the 12:30 CT bar close (13:30 ET). No stop.
  STRETCH: 07:20-14:00 CT, a close <= session VWAP (from 17:01 CT) - 0.5 x ATR (mean Globex-session range of the last 15
    sessions) -> short 1 GC at the next open; stop 0.505 ATR, target 2 x the stop, out at the 15:00 CT close; max 2 signals
    a session, 60 bars apart (counted even when not taken). One position at a time.
  Vote B PROXY: the file needs UpTicks - DownTicks; our exports have total volume only, so B = -sign(sum of volume x
    sign(close - previous close)) over the morning (minute tick rule). The note's own vote-B panel is the reference.
Costs per GC: $7.25 + 1 tick ($10) per market / stop fill (repo standard; the note used $2.30/side + 1 tick); targets
fill 1 tick through at the limit. Basis points (gross, scale-free) as in the note. IS 2018-2024, OOS 2025-2026.
Controls: each vote alone and the blend without each vote (as in the note); following the flow; random side on blend days.
  python3 analysis/gc_combo_test.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import line
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 100.0, 0.10, 7.25
GCF = "checks/candidates/gc_combo/GCCOMBO.txt"


def crude_votes(cl):
    c = cl.c[:, jof(1600)]; rows = []; prev = np.nan; rets = []
    for r in range(cl.D):
        if not np.isfinite(c[r]): continue
        if np.isfinite(prev):
            ret = c[r] / prev - 1; ma = np.mean(np.abs(rets[-20:])) if len(rets) >= 20 else np.nan
            z = ret / ma if ma > 0 else 0.0
            rows.append((pd.Timestamp(cl.ts[r]), int(np.sign(z)) if abs(z) >= 1.5 else 0)); rets.append(ret)
        prev = c[r]
    return pd.Series(dict(rows))


def run(g, cl, votes_on=(1, 1, 1, 1, 1), stretch_on=True, blend_on=True, flow_sign=-1, rand=None):
    O, H, L, C, V = (getattr(g, k).ravel() for k in ("o", "h", "l", "c", "v"))
    gc3 = pd.read_csv(GCF, parse_dates=["Date"]).set_index("Date")
    oil = crude_votes(cl); oil_dates = oil.index.values
    out, ranges = [], []; stats_rows = []
    for r in g.trading:
        s0, s1 = (r - 1) * 1440 + jof(1701), r * 1440 + jof(1600)
        idx = np.arange(s0, s1 + 1); idx = idx[np.isfinite(C[idx])]
        if len(idx) < 300: continue
        atr = np.mean(ranges[-15:]) if len(ranges) >= 15 else np.nan
        ranges.append(np.nanmax(H[idx]) - np.nanmin(L[idx]))
        tp = (H[idx] + L[idx] + C[idx]) / 3; v = np.nan_to_num(V[idx]); vw = np.cumsum(tp * v) / np.maximum(np.cumsum(v), 1e-9)
        hh = ((idx % 1440) // 60) * 100 + (idx % 1440) % 60; day = pd.Timestamp(g.ts[r])
        # blend votes
        ia = np.flatnonzero(hh == 720); idc = np.flatnonzero(hh == 900)
        score = None
        if len(ia) and len(idc) and np.isfinite(atr):
            a, d = ia[0], idc[0]
            vA = np.sign(C[idx[d]] - C[idx[a]])
            seg = idx[a + 1:d + 1]; dc = np.sign(C[seg] - C[idx[a:d]]); flow = np.sign(np.sum(np.nan_to_num(V[seg]) * dc))
            k = np.searchsorted(oil_dates, np.datetime64(day)) - 1; vD = oil.iloc[k] if k >= 0 else 0
            vC, dec = (gc3.loc[day, "Close"] - 10, gc3.loc[day, "Open"] - 10) if day in gc3.index else (0, 0)
            parts = np.array([vA, flow_sign * flow, vC, vD, vA if dec == 1 else 0])
            score = float(np.sum(parts * np.array(votes_on)))
            stats_rows.append(dict(date=day, A=vA, B=-flow, C=vC, D=vD, E=vA if dec == 1 else 0, j=d))
        pos, e, side, qty, stop, tgt, sleeve, j_in, sig, last_sig = 0, 0.0, 0, 0, 0, 0, 0, 0, 0, -9999
        for n, m in enumerate(idx):
            t = hh[n]
            if pos:      # exits on this bar
                x = None
                if sleeve == 2:
                    if H[m] >= e + stop: x, kind = max(O[m], e + stop) + TICK, 0
                    elif L[m] <= e - tgt - TICK: x, kind = e - tgt, 1
                    elif t == 1500: x, kind = C[m] + TICK, 2
                elif t == 1230: x, kind = C[m] - side * TICK, 2
                if x is not None:
                    out.append(dict(date=day, sleeve="blend" if sleeve == 1 else "stretch", side=side, qty=qty, e=e, x=x, kind=kind,
                                    day=r, j0=int(j_in % 1440), j1=int(m % 1440), score=score,
                                    gross=(x - e) * side * PV * qty, bp=(x - e) * side / e * 1e4))
                    pos = 0
            if n + 1 >= len(idx): break
            nxt = idx[n + 1]; took = False
            if stretch_on and 720 <= t <= 1400 and np.isfinite(atr) and C[m] <= vw[n] - 0.5 * atr and sig < 2 and n - last_sig >= 60:
                sig += 1; last_sig = n
                if not pos:
                    e, side, qty, stop, tgt, sleeve, j_in, pos, took = O[nxt] - TICK, -1, 1, 0.505 * atr, 1.01 * atr, 2, nxt, 1, True
            if blend_on and t == 900 and score is not None and not pos and not took and abs(score) >= 2:
                sd = int(np.sign(score)) if rand is None else int(rand.choice([-1, 1]))
                e, side, qty, sleeve, j_in, pos = O[nxt] + sd * TICK, sd, (2 if abs(score) >= 3 else 1), 1, nxt, 1
                e = O[nxt] + side * TICK
    t = pd.DataFrame(out)
    if len(t): t["net"] = t.gross - t.qty * np.where(t.kind == 1, COMM, COMM) * 1.0; t["net1"] = t.net / t.qty
    return t, pd.DataFrame(stats_rows)


def stats(x, nm, dd):
    p = M.perf(x.groupby(x.index).sum().reindex(dd, fill_value=0.0), x.values)
    return (f"   {nm:<28} Sharpe {p['sharpe']:5.2f} Sortino {p['sortino']:5.2f} PF {p['profit_factor']:4.2f} "
            f"Calmar {p['calmar']:5.2f} Ulcer {p['ulcer']:5.2f} maxDD ${p['max_dd']:,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "gc.pkl", "rb")); cl = pickle.load(open(SP + "cl.pkl", "rb"))
    T, V = run(g, cl); T = T[T.date >= "2018-01-01"].reset_index(drop=True)
    dd = pd.DatetimeIndex(pd.Series(pd.DatetimeIndex(g.ts[g.trading]))[lambda x: x >= "2018-01-01"])
    s = lambda t, m=None, col="net": (t[col] if m is None else t[col][m]).set_axis(pd.DatetimeIndex(t.date if m is None else t.date[m]))
    IS, OOS = T.date < "2025-01-01", T.date >= "2025-01-01"
    print(f"trades {len(T)} ({len(T) / (len(dd) / 252) / 52:.2f} a week; note 2.6 IS, 2.76 OOS)")
    print("\nby year: trades / gross bp per trade / net $ (contracts as traded) -- note IS bp 3.5-15.7, 2025 1.6, 2026 10.4")
    print(T.groupby(T.date.dt.year).agg(n=("bp", "size"), bp=("bp", "mean"), net=("net", "sum")).round(1).to_string())
    print("\nper GC (net per contract), contracts as traded in the sums:")
    for nm, m in (("COMBO", None), ("  IS 2018-24", IS), ("  OOS 2025-26", OOS), ("blend", T.sleeve == "blend"),
                  ("  blend IS", (T.sleeve == "blend") & IS), ("  blend OOS", (T.sleeve == "blend") & OOS),
                  ("  blend longs", (T.sleeve == "blend") & (T.side > 0)), ("  blend shorts", (T.sleeve == "blend") & (T.side < 0)),
                  ("  blend score 2", (T.sleeve == "blend") & (T.score.abs() == 2)), ("  blend score >= 3", (T.sleeve == "blend") & (T.score.abs() >= 3)),
                  ("stretch (short)", T.sleeve == "stretch"), ("  stretch IS", (T.sleeve == "stretch") & IS), ("  stretch OOS", (T.sleeve == "stretch") & OOS)):
        print(line(s(T, m, "net1"), nm, 30), f"bp {T.bp[m].mean() if m is not None else T.bp.mean():5.1f}")
    print("\nvotes, research-panel style (gross bp, 09:01 open -> 12:30 close, 2018-2024), our data:")
    gp = []
    for x in V[V.date < "2025-01-01"].itertuples():
        r = g.trading[np.searchsorted(g.ts[g.trading], np.datetime64(x.date))]
        a, b = g.o[r, jof(901)], g.c[r, jof(1230)]
        if np.isfinite(a) and np.isfinite(b): gp.append((x.Index, (b - a) / a * 1e4))
    ret = pd.Series(dict(gp)); W = V.loc[ret.index]
    tt = lambda x: x.mean() / x.std() * np.sqrt(len(x))
    for k in "ABCDE":
        m = W[k] != 0; x = ret[m] * np.sign(W[k][m]); print(f"   vote {k} alone: {m.sum():5d} days, WR {np.mean(x > 0):.1%}, {x.mean():5.1f} bp, t {tt(x):5.2f}")
    sc = W[list("ABCDE")].sum(1); m = sc.abs() >= 2; x = ret[m] * np.sign(sc[m])
    print(f"   all five |score| >= 2: {m.sum()} days, WR {np.mean(x > 0):.1%}, {x.mean():.1f} bp, t {tt(x):.2f}   (note: 715, 58.7%, 7.9 bp, t 4.62)")
    for k in "ABCDE":
        sk = sc - W[k]; m = sk.abs() >= 2; x = ret[m] * np.sign(sk[m]); print(f"   blend without {k}: {m.sum()} days, {x.mean():5.1f} bp, t {tt(x):5.2f}")
    m = W.B != 0; x = ret[m] * -np.sign(W.B[m]); print(f"   FOLLOW the flow: {m.sum()} days, WR {np.mean(x > 0):.1%}, {x.mean():.1f} bp, t {tt(x):.2f} (note −3.1 bp, t −3.2)")
    rng = np.random.default_rng(20261024); b = T[T.sleeve == "blend"]
    raw = (b.x - b.e) * b.side * PV
    rr = np.array([((raw * rng.choice([-1, 1], len(b)) - 2 * TICK * PV - COMM)).mean() for _ in range(1000)])
    m_ = ((b.x - b.e) * b.side * PV - COMM).mean()
    print(f"   random side on the blend days: blend ${m_:.0f} per GC vs random p50 ${np.median(rr):.0f}, beaten by {np.mean(rr >= m_):.1%}")
    print("\nmetrics (daily, contracts as traded, 1-2 GC):")
    for nm, m in (("COMBO", None), ("blend", T.sleeve == "blend"), ("stretch", T.sleeve == "stretch"), ("longs", T.side > 0), ("shorts", T.side < 0)):
        print(stats(s(T, m), nm, dd))
    d23 = dd[dd >= "2023-01-01"]; x = s(T, T.date >= "2023-01-01")
    print("\nresampling COMBO 2023+:"); print("\n".join(R.report({"COMBO": x.groupby(x.index).sum().reindex(d23, fill_value=0.0)})))
    y = s(T); dy = y.groupby(y.index).sum().reindex(dd, fill_value=0.0)
    print(MC.report(y.values, dy, size=0.1, label="COMBO at 1-2 MGC"))
    y1 = s(T, None, "net1"); print(f"      t (per contract) {y1.mean() / y1.std() * np.sqrt(len(y1)):.2f}, DSR at 293 items {M.deflated_sharpe(dy, 293):.2f}")
    T.to_csv(SP + "gc_combo_trades.csv", index=False)
