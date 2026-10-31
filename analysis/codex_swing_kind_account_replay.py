"""Fixed-ledger Swing Target accounting replay; see committed 20261030 plan.

python3 analysis/codex_swing_kind_account_replay.py [scratch_data]
Rebuilds missing ignored caches from canonical fixed-rule helpers, then compares
the five registered account views. No strategy search or live system access.
"""
from pathlib import Path
import gc
import hashlib
import json
import pickle
import subprocess
import sys
import warnings

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
SP = Path(sys.argv[1] if len(sys.argv) > 1 else "scratch_data").resolve()
SP.mkdir(exist_ok=True)
# Legacy modules use argv at import time.
sys.argv = [sys.argv[0], str(SP), "library"]
OUT = ROOT / "analysis/outputs/codex_swing_kind_account_replay"
OUT.mkdir(parents=True, exist_ok=True)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
import funded_bootstrap as FB
import funded_sim as F50
import funded_sim150 as F150
import funded_lab as FL
import portfolio as PF
import build_lab as BL
import swing_target_bench as ST
import overnight_tick_bench as OT
import codex_ob_v2_accounts as TABLE
import codex_anson_accounts as ENGINE


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def prepare():
    """Canonical cache construction only: no scans, placebos or extra benches."""
    from grid24 import Grid24
    for name, args in (("g24", ()), ("ge", ("data/ES_1min_20*.csv", ""))):
        p = SP / (name + ".pkl")
        if not p.exists():
            g = Grid24(*args)
            with p.open("wb") as f:
                pickle.dump(g, f, protocol=4)
            del g
    if not (SP / "lab.pkl").exists():
        g = pd.read_pickle(SP / "g24.pkl")
        lab = FL.Lab(g)
        atr = g.daily_atr(15)
        for name, (path, stop) in BL.REPORTS.items():
            t = PF.load_mc(g, path)
            # Apply the registered common source end before path construction.
            # The current ONB export contains an unfinished October 12 sentinel.
            # It is outside this study; never fabricate an exit for it.
            t = t[t.date <= "2026-07-07"].reset_index(drop=True)
            if name == "OND_MC":
                t = t[t.j0 <= 30].reset_index(drop=True)
            assert (t.j1 >= t.j0).all(), f"Unresolved held path in {name}"
            lab.add(name, t, stop_pts=stop * atr)
        with (SP / "lab.pkl").open("wb") as f:
            pickle.dump(lab, f, protocol=4)
        print("Base report paths built", flush=True)
        del lab, g
        gc.collect()
    if not (SP / "single_print_sessions.pkl").exists():
        import single_print_test as single
        g = pd.read_pickle(SP / "g24.pkl")
        saved = single.load
        single.load = lambda sym: g
        try:
            _, sessions = single.frame()
        finally:
            single.load = saved
        sessions.to_pickle(SP / "single_print_sessions.pkl")
        del g, sessions
        gc.collect()
        print("Fixed single-print flags built", flush=True)
    if not (SP / "s_rank_gap2.pkl").exists():
        import s_rank_gap_round2_test as gap
        s = gap.Sym("CL")
        rolls, _ = gap.rolls_cl(s)
        s.set_rolls(rolls)
        frame = gap.sunday_frame(s)
        with (SP / "s_rank_gap2.pkl").open("wb") as f:
            pickle.dump({"frames": {"CL": frame}}, f, protocol=4)
        del s, frame
        gc.collect()
        print("Fixed CL calendar built", flush=True)
    if not (SP / "rs_trades.csv").exists():
        import relative_strength_test as rs
        days, nq, es = rs.load()
        t = rs.trades(days, nq, rs.signals(days, nq, es))
        t.to_csv(SP / "rs_trades.csv", index=False)
        del days, nq, es, t
        gc.collect()
        print("Fixed RS baseline built", flush=True)
    (SP / "swing_be.csv").write_bytes((ROOT / "checks/candidates/swing_target/codex_be_trades.csv").read_bytes())


