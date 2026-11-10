"""Standing rule (user 2026-11-10): EVERY new strategy the user sends, good or bad on its own, goes against ALL the data to look for a
better version (and through an ingredient breakdown, DEVELOPMENT_PROCESS). This tool does the data part for one trade list:
  python3 analysis/strategy_data_sweep.py TRADES.csv [NAME]      (TRADES.csv: date, net per contract after costs; extra columns ignored)
Splits the strategy's trades by every regime of every daily series in analysis/data_sweep.py (21 series x 3 regimes, last close
before the trade day) and reports:
  - gap t (favourable vs unfavourable regime), same sign in 2018-22 and 2023+, bar t_threshold(63);
  - the best favourable subset (positive in both periods, >= 40 trades) and the FAIR placebo: the best of 63 random splits with the
    same on-shares, picked the same way, 200 runs -> p. Only a version that beats this placebo is a lead (LESSONS 2026-11-10).
Leads then get a book bench (addition and replacement, same size spread evenly as control) and out-of-sample evidence before any
plan change.
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from metrics import t_threshold
from new_data_screen import RULES, prior
from data_sweep import series


def sweep(x, name="strategy", runs=200, seed=1, S=None):
    """x: Series of net per trade-day (index = dates)."""
    S = series() if S is None else S; x = x[x.index >= "2018-01-01"].sort_index(); e = x.index.year <= 2022; rows = []
    for nm, s in S.items():
        for rule, fn in RULES.items():
            v = prior(s, x.index, fn); ok = ~np.isnan(v); h = (v == 1) & ok
            if h.sum() < 20 or (ok & ~h).sum() < 20: continue
            a, b = x[h], x[ok & ~h]; t = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
            g1 = x[e & h].mean() - x[e & ok & ~h].mean(); g2 = x[~e & h].mean() - x[~e & ok & ~h].mean()
            sub = a if t > 0 else b; se = sub.index.year <= 2022
            rows.append(dict(series=nm, rule=rule, keep="on" if t > 0 else "off", t_gap=t, same=np.sign(g1) == np.sign(g2), share=h.sum() / ok.sum(),
                             n_sub=len(sub), sub_mean=sub.mean(), sub_t=sub.mean() / sub.std() * np.sqrt(len(sub)) if len(sub) > 2 else np.nan,
                             sub_1822=sub[se].mean(), sub_23=sub[~se].mean()))
    R = pd.DataFrame(rows); bar = t_threshold(len(R)); tt = x.mean() / x.std() * np.sqrt(len(x))
    print(f"   {name}: {len(x)} trade days, ${x.mean():.0f} a day, t {tt:.2f} (2018-22 ${x[e].mean():.0f}, 2023+ ${x[~e].mean():.0f}); {len(R)} regimes, gap bar |t| >= {bar:.2f}")
    top = R[R.same].reindex(R[R.same].t_gap.abs().sort_values(ascending=False).index).head(8)
    for r in top.itertuples():
        print(f"      {r.series:<26}{r.rule:<13} keep {r.keep:<3} gap t {r.t_gap:5.2f}{' AT BAR' if abs(r.t_gap) >= bar else ''} | subset n {r.n_sub} ${r.sub_mean:.0f} t {r.sub_t:.2f} ({r.sub_1822:.0f} / {r.sub_23:.0f})")
    ok = R[R.same & (R.n_sub >= 40) & (R.sub_1822 > 0) & (R.sub_23 > 0)]
    if not len(ok): print("      no favourable subset positive in both periods"); return R
    best = ok.sort_values("sub_t", ascending=False).iloc[0]; rng = np.random.default_rng(seed); bt = []
    for _ in range(runs):
        b_ = -9
        for sh in R.share.values:
            m = rng.random(len(x)) < sh
            for sub in (x[m], x[~m]):
                if len(sub) >= 40 and sub[sub.index.year <= 2022].mean() > 0 and sub[sub.index.year > 2022].mean() > 0:
                    b_ = max(b_, sub.mean() / sub.std() * np.sqrt(len(sub)))
        bt.append(b_)
    p = np.mean(np.array(bt) >= best.sub_t)
    print(f"   BEST VERSION: {best.series} {best.rule} keep {best.keep}: t {tt:.2f} -> {best.sub_t:.2f}; fair placebo (best of {len(R)} random splits): "
          f"median {np.median(bt):.2f}, 95th {np.percentile(bt, 95):.2f} -> p {p:.3f} {'LEAD' if p < 0.05 else '(luck explains it)'}")
    return R


if __name__ == "__main__":
    t = pd.read_csv(sys.argv[1]); t["date"] = pd.to_datetime(t.date.astype(str).str[:10])
    print(__doc__.split("\n")[0]); sweep(t.groupby(t.date.dt.normalize()).net.sum(), sys.argv[2] if len(sys.argv) > 2 else sys.argv[1])
