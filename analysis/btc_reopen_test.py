"""BTC Reopen MR V4 (H1B_z_lb60_abs1.5; user's NinjaTrader package, 2026-10-24; MultiCharts port and source in
checks/candidates/btc_reopen_mr_v4/). Python rebuild of the rule on our CME BTC futures 1-minute bars (data/BTC_1min_*,
Central time, stamped at the close) and Coinbase spot BTC-USD 1-minute bars (data/BTCUSD_spot_1min_*, same stamping).
  Event: the first futures bar after a scheduled 17:00 CT reopen (Mon-Thu after the 16:00 close; Sun after Fri 16:00) with
  gap >= 30 min, bar <= reopen + 15 min, previous bar <= close + 15 min, not a special-session date (the port's list),
  not in the post-roll warm-up (60 bars with fresh spot after each roll date of the port's list).
  residual bps = 1e4 x [(reopen close / pre-close close - 1) - (spot at reopen / spot at the pre-close bar - 1)]; spot =
  the last spot bar at or before the futures bar, <= 5 min old. Z vs the previous 60 residuals (sample sd); |Z| >= 1.5:
  fade (Z > 0 short) at the next futures bar's open; exit at the open of the bar after the first bar stamped >= fill + 60 min.
Costs per CME BTC contract (5 coins, $25 a $5 tick): $25 round trip + 1 tick per market fill (entry and exit) = $75;
also 2 and 4 ticks a fill (the author's quote-based replay cut 64% of the no-cost result). Author's research window
2018-06-11 .. 2024-09-01 (ours starts 2018-12-17); their sealed period 2024-09-02 onward is reported separately.
  python3 analysis/btc_reopen_test.py
"""
import sys, re, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, resampling as R

PV, TICK, COMM = 5.0, 5.0, 25.0          # $ per index point per contract, tick in points, commission round trip
PORT = "checks/candidates/btc_reopen_mr_v4/BTC_Reopen_MR_V4.txt"


