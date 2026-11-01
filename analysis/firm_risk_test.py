"""Firm-level risk (2026-11-01, review gap #1: 'the accounts are one bet, not many'). Four 150K No-Activation evaluations bought
as a batch, all running the combine set; how often do they fail together, and does spacing or a different mix help?
Engine: plan_150k_test.evaluation (EOD trail $4,000 with intraday touch, DLL $2,000, +$9,000 target, 21 trading days), combine
set at 150K whole-contract sizes (VB 20, ONB $2,750 risk, Bridge 5, EOS $1,250 risk), MultiCharts trade lists, costs in.
Batches start on every trading day 2018-01 .. 2023-09. Variants (fixed before running):
  A  plan today: 4 accounts, one bought per trading day (starts s, s+1, s+2, s+3), same mix
  B  spaced: one per WEEK (starts s, s+5, s+10, s+15), same mix
  C  one a day, but accounts 2 and 4 run Vault Break at half size (VB 10): a less correlated mix
Reference: 4 accounts started ~1 year apart (independent). Measures per batch: passes (of 4), P(0 passes), P(all 4 fail),
P(2+ fail within 10 trading days of each other), mean pairwise correlation of pass/fail.
  tools/run_stamped.sh analysis/firm_risk_test.py scratch_data > analysis/outputs/firm_risk_test_output.txt
"""
import sys, io, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from portfolio import load_mc, paths
from funded_lab import with_slippage
from build_lab import REPORTS
from bridge_monday_confirm import load_bridge_mc
from plan_150k_test import evaluation, R150, ONB30

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"


def outcomes(P, q, D):
    Wc = sum(P[k][0] * q[k] for k in P); Rc = sum(P[k][1] * q[k] for k in P)
    return [evaluation(Wc, Rc, s, D, R150) for s in range(D)]


def batch_stats(chals, offsets, starts):
    rows = []
    for s in starts:
        res = [chals[i][s + o] for i, o in enumerate(offsets)]
        if any(r is None for r in res): continue
        ok = [r[0] == "pass" for r in res]; fail_day = sorted(s + o + r[1] for o, r in zip(offsets, res) if r[0] == "fail")
        close = any(b - a <= 10 for a, b in zip(fail_day, fail_day[1:]))
        rows.append(dict(passes=sum(ok), zero=sum(ok) == 0, allfail=len(fail_day) == 4, close=close, ok=ok))
    df = pd.DataFrame(rows); M = np.array(df.ok.tolist(), float)
    C = np.corrcoef(M.T); corr = C[np.triu_indices(4, 1)].mean()
    return df, corr


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        lab = runpy.run_path("analysis/cl_sunday_fade_bench.py", run_name="__main__")["lab"]
    g = lab.g; atr = g.daily_atr(15); tr = lab.tr; D = len(tr); dates = pd.DatetimeIndex(g.ts[tr])
    P = {}
    for nm, t in (("VB", with_slippage(load_mc(g, REPORTS["VB"][0]))), ("ONB30", with_slippage(load_mc(g, ONB30))),
                  ("MON_BR", load_bridge_mc(g)), ("EOS", with_slippage(load_mc(g, REPORTS["EOS"][0])))):
        w, r_ = paths(g, t); P[nm] = (w[tr] / 10, r_[tr] / 10)
    rk = lambda dl_, m: np.floor(dl_ / (np.nan_to_num(m * atr[tr], nan=1e12) * 2))[:, None]
    full = {"VB": 20.0, "ONB30": rk(2750, 0.25), "MON_BR": 5.0, "EOS": rk(1250, REPORTS["EOS"][1])}
    half = {**full, "VB": 10.0}
    cf, ch = outcomes(P, full, D), outcomes(P, half, D)
    s_lo, s_hi = int(np.argmax(dates >= "2018-01-01")), int(np.argmax(dates >= "2023-09-01"))
    starts = list(range(s_lo, s_hi))
    p = lambda c: np.mean([x[0] == "pass" for x in c[s_lo:s_hi] if x is not None])
    print(f"\nsingle-account pass rate 2018-01..2023-08 starts: full mix {p(cf):.1%}, VB-half mix {p(ch):.1%}")
    print(f"\n{'batch of 4':<52}{'passes avg':>11}{'P(0 pass)':>11}{'P(all 4 fail)':>14}{'P(2 fail <=10d apart)':>23}{'outcome corr':>13}")
    for nm, ch_list, offs, st in (("A  one a day, same mix (plan)", [cf] * 4, [0, 1, 2, 3], starts),
                                  ("B  one a week, same mix", [cf] * 4, [0, 5, 10, 15], starts),
                                  ("C  one a day, accounts 2 + 4 at VB 10", [cf, ch, cf, ch], [0, 1, 2, 3], starts),
                                  ("reference: ~1 year apart (independent)", [cf] * 4, [0, 252, 504, 756], [s for s in starts if s + 756 < s_hi])):
        df, corr = batch_stats(ch_list, offs, st)
        print(f"{nm:<52}{df.passes.mean():>11.2f}{df.zero.mean():>11.1%}{df.allfail.mean():>14.1%}{df.close.mean():>23.1%}{corr:>13.2f}")
