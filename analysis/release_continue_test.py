"""'High-impact releases tend to CONTINUE after the first reaction, medium-impact ones mean revert' (video / two list screenshots, user
2026-11-14). PRE-REGISTERED (this header committed before the first run). Testable half with our data: the HIGH list items whose release
times we hold (data/codex_20261109/macro_events_2018plus.csv, data/treasury_auctions.csv): ADP (07:15 CT), jobs report (07:30), CPI,
retail sales, GDP, core PCE, initial claims (07:30; claims-only days), JOLTS (09:00), Fed decision (13:00), 10-year and 30-year auctions
(12:00 CT close). The MEDIUM list (Fed balance sheet, factory orders, housing starts...) has no release times in our data: NOT tested.
Rule, per NQ, 2018 -> the file's last release: reference = close of the 1-min bar stamped at the release time t0; reaction = close(t0+5) -
reference; FOLLOW = enter at the open of t0+6 in the reaction's direction, out at the close of t0+60, no stop (primary). Also shown: hold
to t0+30, and a 15-minute reaction held to t0+75. Costs $7.25 + 1 tick per side. Claim holds for an item if follow avg > 0 with t >= 2.0;
whole claim if the pooled high list is > 0 with t >= 2.5. Control: random side (the reaction's sign shuffled), 500 runs, pooled.
Known before running (TIER_LIST macro rows): following the 07:30 -> 07:45 reaction to 09:00 LOST on inflation and jobs days.
  tools/run_stamped.sh analysis/release_continue_test.py > analysis/outputs/release_continue_test_output.txt
"""
import sys, pickle, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from grid24 import jof
print(__doc__.split("\n")[0])
g = pickle.load(open("scratch_data/g24.pkl", "rb")); ts = pd.DatetimeIndex(g.ts); row = pd.Series(np.arange(g.D), index=ts)
O, C = g.o.ravel(), g.c.ravel()
M = pd.read_csv("data/codex_20261109/macro_events_2018plus.csv", parse_dates=["time"]).dropna(subset=["actual"])
M["ct"] = M.time.dt.tz_convert("America/Chicago"); M["day"] = pd.DatetimeIndex(M.ct.dt.date); M["hm"] = M.ct.dt.hour * 100 + M.ct.dt.minute
G = {"ADPMNUSNERSA": "ADP", "PAYEMS": "Jobs report", "UNRATE": "Jobs report", "CES0500000003": "Jobs report", "CPIAUCNS": "CPI", "CPILFENS": "CPI",
     "RSAFS": "Retail sales", "GDPC1": "GDP", "PCEPILFE": "Core PCE", "PCEPI": "Core PCE", "ICSA": "Jobless claims", "JTSJOL": "JOLTS", "DFEDTARU": "Fed decision"}
M["grp"] = M.series.map(G); E = M.dropna(subset=["grp"]).drop_duplicates(["grp", "day"])[["grp", "day", "hm"]]
busy = set(zip(E[E.grp != "Jobless claims"].day, E[E.grp != "Jobless claims"].hm))
E = E[~((E.grp == "Jobless claims") & [((d, h) in busy) for d, h in zip(E.day, E.hm)])]          # claims-only days
A = pd.read_csv("data/treasury_auctions.csv", parse_dates=["auction_date"]); A = A[(A.auction_date >= "2018-01-01") & (A.security_type.isin(["Note", "Bond"]))]
for term, nm in (("10-Year", "10-year auction"), ("30-Year", "30-year auction")):
    x = A[A.security_term.str.contains(term.split("-")[0] + "-Year|" + str(int(term.split("-")[0]) - 1) + "-Year 1", regex=True) & (A.closing_time_comp == "01:00 PM")]
    E = pd.concat([E, pd.DataFrame(dict(grp=nm, day=x.auction_date.drop_duplicates().values, hm=1200))])
E = E[(E.day >= "2018-01-01") & E.day.isin(ts)].reset_index(drop=True)
COST = 7.25 + 2 * 5.0
def follow(day, hm, react, hold, side=None):
    i = row[day] * 1440 + jof(hm)
    ref, rc, e, x = C[i], C[i + react], O[i + react + 1], C[i + hold]
    if not all(np.isfinite(v) for v in (ref, rc, e, x)) or rc == ref: return np.nan
    s = np.sign(rc - ref) if side is None else side
    return (x - e) * s * 20 - COST
def tt(x): x = pd.Series(x).dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
def cell(x): x = pd.Series(x).dropna(); return f"${x.mean():6.0f} (t {tt(x):5.2f})"
E["p60"] = [follow(d, h, 5, 60) for d, h in zip(E.day, E.hm)]; E["p30"] = [follow(d, h, 5, 30) for d, h in zip(E.day, E.hm)]
E["p15"] = [follow(d, h, 15, 75) for d, h in zip(E.day, E.hm)]; y = E.day.dt.year
print(f"\n{'release':<17} {'n':>4}  follow 5-min reaction -> +60 (PRIMARY) | -> +30 | 15-min reaction -> +75 | primary 2018-22 / 2023+ | win")
for k, x in E.groupby("grp"):
    yy = x.day.dt.year
    print(f"{k:<17} {x.p60.notna().sum():4d}  {cell(x.p60)} | {cell(x.p30)} | {cell(x.p15)} | ${x.p60[yy <= 2022].mean():5.0f} / ${x.p60[yy >= 2023].mean():5.0f} | {np.mean(x.p60.dropna() > 0):.0%}")
print(f"{'POOLED high list':<17} {E.p60.notna().sum():4d}  {cell(E.p60)} | {cell(E.p30)} | {cell(E.p15)} | ${E.p60[y <= 2022].mean():5.0f} / ${E.p60[y >= 2023].mean():5.0f} | {np.mean(E.p60.dropna() > 0):.0%}")
rng = np.random.default_rng(1); pl = np.array([np.nanmean([follow(d, h, 5, 60, side=rng.choice([-1, 1])) for d, h in zip(E.day, E.hm)]) for _ in range(500)])
print(f"random side (500 runs): mean ${pl.mean():.0f}, p5 ${np.percentile(pl, 5):.0f}, p95 ${np.percentile(pl, 95):.0f}; follow ${E.p60.mean():.0f} -> share of random runs at or below it {np.mean(pl <= E.p60.mean()):.3f}")
print(f"FADE = the mirror: pooled ${(-E.p60 - 2 * COST).mean():.0f} a trade (t {tt(-E.p60 - 2 * COST):.2f})")
