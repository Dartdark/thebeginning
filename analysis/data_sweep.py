"""Full sweep: every daily data series in the repo x 3 regimes x every personal-book piece (user 2026-11-10: 'with the data sets we have,
have all strategies been tested on them to see if the data can unearth hidden optimizations?'). Screen, information only: uses
analysis/new_data_screen.py's regimes (above its 1-year median / z >= 1 vs 60 / rising over 20 closes; last close BEFORE the day).
Multiple testing: the bar is metrics.t_threshold(number of piece x series x regime comparisons); a LEAD also needs the same sign
of the gap in 2018-22 and 2023+. Also listed: the strongest 20 with the same sign in both periods (below the bar = noise-level).
  tools/run_stamped.sh analysis/data_sweep.py > analysis/outputs/data_sweep_output.txt
"""
import sys, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from metrics import t_threshold
from new_data_screen import RULES, prior


def series():
    S = {}
    rd = lambda f, dc, vc: pd.read_csv(f, parse_dates=[dc]).set_index(dc)[vc].astype(float).dropna().sort_index()
    S["VIX"] = rd("data/VIX_daily.csv", "DATE", "CLOSE"); S["VXN"] = rd("data/VXN_daily.csv", "DATE", "CLOSE"); S["VIX3M"] = rd("data/VIX3M_daily.csv", "DATE", "CLOSE")
    c = "data/codex_20261108/"
    for k in ("VIX9D", "VVIX", "SKEW", "OVX", "GVZ"): S[k] = rd(c + f"{k}.csv", "date", "close_index_points")
    S["VIX/VIX3M (term structure)"] = (S["VIX"] / S["VIX3M"]).dropna(); S["VIX9D/VIX"] = (S["VIX9D"] / S["VIX"]).dropna(); S["VXN-VIX"] = (S["VXN"] - S["VIX"]).dropna()
    d = pd.read_csv("data/DIX.csv", parse_dates=["date"]).set_index("date"); S["DIX"] = d.dix.astype(float).dropna(); S["GEX (SqueezeMetrics)"] = d.gex.astype(float).dropna()
    m = pd.read_csv("data/macro_proxies_daily.csv", parse_dates=["date"]).set_index("date")
    S["HYG/LQD credit"] = (m.HYG / m.LQD).dropna(); S["TNX 10y yield"] = m.TNX.dropna(); S["TNX-IRX curve"] = (m.TNX - m.IRX).dropna()
    S["copper/gold"] = (m["HG=F"] / m["GC=F"]).dropna(); S["TIP/IEF breakevens"] = (m.TIP / m.IEF).dropna()
    S["RRP"] = rd("data/nyfed/rrp_daily.csv", "operationDate", "rrp_bn"); S["SPX"] = rd("data/SPX_daily.csv", "date", "close")
    F = pd.read_csv("data/finra/short_volume.csv", sep="|", parse_dates=["Date"])
    F = F[F.Symbol.isin(["QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "AVGO", "TSLA", "COST", "NFLX"]) & (F.TotalVolume > 0)]
    S["GPR (geopolitical)"] = rd("data/GPR_daily.csv", "date", "GPRD")      # Caldara-Iacoviello daily GPR (matteoiacoviello.com), added 2026-11-14 (EdgeFinder triage)
    S["FINRA short ratio"] = (F.ShortVolume / F.TotalVolume).groupby(F.Date).mean().sort_index()
    return S


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    P = pd.read_pickle("scratch_data/personal_P.pkl"); S = series(); rows = []
    for nm, s in S.items():
        for rule, fn in RULES.items():
            on = pd.Series(prior(s, P.index, fn) == 1, index=P.index)
            if on.mean() < 0.05 or on.mean() > 0.95: continue
            for c in P.columns:
                x = P[c][P[c] != 0]; h = on.reindex(x.index).values; a, b = x[h], x[~h]
                if len(a) < 10 or len(b) < 10: continue
                t = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b)); e = x.index.year <= 2022
                g1, g2 = x[e & h].mean() - x[e & ~h].mean(), x[~e & h].mean() - x[~e & ~h].mean()
                rows.append(dict(series=nm, rule=rule, piece=c, on_share=h.mean(), on=a.mean(), off=b.mean(), t=t, g1822=g1, g23=g2, same=np.sign(g1) == np.sign(g2)))
        print(f"   screened {nm}", flush=True)
    R = pd.DataFrame(rows); bar = t_threshold(len(R)); R["lead"] = (R.t.abs() >= bar) & R.same
    print(f"\n   {len(S)} series x 3 regimes x {len(P.columns)} pieces = {len(R)} comparisons; bar |t| >= {bar:.2f} (and the same sign in both periods)")
    print(f"   leads at the bar: {int(R.lead.sum())}; |t| >= 3 with the same sign: {int(((R.t.abs() >= 3) & R.same).sum())}; expected by chance at |t| >= 3: ~{len(R) * 0.0027:.1f}")
    pd.set_option("display.width", 250)
    top = R[R.same].reindex(R[R.same].t.abs().sort_values(ascending=False).index).head(20)
    print("\n   strongest 20 with the same sign in both periods ($ per active day per micro, on / off the regime):")
    for r in top.itertuples():
        print(f"   {r.series:<26}{r.rule:<14}{r.piece:<22} t {r.t:5.2f} | on ${r.on:5.0f} off ${r.off:5.0f} | gap 18-22 {r.g1822:+5.0f} 23+ {r.g23:+5.0f}{'  LEAD' if r.lead else ''}")
    R.to_csv("analysis/outputs/data_sweep_table.csv", index=False)
