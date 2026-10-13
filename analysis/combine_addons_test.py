"""Can today's findings improve the combine plan? (2026-10-13)

Combine plan: Vault Break 8 MNQ + Overnight Bias ADX30 RiskPerTrade $1,100 (MultiCharts trade lists). Candidates
added on top, all from MultiCharts trade lists with +1 tick per market / stop fill: the Bridge's Monday Long NQ
(new today, analysis/bridge_monday_confirm.py), our Monday Long, Late-Day Flow, Vol-Control Sell, Expiration Open
Short and NFP Fade (risk-sized like in the funded plan). Apex 50K challenge rules (portfolio.RULES: $3,000 target,
$2,000 trailing, $1,000 daily loss, 21 trading days), a challenge started on every trading day 2018-2026.
  python3 analysis/combine_addons_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths, challenge
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"

if __name__ == "__main__":
    g = pickle.load(open(SP + "g24.pkl", "rb")); atr = g.daily_atr(15)
    tr = g.trading; D = len(tr); yr = pd.DatetimeIndex(g.ts[tr]).year
    P = {}
    def add(nm, t):
        w, r = paths(g, t); P[nm] = (w[tr] / 10, r[tr] / 10)          # $ per MNQ
    add("VB", with_slippage(load_mc(g, REPORTS["VB"][0])))
    add("ONB30", with_slippage(load_mc(g, "Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx")))
    add("MON_BR", load_bridge_mc(g))
    for k in ("MON_MC", "LDF_MC", "VCS_MC", "EOS", "NFP_MC"):
        add(k, with_slippage(load_mc(g, REPORTS[k][0])))
    risk = lambda dollars, atr_mult: np.floor(dollars / (np.nan_to_num(atr_mult * atr[tr], nan=1e12) * 2))[:, None]
    q_onb = risk(1100, 0.25)

    def score(extra):
        W = P["VB"][0] * 8 + P["ONB30"][0] * q_onb; Rr = P["VB"][1] * 8 + P["ONB30"][1] * q_onb
        for nm, size in extra.items():
            q = risk(size[1], REPORTS[nm][1]) if isinstance(size, tuple) else size
            W = W + P[nm][0] * q; Rr = Rr + P[nm][1] * q
        res = [challenge(W, Rr, np.arange(s, min(s + 21, D))) for s in range(D)]
        ok = np.array([x is not None for x in res])
        o = np.array([np.nan if x is None else float(x[0] == "pass") for x in res])
        days = np.array([np.nan if x is None or x[0] != "pass" else x[1] for x in res])
        fm = np.array([np.nan if x is None else float(x[0] == "fail_mll") for x in res])
        m18, m23 = ok & (yr >= 2018), ok & (yr >= 2023)
        return (np.nanmean(o[m18]), np.nanmean(o[m23]), np.nanmedian(days[m18]), np.nanmean(fm[m18]),
                pd.Series(o[m18]).groupby(yr[m18]).mean().min())

    print(__doc__.split("\n")[0])
    print(f"{'plan':<44} pass 2018-26 | 2023-26 | median days to pass | blown (trailing DD) | worst year")
    rows = [("current: VB 8 + ONB ADX30 $1,100", {})]
    for k in (1, 2, 3, 4, 6): rows.append((f"+ Bridge Monday Long {k} MNQ", {"MON_BR": k}))
    for k in (1, 2, 4): rows.append((f"+ our Monday Long {k} MNQ", {"MON_MC": k}))
    rows.append(("+ both Mondays 2 + 2 MNQ", {"MON_BR": 2, "MON_MC": 2}))
    for k in (2, 4): rows.append((f"+ Late-Day Flow {k} MNQ", {"LDF_MC": k}))
    for k in (1, 2): rows.append((f"+ Vol-Control Sell {k} MNQ", {"VCS_MC": k}))
    for k in (500, 1000): rows.append((f"+ EOS ${k}", {"EOS": ("risk", k)}))
    for k in (500, 1000): rows.append((f"+ NFP Fade ${k}", {"NFP_MC": ("risk", k)}))
    rows += [("+ Bridge Monday 2 + EOS $500", {"MON_BR": 2, "EOS": ("risk", 500)}),
             ("+ Bridge Monday 2 + EOS $500 + VCS 2", {"MON_BR": 2, "EOS": ("risk", 500), "VCS_MC": 2}),
             ("+ Bridge Monday 2 + VCS 2", {"MON_BR": 2, "VCS_MC": 2}),
             ("+ Bridge Monday 2 + EOS $500 + VCS 2 + LDF 2", {"MON_BR": 2, "EOS": ("risk", 500), "VCS_MC": 2, "LDF_MC": 2})]
    for nm, ex in rows:
        a, b, dd, fm, wy = score(ex)
        print(f"{nm:<44} {a:6.1%}      | {b:6.1%}  | {dd:5.0f}              | {fm:6.1%}              | {wy:.1%}")
