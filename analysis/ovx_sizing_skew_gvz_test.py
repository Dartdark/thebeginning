"""A: CL Sunday fade sized up on high-OVX weekends (POST HOC sizing question from watch #37; information only). B: the last two
untested datasets, SKEW and GVZ (user 2026-11-10: 'test this then move on to the last 2 data sets'). PRE-REGISTERED (header
committed before the first run; B = 3 items, bar p < 0.0167 / t >= metrics.t_threshold(3)). Every index value is the last close
BEFORE the day it acts on.
A. CL fade (high OVX = Friday's OVX above its past-252 median): weekends at 1x, high-OVX weekends at 1.5x / 2x, in the personal
   book (CLSundayFade_perMCL column) and the funded 150K bench (CLS 3 MCL -> the multiplied version).
B1 SKEW top decile (previous close above the 90th percentile of its past 252 closes) -> half size for the whole 150K evaluation
   set (current set); evaluation bench + 20-run random-day placebo.
B2 SKEW as a predictor (information + test): NQ 08:31 -> 14:55 return per NQ the day after a top-decile vs a bottom-decile SKEW
   close (difference t), and a rule: short NQ 08:31 -> 14:55, stop 0.5 ATR, after top-decile days; random-side placebo.
B3 GVZ spike (previous close z >= 1 vs its past 60) -> fade gold's previous COMEX session move (07:21 open -> 12:30 close) the next
   session, enter 07:21, out 12:30, stop 0.5 x ATR15; GC $100 / point, $5 + 1 tick per fill; random-side placebo (500 runs).
  tools/run_stamped.sh analysis/ovx_sizing_skew_gvz_test.py > analysis/outputs/ovx_sizing_skew_gvz_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from ingredient_ablation3 import line
import ingredient_ablation4 as IA4
import dual_thrust_bench as DTB, montecarlo as MC, bench150 as BB
from eval_levers150 import challenge, band
from new_data_filters_test import prior


def zfn(n):
    return lambda s: float((s.iloc[-1] - s.iloc[-n - 1:-1].mean()) / s.iloc[-n - 1:-1].std()) if len(s) > n else np.nan


def day_trades(g, dates, sides, t0, t1, stop, pv, tick, comm):
    IA4.COMM = comm; atr = g.daily_atr(15); pos = pd.Series(np.arange(len(g.ts)), index=pd.DatetimeIndex(g.ts)); rows = []
    for d, s in zip(dates, sides):
        if d not in pos.index or s == 0: continue
        r = int(pos[d])
        if np.isnan(atr[r]) or is_early_close(d): continue
        x = IA4.walk(g, r * 1440 + jof(t0) + 1, r * 1440 + jof(t1), int(s), stop * atr[r], pv, tick)
        if x is not None: rows.append((d, int(s), x))
    return pd.DataFrame(rows, columns=["date", "side", "net"])


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    rd = lambda f: pd.read_csv(f, parse_dates=["date"]).set_index("date").close_index_points.astype(float)
    ovx, skew, gvz = rd("data/codex_20261108/OVX.csv"), rd("data/codex_20261108/SKEW.csv"), rd("data/codex_20261108/GVZ.csv")
    # ---------------- A
    print("\nA. CL fade sized up on high-OVX weekends (post hoc; information):")
    P = pd.read_pickle("scratch_data/personal_P.pkl"); col = "CLSundayFade_perMCL"; on = P[col][P[col] != 0]
    hi = prior(ovx, on.index, lambda s: float(s.iloc[-1] > s.iloc[-252:].median()) if len(s) >= 120 else np.nan) == 1
    f = lambda x: (lambda r: (r["pnl_p50"], r["dd_p95"], r["pnl_p50"] / r["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    for k in (1.5, 2.0):
        mult = pd.Series(1.0, index=P.index); mult[on.index[hi]] = k
        for lab, cols in (("full", list(P.columns)), ("core", [c for c in P.columns if c not in ("FC2B", "Kusho", "S47", "S30")])):
            b = P[cols].sum(axis=1); a = b - P[col] + P[col] * mult; parts = []
            for per, m in (("2018-26", np.ones(len(P), bool)), ("2018-22", P.index.year <= 2022), ("2023+", P.index.year >= 2023)):
                x, y = f(b[m]), f(a[m]); parts.append(f"{per} {x[2]:.2f} -> {y[2]:.2f} ({y[2] - x[2]:+.2f}; median ${y[0] - x[0]:+,.0f}, DD ${y[1] - x[1]:+,.0f})")
            print(f"   high-OVX x{k}, {lab} book: " + " | ".join(parts), flush=True)
    ctx = BB.setup(); g, trr, D, dts, lab_ = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"], ctx["lab"]
    ld = pd.DatetimeIndex(lab_.g.ts[lab_.tr]).normalize(); hset = set(on.index[hi])
    ext = {}; var = {}
    for k in (1.5, 2.0):
        m = np.array([k if d in hset else 1.0 for d in ld]); key = f"CLS_x{k}"; ext[key] = (lab_.W["CLS"] * m[:, None], lab_.C["CLS"] * m)
        var[f"CLS high-OVX x{k}"] = {**{q: v for q, v in BB.BASE_FUNDED.items() if q != "CLS"}, key: BB.BASE_FUNDED["CLS"]}
    BB.funded_bench(ctx, var, extra=ext)
    # ---------------- B1
    print("\nB1. SKEW top decile -> half size, 150K evaluation (current set):")
    Pp = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("DT", DTB.dt_trades(g))): w, r = paths(g, t); Pp[nm] = (w[trr] / 10, r[trr] / 10)
    Wb = ctx["Wb"] - 5 * Pp["VB"][0] + 2 * Pp["DT"][0]; Rb = ctx["Rb"] - 5 * Pp["VB"][1] + 2 * Pp["DT"][1]
    S = np.array([pd.Timestamp("2018-01-02") <= d <= pd.Timestamp("2026-09-01") for d in dts]); St = np.flatnonzero(S); e = dts[S] < "2023-01-01"
    top = prior(skew, dts, lambda s: float(s.iloc[-1] > s.iloc[-252:].quantile(0.9)) if len(s) >= 252 else np.nan) == 1
    p0 = np.array([challenge(Wb, Rb, s, D) for s in St]) == "pass"
    hm = lambda m: (Wb * np.where(m, 0.5, 1.0)[:, None], Rb * np.where(m, 0.5, 1.0)[:, None])
    W2, R2 = hm(top); o = np.array([challenge(W2, R2, s, D) for s in St]) == "pass"; lo, hi_ = band(o.astype(float) - p0)
    print(f"   top-decile days {top[S].mean():.1%}; base {p0.mean():.1%} -> {o.mean():.1%} ({o.mean() - p0.mean():+.1%}, band {lo:+.1%} / {hi_:+.1%}; 18-22 {o[e].mean() - p0[e].mean():+.1%}, 23+ {o[~e].mean() - p0[~e].mean():+.1%})")
    rng = np.random.default_rng(9); pl = []
    for _ in range(20):
        mm = np.zeros(D, bool); mm[rng.choice(St, int(top[S].sum()), replace=False)] = True; W3, R3 = hm(mm)
        pl.append((np.array([challenge(W3, R3, s, D) for s in St]) == "pass").mean())
    print(f"   random days (20 runs): mean {np.mean(pl):.1%}, max {np.max(pl):.1%}; p {np.mean(np.array(pl) >= o.mean()):.2f}", flush=True)
    # ---------------- B2
    print("\nB2. SKEW as a predictor of NQ's next session (per NQ):")
    days = pd.DatetimeIndex(g.ts[g.trading]); days = days[(days >= "2018-01-01")]
    dec = prior(skew, days, lambda s: float(np.searchsorted(np.sort(s.iloc[-253:-1].values), s.iloc[-1]) / 252) if len(s) >= 253 else np.nan)
    allL = day_trades(g, days, np.ones(len(days)), 830, 1455, 0.5, 20.0, 0.25, 7.25).set_index("date").net
    q = pd.Series(dec, index=days).reindex(allL.index)
    tq, bq = allL[q >= 0.9], allL[q <= 0.1]
    print(f"   long 08:31 -> 14:55 after top-decile SKEW: n {len(tq)} ${tq.mean():.0f} | after bottom-decile: n {len(bq)} ${bq.mean():.0f} | all days ${allL.mean():.0f}; diff t {(tq.mean() - bq.mean()) / np.sqrt(tq.var() / len(tq) + bq.var() / len(bq)):.2f}")
    sd = days[(pd.Series(dec, index=days) >= 0.9).values]
    Ts = day_trades(g, sd, -np.ones(len(sd)), 830, 1455, 0.5, 20.0, 0.25, 7.25); print(line(Ts.net, Ts.date, "rule: short NQ after top-decile SKEW"))
    rng = np.random.default_rng(3); pm = [day_trades(g, sd, rng.choice([-1, 1], len(sd)), 830, 1455, 0.5, 20.0, 0.25, 7.25).net.mean() for _ in range(100)]
    print(f"   random side (100 runs): 95th ${np.percentile(pm, 95):.0f}; rule ${Ts.net.mean():.0f}; p {np.mean(np.array(pm) >= Ts.net.mean()):.3f}", flush=True)
    # ---------------- B3
    print("\nB3. GVZ spike -> fade gold's previous COMEX session (per GC):")
    gc = pickle.load(open("scratch_data/gc.pkl", "rb")); gd = pd.DatetimeIndex(gc.ts[gc.trading]); gd = gd[gd >= "2018-01-01"]
    cf = pd.Series(gc.c.ravel()).ffill().to_numpy(); pos = pd.Series(np.arange(len(gc.ts)), index=pd.DatetimeIndex(gc.ts))
    zz = prior(gvz, gd, zfn(60)); dates, sides = [], []
    for i in range(1, len(gd)):
        if not (zz[i] >= 1.0): continue
        r0 = int(pos[gd[i - 1]]); mv = cf[r0 * 1440 + jof(1230)] - gc.o[r0, jof(721)]
        if np.isfinite(mv) and mv != 0: dates.append(gd[i]); sides.append(-int(np.sign(mv)))
    Tg = day_trades(gc, dates, sides, 720, 1230, 0.5, 100.0, 0.10, 5.0); print(line(Tg.net, Tg.date, "rule: fade after a GVZ spike"))
    Tf = day_trades(gc, dates, [-s for s in sides], 720, 1230, 0.5, 100.0, 0.10, 5.0); print(line(Tf.net, Tf.date, "control: follow instead"))
    rng = np.random.default_rng(4); pm = [day_trades(gc, dates, rng.choice([-1, 1], len(dates)), 720, 1230, 0.5, 100.0, 0.10, 5.0).net.mean() for _ in range(500)]
    print(f"   random side (500 runs): 95th ${np.percentile(pm, 95):.0f}; rule ${Tg.net.mean():.0f}; p {np.mean(np.array(pm) >= Tg.net.mean()):.3f}")
