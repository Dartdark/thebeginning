"""Ramp to Apex's 20-account limit (user, 2026-10-15: 'show me a plan where I continually add accounts'). A slot is one
account at a time (challenge -> funded PA -> next challenge, analysis/account_pipeline_test.py mechanics: combine set
pass 50.1%, funded 7-strategy plan with cushion sizing, payouts on the day Apex's conditions are met, challenge $50,
activation $85), so N slots never hold more than N accounts. All slots copy the same plan, so their outcomes are linked
by the start-day gaps only. Schedules (trading days from the first account, 2026-10-12):
  A  3 slots (0 / +6 / +11), the current plan, for reference
  B  +1 slot a week (every 5 trading days) to 20
  C  +2 slots a week to 20
  D  gated: 3 slots for 2 months (live check of the edge), then +2 a week to 20  <- proposed
  E  20 at once (shown for the risk: one bet x 20)
Every 10th start day 2018-01 .. 2023-09, 3-year horizon, real day order; cash = payouts - fees. Also at 75% of the
backtest edge (each strategy's average profit per traded day cut by 25%, volatility unchanged).
  python3 analysis/ramp_to_20_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import paths, challenge
from time_clusters_test import trades as plan_trades
from bridge_monday_confirm import load_bridge_mc
from account_pipeline_test import pa_timeline, PLAN, CS, EVAL, slot

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
ACT = 85.0; H = 756
SCHED = {"A  3 slots (current)": [0, 6, 11],
         "B  +1 a week to 20": [0, 6, 11] + [11 + 5 * i for i in range(1, 18)],
         "C  +2 a week to 20": [0, 6, 11] + [11 + 5 * (i // 2 + 1) for i in range(17)],
         "D  3 for 2 months, then +2 a week to 20": [0, 6, 11] + [42 + 5 * (i // 2) for i in range(17)],
         "E  20 at once": [0] * 20}
MONTHS = (3, 6, 12, 24, 36)


def haircut(Wk, Ck, alpha):
    traded = Ck != 0; mu = Ck[traded].mean() if traded.any() else 0.0
    sh = np.where(traded, alpha * mu, 0.0); return Wk - sh[:, None], Ck - sh


if __name__ == "__main__":
    pd.set_option("display.width", 240)
    print(__doc__.split("\n")[0])
    g = pickle.load(open(SP + "g24.pkl", "rb"))
    T = plan_trades(g); atr = g.daily_atr(15); tr = g.trading; D = len(tr); dates = pd.DatetimeIndex(g.ts[tr])
    P = {}
    for nm in ("VB", "ONB_ADX30", "MON_BR", "EOS"):
        w, r = paths(g, T[nm]); P[nm] = (w[tr] / 10, r[tr] / 10)
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    parts = [(P["VB"], 8), (P["ONB_ADX30"], rk(1100, 0.25)), (P["MON_BR"], 2), (P["EOS"], rk(500, 0.30))]
    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    names, b = lab._base(PLAN)
    Wf = np.stack([lab.W[k] for k in names]); Cf = np.stack([lab.C[k] for k in names]); b = np.ascontiguousarray(b)
    s_lo, s_hi = int(np.argmax(dates >= "2018-01-01")), int(np.argmax(dates >= "2023-09-01"))
    starts = list(range(s_lo, min(s_hi, D - H - 60), 10))
    for alpha in (0.0, 0.25):
        W0 = np.zeros_like(parts[0][0][0]); R0 = np.zeros_like(parts[0][0][1])
        for p, q in parts:
            cl = p[1][:, -1]; wh, ch = haircut(p[0], cl, alpha); rh = p[1] - (cl - ch)[:, None]
            W0 = W0 + wh * q; R0 = R0 + rh * q
        chal = [challenge(W0, R0, np.arange(s, min(s + 21, D))) for s in range(D)]
        Wh, Ch = Wf.copy(), Cf.copy()
        for k in range(Wf.shape[0]): Wh[k], Ch[k] = haircut(Wf[k], Cf[k], alpha)
        cache = {}
        def PA(s, h):
            if (s, h) not in cache: cache[(s, h)] = pa_timeline(Wh, Ch, b, s, h, CS["fmin"], CS["fmax"], CS["ref"])
            return cache[(s, h)]
        print(f"\n=== {'backtest edge' if alpha == 0 else '75% of the edge'}: challenge pass {np.mean([c[0] == 'pass' for c in chal if c is not None]):.1%}")
        print(f"{'schedule':<44}" + "".join(f"{f'{m}m median':>12}" for m in MONTHS) + f"{'12m p10':>10}{'36m p10':>10}{'worst cash p10':>15}{'accts paid out / blown (3y)':>29}")
        for nm, offs in SCHED.items():
            res = []
            for s0 in starts:
                tend = s0 + H; cash = np.zeros(H + 1); cnt = dict(challenges=0, funded=0, blown=0, full=0)
                for off in offs:
                    fl, c = slot(s0 + off, tend, chal, PA, ACT)
                    for d, v in fl.items(): cash[d - s0] += v
                    for k in cnt: cnt[k] += c[k]
                cum = np.cumsum(cash)
                res.append({**{f"m{m}": cum[min(H, m * 21)] for m in MONTHS}, "worst": cum.min(), **cnt})
            df = pd.DataFrame(res)
            print(f"{nm:<44}" + "".join(f"{'$' + format(df[f'm{m}'].median(), ',.0f'):>12}" for m in MONTHS)
                  + f"{'$' + format(df.m12.quantile(0.1), ',.0f'):>10}{'$' + format(df.m36.quantile(0.1), ',.0f'):>10}{'$' + format(df.worst.quantile(0.1), ',.0f'):>15}"
                  + f"{f'{df.full.median():.0f} / {df.blown.median():.0f}':>29}", flush=True)
