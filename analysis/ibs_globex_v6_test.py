"""IBS Globex ES 'v6' = v5 with NO emergency stop and exit IBS > 0.7 (user 2026-11-12, after the ingredient breakdown; POST HOC: both
changes were picked on the whole 2016-26 history, so neither period is a clean holdout). Same engine as analysis/ibs_globex_test.py.
Standard test: our costs, both periods, by year, exits, metrics, beta controls, NQ, bootstrap + permutation 2023+, MC at 1 ES / 1 MES,
data sweep at entry, personal book bench (add, replace the most-correlated piece) vs v5.
  tools/run_stamped.sh analysis/ibs_globex_v6_test.py > analysis/outputs/ibs_globex_v6_test_output.txt
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import ibs_globex_test as I, metrics as MT, resampling as RS, montecarlo as MC, strategy_data_sweep as SW

print(__doc__.split("\n")[0])
d, _ = I.minutes("ES"); S = I.sessions(d); pv = 50.0
V = {"v5 (stop 2.5 ATR, exit 0.8)": I.run(d, S), "v6 (no stop, exit 0.7)": I.run(d, S, stop=0, ex=0.7),
     "v6 + time stop off": I.run(d, S, stop=0, ex=0.7, hold=0), "v6 with his costs ($13)": I.run(d, S, stop=0, ex=0.7, costs="his")}
days_idx = pd.DatetimeIndex(sorted(set(S.sess[S.ok]))); days_idx = days_idx[days_idx >= "2018-01-01"]
for nm, T in V.items():
    y = pd.DatetimeIndex(T.entry_ts).year
    print(f"\n== {nm}")
    for lab, m in (("all 2017-26", y > 0), ("his IS 2016-21", y <= 2021), ("his OOS 2022+", y >= 2022), ("design 2018-22", (y >= 2018) & (y <= 2022)), ("holdout 2023+", y >= 2023)):
        print(I.line(T[m], lab))
    print("   by year: " + "  ".join(f"{k} ${g.net.sum():,.0f} ({len(g)})" for k, g in T.groupby(y)))
    print("   exits: " + "  ".join(f"{k}: {len(g)} ${g.net.sum():,.0f} (worst ${g.net.min():,.0f})" for k, g in T.groupby("why")) + f" | worst trade ${T.net.min():,.0f}, avg hold {T.days.mean():.1f}")
    if "his" in nm: continue
    T18 = T[y >= 2018]; D = I.daily_marked(d, T18, pv, days_idx).reindex(days_idx, fill_value=0.0); V[nm] = (T, D)
    for lab, dd, tt in (("all", D, T18), ("2018-22", D[D.index.year <= 2022], T18[pd.DatetimeIndex(T18.entry_ts).year <= 2022]), ("2023+", D[D.index.year >= 2023], T18[pd.DatetimeIndex(T18.entry_ts).year >= 2023])):
        p = MT.perf(dd, tt.net, capital=150_000)
        print(f"   metrics {lab:<8} Sharpe {p['sharpe']:.2f} Sortino {p['sortino']:.2f} PF {p['profit_factor']:.2f} Calmar {p['calmar']:.2f} Ulcer {p['ulcer']:.2f} maxDD ${p['max_dd']:,.0f} (daily marked, incl. open trades) annual ${p['annual']:,.0f}")

T6, D6 = V["v6 (no stop, exit 0.7)"]; T5, D5 = V["v5 (stop 2.5 ATR, exit 0.8)"]; y6 = pd.DatetimeIndex(T6.entry_ts).year; T18 = T6[y6 >= 2018]
print("\n== v6 worst open drawdown inside a trade (no stop: how deep a held loser gets, per ES)")
lo = d.low.to_numpy(); ts = d.ts.to_numpy(); mae = []
for r in T18.itertuples():
    a, b = np.searchsorted(ts, np.datetime64(r.entry_ts)), np.searchsorted(ts, np.datetime64(r.exit_ts)); mae.append((lo[a:b + 1].min() - r.entry) * pv)
mae = np.array(mae); print(f"   median ${np.median(mae):,.0f}, 5% worst ${np.percentile(mae, 5):,.0f}, worst ${mae.min():,.0f} (date {T18.entry_ts.iloc[int(np.argmin(mae))]})")
print("\n== Beta control (v6): random entry days with v6's hold lengths, 300 runs")
c = d.close.to_numpy(); o = d.open.to_numpy(); okk = np.flatnonzero((S.ok & (S.sess >= "2018-01-01")).to_numpy()); DI = S.di.to_numpy().astype(int); rng = np.random.default_rng(1); res = []
for _ in range(300):
    tot = 0.0; p = 0
    for hd in rng.permutation(T18.days.to_numpy()):
        p += int(rng.integers(1, 6))
        if p + int(hd) >= len(okk): break
        tot += (o[DI[okk[p + int(hd)]] + 1] - o[DI[okk[p]] + 1]) * pv - 30.0; p += int(hd)
    res.append(tot)
res = np.array(res); print(f"   random mean ${res.mean():,.0f}, p95 ${np.percentile(res, 95):,.0f}; rule ${T18.net.sum():,.0f}; p {np.mean(res >= T18.net.sum()):.3f}")
dn, _ = I.minutes("NQ"); Tn = I.run(dn, I.sessions(dn), sym="NQ", stop=0, ex=0.7); yn = pd.DatetimeIndex(Tn.entry_ts).year
print("\n== Same v6 on NQ (fresh market for this change)"); print(I.line(Tn[(yn >= 2018) & (yn <= 2022)], "NQ 2018-22")); print(I.line(Tn[yn >= 2023], "NQ 2023+"))
Tn5 = I.run(dn, I.sessions(dn), sym="NQ"); yn5 = pd.DatetimeIndex(Tn5.entry_ts).year; print(I.line(Tn5[(yn5 >= 2018) & (yn5 <= 2022)], "NQ v5 2018-22")); print(I.line(Tn5[yn5 >= 2023], "NQ v5 2023+"))
print("\n== Bootstrap + drawdown permutation, 2023+ (1 ES daily)")
B, P = RS.report({"v5": D5[D5.index.year >= 2023], "v6": D6[D6.index.year >= 2023]}, n=3000, capital=150_000, limits=(10000, 20000, 40000)); print(B); print(P)
print("\n== Monte Carlo v6 (1 ES, 1 MES)")
for size in (1.0, 0.1): print(MC.report(T18.net, D6, size=size, label="IBS v6", trail=1e12))
print("\n== Data sweep v6 (regime at the entry session)")
e = T18.assign(date=(pd.DatetimeIndex(T18.entry_ts) + pd.Timedelta(hours=7) - pd.Timedelta(minutes=1)).normalize())
SW.sweep(e.groupby("date").net.sum(), "ibs_v6_at_entry")
print("\n== Personal book (every piece 1 micro, OT 2 MNQ): return / DD of the 1-year block MC")
with contextlib.redirect_stdout(io.StringIO()):
    Pp = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")["P"]
Pp = Pp[[c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30")]]; base = Pp.sum(axis=1) + Pp.OvernightTick
def mes(T, D):
    f = T.groupby(pd.DatetimeIndex(T.exit_ts).normalize()).size().reindex(Pp.index, fill_value=0) * 0.55
    return D.reindex(Pp.index, fill_value=0.0) / 10 - f
m5, m6 = mes(T5[pd.DatetimeIndex(T5.entry_ts).year >= 2018], D5), mes(T18, D6)
cp = {c: float(np.corrcoef(m6, Pp[c])[0, 1]) for c in Pp}; top = max(cp, key=cp.get); print(f"   v6 most correlated piece: {top} {cp[top]:+.2f}")
def mc(x):
    r = MC.daily_mc(x.values, horizon=252, n=3000, block=20, trail=1e12, seed=1); return r["pnl_p50"], r["dd_p95"], r["pnl_p50"] / r["dd_p95"]
W = {"book": base, "+ v5 1 MES": base + m5, "+ v6 1 MES": base + m6, "+ v6 2 MES": base + 2 * m6, f"- {top} + v6 1 MES": base - Pp[top] + m6, f"- {top} (control)": base - Pp[top]}
for per, m in (("2018-26", np.ones(len(Pp), bool)), ("2018-22", Pp.index.year <= 2022), ("2023+", Pp.index.year >= 2023)):
    r0 = mc(base[m]); print(f"   {per}: " + " | ".join(f"{nm} ${a:,.0f}/${dd:,.0f}={q:.2f}" + ("" if nm == "book" else f" ({q - r0[2]:+.2f})") for nm, x in W.items() for a, dd, q in [mc(x[m])]))
