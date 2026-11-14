"""BTC ADX PREMIUM with a ROUNDED net position on MBT (user 2026-11-13 'test the rounded premium version').
The 6 premium books (ADX 40/42/44/46/48/50, longs only, spot signals, resting MBT stop at each book's stop) run as before; each book
counts 1 unit while full and 0.5 after its half-off. Position held on MBT = ceil(units / 3) contracts: 1 MBT while 0.5-3 units are
open, 2 MBT above 3 (so at most 2 MBT, like the plan's free version). Every change in the position is traded at the price of the
event that caused it (15m close for entries / half-offs / spot exits, the stop price - 1 tick for a resting stop), $1.25 + 1 tick
($0.50) per contract per side. P&L marked every 15m bar on the roll-adjusted series in real-price dollars, booked to the CT trading
day (a bar closing after 16:00 CT counts for the next session). Same personal base as analysis/btc_adx_personal_bench.py.
Compared with: the plan (FREE 2 books, 1 MBT a book) and PREMIUM 1/3 MBT a book (the untradeable equal-risk reference).
  tools/run_stamped.sh analysis/btc_adx_premium_rounded_bench.py > analysis/outputs/btc_adx_premium_rounded_bench_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
src = open("analysis/btc_adx_personal_bench.py", encoding="utf-8").read()
head = src.split("S = PB.run(PB.setup())")[0]
loop = src.split("seg_d, seg_v, tr_usd, peak = [], [], [], []\n")[1].split("ref = pd.read_csv")[0]
g = {"__name__": "bench", "__doc__": __doc__}
exec(compile(head.replace("print(__doc__.split", "pass  # (__doc__.split"), "personal_bench_head", "exec"), g)
print(__doc__.split("\n")[0])
exec(compile("def mark(S):\n    global seg_d, seg_v, tr_usd, peak\n    seg_d, seg_v, tr_usd, peak = [], [], [], []\n"
             + "\n".join("    " + l for l in loop.split("\n")) + "\n    return btc, tr_usd\n", "mark", "exec"), g)
np, pd, PB, MC, days, P, FT, FO, FL, FC, fac, cte, ns = (g[k] for k in ("np", "pd", "PB", "MC", "days", "P", "FT", "FO", "FL", "FC", "fac", "cte", "ns"))
TICK, MULT, COMM_SIDE = 5.0, 0.1, 1.25
ctx = PB.setup()


def books_on_mbt(S):
    """per book: list of (bar, unit change, price) events on MBT, using the same stop / half rules as the marked series"""
    ev = []
    for k in S.itertuples():
        ie = np.searchsorted(FT, np.datetime64(k.t)); ix = np.searchsorted(FT, np.datetime64(k.tx))
        if ix >= len(FT) or ie >= ix: continue
        stop = FC[ie] * (1 - k.R)
        ih = min(max(np.searchsorted(FT, np.datetime64(k.th)), ie), ix) if pd.notna(k.th) else None
        end, px_end = ix, FC[ix]
        seg = np.flatnonzero(FL[ie + 1:ix + 1] <= stop)
        if len(seg):
            j = ie + 1 + seg[0]; end, px_end = j, min(stop, FO[j])
            if ih is not None and j <= ih: ih = None
        if ih is not None and ih <= ie:                      # half-off on the entry candle (as the marked series): open at 0.5
            ev.append((ie, 0, +0.5, FC[ie])); ev.append((end, 2, -0.5, px_end))
        elif ih is not None and ih >= end:                   # half-off on the exit candle: half at that close, half at the exit price
            ev.append((ie, 0, +1.0, FC[ie])); ev.append((end, 3, -0.5, FC[end])); ev.append((end, 2, -0.5, px_end))
        else:
            ev.append((ie, 0, +1.0, FC[ie]))
            if ih is not None: ev.append((ih, 1, -0.5, FC[ih])); ev.append((end, 2, -0.5, px_end))
            else: ev.append((end, 2, -1.0, px_end))
    return sorted(ev, key=lambda e: (e[0], e[1] == 0, -e[1]))   # inside a bar: exits (half at the close first), entries last


def rounded(S, size=lambda u: int(np.ceil(u / 3 - 1e-9))):
    ev = books_on_mbt(S); pnl = np.zeros(len(FT)); u = 0.0; N = 0; last = None; trades = 0; i = 0
    by_bar = {}
    for e in ev: by_bar.setdefault(e[0], []).append(e)
    bars = sorted(by_bar)
    nxt = 0
    for t in range(1, len(FT)):
        sc = MULT / fac[t]
        px = FC[t - 1]
        for (_, _, du, x) in by_bar.get(t, []):
            pnl[t] += N * (x - px) * sc; px = x
            u = max(0.0, u + du); Nn = size(u) if u > 1e-9 else 0.0
            if Nn != N:
                d = abs(Nn - N); trades += d
                pnl[t] -= d * (COMM_SIDE + TICK * MULT)          # commission + 1 tick a contract a side
                N = Nn
        pnl[t] += N * (FC[t] - px) * sc
    day = (cte + pd.Timedelta(hours=8)).tz_localize(None).normalize()
    s = pd.Series(pnl, index=day); s = s[s.index <= days[-1]]
    out = pd.Series(s.to_numpy(), index=ns["to_trading_day"](s.index)).groupby(level=0).sum().reindex(days, fill_value=0.0)
    return out, trades


ser = {}
S6 = PB.run(ctx, books=(40, 42, 44, 46, 48, 50)); S6 = S6[(S6.t >= FT[0]) & (S6.tx <= FT[-1]) & (S6.side == 1)].reset_index(drop=True)
S2 = PB.run(ctx, books=(40, 50)); S2 = S2[(S2.t >= FT[0]) & (S2.tx <= FT[-1]) & (S2.side == 1)].reset_index(drop=True)
ser["FREE"], _ = g["mark"](S2); ser["PREM"], _ = g["mark"](S6)
ser["ROUND"], nt = rounded(S6)
chk, _ = rounded(S2, size=lambda u: u)       # engine check: free books, position = units exactly (fractional) -> should equal the marked plan series
yrs = (days[-1] - pd.Timestamp("2018-12-17")).days / 365.25
print(f"rounded premium: {nt} MBT contract fills, ${ser['ROUND'].sum() / yrs:,.0f} a year | plan free ${ser['FREE'].sum() / yrs:,.0f} | premium 1/3 ${ser['PREM'].sum() / 3 / yrs:,.0f}"
      f" | engine check (free books, position = units, should match the plan): ${chk.sum() / yrs:,.0f}")
for nm, x in (("FREE", ser["FREE"]), ("ROUND", ser["ROUND"]), ("PREM/3", ser["PREM"] / 3)):
    e = x[x.index.year >= 2019].cumsum()
    print(f"   {nm:<7} alone 2019-26: max DD ${(e - e.cummax()).min():,.0f}, worst day ${x.min():,.0f}, by year " + " ".join(f"{y} {v:+,.0f}" for y, v in x.groupby(x.index.year).sum().items() if y >= 2019))
base = P.sum(axis=1)
V = {"base (no BTC)": base, "PLAN: + FREE 1 MBT a book (max 2)": base + ser["FREE"],
     "+ PREMIUM ROUNDED (1 MBT <= 3 units, 2 above)": base + ser["ROUND"], "+ PREMIUM 1/3 MBT a book (ref)": base + ser["PREM"] / 3}
mc = lambda x, sd: (lambda d: (d["pnl_p50"], d["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=sd))
for per, m in (("2019-26", days.year >= 2019), ("2019-22", (days.year >= 2019) & (days.year <= 2022)), ("2023+", days.year >= 2023)):
    print(f"\n{per}: {'variant':<46}{'$ a year p50':>13}{'DD p95':>9}{'ret/DD':>8}{'vs plan':>9}{'seeds better':>14}{'backtest $/yr / DD':>20}")
    R = {nm: [mc(x[m], sd) for sd in range(1, 6)] for nm, x in V.items()}
    pr = [a / b for a, b in R["PLAN: + FREE 1 MBT a book (max 2)"]]
    for nm, rr in R.items():
        r = [a / b for a, b in rr]; x = V[nm][m]; e = x.cumsum(); bt = (x.sum() / (m.sum() / 252)) / -(e - e.cummax()).min()
        print(f"        {nm:<46}${np.mean([a for a, _ in rr]):>11,.0f} ${np.mean([b for _, b in rr]):>7,.0f} {np.mean(r):7.2f} {np.mean(r) - np.mean(pr):+8.2f} "
              f"{sum(a > b for a, b in zip(r, pr))}/5{'':>9}{bt:>10.2f}")
