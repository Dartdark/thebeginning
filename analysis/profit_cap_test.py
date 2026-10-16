"""Daily profit cap vs the 50% consistency rule (user, 2026-10-16: 'wouldn't it be counterproductive to have a trade more
than $1,500 in profit ... cut the trade at $1,500 and possibly pass the day after?').

Apex rules (screenshots in the repo root, 2026-10-15): the EVALUATION card lists no consistency rule (min 1 day to pass,
target $3,000); the 50% consistency requirement is on the Performance Account payout page: 'no single profitable day may
account for 50% or more of total profit since your last approved payout; if not met the payout request is unavailable
until you reach 50% consistency'. So a big day never fails an account; in the PA it can only delay a payout.

Test: flatten everything for the day once the day's open P&L reaches $X (cap), for X = $500 .. $2,000 and no cap.
  Evaluation: the combine set (VB 8, ONB 30 by risk, Bridge Monday 2, EOS by risk), every start day 2018-26, 50K rules.
  Funded PA: the plan (cushion sizing, full from $1,500), every 2nd start day, 1 and 2 years, funded_sim rules
  (consistency on). Variant 'cap only while it binds': the cap is the profit since the last payout (so no day is ever
  above 50%), min $X.
A day's best open P&L comes from each trade's favourable excursion (bar highs for longs, lows for shorts), summed over the
strategies minute by minute; the cap fills at exactly $X (a limit-like exit; slightly flattering to the cap). Within a
minute the loss check runs first (conservative for the cap).
  python3 analysis/profit_cap_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from numba import njit
from portfolio import load_mc, paths, POINT_VALUE, COST
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from plan_150k_test import R50, ONB30
import funded_sim as FS

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
CAPS_X = [np.inf, 2500.0, 2000.0, 1500.0, 1250.0, 1000.0, 750.0, 500.0]


def best_paths(g, t):
    """Favourable-excursion equity path per day ($ per NQ after costs), like portfolio.paths' worst path."""
    best = np.zeros(g.o.shape); qty = t["qty"] if "qty" in t else np.ones(len(t))
    for day, j0, j1, side, entry, px, kind, q in zip(t["day"], t["j0"], t["j1"], t["side"], t["entry"], t["exit"], t["kind"], qty):
        net = ((px - entry) * side * POINT_VALUE - COST) * q; seg = slice(j0, j1 + 1)
        fav = g.h[day, seg] if side > 0 else g.l[day, seg]
        f = ((np.nan_to_num(fav, nan=entry) - entry) * side * POINT_VALUE - COST) * q
        f[-1] = net                               # the exit bar: count only the realised exit (no favourable spike past it)
        best[day, seg] += f; best[day, j1 + 1:] += net
    return best


def evaluation_cap(W, B, R, s, D, r, X):
    bal = r["st"]; floor = r["st"] - r["dd"]
    for n, d in enumerate(range(s, min(s + 21, D)), 1):
        w, b, rr = W[d], B[d], R[d]; lim = max(floor, bal - r["dll"])
        hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
        win = np.nonzero(bal + rr - r["st"] >= r["tgt"])[0]; jp = win[0] if len(win) else len(w)
        cp = np.nonzero(b >= X)[0]; jc = cp[0] if len(cp) else len(w)
        if jc < jb and jc <= jp:                       # cap first: flat at +X
            bal += X
            if bal - r["st"] >= r["tgt"]: return "pass", n
        elif jp < jb: return "pass", n
        elif jb < len(w):
            if lim == floor: return "fail", n
            bal = lim
        else: bal += rr[-1]
        floor = max(floor, min(bal - r["dd"], r["lock"]))
    return ("time", 21) if s + 21 <= D else None


@njit(cache=True)
def pa_cap(W, B, C, base, s, horizon, X, dyn, fmin, fmax, ref):
    K, D, M = W.shape
    bal = FS.START; floor = FS.START - FS.MLL; cyc = FS.START; best = 0.0; qual = 0; paid = 0.0; n = 0; first = -1
    end = min(D, s + horizon); q = np.zeros(K)
    for d in range(s, end):
        f = min(max((bal - floor) / ref, fmin), fmax); anyq = False
        for k in range(K):
            q[k] = np.floor(base[k, d] * f + 1e-9)
            if q[k] > 0: anyq = True
        if not anyq: continue
        p = bal - FS.START; dll = 3000.0 if p >= 6000.0 else (2000.0 if p >= 3000.0 else 1000.0)
        lim = max(floor, bal - dll)
        cap = X
        if dyn: cap = max(X, bal - cyc)                # keep this day below 50% of the profit since the last payout
        pnl = 0.0; done = False
        for j in range(M):
            xw = 0.0; xb = 0.0
            for k in range(K):
                if q[k] > 0: xw += q[k] * W[k, d, j]; xb += q[k] * B[k, d, j]
            if bal + xw <= lim:
                if floor >= bal - dll: return paid, n, 1, first
                pnl = -dll; done = True; break
            if xb >= cap:
                pnl = cap; done = True; break
        if not done:
            for k in range(K): pnl += q[k] * C[k, d]
        bal += pnl
        if pnl >= FS.MIN_DAY: qual += 1
        if pnl > best: best = pnl
        if floor < FS.LOCK: floor = max(floor, min(bal - FS.MLL, FS.LOCK))
        prof = bal - cyc
        if qual >= FS.MIN_DAYS and bal - FS.SAFETY >= FS.CAPS[n] and prof > 0 and best < 0.5 * prof:
            bal -= FS.CAPS[n]; paid += FS.CAPS[n]; n += 1
            if first < 0: first = d - s + 1
            if n == 6: return paid, n, 0, first
            cyc = bal; best = 0.0; qual = 0
    return paid, n, 0, first


