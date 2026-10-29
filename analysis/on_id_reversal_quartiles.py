"""Overnight -> intraday reversal by overnight quartile (paper: Branch & Ma, 'Overnight Return, the Invisible Hand Behind the
Intraday Return? A Retrospective', SSRN 3259614; user upload 2026-10-29). Paper 2011-17: single stocks' intraday return
reverses the overnight return, monotonic by quartile; for the S&P 500 (SPY) the correlation is now slightly POSITIVE.
Our check, NQ and ES 2018-2026: overnight = 15:00 close -> 08:30 open (CT), intraday = 08:30 open -> 15:00 close;
roll-day jumps dropped (|overnight| > 6 sd). Trade: fade the overnight move 08:31 open -> 15:00 when it is in the top /
bottom quartile (thresholds from 2018-22 only), per contract after $7.25 NQ / $5 ES + 1 tick a side.
python3 analysis/on_id_reversal_quartiles.py
"""
import glob, numpy as np, pandas as pd
for sym, pv, cost, tick in (("NQ", 20, 7.25, 0.25), ("ES", 50, 5.0, 0.25)):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"data/{sym}_1min_20*.csv")) if "_ON_" not in f])
    o = d[d.time == 831].set_index("date").open; c = d[d.time == 1500].set_index("date").close
    x = pd.DataFrame(dict(o=o, c=c)).dropna(); x.index = pd.to_datetime(x.index.astype(str)); x = x[x.index >= "2018-01-01"]
    x["on"] = np.log(x.o / x.c.shift(1)); x["id"] = np.log(x.c / x.o); x = x.dropna()
    x = x[(x.on - x.on.mean()).abs() < 6 * x.on.std()]
    print(f"\n{sym}: {len(x)} days, corr(overnight, intraday) {x.on.corr(x.id):+.3f} "
          f"(2018-22 {x.on[:'2022'].corr(x.id[:'2022']):+.3f}, 2023+ {x.on['2023':].corr(x.id['2023':]):+.3f})")
    x["q"] = pd.qcut(x.on, 4, labels=[1, 2, 3, 4])
    for q, g in x.groupby("q", observed=True):
        print(f"   overnight Q{q} (mean {g.on.mean() * 1e4:+6.1f} bp): intraday {g.id.mean() * 1e4:+6.1f} bp, t {g.id.mean() / g.id.std() * np.sqrt(len(g)):+.1f}")
    lo, hi = x.on[:"2022"].quantile([0.25, 0.75])
    sig = np.where(x.on >= hi, -1, np.where(x.on <= lo, 1, 0)); x["pnl"] = sig * (x.c - x.o) * pv - (cost + 2 * tick * pv) * (sig != 0)
    for per, y in (("2018-22", x[:"2022"]), ("2023+", x["2023":])):
        t = y[sig[x.index.isin(y.index)] != 0]
        for side, s in (("fade up (short)", t.on >= hi), ("fade down (long)", t.on <= lo)):
            p = t.pnl[s]; print(f"   {per} {side:17s} {len(p):4d} days ${p.mean():+5.0f}, t {p.mean() / p.std() * np.sqrt(len(p)):+.1f}")
        p = t.pnl; print(f"   {per} both              {len(p):4d} days ${p.mean():+5.0f}, t {p.mean() / p.std() * np.sqrt(len(p)):+.1f};  always long ${((y.c - y.o) * pv - cost - 2 * tick * pv).mean():+.0f}")
