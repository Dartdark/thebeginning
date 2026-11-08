"""Ingredient ablation of three working strategies (user 2026-11-08: 'codes always combine more than one paper'). Information only, no
promotion: each strategy as is, then ONE ingredient removed (or isolated) at a time, per NQ after repo costs, 2018-26 and both periods.
  Twin cap1 (v2.1 holiday rules): breakout setup alone / momentum setup alone / no volatility filter / breakout only in RTH /
    momentum with a target (1.5 x its stop) / breakout stop uncapped
  Overnight Tick: every night 17:05 -> 03:00 / + down day only / + order flow x VIX only (any day) / down day + order flow only /
    down day + VIX only / the full rule
  Bridge noise-area 15-min longs (RTH chart): as is / no noise band (vm 0 = break of the open / prior close) / no target / no stop /
    no daily trade & stop limits / shorts added
  tools/run_stamped.sh analysis/ingredient_ablation.py > analysis/outputs/ingredient_ablation_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import twin_continuation_test as tc


def line(x, d, nm):
    x = pd.Series(np.asarray(x, float)); d = pd.DatetimeIndex(d); tt = lambda v: v.mean() / v.std(ddof=1) * np.sqrt(len(v)) if len(v) > 2 else np.nan
    a, b = x[(d < "2023").tolist()], x[(d >= "2023").tolist()]; pf = x[x > 0].sum() / max(1e-9, -x[x < 0].sum())
    return (f"   {nm:<46} n {len(x):5d} ${x.mean():6.0f} t {tt(x):5.2f} PF {pf:4.2f} total ${x.sum() / 1000:6.0f}k | 2018-22 ${a.mean():5.0f} (t {tt(a):4.1f})"
            f" 2023+ ${b.mean():5.0f} (t {tt(b):4.1f}) | worst ${x.min():,.0f}")


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); B = tc.flatten(g)
    print("\n1. Twin Continuation (cap1, v2.1):")
    for nm, kw in (("as is", {}), ("breakout setup only", dict(use_mo=False)), ("momentum setup only", dict(use_bo=False)),
                   ("no volatility filter", dict(vol_cap=0)), ("breakout entries only in RTH", dict(bo_rth_only=True)),
                   ("momentum with a target (1.5 x stop)", dict(mo_target=112.5)), ("breakout stop uncapped", dict(max_stop_mult=0.0))):
        a = dict(max_stop_mult=1.0, v21=True); a.update(kw); T = tc.simulate(B, **a); T = T[T.date >= "2018-01-01"]
        print(line(T.net, T.date, nm), flush=True)
    print("\n2. Overnight Tick (nights 17:05 -> 03:00, no stop; order-flow data to 2026-07):")
    N = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date"]); have = N.rsv.notna() & N.hi25.notna(); N = N[have & ~N.half]
    hi = N.hi25.astype(bool); cell = ((N.rsv < 0) & hi) | ((N.rsv >= 0) & ~hi)
    for nm, m in (("every night", np.ones(len(N), bool)), ("down day only", N.down), ("order flow x VIX only (any day)", cell),
                  ("down day + order flow < 0 only", N.down & (N.rsv < 0)), ("down day + VIX above its SMA only", N.down & hi),
                  ("full rule (down day + order flow x VIX)", N.down & cell)):
        print(line(N.net[m], N.date[m], nm))
    print("\n3. Bridge noise-area 15-min longs (RTH chart):")
    import bridge_noise_15m_test as BN
    S = BN.series("rth")
    for nm, kw in (("as is (longs only)", dict(shorts=False)), ("no noise band (vm 0)", dict(shorts=False, vm=0.0)), ("no target", dict(shorts=False, rr=100.0)),
                   ("no stop, no target (both off)", dict(shorts=False, sl=1e6, rr=1.0)), ("no daily trade / stop limits", dict(shorts=False, maxtr=99, maxstops=99)),
                   ("shorts added (both sides)", {})):
        T = BN.run(S, **kw); T = T[T.date >= "2018-01-01"]; print(line(T.net, T.date, nm), flush=True)
