"""US macro releases with consensus (Codex data 2026-11-09, data/codex_20261109/; spot-checked against known releases) - user 2026-11-10:
'do it'. PRE-REGISTERED (header committed before the first run).
Release groups (US CT; the 07:30 group days can coincide): INFLATION (CPI / core CPI / PPI / PCE / core PCE), JOBS (payrolls /
unemployment / earnings, first Friday), ADP (07:15), CLAIMS (weekly Thursday), RETAIL, GDP, JOLTS (09:00), FOMC (13:00 decision).
Surprise z = (actual - consensus) / sd of that series' surprises (2018-26); a group day is HOT / COLD by the sign of its largest |z|
release, BIG if |z| >= 1.
A. Screen (standing rule): every personal-book piece's daily P&L (active days) split by (1) release day vs other days, per group;
   (2) on release days, HOT vs COLD. Bar t_threshold(all comparisons), same sign in 2018-22 and 2023+.
B. Surprise engines on NQ, 07:30 groups (INFLATION, JOBS, CLAIMS, RETAIL, GDP): reaction = 07:45 close - 07:29 close; on BIG-surprise
   days, FOLLOW or FADE the reaction from the 07:46 open to the 09:00 close, stop 0.5 x daily ATR15; $7.25 + 1 tick per fill.
   Items: 5 groups x {follow, fade} = 10; bar t_threshold(10). Context (not items): every release day of the group (no surprise
   filter); random-side placebo (500 runs) for any item with t >= 2.
  tools/run_stamped.sh analysis/macro_tests.py > analysis/outputs/macro_tests_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
from metrics import t_threshold
from ingredient_ablation3 import line
import ingredient_ablation4 as IA4

GROUPS = {"INFLATION": ["CPIAUCNS", "CPILFENS", "PPIACO", "PCEPI", "PCEPILFE"], "JOBS": ["PAYEMS", "UNRATE", "CES0500000003"], "ADP": ["ADPMNUSNERSA"],
          "CLAIMS": ["ICSA"], "RETAIL": ["RSAFS"], "GDP": ["GDPC1"], "JOLTS": ["JTSJOL"], "FOMC": ["DFEDTARU"]}


def events():
    M = pd.read_csv("data/codex_20261109/macro_events_2018plus.csv", parse_dates=["time"]); M = M.dropna(subset=["actual"])
    M["ct"] = M.time.dt.tz_convert("America/Chicago"); M["day"] = pd.DatetimeIndex(M.ct.dt.date); M["hm"] = M.ct.dt.hour * 100 + M.ct.dt.minute
    M["s"] = M.actual - M.forecast
    M["z"] = M.groupby("series").s.transform(lambda x: x / x.std())
    g = {s: k for k, v in GROUPS.items() for s in v}; M["group"] = M.series.map(g)
    rows = []
    for (grp, day), x in M.dropna(subset=["group"]).groupby(["group", "day"]):
        zz = x.z.dropna(); zi = zz.loc[zz.abs().idxmax()] if len(zz) else np.nan
        rows.append(dict(group=grp, day=day, hm=int(x.hm.min()), z=zi))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    E = events(); print("   release days by group:", E.groupby("group").size().to_dict())
    # ---------------- A
    P = pd.read_pickle("scratch_data/personal_P.pkl"); rows = []
    for grp, x in E.groupby("group"):
        days = set(x.day); hot = set(x.day[x.z > 0]); cold = set(x.day[x.z < 0])
        for c in P.columns:
            v = P[c][P[c] != 0]; e = v.index.year <= 2022
            for kind, m in (("release day vs other", v.index.isin(days)), ("HOT vs COLD (release days)", None)):
                if m is None:
                    vv = v[v.index.isin(days)]; m = vv.index.isin(hot); ee = vv.index.year <= 2022
                    if m.sum() < 8 or (~m & vv.index.isin(cold)).sum() < 8: continue
                    a, b = vv[m], vv[vv.index.isin(cold)]; mm, cc = m, vv.index.isin(cold)
                    g1 = vv[ee & mm].mean() - vv[ee & cc].mean(); g2 = vv[~ee & mm].mean() - vv[~ee & cc].mean()
                else:
                    if m.sum() < 8: continue
                    a, b = v[m], v[~m]; g1 = v[e & m].mean() - v[e & ~m].mean(); g2 = v[~e & m].mean() - v[~e & ~m].mean()
                t = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
                rows.append(dict(group=grp, test=kind, piece=c, n_a=len(a), a=a.mean(), b=b.mean(), t=t, same=np.sign(g1) == np.sign(g2)))
    R = pd.DataFrame(rows); bar = t_threshold(len(R)); R.to_csv("analysis/outputs/macro_screen_table.csv", index=False)
    print(f"\nA. Screen: {len(R)} comparisons; bar |t| >= {bar:.2f}; at the bar (same sign): {int(((R.t.abs() >= bar) & R.same).sum())}; |t| >= 3 same sign: {int(((R.t.abs() >= 3) & R.same).sum())} (chance ~{len(R) * 0.0027:.1f})")
    top = R[R.same].reindex(R[R.same].t.abs().sort_values(ascending=False).index).head(12)
    for r in top.itertuples():
        print(f"   {r.group:<10}{r.test:<28}{r.piece:<22} t {r.t:5.2f} | n {r.n_a:3d} ${r.a:6.0f} vs ${r.b:6.0f}{'  LEAD' if abs(r.t) >= bar else ''}")
    # ---------------- B
    print(f"\nB. Surprise engines on NQ (per NQ; items 10, bar t >= {t_threshold(10):.2f}):")
    g = pickle.load(open("scratch_data/g24.pkl", "rb")); atr = g.daily_atr(15); pos = pd.Series(np.arange(len(g.ts)), index=pd.DatetimeIndex(g.ts)); IA4.COMM = 7.25
    cf = pd.Series(g.c.ravel()).ffill().to_numpy()
    def run(x, fade, rng=None):
        rows = []
        for r_ in x.itertuples():
            if r_.day not in pos.index: continue
            r = int(pos[r_.day]); c0, c1 = cf[r * 1440 + jof(729)], cf[r * 1440 + jof(745)]
            if not (np.isfinite(c0) and np.isfinite(c1)) or c1 == c0 or np.isnan(atr[r]): continue
            s = int(np.sign(c1 - c0)) * (-1 if fade else 1)
            if rng is not None: s = int(rng.choice([-1, 1]))
            px = IA4.walk(g, r * 1440 + jof(745) + 1, r * 1440 + jof(900), s, 0.5 * atr[r], 20.0, 0.25)
            if px is not None: rows.append((r_.day, s, px))
        return pd.DataFrame(rows, columns=["date", "side", "net"])
    for grp in ("INFLATION", "JOBS", "CLAIMS", "RETAIL", "GDP"):
        x = E[(E.group == grp) & (E.hm == 730)]; big = x[x.z.abs() >= 1]
        print(f"\n   {grp}: release days {len(x)}, big surprises {len(big)}")
        print(line(run(x, False).net, run(x, False).date, "context: follow, every release day"))
        for fade, nm in ((False, "ITEM follow, big surprise"), (True, "ITEM fade, big surprise")):
            T = run(big, fade); print(line(T.net, T.date, nm))
            if len(T) > 10 and T.net.mean() / T.net.std() * np.sqrt(len(T)) >= 2:
                rng = np.random.default_rng(13); pm = [run(big, fade, rng).net.mean() for _ in range(500)]
                print(f"      random side: 95th ${np.percentile(pm, 95):.0f}, real ${T.net.mean():.0f}, p {np.mean(np.array(pm) >= T.net.mean()):.3f}")
