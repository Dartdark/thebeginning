"""HMA / SMA crossover + RSI + LinReg on BTC 4H (pre-registered checks/candidates/hma_btc4h/PREREG.md; user 2026-11-14, ZiadFrancis repo).
  tools/run_stamped.sh analysis/hma_btc4h_test.py > analysis/outputs/hma_btc4h_test_output.txt
"""
import sys, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
print(__doc__.split("\n")[0])


def load_btc():
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/BTCUSD_spot_1min_*.csv"))])
    ts = pd.to_datetime(d.date.astype(str) + d.time.astype(str).str.zfill(4), format="%Y%m%d%H%M")
    ts = ts.dt.tz_localize("America/Chicago", ambiguous="NaT", nonexistent="NaT")
    d = d.assign(ts=ts - pd.Timedelta(minutes=1)).dropna(subset=["ts"]); d["ts"] = d.ts.dt.tz_convert("UTC").dt.tz_localize(None)
    return d.drop_duplicates("ts").set_index("ts").sort_index()[["open", "high", "low", "close"]]


def bars4h(m, offset=None):
    return m.resample("4h", label="left", closed="left", offset=offset).agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()


def wma(x, n):
    w = np.arange(1, n + 1, dtype=float); return pd.Series(x).rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True).values


def hma(c, n):
    raw = 2 * wma(c, int(np.floor(n / 2))) - wma(c, n); return wma(raw, int(np.floor(np.sqrt(n))))


def rsi(c, n=14):
    d = np.diff(c, prepend=np.nan); up = pd.Series(np.where(d > 0, d, 0.0)).ewm(alpha=1 / n, adjust=False).mean()
    dn = pd.Series(np.where(d < 0, -d, 0.0)).ewm(alpha=1 / n, adjust=False).mean(); return (100 - 100 / (1 + up / dn)).values


def linreg(c, n=50):
    x = np.arange(n, dtype=float); xm = x.mean(); sxx = ((x - xm) ** 2).sum()
    def f(a): b = ((x - xm) * (a - a.mean())).sum() / sxx; return a.mean() + b * (x[-1] - xm)
    return pd.Series(c).rolling(n).apply(f, raw=True).values


def signals(b, kind="hma", use_rsi=True, use_lr=True):
    c = b.close.values
    f, s = (hma(c, 16), hma(c, 65)) if kind == "hma" else (pd.Series(c).rolling(16).mean().values, pd.Series(c).rolling(65).mean().values)
    up = (np.r_[np.nan, f[:-1]] <= np.r_[np.nan, s[:-1]]) & (f > s); dn = (np.r_[np.nan, f[:-1]] >= np.r_[np.nan, s[:-1]]) & (f < s)
    ent = up.copy()
    if use_rsi: ent &= rsi(c) > 52
    if use_lr: ent &= c > linreg(c)
    return ent, dn


def trades(b, ent, ext, cost_side):
    c = b.close.values; idx = b.index; out = []; i0 = None
    for i in range(len(c)):
        if i0 is not None and ext[i]:
            out.append((idx[i0], idx[i], c[i0], c[i], c[i] / c[i0] * (1 - cost_side) / (1 + cost_side) - 1, i - i0)); i0 = None
        if i0 is None and ent[i] and not ext[i]: i0 = i
    return pd.DataFrame(out, columns=["entry_t", "exit_t", "entry", "exit", "ret", "bars"])


def equity(b, T):
    """daily-marked equity of a fully-invested long when in a trade (compounded), cash otherwise."""
    c = b.close; r = pd.Series(0.0, index=b.index); pr = c.pct_change().fillna(0.0)
    for t in T.itertuples():
        m = (b.index > t.entry_t) & (b.index <= t.exit_t); r[m] = pr[m]
    adj = pd.Series(0.0, index=b.index)
    for t in T.itertuples():                       # costs at entry / exit bars, so the equity ends at the trade-level return
        k = (1 + t.ret) / (t.exit / t.entry); adj[t.exit_t] += np.log(k)
    eq = np.exp(np.log1p(r).cumsum() + adj.cumsum()); return eq


def stats(b, T, nm, start, end):
    T = T[(T.entry_t >= start) & (T.entry_t < end)]; bb = b[(b.index >= start) & (b.index < end)]
    if len(T) < 3: return f"   {nm}: n {len(T)}"
    eq = equity(bb, T); yrs = (bb.index[-1] - bb.index[0]).days / 365.25; d = eq.resample("1D").last().pct_change().dropna()
    dd = (eq / eq.cummax() - 1).min(); tot = eq.iloc[-1] - 1; bh = bb.close.iloc[-1] / bb.close.iloc[0] - 1
    sh = d.mean() / d.std() * np.sqrt(365); bhd = bb.close.resample("1D").last().pct_change().dropna(); shb = bhd.mean() / bhd.std() * np.sqrt(365)
    expo = T.bars.sum() / len(bb)
    return (f"   {nm:<38} n {len(T):3d} win {np.mean(T.ret > 0):.0%} avg {T.ret.mean() * 100:+5.2f}% | total {tot * 100:+8.0f}% CAGR {((1 + tot) ** (1 / yrs) - 1) * 100:+5.1f}% "
            f"maxDD {dd * 100:5.1f}% Sharpe {sh:4.2f} expo {expo:.0%} | buy&hold {bh * 100:+7.0f}% Sharpe {shb:4.2f}")


