"""TPO single prints as a day-type flag (Red Ledger Research, field study RL-FS-2026-01, "Single Prints Mark the Day, Not the
Level", Sept 2026), replicated on our NQ 2018-2026 and tested as a filter on the plan.

Paper: NQ 2017-24, 30-min TPO of the 9:30-16:00 ET session (13 periods). Interior single print = a run of >= 8 ticks printed by
exactly one period, not containing the session high / low; flag the NEXT session (31% of days). Single prints are not levels
(0 of 21 tests beat distance-matched placebos), but the flagged session overlaps prior value more (56.5% vs 49.3%), is less
directional (|close - open| / range 0.469 vs 0.492) and ~17% narrower than prior volatility predicts (controlled for prior-day
range and efficiency terciles). Suggested use: stand aside / smaller size on breakout / open-drive strategies on flagged days.
Here (CT = ET - 1h): RTH bars closing 8:31 .. 15:00 CT; value area = 70% of 1-minute volume spread evenly over each bar's range.
  A  replication: flag rate; next-session value overlap, efficiency, range / 20-day average; raw and within prior-day
     range x efficiency terciles; by era (2018-19, 2020-22, 2023-26)
  B  the plan's MultiCharts trades (per contract, $7.25 + 1 tick a market / stop fill), flagged vs other sessions, by strategy;
     pre-registered: the breakout strategies (VB, ONB ML) earn less on flagged sessions; design 2018-22 / holdout 2023-26
  C  the paper's responsive idea: at 9:00 CT, if NQ is outside the prior value area, trade back toward the prior POC (target the
     POC, stop the same distance away, out 15:00), flagged vs other sessions
  python3 analysis/single_print_test.py [SCRATCH_DIR]
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from co_oc_reversal_test import load
import metrics as M, resampling as R

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
TK = 4  # ticks per point


def session(g, r):
    j0, j1 = jof(831), jof(1500)
    h, l, c, o, v = g.h[r, j0:j1 + 1], g.l[r, j0:j1 + 1], g.c[r, j0:j1 + 1], g.o[r, j0:j1 + 1], g.v[r, j0:j1 + 1]
    if np.isnan(c).mean() > 0.05 or np.isnan(c[-1]) or np.isnan(o[0]): return None
    lo = int(round(np.nanmin(l) * TK)); hi = int(round(np.nanmax(h) * TK)); n = hi - lo + 1
    cov = np.zeros(n + 1, int); allp = True
    for p in range(13):
        ph, pl = h[30 * p:30 * p + 30], l[30 * p:30 * p + 30]
        if np.isnan(ph).all(): allp = False; continue
        a = int(round(np.nanmin(pl) * TK)) - lo; b = int(round(np.nanmax(ph) * TK)) - lo
        cov[a] += 1; cov[b + 1] -= 1
    cov = np.cumsum(cov)[:n]
    single = cov == 1; sp = False; k = 0
    while k < n:
        if single[k]:
            e = k
            while e + 1 < n and single[e + 1]: e += 1
            if e - k + 1 >= 8 and k > 0 and e < n - 1: sp = True; break
            k = e + 1
        else: k += 1
    vol = np.zeros(n + 1)
    for hh, ll, vv in zip(h, l, v):
        if np.isnan(hh) or np.isnan(vv) or vv <= 0: continue
        a = int(round(ll * TK)) - lo; b = int(round(hh * TK)) - lo
        vol[a] += vv / (b - a + 1); vol[b + 1] -= vv / (b - a + 1)
    vol = np.cumsum(vol)[:n]; poc = int(np.argmax(vol)); va = vol[poc]; a = b = poc; tot = vol.sum()
    while va < 0.7 * tot and (a > 0 or b < n - 1):
        up = vol[b + 1] if b < n - 1 else -1; dn = vol[a - 1] if a > 0 else -1
        if up >= dn: b += 1; va += up
        else: a -= 1; va -= -dn
    cl = c[~np.isnan(c)][-1]
    return dict(open=o[0], close=cl, hi=hi / TK, lo=lo / TK, sp=sp and allp, poc=(lo + poc) / TK, val=(lo + a) / TK,
                vah=(lo + b) / TK, rng=(hi - lo) / TK, eff=abs(cl - o[0]) / max((hi - lo) / TK, 0.25))


def frame():
    g = load("NQ"); rows = {}
    for r in g.trading:
        s = session(g, r)
        if s: rows[pd.Timestamp(g.ts[r])] = dict(s, r=r)
    S = pd.DataFrame(rows).T.apply(pd.to_numeric); S = S[S.index >= "2017-11-01"]
    S["flag"] = S.sp.shift(1).fillna(0).astype(bool)
    S["overlap"] = (S.val <= S.vah.shift(1)) & (S.vah >= S.val.shift(1))
    S["rr"] = S.rng / S.rng.rolling(20).mean().shift(1)
    S["p_rr"] = S.rr.shift(1); S["p_eff"] = S.eff.shift(1)
    return g, S.iloc[21:]


def controlled(S, col):
    """flagged - other, within prior-day range x efficiency terciles, weighted by flagged counts."""
    d = S.dropna(subset=["p_rr", "p_eff", col]).copy()
    d["c"] = pd.qcut(d.p_rr, 3, labels=False).astype(str) + pd.qcut(d.p_eff, 3, labels=False).astype(str)
    diff, w = [], []
    for _, x in d.groupby("c"):
        a, b = x[x.flag][col], x[~x.flag][col]
        if len(a) >= 5 and len(b) >= 5: diff.append(a.mean() - b.mean()); w.append(len(a))
    return np.average(diff, weights=w)


def boot_ci(S, col, n=1000, seed=1):
    rng = np.random.default_rng(seed); idx = np.arange(len(S)); out = []
    for _ in range(n): out.append(controlled(S.iloc[rng.choice(idx, len(idx))], col))
    return np.percentile(out, [2.5, 97.5])


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(__doc__.split("\n")[0])
    g, S = frame()
    print(f"\nA. {len(S)} sessions {S.index[0].date()} .. {S.index[-1].date()}; flagged {S.flag.mean():.0%} (paper 31%)")
    era = pd.cut(S.index.year, [2000, 2019, 2022, 2100], labels=["2018-19", "2020-22", "2023-26"])
    for col, nm in (("overlap", "value overlaps prior value"), ("eff", "efficiency |C-O| / range"), ("rr", "range / 20-day avg")):
        a, b = S[S.flag][col].astype(float), S[~S.flag][col].astype(float); lo, hi = boot_ci(S.assign(**{col: S[col].astype(float)}), col, n=300)
        eras = [controlled(S[era == e].assign(**{col: S[col].astype(float)}), col) for e in ("2018-19", "2020-22", "2023-26")]
        print(f"   {nm:<28} flagged {a.mean():.3f}  other {b.mean():.3f}  controlled {controlled(S.assign(**{col: S[col].astype(float)}), col):+.3f}"
              f" [{lo:+.3f}, {hi:+.3f}]  by era {' '.join(f'{e:+.3f}' for e in eras)}")

    print("\nB. Plan trades (MultiCharts lists), flagged vs other sessions (net $ per contract)")
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        T = runpy.run_path("analysis/plan_agreement_test.py", run_name="__main__")["T"]
    sess = S.index; pos = np.searchsorted(sess, T.date)          # session on / after the entry date (Sunday -> Monday)
    ok = pos < len(sess); T = T[ok].copy(); T["flag"] = S.flag.to_numpy()[pos[ok]]
    T["sess"] = sess[pos[ok]]
    rows = []
    for s_, x in T.groupby("strat"):
        a, b = x[x.flag].net, x[~x.flag].net
        t = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
        dz = lambda m: x[m & x.flag].net.mean() - x[m & ~x.flag].net.mean()
        rows.append(dict(strat=s_, n_flag=len(a), n_other=len(b), flagged=a.mean(), other=b.mean(), t=t,
                         design_diff=dz(x.date.dt.year < 2023), holdout_diff=dz(x.date.dt.year >= 2023)))
    print(pd.DataFrame(rows).round(1).to_string(index=False))

    print("\nC. Responsive: at 9:00 CT outside the prior value area -> toward the prior POC (target POC, stop = same distance, out 15:00)")
    res = {}
    for d, s in S.iterrows():
        r = int(s.r); prev = S.index.get_loc(d) - 1
        if prev < 0: continue
        p = S.iloc[prev]; pe = g.c[r, jof(900)]
        if np.isnan(pe) or p.val <= pe <= p.vah: continue
        side = 1 if pe < p.val else -1; dist = abs(p.poc - pe)
        if dist < 10: continue
        tp, sp_ = p.poc, pe - side * dist; out = None
        for j in range(jof(901), jof(1500) + 1):
            if np.isnan(g.c[r, j]): continue
            if (side > 0 and g.l[r, j] <= sp_) or (side < 0 and g.h[r, j] >= sp_): out = (sp_ - pe) * side - 0.25; break
            if (side > 0 and g.h[r, j] >= tp + 0.25) or (side < 0 and g.l[r, j] <= tp - 0.25): out = (tp - pe) * side; break
        if out is None: out = (g.c[r, jof(1500)] - pe) * side - 0.25
        res[d] = dict(net=out * 20 - 7.25 - 5.0, flag=s.flag, side=side)
    C = pd.DataFrame(res).T; C["net"] = C.net.astype(float); C["flag"] = C.flag.astype(bool)
    for nm, x in (("flagged", C[C.flag]), ("other", C[~C.flag])):
        n = x.net; y = n.index.year
        print(f"   {nm:<8} n {len(n):4d} avg ${n.mean():6.1f} t {n.mean() / n.std() * np.sqrt(len(n)):4.1f} win {np.mean(n > 0):.0%}"
              f" | 2018-22 ${n[y < 2023].mean():6.1f} 2023-26 ${n[y >= 2023].mean():6.1f}")
    x = C[C.flag].net; days = pd.Series(0.0, index=S.index)
    rws = {"all": (days.add(x, fill_value=0), x)}
    for nm, sd in (("longs", 1), ("shorts", -1)):
        xs = C[C.flag & (C.side == sd)].net.astype(float); rws[nm] = (days.add(xs, fill_value=0), xs)
    print("\n   flagged-day responsive trade, standard metrics:"); print(M.table(rws))
    b_, p_ = R.report({k: v[0][v[0].index >= "2023"] for k, v in rws.items()}, n=2000)
    print("\n2023+ bootstrap:\n" + b_ + "\n\n2023+ drawdown permutation:\n" + p_)
    S.to_pickle(SP + "single_print_sessions.pkl"); T.to_pickle(SP + "single_print_trades.pkl")
