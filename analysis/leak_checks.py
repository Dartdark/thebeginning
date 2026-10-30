"""Leak checks for any trade list with entry / exit times and prices (added 2026-10-30, user; idea from the HMM 'leak test' in
an X article and the ICT AMD stop-fill bug the same week).

Three checks, all mechanical:
  L1 fill sanity   every entry and exit price must have traded inside its chart bar (the 1-minute bars labelled in
                   (t - bar, t], our CSV clock = bar END time, CT), within TOL ticks (feeds differ slightly). Catches fills
                   at prices that never traded (the AMD bug: a stop 'filled' above a long entry while price was below it),
                   wrong time zones and wrong bar sizes. The clock offset that fits best (0 / -1 h / +1 h) is reported.
                   Pass: >= 98% of the checked fills inside the bar.
  L2 one-bar delay every entry moved one chart bar later (the open of the 1-minute bar after the fill bar ends), same exit;
                   trades that exit within that bar are dropped. A real edge BENDS (keeps >= half its per-trade Sharpe,
                   DEVELOPMENT_PROCESS 'implementation stresses'); a collapse or sign flip is a look-ahead flag (MNQ London
                   Signal B: t 4.3 -> -2.8 with a 15-minute delay). Fast-decay events (open prints) can fail honestly:
                   the verdict is BEND / BREAK, read with the mechanism. It catches look-ahead into the entry bar (the
                   usual bug: decide on a bar's close, fill at its open); hindsight over the whole holding period is NOT
                   caught by a one-bar delay (self-test) and stays the checker's job (reading the code, L3).
  L3 look-ahead    candidates with fitted parts (thresholds, percentiles, models) also supply trades_fullsample.csv (the
                   same rule fitted on all data); if the full-sample version earns > 1.3x the past-only version per trade,
                   the past-only backtest may still leak, or the fit is unstable (HMM filtered vs smoothed). Run inside
                   checker.py.

Use:
  python3 analysis/leak_checks.py --mc "<MultiCharts report.xlsx>" --symbol NQ --bar 5    one MultiCharts report
  python3 analysis/leak_checks.py --sweep                                                   every plan strategy
  python3 analysis/leak_checks.py --selftest                                                planted leaks must be caught
  checker.py runs L1 / L2 when checks/candidates/<name>/fills.csv exists (columns: entry_time, exit_time, side, entry,
  exit; meta.json adds "symbol" and "bar_minutes") and L3 when trades_fullsample.csv exists.
"""
import sys, glob, argparse, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

TICK = {"NQ": 0.25, "ES": 0.25, "CL": 0.01, "GC": 0.10, "YM": 1.0}
PV = {"NQ": 20, "ES": 50, "CL": 1000, "GC": 100, "YM": 5}
TOL = 2                      # ticks
_BARS = {}


