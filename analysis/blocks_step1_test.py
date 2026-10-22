"""Building blocks, Step 1: entries alone with a neutral exit (pre-registered 2026-10-20, written before any result).

Question: does any of Antigravity's 10 entry blocks (antigravity/jesse tasks/STRATEGY_BUILDING_BLOCKS.md) have an edge of
its own on NQ or ES, before exits and filters? Library: analysis/blocks.py (RTH 15-min bars, Apex-legal, roll-adjusted).

Pre-registered plan (fixed before running):
  Entries: E1 three bars, E2 close breakout (10), E3 close fade (10), E4 low-volume fade (10 / 10), E5 dueling momentum
    (15 / 50), E6 first trading day of the month (long 8:45), E7 Tuesday (long 8:45), E9 SMA 10 / 50 cross,
    E10 stop breakout (10-bar high / low). The catalog's default lengths, no tuning.
    Skipped: E8 COT crowding (weekly positioning; already F as an Apex day trade, TIER_LIST 'COT Dealer Rank ... day trade').
    E6 as written hard-codes past dates (picks years after the fact): replaced by the first trading day of each month.
  Exits (neutral, only to read the entry): XA = hold 4 bars (1 hour), XB = hold to 15:55 CT (one trade a day).
  Markets: NQ ($17.25 a round trip) and ES ($30). 2018-01 to 2026-10. Design 2018-2022, holdout 2023-2026.
  Trials: 7 two-sided entries x 2 sides + 2 long-only = 16 entry-sides x 2 exits x 2 markets = 64.
  Gate to Step 2 (per entry-side, market, exit): design t >= 2.0 AND holdout average > 0 AND random-day placebo p <= 0.05
    (same trades, same bar of the day and side, on random days; 500 runs; full period). Also reported: full-period t vs
    metrics.t_threshold(N) at N = trials-log items + 64.
  Expectation (written in advance): 0-2 survivors; price-pattern entries have failed here before (LESSONS.md).
Survivors get the full report (metrics.perf by side, bootstrap, Monte Carlo) and go to Step 2 (exits).

  python3 analysis/blocks_step1_test.py [SCRATCH_DIR]          (needs g24.pkl / ge.pkl from analysis/build_lab.py)
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import blocks as B, metrics as M, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
N_LOG, N_NEW = 263, 64                                              # trials-log items on 2026-10-20 + this test
LONG_ONLY = {"E6 first day of month", "E7 Tuesday"}


def tstat(x): x = np.asarray(x, float); return x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan


def placebo_p(r, tr, gross, runs=500, seed=7):
    """Share of random-day runs (same bar of the day, same side) whose average is >= the real one."""
    rng = np.random.default_rng(seed); i = tr["i"].to_numpy(); s = tr["side"].to_numpy(); real = tr["pnl"].mean()
    n = len(r.days); hits = 0
    for _ in range(runs):
        d = rng.integers(0, n, len(tr)); hits += (gross[d, i] * s - r.cost).mean() >= real
    return (hits + 1) / (runs + 1)


def summarize(name, r, tr, gross):
    out = []
    sides = [("long", 1)] if name in LONG_ONLY else [("long", 1), ("short", -1)]
    for sn, sv in sides:
        x = tr[tr.side == sv]
        if len(x) < 30: out.append(dict(entry=name, side=sn, n=len(x))); continue
        yr = x.groupby(x.date.dt.year).pnl.sum(); des = x[x.date < "2023"]; hol = x[x.date >= "2023"]
        out.append(dict(entry=name, side=sn, n=len(x), avg=x.pnl.mean(), t=tstat(x.pnl), win=(x.pnl > 0).mean(),
                        yrs=f"{(yr > 0).sum()}/{len(yr)}", des_avg=des.pnl.mean(), des_t=tstat(des.pnl),
                        hol_avg=hol.pnl.mean(), hol_t=tstat(hol.pnl), p=placebo_p(r, x, gross)))
    return out


def full_report(r, tr, label):
    days = pd.Series(0.0, index=r.dates); dp = tr.groupby("date").pnl.sum(); days.loc[dp.index] = dp.values
    rows = {"both": (days, tr.pnl)}
    for sn, sv in (("long", 1), ("short", -1)):
        x = tr[tr.side == sv]
        if len(x):
            dd = pd.Series(0.0, index=r.dates); g = x.groupby("date").pnl.sum(); dd.loc[g.index] = g.values; rows[sn] = (dd, x.pnl)
    print(M.table(rows)); h = days[days.index >= "2023"]
    print(f"   2023+: Sharpe {M.perf(h)['sharpe']:.2f}, DSR at N={N_LOG + N_NEW}: {M.deflated_sharpe(tr.pnl, N_LOG + N_NEW):.2f}")
    print(MC.report(tr.pnl.to_numpy(), days.to_numpy(), size=0.1, label=label + " 1 micro"))


if __name__ == "__main__":
    res, keep = [], {}
    for sym, f in (("NQ", "g24.pkl"), ("ES", "ge.pkl")):
        g = pickle.load(open(SP + f, "rb")); r = B.RTH(g, sym); del g
        print(f"{sym}: {len(r.days)} days {r.dates[0].date()} .. {r.dates[-1].date()}, cost ${r.cost:.2f}")
        for xn, xb in (("XA 4 bars", 4), ("XB to 15:55", None)):
            gross = B.market_pnl(r, xb)
            for name, fn in B.ENTRIES.items():
                tr = B.run(r, fn(r), exit_bars=xb)
                for row in summarize(name, r, tr, gross):
                    row.update(market=sym, exit=xn); res.append(row); keep[(sym, xn, name, row["side"])] = (r, tr)
    df = pd.DataFrame(res); thr = M.t_threshold(N_LOG + N_NEW)
    df["gate"] = (df.des_t >= 2.0) & (df.hol_avg > 0) & (df.p <= 0.05)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
    cols = ["market", "exit", "entry", "side", "n", "avg", "t", "win", "yrs", "des_avg", "des_t", "hol_avg", "hol_t", "p", "gate"]
    print(df[cols].to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    print(f"\nTrials {N_NEW}; full-period bar t >= {thr:.2f} (N = {N_LOG + N_NEW}); design t >= 2.0 by chance ~{0.023 * N_NEW:.1f} of {N_NEW}")
    print(f"Gate passes: {int(df.gate.sum())}; full-period t >= bar: {int((df.t >= thr).sum())}")
    for _, row in df[df.gate].iterrows():
        r, tr = keep[(row.market, row.exit, row.entry, row.side)]
        print(f"\n== {row.market} {row.exit} {row.entry} (gate passed on {row.side}) =="); full_report(r, tr, f"{row.market} {row.entry}")
