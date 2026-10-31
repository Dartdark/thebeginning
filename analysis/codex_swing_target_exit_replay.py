"""Rebuild prerequisites and replay the fixed Swing Target funded comparisons.

Run from repository root:
  python analysis/codex_swing_target_exit_replay.py scratch_data prepare
  python analysis/codex_swing_target_exit_replay.py scratch_data 50 [histories]
  python analysis/codex_swing_target_exit_replay.py scratch_data 150 [histories]
Uses existing research functions; does not rerun signal searches.
"""
import hashlib
import json
import pickle
from pathlib import Path
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, "analysis")
import numpy as np
import pandas as pd

SP = Path(sys.argv[1] if len(sys.argv) > 1 else "scratch_data")
MODE = sys.argv[2] if len(sys.argv) > 2 else "prepare"
N = int(sys.argv[3]) if len(sys.argv) > 3 else 500
OUT = Path("analysis/outputs/codex_swing_target_exit_replay")
if MODE != "prepare":
    OUT = OUT / f"n{N}"
OUT.mkdir(parents=True, exist_ok=True)
SP.mkdir(parents=True, exist_ok=True)


def prepare():
    from grid24 import Grid24
    from build_lab import REPORTS
    from portfolio import load_mc
    from funded_lab import Lab
    from bridge_monday_confirm import load_bridge_mc

    for key, args in (("g24", ()), ("ge", ("data/ES_1min_20*.csv", ""))):
        path = SP / f"{key}.pkl"
        if not path.exists():
            with path.open("wb") as f:
                pickle.dump(Grid24(*args), f, protocol=4)
        print(f"{key} ready", flush=True)
    if not (SP / "lab.pkl").exists():
        g = pd.read_pickle(SP / "g24.pkl")
        atr = g.daily_atr(15)
        lab = Lab(g)
        for key, (report, sa) in REPORTS.items():
            t = load_mc(g, report)
            if key == "OND_MC":
                t = t[t.j0 <= 30].reset_index(drop=True)
            if (t.j1 < t.j0).any():
                # MultiCharts labels its final unclosed ticket ExitShort/open,
                # with a midnight placeholder. It is not a realized trade.
                raw = pd.read_excel(report, sheet_name="List of Trades", header=2)
                exits = raw[raw.Type.astype(str).str.startswith("Exit")].reset_index(drop=True)
                assert len(exits) == len(t)
                bad = t.j1 < t.j0
                assert exits.loc[bad, "Signal"].str.lower().eq("open").all()
                print("Exclude unclosed MC ticket:", key, t[bad].to_dict("records"), flush=True)
                t = t[~bad].reset_index(drop=True)
            lab.add(key, t, stop_pts=sa * atr)
            if key in ("ONB_ML2_MC", "LDF_MC"):
                base = "ONB_ML2" if key == "ONB_ML2_MC" else key
                for side, suffix in ((1, "L"), (-1, "S")):
                    lab.add(f"{base}_{suffix}", t[t.side == side].reset_index(drop=True), stop_pts=sa * atr)
            print(key, len(t), flush=True)
        lab.add("MON_BR_MC", load_bridge_mc(g), slippage=False)
        pd.to_pickle(lab, SP / "lab.pkl")
        del lab, g
    if not (SP / "single_print_sessions.pkl").exists():
        import single_print_test as single
        _, sessions = single.frame()
        sessions.to_pickle(SP / "single_print_sessions.pkl")
        print("single prints ready", flush=True)
    if not (SP / "s_rank_gap2.pkl").exists():
        import s_rank_gap_round2_test as gap
        sym = gap.Sym("CL")
        bars, _ = gap.rolls_cl(sym)
        sym.set_rolls(bars)
        pd.to_pickle({"frames": {"CL": gap.sunday_frame(sym)}}, SP / "s_rank_gap2.pkl")
        print("CL frame ready", flush=True)
    if not (SP / "rs_trades.csv").exists():
        import relative_strength_test as rs
        days, nq, es = rs.load()
        rs.trades(days, nq, rs.signals(days, nq, es)).to_csv(SP / "rs_trades.csv", index=False)
        print("RS ready", flush=True)
    import shutil
    shutil.copyfile("checks/candidates/swing_target/codex_be_trades.csv", SP / "swing_be.csv")


