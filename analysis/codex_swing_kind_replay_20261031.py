"""Replay frozen Swing Target accounting through the repository funded bench.

Run from codex/work: python analysis/codex_swing_kind_replay_20261031.py
  /workspace/thebeginning-source /workspace/scratch prepare|50|150
Source checkout must be Claude 86df2c0; see committed plan for assumptions.
"""
from pathlib import Path
import gc
import hashlib
import json
import os
import pickle
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_swing_kind_replay_20261031"
SOURCE, SCRATCH = (Path(x).resolve() for x in sys.argv[1:3])
MODE = sys.argv[3]
OUT.mkdir(parents=True, exist_ok=True)
assert subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "--short=7", "HEAD"], text=True).strip() == "86df2c0"
subprocess.check_call(["git", "-C", str(ROOT), "cat-file", "-e", "0b72684:agents/codex/plans/swing_kind_replay_20261031.md"])
os.chdir(SOURCE)
sys.path.insert(0, str(SOURCE / "analysis"))
sys.argv = [__file__, str(SCRATCH)]  # legacy modules read scratch from argv[1]
import numpy as np
import pandas as pd
from portfolio import load_mc
from funded_lab import Lab
from build_lab import REPORTS
import swing_target_bench as ST
import funded_bootstrap as FB
import funded_sim as F50
import funded_sim150 as F150


def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, default=str) + "\n")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def prepare():
    g = pickle.load(open(SCRATCH / "g24.pkl", "rb"))
    atr = g.daily_atr(15)
    lab = Lab(g)
    exclusions, counts = [], {}
    for key, (path, stop_atr) in REPORTS.items():
        t = load_mc(g, path)
        raw = pd.read_excel(path, sheet_name="List of Trades", header=2)
        ent = raw[raw.Type.astype(str).str.startswith("Entry")].reset_index(drop=True)
        ex = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
        assert len(t) == len(ent) == len(ex), "Report/grid coverage changed"
        opened = ex.Signal.astype(str).str.lower().eq("open")
        for i in np.flatnonzero(opened):
            exclusions.append(dict(strategy=key, entry=str(ent.Date[i]), exit=str(ex.Date[i]),
                                   signal=str(ex.Signal[i]), reported_mark=float(ex.Price[i])))
        t = t.loc[~opened].reset_index(drop=True)
        if key == "OND_MC":
            t = t[t.j0 <= 30].reset_index(drop=True)  # existing build_lab rule
        assert (t.j1 >= t.j0).all(), (key, "unresolved cross-date/invalid geometry")
        lab.add(key, t, stop_pts=stop_atr * atr)
        counts[key] = len(t)
        if key in ("ONB_ML2_MC", "LDF_MC"):
            base = "ONB_ML2" if key == "ONB_ML2_MC" else key
            for side, label in ((1, "L"), (-1, "S")):
                lab.add(base + "_" + label, t[t.side == side].reset_index(drop=True), stop_pts=stop_atr * atr)
        print(key, len(t), flush=True)
    pickle.dump(lab, open(SCRATCH / "lab.pkl", "wb"), protocol=4)
    del lab
    gc.collect()

    import single_print_test as SP
    SP.load = lambda symbol: g  # reuse identical grid; frame/session rules unchanged
    _, flags = SP.frame()
    flags.to_pickle(SCRATCH / "single_print_sessions.pkl")
    print("flags ready", flush=True)

    import relative_strength_test as RS
    days, nq, es = RS.load()
    rs = RS.trades(days, nq, RS.signals(days, nq, es))
    rs.to_csv(SCRATCH / "rs_trades.csv", index=False)
    del nq, es
    gc.collect()
    print("RS ready", len(rs), flush=True)

    import s_rank_gap_round2_test as GAP
    cl = GAP.Sym("CL")
    cl.set_rolls(GAP.rolls_cl(cl)[0])
    frame = GAP.sunday_frame(cl)
    pickle.dump({"frames": {"CL": frame}}, open(SCRATCH / "s_rank_gap2.pkl", "wb"))
    del cl
    gc.collect()
    ledger = ROOT / "analysis/outputs/codex_swing_target/CODE_BE_trades.csv"
    frozen = SOURCE / "checks/candidates/swing_target/codex_be_trades.csv"
    assert sha(ledger) == sha(frozen), "Different Swing ledger from reviewed source"
    (SCRATCH / "swing_be.csv").write_bytes(ledger.read_bytes())

    lab = ST.OTB.lab_for(150)
    fixed = ST.pt_trades(lab.g)
    raw_st = pd.read_csv(ledger, parse_dates=["date"])
    raw_st = raw_st[raw_st.date >= "2018-01-01"].reset_index(drop=True)
    assert np.array_equal(fixed.date, raw_st.date)
    old = fixed.copy()
    old["kind"] = raw_st.reason.astype(object)
    old.loc[raw_st.apex_flat_violation, "kind"] = 2
    lab.add("ST_FIXED", fixed)
    lab.add("ST_OLD", old)
    assert (fixed.j1 >= fixed.j0).all()
    expected = ((fixed.exit - fixed.entry) * fixed.side * 20 - 7.25 - 5 * (1 + fixed.kind.ne(1))) / 10
    assert np.isclose(lab.C["ST_FIXED"].sum(), expected.sum())
    target_cash = float((fixed.kind == 1).sum() * 0.5)
    assert np.isclose((lab.C["ST_FIXED"] - lab.C["ST_OLD"]).sum(), target_cash)
    assert (lab.W["ST_FIXED"] >= lab.W["ST_OLD"] - 1e-8).all()
    checks = dict(source_commit="86df2c0", plan_commit="0b72684", source_ledger_sha256=sha(ledger),
                  excluded_open_placeholders=exclusions, baseline_trade_counts=counts,
                  grid_first=str(g.ts[0]), grid_last=str(g.ts[-1]), trading_days=lab.D,
                  swing_rows=len(fixed), kind_counts=fixed.kind.value_counts().to_dict(),
                  holiday_repairs=raw_st.loc[raw_st.apex_flat_violation, "date"].astype(str).tolist(),
                  corrected_minus_old_total_per_mnq=target_cash,
                  corrected_cash_reconciles=True, corrected_path_pointwise_no_worse=True,
                  versions={"numpy": np.__version__, "pandas": pd.__version__})
    dump("preparation.json", checks)
    # Retain only the union used by either historical roster plus the two ST paths.
    keys = set(ST.plans50()["50K plan"]) | set(ST.plans150()["150K plan"]) | {"ST_FIXED", "ST_OLD"}
    for attr in ("W", "C", "N", "J0", "stop"):
        d = getattr(lab, attr)
        setattr(lab, attr, {k: v for k, v in d.items() if k in keys})
    pickle.dump(lab, open(SCRATCH / "codex_st_replay_lab.pkl", "wb"), protocol=4)
    files = list((SOURCE / "analysis").glob("*.py")) + list((SOURCE / "data").glob("*.csv"))
    files += list((SOURCE / "mc_reports").glob("*.xlsx"))
    dump("input_hashes.json", {str(p.relative_to(SOURCE)): sha(p) for p in files})
    print(json.dumps(checks, default=str), flush=True)


