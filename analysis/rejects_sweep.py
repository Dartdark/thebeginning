"""Data sweep over the strategies that DIDN'T make a plan (user 2026-11-10: 'do the same ... for all strategies that didn't make it').
Screen, information only. Each candidate's trade list (checks/candidates/<name>/trades.csv | mc_trades.csv | python_trades.csv,
net per contract after costs, summed by date) x the 21 daily data series x 3 regimes of analysis/data_sweep.py (last close
before the day). Two questions per strategy:
  1. does a regime split it (gap t, same sign in 2018-22 and 2023+)?
  2. RESCUE: is the regime's favourable subset a good strategy on its own (t of its trades, positive in both periods, >= 40 trades)?
Multiple testing: bar = metrics.t_threshold(all strategy x series x regime comparisons) for the gap; rescues are LEADS only and
need out-of-sample evidence (WATCHLIST) before anything else.
Excluded: plan pieces and their replicas / filter versions (they were swept in analysis/data_sweep.py).
  tools/run_stamped.sh analysis/rejects_sweep.py > analysis/outputs/rejects_sweep_output.txt
"""
import sys, os, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from metrics import t_threshold
from new_data_screen import RULES, prior
from data_sweep import series

PLAN = {"bridge_noise_15m_longs", "dual_thrust", "fc_2b", "overnight_tick", "papertrend", "relative_strength", "t_oneside", "twin_continuation",
        "finra_longs"}
SKIP_PREFIX = ("finra_longs_", "vb_", "mon_", "st_shorts", "noise_vix", "twin_mo_flow", "btc_")


def load(name):
    d = f"checks/candidates/{name}/"
    for f in ("trades.csv", "mc_trades.csv", "python_trades.csv"):
        if os.path.exists(d + f):
            t = pd.read_csv(d + f)
            if "date" not in t or "net" not in t: return None
            if "kept" in t: return None
            t["date"] = pd.to_datetime(t.date.astype(str).str[:10], errors="coerce"); t = t.dropna(subset=["date"])
            return t.groupby(t.date.dt.normalize()).net.sum()
    return None


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    names = sorted(n for n in os.listdir("checks/candidates") if n not in PLAN and not n.endswith("_replica") and not n.startswith(SKIP_PREFIX))
    X = {}
    for n in names:
        s = load(n)
        if s is not None and len(s) >= 40: X[n] = s[s.index >= "2018-01-01"]
    print(f"   strategies: {len(X)}: {', '.join(X)}")
    S = series(); rows = []
    for nm, ser in S.items():
        for rule, fn in RULES.items():
            for n, x in X.items():
                h = prior(ser, x.index, fn) == 1; ok = ~np.isnan(prior(ser, x.index, fn))
                xx, hh = x[ok], h[ok]
                if hh.sum() < 20 or (~hh).sum() < 20: continue
                a, b = xx[hh], xx[~hh]; t = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
                e = xx.index.year <= 2022
                g1, g2 = xx[e & hh].mean() - xx[e & ~hh].mean(), xx[~e & hh].mean() - xx[~e & ~hh].mean()
                sub = a if t > 0 else b                                   # the favourable subset
                st = sub.mean() / sub.std() * np.sqrt(len(sub)) if len(sub) > 2 and sub.std() > 0 else np.nan
                se = sub.index.year <= 2022
                rows.append(dict(strategy=n, series=nm, rule=rule, keep=("on" if t > 0 else "off"), t_gap=t, same=np.sign(g1) == np.sign(g2),
                                 n_all=len(xx), all_mean=xx.mean(), all_t=xx.mean() / xx.std() * np.sqrt(len(xx)),
                                 n_sub=len(sub), sub_mean=sub.mean(), sub_t=st, sub_1822=sub[se].mean(), sub_23=sub[~se].mean()))
        print(f"   swept {nm}", flush=True)
    R = pd.DataFrame(rows); bar = t_threshold(len(R)); R.to_csv("analysis/outputs/rejects_sweep_table.csv", index=False)
    print(f"\n   {len(X)} strategies x {len(S)} series x 3 regimes = {len(R)} comparisons; gap bar |t| >= {bar:.2f}")
    print(f"   gaps at the bar with the same sign: {int(((R.t_gap.abs() >= bar) & R.same).sum())}; |t| >= 3.5: {int(((R.t_gap.abs() >= 3.5) & R.same).sum())} (chance ~{len(R) * 0.000465:.1f})")
    resc = R[R.same & (R.n_sub >= 40) & (R.sub_1822 > 0) & (R.sub_23 > 0)].copy()
    best = resc.sort_values("sub_t", ascending=False).groupby("strategy").head(1).sort_values("sub_t", ascending=False)
    print("\n   best RESCUE per strategy (favourable regime subset, positive in both periods), strongest first:")
    print(f"   {'strategy':<24}{'all: n / $ / t':>22}   {'regime (keep)':<40}{'subset: n / $ / t':>22}  {'18-22 / 23+':>14}  gap t")
    for r in best.head(25).itertuples():
        print(f"   {r.strategy:<24}{r.n_all:>6} / {r.all_mean:6.0f} / {r.all_t:5.2f}   {(r.series + ' ' + r.rule + ' (' + r.keep + ')'):<40}{r.n_sub:>6} / {r.sub_mean:6.0f} / {r.sub_t:5.2f}  {r.sub_1822:6.0f} / {r.sub_23:<6.0f}  {r.t_gap:5.2f}")
