"""How do 150K evaluations fail? (user 2026-11-09: 'develop a strategy specifically to bolster the eval phase'; diagnosis before design).
Information only. The current 150K evaluation set (VB 20 MNQ, ONB ADX30 risk $2,750, Bridge Monday 5, EOS risk $1,250, Twin cap1 2 MNQ;
bench150 / plan_150k_test.evaluation rules: +$9,000 target, $4,000 trailing floor that keeps trailing, intraday touch fails, $2,000
daily loss limit pauses the day, 21 trading days), every start day 2018-01 -> 2026-09. Per start: outcome and day; for fails, the day
number, the peak profit reached before failing, daily-loss-limit hits before the fail, the fail day's P&L by piece, and what the other
pieces did that day. Also the passes: days to pass and the worst open drawdown on the way.
  tools/run_stamped.sh analysis/eval_failure_diag.py > analysis/outputs/eval_failure_diag_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc
from twin_continuation_bench import grids
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from combine_levers_test import ONB30
from plan_150k_test import R150

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); trr = list(g.trading); D = len(trr); dts = pd.DatetimeIndex(g.ts[trr]); yr = dts.year
    B = tc.flatten(g); Tn = tc.simulate(B, max_stop_mult=1.0, v21=True); Tn = Tn[Tn.date >= "2018-01-01"]; Wt, Rt = grids(g, B, Tn)
    P = {}
    for k, t_ in {"VB": with_slippage(load_mc(g, REPORTS["VB"][0])), "ONB": with_slippage(load_mc(g, ONB30)), "MON_BR": load_bridge_mc(g),
                  "EOS": with_slippage(load_mc(g, REPORTS["EOS"][0]))}.items():
        w, rr = paths(g, t_); P[k] = (w[trr] / 10, rr[trr] / 10)
    P["TWIN"] = (Wt[trr] / 10, Rt[trr] / 10)
    atr = g.daily_atr(15); risk = lambda d, m_: np.floor(d / (np.nan_to_num(m_ * atr[trr], nan=1e12) * 2))[:, None]
    q = {"VB": 20.0, "ONB": risk(2750, 0.25), "MON_BR": 5.0, "EOS": risk(1250, REPORTS["EOS"][1]), "TWIN": 2.0}
    Wp = {k: P[k][0] * q[k] for k in P}; Rp = {k: P[k][1] * q[k] for k in P}
    W = sum(Wp.values()); R = sum(Rp.values()); r = R150; rows = []
    for s in range(D):
        if not (yr[s] >= 2018 and dts[s] <= pd.Timestamp("2026-09-01")) or s + 21 > D: continue
        bal = r["st"]; floor = r["st"] - r["dd"]; peak = 0.0; dll = 0; out = None
        for n, d in enumerate(range(s, s + 21), 1):
            w, rr = W[d], R[d]; lim = max(floor, bal - r["dll"])
            hit = np.nonzero(bal + w <= lim)[0]; jb = hit[0] if len(hit) else len(w)
            win = np.nonzero(bal + rr - r["st"] >= r["tgt"])[0]; jp = win[0] if len(win) else len(w)
            if jp < jb: out = ("pass", n, d, None); break
            if jb < len(w):
                if lim == floor: out = ("fail", n, d, jb); break
                bal = lim; dll += 1
            else: bal += rr[-1]
            peak = max(peak, bal - r["st"]); floor = max(floor, bal - r["dd"])
        if out is None: out = ("time", 21, s + 20, None)
        o, n, d, jb = out; rec = dict(start=dts[s], outcome=o, day=n, peak=peak, dll_hits=dll, end_bal=bal - r["st"])
        if o == "fail":
            for k in P: rec["fail_" + k] = Rp[k][d][min(jb, 1439)]
            rec["fail_floor_gap_start"] = bal - floor                      # room left at the start of the fail day
        rows.append(rec)
    X = pd.DataFrame(rows); n = len(X)
    print(f"\n   starts {n}: pass {np.mean(X.outcome == 'pass'):.1%}, fail {np.mean(X.outcome == 'fail'):.1%}, time-out {np.mean(X.outcome == 'time'):.1%}")
    Fx = X[X.outcome == "fail"]; Px = X[X.outcome == "pass"]
    print("\n1. When fails happen (trading day of the fail):", Fx.day.value_counts(bins=[0, 2, 5, 10, 15, 21]).sort_index().to_dict())
    print(f"   fails that were UP >= $4,500 (half the target) before failing: {np.mean(Fx.peak >= 4500):.0%}; up >= $2,000: {np.mean(Fx.peak >= 2000):.0%}; never up $1,000: {np.mean(Fx.peak < 1000):.0%}")
    print(f"   room to the floor at the start of the fail day: median ${Fx.fail_floor_gap_start.median():,.0f} (quartiles ${Fx.fail_floor_gap_start.quantile(.25):,.0f} / ${Fx.fail_floor_gap_start.quantile(.75):,.0f})")
    print(f"   fails with a daily-loss-limit pause before: {np.mean(Fx.dll_hits > 0):.0%}")
    print("\n2. The fail day, by piece (average $ at the fail minute; share of fail days the piece lost):")
    for k in P: print(f"   {k:<7} ${Fx['fail_' + k].mean():7,.0f}  lost on {np.mean(Fx['fail_' + k] < 0):.0%} of fail days")
    tot = sum(Fx["fail_" + k] for k in P); print(f"   total ${tot.mean():,.0f}; fail days where ONE piece lost > 70% of the day's loss: {np.mean(np.max(np.c_[[-Fx['fail_' + k] for k in P]].T, axis=1) > 0.7 * -tot):.0%}")
    print("\n3. Passes: days to pass", Px.day.describe()[["25%", "50%", "75%"]].to_dict(), f"| passes with a DLL pause on the way {np.mean(Px.dll_hits > 0):.0%}")
    print("   by year: pass / fail / time-out:", {y: f"{np.mean(X[X.start.dt.year == y].outcome == 'pass'):.0%} / {np.mean(X[X.start.dt.year == y].outcome == 'fail'):.0%} / {np.mean(X[X.start.dt.year == y].outcome == 'time'):.0%}" for y in range(2018, 2027)})
    # what kind of day helps: the set's daily P&L distribution
    dly = pd.Series(R[:, -1], index=dts)[(yr >= 2018)]
    print(f"\n4. The set's daily P&L (150K sizes): mean ${dly.mean():,.0f}, sd ${dly.std():,.0f}, days < -$2,000 {np.mean(dly < -2000):.1%}, days > +$2,000 {np.mean(dly > 2000):.1%}; "
          f"worst-intraday < -$4,000 on {np.mean(W[yr >= 2018].min(axis=1) < -4000):.1%} of days")
    print("   daily corr between pieces:", pd.DataFrame({k: Rp[k][:, -1] for k in P}, index=dts)[yr >= 2018].corr().round(2).to_dict())
