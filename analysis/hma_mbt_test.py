"""HMA 16/65 + RSI + LinReg on CME micro bitcoin futures (pre-registered: checks/candidates/hma_btc4h/PREREG.md, Amendment 1).
  tools/run_stamped.sh analysis/hma_mbt_test.py > analysis/outputs/hma_mbt_test_output.txt
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.argv = ["x", "scratch_data"]
import numpy as np, pandas as pd
src = open("analysis/hma_btc4h_test.py").read().split("\nm = load_btc()")[0]; exec(compile(src, "hma_head", "exec"))
import roll_adjust as RA, montecarlo as MC
from cl_forced_flows_test import load
print(__doc__.split("\n")[0])
RA.WINDOWS.setdefault("BTC", (tuple(range(1, 13)), 15, 31))
g = load("BTC"); J = RA.roll_jumps(g, "BTC"); flat = np.arange(g.D * 1440)
o, h, l, c = (x.ravel() for x in (g.o, g.h, g.l, g.c)); cf = pd.Series(c).ffill().to_numpy()
fac = np.ones(len(c))
for j, jump in J.items():
    prev = cf[j - 1]; fac[flat < j] *= (prev + jump) / prev                      # older prices x new / old (ratio back-adjustment)
ts = (pd.DatetimeIndex(np.repeat(g.ts, 1440)) + pd.to_timedelta(np.tile(np.arange(1440), g.D), unit="m"))
ok = np.isfinite(c)
m = pd.DataFrame({"open": o[ok] * fac[ok], "high": h[ok] * fac[ok], "low": l[ok] * fac[ok], "close": c[ok] * fac[ok], "raw": c[ok]}, index=ts[ok])
m.index = (m.index.tz_localize("America/Chicago", ambiguous="NaT", nonexistent="NaT") - pd.Timedelta(minutes=1))
m = m[m.index.notna()]; m.index = m.index.tz_convert("UTC").tz_localize(None); m = m[~m.index.duplicated()].sort_index()
roll_ts = pd.DatetimeIndex([ts[j] for j in J.index]).tz_localize("America/Chicago", ambiguous="NaT", nonexistent="NaT").tz_convert("UTC").tz_localize(None)
print(f"CME BTC 1-min {m.index[0]} .. {m.index[-1]}; {len(J)} rolls removed (ratio)")
B = m.resample("4h", label="left", closed="left").agg({"open": "first", "high": "max", "low": "min", "close": "last", "raw": "last"}).dropna()
ent, ext = signals(B, "hma")
def mbt_trades(cost_extra=True):
    c_ = B.close.values; raw = B.raw.values; idx = B.index; out = []; i0 = None
    for i in range(len(c_)):
        if i0 is not None and ext[i]:
            nroll = int(((roll_ts > idx[i0]) & (roll_ts <= idx[i])).sum())
            cost_pct = 3.50 * (1 + (nroll if cost_extra else 0)) / (0.1 * raw[i0])
            out.append((idx[i0], idx[i], c_[i0], c_[i], c_[i] / c_[i0] - 1 - cost_pct, i - i0, nroll, (c_[i] / c_[i0] - 1) * 0.1 * raw[i0] - 3.50 * (1 + nroll))); i0 = None
        if i0 is None and ent[i] and not ext[i]: i0 = i
    return pd.DataFrame(out, columns=["entry_t", "exit_t", "entry", "exit", "ret", "bars", "rolls", "usd_mbt"])
T = mbt_trades(); S, E = "2019-02-20", "2026-12-31"
print(f"   trades {len((T := T[T.entry_t >= S]))}, avg rolls a trade {T.rolls.mean():.2f}, $ per MBT a trade {T.usd_mbt.mean():.1f} (t {T.usd_mbt.mean() / T.usd_mbt.std() * np.sqrt(len(T)):.2f})")
for nm, a, z in (("whole 2019-02 -> 2026-10", S, E), ("2019-22", S, "2023-01-01"), ("2023+", "2023-01-01", E)): print(stats(B, T, "MBT HMA, " + nm, a, z))
rng = np.random.default_rng(1); BB = B[B.index >= S]; cc = BB.close.values; n = len(cc); L = T.bars.values; real = np.log1p(T.ret).sum(); sims = []
cp = (3.50 / (0.1 * BB.raw.values))
for _ in range(500):
    starts = np.sort(rng.choice(n - L.max() - 1, len(L), replace=False)); tot = 0.0; last = -1
    for s0, ll in zip(starts, rng.permutation(L)):
        s0 = max(s0, last + 1)
        if s0 + ll >= n: continue
        tot += np.log(max(cc[s0 + ll] / cc[s0] - cp[s0], 1e-9)); last = s0 + ll
    sims.append(tot)
sims = np.array(sims)
print(f"   random-timing placebo (500 runs): median total {np.expm1(np.median(sims)) * 100:+.0f}%, p95 {np.expm1(np.percentile(sims, 95)) * 100:+.0f}% vs real {np.expm1(real) * 100:+.0f}% -> p {np.mean(sims >= real):.3f}")
sp = load_btc(); SB = bars4h(sp); SB = SB[(SB.index >= B.index[0]) & (SB.index <= B.index[-1])]; e2, x2 = signals(SB, "hma"); ST = trades(SB, e2, x2, 0.0006)
print(stats(SB, ST, "SPOT HMA same span (6 bp)", S, E))
print("\n== personal book + 1 MBT (P&L in $ booked on the exit day; 1-year block MC median / p95 DD)")
with contextlib.redirect_stdout(io.StringIO()):
    Pp = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")["P"]
Pp = Pp[[k for k in Pp.columns if k not in ("FC2B", "Kusho", "S47", "S30", "VaultBreak")]]; base = Pp.sum(axis=1)
add = T.usd_mbt.groupby(T.exit_t.dt.normalize().values).sum().reindex(Pp.index, fill_value=0.0)
print(f"   corr with the book {np.corrcoef(add, base)[0, 1]:+.2f}; worst trade ${T.usd_mbt.min():,.0f} per MBT")
def mc(x): d = MC.daily_mc(x.values, horizon=252, n=3000, block=20, trail=1e12, seed=1); return d["pnl_p50"], d["dd_p95"], d["pnl_p50"] / d["dd_p95"]
for per, mm in (("2018-26", np.ones(len(Pp), bool)), ("2018-22", Pp.index.year <= 2022), ("2023+", Pp.index.year >= 2023)):
    r0 = mc(base[mm]); r1 = mc((base + add)[mm]); r2 = mc((base + 2 * add)[mm])
    print(f"   {per}: book ${r0[0]:,.0f} / ${r0[1]:,.0f} = {r0[2]:.2f} | +1 MBT {r1[2]:.2f} ({r1[2] - r0[2]:+.2f}) | +2 MBT {r2[2]:.2f} ({r2[2] - r0[2]:+.2f})")
