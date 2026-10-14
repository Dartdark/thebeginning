"""Gold Breakout 15M (user's TradingView description, 2026-10-14) on GC 2018-2026.
Rules as described: broker clock (mode A 'New York + 7h' = CT + 8h all year; mode B fixed GMT+3 = CT + 8h in US summer time,
CT + 9h in winter). Range = high / low of bars opening at broker 00:00 -> 07:00; from broker 07:00 a buy stop at the range high and
a sell stop at the range low, one cancels the other, one trade a day; stop = 1% of the fill (default) or the opposite range edge;
no target; out at broker 20:00. In CT (mode A): range 16:00 -> 23:00 the day before (gold reopens 17:00), entries from 23:00,
out 12:00 CT; the trade stays inside one Apex day (17:00 -> 15:59). Fills on 1-minute bars: stop entry at max(open, level) + 1 tick,
stop-loss at min(open, stop) - 1 tick, time exit at the close -/+ 1 tick; $7.25 commission; 1 GC = $100 a point (10 MGC).
Previously tested: Gold Asian-range breakout (range 20:00 -> 00:00 CT, stop 1 x range, out 10:00): C, worse on the funded bench.
  python3 analysis/gold_breakout_15m_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from co_oc_reversal_test import load, line
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 100.0, 0.10, 7.25


def run(g, mode="A", stop="pct", sl_pct=1.0, rng=None):
    ts = pd.DatetimeIndex(g.ts); O, H, L, C = (getattr(g, k).ravel() for k in "ohlc")
    out = []
    for d in range(1, g.D):
        day = ts[d]
        if day.dayofweek >= 5 or day < pd.Timestamp("2018-01-02"): continue
        off = 8 if mode == "A" else (8 if pd.Timestamp(day, tz="America/Chicago").dst().total_seconds() > 0 else 9)
        b0 = (d - 1) * 1440 + (24 - off) * 60          # broker 00:00 = CT (24 - off):00 the day before
        r0, r1 = b0, b0 + 7 * 60; x = b0 + 20 * 60
        hh, ll = np.nanmax(H[r0:r1]) if np.isfinite(H[r0:r1]).any() else np.nan, np.nanmin(L[r0:r1]) if np.isfinite(L[r0:r1]).any() else np.nan
        if not (np.isfinite(hh) and np.isfinite(ll)) or hh <= ll or not np.isfinite(C[r1:x]).any(): continue
        pos = 0
        for m in range(r1, x):
            if np.isnan(H[m]): continue
            if pos == 0:
                up, dn = H[m] >= hh, L[m] <= ll
                if up and dn: s = 1 if abs(O[m] - hh) < abs(O[m] - ll) else -1
                elif up: s = 1
                elif dn: s = -1
                else: continue
                lvl = hh if s > 0 else ll
                e0 = max(O[m], lvl) if s > 0 else min(O[m], lvl)          # the breakout print
                if rng is not None: s = rng.choice([-1, 1])                 # placebo: random side AT the breakout price
                e = e0 + s * TICK
                sp = (e * (1 - sl_pct / 100) if s > 0 else e * (1 + sl_pct / 100)) if stop == "pct" else (ll if s > 0 else hh)
                risk = abs(e - sp); pos = s; j0 = m; worst = 0.0
                continue
            worst = min(worst, ((L[m] - e) if pos > 0 else (e - H[m])) * PV)
            if (pos > 0 and L[m] <= sp) or (pos < 0 and H[m] >= sp):
                px = (min(O[m], sp) - TICK) if pos > 0 else (max(O[m], sp) + TICK)
                out.append((day, pos, (px - e) * pos * PV - COMM, risk * PV, worst - COMM)); pos = 0; break
        if pos != 0:
            k = x - 1
            while np.isnan(C[k]): k -= 1
            px = C[k] - pos * TICK; out.append((day, pos, (px - e) * pos * PV - COMM, risk * PV, worst - COMM))
    t = pd.DataFrame(out, columns=["d", "side", "net", "risk", "adv"]).set_index("d"); t["R"] = t.net / t.risk; return t


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = load("GC")
    res = {}
    for mode in ("A", "B"):
        for stop in ("pct", "range"):
            t = run(g, mode, stop); res[(mode, stop)] = t
            print(line(t.net, f"clock {mode} ({'NY+7' if mode == 'A' else 'GMT+3'}), stop {stop}", 34)
                  + f" | avg R {t.R.mean():+.3f}, longs ${t.net[t.side > 0].mean():.0f}, shorts ${t.net[t.side < 0].mean():.0f}")
    t = res[("A", "pct")]
    print("\nas described (NY+7, 1% stop) by year:", t.net.groupby(t.index.year).sum().round(0).astype(int).to_dict())
    rng = np.random.default_rng(1); pl = [run(g, "A", "pct", rng=rng).net.mean() for _ in range(20)]
    print(f"placebo (random side at the breakout price, same days, 20 runs): mean ${np.mean(pl):.0f}, max ${np.max(pl):.0f}; real ${t.net.mean():.0f}")
    print("\nsl% sensitivity (NY+7):")
    for sl in (0.5, 0.75, 1.5):
        x = run(g, "A", "pct", sl); print(line(x.net, f"stop {sl}%", 34) + f" | avg R {x.R.mean():+.3f}")
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days >= "2018-01-02"]
    d = t.net.groupby(t.index).sum().reindex(days).fillna(0)
    print("\nstandard metrics, 1 GC (NY+7, 1% stop):"); print(M.table({"all": (d, t.net), "longs": (t.net[t.side > 0].groupby(t.index[t.side > 0]).sum().reindex(days).fillna(0), t.net[t.side > 0]),
                                                              "shorts": (t.net[t.side < 0].groupby(t.index[t.side < 0]).sum().reindex(days).fillna(0), t.net[t.side < 0])}))
    b, p = R.report({"2023+": d[d.index >= "2023"]}, n=2000); print(b); print(p)
    t.to_pickle(SP + "gold15m_trades.pkl")