m = load_btc(); B = bars4h(m); print(f"BTC 4H bars {B.index[0]} .. {B.index[-1]} ({len(B)})")
S, E = "2019-02-20", "2026-12-31"
for kind in ("sma", "hma"):
    ent, ext = signals(B, kind)
    for cs, cl in ((0.0002, "2 bp (his)"), (0.0006, "6 bp (ours)")):
        T = trades(B, ent, ext, cs)
        print(f"\n== {kind.upper()} 16/65 + RSI > 52 + LinReg(50), costs {cl}")
        for nm, a, z in (("whole 2019-02 -> 2026-10", S, E), ("2019-22", S, "2023-01-01"), ("2023+", "2023-01-01", E)): print(stats(B, T, nm, a, z))
    T = trades(B, ent, ext, 0.0006); T = T[T.entry_t >= S].reset_index(drop=True)
    # random-timing placebo: same holding lengths, random non-overlapping starts
    rng = np.random.default_rng(1); BB = B[B.index >= S]; c = BB.close.values; n = len(c); L = T.bars.values; real = np.log1p(T.ret).sum(); sims = []
    for _ in range(500):
        starts = np.sort(rng.choice(n - L.max() - 1, len(L), replace=False)); tot = 0.0; last = -1
        for s0, l in zip(starts, rng.permutation(L)):
            s0 = max(s0, last + 1)
            if s0 + l >= n: continue
            tot += np.log(c[s0 + l] / c[s0] * (1 - 0.0006) / (1 + 0.0006)); last = s0 + l
        sims.append(tot)
    sims = np.array(sims)
    print(f"   random-timing placebo (same {len(L)} holding lengths, random starts, 500 runs): median total {np.expm1(np.median(sims)) * 100:+.0f}%, "
          f"p95 {np.expm1(np.percentile(sims, 95)) * 100:+.0f}% vs real {np.expm1(real) * 100:+.0f}% -> p {np.mean(sims >= real):.3f}")
    print("   ingredients (6 bp): " + " | ".join(f"{nm}: {stats(B, trades(B, *signals(B, kind, **kw), 0.0006), '', S, E).split('|')[1].strip()}"
                                          for nm, kw in (("no RSI", dict(use_rsi=False)), ("no LinReg", dict(use_lr=False)), ("cross only", dict(use_rsi=False, use_lr=False)))))
    if kind == "sma":
        ext_ = pd.read_csv("/home/user/ziadfrancis/coinquant_vs_python_hma_strategy/backtest-trades-sma.csv"); buys = ext_[ext_.side == "BUY"]
        et = pd.to_datetime(buys.ts_init).dt.tz_convert("UTC").dt.tz_localize(None) - pd.Timedelta(hours=4)       # fill at the close = next bar open
        mine = set(T.entry_t); theirs = set(et); print(f"   trade match vs his CoinQuant log (SMA): his {len(theirs)}, ours {len(mine)}, same 4H bar {len(mine & theirs)}"
                                                      f" (+-1 bar {sum(1 for t in mine if any(abs((t - u).total_seconds()) <= 14400 for u in theirs))})")

print("\n== NQ port (24h Globex, 4H bars in Central time; multi-day holds: personal only), per NQ, $7.25 + 1 tick a side")
import jump_lib as JL
nq = JL.minute().set_index("ts")[["open", "high", "low", "close"]]
NB = nq.resample("4h", label="left", closed="left").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
for kind in ("sma", "hma"):
    ent, ext = signals(NB, kind); c = NB.close.values; rows = []; i0 = None
    for i in range(len(c)):
        if i0 is not None and ext[i]: rows.append((NB.index[i0], NB.index[i], (c[i] - c[i0]) * 20 - 7.25 - 10.0)); i0 = None
        if i0 is None and ent[i] and not ext[i]: i0 = i
    NT = pd.DataFrame(rows, columns=["entry_t", "exit_t", "net"]); NT = NT[NT.entry_t >= "2018-01-01"]; y = NT.entry_t.dt.year
    tt_ = lambda x: x.mean() / x.std() * np.sqrt(len(x))
    print(f"   {kind.upper()}: n {len(NT)} avg ${NT.net.mean():,.0f} t {tt_(NT.net):.2f} win {np.mean(NT.net > 0):.0%} PF {NT.net[NT.net > 0].sum() / -NT.net[NT.net < 0].sum():.2f} | "
          f"2018-22 ${NT.net[y <= 2022].mean():,.0f} 2023+ ${NT.net[y >= 2023].mean():,.0f} | total ${NT.net.sum():,.0f} vs NQ long-only over the span "
          f"${(NB.close.iloc[-1] - NB.close[NB.index >= '2018-01-01'].iloc[0]) * 20:,.0f} (unadjusted, rolls included)")
    if kind == "sma":
        NT.assign(date=NT.exit_t.dt.normalize(), entry_date=NT.entry_t.dt.normalize())[["date", "entry_date", "net"]].to_csv("checks/candidates/hma_btc4h/trades_nq_sma.csv", index=False)
