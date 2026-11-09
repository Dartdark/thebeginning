"""Which strategies gain on Vault Break / ONB stop days? (user 2026-11-09: 'find a new strategy that gains on VB and ONB stop days').
Information only (a screen, no selection). Stop days = days a VB (MultiCharts VB v1) or ONB ADX30 (MultiCharts) trade exited at its stop,
2018-26. For every daily P&L series in the repo (personal book columns per micro, funded lab pieces per MNQ, and today's trade lists):
average $ per micro on VB stop days, ONB stop days, both, and all other days; the stop-day minus other-day difference and its t; daily
correlation with VB + ONB. Also the features of stop days known before the open (gap, prior range / ATR, VIX regime, weekday).
  tools/run_stamped.sh analysis/stopday_screen.py > analysis/outputs/stopday_screen_output.txt
"""
import sys, io, pickle, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc
from build_lab import REPORTS
from combine_levers_test import ONB30
from grid24 import jof

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); ts = pd.DatetimeIndex(g.ts); trr = g.trading; dts = pd.DatetimeIndex(ts[trr]); dts = dts[dts >= "2018-01-01"]
    sd = {}
    for nm, f in (("VB", REPORTS["VB"][0]), ("ONB", ONB30)):
        t = load_mc(g, f); t["date"] = ts[t.day.values]; sd[nm] = set(t[(t.kind == 0) & (t.date >= "2018-01-01")].date)
    vb, onb = pd.Series(dts.isin(list(sd["VB"])), index=dts), pd.Series(dts.isin(list(sd["ONB"])), index=dts); anyd = vb | onb
    print(f"   days {len(dts)}; VB stop days {vb.sum()}, ONB stop days {onb.sum()}, both {(vb & onb).sum()}, either {anyd.sum()}")
    S = {}
    Pp = pd.read_pickle("scratch_data/personal_P.pkl")
    for c in Pp.columns: S["personal: " + c] = Pp[c]
    sys.argv = ["x", "scratch_data"]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    ld = pd.DatetimeIndex(lab.g.ts[lab.tr])
    for k in ("OND_MC", "VCS_MC", "NFP_MC", "LDF_MC_S", "LDF_MC_L", "ONB_ML2_S", "ONB_ML2_L"): S["lab: " + k] = pd.Series(lab.C[k], index=ld)
    def dm(d, net): return pd.Series(np.asarray(net, float) / 10, index=pd.DatetimeIndex(d)).groupby(level=0).sum()
    extra = {"FINRA longs": ("checks/candidates/finra_longs/mc_trades.csv", "net_rc", None), "LETF fade": ("checks/candidates/letf_fade/trades.csv", "net", None),
             "FVB shorts": ("checks/candidates/fvb/trades.csv", "net", -1), "T_ONESIDE (MC)": ("checks/candidates/t_oneside/mc_trades_T_ONESIDE_v2.csv", "net", None),
             "Swing Target shorts (MC)": ("checks/candidates/swing_target/mc_trades_v3.csv", "net", -1), "EOS late (14:55)": ("checks/candidates/eos_late/trades.csv", "net", None),
             "MO on ES": ("checks/candidates/mo_es/trades.csv", "net", None), "X1 late relative flow": ("checks/candidates/x1_late_relflow/trades.csv", "net", None),
             "noise-area shorts? (Bridge both)": ("analysis/outputs/bridge_noise_15m_trades_rth.csv", "net", -1)}
    for nm, (f, col, side) in extra.items():
        try:
            t = pd.read_csv(f, parse_dates=["date"]); t = t[t.side == side] if side else t; S[nm] = dm(t.date, t[col])
        except Exception as e: print(f"   (skipped {nm}: {e.__class__.__name__})")
    base = (S["personal: VaultBreak"].reindex(dts, fill_value=0) + S["personal: OvernightBiasML"].reindex(dts, fill_value=0))
    rows = []
    for nm, s in S.items():
        x = s.reindex(dts, fill_value=0.0); act = (x != 0).mean()
        if act < 0.02: continue
        a, b = x[anyd], x[~anyd]; dif = a.mean() - b.mean(); se = np.sqrt(a.var() / len(a) + b.var() / len(b))
        rows.append((nm, x[vb].mean(), x[onb].mean(), x[vb & onb].mean(), a.mean(), b.mean(), dif, dif / se if se else np.nan, x.corr(base), act))
    R = pd.DataFrame(rows, columns=["series", "VB_stop", "ONB_stop", "both", "either", "other", "diff", "t_diff", "corr_VB+ONB", "active"]).sort_values("either", ascending=False)
    pd.set_option("display.width", 250); print("\n   $ per micro a day (sorted by the stop-day average):"); print(R.round(2).to_string(index=False))
    # features of stop days known before the open
    o, pc = g.o[trr, jof(831)], np.r_[np.nan, g.c[trr, jof(1500)][:-1]]; F = pd.DataFrame({"gap": (o - pc), "atr": g.daily_atr(15)[trr]}, index=pd.DatetimeIndex(ts[trr])).reindex(dts)
    rng_prev = pd.Series(np.nanmax(g.h[trr, jof(831):jof(1500) + 1], 1) - np.nanmin(g.l[trr, jof(831):jof(1500) + 1], 1), index=pd.DatetimeIndex(ts[trr])).shift(1).reindex(dts)
    vix = pd.read_csv("data/VIX_daily.csv", parse_dates=["DATE"]).set_index("DATE").CLOSE.sort_index(); hi = (vix > vix.rolling(25).mean()).shift(1).reindex(dts).fillna(False)
    F["gapA"] = F.gap / F.atr; F["prevR"] = rng_prev / F.atr; F["hivix"] = hi; F["dow"] = dts.dayofweek
    for nm, m in (("VB stop days", vb), ("ONB stop days", onb), ("other days", ~anyd)):
        f = F[m]; print(f"   {nm:<14} |gap| / ATR {f.gapA.abs().median():.2f}, gap up {np.mean(f.gapA > 0):.0%}, prior range / ATR {f.prevR.median():.2f}, VIX above SMA25 {f.hivix.mean():.0%}, weekday {f.dow.value_counts(normalize=True).sort_index().round(2).to_dict()}")
