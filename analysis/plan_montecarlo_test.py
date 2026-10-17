"""Monte Carlo on every strategy of the funded plan at plan size, and on the plan as a whole (2026-10-17; NEW_CHAT_BRIEF
'Next ideas': run Monte Carlo on every strategy in the plan at plan size).

Plan (funded_strategies/README.md): VB 3 MNQ (1 on single-print flagged days), ONB ML v2 risk $400, Monday Long 1, EOS risk
$700, Late-Day Flow 2, NFP Fade risk $500, Bridge Monday Long 1, CL Sunday fade 2 MCL. Full size (f = 1: whole MNQ per day as
the bench's lab._base, floored), i.e. the size from a $1,500 cushion; below that cushion the account trades half size, so
these are the worst-case (largest) paths. Daily P&L = the bench's per-day close (MultiCharts lists, $7.25 + 1 tick a fill);
trades = days with a position (one trade a day per strategy).
For each: standard metrics (analysis/metrics.py), Monte Carlo (analysis/montecarlo.py: trade reshuffle + 252-day block
bootstrap with the $2,000 EOD trailing hit probability), all years and 2023 onward.
Then the whole plan: the same at full size, plus a check that the bench reproduces ($10,184 / $12,450, blown 3% / 3%).
  python3 analysis/plan_montecarlo_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
PLAN = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2,
        "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
GROUPS = {"Vault Break (3 / 1 flagged)": ["VB_N", "VB_F"], "Overnight Bias ML v2 ($400)": ["ONB_ML2_MC"],
          "Monday Long (1)": ["MON_MC"], "Expiration Open Short ($700)": ["EOS"], "Late-Day Flow (2)": ["LDF_MC"],
          "NFP Fade ($500)": ["NFP_MC"], "Bridge Monday Long (1)": ["MON_BR_MC"], "CL Sunday fade (2 MCL)": ["CLS"]}

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    argv = sys.argv; sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    sys.argv = argv
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag

    a, c = lab.score(PLAN, 250, fmin=0.5, fmax=1.0, ref=1500.0), lab.score(PLAN, 500, fmin=0.5, fmax=1.0, ref=1500.0)
    print(f"bench check: 1y ${a['expected']:,.0f} blown {a['blown']:.0%} | 2y ${c['expected']:,.0f} blown {c['blown']:.0%} "
          f"(documented $10,184 / $12,450, blown 3% / 3%)")

    names, b = lab._base(PLAN); q = {k: np.floor(b[i] + 1e-9) for i, k in enumerate(names)}
    keep = dates >= "2018-01-01"; d23 = dates[keep] >= "2023-01-01"
    daily = {nm: pd.Series(sum(q[k] * lab.C[k] for k in ks), index=dates)[keep] for nm, ks in GROUPS.items()}
    daily["WHOLE PLAN (full size)"] = sum(daily.values())
    # one row per strategy-day with a position (trades); the plan's 'trades' = its active days
    def trades(nm):
        ks = GROUPS.get(nm, [k for v in GROUPS.values() for k in v])
        act = pd.Series(np.any([lab.W[k].min(1) != 0 for k in ks] + [lab.C[k] != 0 for k in ks], axis=0), index=dates)[keep]
        return daily[nm][act]
    rows, rows23 = {}, {}
    for nm, dl in daily.items():
        t = trades(nm); rows[nm] = (dl, t); rows23[nm] = (dl[d23], t[t.index >= "2023-01-01"])
    print("\nStandard metrics at plan size, 2018-26 ($ per account per day / trade):"); print(M.table(rows))
    print("\n2023 onward:"); print(M.table(rows23))
    print("\nMonte Carlo at plan size (trade reshuffle 10,000 x; 252-day block bootstrap, 10-day blocks, $2,000 EOD trailing from 0, "
          "locks at +$100):")
    summ = []
    for nm, dl in daily.items():
        t = trades(nm)
        print(MC.report(t.to_numpy(), dl.to_numpy(), size=1, label=nm))
        print(MC.report(t[t.index >= "2023-01-01"].to_numpy(), dl[d23].to_numpy(), size=1, label=nm + ", 2023+"))
        tm, dm = MC.trade_mc(t.to_numpy()), MC.daily_mc(dl.to_numpy())
        dm23 = MC.daily_mc(dl[d23].to_numpy())
        summ.append(dict(strategy=nm, trades=len(t), dd_actual=tm["dd_actual"], dd_p95=tm["dd_p95"], dd_p99=tm["dd_p99"],
                         p_dd2000=tm["p_dd_2000"], yr_p5=dm["pnl_p5"], yr_p50=dm["pnl_p50"], p_losing_yr=dm["p_loss"],
                         p_trail=dm["p_trail_hit"], p_losing_yr_23=dm23["p_loss"], p_trail_23=dm23["p_trail_hit"]))
    df = pd.DataFrame(summ).set_index("strategy")
    fm = {c: "${:,.0f}".format for c in ("dd_actual", "dd_p95", "dd_p99", "yr_p5", "yr_p50")}
    fm.update({c: "{:.1%}".format for c in ("p_dd2000", "p_losing_yr", "p_trail", "p_losing_yr_23", "p_trail_23")})
    print("\nSummary (dd = max drawdown over the full trade list reshuffled; yr = one 252-day year; p_trail = P(hit $2,000 EOD trailing in a year)):")
    print(df.to_string(formatters=fm))

    # longs and shorts separately for the two-sided strategies (CLAUDE.md), at the same plan size as the whole strategy
    import resampling as R
    print("\nLongs / shorts separately (same daily size as the strategy):")
    side = {}
    for nm, k, kl, ks in (("Overnight Bias ML v2", "ONB_ML2_MC", "ONB_ML2_L", "ONB_ML2_S"), ("Late-Day Flow", "LDF_MC", "LDF_MC_L", "LDF_MC_S")):
        for sd, kk in (("longs", kl), ("shorts", ks)):
            dl = pd.Series(q[k] * lab.C[kk], index=dates)[keep]; t = dl[pd.Series(lab.C[kk] != 0, index=dates)[keep]]
            side[f"{nm} {sd}"] = (dl, t)
            print(MC.report(t.to_numpy(), dl.to_numpy(), size=1, label=f"{nm} {sd}"))
    print(M.table(side))
    print("\nBootstrap intervals and drawdown permutation, 2023 onward:")
    b_, p_ = R.report({nm: dl[d23] for nm, dl in daily.items()}, n=3000); print(b_); print(p_)