@njit(cache=True)
def pa_all(W, B, C, base, starts, horizon, X, dyn):
    out = np.zeros((len(starts), 4))
    for i in range(len(starts)):
        a, b, c, e = pa_cap(W, B, C, base, starts[i], horizon, X, dyn, 0.5, 1.0, 1500.0)
        out[i, 0] = a; out[i, 1] = b; out[i, 2] = c; out[i, 3] = e
    return out


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        ns = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")
    lab = ns["lab"]; g = lab.g; tr = lab.tr; D = len(tr); dates = pd.DatetimeIndex(g.ts[tr]); atr = g.daily_atr(15)
    S = pd.read_pickle(SP + "single_print_sessions.pkl"); flag = S.flag.reindex(dates).fillna(False).to_numpy().astype(bool)
    T = {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB_ML2_MC": with_slippage(load_mc(g, REPORTS["ONB_ML2_MC"][0])),
         "MON_MC": with_slippage(load_mc(g, REPORTS["MON_MC"][0])), "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0])),
         "LDF_MC": with_slippage(load_mc(g, REPORTS["LDF_MC"][0])), "NFP_MC": with_slippage(load_mc(g, REPORTS["NFP_MC"][0])),
         "MON_BR_MC": load_bridge_mc(g), "ONB30": with_slippage(load_mc(g, ONB30))}
    Bp = {k: best_paths(g, t)[tr] / 10 for k, t in T.items()}            # per MNQ
    # sanity: best >= worst and ends at the same close
    for k in ("VB", "ONB_ML2_MC"):
        w = lab.W[k]; print(f"   check {k}: best >= worst on {np.mean(Bp[k] >= w - 1e-6):.4f} of minutes, same close {np.allclose(Bp[k][:, -1], lab.C[k])}")

    # ---------------- evaluation (combine set)
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    q = {"VB": 8.0, "ONB30": rk(1100, 0.25), "MON_BR_MC": 2.0, "EOS": rk(500, REPORTS["EOS"][1])}
    Wc = 0; Bc = 0; Rc = 0
    for k, qq in q.items():
        w, r_ = paths(g, T[k]); Wc = Wc + w[tr] / 10 * qq; Rc = Rc + r_[tr] / 10 * qq; Bc = Bc + Bp[k] * qq
    print("\n=== Evaluation (50K, $3,000 target, no consistency rule), combine set, every start day 2018-26")
    ok = dates.year >= 2018
    for X in CAPS_X:
        res = [evaluation_cap(Wc, Bc, Rc, s, D, R50, X) for s in range(D)]
        v = np.array([r is not None for r in res]) & ok; o = np.array([r[0] if r else "" for r in res]); nd = np.array([r[1] if r else 0 for r in res])
        print(f"   cap {'none' if not np.isfinite(X) else f'${X:,.0f}':>7}: pass {np.mean(o[v] == 'pass'):5.1%}, blown {np.mean(o[v] == 'fail'):5.1%}, "
              f"out of time {np.mean(o[v] == 'time'):5.1%}, median days to pass {np.median(nd[v & (o == 'pass')]):.0f}", flush=True)

    # ---------------- funded PA (the plan)
    lab.W["VB_F"] = lab.W["VB"] * flag[:, None]; lab.C["VB_F"] = lab.C["VB"] * flag
    lab.W["VB_N"] = lab.W["VB"] * ~flag[:, None]; lab.C["VB_N"] = lab.C["VB"] * ~flag
    Bp["VB_F"] = Bp["VB"] * flag[:, None]; Bp["VB_N"] = Bp["VB"] * ~flag[:, None]
    Bp["CLS"] = np.maximum(lab.W["CLS"], lab.C["CLS"][:, None] * np.ones((1, lab.W["CLS"].shape[1])))
    PLAN = {"VB_N": 3, "VB_F": 1, "ONB_ML2_MC": ("risk", 400), "MON_MC": 1, "EOS": ("risk", 700), "LDF_MC": 2, "NFP_MC": ("risk", 500), "MON_BR_MC": 1, "CLS": 2}
    names, b = lab._base(PLAN)
    Wf = np.ascontiguousarray(np.stack([lab.W[k] for k in names])); Bf = np.ascontiguousarray(np.stack([Bp[k] for k in names]))
    Cf = np.ascontiguousarray(np.stack([lab.C[k] for k in names])); b = np.ascontiguousarray(b)
    print("\n=== Funded PA (50K, consistency on), the plan with cushion sizing; every 2nd start day")
    print(f"{'cap':<34}{'1y paid':>10}{'blown':>7}{'1st payout (days)':>19}{'2y paid':>10}{'blown':>7}{'all 6':>7}")
    for dyn in (False, True):
        for X in (CAPS_X if not dyn else [500.0, 750.0, 1000.0]):
            row = []
            for h in (250, 500):
                st = np.arange(0, D - h, 2); o = pa_all(Wf, Bf, Cf, b, st, h, X, dyn)
                f1 = o[:, 3][o[:, 3] > 0]; row.append((o[:, 0].mean(), o[:, 2].mean(), np.median(f1) if len(f1) else np.nan, np.mean(o[:, 1] == 6)))
            lbl = ("none" if not np.isfinite(X) else f"${X:,.0f}") if not dyn else f"profit since payout, min ${X:,.0f}"
            print(f"{lbl:<34}{'$' + format(row[0][0], ',.0f'):>10}{row[0][1]:>7.0%}{row[0][2]:>19.0f}{'$' + format(row[1][0], ',.0f'):>10}{row[1][1]:>7.0%}{row[1][3]:>7.0%}", flush=True)
