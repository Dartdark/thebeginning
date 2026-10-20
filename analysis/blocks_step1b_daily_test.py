"""Building blocks, Step 1b: the entry blocks AS DESIGNED (daily bars, multi-day holds, many markets), for a personal
account (pre-registered 2026-10-20, written before any result). Not Apex: positions are held overnight.

Why: Step 1 (analysis/blocks_step1_test.py) ran the blocks intraday on 15-min bars because Apex (evaluation AND funded)
must be flat by 15:59 CT; 62 / 64 failed. The catalog's blocks come from swing / trend-following practice on daily charts
across many futures, so test them there before judging the library. Library: analysis/blocks_daily.py.

Pre-registered plan (fixed before running):
  Markets: NQ ES YM GC CL ZN 6E (all the 1-minute data we have 2018-2026). Daily bar = 15:00 CT close, roll-adjusted.
  Entries: the same 9 blocks with the catalog's default lengths (E1 three up / down days, E2 10-day close breakout, E3 its
    fade, E4 low-volume fade, E5 dueling 15 / 50, E6 first trading day of the month long, E7 Tuesday long, E9 SMA 10 / 50
    cross, E10 10-day stop breakout). E8 COT skipped (Antigravity's formula has no defined data; COT reversal index on
    71 markets already tested, TIER_LIST).
  Neutral exits: hold 5 or 20 trading days (Davey-style fixed-bar exits; no stop, no target).
  Costs: commission + 1 tick a fill (NQ $17.25, ES $30, YM $15, GC $34.50, CL $34.50, ZN $45.75, 6E $27); +1 round trip
    when a hold crosses a roll.
  PRIMARY test = the portfolio, as these blocks are used: each trade in R = $ P&L / 20-day ATR in $ (equal risk per
    market), pooled over the 7 markets; t-stat on calendar-month sums of R (robust to overlap and cross-market
    correlation). 16 entry-sides x 2 holds = 32 primary trials.
  Gate (per entry-side and hold): design 2018-2022 monthly t >= 2.0 AND holdout 2023-2026 mean R > 0 AND random-day placebo
    p <= 0.05 (same markets, sides and hold on random signal days, 500 runs, pooled mean R).
  Per-market results are printed too (224 cells) but are secondary: no gate on a single market.
  Expectation (in advance): trend-type blocks (E2, E10, E9) on the diversified set may show the known, weak trend premium
    (our 6-market time-series momentum: Sharpe 0.46, D); fades and patterns ~0.
Survivors get $ metrics at 1 micro per market (metrics.perf, longs / shorts, Monte Carlo) and go to Step 2 (exits).

  python3 analysis/blocks_step1b_daily_test.py [SCRATCH_DIR]     (needs g24 ge ym gc cl zn e6 .pkl)
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import blocks_daily as BD, metrics as M, montecarlo as MC
from blocks import ENTRIES

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
FILES = {"NQ": "g24", "ES": "ge", "YM": "ym", "GC": "gc", "CL": "cl", "ZN": "zn", "6E": "e6"}
MICRO = {"NQ": 0.1, "ES": 0.1, "YM": 0.1, "GC": 0.1, "CL": 0.1, "ZN": 1.0, "6E": 0.1}   # micro size (ZN: no micro)
LONG_ONLY = {"E6 first day of month", "E7 Tuesday"}
HOLDS = (5, 20)
N_LOG, N_NEW = 265, 32


def mt(x):
    """Monthly-sum t-stat of R."""
    if len(x) < 10: return np.nan
    m = x.groupby(x.date.dt.to_period("M")).R.sum(); return m.mean() / m.std(ddof=1) * np.sqrt(len(m))


if __name__ == "__main__":
    D = {}
    for s, f in FILES.items():
        g = pickle.load(open(SP + f + ".pkl", "rb")); D[s] = BD.Daily(g, s); del g
        print(f"{s}: {len(D[s].days)} days, cost ${D[s].cost:.2f}, rolls {len(D[s].jumps)}")
    rng = np.random.default_rng(11); res, per, keep = [], [], {}
    for hold in HOLDS:
        for name, fn in ENTRIES.items():
            T = {s: BD.run(d, fn(d), hold=hold) for s, d in D.items()}
            sides = [("long", 1)] if name in LONG_ONLY else [("long", 1), ("short", -1)]
            for sn, sv in sides:
                parts = {s: t[t.side == sv].assign(mkt=s) for s, t in T.items()}
                x = pd.concat(parts.values(), ignore_index=True).dropna(subset=["R"])
                for s, t in parts.items():
                    if len(t): per.append(dict(hold=hold, entry=name, side=sn, mkt=s, n=len(t), avg=t.pnl.mean(),
                                               t=t.pnl.mean() / t.pnl.std(ddof=1) * np.sqrt(len(t)) if len(t) > 2 else np.nan))
                des, hol = x[x.date < "2023"], x[x.date >= "2023"]; real = x.R.mean(); hits = 0
                for _ in range(500):
                    pr = np.concatenate([BD.placebo_R(D[s], t, hold, rng) for s, t in parts.items() if len(t)])
                    hits += np.nanmean(pr) >= real
                yr = x.groupby(x.date.dt.year).R.sum()
                res.append(dict(hold=hold, entry=name, side=sn, n=len(x), R=real, t_m=mt(x), win=(x.pnl > 0).mean(),
                                yrs=f"{(yr > 0).sum()}/{len(yr)}", des_R=des.R.mean(), des_t=mt(des), hol_R=hol.R.mean(),
                                hol_t=mt(hol), p=(hits + 1) / 501, mk_pos=sum(parts[s].R.mean() > 0 for s in parts if len(parts[s]))))
                keep[(hold, name, sn)] = x
    df = pd.DataFrame(res); df["gate"] = (df.des_t >= 2.0) & (df.hol_R > 0) & (df.p <= 0.05)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
    print("\nPRIMARY: pooled over 7 markets, R per trade (P&L / 20-day ATR $), t on monthly sums")
    print(df.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    thr = M.t_threshold(N_LOG + N_NEW)
    print(f"\nPrimary trials {N_NEW}; gate passes {int(df.gate.sum())}; monthly t >= bar {thr:.2f} (N = {N_LOG + N_NEW}): {int((df.t_m >= thr).sum())}")
    pm = pd.DataFrame(per)
    print("\nSECONDARY: per market, $ per contract after costs (t per trade)")
    print(pm.pivot_table(index=["hold", "entry", "side"], columns="mkt", values="t").round(1).to_string())
    for _, row in df[df.gate].iterrows():
        x = keep[(row.hold, row.entry, row.side)].copy(); x["usd"] = x.pnl * x.mkt.map(MICRO)
        idx = pd.bdate_range("2018-01-01", "2026-10-09"); daily = pd.Series(0.0, index=idx)
        g_ = x.groupby("date").usd.sum(); daily.loc[daily.index.intersection(g_.index)] = g_.reindex(daily.index.intersection(g_.index)).values
        print(f"\n== {row.entry} {row.side}, hold {row.hold} (1 micro per market, P&L booked on the signal day) ==")
        print(M.table({"all": (daily, x.usd)}))
        print("   by market:", x.groupby("mkt").usd.agg(["count", "mean"]).round(0).to_dict("index"))
        print(f"   DSR at N={N_LOG + N_NEW}: {M.deflated_sharpe(x.usd, N_LOG + N_NEW):.2f}")
        print(MC.report(x.usd.to_numpy(), daily.to_numpy(), size=1.0, label=row.entry))
