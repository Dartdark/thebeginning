"""Daily mean reversion with a 200-day filter and a 0.50% stop (Bertola 2026, SSRN 7663278; user upload 2026-11-08).
Paper (6 cash indices 2002-26, daily OHLC): at the close of day t, red RTH candle (close < open) -> long at the close,
green -> short (asymmetric: only when close <= SMA200 of closes); exit at the next close; stop 0.50% from entry,
gap through the stop fills at the open. Claimed S&P 500: CAGR 23%, Sharpe 1.66, PF 1.52, 3,504 trades. Gross of costs.
Here on futures, per 1 contract, costs $7.25 NQ / $5 ES + 1 tick per market / stop fill:
  A  as the paper (pre-registered: no parameter changes): entry at the 15:00 CT RTH close, stop watched on the 24h
     1-min path (futures trade overnight), exit next RTH close. Holds overnight: NOT Apex-legal (personal account only).
  B  stop watched in RTH only (the cash-index paper's view; overnight path ignored, opening gap through the stop fills
     at the 08:30 open) - information only, futures cannot do this without an unprotected night.
  C  Apex-legal: same signal, enter the next 08:30 open, stop 0.50%, flat at 14:59.
  Controls: same days long every day (drift); longs after GREEN days.
  tools/run_stamped.sh analysis/daily_reversal_bertola_test.py > analysis/outputs/daily_reversal_bertola_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M

J0, J1, JE = jof(831), jof(1500), jof(1459)          # first RTH bar (08:30-08:31), RTH close bar, Apex flat bar


def trades(g, pv, comm, tick, mode, rule):
    T = g.trading; o = g.o; h = g.h; l = g.l; c = g.c
    op = o[T, J0]; cl = c[T, J1]
    sma = pd.Series(cl).ffill().rolling(200).mean().to_numpy()   # ffill: an early-close day has no 15:00 bar
    out = []
    for k in range(200, len(T) - 1):
        r, rn = T[k], T[k + 1]
        if np.isnan(op[k]) or np.isnan(cl[k]) or np.isnan(cl[k + 1]): continue
        red, green = cl[k] < op[k], cl[k] > op[k]
        if rule == "asym": side = 1 if red else (-1 if green and cl[k] <= sma[k] else 0)
        elif rule == "sym": side = 1 if red else (-1 if green else 0)
        elif rule == "always_long": side = 1
        elif rule == "long_after_green": side = 1 if green else 0
        if side == 0: continue
        if mode in ("A", "B"):
            e = cl[k]; path = []
            if mode == "A":
                for rr in range(r, rn + 1):
                    a = J1 + 1 if rr == r else 0; b = J1 if rr == rn else 1439
                    for j in range(a, b + 1):
                        if not np.isnan(c[rr, j]): path.append((o[rr, j], h[rr, j], l[rr, j]))
            else:
                for j in range(J0, J1 + 1):
                    if not np.isnan(c[rn, j]): path.append((o[rn, j], h[rn, j], l[rn, j]))
            xe = cl[k + 1]
        else:
            if np.isnan(op[k + 1]): continue
            e = op[k + 1]; path = [(o[rn, j], h[rn, j], l[rn, j]) for j in range(J0, JE + 1) if not np.isnan(c[rn, j])]
            xe = c[rn, JE] if not np.isnan(c[rn, JE]) else path[-1][0]
        stp = e * (1 - 0.005 * side); x = None; kind = "close"
        for (oo, hh, ll) in path:
            if (ll <= stp) if side > 0 else (hh >= stp):
                x = (min(oo, stp) if side > 0 else max(oo, stp)) - side * tick; kind = "stop"; break
        if x is None: x = xe - side * tick
        e2 = e + side * tick
        out.append((pd.Timestamp(g.ts[rn]), side, (x - e2) * side * pv - comm, kind))   # comm = round trip (Codex weekly review 2026-11-06 #3: was 2 * comm)
    t = pd.DataFrame(out, columns=["date", "side", "net", "kind"])
    return t


def line(t, nm):
    x = t.net; tt = x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 1 else np.nan
    pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    a, b = t[t.date < "2023"].net, t[t.date >= "2023"].net
    ts = lambda y: y.mean() / y.std(ddof=1) * np.sqrt(len(y)) if len(y) > 1 else np.nan
    yrs = t.groupby(t.date.dt.year).net.sum()
    return (f"   {nm:<44} n={len(x):5d} ${x.mean():6.0f} PF {pf:4.2f} t {tt:5.1f} stop {np.mean(t.kind == 'stop'):4.0%} "
            f"yrs+ {(yrs > 0).sum()}/{len(yrs)} | 18-22 ${a.mean():5.0f} t {ts(a):4.1f} | 23+ ${b.mean():5.0f} t {ts(b):4.1f}"
            f" | L ${t[t.side > 0].net.mean():5.0f} S ${t[t.side < 0].net.mean() if (t.side < 0).any() else float('nan'):5.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for nm, f, pv, comm in (("NQ", "scratch_data/g24.pkl", 20.0, 7.25), ("ES", "scratch_data/ge.pkl", 50.0, 5.0)):
        g = pickle.load(open(f, "rb"))
        print(f"\n{nm} (per 1 contract, {pd.Timestamp(g.ts[g.trading[200]]).date()} .. {pd.Timestamp(g.ts[g.trading[-1]]).date()}):")
        base = None
        for mode, rule, lab in (("A", "asym", "A asymmetric (paper's main), 24h stop"), ("A", "sym", "A symmetric, 24h stop"),
                                ("B", "asym", "B asymmetric, RTH-only stop (info)"), ("C", "asym", "C Apex-legal open->14:59, asym"),
                                ("A", "always_long", "control: long every close, 24h stop"),
                                ("A", "long_after_green", "control: long after GREEN days")):
            t = trades(g, pv, comm, 0.25, mode, rule); print(line(t, lab))
            if base is None: base = t
            if mode == "A" and rule == "asym":
                print("      by year $:", base.groupby(base.date.dt.year).net.sum().round(0).astype(int).to_dict())
        x = base.groupby("date").net.sum()
        idx = pd.date_range(x.index.min(), x.index.max(), freq="B"); d = x.reindex(idx, fill_value=0.0)
        print(M.table({f"{nm} A asym 2018+": (d, base.set_index("date").net),
                       f"{nm} A asym 2023+": (d[d.index >= "2023"], base[base.date >= "2023"].set_index("date").net),
                       f"{nm} longs": (base[base.side > 0].groupby("date").net.sum().reindex(idx, fill_value=0.0), base[base.side > 0].set_index("date").net),
                       f"{nm} shorts": (base[base.side < 0].groupby("date").net.sum().reindex(idx, fill_value=0.0), base[base.side < 0].set_index("date").net)}))
