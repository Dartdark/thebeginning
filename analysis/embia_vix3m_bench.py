"""EMBIA_V3 with the data sweep's VIX3M-high filter (user 2026-11-14: 'test this anyway'). POST HOC (the filter was picked by the sweep from 63
regimes; fair placebo p 0.02), so this is a bench of a lead, not a pass. Filter = data_sweep RULES['z_high'] on VIX3M, known before the
entry day (new_data_screen.prior). Two uses:
  A. personal book (NQ as coded, holds overnight): personal_portfolio.py pieces at 1 micro (VB, FC2B, Kusho, S47, S30 out, as bench150.personal),
     + EMBIA-VIX3M at 1 / 2 / 3 MNQ (NQ trades / 10 - $0.55 extra micro fee; P&L booked on the exit day), 1-year block MC median / p95 DD.
  B. evaluation book (#5, bench150.LIVE_EVAL): the APEX-legal version (flat 15:55) with the same filter at 1-3 MNQ, minute paths.
  tools/run_stamped.sh analysis/embia_vix3m_bench.py > analysis/outputs/embia_vix3m_bench_output.txt
"""
import sys, io, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from data_sweep import series
from new_data_screen import RULES, prior
print(__doc__.split("\n")[0])
src = open("analysis/embia_v3_test.py").read().split("RES = {}")[0]; exec(compile(src, "embia_head", "exec"))
S = series(); vx = S["VIX3M"]
def filt(T):
    d = T.ts.dt.normalize(); v = prior(vx, d, RULES["z_high"]); return T[(v == 1) & ~np.isnan(v)].reset_index(drop=True)
tsig, sd, av = signals(NQ, "15min")
T_on = filt(simulate(NQ, tsig, sd, av, nq_cost).pipe(lambda T: T[T.ts >= "2018-01-01"]))
T_ap = filt(simulate(NQ, tsig, sd, av, nq_cost, flat=apex_flat, no_entry=apex_noentry).pipe(lambda T: T[T.ts >= "2018-01-01"]))
print(line(T_on, "NQ as coded + VIX3M high")); print(by_year(T_on)); print(line(T_ap, "NQ Apex + VIX3M high")); print(by_year(T_ap))
print(f"   worst trade per NQ: as coded ${T_on.net.min():,.0f}, Apex ${T_ap.net.min():,.0f}; VIX3M-high share of days {np.nanmean(prior(vx, pd.DatetimeIndex(sorted(set(NQ.index.normalize()))), RULES['z_high'])):.0%}")

print("\n== A. personal book (every piece 1 micro; 1-year block MC, median year / p95 DD = return/DD)")
with contextlib.redirect_stdout(io.StringIO()):
    Pp = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")["P"]
Pp.to_pickle("scratch_data/personal_P.pkl")
Pp = Pp[[c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30", "VaultBreak")]]; base = Pp.sum(axis=1)
ex = (T_on.ts + pd.to_timedelta(T_on.mins, unit="m")).dt.normalize()
add = (T_on.net / 10 - 0.55).groupby(ex.values).sum().reindex(Pp.index, fill_value=0.0)
print(f"   daily corr with the book {np.corrcoef(add, base)[0, 1]:+.2f}; trades in the book window {int((add != 0).sum())}")
def mc(x):
    d = MC.daily_mc(x.values, horizon=252, n=3000, block=20, trail=1e12, seed=1); return d["pnl_p50"], d["dd_p95"], d["pnl_p50"] / d["dd_p95"]
for per, m in (("2018-26", np.ones(len(Pp), bool)), ("2018-22", Pp.index.year <= 2022), ("2023+", Pp.index.year >= 2023)):
    r0 = mc(base[m]); out = [f"book ${r0[0]:,.0f} / ${r0[1]:,.0f} = {r0[2]:.2f}"]
    for k in (1, 2, 3):
        r = mc((base + k * add)[m]); out.append(f"+{k} MNQ ${r[0]:,.0f} / ${r[1]:,.0f} = {r[2]:.2f} ({r[2] - r0[2]:+.2f})")
    print(f"   {per}: " + " | ".join(out))

print("\n== B. evaluation book (#5, Apex version + VIX3M high)")
sys.argv = ["x"]; src2 = open("analysis/eval_size_combo.py").read().split("rows = []")[0].replace("cache=True", "cache=False")
ns = {}; exec(compile(src2, "esc_head", "exec"), ns)
book, fresh, now, LIVE, DES, HOL, NOWV, dts, D = (ns[k] for k in ("book", "fresh", "now", "LIVE", "DES", "HOL", "NOWV", "dts", "D"))
pos = pd.Series(np.arange(D), index=dts); W = np.zeros((D, 1440)); R = np.zeros((D, 1440)); hi_, lo_ = NQ.h.values, NQ.l.values
tsm = NQ.index.values
for t in T_ap.itertuples():
    day = t.ts.normalize()
    if day not in pos.index: continue
    i0 = np.searchsorted(tsm, np.datetime64(t.ts)); seg = slice(i0, i0 + int(t.mins) + 1); mins = NQ.index[seg]
    if (mins.normalize() != day).any(): continue
    js = mins.hour * 60 + mins.minute; adv = ((lo_[seg] if t.side > 0 else hi_[seg]) - t.entry) * t.side * 20 - 17.25
    adv[-1] = t.net
    r = pos[day]; W[r, js] += adv; W[r, js[-1] + 1:] += t.net; R[r, js[-1]:] += t.net
W, R = W / 10 - 0.55 * (R != 0), R / 10
def band(d):
    rg = np.random.default_rng(1); n = len(d); nb_ = int(np.ceil(n / 60)); st = rg.integers(0, n, (1000, nb_))
    mm = d[((st[:, :, None] + np.arange(60)) % n).reshape(1000, -1)[:, :n]].mean(1); return np.percentile(mm, 5), np.percentile(mm, 95)
W0, R0 = book(LIVE); f0 = fresh(W0, R0); n0 = now(W0, R0)
for k in (1, 2, 3):
    f = fresh(W0 + k * W, R0 + k * R); n = now(W0 + k * W, R0 + k * R); d2 = f[HOL] - f0[HOL]; d3 = n[NOWV] - n0[NOWV]; b2 = band(d2); b3 = band(d3)
    print(f"   + {k} MNQ: 18-22 {(f[DES] - f0[DES]).mean():+.1%} | 23-26 {d2.mean():+.1%} [{b2[0]:+.1%},{b2[1]:+.1%}] | #5 now {d3.mean():+.1%} [{b3[0]:+.1%},{b3[1]:+.1%}]", flush=True)