def load(pat):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(pat))], ignore_index=True).drop_duplicates(["date", "time"])
    d["dt"] = pd.to_datetime(d.date.astype(str), format="%Y%m%d") + pd.to_timedelta(d.time // 100 * 60 + d.time % 100, unit="m")
    return d.sort_values("dt").reset_index(drop=True)


def lists():
    s = open(PORT).read()
    el = lambda x: pd.Timestamp(year=1900 + int(x) // 10000, month=int(x) // 100 % 100, day=int(x) % 100)
    return ({el(x) for x in re.findall(r"ExD\[\d+\] = (\d+);", s)}, sorted(el(x) for x in re.findall(r"RoD\[\d+\] = (\d+);", s)))


def events(f, s, look=60, zthr=1.5, max_age=5.0, roll_guard=True):
    excl, rolls = lists()
    sp = pd.merge_asof(f[["dt"]], s[["dt", "close"]].rename(columns={"dt": "sdt", "close": "spot"}), left_on="dt", right_on="sdt",
                       direction="backward")
    age = (f.dt - sp.sdt).dt.total_seconds() / 60
    f = f.assign(spot=sp.spot.where((age >= 0) & (age <= max_age)))
    dt = f.dt.to_numpy(); gap = np.r_[np.nan, np.diff(dt).astype("timedelta64[s]").astype(float) / 60]
    fresh = f.spot.notna().to_numpy()
    # post-roll warm-up: index of the first bar on or after each roll date; fresh-spot bars counted from it
    arm = np.searchsorted(dt, np.array(rolls, dtype="datetime64[ns]")) if roll_guard else np.array([], int)
    cfresh = np.r_[0, np.cumsum(fresh)]
    out, hist = [], []
    for i in np.where(gap >= 30)[0]:
        cur, prev = pd.Timestamp(dt[i]), pd.Timestamp(dt[i - 1])
        cands = []
        for d in {prev.normalize(), cur.normalize()}:
            w = (d.dayofweek + 1) % 7                                     # 0 = Sunday .. 6 = Saturday
            if 0 <= w <= 4:
                r = d + pd.Timedelta(hours=17)
                if prev < r <= cur: cands.append((r, w == 0, d))
        if not cands: continue
        r, wk, d = min(cands)
        close = (d - pd.Timedelta(days=2) if wk else d) + pd.Timedelta(hours=16)
        if d in excl or (wk and (d - pd.Timedelta(days=2)) in excl): continue
        if not ((cur - r).total_seconds() / 60 <= 15 and (prev - close).total_seconds() / 60 <= 15): continue
        if roll_guard:
            a = arm[arm <= i]
            if len(a) and cfresh[i] - cfresh[a.max()] < look: continue
        if not (fresh[i] and fresh[i - 1]): continue
        res = 1e4 * ((f.close[i] / f.close[i - 1] - 1) - (f.spot[i] / f.spot[i - 1] - 1))
        z = np.nan
        if len(hist) >= look:
            h = np.array(hist[-look:]); sd = h.std(ddof=1)
            if sd > 1e-12: z = (res - h.mean()) / sd
        hist.append(res)
        out.append(dict(i=i, dt=cur, reopen=r, weekend=wk, resid=res, z=z))
    return pd.DataFrame(out)


def trades(f, ev, zthr=1.5, hold=60, ticks=1):
    o, dt = f.open.to_numpy(), f.dt.to_numpy(); rows = []; busy = np.datetime64("1900-01-01")
    for e in ev[ev.z.abs() >= zthr].itertuples():
        j = e.i + 1
        if j >= len(f) or dt[e.i] < busy: continue
        side = -1 if e.z > 0 else 1; fill = dt[j]; entry = o[j]
        k = np.searchsorted(dt, fill + np.timedelta64(hold, "m"))          # first bar stamped >= fill + hold
        if k + 1 >= len(f): break
        ex = o[k + 1]; busy = dt[k + 1]
        gross = (ex - entry) * side * PV
        rows.append(dict(date=pd.Timestamp(dt[e.i]).normalize(), dt=pd.Timestamp(dt[e.i]), side=side, z=e.z, weekend=e.weekend,
                         entry=entry, exit=ex, gross=gross, net=gross - COMM - 2 * ticks * TICK * PV,
                         hold_min=(dt[k + 1] - fill).astype("timedelta64[m]").astype(int)))
    return pd.DataFrame(rows)


def line(t, nm):
    if len(t) < 3: return f"   {nm:<40} n={len(t)}"
    x = t.net; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum()); tt = x.mean() / x.std() * np.sqrt(len(x))
    by = x.groupby(t.date.dt.year).sum()
    return (f"   {nm:<40} n={len(x):4d} win {np.mean(x > 0):.0%} ${x.mean():7.0f} total ${x.sum():9,.0f} PF {pf:4.2f} t {tt:4.1f} "
            f"yrs+ {(by > 0).sum()}/{len(by)} | gross ${t.gross.mean():6.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    f = load("data/BTC_1min_20*.csv"); s = load("data/BTCUSD_spot_1min_20*.csv")
    print(f"futures {f.dt.min()} -> {f.dt.max()} ({len(f):,} bars); spot {s.dt.min()} -> {s.dt.max()} ({len(s):,} bars)")
    ev = events(f, s); print(f"eligible reopen events {len(ev)} (weekend {ev.weekend.sum()}), with a z {ev.z.notna().sum()}, |z| >= 1.5 {(ev.z.abs() >= 1.5).sum()}")
    SPENT, SEAL = "2024-09-02", "2024-09-02"
    for tk in (1, 2, 4):
        t = trades(f, ev, ticks=tk)
        a, b = t[t.dt < SPENT], t[t.dt >= SEAL]
        print(f"\n{tk} tick(s) a fill (${COMM:.0f} + ${2 * tk * TICK * PV:.0f} a round trip), per CME BTC contract:")
        print(line(a, "author's window (2018-12 .. 2024-09-01)")); print(line(b, "sealed period (2024-09-02 ..)"))
        print(line(t, "all")); print(line(t[t.side > 0], "   longs")); print(line(t[t.side < 0], "   shorts"))
        print(line(t[t.weekend], "   weekend reopens")); print(line(t[~t.weekend], "   daily reopens"))
        if tk == 1:
            print("   by year (net):", t.groupby(t.date.dt.year).net.sum().round(0).astype(int).to_dict())
            t1 = t
    rng = np.random.default_rng(1); ev2 = ev.copy(); rr = []
    for _ in range(200):
        ev2["z"] = ev.z * rng.choice([-1, 1], len(ev)); rr.append(trades(f, ev2).net.mean())
    print(f"\nRandom side at the same events (200 runs, 1 tick): ${np.mean(rr):.0f} (p95 ${np.percentile(rr, 95):.0f}) vs ${t1.net.mean():.0f}")
    for zt in (1.0, 2.0):
        print(line(trades(f, ev, zthr=zt), f"|z| >= {zt}"))
    for h in (30, 120):
        print(line(trades(f, ev, hold=h), f"hold {h} min"))
    print(line(trades(f, events(f, s, roll_guard=False)), "no roll guard"))
    alld = pd.date_range(t1.date.min(), t1.date.max())          # calendar days: Sunday reopens trade
    dl = lambda q: q.groupby(q.date).net.sum().reindex(alld, fill_value=0.0)
    print("\nStandard metrics (1 tick, per contract):")
    print(M.table({"BTC reopen": (dl(t1), t1.net), "longs": (dl(t1[t1.side > 0]), t1.net[t1.side > 0]), "shorts": (dl(t1[t1.side < 0]), t1.net[t1.side < 0])}))
    t1.to_csv("checks/candidates/btc_reopen_mr_v4/python_trades.csv", index=False)
