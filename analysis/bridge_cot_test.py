"""The Bridge's OFB_CotDealerRank_Signal (TFF dealer net, 13-week rank) and its Legacy sister, on NQ, 2026-10-13.

Data: COT_NQ.csv (repo root), exported with multi_strategy/OFB_COT_Exporter.txt: one row per CFTC release with the
chart time it became known (Friday ~14:30-15:45 CT, Sunday 17:15 after holiday Fridays, catch-up dates after the
2019 / 2025 shutdowns). A value is used only from the bar after that time.
State at a release: LONG if rank > RankHi and the last completed daily close > its 50-day SMA, SHORT if rank <
RankLo and the close < SMA, else FLAT. TFF: rank13, 70 / 30. Legacy: rank26, 60 / 40.
  A. As written: re-decided at each release, entry / exit at the next bar's open, held through the week (NOT
     Apex-legal: held overnight and over weekends).
  B. Apex-legal: on each trading day trade the regular session 8:30 open -> 15:00 close in the state known at the
     open (state from the last release before that day).
  C. The plan's MultiCharts trades split by whether they agree with the state.
Per NQ after $7.25 + 1 tick per market fill. Daily close = the last trade at or before 16:00 CT.
  python3 analysis/bridge_cot_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PV, TICK, COST = 20.0, 0.25, 7.25
VARIANTS = {"TFF dealer rank13 70/30 (default)": ("tff_rank13", 70, 30), "TFF rank26 70/30": ("tff_rank26", 70, 30),
            "Legacy commercial rank26 60/40 (sister)": ("leg_rank26", 60, 40), "Legacy rank13 70/30": ("leg_rank13", 70, 30)}


def daily_close(g):
    cf = pd.DataFrame(g.c[:, :jof(1600) + 1]).ffill(axis=1).iloc[:, -1].to_numpy()
    has = ~np.isnan(g.c[:, jof(830):jof(1500)]).all(1)
    return np.where(has, cf, np.nan)


def states(g, cot, col, hi, lo, trend=True, sma_n=50):
    """State per release: +1 / -1 / 0 and the flattened minute index from which it applies."""
    dc = daily_close(g); tr = g.trading
    s = pd.Series(dc[tr], index=tr).dropna(); sma = s.rolling(sma_n).mean()
    out = []
    for r in cot.itertuples():
        d = np.searchsorted(g.dates, r.date); t = r.time
        k = s.index.searchsorted(d, side="left") - 1          # last completed daily close before the release day
        if k < sma_n: continue
        c, m = s.iloc[k], sma.iloc[k]
        rk = getattr(r, col)
        st = 1 if (rk > hi and (c > m or not trend)) else (-1 if (rk < lo and (c < m or not trend)) else 0)
        out.append((d * 1440 + jof(t) + 1, st, pd.Timestamp(str(r.date))))
    return out


def weekly(g, st):
    """A: re-decide at each release, next minute's open; hold to the next release."""
    of = pd.Series(g.o.ravel()).bfill().to_numpy()
    out = []; pos = 0; e = None; t0 = None
    for (k, s_, dt) in st:
        if s_ == pos: continue
        px = of[k]
        if pos != 0:
            x = px - pos * TICK
            out.append(dict(date=t0, exit_date=dt, side=pos, entry=e, exit=x, net=(x - e) * pos * PV - COST))
        if s_ != 0: e = px + s_ * TICK; t0 = dt
        pos = s_
    return pd.DataFrame(out)


def daily(g, st, rand=None):
    """B: each trading day, 8:30 open -> 15:00 close in the state known at the open."""
    ks = np.array([x[0] for x in st]); ss = np.array([x[1] for x in st])
    ts = pd.DatetimeIndex(g.ts); rng = np.random.default_rng(rand) if rand is not None else None
    out = []
    for d in g.trading:
        if ts[d].year < 2018: continue
        i = np.searchsorted(ks, d * 1440 + jof(831), side="right") - 1
        if i < 0 or ss[i] == 0: continue
        o, c = g.o[d, jof(831)], g.c[d, jof(1500)]
        if np.isnan(o) or np.isnan(c): continue
        side = int(ss[i]) if rng is None else int(rng.choice([-1, 1]))
        out.append(dict(day=d, date=ts[d], side=side, j0=jof(831), j1=jof(1500), entry=o + side * TICK, exit=c - side * TICK,
                        kind=2, slips=0, net=(c - o - 2 * side * TICK) * side * PV - COST))
    return pd.DataFrame(out)


