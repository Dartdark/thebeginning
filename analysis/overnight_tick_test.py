"""NQ Overnight Anomaly 'Optimized' = Overnight TickRSV / VIX (user's description + screenshots, 2026-10-24; Codex source
review agents/codex/results/overnight_tickrsv_review.md: WATCH, needs code / data; candidate folder
checks/candidates/overnight_tick/). Rebuild of the described rule on the 24-hour NQ grid (Central time), 2018-2026:
  prior RTH (08:30-15:00 CT = 09:30-16:00 ET): close < open, last bar not before 14:00 CT (no early close);
  TickRSV = (up - down) / (up + down) over 14:15-15:15 CT (15:15-16:15 ET); up / down = aggressor buy / sell volume from
  The Bridge (data/OF_1min_*, the closest data we own to MultiCharts' UpTicks / DownTicks; ends 2026-07-07); second proxy
  from the NQ grid: volume signed by each 1-minute bar's direction;
  VIX: that day's daily close vs the SMA of the last L closes (L 20 = code default, 25 = the author's pick);
  entry if (RSV < 0 and VIX > SMA) or (RSV >= 0 and VIX <= SMA): long at 17:05 CT (18:05 ET bar), exit at 03:00 CT (04:00 ET),
  no stop, 1 NQ. Sunday evenings use Friday's session; one night per RTH session (a holiday Monday evening is skipped). Nights with a contract switch are dropped (as Overnight Anomaly).
Costs per NQ round trip $7.25 + 1 tick per fill. Trades dated by the exit day. Author's split: IS -> 2024-02-12, OOS after.
  python3 analysis/overnight_tick_test.py SCRATCH_DIR
"""
import sys, glob, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from overnight_round import roll_minutes
from co_oc_reversal_test import line
import metrics as M, resampling as R, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COMM = 20.0, 0.25, 7.25
OOS = pd.Timestamp("2024-02-13")


def rsv_of():
    d = pd.concat([pd.read_csv(f, usecols=["date", "time", "upvol", "downvol"]) for f in sorted(glob.glob("data/OF_1min_20*.csv"))])
    d = d[(d.time > 1515) & (d.time <= 1615)].groupby("date")[["upvol", "downvol"]].sum()
    tot = d.upvol + d.downvol
    return ((d.upvol - d.downvol) / tot.where(tot > 0)).rename(lambda x: pd.Timestamp(str(x)))


def nights(g):
    tr = set(g.trading.tolist()); rows = []
    rolls = np.sort(roll_minutes(g, "NQ"))
    jj = np.arange(jof(831), jof(1500) + 1); w = np.arange(jof(1416), jof(1515) + 1)
    for r in range(1, g.D - 1):
        if not (np.isfinite(g.o[r, jof(1706)]) and np.isfinite(g.o[r + 1, jof(301)])): continue
        rp = next((k for k in range(r, r - 4, -1) if k in tr), None)
        if rp is None: continue
        c = g.c[rp, jj]
        if not np.isfinite(c).any(): continue
        last = jj[np.flatnonzero(np.isfinite(c))[-1]]
        o = g.o[rp, jj][np.isfinite(g.o[rp, jj])][0]; cl = c[np.isfinite(c)][-1]
        bo, bc, bv = g.o[rp, w], g.c[rp, w], g.v[rp, w] if hasattr(g, "v") else np.full(len(w), np.nan)
        sv = np.nansum(np.sign(bc - bo) * bv); av = np.nansum(np.abs(np.sign(bc - bo)) * bv)
        ep, xp = g.o[r, jof(1706)], g.o[r + 1, jof(301)]
        a, b = r * 1440 + jof(1706), (r + 1) * 1440 + jof(301)
        roll = ((rolls > a) & (rolls <= b)).any()
        low = np.nanmin(g.l.ravel()[a:b])
        rows.append(dict(date=pd.Timestamp(g.ts[r + 1]), sess=pd.Timestamp(g.ts[rp]), down=cl < o, half=last < jof(1400), roll=roll,
                         rsv_bar=sv / av if av > 0 else np.nan, net=(xp - ep - 2 * TICK) * PV - COMM,
                         adv=min((low - ep - 2 * TICK) * PV - COMM, (xp - ep - 2 * TICK) * PV - COMM)))
    N = pd.DataFrame(rows).drop_duplicates("sess", keep="first")    # one night per RTH session (holiday Mondays reuse none)
    return N[(N.date >= "2018-01-01") & ~N.roll].reset_index(drop=True)


