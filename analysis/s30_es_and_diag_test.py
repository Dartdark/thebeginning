"""S30 ES leg + why the other three bench leads failed (user 2026-11-08). PRE-REGISTERED for the ES part (header committed before the run;
the NQ IBS < 0.10 lead is post hoc, the ES leg is its out-of-market check: same rule, never looked at).
  A  S30 on ES, entry IBS < 0.10 (and the bench IBS < 0.20 for reference): ES 1-minute, cash 08:31-15:00 CT; buy at 15:01 when IBS < x,
     sell at 15:01 when IBS > 0.80; no stop; $5 + 1 tick per fill per ES (MES = 1/10, + $0.55 a trade); marked daily at the 15:00 close,
     roll jumps removed. Standalone by period; book: NQ lead alone vs NQ lead + ES (IBS < 0.10) vs NQ + ES bench rule.
  B  Diagnostics for FVB shorts / S03 longs / Anson longs (and the S30 NQ lead for contrast): per-micro $ a year and Sharpe by period;
     daily corr with the book by period; average P&L on the book's worst 10% days; the existing piece each correlates with most.
  tools/run_stamped.sh analysis/s30_es_and_diag_test.py > analysis/outputs/s30_es_and_diag_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import montecarlo as MC
from grid24 import jof
from overnight_round import roll_minutes
import s30_ibs_test as S3


def s30_daily(g, sym, pv, tick, comm, lo, idx):
    S = S3.sessions(g, sym); S = S[S.date >= "2017-12-01"].reset_index(drop=True); C = g.c.ravel(); rl = np.sort(roll_minutes(g, sym))
    jump = np.zeros(len(S))
    for i in range(1, len(S)):
        m0, m1 = S.r[i - 1] * 1440 + jof(1500), S.r[i] * 1440 + jof(1500)
        for j in rl[(rl > m0) & (rl <= m1)]:
            p = j - 1
            while not np.isfinite(C[p]): p -= 1
            jump[i] += C[j] - C[p]
    pnl = np.zeros(len(S)); pos = 0; n = 0; tr = []
    for i, x in S.iterrows():
        if pos and i > 0 and np.isfinite(x.c15) and np.isfinite(S.c15[i - 1]): pnl[i] += (x.c15 - S.c15[i - 1] - jump[i]) * pv / 10
        if not x.full or not np.isfinite(x.ibs) or not np.isfinite(x.nxt) or x.hi <= x.lo: continue
        if pos == 0 and x.ibs < lo: pos = 1; n += 1; pnl[i] -= tick * pv / 10; e0 = i
        elif pos == 1 and x.ibs > 0.8: pos = 0; pnl[i] -= (tick * pv + comm) / 10 + 0.55; tr.append((S.date[e0], pnl[e0:i + 1].sum() * 10))
    return pd.Series(pnl, index=S.date).reindex(idx, fill_value=0.0), pd.DataFrame(tr, columns=["date", "net_full"])


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); Pp = Pp[[c for c in Pp.columns if c not in ("FC2B", "Kusho", "S47", "S30")]]
    book = Pp.sum(axis=1) + Pp.OvernightTick; idx = Pp.index
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); ge = pickle.load(open("scratch_data/ge.pkl", "rb"))
    nq10, _ = s30_daily(g, "NQ", 20.0, 0.25, 7.25, 0.10, idx)
    print("\nA. S30 ES leg (per ES):")
    tt = lambda x: x.mean() / x.std(ddof=1) * np.sqrt(len(x)) if len(x) > 2 else np.nan
    es = {}
    for lo in (0.10, 0.20):
        s, T = s30_daily(ge, "ES", 50.0, 0.25, 5.0, lo, idx); T = T[T.date >= "2018-01-01"]; es[lo] = s
        a, b = T[T.date < "2023"].net_full, T[T.date >= "2023"].net_full
        print(f"   ES IBS < {lo:.2f}: n {len(T)} ${T.net_full.mean():.0f} t {tt(T.net_full):.2f} | 2018-22 ${a.mean():.0f} (t {tt(a):.1f}) 2023+ ${b.mean():.0f} (t {tt(b):.1f}) | worst ${T.net_full.min():,.0f}")
    print(f"   daily corr ES lead vs NQ lead: {es[0.10][idx.year >= 2018].corr(nq10[idx.year >= 2018]):.2f}")
    mc = lambda x: (lambda d: (d["pnl_p50"], d["dd_p95"], d["pnl_p50"] / d["dd_p95"]))(MC.daily_mc(x.values, horizon=252, n=2000, block=20, trail=1e12, seed=1))
    per = {"2018-26": np.ones(len(idx), bool), "2018-22": idx.year <= 2022, "2023+": idx.year >= 2023}
    print("   book return / DD p95 (OT 2):")
    for nm, add in (("book", 0 * book), ("+ NQ lead (IBS<0.10)", nq10), ("+ NQ lead + ES IBS<0.10", nq10 + es[0.10]), ("+ NQ lead + ES IBS<0.20", nq10 + es[0.20])):
        r = {p: mc((book + add)[m]) for p, m in per.items()}
        print(f"      {nm:<26} " + " | ".join(f"{p} {r[p][2]:.2f}" for p in per) + f" | median ${r['2018-26'][0]:,.0f} DD ${r['2018-26'][1]:,.0f}", flush=True)
    print("\nB. Why the other leads fail (per micro, 1 MNQ):")
    dm = lambda d, net: pd.Series(np.asarray(net, float) / 10 - 0.55, index=pd.DatetimeIndex(d)).groupby(level=0).sum().reindex(idx, fill_value=0.0)
    f = pd.read_csv("checks/candidates/fvb/trades.csv", parse_dates=["date"]); s3 = pd.read_csv("checks/candidates/s03_v2/codex_v2_raw_trades.csv", parse_dates=["date"])
    an = pd.read_csv("checks/candidates/anson/codex_intended_raw_trades.csv", parse_dates=["date"])
    L = {"S30 NQ IBS<0.10 (passed)": nq10, "FVB shorts": dm(f[f.side < 0].date, f[f.side < 0].net),
         "S03 v2 longs": dm(s3[s3.side > 0].date, s3[s3.side > 0].gross_nq - 17.25), "Anson longs": dm(an[an.side > 0].date, an[an.side > 0].gross_nq - 17.25 * an[an.side > 0].qty)}
    worst = book <= book.quantile(0.10)
    for nm, s in L.items():
        out = [f"   {nm}:"]
        for p, m in (("2018-22", per["2018-22"]), ("2023+", per["2023+"])):
            x = s[m]; out.append(f"{p} ${x.sum() / (m.sum() / 252):,.0f}/yr Sharpe {x.mean() / x.std() * np.sqrt(252):.2f} corr {x.corr(book[m]):+.2f}")
        top = Pp.corrwith(s).sort_values(ascending=False).head(2).round(2).to_dict()
        out.append(f"on the book's worst 10% days ${s[worst].mean():+.0f} a day (book there ${book[worst].mean():,.0f}); most like {top}")
        print(" | ".join(out), flush=True)
