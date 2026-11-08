"""Ingredient ablation, round 6: the capital-expansion bench (user 2026-11-08: 'before removing any, see if they can be improved').
Information only (historical component evidence; any improvement found here is post hoc and needs its own pre-registered test and the
book). Pieces with a local rebuild: FVB, Ricochet 1144, DriftPullBack v3, RollZone 24h, S30 IBS, Prior VWAP Trap (its level placebo is
already in checks/candidates/prior_vwap_trap/REVIEW.md: shown, not rerun). Swing Target: round 5. Anson / R2Vault / S03 v2: Codex's code
(no local rebuild). Per contract after the repo costs; 2018-26 and both periods; total $ and max DD. Ricochet loads g24_ext.pkl, linked
here to g24.pkl (NQ to 2026-11-04).
  FVB: no regime skip (prior range / premarket caps off) / no strong-day short block / 1 trade a day / stop 0.36 ATR / entry window 60 /
       240 min / longs only / shorts only
  Ricochet: no re-entries / after an up day (placebo) / every session / stop 100 / target 50
  DriftPullBack v3: no drift condition (0) / drift 0.20 / 1 trade a day / longs only / shorts only / target = stop (80)
  RollZone (plain 0.8 ATR stop): no zone (noise 0) / night entries off / target 0.7 ATR / no target (3 ATR) / stop 0.4 ATR
  S30 IBS (NQ): entry IBS < 0.10 / < 0.30 / exit IBS > 0.50 / exit next close (1-day hold) / IBS < 0.2 only after a down day
  tools/run_stamped.sh analysis/ingredient_ablation6.py > analysis/outputs/ingredient_ablation6_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from ingredient_ablation3 import line


def show(nm, net, dates): print(line(np.asarray(net, float), pd.DatetimeIndex(dates), nm), flush=True)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    # ---------------- FVB
    import fvb_test as FV
    NQ = FV.Frame("NQ"); print("\n1. FVB (check: bench file checks/candidates/fvb/trades.csv):")
    for nm, kw in (("as is", {}), ("no regime skip", dict(max_pr=99, max_pm=99)), ("no strong-day short block", dict(strong_th=99)), ("1 trade a day", dict(max_tr=1)),
                   ("stop 0.36 ATR", dict(stop_frac=0.36)), ("entry window 60 min", dict(window=60)), ("entry window 240 min", dict(window=240))):
        t = FV.run(NQ, count=False, **kw); t = t[t.index >= "2018-01-01"]; show(nm, t.net, t.index)
    t = FV.run(NQ, count=False); t = t[t.index >= "2018-01-01"]; show("longs only", t[t.side > 0].net, t[t.side > 0].index); show("shorts only", t[t.side < 0].net, t[t.side < 0].index)
    # ---------------- Ricochet
    import ricochet_1144_test as RC
    print("\n2. Ricochet 1144 (check: bench file checks/candidates/ricochet_1144/python_trades.csv):")
    for nm, kw in (("as is", {}), ("no re-entries", dict(reentry=False)), ("after an up day (placebo)", dict(signal="green")), ("every session", dict(signal="all")),
                   ("stop 100", dict(stop=100.0)), ("target 50", dict(target=50.0))):
        t = RC.run(**kw); t = t[pd.to_datetime(t.date) >= "2018-01-01"]; show(nm, t.net, pd.to_datetime(t.date))
    # ---------------- DriftPullBack v3
    import drift_pullback_test as DP
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); P = DP.prep(g); base = dict(window=99, start=900, end=1430, flat=1455, slip_ticks=1)
    print("\n3. DriftPullBack v3:")
    for nm, kw in (("as is", {}), ("no drift condition", dict(drift=0.0)), ("drift 0.20%", dict(drift=0.20)), ("1 trade a day", dict(max_tr=1)),
                   ("longs only", dict(shorts=False)), ("shorts only", dict(longs=False)), ("target = stop (80)", dict(ltp=80.0, stp=80.0))):
        t = DP.run(g, P, **{**base, **kw}); show(nm, t.net, t.date)
    # ---------------- RollZone
    import rollzone_24h_test as RZ, s_rank_gap_round2_test as SG
    gz = RZ.grid(); B = RZ.bars5_aligned(gz); S = SG.Sym("NQ", gz); rolls, _ = SG.rolls_index(S)
    print("\n4. RollZone 24h (plain 0.8 ATR stop):")
    for nm, kw in (("as is", {}), ("no zone (noise 0)", dict(noise=0.0)), ("night entries off", dict(night=False)), ("target 0.7 ATR", dict(tgt_atr=0.7)),
                   ("no target (3 ATR)", dict(tgt_atr=3.0)), ("stop 0.4 ATR", dict(stp_atr=0.4))):
        t = RZ.run(gz, B, cap_pts=750.0, rolls=rolls, **kw); t = t[(t.date >= "2018-01-01") & ~t.roll]; show(nm, t.net, t.date)
    # ---------------- S30 IBS (NQ)
    import s30_ibs_test as S3
    from overnight_round import roll_minutes
    print("\n5. S30 IBS, NQ (long; buy 15:01 when IBS < 0.2, sell 15:01 when IBS > 0.8; no stop):")
    S = S3.sessions(g, "NQ"); S = S[S.date >= "2017-12-01"].reset_index(drop=True); rl = np.sort(roll_minutes(g, "NQ")); C = g.c.ravel()
    S["down"] = S.c15 < S.c15.shift(1)
    def s30(lo=0.2, hi=0.8, hold1=False, need_down=False):
        out = []; pos = 0
        for i, x in S.iterrows():
            if not x.full or not np.isfinite(x.ibs) or not np.isfinite(x.nxt) or x.hi <= x.lo: continue
            if pos == 0 and x.ibs < lo and (not need_down or x.down): pos = 1; e = x.nxt + 0.25; ei = i
            elif pos == 1 and ((x.ibs > hi) or hold1):
                px = x.nxt - 0.25; gross = px - e; m0, m1 = S.r[ei] * 1440 + jof(1501), x.r * 1440 + jof(1501)
                for j in rl[(rl > m0) & (rl <= m1)]:
                    p = j - 1
                    while not np.isfinite(C[p]): p -= 1
                    gross -= C[j] - C[p]
                out.append((S.date[ei], gross * 20 - 7.25)); pos = 0
        T = pd.DataFrame(out, columns=["date", "net"]); return T[T.date >= "2018-01-01"]
    for nm, kw in (("as is", {}), ("entry IBS < 0.10", dict(lo=0.10)), ("entry IBS < 0.30", dict(lo=0.30)), ("exit IBS > 0.50", dict(hi=0.50)),
                   ("exit next close (1-day hold)", dict(hold1=True)), ("only after a down close", dict(need_down=True))):
        T = s30(**kw); show(nm, T.net, T.date)
    print("\n6. Prior VWAP Trap (from its review, not rerun): as is $153 (t 3.2); yesterday's close as the level $107 (t 2.3); yesterday's midpoint"
          "\n   $115 (t 2.4); prior VWAP shifted at random +-0.3 ADR $88-169: the level adds ~$30 a trade, the engine is momentum + a 0.5 ADR trailing stop.")
