"""Book test of the four capital-bench leads (user 2026-11-08). PRE-REGISTERED (header committed before the run; 4 variants, all POST HOC
from ingredient_ablation6 / 7, so the bar is a return / DD gain in BOTH periods). Base = the current personal book (personal_P, OT 2 MNQ).
Each lead vs its bench version, added at 1 micro (per NQ net / 10 - $0.55 a trade):
  S30 IBS, NQ: entry IBS < 0.10 vs the bench rule IBS < 0.20 (both NQ-only here, marked to market daily at the 15:00 close, roll jumps
    removed; the bench row was NQ + ES)
  FVB: shorts only vs both sides        S03 Noise Area v2: longs only vs both sides        Anson momentum: longs only vs both sides
Measures: 1-year block-bootstrap MC median year, p5, DD p95, return / DD, capital at the 20% rule; 2018-26, 2018-22, 2023+.
Promotion: return / DD above the base in both periods -> plan candidate (forward log first); else it stays on the bench.
  tools/run_stamped.sh analysis/bench_leads_book_test.py > analysis/outputs/bench_leads_book_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from grid24 import jof
from overnight_round import roll_minutes
import s30_ibs_test as S3

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); Pp = Pp[[c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30")]]
    base = Pp.sum(axis=1) + Pp.OvernightTick; idx = Pp.index
    dm = lambda d, net: pd.Series(np.asarray(net, float) / 10 - 0.55, index=pd.DatetimeIndex(d)).groupby(level=0).sum().reindex(idx, fill_value=0.0)
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); S = S3.sessions(g, "NQ"); S = S[S.date >= "2017-12-01"].reset_index(drop=True)
    C = g.c.ravel(); rl = np.sort(roll_minutes(g, "NQ"))
    jump = pd.Series(0.0, index=S.date)                                    # roll jump inside each 15:00 -> 15:00 day
    for i in range(1, len(S)):
        m0, m1 = S.r[i - 1] * 1440 + jof(1500), S.r[i] * 1440 + jof(1500)
        for j in rl[(rl > m0) & (rl <= m1)]:
            p = j - 1
            while not np.isfinite(C[p]): p -= 1
            jump.iloc[i] += C[j] - C[p]
    def s30_daily(lo):
        pnl = pd.Series(0.0, index=S.date); pos = 0; n = 0
        for i, x in S.iterrows():
            if pos and i > 0 and np.isfinite(x.c15) and np.isfinite(S.c15[i - 1]): pnl.iloc[i] += (x.c15 - S.c15[i - 1] - jump.iloc[i]) * 20 / 10
            if not x.full or not np.isfinite(x.ibs) or not np.isfinite(x.nxt) or x.hi <= x.lo: continue
            if pos == 0 and x.ibs < lo: pos = 1; n += 1; pnl.iloc[i] -= 0.25 * 20 / 10
            elif pos == 1 and x.ibs > 0.8: pos = 0; pnl.iloc[i] -= (0.25 * 20 + 7.25) / 10 + 0.55
        return pnl.reindex(idx, fill_value=0.0), n
    s20, n20 = s30_daily(0.2); s10, n10 = s30_daily(0.1); print(f"   S30 NQ trades (all years): IBS < 0.2 {n20}, IBS < 0.1 {n10}")
    f = pd.read_csv("checks/candidates/fvb/trades.csv", parse_dates=["date"])
    s3 = pd.read_csv("checks/candidates/s03_v2/codex_v2_raw_trades.csv", parse_dates=["date"]); s3["net"] = s3.gross_nq - 17.25
    an = pd.read_csv("checks/candidates/anson/codex_intended_raw_trades.csv", parse_dates=["date"]); an["net"] = an.gross_nq - 17.25 * an.qty
    PAIRS = {"S30 IBS (NQ)": (("bench IBS < 0.20", s20), ("lead IBS < 0.10", s10)),
             "FVB": (("bench both sides", dm(f.date, f.net)), ("lead shorts only", dm(f[f.side < 0].date, f[f.side < 0].net))),
             "S03 Noise Area v2": (("bench both sides", dm(s3.date, s3.net)), ("lead longs only", dm(s3[s3.side > 0].date, s3[s3.side > 0].net))),
             "Anson momentum": (("bench both sides", dm(an.date, an.net)), ("lead longs only", dm(an[an.side > 0].date, an[an.side > 0].net)))}
    mc = lambda x: (lambda d: (d["pnl_p50"], d["pnl_p5"], d["dd_p95"], d["pnl_p50"] / d["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    per = {"2018-26": np.ones(len(idx), bool), "2018-22": idx.year <= 2022, "2023+": idx.year >= 2023}
    B = {p: mc(base[m]) for p, m in per.items()}
    for p in per: print(f"   base {p}: median ${B[p][0]:,.0f}  DD p95 ${B[p][2]:,.0f}  ret/DD {B[p][3]:.2f}")
    for piece, versions in PAIRS.items():
        print(f"\n{piece}:")
        for nm, s in versions:
            r = {p: mc((base + s)[m]) for p, m in per.items()}; ok = all(r[p][3] > B[p][3] for p in ("2018-22", "2023+"))
            print(f"   {nm:<20} " + " | ".join(f"{p} ret/DD {r[p][3]:.2f} ({r[p][3] - B[p][3]:+.2f})" for p in per)
                  + f" | 2018-26 median {r['2018-26'][0] - B['2018-26'][0]:+,.0f}, DD {r['2018-26'][2] - B['2018-26'][2]:+,.0f}, capital {(r['2018-26'][2] - B['2018-26'][2]) / 0.2:+,.0f}"
                  + (" -> PLAN CANDIDATE" if ok else ""), flush=True)
