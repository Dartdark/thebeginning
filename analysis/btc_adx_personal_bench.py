"""BTC ADX longs on MBT (best version: both books ADX 40 / 50, spot signals, resting MBT stop; analysis/btc_adx_mbt_longs_stop_test.py)
against the PERSONAL book (user 2026-11-13 'how much does the best version help the personal book').
Base built locally (scratch_data/personal_P.pkl is cloud-only): analysis/personal_portfolio.py's pieces at 1 micro, minus the
forward-log / retired ones (FC2B, Kusho, S47, S30, VaultBreak), plus Noise-area longs 1 MNQ (checks/candidates/bridge_noise_15m/
trades_longs.csv, per NQ / 10), Overnight Tick at 2 MNQ (user 2026-11-08) and CL Sunday fade at 2 MCL when the last OVX close
before the trade day is above its 1-year median, else 1 (user 2026-11-10; data_sweep OVX, new_data_screen 'above_median').
BTC (v2, user 2026-11-13 'test all this first'): rebuilt trade by trade and MARKED at every CME 16:00 CT close it is held through
(15:45-16:00 CT futures candle), position halves after the half-off, commissions on the exit day; the marks add up to the trade
list exactly. Also: margin in use (CME MBT initial margin ~$2,800 a contract on 2026-03-24 per Schwab, scaled by BTC price),
and the Monte Carlo checked across 5 seeds x 2,000 runs and 1 x 20,000 runs plus the plain backtest return / max DD.
Sizes 1 / 2 / 3 MBT per book. Add AND replace the piece it correlates with most.
Measure (bench150.personal): 1-year block MC (20-day blocks, 2,000 runs), median year $ / p95 drawdown, on 2019-26 (BTC's
window), 2019-22 and 2023+.
  tools/run_stamped.sh analysis/btc_adx_personal_bench.py > analysis/outputs/btc_adx_personal_bench_output.txt
"""
import sys, textwrap, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
print(__doc__.split("\n")[0])
src = open("analysis/personal_portfolio.py", encoding="utf-8").read()
head, body = src.split('if __name__ == "__main__":\n')
body = textwrap.dedent(body.split("    names = {")[0]).replace("print(__doc__", "pass  # print(__doc__")
ns = {}; exec(compile(head, "personal_portfolio_head", "exec"), ns); exec(compile(body, "personal_portfolio_body", "exec"), ns)
P, days, from_trades = ns["P"], ns["days"], ns["from_trades"]
P = P[[c for c in P.columns if c not in ("FC2B", "Kusho", "S47", "S30", "VaultBreak")]].copy()
nbl, _ = from_trades("checks/candidates/bridge_noise_15m/trades_longs.csv", "NoiseLongs"); P["NoiseLongs"] = nbl
P["OvernightTick"] *= 2
from new_data_screen import RULES, prior
from data_sweep import series
ovx = prior(series()["OVX"], P.index, RULES["above_median"]) == 1
P["CLSundayFade_perMCL"] *= np.where(ovx, 2.0, 1.0)
print(f"CL Sunday fade: 2 MCL on {np.mean(ovx[P.CLSundayFade_perMCL.to_numpy() != 0]):.0%} of its trade days (high OVX)")
print(f"base pieces ({P.shape[1]}): {list(P.columns)}; days {days.min().date()} -> {days.max().date()}")

import btc_adx_ensemble_test as PB
MULT, TICK, COMM = 0.1, 5.0, 2.5
fsrc = open("analysis/btc_adx_futures_test.py", encoding="utf-8").read().split(chr(10) + "m = load_fut()")[0].split("import btc_adx_ensemble_test as P")[1].split(chr(10), 2)[2]
fns = {"np": np, "pd": pd, "glob": __import__("glob")}; exec(fsrc, fns)
f = fns["load_fut"](); f15 = PB.rs(f, "15min"); fac = f.f.resample("15min", label="left", closed="left").last().reindex(f15.index).to_numpy()
FT = f15.index.to_numpy(); FO, FL, FC = (f15[k].to_numpy() for k in ("open", "low", "close"))
cte = (f15.index + pd.Timedelta(minutes=15)).tz_localize("UTC").tz_convert("America/Chicago")
MARK = np.flatnonzero((cte.hour == 16) & (cte.minute == 0)); ctd = cte.tz_localize(None).normalize()
S = PB.run(PB.setup()); S = S[(S.t >= FT[0]) & (S.tx <= FT[-1]) & (S.side == 1)].reset_index(drop=True)
seg_d, seg_v, tr_usd, peak = [], [], [], []
for k in S.itertuples():
    ie = np.searchsorted(FT, np.datetime64(k.t)); ix = np.searchsorted(FT, np.datetime64(k.tx))
    if ix >= len(FT) or ie >= ix: continue
    pe = FC[ie] + TICK; real = pe / fac[ie]; stop = pe * (1 - k.R)
    ih = min(max(np.searchsorted(FT, np.datetime64(k.th)), ie), ix) if pd.notna(k.th) else None
    end, exit_px = ix, FC[ix] - TICK
    seg = np.flatnonzero(FL[ie + 1:ix + 1] <= stop)
    if len(seg):
        jj = ie + 1 + seg[0]; exit_px = min(stop, FO[jj]) - TICK; end = jj
        if ih is not None and jj <= ih: ih = None
    pts = sorted(set([ie, end] + [m for m in MARK[(MARK > ie) & (MARK < end)]] + ([ih] if ih is not None and ie < ih < end else [])))
    px = {q: FC[q] for q in pts}; px[ie] = pe; px[end] = exit_px
    q = 1.0; tot = 0.0
    if ih is not None and ih <= ie:          # half-off on the entry candle: half closed at that close, the rest runs at 0.5
        v = 0.5 * (FC[ie] - pe) / pe * real * MULT; seg_d.append(ctd[ie]); seg_v.append(v); tot += v; q = 0.5
    elif ih is not None and ih >= end:       # half-off on the exit candle: that half gets the candle close, not the exit price
        v = 0.5 * (FC[end] - exit_px) / pe * real * MULT; seg_d.append(ctd[end]); seg_v.append(v); tot += v
    for a, b in zip(pts[:-1], pts[1:]):
        v = q * (px[b] - px[a]) / pe * real * MULT
        if ih is not None and b == ih: q = 0.5
        seg_d.append(ctd[b]); seg_v.append(v); tot += v
    c = COMM + (COMM / 4 if ih is not None else 0.0); seg_d.append(ctd[end]); seg_v.append(-c); tot -= c
    tr_usd.append(tot); peak.append((FT[ie], FT[end], real))
