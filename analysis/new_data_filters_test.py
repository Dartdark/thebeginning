"""Untested data as filters (user 2026-11-09: 'do we have data you haven't tested ideas on yet?' -> 'yes'). PRE-REGISTERED (header
committed before the first run; 3 items, rules fixed here; bar p < 0.0167 = 0.05 / 3, t >= metrics.t_threshold(3)).
Data: OVX / VVIX (CBOE daily closes, data/codex_20261108/), HYG / LQD (data/macro_proxies_daily.csv, to 2026-10-23). Every value
is the last close BEFORE the trading day it acts on (no same-day look-ahead).
  1 OVX x CL Sunday fade (funded plan 3 MCL at 150K): oil-scare regime = Friday's OVX close above the median of its past 252
    closes. A: trade only those weekends; B: size 1.5x on them and 0.5x on the others (same average size). Kept vs skipped
    weekends (t), random-weekend placebo (1,000 runs, same count); funded 150K bench (CLS 3 -> A 3 / B).
  2 VVIX spike -> half size for the whole 150K evaluation set (VB 15, ONB $2,750, Bridge 5, EOS $1,250, Twin 2, DT 2):
    spike = the previous close's VVIX z >= 1 vs its past 60 closes. First a diagnostic: share of the plan's big-loss days
    (VB or ONB <= -$1,500 at plan size) on spike days vs all days. Then the evaluation bench (paired, block band) and a
    placebo: the same number of random half-size days (20 runs).
  3 Credit stress (HYG / LQD ratio below its 50-day average AND below its level 20 days earlier, both as of the previous
    close) -> half size on VB and ONB only in the evaluation set. Diagnostic: VB / ONB $ a day on stress vs other days; then
    the evaluation bench and a 20-run random-day placebo.
Adoption: placebo beaten at p < 0.0167 AND a bench gain whose band excludes zero, positive in 2018-22 and 2023+ -> forward log.
  tools/run_stamped.sh analysis/new_data_filters_test.py > analysis/outputs/new_data_filters_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from combine_levers_test import ONB30
import dual_thrust_bench as DTB
import bench150 as BB
from eval_levers150 import challenge, band


def prior(series, dates, fn):
    """fn(past values up to and including the last close before d) -> value, for each date d."""
    s = series.dropna().sort_index(); idx = s.index.values; out = []
    for d in dates:
        k = np.searchsorted(idx, np.datetime64(d), side="left")       # closes strictly before d
        out.append(fn(s.iloc[:k]) if k > 0 else np.nan)
    return np.array(out, dtype=float)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    ctx = BB.setup(base="legacy"); g, trr, D, dts, lab = ctx["g"], ctx["trr"], ctx["D"], ctx["dts"], ctx["lab"]
    rd = lambda f: pd.read_csv(f, parse_dates=["date"]).set_index("date").close_index_points.astype(float)
    ovx, vvix = rd("data/codex_20261108/OVX.csv"), rd("data/codex_20261108/VVIX.csv")
    mac = pd.read_csv("data/macro_proxies_daily.csv", parse_dates=["date"]).set_index("date"); ratio = (mac.HYG / mac.LQD).dropna()
    # ---------------- 1. OVX x CL Sunday fade
    print("\n1. OVX x CL Sunday fade (per MCL, booked on Monday):")
    ld = pd.DatetimeIndex(lab.g.ts[lab.tr]).normalize(); cls = pd.Series(lab.C["CLS"], index=ld); on = cls[cls != 0]; on = on[on.index >= "2018-01-01"]
    hi = prior(ovx, on.index, lambda s: float(s.iloc[-1] > s.iloc[-252:].median()) if len(s) >= 120 else np.nan) == 1
    tt = lambda v: v.mean() / v.std() * np.sqrt(len(v)) if len(v) > 2 else np.nan
    for nm, m in (("all weekends", np.ones(len(on), bool)), ("high OVX (kept by A)", hi), ("low OVX (skipped)", ~hi)):
        x = on[m]; a, b = x[x.index < "2023"], x[x.index >= "2023"]
        print(f"   {nm:<24} n {len(x):3d} ${x.mean():6.1f} t {tt(x):.2f} | 2018-22 ${a.mean():.1f} 2023+ ${b.mean():.1f}")
    k, s = on[hi], on[~hi]; dif = (k.mean() - s.mean()) / np.sqrt(k.var() / len(k) + s.var() / len(s))
    rng = np.random.default_rng(11); pm = np.array([on.values[rng.choice(len(on), len(k), replace=False)].mean() for _ in range(1000)])
    print(f"   kept - skipped t {dif:.2f} | random weekends: 95th ${np.percentile(pm, 95):.1f}, kept ${k.mean():.1f}, p {np.mean(pm >= k.mean()):.3f}")
    mA = pd.Series(0.0, index=ld); mA[on.index[hi]] = 1.0; mB = pd.Series(1.0, index=ld); mB[on.index[hi]] = 1.5; mB[on.index[~hi]] = 0.5
    BB.funded_bench(ctx, {"CLS -> A (high OVX only)": {**{q: v for q, v in BB.BASE_FUNDED.items() if q != "CLS"}, "CLS_A": BB.BASE_FUNDED["CLS"]},
                          "CLS -> B (1.5x high / 0.5x low)": {**{q: v for q, v in BB.BASE_FUNDED.items() if q != "CLS"}, "CLS_B": BB.BASE_FUNDED["CLS"]}},
                    extra={"CLS_A": (lab.W["CLS"] * mA.values[:, None], lab.C["CLS"] * mA.values), "CLS_B": (lab.W["CLS"] * mB.values[:, None], lab.C["CLS"] * mB.values)})
    # ---------------- evaluation base: the current set
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("DT", DTB.dt_trades(g)), ("ONB", with_slippage(load_mc(g, ONB30)))):
        w, r = paths(g, t); P[nm] = (w[trr] / 10, r[trr] / 10)
    Wb = ctx["Wb"] - 5 * P["VB"][0] + 2 * P["DT"][0]; Rb = ctx["Rb"] - 5 * P["VB"][1] + 2 * P["DT"][1]; ctx["Wb"], ctx["Rb"] = Wb, Rb
    atr = g.daily_atr(15); risk = np.floor(2750 / (np.nan_to_num(0.25 * atr[trr], nan=1e12) * 2))
    vbd, onbd = P["VB"][0].min(axis=1) * 15, P["ONB"][0].min(axis=1) * risk; big = (vbd <= -1500) | (onbd <= -1500)
    S = np.array([pd.Timestamp("2018-01-02") <= d <= pd.Timestamp("2026-09-01") for d in dts])
    def placebo(mask, scale_pieces, runs=20):
        rng = np.random.default_rng(5); out = []; n = int(mask[S].sum())
        for _ in range(runs):
            m = np.zeros(D, bool); m[rng.choice(np.flatnonzero(S), n, replace=False)] = True
            W2, R2 = scale_pieces(m); o = np.array([challenge(W2, R2, s, D) for s in np.flatnonzero(S)]); out.append((o == "pass").mean())
        return np.array(out)
    p0 = np.array([challenge(Wb, Rb, s, D) for s in np.flatnonzero(S)]) == "pass"; print(f"\n   150K evaluation base (current set): pass {p0.mean():.1%}")
    def bench(nm, m, scale):
        W2, R2 = scale(m); o = np.array([challenge(W2, R2, s, D) for s in np.flatnonzero(S)]) == "pass"; lo, hi_ = band(o.astype(float) - p0)
        e = dts[S] < "2023-01-01"
        print(f"   {nm:<40} pass {o.mean():5.1%} ({o.mean() - p0.mean():+.1%}, band {lo:+.1%} / {hi_:+.1%}; 18-22 {o[e].mean() - p0[e].mean():+.1%}, 23+ {o[~e].mean() - p0[~e].mean():+.1%})", flush=True)
        pl = placebo(m, scale); print(f"      random days, same count (20 runs): mean {pl.mean():.1%}, max {pl.max():.1%}; p {np.mean(pl >= o.mean()):.2f}")
    half_all = lambda m: (Wb * np.where(m, 0.5, 1.0)[:, None], Rb * np.where(m, 0.5, 1.0)[:, None])
    # ---------------- 2. VVIX
    print("\n2. VVIX spike -> half size, whole evaluation set:")
    spk = prior(vvix, dts, lambda s: float((s.iloc[-1] - s.iloc[-61:-1].mean()) / s.iloc[-61:-1].std() >= 1.0) if len(s) >= 61 else np.nan) == 1
    print(f"   spike days {spk[S].mean():.1%} of days; big VB / ONB loss days: {big[S].mean():.1%} of all days, {big[S & spk].mean():.1%} of spike days, {big[S & ~spk].mean():.1%} of other days")
    bench("half size on VVIX-spike days", spk, half_all)
    # ---------------- 3. Credit stress
    print("\n3. Credit stress (HYG / LQD) -> half size on VB and ONB:")
    st = prior(ratio, dts, lambda s: float(s.iloc[-1] < s.iloc[-50:].mean() and len(s) > 20 and s.iloc[-1] < s.iloc[-21]) if len(s) >= 50 else np.nan) == 1
    vbday, onbday = P["VB"][1][:, -1] * 15, P["ONB"][1][:, -1] * risk
    for nm, x in (("VB 15", vbday), ("ONB $2,750", onbday)):
        print(f"   {nm:<12} $ a day: stress ${x[S & st].mean():.0f} vs other ${x[S & ~st].mean():.0f} (stress days {st[S].mean():.0%}; big-loss share {big[S & st].mean():.1%} vs {big[S & ~st].mean():.1%})")
    rk = risk[:, None]
    half_vo = lambda m: (Wb - (P["VB"][0] * 15 + P["ONB"][0] * rk) * np.where(m, 0.5, 0.0)[:, None], Rb - (P["VB"][1] * 15 + P["ONB"][1] * rk) * np.where(m, 0.5, 0.0)[:, None])
    bench("half VB + ONB on credit-stress days", st, half_vo)
