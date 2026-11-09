"""Evaluation-profile screen of the whole catalog (user 2026-11-09). Information only. Template from Twin cap1, the one add-on that helps
the 150K evaluation: (1) daily Sharpe >= 1.5, (2) $ a day >= $15 at the size where its 1-in-100 intraday day loses $500, (3) active on
>= 30% of trading days, (4) flat or better on VB / ONB big-loss days (mean >= -0.1 x its daily sd). 2018-26. Series with intraday paths
(the evaluation-set builder's 14 pieces + funded-lab pieces) give an exact worst intraday day; daily-only series (personal book columns,
trade-list nets) use the day's close as the worst (flagged 'approx': understates intraday risk). Apex-legal flag: flat within one Apex
trading day (multi-day holds marked no).
  tools/run_stamped.sh analysis/eval_profile_screen.py > analysis/outputs/eval_profile_screen_output.txt
"""
import sys, io, pickle, runpy, contextlib, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    src = open("analysis/eval_set_builder.py").read(); head, main = src.split('if __name__ == "__main__":')
    ns = {}; exec(head, ns); body = main.split("    names = list(U); yr = dts.year")[0]
    with contextlib.redirect_stdout(io.StringIO()):
        exec("def _m():\n" + body + "\n    return locals()\n", ns); L = ns["_m"]()
    U, RISK, dts, lab = L["U"], L["RISK"], L["dts"], L["lab"]; m = dts.year >= 2018
    unit = lambda nm: (np.floor(250.0 / (RISK[nm] * 2.0))[:, None] if nm in RISK else 1.0)
    S = {}                                                       # name -> (daily close per unit, daily worst per unit, exact?, apex legal?)
    for nm in U: W_, R_ = U[nm][0] * unit(nm), U[nm][1] * unit(nm); S[nm] = (R_[:, -1], W_.min(axis=1), True, True)
    ld = pd.DatetimeIndex(lab.g.ts[lab.tr]); pos = pd.Series(np.arange(len(dts)), index=dts)
    for k in ("OND_MC", "VCS_MC", "LDF_MC_L", "LDF_MC_S", "ONB_ML2_L", "ONB_ML2_S"):
        S["lab " + k] = (pd.Series(lab.C[k], index=ld).reindex(dts, fill_value=0).values, pd.Series(lab.W[k].min(axis=1), index=ld).reindex(dts, fill_value=0).values, True, k != "OND_MC" or True)
    Pp = pd.read_pickle("scratch_data/personal_P.pkl")
    multi = {"S30", "Kusho", "SwingTarget": False}
    for c in Pp.columns:
        if c in ("VaultBreak", "OvernightBiasML", "MondayLong", "ExpirationOpenShort", "LateDayFlow", "NFPFade", "BridgeMondayLong", "TwinContinuation", "DualThrust",
                 "RelativeStrength", "OvernightTick", "CLSundayFade_perMCL", "ESMOCFollow_perMES"): continue      # already above with intraday paths
        x = Pp[c].reindex(dts, fill_value=0).values; S["personal " + c + " (approx)"] = (x, np.minimum(x, 0), False, c not in ("S30", "Kusho"))
    def dm(d, net): return pd.Series(np.asarray(net, float) / 10, index=pd.DatetimeIndex(d)).groupby(level=0).sum().reindex(dts, fill_value=0).values
    for nm, (f, col, side, legal) in {"FINRA longs": ("checks/candidates/finra_longs/mc_trades.csv", "net_rc", None, True), "LETF fade": ("checks/candidates/letf_fade/trades.csv", "net", None, True),
                                      "FVB shorts": ("checks/candidates/fvb/trades.csv", "net", -1, True), "T_ONESIDE": ("checks/candidates/t_oneside/mc_trades_T_ONESIDE_v2.csv", "net", None, True),
                                      "noise-area longs": ("analysis/outputs/bridge_noise_15m_trades_rth.csv", "net", 1, True), "S03 v2 longs": ("checks/candidates/s03_v2/codex_v2_apex_trades.csv", "gross_nq", 1, True),
                                      "Ricochet T80": ("checks/candidates/ricochet_1144/python_trades_t80.csv", "net", None, True), "S30 NQ IBS<0.10": (None, None, None, False)}.items():
        try:
            if f is None: continue
            t = pd.read_csv(f, parse_dates=["date"]); t = t[t.side == side] if side else t
            v = t[col] - (17.25 if col == "gross_nq" else 0); x = dm(t.date, v); S[nm + " (approx)"] = (x, np.minimum(x, 0), False, legal)
        except Exception as e: print(f"   skipped {nm}: {e.__class__.__name__}")
    VB = U["VB"][0] * unit("VB") * 20; ON = U["ONB30"][0] * unit("ONB30") * 11
    big = (VB.min(axis=1) <= -1500) | (ON.min(axis=1) <= -1500)
    rows = []
    for nm, (c, w, exact, legal) in S.items():
        c, w = np.asarray(c, float)[m], np.asarray(w, float)[m]; act = (c != 0).mean()
        if act < 0.01 or c.std() == 0: continue
        p1 = np.percentile(w[w < 0], 1) if (w < 0).any() else -1.0; size = 500.0 / max(1e-9, -p1)
        sh = c.mean() / c.std() * np.sqrt(252); day = c.mean() * size; bad = c[big[m]].mean() / c.std()
        ok = [sh >= 1.5, day >= 15, act >= 0.30, bad >= -0.1]
        rows.append((nm, round(sh, 2), round(day, 1), round(act, 2), round(bad, 2), round(size, 2), sum(ok), "".join("Y" if o else "." for o in ok), "exact" if exact else "approx", "yes" if legal else "NO"))
    R = pd.DataFrame(rows, columns=["piece", "Sharpe", "$/day @p1=$500", "active", "bad-day/sd", "units @p1=$500", "passes", "S$AB", "paths", "Apex"])
    pd.set_option("display.width", 220); print(R.sort_values(["passes", "Sharpe"], ascending=False).to_string(index=False))
    print(f"\n   VB / ONB big-loss days (either <= -$1,500 at plan size): {int(big[m].sum())}. Columns S$AB = Sharpe / $ a day / active / bad days.")
