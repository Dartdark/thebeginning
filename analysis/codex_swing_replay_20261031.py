"""Reproduce the frozen Swing Target accounting replay using existing lab tools.

Run from repo root: python analysis/codex_swing_replay_20261031.py prep
then: python analysis/codex_swing_replay_20261031.py 50|150 [histories=500]
Scratch grids first: python analysis/build_lab.py scratch_data (its lab stage may
fail on unfinished MC rows; prep rebuilds that stage with a closed-ticket adapter).
"""
import contextlib
import hashlib
import json
from pathlib import Path
import pickle
import shutil
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, "analysis")
# Existing modules interpret argv[1] as their scratch directory at import time.
ARGS = sys.argv[1:]
sys.argv = [sys.argv[0], "scratch_data", "merge"]
import numpy as np
import pandas as pd
import portfolio
from build_lab import REPORTS
from funded_lab import Lab
import funded_bootstrap as FB
import swing_target_bench as ST

OUT = Path("analysis/outputs/codex_swing_replay")
SP = Path("scratch_data")
OUT.mkdir(parents=True, exist_ok=True)
ORIGINAL_LOAD = portfolio.load_mc
AUDIT = []


def closed_mc(g, path):
    """Preserve load_mc mapping; remove only explicitly unfinished `open` rows."""
    t = ORIGINAL_LOAD(g, path)
    raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
    ent = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
    ex = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
    assert len(ent) == len(ex), path
    dates = pd.to_datetime(ent.Date).dt.strftime("%Y%m%d").astype(int).to_numpy()
    day = np.searchsorted(g.dates, dates)
    keep = (day < g.D) & (g.dates[np.minimum(day, g.D - 1)] == dates)
    terminal = ex.Signal.astype(str).str.strip().str.lower().eq("open").to_numpy()[keep]
    assert len(terminal) == len(t), path
    for i in np.flatnonzero(terminal):
        AUDIT.append(dict(report=path, reason="unfinished open valuation", **t.iloc[i].astype(str).to_dict()))
    return t.loc[~terminal].reset_index(drop=True)


