"""BTC ADX ensemble: SPOT signals, MBT execution (user 2026-11-13 'let's test this'). The books run exactly as in
analysis/btc_adx_ensemble_test.py on Coinbase spot (24/7: entries, stops, half-offs, targets, EMA / time exits all decided on
spot candles). Every book fill is copied onto CME Bitcoin futures at the close of the same 15-minute candle, or, when CME is
closed (16:00-17:00 CT, weekends, holidays), at the close of the first futures candle after it. A book whose entry and exit both
fall in one closure is never traded. No resting stop on the futures: the exit is whatever futures trade when spot says out.
Per MBT (0.1 BTC), 1 MBT per book, $2.50 round trip + 1 tick (5 points) on every fill = 17.5 points a fill; rolls removed by ratio.
R = the spot book's stop distance (2.5 ATR) in % x the futures entry price.
Not modelled: Apex rules (it holds overnight and over weekends: personal account only), margin, a resting disaster stop.
  tools/run_stamped.sh analysis/btc_adx_spot_signal_mbt_test.py > analysis/outputs/btc_adx_spot_signal_mbt_test_output.txt
"""
import sys, io, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import btc_adx_ensemble_test as P
print(__doc__.split("\n")[0])
MULT, CPTS = 0.1, 17.5
src = open("analysis/btc_adx_futures_test.py", encoding="utf-8").read().split("\nm = load_fut()")[0].split("import btc_adx_ensemble_test as P")[1].split("\n", 2)[2]
ns = {"np": np, "pd": pd, "glob": __import__("glob")}; exec(src, ns)
f = ns["load_fut"](); f15 = P.rs(f, "15min"); fac = f.f.resample("15min", label="left", closed="left").last().reindex(f15.index).to_numpy()
FT = f15.index.to_numpy(); FC = f15.close.to_numpy()
S = P.run(P.setup())
S = S[(S.t >= FT[0]) & (S.tx <= FT[-1])].reset_index(drop=True)
print(f"spot book trades in the futures window ({pd.Timestamp(FT[0]).date()} -> {pd.Timestamp(FT[-1]).date()}): {len(S)}, spot mean {S.r.mean():+.3f}R")


def mirror(S, delay=0, gates=None):
    rows = []
    for k in S.itertuples():
        ie = np.searchsorted(FT, np.datetime64(k.t)) + delay; ix = np.searchsorted(FT, np.datetime64(k.tx)) + delay
        if ix >= len(FT) or ie >= ix: continue                                       # opened and closed inside one CME closure
        pe, px_ = FC[ie], FC[ix]; fills = 2; ret = k.side * (px_ - pe) / pe
        if pd.notna(k.th):
            ih = min(max(np.searchsorted(FT, np.datetime64(k.th)) + delay, ie), ix)
            ret = 0.5 * k.side * (FC[ih] - pe) / pe + 0.5 * ret; fills = 2.5
        real = pe / fac[ie]; usd = ret * real * MULT - fills * CPTS * MULT
        rows.append((k.t, FT[ie], FT[ix], k.side, k.book, usd, k.R * real * MULT, k.r, (FT[ie] - np.datetime64(k.t)) / np.timedelta64(1, "h"),
                     (FT[ix] - np.datetime64(k.tx)) / np.timedelta64(1, "h")))
    d = pd.DataFrame(rows, columns=["t_spot", "t", "tx", "side", "book", "usd", "stop_usd", "r_spot", "late_in", "late_out"])
    d["r"] = d.usd / d.stop_usd; d["yr"] = pd.DatetimeIndex(d.t).year; d["day"] = pd.DatetimeIndex(d.tx).normalize()
    return d


def report(d, nm):
    x = d.usd; pf = x[x > 0].sum() / -x[x < 0].sum(); t = x.mean() / x.std(ddof=1) * np.sqrt(len(x))
    dd = d.groupby("day").usd.sum(); td = dd.mean() / dd.std(ddof=1) * np.sqrt(len(dd)); eq = dd.cumsum(); mdd = (eq - eq.cummax()).min()
    yrs = (d.t.max() - d.t.min()).days / 365.25; a = d[d.yr <= 2022]; z = d[d.yr >= 2023]
    tt = lambda g: g.r.mean() / g.r.std(ddof=1) * np.sqrt(len(g))
    print(f"\n{nm}\n  {len(d)} book trades, win {np.mean(x > 0):.1%}, ${x.mean():.1f} per MBT a trade, PF {pf:.2f}, t {t:.2f} (daily t {td:.2f}), ${x.sum() / yrs:,.0f} a year, "
          f"max DD ${mdd:,.0f}, worst trade ${x.min():,.0f} ({d.r.min():.1f}R), worst day ${dd.min():,.0f}; stop $ per MBT median {d.stop_usd.median():.0f} (2025+ {d.stop_usd[d.yr >= 2025].median():.0f})")
    print(f"  R: mean {d.r.mean():+.3f} (t {tt(d):.2f}) vs the same trades on spot {d.r_spot.mean():+.3f} | 2019-22 {a.r.mean():+.3f} (t {tt(a):.2f}) | 2023+ {z.r.mean():+.3f} (t {tt(z):.2f})")
    for s, n in ((1, "longs"), (-1, "shorts")):
        g = d[d.side == s]; print(f"  {n}: n {len(g)} ${g.usd.mean():.1f} R {g.r.mean():+.3f} t {tt(g):.2f} | 2023+ R {g.r[g.yr >= 2023].mean():+.3f} t {tt(g[g.yr >= 2023]):.2f}")
    for b in (40, 50):
        g = d[d.book == b]; print(f"  book ADX>{b}: n {len(g)} R {g.r.mean():+.3f} t {tt(g):.2f} | 2023+ {g.r[g.yr >= 2023].mean():+.3f} t {tt(g[g.yr >= 2023]):.2f}")
    print("  by year $: " + "  ".join(f"{y} {g.usd.sum():+,.0f} ({len(g)})" for y, g in d.groupby("yr")))
    li = d.late_in > 0.01; lo = d.late_out > 0.01
    print(f"  entered late (CME closed at the signal): {li.mean():.0%} of trades, R {d.r[li].mean():+.3f} vs on time {d.r[~li].mean():+.3f}; exited late: {lo.mean():.0%}, R {d.r[lo].mean():+.3f} vs on time {d.r[~lo].mean():+.3f}")
    print(f"  losses worse than -1.5R: {np.sum(d.r < -1.5)} (worst five R: {np.sort(d.r.to_numpy())[:5].round(2).tolist()})")


M = mirror(S); report(M, "MIRROR: spot signals, every fill on MBT at the same or next available 15m close")
report(M[M.late_in < 0.01], "  only books whose entry signal came while CME was open")
report(mirror(S, delay=1), "  every fill one 15m candle late (execution lag)")
M.assign(date=pd.DatetimeIndex(M.tx).normalize().date, net=M.usd).to_csv("scratch_data/btc_adx_spot_signal_mbt_trades.csv", index=False)