def replay(which):
    import swing_target_bench as st
    import funded_bootstrap as fb
    import funded_sim as f50
    import funded_sim150 as f150
    from funded_lab import with_slippage

    lab = st.OTB.lab_for(which)
    t = st.pt_trades(lab.g)
    lab.add("ST", t)
    # Recreate the former text encoding, retaining numeric kind=2 on holiday fixes.
    source = pd.read_csv(SP / "swing_be.csv", parse_dates=["date"])
    source = source[source.date >= "2018-01-01"].reset_index(drop=True)
    old = t.copy()
    old["kind"] = source.reason.astype(object)
    old.loc[source.apex_flat_violation, "kind"] = 2
    lab.add("ST_legacy", old)
    slipped = with_slippage(t)
    expected = (slipped.exit - slipped.entry) * slipped.side * 20 - 7.25
    daily = pd.Series(lab.C["ST"] * 10, index=pd.DatetimeIndex(lab.g.ts[lab.tr]))
    np.testing.assert_allclose(daily.sum(), expected.sum(), atol=1e-7)
    # The unmodified ledger's net must also agree for every non-holiday row.
    mask = ~source.apex_flat_violation
    np.testing.assert_allclose(expected[mask], source.net[mask], atol=1e-7)
    audit = dict(trades=len(t), reasons=source.reason.value_counts().to_dict(),
                 holiday_exits=int(source.apex_flat_violation.sum()),
                 daily_net_per_nq=float(daily.sum()), trade_net_per_nq=float(expected.sum()),
                 legacy_net_per_nq=float(lab.C["ST_legacy"].sum() * 10),
                 trading_days=len(daily), first=str(daily.index.min()), last=str(daily.index.max()),
                 source_sha256=hashlib.sha256((SP / "swing_be.csv").read_bytes()).hexdigest())
    plans = st.plans50() if which == 50 else st.plans150()
    adopted = "VB 2/1 -> 1/1 + ST 1" if which == 50 else "DT 2 -> ST 2"
    plans["replacement slot empty"] = {k: v for k, v in plans[adopted].items() if k != "ST"}
    plans["adopted, legacy encoding"] = {("ST_legacy" if k == "ST" else k): v for k, v in plans[adopted].items()}
    fb.F = f50 if which == 50 else f150
    kw = {} if which == 50 else {"ref": 3000.0}
    print(json.dumps(audit, indent=2), flush=True)
    res, y1, nmin = fb.Boot(lab).run(plans, n=N, H=500, L=20, seed=20261030, **kw)
    pd.to_pickle((res, y1), OUT / f"{which}_histories.pkl")
    bench = fb.Boot.__new__(fb.Boot)
    bench.run = lambda *args, **kwargs: (res, y1, nmin)
    table, formatted, _ = bench.compare(plans)
    table.to_csv(OUT / f"{which}_summary.csv")
    print(formatted, flush=True)
    rng = np.random.default_rng(20261030)
    boot = rng.integers(0, N, size=(10000, N))
    paired = {}
    for control in (next(iter(plans)), "replacement slot empty", "adopted, legacy encoding"):
        stats = {}
        for metric, diff in (("y1", y1[adopted] - y1[control]),
                             ("y2", res[adopted][:, 0] - res[control][:, 0]),
                             ("blown", res[adopted][:, 3] - res[control][:, 3])):
            lo, hi = np.percentile(diff[boot].mean(axis=1), [5, 95])
            stats[metric] = {"mean": float(diff.mean()), "p5": float(lo), "p95": float(hi)}
        paired[control] = stats
    payload = {"audit": audit, "plans": plans, "seed": 20261030, "histories": N,
               "block_days": 20, "horizon": 500, "paired": paired}
    (OUT / f"{which}_audit.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps(paired, indent=2), flush=True)


if __name__ == "__main__":
    if MODE == "prepare":
        prepare()
    else:
        replay(int(MODE))
