"""BTC ADX ensemble, LONGS ONLY, spot signals -> MBT, with a RESTING STOP on the futures (user 2026-11-13 'yes, test it').
Signals and spot-side exits (half-off, target, EMA / time exit) as in analysis/btc_adx_spot_signal_mbt_test.py. New: each book
also rests a sell stop on MBT at futures entry x (1 - R), R = the spot book's 2.5-ATR stop in %. Walked on futures 15m candles:
first candle whose low <= stop fills at min(stop, that candle's open) (a gap through the stop or a reopen gap fills at the open),
minus 1 tick; after a half-off only the remaining half is stopped. Spot's own stop / guard exit is kept too (whichever is first).
Sizing: 1% of the account per R per book, whole MBT contracts (at least 1; a book is skipped when 1 MBT risks > 2%),
on a $25,000 and a $50,000 account, not compounded (fixed $ risk). Costs $2.50 round trip + 1 tick a fill per MBT.
Personal account only (multi-day holds).
  tools/run_stamped.sh analysis/btc_adx_mbt_longs_stop_test.py > analysis/outputs/btc_adx_mbt_longs_stop_test_output.txt
  tools/run_stamped.sh analysis/btc_adx_mbt_longs_stop_test.py book50 > analysis/outputs/btc_adx_mbt_longs_stop_book50_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import btc_adx_ensemble_test as P
print(__doc__.split("\n")[0])
MULT, TICK, COMM = 0.1, 5.0, 2.5
src = open("analysis/btc_adx_futures_test.py", encoding="utf-8").read().split("\nm = load_fut()")[0].split("import btc_adx_ensemble_test as P")[1].split("\n", 2)[2]
ns = {"np": np, "pd": pd, "glob": __import__("glob")}; exec(src, ns)
f = ns["load_fut"](); f15 = P.rs(f, "15min"); fac = f.f.resample("15min", label="left", closed="left").last().reindex(f15.index).to_numpy()
FT = f15.index.to_numpy(); FO, FL, FC = (f15[k].to_numpy() for k in ("open", "low", "close"))
BOOKS = (50,) if "book50" in sys.argv else (40, 50)          # book50: a standalone single book ADX > 50, longs only (user 11/13)
S = P.run(P.setup(), books=BOOKS, longs_only="book50" in sys.argv); S = S[(S.t >= FT[0]) & (S.tx <= FT[-1]) & (S.side == 1)].reset_index(drop=True)
print(f"books {BOOKS}, longs-only signal engine: {'book50' in sys.argv}")
print(f"spot LONG book trades in the futures window: {len(S)}, spot mean {S.r.mean():+.3f}R")


def trades(S, resting=True):
    rows = []
    for k in S.itertuples():
        ie = np.searchsorted(FT, np.datetime64(k.t)); ix = np.searchsorted(FT, np.datetime64(k.tx))
        if ix >= len(FT) or ie >= ix: continue
        pe = FC[ie] + TICK; real = pe / fac[ie]; stop = pe * (1 - k.R)
        ih = min(max(np.searchsorted(FT, np.datetime64(k.th)), ie), ix) if pd.notna(k.th) else None
        exit_px, why, half_px = FC[ix] - TICK, "spot", (FC[ih] if ih is not None else None)
        if resting:
            seg = np.flatnonzero(FL[ie + 1:ix + 1] <= stop)
            if len(seg):
                j = ie + 1 + seg[0]; px = min(stop, FO[j]) - TICK
                if ih is None or j <= ih: half_px = None; ih = None
                exit_px, why = px, "stop"
        ret = (exit_px - pe) / pe if half_px is None else 0.5 * (half_px - pe) / pe + 0.5 * (exit_px - pe) / pe
        fills = 2.5 if half_px is not None else 2
        usd = ret * real * MULT - COMM - (fills - 2) * COMM / 2          # per MBT; ticks already in the prices
        rows.append((FT[ie], FT[ix], k.book, usd, k.R * real * MULT, why))
    d = pd.DataFrame(rows, columns=["t", "tx", "book", "usd", "risk", "why"])
    d["r"] = d.usd / d.risk; d["yr"] = pd.DatetimeIndex(d.t).year; d["day"] = pd.DatetimeIndex(d.tx).normalize()
    return d


def show(d, nm):
    tt = lambda g: g.r.mean() / g.r.std(ddof=1) * np.sqrt(len(g))
    x = d.usd; pf = x[x > 0].sum() / -x[x < 0].sum()
    print(f"\n{nm}\n  per MBT: {len(d)} book trades, win {np.mean(x > 0):.1%}, ${x.mean():.1f} a trade, PF {pf:.2f}, R {d.r.mean():+.3f} (t {tt(d):.2f}); "
          f"2019-22 {d.r[d.yr <= 2022].mean():+.3f}R (t {tt(d[d.yr <= 2022]):.2f}), 2023+ {d.r[d.yr >= 2023].mean():+.3f}R (t {tt(d[d.yr >= 2023]):.2f})")
    print(f"  worst trade {d.r.min():.2f}R, losses past -1.2R: {np.sum(d.r < -1.2)}; exits {d.why.value_counts().to_dict()}")
    for b in BOOKS: g = d[d.book == b]; print(f"  book ADX>{b}: n {len(g)} R {g.r.mean():+.3f} t {tt(g):.2f} | 2023+ t {tt(g[g.yr >= 2023]):.2f}")
    for acct in (25000, 50000):
        n = np.floor(0.01 * acct / d.risk).clip(lower=1); ok = n * d.risk <= 0.02 * acct; g = d[ok].assign(pnl=(n * d.usd)[ok])
        dd = g.groupby("day").pnl.sum(); eq = dd.cumsum(); mdd = (eq - eq.cummax()).min(); yrs = (d.t.max() - d.t.min()).days / 365.25
        under = (eq < eq.cummax()); runs = (under != under.shift()).cumsum()[under]; longest = (dd.index.to_series()[under].groupby(runs).agg(lambda s: (s.max() - s.min()).days).max())
        print(f"  ${acct:,} at 1% per R: {len(g)} trades ({(~ok).sum()} skipped, 1 MBT > 2%), MBT per book median {n[ok].median():.0f}, ${g.pnl.sum() / yrs:,.0f} a year "
              f"({g.pnl.sum() / yrs / acct:.1%}), max DD ${mdd:,.0f} ({mdd / acct:.1%}), longest under water {longest} days | "
              + " ".join(f"{y} {v:+,.0f}" for y, v in g.groupby("yr").pnl.sum().items()))


show(trades(S, resting=False), "LONGS, no resting stop (exits follow spot only)")
D = trades(S); show(D, "LONGS, resting stop on MBT at the spot stop distance")
D.assign(date=pd.DatetimeIndex(D.tx).normalize().date, net=D.usd).to_csv("scratch_data/btc_adx_mbt_longs_stop_trades.csv", index=False)
