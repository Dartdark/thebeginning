"""CoT reversal index (Dreesmann, Herberger & Charifzadeh 2023, 'The Commitment of Traders report as a trading signal?',
IJFMD 9(1/2); user's PDF 2026-10-15). Paper: Williams commercial index = (commercial net - its 26-week low) / (26-week high
- low); >= 0.7 'buying climax' -> long, <= 0.3 -> short, confirmed by a rising / falling 10-week moving average of the close
(plus non-commercial / non-reportable contrarian readings and a 30% commercial-OI check). 71 markets 1986-2020: long-only
beat the S&P's Sharpe 1.07 in 6 markets, mostly stock indices (5 of 10 index futures, Sharpe 1.24-2.09); as a portfolio it
underperformed. User's idea: use it on ES / NQ only, as a weekly gate on strategies we already run.
Here, CFTC Legacy futures-only reports (data/cot/deacot*.zip), NQ 'NASDAQ MINI' 209742 and ES 'E-MINI S&P 500' 13874A,
2018-2026. A report (as of Tuesday) is used from the Monday after its Friday release. Pre-registered, the paper's numbers:
  index  commercial net, 26-week min-max (0..1); state LONG if index >= 0.7 and the 10-week MA of weekly closes is rising,
         SHORT if <= 0.3 and the MA is falling, else NEUTRAL. Also shown: index alone (no MA)
  A  standalone, the weekly state traded as an Apex day trade (8:30 -> 15:00 CT every day in the state), 1 contract, NQ and
     ES, vs placebo (same days, random side) and vs 'long every day'
  B  the user's gate on the plan's NQ trades: agree (long in LONG / short in SHORT), against, neutral -- per strategy, and
     the gate 'keep only agreeing trades' vs all trades
  python3 analysis/cot_reversal_index_test.py [SCRATCH_DIR]
"""
import sys, pickle, zipfile, glob, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from portfolio import load_mc
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
MK = {"NQ": ("209742", 20.0, 0.25, 7.25), "ES": ("13874A", 50.0, 0.25, 5.0)}


def legacy(code):
    out = []
    for f in sorted(glob.glob("data/cot/deacot*.zip")):
        z = zipfile.ZipFile(f); d = pd.read_csv(z.open(z.namelist()[0]), low_memory=False)
        d = d[d["CFTC Contract Market Code"].astype(str).str.strip() == code]
        out.append(pd.DataFrame({"asof": pd.to_datetime(d["As of Date in Form YYYY-MM-DD"]),
                                 "com": d["Commercial Positions-Long (All)"] - d["Commercial Positions-Short (All)"],
                                 "oi": d["Open Interest (All)"]}))
    c = pd.concat(out).drop_duplicates("asof").sort_values("asof").set_index("asof")
    lo, hi = c.com.rolling(26).min(), c.com.rolling(26).max()
    c["idx"] = (c.com - lo) / (hi - lo)
    return c


def states(g, c, use_ma=True):
    """Daily state (+1 / -1 / 0) per trading day, from the last report usable before that day."""
    tr = g.trading; ts = pd.DatetimeIndex(g.ts[tr])
    cf = pd.DataFrame(g.c[tr, :jof(1500) + 1]).ffill(axis=1).iloc[:, -1]
    cl = pd.Series(cf.to_numpy(), index=ts).dropna()
    wk = cl.resample("W-FRI").last().dropna(); ma = wk.rolling(10).mean()
    rows = []
    for asof, r in c.iterrows():
        use_from = asof + pd.Timedelta(days=6)                        # Tuesday -> following Monday
        m = ma[ma.index <= asof + pd.Timedelta(days=3)]               # weekly closes up to the release Friday
        if len(m) < 2 or np.isnan(r.idx): continue
        up, dn = m.iloc[-1] > m.iloc[-2], m.iloc[-1] < m.iloc[-2]
        s = 1 if (r.idx >= 0.7 and (up or not use_ma)) else (-1 if (r.idx <= 0.3 and (dn or not use_ma)) else 0)
        rows.append((use_from, s))
    S = pd.Series([s for _, s in rows], index=[d for d, _ in rows]).sort_index()
    return S.reindex(ts, method="ffill").fillna(0).astype(int)


def day_trades(g, st, sym, rand=None):
    _, pv, tick, comm = MK[sym]; tr = g.trading; ts = pd.DatetimeIndex(g.ts[tr])
    o, c = g.o[tr, jof(831)], g.c[tr, jof(1500)]
    rng = np.random.default_rng(rand) if rand is not None else None
    s = st.to_numpy().copy()
    if rng is not None: s = np.where(s != 0, rng.choice([-1, 1], len(s)), 0)
    net = ((c - o) * s - 2 * tick) * pv - comm
    ok = (s != 0) & ~np.isnan(o) & ~np.isnan(c) & (ts.year >= 2018)
    return pd.Series(net[ok], index=ts[ok]), s[ok]


