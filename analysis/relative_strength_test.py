"""Relative Strength NQ / ES (user's RelStrength_v3 + research note, 2026-10-20): independent Python rebuild and checks.
Code and note: checks/candidates/relative_strength/ (RelStrength_v3.txt, Relative_Strength_research_note.pdf).

Rule (from the code): 1-minute RTH bars 8:31-15:00 CT. Beta of NQ on ES and the residual variance = exponential averages
(alpha 2 / (20 x 390 + 1)) of 1-minute RTH log returns in bp, over NYSE full and early-close days excluded. At the 9:00 bar:
Z = (NQ log move since the 8:30 close - beta x ES's) / sqrt(residual variance x 30). Z >= 1.25 buy, <= -1.25 short, market at
the 9:01 open; stop 0.6 x and target 1.0 x the average 8:30-15:00 range of the last 20 clean days, active from 9:02; flat at
the 15:00 close. One trade a day.

Pre-registered checks (written before running, 2026-10-20):
  R  replica vs the note: 1,290 trades 2017-26, PF 1.37 gross, longs PF 1.46 / shorts 1.29, 52% win, every year positive.
  Costs: $7.25 + 1 tick ($5) per market / stop fill (target limits: no slippage). Limit fills on touch (MultiCharts default);
     sensitivity: limits need a 1-tick trade-through.
  P1 random side on the same days (500 runs).
  P2 own momentum: the same rule with beta = 0 (Z = NQ's own move / its own 1-minute spread): does removing ES add anything?
  P3 market part: trade NQ in the direction of beta x ES's move only (Z of the ES-explained part, same threshold).
  Split: RS trades where NQ's own 8:30-9:00 move has the same sign as the trade vs the opposite sign (the opposite-sign
     trades are the only ones that are purely 'relative').
  Neighbours (robustness, counted as trials): Z 1.0 / 1.5 / 2.0, decide 9:15 / 9:30.
  Metrics by side, 2023+ bootstrap (resampling), Monte Carlo at 1 MNQ, deflated Sharpe at the trials-log N.
  python3 analysis/relative_strength_test.py [SCRATCH_DIR]          (needs g24.pkl, ge.pkl)
"""
import sys, re, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
import metrics as M, montecarlo as MC

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
CODE = "checks/candidates/relative_strength/RelStrength_v3.txt"
PV, TICK, COMM = 20.0, 0.25, 7.25
N_LOG = 297


def holidays():
    txt = open(CODE).read(); return {int(x) + 19000000 for x in re.findall(r"Hol(?:Full|Early)\[\d+\] = (\d{7})", txt)}


def load():
    g = pickle.load(open(SP + "g24.pkl", "rb")); e = pickle.load(open(SP + "ge.pkl", "rb"))
    hol = holidays(); rows = []
    ei = {int(d): k for k, d in enumerate(e.dates)}
    a, b = jof(830), jof(1500)
    for d in g.trading:
        dt = int(g.dates[d])
        if dt < 20170901 or dt not in ei: continue
        k = ei[dt]
        if np.isnan(g.c[d, a + 1:b + 1]).all() or np.isnan(e.c[k, a + 1:b + 1]).all(): continue
        rows.append((d, k, dt, dt not in hol and g.last_j[d] >= b and e.last_j[k] >= b))
    days = pd.DataFrame(rows, columns=["d", "k", "date", "ok"])
    f = lambda x: pd.DataFrame(x).ffill(axis=1).to_numpy()
    N = {c: f(getattr(g, c)[days.d.to_numpy(), a:b + 1]) for c in ("o", "h", "l", "c")}   # col 0 = 8:30 bar
    E = f(e.c[days.k.to_numpy(), a:b + 1])
    N["o"] = np.where(np.isnan(N["o"]), N["c"], N["o"])
    return days, N, E


