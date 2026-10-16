"""Ramp speed: +2 vs +3 150K accounts a week (user, 2026-10-16), on the agreed plan (#1-#2 50K at 0 / +6, #3 150K at +11;
50K slots switch to 150K after their first funded account). Copy of analysis/ramp150_test.py with other schedules.
Original docstring: Ramp to 20 accounts with 150K No-Activation accounts (user, 2026-10-16). Real Apex prices / rules (analysis/apex_paths_test.py):
50K EOD single $59 + $130 activation on a pass; 150K No-Activation $249, no activation. Slot = one account at a time
(evaluation -> PA -> next evaluation). Schedules (trading days from the first account, 2026-10-12):
  A  the plan: 3 x 50K at 0 / +6 / +11 (they keep cycling as 50K), then after the 2-month gate +2 x 150K a week to 20
  B  as A, but each 50K slot switches to 150K after its first funded account finishes or blows
  C  all 20 slots 150K (first 3 at 0 / +6 / +11, the rest +2 a week from day 42), for reference
  D  the 50K-only ramp (same timing, all 50K), for comparison with analysis/ramp_to_20_test.py
150K: evaluation = combine set x 2.5, funded = plan x 1.5 with full size from a $3,000 cushion; 50K: current settings.
Every 10th start day 2018-01 .. 2023-09, 3 years, real day order; cash = payouts - fees. Also at 75% of the edge.
Reported: median cash at 3 / 6 / 12 / 24 / 36 months, 10th percentile at 12 / 36, worst cash (10th pct), median months
until cumulative cash reaches $100k (the personal account's full 1-NQ size).
  python3 analysis/ramp150_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import account_pipeline_test as A50, account_pipeline150 as A150
from plan_150k_test import evaluation, R150, R50, ONB30
from ramp_to_20_test import haircut

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
H = 756; MONTHS = (3, 6, 12, 24, 36)
FIRST3 = [0, 6, 11]; LATER = [42 + 5 * (i // 2) for i in range(17)]


def slot_mixed(t0, tend, sizes, switch_after_first):
    """Cash flows of one slot; sizes: dict name -> (chal, PA, eval, act). Starts as 'first'; switches to '150' after its first
    funded account ends if switch_after_first."""
    flow = {}; t = t0; cur = sizes["first"]; done_one = False
    while t < tend:
        chal, PA, ev, act = cur
        r = chal[t]
        if r is None: break
        flow[t] = flow.get(t, 0.0) - ev; out, k = r; t += k
        if out != "pass" or t >= tend: continue
        flow[t] = flow.get(t, 0.0) - act
        pday, pamt, n, e, blown = PA(t, tend - t)
        for i in range(n):
            if pday[i] < tend: flow[int(pday[i])] = flow.get(int(pday[i]), 0.0) + pamt[i]
        t += e
        if switch_after_first and not done_one: cur = sizes["150"]; done_one = True
    return flow


if __name__ == "__main__":
    pd.set_option("display.width", 240)
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; atr = g.daily_atr(15); tr = lab.tr; D = len(tr); dates = pd.DatetimeIndex(g.ts[tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    PLAN = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    P150 = {n: (("risk", v[1] * 1.5) if isinstance(v, tuple) else v * 1.5) for n, v in PLAN.items()}
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r_ = paths(g, t); P[nm] = (w[tr] / 10, r_[tr] / 10)
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": rk(1100, 0.25), "MON_BR": 2.0, "EOS": rk(500, REPORTS["EOS"][1])}
    s_lo, s_hi = int(np.argmax(dates >= "2018-01-01")), int(np.argmax(dates >= "2023-09-01")); starts = list(range(s_lo, min(s_hi, D - H - 60), 10))
    for alpha in (0.0, 0.25):
        Wc = np.zeros_like(P["VB"][0]); Rc = np.zeros_like(P["VB"][1])
        for k in P:
            cl = P[k][1][:, -1]; wh, ch = haircut(P[k][0], cl, alpha); rh = P[k][1] - (cl - ch)[:, None]
            Wc = Wc + wh * q[k]; Rc = Rc + rh * q[k]
        sizes = {}
        for nm, mod, rules, ck, plan, ref, ev, act in (("50", A50, R50, 1.0, PLAN, 1500.0, 59.0, 130.0), ("150", A150, R150, 2.5, P150, 3000.0, 249.0, 0.0)):
            chal = [evaluation(Wc * ck, Rc * ck, s, D, rules) for s in range(D)]
            names, b = lab._base(plan)
            Wf = np.stack([lab.W[k] for k in names]); Cf = np.stack([lab.C[k] for k in names]); b = np.ascontiguousarray(b)
            for i in range(Wf.shape[0]): Wf[i], Cf[i] = haircut(Wf[i], Cf[i], alpha)
            cache = {}
            def PA(s, h, mod=mod, Wf=Wf, Cf=Cf, b=b, ref=ref, cache=cache):
                if (s, h) not in cache: cache[(s, h)] = mod.pa_timeline(Wf, Cf, b, s, h, 0.5, 1.0, ref)
                return cache[(s, h)]
            sizes[nm] = (chal, PA, ev, act)
            print(f"   {'edge 100%' if alpha == 0 else 'edge 75%'} {nm}K evaluation pass {np.mean([c[0] == 'pass' for c in chal if c is not None]):.1%}", flush=True)
        L2 = [42 + 5 * (i // 2) for i in range(17)]; L3 = [42 + 5 * (i // 3) for i in range(17)]
        base3 = [(0, "50", True), (6, "50", True), (11, "150", False)]
        SCHED = {"+2 x 150K a week to 20 (agreed plan)": base3 + [(o, "150", False) for o in L2],
                 "+3 x 150K a week to 20": base3 + [(o, "150", False) for o in L3]}
        print(f"\n=== {'backtest edge' if alpha == 0 else '75% of the edge'}")
        print(f"{'schedule':<52}" + "".join(f"{f'{m}m':>10}" for m in MONTHS) + f"{'12m p10':>10}{'36m p10':>11}{'worst p10':>11}{'months to $100k':>17}")
        for nm, offs in SCHED.items():
            rows = []
            for s0 in starts:
                cash = np.zeros(H + 1)
                for off, sz, sw in offs:
                    fl = slot_mixed(s0 + off, s0 + H, {"first": sizes[sz], "150": sizes["150"]}, sw)
                    for d, v in fl.items(): cash[d - s0] += v
                cum = np.cumsum(cash); hit = np.argmax(cum >= 100_000) / 21 if (cum >= 100_000).any() else np.inf
                rows.append({**{f"m{m}": cum[min(H, m * 21)] for m in MONTHS}, "worst": cum.min(), "hit": hit})
            df = pd.DataFrame(rows); mh = np.median(df.hit)
            print(f"{nm:<52}" + "".join(f"{'$' + format(df[f'm{m}'].median() / 1000, ',.0f') + 'k':>10}" for m in MONTHS)
                  + f"{'$' + format(df.m12.quantile(0.1) / 1000, ',.0f') + 'k':>10}{'$' + format(df.m36.quantile(0.1) / 1000, ',.0f') + 'k':>11}"
                  + f"{'$' + format(df.worst.quantile(0.1) / 1000, ',.1f') + 'k':>11}{('>36' if not np.isfinite(mh) else f'{mh:.1f}'):>17}", flush=True)
