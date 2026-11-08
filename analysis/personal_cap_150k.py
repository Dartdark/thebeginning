"""Personal-only strategies with a capped stop, added to the 150K EVALUATION (user 2026-11-08: 'like Twin'). PRE-REGISTERED (header
committed before the first run). Pieces (intraday, Apex-legal, MultiCharts trade lists 2018+): FC 2B v2, Dual Thrust v4, PaperTrend v2
(Claude's code), S47 v2, Swing Target v3. Not tested here: Overnight Tick (overnight path; already in the 150K funded plan), Kusho v9
and S30 (multi-day holds, not Apex-legal).
Cap: every trade's stop at most 0.25 x the 15-day daily ATR (prior day; ONB's stop size): replay each trade on 1-minute bars from its
entry minute to its exit minute; the first minute beyond entry -/+ cap exits there (gap: at the minute's open). Costs: repo costs via
funded_lab.with_slippage + portfolio.paths ($7.25 + 1 tick per fill). Bench: 150K evaluation set (VB 20, ONB ADX30 $2,750, Bridge 5,
EOS $1,250) + each piece at 2 / 4 MNQ, original vs capped; corrected engine; paired pass difference, 60-day blocks.
  tools/run_stamped.sh analysis/personal_cap_150k.py > analysis/outputs/personal_cap_150k_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30
from plan_150k_test import evaluation, R150
from grid24 import jof

FILES = {"FC 2B v2": "checks/candidates/fc_2b/mc_v2_trades_all.csv", "Dual Thrust v4": "checks/candidates/dual_thrust/mc_trades.csv",
         "PaperTrend v2": "checks/candidates/papertrend/mc_trades_claude.csv", "S47 v2": "checks/candidates/s47_v2/mc_trades_S47_v2.csv",
         "Swing Target v3": "checks/candidates/swing_target/mc_trades_v3.csv"}


def frame(g, f):
    t = pd.read_csv(f); t = t[(t.date >= "2018-01-01") & (t.date == t.exit_date)].reset_index(drop=True)
    row = np.searchsorted(g.dates, pd.to_datetime(t.date).dt.strftime("%Y%m%d").astype(int).to_numpy())
    return pd.DataFrame(dict(day=row, j0=jof(t.t_in.to_numpy()), j1=jof(t.t_out.to_numpy()), side=t.side.to_numpy(),
                             entry=t.entry.to_numpy(), exit=t.exit.to_numpy(), kind=np.where(t.kind.str.contains("T|Target|LT|ST", regex=True) & ~t.kind.str.contains("Stop|SL|eod|XL|LX|SX", regex=True), 1, 2)))


def cap(g, t, atr):
    t = t.copy(); n = 0
    for k in range(len(t)):
        r, j0, j1, s, e = int(t.day[k]), int(t.j0[k]), int(t.j1[k]), int(t.side[k]), t.entry[k]
        a = atr[r - 1] if r > 0 else np.nan
        if not np.isfinite(a): continue
        st = e - s * 0.25 * a; lo = g.l[r, j0:j1 + 1]; hi = g.h[r, j0:j1 + 1]; op = g.o[r, j0:j1 + 1]
        hit = np.nonzero(lo <= st)[0] if s > 0 else np.nonzero(hi >= st)[0]
        if len(hit):
            m = hit[0]; px = (min(op[m], st) if s > 0 else max(op[m], st))
            if (px - e) * s < (t.exit[k] - e) * s or (j0 + m) < j1:
                t.loc[k, ["exit", "j1", "kind"]] = [px, j0 + m, 0]; n += 1
    return t, n


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); trr = g.trading; D = len(trr); yr = pd.DatetimeIndex(g.ts[trr]).year
    P = {}
    for k, t in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB30": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
                 "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, rr = paths(g, t); P[k] = (w[trr] / 10, rr[trr] / 10)
    risk = lambda d, m: np.floor(d / (np.nan_to_num(m * atr[trr], nan=1e12) * 2))[:, None]
    base = {"VB": 20.0, "ONB30": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1])}
    Wb = sum(P[k][0] * v for k, v in base.items()); Rb = sum(P[k][1] * v for k, v in base.items()); ok = yr >= 2018
    def ev(Wx, Rx):
        res = [evaluation(Wb + Wx, Rb + Rx, s, D, R150) for s in range(D)]
        return np.array([x[0] if x else "" for x in res]), ok & np.array([x is not None for x in res])
    o0, v0 = ev(0.0 * Wb, 0.0 * Rb)
    def boot(o, v):
        d = ((o == "pass").astype(float) - (o0 == "pass").astype(float))[v & v0]; rng = np.random.default_rng(1); nb = int(np.ceil(len(d) / 60))
        st = rng.integers(0, len(d), (2000, nb)); m = d[((st[:, :, None] + np.arange(60)) % len(d)).reshape(2000, -1)[:, :len(d)]].mean(axis=1)
        return d.mean(), np.percentile(m, 5), np.percentile(m, 95)
    ps0 = o0 == "pass"
    print(f"\n150K evaluation set alone: pass {ps0[v0].mean():.1%} (18-22 {ps0[v0 & (yr < 2023)].mean():.1%}, 23+ {ps0[v0 & (yr >= 2023)].mean():.1%})")
    for nm, f in FILES.items():
        t0 = frame(g, f); tc_, ncap = cap(g, t0, atr)
        net = lambda t: (with_slippage(t).eval("(exit - entry) * side") * 20 - 7.25)
        n0, n1 = net(t0), net(tc_)
        tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x))
        print(f"\n{nm}: {len(t0)} trades; original ${n0.mean():.0f} (t {tt(n0):.2f}, worst ${n0.min():,.0f}); capped ${n1.mean():.0f} (t {tt(n1):.2f}, worst ${n1.min():,.0f}); {ncap} trades cut by the cap")
        for lab, t in (("original", t0), ("capped", tc_)):
            w, rr = paths(g, with_slippage(t)); W1, R1 = w[trr] / 10, rr[trr] / 10
            for q in (2, 4):
                o, v = ev(q * W1, q * R1); ps = o == "pass"; m, lo, hi = boot(o, v)
                print(f"   + {q} MNQ {lab:<8}: pass {ps[v].mean():5.1%} (18-22 {ps[v & (yr < 2023)].mean():5.1%}, 23+ {ps[v & (yr >= 2023)].mean():5.1%}) fail {(o[v] == 'fail').mean():5.1%}"
                      f" | vs set {m:+.1%} ({lo:+.1%} / {hi:+.1%})", flush=True)