def line(t, nm, w=48):
    if len(t) < 3: return f"{nm:<{w}} n={len(t)}"
    x = t.net; y = pd.to_datetime(t.date).dt.year; by = x.groupby(y).sum()
    pf = lambda q: q[q > 0].sum() / max(1e-9, -q[q < 0].sum())
    return (f"{nm:<{w}} n={len(x):4d} win {np.mean(x > 0):.0%} avg ${x.mean():6.0f} PF {pf(x):.2f} t={x.mean() / x.std() * np.sqrt(len(x)):4.1f}"
            f" yrs+ {(by > 0).sum()}/{len(by)} | 18-22 ${x[y < 2023].mean():6.0f} | 23-26 ${x[y >= 2023].mean():6.0f}"
            f" | L ${x[t.side > 0].mean():6.0f} (n {np.sum(t.side > 0)}) S ${x[t.side < 0].mean():6.0f} (n {np.sum(t.side < 0)})")


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    cot = pd.read_csv("data/COT_NQ.csv")
    print(__doc__.split("\n")[0]); print(f"releases: {len(cot)} ({cot.date.min()} .. {cot.date.max()})")
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[days.year >= 2018]
    dl = lambda t: t.groupby(pd.to_datetime(t.date)).net.sum().reindex(days, fill_value=0.0)
    D = {}
    for nm, (col, hi, lo) in VARIANTS.items():
        st = states(g, cot, col, hi, lo)
        print(f"\n== {nm}: state shares long {np.mean([x[1] == 1 for x in st]):.0%}, short {np.mean([x[1] == -1 for x in st]):.0%}")
        w = weekly(g, st)
        print("A. as written (weekly hold): " + line(w, "", 0))
        nt = weekly(g, states(g, cot, col, hi, lo, trend=False))
        print("   without the 50-day SMA filter: " + line(nt, "", 0))
        d_ = daily(g, st); D[nm] = d_
        print("B. Apex daily (8:30 -> 15:00):  " + line(d_, "", 0))
        pl = [daily(g, st, rand=r).net.mean() for r in range(20)]
        print(f"   placebo (same days, random side, 20 runs): ${np.mean(pl):.0f} ({min(pl):.0f}..{max(pl):.0f}) vs ${d_.net.mean():.0f}")

    # control: the 50-day SMA trend alone (long above / short below), every day
    st_sma = states(g, cot, "tff_rank13", -1, 101)          # rank always > -1 -> long when above SMA; < 101 short below
    print("\nControl: the 50-day SMA trend alone (long above, short below, Apex daily): " + line(daily(g, st_sma), "", 0))
    always_long = daily(g, states(g, cot, "tff_rank13", -1, -1, trend=False))
    print("Control: long every day 8:30 -> 15:00: " + line(always_long, "", 0))

    base = D["TFF dealer rank13 70/30 (default)"]
    print("\nStandard metrics per NQ (Apex daily version, TFF default):")
    rows = {"all": (dl(base), base.net), "longs": (dl(base[base.side > 0]), base.net[base.side > 0]),
            "shorts": (dl(base[base.side < 0]), base.net[base.side < 0])}
    print(M.table(rows))
    bt, pm = R.report({f"{k} 2023+": v[0][v[0].index >= "2023-01-01"] for k, v in rows.items()}, n=3000); print(bt); print(pm)

    print("\nC. The plan's MultiCharts trades vs the TFF state known at entry (agree / disagree / flat state):")
    st = states(g, cot, "tff_rank13", 70, 30); ks = np.array([x[0] for x in st]); ss = np.array([x[1] for x in st])
    for nm, (f, _) in REPORTS.items():
        if nm == "OND_MC": continue
        t = with_slippage(load_mc(g, f)); t["net"] = (t.exit - t.entry) * t.side * PV - COST
        t["date"] = pd.DatetimeIndex(g.ts[t.day.values]); t = t[t.date.dt.year >= 2018]
        i = np.searchsorted(ks, t.day.to_numpy() * 1440 + t.j0.to_numpy(), side="right") - 1
        stt = np.where(i >= 0, ss[np.maximum(i, 0)], 0) * t.side.to_numpy()
        a, b, z = t.net[stt > 0], t.net[stt < 0], t.net[stt == 0]
        dt = (a.mean() - b.mean()) / np.sqrt(a.var() / max(len(a), 1) + b.var() / max(len(b), 1)) if len(a) > 2 and len(b) > 2 else np.nan
        print(f"   {nm:<12} agree ${a.mean():6.0f} (n {len(a):4d}) | disagree ${b.mean():6.0f} (n {len(b):4d}) | flat ${z.mean():6.0f} (n {len(z):4d}) | diff t {dt:+.1f}")

    print("\nControl for A: weekly hold, long whenever the close > 50-day SMA at a release (no COT), flat otherwise:")
    w_sma = weekly(g, states(g, cot, "tff_rank13", -1, -1))
    print("   " + line(w_sma, "", 0))
    w_cot = weekly(g, states(g, cot, "tff_rank13", 70, 30))
    wl = w_cot[w_cot.side > 0]
    print(f"   TFF default longs only: n {len(wl)} avg ${wl.net.mean():.0f}; per week held: COT longs "
          f"${wl.net.sum() / max(1, ((pd.to_datetime(wl.exit_date) - pd.to_datetime(wl.date)).dt.days.sum() / 7)):.0f}"
          f" vs SMA-only ${w_sma.net.sum() / max(1, ((pd.to_datetime(w_sma.exit_date) - pd.to_datetime(w_sma.date)).dt.days.sum() / 7)):.0f}")
