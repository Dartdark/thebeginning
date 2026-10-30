"""Budget-driven 150K ramp (user, 2026-10-30): the plan as agreed, not the 10/16 schedule. Day 0 = Mon 2026-11-02 (#4 bought
Sun 11/01 from savings). Job Tue 11/10 - Thu 12/24, $25 x 8 h, paid each Friday (11/13 ... 12/18, last pay 12/24);
all pay goes to 150K No-Activation evaluations ($249); payouts are spent on evaluations too; at most 20 open accounts
(evaluations + funded). An account frees its place when its evaluation fails or its funded account ends (6 payouts or
blown). Scenarios: 5 or 6 days a week, after tax (x 0.85); job ends 12/24 or continues through 2027. #2 (50K) left out
(a bonus if it passes). Engine and plan as analysis/ramp150_speed_test.py (evaluation = combine set x 2.5; funded =
the 10/16 funded plan x 1.5 -- the current 150K plan earned ~15% more on the funded bench, so funded payouts here are
on the low side). Every 10th start day 2018-01 .. 2023-09, real day order; also at 75% of the edge.
  python3 analysis/ramp_budget_test.py [SCRATCH_DIR] > analysis/outputs/ramp_budget_test_output.txt
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
import account_pipeline150 as A150
from plan_150k_test import evaluation, R150, ONB30
from ramp_to_20_test import haircut

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
H = 300; DEC31 = 41; END27 = DEC31 + 252; FEE = 249.0; CAP = 20; TAX = 0.85
# trading-day offsets from Mon 11/02 of each payday and the days worked that week (Thanksgiving 11/26 closed for CME RTH)
PAY = [(9, 4), (14, 5), (18, 5), (23, 5), (28, 5), (33, 5), (37, 4)]           # 11/13, 11/20, 11/27, 12/4, 12/11, 12/18, 12/24


def income(days_per_week, keep_job):
    inc = {}
    for d, n in PAY: inc[d] = inc.get(d, 0.0) + 200.0 * min(n + (days_per_week - 5), days_per_week) * TAX
    if keep_job:
        for d in range(42, H, 5): inc[d] = inc.get(d, 0.0) + 200.0 * days_per_week * TAX
    return inc


def run(s0, chal, PA, inc, per_day=99):
    cash = FEE; pay = {}; ends = []; funded_by_dec31 = 0; evals = 0; fees = 0.0; first_pay = None; got27 = 0.0
    for d in range(H):
        cash += inc.get(d, 0.0) + pay.pop(d, 0.0)
        ends = [e for e in ends if e > d]; today = 0
        while today < per_day and cash >= FEE and len(ends) < CAP and s0 + d < len(chal):
            r = chal[s0 + d]
            if r is None: break
            cash -= FEE; fees += FEE; evals += d <= DEC31; today += 1; out, k = r
            if out != "pass": ends.append(d + k); continue
            p = d + k; funded_by_dec31 += p <= DEC31
            pday, pamt, n, e, blown = PA(s0 + p, H - p)
            for i in range(n):
                dd = int(pday[i]) - s0
                if dd < H:
                    pay[dd] = pay.get(dd, 0.0) + pamt[i]
                    if DEC31 < dd <= END27: got27 += pamt[i]
                    first_pay = dd if first_pay is None else min(first_pay, dd)
            ends.append(p + e)
    return dict(funded=funded_by_dec31, evals=evals, fees=fees, payouts27=got27, first=first_pay)


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
    s_lo, s_hi = int(np.argmax(dates >= "2018-01-01")), int(np.argmax(dates >= "2023-09-01"))
    starts = list(range(s_lo, min(s_hi, D - H - 60), 10))
    for alpha in (0.0, 0.25):
        Wc = np.zeros_like(P["VB"][0]); Rc = np.zeros_like(P["VB"][1])
        for k in P:
            cl = P[k][1][:, -1]; wh, ch = haircut(P[k][0], cl, alpha); rh = P[k][1] - (cl - ch)[:, None]
            Wc = Wc + wh * q[k]; Rc = Rc + rh * q[k]
        chal = [evaluation(Wc * 2.5, Rc * 2.5, s, D, R150) for s in range(D)]
        names, b = lab._base(P150)
        Wf = np.stack([lab.W[k] for k in names]); Cf = np.stack([lab.C[k] for k in names]); b = np.ascontiguousarray(b)
        for i in range(Wf.shape[0]): Wf[i], Cf[i] = haircut(Wf[i], Cf[i], alpha)
        cache = {}
        def PA(s, h):
            if (s, h) not in cache: cache[(s, h)] = A150.pa_timeline(Wf, Cf, b, s, h, 0.5, 1.0, 3000.0)
            return cache[(s, h)]
        print(f"\n=== {'backtest edge' if alpha == 0 else '75% of the edge'}  (150K evaluation pass "
              f"{np.mean([c[0] == 'pass' for c in chal if c is not None]):.1%})")
        print(f"{'scenario':<40}{'evals to Dec 31':>16}{'funded by Dec 31 (p10-p50-p90)':>33}{'first payout':>14}"
              f"{'2027 payouts p10 / p50 / p90':>32}{'P(0 funded Dec31)':>19}")
        for nm, dpw, keep, pdy in (("5 d/wk, job ends 12/24, all on payday", 5, False, 99), ("5 d/wk, job ends, 1 a day", 5, False, 1),
                                   ("6 d/wk, job ends, 1 a day", 6, False, 1), ("5 d/wk, job kept*, all on payday", 5, True, 99),
                                   ("5 d/wk, job kept*, 1 a day", 5, True, 1), ("6 d/wk, job kept*, 1 a day", 6, True, 1)):
            inc = income(dpw, keep)
            rows = pd.DataFrame([run(s0, chal, PA, inc, pdy) for s0 in starts])
            fp = rows["first"].dropna()
            month = lambda d: (pd.Timestamp("2026-11-02") + pd.tseries.offsets.BDay(int(d))).strftime("%b %d")
            print(f"{nm:<40}{rows.evals.median():>16.0f}{f'{rows.funded.quantile(.1):.0f} - {rows.funded.median():.0f} - {rows.funded.quantile(.9):.0f}':>33}"
                  f"{month(fp.median()) if len(fp) else '-':>14}"
                  f"{'$' + format(rows.payouts27.quantile(.1) / 1e3, ',.0f') + 'k / $' + format(rows.payouts27.median() / 1e3, ',.0f') + 'k / $' + format(rows.payouts27.quantile(.9) / 1e3, ',.0f') + 'k':>32}{(rows.funded == 0).mean():>19.0%}", flush=True)