def bars(sym):
    """1-minute bars indexed by bar END time (CT), RTH + night files merged."""
    if sym not in _BARS:
        fs = sorted(glob.glob(f"data/{sym}_1min_20*.csv") + glob.glob(f"data/{sym}_1min_ON_20*.csv"))
        d = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates(["date", "time"])
        d.index = pd.to_datetime(d.date.astype(str)) + pd.to_timedelta(d.time // 100, "h") + pd.to_timedelta(d.time % 100, "m")
        _BARS[sym] = d.sort_index()[["open", "high", "low", "close"]]
    return _BARS[sym]


def _window(b, t, bar):
    i0, i1 = b.index.searchsorted(t - pd.Timedelta(minutes=bar), "right"), b.index.searchsorted(t, "right")
    return b.iloc[i0:i1]


def fill_sanity(F, sym, bar, offsets=(0, -60, 60)):
    b = bars(sym); tol = TOL * TICK[sym]; best = None
    for off in offsets:
        res = []
        for _, r in F.iterrows():
            for col, tcol in (("entry", "entry_time"), ("exit", "exit_time")):
                w = _window(b, r[tcol] + pd.Timedelta(minutes=off), bar)
                if len(w) == 0: continue
                res.append(dict(time=r[tcol], kind=col, price=r[col], lo=w.low.min(), hi=w.high.max(),
                                ok=(w.low.min() - tol <= r[col] <= w.high.max() + tol)))
        R = pd.DataFrame(res)
        if len(R) and (best is None or R.ok.mean() > best[1].ok.mean()): best = (off, R)
    return best


def delay(F, sym, bar, off=0):
    b = bars(sym); out = []
    for _, r in F.iterrows():
        t = r.entry_time + pd.Timedelta(minutes=off)
        i = b.index.searchsorted(t, "right")                      # first 1-min bar that starts at / after the fill bar's end
        if i >= len(b) or b.index[i] >= r.exit_time + pd.Timedelta(minutes=off) or (b.index[i] - t) > pd.Timedelta(hours=2):
            continue
        out.append(dict(time=r.entry_time, side=r.side, orig=(r.exit - r.entry) * r.side, delayed=(r.exit - b.open.iloc[i]) * r.side))
    return pd.DataFrame(out)


def sharpe(x): return x.mean() / x.std() if len(x) > 2 and x.std() > 0 else np.nan


def tstat(x): return sharpe(x) * np.sqrt(len(x)) if len(x) > 2 else np.nan


def report(name, F, sym, bar, cost=None):
    F = F[F.entry_time >= "2018-01-01"].copy()
    # a position still open at report end is listed with exit 00:00 (before its entry): drop only those sentinels; trades
    # opening and closing in the same bar stay in L1 (Codex 2026-10-30: they were excluded, so G10 could pass impossible fills)
    F = F[F.exit_time >= F.entry_time]
    pv = PV[sym]; cost = cost if cost is not None else {"NQ": 17.25, "ES": 30.0, "CL": 27.25, "GC": 27.25}.get(sym, 0)
    fs_ = fill_sanity(F, sym, bar)
    if fs_ is None: return f"### {name}: no bar data covers its fills", dict(name=name, l1=np.nan, off=0, n=0, orig=np.nan, delayed=np.nan, t0=np.nan, t1=np.nan, keep=np.nan, l1_ok=False, l2_ok=False)
    off, R = fs_
    bad = R[~R.ok]; l1 = R.ok.mean() >= 0.98
    D = delay(F[F.exit_time > F.entry_time], sym, bar, off)   # L2 (one-bar delay) needs a trade that outlives its entry bar
    o, dl = D.orig * pv - cost, D.delayed * pv - cost
    keep = sharpe(dl) / sharpe(o) if sharpe(o) and sharpe(o) > 0 else np.nan
    l2 = bool(keep >= 0.5) if not np.isnan(keep) else False
    lines = [f"### {name} ({sym}, {bar}-min chart, {len(F)} trades 2018+)",
             f"- L1 fill sanity: {R.ok.mean():.1%} of {len(R)} fills inside their bar (+/- {TOL} ticks), clock offset {off:+d} min -> "
             f"**{'PASS' if l1 else 'FAIL'}**" + (f"; worst: " + "; ".join(f"{x.time:%Y-%m-%d %H:%M} {x.kind} {x.price} vs bar {x.lo}-{x.hi}"
                                                                  for x in bad.assign(gap=np.maximum(bad.lo - bad.price, bad.price - bad.hi)).nlargest(3, 'gap').itertuples()) if len(bad) else ""),
             f"- L2 one-bar delay: {len(D)} trades; net ${o.mean():.0f} (t {tstat(o):.1f}) -> ${dl.mean():.0f} (t {tstat(dl):.1f}); "
             f"Sharpe kept {keep:.0%} -> **{'BEND' if l2 else 'BREAK'}**"]
    return "\n".join(lines), dict(name=name, l1=R.ok.mean(), off=off, n=len(D), orig=o.mean(), delayed=dl.mean(), t0=tstat(o), t1=tstat(dl), keep=keep, l1_ok=l1, l2_ok=l2)


def from_mc(path):
    from live_vs_backtest import read_trades
    T = read_trades(path); T = T.rename(columns={})
    return T[["entry_time", "exit_time", "side", "entry", "exit"]]


PLAN = [  # (name, report, symbol, bar minutes)
    ("Vault Break (SP)", "30 Minutes NQ Vault Break SP.xlsx", "NQ", 30),
    ("Swing Target v3", "1 Minute Swing Target v3.xlsx", "NQ", 1),
    ("Overnight Bias ML v2 (funded)", "15 Minutes Overnight Bias ML (funded) v2.xlsx", "NQ", 15),
    ("Overnight Bias v2 (combine, ADX30)", "15 Minutes NQ Overnight Bias v2.xlsx", "NQ", 15),
    ("Overnight Tick / VIX", "5 Minutes Overnight Tick VIX.xlsx", "NQ", 5),
    ("Expiration Open Short", "Report EOS v1.xlsx", "NQ", 5),
    ("Late-Day Flow", "5 Minutes Late Day Flow.xlsx", "NQ", 5),
    ("NFP Fade", "5 Minutes NFP Fade.xlsx", "NQ", 5),
    ("Bridge Monday Long", "5 Minutes Bridge Monday Longs.xlsx", "NQ", 5),
    ("Monday Long", "5 Minutes NQ Monday Longs.xlsx", "NQ", 5),
    ("T_ONESIDE v2", "1 Minute T_ONESIDE v2.xlsx", "NQ", 1),
    ("Relative Strength", "1 Minute Relative Strength.xlsx", "NQ", 1),
    ("Dual Thrust v4", "1 Minute Dual Thrust v4.xlsx", "NQ", 1),
    ("ES MOC follow", "5 Minutes ES MOC Follow.xlsx", "ES", 5),
    ("CL Sunday gap fade", "5 Minutes CL Sunday Gap.xlsx", "CL", 5),
]


def sweep():
    out, rows = ["# Leak-check sweep of the plan strategies (MultiCharts trade lists)\n",
                 "`python3 analysis/leak_checks.py --sweep`; L1 fill sanity / L2 one-bar delay as defined in `analysis/leak_checks.py`. "
                 "Costs: repo standard per round trip; delay keeps the same exit.\n"], []
    for name, pat, sym, bar in PLAN:
        fs = [f for f in glob.glob("mc_reports/*.xlsx") if f.endswith(pat)]
        if not fs: out.append(f"### {name}: report not found ({pat})\n"); continue
        txt, row = report(name, from_mc(fs[0]), sym, bar); out.append(txt + "\n"); rows.append(row); print(txt, flush=True)
    S = pd.DataFrame(rows)
    out.append("## Summary\n\n| Strategy | L1 fills in bar | clock | L2 net -> delayed | t -> t | Sharpe kept | Verdict |\n|---|---|---|---|---|---|---|")
    for r in S.itertuples():
        out.append(f"| {r.name} | {r.l1:.1%} | {r.off:+d} min | ${r.orig:.0f} -> ${r.delayed:.0f} | {r.t0:.1f} -> {r.t1:.1f} | {r.keep:.0%} | "
                   f"{'PASS' if r.l1_ok else 'FILL FLAG'} / {'BEND' if r.l2_ok else 'BREAK'} |")
    open("analysis/outputs/leak_sweep.md", "w").write("\n".join(out) + "\n")
    return S


def selftest():
    """Positive controls: the checks must catch planted leaks."""
    F = from_mc(glob.glob("mc_reports/*5 Minutes Late Day Flow.xlsx")[0]); F = F[F.entry_time >= "2018-01-01"]
    bad = F.copy(); bad.loc[bad.index[::10], "entry"] += 20 * bad.side[bad.index[::10]].values * -1   # 10% of fills 20 pts better
    off, R = fill_sanity(bad, "NQ", 5); print(f"planted bad fills: {R.ok.mean():.1%} inside -> {'caught' if R.ok.mean() < 0.98 else 'MISSED'}")
    b = bars("NQ"); cheat = F.copy()            # the common leak: side decided with the fill bar's own close, filled at its open
    for i, r in cheat.iterrows():
        w = _window(b, r.entry_time, 5)
        if len(w): cheat.loc[i, "side"] = 1 if w.close.iloc[-1] > r.entry else -1
    D = delay(cheat, "NQ", 5); o, dl = D.orig * 20 - 17.25, D.delayed * 20 - 17.25
    print(f"look-ahead side: net ${o.mean():.0f} (t {tstat(o):.1f}) -> delayed ${dl.mean():.0f} (t {tstat(dl):.1f}), kept "
          f"{sharpe(dl) / sharpe(o):.0%} -> {'caught' if sharpe(dl) / sharpe(o) < 0.5 else 'MISSED'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mc"); ap.add_argument("--symbol", default="NQ"); ap.add_argument("--bar", type=int, default=5)
    ap.add_argument("--sweep", action="store_true"); ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    if a.selftest: selftest()
    elif a.sweep: sweep()
    else: print(report(a.mc, from_mc(a.mc), a.symbol, a.bar)[0])