def configurations(which):
    pl = ST.plans50() if which == 50 else ST.plans150()
    base = pl[f"{which}K plan"]
    add = pl["+ ST 1 MNQ" if which == 50 else "+ ST 2 MNQ"]
    adopted = pl["VB 2/1 -> 1/1 + ST 1" if which == 50 else "DT 2 -> ST 2"]
    empty = {k: v for k, v in adopted.items() if k != "ST"}
    legacy = {("ST_TEXT" if k == "ST" else k): v for k, v in adopted.items()}
    return {"base": base, "addition": add, "replacement": adopted,
            "empty_slot": empty, "replacement_text": legacy}


def summary(r, y1):
    t6 = np.where(r[:, 1] == 6, r[:, 2], np.inf)
    med = np.median(t6)
    return dict(y1=float(y1.mean()), y1_p5=float(np.percentile(y1, 5)),
                y2=float(r[:, 0].mean()), y2_p5=float(np.percentile(r[:, 0], 5)),
                blown=float(r[:, 3].mean()), all6=float((r[:, 1] == 6).mean()),
                median_days6=float(med) if np.isfinite(med) else None)


def paired_ci(x):
    # Monte Carlo sampling uncertainty of the mean, not uncertainty about edge persistence.
    rng = np.random.default_rng(20261030)
    means = x[rng.integers(0, len(x), (2000, len(x)))].mean(axis=1)
    return np.percentile(means, [5, 95]).tolist()