def signals(days, N, E, decide=900, beta_mode="rel"):
    """Z at the decide bar for every day (NaN where no check), replaying the EWMA over RTH bars of OK days."""
    alpha = 2 / (20 * 390 + 1); cov = v1 = v2 = 0.0; nest = 0; beta = res = 0.0
    jd = jof(decide) - jof(830); Z = np.full(len(days), np.nan)
    ra = 10000 * np.log(N["c"][:, 1:] / N["c"][:, :-1]); rb = 10000 * np.log(E[:, 1:] / E[:, :-1])   # bar t = col t+1
    ok = days.ok.to_numpy()
    for i in range(len(days)):
        if ok[i]:
            for t in range(390):
                x, y = ra[i, t], rb[i, t]
                if not (np.isfinite(x) and np.isfinite(y)): continue
                if nest == 0: cov, v1, v2 = x * y, x * x, y * y
                else: cov += alpha * (x * y - cov); v1 += alpha * (x * x - v1); v2 += alpha * (y * y - v2)
                nest += 1
                if v1 > 0 and v2 > 0: beta = cov / v2; res = v1 - 2 * beta * cov + beta * beta * v2
                if t + 1 == jd and nest >= 5 * 390 and res > 0:
                    mn = 10000 * np.log(N["c"][i, jd] / N["c"][i, 0]); me = 10000 * np.log(E[i, jd] / E[i, 0])
                    if beta_mode == "rel": Z[i] = (mn - beta * me) / np.sqrt(res * jd)
                    elif beta_mode == "own": Z[i] = mn / np.sqrt(v1 * jd)
                    elif beta_mode == "mkt": Z[i] = beta * me / np.sqrt(beta * beta * v2 * jd)
        # days that are not OK are not checked (the code requires DayOK at the decision)
    return Z


def trades(days, N, Z, zmin=1.25, decide=900, through=0.0, stop_f=0.6, tgt_f=1.0):
    rng_ = N["h"][:, 1:].max(1) - N["l"][:, 1:].min(1); ok = days.ok.to_numpy()
    hist, out = [], []; jd = jof(decide) - jof(830)
    for i in range(len(days)):
        avg = np.mean(hist[-20:]) if hist else np.nan
        z = Z[i]
        if ok[i] and np.isfinite(z) and abs(z) >= zmin and np.isfinite(avg) and jd + 1 <= 389:
            s = 1 if z > 0 else -1; e = N["o"][i, jd + 1]; sp = e - s * stop_f * avg; tp = e + s * tgt_f * avg
            x, kind = None, "flat"
            for t in range(jd + 2, 391):
                o, h, l = N["o"][i, t], N["h"][i, t], N["l"][i, t]
                if s > 0:
                    if l <= sp: x, kind = (min(o, sp), "stop"); break
                    if h >= tp + through: x, kind = (max(o, tp), "target"); break
                else:
                    if h >= sp: x, kind = (max(o, sp), "stop"); break
                    if l <= tp - through: x, kind = (min(o, tp), "target"); break
            if x is None: x = N["c"][i, 390]
            cost = COMM + TICK * PV * (1 if kind == "target" else 2)
            out.append((pd.Timestamp(str(days.date[i])), s, z, e, x, kind, (x - e) * s * PV, (x - e) * s * PV - cost))
        if ok[i]: hist.append(rng_[i])
    return pd.DataFrame(out, columns=["date", "side", "z", "entry", "exit", "kind", "gross", "pnl"])


def tstat(x): x = np.asarray(x, float); return x.mean() / x.std(ddof=1) * np.sqrt(len(x))


def line(nm, t, col="pnl"):
    x = t[col]; yr = t.groupby(t.date.dt.year)[col].sum(); gp, gl = x[x > 0].sum(), -x[x < 0].sum()
    h = t[t.date >= "2023"][col]; dsn = t[t.date < "2023"][col]
    print(f"   {nm:<44} n {len(t):4d}  ${x.mean():5.0f}  PF {gp / gl:4.2f}  t {tstat(x):4.1f}  win {(x > 0).mean():.0%}  "
          f"yrs+ {(yr > 0).sum()}/{len(yr)} | <2023 ${dsn.mean():.0f} (t {tstat(dsn):.1f})  2023+ ${h.mean():.0f} (t {tstat(h):.1f})")


