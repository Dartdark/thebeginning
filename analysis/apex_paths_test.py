"""Which Apex path? (user, 2026-10-15, with Apex's prices and rules from the screenshots uploaded to the repo):
  50K EOD             eval $59 (5-pack $24.50 each) + activation $130   | target $3,000, $2,000 EOD DD, $1,000 DLL, 60 MNQ
  50K no-activation   eval $119 (5-pack $109 each), no activation        | same rules
  150K EOD            eval $219 (5-pack $199 each) + activation $150   | target $9,000, $4,000 EOD DD, $2,000 DLL, 120 MNQ
  150K no-activation  eval $249, no activation                          | same rules
  PA payouts: 50K 1,500 / 1,500 / 2,000 / 2,500 / 2,500 / 3,000 = $13,000; 150K 2,500 / 3,000 / 3,000 / 3,000 / 4,000 /
  5,000 = $20,500; 5 days >= $250 (150K $350), min balance to request $52,600 / $154,600, 50% consistency, then the PA closes.
One slot = one account at a time: evaluation (retry on a fail) -> PA -> next evaluation. 50K: combine set, funded plan
(cushion $1,500). 150K: combine set x 2.5, funded plan x 1.5 (cushion $3,000) (analysis/plan_150k_test.py). Every 5th start
day 2018-01 .. 2023-09, 3 years, real day order. Reported per slot: payouts, evaluations / activations bought, days to the
first payout and to one full account ($13,000 / $20,500), and the net under each path's fees.
  python3 analysis/apex_paths_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import account_pipeline_test as A50, account_pipeline150 as A150
from plan_150k_test import evaluation, R150, R50, ONB30

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
H = 756
PATHS = {"50K EOD (+$130 activation)": ("50K", 59.0, 24.5, 130.0), "50K no-activation": ("50K", 119.0, 109.0, 0.0),
         "150K EOD (+$150 activation)": ("150K", 219.0, 199.0, 150.0), "150K no-activation": ("150K", 249.0, 249.0, 0.0)}

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; atr = g.daily_atr(15); tr = lab.tr; D = len(tr); dates = pd.DatetimeIndex(g.ts[tr])
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    PLAN = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r_ = paths(g, t); P[nm] = (w[tr] / 10, r_[tr] / 10)
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": rk(1100, 0.25), "MON_BR": 2.0, "EOS": rk(500, REPORTS["EOS"][1])}
    Wc = sum(P[k][0] * q[k] for k in P); Rc = sum(P[k][1] * q[k] for k in P)
    s_lo, s_hi = int(np.argmax(dates >= "2018-01-01")), int(np.argmax(dates >= "2023-09-01")); starts = list(range(s_lo, min(s_hi, D - H - 30), 5))
    SIZE = {}
    for nm, mod, rules, ck, plan, ref, cap in (("50K", A50, R50, 1.0, PLAN, 1500.0, 13000.0),
                                               ("150K", A150, R150, 2.5, {n: (("risk", v[1] * 1.5) if isinstance(v, tuple) else v * 1.5) for n, v in PLAN.items()}, 3000.0, 20500.0)):
        chal = [evaluation(Wc * ck, Rc * ck, s, D, rules) for s in range(D)]
        names, b = lab._base(plan)
        Wf = np.stack([lab.W[k] for k in names]); Cf = np.stack([lab.C[k] for k in names]); b = np.ascontiguousarray(b)
        cache = {}
        def PA(s, h):
            if (s, h) not in cache: cache[(s, h)] = mod.pa_timeline(Wf, Cf, b, s, h, 0.5, 1.0, ref)
            return cache[(s, h)]
        rows = []
        for s0 in starts:
            fl, c = mod.slot(s0, s0 + H, chal, PA, 0.0)
            pays = sorted((d - s0, v) for d, v in fl.items() if v > 0)
            cum = np.cumsum([v for _, v in pays]) if pays else np.array([0.0])
            first = pays[0][0] if pays else np.inf
            full = pays[int(np.argmax(cum >= cap))][0] if pays and (cum >= cap).any() else np.inf
            rows.append(dict(pay12=sum(v for d, v in pays if d <= 252), pay24=sum(v for d, v in pays if d <= 504), pay36=sum(v for _, v in pays),
                             first=first, tfull=full, **c))
        SIZE[nm] = (pd.DataFrame(rows), np.mean([x[0] == "pass" for x in chal if x is not None]))
    print(f"\nPer slot (one account at a time), means over {len(starts)} start days; days = trading days from buying the first evaluation")
    for nm, (df, pr) in SIZE.items():
        print(f"   {nm:<5} eval pass {pr:.1%} | payouts 12m ${df.pay12.mean():,.0f}, 24m ${df.pay24.mean():,.0f}, 36m ${df.pay36.mean():,.0f} | "
              f"evals {df.challenges.mean():.1f}, funded {df.funded.mean():.1f}, completed accounts {df.full.mean():.1f} | "
              f"median days to 1st payout {np.median(df['first']):.0f}, to one full account's worth {np.median(df.tfull):.0f}")
    print(f"\n{'path':<30} {'eval':>7} {'act':>5} {'cost per funded acct':>21} {'fees 3y':>8} {'net 12m':>9} {'net 36m':>9} {'net per $1 of fees (3y)':>24}")
    for nm, (sz, ev1, ev5, act) in PATHS.items():
        df, pr = SIZE[sz]
        for lbl, ev in (("single", ev1), ("5-pack", ev5)):
            if lbl == "5-pack" and ev5 == ev1: continue
            fees = df.challenges * ev + df.funded * act
            per_funded = ev / pr + act
            net36 = df.pay36 - fees
            # fees in the first 12 months: approximate by the share of evaluations bought in year 1 (~ the 3-year rate)
            net12 = df.pay12 - fees / 3
            print(f"{nm + ' (' + lbl + ')':<30} ${ev:>6.2f} ${act:>4.0f} ${per_funded:>20,.0f} ${fees.mean():>7,.0f} ${net12.mean():>8,.0f} ${net36.mean():>8,.0f} {net36.mean() / fees.mean():>24.0f}")