def main():
    prepare()
    parity, rows, diffs, calendars, audits = [], [], [], [], []
    # Meaningful simulator fixtures cover payouts, trail, DLL, zero size, rounding.
    for which, f in ((50, F50), (150, F150)):
        parameters = ENGINE.rules(f, f"{which}K_funded")
        for label, close, low, q in (("payout", 350., -10., 1.),
                ("trail", -500., -5000., 1.), ("dll", 100., -2100., 1.),
                ("zero", 0., 0., 0.), ("rounding", 120., -120., 2.5)):
            w, c, b = np.full((1, 40, 3), low), np.full((1, 40), close), np.full((1, 40), q)
            table = TABLE.make_table(w, c, b)
            hist = np.random.default_rng(1).integers(0, 40, (2, 500))
            parity += ENGINE.parity_check(w, c, table, hist, f, parameters, f"{which}/{label}")
    for which, f in ((50, F50), (150, F150)):
        lab = OT.lab_for(which)
        ST.SP = str(SP) + "/"
        t = ST.pt_trades(lab.g)
        legacy = t.copy()
        reasons = pd.read_csv(SP / "swing_be.csv", parse_dates=["date"]).set_index("date").reason
        legacy["kind"] = legacy.date.map(reasons)
        # Legacy loader overwrote holiday exit kinds with numeric 2 as well.
        repairs = pd.read_csv(SP / "swing_be.csv", parse_dates=["date"])
        repair_dates = repairs.loc[repairs.apex_flat_violation, "date"]
        legacy.loc[legacy.date.isin(repair_dates), "kind"] = 2
        lab.add("ST", t)
        lab.add("ST_TEXT", legacy)
        dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
        use = np.asarray((dates >= "2018-01-01") & (dates <= "2026-07-07"))
        plans = configurations(which)
        keys = sorted(set().union(*(set(p) for p in plans.values())))
        # Restrict before allocating stacked paths; retain identical calendar across all views.
        for attr in ("W", "C", "stop", "N", "J0"):
            old = getattr(lab, attr)
            setattr(lab, attr, {k: np.ascontiguousarray(v[use]) for k, v in old.items() if k in keys})
        lab.tr = lab.tr[use]
        lab.D = len(lab.tr)
        dates = dates[use]
        lab.yr = dates.year
        audits.append(dict(account=which, ledger_rows=len(t), kind_counts=t.kind.value_counts().to_dict(),
            repaired_dates=repair_dates.dt.strftime("%Y-%m-%d").tolist(),
            corrected_minus_text_cash_per_MNQ=float((lab.C["ST"] - lab.C["ST_TEXT"]).sum()),
            daily_min_changed=int((np.abs(lab.W["ST"].min(1)-lab.W["ST_TEXT"].min(1)) > 1e-8).sum())))
        parameters = ENGINE.rules(f, f"{which}K_funded")
        histories = {}
        for cohort, start in (("2018_plus", "2018-01-01"), ("2023_plus", "2023-01-01")):
            histories[cohort] = FB.Boot(lab, start=start)._histories(1000, 500, 20, 20261030)
            np.save(OUT / f"histories_{which}_{cohort}.npy", histories[cohort])
            eligible = dates[dates >= start]
            calendars.append(dict(account=which, cohort=cohort, first=str(eligible.min().date()),
                                  last=str(eligible.max().date()), sessions=len(eligible)))
        W = np.stack([lab.W[k] for k in keys])
        C = np.stack([lab.C[k] for k in keys])
        # Same exact minute compression as canonical Boot; changes in any column retained.
        chg = np.zeros(W.shape[2], bool)
        chg[-1] = True
        chg[1:] |= (np.abs(np.diff(W, axis=2)) > 0).any(axis=(0, 1))
        chg[0] |= (W[:, :, 0] != 0).any()
        W = np.ascontiguousarray(W[:, :, chg])
        all_results = {cohort: {} for cohort in histories}
        for name, plan in plans.items():
            names, base = lab._base(plan)
            b = np.zeros((len(keys), lab.D))
            for i, k in enumerate(names):
                b[keys.index(k)] = base[i]
            table = TABLE.make_table(W, C, b)
            for cohort, hist in histories.items():
                # Verify full-size integer/cushion state and all five simulator outputs.
                parity += ENGINE.parity_check(W, C, table, hist[:3], f, parameters,
                                               f"{which}/{cohort}/{name}")
                r = ENGINE.run_table(table, hist, 500, parameters)
                y1 = ENGINE.run_table(table, hist, 250, parameters)[:, 0]
                all_results[cohort][name] = (r, y1)
                np.savez_compressed(OUT / f"results_{which}_{cohort}_{name}.npz", results=r, y1=y1)
                rows.append(dict(account=which, cohort=cohort, plan=name, **summary(r, y1)))
            print(f"{which}K {name} replayed", flush=True)
            del table
        for cohort, results in all_results.items():
            for name, control in (("replacement", "base"), ("replacement", "empty_slot"),
                                   ("replacement", "replacement_text"), ("addition", "base")):
                r, y = results[name]
                br, by = results[control]
                for metric, delta in (("y1", y-by), ("y2", r[:, 0]-br[:, 0]),
                                      ("blown", r[:, 3]-br[:, 3])):
                    lo, hi = paired_ci(delta)
                    diffs.append(dict(account=which, cohort=cohort, plan=name, control=control,
                        metric=metric, mean=float(delta.mean()), mean_mc_p5=lo, mean_mc_p95=hi,
                        changed_histories=int((np.abs(delta)>1e-8).sum())))
        del lab, W, C
        gc.collect()
    pd.DataFrame(rows).to_csv(OUT / "summary.csv", index=False)
    pd.DataFrame(diffs).to_csv(OUT / "paired_differences.csv", index=False)
    dump("parity.json", parity)
    dump("ledger_checks.json", audits)
    sources = sorted((ROOT / "analysis").glob("*.py"))
    inputs = sorted((ROOT / "data").glob("*.csv")) + sorted((ROOT / "mc_reports").glob("*.xlsx"))
    inputs += [ROOT / "checks/candidates/swing_target/codex_be_trades.csv",
               ROOT / "checks/candidates/overnight_tick/python_trades.csv"]
    dump("manifest.json", dict(code_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        plan_commit="531e3b1", seed=20261030, histories=1000, horizon=500, block=20,
        calendars=calendars, plans={str(w): configurations(w) for w in (50, 150)},
        sources={str(p.relative_to(ROOT)):sha(p) for p in sources},
        inputs={str(p.relative_to(ROOT)):sha(p) for p in inputs},
        caches={p.name:sha(p) for p in SP.iterdir() if p.suffix in (".pkl", ".csv")},
        versions={"numpy": np.__version__, "pandas": pd.__version__},
        limits=["Historical base roster; 50K RS slot predates T_ONESIDE replacement",
                "Existing CLS and OT daily-adverse approximation; MOC uses existing close marks",
                "NQ-equivalent fees; no native micro fee/fill verification",
                "MC interval covers Monte Carlo mean sampling only, not edge/model uncertainty",
                "Fixed CODE_BE ledger plus three holiday repairs, not a new v3 signal replication"] ))
    print(pd.DataFrame(rows).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