def line(x, side=None, nm="", w=40):
    x = pd.Series(x); y = x.index.year; by = x.groupby(y).sum(); pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    t = x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
    s = (f"   {nm:<{w}} n={len(x):4d} avg ${x.mean():6.0f} PF {pf:4.2f} t {t:+4.1f} yrs+ {(by > 0).sum()}/{len(by)}"
         f" | 18-22 ${x[y < 2023].mean():6.0f} 23-26 ${x[y >= 2023].mean():6.0f}")
    if side is not None: s += f" | L ${x[side > 0].mean():5.0f} (n {np.sum(side > 0)}) S ${x[side < 0].mean():5.0f} (n {np.sum(side < 0)})"
    return s


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    G = {"NQ": pickle.load(open(SP + "g24.pkl", "rb")), "ES": pickle.load(open(SP + "ge.pkl", "rb"))}
    C = {s: legacy(MK[s][0]) for s in MK}
    ST = {}
    for s in MK:
        c = C[s]; c18 = c[c.index >= "2018-01-01"]
        print(f"\n{s}: {len(c)} reports {c.index.min().date()}..{c.index.max().date()}; index >= 0.7 {np.mean(c18.idx >= 0.7):.0%} of weeks, "
              f"<= 0.3 {np.mean(c18.idx <= 0.3):.0%}; commercial net corr with NQ/ES weekly close level n/a")
        for use_ma in (True, False):
            st = states(G[s], c, use_ma); ST[(s, use_ma)] = st
            st18 = st[st.index.year >= 2018]
            net, side = day_trades(G[s], st, s)
            print(f"  A. {'index + 10-week MA (paper)' if use_ma else 'index alone'}: days LONG {np.mean(st18 == 1):.0%}, SHORT {np.mean(st18 == -1):.0%}")
            print(line(net, side, f"{s} day trade in the state"))
            pl = [day_trades(G[s], st, s, rand=r)[0].mean() for r in range(50)]
            print(f"      placebo (same days, random side, 50 runs) avg ${np.mean(pl):.0f} (5-95% {np.percentile(pl, 5):.0f}..{np.percentile(pl, 95):.0f})")
        allong, _ = day_trades(G[s], pd.Series(1, index=ST[(s, True)].index), s)
        print(line(allong, None, f"{s} control: long every day"))
        if s == "NQ":
            x = net.groupby(net.index.year).sum()
    # standard metrics for the paper version, NQ
    net, side = day_trades(G["NQ"], ST[("NQ", True)], "NQ")
    print("\nStandard metrics, NQ paper version as a day trade (per NQ):")
    print(M.table({"all": (net, net), "longs": (net[side > 0], net[side > 0]), "shorts": (net[side < 0], net[side < 0])}))

    print("\nB. The plan's NQ trades by the CoT state at entry (NQ index; ES index in the second block). 'gate' = keep only agreeing trades")
    g = G["NQ"]; ts_tr = pd.DatetimeIndex(g.ts[g.trading])
    plans = {k: with_slippage(load_mc(g, f)) for k, (f, _) in REPORTS.items() if k in ("VB", "ONB_ML2_MC", "EOS", "MON_MC", "LDF_MC", "NFP_MC")}
    plans["MON_BR"] = load_bridge_mc(g)
    for src in ("NQ", "ES"):
        st = ST[(src, True)]; st_day = pd.Series(st.to_numpy(), index=st.index)
        print(f"\n  state from the {src} index (+ MA):")
        for nm, t in plans.items():
            t = t.copy(); dt = pd.DatetimeIndex(g.ts[t.day.to_numpy()]); t = t[dt.year >= 2018]; dt = dt[dt.year >= 2018]
            net = (t.exit - t.entry).to_numpy() * t.side.to_numpy() * 20.0 - 7.25
            s_ = st_day.reindex(dt.normalize(), method="ffill").fillna(0).to_numpy() * t.side.to_numpy()
            a, b, z = net[s_ > 0], net[s_ < 0], net[s_ == 0]
            dtt = (a.mean() - b.mean()) / np.sqrt(a.var() / max(len(a), 1) + b.var() / max(len(b), 1)) if len(a) > 2 and len(b) > 2 else np.nan
            print(f"   {nm:<11} all ${net.mean():5.0f} (n {len(net):4d}) | agree ${a.mean() if len(a) else np.nan:5.0f} (n {len(a):3d}) "
                  f"against ${b.mean() if len(b) else np.nan:5.0f} (n {len(b):3d}) neutral ${z.mean():5.0f} (n {len(z):4d}) | agree-vs-against t {dtt:+.1f}"
                  f" | gate keeps {len(a) / len(net):.0%} of trades, {a.sum() / net.sum():.0%} of P&L")