seg_d = pd.DatetimeIndex(seg_d); keep = seg_d <= days[-1]
btc = pd.Series(np.array(seg_v)[keep], index=ns["to_trading_day"](seg_d[keep])).groupby(level=0).sum().reindex(days, fill_value=0.0)
ref = pd.read_csv("scratch_data/btc_adx_mbt_longs_stop_trades.csv")
print(f"BTC marked: {len(tr_usd)} trades, sum ${sum(tr_usd):,.0f} vs trade list ${ref.usd.sum():,.0f} (diff ${sum(tr_usd) - ref.usd.sum():,.2f}); "
      f"booked to {days[-1].date()}: ${btc.sum():,.0f}")
t = ref.assign(t=pd.to_datetime(ref.t))
# margin: contracts open at once (1 MBT a book) x $2,800 scaled by BTC price (BTC ~ $84k on 2026-03-24)
ev = sorted([(a, +1, r) for a, b, r in peak] + [(b, -1, r) for a, b, r in peak], key=lambda e: (e[0], e[1]))
n = 0; mx = 0; mxm = 0.0
for tt, dlt, r in ev:
    n += dlt
    if n > mx: mx = n
    mxm = max(mxm, n * 2800 * r / 84000)
print(f"margin: at most {mx} books open at once; peak margin at 1 MBT a book ~${mxm:,.0f} (at BTC $81k today: ${mx * 2800 * 81000 / 84000:,.0f} a size step)")
cor = {c: np.corrcoef(btc[btc.index.year >= 2019], P[c][P.index.year >= 2019])[0, 1] for c in P}
top = max(cor, key=lambda c: cor[c])
print("daily corr with each piece (2019+): " + ", ".join(f"{c} {v:+.2f}" for c, v in sorted(cor.items(), key=lambda kv: -kv[1])))
print(f"corr with the whole book {np.corrcoef(btc[btc.index.year >= 2019], P.sum(axis=1)[P.index.year >= 2019])[0, 1]:+.2f}; most-overlapping piece: {top}")


def mc(x, seed=1, n=2000):
    d = MC.daily_mc(x.values, horizon=252, n=n, block=20, trail=1e12, seed=seed); return d["pnl_p50"], d["dd_p95"]


base = P.sum(axis=1)
V = {"book as is": base}
for k in (1, 2, 3): V[f"+ BTC longs {k} MBT a book"] = base + k * btc
for k in (1, 2): V[f"{top} -> BTC {k} MBT"] = base - P[top] + k * btc
for per, m in (("2019-26", days.year >= 2019), ("2019-22", (days.year >= 2019) & (days.year <= 2022)), ("2023+", days.year >= 2023)):
    print(f"\n{per}: {'variant':<30}{'$ a year p50':>13}{'DD p95':>10}{'ret/DD':>8}{'diff':>7}{'capital (DD/0.20)':>19}")
    r0 = None
    for nm, x in V.items():
        p50, dd = mc(x[m]); r = p50 / dd; r0 = r if r0 is None else r0
        print(f"        {nm:<30}${p50:>11,.0f} ${dd:>8,.0f} {r:7.2f} {r - r0:+6.2f} ${dd / 0.20:>16,.0f}")

print(chr(10) + "Monte Carlo check, return/DD (p50 / p95 DD) by seed (2,000 runs each) and with 20,000 runs; plus the plain backtest $ a year / max DD:")
for per, m in (("2019-26", days.year >= 2019), ("2019-22", (days.year >= 2019) & (days.year <= 2022)), ("2023+", days.year >= 2023)):
    for nm in ("book as is", "+ BTC longs 1 MBT a book", "+ BTC longs 2 MBT a book", "+ BTC longs 3 MBT a book"):
        x = V[nm][m]; rs_ = [(lambda a: a[0] / a[1])(mc(x, seed=sd)) for sd in range(1, 6)]; big = (lambda a: a[0] / a[1])(mc(x, seed=11, n=20000))
        e = x.cumsum(); bt = (x.sum() / (m.sum() / 252)) / -(e - e.cummax()).min()
        print(f"   {per} {nm:<26} seeds {min(rs_):.2f}-{max(rs_):.2f} (mean {np.mean(rs_):.2f}) | 20k runs {big:.2f} | backtest $/yr / max DD {bt:.2f}")
