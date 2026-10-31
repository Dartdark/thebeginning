"""Gold when NQ is at or below its 200-day moving average (user's question, 2026-10-25). Daily closes (data/ndx_gold_daily.csv,
Yahoo): Nasdaq-100 index ^NDX (NQ's underlying), gold as GLD (dividend-adjusted ETF, 2004-11+) and GC=F (front gold future,
2000-08+, not roll-adjusted). Rule: at today's close, if NDX <= its 200-day SMA, hold gold from today's close to tomorrow's
(no look-ahead); otherwise cash (0%). Compared with: gold held only when NDX is above its 200-day; gold all the time;
random days with the same share of time in the market (placebo); and two portfolios - NDX when above / gold when below
(a 'switch'), against buying and holding NDX. No costs or interest (a few trades a year; costs are negligible).
  python3 analysis/gold_when_nq_below_200_test.py > analysis/outputs/gold_when_nq_below_200_test_output.txt
"""
import numpy as np, pandas as pd

df = pd.read_csv("data/ndx_gold_daily.csv", parse_dates=["date"]).set_index("date")
ndx = df.NDX.dropna(); sma = ndx.rolling(200).mean()
below = (ndx <= sma).where(sma.notna())


def st(r):
    r = r.dropna(); n = len(r) / 252; nav = (1 + r).cumprod()
    cagr = nav.iloc[-1] ** (1 / n) - 1 if n > 0 else np.nan
    return dict(cagr=cagr, vol=r.std() * np.sqrt(252), sharpe=r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan,
                mdd=(nav / nav.cummax() - 1).min(), tim=(r != 0).mean())


def line(nm, r):
    s = st(r); return f"   {nm:<52} CAGR {s['cagr']:6.1%}  vol {s['vol']:5.1%}  Sharpe {s['sharpe']:5.2f}  maxDD {s['mdd']:6.1%}  in market {s['tim']:4.0%}"


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    for gname, start in (("GLD", "2004-11-19"), ("GC=F", "2000-09-01")):
        gold = df[gname].dropna(); gr = gold.pct_change()
        if gname == "GC=F": gr = gr.where(gr.abs() < 0.12)                       # drops roll / bad-print jumps (rare)
        sig = below.shift(1).reindex(gr.index)                                     # yesterday's close decides today's hold
        nr = ndx.pct_change().reindex(gr.index)
        w = (gr.index >= start) & sig.notna()
        g, s, n = gr[w].fillna(0), sig[w].astype(bool), nr[w].fillna(0)
        print(f"\n{gname}, {g.index[0].date()} .. {g.index[-1].date()}: NDX at / below its 200-day on {s.mean():.0%} of days")
        print(line("gold only when NDX <= 200-day (the rule)", g.where(s, 0)))
        print(line("gold only when NDX > 200-day", g.where(~s, 0)))
        print(line("gold all the time", g))
        rng = np.random.default_rng(1); sh = []
        for k in range(500):
            m = rng.random(len(g)) < s.mean(); x = g.where(m, 0); sh.append(x.mean() / x.std() * np.sqrt(252))
        print(f"   placebo (random days, same time in market, 500 runs): Sharpe median {np.median(sh):.2f}, 95th pct {np.percentile(sh, 95):.2f}")
        print(f"   gold's average daily return: NDX below {g[s].mean() * 252:+.1%} a year-equivalent, above {g[~s].mean() * 252:+.1%}; "
              f"t of the difference {(g[s].mean() - g[~s].mean()) / np.sqrt(g[s].var() / s.sum() + g[~s].var() / (~s).sum()):.1f}")
        print(line("switch: NDX when above, gold when below", n.where(~s, g)))
        print(line("switch: NDX when above, cash when below", n.where(~s, 0)))
        print(line("NDX buy and hold", n))
        # episodes: each stretch below the 200-day
        ep = (s != s.shift()).cumsum()[s]
        E = pd.DataFrame(dict(start=g[s].groupby(ep).apply(lambda x: x.index[0]), days=g[s].groupby(ep).size(),
                              gold=g[s].groupby(ep).apply(lambda x: (1 + x).prod() - 1), ndx=n[s].groupby(ep).apply(lambda x: (1 + x).prod() - 1)))
        big = E[E.days >= 20]
        print(f"   below-200 stretches: {len(E)} ({len(big)} of 20+ days); gold up in {(big.gold > 0).mean():.0%} of the long ones; "
              f"median gold {big.gold.median():+.1%}, median NDX {big.ndx.median():+.1%}")
        print("   long stretches (start, days, gold, NDX):")
        for r in big.sort_values("start").itertuples():
            print(f"      {r.start.date()}  {r.days:4d}d  gold {r.gold:+6.1%}  NDX {r.ndx:+6.1%}")
        yr = g.where(s, 0).groupby(g.index.year).apply(lambda x: (1 + x).prod() - 1)
        print("   rule by year:", "  ".join(f"{k}: {v:+.0%}" for k, v in yr.items()))
