"""Budget ramp, before vs now (user 2026-11-09: 'I meant over months and years; the last time we did that was a week or two ago').
Same engine, schedule and scenarios as analysis/ramp_budget_test.py (rerun 2026-11-08 on the corrected evaluation floor: 2027 median
$237k, 5 d/wk, job ends, 1 a day); only the plans change. Information only.
  before (as run 11/08): evaluation VB 20, ONB ADX30 $2,750, Bridge Monday 5, EOS $1,250; funded = the 10/16 plan x 1.5 (VB 3 normal).
  now: evaluation + Twin 2 MNQ, VB 15 + Dual Thrust 2 MNQ; funded = plan x 1.5 with VB_N 2 (funded_bootstrap.PLAN 11/08) + Twin 2.
Kept as 11/08 for a clean comparison: paydays from Fri 11/13 (the real first payday is likely Mon 11/17, ~2 trading days later),
Day 0 = Mon 2026-11-02, at most 20 open accounts, 85% of pay after tax, payouts reinvested, every 10th start day 2018-01 .. 2023-09.
Adds payouts by month (median across start days, cumulative) for the main scenario.
  tools/run_stamped.sh analysis/progress_ramp.py > analysis/outputs/progress_ramp_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from plan_150k_test import evaluation, R150, ONB30
from ramp_to_20_test import haircut
import account_pipeline150 as A150
import dual_thrust_bench as DTB
import bench150 as BB
from ramp_budget_test import income, H, DEC31, END27, FEE, CAP

MONTHS = pd.date_range("2026-11-01", "2027-12-01", freq="MS")


def run(s0, chal, PA, inc, per_day=1):
    cash = FEE; pay = {}; ends = []; funded = 0; evals = 0; first = None; got27 = 0.0; paid = {}
    for d in range(H):
        cash += inc.get(d, 0.0) + pay.pop(d, 0.0)
        ends = [e for e in ends if e > d]; today = 0
        while today < per_day and cash >= FEE and len(ends) < CAP and s0 + d < len(chal):
            r = chal[s0 + d]
            if r is None: break
            cash -= FEE; evals += d <= DEC31; today += 1; out, k = r
            if out != "pass": ends.append(d + k); continue
            p = d + k; funded += p <= DEC31
            pday, pamt, n, e, blown = PA(s0 + p, H - p)
            for i in range(n):
                dd = int(pday[i]) - s0
                if dd < H:
                    pay[dd] = pay.get(dd, 0.0) + pamt[i]; paid[dd] = paid.get(dd, 0.0) + pamt[i]
                    if DEC31 < dd <= END27: got27 += pamt[i]
                    first = dd if first is None else min(first, dd)
            ends.append(p + e)
    when = lambda d: pd.Timestamp("2026-11-02") + pd.tseries.offsets.BDay(int(d))
    bym = pd.Series(paid).groupby(lambda d: when(d).to_period("M").to_timestamp()).sum() if paid else pd.Series(dtype=float)
    return dict(funded=funded, evals=evals, payouts27=got27, first=first, bym=bym.reindex(MONTHS, fill_value=0.0).cumsum())


if __name__ == "__main__":
    pd.set_option("display.width", 240); print(__doc__.split("\n")[0])
    ctx = BB.setup(); g, lab = ctx["g"], ctx["lab"]; tr = lab.tr; D = len(tr); dates = pd.DatetimeIndex(g.ts[tr]); atr = g.daily_atr(15)
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, ONB30))), ("MON_BR", load_bridge_mc(g)),
                  ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0]))), ("DT", DTB.dt_trades(g))):
        w, r_ = paths(g, t); P[nm] = (w[tr] / 10, r_[tr] / 10)
    P["TWIN"] = (ctx["Wt"], ctx["Rt"])
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    EV = {"before": {"VB": 20.0, "ONB30": rk(2750, 0.25), "MON_BR": 5.0, "EOS": rk(1250, REPORTS["EOS"][1])}}
    EV["now"] = {**EV["before"], "VB": 15.0, "DT": 2.0, "TWIN": 2.0}
    old = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    FU = {"before": BB.sc(old, 1.5), "now": BB.BASE_FUNDED}
    s_lo, s_hi = int(np.argmax(dates >= "2018-01-01")), int(np.argmax(dates >= "2023-09-01")); starts = list(range(s_lo, min(s_hi, D - H - 60), 10))
    month = lambda d: (pd.Timestamp("2026-11-02") + pd.tseries.offsets.BDay(int(d))).strftime("%b %d")
    for alpha in (0.0, 0.25):
        print(f"\n=== {'backtest edge' if alpha == 0 else '75% of the edge'}")
        print(f"{'plan / scenario':<46}{'eval pass':>10}{'evals to Dec 31':>16}{'funded Dec 31 p10-p50-p90':>28}{'first payout':>14}{'2027 payouts p10 / p50 / p90':>32}{'P(0 funded)':>13}")
        for tag in ("before", "now"):
            Wc = 0; Rc = 0
            for k, q in EV[tag].items():
                cl = P[k][1][:, -1]; wh, ch = haircut(P[k][0], cl, alpha); rh = P[k][1] - (cl - ch)[:, None]; Wc = Wc + wh * q; Rc = Rc + rh * q
            chal = [evaluation(Wc, Rc, s, D, R150) for s in range(D)]; pr = np.mean([c[0] == "pass" for c in chal if c is not None])
            names, b = lab._base(FU[tag]); Wf = np.stack([lab.W[k] for k in names]); Cf = np.stack([lab.C[k] for k in names]); b = np.ascontiguousarray(b)
            for i in range(Wf.shape[0]): Wf[i], Cf[i] = haircut(Wf[i], Cf[i], alpha)
            cache = {}
            def PA(s, h, cache=cache, Wf=Wf, Cf=Cf, b=b):
                if (s, h) not in cache: cache[(s, h)] = A150.pa_timeline(Wf, Cf, b, s, h, 0.5, 1.0, 3000.0)
                return cache[(s, h)]
            for nm, dpw, keep in (("5 d/wk, job ends 12/24, 1 a day", 5, False), ("6 d/wk, job ends, 1 a day", 6, False), ("5 d/wk, job kept*, 1 a day", 5, True)):
                rows = [run(s0, chal, PA, income(dpw, keep)) for s0 in starts]; R = pd.DataFrame([{k: v for k, v in r.items() if k != "bym"} for r in rows]); fp = R["first"].dropna()
                q = lambda c, p: R[c].quantile(p)
                print(f"{tag + ': ' + nm:<46}{pr:>10.1%}{R.evals.median():>16.0f}{f'{q(chr(102) + 'unded', .1):.0f} - {R.funded.median():.0f} - {q(chr(102) + 'unded', .9):.0f}':>28}"
                      f"{month(fp.median()) if len(fp) else '-':>14}{'$' + format(q('payouts27', .1) / 1e3, ',.0f') + 'k / $' + format(R.payouts27.median() / 1e3, ',.0f') + 'k / $' + format(q('payouts27', .9) / 1e3, ',.0f') + 'k':>32}{(R.funded == 0).mean():>13.0%}", flush=True)
                if nm.startswith("5 d/wk, job ends"):
                    M = pd.concat([r["bym"] for r in rows], axis=1)
                    print("      cumulative payouts by month (median / p10 / p90): " + " | ".join(f"{d.strftime('%b%y')} ${M.loc[d].median() / 1e3:,.0f}k ({M.loc[d].quantile(.1) / 1e3:,.0f}-{M.loc[d].quantile(.9) / 1e3:,.0f})" for d in MONTHS[2::2]))
