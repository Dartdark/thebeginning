"""Offset Donchian breakout + MA5 / MA50 filter ('Donkey w/ MAVS', user's file 2026-10-24; checks/candidates/donchian_mavs/).
User's MultiCharts run: MGCZ6 1-minute, NumContracts 3, StopTradeTime 1399, 2026-06-08 -> 08-28: ~4,100 trades, PF ~8.
Rebuild as coded on our GC 1-minute bars (data/GC_1min_*, CT, close-stamped), per 1 MGC ($10 a point, tick 0.1 = $1):
  bands from closes [5..14] bars back; long if close > that high, close outside the live 10-bar range, MA5 > MA50 (short mirror);
  entry next bar open (reverses); exits: stop at the opposite offset band (fills at the open when the open is already beyond it),
  close crossing MA5 -> next bar open; daily caps -$500 / +$1,000 on 3 contracts, reset at midnight; entries 18:00 -> 13:59.
Costs per MGC round trip: commission $1.04 + 1 tick per market / stop fill ($2), and a zero-cost run like the report's.
  python3 analysis/donchian_mavs_test.py
"""
import glob, numpy as np, pandas as pd
PV, TICK, COMM, Q = 10.0, 0.1, 1.04, 3


def load(yrs):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/GC_1min_20*.csv")) if int(f[-8:-4]) in yrs])
    return d.drop_duplicates(["date", "time"]).sort_values(["date", "time"]).reset_index(drop=True)


def run(d, L=10, off=5, ma=5, tma=50, start=1800, stop=1399, costs=True):
    c, o, h, l = (d[k].to_numpy(float) for k in ("close", "open", "high", "low"))
    t, dt = d.time.to_numpy(), d.date.to_numpy(); s = pd.Series(c)
    ub = s.shift(off).rolling(L).max().to_numpy(); lb = s.shift(off).rolling(L).min().to_numpy()
    cu = s.rolling(L).max().to_numpy(); cl = s.rolling(L).min().to_numpy()
    m5 = s.rolling(ma).mean().to_numpy(); m50 = s.rolling(tma).mean().to_numpy()
    pos, ep, rows = 0, 0.0, []; day, day0, realized = None, 0.0, 0.0
    slip = TICK if costs else 0.0; fee = COMM if costs else 0.0
    def close_at(px, j, why):
        nonlocal pos, realized
        px = px - pos * slip; pnl = (px - ep) * pos * PV - fee
        rows.append(dict(date=dt[j], time=t[j], side=pos, pnl=pnl, why=why)); realized += pnl; pos = 0
    for i in range(tma + L + off, len(c) - 1):
        if dt[i] != day: day = dt[i]; day0 = realized
        dpnl = (realized - day0 + (pos * (c[i] - ep) * PV if pos else 0)) * Q
        cap = dpnl <= -500 or dpnl >= 1000
        win = (t[i] >= start or t[i] < stop) if start > stop else (start <= t[i] < stop)
        j = i + 1; mkt_exit = False; new = 0
        if pos and cap: mkt_exit = True
        if pos == 1 and not cap and c[i] < m5[i] and c[i - 1] >= m5[i - 1]: mkt_exit = True
        if pos == -1 and not cap and c[i] > m5[i] and c[i - 1] <= m5[i - 1]: mkt_exit = True
        out = c[i] >= cu[i] or c[i] <= cl[i]
        if not cap and win and out:
            if pos <= 0 and c[i] > ub[i] and m5[i] > m50[i]: new = 1
            elif pos >= 0 and c[i] < lb[i] and m5[i] < m50[i]: new = -1
        stp = lb[i] if pos == 1 else ub[i] if pos == -1 else np.nan
        if pos and (mkt_exit or (new and new != pos)): close_at(o[j], j, "mkt")
        elif pos == 1 and not cap and (o[j] <= stp or l[j] <= stp): close_at(min(o[j], stp), j, "stop")
        elif pos == -1 and not cap and (o[j] >= stp or h[j] >= stp): close_at(max(o[j], stp), j, "stop")
        if new and pos == 0: pos = new; ep = o[j] + new * slip
    x = pd.DataFrame(rows); x["d"] = pd.to_datetime(x.date.astype(str)); return x


def line(x, nm):
    p = x.pnl; pf = p[p > 0].sum() / max(1e-9, -p[p < 0].sum()); tt = p.mean() / p.std() * np.sqrt(len(p))
    by = p.groupby(x.d.dt.year).sum()
    return (f"   {nm:<42} n={len(p):6d} win {np.mean(p > 0):.0%} ${p.mean():6.2f}/MGC PF {pf:4.2f} t {tt:5.1f} "
            f"total x3 ${3 * p.sum():>10,.0f} | yrs+ {(by > 0).sum()}/{len(by)}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    d26 = load({2026}); w = d26[(d26.date >= 20260608) & (d26.date <= 20260828)].reset_index(drop=True)
    print("\n1. The report's period (2026-06-08 -> 08-28), per 1 MGC:")
    print(line(run(w, costs=False), "no costs (as the report)")); print(line(run(w), "with costs"))
    a = run(load(set(range(2018, 2027))))
    print("\n2. 2018-2026, with costs:"); print(line(a, "all"))
    print(line(a[a.side > 0], "longs")); print(line(a[a.side < 0], "shorts"))
    print("   by year x3 MGC:", a.groupby(a.d.dt.year).pnl.sum().mul(3).round(0).astype(int).to_dict())
    print("   gross per trade (no costs), 2018-26:", f"${run(load(set(range(2018, 2027))), costs=False).pnl.mean():.2f}/MGC; costs ${COMM + 2 * TICK * PV:.2f}")
