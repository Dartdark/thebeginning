"""Apex versions of the four capital-bench leads (user 2026-11-08: 'maybe they fit Apex better'). PRE-REGISTERED (header committed before the
run; 4 items on post hoc leads). All flat by the close:
  FVB shorts only (as is: out 15:11 CT)     S03 v2 longs only (Codex's v2_apex ledger)     Anson longs only (Codex's intended_apex ledger)
  S30 intraday: the day AFTER a cash-session IBS < 0.10 close, buy NQ at the 08:31 open, out at the 15:00 close, stop 0.5 x ATR15
    (S30 itself holds for days; this keeps only the next-day rebound) - standalone also vs random-day longs (same count per year, 500 runs)
Worst intraday path per trade: FVB / S30 from the 1-minute lows / highs, Codex ledgers from their observed MAE; per MNQ = per NQ / 10.
Benches: 150K evaluation (set + Twin 2 MNQ) + 2 MNQ each; funded 150K x 1.5 + Twin 2 + 2 MNQ each. Per NQ costs $7.25 + 1 tick per fill.
  tools/run_stamped.sh analysis/bench_leads_apex_test.py > analysis/outputs/bench_leads_apex_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from replica import is_early_close
from ingredient_ablation3 import line
from new_sources_150k import daypaths
import s30_ibs_test as S3
import bench150 as BB

PV, TICK, COMM = 20.0, 0.25, 7.25

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); ts = pd.DatetimeIndex(g.ts); L = {}
    f = pd.read_csv("checks/candidates/fvb/trades.csv", parse_dates=["date"]); f = f[(f.side < 0) & (f.date >= "2018-01-01")]
    adv = [min((np.nanmax(g.h[r.row, int(r.j0):int(r.j1) + 1]) - r.entry) * -1 * PV - (r.entry - r.exit) * PV + r.net, r.net) for r in f.itertuples()]
    L["FVB shorts"] = (f.date, np.array(adv), f.net.values)
    for nm, fl in (("S03 v2 longs", "s03_v2/codex_v2_apex_trades.csv"), ("Anson longs", "anson/codex_intended_apex_trades.csv")):
        t = pd.read_csv("checks/candidates/" + fl, parse_dates=["date"]); t = t[(t.side > 0) & (t.date >= "2018-01-01")]; q = t.qty if "qty" in t else 1.0
        net = (t.gross_nq - 17.25 * q).values; L[nm] = (t.date, np.minimum(-t.mae_points_observed.abs().values * PV * q - 17.25 * q, net), net)
    S = S3.sessions(g, "NQ"); S = S[S.date >= "2017-12-01"].reset_index(drop=True); pos = pd.Series(np.arange(len(ts)), index=ts)
    def nextday(days):
        rows = []
        for d in days:
            if d not in pos.index or is_early_close(d): continue
            r = int(pos[d])
            if np.isnan(atr[r]) or np.isnan(g.o[r, jof(831)]) or np.isnan(g.c[r, jof(1500)]): continue
            e = g.o[r, jof(831)] + TICK; sp = e - 0.5 * atr[r]; px = None; w = 0.0
            for j in range(jof(831), jof(1500) + 1):
                if np.isnan(g.c[r, j]): continue
                w = min(w, g.l[r, j] - e)
                if g.l[r, j] <= sp: px = min(g.o[r, j], sp) - TICK; break
            if px is None: px = g.c[r, jof(1500)] - TICK
            n_ = (px - e) * PV - COMM; rows.append((d, min(w * PV - COMM, n_), n_))
        return pd.DataFrame(rows, columns=["date", "adv", "net"])
    sig = [S.date[i + 1] for i in range(len(S) - 1) if S.full[i] and np.isfinite(S.ibs[i]) and S.ibs[i] < 0.10 and S.date[i + 1] >= pd.Timestamp("2018-01-01")]
    T = nextday(sig); L["S30 intraday (next day after IBS<0.10)"] = (T.date, T.adv.values, T.net.values)
    alld = nextday([d for d in S.date if d >= pd.Timestamp("2018-01-01")]).set_index("date").net; cnt = T.groupby(T.date.dt.year).size(); rng = np.random.default_rng(53)
    pm = [np.mean(np.concatenate([alld[alld.index.year == y].sample(n, random_state=int(rng.integers(1e9))).values for y, n in cnt.items()])) for _ in range(500)]
    print("\n   standalone (per NQ, flat by the close):")
    for nm, (d, a, n) in L.items(): print(line(n, d, nm))
    print(f"   S30 intraday vs random-day longs (same exits): ${np.mean(pm):.0f}, 95th ${np.percentile(pm, 95):.0f}; real ${T.net.mean():.0f}; p {np.mean(np.array(pm) >= T.net.mean()):.3f}", flush=True)
    ctx = BB.setup(); dts, D = ctx["dts"], ctx["D"]; dp = pd.Series(np.arange(D), index=dts); P = {}
    for nm, (d, a, n) in L.items(): P[nm] = daypaths(D, [(int(dp[x]) if x in dp.index else None, aa, nn) for x, aa, nn in zip(pd.DatetimeIndex(d), a, n)])
    print(); BB.eval_bench(ctx, {f"+ {nm} 2 MNQ": (2 * W, 2 * R) for nm, (W, R) in P.items()})
    lab = ctx["lab"]
    for nm, (W, R) in P.items(): lab.W[nm] = W; lab.C[nm] = R[:, -1]
    print(); BB.funded_bench(ctx, {f"+ {nm} 2 MNQ": {**BB.BASE_FUNDED, nm: 2} for nm in P})
