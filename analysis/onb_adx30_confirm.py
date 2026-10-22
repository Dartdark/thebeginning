"""MultiCharts confirmation of Overnight Bias ADX30 / 0.25 ATR for the combine (2026-10-13).
Report '... 15 Minutes NQ Overnight Bias.xlsx' (inputs ADXMin 30, StopAtrPct 0.25), compared trade by trade
with the Python version, standard metrics (whole / longs / shorts), bootstrap + permutation on 2023+,
and the challenge simulator (VB 8 MNQ + ONB RiskPerTrade 1100, 21 trading days, real day order) with the
MultiCharts lists of both versions (ADX 20: 'mc_reports/Backtesting Strategy Performance Report ONB v2.xlsx').
  python3 analysis/onb_adx30_confirm.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths, challenge
from funded_lab import with_slippage
from candidates24 import overnight_bias24
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
NEW = "mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx"
OLD = "mc_reports/Backtesting Strategy Performance Report ONB v2.xlsx"
VBF = "mc_reports/Backtesting Strategy Performance Report VB v1.xlsx"
pf = lambda s: s[s > 0].sum() / max(1e-9, -s[s < 0].sum())


def net(t):
    return (t.exit - t.entry) * t.side * 20 - 7.25 - 5 * (1 + (t.kind != 1))


if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15)
    tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year
    mc = {k: load_mc(g, f) for k, f in (("ADX30", NEW), ("ADX20", OLD))}
    for k, t in mc.items():
        t["date"] = pd.DatetimeIndex(g.ts[t.day.values]); t["net"] = net(t)
    print(__doc__.split("\n")[0])
    py = overnight_bias24(g, adx_min=30, stop_atr=0.25)
    py["net"] = py.net - 5 * (1 + (py.kind != 1))
    for k, t in mc.items():
        x = t.net; y = t.date.dt.year
        print(f"\nMultiCharts {k}: n={len(t)} win {np.mean(x > 0):.0%} avg ${x.mean():.0f} PF {pf(x):.2f}"
              f" t={x.mean() / x.std() * np.sqrt(len(x)):.1f} | longs n={(t.side > 0).sum()} ${x[t.side > 0].mean():.0f}"
              f" PF {pf(x[t.side > 0]):.2f} | shorts n={(t.side < 0).sum()} ${x[t.side < 0].mean():.0f} PF {pf(x[t.side < 0]):.2f}")
        print("   by year:", x.groupby(y).sum().round(0).astype(int).to_dict(), "| years +", int((x.groupby(y).sum() > 0).sum()))
    t = mc["ADX30"]
    mm = py[["day", "side", "entry", "net"]].merge(t[["day", "side", "entry", "net"]], on="day", how="outer",
                                                  suffixes=("_py", "_mc"), indicator=True)
    b = mm[mm._merge == "both"]
    print(f"\nMatch with Python ADX30 ({len(py)} trades): {mm._merge.value_counts().to_dict()}; common days same side"
          f" {np.mean(b.side_py == b.side_mc):.1%}, entry within 1 tick {np.mean(abs(b.entry_py - b.entry_mc) <= 0.26):.1%},"
          f" P&L corr {np.corrcoef(b.net_py, b.net_mc)[0, 1]:.3f}, Python ${b.net_py.mean():.0f} vs MC ${b.net_mc.mean():.0f}")
    for lab_, side in (("only in Python", "left_only"), ("only in MultiCharts", "right_only")):
        r = mm[mm._merge == side]
        if len(r): print(f"   {lab_} ({len(r)}):", ", ".join(str(pd.Timestamp(g.ts[int(d)]).date()) for d in r.day[:12]))

    days = pd.DatetimeIndex(g.ts[tr]); days = days[days.year >= 2018]; D2 = days[days.year >= 2023]
    dl = lambda q, ix: q.groupby(q.date).net.sum().reindex(ix, fill_value=0.0)
    rows = {}
    for k, q in mc.items():
        q = q[q.date.dt.year >= 2018]
        for s_, nm in ((0, "all"), (1, "longs"), (-1, "shorts")):
            qq = q if s_ == 0 else q[q.side == s_]
            rows[f"{k} {nm} 2018-26"] = (dl(qq, days), qq.net)
            h = qq[qq.date.dt.year >= 2023]; rows[f"{k} {nm} 2023-26"] = (dl(h, D2), h.net)
    print("\nStandard metrics per NQ (MultiCharts trades, +1 tick per fill):"); print(M.table(rows))
    Bt, Pm = R.report({f"ADX30 {nm} 2023-26": dl((t if s_ == 0 else t[t.side == s_])[lambda z: z.date.dt.year >= 2023], D2)
                       for s_, nm in ((0, "all"), (1, "longs"), (-1, "shorts"))}, n=5000)
    print("\nBootstrap 2023-26:"); print(Bt); print("\nPermutation 2023-26:"); print(Pm)

    print("\nChallenge (VB 8 MNQ + ONB RiskPerTrade 1100, 21 trading days, every start day, with slippage):")
    vb = load_mc(g, VBF); w, r = paths(g, with_slippage(vb)); VBw, VBc = w[tr] / 10, r[tr] / 10
    for k, sa in (("ADX20", 0.30), ("ADX30", 0.25)):
        w, r = paths(g, with_slippage(mc[k])); Ow, Oc = w[tr] / 10, r[tr] / 10
        q = np.floor(1100 / (sa * np.nan_to_num(atr[tr], nan=1e12) * 2))[:, None]
        for nm, (W, Rr) in (("VB 8 + ONB $1,100", (VBw * 8 + Ow * q, VBc * 8 + Oc * q)), ("ONB $1,100 alone", (Ow * q, Oc * q))):
            res = [challenge(W, Rr, np.arange(s, min(s + 21, D))) for s in range(D)]
            o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
            dd = np.array([np.nan if x is None or x[0] != "pass" else x[1] for x in res])
            print(f"   {k} {nm:<20} pass {np.nanmean(o):.1%} | 2018-22 {np.nanmean(o[yr < 2023]):.1%} | 2023-26 {np.nanmean(o[yr >= 2023]):.1%}"
                  f" | worst start year {pd.Series(o[yr >= 2018]).groupby(yr[yr >= 2018]).mean().min():.1%} | median days {np.nanmedian(dd):.0f}")
