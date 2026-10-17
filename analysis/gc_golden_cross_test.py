"""User's rule (2026-10-17): gold futures (GC), 1-hour chart, buy when SMA50 crosses above SMA200, close when it crosses
back below; no stop, no target; Oct 2023 - Oct 2026. As written (long only, held overnight / over weekends).
Fills at the next hourly bar's open, $7.25 + 1 tick ($10) per side per GC ($100 / point). Prices back-adjusted for
contract rolls (roll bars from s_rank_gap_round2_test.rolls_gc; unadjusted data jump UP at gold rolls, flattering longs).
Context: buy-and-hold over the same span, time in market, 2018-26 by year, random-entry placebo with the same holding
times, Monte Carlo at 1 MGC. NOTE: holds overnight, so it can't run on Apex (flat by 15:59 CT).
  python3 analysis/gc_golden_cross_test.py
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import s_rank_gap_round2_test as SR, montecarlo as MC, metrics as M

PV, COST = 100.0, 7.25 + 10.0


def hourly():
    S = SR.Sym("GC"); bars, _ = SR.rolls_gc(S); S.set_rolls(bars)
    j, _, _ = S.jumps(); adj = np.zeros(S.N); adj[S.rollbars] = np.nan_to_num(j[S.rollbars])
    cum = np.cumsum(adj)                           # jumps up to and including t
    ts = pd.DatetimeIndex(S.TS).repeat(1440) + pd.to_timedelta(np.tile(np.arange(1440), len(S.TS)), unit="m")
    df = pd.DataFrame(dict(o=S.O - cum + cum[-1], h=S.H - cum + cum[-1], l=S.L - cum + cum[-1], c=S.C - cum + cum[-1]), index=ts)
    df.loc[np.isnan(S.C)] = np.nan
    # back-adjusted to the latest contract: each price + the roll jumps that came after it
    df = df.dropna()
    hb = df.resample("60min", label="right", closed="right").agg(dict(o="first", h="max", l="min", c="last")).dropna()
    return hb, S


def run(hb, start, end):
    c = hb.c; f, s = c.rolling(50).mean(), c.rolling(200).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1)); dn = (f < s) & (f.shift(1) >= s.shift(1))
    trades = []; pos = None; idx = hb.index
    for i in range(len(hb) - 1):
        t = idx[i]
        if pos is None and up.iloc[i] and start <= t < end: pos = (idx[i + 1], hb.o.iloc[i + 1])
        elif pos is not None and dn.iloc[i]:
            trades.append(dict(entry_time=pos[0], entry=pos[1], exit_time=idx[i + 1], exit=hb.o.iloc[i + 1])); pos = None
    if pos is not None: trades.append(dict(entry_time=pos[0], entry=pos[1], exit_time=idx[-1], exit=hb.c.iloc[-1], open=True))
    t = pd.DataFrame(trades); t["net"] = (t.exit - t.entry) * PV - 2 * COST; t["days"] = (t.exit_time - t.entry_time).dt.total_seconds() / 86400
    return t


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    hb, S = hourly()
    A, B = pd.Timestamp("2023-10-01"), pd.Timestamp("2026-10-14")
    t = run(hb, A, B); t = t[t.entry_time < B]
    inmkt = t.days.sum() / ((B - A).days)
    bh0 = hb.c[hb.index >= A].iloc[0]; bh1 = hb.c[hb.index < B].iloc[-1]
    print(f"\nOct 2023 - Oct 2026 (1 GC, roll-adjusted, net): {len(t)} trades, total ${t.net.sum():,.0f}, avg ${t.net.mean():,.0f}, "
          f"win {np.mean(t.net > 0):.0%}, PF {t.net[t.net > 0].sum() / max(1, -t.net[t.net < 0].sum()):.2f}; median hold {t.days.median():.1f} days, "
          f"in the market {inmkt:.0%} of the time")
    print(f"   buy and hold 1 GC over the same span: ${(bh1 - bh0) * PV:,.0f} (gold {bh0:.0f} -> {bh1:.0f}, roll-adjusted)")
    print(f"   biggest trades: " + ", ".join(f"{r.entry_time:%Y-%m-%d} {r.days:.0f}d ${r.net:,.0f}" for r in t.nlargest(3, 'net').itertuples()))
    # worst open drawdown inside trades (no stop)
    worst = []
    for r in t.itertuples():
        w = hb.l[(hb.index >= r.entry_time) & (hb.index <= r.exit_time)].min(); worst.append((w - r.entry) * PV)
    print(f"   worst open loss inside a trade: ${min(worst):,.0f} per GC (${min(worst) / 10:,.0f} per MGC; Apex trailing drawdown $2,000)")
    # full history by year
    T = run(hb, pd.Timestamp("2018-01-01"), B)
    print("\n2018-26, same rule:", f"{len(T)} trades, avg ${T.net.mean():,.0f}, t {T.net.mean() / T.net.std() * np.sqrt(len(T)):.1f}")
    by = T.net.groupby(T.entry_time.dt.year).sum(); bhy = hb.c.groupby(hb.index.year).agg(["first", "last"]); bhy = (bhy["last"] - bhy["first"]) * PV
    print("   by year, rule / buy-and-hold ($ per GC): " + " | ".join(f"{y} {by.get(y, 0):,.0f} / {bhy[y]:,.0f}" for y in by.index))
    # placebo: random entries with the same holding times, Oct 2023 - Oct 2026
    rng = np.random.default_rng(1); ix = hb.index[(hb.index >= A) & (hb.index < B)]; pl = []
    for _ in range(2000):
        tot = 0.0
        for d in t.days:
            e = ix[rng.integers(0, len(ix))]; x = hb.index.searchsorted(e + pd.Timedelta(days=d)); x = min(x, len(hb) - 1)
            tot += (hb.c.iloc[x] - hb.c.loc[e]) * PV - 2 * COST
        pl.append(tot)
    pl = np.array(pl); print(f"\nPlacebo (random entries, same holding times, Oct 2023 - Oct 2026): median ${np.median(pl):,.0f}, 95th ${np.percentile(pl, 95):,.0f}; "
                             f"P(random >= rule) {np.mean(pl >= t.net.sum()):.2f}")
    days = pd.bdate_range(A, B); dl = t.net.groupby(t.exit_time.dt.normalize()).sum().reindex(days, fill_value=0)
    print(M.table({"GC golden cross 1h, per GC": (dl, t.net)}))
    print(MC.report(t.net.to_numpy(), dl.to_numpy(), size=0.1, label="at 1 MGC"))
