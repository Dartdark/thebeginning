"""BTC ADX ensemble FREE vs PREMIUM (user 2026-11-13: the author's site shows 'BTCAdxEnsemblePremium', no code, described as the free
strategy with SIX ADX books at 40 / 42 / 44 / 46 / 48 / 50 instead of two at 40 / 50; site's 2024 BTC-USDT 15m snapshot: free +43.2%,
54 trades, DD -15.1%, Sharpe 1.36; premium +78.5%, 51 trades, DD -9.1%, Sharpe 2.09). Everything else is assumed identical (same
description). Sizing as in the free code: each book risks RISK / CAP % of balance x CAP / n_books = 6% / n_books, so free = 3% a book,
premium = 1% a book, 6% when every book is open: premium puts more weight on high ADX (at ADX 41 1/6 of the risk vs 1/2 in free).
 A. Spot (Coinbase 1-min, port of analysis/btc_adx_ensemble_test.py, 0.07% a side): account % per year (not compounded), daily-summed
    t, max DD in account %, by year, 2024 alone (the site's window), position trades in 2024.
 B. Longs on MBT, spot signals, resting MBT stop (the personal-plan version), at EQUAL total risk: free 1 MBT a book (2 books),
    premium 1/3 MBT a book (6 books) -> both at most 2 MBT; also premium at 1 MBT a book (6 MBT max, 3x the risk).
  tools/run_stamped.sh analysis/btc_adx_premium_test.py > analysis/outputs/btc_adx_premium_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import btc_adx_ensemble_test as P
print(__doc__.split("\n")[0])
FREE, PREM = (40, 50), (40, 42, 44, 46, 48, 50)
ctx = P.setup()


def acct(d, nb, yrs_mask=None):
    w = 6.0 / nb                                                   # account % per R per book
    x = d.assign(a=d.r * w, day=pd.DatetimeIndex(d.tx).normalize())
    if yrs_mask is not None: x = x[yrs_mask(x)]
    dd = x.groupby("day").a.sum(); full = pd.date_range(dd.index.min(), dd.index.max()); dd = dd.reindex(full, fill_value=0.0)
    eq = dd.cumsum(); yrs = len(full) / 365.25
    t = dd.mean() / dd.std(ddof=1) * np.sqrt(len(dd)); sh = dd.mean() / dd.std(ddof=1) * np.sqrt(365)
    return dict(pct_yr=dd.sum() / yrs, t=t, sharpe=sh, mdd=(eq - eq.cummax()).min(), n=len(x))


def positions(d):
    """net-position trades: merge overlapping book trades into one position (the site counts these)"""
    iv = sorted(zip(d.t, d.tx)); n = 0; end = None
    for a, b in iv:
        if end is None or a > end: n += 1; end = b
        else: end = max(end, b)
    return n


res = {}
for nm, books in (("FREE 2 books 40/50", FREE), ("PREMIUM 6 books 40-50", PREM)):
    d = P.run(ctx, books=books); res[nm] = d
    print(f"\n{nm}: {len(d)} book trades, mean {d.r.mean():+.3f}R per book trade")
    for per, f in (("2018-26", None), ("2018-22", lambda x: x.yr <= 2022), ("2023+", lambda x: x.yr >= 2023), ("2024 (site window)", lambda x: x.yr == 2024)):
        s = acct(d, len(books), f)
        print(f"  {per:<20} {s['pct_yr']:+6.1f}% a year (not compounded), daily t {s['t']:5.2f}, Sharpe {s['sharpe']:4.2f}, max DD {s['mdd']:6.1f}%  ({s['n']} book trades)")
    print("  by year %: " + "  ".join(f"{y} {g.r.sum() * 6 / len(books):+.1f}" for y, g in d.groupby("yr")))
    print(f"  2024 position trades (merged books): {positions(d[d.yr == 2024])}; longs {np.mean(d[d.yr == 2024].side == 1):.0%} of book trades")
    for s_, lab in ((1, "longs"), (-1, "shorts")):
        g = d[d.side == s_]; z = g[g.yr >= 2023]
        print(f"  {lab}: {g.r.sum() * 6 / len(books) / ((d.t.max() - d.t.min()).days / 365.25):+.1f}% a year; 2023+ {z.r.sum() * 6 / len(books) / 3.8:+.1f}% a year")
a, b = res["FREE 2 books 40/50"], res["PREMIUM 6 books 40-50"]
print("\npaired, yearly account % premium - free: " + "  ".join(f"{y} {b[b.yr == y].r.sum() - a[a.yr == y].r.sum() * 3:+.1f}" for y in sorted(set(a.yr))))

# ---- B: longs on MBT, spot signals, resting stop
MULT, TICK, COMM = 0.1, 5.0, 2.5
src = open("analysis/btc_adx_futures_test.py", encoding="utf-8").read().split(chr(10) + "m = load_fut()")[0].split("import btc_adx_ensemble_test as P")[1].split(chr(10), 2)[2]
ns = {"np": np, "pd": pd, "glob": __import__("glob")}; exec(src, ns)
f = ns["load_fut"](); f15 = P.rs(f, "15min"); fac = f.f.resample("15min", label="left", closed="left").last().reindex(f15.index).to_numpy()
FT = f15.index.to_numpy(); FO, FL, FC = (f15[k].to_numpy() for k in ("open", "low", "close"))


def mbt(S):
    rows = []
    for k in S[(S.side == 1) & (S.t >= FT[0]) & (S.tx <= FT[-1])].itertuples():
        ie = np.searchsorted(FT, np.datetime64(k.t)); ix = np.searchsorted(FT, np.datetime64(k.tx))
        if ix >= len(FT) or ie >= ix: continue
        pe = FC[ie] + TICK; real = pe / fac[ie]; stop = pe * (1 - k.R)
        ih = min(max(np.searchsorted(FT, np.datetime64(k.th)), ie), ix) if pd.notna(k.th) else None
        exit_px, half_px = FC[ix] - TICK, (FC[ih] if ih is not None else None)
        seg = np.flatnonzero(FL[ie + 1:ix + 1] <= stop)
        if len(seg):
            j = ie + 1 + seg[0]; exit_px = min(stop, FO[j]) - TICK
            if ih is None or j <= ih: half_px = None
        ret = (exit_px - pe) / pe if half_px is None else 0.5 * (half_px - pe) / pe + 0.5 * (exit_px - pe) / pe
        rows.append((FT[ix], k.book, ret * real * MULT - COMM - (COMM / 4 if half_px is not None else 0)))
    d = pd.DataFrame(rows, columns=["tx", "book", "usd"]); d["day"] = pd.DatetimeIndex(d.tx).normalize(); d["yr"] = d.day.dt.year
    return d


print("\nB. LONGS on MBT (spot signals, resting stop), $ per year / max DD / daily t:")
for nm, books, w in (("FREE, 1 MBT a book (max 2 MBT)", FREE, 1.0), ("PREMIUM, 1/3 MBT a book (max 2 MBT, equal risk)", PREM, 1 / 3),
                     ("PREMIUM, 1 MBT a book (max 6 MBT)", PREM, 1.0)):
    d = mbt(res["FREE 2 books 40/50"] if books == FREE else res["PREMIUM 6 books 40-50"]); d["usd"] *= w
    for per, m in (("2019-26", d.yr >= 2019), ("2019-22", d.yr <= 2022), ("2023+", d.yr >= 2023)):
        x = d[m]; dd = x.groupby("day").usd.sum(); full = pd.date_range(dd.index.min(), dd.index.max()); dd = dd.reindex(full, fill_value=0.0); eq = dd.cumsum()
        t = dd.mean() / dd.std(ddof=1) * np.sqrt(len(dd)); yrs = len(full) / 365.25; mdd = (eq - eq.cummax()).min()
        print(f"  {nm:<48} {per:<8} ${dd.sum() / yrs:7,.0f} a year, max DD ${mdd:7,.0f}, $/yr / DD {dd.sum() / yrs / -mdd:4.2f}, daily t {t:4.2f}")
    d.assign(date=d.day.dt.date, net=d.usd).to_csv(f"scratch_data/btc_adx_mbt_longs_{'free' if books == FREE else 'prem'}_{w:.2f}.csv", index=False)