def run(which):
    lab_hash = sha(SCRATCH / "codex_st_replay_lab.pkl")
    lab = pickle.load(open(SCRATCH / "codex_st_replay_lab.pkl", "rb"))
    FB.F = F50 if which == 50 else F150
    original = ST.plans50() if which == 50 else ST.plans150()
    base = original[f"{which}K plan"]
    replace = original["VB 2/1 -> 1/1 + ST 1" if which == 50 else "DT 2 -> ST 2"]
    empty = {k: v for k, v in replace.items() if k != "ST"}
    qty = replace["ST"]
    plans = dict(BASE=base, REPLACE_OLD={**empty, "ST_OLD": qty},
                 REPLACE_FIXED={**empty, "ST_FIXED": qty}, EMPTY=empty,
                 ADD_FIXED={**base, "ST_FIXED": qty})
    signature = json.dumps(dict(lab=lab_hash, script=sha(__file__), plans=plans,
                                seed=20261031, n=500, H=500, L=20), sort_keys=True)
    boot = FB.Boot(lab)
    kw = {} if which == 50 else dict(ref=3000.0)
    # Ten checkpoints with disjoint seed streams, 50 paired histories each.
    # Preserve the registered single RNG stream by generating the full matrix once.
    histories = boot._histories(500, 500, 20, 20261031)
    aggregate, aggregate_y = {k: [] for k in plans}, {k: [] for k in plans}
    start = time.time()
    for chunk in range(10):
        path = OUT / f"{which}_chunk_{chunk}.npz"
        if path.exists():
            data = np.load(path)
            assert str(data["signature"]) == signature, "Checkpoint input/code identity changed"
            res = {k: data[k] for k in plans}
            y1 = {k: data[k + "_y1"] for k in plans}
        else:
            boot._histories = lambda *args: histories[chunk * 50:(chunk + 1) * 50]
            res, y1, nmin = boot.run(plans, n=50, L=20, seed=20261031, **kw)
            np.savez_compressed(path, signature=signature, **res, **{k + "_y1": v for k, v in y1.items()})
            print(which, "checkpoint", chunk + 1, "elapsed seconds", round(time.time() - start), "minutes", nmin, flush=True)
        for k in plans:
            aggregate[k].append(res[k]); aggregate_y[k].append(y1[k])
    res = {k: np.concatenate(v) for k, v in aggregate.items()}
    y1 = {k: np.concatenate(v) for k, v in aggregate_y.items()}
    boot.run = lambda *args, **kwargs: (res, y1, 0)
    df, table, _ = boot.compare(plans)
    df.to_csv(OUT / f"{which}_summary.csv")
    effects = []
    for a, b in [("REPLACE_FIXED", "BASE"), ("REPLACE_FIXED", "EMPTY"), ("REPLACE_FIXED", "REPLACE_OLD")]:
        for metric, delta in [("y1", y1[a] - y1[b]), ("y2", res[a][:, 0] - res[b][:, 0]),
                              ("blown", res[a][:, 3] - res[b][:, 3])]:
            se = delta.std(ddof=1) / np.sqrt(len(delta))
            effects.append(dict(a=a, b=b, metric=metric, mean=float(delta.mean()),
                                mc_se=float(se), mc_95_low=float(delta.mean() - 1.96 * se),
                                mc_95_high=float(delta.mean() + 1.96 * se),
                                changed_histories=int(np.count_nonzero(delta))))
    pd.DataFrame(effects).to_csv(OUT / f"{which}_paired_effects.csv", index=False)
    dump(f"{which}_run.json", dict(plans=plans, seed=20261031, n=500, H=500, L=20,
                                  first_year_days=250, seconds=time.time() - start,
                                  preregistration="0b72684", source="86df2c0",
                                  lab_sha256=lab_hash, script_sha256=sha(__file__)))
    print(table, flush=True)


if MODE == "prepare":
    prepare()
else:
    run(int(MODE))