def prep():
    g = pickle.load(open(SP / "g24.pkl", "rb"))
    atr = g.daily_atr(15)
    lab = Lab(g)
    for k, (path, stop) in REPORTS.items():
        t = closed_mc(g, path)
        if k == "OND_MC":
            removed = t[t.j0 > 30]
            AUDIT.extend(dict(report=path, reason="existing OND MaxEntryDelay filter", **r.astype(str).to_dict())
                         for _, r in removed.iterrows())
            t = t[t.j0 <= 30].reset_index(drop=True)
        assert (t.j1 >= t.j0).all(), (k, t[t.j1 < t.j0])
        lab.add(k, t, stop_pts=stop * atr)
        if k in ("ONB_ML2_MC", "LDF_MC"):
            base = k.replace("_MC", "") if k == "ONB_ML2_MC" else k
            for side, suffix in ((1, "L"), (-1, "S")):
                lab.add(f"{base}_{suffix}", t[t.side == side].reset_index(drop=True), stop_pts=stop * atr)
        print(k, len(t), flush=True)
    pickle.dump(lab, open(SP / "lab.pkl", "wb"), protocol=4)
    pd.DataFrame(AUDIT).to_csv(OUT / "excluded_report_rows.csv", index=False)

    # Rebuild only the cache-producing functions, without unrelated return searches.
    import single_print_test as single
    single.load = lambda sym: g if sym == "NQ" else (_ for _ in ()).throw(ValueError(sym))
    _, sessions = single.frame()
    sessions.to_pickle(SP / "single_print_sessions.pkl")
    print("single prints", len(sessions), flush=True)
    import s_rank_gap_round2_test as gaps
    sym = gaps.Sym("CL")
    sym.set_rolls([])  # fast_plan_lab uses ok/gA/atr only; it does not use the frame's roll column.
    frame = gaps.sunday_frame(sym)
    pickle.dump({"frames": {"CL": frame}}, open(SP / "s_rank_gap2.pkl", "wb"))
    del sym
    import relative_strength_test as rs
    days, n, e = rs.load()
    t = rs.trades(days, n, rs.signals(days, n, e))
    t.to_csv(SP / "rs_trades.csv", index=False)
    print("RS", len(t), flush=True)
    shutil.copyfile("checks/candidates/swing_target/codex_be_trades.csv", SP / "swing_be.csv")
    sources = list(REPORTS.values())
    files = [x[0] for x in sources] + [
        "analysis/swing_target_bench.py", "analysis/funded_lab.py", "analysis/portfolio.py",
        "analysis/funded_bootstrap.py", "analysis/funded_sim.py", "analysis/funded_sim150.py",
        "checks/candidates/swing_target/codex_be_trades.csv",
        "checks/candidates/overnight_tick/python_trades.csv"]
    files += [str(p) for p in Path("data").glob("*1min*csv")]
    manifest = {f: hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in sorted(files)}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def run(which, n):
    lab = ST.OTB.lab_for(which)
    t = ST.pt_trades(lab.g)
    assert set(t.kind) <= {0, 1, 2}
    assert (t.j1 >= t.j0).all()
    lab.add("ST", t)
    legacy = t.copy()
    # Reconstruct the precise pre-repair interface, including numeric kind=2
    # on the three holiday repairs (they were never text kinds).
    raw = pd.read_csv(SP / "swing_be.csv")
    legacy["kind"] = raw.reason.to_numpy().astype(object)
    legacy.loc[raw.apex_flat_violation.to_numpy(), "kind"] = 2
    lab.add("ST_legacy", legacy)
    np.testing.assert_allclose(lab.C["ST"].sum() - lab.C["ST_legacy"].sum(), 132.0, atol=1e-7)
    plans = ST.plans50() if which == 50 else ST.plans150()
    base = plans[next(iter(plans))]
    slots = ["VB_N", "RS_L"] if which == 50 else ["DT"]
    for slot in slots:
        empty = {k: v for k, v in base.items() if k != slot}
        if slot == "VB_N":
            empty[slot] = 1  # remove exactly the one replaced contract, retaining VB_F.
        plans[f"EMPTY {slot}"] = empty
    adopted = "VB 2/1 -> 1/1 + ST 1" if which == 50 else "DT 2 -> ST 2"
    plans["adopted, legacy accounting"] = {("ST_legacy" if k == "ST" else k): v for k, v in plans[adopted].items()}
    FB.F = ST.F50 if which == 50 else ST.F150
    boot = FB.Boot(lab)
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    boot.days = boot.days[dates[boot.days] <= "2026-10-09"]
    kw = {} if which == 50 else {"ref": 3000.0}
    print(f"{which}K: {n} paired histories, {len(boot.days)} source days, {len(plans)} plans", flush=True)
    res, y1, minutes = boot.run(plans, n=n, H=500, L=20, seed=1, **kw)
    pickle.dump((res, y1), open(SP / f"codex_st{which}_results.pkl", "wb"))
    boot.run = lambda *a, **k: (res, y1, minutes)
    df, summary, _ = boot.compare(plans)
    df.to_csv(OUT / f"funded_{which}.csv")
    (OUT / f"funded_{which}.txt").write_text(summary + "\n")
    print(summary, flush=True)
    # Monte Carlo uncertainty of paired means; quantiles of per-history differences
    # are separately labeled, never confused with confidence in the mean.
    rng = np.random.default_rng(20261031)
    pairs = []
    for comparator in [next(iter(plans)), f"EMPTY {slots[0]}", "adopted, legacy accounting"]:
        for horizon, a, b in [("1y", y1[adopted], y1[comparator]), ("2y", res[adopted][:, 0], res[comparator][:, 0]),
                              ("blown_2y", res[adopted][:, 3], res[comparator][:, 3])]:
            delta = a - b
            draws = delta[rng.integers(0, n, size=(2000, n))].mean(axis=1)
            pairs.append(dict(adopted=adopted, comparator=comparator, metric=horizon, mean=delta.mean(),
                              mean_ci_low=np.percentile(draws, 2.5), mean_ci_high=np.percentile(draws, 97.5),
                              path_p5=np.percentile(delta, 5), path_p95=np.percentile(delta, 95)))
    pd.DataFrame(pairs).to_csv(OUT / f"paired_{which}.csv", index=False)
    (OUT / f"run_{which}.json").write_text(json.dumps(dict(n=n, seed=1, block=20, horizon=500,
        cutoff="2026-10-09", source_days=len(boot.days), compressed_minutes=int(minutes),
        st_trades=len(t), st_exit_kinds=t.kind.value_counts().to_dict(), plans=plans), indent=2) + "\n")


if __name__ == "__main__":
    if ARGS == ["prep"]:
        prep()
    else:
        run(int(ARGS[0]), int(ARGS[1]) if len(ARGS) > 1 else 500)