def stats(x, nm):
    days = pd.bdate_range(x.index.min(), x.index.max())
    p = M.perf(x.groupby(x.index).sum().reindex(days, fill_value=0.0), x.values)
    return (f"   {nm:<34} Sharpe {p['sharpe']:4.2f} Sortino {p['sortino']:4.2f} PF {p['profit_factor']:4.2f} "
            f"Calmar {p['calmar']:4.2f} Ulcer {p['ulcer']:4.2f} maxDD ${p['max_dd']:,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb")); N = nights(g)
    rsv = rsv_of(); N["rsv"] = N.sess.map(rsv)
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE
    for L in (10, 20, 25, 30, 40): N[f"hi{L}"] = N.sess.map(vix > vix.rolling(L).mean())
    base = N.down & ~N.half
    have = N.rsv.notna() & N.hi20.notna()
    print(f"nights {len(N)} (2018 -> {N.date.max().date()}), down-day nights {base.sum()}, with order-flow data {(base & have).sum()} "
          f"(order flow ends {rsv.index.max().date()})")
    cell = lambda q, L=25: ((q < 0) & N[f"hi{L}"]) | ((q >= 0) & ~N[f"hi{L}"].astype(bool))
    s = lambda m: N.net[m].set_axis(N.date[m])
    sig = base & have & cell(N.rsv)
    print("\n1. Per NQ after costs (17:05 -> 03:00 CT):")
    for nm, m in (("rule, VIX SMA 25 (author's pick)", sig), ("rule, VIX SMA 20 (code default)", base & have & cell(N.rsv, 20)),
                  ("baseline: every down-day night (same span)", base & have), ("every night (same span)", ~N.half & have)):
        print(line(s(m), nm, 44))
    print("\n   the four cells (down days, SMA 25):")
    hi = N.hi25.astype(bool)
    for nm, m in (("RSV < 0, VIX > SMA   (taken)", (N.rsv < 0) & hi), ("RSV >= 0, VIX <= SMA (taken)", (N.rsv >= 0) & ~hi),
                  ("RSV < 0, VIX <= SMA  (skipped)", (N.rsv < 0) & ~hi), ("RSV >= 0, VIX > SMA  (skipped)", (N.rsv >= 0) & hi)):
        print(line(s(base & have & m), nm, 44))
    print("\n   author's periods (rule, SMA 25):")
    print(line(s(sig & (N.date < OOS)), "IS 2018 -> 2024-02-12", 44)); print(line(s(sig & (N.date >= OOS)), "OOS 2024-02-13 ->", 44))
    print(line(s(base & have & (N.date >= OOS)), "   baseline down days, OOS", 44))
    print("   by year (rule SMA 25 / baseline):", {y: f"{a:,.0f} / {b:,.0f}" for y, a, b in
          zip(*[s(sig).groupby(lambda d: d.year).sum().index], s(sig).groupby(lambda d: d.year).sum(), s(base & have).groupby(lambda d: d.year).sum())})
    print("\n2. Sensitivity (not chosen on): VIX SMA length / second RSV proxy")
    for L in (10, 20, 25, 30, 40): print(line(s(base & have & cell(N.rsv, L)), f"VIX SMA {L}", 44))
    print(line(s(base & N.rsv_bar.notna() & cell(N.rsv_bar)), "RSV from bar-direction volume, SMA 25", 44))
    print(line(s(base & N.rsv_bar.notna() & cell(N.rsv_bar) & (N.date > "2026-07-07")), "  same, after the order-flow data ends", 44))
    print(f"   agreement of the two RSV signs: {np.mean(np.sign(N.rsv[have]) == np.sign(N.rsv_bar[have])):.0%}")
    rng = np.random.default_rng(20261024); pool = s(base & have).values; k = sig.sum(); mb = s(sig).mean()
    dr = np.array([rng.choice(pool, k, replace=False).mean() for _ in range(2000)])
    print(f"\n3. Random down-day nights, same count {k} (2,000 draws): mean ${dr.mean():.1f}, p95 ${np.percentile(dr, 95):.1f}; rule ${mb:.1f}; "
          f"share of draws >= rule {np.mean(dr >= mb):.1%}")
    rsh = []
    for _ in range(500):
        perm = N.hi25.sample(frac=1, random_state=int(rng.integers(1e9))).values
        hp = pd.Series(perm, index=N.index).astype(bool)
        m = base & have & (((N.rsv < 0) & hp) | ((N.rsv >= 0) & ~hp)); rsh.append(s(m).mean())
    print(f"   VIX regime shuffled across nights (500): mean ${np.mean(rsh):.1f}, p95 ${np.percentile(rsh, 95):.1f}; share >= rule {np.mean(np.array(rsh) >= mb):.1%}")
    print("\n4. Standard metrics per NQ (rule SMA 25; long only):")
    print(stats(s(sig), "rule all")); print(stats(s(sig & (N.date >= "2023-01-01")), "rule 2023+"))
    print(stats(s(base & have), "baseline down days all"))
    t = N[sig][["date", "sess", "net", "adv", "rsv", "rsv_bar"]].assign(side=1)
    print(MC.report(t.net, t.set_index("date").net.groupby(level=0).sum().reindex(pd.bdate_range(t.date.min(), t.date.max()), fill_value=0.0), size=0.1, label="1 MNQ"))
    t.to_csv("checks/candidates/overnight_tick/python_trades.csv", index=False)
    N.to_csv("checks/candidates/overnight_tick/nights.csv", index=False)
