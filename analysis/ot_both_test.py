"""Overnight Tick parent + 'any day' together (user 2026-11-08: 'does OT any day improve any book if added alongside its parent?').
PRE-REGISTERED (header committed before the run; 1 variant: add any-day 1 MNQ on top of the plan's OT). Nights from
checks/candidates/overnight_tick/nights.csv (order flow to 2026-07-07). Any-day includes every parent night, so 'both' = 2x on parent
nights + 1x on the extra up-day nights. Books: personal (OT 2 MNQ now) + any-day 1 MNQ, compared with + parent 1 more MNQ (OT 3) and +
the extra up-day nights only 1 MNQ; funded 150K x 1.5 + Twin 2 + OT 2 (the 150K funded plan has OT 2) + any-day 1; 150K evaluation
set + Twin 2 + OT 2 + any-day 1 (information: OT is not in the evaluation set).
  tools/run_stamped.sh analysis/ot_both_test.py > analysis/outputs/ot_both_test_output.txt
"""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
from new_sources_150k import daypaths
import bench150 as BB

if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    N = pd.read_csv("checks/candidates/overnight_tick/nights.csv", parse_dates=["date", "sess"]); N = N[N.rsv.notna() & N.hi25.notna() & ~N.half]
    hi = N.hi25.astype(bool); cell = ((N.rsv < 0) & hi) | ((N.rsv >= 0) & ~hi)
    S = {"parent": N[N.down & cell], "any day": N[cell], "extra up-day nights": N[~N.down & cell]}
    for k, t in S.items(): print(f"   {k:<20} n {len(t)} ${t.net.mean():.0f}")
    ctx = BB.setup(base="legacy"); dts, D = ctx["dts"], ctx["D"]; dpos = pd.Series(np.arange(D), index=dts); PT = {}
    for k, t in S.items(): PT[k] = daypaths(D, [(int(dpos[d]) if d in dpos.index else None, a, n) for d, a, n in zip(t.date, t.adv, t.net)])
    dm = lambda t: (t.groupby("date").net.sum() / 10 - 0.55 * t.groupby("date").size())
    print("\n   Personal book 1-year MC return / DD p95 (OT already 2 MNQ; to 2026-07-07):")
    Pp = pd.read_pickle("scratch_data/personal_P.pkl"); ot = Pp.OvernightTick
    BB.personal({"OT 2 (plan)": ot, "+ any-day 1": ot.add(dm(S["any day"]), fill_value=0.0), "+ parent 1 (OT 3)": ot.add(dm(S["parent"]), fill_value=0.0), "+ extra up-days 1": ot.add(dm(S["extra up-day nights"]), fill_value=0.0)}, end="2026-07-07")
    lab = ctx["lab"]
    for k in S: lab.W["OT_" + k] = PT[k][0]; lab.C["OT_" + k] = PT[k][1][:, -1]
    BB.BASE_FUNDED = {**BB.BASE_FUNDED, "OT_parent": 2}
    print(); BB.funded_bench(ctx, {"+ any-day 1": {**BB.BASE_FUNDED, "OT_any day": 1}, "+ parent 1 (OT 3)": {**BB.BASE_FUNDED, "OT_parent": 3},
                                   "+ extra up-days 1": {**BB.BASE_FUNDED, "OT_extra up-day nights": 1}}, end="2026-07-07", label="Funded 150K x 1.5 + Twin 2 + OT 2")
    ctx["Wb"] = ctx["Wb"] + 2 * PT["parent"][0]; ctx["Rb"] = ctx["Rb"] + 2 * PT["parent"][1]
    print(); BB.eval_bench(ctx, {"+ any-day 1": PT["any day"], "+ extra up-days 1": PT["extra up-day nights"]}, end="2026-06-01", label="150K evaluation (set + Twin 2 + OT 2)")
