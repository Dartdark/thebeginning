"""T_ONESIDE (user's upload 2026-10-24: PowerLanguage file + 'Night-volume switch' research note; checks/candidates/t_oneside/).
Rebuild of the frozen file on the 24-hour NQ grid, 2018-2026 (1-min bars, close-stamped, CT):
  - Night = 17:00 reopen -> the 08:29 bar (at least 30 bars). Heavy ('fat') night: its volume > 1.4 x the median of the
    prior 20 valid nights.
  - T (fat nights): fade the night's move (open of the first night bar -> 08:29 close): market at the open of the 08:30
    bar (08:29:00 CT, a minute before the bell), out at the open of the 08:45 bar (08:44:00).
  - OS (other valid nights): at the 09:59 bar, (morning high - 08:29 open) > 2 x (08:29 open - morning low) and close >
    the session VWAP (from the 08:30 bar) -> long at the next open (09:59:00); out at the next open after a close below
    VWAP, else at the 11:00 bar's open (10:59:00).
  - The file has NO stop. The note's headline adds 0.40 (T) / 0.30 (OS) x ATRd, ATRd = mean 08:31-15:00 range of the
    last 20 full sessions; both are run here (stop from the fill, entry bar included, fill at the stop).
Costs: ours $7.25 + 1 tick per fill ($17.25 a round trip); the note's $13.50 shown for parity.
Volume = the exported 1-min volume (MultiCharts 'Volume', up-ticks on our exports; the switch is a ratio, so a
proportional proxy works; noted as a caveat).
The author's own pre-declared falsification cells (note p.4, 'none run yet') + our placebos:
  1 fade on quiet nights; 2 OS long on heavy nights; 3 fade by tercile of the volume ratio; 4 symmetry (quiet night,
  one-sided DOWN morning below VWAP -> short); 5 the fade entered at the bell (08:30:00) instead of 08:29:00;
  random side on the fade days (1,000 runs).
  python3 analysis/t_oneside_test.py SCRATCH_DIR
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import line
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25


def days(g):
    O, H, L, C, V = (getattr(g, k).ravel() for k in ("o", "h", "l", "c", "v"))
    ok = np.flatnonzero(np.isfinite(C)); mins = ok % 1440; hh = (mins // 60) * 100 + mins % 60
    isday = (hh >= 830) & (hh < 1700)
    lastday = np.maximum.accumulate(np.where(isday, np.arange(len(ok)), -1))      # position in ok of the last day bar so far
    rows, buf, rng_hist = [], [], []
    for r in g.trading:
        e = r * 1440 + jof(829); k = np.searchsorted(ok, e, side="right") - 1
        if k < 0: continue
        ld = lastday[k]; night = ok[ld + 1:k + 1]
        jj = np.arange(jof(830), jof(1500) + 1); full = np.isfinite(g.c[r, jof(1455):jof(1500) + 1]).any()
        atr = np.mean(rng_hist[-20:]) if len(rng_hist) >= 20 else np.nan
        if full: rng_hist.append(np.nanmax(g.h[r, jof(831):jof(1500) + 1]) - np.nanmin(g.l[r, jof(831):jof(1500) + 1]))
        n = len(night); valid = n >= 30
        if n == 0 or not np.isfinite(g.o[r, jof(830)]):
            continue
        vol = np.nansum(V[night]); ret = C[night[-1]] - O[night[0]]
        med = np.median(buf[-20:]) if len(buf) >= 20 else np.nan
        rows.append(dict(r=r, date=pd.Timestamp(g.ts[r]), n=n, valid=valid, vol=vol, med=med, ratio=vol / med if med > 0 else np.nan,
                         ret=ret, atr=atr, full=full))
        if valid: buf.append(vol)
    return pd.DataFrame(rows)


def hold(g, r, side, j_in, j_out_max, stop=np.nan, vwap_exit=False, vw=None):
    """Market entry at the open of bar j_in; out at the open of bar j_out_max (or earlier: VWAP close / stop)."""
    e = g.o[r, j_in]
    if not np.isfinite(e): return None
    sp = e - side * stop if np.isfinite(stop) else np.nan
    for j in range(j_in, j_out_max):
        if np.isfinite(sp) and np.isfinite(g.l[r, j]):
            if (side > 0 and g.l[r, j] <= sp) or (side < 0 and g.h[r, j] >= sp):
                return e, sp, j, 0
        if vwap_exit and j > j_in - 1 and np.isfinite(g.c[r, j]) and (g.c[r, j] - vw[j - jof(830)]) * side < 0:
            x = g.o[r, j + 1]
            if np.isfinite(x): return e, x, j, 2
    x = g.o[r, j_out_max]
    if not np.isfinite(x): x = g.c[r, j_out_max - 1]
    return e, x, j_out_max - 1, 2


def morning(g, r):
    jj = np.arange(jof(830), jof(1100) + 1)
    h, l, c, v = g.h[r, jj], g.l[r, jj], g.c[r, jj], np.nan_to_num(g.v[r, jj])
    tp = np.nan_to_num((h + l + c) / 3); cv = np.cumsum(v)
    vw = np.where(cv > 0, np.cumsum(tp * v) / np.maximum(cv, 1e-9), np.nan)
    k = jof(959) - jof(830); px = g.o[r, jof(830)]
    return px, np.nanmax(h[:k + 1]), np.nanmin(l[:k + 1]), c[k], vw[k], vw


def build(g, D, stop=False, cells=False):
    out = []
    for x in D[D.valid & (D.med > 0) & D.atr.notna()].itertuples():
        r = x.r; fat = x.vol > 1.4 * x.med
        px, bh, bl, c959, vw959, vw = morning(g, r)
        up = (bh - px) > 2 * (px - bl); dn = (px - bl) > 2 * (bh - px)
        def add(cell, side, *a, **k):
            h_ = hold(g, r, side, *a, **k)
            if h_: e, xp, j1, kind = h_; out.append(dict(date=x.date, cell=cell, side=side, day=r, j0=a[0], j1=j1, entry=e, exit=xp,
                                                         kind=kind, ratio=x.ratio, gross=(xp - e) * side * PV))
        fs = -np.sign(x.ret)
        if fat and fs != 0: add("T", fs, jof(830), jof(845), stop=0.40 * x.atr if stop else np.nan)
        if not fat and up and np.isfinite(c959) and c959 > vw959:
            add("OS", 1, jof(1000), jof(1100), stop=0.30 * x.atr if stop else np.nan, vwap_exit=True, vw=vw)
        if cells:
            if not fat and fs != 0: add("c1 fade quiet", fs, jof(830), jof(845))
            if fat and up and np.isfinite(c959) and c959 > vw959: add("c2 OS long heavy", 1, jof(1000), jof(1100), vwap_exit=True, vw=vw)
            if fs != 0: add("c3 fade all valid", fs, jof(830), jof(845))
            if not fat and dn and np.isfinite(c959) and c959 < vw959: add("c4 OS short quiet", -1, jof(1000), jof(1100), vwap_exit=True, vw=vw)
            if fat and fs != 0: add("c5 fade at the bell", fs, jof(831), jof(845))
    t = pd.DataFrame(out)
    slip = np.where(t.kind == 0, 1, 1) * 2 * TICK * PV              # 1 tick on entry + 1 on the exit (market or stop)
    t["net"] = t.gross - slip - COMM; t["net_note"] = t.gross - slip - 3.50
    return t


def stats(x, nm, dd):
    p = M.perf(x.groupby(x.index).sum().reindex(dd, fill_value=0.0), x.values)
    return (f"   {nm:<24} Sharpe {p['sharpe']:5.2f} Sortino {p['sortino']:5.2f} PF {p['profit_factor']:4.2f} "
            f"Calmar {p['calmar']:5.2f} Ulcer {p['ulcer']:5.2f} maxDD ${p['max_dd']:,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    D = days(g); D = D[D.date >= "2017-12-01"].reset_index(drop=True)
    s = lambda t, m=None, col="net": (t[col] if m is None else t[col][m]).set_axis(pd.DatetimeIndex(t.date if m is None else t.date[m]))
    A = build(g, D, stop=False, cells=True); A = A[A.date >= "2018-01-01"]
    S_ = build(g, D, stop=True); S_ = S_[S_.date >= "2018-01-01"]
    dd = pd.DatetimeIndex(D.date[D.date >= "2018-01-01"]); fatshare = (D.vol > 1.4 * D.med)[D.valid & (D.med > 0)].mean()
    print(f"valid nights {D.valid.sum()}, fat share {fatshare:.0%}")
    print("\nparity with the note (its costs $13.50; MultiCharts 2016-10 -> 2026-08):")
    for nm, t in (("file (no stop)", A[A.cell.isin(["T", "OS"])]), ("note's stop", S_)):
        w = t[t.date <= "2026-08-13"]; x = w.net_note; pf = x[x > 0].sum() / -x[x < 0].sum()
        print(f"   {nm:<16} trades {len(w)} ({len(w) / ((w.date.max() - w.date.min()).days / 365.25):.0f} a year), avg ${x.mean():.2f}, PF {pf:.2f}, "
              f"win {np.mean(x > 0):.1%}  | note: no stop 988 / 99 a year $115.95 PF 1.41; stop $125.36 PF 1.47")
    print("\nper NQ at our costs, 2018-2026:")
    for nm, t in (("file (no stop)", A), ("note's stop", S_)):
        print(f" {nm}:")
        tt = t[t.cell.isin(["T", "OS"])]
        print(line(s(tt), "whole book", 40))
        for c, lab in (("T", "T fade (heavy nights)"), ("OS", "OS long (quiet nights)")):
            print(line(s(tt, tt.cell == c), lab, 40))
        print(line(s(tt, (tt.cell == "T") & (tt.side > 0)), "   T longs (night was down)", 40))
        print(line(s(tt, (tt.cell == "T") & (tt.side < 0)), "   T shorts (night was up)", 40))
        print(line(s(tt, tt.date >= "2023-09-08"), "whole book, after their split 2023-09-08", 40))
    print("\nthe author's falsification cells (no stop):")
    T0 = A[A.cell == "T"]
    for c in ("c1 fade quiet", "c3 fade all valid", "c2 OS long heavy", "c4 OS short quiet", "c5 fade at the bell"):
        print(line(s(A, A.cell == c), c, 40))
    c3 = A[A.cell == "c3 fade all valid"].copy(); c3["q"] = pd.qcut(c3.ratio, 3, labels=["low", "mid", "high"])
    print("   3. fade by tercile of the volume ratio:", {str(k): f"${v:.0f}" for k, v in c3.groupby("q").net.mean().items()},
          "| ratio cut points", np.round(c3.ratio.quantile([1 / 3, 2 / 3]).values, 2))
    c3["q5"] = pd.qcut(c3.ratio, 5, labels=False); print("      by quintile:", c3.groupby("q5").net.mean().round(0).to_dict())
    rng = np.random.default_rng(20261024); raw = T0.gross * T0.side
    r_ = np.array([(raw * rng.choice([-1, 1], len(T0)) - 2 * TICK * PV - COMM).mean() for _ in range(1000)])
    print(f"   random side on the fade days: T ${T0.net.mean():.0f} vs random p50 ${np.median(r_):.0f}, beaten by {np.mean(r_ >= T0.net.mean()):.1%}")
    print("\nby year (per NQ, no stop / stop):")
    by = pd.DataFrame({f"{c} {k}": s(t, t.cell == c).groupby(lambda d: d.year).sum() for k, t in (("nostop", A), ("stop", S_)) for c in ("T", "OS")})
    print(by.round(0).to_string())
    print("\nmetrics (daily, per NQ, our costs):")
    for k, t in (("no stop", A), ("stop", S_)):
        tt = t[t.cell.isin(["T", "OS"])]
        for nm, m in (("book", None), ("T", tt.cell == "T"), ("OS", tt.cell == "OS"), ("longs", tt.side > 0), ("shorts", tt.side < 0)):
            print(stats(s(tt, m), f"{k}: {nm}", dd))
    d23 = dd[dd >= "2023-01-01"]
    for nm, t in (("book (stop)", S_), ("T (stop)", S_[S_.cell == "T"])):
        x = s(t, t.date >= "2023-01-01"); print(f"\nresampling {nm}, 2023+:"); print("\n".join(R.report({nm: x.groupby(x.index).sum().reindex(d23, fill_value=0.0)})))
    for nm, t in (("book (stop)", S_), ("T (stop)", S_[S_.cell == "T"]), ("OS (stop)", S_[S_.cell == "OS"])):
        y = s(t); dy = y.groupby(y.index).sum().reindex(dd, fill_value=0.0)
        print(MC.report(y.values, dy, size=0.1, label=f"{nm} 1 MNQ")); print(f"      t {y.mean() / y.std() * np.sqrt(len(y)):.2f}, DSR at 291 items {M.deflated_sharpe(dy, 291):.2f}")
    A.to_csv(SP + "t_oneside_nostop.csv", index=False); S_.to_csv(SP + "t_oneside_stop.csv", index=False)