def daily(t, idx):
    s = pd.Series(0.0, index=idx); g = t.groupby("date").pnl.sum(); s.loc[g.index] = g.values; return s


if __name__ == "__main__":
    days, N, E = load(); idx = pd.DatetimeIndex([pd.Timestamp(str(x)) for x in days.date])
    print(f"days {len(days)} ({days.date.iloc[0]} .. {days.date.iloc[-1]}), OK {days.ok.sum()}")
    Z = signals(days, N, E); T = trades(days, N, Z)
    print("\nR  Replica (note: 1,290 trades 2017-26, PF 1.37 gross, longs 1.46 / shorts 1.29, 52% win)")
    line("gross (no costs), all", T, "gross"); line("net, all", T)
    line("net, longs", T[T.side > 0]); line("net, shorts", T[T.side < 0])
    print("   exits:", T.groupby("kind").pnl.agg(["count", "mean"]).round(0).to_dict("index"))
    print("   by year (net $):", T.groupby(T.date.dt.year).pnl.sum().round(0).to_dict())
    Tt = trades(days, N, Z, through=TICK); line("net, limits need 1-tick trade-through", Tt)
    rng = np.random.default_rng(3); real = T.pnl.mean()
    Tf = trades(days, N, -Z)                                        # every signal day traded the other way (exits redone)
    both = T.merge(Tf[["date", "pnl"]], on="date", suffixes=("", "_flip"))
    hits = 0
    for _ in range(500):
        m = rng.random(len(both)) < 0.5; hits += np.where(m, both.pnl, both.pnl_flip).mean() >= real
    print(f"\nP1 random side on the same days: real ${real:.0f}, opposite side ${both.pnl_flip.mean():.0f}, p = {(hits + 1) / 501:.3f}")
    print("\nP2 / P3 controls (same exits, same threshold 1.25)")
    Zo = signals(days, N, E, beta_mode="own"); To = trades(days, N, Zo); line("P2 own momentum (beta = 0)", To)
    Zm = signals(days, N, E, beta_mode="mkt"); Tm = trades(days, N, Zm); line("P3 market part (beta x ES move)", Tm)
    own = pd.Series(np.sign(10000 * np.log(N["c"][:, 30] / N["c"][:, 0])), index=idx)
    T["own_same"] = own.reindex(T.date).to_numpy() == T.side.to_numpy()
    line("RS trades, NQ's own move same sign", T[T.own_same]); line("RS trades, NQ's own move OPPOSITE sign", T[~T.own_same])
    ov = T.date.isin(To.date).mean(); print(f"   share of RS days that the own-momentum rule also trades: {ov:.0%}")
    print("\nNeighbours")
    for z in (1.0, 1.5, 2.0): line(f"Z {z}", trades(days, N, Z, zmin=z))
    for dc in (915, 930): line(f"decide {dc}", trades(days, N, signals(days, N, E, decide=dc), decide=dc))
    print("\nMetrics (1 NQ, net)")
    rows = {"both": (daily(T, idx), T.pnl), "long": (daily(T[T.side > 0], idx), T[T.side > 0].pnl),
            "short": (daily(T[T.side < 0], idx), T[T.side < 0].pnl)}
    print(M.table(rows))
    h = daily(T, idx); h = h[h.index >= "2023"]; print(f"   2023+: Sharpe {M.perf(h)['sharpe']:.2f}")
    for n in (1, N_LOG): print(f"   DSR at N={n}: {M.deflated_sharpe(T.pnl, n):.3f}")
    print(f"   t bar at N={N_LOG}: {M.t_threshold(N_LOG):.2f}")
    print(MC.report(T.pnl.to_numpy(), daily(T, idx).to_numpy(), size=0.1, label="RS 1 MNQ"))
    print(MC.report(T.pnl.to_numpy(), daily(T, idx).to_numpy(), size=1.0, label="RS 1 NQ", trail=20000))
    T.to_csv(SP + "rs_trades.csv", index=False)
