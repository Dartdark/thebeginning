"""What does the pipeline make in its first months? (user, 2026-10-15). The user's schedule: combine #1 started 2026-10-12,
#2 on Tue 10/20 (+6 trading days), #3 about a week later (+11); each slot then cycles challenge -> funded PA -> next
challenge (analysis/account_pipeline_test.py: combine set pass 50.1%, funded 7-strategy plan with cushion sizing, payouts
on the day Apex's conditions are met, challenge $50, activation $85). Every 5th start day 2018-01 .. 2023-10, real day
order. Reported at 1 / 2 / 3 / 6 / 12 months (21 trading days each): cash (payouts - fees), mean / median / 10th-90th
percentile, chance of being up, of having at least one funded account, and of having received any payout.
  python3 analysis/first_months_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import paths, challenge
from time_clusters_test import trades as plan_trades
from bridge_monday_confirm import load_bridge_mc
from account_pipeline_test import pa_timeline, PLAN, CS, EVAL

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
ACT = 85.0; OFFS = (0, 6, 11); MONTHS = (1, 2, 3, 6, 12)

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    T = plan_trades(g); atr = g.daily_atr(15); tr = g.trading; D = len(tr); dates = pd.DatetimeIndex(g.ts[tr])
    P = {}
    for nm in ("VB", "ONB_ADX30", "MON_BR", "EOS"):
        w, r = paths(g, T[nm]); P[nm] = (w[tr] / 10, r[tr] / 10)
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    parts = [(P["VB"], 8), (P["ONB_ADX30"], rk(1100, 0.25)), (P["MON_BR"], 2), (P["EOS"], rk(500, 0.30))]
    W0 = sum(p[0] * q for p, q in parts); R0 = sum(p[1] * q for p, q in parts)
    chal = [challenge(W0, R0, np.arange(s, min(s + 21, D))) for s in range(D)]
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    names, b = lab._base(PLAN)
    Wf = np.stack([lab.W[k] for k in names]); Cf = np.stack([lab.C[k] for k in names]); b = np.ascontiguousarray(b)
    cache = {}
    def PA(s, h):
        if (s, h) not in cache: cache[(s, h)] = pa_timeline(Wf, Cf, b, s, h, CS["fmin"], CS["fmax"], CS["ref"])
        return cache[(s, h)]
    H = 12 * 21 + 1
    s_lo, s_hi = int(np.argmax(dates >= "2018-01-01")), int(np.argmax(dates >= "2023-10-01"))
    rows = []
    for s0 in range(s_lo, s_hi, 5):
        tend = s0 + H; cash = np.zeros(H + 1); funded_by = np.full(len(OFFS), np.inf); paid_by = np.inf
        for i, off in enumerate(OFFS):
            t = s0 + off
            while t < tend:
                r = chal[t]
                if r is None: break
                cash[t - s0] -= EVAL; out, k = r; t += k
                if out != "pass" or t >= tend: continue
                cash[t - s0] -= ACT; funded_by[i] = min(funded_by[i], t - s0)
                pday, pamt, n, e, blown = PA(t, tend - t)
                for j in range(n):
                    if pday[j] < tend: cash[int(pday[j]) - s0] += pamt[j]; paid_by = min(paid_by, pday[j] - s0)
                t += e
        cum = np.cumsum(cash)
        rows.append({**{f"m{m}": cum[m * 21] for m in MONTHS}, **{f"f{m}": float(np.min(funded_by) <= m * 21) for m in MONTHS},
                     **{f"p{m}": float(paid_by <= m * 21) for m in MONTHS}})
    df = pd.DataFrame(rows)
    print(f"\n{len(df)} start days; 3 slots started at +0 / +6 / +11 trading days (the user's schedule)\n")
    print(f"{'after':<10} {'mean cash':>10} {'median':>9} {'10th pct':>9} {'90th pct':>9} {'P(up)':>7} {'P(>=1 funded)':>14} {'P(any payout)':>14}")
    for m in MONTHS:
        x = df[f"m{m}"]
        print(f"{m:>2} month{'s' if m > 1 else ' '}  ${x.mean():>9,.0f} ${x.median():>8,.0f} ${x.quantile(0.1):>8,.0f} ${x.quantile(0.9):>8,.0f} "
              f"{np.mean(x > 0):>7.0%} {df[f'f{m}'].mean():>14.0%} {df[f'p{m}'].mean():>14.0%}")
