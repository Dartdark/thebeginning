"""How many accounts to run: the full Apex pipeline over real history (2026-10-14).

Each "slot" is one account at a time, cycling: buy a 50K challenge ($EVAL each try) -> on a pass, activate a funded PA
($ACT) -> run it until the 6th payout ($13,000) or until it is blown -> buy the next challenge. Run N slots in parallel.
  - Challenge: the current combine set (VB 8 MNQ + ONB ADX30 $1,100 + Bridge Monday Long 2 MNQ + EOS $500), the real-day
    challenge simulator (analysis/portfolio.py; $3,000 target, $2,000 MLL, $1,000 DLL, 21 days).
  - Funded: the 7-strategy funded plan with cushion sizing (full size from $1,500), the funded simulator
    (analysis/funded_sim.py rules, payouts on the day the conditions are met).
  - Accounts trading the same strategies on the same days get the same trades; they differ only through their start
    days and cushions, so their outcomes are correlated exactly as far as the real history makes them.
  - Slots start together, or staggered (a new slot every k trading days).
Every start month 2018-01 .. 2023-10 (3-year windows), cash = payouts - challenge fees - activation fees.
Fees are inputs (Apex prices change with promotions): EVAL $50 a challenge (HANDOFF), ACT $0 / $85 / $140 a PA.
  python3 analysis/account_pipeline_test.py [SCRATCH_DIR]
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import funded_sim as F
from funded_sim import njit, _dll, START, MLL, LOCK, SAFETY, MIN_DAY, MIN_DAYS, CAPS
from portfolio import paths, challenge
from time_clusters_test import trades as plan_trades
from bridge_monday_confirm import load_bridge_mc

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
H = 750                     # 3-year window, trading days
EVAL = 50.0
CS = dict(fmin=0.5, fmax=1.0, ref=1500.0)
PLAN = {"VB": 3, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1}


@njit(cache=True)
def pa_timeline(W, C, base, s, horizon, fmin, fmax, ref):
    """run_pa_sized (keep 0, consistency on, no stage) that also returns each payout's day. Returns
    (days[6], amounts[6], n, end_day_offset, blown)."""
    K, D, M = W.shape
    pday = np.full(6, -1); pamt = np.zeros(6)
    bal = START; floor = START - MLL; cyc_start = START; best = 0.0; qual = 0; n = 0
    end = min(D, s + horizon); q = np.zeros(K)
    for d in range(s, end):
        f = (bal - floor) / ref
        f = min(max(f, fmin), fmax)
        any_q = False
        for k in range(K):
            q[k] = np.floor(base[k, d] * f + 1e-9)
            if q[k] > 0: any_q = True
        if not any_q: continue
        dll = _dll(bal); lim = max(floor, bal - dll); low = 0.0
        for j in range(M):
            x = 0.0
            for k in range(K):
                if q[k] > 0: x += q[k] * W[k, d, j]
            if x < low: low = x
        if bal + low <= lim:
            if floor >= bal - dll:
                return pday, pamt, n, d - s + 1, 1
            pnl = -dll
        else:
            pnl = 0.0
            for k in range(K): pnl += q[k] * C[k, d]
        bal += pnl
        if pnl >= MIN_DAY: qual += 1
        if pnl > best: best = pnl
        if floor < LOCK: floor = max(floor, min(bal - MLL, LOCK))
        prof = bal - cyc_start; room = bal - SAFETY; cap = CAPS[n]
        if qual >= MIN_DAYS and room >= cap and prof > 0 and best < 0.5 * prof:
            bal -= cap; pday[n] = d; pamt[n] = cap; n += 1
            if n == 6: return pday, pamt, n, d - s + 1, 0
            cyc_start = bal; best = 0.0; qual = 0
    return pday, pamt, n, end - s, 0


def slot(t0, tend, chal, PA, act):
    """Cash flows (day -> $) of one slot from day t0 to tend; also counts."""
    flow = {}; t = t0; n_ch = n_pa = n_blown = n_full = 0
    while t < tend:
        r = chal[t]
        if r is None: break
        flow[t] = flow.get(t, 0.0) - EVAL; n_ch += 1
        out, k = r; t += k
        if out != "pass": continue
        if t >= tend: break
        flow[t] = flow.get(t, 0.0) - act; n_pa += 1
        pday, pamt, n, e, blown = PA(t, tend - t)
        for i in range(n):
            if pday[i] < tend: flow[int(pday[i])] = flow.get(int(pday[i]), 0.0) + pamt[i]
        n_blown += blown; n_full += (n == 6); t += e
    return flow, dict(challenges=n_ch, funded=n_pa, blown=n_blown, full=n_full)


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
    ok = [c for c in chal if c is not None]
    print(f"challenge: pass {np.mean([c[0] == 'pass' for c in ok]):.1%} of start days, median {np.median([c[1] for c in ok]):.0f} days per try")

    lab = pickle.load(open(SP + "lab.pkl", "rb")); lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
    names, b = lab._base(PLAN)
    Wf = np.stack([lab.W[k] for k in names]); Cf = np.stack([lab.C[k] for k in names]); b = np.ascontiguousarray(b)
    cache = {}
    def PA(s, h):
        key = (s, h)
        if key not in cache: cache[key] = pa_timeline(Wf, Cf, b, s, h, CS["fmin"], CS["fmax"], CS["ref"])
        return cache[key]
    # sanity: single PA from each start = funded bench
    tot = [PA(s, 750)[1].sum() for s in range(0, D - 750, 5)]
    print(f"funded PA alone (3 years, every 5th start): mean paid ${np.mean(tot):,.0f}, all 6 {np.mean(np.array(tot) >= 13000):.0%}")

    starts = [int(np.argmax(dates >= pd.Timestamp(y, m, 1))) for y in range(2018, 2024) for m in range(1, 13) if pd.Timestamp(y, m, 1) <= pd.Timestamp("2023-10-01")]
    rows = []
    for act in (0.0, 85.0, 140.0):
        for N, stag in ((1, 0), (2, 0), (2, 10), (3, 0), (3, 10), (5, 0), (5, 10), (5, 21), (10, 10), (20, 5)):
            res = []
            for s0 in starts:
                tend = min(D, s0 + H); cash = np.zeros(tend - s0 + 1); cnt = dict(challenges=0, funded=0, blown=0, full=0)
                blown_days = []
                for i in range(N):
                    fl, c = slot(s0 + i * stag, tend, chal, PA, act)
                    for d, v in fl.items(): cash[d - s0] += v
                    for k in cnt: cnt[k] += c[k]
                cum = np.cumsum(cash)
                m = lambda months: cum[min(len(cum) - 1, months * 21)]
                hit = np.argmax(cum >= 13000) if (cum >= 13000).any() else np.inf
                res.append(dict(net6=m(6), net12=m(12), net24=m(24), net36=cum[-1], days13k=hit, worst=cum.min(), **cnt))
            df = pd.DataFrame(res)
            rows.append(dict(act=act, N=N, stagger=stag, net6=df.net6.median(), net12=df.net12.median(), net24=df.net24.median(), net36=df.net36.median(),
                             p10_12=df.net12.quantile(0.1), months_to_13k=np.median(df.days13k) / 21, worst_cash=df.worst.median(),
                             per_month_36=df.net36.median() / 36, challenges=df.challenges.median(), funded=df.funded.median(),
                             blown=df.blown.median(), full=df.full.median()))
    R = pd.DataFrame(rows)
    fm = {c: "${:,.0f}".format for c in ("net6", "net12", "net24", "net36", "p10_12", "worst_cash", "per_month_36")}
    fm["months_to_13k"] = lambda v: ">36" if not np.isfinite(v) else f"{v:.1f}"
    for act in (0.0, 85.0, 140.0):
        print(f"\n=== Activation fee ${act:.0f} per funded account (challenge ${EVAL:.0f} a try); medians over {len(starts)} start months 2018-2023")
        print(R[R.act == act].drop(columns="act").to_string(index=False, formatters=fm))

    # correlation of blow-ups: same-day starts vs staggered, N = 5
    print("\nSimultaneous failures (N = 5, ACT $85): share of start months with 3+ funded accounts blown within the same 10 trading days")
    for stag in (0, 10, 21):
        k3 = 0
        for s0 in starts:
            tend = min(D, s0 + H); ev = []
            for i in range(5):
                t = s0 + i * stag
                while t < tend:
                    r = chal[t]
                    if r is None: break
                    out, k = r; t += k
                    if out != "pass" or t >= tend: continue
                    pday, pamt, n, e, bl = PA(t, tend - t)
                    if bl: ev.append(t + e)
                    t += e
            ev = np.sort(ev); k3 += any(ev[j + 2] - ev[j] <= 10 for j in range(len(ev) - 2)) if len(ev) >= 3 else 0
        print(f"   stagger {stag:2d} days: {k3 / len(starts):.0%}")
    pickle.dump(R, open(SP + "account_pipeline.pkl", "wb"))

    print("\n=== Stress test: each strategy's average profit per trading day cut by a share alpha (volatility unchanged),"
          " in the challenge and the funded phase; ACT $85, stagger 10 days")
    def haircut(Wk, Ck, alpha):
        """Wk: (D, M) open-equity path, Ck: (D,) close (per unit). Shift traded days down by alpha x mean daily close."""
        traded = Ck != 0; mu = Ck[traded].mean() if traded.any() else 0.0
        sh = np.where(traded, alpha * mu, 0.0)
        return Wk - sh[:, None], Ck - sh
    rows2 = []
    for alpha in (0.25, 0.5):
        W0h = np.zeros_like(W0); R0h = np.zeros_like(R0)
        for p, q in parts:
            cl = p[1][:, -1]; wh, ch = haircut(p[0], cl, alpha)
            rh = p[1] - (cl - ch)[:, None]
            W0h += wh * q; R0h += rh * q
        chal_h = [challenge(W0h, R0h, np.arange(s, min(s + 21, D))) for s in range(D)]
        okh = [c for c in chal_h if c is not None]; pr = np.mean([c[0] == "pass" for c in okh])
        Wh = Wf.copy(); Ch = Cf.copy()
        for k in range(Wf.shape[0]): Wh[k], Ch[k] = haircut(Wf[k], Cf[k], alpha)
        cache_h = {}
        def PAh(s, h):
            if (s, h) not in cache_h: cache_h[(s, h)] = pa_timeline(Wh, Ch, b, s, h, CS["fmin"], CS["fmax"], CS["ref"])
            return cache_h[(s, h)]
        tot = np.array([PAh(s, 750)[1].sum() for s in range(0, D - 750, 5)]); bl = np.mean([PAh(s, 750)[4] for s in range(0, D - 750, 5)])
        print(f"   alpha {alpha}: challenge pass {pr:.1%}; funded PA alone (3 years) mean ${tot.mean():,.0f}, all 6 {np.mean(tot >= 13000):.0%}, blown {bl:.0%}")
        for N in (1, 3, 5, 10):
            res = []
            for s0 in starts:
                tend = min(D, s0 + H); cash = np.zeros(tend - s0 + 1); cnt = dict(challenges=0, funded=0, blown=0, full=0)
                for i in range(N):
                    fl, c = slot(s0 + i * 10, tend, chal_h, PAh, 85.0)
                    for d, v in fl.items(): cash[d - s0] += v
                    for kk in cnt: cnt[kk] += c[kk]
                cum = np.cumsum(cash); hit = np.argmax(cum >= 13000) if (cum >= 13000).any() else np.inf
                res.append(dict(net12=cum[min(len(cum) - 1, 252)], net36=cum[-1], worst=cum.min(), days13k=hit, **cnt))
            df = pd.DataFrame(res)
            rows2.append(dict(alpha=alpha, N=N, net12=df.net12.median(), p10_12=df.net12.quantile(0.1), net36=df.net36.median(), p10_36=df.net36.quantile(0.1),
                              worst_cash=df.worst.median(), worst_cash_p10=df.worst.quantile(0.1), months_to_13k=np.median(df.days13k) / 21,
                              challenges=df.challenges.median(), funded=df.funded.median(), blown=df.blown.median(), full=df.full.median()))
    R2 = pd.DataFrame(rows2)
    fm2 = {c: "${:,.0f}".format for c in ("net12", "p10_12", "net36", "p10_36", "worst_cash", "worst_cash_p10")}
    fm2["months_to_13k"] = lambda v: ">36" if not np.isfinite(v) else f"{v:.1f}"
    print(R2.to_string(index=False, formatters=fm2))
